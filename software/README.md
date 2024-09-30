# BudapestMetroDisplay - Software

## Installation

### Linux

### Proxmox

You can easily run the software for this project in a Proxmox LXC.

This is a basic Debian LXC with python,
and this software automatically installated and configured.

To create a new Proxmox VE BudapestMetroDisplay LXC,
run the command below in the **Proxmox VE Shell**.

```bash
bash -c "$(wget -qLO - https://github.com/denes44/BudapestMetroDisplay/raw/main/software/proxmox/ct/debian.sh)"
```

In the future you can use the `update` command inside the LXC to
**update the application**.

This script is customized from the Debian LXC install script, from
[tteck's Proxmox helper scripts](https://github.com/tteck/Proxmox/tree/main)

## Configuration

The different configuration options can be changed by environmental values.

### Public transport data

#### BKK OpenData API key

This is the only required value, you need to obtain your own API key from the
[BKK OpenData](https://opendata.bkk.hu/home) portal.

```text
BKK_API_KEY = "your_api_key"
```

### API update details

These are the configurable parameters for updating the public transport data:

```text
BKK_API_UPDATE_INTERVAL = 2 # Delay between consecutive API calls in seconds
BKK_API_UPDATE_REALTIME = 60 # Update frequency for realtime data in seconds
BKK_API_UPDATE_REGULAR = 1800 # Update frequency for regular data in seconds
BKK_API_UPDATE_ALERTS = 60 # Update frequency for alerts for non-realtime routes in seconds
```

These default values seems to be working fine, but you are able to adjust is
carefully is you'd want. Make sure you are don't overloading the API server
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

### sACN settings

You can change the default universe and fps of the sACN (E1.31) data
that is sent out:

```text
SACN_UNIVERSE = 1 # DMX universe to send out data with the sACN protocol
SACN_FPS = 1 # Idle update frequency (automatically goes higher during fade time)
```

### LED settings

The default fade time of the LEDs can also be changed:

```text
LED_FADE_TIME = 1.0 # Fade time in seconds for the LED turn on and off action
```
