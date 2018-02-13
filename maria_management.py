"""MariaDB Connector Class

The strom project takes advantage of SQL look up speeds to store the dstream templates in a
Maria database. The methods for interacting with the Maria database are written using the
PyMySQL pure python client library and are called by the Coordinator.

Legacy functions that are no longer used can be found at the end of the file for historical
purposes.
"""

__version__  = "0.1"
__author__ = "Justine <justine@tura.io>"

#!/usr/bin/python
import copy
import gc
import itertools
import json

import pymysql.cursors
from pymysql.constants import ER

from logging import (DEBUG, INFO)
from strom.utils.logger.logger import logger
from strom.utils.configer import configer

def _stringify_by_adding_quotes(dict):
    return '"' + str(dict) + '"'

def _stringify_uuid(uuid):
    return str(uuid).replace("-", "_")

class SQL_Connection:
    def __init__(self):
        # Prevent connection leakage by manually invoking the Python garbage collector to avoid
        # running out of database connections.
        gc.collect()
        # Set up connection to 'test' database in the MariaDB instance on Docker
        logger.info(configer['host'])
        self.mariadb_connection = pymysql.connect(host=configer['host'], database=configer['database'], user=configer['user'], password=configer['password'], charset=configer['charset'], cursorclass=pymysql.cursors.DictCursor, autocommit=configer['autocommit'])
        self.cursor = self.mariadb_connection.cursor()

    # def _close_connection(self):# NOTE replaced by sqliteDB.close()
    #     # close pooled connection and return it to the connection pool as an available connection
    #     logger.info("Closing connection")
    #     self.mariadb_connection.close()
    #     gc.collect()

    # ***** Metadata Table and Methods *****

    # def create_metadata_table(self):# NOTE replaced by sqliteDB.table(meta_df, 'metadata', 'fail')
    #     """
    #     Called by the Coordinator in the process_template function when processing a new dstream.
    #     """
    #     table = ("CREATE TABLE template_metadata ("
    #         "  `unique_id` int(50) NOT NULL AUTO_INCREMENT,"
    #         "  `stream_name` varchar(60) NOT NULL,"
    #         "  `stream_token` varchar(60) NOT NULL,"
    #         "  `version` decimal(10, 2) NOT NULL,"
    #         "  `template_id` varchar(60) NOT NULL,"
    #         "  PRIMARY KEY (`unique_id`)"
    #         ") ENGINE=InnoDB")
    #     logger.info("Creating table")
    #     try:
    #         self.cursor.execute(table)
    #     except pymysql.err.InternalError as err:
    #         if ER.TABLE_EXISTS_ERROR:
    #             logger.error("table already exists")
    #         raise err

    # NOTE should be replaced by sqliteDB.create(~) and sqliteDB.serialize(dstream)
    # def insert_row_into_metadata_table(self, stream_name, stream_token, version, template_id):
    #     """
    #     Called by the Coordinator in the process_template function when processing a new dstream.
    #     :param stream_name: stream_name from a dstream
    #     :type stream_name: str
    #     :param stream_token: stream_token from a dstream
    #     :type stream_token: Python UUID (converted to a string in function)
    #     :param version: version number of a dstream (incremented whenever a dstream is updated)
    #     :type version: decimal
    #     :param template_id: the Mongo-generated unique id
    #     :type template_id: str
    #     """
    #     add_row = ("INSERT INTO template_metadata "
    #     "(stream_name, stream_token, version, template_id) "
    #     "VALUES (%s, %s, %s, %s)")
    #     stringified_stream_token_uuid = _stringify_uuid(stream_token)
    #     row_columns = (stream_name, stringified_stream_token_uuid, version, template_id)
    #     try:
    #         logger.info("Inserting row")
    #         self.cursor.execute(add_row, row_columns)
    #         self.mariadb_connection.commit()
    #         if (self.cursor.rowcount != 1):
    #             raise KeyError
    #         else:
    #             return self.cursor.rowcount
    #             logger.info("Row inserted")
    #     except pymysql.err.ProgrammingError as err:
    #         raise err

    def return_template_id_for_latest_version_of_stream(self, stream_token):
        """
        Called by the Coordinator in the _retrieve_current_template function to obtain the Mongo-generated unique id for
        the latest version of a stream. The _retrieve_current_template function on the Coordinator class then uses
        that unique Mongo id to retrieve the template document from the Mongo database.
        :param stream_token: stream_token from a dstream
        :type stream_token: Python UUID (converted to a string in function)
        """
        stringified_stream_token_uuid = _stringify_uuid(stream_token)
        query = ("SELECT `template_id` FROM template_metadata WHERE stream_token = %s AND version = ("
                "SELECT MAX(version) FROM template_metadata WHERE stream_token = %s)")
        try:
            logger.info("Returning template_id for latest version of stream by stream_token")
            self.cursor.execute(query, [stringified_stream_token_uuid, stringified_stream_token_uuid])
            result = self.cursor.fetchall()
            if len(result) == 1:
                logger.info(result[0]["template_id"])
                return result[0]["template_id"]
            else:
                raise pymysql.err.ProgrammingError
        except pymysql.err.ProgrammingError as err:
            raise err

    # def check_metadata_table_exists(self):# NOTE replaced by sqliteDB.table_exists(table)
    #     """
    #     Called by the Coordinator in the process_template function to verify that the template_metadata
    #     table exists before creating it. This function was created to prevent errors when process_template
    #     was executed with a template_metadata table already in the database.
    #     """
    #     query = ("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'test' AND table_name = 'template_metadata'")
    #     try:
    #         logger.info("Checking if template_metadata table exists")
    #         self.cursor.execute(query)
    #         results = self.cursor.fetchall()
    #         if results[0]['COUNT(*)'] == 1:
    #             return True
    #         else:
    #             return False
    #     except pymysql.err.ProgrammingError as err:
    #         raise err
    #
    # def _check_table_exists(self, table_name):
    #     """
    #     Function for verifying successful creation of a table. Used for testing purposes.
    #     :param table_name: table name in Maria. Derived from a stream_token
    #     :type table_name: str
    #     """
    #
    #     stringified_table_name = str(table_name).replace("-", "_")
    #     query = ("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'test' AND table_name = %s")
    #     try:
    #         logger.info("Checking if table " + stringified_table_name + " exists")
    #         self.cursor.execute(query, [stringified_table_name])
    #         results = self.cursor.fetchall()
    #         if results[0]['COUNT(*)'] == 1:
    #             return True
    #         else:
    #             return False
    #     except pymysql.err.ProgrammingError as err:
    #         raise err

