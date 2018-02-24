import json
import pandas

from .abstract_interface import StorageInterface
from .sqlitedb import SqliteDB

__version__ = '0.0.1'
__author__ = 'Molly LeCompte'

default = pandas.DataFrame.from_dict([{"stream_name": "driver_data", "version": 0, "stream_token": "abc123","template_id":"tempID","user_description":"demo template for unit tests", "timestamp": None, "measures": {"location": {"val": None, "dtype": "varchar(60)"}}, "fields": {"region-code": {}}, "user_ids": {"driver-id": {}, "id": {}}, "tags": {}, "foreign_keys": [], "filters": [{"partition_list": [], "measure_list": ["timestamp"], "transform_type": "filter_data", "transform_name": "ButterLowpass", "param_dict": {"order": 2, "nyquist": 0.01, "filter_name": "_buttery"}, "logical_comparison": "AND"}, {"partition_list": [], "measure_list": ["timestamp"], "transform_type": "filter_data", "transform_name": "WindowAverage", "param_dict": {"window_len": 3, "filter_name": "_winning"}, "logical_comparison": "AND"}], "dparam_rules": [{"partition_list": [["timestamp", 1510603551106, ">"], ["timestamp", 1510603551391, "<"]], "measure_list": ["timestamp", "timestamp_winning"], "transform_type": "derive_param", "transform_name": "DeriveSlope", "param_dict": {"func_params": {"window_len": 1}, "measure_rules": {"rise_measure": "timestamp_winning", "run_measure": "timestamp", "output_name": "time_slope"}}, "logical_comparison": "AND"}, {"partition_list": [], "measure_list": ["timestamp"], "transform_type": "derive_param", "transform_name": "DeriveChange", "param_dict": {"func_params": {"window_len": 1, "angle_change": False}, "measure_rules": {"target_measure": "timestamp", "output_name": "time_change"}}, "logical_comparison": "AND"}, {"partition_list": [], "measure_list": ["timestamp"], "transform_type": "derive_param", "transform_name": "DeriveCumsum", "param_dict": {"func_params": {"offset": 0}, "measure_rules": {"target_measure": "timestamp", "output_name": "time_sum"}}, "logical_comparison": "AND"}, {"partition_list": [], "measure_list": ["timestamp"], "transform_type": "derive_param", "transform_name": "DeriveWindowSum", "param_dict": {"func_params": {"window_len": 3}, "measure_rules": {"target_measure": "timestamp", "output_name": "time_window_sum"}}, "logical_comparison": "AND"}, {"partition_list": [], "measure_list": ["timestamp"], "transform_type": "derive_param", "transform_name": "DeriveScaled", "param_dict": {"func_params": {"scalar": -1}, "measure_rules": {"target_measure": "timestamp", "output_name": "negatime"}}, "logical_comparison": "AND"}, {"partition_list": [], "measure_list": ["location"], "transform_type": "derive_param", "transform_name": "DeriveDistance", "param_dict": {"func_params": {"window_len": 1, "distance_func": "euclidean", "swap_lon_lat": True}, "measure_rules": {"spatial_measure": "location", "output_name": "dist1"}}, "logical_comparison": "AND"}, {"partition_list": [], "measure_list": ["location"], "transform_type": "derive_param", "transform_name": "DeriveDistance", "param_dict": {"func_params": {"window_len": 1, "distance_func": "great_circle", "swap_lon_lat": True}, "measure_rules": {"spatial_measure": "location", "output_name": "dist2"}}, "logical_comparison": "AND"}, {"partition_list": [], "measure_list": ["location"], "transform_type": "derive_param", "transform_name": "DeriveHeading", "param_dict": {"func_params": {"window_len": 1, "units": "deg", "heading_type": "bearing", "swap_lon_lat": True}, "measure_rules": {"spatial_measure": "location", "output_name": "head1"}}, "logical_comparison": "AND"}, {"partition_list": [], "measure_list": ["location"], "transform_type": "derive_param", "transform_name": "DeriveHeading", "param_dict": {"func_params": {"window_len": 1, "units": "deg", "heading_type": "flat_angle", "swap_lon_lat": True}, "measure_rules": {"spatial_measure": "location", "output_name": "head2"}}, "logical_comparison": "AND"}, {"partition_list": [], "measure_list": ["location"], "transform_type": "derive_param", "transform_name": "DeriveInBox", "param_dict": {"func_params": {"upper_left_corner": [-122.6835826856399, 45.515814287782455], "lower_right_corner": [-122.678529, 45.511597]}, "measure_rules": {"spatial_measure": "location", "output_name": "boxy"}}, "logical_comparison": "AND"}], "event_rules": {"test_event": {"partition_list": [], "measure_list": ["timestamp", "head1"], "transform_type": "detect_event", "transform_name": "DetectThreshold", "param_dict": {"event_rules": {"measure": "head1", "threshold_value": 69.2, "comparison_operator": ">=", "absolute_compare": True}, "event_name": "nice_event", "stream_id": "abc123"}, "logical_comparison": "AND"}}, "storage_rules": {"store_raw": True, "store_filtered": True, "store_derived": True}, "engine_rules": {"kafka": "test"}}])


class SqliteInterface(StorageInterface):
    def __init__(self, db_file):
        super().__init__()
        self.db = SqliteDB(db_file)

    def seed_template_table(self):
        self.open_connection()
        self.db.serialize(default, default.columns.values.tolist())
        self.db.table(default, "templates", "fail")
        self.close_connection()

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
        query = f"SELECT {retrieval_args} from '{stream_token}_data';".replace("[", "").replace("]", "").replace("'*'", "*")
        if "start_ts" in retrieval_kwargs:
            start = retrieval_kwargs['start_ts']
            query = query + f' AND timestamp >= {start}'
        if "end_ts" in retrieval_kwargs:
            end = retrieval_kwargs['end_ts']
            query = query + f' AND timestamp <= {end}'

        print(query)
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