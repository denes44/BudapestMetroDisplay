#  MIT License
#
#  Copyright (c) 2024 denes44
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

# ruff: noqa: D101, D102, D103, D107, S101, ANN204, ANN201, ANN001

from datetime import datetime

from BudapestMetroDisplay.aps_helpers import (
    calculate_average_time_between_jobs,
    count_jobs_by_argument,
    find_soonest_job_by_argument,
    get_jobs_by_argument,
)


class MockScheduler:
    def __init__(self):
        self.jobs = []

    def add_job(self, job):
        self.jobs.append(job)

    def get_jobs(self):
        return self.jobs


class MockJob:
    def __init__(self, args=None, next_run_time=None):
        self.args = args or []
        self.next_run_time = next_run_time


def test_count_jobs_by_argument_counts_correctly() -> None:
    scheduler = MockScheduler()
    scheduler.add_job(MockJob(args=[1, 2, 3]))
    scheduler.add_job(MockJob(args=[1, 2, 3]))
    scheduler.add_job(MockJob(args=[4, 5, 6]))
    assert count_jobs_by_argument(scheduler, 2, 1) == 2


def test_count_jobs_by_argument_no_match() -> None:
    scheduler = MockScheduler()
    scheduler.add_job(MockJob(args=[1, 2, 3]))
    scheduler.add_job(MockJob(args=[4, 5, 6]))
    assert count_jobs_by_argument(scheduler, 7, 1) == 0


def test_get_jobs_by_argument_returns_correct_jobs() -> None:
    scheduler = MockScheduler()
    job1 = MockJob(args=[1, 2, 3])
    job2 = MockJob(args=[1, 2, 3])
    job3 = MockJob(args=[4, 5, 6])
    scheduler.add_job(job1)
    scheduler.add_job(job2)
    scheduler.add_job(job3)
    result = get_jobs_by_argument(scheduler, 2, 1)
    assert result == [job1, job2]


def test_get_jobs_by_argument_no_match() -> None:
    scheduler = MockScheduler()
    scheduler.add_job(MockJob(args=[1, 2, 3]))
    scheduler.add_job(MockJob(args=[4, 5, 6]))
    result = get_jobs_by_argument(scheduler, 7, 1)
    assert result == []


def test_find_soonest_job_by_argument_finds_correct_job() -> None:
    scheduler = MockScheduler()
    job1 = MockJob(args=[1, 2, 3], next_run_time=datetime(2024, 1, 1, 12, 0))
    job2 = MockJob(args=[1, 2, 3], next_run_time=datetime(2024, 1, 1, 10, 0))
    job3 = MockJob(args=[4, 5, 6], next_run_time=datetime(2024, 1, 1, 11, 0))
    scheduler.add_job(job1)
    scheduler.add_job(job2)
    scheduler.add_job(job3)
    result = find_soonest_job_by_argument(scheduler, 2, 1)
    assert result == job2


def test_find_soonest_job_by_argument_no_match() -> None:
    scheduler = MockScheduler()
    scheduler.add_job(
        MockJob(args=[1, 2, 3], next_run_time=datetime(2024, 1, 1, 12, 0)),
    )
    scheduler.add_job(
        MockJob(args=[4, 5, 6], next_run_time=datetime(2024, 1, 1, 10, 0)),
    )
    result = find_soonest_job_by_argument(scheduler, 7, 1)
    assert result is None


def calculate_average_time_between_jobs_calculates_correctly() -> None:
    job1 = MockJob(next_run_time=datetime(2024, 1, 1, 10, 0))
    job2 = MockJob(next_run_time=datetime(2024, 1, 1, 11, 0))
    job3 = MockJob(next_run_time=datetime(2024, 1, 1, 12, 0))
    result = calculate_average_time_between_jobs([job1, job2, job3])
    assert result == 3600.0


def calculate_average_time_between_jobs_not_enough_jobs() -> None:
    job1 = MockJob(next_run_time=datetime(2024, 1, 1, 10, 0))
    result = calculate_average_time_between_jobs([job1])
    assert result is None
