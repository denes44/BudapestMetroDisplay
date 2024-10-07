#  MIT License
#
#  Copyright (c) 2024 [fullname]
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom
#  the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
from typing import Any

# Variable for associating the stopIds to the LEDs
stops_led: dict[str, int] = {
    # M1-es Vörösmarty tér-tól Mexikói út-ig
    "BKK_F00965": 53,
    "BKK_F00963": 19,
    "BKK_F00997": 54,
    "BKK_F01080": 55,
    "BKK_F01086": 56,
    "BKK_F01093": 57,
    "BKK_F01096": 58,
    "BKK_F01101": 59,
    "BKK_F01103": 60,
    "BKK_F02697": 61,
    "BKK_F02888": 62,
    # M1-es Mexikói út-tól Vörösmarty tér-ig
    "BKK_F02887": 62,
    "BKK_F02696": 61,
    "BKK_F01102": 60,
    "BKK_F01100": 59,
    "BKK_F01095": 58,
    "BKK_F01092": 57,
    "BKK_F01085": 56,
    "BKK_F01079": 55,
    "BKK_F00996": 54,
    "BKK_F00962": 19,
    "BKK_F00964": 53,
    # M2-es Déli pályaudvar-tól Örs vezér tere-ig
    "BKK_F00094": 15,
    "BKK_F02481": 16,
    "BKK_F00063": 17,
    "BKK_F00959": 18,
    "BKK_F00961": 19,
    "BKK_F01019": 20,
    "BKK_F01292": 21,
    "BKK_F01336": 22,
    "BKK_F01325": 23,
    "BKK_F01743": 24,
    # "BKK_F01749": 25, #duplicate
    # M2-es Örs vezér tere-tól Déli pályaudvar-ig
    "BKK_F01749": 25,
    "BKK_F01742": 24,
    "BKK_F01324": 23,
    "BKK_F01335": 22,
    "BKK_F01291": 21,
    "BKK_F01018": 20,
    "BKK_F00960": 19,
    "BKK_F00958": 18,
    "BKK_F00062": 17,
    "BKK_F02480": 16,
    "BKK_F00093": 15,
    # M3-as Újpest-központ-tól Kőbánya-Kispest-ig
    "BKK_F00913": 35,
    "BKK_F00898": 36,
    "BKK_F02685": 37,
    "BKK_F02683": 38,
    "BKK_F02638": 39,
    "BKK_F02681": 40,
    "BKK_F02614": 41,
    "BKK_F00937": 42,
    "BKK_F00957": 43,
    "BKK_F00955": 19,
    "BKK_F00953": 44,
    "BKK_F01290": 12,
    "BKK_F01189": 45,
    "BKK_F01233": 46,
    "BKK_F01253": 47,
    "BKK_F01283": 48,
    "BKK_F01494": 49,
    "BKK_F01879": 50,
    "BKK_F01542": 51,
    "BKK_F01544": 52,
    # M3-as Kőbánya-Kispest-től Újpest-központ-ig
    "BKK_F01543": 52,
    "BKK_F01541": 51,
    "BKK_F01878": 50,
    "BKK_F01493": 49,
    "BKK_F01282": 48,
    "BKK_F01252": 47,
    "BKK_F01232": 46,
    "BKK_F01188": 45,
    "BKK_F01289": 12,
    "BKK_F00952": 44,
    "BKK_F00954": 19,
    "BKK_F00956": 43,
    "BKK_F00936": 42,
    "BKK_F02613": 41,
    "BKK_F02680": 40,
    "BKK_F02637": 39,
    "BKK_F02682": 38,
    "BKK_F02684": 37,
    "BKK_F00897": 36,
    "BKK_F00912": 35,
    # M4-es Keleti pályaudvar-tól Kelenföld vasútállomás-ig
    "BKK_056233": 22,
    "BKK_056231": 14,
    "BKK_056229": 13,
    "BKK_056227": 12,
    "BKK_056225": 11,
    "BKK_056223": 10,
    "BKK_056221": 9,
    "BKK_056219": 8,
    "BKK_056217": 7,
    "BKK_056215": 6,
    # M4-es Kelenföld vasútállomás-tól Keleti pályaudvar-ig
    "BKK_056216": 6,
    "BKK_056218": 7,
    "BKK_056220": 8,
    "BKK_056222": 9,
    "BKK_056224": 10,
    "BKK_056226": 11,
    "BKK_056228": 12,
    "BKK_056230": 13,
    "BKK_056232": 14,
    "BKK_056234": 22,
    # H5-ös (2487) Rómaifürdő-től Batthyányi tér-ig
    "BKK_09159205": 34,
    "BKK_09100203": 33,
    "BKK_09084201": 32,
    "BKK_09118199": 31,
    "BKK_09068197": 30,
    "BKK_09050195": 29,
    "BKK_09043193": 28,
    "BKK_09019191": 27,
    "BKK_09001187": 17,
    "BKK_09001188": 17,
    "BKK_09001189": 17,
    # H5-ös (2632) Batthyány tér-től Rómaifürdő-ig
    # "BKK_09001187": 17,
    # "BKK_09001188": 17,
    # "BKK_09001189": 17,
    "BKK_09019190": 27,
    "BKK_09043192": 28,
    "BKK_09050194": 29,
    "BKK_09068196": 30,
    "BKK_09118198": 31,
    "BKK_09084200": 32,
    "BKK_09100202": 33,
    "BKK_09159204": 34,
    # H6-os (2685) Pesterzsébet felső-től Közvágóhíd-ig
    "BKK_19729240": 0,
    "BKK_19726239": 1,
    "BKK_19720236": 2,
    "BKK_19720237": 2,
    # H6-os (9135) Közvágóhíd-től Pesterzsébet felső-ig
    # "BKK_19720236": 2,
    # "BKK_19720237": 2,
    "BKK_19726238": 1,
    "BKK_19729241": 0,
    # H7-es Szabadkikötő-től Boráros tér-ig
    "BKK_09223228": 3,
    "BKK_09221227": 4,
    "BKK_09220224": 5,
    "BKK_09220225": 5,
    # H7-es (2326) Boráros tér-től Szabadkikötő-ig
    # "BKK_09220224": 5,
    # "BKK_09220225": 5,
    "BKK_09221226": 4,
    "BKK_09223229": 3,
    # H8/H9-es (1071) Rákosfalva-tól Örs vezér tere-ig
    "BKK_19798282": 26,
    "BKK_19795278": 25,
    "BKK_19795279": 25,
    "BKK_19795280": 25,
    # H8/H9-es (1100) Örs vezér tere-től Rákosfalva-ig
    # "BKK_19795278": 25,
    # "BKK_19795279": 25,
    # "BKK_19795280": 25,
    "BKK_19798281": 26,
}

