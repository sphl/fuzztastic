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

from collections import defaultdict, namedtuple
from concurrent.futures import ThreadPoolExecutor
from itertools import chain

import pandas as pd
import plotly.graph_objects as go

from fuzztastic.utils.math import avg, div
from fuzztastic.visualization import Visualization

BBInfo = namedtuple("BBInfo", ["id", "lines", "hit_count"])


def to_tree_dict(bb_metadata: dict, bb_cov_data: list[int]) -> dict:
    """
    Converts basic block metadata and coverage data into a (nested) dictionary structure.
    """
    bb_cov_tree_dict: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for bb in bb_metadata:
        bb_cov_tree_dict[bb["program"]][bb["file"]][bb["function"]].append(
            BBInfo(bb["id"], bb["lines"], bb_cov_data[bb["id"]])
        )

    return bb_cov_tree_dict


def to_tree_dataframe(bb_metadata: dict, bb_cov_data: list[int]) -> pd.DataFrame:
    """
    Converts basic block metadata and coverage data into a table structure.
    """

    def to_tree_entry(id: str, label: str, value: int, hit_count: int, parent: str) -> dict:
        return {"ids": id, "labels": label, "values": value, "hit_counts": hit_count, "parents": parent}

    bb_cov_tree_dict = to_tree_dict(bb_metadata, bb_cov_data)

    bb_cov_tree_list = []

    args = []
    for program, files in bb_cov_tree_dict.items():
        program_id = program
        program_hit_count = int(
            avg([bb.hit_count for file in files.values() for function in file.values() for bb in function])
        )

        bb_cov_tree_list.append(to_tree_entry(program_id, program, 0, program_hit_count, ""))

        for file, functions in files.items():
            args.append((program_id, file, functions))

    def process_file(program_id: str, file: str, functions: dict[str, list[BBInfo]]) -> list[dict]:
        entries = []

        file_id = f"{program_id}::{file}"
        file_hit_count = int(avg([bb.hit_count for function in functions.values() for bb in function]))

        entries.append(to_tree_entry(file_id, file, 0, file_hit_count, program_id))

        for function, basic_blocks in functions.items():
            function_id = f"{file_id}::{function}"
            function_hit_count = int(avg([bb.hit_count for bb in basic_blocks]))

            entries.append(to_tree_entry(function_id, function, 0, function_hit_count, file_id))

            for bb in basic_blocks:
                bb_id = f"{function_id}::BB_{bb.id}"
                bb_line_range = f"{min(bb.lines)}-{max(bb.lines)}" if len(bb.lines) > 1 else str(bb.lines[0])
                bb_label = f"BB {bb.id} (L:{bb_line_range})"

                entries.append(to_tree_entry(bb_id, bb_label, len(bb.lines), bb.hit_count, function_id))

        return entries

    with ThreadPoolExecutor() as executor:
        bb_cov_tree_list.extend(chain.from_iterable(executor.map(lambda arg: process_file(*arg), args)))

    return pd.DataFrame(bb_cov_tree_list)


class TreemapVisualization(Visualization):
    """
    A class for visualizing code coverage using a treemap.
    """

    def _update_figure(self, bb_cov_data: list[int]) -> go.Figure:
        """
        Updates the treemap figure with the current coverage data.
        """
        bb_cov_tree_df = to_tree_dataframe(self._bb_metadata, bb_cov_data)

        bb_cov_tree_df["hit_count_labels"] = bb_cov_tree_df["labels"].apply(
            lambda s: "# BB Executions" if "BB" in s else "Avg. # BB Executions"
        )

        fuzzing_dur = self._get_fuzzing_duration()
        bb_coverage = avg([1 if hc > 0 else 0 for hc in bb_cov_data])

        figure = go.Figure(
            go.Treemap(
                ids=bb_cov_tree_df["ids"],
                labels=bb_cov_tree_df["labels"],
                values=bb_cov_tree_df["values"],
                parents=bb_cov_tree_df["parents"],
                customdata=bb_cov_tree_df[["hit_count_labels", "hit_counts"]],
                textinfo="label",
                textposition="middle center",
                hovertemplate="<b>%{label}</b><br>%{customdata[0]}: %{customdata[1]}<extra></extra>",
                marker=dict(
                    colors=bb_cov_tree_df["hit_counts"],
                    line=dict(width=1, color="lightgray"),
                    colorscale=[
                        (0.0, "white"),
                        (div(1, max(bb_cov_data), 0.00001), "lightyellow"),
                        (0.2, "yellow"),
                        (0.4, "orange"),
                        (0.6, "red"),
                        (0.8, "darkred"),
                        (1.0, "black"),
                    ],
                    showscale=True,
                    colorbar=dict(title="# BB Executions", tickformat=",d"),
                ),
            )
        )

        layout = dict(
            title=dict(
                text=f"FuzzTastic Coverage Treemap<br><sub>Fuzzing Duration: {fuzzing_dur.hours}h {fuzzing_dur.minutes}m {fuzzing_dur.seconds}s | Basic Block Coverage: {bb_coverage:.2%}</sub>",
                font=dict(size=22),
                x=0.5,
            ),
            uirevision="constant",
            margin=dict(t=150, b=50, l=50, r=50),
        )

        figure.update_layout(**layout)

        return figure