# ***** Stream Token Table and Methods *****
    # def create_stream_lookup_table(self, dstream):# NOTE replaced by sqliteDB.table(df, 'lookup', 'fail')
    #     """
    #     Called by the Coordinator in process_template.
    #     :param dstream: an instance of the DStream class (see the dstream module)
    #     :type dstream: DStream class object
    #     """
    #     measure_columns = ""
    #     # for each item in the measures dictionary
    #         # create a column for that measure
    #     for measure in dstream['measures']:
    #         measure_columns += "  `" + measure + "` " + dstream['measures'][measure]['dtype'] + ","
    #
    #     uid_columns = ""
    #     # for each item in the uids dictionary
    #         # create a column for that uid
    #     for uid in dstream['user_ids']:
    #         uid_columns += "  `" + uid + "` varchar(60),"
    #
    #     filter_columns = ""
    #     # for each item in the filters dictionary
    #         # create a column for that filter
    #     for filt in dstream['filters']:
    #         filter_columns += "  `" + filt["filter_name"] + "` varchar(60),"
    #
    #     stringified_stream_token_uuid = _stringify_uuid(dstream["stream_token"])
    #
    #     table = ("CREATE TABLE `%s` ("
    #         "  `unique_id` int(10) NOT NULL AUTO_INCREMENT,"
    #         "  `version` decimal(10, 2) NOT NULL,"
    #         "  `time_stamp` decimal(20, 5) NOT NULL,"
    #         "%s"
    #         "%s"
    #         "%s"
    #         "  `tags` varchar(60),"
    #         "  `fields` varchar(60),"
    #         "  PRIMARY KEY (`unique_id`)"
    #         ") ENGINE=InnoDB" % (stringified_stream_token_uuid, measure_columns, uid_columns, filter_columns))
    #     logger.info(table)
    #     dstream_particulars = (measure_columns, uid_columns, filter_columns)
    #     try:
    #         logger.info("Creating stream lookup table")
    #         self.cursor.execute(table)
    #     except pymysql.err.ProgrammingError as err:
    #         raise err

    def insert_rows_into_stream_lookup_table(self, bstream):
        """
        Called by the Coordinator in the _store_raw function and the in run function for the
        storage thread class to populate a stream look up table of a given stream token
        with a bstream.
        :param bstream: an instance of the BStream class
        :type bstream: BStream class object
        """
        stringified_stream_token_uuid = _stringify_uuid(bstream["stream_token"])

        measure_columns = ""
        # for each item in the measures dictionary
            # create a column for that measure
        for measure in bstream['measures']:
            measure_columns += "  `" + measure + "`,"

        uid_columns = ""
        # for each item in the uids dictionary
            # create a column for that uid
        for uid in bstream['user_ids']:
            uid_columns += "  `" + uid + "`,"

        columns = (
            "(`version`,"
            " `time_stamp`,"
            "%s"
            "%s"
            " `tags`,"
            " `fields`)"
        % (measure_columns, uid_columns))

        logger.info("Finished creating columns")
        measure_dict_array = list(bstream["measures"].values())
        measure_matrix = [ m['val'] for m in measure_dict_array ]
        measure_values = [ [str(item) for item in group] for group in measure_matrix ]

        uid_values = [ [str(item) for item in group] for group in list(bstream["user_ids"].values()) ]

        # tag_values = [ tag for tag in bstream["tags"].values() ]
        tag_values = str(bstream["tags"])
        field_values = [ f for f in list(bstream["fields"].values()) ]

        logger.info("Created values arrays")

        value_tuples = list(zip(itertools.repeat(bstream["version"]), bstream["timestamp"], *measure_values, *uid_values, itertools.repeat(tag_values), *field_values))
        # The number of columns for measures, user_ids, and filters vary by dstream/bstream, so we need to build the number of
        # string interpolations dynamically for the query values. There will always be at least one '%s', so the value_interpolations
        # variable will be the length of one tuple minus 1.
        value_interpolations = (len(value_tuples[0]) - 1) * ", %s"
        query = ("INSERT INTO `%s` %s " % (stringified_stream_token_uuid, columns)) + "VALUES (%s" + value_interpolations + ")"
        try:
            logger.info("Inserting rows into table " + stringified_stream_token_uuid)
            self.cursor.executemany(query, value_tuples)
            self.mariadb_connection.commit()
            logger.info("Inserted rows")
            logger.info(self.cursor.rowcount)
            return self.cursor.rowcount
        except pymysql.err.ProgrammingError as err:
            raise err

    def retrieve_by_timestamp_range(self, dstream, start, end):
        """
        Called by the Coordinator in the _retrieve_data_by_timestamp function.
        :param dstream: an instance of the DStream class (see the dstream module)
        :type dstream: obj
        :param start: the minimum timestamp for a query range
        :type start: decimal
        :param end: the maximum timestamp for a query range
        :param end: decimal
        """
        stringified_stream_token_uuid = _stringify_uuid(dstream["stream_token"])
        dstream_particulars = (stringified_stream_token_uuid, start, end)
        query = ("SELECT * FROM `%s` " % (stringified_stream_token_uuid)) + "WHERE time_stamp BETWEEN %s AND %s"
        try:
            logger.info("Returning all records within timestamp range")
            self.cursor.execute(query, [start, end])
            results = self.cursor.fetchall()
            for row in results:
                logger.info(row)
            logger.info(self.cursor.rowcount)
            return self.cursor.rowcount
        except pymysql.err.ProgrammingError as err:
            raise err

    def _select_all_from_stream_lookup_table(self, dstream):
        """
        Select all rows from a stream look up table. Used for testing purposes.
        :param dstream: an instance of the DStream class (see the dstream module)
        :type dstream: DStream class object
        """

        stringified_stream_token_uuid = _stringify_uuid(dstream["stream_token"])
        query = ("SELECT * FROM `%s`" % stringified_stream_token_uuid)
        try:
            logger.info("Returning all records from stream lookup table " + stringified_stream_token_uuid)
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            for row in results:
                logger.info(row)
            return self.cursor.rowcount
        except pymysql.err.ProgrammingError as err:
            raise err

    # def create_stream_filtered_table(self, dstream):#NOTE replaced by sqliteDB.table(df, 'filtered', 'fail')
    #     """
    #     Called by the Coordinator in the process_template function
    #     Insert row into table for storing filtered measures
    #     Creates table by parsing the dstream template
    #     :param dstream: an instance of the DStream class (see the dstream module)
    #     :type dstream: DStream class object
    #     """
    #     coll_tuples = [(f["filter_name"], mv["dtype"]) for f in dstream["filters"] for m, mv in dstream["measures"].items() if f["measures"][0] == m]
    #     measure_columns = ""
    #     # for each item in the measures dictionary
    #         # create a column for that measure
    #     for coll in coll_tuples:
    #         measure_columns += "  `" + coll[0] + "` " + coll[1] + ","
    #
    #     filter_table_stream_token_uuid = _stringify_uuid(dstream["stream_token"]) + "_filter"
    #
    #     table = ("CREATE TABLE `%s` ("
    #         "  `unique_id` int(10) NOT NULL AUTO_INCREMENT,"
    #         # "  `version` decimal(10, 2) NOT NULL,"
    #         "%s"
    #         "  `time_stamp` decimal(20, 5) NOT NULL,"
    #         "  PRIMARY KEY (`unique_id`)"
    #         ") ENGINE=InnoDB" % (filter_table_stream_token_uuid, measure_columns))
    #
    #     try:
    #         logger.info("Creating filtered measures table for stream")
    #         self.cursor.execute(table)
    #     except pymysql.err.ProgrammingError as err:
    #         raise err

    # def insert_rows_into_stream_filtered_table(self, dictionary):# NOTE replaced by sqliteDB.create(~)
    #     """
    #     Called by the Coordinator in the _store_filtered function
    #     Called by the storage thread in the run function
    #     Insert row into table for storing filtered measures
    #     :param dictionary: Python diction with stream_token, filtered measures, and timestamp for a bstream
    #     :type dictionary: dict
    #     """
    #     filter_table_stream_token_uuid = _stringify_uuid(dictionary["stream_token"]) + "_filter"
    #
    #     measure_columns = ""
    #     # for each item in the measures dictionary
    #         # create a column for that measure
    #     for measure in dictionary['filter_measures']:
    #         measure_columns += "  `" + measure + "`,"
    #
    #     columns = (
    #         # "(`version`,"
    #         "%s"
    #         " `time_stamp`"
    #     % (measure_columns))
    #
    #     logger.info("Finished creating columns")
    #     measure_dict_array = list(dictionary["filter_measures"].values())
    #     measure_matrix = [ m['val'] for m in measure_dict_array ]
    #     measure_values = [ [str(item) for item in group] for group in measure_matrix ]
    #
    #     logger.info("Created values arrays")
    #
    #     value_tuples = list(zip(*measure_values, dictionary["timestamp"]))
    #     # The number of columns for measures, user_ids, and filters vary by dstream/bstream, so we need to build the number of
    #     # string interpolations dynamically for the query values. There will always be at least one '%s', so the value_interpolations
    #     # variable will be the length of one tuple minus 1.
    #     value_interpolations = (len(value_tuples[0]) - 1) * ", %s"
    #     query = ("INSERT INTO `%s` (%s) " % (filter_table_stream_token_uuid, columns)) + "VALUES (%s" + value_interpolations + ")"
    #     try:
    #         logger.info("Inserting rows into table " + filter_table_stream_token_uuid)
    #         self.cursor.executemany(query, value_tuples)
    #         self.mariadb_connection.commit()
    #         logger.info("Inserted rows")
    #         logger.info(self.cursor.rowcount)
    #         return self.cursor.rowcount
    #     except pymysql.err.ProgrammingError as err:
    #         raise err

    #  Legacy methods no longer in use: # NOTE DEPRECATED
    # def _retrieve_by_stream_name(self, stream_name):
    #     """
    #     Retrieve dstream template by stream_name in the process data method(s). No longer used.
    #     :param stream_name: stream_name of a dstream
    #     :type stream_name: str
    #     """
    #
    #     query = ('SELECT * FROM template_metadata WHERE stream_name = %s')
    #     try:
    #         logger.info("Querying by stream name")
    #         self.cursor.execute(query, [stream_name])
    #         results = self.cursor.fetchall()
    #         for dictionary in results:
    #             logger.info("uid: {}, name: {}, stream: {}, version: {}, template_id: {}".format(dictionary["unique_id"], dictionary["stream_name"], dictionary["stream_token"], dictionary["version"], dictionary["template_id"]))
    #         return self.cursor.rowcount
    #     except pymysql.err.ProgrammingError as err:
    #         raise err
    #
    # def _retrieve_by_id(self, unique_id):
    #     """
    #     Function for selecting a row from the template_metadata table by SQL-generated id. No longer used.
    #     :param unique_id: SQL-generated unique id for a row
    #     :type unique_id: int
    #     """
    #
    #     query = ("SELECT * FROM template_metadata WHERE unique_id = %s")
    #     try:
    #         logger.info("Querying by unique id")
    #         self.cursor.execute(query, [unique_id])
    #         result = self.cursor.fetchone()
    #         logger.info("uid: {}, name: {}, stream: {}, version: {}, template_id: {}".format(result["unique_id"], result["stream_name"], result["stream_token"], result["version"], result["template_id"]))
    #         # convert version from decimal to float
    #         float_version =  float(result['version'])
    #         result['version'] = float_version
    #         return result
    #     except pymysql.err.ProgrammingError as err:
    #         raise err
    #
    # def _retrieve_by_stream_token(self, stream_token):
    #     """
    #     Function for selecting a row from the template_metadata table by stream token. No longer used.
    #     :param stream_token: stream_token from a dstream
    #     :type stream_token: Python UUID (converted to a string in function)
    #     """
    #
    #     stringified_stream_token_uuid = _stringify_uuid(stream_token)
    #     query = ("SELECT * FROM template_metadata WHERE stream_token = %s")
    #     try:
    #         logger.info("Querying by stream token")
    #         self.cursor.execute(query, [stringified_stream_token_uuid])
    #         results = self.cursor.fetchall()
    #         for dictionary in results:
    #             logger.info("uid: {}, name: {}, stream: {}, version: {}, template_id: {}".format(dictionary["unique_id"], dictionary["stream_name"], dictionary["stream_token"], dictionary["version"], dictionary["template_id"]))
    #         return self.cursor.rowcount
    #     except pymysql.err.ProgrammingError as err:
    #         raise err
    #
    # def _select_all_from_metadata_table(self):
    #     """
    #     Select all rows from the template_metadata table. No longer used.
    #     """
    #
    #     query = ("SELECT * FROM template_metadata")
    #     try:
    #         logger.info("Returning all data from template_metadata table")
    #         self.cursor.execute(query)
    #         results = self.cursor.fetchall()
    #         for row in results:
    #             logger.info(row)
    #         return self.cursor.rowcount
    #     except pymysql.err.ProgrammingError as err:
    #         raise err
    #
    # def _insert_row_into_stream_lookup_table(self, dstream):
    #     """
    #     Called by the Coordinator in the _store_raw_old function to insert rows one by one.
    #     No longer used.
    #     :param dstream: an instance of the DStream class (see the dstream module)
    #     :type dstream: DStream class object
    #     """
    #
    #     stringified_stream_token_uuid = _stringify_uuid(dstream["stream_token"])
    #
    #     measure_columns = ""
    #     # for each item in the measures dictionary
    #         # create a column for that measure
    #     for measure in dstream['measures']:
    #         measure_columns += "  `" + measure + "`,"
    #
    #     uid_columns = ""
    #     # for each item in the uids dictionary
    #         # create a column for that uid
    #     for uid in dstream['user_ids']:
    #         uid_columns += "  `" + uid + "`,"
    #
    #     columns = (
    #         "(`version`,"
    #         " `time_stamp`,"
    #         "%s"
    #         "%s"
    #         " `tags`,"
    #         " `fields`)"
    #     % (measure_columns, uid_columns))
    #
    #     measure_values = ""
    #     for key, value in dstream["measures"].items():
    #         # measure_values += ' "' + str(value["val"]) + '",'
    #         measure_values += _stringify_by_adding_quotes(value["val"]) + ','
    #
    #     uid_values = ""
    #     for key, value in dstream["user_ids"].items():
    #         # uid_values += ' "' + str(value) + '",'
    #         uid_values += _stringify_by_adding_quotes(value) + ','
    #
    #     values = (
    #         "(%s, "
    #         "%s,"
    #         "%s"
    #         "%s"
    #         "%s,"
    #         "%s)"
    #     % (dstream["version"], dstream["timestamp"], measure_values, uid_values, _stringify_by_adding_quotes(dstream["tags"]), _stringify_by_adding_quotes(dstream["fields"])))
    #
    #     query = ("INSERT INTO `%s` %s VALUES %s" % (stringified_stream_token_uuid, columns, values))
    #
    #     try:
    #         logger.info("Inserting row into table " + stringified_stream_token_uuid)
    #         self.cursor.execute(query)
    #         self.mariadb_connection.commit()
    #         logger.info("Inserted row")
    #         logger.info(self.cursor.lastrowid)
    #         return self.cursor.lastrowid
    #     except pymysql.err.ProgrammingError as err:
    #         raise err
    #
    # def _insert_filtered_measure_into_stream_lookup_table(self, stream_token, filtered_measure, value, unique_id):
    #     """
    #     Called by the Coordinator in the _store_filtered_old_dumb function. No longer used because of its
    #     inefficiency.
    #     :param stream_token: stream_token from a dstream
    #     :type stream_token: Python UUID (converted to a string in function)
    #     :param filtered_measure: the name of a filtered measure
    #     :type filtered_measure: str
    #     :param value: value for the filtered_measure
    #     :type value: str
    #     :param unique_id: SQL-generated unique id for a row
    #     :type unique_id: int
    #     """
    #
    #     stringified_stream_token_uuid = _stringify_uuid(stream_token)
    #     # Using string interpolation for the table and column name in the construction of the SQL query before the
    #     # self.execute() call.
    #     # Note that the string interpolation for the values themselves will still be interpolated in the self.execute()
    #     # call, but the interpolation for the table and column names occur beforehand.
    #     query = ("UPDATE `%s` SET %s " % (stringified_stream_token_uuid, filtered_measure)) + "= %s WHERE unique_id = %s"
    #     parameters = (value, unique_id)
    #     try:
    #         logger.info("Updating", filtered_measure, "at", unique_id)
    #         self.cursor.execute(query, parameters)
    #         self.mariadb_connection.commit()
    #         logger.info("Updated", filtered_measure, "at", unique_id)
    #         if (self.cursor.rowcount != 1):
    #             raise KeyError
    #         return self.cursor.rowcount
    #     except pymysql.err.ProgrammingError as err:
    #         raise err
    #
    # def _select_data_by_column_where(self, dstream, data_column, filter_column, value):
    #     """
    #     Return all values in a stream lookup table for a given column. Formerly used for testing purposes.
    #     :param dstream: an instance of the DStream class (see the dstream module)
    #     :type dstream: DStream class object
    #     :param data_column: the data of a table column that we want to retrieve by a specific filter_column value
    #     :type data_column: str/int/decimal
    #     :param filter_column: name of a filtered measure
    #     :type filter_column: str
    #     :param value: value for the filtered_measure
    #     :type value: str
    #     """
    #
    #     stringified_stream_token_uuid = _stringify_uuid(dstream["stream_token"])
    #     query = ("SELECT `%s` FROM %s WHERE %s = %s" % (data_column, stringified_stream_token_uuid, filter_column, value))
    #     try:
    #         logger.info("Returning data")
    #         self.cursor.execute(query)
    #         results = self.cursor.fetchall()
    #         logger.info(results)
    #         return self.cursor.rowcount
    #     except pymysql.err.ProgrammingError as err:
    #         raise err
