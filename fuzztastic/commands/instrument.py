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

import logging
from pathlib import Path
from typing import Annotated

import typer

from fuzztastic import DEFAULT_CONFIG_FILE, Config
from fuzztastic.utils.proc import run_shell_command

FT_PASS_ENVVAR_OUTPUT_FILE: str = "FT_PASS_OUTPUT_FILE"

DEFAULT_OUTPUT_FILE: Path = Path.cwd() / "output.json"


def main(
    input_bc_file: Annotated[
        Path,
        typer.Option(
            "--input-bc",
            readable=True,
            exists=True,
            file_okay=True,
            dir_okay=False,
            resolve_path=True,
            help="Path to the bitcode file to be instrumented.",
        ),
    ],
    output_bc_file: Annotated[
        Path, typer.Option("--output-bc", exists=False, resolve_path=True, help="Path to the output bitcode file.")
    ],
    bb_metadata_file: Annotated[
        Path,
        typer.Option("--output", exists=False, resolve_path=True, help="Path to the output basic block metadata file."),
    ] = DEFAULT_OUTPUT_FILE,
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
    Instruments a bitcode file with the FuzzTastic LLVM pass.
    """
    config = Config.from_yaml(config_file).instrumentation

    ft_env_vars = {FT_PASS_ENVVAR_OUTPUT_FILE: str(bb_metadata_file)}
    instrumentation_cmd = f"{config.llvm_opt_path} -load-pass-plugin {config.ft_llvm_pass_path} -passes=fuzztastic {str(input_bc_file)} -o {str(output_bc_file)}"

    try:
        run_shell_command(instrumentation_cmd, env_vars=ft_env_vars)
    except Exception as ex:
        logging.error(ex)
    except KeyboardInterrupt:
        pass
