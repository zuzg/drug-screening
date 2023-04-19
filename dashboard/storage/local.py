import os
import pathlib

from .base import FileStorage


class LocalFileStorage(FileStorage):
    def __init__(
        self,
        data_folder: pathlib.Path | str,
    ) -> None:
        if isinstance(data_folder, str):
            data_folder = pathlib.Path(data_folder)
        if data_folder.exists() and not data_folder.is_dir():
            raise ValueError(f"{data_folder} is not a directory")
        if not data_folder.exists():
            os.makedirs(data_folder)
        self.data_folder = data_folder

    def read_file(self, name: str) -> bytes:
        with open(self.data_folder / name, "rb") as f:
            return f.read()

    def save_file(self, name: str, content: bytes) -> None:
        with open(self.data_folder / name, "wb") as f:
            f.write(content)
