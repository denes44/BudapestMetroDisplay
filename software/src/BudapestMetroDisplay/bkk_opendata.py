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

from datetime import datetime, timedelta, time
import logging
from random import randint
from typing import List, Dict, Any, Union

from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
import requests

from BudapestMetroDisplay import aps_helpers
from BudapestMetroDisplay import led_control
from BudapestMetroDisplay._version import __version__
from BudapestMetroDisplay.main import settings
from BudapestMetroDisplay.stops import stops_led, stop_no_service

logger = logging.getLogger(__name__)
# Set the logging level for urllib3 to INFO
logging.getLogger("urllib3").setLevel(logging.INFO)
# Set logging level for requests to INFO
logging.getLogger("requests").setLevel(logging.INFO)

# Define base URL
API_BASE_URL: str = "https://futar.bkk.hu/api/query/v1/ws/otp/api/where/"

# Define the API request parameters for the different schedule updates
API_SCHEDULE_PARAMETERS: dict[str, dict[str, Any]] = {
    "REGULAR": {
        "minutesBefore": 0,
        "minutesAfter": round((settings.bkk.api_update_regular + 300) / 60),
        "limit": 200,
        "nextSchedule": timedelta(seconds=settings.bkk.api_update_regular),
    },
    "REALTIME": {
        "minutesBefore": 0,
        "minutesAfter": round(settings.bkk.api_update_realtime * 2 / 60),
        "limit": 100,
        "nextSchedule": timedelta(seconds=settings.bkk.api_update_realtime),
    },
}

# Default delay to turn off the LED
# when there is no separate arrival and departure time is available
ACTION_DELAY: dict[str, int] = {
    "BKK_5100": 10,  # M1
    "BKK_5200": 10,  # M2
    "BKK_5300": 10,  # M3
    "BKK_5400": 10,  # M4
    "BKK_H5": 15,  # H5
    "BKK_H6": 15,  # H6
    "BKK_H7": 15,  # H7
    "BKK_H8": 15,  # H8
    "BKK_H9": 15,  # H9
}

# Set minimum log level for APScheduler
logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)
logging.getLogger("apscheduler.scheduler").setLevel(logging.WARNING)

# Initialize APScheduler with a persistent job store
# for scheduling the departures (when we turn on the LEDs)
departure_scheduler: BackgroundScheduler = BackgroundScheduler(
    jobstores={"default": MemoryJobStore()}  # Use in-memory job storage
)
departure_scheduler.start()

# Initialize scheduler with MemoryJobStore
# for scheduling turning off the LEDs after departure
led_scheduler: BackgroundScheduler = BackgroundScheduler(
    jobstores={"default": MemoryJobStore()}  # Use in-memory job storage
)
led_scheduler.start()

# Initialize scheduler with MemoryJobStore for scheduling the API updates
api_update_scheduler: BackgroundScheduler = BackgroundScheduler(
    jobstores={"default": MemoryJobStore()}  # Use in-memory job storage
)
api_update_scheduler.start()


def create_schedule_updates(stop_sets: tuple[tuple[str, tuple[str, ...]], ...],
                            schedule_type: str):
    """
    Creates schedules in APScheduler for the API requests
    to update the data for the provided stops.

    :param stop_sets: A tuple which consist the stop set name as a string
    and a tuple with the stop ids
    :param schedule_type: REGULAR or REALTIME,
    affects the API update parameters
    """
    # Store the current time when we started the update process
    start_time = datetime.now()
    i = 0  # Value for delaying the schedules from each other for initial updates

    # Check if the supplied schedule_type parameter is valid,
    # and the API call parameters are available in API_SCHEDULE_PARAMETERS
    if schedule_type not in API_SCHEDULE_PARAMETERS:
        logging.error(f"Invalid schedule type request: {schedule_type}")
        return

    logging.info(
        f"Starting updating the {schedule_type} schedules for stop set "
        f"({', '.join(stop_set for stop_set, _ in stop_sets)})"
    )

    for stop_set in stop_sets:
        # Schedule the API calls from each other by settings.bkk.api_update_interval
        # starting from the current time
        delay: int = i * settings.bkk.api_update_interval
        i += 1
        job_time: datetime = start_time + timedelta(seconds=delay)  # job start time
        job_id: str = f"{stop_set[0]}_{schedule_type}"  # job reference id

        # Add the job to the scheduler
        api_update_scheduler.add_job(
            fetch_schedule_for_stops,
            "date",
            run_date=job_time,
            args=[stop_set, schedule_type],
            id=job_id,
            replace_existing=True,
            # If the job exists, it will be replaced with the new time
        )

        logger.debug(
            f"Scheduling {schedule_type} API updates for stop set "
            f"{stop_set[0]} at {str(job_time)}."
        )