# Variable for storing the routes with the stopIds for schedule updates
# Only for metro lines, because these will only need REGULAR updates
stops_metro: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "M1",
        (
            "BKK_F00965",
            "BKK_F00963",
            "BKK_F00997",
            "BKK_F01080",
            "BKK_F01086",
            "BKK_F01093",
            "BKK_F01096",
            "BKK_F01101",
            "BKK_F01103",
            "BKK_F02697",
            "BKK_F02888",
            "BKK_F02887",
            "BKK_F02696",
            "BKK_F01102",
            "BKK_F01100",
            "BKK_F01095",
            "BKK_F01092",
            "BKK_F01085",
            "BKK_F01079",
            "BKK_F00996",
            "BKK_F00962",
            "BKK_F00964",
        ),
    ),
    (
        "M2",
        (
            "BKK_F00094",
            "BKK_F02481",
            "BKK_F00063",
            "BKK_F00959",
            "BKK_F00961",
            "BKK_F01019",
            "BKK_F01292",
            "BKK_F01336",
            "BKK_F01325",
            "BKK_F01743",
            "BKK_F01749",
            "BKK_F01742",
            "BKK_F01324",
            "BKK_F01335",
            "BKK_F01291",
            "BKK_F01018",
            "BKK_F00960",
            "BKK_F00958",
            "BKK_F00062",
            "BKK_F02480",
            "BKK_F00093",
        ),
    ),
    (
        "M3",
        (
            "BKK_F00913",
            "BKK_F00898",
            "BKK_F02685",
            "BKK_F02683",
            "BKK_F02638",
            "BKK_F02681",
            "BKK_F02614",
            "BKK_F00937",
            "BKK_F00957",
            "BKK_F00955",
            "BKK_F00953",
            "BKK_F01290",
            "BKK_F01189",
            "BKK_F01233",
            "BKK_F01253",
            "BKK_F01283",
            "BKK_F01494",
            "BKK_F01879",
            "BKK_F01542",
            "BKK_F01544",
            "BKK_F01543",
            "BKK_F01541",
            "BKK_F01878",
            "BKK_F01493",
            "BKK_F01282",
            "BKK_F01252",
            "BKK_F01232",
            "BKK_F01188",
            "BKK_F01289",
            "BKK_F00952",
            "BKK_F00954",
            "BKK_F00956",
            "BKK_F00936",
            "BKK_F02613",
            "BKK_F02680",
            "BKK_F02637",
            "BKK_F02682",
            "BKK_F02684",
            "BKK_F00897",
            "BKK_F00912",
        ),
    ),
    (
        "M4",
        (
            "BKK_056233",
            "BKK_056231",
            "BKK_056229",
            "BKK_056227",
            "BKK_056225",
            "BKK_056223",
            "BKK_056221",
            "BKK_056219",
            "BKK_056217",
            "BKK_056215",
            "BKK_056216",
            "BKK_056218",
            "BKK_056220",
            "BKK_056222",
            "BKK_056224",
            "BKK_056226",
            "BKK_056228",
            "BKK_056230",
            "BKK_056232",
            "BKK_056234",
        ),
    ),
)

