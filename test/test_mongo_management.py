import unittest
import json
from strom.database.mongo_management import MongoManager


class TestMongoManager(unittest.TestCase):
    def setUp(self):
        demo_data_dir = "demo_data/"
        self.manager = MongoManager()
        self.dstream_template = json.load(open(demo_data_dir + "demo_template.txt"))
        self.bstream = json.load(open(demo_data_dir + "demo_bstream_trip26.txt"))

    def test_insert_retrieve(self):
        token = self.dstream_template["stream_token"]

        inserted_id = self.manager.insert(self.dstream_template, 'template')
        queried = self.manager.get_by_id(inserted_id, 'template')

        inserted_id2 = self.manager.insert(self.bstream, 'derived')
        queried2 = self.manager.get_by_id(inserted_id2, 'derived', token)

        inserted_id3 = self.manager.insert(self.bstream, 'event')
        queried3 = self.manager.get_by_id(inserted_id3, 'event', token)

        self.assertEqual(inserted_id, queried["_id"])
        self.assertEqual(inserted_id2, queried2["_id"])
        self.assertEqual(inserted_id3, queried3["_id"])


    def test_get_all_coll(self):
        self.manager.insert(self.bstream, 'derived')
        self.manager.insert(self.bstream, 'derived')
        self.manager.insert(self.bstream, 'event')
        self.manager.insert(self.bstream, 'event')

        all_derived = self.manager.get_all_coll('derived', 'abc123')
        all_events = self.manager.get_all_coll('event', 'abc123')

        self.assertTrue(len(all_derived) >= 2)
        self.assertTrue(len(all_events) >= 2)
        self.assertIn(self.manager.derived_coll_suffix, all_derived[-1].keys())
        self.assertIn(self.manager.event_coll_suffix, all_events[-1].keys())
        self.assertNotIn(self.manager.event_coll_suffix, all_derived[-1].keys())
        self.assertNotIn(self.manager.derived_coll_suffix, all_events[-1].keys())


if __name__ == "__main__":
    unittest.main()