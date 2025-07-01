import itertools
from pathlib import Path

from pixel_font_knife import glyph_file_util, glyph_mapping_util

from tools.configs import path_define, options
from tools.configs.font import FontConfig


def format_glyphs(font_config: FontConfig):
    for width_mode_dir_name in itertools.chain(['common'], options.width_modes):
        width_mode_dir = path_define.glyphs_dir.joinpath(str(font_config.font_size), width_mode_dir_name)
        context = glyph_file_util.load_context(width_mode_dir)
        glyph_file_util.normalize_context(context, width_mode_dir, options.language_flavors)


def format_mapping(file_path: Path):
    mapping = glyph_mapping_util.load_mapping(file_path)
    glyph_mapping_util.save_mapping(mapping, file_path, options.language_flavors)
