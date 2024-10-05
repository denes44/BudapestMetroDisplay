import pytest
import os

from pydantic import ValidationError

# Mock environment variables before importing the module
# LED Configuration
os.environ["LED_DIM_RATIO"] = "0.333"
os.environ["LED_FADE_TIME"] = "5.3"

# sACN Configuration
os.environ["SACN_MULTICAST"] = "False"
os.environ["SACN_UNICAST_IP"] = "192.168.1.1"
os.environ["SACN_UNIVERSE"] = "2"
os.environ["SACN_FPS"] = "15"

# BKK Configuration
os.environ["BKK_API_KEY"] = "test_api_key"
os.environ["BKK_API_UPDATE_INTERVAL"] = "6"
os.environ["BKK_API_UPDATE_REALTIME"] = "82"
os.environ["BKK_API_UPDATE_REGULAR"] = "3456"
os.environ["BKK_API_UPDATE_ALERTS"] = "123"

# ESPHome Configuration
os.environ["ESPHOME_USED"] = "True"
os.environ["ESPHOME_DEVICE_IP"] = "192.168.1.2"
os.environ["ESPHOME_API_KEY"] = "0LTLKmoTVR0BO3xppXQkIBVb0VzDLZFqAplYnADTbOY="

from src.BudapestMetroDisplay.config import AppConfig, LEDConfig, SACNConfig, BKKConfig, ESPHomeConfig


def test_app_config_initializes_correctly():
    config = AppConfig()
    # LED Configuration
    assert os.environ["LED_DIM_RATIO"] == "0.333"
    assert os.environ["LED_FADE_TIME"] == "5.3"

    # sACN Configuration
    assert os.environ["SACN_MULTICAST"] == "False"
    assert os.environ["SACN_UNICAST_IP"] == "192.168.1.1"
    assert os.environ["SACN_UNIVERSE"] == "2"
    assert os.environ["SACN_FPS"] == "15"

    # BKK Configuration
    assert os.environ["BKK_API_KEY"] == "test_api_key"
    assert os.environ["BKK_API_UPDATE_INTERVAL"] == "6"
    assert os.environ["BKK_API_UPDATE_REALTIME"] == "82"
    assert os.environ["BKK_API_UPDATE_REGULAR"] == "3456"
    assert os.environ["BKK_API_UPDATE_ALERTS"] == "123"

    # ESPHome Configuration
    assert os.environ["ESPHOME_USED"] == "True"
    assert os.environ["ESPHOME_DEVICE_IP"] == "192.168.1.2"
    assert os.environ["ESPHOME_API_KEY"] == "0LTLKmoTVR0BO3xppXQkIBVb0VzDLZFqAplYnADTbOY="

    # List of environment variable keys to delete
    env_vars = [
        "LED_DIM_RATIO", "LED_FADE_TIME",
        "SACN_MULTICAST", "SACN_UNICAST_IP", "SACN_UNIVERSE", "SACN_FPS",
        "BKK_API_KEY", "BKK_API_UPDATE_INTERVAL", "BKK_API_UPDATE_REALTIME", "BKK_API_UPDATE_REGULAR",
        "BKK_API_UPDATE_ALERTS",
        "ESPHOME_USED", "ESPHOME_DEVICE_IP", "ESPHOME_API_KEY"
    ]

    # Delete each environment variable
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]


def test_led_config_dim_ratio_within_bounds():
    config = LEDConfig(dim_ratio=0.5)
    assert config.dim_ratio == 0.5


def test_led_config_dim_ratio_out_of_bounds_positive():
    with pytest.raises(ValidationError):
        LEDConfig(dim_ratio=1.5)


def test_led_config_dim_ratio_out_of_bounds_negative():
    with pytest.raises(ValidationError):
        LEDConfig(dim_ratio=-2.5)


def test_led_config_fade_time_positive():
    config = LEDConfig(fade_time=2.0)
    assert config.fade_time == 2.0


