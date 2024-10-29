from unittest.mock import Mock, patch
from cores.exporter import Exporter
import os


class TestExporter:
    def setup_method(self):
        self.exporter = Exporter("dummy_dir")

    def teardown_method(self):
        os.rmdir("dummy_dir")

    def test_format(self):

        data = [1, 2, 3]
        data2 = [0.5, 0.1, 0]
        timestamp = [
            "2024-10-01T00:00:00Z",
            "2024-10-01T01:00:00Z",
            "2024-10-01T02:00:00Z",
        ]
        expected_output = [
            {"timestamp": "2024-10-01T00:00:00Z", "value": 1, "failed": 0.5},
            {"timestamp": "2024-10-01T01:00:00Z", "value": 2, "failed": 0.1},
            {"timestamp": "2024-10-01T02:00:00Z", "value": 3, "failed": 0},
        ]

        actual_output = self.exporter.format(data, data2, timestamp)
        assert actual_output == expected_output

    @patch("cores.exporter.get_now_str")
    def test_generate_filepath(self, mock_get_now_str):
        mock_get_now_str.return_value = "20240535000000"
        prefix = "test"
        extension = "csv"
        expected_output = "dummy_dir/test_20240535000000.csv"

        actual_output = self.exporter.generate_filepath(
            prefix, extension, with_timestamp=True
        )
        assert str(actual_output) == expected_output

    def test_export_csv(self):
        data = {"a": 1, "b": 2}
        prefix = "test"
        self.exporter.to_csv = Mock()
        self.exporter.export(data, "csv", prefix)

        self.exporter.to_csv.assert_called_once_with([data], prefix, True)

    def test_export_json(self):
        data = {"a": 1, "b": 2}
        prefix = "test"
        self.exporter.to_json = Mock()
        self.exporter.export(data, "json", prefix)

        self.exporter.to_json.assert_called_once_with(data, prefix, True)
