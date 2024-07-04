from pathlib import Path
from typing import Any

import yaml


def is_empty_dir(path: Path) -> bool:
    for item_path in path.iterdir():
        if item_path.name == '.DS_Store':
            continue
        return False
    return True


def read_yaml(path: Path) -> Any:
    with path.open('rb') as file:
        return yaml.safe_load(file)
