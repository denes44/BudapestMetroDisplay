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
from pathlib import Path
import sys
from typing import Optional, Any

from pydantic import Field, field_validator, IPvAnyAddress, ValidationError, \
    DirectoryPath, model_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class LEDConfig(BaseSettings):
    dim_ratio: float = Field(
        default=0.25,
        ge=0,
        le=1,
        description="Dim ratio for the background brightness of the LEDs \
            (0 means totally off)",
    )
    fade_time: float = Field(
        default=0.5,
        ge=0,
        description="Fade time in seconds for the LED turn on and off action",
    )

    model_config = SettingsConfigDict(
        env_prefix="LED_", frozen=True
    )


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
    def check_unicast_ip(cls, value: IPvAnyAddress,
                         info: ValidationInfo) -> IPvAnyAddress:
        if "multicast" in info.data and not info.data["multicast"] and value is None:
            raise ValueError("unicast_ip must be a valid IP address when using unicast")
        return value

    model_config = SettingsConfigDict(
        env_prefix="SACN_", frozen=True
    )


class BKKConfig(BaseSettings):
    api_key: str = Field(
        pattern=(
            r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-'
            r'[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-'
            r'[a-fA-F0-9]{12}$'
        ),
        description="API key for the BKK OpenData portal")
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

    model_config = SettingsConfigDict(
        env_prefix="BKK_", frozen=True
    )


class ESPHomeConfig(BaseSettings):
    used: bool = Field(
        default=False,
        description="Whether to use brightness data from ESPHome \
            to determine the minimum brightness",
    )
    device_ip: Optional[IPvAnyAddress] = Field(
        default=None, description="The IP address of the ESPHome device"
    )
    api_key: Optional[str] = Field(default=None, pattern=r"^[A-Za-z0-9+/]{43}=$",
                                   description="The API key of the ESPHome device")

    @field_validator("device_ip")
    def check_unicast_ip(cls, value, info: ValidationInfo):
        if "used" in info.data and info.data["used"] and value is None:
            raise ValueError("Device IP must be filled out when using ESPHome")
        return value

    @field_validator("api_key")
    def check_api_key(cls, value, info: ValidationInfo):
        if "used" in info.data and info.data["used"] and (
                value is None or len(value) == 0):
            raise ValueError("API key must be filled out when using ESPHome")
        return value

    model_config = SettingsConfigDict(
        env_prefix="ESPHOME_", frozen=True
    )


class LogConfig(BaseSettings):
    path: DirectoryPath = Field(default=Path("./log"),
                                description="The directory to store log files")

    model_config = SettingsConfigDict(
        env_prefix="LOG_", frozen=True
    )

    # Use `model_validator` to create the log directory if it doesn't exist
    @model_validator(mode="before")
    @classmethod
    def ensure_log_directory_exists(cls, values: Any) -> Any:
        path = values.get("path", Path("./log"))
        path = Path(path)  # Ensure `path` is a Path object

        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValidationError(f"Unable to create log directory at {path}: {e}")

        # Update `path` back in `values`
        values["path"] = path
        return values


class AppConfig(BaseSettings):
    try:
        led: LEDConfig = LEDConfig()
        sacn: SACNConfig = SACNConfig()
        bkk: BKKConfig = BKKConfig()  # type: ignore[call-arg]
        esphome: ESPHomeConfig = ESPHomeConfig()
        log: LogConfig = LogConfig()
    except ValidationError as e:
        logger.error("Configuration Error: Please check your environment variables")
        logger.error(e)
        sys.exit(1)  # Exit the application with a non-zero status code

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", frozen=True
    )


settings = AppConfig()
