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

from typing import Optional, Any

from apscheduler.job import Job
from apscheduler.schedulers.base import BaseScheduler
import numpy as np


def count_jobs_by_argument(
        scheduler: BaseScheduler, search_value: Any, arg_position: int
) -> int:
    """
    Count the number of jobs in a BaseScheduler which matches the search value

    :param scheduler: BackgroundScheduler instance
    :param search_value: The value to match the argument with
    :param arg_position: The index of the argument we want to compare
    :return: The number of jobs in which the argument matches the search value
    """
    i = 0
    for job in scheduler.get_jobs():
        job_args = job.args
        if len(job_args) > arg_position and job_args[arg_position] == search_value:
            i += 1
    return i


def get_jobs_by_argument(
        scheduler: BaseScheduler, search_value: Any, arg_position: int
) -> list[Job]:
    """
    Returns the jobs from a BaseScheduler which arguments matches the search value

    :param scheduler: BackgroundScheduler instance
    :param search_value: The value to match the argument with
    :param arg_position: The index of the argument we want to compare
    :return: The jobs that are matches the search value
    """
    jobs = scheduler.get_jobs()
    filtered_jobs = []

    for job in jobs:
        job_args = job.args
        # Check if the argument matches
        if len(job_args) > arg_position and job.args[arg_position] == search_value:
            filtered_jobs.append(job)

    return filtered_jobs


def find_soonest_job_by_argument(
        scheduler: BaseScheduler, search_value: Any, arg_position: int
) -> Optional[Job]:
    """
    Find the soonest job based on the next run time, filtered by a specific argument.

    :param scheduler: The APScheduler instance.
    :param search_value: The value to match the argument with
    :param arg_position: The index of the argument we want to compare
    :return:
    """
    soonest_job = None
    for job in scheduler.get_jobs():
        job_args = job.args
        # Check if the job has the specified argument and value
        if len(job_args) > arg_position and job_args[arg_position] == search_value:
            if soonest_job is None or (
                    job.next_run_time and
                    job.next_run_time < soonest_job.next_run_time
            ):
                soonest_job = job

    return soonest_job


def calculate_average_time_between_jobs(filtered_jobs: list[Job]) -> Optional[float]:
    """
    Calculates the average time between the jobs supplied in a list

    :param filtered_jobs: A list of Jobs to check
    :return: Return the average time between jobs in seconds,
        or None, when the time cannot be determined
    """
    # Extract the next run times and sort them
    run_times = [job.next_run_time for job in filtered_jobs if job.next_run_time]
    run_times = sorted(run_times)

    if len(run_times) < 2:
        return None  # Not enough jobs to calculate time difference

    # Calculate differences in seconds
    time_differences = [
        (run_times[i] - run_times[i - 1]).total_seconds()
        for i in range(1, len(run_times))
    ]

    # Calculate average difference
    average_diff = np.mean(time_differences) if time_differences else None
    return average_diff
