from collections.abc import Callable

import pytest
import unicodedata2
import unidata_blocks
from pixel_font_knife.cmap.context import CmapContext

from tools.config import options
from tools.config.font import FontConfig
from tools.config.glyph.bitmap import GlyphBitmapRules
from tools.config.options import FontSize, GlyphScope


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
@pytest.mark.parametrize('glyph_scope', options.GLYPH_SCOPES)
def test_default_flavor(
        load_cmap_context: Callable[[FontSize, GlyphScope], CmapContext],
        glyph_bitmap_rules: GlyphBitmapRules,
        font_size: FontSize,
        glyph_scope: GlyphScope,
) -> None:
    context = load_cmap_context(font_size, glyph_scope)
    flavor_rules = glyph_bitmap_rules.cmap_rules.flavor_rules

    for code_point, glyph_variants in sorted(context.items()):
        if code_point in flavor_rules.allow_missing_default.get(glyph_scope, ()):
            continue

        assert None in glyph_variants, f'[{font_size}px] missing default flavor: {glyph_scope} {code_point:04X}'


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
@pytest.mark.parametrize('glyph_scope', options.GLYPH_SCOPES)
def test_duplicate_glyph_bitmap(
        load_cmap_context: Callable[[FontSize, GlyphScope], CmapContext],
        font_size: FontSize,
        glyph_scope: GlyphScope,
) -> None:
    context = load_cmap_context(font_size, glyph_scope)

    for code_point, glyph_variants in sorted(context.items()):
        bitmap_strings = {}
        for glyph_file in set(glyph_variants.values()):
            bitmap_string = str(glyph_file.canvas.bitmap)
            assert bitmap_string not in bitmap_strings, f'[{font_size}px] duplicate glyph bitmap:\n{str(glyph_file.file_path)!r}\n{str(bitmap_strings[bitmap_string].file_path)!r}'
            bitmap_strings[bitmap_string] = glyph_file


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
def test_top_and_right_padding(
        load_cmap_context: Callable[[FontSize, GlyphScope], CmapContext],
        glyph_bitmap_rules: GlyphBitmapRules,
        font_size: FontSize,
) -> None:
    context = load_cmap_context(font_size, 'common')
    padding_rules = glyph_bitmap_rules.cmap_rules.padding_rules

    for code_point, glyph_variants in sorted(context.items()):
        block = unidata_blocks.get_block_by_code_point(code_point)

        for glyph_file in set(glyph_variants.values()):
            if (
                    block.name not in padding_rules.allow_no_top_blocks and
                    code_point not in padding_rules.allow_no_top_code_points
            ):
                assert glyph_file.canvas.is_blank or glyph_file.canvas.trimmed_padding.top >= 1, f'[{font_size}px] glyph has no 1px top padding: {str(glyph_file.file_path)!r}'

            if (
                    block.name not in padding_rules.allow_no_right_blocks and
                    code_point not in padding_rules.allow_no_right_code_points
            ):
                assert glyph_file.canvas.is_blank or glyph_file.canvas.trimmed_padding.right >= 1, f'[{font_size}px] glyph has no 1px right padding: {str(glyph_file.file_path)!r}'


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
@pytest.mark.parametrize('glyph_scope', options.GLYPH_SCOPES)
def test_glyph_bitmap_dimensions(
        load_font_config: Callable[[FontSize], FontConfig],
        load_cmap_context: Callable[[FontSize, GlyphScope], CmapContext],
        font_size: FontSize,
        glyph_scope: GlyphScope,
) -> None:
    canvas_height = load_font_config(font_size).canvas_height
    context = load_cmap_context(font_size, glyph_scope)

    for code_point, glyph_variants in sorted(context.items()):
        east_asian_width = unicodedata2.east_asian_width(chr(code_point))

        for glyph_file in set(glyph_variants.values()):
            if glyph_scope == 'common' or glyph_scope == 'monospaced':
                assert glyph_file.canvas.height % font_size == 0, f'[{font_size}px] glyph bitmap dimensions error: {str(glyph_file.file_path)!r}'

                match east_asian_width:
                    case 'H' | 'Na':  # Halfwidth or Narrow
                        assert glyph_file.canvas.width == font_size / 2, f'[{font_size}px] glyph bitmap dimensions error: {str(glyph_file.file_path)!r}'
                    case 'F' | 'W':  # Fullwidth or Wide
                        assert glyph_file.canvas.width == font_size, f'[{font_size}px] glyph bitmap dimensions error: {str(glyph_file.file_path)!r}'
                    case _:  # Ambiguous (A) or Neutral (N)
                        assert glyph_file.canvas.width % (font_size / 2) == 0, f'[{font_size}px] glyph bitmap dimensions error: {str(glyph_file.file_path)!r}'

            if glyph_scope == 'proportional':
                assert glyph_file.canvas.height == canvas_height, f'[{font_size}px] glyph bitmap dimensions error: {str(glyph_file.file_path)!r}'