def create_alert_updates(routes: tuple[str, ...]):
    """
    Creates schedules in APScheduler for the API requests
    to update the alerts for the provided routes.

    :param routes: A tuple which consist the route ids
    """
    # Store the current time when we started the update process
    start_time = datetime.now()
    i = 0  # Value for delaying the schedules from each other for initial updates

    # TODO change to debug later
    logging.info(f"Starting updating the alerts for routes {routes}")

    for route_id in routes:
        # Schedule the API calls from each other by settings.bkk.api_update_interval
        # starting from the current time
        delay: int = i * settings.bkk.api_update_interval
        i += 1
        job_time: datetime = start_time + timedelta(seconds=delay)  # job start time
        job_id: str = f"{route_id}_ALERTS"  # job reference id

        # Add the job to the scheduler
        api_update_scheduler.add_job(
            fetch_alerts_for_route,
            "date",
            run_date=job_time,
            args=[route_id],
            id=job_id,
            replace_existing=True,
            # If the job exists, it will be replaced with the new time
        )

        logger.debug(
            f"Scheduling alerts API updates for routes {routes} at {str(job_time)}."
        )


def fetch_schedule_for_stops(stop_set: tuple[str, tuple[str, ...]],
                             schedule_type: str):
    """
    Callback function for the APScheduler jobs.
    Makes an arrivals-and-departures-for-stop API request to the BKK OpenData server
    for the supplied stops.

    :param stop_set: A tuple which consist the stop set name as a string
        and a tuple with the stop ids we want to get the schedules for
    :param schedule_type: REGULAR or REALTIME, affects the API update parameters
    """

    # Calculate next schedule time
    if schedule_type == "REALTIME" and (
            time(0, 30) <= datetime.now().time() <= time(4, 0)
    ):
        # When the current time is between 00:30 and 04:00
        # schedule the next REALTIME update for 04:00
        job_time = datetime.combine(datetime.today(), time(4, 0))
    else:
        # Otherwise schedule the next update according to the configuration
        job_time = (
                datetime.now()
                + API_SCHEDULE_PARAMETERS[schedule_type]["nextSchedule"]
        )

    url: str = f"{API_BASE_URL}arrivals-and-departures-for-stop"

    headers: dict[str, str] = {"Accept": "application/json"}

    # Get schedule data for all stops in the stop set
    params: dict[str, str | int | List[str]] = {
        "stopId": list(stop_set[1]),
        "minutesBefore": API_SCHEDULE_PARAMETERS[schedule_type]["minutesBefore"],
        "minutesAfter": API_SCHEDULE_PARAMETERS[schedule_type]["minutesAfter"],
        "limit": API_SCHEDULE_PARAMETERS[schedule_type]["limit"],
        "onlyDepartures": "false",
        "appVersion": f"BudapestMetroDisplay {__version__}",
        "version": "4",
        "includeReferences": "routes,alerts",
        "key": settings.bkk.api_key,
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)

        if response.status_code == 200:
            store_departures(response.json(), stop_set[0])

            logger.debug(
                f"Successfully updated {schedule_type} schedules for stop set "
                f"{stop_set[0]}. Next update scheduled for {str(job_time)}"
            )
        else:
            # Reschedule the failed action for 1 minute later
            job_time = datetime.now() + timedelta(minutes=1)

            logger.error(
                f"Failed to update {schedule_type} schedules for stop set "
                f"{stop_set[0]}: {response.status_code}. "
                f"Rescheduled for {str(job_time)}."
            )
    except requests.exceptions.ReadTimeout as e:
        job_time = datetime.now() + timedelta(minutes=1)
        logger.warning(
            f"Timeout occurred when updating {schedule_type} schedules for stop set "
            f"{stop_set[0]}. Rescheduled for {str(job_time)}.")
        logger.warning(e)
    except requests.exceptions.ConnectionError as e:
        job_time = datetime.now() + timedelta(minutes=5)
        logger.warning(
            f"Connection error when updating {schedule_type} schedules for stop set "
            f"{stop_set[0]}. Rescheduled for {str(job_time)}.")
        logger.warning(e)
    except requests.exceptions.RequestException as e:
        job_time = datetime.now() + timedelta(minutes=1)
        logger.warning(
            f"Error when updating {schedule_type} schedules for stop set {stop_set[0]}."
            f"Rescheduled for {str(job_time)}.")
        logger.warning(e)

    # Get schedule data for the first stop in the stop set
    # for the schedule interval calculation
    if schedule_type == "REGULAR":
        params["stopId"] = stop_set[1][0]
        try:
            response = requests.get(url, headers=headers, params=params,
                                    timeout=5)

            if response.status_code == 200:
                calculate_schedule_interval((response.json()), stop_set[0])

                logger.debug(
                    f"Successfully updated schedules for stop set {stop_set[0]} "
                    f"for schedule interval calculation. "
                    f"Next update scheduled for {str(job_time)}"
                )
            else:
                # Reschedule the failed action for 1 minute later
                job_time = datetime.now() + timedelta(minutes=1)

                logger.error(
                    f"Failed to update schedules for stop set {stop_set[0]} "
                    f"for schedule interval calculation: {response.status_code}. "
                    f"Rescheduled for {str(job_time)}."
                )
        except requests.exceptions.ReadTimeout as e:
            job_time = datetime.now() + timedelta(minutes=1)
            logger.warning(
                f"Timeout occurred when updating schedules for stop set {stop_set[0]} "
                f"for schedule interval calculation. "
                f"Next update scheduled for {str(job_time)}")
            logger.warning(e)
        except requests.exceptions.ConnectionError as e:
            job_time = datetime.now() + timedelta(minutes=5)
            logger.error(
                f"Connection error when updating schedules for stop set {stop_set[0]} "
                f"for schedule interval calculation. "
                f"Next update scheduled for {str(job_time)}")
            logger.error(e)
        except requests.exceptions.RequestException as e:
            job_time = datetime.now() + timedelta(minutes=1)
            logger.error(
                f"Error when updating schedules for stop set {stop_set[0]} "
                f"for schedule interval calculation. "
                f"Next update scheduled for {str(job_time)}")
            logger.error(e)

    job_id: str = f"{stop_set[0]}_{schedule_type}"

    api_update_scheduler.add_job(
        fetch_schedule_for_stops,
        "date",
        run_date=job_time,
        args=[stop_set, schedule_type],
        id=job_id,
        replace_existing=True,
        # If the job exists, it will be replaced with the new time
    )


