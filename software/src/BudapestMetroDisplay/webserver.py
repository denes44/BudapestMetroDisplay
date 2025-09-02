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

from apscheduler.job import Job
from flask import Flask, render_template

from BudapestMetroDisplay.network import network

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/schedules", defaults={"route_id": None}, methods=["GET"])
@app.route("/schedules/<route_id>", methods=["GET"])
def get_schedules(route_id: str | None) -> str:
    """Return an HTML page with the filtered schedules.

    :param route_id: Specify a route_id to filter the jobs. Use None the return
        all jobs.
    """
    from BudapestMetroDisplay.bkk_opendata import departure_scheduler

    jobs: list[Job] = departure_scheduler.get_jobs()
    job_list = []
    for job in jobs:
        if route_id is None or job.args[0].route.route_id == route_id:
            # Add the job to the list if route_id wasn't specified,
            # or if it matches the route_id of the job
            job_info = {
                "id": job.id,
                "stop_name": job.args[0].name,
                "arg1": job.args[0].route.name,
                "arg2": job.args[1],
                "arg3": job.args[2],
                "arg4": job.args[3],
            }
            job_list.append(job_info)
    return render_template("schedules.html", jobs=job_list, network=network)


@app.route("/jobs", methods=["GET"])
def get_jobs() -> str:
    """Return an HTML page with the API update schedules."""
    from BudapestMetroDisplay.bkk_opendata import api_update_scheduler

    jobs: list[Job] = api_update_scheduler.get_jobs()

    return render_template("jobs.html", jobs=jobs)


def start_webserver() -> None:
    """Start the webserver in a separate thread."""
    thread = threading.Thread(
        target=lambda: app.run(debug=False, use_reloader=False),
        daemon=True,
        name="Webserver thread",
    )
    thread.start()
