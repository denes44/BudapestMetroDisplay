# BudapestMetroDisplay - Hardware

## PCB Size

The size of the PCB is 210 mm x 300 mm.

It fits perfectly in an IKEA LOMVIKEN 21x30 cm picture frame
(IKEA article number is 903.143.03).
The edge of the PCB is designed to not interfere with the edge
of the picture frame.
There is a template available to cut out areas of the back of the picture frame,
so the components can fit: [hardware/pcb_cutout.pdf](hardware/pcb_cutout.pdf)

## Controller

The PCB is designed to accomodate an ESP32-S3 SuperMini controller
as an internal controller.
The task of the internal controller is to receive sACN (E1.31) data
from the software and display it on the LEDs.

<img src="https://esphome.io/_static/made-for-esphome-black-on-white.png" width="150">

The default firmware is ESPHome, you can find the configuration to it in the
[esphome](esphome/README.md) folder.

The control software has an extra feature, it can take account the
global brightness that is set in ESPHome, so the LEDs won't go dark below 11%
(between 0% and 11% the LED stays dark).

In theory, different firmware can be used if it supports sACN (E1.31),
but the brightness compensation feature won't be available

For more advanced uses
(for example run the software directly on a more advanced controller),
a 3 pole PH2.0 connector is available for an external controller.
The data source for the LEDs can be selected by an SMD solder bridge.

## LEDs

63 pcs SK6805-EC20 2mm x 2mm LED for every stop.
The power consumtion is 5 mA for each LED,
so the total consumption for the LEDs is 315 mA

### LED addresses

| LED no. | DMX address | Stop |
| ------  | ----------- | ---- |
| 0       | 0           | H6 - Pesterzsébet felső |
| 1       | 3           | H6 - Kén utca |
| 2       | 6           | H6 - Közvágóhíd |
| 3       | 9           | H7 - Szabadkikötő |
| 4       | 12          | H7 - Müpa - Nemzeti Színház |
| 5       | 15          | H7 - Boráros tér |
| 6       | 18          | M4 - Kelenföld vasútállomás |
| 7       | 21          | M4 - Bikás park |
| 8       | 24          | M4 - Újbuda-központ |
| 9       | 27          | M4 - Móricz Zsigmond körtér |
| 10      | 30          | M4 - Szent Gellért tér - Műegyetem |
| 11      | 33          | M4 - Fővám tér |
| 12      | 36          | M4/M3 - Kálvin tér |
| 13      | 39          | M4 - Rákóczi tér |
| 14      | 42          | M4 - II. János Pál pápa tér |
| 15      | 45          | M2 - Déli pályaudvar |
| 16      | 48          | M2 - Széll Kálmán tér |
| 17      | 51          | M2/H5 - Batthány tér |
| 18      | 54          | M2 - Kossuth Lajos tér |
| 19      | 57          | M2/M1/M3 - Deák Ferenc tér |
| 20      | 60          | M2 - Astoria |
| 21      | 63          | M2 - Blaha Lujza tér |
| 22      | 66          | M2/M4 - Keleti pályaudvar |
| 23      | 69          | M2 - Puskás Ferenc Stadion |
| 24      | 72          | M2 - Pillangó utca |
| 25      | 75          | M2/H9 - Örs vezér tere |
| 26      | 78          | H9 - Rákosfalva |
| 27      | 81          | H5 - Margit híd, budai hídfő |
| 28      | 84          | H5 - Szépvölgyi út |
| 29      | 87          | H5 - Tímár utca |
| 30      | 90          | H5 - Szentlélek tér |
| 31      | 93          | H5 - Filatorigát |
| 32      | 96          | H5 - Kaszásdűlő |
| 33      | 99          | H5 - Aquincum |
| 34      | 102         | H5 - Rómaifürdő |
| 35      | 105         | M3 - Újpest-központ |
| 36      | 108         | M3 - Újpest-városkapu |
| 37      | 111         | M3 - Gyöngyösi utca |
| 38      | 114         | M3 - Forgách utca |
| 39      | 117         | M3 - Göncz Árpád városközpont |
| 40      | 120         | M3 - Dózsa György út |
| 41      | 123         | M3 - Lehel tér |
| 42      | 126         | M3 - Nyugati pályaudvar |
| 43      | 129         | M3 - Arany János utca |
| 44      | 132         | M3 - Ferenciek tere |
| 45      | 135         | M3 - Corvin-negyed |
| 46      | 138         | M3 - Semmelweis Klinikák |
| 47      | 141         | M3 - Nagyvárad tér |
| 48      | 144         | M3 - Népliget |
| 49      | 147         | M3 - Ecseri út |
| 50      | 150         | M3 - Pöttyös utca |
| 51      | 153         | M3 - Határ út |
| 52      | 156         | M3 - Kőbánya-Kispest |
| 53      | 159         | M1 - Vörösmarty tér |
| 54      | 162         | M1 - Bajcsy-Zsilinszky út |
| 55      | 165         | M1 - Opera |
| 56      | 168         | M1 - Oktogon |
| 57      | 171         | M1 - Vörösmarty utca |
| 58      | 174         | M1 - Kodály körönd |
| 59      | 177         | M1 - Bajza utca |
| 60      | 180         | M1 - Hősök tere |
| 61      | 183         | M1 - Széchenyi fürdő |
| 62      | 186         | M1 - Mexikói út |