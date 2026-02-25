import itertools

import unicodedata2
import unidata_blocks
from pixel_font_knife import glyph_file_util

from tools import configs
from tools.configs import path_define, options
from tools.configs.options import FontSize


def check_glyphs(font_size: FontSize):
    canvas_size = configs.font_configs[font_size].canvas_size

    for width_mode_dir_name in itertools.chain(['common'], options.width_modes):
        context = glyph_file_util.load_context(path_define.glyphs_dir.joinpath(str(font_size), width_mode_dir_name))

        for code_point, flavor_group in sorted(context.items()):
            if code_point == -1:
                block = None
                east_asian_width = 'F'
            else:
                block = unidata_blocks.get_block_by_code_point(code_point)
                east_asian_width = unicodedata2.east_asian_width(chr(code_point))

            if code_point not in (
                    0x2E95,
            ):
                assert None in flavor_group, f'[{font_size}px] missing default flavor: {width_mode_dir_name} {code_point:04X}'

            bitmap_strings = {}
            for glyph_file in set(flavor_group.values()):
                bitmap_string = str(glyph_file.bitmap)
                assert bitmap_string not in bitmap_strings, f"[{font_size}px] duplicate glyph bitmaps:\n'{glyph_file.file_path}'\n'{bitmap_strings[bitmap_string].file_path}'"
                bitmap_strings[bitmap_string] = glyph_file

                if width_mode_dir_name == 'common':
                    if block is not None and block.name not in (
                            'Box Drawing',
                            'Block Elements',
                            'Halfwidth and Fullwidth Forms',
                    ) and code_point not in (
                            0x2013,
                            0x2015,
                            0x25EF,
                            0x3030,
                            0x3035,
                    ):
                        assert all(color == 0 for color in glyph_file.bitmap[0]), f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"
                        assert all(glyph_file.bitmap[i][-1] == 0 for i in range(0, len(glyph_file.bitmap))), f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"

                if width_mode_dir_name == 'common':
                    assert glyph_file.height % font_size == 0, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"

                if width_mode_dir_name == 'monospaced':
                    assert glyph_file.height == font_size, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"

                if width_mode_dir_name == 'proportional':
                    assert glyph_file.height == canvas_size, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"

                if width_mode_dir_name == 'common' or width_mode_dir_name == 'monospaced':
                    match east_asian_width:
                        case 'H' | 'Na':  # Halfwidth or Narrow
                            assert glyph_file.width == font_size / 2, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"
                        case 'F' | 'W':  # Fullwidth or Wide
                            assert glyph_file.width == font_size, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"
                        case _:  # Ambiguous (A) or Neutral (N)
                            assert glyph_file.width % (font_size / 2) == 0, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"
