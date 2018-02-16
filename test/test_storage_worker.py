import unittest
import pickle
import json
import pandas as pd
from time import sleep
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
        self.storage_worker = StorageWorker(self.q, storage_config, 'local')

    def test_init_interface(self):
        self.assertIsInstance(self.interface, SqliteInterface)

    def test_storage_worker_store(self):
        self.interface.open_connection()
        with self.assertRaises(ValueError):
            storage_worker_store(self.interface, ('boof', 'woof'))

        with self.assertRaises(ValueError):
            storage_worker_store(self.interface, ('template', 'boof', 'woof'))

        # store template
        # DELETE DB FILE BEFORE RUNNING TO AVOID DUPE TEMPLATE  
        storage_worker_store(self.interface, ('template', self.template_pd))
        r = self.interface.retrieve_template_by_id('dumb')
        self.assertIsInstance(r, object)
        self.assertEqual(r['stream_token'], 'abc123')

        # store bstream measures data
        storage_worker_store(self.interface, ('bstream', self.stream_token, self.bstream))

        a = self.interface.db.select(query='SELECT * FROM abc123_data')
        self.assertIsInstance(a,pd.DataFrame)
        self.assertGreaterEqual(a.shape[0], 50) # 50 dstreams in test data
        for col in ['fields', 'id', 'location', 'tags', 'timestamp']:
            self.assertIn(col, a.columns)
        self.interface.close_connection()

    def test_storage_worker_thread(self):
        self.interface.open_connection()
        sleep(1)

        self.storage_worker.start()

        self.assertIsInstance(self.storage_worker.interface, SqliteInterface)

        print("sleeping")
        sleep(1)
        old_data = self.interface.db.select(query='SELECT * FROM abc123_data')
        old_data_rows = old_data.shape[0]
        self.q.put(('bstream', self.stream_token, self.bstream))
        sleep(1)
        new_data = self.interface.db.select(query='SELECT * FROM abc123_data')
        new_data_rows = new_data.shape[0]
        self.assertEqual(new_data_rows, old_data_rows + 50)
        self.interface.close_connection()
        self.q.put('stop_storage')



if __name__ == '__main__':
    unittest.main()
