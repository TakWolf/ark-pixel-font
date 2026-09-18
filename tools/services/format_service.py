import sys

from pixel_font_knife.cmap.context import CmapContext
from pixel_font_knife.cmap.mapping.mapping import CmapMapping
from pixel_font_knife.named.context import NamedContext
from pixel_font_knife.utils import fs_util

from tools.configs import path_define, options
from tools.configs.options import FontSize


def normalize_cmap_glyphs(font_size: FontSize) -> None:
    for glyph_scope in options.GLYPH_SCOPES:
        glyph_scope_dir = path_define.GLYPHS_DIR.joinpath(str(font_size), 'cmap', glyph_scope)
        context = CmapContext.load(glyph_scope_dir, allowed_flavors=options.LANGUAGE_FLAVORS)
        context.normalize(glyph_scope_dir, flavor_order=options.LANGUAGE_FLAVORS)


def normalize_named_glyphs(font_size: FontSize) -> None:
    for glyph_scope in options.GLYPH_SCOPES:
        glyph_scope_dir = path_define.GLYPHS_DIR.joinpath(str(font_size), 'named', glyph_scope)
        context = NamedContext.load(glyph_scope_dir, allowed_flavors=options.LANGUAGE_FLAVORS)
        context.normalize(flavor_order=options.LANGUAGE_FLAVORS)


def format_glyphs() -> None:
    if sys.platform != 'win32':
        fs_util.format_glyph_files(path_define.GLYPHS_DIR)


def format_mappings() -> None:
    for file_path in path_define.CONFIGS_MAPPINGS_DIR.rglob('*.yaml'):
        if not file_path.is_file():
            continue

        mapping = CmapMapping.load_yaml(file_path, allowed_flavors=options.LANGUAGE_FLAVORS)
        mapping.save_yaml(file_path, flavor_order=options.LANGUAGE_FLAVORS)
