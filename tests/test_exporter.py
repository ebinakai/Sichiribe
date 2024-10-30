from cores.export_utils import build_data_records


class TestBuildDataRecords:
    def test_basic_case(self):
        data_dict = {
            "timestamp": [1, 2, 3],
            "value": [100, 200, 300],
            "failed": [False, True, False],
        }
        expected = [
            {"timestamp": 1, "value": 100, "failed": False},
            {"timestamp": 2, "value": 200, "failed": True},
            {"timestamp": 3, "value": 300, "failed": False},
        ]
        assert build_data_records(data_dict) == expected

    def test_empty_dict(self):
        data_dict = {}
        expected = []
        assert build_data_records(data_dict) == expected

    def test_single_key_single_value(self):
        data_dict = {"timestamp": [1]}
        expected = [{"timestamp": 1}]
        assert build_data_records(data_dict) == expected
