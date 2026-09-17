import unicodedata2
import unidata_blocks
from pixel_font_knife import glyph_file_util, glyph_mapping_util

from tools import configs
from tools.configs import path_define, options
from tools.configs.options import FontSize


def check_glyphs(font_size: FontSize) -> None:
    canvas_size = configs.FONT_CONFIGS[font_size].canvas_size

    for glyph_scope in options.GLYPH_SCOPES:
        context = glyph_file_util.load_context(path_define.GLYPHS_DIR.joinpath(str(font_size), 'cmap', glyph_scope))

        for code_point, flavor_group in sorted(context.items()):
            block = unidata_blocks.get_block_by_code_point(code_point)
            east_asian_width = unicodedata2.east_asian_width(chr(code_point))

            if code_point not in (
                    0x2E95,
            ):
                assert None in flavor_group, f'[{font_size}px] missing default flavor: {glyph_scope} {code_point:04X}'

            for language_flavor, glyph_file in flavor_group.items():
                assert language_flavor is None or language_flavor in options.LANGUAGE_FLAVORS, f"[{font_size}px] unknown flavor: {language_flavor}\n'{glyph_file.file_path}'"

            bitmap_strings = {}
            for glyph_file in set(flavor_group.values()):
                bitmap_string = str(glyph_file.bitmap)
                assert bitmap_string not in bitmap_strings, f"[{font_size}px] duplicate glyph bitmaps:\n'{glyph_file.file_path}'\n'{bitmap_strings[bitmap_string].file_path}'"
                bitmap_strings[bitmap_string] = glyph_file

                if glyph_scope == 'common' and block is not None and block.name not in (
                        'Box Drawing',
                        'Block Elements',
                ) and code_point not in (
                        0x25D8, 0x25D9, 0x25DA, 0x25DB,
                        0x25E2, 0x25E3, 0x25E4, 0x25E5,
                        0x25F8, 0x25F9, 0x25FA, 0x25FF,
                ):
                    if code_point not in (
                            0x3035,
                    ):
                        assert all(pixel == 0 for pixel in glyph_file.bitmap[0]), f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"

                    if code_point not in (
                            0x2013,
                            0x2015,
                            0x3030,
                    ):
                        assert all(glyph_file.bitmap[i][-1] == 0 for i in range(0, len(glyph_file.bitmap))), f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"

                if glyph_scope == 'common' or glyph_scope == 'monospaced':
                    assert glyph_file.height % font_size == 0, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"

                    match east_asian_width:
                        case 'H' | 'Na':  # Halfwidth or Narrow
                            assert glyph_file.width == font_size / 2, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"
                        case 'F' | 'W':  # Fullwidth or Wide
                            assert glyph_file.width == font_size, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"
                        case _:  # Ambiguous (A) or Neutral (N)
                            assert glyph_file.width % (font_size / 2) == 0, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"

                if glyph_scope == 'proportional':
                    assert glyph_file.height == canvas_size, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"


def check_mappings() -> None:
    for file_path in path_define.CONFIGS_MAPPINGS_DIR.iterdir():
        if file_path.suffix != '.yaml':
            continue
        mapping = glyph_mapping_util.load_mapping(file_path)

        for code_point, flavor_group in sorted(mapping.items()):
            for language_flavor, source_glyph in flavor_group.items():
                assert language_flavor is None or language_flavor == '*' or language_flavor in options.LANGUAGE_FLAVORS, f"unknown target flavor: 0x{code_point:04X} {language_flavor}\n'{file_path}'"
                assert source_glyph.flavor is None or source_glyph.flavor in options.LANGUAGE_FLAVORS, f"unknown source flavor: 0x{code_point:04X} {language_flavor} -> 0x{source_glyph.code_point:04X} {source_glyph.flavor}\n'{file_path}'"
