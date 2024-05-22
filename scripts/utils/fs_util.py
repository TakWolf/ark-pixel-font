import os
import shutil
import tomllib
from typing import Any


def delete_dir(path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
    if os.path.exists(path):
        shutil.rmtree(path)


def read_str(path: str | bytes | os.PathLike[str] | os.PathLike[bytes]) -> str:
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()


def write_str(text: str, path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(text)


def read_toml(path: str | bytes | os.PathLike[str] | os.PathLike[bytes]) -> Any:
    return tomllib.loads(read_str(path))
