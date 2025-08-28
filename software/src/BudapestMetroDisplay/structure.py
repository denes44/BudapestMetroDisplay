# transit_leds.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterator, List, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict
import time

RGB = Tuple[int, int, int]


# ========= helpers =========

def _clamp8(x: int) -> int:
    return 0 if x < 0 else 255 if x > 255 else x

def _rgb_clamp(rgb: RGB) -> RGB:
    return (_clamp8(rgb[0]), _clamp8(rgb[1]), _clamp8(rgb[2]))

def _rgb_max(a: RGB, b: RGB) -> RGB:
    return (a[0] if a[0] >= b[0] else b[0],
            a[1] if a[1] >= b[1] else b[1],
            a[2] if a[2] >= b[2] else b[2])


# ========= lighting core =========

@dataclass
class LED:
    """
    Physical RGB LED (1-based index).
    - (r,g,b) is the *current* output color.
    - default_override pins a default color for this LED (if None -> computed).
    - 'stops' back-ref lets the LED compute its default from attached Stops' Routes.
    """
    index: int
    r: int = 0
    g: int = 0
    b: int = 0
    stops: List["Stop"] = field(default_factory=list)      # back-references from Stops
    default_override: Optional[RGB] = None

    def set_rgb(self, r: int, g: int, b: int) -> None:
        self.r, self.g, self.b = _clamp8(r), _clamp8(g), _clamp8(b)

    def off(self) -> None:
        self.r = self.g = self.b = 0

    def set_default_override(self, color: Optional[RGB]) -> None:
        self.default_override = None if color is None else _rgb_clamp(color)

    def get_default_color(self) -> RGB:
        """
        If override set -> return it.
        Else -> per-channel max of default colors from Routes of attached Stops.
        If no stops -> black.
        """
        if self.default_override is not None:
            return self.default_override
        c: RGB = (0, 0, 0)
        for st in self.stops:
            if st.route is not None:
                c = _rgb_max(c, st.route.default_color)
        return c

    def reset_to_default(self) -> None:
        self.set_rgb(*self.get_default_color())


class LedStrip:
    """
    Minimal strip: references LED objects and packs to a sACN/DMX tuple
    as (led1_r, led1_g, led1_b, led2_r, led2_g, led2_b, ...) in ascending LED.index.
    """
    def __init__(self, leds: List[LED]) -> None:
        self.leds_by_index: Dict[int, LED] = {led.index: led for led in leds}

    def clear(self) -> None:
        for led in self.leds_by_index.values():
            led.off()

    def apply_defaults(self) -> None:
        for led in self.leds_by_index.values():
            led.reset_to_default()

    def set_led(self, index_1b: int, rgb: RGB) -> None:
        led = self.leds_by_index.get(index_1b)
        if led:
            led.set_rgb(*_rgb_clamp(rgb))

    def to_tuple(self) -> Tuple[int, ...]:
        out: List[int] = []
        for idx in sorted(self.leds_by_index.keys()):
            led = self.leds_by_index[idx]
            out.extend((led.r, led.g, led.b))
        return tuple(out)


# ========= transit domain =========

class StopId(BaseModel):
    stop_id: str
    in_service: bool = True


class Route(BaseModel):
    """
    Route with a default color; owns Stop objects.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    route_code: str                 # stored on the object; Network won't key on it
    name: str
    default_color: RGB = (0, 0, 0)
    mode: Optional[str] = None
    stops: List["Stop"] = Field(default_factory=list)

    def set_default_color(self, rgb: RGB) -> None:
        self.default_color = _rgb_clamp(rgb)

    def add_stop(self, stop: "Stop") -> None:
        """
        Link Stop <-> Route and Stop <-> LED (back-refs).
        """
        if stop not in self.stops:
            self.stops.append(stop)
        if stop.route is not self:
            stop.route = self
        if stop not in stop.led.stops:
            stop.led.stops.append(stop)

    def remove_stop(self, stop: "Stop") -> None:
        if stop in self.stops:
            self.stops.remove(stop)
        if stop.route is self:
            stop.route = None
        if stop in stop.led.stops:
            stop.led.stops.remove(stop)


class Stop(BaseModel):
    """
    Physical stop referencing a Route and a LED.
    - is_terminus: behavior for service evaluation:
        * terminus -> out of service if ANY StopId is down (require ALL up)
        * intermediate -> out of service only if ALL StopIds are down (require ANY up)
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: Optional[str] = None
    led: LED
    route: Optional[Route] = None
    is_terminus: bool = False
    stop_ids: Dict[str, StopId] = Field(default_factory=dict)  # stop_id -> StopId

    @property
    def default_color(self) -> RGB:
        return (0, 0, 0) if self.route is None else self.route.default_color

    def add_stop_id(self, stop_id: str, *, in_service: bool = True) -> None:
        if stop_id not in self.stop_ids:
            self.stop_ids[stop_id] = StopId(stop_id=stop_id, in_service=in_service)

    def set_stop_id_service(self, stop_id: str, in_service: bool) -> None:
        if stop_id in self.stop_ids:
            self.stop_ids[stop_id].in_service = in_service

    def is_in_service(self) -> bool:
        """
        Terminus:     False if ANY StopId is down -> require ALL True.
        Intermediate: False only if ALL StopIds are down -> require ANY True.
        If no StopIds -> False.
        """
        states = [si.in_service for si in self.stop_ids.values()]
        if not states:
            return False
        return all(states) if self.is_terminus else any(states)


