import datetime
import os
import tomllib
from typing import Final

import configs
from configs import path_define


class HorizontalHeader:
    def __init__(self, config_data: dict):
        self.ascent: int = config_data['ascent']
        self.descent: int = config_data['descent']
        self.x_height: int = config_data['x_height']
        self.cap_height: int = config_data['cap_height']

    @property
    def line_height(self) -> int:
        return self.ascent - self.descent


class FontConfig:
    VERSION: Final[str] = datetime.datetime.now(datetime.UTC).strftime("%Y.%m.%d")
    FAMILY_NAME: Final[str] = 'Ark Pixel'
    OUTPUTS_NAME: Final[str] = 'ark-pixel'
    MANUFACTURER: Final[str] = 'TakWolf'
    DESIGNER: Final[str] = 'TakWolf'
    DESCRIPTION: Final[str] = 'Open source Pan-CJK pixel font.'
    COPYRIGHT_INFO: Final[str] = "Copyright (c) 2021, TakWolf (https://takwolf.com), with Reserved Font Name 'Ark Pixel'."
    LICENSE_INFO: Final[str] = 'This Font Software is licensed under the SIL Open Font License, Version 1.1.'
    VENDOR_URL: Final[str] = 'https://ark-pixel-font.takwolf.com'
    DESIGNER_URL: Final[str] = 'https://takwolf.com'
    LICENSE_URL: Final[str] = 'https://scripts.sil.org/OFL'

    def __init__(self, size: int):
        config_file_path = os.path.join(path_define.glyphs_dir, str(size), 'config.toml')
        with open(config_file_path, 'rb') as file:
            config_data: dict = tomllib.load(file)['font']

        self.size: int = config_data['size']
        assert self.size == size, f'Font Config size not equals: expect {size} but actually {self.size}'

        self._width_mode_to_horizontal_header: dict[str, HorizontalHeader] = {}
        for width_mode in configs.width_modes:
            horizontal_header = HorizontalHeader(config_data[width_mode])
            assert (horizontal_header.line_height - self.size) % 2 == 0, f"Font Horizontal Header {self.size} {width_mode}: the difference between 'line_height' and 'size' must be a multiple of 2"
            self._width_mode_to_horizontal_header[width_mode] = horizontal_header

        self.demo_html_file_name = f'demo-{self.size}px.html'
        self.preview_image_file_name = f'preview-{self.size}px.png'

    @property
    def line_height(self) -> int:
        return self._width_mode_to_horizontal_header['proportional'].line_height

    def get_horizontal_header(self, width_mode: str) -> HorizontalHeader:
        return self._width_mode_to_horizontal_header[width_mode]

    def get_font_file_name(self, width_mode: str, language_flavor: str, font_format: str) -> str:
        return f'{FontConfig.OUTPUTS_NAME}-{self.size}px-{width_mode}-{language_flavor}.{font_format}'

    def get_font_collection_file_name(self, width_mode: str, font_format: str) -> str:
        return f'{FontConfig.OUTPUTS_NAME}-{self.size}px-{width_mode}.{font_format}'

    def get_info_file_name(self, width_mode: str) -> str:
        return f'font-info-{self.size}px-{width_mode}.md'

    def get_alphabet_txt_file_name(self, width_mode: str) -> str:
        return f'alphabet-{self.size}px-{width_mode}.txt'

    def get_release_zip_file_name(self, width_mode: str, font_format: str) -> str:
        return f'{FontConfig.OUTPUTS_NAME}-font-{self.size}px-{width_mode}-{font_format}-v{FontConfig.VERSION}.zip'

    def get_alphabet_html_file_name(self, width_mode: str) -> str:
        return f'alphabet-{self.size}px-{width_mode}.html'
