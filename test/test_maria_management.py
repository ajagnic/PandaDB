import unittest
import json
import gc
from strom.database.maria_management import SQL_Connection

class TestSQL_Connection(unittest.TestCase):
    def setUp(self):
        self.cnx = SQL_Connection()
        self.cursor = self.cnx.cursor
        demo_data_dir = "./demo_data/"
        self.dstream = json.load(open(demo_data_dir+"demo_template.txt"))
        self.dstreams = json.load(open(demo_data_dir+"first_seven_from_demo_trip.txt"))
        self.bstream = json.load(open(demo_data_dir+"demo_bstream_trip26.txt"))

    def test_init(self):
        self.assertIsInstance(self.cnx, SQL_Connection)
        self.assertIs(self.cursor, self.cnx.cursor)

    def test_mariadb(self):

        # Initialize tables
        metadata_table = self.cnx.create_metadata_table()
        stream_lookup_table = self.cnx.create_stream_lookup_table(self.dstream)
        stream_filter_table = self.cnx.create_stream_filtered_table(self.dstream)

        # Check if tables exist
        self.assertTrue(self.cnx.check_metadata_table_exists())
        self.assertTrue(self.cnx._check_table_exists('template_metadata'))
        self.assertTrue(self.cnx._check_table_exists('abc123'))
        self.assertTrue(self.cnx._check_table_exists('abc123_filter'))

        # Insert rows into metadata_table
        self.assertEqual(self.cnx.insert_row_into_metadata_table("stream_one", "stream_token_one", 1.0, "filler"), 1)
        self.assertEqual(self.cnx.insert_row_into_metadata_table("stream_two", "stream_token_two", 1.1, "woo"), 1)
        self.assertEqual(self.cnx.insert_row_into_metadata_table("stream_three", "stream_token_three", 1.2, "great"), 1)
        self.assertEqual(self.cnx.insert_row_into_metadata_table("stream_three", "stream_token_three", 1.3, "right"), 1)

        # Retrieve from metadata_table (TEST)
        self.assertDictEqual(self.cnx._retrieve_by_id(2), {"unique_id":2, "stream_name":"stream_two", "stream_token":"stream_token_two", "version":1.10, "template_id":"woo"})
        self.assertEqual(self.cnx._retrieve_by_stream_name("stream_two"), 1)
        self.assertEqual(self.cnx._retrieve_by_stream_token("stream_token_one"), 1)
        self.assertEqual(self.cnx.return_template_id_for_latest_version_of_stream("stream_token_three"), "right")
        self.assertEqual(self.cnx._select_all_from_metadata_table(), 4)

        # Insert rows into stream_lookup_table in one call
        self.assertEqual(self.cnx.insert_rows_into_stream_lookup_table(self.bstream), 283)

        # Insert rows into stream_lookup_table one by one
        for dstream in self.dstreams:
            self.cnx.insert_row_into_stream_lookup_table(dstream)

        # Insert value into filtered measure in stream_lookup_table
        self.assertEqual(self.cnx.insert_filtered_measure_into_stream_lookup_table("abc123", "buttery_location", "dummy data dummy data dummy data dummy data", 1), 1)

        # Retrieve from stream_lookup_table
        self.assertEqual(self.cnx.retrieve_by_timestamp_range(self.dstream, 1510603551107, 1510603551109), 3)
        self.assertEqual(self.cnx.return_template_id_for_latest_version_of_stream("stream_token_three"), "right")

        # Insert rows into stream filter table
        self.assertEqual(self.cnx.insert_rows_into_stream_filtered_table(self.bstream), 283)

        # Close connection
        gc.collect()
        self.cnx._close_connection()


if __name__ == "__main__":
    unittest.main()
