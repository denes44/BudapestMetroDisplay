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
import time as time2
from datetime import datetime, time, timedelta
from random import randint
from typing import Any

import requests
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from BudapestMetroDisplay import aps_helpers
from BudapestMetroDisplay._version import __version__
from BudapestMetroDisplay.config import settings
from BudapestMetroDisplay.model import Route, StopId

logger = logging.getLogger(__name__)
# Set the logging level for urllib3 to INFO
logging.getLogger("urllib3").setLevel(logging.INFO)
# Set the logging level for requests to INFO
logging.getLogger("requests").setLevel(logging.INFO)

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

# Set the minimum log level for APScheduler
logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)
logging.getLogger("apscheduler.scheduler").setLevel(logging.WARNING)

# Initialize APScheduler with a persistent job store
# for scheduling the arrival and departure updates
departure_scheduler: BackgroundScheduler = BackgroundScheduler(
    jobstores={"default": MemoryJobStore()},  # Use in-memory job storage
)
departure_scheduler.start()

# Initialize scheduler with MemoryJobStore for scheduling the API updates
api_update_scheduler: BackgroundScheduler = BackgroundScheduler(
    jobstores={"default": MemoryJobStore()},  # Use in-memory job storage
)
api_update_scheduler.start()


def create_schedule_updates(
    route: Route,
    schedule_type: str,
    delay: int = 0,
) -> None:
    """Create jobs to update the data for the provided route.

    The method puts the jobs in APScheduler, which later will make the API calls.

    :param route: A Route object we want to update
    :param schedule_type: REGULAR or REALTIME
    :param delay: An extra delay in seconds for the start of the job
    affects the API update parameters
    """
    # Check if the supplied schedule_type parameter is valid,
    # and the API call parameters are available in API_SCHEDULE_PARAMETERS
    if schedule_type not in API_SCHEDULE_PARAMETERS:
        logger.error(f"Invalid schedule type request: {schedule_type}")
        return

    logger.info(
        f"Starting updating the {schedule_type} schedules for route {route.name}.",
    )

    job_time: datetime = datetime.now() + timedelta(seconds=delay)  # job start time
    job_id: str = f"{route.name}_{schedule_type}"  # job reference id

    # Add the job to the scheduler
    api_update_scheduler.add_job(
        fetch_schedule_for_route,
        trigger="date",
        run_date=job_time,
        args=[route, schedule_type],
        id=job_id,
        replace_existing=True,
        # If the job exists, it will be replaced with the new time
    )

    logger.debug(
        f"Scheduling {schedule_type} API updates for route "
        f"{route.name} at {job_time!s}.",
    )


def create_alert_updates(route: Route, delay: int = 0) -> None:
    """Create jobs in APScheduler to update the alerts for the provided route.

    The method puts the job in APScheduler, which later will make the API calls.

    :param route: A Route object we want to update
    :param delay: An extra delay in seconds for the start of the job
    affects the API update parameters
    """
    # Store the current time when we started the update process
    start_time = datetime.now()

    logger.info(f"Starting updating the alerts for route {route.name}")

    job_time: datetime = start_time + timedelta(seconds=delay)  # job start time
    job_id: str = f"{route.route_id}_ALERTS"  # job reference id

    # Add the job to the scheduler
    api_update_scheduler.add_job(
        fetch_alerts_for_route,
        trigger="date",
        run_date=job_time,
        args=[route],
        id=job_id,
        replace_existing=True,
        # If the job exists, it will be replaced with the new time
    )

    logger.debug(
        f"Scheduling alerts API updates for route {route.name} at {job_time!s}.",
    )


