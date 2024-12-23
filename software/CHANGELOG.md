# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2024-10-30

## Changed

- Bumped sACN python module minimum required version to 1.10.0
- ESPHome API key is now an optional parameter (because using the encryption is optional as well)
- Removed unused dependencies and updated pydantic-settings, pydantic_core to the latest version

## [0.2.0] - 2024-10-26

### Added

- Added a configuration option to set the location where to save the log files
- User friendly error message, when one of the configuration options fails the validation

### Changed

- Modifying the schedule times +/- 3 seonds randomly to make it look better on the display
  - Since the subway data is not realtime, a lot of schedules starts at the same time accross all stops
- Now the BKK and ESPHome API key format is validated instead of checking if they are longer then 1 character

### Fixed 

- Fixed unicast mode for sACN, previously the IP address was not set correctly

## [0.1.0] - 2024-10-07

### Added

- Controlling the LEDs between the color of the route and their default color
- With special consideration when one stops serves multiple routes (e.g. Kálvin tér with both M3 and M4)
    - The default color is the combination of the routes that are currently operational
- User adjustable fade time for the LED actions
- User adjustable dim ratio for the background brightness of the LEDs (it can be turned off alltogether)
- sACN output for controlling the LED display
    - The universe and FPS can be changed by the user
    - The sACN output could work both in unicast and multicast mode defineable by the user
- Brightness feedback from the ESPHome firmware running of the device, so we can compensate
if the resulting value for the LED would fall under the turn on treshold of the LED (11%, decimal 28)
- Schedule updating from the BKK OpenData API
    - Regular updates for every stop (interval can be changed by the user)
    - Realtime updates for the suburban railways only (interval can be changed by the user)
        - Realtime data is not available for the subway
    - Frequent alert update for subway so the alerts not just get updated with the regular update
        - The frequent realtime update for the suburban railway also updates the alerts, so this is only necessary for the subway
- The LED on time is determined by how busy a route is, when BKK OpenData API does not provide separate arrival and departure times
- Processing alerts from the BKK OpenData API to determine if a stop is operational or not
    - We use this to determine the backgorund color of the LEDs
        - When a stop is served by multiple routes, if one of the routes is not operational, we change the background color accordingly
        - The LED is turned off when there is no route that is operational for the given stop
- Multi level loggin to file. The default log level is INFO, it can be changed by command line parameters to DEBUG or TRACE
- Basic webserver for checking the stored schedules
