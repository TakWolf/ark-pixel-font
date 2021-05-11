import os
import time

from configs import workspace_define
from utils import unicode_util

unicode_blocks = unicode_util.load_blocks_db(workspace_define.unicode_blocks_db_path)
unicode_block_name_translations = unicode_util.load_block_name_translations(workspace_define.unicode_block_name_translations_file_path)

version_name = '0.0.1'
version_time = time.strftime("%Y%m%d")
version = f'{version_name}-{version_time}'
copyright_string = "Copyright (c) 2021, TakWolf (https://ark-pixel-font.takwolf.com), with Reserved Font Name 'Ark Pixel'."
designer = 'TakWolf'
description = 'Ark pixel font.'
vendor_url = 'https://ark-pixel-font.takwolf.com'
designer_url = 'https://takwolf.com'
license_description = 'This Font Software is licensed under the SIL Open Font License, Version 1.1.'
license_info_url = 'https://scripts.sil.org/OFL'

language_flavors = [
    'sc',     # 简体中文
    'tc_hk',  # 繁体中文-中国香港
    'tc_tw',  # 繁体中文-中国台湾
    'jp',     # 日文
    'ko'      # 韩文
]


class FontConfig:
    def __init__(self, px, ascent_px, descent_px, is_include_draft):
        # 字体信息
        self.display_name = f'Ark Pixel {px}px'
        self.unique_name = f'ArkPixel-{px}px'
        self.style_name = 'Regular'
        # 字体参数
        self.px = px
        self.ascent_px = ascent_px
        self.descent_px = descent_px
        self.em_dot_size = 100
        self.units_per_em = px * self.em_dot_size
        self.ascent = ascent_px * self.em_dot_size
        self.descent = descent_px * self.em_dot_size
        # 相关路径
        self.output_basic_name = f'ark-pixel-{px}px'
        self.release_basic_name = f'ark-pixel-font-{px}px'
        self.design_dir = os.path.join(workspace_define.design_dir, str(px))
        self.zip_file_name = f'{self.release_basic_name}-all-v{version}.zip'
        self.zip_file_release_path = os.path.join(workspace_define.release_dir, self.zip_file_name)
        # 构建参数
        self.is_include_draft = is_include_draft
        # 语言变种相关配置
        self.language_flavor_configs = {}
        for language_flavor in language_flavors:
            self.language_flavor_configs[language_flavor] = FontLanguageFlavorConfig(self, language_flavor)


class FontLanguageFlavorConfig:
    def __init__(self, font_config, language_flavor):
        self.language_flavor = language_flavor
        # 字体信息
        self.display_name = f'{font_config.display_name} {language_flavor.upper()}'
        self.unique_name = f'{font_config.unique_name}-{language_flavor.upper()}'
        # 相关路径
        self.otf_file_name = f'{font_config.output_basic_name}-{language_flavor}.otf'
        self.otf_file_output_path = os.path.join(workspace_define.outputs_dir, self.otf_file_name)
        self.ttf_file_name = f'{font_config.output_basic_name}-{language_flavor}.ttf'
        self.ttf_file_output_path = os.path.join(workspace_define.outputs_dir, self.ttf_file_name)
        self.zip_file_name = f'{font_config.release_basic_name}-{language_flavor}-v{version}.zip'
        self.zip_file_release_path = os.path.join(workspace_define.release_dir, self.zip_file_name)


font_configs = [
    FontConfig(12, 10, -2, False),
    FontConfig(16, 13, -3, False)
]
