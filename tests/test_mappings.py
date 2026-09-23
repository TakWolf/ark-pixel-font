from pathlib import Path

import pytest
from pixel_font_knife.cmap.mapping.mapping import CmapMapping

from tools.config import path_define, options


@pytest.mark.parametrize(
    'file_path',
    sorted(path_define.CONFIGS_MAPPINGS_DIR.rglob('*.yaml')),
    ids=lambda file_path: str(file_path.relative_to(path_define.CONFIGS_MAPPINGS_DIR).with_suffix(''))
)
def test_mappings(file_path: Path) -> None:
    CmapMapping.load_yaml(file_path, allowed_flavors=options.LANGUAGE_FLAVORS)
