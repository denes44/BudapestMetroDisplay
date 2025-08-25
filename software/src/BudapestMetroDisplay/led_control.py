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

import inspect
import logging
import threading
import time
import uuid
from math import ceil
from threading import Lock

import sacn
from sacn import sACNsender

from BudapestMetroDisplay import stops
from BudapestMetroDisplay._version import __version__
from BudapestMetroDisplay.config import settings
from BudapestMetroDisplay.stops import common_stops

logger = logging.getLogger(__name__)

# The default LED color for the routes
ROUTE_COLORS: dict[str, tuple[int, int, int]] = {
    "BKK_5100": (255, 255, 0),  # M1
    "BKK_5200": (255, 0, 0),  # M2
    "BKK_5300": (0, 0, 255),  # M3
    "BKK_5400": (0, 255, 0),  # M4
    "BKK_H5": (255, 0, 255),  # H5
    "BKK_H6": (255, 0, 255),  # H6
    "BKK_H7": (255, 0, 255),  # H7
    "BKK_H8": (255, 0, 255),  # H8
    "BKK_H9": (255, 0, 255),  # H9
}

# The default dimmed LED color for the routes
ROUTE_COLORS_DIM: dict[str, tuple[int, int, int]] = {
    route: (
        int(color[0] * settings.led.dim_ratio),
        int(color[1] * settings.led.dim_ratio),
        int(color[2] * settings.led.dim_ratio),
    )
    for route, color in ROUTE_COLORS.items()
}
# Define default colors for each LED
DEFAULT_COLORS: list[tuple[int, int, int]] = [
    *([ROUTE_COLORS_DIM["BKK_H6"]] * 3),  # H6
    *([ROUTE_COLORS_DIM["BKK_H7"]] * 3),  # H7
    *([ROUTE_COLORS_DIM["BKK_5400"]] * 6),  # M4
    (
        0,
        int(255 * settings.led.dim_ratio),
        int(255 * settings.led.dim_ratio),
    ),  # M4/M3 Kálvin tér
    *([ROUTE_COLORS_DIM["BKK_5400"]] * 2),  # M4
    *([ROUTE_COLORS_DIM["BKK_5200"]] * 2),  # M2
    (
        int(255 * settings.led.dim_ratio),
        0,
        int(128 * settings.led.dim_ratio),
    ),  # M2/H5 Batthyány tér
    *([ROUTE_COLORS_DIM["BKK_5200"]] * 1),  # M2
    (
        int(255 * settings.led.dim_ratio),
        int(255 * settings.led.dim_ratio),
        int(255 * settings.led.dim_ratio),
    ),  # M1/M2/M3 Deák Ferenc tér
    *([ROUTE_COLORS_DIM["BKK_5200"]] * 2),  # M2
    (
        int(255 * settings.led.dim_ratio),
        int(128 * settings.led.dim_ratio),
        0,
    ),  # M2/M4 Keleti pályaudvar
    *([ROUTE_COLORS_DIM["BKK_5200"]] * 2),  # M2
    (
        int(255 * settings.led.dim_ratio),
        int(0 * settings.led.dim_ratio),
        int(48 * settings.led.dim_ratio),
    ),  # M2/H9 Örs vezér tere
    *([ROUTE_COLORS_DIM["BKK_H9"]] * 1),  # H9
    *([ROUTE_COLORS_DIM["BKK_H5"]] * 8),  # H5
    *([ROUTE_COLORS_DIM["BKK_5300"]] * 18),  # M3
    *([ROUTE_COLORS_DIM["BKK_5100"]] * 10),  # M1
]
DEFAULT_COLORS_ORIGINAL = list(DEFAULT_COLORS)

# Number of LEDs
NUM_LEDS: int = len(DEFAULT_COLORS)
# Initialize LED states with (0, 0, 0)
led_states: list[int] = [0, 0, 0] * NUM_LEDS
# Lock to synchronize access to LED states (led_states)
led_lock: Lock = threading.Lock()
# Initialize a dictionary of locks for each LED index
led_locks: dict[int, Lock] = {i: threading.Lock() for i in range(NUM_LEDS)}

# sACN sender interface
sender: sACNsender | None = None


