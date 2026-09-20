from collections.abc import Callable
from functools import cache

import pytest
from pixel_font_knife.cmap.context import CmapContext

from tools.configs import path_define, options
from tools.configs.options import FontSize, GlyphScope


@pytest.fixture(scope='session')
def load_cmap_context() -> Callable[[FontSize, GlyphScope], CmapContext]:
    @cache
    def load(font_size: FontSize, glyph_scope: GlyphScope) -> CmapContext:
        return CmapContext.load(
            path_define.GLYPHS_DIR.joinpath(str(font_size), 'cmap', glyph_scope),
            allowed_flavors=options.LANGUAGE_FLAVORS,
        )

    return load
