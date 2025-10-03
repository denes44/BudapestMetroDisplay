# Changelog for ESPHome firmware

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - Unreleased

### Breaking change

- The default sACN mode is unicast from now on

### Added

- Factory resetting the device is now possible
	- From the Web GUI
	- Or by power-cycling the device 5 times with less then 10s between
	  the power cycles

## [1.1.0] - 2025-09-04

### Changed

- The default colors of the suburban railways is now purple now,
in accordance with the change in the software (v1.1.0)

### Fixed

- The device won't restart after every 15 minutes if an API connection is not
made to the device
- The device now correctly reloads it's previous brightness value when restarted
- The LEDs won't flash with a white color during boot

## [1.0.1] - 2025-02-19

### Changed

- **Minimum required ESPHome version: 2025.2.0**
- Changed the default CPU frequency from 160 MHz to 240 MHz
- Adapted the new RMT led driver configuration to the 2025.2.0 changes
  - The main LED chain now can use more resources than before,
    so the previous flickering is now gone
- Use 5.3.1 esp-idf framework version instead of the recommended
  with 6.9.0 esp32 platform version
  - These versions are also needed to fix the flickering
    mentioned in the previous point

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
