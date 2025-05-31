import argparse
import time
from checkmem.memory import build_memory_recorder, MemoryStore
from checkmem.termination import termination
import sys


def main():

    parser = argparse.ArgumentParser(description="Check memory usage on the nodes.")
    parser.add_argument(
        "--min_mem", type=int, default=0, help="Minimum memory usage in MB to report."
    )
    parser.add_argument(
        "--record_time",
        type=int,
        default=30,
        help="Time interval in seconds during which memory is used",
    )
    parser.add_argument(
        "--sleep_interval",
        type=int,
        default=1,
        help="Time in seconds to wait before checking memory again.",
    )
    parser.add_argument(
        "--recorder_type",
        type=str,
        default="node",
        help="Defines what to record. Options are 'node' for node memory usage and 'process' for process memory usage.",
    )
    parser.add_argument(
        "--max_records",
        type=int,
        default=10,
        help="Maximum number of records to keep in memory before dumping to disk.",
    )
    parser.add_argument(
        "--name", type=str, default="checkmem_trace", help="Name of the memory trace."
    )

    args = parser.parse_args()
    store = MemoryStore(args.name)
    recorder = build_memory_recorder(args.recorder_type)

    print("Starting checking memory")
    sys.stdout.flush()

    terminator = termination()

    while not terminator.terminating:
        store.append(recorder())

        if len(store.mem_trace) > args.max_records:
            store.dump()

        time.sleep(args.sleep_interval)

    store.dump()
    print("Finished checking memory")
