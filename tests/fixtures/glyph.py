import pytest

from tools.config.glyph.bitmap import GlyphBitmapRules


@pytest.fixture(scope='session')
def glyph_bitmap_rules() -> GlyphBitmapRules:
    return GlyphBitmapRules.load()
