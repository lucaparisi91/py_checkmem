from datetime import datetime
import numpy as np
import subprocess
import pandas as pd
from mpi4py import MPI
import os


class MemoryStore:
    """A class to store memory usage snapshots in a DataFrame and save them to a file.

    The class is responsible for storing memory usage data in a DataFrame and saving it to a file.
    """

    def __init__(self, name):
        self.name = name
        self.dataset_name = "memory_usage"
        self.comm = MPI.COMM_WORLD

        os.makedirs(self.name, exist_ok=True)

        self.filename = os.path.join(name, "trace" + str(self.comm.Get_rank()) + ".txt")
        self.reset_data()
        self.first_dump = True

    def reset_data(self):
        self.mem_trace = []

    def get_data(self):
        if len(self.mem_trace) == 0:
            return pd.DataFrame()
        else:
            return pd.concat(self.mem_trace).reset_index(drop=True)

    def append(self, mem_snapshot: pd.DataFrame):
        """Append a snapshot of the memory to the in-memory trace."""
        self.mem_trace.append(mem_snapshot)
        return self

    def dump(self):
        """Save the memory trace to the HDF5 file."""
        sep = " "

        if self.first_dump:
            self.get_data().to_csv(
                self.filename, mode="w", header=True, index=False, sep=sep
            )
            self.first_dump = False
        else:
            self.get_data().to_csv(
                self.filename, mode="a", header=False, index=False, sep=" "
            )
        self.reset_data()


class MemoryUsage:
    """A class to record memory usage snapshots"""

    def __init__(self, columns=[], min_mem=0):
        self.start_time = datetime.now().timestamp()
        self.min_mem = min_mem
        self.columns = columns

    def _get_shell_info(self, cmd) -> np.ndarray:
        """Get the memory usage data provided a shell command.

        Returns a numpy array with the first element being the timestamp
        and the rest being the memory metrics."""

        lines = (
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            .decode()
            .splitlines()
        )
        lines = [line.strip().split(" ") for line in lines]

        return lines


class NodeMemory(MemoryUsage):
    """A class to record memory usage on the node."""

    def __init__(self, min_mem=0):

        super().__init__(
            columns=["time", "total", "used", "free", "shared", "buffers", "cached"],
            min_mem=min_mem,
        )

    def __call__(self) -> pd.DataFrame:
        cmd = (
            r'free | grep Mem | awk "{if (\$3 > '
            + str(self.min_mem)
            + r' ) print \$2,\$3,\$4,\$5,\$6,\$7}"'
        )
        results = self._get_shell_info(cmd)[0]

        return pd.DataFrame(
            columns=self.columns,
            data=[
                (datetime.now().timestamp() - self.start_time,)
                + tuple(int(count) for count in results)
            ],
        )


class ProcessorMemory(MemoryUsage):

    def __init__(self, min_mem: float = 0):

        super().__init__(columns=["timestamp", "rss", "pid", "cmd"], min_mem=min_mem)

    def __call__(self):

        cmd = (
            r'ps -F | tail -n +2 | awk "{ if (\$6 >'
            + str(self.min_mem)
            + r') print \$6,\$2,\$11 }"'
        )
        results = self._get_shell_info(cmd)
        timestamp = datetime.now().timestamp() - self.start_time

        data = pd.DataFrame(
            {
                "timestamp": [timestamp for i in range(len(results))],
                "rss": [int(result[0]) for result in results],
                "pid": [str(result[1]) for result in results],
                "cmd": [str(result[2]) for result in results],
            }
        )

        return data


def build_memory_recorder(type, *args, **kwds):
    """Factory function to create a memory recorder based on the type."""
    if type == "node":
        return NodeMemory(*args, **kwds)
    elif type == "process":
        return ProcessorMemory(*args, **kwds)
    else:
        raise ValueError(f"Unknown memory recorder type: {type}")
