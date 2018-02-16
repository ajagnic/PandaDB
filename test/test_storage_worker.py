import unittest
import pickle
import json
import pandas as pd
from queue import Queue
from strom.storage.sqlite_interface import SqliteInterface
from strom.storage.storage_worker import storage_worker_store, StorageWorker, storage_config, init_interface

with open('demo_data/pickled_d.pickle', 'rb') as handle:
    b = pickle.load(handle)

template = json.load(open('demo_data/demo_template.txt'))


class TestStorageWorker(unittest.TestCase):
    def setUp(self):
        self.stream_token = 'abc123'
        self.bstream = b['measures']
        self.template = template
        self.template_pd = pd.DataFrame({
            'stream_token': template['stream_token'],
            'template_id': template['template_id'],
            'stream_name': template['stream_name'],
            'version': template['version'],
            'user_description': template['user_description'],
            'template': json.dumps(template)}, index=[0])
        self.q = Queue()
        self.interface = init_interface(storage_config['local']['interface'], storage_config['local']['args'], storage_config['local']['kwargs'])

    def test_interface(self):
        self.assertIsInstance(self.interface, SqliteInterface)

    def test_storage_worker_store(self):
        with self.assertRaises(ValueError):
            storage_worker_store(self.interface, ('boof', 'woof'))


        with self.assertRaises(ValueError):
            storage_worker_store(self.interface, ('template', 'boof', 'woof'))


        self.interface.db.create(self.template_pd, 'template')


        storage_worker_store(self.interface, ('template', self.template_pd))
        r = self.interface.retrieve_template_by_id('dumb')
        print(r)

        # print(self.bstream)
        # print(self.bstream.dtypes)

        # storage_worker_store(self.interface, ('bstream', self.stream_token, self.bstream))

        # a = self.interface.db.select(query='SELECT * FROM abc123_data')
        # print(a)


if __name__ == '__main__':
    unittest.main()
