from pixel_font_knife import glyph_mapping_util
from pixel_font_knife.kerning_util import KerningConfig

from tools.configs import path_define, options
from tools.configs.font import FontConfig

VERSION = '2026.09.01'

FONT_CONFIGS = {font_size: FontConfig.load(font_size) for font_size in options.FONT_SIZES}

MAPPINGS = [
    glyph_mapping_util.load_mapping(path_define.CONFIGS_MAPPINGS_DIR.joinpath('0080-00FF Latin-1 Supplement.yaml')),
    glyph_mapping_util.load_mapping(path_define.CONFIGS_MAPPINGS_DIR.joinpath('2E80-2EFF CJK Radicals Supplement.yaml')),
    glyph_mapping_util.load_mapping(path_define.CONFIGS_MAPPINGS_DIR.joinpath('2F00-2FDF Kangxi Radicals.yaml')),
]

KERNING_TEMPLATE_DEFAULT = KerningConfig.load(path_define.CONFIGS_KERNING_DIR.joinpath('default.yaml'))

LANGUAGE_FLAVOR_TO_FONT_NAME = {
    'latin': 'latin',
    'zh_hans': 'zh-Hans',
    'zh_hant': 'zh-Hant',
    'zh_hk': 'zh-HK',
    'zh_tw': 'zh-TW',
    'ja': 'ja',
    'ko': 'ko',
}

LANGUAGE_FLAVOR_TO_LOCALE = {
    'latin': 'en',
    'zh_hans': 'zh-Hans',
    'zh_hant': 'zh-Hant',
    'zh_hk': 'zh-Hant-HK',
    'zh_tw': 'zh-Hant-TW',
    'ja': 'ja',
    'ko': 'ko',
}
