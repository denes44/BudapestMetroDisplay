# BudapestMetroDisplay - Docker

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv6 Architecture][armv6-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv6-shield]: https://img.shields.io/badge/armv6-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg

![Uses alpinelinux 3.20](https://img.shields.io/badge/alpine-3.20-blue?logo=alpinelinux)
![Uses python 3.12](https://img.shields.io/badge/python-3.12-blue?logo=python)


This is a control software to use with the BudapestMetroDisplay
hardware LED display, which displays budapest's subway and
suburban railway network.

It gets the schedule, realtime and alert data from the
[BKK OpenData](https://opendata.bkk.hu/home) portal.
You need to obtain an API key for yourself to use the software.

The software processes the data from the API and controls the LEDs
via sACN (E1.31) protocol.

## Configuration



## More information

You can read more information about the project at [GitHub](https://github.com/denes44/BudapestMetroDisplay).

- README of the software: [software/README.md](https://github.com/denes44/BudapestMetroDisplay/blob/main/software/README.md)
- CHANGELOG of the software: [software/CHANGELOG.md](https://github.com/denes44/BudapestMetroDisplay/blob/main/software/CHANGELOG.md)
 
- README of the ESPHome firmware: [esphome/README.md](https://github.com/denes44/BudapestMetroDisplay/blob/main/esphome/README.md)
- CHANGELOG of the ESPHome firmware: [esphome/CHANGELOG.md](https://github.com/denes44/BudapestMetroDisplay/blob/main/esphome/CHANGELOG.md)
 
- README of the hardware: [hardware/README.md](https://github.com/denes44/BudapestMetroDisplay/blob/main/hardware/README.md)
- CHANGELOG of the hardware: [hardware/CHANGELOG.md](https://github.com/denes44/BudapestMetroDisplay/blob/main/hardware/CHANGELOG.md)