def fetch_alerts_for_route(route_id: str):
    """
    Callback function for the APScheduler jobs.
    Makes a route-details API request to the BKK OpenData server
    for the supplied route_id.

    :param route_id: The id of the stop we want to get the details for
    """

    # Calculate next schedule time
    job_time = datetime.now() + timedelta(
        minutes=settings.bkk.api_update_alerts)

    url: str = f"{API_BASE_URL}route-details"

    headers: dict[str, str] = {"Accept": "application/json"}

    params: dict[str, Union[str, int]] = {
        "routeId": route_id,
        "appVersion": f"BudapestMetroDisplay {__version__}",
        "version": "4",
        "includeReferences": "alerts",
        "key": settings.bkk.api_key,
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)

        if response.status_code == 200:
            process_alerts(response.json(), route_id)

            logger.debug(
                f"Successfully updated alerts for route {route_id}. "
                f"Next update scheduled for {str(job_time)}"
            )
        else:
            # Reschedule the failed action for 1 minute later
            job_time = datetime.now() + timedelta(minutes=1)

            logger.error(
                f"Failed to update alerts for route {route_id}: {response.status_code}."
                f"Rescheduled for {str(job_time)}."
            )
    except requests.exceptions.ReadTimeout as e:
        job_time = datetime.now() + timedelta(minutes=1)
        logger.warning(
            f"Timeout occurred when updating alerts for route {route_id}. "
            f"Next update scheduled for {str(job_time)}")
        logger.warning(e)
    except requests.exceptions.ConnectionError as e:
        job_time = datetime.now() + timedelta(minutes=5)
        logger.error(
            f"Connection error when updating alerts for route {route_id}. "
            f"Next update scheduled for {str(job_time)}")
        logger.error(e)
    except requests.exceptions.RequestException as e:
        job_time = datetime.now() + timedelta(minutes=1)
        logger.error(
            f"Error when updating alerts for route {route_id}. "
            f"Next update scheduled for {str(job_time)}")
        logger.error(e)

    job_id: str = f"{route_id}_ALERTS"

    api_update_scheduler.add_job(
        fetch_alerts_for_route,
        "date",
        run_date=job_time,
        args=[route_id],
        id=job_id,
        replace_existing=True,
        # If the job exists, it will be replaced with the new time
    )


