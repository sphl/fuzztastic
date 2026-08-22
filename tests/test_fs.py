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

import os
import tempfile
import unittest
from pathlib import Path

from fuzztastic.utils.fs import get_distinct_subpaths, is_likely_file


class TestIsLikelyFile(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = Path(tempfile.mkdtemp())

        self.test_file = self.test_dir / "test_file.txt"
        self.test_file.write_text("test")

    def tearDown(self) -> None:
        if self.test_file.exists():
            self.test_file.unlink()

        if self.test_dir.exists():
            os.rmdir(self.test_dir)

    def test_existing_file(self) -> None:
        # Arrange
        path = self.test_file

        # Act
        result = is_likely_file(path)

        # Assert
        self.assertTrue(result)

    def test_existing_dir(self) -> None:
        # Arrange
        path = self.test_dir

        # Act
        result = is_likely_file(path)

        # Assert
        self.assertFalse(result)

    def test_nonexistent_file(self) -> None:
        # Arrange
        path = Path("/nonexistent/file.txt")

        # Act
        result = is_likely_file(path)

        # Assert
        self.assertTrue(result)

    def test_nonexistent_dir(self) -> None:
        # Arrange
        path = Path("/nonexistent/dir")

        # Act
        result = is_likely_file(path)

        # Assert
        self.assertFalse(result)

    def test_nonexistent_file_with_multiple_extensions(self) -> None:
        # Arrange
        path = Path("/nonexistent/file.tar.gz")

        # Act
        result = is_likely_file(path)

        # Assert
        self.assertTrue(result)

    def test_nonexistent_hidden_file(self) -> None:
        # Arrange
        path = Path("/nonexistent/.hidden_file.txt")

        # Act
        result = is_likely_file(path)

        # Assert
        self.assertTrue(result)

    def test_nonexistent_hidden_dir(self) -> None:
        # Arrange
        path = Path("/nonexistent/.hidden_dir")

        # Act
        result = is_likely_file(path)

        # Assert
        self.assertFalse(result)

    def test_root_dir(self) -> None:
        # Arrange
        path = Path("/")

        # Act
        result = is_likely_file(path)

        # Assert
        self.assertFalse(result)

    def test_current_dir(self) -> None:
        # Arrange
        path = Path(".")

        # Act
        result = is_likely_file(path)

        # Assert
        self.assertFalse(result)

    def test_parent_dir(self) -> None:
        # Arrange
        path = Path("..")

        # Act
        result = is_likely_file(path)

        # Assert
        self.assertFalse(result)


class TestGetDistinctSubpaths(unittest.TestCase):
    def test_distinct_filenames(self) -> None:
        # Arrange
        paths = ["/a/foo.c", "/b/bar.c"]

        # Act
        result = get_distinct_subpaths(paths)

        # Assert
        self.assertEqual(result, {"/a/foo.c": "foo.c", "/b/bar.c": "bar.c"})

    def test_same_filename_different_dir(self) -> None:
        # Arrange
        paths = ["/a/file.c", "/b/file.c"]

        # Act
        result = get_distinct_subpaths(paths)

        # Assert
        self.assertEqual(result, {"/a/file.c": "a/file.c", "/b/file.c": "b/file.c"})

    def test_same_filename_and_dir(self) -> None:
        # Arrange
        paths = ["/a/b/file.c", "/a/b/file.c"]

        # Act
        result = get_distinct_subpaths(paths)

        # Assert - full path returned when suffix is not unique
        self.assertEqual(result, {"/a/b/file.c": "/a/b/file.c"})

    def test_mixed_unique_and_ambiguous(self) -> None:
        # Arrange
        paths = ["/a/foo.c", "/a/shared.c", "/b/shared.c"]

        # Act
        result = get_distinct_subpaths(paths)

        # Assert
        self.assertEqual(result, {"/a/foo.c": "foo.c", "/a/shared.c": "a/shared.c", "/b/shared.c": "b/shared.c"})

    def test_single_path(self) -> None:
        # Arrange
        paths = ["/a/b/file.c"]

        # Act
        result = get_distinct_subpaths(paths)

        # Assert
        self.assertEqual(result, {"/a/b/file.c": "file.c"})

    def test_empty_list(self) -> None:
        # Arrange
        paths: list[str] = []

        # Act
        result = get_distinct_subpaths(paths)

        # Assert
        self.assertEqual(result, {})
