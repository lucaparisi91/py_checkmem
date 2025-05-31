from checkmem.memory import NodeMemory,MemoryStore
import time 
import shutil
import os
import pytest 
import pandas as pd

@pytest.fixture
def experiment_directory():
    name="experiment_directory"
    os.makedirs(name,exist_ok=False)
    yield name
    shutil.rmtree(name)



def test_node_memory_usage():
    mem_usage= NodeMemory()
    mem_data=mem_usage()
    assert len(mem_data) == 1


def test_memory_store(experiment_directory):

    store = MemoryStore(os.path.join(experiment_directory,"test_memory_store"))
    mem_usage= NodeMemory()

    store.append(mem_usage() )
    store.append(mem_usage() )
    
    assert len(store.get_data()) == 2

    store.dump()
    assert len(store.get_data()) == 0

    time.sleep(1)
    store.append(mem_usage() )
    assert len(store.get_data()) == 1

    store.dump()

    stored_data = pd.read_csv(store.filename, sep=" ")

    assert( mem_usage.columns == stored_data.columns.tolist() )    
    assert len(stored_data) == 3