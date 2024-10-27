from cores.exporter import Exporter


class TestExporter:
    def setup_method(self):
        self.exporter = Exporter('dummy', 'dummy_dir')

    def test_format(self):

        data = [1, 2, 3]
        data2 = [0.5, 0.1, 0]
        timestamp = [
            '2024-10-01T00:00:00Z',
            '2024-10-01T01:00:00Z',
            '2024-10-01T02:00:00Z']
        expected_output = [
            {"timestamp": '2024-10-01T00:00:00Z', "value": 1, "failed": 0.5},
            {"timestamp": '2024-10-01T01:00:00Z', "value": 2, "failed": 0.1},
            {"timestamp": '2024-10-01T02:00:00Z', "value": 3, "failed": 0}
        ]

        actual_output = self.exporter.format(data, data2, timestamp)
        assert actual_output == expected_output

    def test_filter_dict(self):

        dic = {'a': 1, 'b': 2, 'c': 3}
        excluded_keys = ['b', 'c']
        expected_output = {'a': 1}

        actual_output = self.exporter.filter_dict(dic, excluded_keys)
        assert actual_output == expected_output
