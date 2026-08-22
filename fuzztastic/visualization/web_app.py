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

import logging
import threading

import dash
from dash import dcc, html
from dash.dependencies import Input, Output

from fuzztastic.shm import SharedMemory
from fuzztastic.visualization.base import Visualization


class VisualizationApp:
    """Dash application that hosts one or more visualizations."""

    def __init__(self, port: int, visualizations: list[Visualization], bb_metadata: dict, ft_shm: SharedMemory) -> None:
        self._port = port
        self._visualizations = visualizations
        self._bb_metadata = bb_metadata
        self._ft_shm = ft_shm

        self._app = dash.Dash(__name__)

        self._running = False
        self._thread: threading.Thread | None = None

        for i, visualization in enumerate(self._visualizations):
            self._register_callbacks(f"visualization-{i}", visualization)

        self._app.layout = self._create_layout()

    def _register_callbacks(self, visualization_id: str, visualization: Visualization) -> None:
        """Register callbacks for a given visualization."""

        @self._app.callback(
            [Output(f"{visualization_id}-figure", "figure"), Output(f"{visualization_id}-interval", "disabled")],
            [Input(f"{visualization_id}-interval", "n_intervals")],
        )
        def update_figure(_):  # type: ignore
            bb_cov_data = self._ft_shm.read()
            return visualization.update_figure(self._bb_metadata, bb_cov_data), not self._running

    def _create_layout(self) -> html.Div:
        """Create a single-panel or tabbed layout depending on the number of visualizations."""
        intervals = html.Div(
            [
                dcc.Interval(id=f"visualization-{i}-interval", interval=visualization.interval, n_intervals=0)
                for i, visualization in enumerate(self._visualizations)
            ]
        )

        content: dcc.Graph | dcc.Tabs
        if len(self._visualizations) == 1:
            content = dcc.Graph(id="visualization-0-figure", style={"height": "95vh"})
        else:
            content = dcc.Tabs(
                children=[
                    dcc.Tab(
                        label=visualization.label,
                        children=[dcc.Graph(id=f"visualization-{i}-figure", style={"height": "95vh"})],
                    )
                    for i, visualization in enumerate(self._visualizations)
                ]
            )

        return html.Div([intervals, content])

    def start(self) -> None:
        """Start the Dash application in a separate thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        """Run the Dash application."""
        self._app.logger.setLevel(logging.WARNING)
        logging.getLogger("werkzeug").setLevel(logging.WARNING)

        self._app.run(host="0.0.0.0", port=self._port, debug=False, use_reloader=False, threaded=True)

    def is_running(self) -> bool:
        """Check if the Dash application is running."""
        return self._running

    def stop(self) -> None:
        """Stop the Dash application."""
        if not self._running:
            return

        self._running = False
        self._thread = None
