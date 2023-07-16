import os
import pathlib
import typing
import pandas as pd
import time

from .base import FileStorage


class LocalFileStorage(FileStorage):
    data_folder: typing.ClassVar[pathlib.Path | str]

    @classmethod
    def set_data_folder(cls, data_folder: pathlib.Path | str) -> None:
        if isinstance(data_folder, str):
            data_folder = pathlib.Path(data_folder)
        if data_folder.exists() and not data_folder.is_dir():
            raise ValueError(f"{data_folder} is not a directory")
        if not data_folder.exists():
            os.makedirs(data_folder)
        cls.data_folder = data_folder

    def read_file(self, name: str) -> bytes:
        if not hasattr(self, "data_folder"):
            raise ValueError("data_folder is not set")
        with open(self.data_folder / name, "rb") as f:
            return f.read()

    def save_file(self, name: str, content: bytes) -> None:
        if not hasattr(self, "data_folder"):
            raise ValueError("data_folder is not set")
        with open(self.data_folder / name, "wb") as f:
            f.write(content)

    def delete_file(self, name: str, seconds: int = 0) -> None:
        time.sleep(seconds)
        if not hasattr(self, "data_folder"):
            raise ValueError("data_folder is not set")
        file_path = self.data_folder / name
        if file_path.exists():
            os.remove(file_path)
        else:
            raise FileNotFoundError(f"File {file_path} does not exist")

    def file_exists(self, name: str) -> bool:
        if not hasattr(self, "data_folder"):
            raise ValueError("data_folder is not set")
        file_path = self.data_folder / name
        return file_path.exists()
