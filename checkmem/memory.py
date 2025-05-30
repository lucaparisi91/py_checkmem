
from datetime import datetime
import numpy as np
import subprocess
import pandas as pd
from mpi4py import MPI
import os

class MemoryStore:
    """ A class to store memory usage snapshots in a DataFrame and save them to a file.
    
    The class is responsible for storing memory usage data in a DataFrame and saving it to a file.
    """    

    def __init__(self,name,max_records=10):
        self.max_records=max_records
        self.name=name
        self.dataset_name = "memory_usage"
        self.comm = MPI.COMM_WORLD
        os.makedirs(self.name, exist_ok=True)
        self.filename = os.path.join( name, "name" + str(self.comm.Get_rank()) + ".txt")
        self.reset_data()


    def reset_data(self):
        self.mem_trace=[]
    
    def get_data(self):
        return pd.concat(self.mem_trace).reset_index(drop=True)
    
    def append(self,mem_snapshot : pd.DataFrame):
        """ Append a snapshot of the memory to the in-memory trace."""
        self.mem_trace.append(mem_snapshot)
        return self

    def dump(self):
        """ Save the memory trace to the HDF5 file."""
        self.get_data().to_csv(self.filename, mode='a', header=False, index=False,sep=" ")
        self.reset_data()


class MemoryUsage:
    """ A class to record memory usage snapshots"""

    def __init__(self,columns=[],min_mem=0):
        self.start_time = datetime.now().timestamp()
        self.min_mem = min_mem
        self.columns = columns

    def _get_shell_info(self,cmd) -> np.ndarray:
        """ Get the memory usage data provided a shel command. Returns a numpy array with the first element being the timestamp and the rest being the memory metrics."""

        
        lines=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True).decode().splitlines()
        lines=[line.strip().split(" ") for line in lines ]

        return lines
    
class NodeMemory(MemoryUsage):

    def __init__(self,min_mem=0):

        super().__init__(columns=["time","total","used","free","shared","buffers","cached"],min_mem=min_mem)
        
    def __call__(self) -> np.ndarray:
        cmd=r'free | grep Mem | awk "{if (\$3 > ' + str(self.min_mem) + r' ) print \$2,\$3,\$4,\$5,\$6,\$7}"'
        results= self._get_shell_info(cmd)[0]

        return pd.DataFrame( columns=self.columns,data= [(datetime.now().timestamp() - self.start_time,) + tuple( int(count) for count in results ) ] )

# class ProcessorMemory(MemoryUsage):

#     def __init__(self,min_mem=0):

#         super().__init__(columns=["timestamp","total","used","free","shared","buffers","cached"],min_mem=min_mem)

#     def __call__(self) -> np.ndarray:
        
#         cmd=r'ps -F | tail -n +2 | awk "{ if (\$6 >' +  str(self.min_memory) +r') print \$6,\$2,\$11 }"'

#         return self._get_memory_data(cmd)    

