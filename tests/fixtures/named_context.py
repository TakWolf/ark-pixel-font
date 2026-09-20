from collections.abc import Callable
from functools import cache

import pytest
from pixel_font_knife.named.context import NamedContext

from tools.configs import path_define, options
from tools.configs.options import FontSize, GlyphScope


@pytest.fixture(scope='session')
def load_named_context() -> Callable[[FontSize, GlyphScope], NamedContext]:
    @cache
    def load(font_size: FontSize, glyph_scope: GlyphScope) -> NamedContext:
        return NamedContext.load(
            path_define.GLYPHS_DIR.joinpath(str(font_size), 'named', glyph_scope),
            allowed_flavors=options.LANGUAGE_FLAVORS,
        )

    return load
