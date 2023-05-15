import pytest

from app.storage import LocalFileStorage


def test_save_file_saves_corectly(tmp_path):
    file_storage = LocalFileStorage(tmp_path)
    file_storage.save_file("test", b"test")
    assert (tmp_path / "test").read_bytes() == b"test"


def test_read_file_returns_correctly(tmp_path):
    file_storage = LocalFileStorage(tmp_path)
    file_storage.save_file("test", b"test")
    assert file_storage.read_file("test") == b"test"


def test_read_file_raises_on_missing_file(tmp_path):
    file_storage = LocalFileStorage(tmp_path)
    with pytest.raises(FileNotFoundError):
        file_storage.read_file("test")
