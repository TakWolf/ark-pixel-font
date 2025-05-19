from pixel_font_knife import glyph_mapping_util
from pixel_font_knife.kerning_util import KerningConfig

from tools.configs import path_define, options
from tools.configs.font import FontConfig

version = '2026.07.20'

font_configs = {font_size: FontConfig.load(font_size) for font_size in options.font_sizes}

mappings = [
    glyph_mapping_util.load_mapping(path_define.mappings_dir.joinpath('2E80-2EFF CJK Radicals Supplement.yaml')),
    glyph_mapping_util.load_mapping(path_define.mappings_dir.joinpath('2F00-2FDF Kangxi Radicals.yaml')),
    glyph_mapping_util.load_mapping(path_define.mappings_dir.joinpath('F900-FAFF CJK Compatibility Ideographs.yaml')),
]

kerning_config = KerningConfig.load(path_define.kernings_dir.joinpath('default.yaml'))

locale_to_language_flavor = {
    'en': 'latin',
    'zh-cn': 'zh_cn',
    'zh-hk': 'zh_hk',
    'zh-tw': 'zh_tw',
    'zh-tr': 'zh_tr',
    'ja': 'ja',
    'ko': 'ko',
}