def store_departures(json_response, reference_id: str):
    """
    Processes the ArrivalsAndDeparturesForStopOTPMethodResponse API response
    from the arrivals-and-departures-for-stop method.
    As a result stores the retrieved departures in a persistent APScheduler instance
    which will control the LED states.

    :param json_response: JSON return data from the BKK OpenData API
    :param reference_id: Internal reference to identify the API request in the logs
    :return:
    """
    # Check if JSON looks valid
    if (
            not json_response
            or "data" not in json_response
            or "entry" not in json_response["data"]
    ):
        logger.error(
            f"No valid schedule data in API response for stop(s) {reference_id}"
        )
        return

    # Check if we exceeded the query limit
    if json_response["data"].get("limitExceeded", "false") == "true":
        logger.warning(
            f"Query limit is exceeded when updating stop(s) {reference_id}")

    # Get routeId
    if (
            "routeIds" in json_response["data"]["entry"]
            and len(json_response["data"]["entry"]["routeIds"]) > 0
    ):
        route_id: str = json_response["data"]["entry"].get("routeIds", [])[0]
    elif (
            "routes" in json_response["data"]["references"]
            and len(json_response["data"]["references"]["routes"]) > 0
    ):
        route_id = list(json_response["data"]["references"]["routes"].keys())[
            0]
    else:
        logger.warning(
            f"No route IDs found or the list is empty when updating stop(s) "
            f"{reference_id}"
        )
        return

    # Get stopId, when there is only one stop in the response
    stop_id_global: str = json_response["data"]["entry"].get("stopId", None)

    # Get stopTimes from TransitArrivalsAndDepartures
    stop_times = json_response["data"]["entry"].get("stopTimes", [])
    if len(stop_times) == 0:
        logger.debug(
            f"No schedule data found when updating stop(s) {reference_id}")

    # Iterate through the TransitScheduleStopTimes in the TransitArrivalsAndDepartures
    for stop_time in stop_times:
        trip_id: str = stop_time.get("tripId")

        # Get stopId, when the response contains schedules for multiple stops
        if "stopId" in stop_time:
            stop_id = stop_time.get("stopId")
        else:
            stop_id = stop_id_global

        # Check if we are interested in the provided stopId
        if stop_id not in stops_led:
            logger.debug(
                f"Got update for stop {stop_id}, route {route_id}, "
                f"but we don't need that, skipping"
            )
            continue

        # Get the predicted or scheduled departure and arrival times
        # CASE #1: Both arrival and departure time available as predicted
        # [middle stop with realtime data]
        arrival_time: int
        delay: int
        if (
                "predictedArrivalTime" in stop_time
                and "predictedDepartureTime" in stop_time
                and not stop_time.get("uncertain", False)
        ):
            # Arrival time is different from the departure,
            # lets use the difference between them for the LED turn off delay
            if stop_time.get("predictedArrivalTime") != stop_time.get(
                    "predictedDepartureTime"
            ):
                arrival_time = stop_time.get("predictedArrivalTime")
                delay = stop_time.get(
                    "predictedDepartureTime") - stop_time.get(
                    "predictedArrivalTime"
                )
            # Arrival time is the same as the departure,
            # use predefined delay for LED turn off
            else:
                arrival_time = (
                        stop_time.get("predictedDepartureTime")
                        - ACTION_DELAY[route_id]
                )
                delay = ACTION_DELAY[route_id]
        # CASE #2: Only predicted arrival time is available
        # [end stop with realtime data]
        # Use the predefined delay for LED turn off
        elif "predictedArrivalTime" in stop_time and not stop_time.get(
                "uncertain", False
        ):
            arrival_time = (
                    stop_time.get("predictedArrivalTime")
                    - ACTION_DELAY[route_id]
            )
            delay = ACTION_DELAY[route_id]
        # CASE #3: Only predicted departure time is available
        # [start stop with realtime data]
        # Use the predefined delay for LED turn off
        elif "predictedDepartureTime" in stop_time and not stop_time.get(
                "uncertain", False
        ):
            arrival_time = (
                    stop_time.get("predictedDepartureTime")
                    - ACTION_DELAY[route_id]
            )
            delay = ACTION_DELAY[route_id]
        # CASE #4: Both arrival and departure time available as scheduled time
        # [middle stop, no realtime data]
        elif "arrivalTime" in stop_time and "departureTime" in stop_time:
            # Arrival time is different from the departure,
            # lets use the difference between them for the LED turn off delay
            if stop_time.get("arrivalTime") != stop_time.get("departureTime"):
                arrival_time = (stop_time.get("arrivalTime")
                                + randint(-3, 3)
                                )
                delay = (stop_time.get("departureTime")
                         - stop_time.get("arrivalTime")
                         )
            # Arrival time is the same as the departure,
            # use predefined delay for LED turn off
            else:
                arrival_time = (stop_time.get("departureTime")
                                - ACTION_DELAY[route_id]
                                + randint(-3, 3)
                                )
                delay = ACTION_DELAY[route_id]
        # CASE #5: Only scheduled arrival time is available
        # [end stop with no realtime data]
        # Use the predefined delay for LED turn off
        elif "arrivalTime" in stop_time:
            arrival_time = (stop_time.get("arrivalTime")
                            - ACTION_DELAY[route_id]
                            + randint(-3, 3)
                            )
            delay = ACTION_DELAY[route_id]
        # CASE #6: Only scheduled departure time is available
        # [start stop with no realtime data]
        # Use the predefined delay for LED turn off
        elif "departureTime" in stop_time:
            arrival_time = (stop_time.get("departureTime")
                            - ACTION_DELAY[route_id]
                            + randint(-3, 3)
                            )
            delay = ACTION_DELAY[route_id]
        # CASE #7: No valid time data is available
        else:
            logger.debug(
                f"No valid arrival/departure time found "
                f"when updating stop {stop_id}, route {route_id}"
            )
            continue

        # We processed valid schedule data for this stop,
        # that means that the stop is operational
        if stop_no_service[stop_id]:
            stop_no_service[stop_id] = False
            # Reset the LED to the default color
            led_control.calculate_default_color(stops_led[stop_id])
            # Change the LED color to the default color
            # if there is no ongoing LED action for this LED
            if not led_control.led_locks[stops_led[stop_id]].locked():
                led_control.reset_led_to_default(stops_led[stop_id])

        # Schedule the action 10 seconds before the departure."""
        job_id: str = f"{stop_id}+{trip_id}"
        job_time: datetime = datetime.fromtimestamp(arrival_time)

        if job_time > datetime.now():
            departure_scheduler.add_job(
                action_to_execute,
                "date",
                run_date=job_time,
                args=[stop_id, route_id, trip_id, job_time, delay],
                id=job_id,
                replace_existing=True,
                # If the job exists, it will be replaced with the new time
            )

            logger.trace(  # type: ignore[attr-defined]
                f"Scheduled action for departure: stop_id={stop_id}, "
                f"route_id={route_id}, trip_id={trip_id}, "
                f"departure_time={str(datetime.fromtimestamp(arrival_time))}"
            )
        else:
            logger.trace(  # type: ignore[attr-defined]
                f"Action for departure: stop_id={stop_id}, route_id={route_id}, "
                f"trip_id={trip_id}, "
                f"departure_time={str(datetime.fromtimestamp(arrival_time))} "
                f"was in the past, skipping"
            )

    # Check if there is any active alerts in the response and process them
    alerts = json_response["data"]["entry"].get("alertIds", [])
    if len(alerts) > 0:
        process_alerts(json_response, reference_id)


