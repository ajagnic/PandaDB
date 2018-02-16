from threading import Thread
from .sqlite_interface import SqliteInterface


__version__ = '0.0.1'
__author__ = 'Molly LeCompte'


storage_config = {
    'local': {'interface': SqliteInterface, 'args': ['../../strom_storage.db'], 'kwargs': {}},
}


def storage_worker_store(interface, item):
    if type(item) is tuple:
        if item[0] == 'template':
            if len(item) == 2:
                interface.store_template(item[1])
            else:
                raise ValueError(
                    f"Invalid storage tuple- template storage expects tuple len 2, received len {len(item)}")
        elif item[0] == 'bstream':
            if len(item) == 3:
                interface.store_bstream_data(item[1], item[2])
            else:
                raise ValueError(
                    f"Invalid storage tuple- bstream storage expects tuple len 3, received len {len(item)}")
        else:
            raise ValueError(f"Invalid storage tuple item {item[0]}- tuple index 0 must be str 'template' or 'bstream'")
    else:
        raise ValueError (f"Invalid storage item- expects type tuple, received type {type(item)}")


def init_interface(interface, args, kwargs):
    return interface(*args, **kwargs)


class StorageWorker(Thread):
    def __init__(self, queue, config, storage_type):
        super().__init__()
        self.q = queue
        self.interface = init_interface(config[storage_type]['interface'], config[storage_type]['args'], config[storage_type]['kwargs'])
        self.running = False


    def run(self):
        self.interface.open_connection()
        self.running = True
        while True:
            item = self.q.get()
            if item == 'stop_storage':
                break
            storage_worker_store(self.interface, item)
        print('THREAD CLOSING')
        self.interface.close_connection()