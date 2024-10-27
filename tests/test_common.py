import pytest
from cores.common import read_config, filter_dict
import os
import json


class TestReadConfig:
    def setup_method(self):
        expected_config = {
            "a": 42,
            "b": "test",
            "c": [1, 2, 3],
        }

        config_path = "tests/config.json"
        with open(config_path, 'w') as f:
            json.dump(expected_config, f)

        self.config_path = config_path
        self.expected_config = expected_config

    def teardown_method(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_read_config(self):
        returned_config = read_config(
            self.config_path, set(
                self.expected_config.keys()))
        assert returned_config == self.expected_config

    def test_read_config_missing_file(self):
        with pytest.raises(FileNotFoundError):
            read_config("dummy/missing.json", [])

    def test_read_config_missing_key(self):
        required_keys = ["a", "b", "d"]
        with pytest.raises(KeyError):
            read_config(self.config_path, required_keys)


class TestExcludeFilterDict:
    def setup_method(self):
        self.dic = {'a': 1, 'b': 2, 'c': 3}

    def teardown_method(self):
        actual_output = filter_dict(
            self.dic, lambda k, _: k not in self.excluded_keys)
        assert actual_output == self.expected_output

    def test_filter_dict(self):
        self.excluded_keys = {'b', 'c'}
        self.expected_output = {'a': 1}

    def test_filter_dict_empty(self):
        self.excluded_keys = {'a', 'b', 'c'}
        self.expected_output = {}

    def test_filter_dict_all(self):
        self.excluded_keys = set(self.dic.keys())
        self.expected_output = {}

    def test_filter_dict_not_excluded(self):
        self.excluded_keys = {'d'}
        self.expected_output = self.dic


class TestIncludeFilterDict:
    def setup_method(self):
        self.dic = {'a': 1, 'b': 2, 'c': 3}

    def teardown_method(self):
        actual_output = filter_dict(
            self.dic, lambda k, _: k in self.included_keys)
        assert actual_output == self.expected_output

    def test_filter_dict(self):
        self.included_keys = {'b', 'c'}
        self.expected_output = {'b': 2, 'c': 3}

    def test_filter_dict_empty(self):
        self.included_keys = set()
        self.expected_output = {}

    def test_filter_dict_all(self):
        self.included_keys = set(self.dic.keys())
        self.expected_output = self.dic

    def test_filter_dict_not_included(self):
        self.included_keys = {'d'}
        self.expected_output = {}
