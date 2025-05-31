from checkmem.memory import NodeMemory,MemoryStore, ProcessorMemory
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


def test_process_memory_usage():
    mem_usage= ProcessorMemory()
    mem_data=mem_usage()
    assert len(mem_data) > 1
    assert set(mem_data.columns.tolist()) == set(mem_usage.columns)

def test_store_node_memory(experiment_directory):

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
    assert set(stored_data.columns.tolist()) == set(mem_usage.columns)
    assert len(stored_data) == 3


def test_store_processor_memory(experiment_directory):

    store = MemoryStore(os.path.join(experiment_directory,"test_process_store"))
    mem_usage= ProcessorMemory()

    store.append(mem_usage() )
    store.append(mem_usage() )
    
    data= store.get_data()
    assert( len(set(data["timestamp"] ) ) == 2 )

    store.dump()
    stored_data = pd.read_csv(store.filename, sep=" ")
    assert(data.columns.tolist() == stored_data.columns.tolist())
    
    data["timestamp"] = pytest.approx(stored_data["timestamp"])
    data["rss"] = pytest.approx(stored_data["rss"])
    data["pid"] = stored_data["rss"]
    data["cmd"] = stored_data["cmd"]
    





