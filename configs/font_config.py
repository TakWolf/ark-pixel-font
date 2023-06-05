import os
import tomllib
from typing import Final

import configs
from configs import path_define


class FontAttrs:
    def __init__(self, config_data: dict, size: int, line_height: int):
        self.box_origin_y: int = config_data['box_origin_y']
        self.ascent: int = self.box_origin_y + int((line_height - size) / 2)
        self.descent: int = self.ascent - line_height
        self.x_height: int = config_data['x_height']
        self.cap_height: int = config_data['cap_height']


class FontConfig:
    FAMILY_NAME: Final[str] = 'Ark Pixel'
    MANUFACTURER: Final[str] = 'TakWolf'
    DESIGNER: Final[str] = 'TakWolf'
    DESCRIPTION: Final[str] = 'Open source Pan-CJK pixel font.'
    COPYRIGHT_INFO: Final[str] = "Copyright (c) 2021, TakWolf (https://takwolf.com), with Reserved Font Name 'Ark Pixel'."
    LICENSE_INFO: Final[str] = 'This Font Software is licensed under the SIL Open Font License, Version 1.1.'
    VENDOR_URL: Final[str] = 'https://ark-pixel-font.takwolf.com'
    DESIGNER_URL: Final[str] = 'https://takwolf.com'
    LICENSE_URL: Final[str] = 'https://scripts.sil.org/OFL'

    def __init__(self, size: int):
        self.root_dir = os.path.join(path_define.glyphs_dir, str(size))

        config_file_path = os.path.join(self.root_dir, 'config.toml')
        with open(config_file_path, 'rb') as file:
            config_data: dict = tomllib.load(file)['font']

        self.size: int = config_data['size']
        assert self.size == size, f'Font config size not equals: expect {size} but actually {self.size}'
        self.line_height: int = config_data['line_height']
        assert (self.line_height - self.size) % 2 == 0, f"Font config {self.size}: the difference between 'line_height' and 'size' must be a multiple of 2"

        self._attrs_group = {
            'monospaced': FontAttrs(config_data['monospaced'], self.size, self.size),
            'proportional': FontAttrs(config_data['proportional'], self.size, self.line_height),
        }

        self.demo_html_file_name = f'demo-{self.size}px.html'
        self.preview_image_file_name = f'preview-{self.size}px.png'

    def get_attrs(self, width_mode: str) -> FontAttrs:
        return self._attrs_group[width_mode]

    def get_font_file_name(self, width_mode: str, language_flavor: str, font_format: str) -> str:
        return f'{FontConfig.FAMILY_NAME.lower().replace(" ", "-")}-{self.size}px-{width_mode}-{language_flavor}.{font_format}'

    def get_info_file_name(self, width_mode: str) -> str:
        return f'font-info-{self.size}px-{width_mode}.md'

    def get_alphabet_txt_file_name(self, width_mode: str) -> str:
        return f'alphabet-{self.size}px-{width_mode}.txt'

    def get_release_zip_file_name(self, width_mode: str, font_format: str) -> str:
        return f'{FontConfig.FAMILY_NAME.lower().replace(" ", "-")}-font-{self.size}px-{width_mode}-{font_format}-v{configs.version}.zip'

    def get_alphabet_html_file_name(self, width_mode: str) -> str:
        return f'alphabet-{self.size}px-{width_mode}.html'
