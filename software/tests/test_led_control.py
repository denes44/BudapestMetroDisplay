import os
import threading
from unittest.mock import MagicMock, patch

import pytest

# Mock environment variables before importing the module
os.environ["BKK_API_KEY"] = "test_api_key"

from BudapestMetroDisplay.main import settings  # noqa: E402
from BudapestMetroDisplay import led_control  # noqa: E402
from BudapestMetroDisplay import stops  # noqa: E402


@pytest.fixture(autouse=True)
def mock_logger(monkeypatch):
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


def test_find_key_by_value_returns_correct_key():
    d = {"a": 1, "b": 2, "c": 3}
    assert led_control.find_key_by_value(d, 2) == "b"


def test_find_key_by_value_returns_none_for_missing_value():
    d = {"a": 1, "b": 2, "c": 3}
    assert led_control.find_key_by_value(d, 4) is None


def test_find_keys_by_value_returns_correct_keys():
    d = {"a": 1, "b": 2, "c": 1}
    assert led_control.find_keys_by_value(d, 1) == ["a", "c"]


def test_find_keys_by_value_returns_empty_list_for_missing_value():
    d = {"a": 1, "b": 2, "c": 3}
    assert led_control.find_keys_by_value(d, 4) == []


def test_fade_color_fades_correctly(monkeypatch):
    led_index = 4
    current_color = (0, 0, 0)
    target_color = (255, 129, 63)
    steps = 10
    delay = 0.01

    def mock_update_sacn():
        pass

    monkeypatch.setattr("BudapestMetroDisplay.led_control.update_sacn",
                        mock_update_sacn)
    led_control.fade_color(led_index, current_color, target_color, steps, delay)
    assert led_control.led_states[led_index * 3: led_index * 3 + 3] == list(
        target_color)


def test_reset_leds_to_default_sets_all_leds_correctly():
    # Change color of one LED to check if it is reset
    led_index = 4
    led_control.led_states[led_index * 3: led_index * 3 + 3] = (255, 255, 255)

    # Reset all LEDs
    led_control.reset_leds_to_default()
    # Check if all LEDs are reset to default color
    assert led_control.led_states == [value for color in led_control.DEFAULT_COLORS for
                                      value in color]


def test_reset_led_to_default_sets_specific_led_correctly(monkeypatch):
    # Change color of one LED to check if it is reset
    led_index = 4
    target_color = led_control.DEFAULT_COLORS[led_index]
    event = threading.Event()

    # Mock the fade_color function to set the target color directly
    def mock_fade_color(_led_index, _current_color, _target_color, _steps, _delay):
        led_control.led_states[_led_index * 3: _led_index * 3 + 3] = _target_color
        event.set()

    monkeypatch.setattr("BudapestMetroDisplay.led_control.fade_color", mock_fade_color)

    # Change color of the LED
    led_control.led_states[led_index * 3: led_index * 3 + 3] = (255, 255, 255)
    # Reset the LED
    led_control.reset_led_to_default(led_index)
    # Wait for the fade to finish
    event.wait(timeout=1)
    # Check if the LED is reset to default color
    assert led_control.led_states[led_index * 3: led_index * 3 + 3] == list(
        target_color)


def test_reset_led_to_default_sets_specific_led_correctly_with_no_alert(monkeypatch):
    # Change color of one LED to check if it is reset
    led_index = 6
    target_color = led_control.DEFAULT_COLORS[led_index]
    event = threading.Event()

    # Mock the fade_color function to set the target color directly
    def mock_fade_color(_led_index, _current_color, _target_color, _steps, _delay):
        led_control.led_states[_led_index * 3: _led_index * 3 + 3] = _target_color
        event.set()

    monkeypatch.setattr("BudapestMetroDisplay.led_control.fade_color", mock_fade_color)

    # Change color of the LED
    led_control.led_states[led_index * 3: led_index * 3 + 3] = (255, 255, 255)
    # Set alerts for the stopIds of this LED
    led_control.stops.stop_no_service["BKK_056215"] = False
    led_control.stops.stop_no_service["BKK_056216"] = True
    # Reset the LED
    led_control.reset_led_to_default(led_index)
    # Wait for the fade to finish
    event.wait(timeout=1)
    # Check if the LED is reset to default color
    assert led_control.led_states[led_index * 3: led_index * 3 + 3] == list(
        target_color)


