# BudapestMetroDisplay - Home Assistant Addon

## Software

This is a control software to use with the BudapestMetroDisplay
hardware LED display, which displays budapest's subway and
suburban railway network.

It gets the schedule, realtime and alert data from the
[BKK OpenData](https://opendata.bkk.hu/home) portal.
You need to obtain an API key for yourself to use the software.

The software processes the data from the API and controls the LEDs
via sACN (E1.31) protocol.
