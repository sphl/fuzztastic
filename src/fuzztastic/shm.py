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

from ctypes import c_uint64, sizeof
from mmap import MAP_SHARED, PROT_READ, PROT_WRITE, mmap
from typing import List

import numpy as np
import posix_ipc


class SharedMemory:
    """
    A class to manage shared memory (SHM) segments.
    """

    def __init__(self, name: str, size: int) -> None:
        self._name = name
        self._size = size
        self._shm = None
        self._mem = None

    @property
    def _num_bytes(self) -> int:
        """
        Get the number of bytes in the SHM segment.
        """
        return self._size * sizeof(c_uint64)

    def open(self) -> None:
        """
        Open the SHM segment.
        """
        if self._shm:
            raise RuntimeError("Shared memory segment is already open!")

        self._shm = posix_ipc.SharedMemory(self._name, posix_ipc.O_CREAT, size=self._num_bytes, read_only=False)
        self._mem = mmap(self._shm.fd, self._num_bytes, MAP_SHARED, PROT_READ | PROT_WRITE)  # type: ignore

        # Initialize the SHM segment with zeros
        self.write([0] * self._size)

    def read(self) -> List[int]:
        """
        Read the data from the SHM segment.
        """
        if not self._shm:
            raise RuntimeError("Shared memory segment is not open!")

        self._mem.seek(0)
        data = self._mem.read(self._num_bytes)

        return np.frombuffer(data, dtype=c_uint64, count=self._size).tolist()

    def write(self, data: List[int]) -> None:
        """
        Write the given data to the SHM segment.
        """
        if not self._shm:
            raise RuntimeError("Shared memory segment is not open!")

        data = np.array(data[: self._size], dtype=c_uint64).tobytes()

        self._mem.seek(0)
        self._mem.write(data)
        self._mem.flush()

    def close(self) -> None:
        """
        Close the SHM segment.
        """
        if not self._shm:
            return

        self._mem.close()
        self._mem = None

        try:
            self._shm.unlink()
        except posix_ipc.ExistentialError:
            # SHM segment is already unlinked
            pass

        self._shm.close_fd()
        self._shm = None