def test_led_config_fade_time_zero():
    config = LEDConfig(fade_time=0.0)
    assert config.fade_time == 0.0


def test_led_config_fade_time_non_positive():
    with pytest.raises(ValidationError):
        LEDConfig(fade_time=-1.0)


def test_sacn_config_multicast_default():
    config = SACNConfig()
    assert config.multicast is True


def test_sacn_config_unicast_ip_required():
    with pytest.raises(ValidationError):
        SACNConfig(multicast=False, unicast_ip=None)


def test_sacn_config_unicast_ipv4():
    config = SACNConfig(multicast=False, unicast_ip="192.168.1.1")
    assert config.unicast_ip.__str__() == "192.168.1.1"


def test_sacn_config_unicast_ipv6():
    config = SACNConfig(multicast=False, unicast_ip="2001:0000:130F:0000:0000:09C0:876A:130B")
    assert config.unicast_ip.__str__() == "2001:0:130f::9c0:876a:130b"


def test_bkk_config_api_key_required_none():
    with pytest.raises(ValidationError):
        BKKConfig(api_key=None)


def test_bkk_config_api_key_required_empty():
    with pytest.raises(ValidationError):
        BKKConfig(api_key="")


def test_bkk_config_api_key_required():
    config = BKKConfig(api_key="sgd456-efe54g-s5f4ee")
    assert config.api_key == "sgd456-efe54g-s5f4ee"


def test_bkk_config_api_update_interval_positive():
    config = BKKConfig(api_key="sgd456-efe54g-s5f4ee", api_update_interval=5)
    assert config.api_update_interval == 5


def test_bkk_config_api_update_interval_out_of_bounds():
    with pytest.raises(ValidationError):
        BKKConfig(api_update_interval=-5)


def test_bkk_config_api_update_realtime_positive():
    config = BKKConfig(api_key="sgd456-efe54g-s5f4ee", api_update_realtime=5)
    assert config.api_update_realtime == 5


def test_bkk_config_api_update_realtime_out_of_bounds():
    with pytest.raises(ValidationError):
        BKKConfig(api_update_realtime=-5)


def test_bkk_config_api_update_regular_positive():
    config = BKKConfig(api_key="sgd456-efe54g-s5f4ee", api_update_regular=5)
    assert config.api_update_regular == 5


def test_bkk_config_api_update_regular_out_of_bounds():
    with pytest.raises(ValidationError):
        BKKConfig(api_update_regular=-5)


def test_bkk_config_api_update_alerts_positive():
    config = BKKConfig(api_key="sgd456-efe54g-s5f4ee", api_update_alerts=5)
    assert config.api_update_alerts == 5


def test_bkk_config_api_update_alerts_out_of_bounds():
    with pytest.raises(ValidationError):
        BKKConfig(api_update_alerts=-5)


def test_esphome_config_used_requires_ip():
    with pytest.raises(ValidationError):
        ESPHomeConfig(used=True, device_ip=None, api_key="test")


def test_esphome_config_used_requires_key():
    with pytest.raises(ValidationError):
        ESPHomeConfig(used=True, device_ip="192.168.1.1", api_key=None)


def test_esphome_config_used_requires_ip_and_key():
    with pytest.raises(ValidationError):
        ESPHomeConfig(used=True, device_ip=None, api_key=None)


def test_esphome_config_used_empty_api_key():
    with pytest.raises(ValidationError):
        ESPHomeConfig(used=True, device_ip="192.168.1.1", api_key="")


def test_esphome_config_used_ipv6():
    config = ESPHomeConfig(used=True, device_ip="2001:0000:130F:0000:0000:09C0:876A:130B", api_key="test")
    assert config.used is True
    assert config.device_ip.__str__() == "2001:0:130f::9c0:876a:130b"
    assert config.api_key == "test"


def test_esphome_config_not_used_allows_missing_ip_and_key():
    config = ESPHomeConfig(used=False)
    assert config.used is False
    assert config.device_ip is None
    assert config.api_key is None