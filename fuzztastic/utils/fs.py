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

from collections import Counter
from pathlib import Path


def is_likely_file(path: Path) -> bool:
    """Check if the given path is (likely) a file."""
    return path.is_file() if path.exists() else path.suffix != ""


def get_distinct_subpaths(paths: list[str]) -> dict[str, str]:
    """Return the shortest unique path suffix for each path in the list."""
    path_objs = [Path(p) for p in paths]

    suffix_counts: Counter = Counter()
    for p in path_objs:
        for k in range(1, len(p.parts) + 1):
            suffix_counts[p.parts[-k:]] += 1

    result = {}
    for p in path_objs:
        for k in range(1, len(p.parts) + 1):
            suffix = p.parts[-k:]
            if suffix_counts[suffix] == 1 or k == len(p.parts):
                result[str(p)] = Path(*suffix).as_posix()
                break

    return result
