import json

from .abstract_interface import StorageInterface
from .sqlitedb import SqliteDB

__version__ = '0.0.1'
__author__ = 'Molly LeCompte'


class SqliteInterface(StorageInterface):
    def __init__(self, db_file):
        super().__init__()
        self.db = SqliteDB(db_file)

    def store_template(self, template_df):
        self.db.create(template_df, 'templates')

    def retrieve_template_by_id(self, template_id):
        result_df = self.db.retrieve('templates', 'template_id', f"'{template_id}'")

        if result_df.shape[0] == 1:
            # return json.loads(result_df.iloc[0])
            return result_df.iloc[0]
        # print(result_df.shape[0])

        # HANDLE CASES WITH 0 OR MULTI RESULT

    def retrieve_current_template(self, stream_token):
        result_df = self.db.retrieve(f'templates', 'stream_token', stream_token, latest=True)

        if result_df.shape[0] == 1:
            return json.loads(result_df.iloc[0])

        # HANDLE CASES WITH 0 OR MULTI RESULT

    def retrieve_all_templates(self):
        return self.db.select(query='SELECT * FROM templates')

    def store_bstream_data(self, token, bstream_df):
        object_columns = list(bstream_df.select_dtypes(include=["object"]).columns)
        self.db.create(self.db.serialize(bstream_df, object_columns), f'{token}_data')

    def retrieve_data(self, stream_token, *retrieval_args, **retrieval_kwargs):
        retrieval_args = [arg for arg in retrieval_args]
        # ADD VALIDATION FOR RETRIEVAL ARGS
        query = f'SELECT {retrieval_args} from {stream_token}_data'.replace("[", "").replace("]", "").replace("'", "")
        if "start_ts" in retrieval_kwargs:
            start = retrieval_kwargs['start_ts']
            query = query + f' AND timestamp >= {start}'
        if "end_ts" in retrieval_kwargs:
            end = retrieval_kwargs['end_ts']
            query = query + f' AND timestamp <= {end}'

        result = self.db.select(query=query)

        return result

    def retrieve_all_by_token(self, stream_token):# NEW
        return self.db.retrieve("templates", "stream_token", f"'{stream_token}'")

    def retrieve_current_by_id(self, template_id):# NEW
        return self.db.retrieve("templates", "template_id", f"'{template_id}'", latest=True)

    def open_connection(self):
        self.db.connect()

    def close_connection(self):
        self.db.close()