from functools import lru_cache
import os
from typing import BinaryIO

from src.core.config import BASE_DIR, settings
from urllib.parse import quote, urljoin


class StorageBackend():
    def __init__(self) -> None:
        pass

    def upload_file(self, file: BinaryIO, path: str) -> str:
        '''
        Uploads the file to the server and returns a url to that file
        '''

        raise NotImplementedError()

    def get_file(self, path: str) -> bytes | None:
        '''
        Gets the file
        '''

        raise NotImplementedError()

class FileStorageBackend(StorageBackend):
    def __init__(self) -> None:
        super().__init__()

        path = settings.static_path
        if path.startswith('/'):
            path = path[1:]

        self.base_path = path
        self.base_url = settings.static_url
        print(self.base_url, self.base_path)


    def _filepath_to_uri(self, path):
        """Convert a file system path to a URI portion that is suitable for
        inclusion in a URL.

        Encode certain chars that would normally be recognized as special chars
        for URIs. Do not encode the ' character, as it is a valid character
        within URIs. See the encodeURIComponent() JavaScript function for details.
        """
        if path is None:
            return path
        # I know about `os.sep` and `os.altsep` but I want to leave
        # some flexibility for hardcoding separators.
        return quote(str(path).replace("\\", "/"), safe="/~!*()'")

    def get_url(self, path: str | None) -> str | None:
        if path is None:
            return None

        path = self._filepath_to_uri(f'static/{path}')
        return urljoin(self.base_url, path)

    def upload_file(self, file: BinaryIO, path: str) -> str:
        if path.startswith('/'):
            path = path[1:]

        file_path = BASE_DIR.parent / self.base_path / path
        file_dir ='/'.join(str(file_path.resolve()).split('/')[:-1])
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        with open(file_path, 'wb') as f:
            file.seek(0)
            f.write(file.read())

        return path

    def get_file(self, path: str) -> bytes | None:
        if path.startswith('/'):
            path = path[1:]

        file_path = BASE_DIR.parent / self.base_path / path
        if not os.path.exists(file_path):
            return None

        file_data: bytes | None = None
        with open(file_path, 'rb') as f:
            file_data = f.read()

        return file_data

@lru_cache
def get_storage_backend():
    return FileStorageBackend()

storage_backend = get_storage_backend()
