import logging
import os
import shutil
import tomllib
from typing import Any

logger = logging.getLogger('fs_util')


def make_dir(path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception(f"Path exists but not a directory: '{path}'")
    else:
        os.makedirs(path)
        logger.info("Make directory: '%s'", path)


def delete_file(path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
    if os.path.exists(path):
        if not os.path.isfile(path):
            raise Exception(f"Path not a file: '{path}'")
        os.remove(path)
        logger.info("Delete file: '%s'", path)


def delete_dir(path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception(f"Path not a directory: '{path}'")
        shutil.rmtree(path)
        logger.info("Delete directory: '%s'", path)


def delete_item(path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
    if os.path.isfile(path):
        os.remove(path)
        logger.info("Delete file: '%s'", path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
        logger.info("Delete directory: '%s'", path)


def copy_the_file(
        name: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        dir_from: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        dir_to: str | bytes | os.PathLike[str] | os.PathLike[bytes],
):
    path_from = os.path.join(dir_from, name)
    path_to = os.path.join(dir_to, name)
    shutil.copyfile(path_from, path_to)
    logger.info("Copy file: '%s' -> '%s'", path_from, path_to)


def copy_the_dir(
        name: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        dir_from: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        dir_to: str | bytes | os.PathLike[str] | os.PathLike[bytes],
):
    path_from = os.path.join(dir_from, name)
    path_to = os.path.join(dir_to, name)
    shutil.copytree(path_from, path_to)
    logger.info("Copy directory: '%s' -> '%s'", path_from, path_to)


def copy_the_item(
        name: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        dir_from: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        dir_to: str | bytes | os.PathLike[str] | os.PathLike[bytes],
):
    path_from = os.path.join(dir_from, name)
    path_to = os.path.join(dir_to, name)
    if os.path.isfile(path_from):
        shutil.copyfile(path_from, path_to)
        logger.info("Copy file: '%s' -> '%s'", path_from, path_to)
    elif os.path.isdir(path_from):
        shutil.copytree(path_from, path_to)
        logger.info("Copy directory: '%s' -> '%s'", path_from, path_to)


def read_str(path: str | bytes | os.PathLike[str] | os.PathLike[bytes]) -> str:
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()


def write_str(text: str, path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(text)


def read_toml(path: str | bytes | os.PathLike[str] | os.PathLike[bytes]) -> Any:
    return tomllib.loads(read_str(path))
