import abc


class FileStorage(abc.ABC):
    @abc.abstractmethod
    def read_file(self, name: str) -> bytes:
        ...

    @abc.abstractmethod
    def save_file(self, name: str, content: bytes) -> None:
        ...

    @abc.abstractmethod
    def delete_file(self, name: str) -> None:
        ...

    @abc.abstractmethod
    def file_exists(self, name: str) -> bool:
        ...
