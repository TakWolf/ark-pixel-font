from tools.configs import path_define, options
from tools.configs.font import FontConfig

version = '2025.03.14'

font_configs = {font_size: FontConfig.load(font_size) for font_size in options.font_sizes}

mapping_file_paths = [
    path_define.mappings_dir.joinpath('2700-27BF Dingbats.yml'),
    path_define.mappings_dir.joinpath('2E80-2EFF CJK Radicals Supplement.yml'),
    path_define.mappings_dir.joinpath('2F00-2FDF Kangxi Radicals.yml'),
]
