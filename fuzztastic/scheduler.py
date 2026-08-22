# Copyright 2026 Stephan Lipp
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import threading
import time
from collections import namedtuple
from collections.abc import Callable
from typing import Any

IntervalPhase = namedtuple("IntervalPhase", ["duration", "interval"])
Interval = namedtuple("Interval", ["default", "phases"])

INTERVAL_SPEC_FORMAT: str = r"^((?:\d+@\d+;)*)-@(\d+)$"


def parse_interval_spec(interval_spec: str) -> Interval:
    """Parse the interval specification string into an 'Interval' object."""
    match = re.match(INTERVAL_SPEC_FORMAT, interval_spec.replace(" ", ""))

    if not match:
        raise ValueError(f"Invalid interval specification: '{interval_spec}'!")

    phases_str = match.group(1).strip(";")

    phases = []
    dft_interval = int(match.group(2))

    if phases_str:
        acc_duration = 0
        for phase in phases_str.split(";"):
            duration, interval = map(int, phase.split("@"))
            acc_duration += duration
            phases.append(IntervalPhase(duration=acc_duration, interval=interval))

    return Interval(default=dft_interval, phases=phases)


class Scheduler:
    """A scheduler that executes a given task at the specified interval(s)."""

    def __init__(self, interval_spec: str, task: Callable[..., None]) -> None:
        self._interval = parse_interval_spec(interval_spec)
        self._task = task

        self._running = False
        self._start_time = None
        self._thread = None

    def _get_current_interval(self) -> int:
        """Return the current interval based on the elapsed time."""
        assert self._running, "Scheduler is not running!"

        interval = self._interval.default
        elapsed_time = time.time() - self._start_time  # type: ignore

        for phase in self._interval.phases:
            if elapsed_time <= phase.duration:
                interval = phase.interval
                break

        return interval

    def start(self, *args: Any, **kwargs: Any) -> None:
        """Start the scheduler."""
        if self._running:
            raise RuntimeError("Scheduler is already running!")

        self._running = True
        self._start_time = time.time()  # type: ignore

        self._thread = threading.Thread(target=self._run, args=(self._task, args, kwargs), daemon=True)  # type: ignore

        self._thread.start()  # type: ignore

    def _run(self, task: Callable[..., None], args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        """Run the task at the specified interval(s)."""
        while self._running:
            time.sleep(self._get_current_interval())
            task(*args, **kwargs)

    def is_running(self) -> bool:
        """Check if the scheduler is currently running."""
        return self._running

    def stop(self) -> None:
        """Stop the scheduler."""
        if not self._running:
            return

        self._running = False
        self._start_time = None
        self._thread.join()  # type: ignore
        self._thread = None
