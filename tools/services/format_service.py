import itertools
import shutil
from io import StringIO
from pathlib import Path

from pixel_font_knife import glyph_file_util, glyph_mapping_util

from tools import configs
from tools.configs import path_define
from tools.configs.font import FontConfig


def _is_empty_dir(path: Path) -> bool:
    for item_path in path.iterdir():
        if item_path.name == '.DS_Store':
            continue
        return False
    return True


def format_glyphs(font_config: FontConfig):
    for width_mode_dir_name in itertools.chain(['common'], configs.width_modes):
        width_mode_dir = path_define.glyphs_dir.joinpath(str(font_config.font_size), width_mode_dir_name)
        context = glyph_file_util.load_context(width_mode_dir)
        glyph_file_util.normalize_context(context, width_mode_dir, configs.language_flavors)

        for file_dir, _, _ in width_mode_dir.walk(top_down=False):
            if _is_empty_dir(file_dir):
                shutil.rmtree(file_dir)


def format_mapping(file_path: Path):
    mapping = glyph_mapping_util.load_mapping(file_path)

    only_default = True
    for source_group in mapping.values():
        if len(source_group) > 1 or None not in source_group:
            only_default = False
            break

    if only_default:
        buffer = StringIO()
        for code_point, source_group in sorted(mapping.items()):
            c = chr(code_point)
            if not c.isprintable():
                c = f'0x{code_point:04X}'
            source_code_point = source_group[None].code_point
            source_c = chr(source_code_point)
            if not source_c.isprintable():
                source_c = f'0x{source_code_point:04X}'
            buffer.write('\n')
            buffer.write(f'# {c} <- {source_c}\n')
            buffer.write(f'0x{code_point:04X}:\n')
            buffer.write(f'  ~: 0x{source_code_point:04X}\n')
        file_path.write_text(buffer.getvalue(), 'utf-8')
    else:
        glyph_mapping_util.save_mapping(mapping, file_path, configs.language_flavors)
