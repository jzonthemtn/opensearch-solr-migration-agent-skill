"""Tests for storage.py"""
import sys
import os
import json
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from storage import FileStorage, StorageInterface


@pytest.fixture
def tmp_storage(tmp_path):
    return FileStorage(base_path=str(tmp_path))


def test_save_and_load(tmp_storage):
    data = {"key": "value", "count": 42}
    tmp_storage.save("session1", data)
    loaded = tmp_storage.load("session1")
    assert loaded == data


def test_load_nonexistent_returns_none(tmp_storage):
    assert tmp_storage.load("does-not-exist") is None


def test_list_sessions_empty(tmp_storage):
    assert tmp_storage.list_sessions() == []


def test_list_sessions_after_save(tmp_storage):
    tmp_storage.save("s1", {})
    tmp_storage.save("s2", {})
    sessions = tmp_storage.list_sessions()
    assert set(sessions) == {"s1", "s2"}


def test_save_overwrites(tmp_storage):
    tmp_storage.save("s1", {"v": 1})
    tmp_storage.save("s1", {"v": 2})
    assert tmp_storage.load("s1") == {"v": 2}


def test_creates_directory_if_missing(tmp_path):
    new_dir = str(tmp_path / "new_sessions")
    storage = FileStorage(base_path=new_dir)
    assert os.path.exists(new_dir)


def test_file_storage_is_storage_interface():
    assert issubclass(FileStorage, StorageInterface)


def test_save_complex_data(tmp_storage):
    data = {"history": [{"user": "hi", "assistant": "hello"}], "facts": {"migrated": True}}
    tmp_storage.save("complex", data)
    assert tmp_storage.load("complex") == data
