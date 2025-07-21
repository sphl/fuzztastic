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

from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path

import yaml

VisualizationConfig = namedtuple("VisualizationConfig", ["port", "interval"])
TrackingConfig = namedtuple("TrackingConfig", ["interval_spec", "visualization"])

InstrumentationConfig = namedtuple("InstrumentationConfig", ["llvm_opt_path", "ft_llvm_pass_path"])

DEFAULT_CONFIG_FILE: Path = Path.cwd() / "config.yaml"


@dataclass
class Config:
    """
    FuzzTastic configuration.
    """

    tracking: TrackingConfig = None  # type: ignore
    instrumentation: InstrumentationConfig = None  # type: ignore

    @classmethod
    def from_yaml(cls, file_path: Path) -> "Config":
        """
        Load configuration from a YAML file.
        """
        config = yaml.safe_load(file_path.read_text())

        return cls(
            tracking=TrackingConfig(
                interval_spec=config.get("tracking", {}).get("interval", "-@60"),
                visualization=VisualizationConfig(
                    port=config.get("tracking", {}).get("visualization", {}).get("port", 8050),
                    interval=config.get("tracking", {}).get("visualization", {}).get("interval", 30),
                ),
            ),
            instrumentation=InstrumentationConfig(
                llvm_opt_path=config.get("instrumentation", {}).get("llvm_opt", "/usr/bin/opt"),
                ft_llvm_pass_path=config.get("instrumentation", {}).get(
                    "ft_llvm_pass", "/fuzztastic/instrumentation/build/libfuzztasticpass.so"
                ),
            ),
        )