def action_to_execute(
        stop_id: str, route_id: str, trip_id: str, job_time: datetime,
        delay: int
):
    """
    Changes the LED of the specified stop(stop_id) to the associated color,
    and schedules the turn-off of the LED in APScheduler after the supplied delay.

    :param stop_id: stopId from the BKK OpenData API
    :param route_id: routeId from the BKK OpenData API
    :param trip_id: tripId from the BKK OpenData API
    :param job_time: The time this job was scheduled in APScheduler
    :param delay: The amount of time needs to be elapsed in seconds
        between the turn on and turn off action
    """
    if job_time < datetime.now() - timedelta(seconds=20):
        logger.trace(  # type: ignore[attr-defined]
            "Action trigger time is in the past, skipping")
        return

    logger.trace(  # type: ignore[attr-defined]
        f"Action triggered for stop: {stop_id}, route: {route_id}, trip: {trip_id}, "
        f"LED off delay: {delay} sec"
    )

    led_id: int = stops_led[stop_id]

    # Change LED color according to the color of the route
    led_control.set_led_color(led_id, led_control.ROUTE_COLORS[route_id])

    # Schedule an action at the departure time to turn the LED back to the default value
    led_job_time = job_time + timedelta(seconds=delay)

    led_scheduler.add_job(
        led_control.reset_led_to_default,
        "date",
        run_date=led_job_time,
        args=[led_id],
        id=str(led_id),
        replace_existing=True,
        # If the job exists, it will be replaced with the new time
    )


