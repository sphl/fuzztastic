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
import sys

import typer

from src.fuzztastic.commands import instrument, track

logging.basicConfig(format="%(asctime)s FuzzTastic[%(levelname)s]: %(message)s", level=logging.INFO, stream=sys.stdout)

app = typer.Typer()

app.command(name="instrument", help="Instrument a bitcode file with the FuzzTastic LLVM pass.")(instrument.main)
app.command(name="track", help="Track code coverage during a fuzzing campaign.")(track.main)