def test_set_led_color_sets_color_correctly(monkeypatch):
    # Set the new color for the LED
    led_index = 4
    new_color = (0, 255, 0)
    event = threading.Event()

    # Mock the fade_color function to set the target color directly
    def mock_fade_color(_led_index, _current_color, _target_color, _steps, _delay):
        led_control.led_states[_led_index * 3: _led_index * 3 + 3] = _target_color
        event.set()

    monkeypatch.setattr("BudapestMetroDisplay.led_control.fade_color", mock_fade_color)
    # Set the new color
    led_control.set_led_color(led_index, new_color)
    # Wait for the fade to finish
    event.wait(timeout=1)
    # Check if the LED is set to the new color
    assert led_control.led_states[led_index * 3: led_index * 3 + 3] == list(new_color)


def test_set_led_color_combines_colors_correctly(monkeypatch):
    # Set the new color for the LED
    led_index = 4
    current_color = led_control.ROUTE_COLORS["BKK_5200"]
    new_color = led_control.ROUTE_COLORS["BKK_5300"]
    expected_color = (255, 0, 255)
    event = threading.Event()

    # Mock the fade_color function to set the target color directly
    def mock_fade_color(_led_index, _current_color, _target_color, _steps, _delay):
        led_control.led_states[_led_index * 3: _led_index * 3 + 3] = _target_color
        event.set()

    monkeypatch.setattr("BudapestMetroDisplay.led_control.fade_color", mock_fade_color)
    # Set the LED color
    led_control.led_states[led_index * 3: led_index * 3 + 3] = current_color
    # Set the LED to the new color
    led_control.set_led_color(led_index, new_color)
    # Wait for the fade to finish
    event.wait(timeout=1)
    # Check if the LED is set to the new color combined with the current color
    assert led_control.led_states[led_index * 3: led_index * 3 + 3] == list(
        expected_color)


def test_set_led_color_does_not_combine_colors(monkeypatch):
    # Set the new color for the LED
    led_index = 4
    current_color = led_control.ROUTE_COLORS_DIM["BKK_5200"]
    new_color = led_control.ROUTE_COLORS["BKK_5300"]
    expected_color = led_control.ROUTE_COLORS["BKK_5300"]
    event = threading.Event()

    # Mock the fade_color function to set the target color directly
    def mock_fade_color(_led_index, _current_color, _target_color, _steps, _delay):
        led_control.led_states[_led_index * 3: _led_index * 3 + 3] = _target_color
        event.set()

    monkeypatch.setattr("BudapestMetroDisplay.led_control.fade_color", mock_fade_color)
    # Set the LED color
    led_control.led_states[led_index * 3: led_index * 3 + 3] = current_color
    # Set the LED to the new color
    led_control.set_led_color(led_index, new_color)
    # Wait for the fade to finish
    event.wait(timeout=1)
    # Check if the LED is set to the new color combined with the current color
    assert led_control.led_states[led_index * 3: led_index * 3 + 3] == list(
        expected_color)


def test_get_led_color_returns_correct_color():
    led_index = 4
    expected_color = (100, 100, 100)
    led_control.led_states[led_index * 3: led_index * 3 + 3] = expected_color
    assert led_control.get_led_color(led_index) == expected_color


def test_get_led_color_returns_none_for_invalid_index():
    assert led_control.get_led_color(-1) is None
    assert led_control.get_led_color(led_control.NUM_LEDS) is None


def test_activate_sacn():
    # Mock the sACNsender
    mock_sender = MagicMock()

    # Patch the sACNsender with the mock
    with (patch('BudapestMetroDisplay.led_control.sacn.sACNsender',
                return_value=mock_sender)):
        # Call the function to test
        led_control.activate_sacn()

        # Verify that the sACNsender was started
        mock_sender.start.assert_called_once()
        # Verify that the output was activated
        mock_sender.activate_output.assert_called_once_with(
            led_control.settings.sacn.universe)
        # Verify that the multicast setting was applied
        mock_sender.__getitem__.return_value.multicast = \
            led_control.settings.sacn.multicast
        if not led_control.settings.sacn.multicast:
            # Verify that the destination was set if multicast is enabled
            mock_sender.__getitem__.return_value.destination = \
                led_control.settings.sacn.unicast_ip


def test_deactivate_sacn():
    # Mock the sender
    mock_sender = MagicMock()

    # Patch the sender with the mock
    with patch('BudapestMetroDisplay.led_control.sender', mock_sender):
        # Call the function to test
        led_control.deactivate_sacn()

        # Verify that the stop method was called
        mock_sender.stop.assert_called_once()


