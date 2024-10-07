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

import asyncio
import logging
import threading

from aioesphomeapi import (
    APIClient,
    APIConnectionError,
    ReconnectLogic,
    EntityState,
    LightState,
)

from BudapestMetroDisplay._version import __version__
from BudapestMetroDisplay.main import settings

logger = logging.getLogger(__name__)
brightness: float = 1.0

client: APIClient
entities = None


def on_state_change(state: EntityState):
    """Callback function that handles state changes."""
    global brightness

    # Check if this is a light entity
    if isinstance(state, LightState):
        brightness = state.brightness if hasattr(state, "brightness") else 1.0
        logger.debug(f"ESPHome Light brightness updated to {brightness * 100:.0f}%")


async def on_connect() -> None:
    try:
        # Subscribe to the state changes
        client.subscribe_states(on_state_change)
    except APIConnectionError as err:
        logger.error(
            f"Error getting initial data for {settings.esphome.device_ip}: {err}"
        )
        # Re-connection logic will trigger after this
        await client.disconnect()


async def on_disconnect(expected_disconnect) -> None:
    """Run disconnect stuff on API disconnect."""
    logger.info(f"Disconnected changed to '{expected_disconnect}'")


async def on_connect_error(err: Exception) -> None:
    """Show connection errors."""
    logger.error(f"Failed to connect with error '{err}'")


async def connect_and_subscribe():
    """Connect to the ESPHome device and subscribe to state changes."""
    global client, entities

    client = APIClient(
        settings.esphome.device_ip.__str__(),
        6053,
        None,
        noise_psk=settings.esphome.api_key,
        client_info=f"BudapestMetroDisplay {__version__}",
    )

    # Build reconnect logic
    reconnect_logic = ReconnectLogic(
        client=client,
        on_connect=on_connect,
        on_disconnect=on_disconnect,
        zeroconf_instance=None,
        name="ESPHome",
        on_connect_error=on_connect_error,
    )

    await reconnect_logic.start()


def esphome_background_process(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def start_background_loop():
    loop = asyncio.new_event_loop()
    threading.Thread(
        target=esphome_background_process, args=(loop,), daemon=True, name="ESPHome"
    ).start()
    return loop