def calculate_schedule_interval(json_response, reference_id: str):
    """
    Processes the ArrivalsAndDeparturesForStopOTPMethodResponse API response
    from the arrivals-and-departures-for-stop method.
    It checks time between the schedules for each route
    and updates the ACTION_DELAY dictionary accordingly.

    :param json_response: JSON return data from the BKK OpenData API
    :param reference_id: Internal reference to identify the API request in the logs
    :return:
    """
    # Check if JSON looks valid
    if (
            not json_response
            or "data" not in json_response
            or "entry" not in json_response["data"]
    ):
        logger.error(
            f"No valid schedule data in API response "
            f"for schedule intervals for {reference_id}"
        )
        return

    # Check if we exceeded the query limit
    if json_response["data"].get("limitExceeded", "false") == "true":
        logger.warning(
            f"Query limit is exceeded when updating "
            f"schedule intervals for {reference_id}"
        )

    # Get routeId
    route_id: str
    if (
            "routeIds" in json_response["data"]["entry"]
            and len(json_response["data"]["entry"]["routeIds"]) > 0
    ):
        route_id = json_response["data"]["entry"].get("routeIds", [])[0]
    elif (
            "routes" in json_response["data"]["references"]
            and len(json_response["data"]["references"]["routes"]) > 0
    ):
        route_id = list(json_response["data"]["references"]["routes"].keys())[0]
    else:
        logger.warning(
            f"No route IDs found or the list is empty when updating "
            f"schedule intervals for {reference_id}"
        )
        return

    # Get stopTimes from TransitArrivalsAndDepartures
    stop_times = json_response["data"]["entry"].get("stopTimes", [])
    if len(stop_times) < 2:
        logger.debug(
            f"Not enough schedule data found when updating "
            f"schedule intervals for {reference_id}"
        )
        return

    # Variable to store the necessary data from the first two relevant stops
    data: List[Dict[str, Any]] = [{} for _ in range(2)]

    # Iterate through the TransitScheduleStopTimes
    # in the TransitArrivalsAndDepartures
    i = 0
    for stop_time in stop_times:
        # Check if the stopHeadsign is the same as the first one
        if i > 0 and stop_time.get("stopHeadsign") != data[0]["stopHeadsign"]:
            continue

        # Store the stopHeadsign data
        data[i]["stopHeadsign"] = stop_time.get("stopHeadsign")

        # Get the scheduled departure or arrival times
        # CASE #1: Both arrival and departure time available as scheduled time
        # [middle stop, no realtime data]
        if "arrivalTime" in stop_time and "departureTime" in stop_time:
            data[i]["time"] = stop_time.get("departureTime")
        # CASE #2: Only scheduled arrival time is available
        # [end stop with no realtime data]
        elif "arrivalTime" in stop_time:
            data[i]["time"] = stop_time.get("arrivalTime")
        # CASE #3: Only scheduled departure time is available
        # [start stop with no realtime data]
        elif "departureTime" in stop_time:
            data[i]["time"] = stop_time.get("departureTime")
        # CASE #4: No valid time data is available
        else:
            logger.debug(
                f"No valid arrival/departure time found when updating "
                f"route {route_id} during schedule interval calculation"
            )
            continue
        i += 1

        if i == 2:
            break

    # Calculate the difference between the two schedules
    # Check if the departure times are available for both stops
    if "time" not in data[0] or "time" not in data[1]:
        # No valid schedule data found, set the difference to -1
        logger.debug(
            f"No valid schedule data found when updating "
            f"schedule intervals for {reference_id}"
        )
        difference = -1
    else:
        # Calculate the difference between the two schedules
        difference = (data[1]["time"] - data[0]["time"]) / 60

    # Update the ACTION_DELAY dictionary according to the calculated difference
    if difference > 0:
        if route_id.startswith("BKK_5"):  # Subway
            if difference <= 2:
                ACTION_DELAY[route_id] = 15
            elif difference < 5.5:
                ACTION_DELAY[route_id] = 20
            else:
                ACTION_DELAY[route_id] = 30
        elif route_id.startswith("BKK_H"):  # Suburban railway
            if difference < 5.5:
                ACTION_DELAY[route_id] = 20
            elif difference < 10.5:
                ACTION_DELAY[route_id] = 30
            else:
                ACTION_DELAY[route_id] = 45
    # No valid schedule data found, set the default delay
    elif difference == -1:
        if route_id.startswith("BKK_5"):  # Subway
            ACTION_DELAY[route_id] = 30
        elif route_id.startswith("BKK_H"):  # Suburban railway
            ACTION_DELAY[route_id] = 45

    logger.debug(
        f"Recalculated LED turn off delay for route {route_id}, "
        f"schedule delay: {difference:.1f} min, new delay: {ACTION_DELAY[route_id]} sec"
    )


