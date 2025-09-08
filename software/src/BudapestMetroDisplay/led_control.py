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
import uuid
from math import ceil

from sacn import sACNsender

from BudapestMetroDisplay._version import __version__
from BudapestMetroDisplay.config import settings

logger = logging.getLogger(__name__)

# sACN sender interface
sender: sACNsender | None = None


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
