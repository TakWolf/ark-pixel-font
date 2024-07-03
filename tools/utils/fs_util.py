import shutil
from pathlib import Path
from typing import Any

import yaml


def delete_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)


def is_empty_dir(path: Path) -> bool:
    for item_path in path.iterdir():
        if item_path.name == '.DS_Store':
            continue
        return False
    return True


def read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text('utf-8'))
