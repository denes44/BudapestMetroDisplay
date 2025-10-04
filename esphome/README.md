# BudapestMetroDisplay - ESPHome Firmware

<img src="https://esphome.io/guides/images/made-for-esphome-black-on-white.svg" alt="Made for ESPHome logo" width="400">

![Latest version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fdenes44%2FBudapestMetroDisplay%2Frefs%2Fheads%2Fmain%2Fesphome%2Ffirmware%2Fmanifest.json&query=%24.version&logo=esphome&label=latest%20version&color=orange&logo=esphome)

## Firmware

The default firmware to use is [firmware/metro-display-esp32s3.factory.bin](firmware/metro-display-esp32s3.factory.bin).
With this firmware you can use [Improv via BLE](https://esphome.io/components/esp32_improv)
or [Improv via Serial](https://esphome.io/components/improv_serial)
to provision your device.

## Configuration

### Factory

The factory firmware uses the [metro-display.factory.yaml](metro-display.factory.yaml)
configuration file.

### ESPHome Dashboard

To import the configuration to your ESPHome Dashboard, use the [metro-display.yaml](metro-display.yaml)
file.

By default this file imports the core configuration from GitHub dynamically.

### Core functionality

Both of these config files import the [metro-display-core.yaml](metro-display-core.yaml)
configuration file which contains the core functionality for the device.

## Firmware update

### Factory

In this configuration mode, the device uses the built-in [HTTP Update platform](https://esphome.io/components/update/http_request.html).

If an update is available, you can update the device from the Web GUI, or from
Home Assistant directly, if you added the device to Home Assistant.

### ESPHome Dashboard

In this configuration mode, a text sensor called `Remote YAML Update`
is provided, to indicate if the remote core yaml configuration is newer than
what's installed on the device.

If you do a firmware install from the dashboard, the build process will use
the new core yaml file from GitHub dynamically.
