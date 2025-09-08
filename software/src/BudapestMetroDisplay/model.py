# transit_leds.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

from BudapestMetroDisplay.config import settings
from BudapestMetroDisplay.led_helpers import _clamp8, _rgb_clamp, _rgb_max, _rgb_scale

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

RGB = tuple[int, int, int]


class LED(BaseModel):
    """Physical RGB LED.

    - (r,g,b) is the *current* output color.
    - default_override pins a default color for this LED (if None -> computed).
    - 'stops' back-ref lets the LED compute its default from attached Stops' Routes.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    index: int
    r: int = 0
    g: int = 0
    b: int = 0
    stops: list[Stop] = field(default_factory=list)  # back-references from Stops
    color_override: RGB | None = None

    @property
    def default_color(self) -> RGB:
        """Return the default color of the LED.

        If override set -> return it.
        Else -> per-channel max of default colors from Routes of attached Stops.
        If no stops -> black.
        """
        if self.color_override is not None:
            return self.color_override
        c: RGB = (0, 0, 0)
        for st in self.stops:
            if st.route is not None:
                c = _rgb_max(c, st.route.color)
        return c

    @property
    def target_color(self) -> RGB:
        """Compute the desired target color for the LED.

        1) If ALL Stops on an LED are NOT operational
              → BLACK (0,0,0)
        2) Else if ANY vehicle present on that LED
              → channel-wise MAX of present Routes' default_color
        3) Else (idle)
              → LED.get_default_color() * settings.led.dim_ratio
        """
        # ---------- Rule 1: blackout if ALL attached Stops are down ----------
        # We assume "down" until we find a Stop that says it IS in service.
        all_down: bool = True
        for st in self.stops:
            if st.in_service:
                all_down = False
                break
        if all_down:
            return 0, 0, 0  # Absolute priority: black out this LED

        # ---------- Rule 2: presence color if ANY vehicle present ----------
        # Collect the default_color of Routes that currently have presence on this LED.
        present_colors: list[RGB] = []
        for st in self.stops:
            if st.route is None:
                continue  # A Stop without a Route contributes nothing
            # Presence for a Stop means any of its StopIds report vehicle_present=True.
            if st.vehicle_present:
                present_colors.append(st.route.default_color)

        if present_colors:
            # Max-blend all present Route colors channel-wise to get the presence color.
            c: RGB = (0, 0, 0)
            for col in present_colors:
                c = _rgb_max(c, col)

            return c

        # ---------- Rule 3: idle → dimmed default ----------
        # Apply your globally configured idle dim ratio to the default color
        return _rgb_scale(self.get_default_color(), settings.led.dim_ratio)

    def set_rgb(self, r: int, g: int, b: int) -> None:
        """Set the LED colors to a specific value."""
        self.r, self.g, self.b = _clamp8(r), _clamp8(g), _clamp8(b)

    def off(self) -> None:
        """Set the LED colors to off."""
        self.r = self.g = self.b = 0

    def set_color_override(self, color: RGB | None) -> None:
        """Set an override color to the LED.

        If an override color is set, it will be used instead of the computed
        color from the Routes that the LED belongs to.
        """
        self.color_override = None if color is None else _rgb_clamp(color)

    def reset_to_default(self) -> None:
        """Reset the LEDs color to its default."""
        self.set_rgb(
            self.default_color[0],
            self.default_color[1],
            self.default_color[2],
        )


class LedStrip(BaseModel):
    """An LED Strip that holds LEDs to make them easier to handle."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    leds: list[LED]

    def off(self) -> None:
        """Turn off all LEDs in the LED Strip."""
        for led in self.leds:
            led.off()

    def reset_to_default(self) -> None:
        """Reset all LEDs in the LED Strip to its default color."""
        for led in self.leds:
            led.reset_to_default()

    def set_led(self, index: int, rgb: RGB) -> None:
        """Set the color of a LED with a specific index."""
        for led in self.leds:
            if led.index == index:
                led.set_rgb(*_rgb_clamp(rgb))

    def to_tuple(self) -> tuple[int, ...]:
        """Return the values of the LEDs in the LED Strip as one big tuple."""
        out: list[int] = []
        for idx in sorted(self.leds_by_index.keys()):
            led = self.leds_by_index[idx]
            out.extend((led.r, led.g, led.b))
        return tuple(out)