def find_key_by_value(d: dict[str, int], target_value: int) -> str | None:
    """Find the supplied value (target_value) in the supplied dictionary.

    :param d: A dictionary to look for a value
    :param target_value: The value to look in the dictionary
    :return: Returns the key of the value if found, None otherwise
    """
    for key, value in d.items():
        if value == target_value:
            return key
    return None  # Return None if the value is not found


def find_keys_by_value(d: dict[str, int], target_value: int) -> list[str]:
    """Find all keys in the supplied dictionary that match the target_value.

    :param d: A dictionary to look for values
    :param target_value: The value to look for in the dictionary
    :return: A list of keys that match the value, or an empty list if none are found
    """
    return [key for key, value in d.items() if value == target_value]


def fade_color(
    led_index: int,
    current_color: tuple[int, int, int],
    target_color: tuple[int, int, int],
    steps: int = 100,
    delay: float = 0.05,
) -> None:
    """Fade from the current color to the target color of a specific LED.

    :param led_index: Index of the LED to update
    :param current_color: Tuple (r, g, b) representing the starting RGB color
    :param target_color: Tuple (r, g, b) representing the target RGB color
    :param steps: Number of steps in the fading process
    :param delay: Time to wait between each step in seconds
    """
    r1, g1, b1 = current_color
    r2, g2, b2 = target_color

    with led_locks[led_index]:  # Acquire the lock for the specific LED index
        for i in range(steps + 1):
            # Calculate the intermediate color
            r = int(r1 + (r2 - r1) * (i / steps))
            g = int(g1 + (g2 - g1) * (i / steps))
            b = int(b1 + (b2 - b1) * (i / steps))

            # Set the LED to the intermediate color
            with led_lock:
                led_states[led_index * 3 : led_index * 3 + 3] = [r, g, b]

            # Update the sACN values
            update_sacn()

            time.sleep(delay)

        # Ensure the final color is set correctly,
        # to avoid rounding errors dealing with floats
        with led_lock:
            led_states[led_index * 3 : led_index * 3 + 3] = [r2, g2, b2]
        update_sacn()


