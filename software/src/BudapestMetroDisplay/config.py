#  MIT License
#
#  Copyright (c) 2024 denes44
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
import logging
import sys
from typing import Optional

from pydantic import Field, field_validator, IPvAnyAddress, ValidationError
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class LEDConfig(BaseSettings):
    dim_ratio: float = Field(
        default=0.25,
        ge=0,
        le=1,
        description="Dim ratio for the background brightness of the LEDs (0 means totally off)",
    )
    fade_time: float = Field(
        default=1.0,
        gt=0,
        description="Fade time in seconds for the LED turn on and off action",
    )

    class Config:
        env_prefix = "LED_"  # Only load env variables starting with LED_
        frozen = True  # Make this settings class immutable


class SACNConfig(BaseSettings):
    multicast: bool = Field(
        default=True,
        description="Whether the sACN protocol should use multicast or unicast",
    )
    unicast_ip: Optional[IPvAnyAddress] = Field(
        default=None, description="The destination IP address for unicast sACN"
    )
    universe: int = Field(
        default=1,
        ge=1,
        lt=64000,
        description="DMX universe to send out data with the sACN protocol",
    )
    fps: int = Field(default=60, ge=1, description="Idle update frequency")

    @field_validator("unicast_ip")
    def check_unicast_ip(cls, value: IPvAnyAddress, info: ValidationInfo) -> IPvAnyAddress:
        if "multicast" in info.data and not info.data["multicast"] and value is None:
            raise ValueError("unicast_ip must be a valid IP address when using unicast")
        return value

    class Config:
        env_prefix = "SACN_"  # Only load env variables starting with SACN_
        frozen = True  # Make this settings class immutable


class BKKConfig(BaseSettings):
    api_key: str = Field(description="API key for the BKK OpenData portal")
    api_update_interval: int = Field(
        default=2, gt=0, description="Delay between consecutive API calls in seconds"
    )
    api_update_realtime: int = Field(
        default=60, gt=0, description="Update frequency for realtime data in seconds"
    )
    api_update_regular: int = Field(
        default=1800, gt=0, description="Update frequency for regular data in seconds"
    )
    api_update_alerts: int = Field(
        default=600,
        gt=0,
        description="Update frequency for alerts for non-realtime routes in seconds",
    )

    class Config:
        env_prefix = "BKK_"  # Only load env variables starting with BKK_
        frozen = True  # Make this settings class immutable


class ESPHomeConfig(BaseSettings):
    used: bool = Field(
        default=False,
        description="Whether to use brightness data from ESPHome to determine the minimum brightness",
    )
    device_ip: Optional[IPvAnyAddress] = Field(
        default=None, description="The IP address of the ESPHome device"
    )
    api_key: Optional[str] = Field(default=None, description="The API key of the ESPHome device")

    @field_validator("device_ip", "api_key")
    def check_unicast_ip(cls, value, info: ValidationInfo):
        if "used" in info.data and info.data["used"] and value is None:
            raise ValueError("Device IP and API key must be filled out when using ESPHome")
        return value

    class Config:
        env_prefix = "ESPHOME_"  # Only load env variables starting with LED_
        frozen = True  # Make this settings class immutable


class AppConfig(BaseSettings):
    try:
        led: LEDConfig = LEDConfig()
        sacn: SACNConfig = SACNConfig()
        bkk: BKKConfig = BKKConfig()
        esphome: ESPHomeConfig = ESPHomeConfig()
    except ValidationError as e:
        logger.error("Configuration Error: Please check your environment variables")
        logger.error(e)
        sys.exit(1)  # Exit the application with a non-zero status code

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", frozen=True
    )


settings = AppConfig()
