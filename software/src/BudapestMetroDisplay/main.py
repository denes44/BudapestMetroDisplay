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

import argparse
import asyncio
from asyncio import AbstractEventLoop
import logging
import signal
import sys
import time

from BudapestMetroDisplay.config import settings
from BudapestMetroDisplay import bkk_opendata
from BudapestMetroDisplay import led_control
from BudapestMetroDisplay import log
from BudapestMetroDisplay import webserver
from BudapestMetroDisplay._version import __version__
from BudapestMetroDisplay.stops import stops_metro, stops_railway, alert_routes

if settings.esphome.used:
    from BudapestMetroDisplay.esphome import start_background_loop, \
        connect_and_subscribe

logger = logging.getLogger(__name__)

parser = None
loop: AbstractEventLoop


def handle_exit_signal(signum, frame):
    """Handle signals for a clean exit."""
    logger.info("Signal received, stopping threads...")
    bkk_opendata.departure_scheduler.shutdown()
    logger.debug("Departure scheduler shut down")
    bkk_opendata.led_scheduler.shutdown(wait=False)
    logger.debug("LED scheduler shut down")
    bkk_opendata.api_update_scheduler.shutdown(wait=False)
    logger.debug("API Update scheduler shut down")
    led_control.deactivate_sacn()
    logger.debug("sACN update thread shut down")
    if settings.esphome.used:
        loop.stop()
        logger.debug("ESPHome update thread shut down")
    logger.info("Cleanup complete. Exiting...")
    exit(0)


# Set the global exception hook
sys.excepthook = log.log_exception


def main():
    global parser, loop

    if settings.esphome.used:
        loop = start_background_loop()
        loop.call_soon_threadsafe(asyncio.create_task, connect_and_subscribe())

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Run the BKK Opendata and LED Control Program."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode for verbose output."
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Enable trace mode for verbose output."
    )

    # Set up logging with or without debug mode
    log.setup_logging(parser)
    logger.info(f"Program started, version {__version__}")

    # Register the exit handler for signals (e.g., Ctrl+C)
    signal.signal(signal.SIGINT, handle_exit_signal)
    signal.signal(signal.SIGTERM, handle_exit_signal)

    # Create schedules for updating the departures data
    bkk_opendata.create_schedule_updates(stops_metro, "REGULAR")
    bkk_opendata.create_schedule_updates(stops_railway, "REGULAR")
    # Create schedules for updating the realtime data
    bkk_opendata.create_schedule_updates(stops_railway, "REALTIME")
    # Create schedules for updating the alarm data for non-realtime stops
    bkk_opendata.create_alert_updates(alert_routes)

    # Start the sACN sending routine with continuous updates
    led_control.reset_leds_to_default()
    # Start sending LED data via sACN
    led_control.activate_sacn()

    webserver.start_webserver()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
