import argparse
import subprocess
import numpy as np
import time
from datetime import datetime
import h5py
from mpi4py import MPI
import signal

class memoryStore:
    """ A class to store memory usage snapshots in a DataFrame and save them to a file."""    

    def __init__(self,filename,max_records=10):
        self.max_records=max_records
        self.filename=filename
        self.start_time=datetime.now().timestamp()
        self.dataset_name = "memory_usage"
        self.comm = MPI.COMM_WORLD

        self.f = h5py.File(filename,'w',driver='mpio', comm=MPI.COMM_WORLD)

        if not self.dataset_name in self.f.keys():
            self.timing_data= self.f.create_dataset(self.dataset_name, (self.comm.Get_size(),0, 7), maxshape=(self.comm.Get_size(),None, 7), dtype='f')
        else:
            self.timing_data = self.f[self.dataset_name]
        self.reset_data()

    def reset_data(self):
        self.mem_trace=[]


    def append(self,mem_snapshot):
        """ Append a snapshot of the memory to the in-memory trace."""
        self.mem_trace.append(mem_snapshot)

    def dump(self):
        """ Save the memory trace to the HDF5 file."""
        mem_trace_np = np.array(self.mem_trace)
        ntimes=self.timing_data.shape[1]
        self.timing_data.resize(axis=1,size=ntimes+ mem_trace_np.shape[0] )
        self.timing_data[self.comm.Get_rank(),ntimes:,:]=mem_trace_np
        self.reset_data()

    def close(self):
        self.f.close()

class ProgramTerminator:

    def start_to_close(self,signum, frame):
        print("Terminating")
        self.terminating = True

    def __init__(self):
        
        self.terminating = False
        signal.signal(signal.SIGTERM, self.start_to_close)
        signal.signal(signal.SIGINT, self.start_to_close)

def get_memory_usage(min_mem,start_time):

    mem_data=np.zeros(7,dtype=float)
    cmd=r'free | grep Mem | awk "{if (\$3 > ' + str(min_mem) + r' ) print \$2,\$3,\$4,\$5,\$6,\$7}"'
    #cmd=r'free | grep Mem  | awk "{if (\$3 > 0 ) print $i,\$2,\$3,\$4,\$5,\$6,\$7}"'
    results=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
    mem_data[1:]=np.array([int(count) for count in results.decode().strip().split(" ")])
    mem_data[0]=datetime.now().timestamp() - start_time
    return mem_data


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Check memory usage on the nodes.")

    parser.add_argument("--min_mem", type=int, default=0, help="Minimum memory usage in MB to report.")
    parser.add_argument("--record_time", type=int, default=30, help="Time interval in seconds during which memory is used")
    parser.add_argument("--sleep_interval", type=int, default=1, help="Time in seconds to wait before checking memory again.")

    args = parser.parse_args()
    store=memoryStore("mem_trace.hdf5")
    start_time = datetime.now().timestamp()
    print("Starting checking memory")

    terminator=ProgramTerminator()

    while not terminator.terminating:
        store.append(get_memory_usage(0,start_time) )

        if len(store.mem_trace) > store.max_records:
            store.dump()

        #if (not terminating):
        time.sleep(args.sleep_interval)

    store.dump()
    store.close()
    print("Finished checking memory")