def calculate_default_color(led_index: int) -> None:
    """Recalculate the default LED colors.

    The method considers the active alerts for every stop,
    and calculates the default color of the stops according to the active routes.
    """
    # Check whether this LED belongs to multiple routes
    if led_index not in common_stops:
        # LED belongs to single route
        stop_ids: list[str] = [
            sid for sid, idx in stops.stops_led.items() if idx == led_index
        ]

        if all(stops.stop_no_service.get(sid, False) for sid in stop_ids):
            DEFAULT_COLORS[led_index] = (0, 0, 0)
        else:
            DEFAULT_COLORS[led_index] = DEFAULT_COLORS_ORIGINAL[led_index]
    else:
        # LED belongs to multiple routes
        route_status: dict[
            str,
            bool,
        ] = {}  # Status of each route for the specific stop/LED
        for route in common_stops[led_index]:
            route_id: str = route["route_id"]
            stop_ids = route["stop_ids"]

            # Check if all stops in the stop_ids list
            # have no service status for the current route
            if all(stops.stop_no_service.get(stop_id) for stop_id in stop_ids):
                route_status[route_id] = False
            else:
                route_status[route_id] = True

        # Determine the default color based on
        # which routes are operational at the specific stop/LED
        if led_index == 12:  # Kálvin tér: M3,M4
            if (
                route_status["BKK_5300"] and route_status["BKK_5400"]
            ):  # Both M3 and M4 are operational
                DEFAULT_COLORS[led_index] = (
                    0,
                    int(255 * settings.led.dim_ratio),
                    int(255 * settings.led.dim_ratio),
                )
            elif route_status["BKK_5300"]:  # Only M3 is operational
                DEFAULT_COLORS[led_index] = ROUTE_COLORS_DIM["BKK_5300"]
            elif route_status["BKK_5400"]:  # Only M4 is operational
                DEFAULT_COLORS[led_index] = ROUTE_COLORS_DIM["BKK_5400"]
            else:
                DEFAULT_COLORS[led_index] = (0, 0, 0)
        elif led_index == 17:  # Batthyány tér: M2,H5
            if (
                route_status["BKK_5200"] and route_status["BKK_H5"]
            ):  # Both M2 and H5 are operational
                DEFAULT_COLORS[led_index] = (
                    int(255 * settings.led.dim_ratio),
                    0,
                    int(128 * settings.led.dim_ratio),
                )
            elif route_status["BKK_5200"]:  # Only M2 is operational
                DEFAULT_COLORS[led_index] = ROUTE_COLORS_DIM["BKK_5200"]
            elif route_status["BKK_H5"]:  # Only H5 is operational
                DEFAULT_COLORS[led_index] = ROUTE_COLORS_DIM["BKK_H5"]
            else:
                DEFAULT_COLORS[led_index] = (0, 0, 0)
        elif led_index == 19:  # Deák Ferenc tér: M1,M2,M3
            r: int = 0
            g: int = 0
            b: int = 0

            if route_status["BKK_5100"]:  # M1 is operational
                r = int(255 * settings.led.dim_ratio)
                g = int(255 * settings.led.dim_ratio)
            if route_status["BKK_5200"]:  # M2 is operational
                r = int(255 * settings.led.dim_ratio)
            if route_status["BKK_5300"]:  # M3 is operational
                b = int(255 * settings.led.dim_ratio)

            DEFAULT_COLORS[led_index] = (r, g, b)
        elif led_index == 22:  # Keleti pályaudvar: M2,M4
            if (
                route_status["BKK_5200"] and route_status["BKK_5400"]
            ):  # Both M2 and M4 are operational
                DEFAULT_COLORS[led_index] = (
                    int(255 * settings.led.dim_ratio),
                    int(128 * settings.led.dim_ratio),
                    0,
                )
            elif route_status["BKK_5200"]:  # Only M2 is operational
                DEFAULT_COLORS[led_index] = ROUTE_COLORS_DIM["BKK_5200"]
            elif route_status["BKK_5400"]:  # Only M4 is operational
                DEFAULT_COLORS[led_index] = ROUTE_COLORS_DIM["BKK_5400"]
            else:
                DEFAULT_COLORS[led_index] = (0, 0, 0)
        elif led_index == 25:  # Örs vezér tere: M2,H8/9
            if (
                route_status["BKK_5200"] and route_status["BKK_H8"]
            ):  # Both M2 and H8 are operational
                DEFAULT_COLORS[led_index] = (
                    int(255 * settings.led.dim_ratio),
                    0,
                    int(48 * settings.led.dim_ratio),
                )
            elif route_status["BKK_5200"]:  # Only M2 is operational
                DEFAULT_COLORS[led_index] = ROUTE_COLORS_DIM["BKK_5200"]
            elif route_status["BKK_H8"]:  # Only H8 is operational
                DEFAULT_COLORS[led_index] = ROUTE_COLORS_DIM["BKK_H8"]
            else:
                DEFAULT_COLORS[led_index] = (0, 0, 0)


def reset_leds_to_default() -> None:
    """Reset the color of all LEDs to the default value."""
    global led_states
    with led_lock:
        led_states = [value for color in DEFAULT_COLORS for value in color]
    # Update the sACN values
    if sender is not None and len(sender.get_active_outputs()) == 1:
        update_sacn()
    logger.debug("All LEDs were reset to their default colors")


def reset_led_to_default(led_index: int, *, fade: bool = True) -> None:
    """Reset the color of a specific LED to the default value.

    :param led_index: The index of the LED
    :param fade: Whether to use fade or not
    """
    if 0 <= led_index < NUM_LEDS:
        if fade:
            with led_lock:
                # Get the current color
                current_color: tuple[int, int, int] = (
                    led_states[led_index * 3],  # Red component
                    led_states[led_index * 3 + 1],  # Green component
                    led_states[led_index * 3 + 2],  # Blue component
                )

            # Calculate fade parameters
            steps: int = int(settings.led.fade_time / 0.005)  # Number of steps
            delay: float = 0.005  # Time to wait between steps

            # Start the fading effect in a separate thread
            threading.Thread(
                target=fade_color,
                args=(
                    led_index,
                    current_color,
                    DEFAULT_COLORS[led_index],
                    steps,
                    delay,
                ),
            ).start()

            logger.trace(  # type: ignore[attr-defined]
                f"LED {led_index} fading from color {current_color!s} "
                f"to default color {DEFAULT_COLORS[led_index]!s}",
            )
        else:
            with led_lock:
                led_states[led_index * 3 : led_index * 3 + 3] = DEFAULT_COLORS[
                    led_index
                ]
            logger.trace(  # type: ignore[attr-defined]
                f"LED {led_index} set color "
                f"to default color {DEFAULT_COLORS[led_index]!s}",
            )
    else:
        logger.error(
            f"Invalid LED index {led_index} when trying to reset the value, "
            f"caller: {inspect.stack()[1].function}",
        )


