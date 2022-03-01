import os.path

from jinja2 import Environment, FileSystemLoader

from configs import workspace_define
from configs.font_define import FontConfig
from utils import unicode_util

font_configs = [
    FontConfig(10, 9),
    FontConfig(12, 10),
    FontConfig(16, 13),
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

design_dirs = [workspace_define.design_dir]

unicode_blocks = unicode_util.load_blocks_db(os.path.join(workspace_define.unidata_dir, 'blocks.txt'))

template_env = Environment(loader=FileSystemLoader(workspace_define.templates_dir))
