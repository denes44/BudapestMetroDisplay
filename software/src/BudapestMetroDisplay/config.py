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
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Union

from pydantic import Field, validator

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    unicast_ip: Union[IPv4Address, IPv6Address] = Field(
        default="127.0.0.1", description="The destination IP address for unicast sACN"
    )
    universe: int = Field(
        default=1,
        ge=1,
        lt=64000,
        description="DMX universe to send out data with the sACN protocol",
    )
    fps: int = Field(default=60, ge=1, description="Idle update frequency")

    @validator("unicast_ip", pre=True)
    def validate_ip(cls, value):
        return ip_address(value)

    @validator("unicast_ip")
    def check_unicast_ip(cls, value, values):
        if not values.get("multicast") and not value:
            raise ValueError("unicast_ip must be a valid IP address when using unicast")
        return value

    class Config:
        env_prefix = "SACN_"  # Only load env variables starting with SACN_
        frozen = True  # Make this settings class immutable


class BKKConfig(BaseSettings):
    api_key: str = Field(default="", description="API key for the BKK OpenData portal")
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
    device_ip: Union[IPv4Address, IPv6Address] = Field(
        default="127.0.0.1", description="The IP address of the ESPHome device"
    )
    api_key: str = Field(default="", description="The API key of the ESPHome device")

    @validator("device_ip", pre=True)
    def validate_ip(cls, value):
        return ip_address(value)

    class Config:
        env_prefix = "ESPHOME_"  # Only load env variables starting with LED_
        frozen = True  # Make this settings class immutable


class AppConfig(BaseSettings):
    led: LEDConfig = LEDConfig()
    sacn: SACNConfig = SACNConfig()
    bkk: BKKConfig = BKKConfig()
    esphome: ESPHomeConfig = ESPHomeConfig()

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", frozen=True
    )


settings = AppConfig()
