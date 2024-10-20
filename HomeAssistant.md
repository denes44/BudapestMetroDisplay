# BudapestMetroDisplay - Home Assistant Quick Start Guide

## Installing the firmware

If you got your display with the controller and firmware preinstalled,
you can skip to the next step.

## Connect to display to WiFi

### Using Improv Wi-Fi

- With your phone (or other BLE capable device), go to [improv-wifi.com](https://www.improv-wifi.com/)
- At `Improv via BLE` click `Connect device to Wi-Fi`
- Select the device, and click `Pair`
- Enter your Wi-Fi network's credentials (SSID and password) and click `Save`
- The device will now connect to the selected Wi-Fi network

### Using by connecting to the device

## Add the display to Home Assistant

After connecting the display to your WiFi network, click on this button
to open the integrations page in Home Assistant:

[![Open your Home Assistant instance and show your integrations.](https://my.home-assistant.io/badges/integrations.svg)](https://my.home-assistant.io/redirect/integrations/)

## Install the software as a Home Assistant add-on

To install the software as a Home Assistant add-on, first you need to
add this repository to the add-on store:

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fdenes44%2FBudapestMetroDisplay)

After adding the repository to Home Assistant, you need to install the add-on.

You will be able access the configuration options at the `Options` tab
of the addon. You can read about the different options at the
`Documentation` tab, or you can check them here in the [documentation](software/README.md#configuration-options)

## Obtaining API key from the BKK OpenData portal

You need to register to the [BKK OpenData](https://opendata.bkk.hu/home) portal
to obtain an API key for yourself.

On the left, click `Key management`, and then click `New` on the right
to create a new API key.

For the `Purpose of use` for example you can enter
`BudapestMetroDisplay wall display`.

## Configuring the Home Assistant add-on

blabla

## Using the device in Home Assistant
