import pytest

from dashboard.storage import LocalFileStorage


@pytest.fixture
def temp_file_storage(tmp_path) -> LocalFileStorage:
    LocalFileStorage.set_data_folder(tmp_path)
    file_storage = LocalFileStorage()
    return file_storage


def test_save_file_saves_corectly(temp_file_storage: LocalFileStorage, tmp_path):
    temp_file_storage.save_file("test", b"test")
    assert (tmp_path / "test").read_bytes() == b"test"


def test_read_file_returns_correctly(temp_file_storage: LocalFileStorage):
    temp_file_storage.save_file("test", b"test")
    assert temp_file_storage.read_file("test") == b"test"


def test_read_file_raises_on_missing_file(temp_file_storage: LocalFileStorage):
    with pytest.raises(FileNotFoundError):
        temp_file_storage.read_file("test")
