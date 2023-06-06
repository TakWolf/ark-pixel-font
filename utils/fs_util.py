import os
import shutil
from typing import Iterator


def delete_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)


def make_dirs(path: str):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception(f"Path exists but not a directory: '{path}'")
    else:
        os.makedirs(path)


def walk_files(top: str) -> Iterator[tuple[str, str]]:
    for parent, _, names in os.walk(top):
        for name in names:
            yield parent, name
