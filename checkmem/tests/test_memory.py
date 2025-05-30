from checkmem.memory import NodeMemory,MemoryStore
import time 

def test_node_memory_usage():
    mem_usage= NodeMemory()
    mem_data=mem_usage()
    assert len(mem_data) == 1

def test_memory_store():

    store = MemoryStore("test_memory_store", max_records=5)
    mem_usage= NodeMemory()

    store.append(mem_usage() )
    store.dump()

    time.sleep(2)
    store.append(mem_usage() )

    print(store.get_data())
    store.dump()

    
