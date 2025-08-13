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

import unittest

from fuzztastic.scheduler import Interval, IntervalPhase, parse_interval_spec


class TestParseIntervalSpec(unittest.TestCase):
    def test_valid_with_phases(self) -> None:
        # Arrange
        interval_spec = "10@5;20@10;-@30"

        expected = Interval(
            default=30, phases=[IntervalPhase(duration=10, interval=5), IntervalPhase(duration=30, interval=10)]
        )

        # Act
        actual = parse_interval_spec(interval_spec)

        # Assert
        self.assertEqual(actual.default, expected.default)
        self.assertEqual(actual.phases, expected.phases)

    def test_valid_without_phases(self) -> None:
        # Arrange
        interval_spec = "-@15"

        # Act
        actual = parse_interval_spec(interval_spec)

        # Assert
        self.assertEqual(actual.default, 15)
        self.assertEqual(actual.phases, [])

    def test_invalid_missing_dash(self) -> None:
        # Arrange
        interval_spec = "10@5;20@10;30"

        # Act & Assert
        with self.assertRaises(ValueError):
            parse_interval_spec(interval_spec)

    def test_invalid_wrong_delimiter(self) -> None:
        # Arrange
        interval_spec = "10-5;20-10;-@30"

        # Act & Assert
        with self.assertRaises(ValueError):
            parse_interval_spec(interval_spec)

    def test_invalid_empty_string(self) -> None:
        # Arrange
        interval_spec = ""

        # Act & Assert
        with self.assertRaises(ValueError):
            parse_interval_spec(interval_spec)

    def test_spaces_in_input(self) -> None:
        # Arrange
        interval_spec = " 10@5 ; 20@10 ; -@30 "

        expected = Interval(
            default=30, phases=[IntervalPhase(duration=10, interval=5), IntervalPhase(duration=30, interval=10)]
        )

        # Act
        actual = parse_interval_spec(interval_spec)

        # Assert
        self.assertEqual(actual.default, expected.default)
        self.assertEqual(actual.phases, expected.phases)

    def test_single_phase(self) -> None:
        # Arrange
        interval_spec = "25@10;-@50"

        expected = Interval(default=50, phases=[IntervalPhase(duration=25, interval=10)])

        # Act
        actual = parse_interval_spec(interval_spec)

        # Assert
        self.assertEqual(actual.default, expected.default)
        self.assertEqual(actual.phases, expected.phases)
