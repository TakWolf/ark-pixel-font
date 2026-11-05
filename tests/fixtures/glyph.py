import pytest

from tools.config.glyph.bitmap import BitmapGlobalRules


@pytest.fixture(scope='session')
def bitmap_global_rules() -> BitmapGlobalRules:
    return BitmapGlobalRules.load()
