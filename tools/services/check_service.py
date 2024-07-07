import itertools
import unicodedata
from io import BytesIO

import unidata_blocks
from pixel_font_knife import glyph_file_util

from tools import configs
from tools.configs import path_define
from tools.configs.font import FontConfig


def check_font_config(font_config: FontConfig):
    for width_mode, layout_param in font_config.layout_params.items():
        if width_mode == 'monospaced':
            assert layout_param.line_height == font_config.font_size, f"[{font_config.font_size}px] Font config illegal 'monospaced.line_height': {layout_param.line_height}"
        else:
            assert width_mode == 'proportional', f"[{font_config.font_size}px] Font config illegal 'width_mode': {width_mode}"
            assert (layout_param.line_height - font_config.font_size) % 2 == 0, f"[{font_config.font_size}px] Font config illegal 'proportional.line_height': {layout_param.line_height}"


def check_glyph_files(font_config: FontConfig):
    for width_mode_dir_name in itertools.chain(['common'], configs.width_modes):
        width_mode_dir = path_define.glyphs_dir.joinpath(str(font_config.font_size), width_mode_dir_name)
        context = glyph_file_util.load_context(width_mode_dir)
        for code_point, flavor_group in context.items():
            assert '' in flavor_group, f'[{font_config.font_size}px] Missing default flavor: {width_mode_dir_name} {code_point:04X}'

            if code_point == -1:
                code_name = 'notdef'
                block = None
                file_dir = width_mode_dir
                east_asian_width = 'F'
            else:
                code_name = f'{code_point:04X}'
                block = unidata_blocks.get_block_by_code_point(code_point)
                file_dir = width_mode_dir.joinpath(f'{block.code_start:04X}-{block.code_end:04X} {block.name}')
                if block.code_start == 0x4E00:
                    file_dir = file_dir.joinpath(f'{code_name[0:-2]}-')
                east_asian_width = unicodedata.east_asian_width(chr(code_point))

            for glyph_file in set(flavor_group.values()):
                if len(glyph_file.flavors) > 0:
                    file_name = f'{code_name} {','.join(sorted(glyph_file.flavors, key=lambda x: configs.language_flavors.index(x)))}.png'
                else:
                    file_name = f'{code_name}.png'
                file_path = file_dir.joinpath(file_name)
                assert glyph_file.file_path == file_path, f"[{font_config.font_size}px] Glyph file path is not standardized: '{glyph_file.file_path}' -> '{file_path}'"

                if width_mode_dir_name == 'common' or width_mode_dir_name == 'monospaced':
                    assert glyph_file.height == font_config.font_size, f"[{font_config.font_size}px] Glyph data error: '{glyph_file.file_path}'"

                    # H/Halfwidth or Na/Narrow
                    if east_asian_width == 'H' or east_asian_width == 'Na':
                        assert glyph_file.width == font_config.font_size / 2, f"[{font_config.font_size}px] Glyph data error: '{glyph_file.file_path}'"
                    # F/Fullwidth or W/Wide
                    elif east_asian_width == 'F' or east_asian_width == 'W':
                        assert glyph_file.width == font_config.font_size, f"[{font_config.font_size}px] Glyph data error: '{glyph_file.file_path}'"
                    # A/Ambiguous or N/Neutral
                    else:
                        assert glyph_file.width == font_config.font_size / 2 or glyph_file.width == font_config.font_size, f"[{font_config.font_size}px] Glyph data error: '{glyph_file.file_path}'"

                    if block is not None:
                        if 'CJK Unified Ideographs' in block.name:
                            assert all(alpha == 0 for alpha in glyph_file.bitmap[0]), f"[{font_config.font_size}px] Glyph data error: '{glyph_file.file_path}'"
                            assert all(glyph_file.bitmap[i][-1] == 0 for i in range(0, len(glyph_file.bitmap))), f"[{font_config.font_size}px] Glyph data error: '{glyph_file.file_path}'"

                if width_mode_dir_name == 'proportional':
                    assert glyph_file.height == font_config.line_height, f"[{font_config.font_size}px] Glyph data error: '{glyph_file.file_path}'"

                glyph_bytes = BytesIO()
                glyph_file.bitmap.dump_png(glyph_bytes)
                assert glyph_file.file_path.read_bytes() == glyph_bytes.getvalue(), f"[{font_config.font_size}px] Glyph file data is not standardized: '{glyph_file.file_path}'"
