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

import time
from abc import ABC, abstractmethod
from collections import namedtuple
from enum import StrEnum

import plotly.graph_objects as go

Duration = namedtuple("Duration", ["hours", "minutes", "seconds"])


class VisualizationType(StrEnum):
    """Enumeration of visualization types."""

    TREEMAP = "treemap"


class Visualization(ABC):
    """A abstract base class for visualizations."""

    def __init__(self, start_time: float, interval: int, label: str) -> None:
        self._start_time = start_time
        self._interval = interval * 1000
        self._label = label

    @property
    def interval(self) -> int:
        """Update interval in milliseconds."""
        return self._interval

    @property
    def label(self) -> str:
        """Visualization label."""
        return self._label

    def _get_fuzzing_duration(self) -> Duration:
        """Return the current fuzzing duration."""
        elapsed_time = time.time() - self._start_time

        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        return Duration(int(hours), int(minutes), int(seconds))

    @abstractmethod
    def update_figure(self, bb_metadata: dict, bb_cov_data: list[int]) -> go.Figure:
        """Update the figure with the current coverage data."""
        pass
