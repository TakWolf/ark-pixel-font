import shutil
import tomllib
from pathlib import Path
from typing import Any


def delete_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)


def is_empty_dir(path: Path) -> bool:
    for item_path in path.iterdir():
        if item_path.name == '.DS_Store':
            continue
        return False
    return True


def read_toml(path: Path) -> Any:
    return tomllib.loads(path.read_text('utf-8'))
