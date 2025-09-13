# transit_leds.py
from __future__ import annotations

import logging
import time as _t
from dataclasses import field
from threading import Lock
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from BudapestMetroDisplay.config import settings
from BudapestMetroDisplay.led_helpers import (
    _clamp8,
    _rgb_clamp,
    _rgb_max,
    _rgb_scale,
    ease_in_out_quad,
)

RGB = tuple[int, int, int]
logger = logging.getLogger(__name__)


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
    def color(self) -> RGB:
        """Get the LED color as an RGB tuple."""
        return self.r, self.g, self.b

    @color.setter
    def color(self, value: RGB) -> None:
        """Set the LED color from an (r, g, b) tuple (auto-clamped to 0..255)."""
        r, g, b = _rgb_clamp(value)
        self.r, self.g, self.b = r, g, b

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
                c = _rgb_max(c, st.color)
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
                present_colors.append(st.color)

        if present_colors:
            # Max-blend all present Route colors channel-wise to get the presence color.
            c: RGB = (0, 0, 0)
            for col in present_colors:
                c = _rgb_max(c, col)

            return c

        # ---------- Rule 3: idle → dimmed default ----------
        # Apply your globally configured idle dim ratio to the default color
        return _rgb_scale(self.default_color, settings.led.dim_ratio)


class LedStrip(BaseModel):
    """An LED Strip that holds LEDs to make them easier to handle."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    leds: list[LED] = Field(default_factory=list)

    # Active animations for LEDs that are currently transitioning colors.
    anims: dict[int, Animation] = Field(default_factory=dict)
    previous_target_color: dict[int, RGB] = Field(default_factory=dict)

    def to_tuple(self) -> tuple[int, ...]:
        """Pack current LED colors to sACN/DMX order.

        (led1_r, led1_g, led1_b, led2_r, led2_g, led2_b, ...)
        Ordered by ascending LED.index for stable output.
        """
        out: list[int] = []
        for led in sorted(self.leds, key=lambda l: l.index):
            out.extend((led.r, led.g, led.b))
        return tuple(out)

    def step(self) -> None:
        """Advance all active animations to the current time and remove those that finished."""
        # Grab the timestamp once per frame for consistent stepping.
        now: float = _t.perf_counter()

        # Check if any LEDs have its target color changed
        for led in self.leds:
            target_color: RGB = led.target_color

            anim: Animation = self.anims.get(led.index)
            if anim is not None:
                # Target color changed, start a new animation.
                if target_color != anim.end:
                    # If mid-fade, sample the current color.
                    start_color: RGB = anim.sample(now)

                    self.anims[led.index] = Animation(
                        led=led,
                        start=start_color,  # starting color (sampled if mid-fade)
                        end=target_color,  # new target color
                        t0=now,  # start timestamp
                    )
            elif (
                self.previous_target_color.get(led.index) is not None
                and target_color != self.previous_target_color[led.index]
            ):
                # Animation does not exist, but the target color has changed
                # since the previous frame.
                self.anims[led.index] = Animation(
                    led=led,
                    start=led.color,  # starting color
                    end=target_color,  # new target color
                    t0=now,  # start timestamp
                )

            self.previous_target_color[led.index] = target_color

        # Collect indices that finish this frame to remove after iteration.
        finished: list[int] = []

        now = _t.perf_counter()

        # Drive each animation: set the LED.r/g/b to the correct mid-fade color.
        for idx, anim in self.anims.items():
            if anim.step(now):  # step returns True if finished
                finished.append(idx)

        # Drop finished animations
        for idx in finished:
            self.anims.pop(idx, None)


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
    _lock: Lock = PrivateAttr(default_factory=Lock)

    @property
    def lock(self) -> Lock:
        """Return the lock object for this Route."""
        return self._lock

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
        with self._lock:
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
    _lock: Lock = PrivateAttr(default_factory=Lock)

    @property
    def lock(self) -> Lock:
        """Return the lock object for this Stop."""
        return self._lock

    def model_post_init(self, __context: Any, /) -> None:
        """Link Stop <-> LED."""
        if self not in self.led.stops:
            self.led.stops.append(self)

    @property
    def color(self) -> RGB:
        """The default LED color of the Stop inherited from its Route."""
        return (0, 0, 0) if self.route is None else self.route.color

    @property
    def in_service(self) -> bool:
        """Return the in service status of the Stop.

        If it's a terminus Stop, the Stop is no service if ANY of its
            StopIds are in no service.
        If it's an intermediate Stop, the Stop is no service if ALL of its
            StopIds are in no service.
        If there are no StopIds associated with the Stop, it always returns False.
        """
        with self._lock:
            states = [si.in_service for si in self.stop_ids]

        if not states:
            return False

        return all(states) if self.is_terminus else any(states)

    @property
    def vehicle_present(self) -> bool:
        """Return the vehicle present status of the Stop."""
        with self._lock:
            return any(si.vehicle_present for si in self.stop_ids)

    def add_stop_id(self, stop_id: StopId) -> None:
        """Add a StopId to the Stop."""
        with self._lock:
            if stop_id not in self.stop_ids:
                self.stop_ids.append(stop_id)

            # Link Stop <-> StopId
            if stop_id.stop is not self:
                stop_id.stop = self


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


class Animation(BaseModel):
    """Represents one animation that drives a LED from a start to an end color.

    Fields:
      - led   : the LED instance to mutate each frame
      - start : starting RGB at the moment the animation began
      - end   : target RGB we want to reach
      - t0    : start time (monotonic perf_counter) to compute progress
      - dur   : total duration in seconds (0 means snap instantly)
    """

    # Allow non-Pydantic types (callables, LED objects) inside this model.
    model_config = ConfigDict(arbitrary_types_allowed=True)

    led: LED  # LED object to update
    start: RGB  # Starting color
    end: RGB  # Target color
    t0: float  # Time when animation started (seconds, monotonic)
    dur: float = settings.led.fade_time  # Duration in seconds (>= 0)

    def sample(self, now: float) -> RGB:
        """Compute the interpolated color for the time 'now'.

        Returns the color we should display at 'now'.
        """
        # Snap instantly if the duration is zero (or negative for safety).
        if self.dur <= 0:
            return _rgb_clamp(self.end)

        # Compute normalized progress u in [0,1].
        u: float = (now - self.t0) / self.dur

        # If not yet started, stay at the start color.
        if u <= 0.0:
            return _rgb_clamp(self.start)

        # If finished (or overshot), use the end color.
        if u >= 1.0:
            return _rgb_clamp(self.end)

        # Apply easing to the linear progress to get a smoother curve.
        k: float = ease_in_out_quad(u)

        # Interpolate each channel separately using the eased progress.
        r = int(self.start[0] + (self.end[0] - self.start[0]) * k)
        g = int(self.start[1] + (self.end[1] - self.start[1]) * k)
        b = int(self.start[2] + (self.end[2] - self.start[2]) * k)

        # Clamp to ensure valid DMX/sACN byte values and return.
        return _clamp8(r), _clamp8(g), _clamp8(b)

    def step(self, now: float) -> bool:
        """Advance the LED to the color corresponding to time 'now'.

        Returns True when the animation is finished.
        """
        # Compute the color for 'now' (does not mutate LED yet).
        r, g, b = self.sample(now)

        # Write the computed color onto the actual LED object (stateful side effect).
        self.led.r, self.led.g, self.led.b = r, g, b

        # Tell the caller whether we're done (for pruning finished animations).
        return (self.dur <= 0) or (now - self.t0 >= self.dur)