def set_led_color(led_index: int, color: tuple[int, int, int]) -> None:
    """Reset the color of a specific LED to the supplied RGB tuple.

    :param led_index: The index of the LED
    :param color: A tuple (red, green, blue) representing the RGB values (0-255)
    """
    if 0 <= led_index < NUM_LEDS:
        with led_lock:
            # Get the current color
            current_color: tuple[int, int, int] = (
                led_states[led_index * 3],  # Red component
                led_states[led_index * 3 + 1],  # Green component
                led_states[led_index * 3 + 2],  # Blue component
            )
        # Check if the current color matches one of the ROUTE_COLORS
        if current_color in ROUTE_COLORS.values():
            # Combine the current color with the new color
            color = (
                min(color[0] + current_color[0], 255),
                min(color[1] + current_color[1], 255),
                min(color[2] + current_color[2], 255),
            )

        # Calculate fade parameters
        steps: int = int(settings.led.fade_time / 0.05)  # Number of steps
        delay: float = 0.05  # Time to wait between steps

        # Start the fading effect in a separate thread
        threading.Thread(
            target=fade_color,
            args=(led_index, current_color, color, steps, delay),
        ).start()

        logger.trace(  # type: ignore[attr-defined]
            f"LED {led_index} fading from color {current_color!s} to color {color!s}",
        )
    else:
        logger.error(
            f"Invalid LED index {led_index} when trying to change the value, "
            f"caller: {inspect.stack()[1].function}",
        )


def get_led_color(led_index: int) -> tuple[int, int, int] | None:
    """Retrieve the color of a specific LED as an RGB tuple.

    :param led_index: The index of the LED
    :return: A tuple (red, green, blue) representing the RGB values (0-255)
        or None if the led_index is invalid
    """
    if 0 <= led_index < NUM_LEDS:
        with led_lock:
            return (
                led_states[led_index * 3],
                led_states[led_index * 3 + 1],
                led_states[led_index * 3 + 2],
            )
    else:
        logger.error(
            f"Invalid LED index {led_index} when trying to get the value, "
            f"caller: {inspect.stack()[1].function}",
        )
        return None


def activate_sacn() -> None:
    """Start the sACN sender."""
    global sender
    sender = sacn.sACNsender(
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
    update_sacn()
    logger.info(
        f"sACN settings: "
        f"{'multicast' if sender[settings.sacn.universe].multicast else 'unicast'}, "
        f"destination ip: {sender[settings.sacn.universe].destination}",
    )


def deactivate_sacn() -> None:
    """Stop the sACN sender."""
    if sender is not None:
        sender.stop()


def update_sacn() -> None:
    """Update the internal tuple of the sACN to the latest values.

    Ensure each value is at least 28 when multiplied by esphome.brightness.
    """
    if sender is not None and sender[settings.sacn.universe].dmx_data is not None:
        if settings.esphome.used:
            from BudapestMetroDisplay.esphome import brightness

            # Create a new list with modified values
            modified_led_states: list[int] = [
                (
                    ceil(28 / brightness)
                    if value * brightness < 28 and value != 0
                    else value
                )
                for value in led_states
            ]

            # Convert the modified list to a tuple and assign it to dmx_data
            sender[settings.sacn.universe].dmx_data = tuple(modified_led_states)
        else:
            sender[settings.sacn.universe].dmx_data = tuple(led_states)
