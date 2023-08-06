import os
import shutil
from collections.abc import Iterator


def delete_dir(path: str):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception(f"Path not a directory: '{path}'")
        shutil.rmtree(path)


def make_dirs(path: str):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception(f"Path exists but not a directory: '{path}'")
    else:
        os.makedirs(path)


def walk_files(path: str) -> Iterator[tuple[str, str]]:
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception(f"Path not a directory: '{path}'")
        for parent, _, names in os.walk(path):
            for name in names:
                yield parent, name