def process_alerts(json_response, reference_id: str):
    # Check if JSON looks valid
    if (
            not json_response
            or "data" not in json_response
            or "references" not in json_response["data"]
            or "alerts" not in json_response["data"]["references"]
    ):
        logger.error(
            f"No valid alerts data in API response for stop(s) {reference_id}")
        return

    # Get stopTimes from TransitArrivalsAndDepartures
    alerts = json_response["data"]["references"].get("alerts")
    if len(alerts) == 0:
        logger.debug(
            f"No alert data found when updating stop(s) {reference_id}")

    # Iterate through the TransitScheduleStopTimes in the TransitArrivalsAndDepartures
    for alert_id, alert_details in alerts.items():
        # If the start time of the alert is in the future, return False
        if alert_details["start"] > datetime.now().timestamp():
            continue

        # Iterate the TransitAlertRoutes in the TransitAlert
        for route in alert_details["routes"]:
            route_id: str = route.get("routeId", "")
            effect_type: str = route.get("effectType", "")

            # If the effectType is not NO_SERVICE
            # we don't process the TransitAlertRoute anymore
            if effect_type != "NO_SERVICE":
                continue

            # Iterate through stopIds in the TransitAlertRoute
            for stop_id in route.get("stopIds", []):
                # Check if we are interested in the stopId
                if stop_id not in stops_led:
                    continue

                # Check whether the stop is operational now
                if not stop_no_service[stop_id]:
                    # Check if we have a schedule for this stop_id,
                    # because if we have, then the stop is not really out of service
                    soonest_job = aps_helpers.find_soonest_job_by_argument(
                        departure_scheduler, stop_id, 0
                    )

                    if soonest_job is not None:
                        # We found at least one schedule for this stop,
                        # so we'll ignore the NO_SERVICE alert
                        logger.debug(
                            f"Found NO_SERVICE alert {alert_details['id']} "
                            f"for stop {stop_id}, route {route_id}, "
                            f"but there are active schedules for that stop, "
                            f"so we'll ignore that"
                        )
                    else:
                        # No schedule found for this stop,
                        # so we'll process the NO_SERVICE alert
                        logger.debug(
                            f"Found NO_SERVICE alert {alert_details['id']} "
                            f"for stop {stop_id}, route {route_id}"
                        )
                        # Set the no_service flag for this stop
                        stop_no_service[stop_id] = True

                        # Calculate the default color for this stop according to
                        # which route is operation for the stop
                        led_control.calculate_default_color(stops_led[stop_id])
                        # Change the LED color to the default color
                        # if there is no ongoing LED action for this LED
                        if not led_control.led_locks[stops_led[stop_id]].locked():
                            led_control.reset_led_to_default(stops_led[stop_id])
