""" pandadb tests """
import unittest
import pandas
import json
from time import sleep
from sqlitedb import SqliteDB

__version__='0.0.1'
__author__='Adrian Agnic'


class TestPandaDB(unittest.TestCase):
    def setUp(self):
        self.db = SqliteDB(":memory:")
        self.db.connect()
        self.daf = pandas.DataFrame({"name":['aj', 'as', 'aj'], "version":[0.5, 1.5, 2.0]}, index=[0,1,2])

    def test_table(self):
        self.db.table(df=self.daf, table='test', action='replace')
        res = self.db.select(query="SELECT * FROM test;")
        del res['index']
        self.assertIsNone(pandas.util.testing.assert_frame_equal(res, self.daf))

    def test_select(self):
        self.db.table(df=self.daf, table='test', action='replace')
        res = self.db.select(table='test')
        del res['index']
        self.assertIsNone(pandas.util.testing.assert_frame_equal(res, self.daf))

    def test_create(self):
        self.db.table(df=self.daf, table='test', action='replace')
        odaf = self.db.select(table='test')
        adddaf = pandas.DataFrame({"name":"aj", "version":0.6, "extra":5}, index=[0])
        self.db.create(df=adddaf, table='test')
        newdaf = self.db.select(table='test')
        odaf = odaf.append(adddaf)
        odaf = odaf.reset_index()
        self.assertIsNone(pandas.util.testing.assert_frame_equal(odaf, newdaf))

    def test_exists(self):
        self.assertFalse(self.db.exists('test'))
        self.db.table(df=self.daf, table='test', action='replace')
        self.assertTrue(self.db.exists('test'))

    def test_serialize(self):
        serdaf = self.db.serialize(df=self.daf, fields=('name',))
        try:
            unser = json.loads(serdaf.at[0, 'name'])
        except:
            self.fail()

    def test_retrieve(self):
        self.db.table(df=self.daf, table='test', action='replace')
        res = self.db.retrieve(table='test', col='name', val="'aj'", latest=True)
        ores = self.db.select(query="SELECT * FROM test WHERE version=2.0;")
        self.assertIsNone(pandas.util.testing.assert_frame_equal(res, ores))

    def test_query(self):
        self.db.table(df=self.daf, table='test', action='replace')
        self.assertTrue(self.db.exists('test'))
        self.db.query("DROP table test;")
        self.assertFalse(self.db.exists('test'))

    def tearDown(self):
        self.db.close()


if __name__ == '__main__':
    unittest.main()
