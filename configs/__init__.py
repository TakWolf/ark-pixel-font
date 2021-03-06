import os

from jinja2 import Environment, FileSystemLoader

from configs import path_define
from configs.font_config import FontConfig
from configs.git_deploy_config import GitDeployConfig
from utils.unidata_util import UnidataDB

font_name = font_config.display_name_prefix
font_version = font_config.version

font_configs = [
    FontConfig(10, 9, 5, 7),
    FontConfig(12, 10, 6, 8),
    FontConfig(16, 13, 7, 10),
]
font_config_map = {font_config.px: font_config for font_config in font_configs}

language_specifics = [
    'latin',  # 拉丁语
    'zh_cn',  # 中文-中国大陆
    'zh_hk',  # 中文-香港特别行政区
    'zh_tw',  # 中文-台湾地区
    'zh_tr',  # 中文-传统印刷
    'ja',     # 日语
    'ko',     # 朝鲜语
]

locale_map = {
    'en': 'latin',
    'zh-cn': 'zh_cn',
    'zh-hk': 'zh_hk',
    'zh-tw': 'zh_tw',
    'zh-tr': 'zh_tr',
    'ja': 'ja',
    'ko': 'ko',
}

font_formats = ['otf', 'woff2', 'ttf']

unidata_db = UnidataDB(os.path.join(path_define.unidata_dir, 'Blocks.txt'))

template_env = Environment(loader=FileSystemLoader(path_define.templates_dir))

git_deploy_configs = [GitDeployConfig(
    'git@github.com:TakWolf/ark-pixel-font.git',
    'github',
    'gh-pages',
)]
