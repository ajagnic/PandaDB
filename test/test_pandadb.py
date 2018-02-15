""" pandadb tests """
import unittest
import pandas
from sqlitedb import SqliteDB

__version__='0.0.1'
__author__='Adrian Agnic'


class TestPandaDB(unittest.TestCase):
    def setUp(self):
        self.db = SqliteDB(":memory:")
        self.db.connect()
        self.daf = pandas.DataFrame({}, index=[])

    def test_table(self):
        pass


if __name__ == '__main__':
    unittest.main()
