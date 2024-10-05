import threading
from unittest.mock import MagicMock, patch

import pytest, os

# Mock environment variables before importing the module
os.environ["BKK_API_KEY"] = "test_api_key"

from BudapestMetroDisplay import led_control


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

    monkeypatch.setattr("BudapestMetroDisplay.led_control.update_sacn", mock_update_sacn)
    led_control.fade_color(led_index, current_color, target_color, steps, delay)
    assert led_control.led_states[led_index * 3: led_index * 3 + 3] == list(target_color)


def test_reset_leds_to_default_sets_all_leds_correctly():
    # Change color of one LED to check if it is reset
    led_index = 4
    led_control.led_states[led_index * 3: led_index * 3 + 3] = (255, 255, 255)

    # Reset all LEDs
    led_control.reset_leds_to_default()
    # Check if all LEDs are reset to default color
    assert led_control.led_states == [value for color in led_control.DEFAULT_COLORS for value in color]


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
    assert led_control.led_states[led_index * 3: led_index * 3 + 3] == list(target_color)


def test_reset_led_to_default_sets_specific_led_correctly_with_alert(monkeypatch):
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
    led_control.stops.stop_no_service["BKK_056215"] = True
    led_control.stops.stop_no_service["BKK_056216"] = True
    # Reset the LED
    led_control.reset_led_to_default(led_index)
    # Wait for the fade to finish
    event.wait(timeout=1)
    # Check if the LED is reset to default color
    assert led_control.led_states[led_index * 3: led_index * 3 + 3] == [0, 0, 0]


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
    assert led_control.led_states[led_index * 3: led_index * 3 + 3] == list(target_color)


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
    assert led_control.led_states[led_index * 3: led_index * 3 + 3] == list(expected_color)


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
    assert led_control.led_states[led_index * 3: led_index * 3 + 3] == list(expected_color)


def test_get_led_color_returns_correct_color():
    led_index = 4
    expected_color = (100, 100, 100)
    led_control.led_states[led_index * 3: led_index * 3 + 3] = expected_color
    assert led_control.get_led_color(led_index) == expected_color


def test_get_led_color_returns_none_for_invalid_index():
    assert led_control.get_led_color(-1) is None
    assert led_control.get_led_color(led_control.NUM_LEDS) is None


def test_update_sacn():
    # Mock the sACNsender and its universe
    mock_sender = MagicMock()
    mock_universe = MagicMock()
    mock_sender.__getitem__.return_value = mock_universe

    # Patch the sender with the mock
    with patch('BudapestMetroDisplay.led_control.sender', mock_sender):
        # Set the led_states to a known value
        led_control.led_states[:] = [10, 20, 30] * (len(led_control.led_states) // 3)
        expected_dmx_data = tuple(led_control.led_states)

        # Call the function to test
        led_control.update_sacn()

        # Verify that the dmx_data was updated correctly
        mock_universe.dmx_data = expected_dmx_data
        mock_sender.__getitem__.assert_called_with(led_control.settings.sacn.universe)
        assert mock_universe.dmx_data == expected_dmx_data


def test_update_sacn_esphome(monkeypatch):
    # Mock the sACNsender and its universe
    mock_sender = MagicMock()
    mock_universe = MagicMock()
    mock_sender.__getitem__.return_value = mock_universe

    # Patch the sender with the mock
    with patch('BudapestMetroDisplay.led_control.sender', mock_sender):
        # Mock esphome.used as True and brightness value
        with patch.dict('BudapestMetroDisplay.led_control.settings.esphome.__dict__', {'used': True}), \
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
            mock_sender.__getitem__.assert_called_with(led_control.settings.sacn.universe)
            assert mock_universe.dmx_data == expected_dmx_data
