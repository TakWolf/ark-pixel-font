from tools.configs import path_define, options
from tools.configs.font import FontConfig

version = '2025.08.11'

font_configs = {font_size: FontConfig.load(font_size) for font_size in options.font_sizes}

mapping_file_paths = [
    path_define.mappings_dir.joinpath('2700-27BF Dingbats.yml'),
    path_define.mappings_dir.joinpath('2E80-2EFF CJK Radicals Supplement.yml'),
    path_define.mappings_dir.joinpath('2F00-2FDF Kangxi Radicals.yml'),
]

locale_to_language_flavor = {
    'en': 'latin',
    'zh-cn': 'zh_cn',
    'zh-hk': 'zh_hk',
    'zh-tw': 'zh_tw',
    'zh-tr': 'zh_tr',
    'ja': 'ja',
    'ko': 'ko',
}