# ========= network (stores only Route objects) =========

class Network:
    """
    Holds ONLY Route objects. All lookups/LEDs/stops are derived by walking routes.
    """
    def __init__(self) -> None:
        self.routes: List[Route] = []  # list only; Route holds its own route_code

    # -- route ops --
    def add_route(self, route: Route) -> None:
        if route not in self.routes:
            self.routes.append(route)

    def get_route(self, route_code: str) -> Optional[Route]:
        for r in self.routes:
            if r.route_code == route_code:
                return r
        return None

    # -- derived iterators --
    def iter_stops(self) -> Iterator[Stop]:
        for r in self.routes:
            for s in r.stops:
                yield s

    def iter_leds(self) -> Iterator[LED]:
        seen: set[int] = set()
        for s in self.iter_stops():
            idx = s.led.index
            if idx not in seen:
                seen.add(idx)
                yield s.led

    # -- lookups --
    def get_stopid(self, stop_id: str) -> Optional[StopId]:
        """Lookup a StopId by its id string."""
        for s in self.iter_stops():
            si = s.stop_ids.get(stop_id)
            if si is not None:
                return si
        return None

    def get_stop_by_stopid(self, stop_id: str) -> Optional[Stop]:
        for s in self.iter_stops():
            if stop_id in s.stop_ids:
                return s
        return None

    def get_led_by_stopid(self, stop_id: str) -> Optional[LED]:
        st = self.get_stop_by_stopid(stop_id)
        return None if st is None else st.led

    # -- sACN helpers --
    def make_ledstrip(self) -> LedStrip:
        """Build a LedStrip over all LEDs referenced by the network."""
        return LedStrip(list(self.iter_leds()))

    def apply_route_defaults_to_leds(self) -> None:
        """Set each LED’s current color to its computed default."""
        for led in self.iter_leds():
            led.reset_to_default()


# ========= fader (animation engine for fades) =========

def ease_linear(t: float) -> float:
    return t

def ease_in_out_quad(t: float) -> float:
    return 2*t*t if t < 0.5 else 1 - ((-2*t + 2) ** 2) / 2

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
    """
    Drives per-LED fades. Call step() at your frame rate, then pack via strip.to_tuple().
    One active animation per LED index (new fades overwrite running ones for that LED).
    """
    def __init__(self, leds: List[LED]) -> None:
        self._anims: Dict[int, _Anim] = {}
        self._leds: Dict[int, LED] = {led.index: led for led in leds}

    def fade_led(self, index: int, to: RGB, duration: float = 0.5,
                 ease: Callable[[float], float] = ease_linear) -> None:
        led = self._leds[index]
        self._anims[index] = _Anim(
            led=led,
            start=(led.r, led.g, led.b),
            end=_rgb_clamp(to),
            t0=time.perf_counter(),
            dur=max(0.0, float(duration)),
            ease=ease
        )

    def fade_stop(self, stop: Stop, to: RGB, duration: float = 0.5,
                  ease: Callable[[float], float] = ease_linear) -> None:
        self.fade_led(stop.led.index, to, duration, ease)

    def fade_route(self, route: Route, to: RGB, duration: float = 0.5,
                   ease: Callable[[float], float] = ease_linear) -> None:
        for st in route.stops:
            self.fade_led(st.led.index, to, duration, ease)

    def fade_to_defaults(self, duration: float = 0.5,
                         ease: Callable[[float], float] = ease_linear) -> None:
        now = time.perf_counter()
        for led in self._leds.values():
            target = led.get_default_color()
            self._anims[led.index] = _Anim(
                led=led,
                start=(led.r, led.g, led.b),
                end=_rgb_clamp(target),
                t0=now,
                dur=max(0.0, float(duration)),
                ease=ease
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


# ========= convenience =========

def make_leds(n: int) -> List[LED]:
    """Create LEDs with indices 1..n."""
    return [LED(index=i) for i in range(1, n + 1)]
