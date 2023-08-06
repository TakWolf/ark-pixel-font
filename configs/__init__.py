import random

from configs.font_config import FontConfig
from configs.git_deploy_config import GitDeployConfig

build_random_key = random.random()

width_modes = [
    'monospaced',
    'proportional',
]

width_mode_dir_names = [
    'common',
    'monospaced',
    'proportional',
]

language_flavors = [
    'latin',
    'zh_cn',
    'zh_hk',
    'zh_tw',
    'zh_tr',
    'ja',
    'ko',
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

font_formats = ['otf', 'woff2', 'ttf', 'bdf']

font_collection_formats = ['otc', 'ttc']

font_configs = [FontConfig(size) for size in [10, 12, 16]]
font_size_to_config = {font_config.size: font_config for font_config in font_configs}

git_deploy_configs = [GitDeployConfig(
    url='git@github.com:TakWolf/ark-pixel-font.git',
    remote_name='github',
    branch_name='gh-pages',
)]
