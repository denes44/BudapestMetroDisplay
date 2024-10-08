# Changelog for ESPHome firmware

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-10-xx

### Added

- Configuration for the hardware LED display as a light with sACN (E1.31) support
- Test functionately for visually testing the LEDs on the hardware
	- Can be turned on by software or with the `BOOT` hardware button
- Default values for the LEDs which is loaded after startup (and after turning of the test mode)
- Buttons for restart, restart in safe mode and shutdown
- Sensor for WiFi signal strength and connection status
