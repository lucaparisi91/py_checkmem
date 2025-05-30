import argparse
import numpy as np
import time
from datetime import datetime
from checkmem.memory import memoryStore
from checkmem.termination import termination



def main():

    parser = argparse.ArgumentParser(description="Check memory usage on the nodes.")
    parser.add_argument("--min_mem", type=int, default=0, help="Minimum memory usage in MB to report.")
    parser.add_argument("--record_time", type=int, default=30, help="Time interval in seconds during which memory is used")
    parser.add_argument("--sleep_interval", type=int, default=1, help="Time in seconds to wait before checking memory again.")

    args = parser.parse_args()
    store=memoryStore("mem_trace.hdf5")
    start_time = datetime.now().timestamp()
    print("Starting checking memory")

    terminator=termination()

    while not terminator.terminating:
        store.append(get_memory_usage(0,start_time) )

        if len(store.mem_trace) > store.max_records:
            store.dump()

        #if (not terminating):
        time.sleep(args.sleep_interval)

    store.dump()
    store.close()
    print("Finished checking memory")
