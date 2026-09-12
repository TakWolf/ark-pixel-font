import itertools

from pixel_font_knife import glyph_file_util, glyph_mapping_util

from tools.configs import path_define, options
from tools.configs.options import FontSize


def format_glyphs(font_size: FontSize) -> None:
    for width_mode_dir_name in itertools.chain(['common'], options.WIDTH_MODES):
        width_mode_dir = path_define.GLYPHS_DIR.joinpath(str(font_size), width_mode_dir_name)
        context = glyph_file_util.load_context(width_mode_dir)
        glyph_file_util.normalize_context(context, width_mode_dir, options.LANGUAGE_FLAVORS)


def format_mappings() -> None:
    for file_path in path_define.MAPPINGS_DIR.iterdir():
        if file_path.suffix != '.yaml':
            continue
        mapping = glyph_mapping_util.load_mapping(file_path)
        glyph_mapping_util.save_mapping(mapping, file_path, options.LANGUAGE_FLAVORS)
