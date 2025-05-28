import argparse
import subprocess
import numpy as np
import pandas as pd
import time
from datetime import datetime
import h5py
from mpi4py import MPI

class memoryStore:
    """ A class to store memory usage snapshots in a DataFrame and save them to a file."""    

    def __init__(self,filename):
        self.max_records=100
        self.filename=filename
        self.start_time=datetime.now().timestamp()
        self.dataset_name = "memory_usage"
        self.comm = MPI.COMM_WORLD

        self.f = h5py.File(filename,'a',driver='mpio', comm=MPI.COMM_WORLD)

        if not self.dataset_name in self.f.keys():
            self.timing_data= self.f.create_dataset(self.dataset_name, (self.comm.Get_size(),0, 7), maxshape=(self.comm.Get_size(),None, 7), dtype='f')
        else:
            self.timing_data = self.f[self.dataset_name]
        self.reset_data()

    def reset_data(self):
        self.mem_trace=pd.DataFrame( columns=["timestap","total","used","free","shared","buff_cache","available"],dtype=float)    

    def append(self,mem_snapshot):
        
        self.mem_trace.loc[len(self.mem_trace),:]=mem_snapshot    

    def dump(self):
        mem_trace_np = self.mem_trace.to_numpy()
        ntimes=self.timing_data.shape[1]
        ntimes=self.timing_data.resize(axis=1,size=ntimes+ mem_trace_np.shape[0] )
        self.timing_data[self.comm.Get_rank(),ntimes:,:]=mem_trace_np

    def close(self):
        self.f.close()

def get_memory_usage(min_mem,start_time):
    
    mem_data=np.zeros(7,dtype=int)
    cmd=r'free | grep Mem | awk "{if (\$3 > ' + str(min_mem) + r' ) print \$2,\$3,\$4,\$5,\$6,\$7}"'
    #cmd=r'free | grep Mem  | awk "{if (\$3 > 0 ) print $i,\$2,\$3,\$4,\$5,\$6,\$7}"'
    results=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
    mem_data[1:]=np.array([int(count) for count in results.decode().strip().split(" ")])
    mem_data[0]=datetime.now().timestamp() - start_time
    return mem_data

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Check memory usage on the nodes.")

    parser.add_argument("--min_mem", type=int, default=0, help="Minimum memory usage in MB to report.")
    parser.add_argument("--sleep_interval", type=int, default=0, help="Minimum time in seconds to wait before checking memory again.")
    
    args = parser.parse_args()

    store=memoryStore("mem_trace.hdf5")
    start_time = datetime.now().timestamp()
    print("Starting checking memory")
    #time.sleep(args.sleep_interval)
    store.append(get_memory_usage(0,start_time) )
    store.dump()
    print("Finished checking memory")
    store.close()