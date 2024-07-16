import itertools
import shutil
from pathlib import Path

import unidata_blocks
from loguru import logger
from pixel_font_knife import glyph_file_util

from tools import configs
from tools.configs import path_define
from tools.configs.font import FontConfig


def _is_empty_dir(path: Path) -> bool:
    for item_path in path.iterdir():
        if item_path.name == '.DS_Store':
            continue
        return False
    return True


def format_glyph_files(font_config: FontConfig):
    for width_mode_dir_name in itertools.chain(['common'], configs.width_modes):
        width_mode_dir = path_define.glyphs_dir.joinpath(str(font_config.font_size), width_mode_dir_name)
        context = glyph_file_util.load_context(width_mode_dir)
        for code_point, flavor_group in context.items():
            if code_point == -1:
                code_name = 'notdef'
                file_dir = width_mode_dir
            else:
                code_name = f'{code_point:04X}'
                block = unidata_blocks.get_block_by_code_point(code_point)
                file_dir = width_mode_dir.joinpath(f'{block.code_start:04X}-{block.code_end:04X} {block.name}')
                if block.code_start == 0x4E00:
                    file_dir = file_dir.joinpath(f'{code_name[0:-2]}-')

            for glyph_file in set(flavor_group.values()):
                if len(glyph_file.flavors) > 0:
                    file_name = f'{code_name} {','.join(sorted(glyph_file.flavors, key=lambda x: configs.language_flavors.index(x)))}.png'
                else:
                    file_name = f'{code_name}.png'
                file_path = file_dir.joinpath(file_name)
                if glyph_file.file_path != file_path:
                    assert not file_path.exists(), f"[{font_config.font_size}px] duplicate glyph files: '{glyph_file.file_path}' -> '{file_path}'"
                    file_dir.mkdir(parents=True, exist_ok=True)
                    glyph_file.file_path.rename(file_path)
                    logger.info("Format glyph file path: '{}' -> '{}'", glyph_file.file_path, file_path)
                    glyph_file.file_path = file_path

                glyph_file.bitmap.save_png(glyph_file.file_path)

        for file_dir, _, _ in width_mode_dir.walk(top_down=False):
            if _is_empty_dir(file_dir):
                shutil.rmtree(file_dir)
