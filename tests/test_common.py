from cores.common import filter_dict


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