def fetch_schedule_for_route(
    route: Route,
    schedule_type: str,
) -> None:
    """Send API request to fetch the schedule for the selected stops.

    Callback function for the APScheduler jobs.
    Makes an arrivals-and-departures-for-stop API request to the BKK OpenData server
    for the selected stops.

    :param route: A Route object we want to get the schedules for
    :param schedule_type: REGULAR or REALTIME, affects the API update parameters
    """
    start = time2.perf_counter()

    # Calculate the next schedule time
    if schedule_type == "REALTIME" and (
        time(0, 30) <= datetime.now().time() <= time(4, 0)
    ):
        # When the current time is between 00:30 and 04:00,
        # schedule the next REALTIME update for 04:00
        job_time = datetime.combine(datetime.today(), time(4, 0))
    else:
        # Otherwise schedule the next update according to the configuration
        job_time = (
            datetime.now() + API_SCHEDULE_PARAMETERS[schedule_type]["nextSchedule"]
        )

    url: str = f"{settings.bkk.api_base_url}arrivals-and-departures-for-stop"

    headers: dict[str, str] = {"Accept": "application/json"}

    # Get schedule data for all stops in the stop set
    params: dict[str, str | int | list[str]] = {
        "stopId": route.get_stop_ids(string_only=True),
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
            # Recalculate schedule intervals for REGULAR updates
            if schedule_type == "REGULAR":
                calculate_schedule_interval((response.json()), route)

            latest_departure_time: int = process_schedule(response.json(), route)

            if schedule_type != "REALTIME" and latest_departure_time == -1:
                job_time = datetime.now() + timedelta(minutes=1)
                logger.debug(
                    f"There were no departures during {schedule_type} schedule update "
                    f"for route {route.name}. "
                    f"Next update scheduled for {job_time!s}",
                )
            elif (
                schedule_type != "REALTIME"
                and datetime.fromtimestamp(latest_departure_time) < job_time
            ):
                job_time = datetime.fromtimestamp(latest_departure_time) - timedelta(
                    minutes=5,
                )
                logger.debug(
                    f"The calculated next {schedule_type} schedule update "
                    f"for route {route.name} is later than the last departure "
                    f"we stored, so next update time was adjusted accordingly. "
                    f"Next update scheduled for {job_time!s}",
                )
            else:
                message: str = (
                    f"Successfully updated {schedule_type} schedules for route "
                    f"{route.name}. Next update scheduled for {job_time!s}"
                )

                if schedule_type == "REGULAR":
                    logger.debug(message)
                else:
                    logger.trace(message)  # type: ignore[attr-defined]
        else:
            # Reschedule the failed action for 1 minute later
            job_time = datetime.now() + timedelta(minutes=1)

            logger.error(
                f"Failed to update {schedule_type} schedules for route "
                f"{route.name}: {response.status_code}. "
                f"Rescheduled for {job_time!s}.",
            )
    except requests.exceptions.JSONDecodeError as e:
        job_time = datetime.now() + timedelta(minutes=1)
        logger.warning(
            "The response did not contain valid JSON data when updating "
            f"{schedule_type} schedules for route {route.name}. "
            f"Rescheduled for {job_time!s}.",
        )
        logger.warning(e)
    except requests.exceptions.InvalidJSONError as e:
        job_time = datetime.now() + timedelta(minutes=1)
        logger.warning(
            "The response contained invalid JSON data when updating "
            f"{schedule_type} schedules for route {route.name}. "
            f"Rescheduled for {job_time!s}.",
        )
        logger.warning(e)
    except requests.exceptions.ReadTimeout as e:
        job_time = datetime.now() + timedelta(minutes=1)
        logger.warning(
            f"Timeout occurred when updating {schedule_type} schedules for route "
            f"{route.name}. Rescheduled for {job_time!s}.",
        )
        logger.warning(e)
    except requests.exceptions.ConnectionError as e:
        job_time = datetime.now() + timedelta(minutes=5)
        logger.warning(
            f"Connection error when updating {schedule_type} schedules for route "
            f"{route.name}. Rescheduled for {job_time!s}.",
        )
        logger.warning(e)
    except requests.exceptions.RequestException as e:
        job_time = datetime.now() + timedelta(minutes=1)
        logger.warning(
            f"Error when updating {schedule_type} schedules for route {route.name}."
            f"Rescheduled for {job_time!s}.",
        )
        logger.warning(e)

    job_id: str = f"{route.name}_{schedule_type}"

    api_update_scheduler.add_job(
        fetch_schedule_for_route,
        trigger="date",
        run_date=job_time,
        args=[route, schedule_type],
        id=job_id,
        replace_existing=True,
        # If the job exists, it will be replaced with the new time
    )

    end = time2.perf_counter()

    logger.debug(f"Execution time: {end - start:.6f} seconds")


def fetch_alerts_for_route(route: Route) -> None:
    """Send an API request to fetch the alerts for a selected route.

    Callback function for the APScheduler jobs.
    Makes a route-details API request to the BKK OpenData server
    for the supplied route_id.

    :param route: A Route object we want to update
    """
    # Calculate the next schedule time
    job_time = datetime.now() + timedelta(seconds=settings.bkk.api_update_alerts)

    url: str = f"{settings.bkk.api_base_url}route-details"

    headers: dict[str, str] = {"Accept": "application/json"}

    params: dict[str, str | int] = {
        "routeId": route.route_id,
        "appVersion": f"BudapestMetroDisplay {__version__}",
        "version": "4",
        "includeReferences": "alerts",
        "key": settings.bkk.api_key,
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)

        if response.status_code == 200:
            process_alerts(response.json(), route, is_alert_only=True)

            logger.debug(
                f"Successfully updated alerts for route {route.name}. "
                f"Next update scheduled for {job_time!s}",
            )
        else:
            # Reschedule the failed action for 1 minute later
            job_time = datetime.now() + timedelta(minutes=1)

            logger.error(
                f"Failed to update alerts for route {route.name}, "
                f" HTTP {response.status_code}. "
                f"Rescheduled for {job_time!s}.",
            )
    except requests.exceptions.JSONDecodeError as e:
        job_time = datetime.now() + timedelta(minutes=1)
        logger.warning(
            "The response did not contain valid JSON data when updating "
            f"alerts for route {route.name}. "
            f"Next update scheduled for {job_time!s}",
        )
        logger.warning(e)
    except requests.exceptions.InvalidJSONError as e:
        job_time = datetime.now() + timedelta(minutes=1)
        logger.warning(
            "The response contained invalid JSON data when updating "
            f"alerts for route {route.name}. "
            f"Next update scheduled for {job_time!s}",
        )
        logger.warning(e)
    except requests.exceptions.ReadTimeout as e:
        job_time = datetime.now() + timedelta(minutes=1)
        logger.warning(
            f"Timeout occurred when updating alerts for route {route.name}. "
            f"Next update scheduled for {job_time!s}",
        )
        logger.warning(e)
    except requests.exceptions.ConnectionError:
        job_time = datetime.now() + timedelta(minutes=5)
        logger.exception(
            f"Connection error when updating alerts for route {route.name}. "
            f"Next update scheduled for {job_time!s}",
        )
    except requests.exceptions.RequestException:
        job_time = datetime.now() + timedelta(minutes=1)
        logger.exception(
            f"Error when updating alerts for route {route.name}. "
            f"Next update scheduled for {job_time!s}",
        )

    job_id: str = f"{route.route_id}_ALERTS"

    api_update_scheduler.add_job(
        fetch_alerts_for_route,
        trigger="date",
        run_date=job_time,
        args=[route],
        id=job_id,
        replace_existing=True,
        # If the job exists, it will be replaced with the new time
    )


def process_schedule(json_response: Any, route: Route) -> int:
    """Process the API response and store the departures.

    Processes the ArrivalsAndDeparturesForStopOTPMethodResponse API response
    from the arrivals-and-departures-for-stop method.
    As a result, stores the retrieved departures in an APScheduler instance
    which will control the vehicle_present status of the StopIds.

    :param json_response: JSON return data from the BKK OpenData API
    :param route: The Route that the schedule data belongs to
    :return: Timestamp of the latest departure in the data provided,
        -1 if there are no valid departures
    """
    # Check if JSON looks valid
    if (
        not json_response
        or "data" not in json_response
        or "entry" not in json_response["data"]
    ):
        logger.error(
            f"No valid schedule data in API response for route {route.name}",
        )
        return -1

    # Check if we exceeded the query limit
    if json_response["data"].get("limitExceeded", "false") == "true":
        logger.warning(f"Query limit is exceeded when updating route {route.name}")

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
        route_id = next(json_response["data"]["references"]["routes"].keys())
    else:
        logger.warning(
            f"No route IDs found or the list is empty when updating route {route.name}",
        )
        return -1

    # Check if the routeId from the data matches the Route
    if route_id != route.route_id:
        logger.warning(
            f"Route IDs from the data doesn't match with the "
            f"supplied route {route.name} when storing schedule data",
        )
        return -1

    # Get stopId when there is only one stop in the response
    stop_id_global: str = json_response["data"]["entry"].get("stopId", None)

    # Get stopTimes from TransitArrivalsAndDepartures
    stop_times = json_response["data"]["entry"].get("stopTimes", [])
    if len(stop_times) == 0:
        logger.trace(  # type: ignore[attr-defined]
            f"No schedule data found when updating route {route.name}",
        )

    latest_departure_time: int = -1
    # Iterate through the TransitScheduleStopTimes in the TransitArrivalsAndDepartures
    for stop_time in stop_times:
        trip_id: str = stop_time.get("tripId")

        # Get stopId when the response contains schedules for multiple stops
        stop_id = stop_time.get("stopId") if "stopId" in stop_time else stop_id_global

        # Check if we are interested in the provided stopId
        if stop_id not in route.get_stop_ids(string_only=True):
            logger.debug(
                f"Got update for stop ID {stop_id}, route {route.name}, "
                f"but we don't need that, skipping",
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
            # let's use the difference between them for the departure delay
            if stop_time.get("predictedArrivalTime") != stop_time.get(
                "predictedDepartureTime",
            ):
                arrival_time = stop_time.get("predictedArrivalTime")
                delay = stop_time.get("predictedDepartureTime") - stop_time.get(
                    "predictedArrivalTime",
                )
            # Arrival time is the same as the departure,
            # use predefined delay for departure delay
            else:
                arrival_time = stop_time.get(
                    "predictedDepartureTime",
                ) - calculate_departure_delay(route)
                delay = calculate_departure_delay(route)
        # CASE #2: Only predicted arrival time is available
        # [end stop with realtime data]
        # Use the predefined delay for departure delay
        elif "predictedArrivalTime" in stop_time and not stop_time.get(
            "uncertain",
            False,
        ):
            arrival_time = stop_time.get(
                "predictedArrivalTime",
            ) - calculate_departure_delay(route)
            delay = calculate_departure_delay(route)
        # CASE #3: Only predicted departure time is available
        # [start stop with realtime data]
        # Use the predefined delay for departure delay
        elif "predictedDepartureTime" in stop_time and not stop_time.get(
            "uncertain",
            False,
        ):
            arrival_time = stop_time.get(
                "predictedDepartureTime",
            ) - calculate_departure_delay(route)
            delay = calculate_departure_delay(route)
        # CASE #4: Both arrival and departure time available as scheduled time
        # [middle stop, no realtime data]
        elif "arrivalTime" in stop_time and "departureTime" in stop_time:
            # Arrival time is different from the departure,
            # let's use the difference between them for the departure delay
            if stop_time.get("arrivalTime") != stop_time.get("departureTime"):
                arrival_time = stop_time.get("arrivalTime") + randint(-3, 3)
                delay = stop_time.get("departureTime") - stop_time.get("arrivalTime")
            # Arrival time is the same as the departure,
            # use predefined delay for departure delay
            else:
                arrival_time = (
                    stop_time.get("departureTime")
                    - calculate_departure_delay(route)
                    + randint(-3, 3)
                )
                delay = calculate_departure_delay(route)
        # CASE #5: Only scheduled arrival time is available
        # [end stop with no realtime data]
        # Use the predefined delay for departure delay
        elif "arrivalTime" in stop_time:
            arrival_time = (
                stop_time.get("arrivalTime")
                - calculate_departure_delay(route)
                + randint(-3, 3)
            )
            delay = calculate_departure_delay(route)
        # CASE #6: Only scheduled departure time is available
        # [start stop with no realtime data]
        # Use the predefined delay for departure delay
        elif "departureTime" in stop_time:
            arrival_time = (
                stop_time.get("departureTime")
                - calculate_departure_delay(route)
                + randint(-3, 3)
            )
            delay = calculate_departure_delay(route)
        # CASE #7: No valid time data is available
        else:
            logger.debug(
                f"No valid arrival/departure time found "
                f"when updating stop {stop_id}, route {route.name}",
            )
            continue

        # We processed valid schedule data for this stop,
        # that means that the stop is operational
        if not route.get_stop_id(stop_id).in_service:
            route.get_stop_id(stop_id).in_service = True

        # Schedule the action before the departure."""
        job_id: str = f"{stop_id}+{trip_id}_arrival"
        job_time: datetime = datetime.fromtimestamp(arrival_time)

        latest_departure_time = max(latest_departure_time, arrival_time)

        if job_time > datetime.now():
            departure_scheduler.add_job(
                vehicle_arrival,
                trigger="date",
                run_date=job_time,
                args=[route.get_stop_id(stop_id), trip_id, job_time, delay],
                id=job_id,
                replace_existing=True,
                # If the job exists, it will be replaced with the new time
            )

            logger.trace(  # type: ignore[attr-defined]
                f"Scheduled action for departure: stop_id={stop_id}, "
                f"trip_id={trip_id}, route {route.name}, "
                f"departure_time={datetime.fromtimestamp(arrival_time)!s}",
            )
        else:
            logger.trace(  # type: ignore[attr-defined]
                f"Action for departure: stop_id={stop_id}, trip_id={trip_id}, "
                f"route {route.name}, "
                f"departure_time={datetime.fromtimestamp(arrival_time)!s} "
                f"was in the past, skipping",
            )

    # Check if there are any active alerts in the response and process them
    alerts = json_response["data"]["entry"].get("alertIds", [])
    if len(alerts) > 0:
        process_alerts(json_response, route)

    return latest_departure_time


def process_alerts(
    json_response: Any,
    route: Route,
    *,
    is_alert_only: bool = False,
) -> None:
    """Process API response to determine the interval between schedules for a route.

    Process the ArrivalsAndDeparturesForStopOTPMethodResponse API response
    from the arrivals-and-departures-for-stop method.
    It checks time between the schedules for each route
    and updates the ACTION_DELAY dictionary accordingly.

    :param json_response: JSON return data from the BKK OpenData API
    :param route: The Route that the alert data belongs to
    :param is_alert_only: If True, the API data comes from an alert-only update,
        not a regular schedule update
    :return:
    """
    # Check if JSON looks valid
    if (
        not json_response
        or "data" not in json_response
        or "references" not in json_response["data"]
        or "alerts" not in json_response["data"]["references"]
    ):
        logger.error(f"No valid alerts data in API response for route {route.name}")
        return

    alerts = json_response["data"]["references"].get("alerts")
    if len(alerts) == 0:
        logger.trace(  # type: ignore[attr-defined]
            f"No alert data found when updating route {route.name}",
        )

    # Iterate through the TransitScheduleStopTimes in the TransitArrivalsAndDepartures
    for alert_details in alerts.values():
        # If the start time of the alert is in the future, return False
        if alert_details["start"] > datetime.now().timestamp():
            continue

        # Iterate the TransitAlertRoutes in the TransitAlert
        for alert_route in alert_details["routes"]:
            effect_type: str = alert_route.get("effectType", "")

            # If the effectType is not NO_SERVICE,
            # we don't process the TransitAlertRoute anymore
            if effect_type != "NO_SERVICE":
                continue

            # Iterate through stopIds in the TransitAlertRoute
            for stop_id in alert_route.get("stopIds", []):
                # Check if we are interested in the stopId
                if stop_id not in route.get_stop_ids(string_only=True):
                    continue

                sid = route.get_stop_id(stop_id)
                # Check whether the stop is operational now
                if sid.in_service:
                    # Check if we have a schedule for this stop_id,
                    # because if we have, then the stop is not really out of service
                    soonest_job = aps_helpers.find_soonest_job_by_argument(
                        departure_scheduler,
                        stop_id,
                        0,
                    )

                    if soonest_job is not None:
                        # We found at least one schedule for this stop,
                        # so we'll ignore the NO_SERVICE alert
                        logger.debug(
                            f"Found NO_SERVICE alert {alert_details['id']} "
                            f"for {sid.stop.name}, route {route.name}, "
                            f"but there are active schedules for that stop, "
                            f"so we'll ignore that",
                        )
                    else:
                        # No schedule found for this stop,
                        # so we'll process the NO_SERVICE alert
                        logger.debug(
                            f"Found NO_SERVICE alert {alert_details['id']} "
                            f"for {sid.stop.name}, route {route.name}",
                        )
                        # Set the operation state of this StopId
                        sid.in_service = False

                        # Update the regular schedule data for the route
                        # because of the active alert
                        if is_alert_only:
                            create_schedule_updates(route, "REGULAR")


def vehicle_arrival(
    stop_id: StopId,
    trip_id: str,
    job_time: datetime,
    delay: int,
) -> None:
    """Execute actions for a vehicle arrival.

    Callback function for a stop schedule.
    Changes the vehicle_present property of the StopId to True,
    and schedules another action to turn it back to False after the delay.

    :param stop_id: The StopId object the departure is related to
    :param trip_id: tripId from the BKK OpenData API
    :param job_time: The time this job was scheduled in APScheduler
    :param delay: The amount of time needs to be elapsed in seconds
        between the turn-on and turn-off action
    """
    if job_time < datetime.now() - timedelta(seconds=20):
        logger.trace(  # type: ignore[attr-defined]
            "Action trigger time is in the past, skipping",
        )
        return

    logger.trace(  # type: ignore[attr-defined]
        f"Vehicle arrived for stop: {stop_id.stop.name}, "
        f"route: {stop_id.stop.route.name}, "
        f"trip: {trip_id}, departing after: {delay} sec",
    )

    stop_id.vehicle_present = True

    # Schedule an action at the departure time to turn vehicle_present to False
    job_time_departure = job_time + timedelta(seconds=delay)
    job_id: str = f"{stop_id.stop_id}+{trip_id}_departure"

    departure_scheduler.add_job(
        vehicle_departure,
        trigger="date",
        run_date=job_time_departure,
        args=[stop_id, trip_id, job_time_departure],
        id=job_id,
        replace_existing=True,
        # If the job exists, it will be replaced with the new time
    )


def vehicle_departure(
    stop_id: StopId,
    trip_id: str,
    job_time: datetime,
) -> None:
    """Execute actions for a vehicle departure.

    Callback function for a stop schedule.
    Changes the vehicle_present property of the StopId to False.

    :param stop_id: The StopId object the departure is related to
    :param trip_id: tripId from the BKK OpenData API
    :param job_time: The time this job was scheduled in APScheduler
    """
    if job_time < datetime.now() - timedelta(seconds=20):
        logger.trace(  # type: ignore[attr-defined]
            "Action trigger time is in the past, skipping",
        )
        return

    logger.trace(  # type: ignore[attr-defined]
        f"Vehicle departure for stop: {stop_id.stop.name}, "
        f"route: {stop_id.stop.route.name}, "
        f"trip: {trip_id}",
    )

    stop_id.vehicle_present = False


def calculate_schedule_interval(json_response: Any, route: Route) -> None:
    """Process API response to determine the interval between schedules for a route.

    Process the ArrivalsAndDeparturesForStopOTPMethodResponse API response
    from the arrivals-and-departures-for-stop method.
    It checks time between the schedules for each route
    and updates the Route's schedule_interval property accordingly.

    :param json_response: JSON return data from the BKK OpenData API
    :param route: The Route that the schedule data belongs to
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
            f"for schedule intervals for route {route.name}",
        )
        return

    # Check if we exceeded the query limit
    if json_response["data"].get("limitExceeded", "false") == "true":
        logger.warning(
            f"Query limit is exceeded when updating "
            f"schedule intervals for route {route.name}",
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
        route_id = next(json_response["data"]["references"]["routes"].keys())
    else:
        logger.warning(
            f"No route IDs found or the list is empty when updating "
            f"schedule intervals for route {route.name}",
        )
        return

    # Check if the routeId from the data matches the Route
    if route_id != route.route_id:
        logger.warning(
            f"Route IDs from the data doesn't match with the "
            f"supplied route {route.name}",
        )
        return

    # Get stopTimes from TransitArrivalsAndDepartures
    stop_times = json_response["data"]["entry"].get("stopTimes", [])
    if len(stop_times) < 2:
        logger.debug(
            f"Not enough schedule data found when updating "
            f"schedule intervals for route {route.name}",
        )
        return

    # Variable to store the necessary data from the first two relevant stops
    stop_id: str = stop_times[0].get("stopId", "")
    stop_headsign: str = stop_times[0].get("stopHeadsign", "")
    field: str

    if stop_times[0].get("departureTime") is not None:
        field = "departureTime"
    else:
        field = "arrivalTime"
    last_time: int = stop_times[0].get(field, 0)

    deltas: list[int] = []

    # Iterate through the TransitScheduleStopTimes
    # in the TransitArrivalsAndDepartures
    for stop_time in stop_times[1:]:  # skip the first item
        # Check if the stopId and stopHeadsign are the same as the first one
        if (
            stop_time.get("stopId") != stop_id
            or stop_time.get("stopHeadsign") != stop_headsign
        ):
            continue

        current_time: int = stop_time.get(field, 0)
        delta: int = current_time - last_time
        deltas.append(delta)
        last_time = current_time

    avg = sum(deltas) / len(deltas) / 60 if deltas else -1

    # Store result
    route.schedule_interval = avg

    logger.debug(
        f"Recalculated departure delay for route {route.name}, schedule interval:  "
        f"{avg:.1f} min, delay: {calculate_departure_delay(route)} sec",
    )


def calculate_departure_delay(route: Route) -> int:
    """Calculate departure delay according to the average schedule interval of a Route.

    :param route: The Route object for the calculation
    :return: The departure delay in seconds
    """
    delay: int = 0

    if route.schedule_interval >= 0:
        if route.type == "subway":
            if route.schedule_interval <= 2:
                delay = 15
            elif route.schedule_interval < 5.5:
                delay = 20
            else:
                delay = 30
        elif route.type == "railway":
            if route.schedule_interval < 5.5:
                delay = 20
            elif route.schedule_interval < 10.5:
                delay = 30
            else:
                delay = 45
    # No valid schedule data found, set the default delay
    elif route.schedule_interval == -1:
        if route.type == "subway":
            delay = 30
        elif route.type == "railway":
            delay = 45

    return delay
