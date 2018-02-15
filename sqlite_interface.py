import json
from .abstract_interface import StorageInterface
from .sqlitedb import SqliteDB


__version__ = '0.0.1'
__author__ = 'Molly LeCompte'


class SqliteInterface(StorageInterface):
    def __init__(self, db_file):
        super().__init__()
        self.db = SqliteDB(db_file)

    def store_template(self, template):
        self.db.create(template, 'templates')

    def retrieve_template_by_id(self, template_id):
        result_df = self.db.retrieve('templates', 'template_id', template_id)

        if result_df.size == 1:
            return json.loads(result_df.iloc[0])

        # HANDLE CASES WITH 0 OR MULTI RESULT

    def retrieve_current_template(self, stream_token):
        result_df = self.db.retrieve(f'templates', 'stream_token', stream_token, latest=True)

        if result_df.size == 1:
            return json.loads(result_df.iloc[0])

        # HANDLE CASES WITH 0 OR MULTI RESULT

    def store_bstream(self, bstream):
        token = bstream["stream_token"]
        self.db.create(bstream, f'{token}_data')

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