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

import json
import logging
import time
from pathlib import Path
from typing import Annotated

import typer

from fuzztastic import DEFAULT_CONFIG_FILE, Config
from fuzztastic.scheduler import Scheduler
from fuzztastic.shm import SharedMemory
from fuzztastic.utils.fs import is_likely_file
from fuzztastic.utils.io import write_text
from fuzztastic.utils.proc import run_shell_command
from fuzztastic.visualization import Visualization
from fuzztastic.visualization.treemap import TreemapVisualization

FT_ENVVAR_SHM_NAME: str = "FT_SHM_NAME"
FT_ENVVAR_BB_COUNT: str = "FT_BB_COUNT"

DEFAULT_OUTPUT_FILE: Path = Path.cwd() / "output.txt"
DEFAULT_SHM_NAME: str = "fuzztastic_shm"


def persist_cov_data(output_path: Path, is_file: bool, start_time: float, shm: SharedMemory) -> None:
    """
    Stores the new coverage data in the output file.
    """
    report_time = time.time()
    report_file = output_path if is_file else output_path / f"ft_cov_{int(report_time)}.json"

    cov_data = shm.read()
    cov_data_json = {"elapsed_time": round(report_time - start_time, 3), "coverage": cov_data}

    if is_file:
        cov_data_json_str = json.dumps(cov_data_json)
    else:
        cov_data_json_str = json.dumps(cov_data_json, indent=4)

    write_text(report_file, cov_data_json_str, linebreak=is_file, append=is_file)


def main(
    bb_metadata_file: Annotated[
        Path,
        typer.Option(
            "--input",
            readable=True,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the basic block metadata file.",
        ),
    ],
    fuzzing_cmd: Annotated[str, typer.Option("--command", help="Shell command to run the fuzzer.")],
    output_file: Annotated[
        Path, typer.Option("--output", exists=False, resolve_path=True, help="Path to the output file or directory.")
    ] = DEFAULT_OUTPUT_FILE,
    ft_shm_name: Annotated[
        str, typer.Option("--shm-name", help="Name of the shared memory segment.")
    ] = DEFAULT_SHM_NAME,
    enable_visualization: Annotated[
        bool, typer.Option("--visualization", is_flag=True, help="Enable the coverage treemap visualization.")
    ] = False,
    config_file: Annotated[
        Path,
        typer.Option(
            "--config",
            readable=True,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the configuration file.",
        ),
    ] = DEFAULT_CONFIG_FILE,
) -> None:
    """
    Monitors code coverage during a fuzzing campaign.
    """
    bb_metadata = json.loads(bb_metadata_file.read_text())
    num_bbs = len(bb_metadata)

    if num_bbs == 0:
        typer.echo(f"ERROR: Basic block metadata file '{bb_metadata_file}' is empty!", err=True)
        raise typer.Exit(1)

    is_file = is_likely_file(output_file)

    if not is_file and not output_file.exists():
        output_file.mkdir(parents=True)

    config = Config.from_yaml(config_file).monitoring
    ft_env_vars = {FT_ENVVAR_SHM_NAME: ft_shm_name, FT_ENVVAR_BB_COUNT: str(num_bbs)}

    start_time = time.time()

    visualization: Visualization | None = None

    scheduler = Scheduler(config.interval_spec, persist_cov_data)
    ft_shm = SharedMemory(ft_shm_name, num_bbs)

    if enable_visualization:
        visualization = TreemapVisualization(
            bb_metadata, ft_shm, start_time, config.visualization.interval, config.visualization.port
        )

    ft_shm.open()
    scheduler.start(output_file, is_file, start_time, ft_shm)

    if enable_visualization:
        visualization.start()  # type: ignore

    try:
        run_shell_command(fuzzing_cmd, ft_env_vars)
    except (ValueError, RuntimeError) as ex:
        logging.error(ex)
    except KeyboardInterrupt:
        pass

    if enable_visualization:
        visualization.stop()  # type: ignore

    scheduler.stop()
    ft_shm.close()
