# BudapestMetroDisplay - Software

![Latest version](https://img.shields.io/pypi/v/BudapestMetroDisplay?label=latest%20version%20at%20pypi&color=orange&logo=pypi)
## Installation

### Linux / Windows / Other

You can install the application from the Python Package Index:
[https://pypi.org/project/BudapestMetroDisplay/](https://pypi.org/project/BudapestMetroDisplay/)

Just run this command after installing python and pip
(and virtual environment if you'd like, etc.):

```bash
pip install BudapestMetroDisplay
```

The different configuration options can be set using environmental values
according to your system.

You can find the possible options and required values
in the [Configuration options](#configuration-options) chapter.

### Home Assistant Add-on

To install the software as a Home Assistant add-on, first you need to
add this repository to the add-on store
(not available in every installation type):

[![Open your Home Assistant instance and show the add add-on repository dialog
with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fdenes44%2FBudapestMetroDisplay)

You will be able access the configuration options at the `Options` tab
of the addon.

### Proxmox

You can easily run the software for this project in a Proxmox LXC.

This is a basic Debian LXC with python, and this software
automatically installated and configured.

#### Install

To create a new Proxmox VE BudapestMetroDisplay LXC,
run the command below in the **Proxmox VE Shell**.

```bash
bash -c "$(wget -qLO - https://github.com/denes44/BudapestMetroDisplay/raw/main/proxmox-script/ct/BudapestMetroDisplay.sh)"
```

This script is customized from the Debian LXC install script, from
[tteck's Proxmox helper scripts](https://github.com/tteck/Proxmox/tree/main)

The application is installed to the `/opt/BudapestMetroDisplay` folder.

`systemd` is used to automatically start the application.

The `.venv` folder consists the Python virtual environment which will run
the application.

The `log` folder consists the log generated while running the application.

#### Update

In the future you can use the `update` command inside the LXC to
**update the application**.

#### Configure

During the creation of the LXC the install script will download the
[sample .env file](https://github.com/denes44/BudapestMetroDisplay/blob/main/software/src/BudapestMetroDisplay/.env.sample)
which will contains all the possible environment values
and their default values.

The location of this file will be:

```text
/opt/BudapestMetroDisplay/.venv
```

You need to uncomment the ones you would like to customize.

You can find the possible options and required values
in the [Configuration options](#configuration-options) chapter.

## Configuration options

The different configuration options can be changed by environmental values.

### Public transport data

#### BKK OpenData API key

This is the only required value, you need to obtain your own API key from the
[BKK OpenData](https://opendata.bkk.hu/home) portal.

```text
BKK_API_KEY = "your_api_key"
```

#### API update details

These are the configurable parameters for updating the public transport data:

```text
BKK_API_UPDATE_INTERVAL = 2 # Delay between consecutive API calls in seconds
BKK_API_UPDATE_REALTIME = 60 # Update frequency for realtime data in seconds
BKK_API_UPDATE_REGULAR = 1800 # Update frequency for regular data in seconds
BKK_API_UPDATE_ALERTS = 600 # Update frequency for alerts for non-realtime routes in seconds
```

All of these values are in **seconds**, and the **minimum value is 1**.

These default values seems to be working fine, but you are able to adjust is
carefully is you'd want. Make sure you are not overloading the API server
(but it's your API key, so... :))

For realtime updates, the update frequency is `BKK_API_UPDATE_REALTIME` seconds,
but the requested data from the API is two times this value
from the current time.

For regular updates, the update frequency is `BKK_API_UPDATE_REGULAR` seconds,
but the requested data from the API is 5 minutes more.

The idea is to to get our base data for a long time to not overload the API
(bigger response, but less frequent), and then update the data for
specific stops (only the suburban railways have realtime data available)
frequently (small responses, but more frequent).

Because we don't update the subway stops very frequently (there is no need
for that, because there are no realtime data available for them), there is the
`BKK_API_UPDATE_ALERTS` parameter, which updates only the TravelAlerts and only
for the subway stops. That way if there is an active travel alert,
we can informed about them sooner than the next regular schedule update.

Also very different values might cause the application to function
not as intended.
For example the value of `BKK_API_UPDATE_REGULAR` might affect the detection
of out of service stops. Make sure that this value is higher than the maximum
following distance of the vehicles.

The `BKK_API_UPDATE_INTERVAL` value is used during startup when we send out
a lot of API calls to update everything. In order to not overload the API
server, we wait this amount between the API calls.

### sACN settings

Two options are availble for the network transmission, `multicast` and `unicast`,
with the default beeing `multicast`.
Because of this the target device's IP address is not needed.

If your network does not support `multicast`, you need to use `unicast`.
In this case, setting a destination IP address is mandatory.

```text
SACN_MULTICAST = True # Whether to use multicast or unicast for the transmission
SACN_UNICAST_IP = # The destination IP address for unicast sACN
```

You can change the default universe and the maximum fps of the
sACN (E1.31) data that is sent out:

```text
SACN_UNIVERSE = 1 # DMX universe to send out data with the sACN protocol
SACN_FPS = 1 # FPS limit
```

Your can choose the **universe value between 1 and 63 999**.

The **minimum value for the FPS is 1**.

### LED settings

You can specify the dim ratio for the display.
```text
LED_DIM_RATIO = 0.25 # Dim ratio for the background brightness of the LEDs (0 means totally off)
```
It defines the brightness relative to the maximum brightness, when there is no
vehicles at the stop. It's a **value between 0.0 and 1.0**.
Value 0 means the LEDs will be off when there is no vehicle at the stop,
and value 1 means the LEDs will be on all the time, so I would not recommend that.

If you are not using the display on maximum brightness, this settings can make
the dimmer colors wrong, because they LEDs can only turn on above 11% brightness:

```text
LED color
	100%, 50%, 0%
With LED_DIM_RATO 0.25
	25%, 12%, 0%
But if your global brightness is 75%
	19%, 9%, 0%
Green LED is under 11%, so it will stay OFF
```

The default fade time of the LEDs can also be changed.
To disable fade, just set this value to zero.

```text
LED_FADE_TIME = 1.0 # Fade time in seconds for the LED turn on and off action
```

### ESPHome settings

For the previously mentioned "brightness problem", the software can connect
to the ESPHome firmware that is running on the device to get the brightness
value.

```text
ESPHOME_USED = False # Whether to use brightness data from ESPHome to determine the minimum brightness
ESPHOME_DEVICE_IP = # The IP address of the ESPHome device
ESPHOME_API_KEY = # The API key of the ESPHome device
```

It's a simple mechanism if a LED value multiplied with the brightness value
from the device would fall below 11%, the application will send out 11% instead.
Set the `ESPHOME_USED` variable to **True if you want to turn on this function.**

Using the previous example:
```text
LED color
	100%, 50%, 0%
With LED_DIM_RATO 0.25
	25%, 12%, 0%
If your global brightness is 75%
	19%, 9%, 0%
With brightness compensation
	19%, 11%, 0%
```

### Log settings

The default location for saving the logs is the `logs` subfolder
in the current running directory, but it can be changed with the following
setting:

```text
LOG_PATH = # The directory to store log files
```
