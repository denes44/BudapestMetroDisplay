# BudapestMetroDisplay - Home Assistant Quick Start Guide

## Installing the firmware

**If you got your display with the controller and firmware preinstalled,
you can skip to the next chapter.**

Otherwise you should follow these steps:
1. Select the [esphome-latest](https://github.com/denes44/BudapestMetroDisplay/releases/tag/esphome-latest)
firmware from the GitHub Releases
1. Download factory firmware binary file called `metro-display-esp32s3.factory.bin`
1. Connect your ESP32 board to the computer via an USB cable, while holding down the `BOOT` button
1. Go the the [ESPHome Web](https://web.esphome.io/) page to flash the firmware to the ESP32 board
1. Press `Connect` and select the serial port for your board
1. Then press the `Install` button, and select the previously downloaded firmware file
1. Press `Install` and wait while the firmware uploads to the device

## Connect the display to WiFi

### Using Improv Wi-Fi

1. With your phone (or other BLE capable device), go to [improv-wifi.com](https://www.improv-wifi.com/)
1. At `Improv via BLE` click `Connect device to Wi-Fi`
1. Select the device, and click `Pair` (You need to enable Bluetooth for this step)
1. Enter your Wi-Fi network's credentials (SSID and password) and click `Save`
1. The device will now connect to the selected Wi-Fi network

### Connecting to the Wi-Fi AP provided by the device

1. Connect to the `Metro Display Fallback AP` SSID
1. Select the Wi-Fi network that you want the device to use

The same Fallback AP will be provided by the device in case it fails to connect
to the previously set Wi-Fi network.

## Add the display to Home Assistant

After connecting the display to your WiFi network, click on this button
to open the integrations page in Home Assistant:

[![Open your Home Assistant instance and show your integrations.](https://my.home-assistant.io/badges/integrations.svg)](https://my.home-assistant.io/redirect/integrations/)

Home Assistant should automatically recognize the device from the network.

If not, you can manually add itt using the ESPHome integration:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=esphome)

## Install the software as a Home Assistant App

To install the software as a Home Assistant App, first you need to
add this repository to the add-on store:

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fdenes44%2FBudapestMetroDisplay)

After adding the repository to Home Assistant, you need to install the App.

You will be able access the configuration options at the `Options` tab
of the addon. You can read about the different options at the
`Documentation` tab, or you can check them here in the [documentation](software/README.md#configuration-options)

## API key

If you bought this display from an official source, you can use
the proxy API server and key that was provided to you during the purchase.

Otherwise you need to request your own API key directly from the BKK OpenData
portal.

### Obtaining API key from the BKK OpenData portal

You need to register to the [BKK OpenData](https://opendata.bkk.hu/home) portal
to obtain an API key for yourself.

On the left, click `Key management`, and then click `New` on the right
to create a new API key.

For the `Purpose of use` for example you can enter
`BudapestMetroDisplay wall display`.

## Configuring the Home Assistant add-on

In the `Settings`, select the `Apps` section, then select BudapestMetroDisplay:

[![Open your Home Assistant instance and show the dashboard of an add-on.](https://my.home-assistant.io/badges/supervisor_addon.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?addon=12f81477_budapestmetrodisplay)

At the top of the page in the `Documentation` tab you will find an explanation
for each configuration setting.

In the `Configuration` tab, you can configure each setting.
By default, Home Assistant only shows the settings that are configured, if you
want to see all of them, click on the `Show unused optional configuration
options` toggle at the bottom.

You won't need to touch most of the parameters, only the `BKK_API_KEY` (and
`BKK_API_BASE_URL` if you are using a proxy API server), and `SACN_UNICAST_IP`
(you should set the IP address of the display here).

Although it's not required, it's highly recommended (you can read the
documentation for the why) to turn on the `ESPHOME_USED` parameter and enter
the display's IP address again for the `ESPHOME_DEVICE_IP` setting.

## Using the device in Home Assistant

If you select the device in Home Assistant, you will find 2 RGB lights as the
main feature of the device.

One is the transport network itself. You can use it as a normal RGB light, but
if you want to display the live data on it, the `E1.31` effect should be
selected for the light. This is done automatically each time you turn on the
light.

The other one is the Metro Logo, which works completely separated from the
other LEDs, you can select any color for the lamps.

There is an Ambient Light sensor (from hardware version ABA) which you can use
in various automations, and Test mode that cycles through every color on the
LEDs if you want to check them.
