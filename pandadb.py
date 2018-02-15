""" abstract database class w/ default pandas-sql interface
~ NOTES ~
*   pandas.to_sql method creates columns 'index' and 'level_0' for backup reference to original indices
*   pandas.read_sql only really works for 'select' statements, use the query method for drops, inserts, etc.
*   retrieve method is hard-coded to a search a column named 'version'
"""
import pandas
import json
from abc import ABCMeta, abstractmethod

__version__='0.0.1'
__author__='Adrian Agnic'


class PandaDB(metaclass=ABCMeta):

    def __init__(self, conn):
        """
        :type conn: database connection object
        :param conn: assign this property in interface through connect() override
        """
        self.conn = conn
        super().__init__()

    @abstractmethod
    def connect(self):
        """ override with specific engine connection method """
        pass

    @abstractmethod
    def close(self):
        """ might require override depending on engine close method """
        try:
            self.conn.close()
        except Exception as err:
            print(err)
            return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~BASIC METHODS
    @abstractmethod
    def select(self, query, pars, table):
        """ standard sql parametrized select, default select all if just given table name
        eg. db.select(table='test') or db.select(query="select * from test;")
        :type query: str
        :param query: standard sql query with ? or '?' for params
        :type pars: list, tuple
        :param pars: values to be passed into query
        :type table: str
        :param table: name of table
        :return: pandas
        """
        if not query:
            stmnt = "SELECT * FROM {0}".format(str(table))
            defres = pandas.read_sql(sql=stmnt, con=self.conn)
            return defres
        res = pandas.read_sql(sql=str(query), con=self.conn, params=pars)
        return res

    @abstractmethod
    def table(self, df, table, action):
        """
        eg. db.table(df=myDataframe, table='test', action='replace')
        :type df: pandas
        :param df: dataframe to seed table with
        :type table: str
        :param table: name of table
        :type action: str
        :param action: action to take if table exists: 'replace', 'append', or 'fail'
        """
        df.to_sql(name=str(table), con=self.conn, if_exists=str(action))

    @abstractmethod
    def create(self, df, table):
        """ similar to table method but w/ flexibility with # of columns and meant for inserting data
        eg. db.create(df=myDataframe, table='test')
        :type df: pandas
        :param df: row(s), as a dataframe, to be created
        :type table: str
        :param table: name of table
        """
        try:
            df.to_sql(name=str(table), con=self.conn, if_exists="append")
        except:
            daf = self.select(table=str(table))
            daf = daf.append(df)
            daf.to_sql(name=str(table), con=self.conn, if_exists="replace")

    @abstractmethod
    def query(self, stmnt):
        """ normal database query method, override this
        :type stmnt: str
        :param stmnt: normal sql query
        """
        pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~SPECIFIC METHODS
    @abstractmethod
    def exists(self, table):
        """
        :type table: str
        :param table: name of table
        :return: boolean
        """
        # NOTE could be done more elegantly
        try:
            bewl = self.select(table=str(table))
        except Exception as err:
            print(err)
            return False
        return True

    @abstractmethod
    def serialize(self, df, fields):
        """ serializes data for e. given field
        :type df: pandas
        :param df: dataframe with fields needing to be serialized
        :type fields: list, tuple
        :param fields: names of fields to serialize
        :return: pandas
        """
        for key in fields:
            if key in df.columns.values.tolist():
                df[key] = df[key].apply(lambda x: json.dumps(x))
        return df

    @abstractmethod
    def retrieve(self, table, col, val, latest):
        """ wrapper around select, but builds query first and has latest version functionality
        :type table: str
        :param table: name of table
        :type col: str
        :param col: name of column
        :type val: any, enclosing quotes if str (eg. "'stringValue'")
        :param val: name of value to search for
        :type latest: bool
        :param latest: flag for returning only latest version of result
        :return: pandas
        """
        if latest is True:
            lstmnt = "SELECT * FROM {0} WHERE {1}={2} AND version=(SELECT MAX(version) FROM {0} WHERE {1}={2});".format(str(table), str(col), str(val))
            ldfres = self.select(query=lstmnt)
            return ldfres
        stmnt = "SELECT * FROM {0} WHERE {1}={2};".format(str(table), str(col), str(val))
        dfres = self.select(query=stmnt)
        return dfres
