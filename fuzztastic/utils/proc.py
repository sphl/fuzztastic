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

import os
import subprocess
from pathlib import Path


def run_shell_command(cmd: str, env_vars: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """Run the given shell command."""
    env = os.environ.copy()

    if env_vars is not None:
        env.update(env_vars)

    return subprocess.run(cmd, shell=True, cwd=Path.cwd(), env=env, capture_output=False)
