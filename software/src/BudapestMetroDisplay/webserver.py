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

import logging
import threading

from flask import Flask, render_template

logger = logging.getLogger(__name__)

app = Flask(__name__)
stop_names = {
    "BKK_F00965": "Vörösmarty tér",
    "BKK_F00963": "Deák Ferenc tér",
    "BKK_F00997": "Bajcsy-Zsilinszky út",
    "BKK_F01080": "Opera",
    "BKK_F01086": "Oktogon",
    "BKK_F01093": "Vörösmarty utca",
    "BKK_F01096": "Kodály körönd",
    "BKK_F01101": "Bajza utca",
    "BKK_F01103": "Hősök tere",
    "BKK_F02697": "Széchenyi fürdő",
    "BKK_F02888": "Mexikói út",
    "BKK_F00094": "Déli pályaudvar",
    "BKK_F02481": "Szél Kálmán tér",
    "BKK_F00063": "Batthyány tér",
    "BKK_F00959": "Kossuth Lajos tér",
    "BKK_F00961": "Deák Ferenc tér",
    "BKK_F01019": "Astoria",
    "BKK_F01292": "Blaha Lujza tér",
    "BKK_F01336": "Keleti pályaudvar",
    "BKK_F01325": "Puskás Ferenc Stadion",
    "BKK_F01743": "Pillangó utca",
    "BKK_F01749": "Örs vezér tere",
    "BKK_F00913": "Újpest-központ",
    "BKK_F00898": "Újpest-városkapu",
    "BKK_F02685": "Gyöngyösi utca",
    "BKK_F02683": "Forgách utca",
    "BKK_F02638": "Göncz Árpád városközpont",
    "BKK_F02681": "Dózsa György út",
    "BKK_F02614": "Lehel tér",
    "BKK_F00937": "Nyugati pályaudvar",
    "BKK_F00957": "Arany János utca",
    "BKK_F00955": "Deák Ferenc tér",
    "BKK_F00953": "Ferenciek tere",
    "BKK_F01290": "Kálvin tér",
    "BKK_F01189": "Corvin-negyed",
    "BKK_F01233": "Klinikák",
    "BKK_F01253": "Nagyvárad tér",
    "BKK_F01283": "Népliget",
    "BKK_F01494": "Ecseri út",
    "BKK_F01879": "Pöttyös utca",
    "BKK_F01542": "Határ út",
    "BKK_F01544": "Kőbánya-Kispest",
    "BKK_056215": "Kelenföldi pályaudvar",
    "BKK_056217": "Bikás park",
    "BKK_056219": "Újbuda-Központ",
    "BKK_056221": "Móricz Zsigmond körtér",
    "BKK_056223": "Szent Gellért tér",
    "BKK_056225": "Fővám tér",
    "BKK_056227": "Kálvin tér",
    "BKK_056229": "Rákóczi tér",
    "BKK_056231": "II. János Pál pápa tér",
    "BKK_056233": "Keleti pályaudvar",
    "BKK_09001187": "Batthyány tér",
    "BKK_09019190": "Margit híd",
    "BKK_09043192": "Szépvölgyi út",
    "BKK_09050194": "Tímár utca",
    "BKK_09068196": "Szentlélek tér",
    "BKK_09118198": "Filatorigát",
    "BKK_09084200": "Kaszásdűlű",
    "BKK_09100202": "Aquincum",
    "BKK_09159204": "Rómaifürdő",
    "BKK_19720236": "Közvágóhíd",
    "BKK_19726238": "Kén utca",
    "BKK_19729241": "Pesterzsébet felső",
    "BKK_09220224": "Boráros tér",
    "BKK_09221226": "Müpa",
    "BKK_09223229": "Szabadkikötő",
    "BKK_19795278": "Örs vezér tere",
    "BKK_19798281": "Rákosfalva",
    "BKK_F00964": "Vörösmarty tér",
    "BKK_F00962": "Deák Ferenc tér",
    "BKK_F00996": "Bajcsy-Zsilinszky út",
    "BKK_F01079": "Opera",
    "BKK_F01085": "Oktogon",
    "BKK_F01092": "Vörösmarty utca",
    "BKK_F01095": "Kodály körönd",
    "BKK_F01100": "Bajza utca",
    "BKK_F01102": "Hősök tere",
    "BKK_F02696": "Széchenyi fürdő",
    "BKK_F02887": "Mexikói út",
    "BKK_F00093": "Déli pályaudvar",
    "BKK_F02480": "Szél Kálmán tér",
    "BKK_F00062": "Batthyány tér",
    "BKK_F00958": "Kossuth Lajos tér",
    "BKK_F00960": "Deák Ferenc tér",
    "BKK_F01018": "Astoria",
    "BKK_F01291": "Blaha Lujza tér",
    "BKK_F01335": "Keleti pályaudvar",
    "BKK_F01324": "Puskás Ferenc Stadion",
    "BKK_F01742": "Pillangó utca",
    "BKK_F00912": "Újpest-központ",
    "BKK_F00897": "Újpest-városkapu",
    "BKK_F02684": "Gyöngyösi utca",
    "BKK_F02682": "Forgách utca",
    "BKK_F02637": "Göncz Árpád városközpont",
    "BKK_F02680": "Dózsa György út",
    "BKK_F02613": "Lehel tér",
    "BKK_F00936": "Nyugati pályaudvar",
    "BKK_F00956": "Arany János utca",
    "BKK_F00954": "Deák Ferenc tér",
    "BKK_F00952": "Ferenciek tere",
    "BKK_F01289": "Kálvin tér",
    "BKK_F01188": "Corvin-negyed",
    "BKK_F01232": "Klinikák",
    "BKK_F01252": "Nagyvárad tér",
    "BKK_F01282": "Népliget",
    "BKK_F01493": "Ecseri út",
    "BKK_F01878": "Pöttyös utca",
    "BKK_F01541": "Határ út",
    "BKK_F01543": "Kőbánya-Kispest",
    "BKK_056216": "Kelenföldi pályaudvar",
    "BKK_056218": "Bikás park",
    "BKK_056220": "Újbuda-Központ",
    "BKK_056222": "Móricz Zsigmond körtér",
    "BKK_056224": "Szent Gellért tér",
    "BKK_056226": "Fővám tér",
    "BKK_056228": "Kálvin tér",
    "BKK_056230": "Rákóczi tér",
    "BKK_056232": "II. János Pál pápa tér",
    "BKK_056234": "Keleti pályaudvar",
    "BKK_09001188": "Batthyány tér",
    "BKK_09019191": "Margit híd",
    "BKK_09043193": "Szépvölgyi út",
    "BKK_09050195": "Tímár utca",
    "BKK_09068197": "Szentlélek tér",
    "BKK_09118199": "Filatorigát",
    "BKK_09084201": "Kaszásdűlű",
    "BKK_09100203": "Aquincum",
    "BKK_09159205": "Rómaifürdő",
    "BKK_19720237": "Közvágóhíd",
    "BKK_19726239": "Kén utca",
    "BKK_19729240": "Pesterzsébet felső",
    "BKK_09220225": "Boráros tér",
    "BKK_09221227": "Müpa",
    "BKK_09223228": "Szabadkikötő",
    "BKK_19795279": "Örs vezér tere",
    "BKK_19798282": "Rákosfalva",
    "BKK_09001189": "Batthyány tér",
    "BKK_19795280": "Örs vezér tere",
}


@app.route('/schedules', defaults={'route_id': None}, methods=['GET'])
@app.route('/schedules/<route_id>', methods=['GET'])
def get_schedules(route_id):
    from BudapestMetroDisplay.bkk_opendata import departure_scheduler
    from BudapestMetroDisplay.led_control import ROUTE_COLORS
    jobs = departure_scheduler.get_jobs()
    job_list = []
    for job in jobs:
        if route_id is None or job.args[1] == route_id:
            job_info = {
                'id': job.id,
                'stop_name': stop_names.get(job.args[0], 'Unknown'),
                'arg1': job.args[1],
                'arg2': job.args[2],
                'arg3': job.args[3],
                'arg4': job.args[4]
            }
            job_list.append(job_info)
    return render_template(
        'schedules.html', jobs=job_list, route_colors=ROUTE_COLORS)


def start_webserver():
    thread = threading.Thread(target=lambda: app.run(debug=False, use_reloader=False))
    thread.daemon = True
    thread.start()
