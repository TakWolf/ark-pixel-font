import datetime
import os
from typing import Final

from scripts import configs
from scripts.configs import path_define
from scripts.utils import fs_util


class LayoutParam:
    @staticmethod
    def from_data(data: dict[str, int]) -> 'LayoutParam':
        return LayoutParam(data['ascent'], data['descent'], data['x_height'], data['cap_height'])

    def __init__(self, ascent: int, descent: int, x_height: int, cap_height: int):
        self.ascent = ascent
        self.descent = descent
        self.x_height = x_height
        self.cap_height = cap_height

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
    LICENSE_URL: Final[str] = 'https://openfontlicense.org'

    @staticmethod
    def load_all() -> dict[int, 'FontConfig']:
        return {font_size: FontConfig.load(font_size) for font_size in configs.font_sizes}

    @staticmethod
    def load(size: int) -> 'FontConfig':
        config_file_path = os.path.join(path_define.glyphs_dir, str(size), 'config.toml')
        config_data: dict = fs_util.read_toml(config_file_path)['font']
        assert size == config_data['size'], f"Config 'size' error: '{config_file_path}'"

        layout_params = {}
        for width_mode in configs.width_modes:
            layout_param = LayoutParam.from_data(config_data[width_mode])
            if width_mode == 'monospaced':
                assert layout_param.line_height == size, f"Config 'monospaced.line_height' error: '{config_file_path}'"
            else:
                assert (layout_param.line_height - size) % 2 == 0, f"Config 'proportional.line_height' error: '{config_file_path}'"
            layout_params[width_mode] = layout_param

        return FontConfig(size, layout_params)

    def __init__(self, size: int, layout_params: dict[str, LayoutParam]):
        self.size = size
        self.layout_params = layout_params

        self.demo_html_file_name = f'demo-{size}px.html'
        self.preview_image_file_name = f'preview-{size}px.png'

    @property
    def line_height(self) -> int:
        return self.layout_params['proportional'].line_height

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
