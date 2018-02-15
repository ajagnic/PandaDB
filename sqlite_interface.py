from .abstract_interface import StorageInterface
from .sqlitedb import SqliteDB


__version__ = '0.0.1'
__author__ = 'Molly LeCompte'

class SqliteInterface(StorageInterface):
    def __init__(self, db_file):
        super().__init__()
        self.db = SqliteDB(db_file)

    def store_template(self, template):
        self.db.create(template, f'{template["stream_token"]}_templates')

    def retrieve_template_by_id(self, template_id):
