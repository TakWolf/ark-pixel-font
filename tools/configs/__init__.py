from pixel_font_knife import glyph_mapping_util
from pixel_font_knife.kerning_util import KerningConfig

from tools.configs import path_define, options
from tools.configs.font import FontConfig

VERSION = '2026.09.01'

FONT_CONFIGS = {font_size: FontConfig.load(font_size) for font_size in options.FONT_SIZES}

MAPPINGS = [
    glyph_mapping_util.load_mapping(path_define.MAPPINGS_DIR.joinpath('0080-00FF Latin-1 Supplement.yaml')),
    glyph_mapping_util.load_mapping(path_define.MAPPINGS_DIR.joinpath('2E80-2EFF CJK Radicals Supplement.yaml')),
    glyph_mapping_util.load_mapping(path_define.MAPPINGS_DIR.joinpath('2F00-2FDF Kangxi Radicals.yaml')),
]

KERNING_CONFIG = KerningConfig.load(path_define.KERNINGS_DIR.joinpath('default.yaml'))

LOCALE_TO_LANGUAGE_FLAVOR = {
    'en': 'latin',
    'zh-cn': 'zh_cn',
    'zh-hk': 'zh_hk',
    'zh-tw': 'zh_tw',
    'zh-tr': 'zh_tr',
    'ja': 'ja',
    'ko': 'ko',
}