# Variable for storing the routes with the stopIds for schedule updates
# Only for suburban railway lines,
# because these will need both REGULAR and REALTIME updates
stops_railway: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "H5",
        (
            "BKK_09159205",
            "BKK_09100203",
            "BKK_09084201",
            "BKK_09118199",
            "BKK_09068197",
            "BKK_09050195",
            "BKK_09043193",
            "BKK_09019191",
            "BKK_09001187",
            "BKK_09001188",
            "BKK_09001189",
        ),
    ),
    ("H6", ("BKK_19729240", "BKK_19726239", "BKK_19720236", "BKK_19720237")),
    ("H7", ("BKK_09223228", "BKK_09221227", "BKK_09220224", "BKK_09220225")),
    ("H8", ("BKK_19798282", "BKK_19795278", "BKK_19795279", "BKK_19795280")),
)

# Variable for storing the routes that we want to update more frequently
# than REGULAR updates to check for TravelAlarms
# For REALTIME updated routes, this is not needed
alert_routes: tuple[str, ...] = (
    "BKK_5100",
    "BKK_5200",
    "BKK_5300",
    "BKK_5400",
)
# Variable to store if a stop is not serviced at the moment
stop_no_service: dict[str, bool] = {stop_id: False for stop_id in stops_led}

common_stops: dict[int, tuple[dict[str, Any], ...]] = {
    12: (
        {
            "name": "M3",
            "route_id": "BKK_5300",
            "stop_ids": ["BKK_F01290", "BKK_F01289"],
        },
        {
            "name": "M4",
            "route_id": "BKK_5400",
            "stop_ids": ["BKK_056227", "BKK_056228"],
        },
    ),
    17: (
        {
            "name": "M2",
            "route_id": "BKK_5200",
            "stop_ids": ["BKK_F00063", "BKK_F00062"],
        },
        {
            "name": "H5",
            "route_id": "BKK_H5",
            "stop_ids": ["BKK_09001187", "BKK_09001188", "BKK_09001189"],
        },
    ),
    19: (
        {
            "name": "M1",
            "route_id": "BKK_5100",
            "stop_ids": ["BKK_F00963", "BKK_F00962"],
        },
        {
            "name": "M2",
            "route_id": "BKK_5200",
            "stop_ids": ["BKK_F00961", "BKK_F00960"],
        },
        {
            "name": "M3",
            "route_id": "BKK_5300",
            "stop_ids": ["BKK_F00955", "BKK_F00954"],
        },
    ),
    22: (
        {
            "name": "M2",
            "route_id": "BKK_5200",
            "stop_ids": ["BKK_F01336", "BKK_F01335"],
        },
        {
            "name": "M4",
            "route_id": "BKK_5400",
            "stop_ids": ["BKK_056233", "BKK_056234"],
        },
    ),
    25: (
        {
            "name": "M2",
            "route_id": "BKK_5200",
            "stop_ids": ["BKK_F01749"],
        },
        {
            "name": "H8",
            "route_id": "BKK_H8",
            "stop_ids": ["BKK_19795278", "BKK_19795279", "BKK_19795280"],
        },
    ),
}