# ========= transit domain =========
class Network(BaseModel):
    """A Network that consists of Routes.

    routes: The list of Routes that belong to this Network
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    routes: list[Route] = Field(default_factory=list)

    def add_route(self, route: Route) -> None:
        """Add a Route to the Network."""
        if route not in self.routes:
            self.routes.append(route)

    def get_route(self, route_id: str) -> Route | None:
        """Return the Route with a specific ID."""
        for r in self.routes:
            if r.route_id == route_id:
                return r
        return None

    # -- derived iterators --
    def iter_stops(self) -> Iterator[Stop]:
        """Collect all Stops from the Routes of the Network."""
        for r in self.routes:
            yield from r.stops

    def iter_leds(self) -> Iterator[LED]:
        """Collect all LEDs from the Stops of the Network."""
        seen: set[int] = set()
        for stop in self.iter_stops():
            led_index = stop.led.index
            if led_index not in seen:
                seen.add(led_index)
                yield stop.led

    # -- lookups --
    def get_stopid(self, stop_id: str) -> StopId | None:
        """Look up a StopId by its API ID string."""
        return next(
            (
                sid
                for stop in self.iter_stops()
                for sid in stop.stop_ids
                if sid.stop_id == stop_id
            ),
            None,
        )

    def get_stop_by_stopid(self, stop_id: str) -> Stop | None:
        """Look up a Stop by the API ID string of a corresponding StopId."""
        return next(
            (
                stop
                for stop in self.iter_stops()
                if any(sid.stop_id == stop_id for sid in stop.stop_ids)
            ),
            None,
        )


class Route(BaseModel):
    """A Route that consists of Stops and has its own properties.

    route_id: The API ID of the Route
    name: User-friendly name of the Route
    color: The color of the Route that is shown on the LEDs
    type: The type of the Route, Subway/Railway
    stops: List of Stops that belong to the Route
    schedule_interval: The average second between each consecutive departure
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    route_id: str
    name: str
    _color: RGB = (0, 0, 0)
    type: str | None = None
    stops: list[Stop] = Field(default_factory=list)
    schedule_interval: float = -1

    @property
    def color(self) -> RGB:
        """Return the color of the Route."""
        return self._color

    @color.setter
    def color(self, rgb: RGB) -> None:
        """Set the color of the Route."""
        self._color = _rgb_clamp(rgb)

    def add_stop(self, stop: Stop) -> None:
        """Link Route <-> Stop."""
        if stop not in self.stops:
            self.stops.append(stop)  # Add Stop to the Route
        if stop.route is not self:
            stop.route = self  # Set the Route for the Stop

    def get_stop_id(self, stop_id: str) -> StopId | None:
        """Return the StopId object in this Route that matches stop_id.

        Returns None if not found.
        """
        return next(
            (
                sid
                for stop in self.stops
                for sid in stop.stop_ids
                if sid.stop_id == stop_id
            ),
            None,
        )

    def get_stop_ids(self, *, string_only: bool = False) -> list[StopId] | list[str]:
        """Return all Stop IDs of the Route.

        If string_only is True, return only the stop_id strings;
        otherwise return StopId objects.
        """
        return (
            [sid.stop_id for stop in self.stops for sid in stop.stop_ids]
            if string_only
            else [sid for stop in self.stops for sid in stop.stop_ids]
        )


class Stop(BaseModel):
    """A physical stop along a Route.

    name: User friendly name of the stop
    led: The LED object that belongs to this stop
    route: The Route object that this Stop is part of
    is_terminus: Whether this Stop is a terminus stop
    stop_ids: List of StopIds that belongs to this Stop
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str | None = None
    led: LED
    route: Route | None = None
    is_terminus: bool = False
    stop_ids: list[StopId] = Field(default_factory=list)

    def model_post_init(self, __context: Any, /) -> None:
        """Link Stop <-> LED."""
        if self not in self.led.stops:
            self.led.stops.append(self)

    @property
    def default_color(self) -> RGB:
        """The default LED color of the Stop inherited from its Route."""
        return (0, 0, 0) if self.route is None else self.route.color

    def add_stop_id(self, stop_id: StopId) -> None:
        """Add a StopId to the Stop."""
        if stop_id not in self.stop_ids:
            self.stop_ids.append(stop_id)

        # Link Stop <-> StopId
        if stop_id.stop is not self:
            stop_id.stop = self

    @property
    def in_service(self) -> bool:
        """Return the in service status of the Stop.

        If it's a terminus Stop, the Stop is no service if ANY of its
            StopIds are in no service.
        If it's an intermediate Stop, the Stop is no service if ALL of its
            StopIds are in no service.
        If there are no StopIds associated with the Stop, it always returns False.
        """
        states = [si.in_service for si in self.stop_ids]
        if not states:
            return False
        return all(states) if self.is_terminus else any(states)

    @property
    def vehicle_present(self) -> bool:
        """Return the vehicle present status of the Stop."""
        return any(si.vehicle_present for si in self.stop_ids)


class StopId(BaseModel):
    """A single StopId that is part of a Stop.

    stop_id: The API ID of the StopId
    stop: The Stop object this StopId belongs to
    in_service: Whether the StopId is in service
    vehicle_present: Whether a vehicle is present at the StopId
    """

    stop_id: str
    stop: Stop | None = None
    in_service: bool = True
    vehicle_present: bool = False


@dataclass
class _Anim:
    led: LED
    start: RGB
    end: RGB
    t0: float
    dur: float
    ease: Callable[[float], float]

    def step(self, now: float) -> bool:
        """Advance animation. Return True when finished."""
        if self.dur <= 0:
            self.led.set_rgb(*self.end)
            return True
        u = max(0.0, min(1.0, (now - self.t0) / self.dur))
        k = self.ease(u)
        r = int(self.start[0] + (self.end[0] - self.start[0]) * k)
        g = int(self.start[1] + (self.end[1] - self.start[1]) * k)
        b = int(self.start[2] + (self.end[2] - self.start[2]) * k)
        self.led.set_rgb(r, g, b)
        return u >= 1.0
