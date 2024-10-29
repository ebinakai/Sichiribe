import pytest
from gui.utils.data_store import DataStore


class TestDataStore:
    def setup_method(self):
        self.data_store = DataStore.get_instance()
        self.data_store.clear()

    def test_set(self):
        self.data_store.set("key", "value")
        assert self.data_store.get("key") == "value"

    def test_get_missing_key(self):
        with pytest.raises(ValueError):
            self.data_store.get("missing_key")

    def test_set_all(self):
        self.data_store.set("key1", "value1")
        self.data_store.set_all({"key2": "value2", "key3": "value3"})
        assert self.data_store.get_all() == {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }

    def test_get_all(self):
        self.data_store.set("key1", "value1")
        self.data_store.set("key2", "value2")
        assert self.data_store.get_all() == {"key1": "value1", "key2": "value2"}

    def test_has(self):
        self.data_store.set("key", "value")
        assert self.data_store.has("key")
        assert not self.data_store.has("missing_key")

    def test_clear(self):
        self.data_store.set("key", "value")
        self.data_store.clear()
        assert self.data_store.get_all() == {}

    def test_singleton(self):
        with pytest.raises(Exception):
            DataStore()
