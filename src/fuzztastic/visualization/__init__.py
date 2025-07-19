# Copyright 2021-2025 Chair for Software & Systems Engineering, TUM
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

import threading
import time
from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Dict, List

import dash
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output

from fuzztastic.shm import SharedMemory

Duration = namedtuple("Duration", ["hours", "minutes", "seconds"])


class Visualization(ABC):
    """
    A abstract base class for visualizations.
    """

    def __init__(self, bb_metadata: Dict, shm: SharedMemory, start_time: float, interval: int, port: int) -> None:
        self._bb_metadata = bb_metadata
        self._shm = shm
        self._start_time = start_time
        self._interval = interval
        self._port = port

        self._running = False
        self._stop_event = threading.Event()
        self._thread = None

        self._app = dash.Dash(__name__)
        self._setup_app_layout()
        self._setup_app_callbacks()

    def _setup_app_layout(self) -> None:
        """
        Sets up the app layout.
        """
        self._app.layout = html.Div(
            [
                dcc.Store(id="zoom-state", data={}),
                dcc.Interval(id="interval", interval=self._interval, n_intervals=0),
                dcc.Graph(id="figure", style={"height": "90vh"}),
            ]
        )

    def _setup_app_callbacks(self) -> None:
        """
        Sets up the app update callbacks.
        """

        @self._app.callback(Output("zoom-state", "data"), [Input("figure", "relayout_data")], prevent_initial_call=True)
        def update_zoom_state(relayout_data: Dict) -> Dict:
            return self._update_zoom_state(relayout_data)

        @self._app.callback(
            Output("figure", "figure"),
            [Input("interval", "n_intervals")],
            [dash.dependencies.State("zoom-state", "data")],
        )
        def update_figure(n_interval: int, zoom_state: Dict) -> go.Figure:
            # Read the BB coverage data from SHM segment
            bb_cov_data = self._shm.read()

            return self._update_figure(bb_cov_data, zoom_state)

    @abstractmethod
    def _update_zoom_state(self, relayout_data: Dict) -> Dict:
        """
        Updates the zoom state based on the current app interaction.
        """
        pass

    @abstractmethod
    def _update_figure(self, bb_cov_data: List[int], zoom_state: Dict) -> go.Figure:
        """
        Updates the figure with the current coverage data.
        """
        pass

    def _get_fuzzing_duration(self) -> Duration:
        """
        Returns the current fuzzing duration.
        """
        elapsed_time = time.time() - self._start_time

        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        return Duration(int(hours), int(minutes), int(seconds))

    def start(self) -> None:
        """
        Starts the visualization.
        """
        if self._running:
            raise RuntimeError("Visualization is already running!")

        self._running = True

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)  # type: ignore

        self._thread.start()  # type: ignore

    def _run(self) -> None:
        """
        Runs the visualization web app server.
        """
        self._app.run(port=self._port, debug=False, use_reloader=False, threaded=True)

    def is_running(self) -> bool:
        """
        Checks if the visualization is currently running.
        """
        return self._running

    def stop(self) -> None:
        """
        Stops the visualization.
        """
        if not self._running:
            return

        self._running = False
        self._stop_event.set()
        self._thread = None
