#  MIT License
#
#  Copyright (c) 2024 denes44
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

# ruff: noqa: D103, ANN001, ANN202

import os
from unittest.mock import MagicMock, patch

import pytest

# Mock environment variables before importing the module
os.environ["BKK_API_KEY"] = "test_api_key"

from BudapestMetroDisplay import led_control


@pytest.fixture(autouse=True)
def mock_logger(monkeypatch) -> None:
    class MockLogger:
        def trace(self, message):
            pass

        def debug(self, message):
            pass

        def info(self, message):
            pass

        def warning(self, message):
            pass

        def error(self, message):
            pass

    mock_logger = MockLogger()
    monkeypatch.setattr("BudapestMetroDisplay.led_control.logger", mock_logger)


def test_activate_sacn() -> None:
    # Mock the sACNsender
    mock_sender = MagicMock()

    # Patch the sACNsender with the mock
    with patch(
        "BudapestMetroDisplay.led_control.sacn.sACNsender",
        return_value=mock_sender,
    ):
        # Call the function to test
        led_control.activate_sacn()

        # Verify that the sACNsender was started
        mock_sender.start.assert_called_once()
        # Verify that the output was activated
        mock_sender.activate_output.assert_called_once_with(
            led_control.settings.sacn.universe,
        )
        # Verify that the multicast setting was applied
        mock_sender.__getitem__.return_value.multicast = (
            led_control.settings.sacn.multicast
        )
        if not led_control.settings.sacn.multicast:
            # Verify that the destination was set if multicast is enabled
            mock_sender.__getitem__.return_value.destination = (
                led_control.settings.sacn.unicast_ip
            )


def test_deactivate_sacn() -> None:
    # Mock the sender
    mock_sender = MagicMock()

    # Patch the sender with the mock
    with patch("BudapestMetroDisplay.led_control.sender", mock_sender):
        # Call the function to test
        led_control.deactivate_sacn()

        # Verify that the stop method was called
        mock_sender.stop.assert_called_once()