def test_update_sacn():
    # Mock the sACNsender and its universe
    mock_sender = MagicMock()
    mock_universe = MagicMock()
    mock_sender.__getitem__.return_value = mock_universe

    # Patch the sender with the mock
    # Patch the sender with the mock
    with patch('BudapestMetroDisplay.led_control.sender', mock_sender):
        # Mock esphome.used as True and brightness value
        with patch.dict('BudapestMetroDisplay.led_control.settings.esphome.__dict__',
                        {'used': False}):
            # Set the led_states to a known value
            led_control.led_states[:] = [10, 20, 30] * (
                    len(led_control.led_states) // 3)
            expected_dmx_data = tuple(led_control.led_states)

            # Call the function to test
            led_control.update_sacn()

            # Verify that the dmx_data was updated correctly
            mock_universe.dmx_data = expected_dmx_data
            mock_sender.__getitem__.assert_called_with(
                led_control.settings.sacn.universe)
            assert mock_universe.dmx_data == expected_dmx_data


def test_update_sacn_esphome(monkeypatch):
    # Mock the sACNsender and its universe
    mock_sender = MagicMock()
    mock_universe = MagicMock()
    mock_sender.__getitem__.return_value = mock_universe

    # Patch the sender with the mock
    with patch('BudapestMetroDisplay.led_control.sender', mock_sender):
        # Mock esphome.used as True and brightness value
        with patch.dict('BudapestMetroDisplay.led_control.settings.esphome.__dict__',
                        {'used': True}), \
                patch('BudapestMetroDisplay.esphome.brightness', 0.66):
            # Set the led_states to a known value
            led_control.led_states = [0, 0, 0] * led_control.NUM_LEDS
            # Set the first 3 LEDs to the expected result
            led_control.led_states[0:3] = [169, 85, 43]
            expected_dmx_data = tuple(led_control.led_states)
            # Set the first 3 LEDs to the starting value
            led_control.led_states[0:3] = [255, 128, 64]

            # Call the function to test
            led_control.update_sacn()

            # Verify that the dmx_data was updated correctly
            mock_universe.dmx_data = expected_dmx_data
            mock_sender.__getitem__.assert_called_with(
                led_control.settings.sacn.universe)
            assert mock_universe.dmx_data == expected_dmx_data


def test_calculate_default_color_led12():
    led_test = 12  # Kálvin tér
    # Initialize the route status dictionary
    stops.stop_no_service = {stop_id: False for stop_id in stops.stops_led}
    led_control.calculate_default_color(led_test)
    assert led_control.DEFAULT_COLORS[led_test] == (
        0, int(255 * settings.led.dim_ratio), int(255 * settings.led.dim_ratio))
    # Set the NO_SERVICE status for one direction of Kálvin tér M4
    stops.stop_no_service["BKK_056227"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == (
        0, int(255 * settings.led.dim_ratio), int(255 * settings.led.dim_ratio))
    # Set the NO_SERVICE status for the other direction of Kálvin tér M4
    stops.stop_no_service["BKK_056228"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_5300"]
    # Set the NO_SERVICE status for one direction of Kálvin tér M3
    stops.stop_no_service["BKK_F01290"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_5300"]
    # Set the NO_SERVICE status for one direction of Kálvin tér M3
    stops.stop_no_service["BKK_F01289"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == (0, 0, 0)
    # Clear the NO_SERVICE status for one direction of Kálvin tér M4
    stops.stop_no_service["BKK_056227"] = False
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_5400"]


def test_calculate_default_color_led17():
    led_test = 17
    # Initialize the route status dictionary
    stops.stop_no_service = {stop_id: False for stop_id in stops.stops_led}
    led_control.calculate_default_color(led_test)
    assert led_control.DEFAULT_COLORS[led_test] == (
        int(255 * settings.led.dim_ratio), 0, int(128 * settings.led.dim_ratio))
    # Set the NO_SERVICE status for one direction of Batthyányi tér M2
    stops.stop_no_service["BKK_F00063"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == (
        int(255 * settings.led.dim_ratio), 0, int(128 * settings.led.dim_ratio))
    # Set the NO_SERVICE status for second direction of Batthyányi tér M2
    stops.stop_no_service["BKK_F00062"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_H5"]
    # Set the NO_SERVICE status for one direction of Batthyányi tér H5
    stops.stop_no_service["BKK_09001187"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_H5"]
    # Set the NO_SERVICE status for second direction of Batthyányi tér H5
    stops.stop_no_service["BKK_09001188"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_H5"]
    # Set the NO_SERVICE status for third direction of Batthyányi tér H5
    stops.stop_no_service["BKK_09001189"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == (0, 0, 0)
    # Clear the NO_SERVICE status for second direction of Batthyányi tér M2
    stops.stop_no_service["BKK_F00062"] = False
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_5200"]


def test_calculate_default_color_led22():
    led_test = 22  # Keleti pályaudvar
    # Initialize the route status dictionary
    stops.stop_no_service = {stop_id: False for stop_id in stops.stops_led}
    led_control.calculate_default_color(led_test)
    assert led_control.DEFAULT_COLORS[led_test] == (
        int(255 * settings.led.dim_ratio), int(128 * settings.led.dim_ratio), 0)
    # Set the NO_SERVICE status for one direction of Keleti pályaudvar M4
    stops.stop_no_service["BKK_056233"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == (
        int(255 * settings.led.dim_ratio), int(128 * settings.led.dim_ratio), 0)
    # Set the NO_SERVICE status for second direction of Keleti pályaudvar M4
    stops.stop_no_service["BKK_056234"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_5200"]
    # Set the NO_SERVICE status for one direction of Keleti pályaudvar M3
    stops.stop_no_service["BKK_F01336"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_5200"]
    # Set the NO_SERVICE status for second direction of Keleti pályaudvar M3
    stops.stop_no_service["BKK_F01335"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == (0, 0, 0)
    # Clear the NO_SERVICE status for second direction of Keleti pályaudvar M4
    stops.stop_no_service["BKK_056234"] = False
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_5400"]


def test_calculate_default_color_led25():
    led_test = 25  # Örs vezér tere
    # Initialize the route status dictionary
    stops.stop_no_service = {stop_id: False for stop_id in stops.stops_led}
    led_control.calculate_default_color(led_test)
    assert led_control.DEFAULT_COLORS[led_test] == (
        int(255 * settings.led.dim_ratio), 0, int(48 * settings.led.dim_ratio))
    # Set the NO_SERVICE status for one direction of Örs vezér tere M2
    stops.stop_no_service["BKK_F01749"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_H8"]
    # Set the NO_SERVICE status for one direction of Örs vezér tere H8
    stops.stop_no_service["BKK_19795278"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_H8"]
    # Set the NO_SERVICE status for second direction of Örs vezér tere H8
    stops.stop_no_service["BKK_19795279"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_H8"]
    # Set the NO_SERVICE status for third direction of Örs vezér tere H8
    stops.stop_no_service["BKK_19795280"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == (0, 0, 0)
    # Clear the NO_SERVICE status for one direction of Örs vezér tere M2
    stops.stop_no_service["BKK_F01749"] = False
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == led_control.ROUTE_COLORS_DIM[
        "BKK_5200"]


def test_calculate_default_color_led19():
    led_test = 19  # Deák Ferenc tér
    # Initialize the route status dictionary
    stops.stop_no_service = {stop_id: False for stop_id in stops.stops_led}
    led_control.calculate_default_color(led_test)
    assert led_control.DEFAULT_COLORS[led_test] == (
        int(255 * settings.led.dim_ratio), int(255 * settings.led.dim_ratio),
        int(255 * settings.led.dim_ratio))
    # Set the NO_SERVICE status for one direction of Deák Ferenc tér M1
    stops.stop_no_service["BKK_F00963"] = True
    assert led_control.DEFAULT_COLORS[led_test] == (
        int(255 * settings.led.dim_ratio), int(255 * settings.led.dim_ratio),
        int(255 * settings.led.dim_ratio))
    # Set the NO_SERVICE status for second direction of Deák Ferenc tér M1
    stops.stop_no_service["BKK_F00962"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == (
        int(255 * settings.led.dim_ratio), 0, int(255 * settings.led.dim_ratio))
    # Set the NO_SERVICE status for one direction of Örs vezér tere M2
    stops.stop_no_service["BKK_F00961"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == (
        int(255 * settings.led.dim_ratio), 0, int(255 * settings.led.dim_ratio))
    # Set the NO_SERVICE status for second direction of Örs vezér tere M2
    stops.stop_no_service["BKK_F00960"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == (
        0, 0, int(255 * settings.led.dim_ratio))
    # Set the NO_SERVICE status for one direction of Örs vezér tere M3
    stops.stop_no_service["BKK_F00955"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == (
        0, 0, int(255 * settings.led.dim_ratio))
    # Set the NO_SERVICE status for second direction of Örs vezér tere M2
    stops.stop_no_service["BKK_F00954"] = True
    led_control.calculate_default_color(led_test)
    led_control.reset_leds_to_default()
    assert led_control.DEFAULT_COLORS[led_test] == (0, 0, 0)
