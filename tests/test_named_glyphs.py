from collections.abc import Callable

import pytest
from pixel_font_knife.named.context import NamedContext

from tools.config import options
from tools.config.font import FontConfig
from tools.config.options import FontSize, GlyphScope


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
@pytest.mark.parametrize('glyph_scope', options.GLYPH_SCOPES)
def test_default_flavor(
        load_named_context: Callable[[FontSize, GlyphScope], NamedContext],
        font_size: FontSize,
        glyph_scope: GlyphScope,
) -> None:
    context = load_named_context(font_size, glyph_scope)

    for name_key, glyph_variants in sorted(context.items()):
        assert None in glyph_variants, f'[{font_size}px] missing default flavor: {glyph_scope} {name_key}'


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
@pytest.mark.parametrize('glyph_scope', options.GLYPH_SCOPES)
def test_duplicate_glyph_bitmap(
        load_named_context: Callable[[FontSize, GlyphScope], NamedContext],
        font_size: FontSize,
        glyph_scope: GlyphScope,
) -> None:
    context = load_named_context(font_size, glyph_scope)

    for name_key, glyph_variants in sorted(context.items()):
        bitmap_strings = {}
        for glyph_file in set(glyph_variants.values()):
            bitmap_string = str(glyph_file.canvas.bitmap)
            assert bitmap_string not in bitmap_strings, f'[{font_size}px] duplicate glyph bitmap:\n{str(glyph_file.file_path)!r}\n{str(bitmap_strings[bitmap_string].file_path)!r}'
            bitmap_strings[bitmap_string] = glyph_file


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
def test_top_right_padding(
        load_named_context: Callable[[FontSize, GlyphScope], NamedContext],
        font_size: FontSize,
) -> None:
    context = load_named_context(font_size, 'common')

    for name_key, glyph_variants in sorted(context.items()):
        for glyph_file in set(glyph_variants.values()):
            assert glyph_file.canvas.is_blank or glyph_file.canvas.trimmed_padding.top >= 1, f'[{font_size}px] glyph has no 1px top padding: {str(glyph_file.file_path)!r}'
            assert glyph_file.canvas.is_blank or glyph_file.canvas.trimmed_padding.right >= 1, f'[{font_size}px] glyph has no 1px right padding: {str(glyph_file.file_path)!r}'


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
@pytest.mark.parametrize('glyph_scope', options.GLYPH_SCOPES)
def test_glyph_bitmap_dimensions(
        load_font_config: Callable[[FontSize], FontConfig],
        load_named_context: Callable[[FontSize, GlyphScope], NamedContext],
        font_size: FontSize,
        glyph_scope: GlyphScope,
) -> None:
    canvas_height = load_font_config(font_size).canvas_height
    context = load_named_context(font_size, glyph_scope)

    for name_key, glyph_variants in sorted(context.items()):
        for glyph_file in set(glyph_variants.values()):
            if glyph_scope == 'common' or glyph_scope == 'monospaced':
                assert glyph_file.canvas.height % font_size == 0, f'[{font_size}px] glyph bitmap dimensions error: {str(glyph_file.file_path)!r}'
                assert glyph_file.canvas.width % (font_size / 2) == 0, f'[{font_size}px] glyph bitmap dimensions error: {str(glyph_file.file_path)!r}'

            if glyph_scope == 'proportional':
                assert glyph_file.canvas.height == canvas_height, f'[{font_size}px] glyph bitmap dimensions error: {str(glyph_file.file_path)!r}'
