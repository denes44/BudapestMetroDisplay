# transit_leds.py
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

RGB = tuple[int, int, int]


# ========= helpers =========


def _clamp8(x: int) -> int:
    return 0 if x < 0 else min(x, 255)


def _rgb_clamp(rgb: RGB) -> RGB:
    return _clamp8(rgb[0]), _clamp8(rgb[1]), _clamp8(rgb[2])


def _rgb_max(a: RGB, b: RGB) -> RGB:
    return max(a[0], b[0]), max(a[1], b[1]), max(a[2], b[2])


# ========= lighting core =========


@dataclass
class LED:
    """Physical RGB LED.

    - (r,g,b) is the *current* output color.
    - default_override pins a default color for this LED (if None -> computed).
    - 'stops' back-ref lets the LED compute its default from attached Stops' Routes.
    """

    index: int
    r: int = 0
    g: int = 0
    b: int = 0
    stops: list[Stop] = field(default_factory=list)  # back-references from Stops
    color_override: RGB | None = None

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

    def get_default_color(self) -> RGB:
        """Return default color of the LED.

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

    def reset_to_default(self) -> None:
        """Reset the LEDs color to its default."""
        self.set_rgb(*self.get_default_color())


class LedStrip:
    """An LED Strip that hold LEDs, to make them easier to handle."""

    def __init__(self, leds: list[LED]) -> None:
        self.leds_by_index: dict[int, LED] = {led.index: led for led in leds}

    def off(self) -> None:
        """Turn off all LEDs in the LED Strip."""
        for led in self.leds_by_index.values():
            led.off()

    def reset_to_default(self) -> None:
        """Reset all LEDs in the LED Stripto its default color."""
        for led in self.leds_by_index.values():
            led.reset_to_default()

    def set_led(self, index_1b: int, rgb: RGB) -> None:
        """Set the color of a LED with a specific index."""
        led = self.leds_by_index.get(index_1b)
        if led:
            led.set_rgb(*_rgb_clamp(rgb))

    def to_tuple(self) -> tuple[int, ...]:
        """Return the values of the LEDs in the LED Strip as one big touple."""
        out: list[int] = []
        for idx in sorted(self.leds_by_index.keys()):
            led = self.leds_by_index[idx]
            out.extend((led.r, led.g, led.b))
        return tuple(out)


# ========= transit domain =========
class Network(BaseModel):
    """A Network which consist of Routes.

    routes: The list of Routes that belongs to this Network
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
        """Lookup a StopId by its API ID string."""
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
        """Lookup a Stop by the API ID string of a corresponding StopId."""
        return next(
            (
                stop
                for stop in self.iter_stops()
                if any(sid.stop_id == stop_id for sid in stop.stop_ids)
            ),
            None,
        )


class Route(BaseModel):
    """A Route which consist of Stops, and has its own properties.

    route_id: The API ID of the Route
    name: User-friendly name of the Route
    color: The color of the Route that is shown on the LEDs
    type: The type of the Route, Subway/Railway
    stops: List of Stops that are belongs to the Route
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    route_id: str
    name: str
    _color: RGB = (0, 0, 0)
    type: str | None = None
    stops: list[Stop] = Field(default_factory=list)

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

    def is_in_service(self) -> bool:
        """Return the in service status of the Stop.

        If it's a terminus Stop, the Stop is no service if ANY of it's
            StopIds are in no service.
        If it's an intermediate Stop, the Stop is no service if ALL of it's
            StopIds are in no service.
        If there are no StopIds associated to the Stop,
        it always returns False.
        """
        states = [si.in_service for si in self.stop_ids]
        if not states:
            return False
        return all(states) if self.is_terminus else any(states)


class StopId(BaseModel):
    """A single StopId that is part of a Stop.

    stop_id: The API ID of the StopId
    stop: The Stop object this StopId belongs to
    in_service: Whether the StopId is in service
    """

    stop_id: str
    stop: Stop | None = None
    in_service: bool = True


# ========= fader (animation engine for fades) =========


def ease_linear(t: float) -> float:
    return t


def ease_in_out_quad(t: float) -> float:
    return 2 * t * t if t < 0.5 else 1 - ((-2 * t + 2) ** 2) / 2


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


class Fader:
    """Drives per-LED fades. Call step() at your frame rate, then pack via strip.to_tuple().
    One active animation per LED index (new fades overwrite running ones for that LED).
    """

    def __init__(self, leds: list[LED]) -> None:
        self._anims: dict[int, _Anim] = {}
        self._leds: dict[int, LED] = {led.index: led for led in leds}

    def fade_led(
        self,
        index: int,
        to: RGB,
        duration: float = 0.5,
        ease: Callable[[float], float] = ease_linear,
    ) -> None:
        led = self._leds[index]
        self._anims[index] = _Anim(
            led=led,
            start=(led.r, led.g, led.b),
            end=_rgb_clamp(to),
            t0=time.perf_counter(),
            dur=max(0.0, float(duration)),
            ease=ease,
        )

    def fade_stop(
        self,
        stop: Stop,
        to: RGB,
        duration: float = 0.5,
        ease: Callable[[float], float] = ease_linear,
    ) -> None:
        self.fade_led(stop.led.index, to, duration, ease)

    def fade_route(
        self,
        route: Route,
        to: RGB,
        duration: float = 0.5,
        ease: Callable[[float], float] = ease_linear,
    ) -> None:
        for st in route.stops:
            self.fade_led(st.led.index, to, duration, ease)

    def fade_to_defaults(
        self,
        duration: float = 0.5,
        ease: Callable[[float], float] = ease_linear,
    ) -> None:
        now = time.perf_counter()
        for led in self._leds.values():
            target = led.get_default_color()
            self._anims[led.index] = _Anim(
                led=led,
                start=(led.r, led.g, led.b),
                end=_rgb_clamp(target),
                t0=now,
                dur=max(0.0, float(duration)),
                ease=ease,
            )

    def cancel_led(self, index: int, *, snap_to_end: bool = False) -> None:
        anim = self._anims.pop(index, None)
        if anim and snap_to_end:
            anim.led.set_rgb(*anim.end)

    def step(self) -> None:
        now = time.perf_counter()
        finished = [idx for idx, anim in self._anims.items() if anim.step(now)]
        for idx in finished:
            self._anims.pop(idx, None)

    def is_active(self) -> bool:
        return bool(self._anims)
