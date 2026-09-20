from collections.abc import Callable

import pytest
import unicodedata2
import unidata_blocks
from pixel_font_knife.cmap.context import CmapContext

from tools.configs import FontConfig, options
from tools.configs.options import FontSize, GlyphScope


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
@pytest.mark.parametrize('glyph_scope', options.GLYPH_SCOPES)
def test_default_flavor(
        load_cmap_context: Callable[[FontSize, GlyphScope], CmapContext],
        font_size: FontSize,
        glyph_scope: GlyphScope,
) -> None:
    context = load_cmap_context(font_size, glyph_scope)

    for code_point, glyph_variants in sorted(context.items()):
        if glyph_scope == 'common' and code_point in (
                0x2E95,
        ):
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
            assert bitmap_string not in bitmap_strings, f"[{font_size}px] duplicate glyph bitmap:\n'{glyph_file.file_path}'\n'{bitmap_strings[bitmap_string].file_path}'"
            bitmap_strings[bitmap_string] = glyph_file


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
def test_top_right_padding(
        load_cmap_context: Callable[[FontSize, GlyphScope], CmapContext],
        font_size: FontSize,
) -> None:
    context = load_cmap_context(font_size, 'common')

    for code_point, glyph_variants in sorted(context.items()):
        block = unidata_blocks.get_block_by_code_point(code_point)

        for glyph_file in set(glyph_variants.values()):
            if block.name in ('Box Drawing', 'Block Elements'):
                continue

            if code_point in (
                    0x25D8, 0x25D9, 0x25DA, 0x25DB,
                    0x25E2, 0x25E3, 0x25E4, 0x25E5,
                    0x25F8, 0x25F9, 0x25FA, 0x25FF,
            ):
                continue

            if code_point not in (
                    0x3035,
            ):
                assert glyph_file.canvas.is_blank or glyph_file.canvas.trimmed_padding.top >= 1, f"[{font_size}px] glyph has no 1px top padding: '{glyph_file.file_path}'"

            if code_point not in (
                    0x2013,
                    0x2015,
                    0x3030,
            ):
                assert glyph_file.canvas.is_blank or glyph_file.canvas.trimmed_padding.right >= 1, f"[{font_size}px] glyph has no 1px right padding: '{glyph_file.file_path}'"


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
@pytest.mark.parametrize('glyph_scope', options.GLYPH_SCOPES)
def test_glyph_bitmap_dimensions(
        load_font_config: Callable[[FontSize], FontConfig],
        load_cmap_context: Callable[[FontSize, GlyphScope], CmapContext],
        font_size: FontSize,
        glyph_scope: GlyphScope,
) -> None:
    canvas_size = load_font_config(font_size).canvas_size
    context = load_cmap_context(font_size, glyph_scope)

    for code_point, glyph_variants in sorted(context.items()):
        east_asian_width = unicodedata2.east_asian_width(chr(code_point))

        for glyph_file in set(glyph_variants.values()):
            if glyph_scope == 'common' or glyph_scope == 'monospaced':
                assert glyph_file.canvas.height % font_size == 0, f"[{font_size}px] glyph bitmap dimensions error: '{glyph_file.file_path}'"

                match east_asian_width:
                    case 'H' | 'Na':  # Halfwidth or Narrow
                        assert glyph_file.canvas.width == font_size / 2, f"[{font_size}px] glyph bitmap dimensions error: '{glyph_file.file_path}'"
                    case 'F' | 'W':  # Fullwidth or Wide
                        assert glyph_file.canvas.width == font_size, f"[{font_size}px] glyph bitmap dimensions error: '{glyph_file.file_path}'"
                    case _:  # Ambiguous (A) or Neutral (N)
                        assert glyph_file.canvas.width % (font_size / 2) == 0, f"[{font_size}px] glyph bitmap dimensions error: '{glyph_file.file_path}'"

            if glyph_scope == 'proportional':
                assert glyph_file.canvas.height == canvas_size, f"[{font_size}px] glyph bitmap dimensions error: '{glyph_file.file_path}'"
