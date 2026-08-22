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

import unittest

from fuzztastic.shm import SharedMemory


class TestSharedMemory(unittest.TestCase):
    def setUp(self) -> None:
        self.shm_name = "test_shm"
        self.shm_size = 10

    def tearDown(self) -> None:
        import posix_ipc

        for name in [self.shm_name, self.shm_name + "_1", self.shm_name + "_2"]:
            try:
                shm = posix_ipc.SharedMemory(name)
                shm.unlink()
                shm.close_fd()
            except (posix_ipc.ExistentialError, FileNotFoundError):
                # Shared memory doesn't exist, which is fine
                pass

    def test_num_bytes_property(self) -> None:
        # Arrange
        shm = SharedMemory(self.shm_name, self.shm_size)
        expected = self.shm_size * 8

        # Act
        actual = shm._num_bytes

        # Assert
        self.assertEqual(actual, expected)

    def test_open_already_open_raises_error(self) -> None:
        # Arrange
        shm = SharedMemory(self.shm_name, self.shm_size)
        shm.open()

        # Act & Assert
        with self.assertRaises(RuntimeError):
            shm.open()

        # Cleanup
        shm.close()

    def test_close_not_open(self) -> None:
        # Arrange
        shm = SharedMemory(self.shm_name, self.shm_size)

        # Act & Assert (should not raise an exception)
        shm.close()

    def test_read_not_open_raises_error(self) -> None:
        # Arrange
        shm = SharedMemory(self.shm_name, self.shm_size)

        # Act & Assert
        with self.assertRaises(RuntimeError):
            shm.read()

    def test_write_not_open_raises_error(self) -> None:
        # Arrange
        shm = SharedMemory(self.shm_name, self.shm_size)
        test_data = [1, 2, 3, 4, 5]

        # Act & Assert
        with self.assertRaises(RuntimeError):
            shm.write(test_data)

    def test_initial_data_is_zeroed(self) -> None:
        # Arrange
        shm = SharedMemory(self.shm_name, self.shm_size)
        expected = [0] * self.shm_size

        shm.open()

        # Act
        actual = shm.read()

        # Assert
        self.assertEqual(actual, expected)

        # Cleanup
        shm.close()

    def test_write_and_read_data(self) -> None:
        # Arrange
        shm = SharedMemory(self.shm_name, self.shm_size)
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        shm.open()

        # Act
        shm.write(expected)
        actual = shm.read()

        # Assert
        self.assertEqual(actual, expected)

        # Cleanup
        shm.close()

    def test_write_partial_data(self) -> None:
        # Arrange
        shm = SharedMemory(self.shm_name, self.shm_size)
        test_data = [1, 2, 3, 4, 5]  # Less data than size
        expected = [1, 2, 3, 4, 5, 0, 0, 0, 0, 0]  # Padded with zeros

        shm.open()

        # Act
        shm.write(test_data)
        actual = shm.read()

        # Assert
        self.assertEqual(actual, expected)

        # Cleanup
        shm.close()

    def test_write_excess_data_truncated(self) -> None:
        # Arrange
        shm = SharedMemory(self.shm_name, self.shm_size)
        test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]  # More data than size
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Truncated to size

        shm.open()

        # Act
        shm.write(test_data)
        actual = shm.read()

        # Assert
        self.assertEqual(actual, expected)

        # Cleanup
        shm.close()

    def test_multiple_writes_overwrite(self) -> None:
        # Arrange
        shm = SharedMemory(self.shm_name, self.shm_size)
        expected_1 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        expected_2 = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

        shm.open()

        # Act
        shm.write(expected_1)
        actual_1 = shm.read()

        shm.write(expected_2)
        actual_2 = shm.read()

        # Assert
        self.assertEqual(actual_1, expected_1)
        self.assertEqual(actual_2, expected_2)

        # Cleanup
        shm.close()

    def test_two_shms_independent_data(self) -> None:
        # Arrange
        shm_1 = SharedMemory(self.shm_name + "_1", 5)
        shm_2 = SharedMemory(self.shm_name + "_2", 5)
        expected_1 = [10, 20, 30, 40, 50]
        expected_2 = [100, 200, 300, 400, 500]

        shm_1.open()
        shm_2.open()

        # Act
        shm_1.write(expected_1)
        actual_1 = shm_1.read()

        shm_2.write(expected_2)
        actual_2 = shm_2.read()

        # Assert
        self.assertEqual(actual_1, expected_1)
        self.assertEqual(actual_2, expected_2)

        # Cleanup
        shm_1.close()
        shm_2.close()

    def test_two_shms_different_sizes(self) -> None:
        # Arrange
        shm_1 = SharedMemory(self.shm_name + "_1", 3)
        shm_2 = SharedMemory(self.shm_name + "_2", 7)
        expected_1 = [1, 2, 3]
        expected_2 = [10, 20, 30, 40, 50, 60, 70]

        shm_1.open()
        shm_2.open()

        # Act
        shm_1.write(expected_1)
        actual_1 = shm_1.read()

        shm_2.write(expected_2)
        actual_2 = shm_2.read()

        # Assert
        self.assertEqual(actual_1, expected_1)
        self.assertEqual(actual_2, expected_2)

        # Cleanup
        shm_1.close()
        shm_2.close()
