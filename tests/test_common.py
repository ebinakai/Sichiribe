import pytest
from cores.common import load_setting, filter_dict
import os
import json
from pathlib import Path


class TestReadConfig:
    def setup_class(self):
        expected_setting = {
            "a": 42,
            "b": "test",
            "c": [1, 2, 3],
        }

        setting_path = "tests/setting.json"
        with open(setting_path, "w") as f:
            json.dump(expected_setting, f)

        self.setting_path = setting_path
        self.expected_setting = expected_setting

    def teardown_class(self):
        if Path(self.setting_path).exists():
            os.remove(self.setting_path)

    def test_load_setting(self):
        returned_setting = load_setting(
            self.setting_path, set(self.expected_setting.keys())
        )
        assert returned_setting == self.expected_setting

    def test_load_setting_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_setting("dummy/missing.json", [])

    def test_load_setting_missing_key(self):
        required_keys = ["a", "b", "d"]
        with pytest.raises(KeyError):
            load_setting(self.setting_path, required_keys)


class TestExcludeFilterDict:
    def setup_method(self):
        self.dic = {"a": 1, "b": 2, "c": 3}

    def teardown_method(self):
        actual_output = filter_dict(self.dic, lambda k, _: k not in self.excluded_keys)
        assert actual_output == self.expected_output

    def test_filter_dict(self):
        self.excluded_keys = {"b", "c"}
        self.expected_output = {"a": 1}

    def test_filter_dict_empty(self):
        self.excluded_keys = {"a", "b", "c"}
        self.expected_output = {}

    def test_filter_dict_all(self):
        self.excluded_keys = set(self.dic.keys())
        self.expected_output = {}

    def test_filter_dict_not_excluded(self):
        self.excluded_keys = {"d"}
        self.expected_output = self.dic


class TestIncludeFilterDict:
    def setup_method(self):
        self.dic = {"a": 1, "b": 2, "c": 3}

    def teardown_method(self):
        actual_output = filter_dict(self.dic, lambda k, _: k in self.included_keys)
        assert actual_output == self.expected_output

    def test_filter_dict(self):
        self.included_keys = {"b", "c"}
        self.expected_output = {"b": 2, "c": 3}

    def test_filter_dict_empty(self):
        self.included_keys = set()
        self.expected_output = {}

    def test_filter_dict_all(self):
        self.included_keys = set(self.dic.keys())
        self.expected_output = self.dic

    def test_filter_dict_not_included(self):
        self.included_keys = {"d"}
        self.expected_output = {}
