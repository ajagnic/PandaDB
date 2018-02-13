""" sub-class of pandadb, utilizes sqlite3 """
import sqlite3 as sql
from pandadb import PandaDB

__version__='0.0.1'
__author__='Adrian Agnic'


class SqliteDB(PandaDB):

    def __init__(self, filename):
        self.db = str(filename)
        self.conn = None
        super().__init__(self.conn)

    def connect(self):
        """ pandadb override """
        self.conn = sql.connect(self.db)

    def close(self):
        super().close()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def select(self, query=None, pars=None, table=None):
        return super().select(query, pars, table)

    def table(self, df, table, action="fail"):
        super().table(df, table, action)

    def create(self, df=None, table=None):
        super().create(df, table)

    def query(self, stmnt):
        """ pandadb override, normal sqlite query method """
        cur = self.conn.cursor()
        cur.execute(str(stmnt))
        self.conn.commit()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def exists(self, table):
        return super().exists(table)

    def serialize(self, df, fields):
        return super().serialize(df, fields)

    def retrieve(self):# NOTE TODO
        pass
