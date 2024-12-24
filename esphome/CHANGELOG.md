# Changelog for ESPHome firmware

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-21

### Changed

- Changed the firmware update method
  - By default, the device uses the built-in HTTP update platform
  - After importing the device to the ESP Home dashboard, it provides
    a text sensor to detect if the remote YAML configuration is changed
  - The device checks for update every 6 hours
- Changed the default colors
- New grouping for the entities on the web gui

### Fixed

- Fixed syntax error for the web server sorting options
- Fixed script that loads default colors on startup

## [0.1.2] - 2024-10-12

### Changed

- Changed the URL for the firmware update check

## [0.1.1] - 2024-10-12

### Added

- Added configuration for importing the device to the ESP Home dashboard
- Added option to check for firmware updates from github


### Changed

- Rearranged the order of the entities in the web server view

## [0.1.0] - 2024-10-12

### Added

- Configuration for the hardware LED display as a light with sACN (E1.31) support
- Test functionately for visually testing the LEDs on the hardware
    - Can be turned on by software or with the `BOOT` hardware button
- Default values for the LEDs which is loaded after startup (and after turning of the test mode)
- Buttons for restart, restart in safe mode and shutdown
- Sensor for WiFi signal strength and connection status
