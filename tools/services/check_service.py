import itertools
import unicodedata

import unidata_blocks
from pixel_font_knife import glyph_file_util, glyph_mapping_util
from pixel_font_knife.glyph_mapping_util import SourceFlavorGroup

from tools import configs
from tools.configs import path_define, options
from tools.configs.options import FontSize


def check_glyph_files(font_size: FontSize, mappings: list[dict[int, SourceFlavorGroup]]):
    canvas_size = configs.font_configs[font_size].canvas_size

    for width_mode_dir_name in itertools.chain(['common'], options.width_modes):
        context = glyph_file_util.load_context(path_define.glyphs_dir.joinpath(str(font_size), width_mode_dir_name))
        for mapping in mappings:
            glyph_mapping_util.apply_mapping(context, mapping)

        for code_point, flavor_group in sorted(context.items()):
            assert None in flavor_group, f'[{font_size}px] missing default flavor: {width_mode_dir_name} {code_point:04X}'

            if code_point == -1:
                block = None
                east_asian_width = 'F'
            else:
                block = unidata_blocks.get_block_by_code_point(code_point)
                east_asian_width = unicodedata.east_asian_width(chr(code_point))

            bitmap_strings = {}
            for glyph_file in set(flavor_group.values()):
                bitmap_string = str(glyph_file.bitmap)
                assert bitmap_string not in bitmap_strings, f"[{font_size}px] duplicate glyph bitmaps:\n'{glyph_file.file_path}'\n'{bitmap_strings[bitmap_string].file_path}'"
                bitmap_strings[bitmap_string] = glyph_file

                if width_mode_dir_name == 'common':
                    if block is not None:
                        if block.name not in (
                                'Box Drawing',
                                'Block Elements',
                                'Halfwidth and Fullwidth Forms',
                        ) and code_point not in (
                                0x2013,
                                0x2015,
                                0x25EF,
                                0x3030,
                        ):
                            assert all(color == 0 for color in glyph_file.bitmap[0]), f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"
                            assert all(glyph_file.bitmap[i][-1] == 0 for i in range(0, len(glyph_file.bitmap))), f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"

                if width_mode_dir_name == 'common' or width_mode_dir_name == 'monospaced':
                    assert glyph_file.height == font_size, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"

                    # H/Halfwidth or Na/Narrow
                    if east_asian_width == 'H' or east_asian_width == 'Na':
                        assert glyph_file.width == font_size / 2, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"
                    # F/Fullwidth or W/Wide
                    elif east_asian_width == 'F' or east_asian_width == 'W':
                        assert glyph_file.width == font_size, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"
                    # A/Ambiguous or N/Neutral
                    else:
                        assert glyph_file.width == font_size / 2 or glyph_file.width == font_size, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"

                if width_mode_dir_name == 'proportional':
                    assert glyph_file.height == canvas_size, f"[{font_size}px] glyph bitmap size error: '{glyph_file.file_path}'"
