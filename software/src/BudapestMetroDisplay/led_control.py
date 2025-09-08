#  MIT License
#
#  Copyright (c) 2024 [fullname]
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom
#  the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.

import logging
import threading
import time as _t
import uuid
from collections.abc import Callable
from math import ceil

from sacn import sACNsender

from BudapestMetroDisplay._version import __version__
from BudapestMetroDisplay.config import settings
from BudapestMetroDisplay.model import LedStrip
from BudapestMetroDisplay.network import led_strip

logger = logging.getLogger(__name__)

# sACN sender interface
sender: sACNsender


def start_renderer(stop_event: threading.Event | None = None) -> None:
    """Start the rendering loop in a separate thread."""
    # Set the LEDs to their initial target color.
    for led in led_strip.leds:
        led.set_rgb(led.target_color[0], led.target_color[1], led.target_color[2])

    # Start the renderer in a separate thread.
    thread = threading.Thread(
        target=run_renderer,
        kwargs={
            "strip": led_strip,
            "set_dmx": update_sacn,
            "stop_event": stop_event,
        },
        daemon=True,
        name="Renderer thread",
    )
    thread.start()


def run_renderer(
    strip: LedStrip,
    set_dmx: Callable[
        [tuple[int, ...]],
        None,
    ],  # Callback that sends the DMX tuple to your sACN sender
    stop_event: threading.Event
    | None = None,  # Optional cooperative stop flag for clean shutdown
) -> None:
    """Run the main render loop for updating the LEDs.

    Each frame (at settings.sacn.fps):
      1) Step the animations (updates LED.r/g/b to their in-between colors)
      2) Pack LEDs into a DMX tuple (strip.to_tuple) and send via set_dmx(...)
      3) Sleep just enough to maintain the target frame rate (frame pacing)
    """
    logger.info("LED renderer thread started")

    # Convert FPS to a frame duration in seconds (guard against 0 or negative).
    frame = 1.0 / max(1, int(settings.sacn.fps))

    # Anchor a monotonic "next frame" timestamp; using monotonic avoids time jumps.
    next_tick = _t.perf_counter()

    # Infinite loop until you signal stop_event (or kill the thread/process).
    while True:
        # If a stop flag is provided and set, exit gracefully.
        if stop_event is not None and stop_event.is_set():
            break

        # 1) Advance all animations to NOW (writes LED.r/g/b with the mid-fade color)
        strip.step()

        # 2) Pack the current LED colors into the exact DMX ordering and send it
        payload = strip.to_tuple()  # (led1_r, led1_g, led1_b, led2_r, ...)
        set_dmx(payload)  # You implement this to push into your sACN sender

        # 3) Frame pacing to hit the requested FPS (simple fixed-step scheduler)
        next_tick += frame  # Schedule the ideal time of the next frame
        sleep_for = (
            next_tick - _t.perf_counter()
        )  # Sleep for the remaining time in the frame
        if sleep_for > 0:
            _t.sleep(sleep_for)  # Sleep the remaining budget
        else:
            # If we're late (negative budget), skip sleeping and re-anchor to NOW
            # so we don't drift further behind in future frames.
            next_tick = _t.perf_counter()


def activate_sacn() -> None:
    """Start the sACN sender."""
    global sender
    sender = sACNsender(
        source_name=f"BudapestMetroDisplay {__version__}",
        cid=tuple(
            uuid.uuid5(
                uuid.UUID("12345678-1234-5678-1234-567812345678"),
                "BudapestMetroDisplay",
            ).bytes,
        ),
        fps=settings.sacn.fps,
    )
    sender.start()

    sender.activate_output(settings.sacn.universe)
    sender[settings.sacn.universe].multicast = settings.sacn.multicast
    if not settings.sacn.multicast:
        sender[settings.sacn.universe].destination = str(settings.sacn.unicast_ip)

    logger.info(
        f"sACN settings: "
        f"{'multicast' if sender[settings.sacn.universe].multicast else 'unicast'}, "
        f"destination ip: {sender[settings.sacn.universe].destination}",
    )


def deactivate_sacn() -> None:
    """Stop the sACN sender."""
    if sender is not None:
        sender.stop()


def update_sacn(payload: tuple[int, ...]) -> None:
    """Update the internal tuple of the sACN to the latest values.

    Ensure each value is at least 28 when multiplied by esphome.brightness.
    """
    if sender is not None and sender[settings.sacn.universe].dmx_data is not None:
        if settings.esphome.used:
            from BudapestMetroDisplay.esphome import brightness

            # Create a new list with modified values
            modified_payload: list[int] = [
                (
                    ceil(28 / brightness)
                    if value * brightness < 28 and value != 0
                    else value
                )
                for value in payload
            ]

            # Convert the modified list to a tuple and assign it to dmx_data
            sender[settings.sacn.universe].dmx_data = tuple(modified_payload)
        else:
            sender[settings.sacn.universe].dmx_data = tuple(payload)
