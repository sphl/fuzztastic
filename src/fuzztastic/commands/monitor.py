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

import typer
from typing_extensions import Annotated

from fuzztastic import Config
from fuzztastic.scheduler import Scheduler
from fuzztastic.shm import SharedMemory
from fuzztastic.utils.fs import is_likely_file
from fuzztastic.utils.io import write_text
from fuzztastic.utils.proc import run_shell_command

FT_ENVVAR_SHM_NAME: str = "FT_SHM_NAME"
FT_ENVVAR_BB_COUNT: str = "FT_BB_COUNT"

DEFAULT_OUTPUT_FILE: Path = Path.cwd() / "output.txt"
DEFAULT_SHM_NAME: str = "fuzztastic_shm"
DEFAULT_CONFIG_FILE: Path = Path.cwd() / "config.yaml"


def get_num_bbs(bb_info_file: Path) -> int:
    """
    Returns the number of basic blocks (BBs).
    """
    return len(json.loads(bb_info_file.read_text()))


def persist_cov_data(output_path: Path, is_file: bool, start_time: float, shm: SharedMemory) -> None:
    """
    Stores the new coverage data in the output file.
    """
    report_time = time.time()
    report_file = output_path if is_file else output_path / f"ft_cov_{int(report_time)}.json"

    cov_data = shm.read()
    cov_data_json = {"elapsed_time": round(report_time - start_time, 3), "bb_coverage": cov_data}

    if is_file:
        cov_data_json_str = json.dumps(cov_data_json)
    else:
        cov_data_json_str = json.dumps(cov_data_json, indent=4)

    write_text(report_file, cov_data_json_str, linebreak=is_file, append=is_file)


def main(
    bb_info_file: Annotated[
        Path,
        typer.Option(
            "--input",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the basic block info file.",
        ),
    ],
    fuzzer_cmd: Annotated[str, typer.Option("--command", help="Shell command to run the fuzzer.")],
    output_path: Annotated[
        Path, typer.Option("--output", exists=False, resolve_path=True, help="Path to the output file or directory.")
    ] = DEFAULT_OUTPUT_FILE,
    shm_name: Annotated[str, typer.Option("--shm-name", help="Name of the shared memory segment.")] = DEFAULT_SHM_NAME,
    config_file: Annotated[
        Path,
        typer.Option(
            "--config",
            writable=False,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the configuration file.",
        ),
    ] = DEFAULT_CONFIG_FILE,
) -> None:
    """
    Monitors the fuzzing campaign and persists the coverage data.
    """
    num_bbs = get_num_bbs(bb_info_file)

    if num_bbs == 0:
        typer.echo(f"ERROR: Basic block info file '{bb_info_file}' is empty!", err=True)
        raise typer.Exit(1)

    is_file = is_likely_file(output_path)

    if not is_file and not output_path.exists():
        output_path.mkdir(parents=True)

    config = Config.from_yaml(config_file)
    ft_env_vars = {FT_ENVVAR_SHM_NAME: shm_name, FT_ENVVAR_BB_COUNT: str(num_bbs)}

    scheduler = Scheduler(config.interval_spec, persist_cov_data)
    shm = SharedMemory(shm_name, num_bbs)

    start_time = time.time()

    shm.open()
    scheduler.start(output_path, is_file, start_time, shm)

    try:
        run_shell_command(fuzzer_cmd, ft_env_vars)
    except (ValueError, RuntimeError) as ex:
        logging.error(ex)
    except KeyboardInterrupt:
        pass

    scheduler.stop()
    shm.close()
