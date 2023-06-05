import os
import tomllib

import configs
from configs import path_define


class FontAttrs:
    def __init__(self, config_data, size, line_height):
        self.box_origin_y = config_data['box_origin_y']
        self.ascent = self.box_origin_y + int((line_height - size) / 2)
        self.descent = self.ascent - line_height
        self.x_height = config_data['x_height']
        self.cap_height = config_data['cap_height']


class FontConfig:
    FAMILY_NAME = 'Ark Pixel'
    MANUFACTURER = 'TakWolf'
    DESIGNER = 'TakWolf'
    DESCRIPTION = 'Open source Pan-CJK pixel font.'
    COPYRIGHT_INFO = "Copyright (c) 2021, TakWolf (https://takwolf.com), with Reserved Font Name 'Ark Pixel'."
    LICENSE_INFO = 'This Font Software is licensed under the SIL Open Font License, Version 1.1.'
    VENDOR_URL = 'https://ark-pixel-font.takwolf.com'
    DESIGNER_URL = 'https://takwolf.com'
    LICENSE_URL = 'https://scripts.sil.org/OFL'

    def __init__(self, size, px_to_units=100):
        self.root_dir = os.path.join(path_define.glyphs_dir, str(size))

        config_file_path = os.path.join(path_define.glyphs_dir, str(size), 'config.toml')
        with open(config_file_path, 'rb') as file:
            config_data = tomllib.load(file)['font']

        self.size = config_data['size']
        assert self.size == size, f'Font config size not equals: expect {size} but actually {self.size}'
        self.line_height = config_data['line_height']
        assert (self.line_height - size) % 2 == 0, f"Font config {self.size}: the difference between 'line_height' and 'size' must be a multiple of 2"

        self._attrs_group = {
            'monospaced': FontAttrs(config_data['monospaced'], self.size, self.size),
            'proportional': FontAttrs(config_data['proportional'], self.size, self.line_height),
        }

        self.px_to_units = px_to_units

        self.demo_html_file_name = f'demo-{size}px.html'
        self.preview_image_file_name = f'preview-{size}px.png'

    def get_name_strings(self, width_mode, language_flavor):
        style_name = 'Regular'
        display_name = f'{FontConfig.FAMILY_NAME} {self.size}px {width_mode.capitalize()} {language_flavor}'
        unique_name = f'{FontConfig.FAMILY_NAME.replace(" ", "-")}-{self.size}px-{width_mode.capitalize()}-{language_flavor}-{style_name}'
        return {
            'copyright': FontConfig.COPYRIGHT_INFO,
            'familyName': display_name,
            'styleName': style_name,
            'uniqueFontIdentifier': f'{unique_name};{configs.version}',
            'fullName': display_name,
            'version': configs.version,
            'psName': unique_name,
            'designer': FontConfig.DESIGNER,
            'description': FontConfig.DESCRIPTION,
            'vendorURL': FontConfig.VENDOR_URL,
            'designerURL': FontConfig.DESIGNER_URL,
            'licenseDescription': FontConfig.LICENSE_INFO,
            'licenseInfoURL': FontConfig.LICENSE_URL,
        }

    def get_attrs(self, width_mode):
        return self._attrs_group[width_mode]

    def get_font_file_name(self, width_mode, language_flavor, font_format):
        return f'{FontConfig.FAMILY_NAME.lower().replace(" ", "-")}-{self.size}px-{width_mode}-{language_flavor}.{font_format}'

    def get_info_file_name(self, width_mode):
        return f'font-info-{self.size}px-{width_mode}.md'

    def get_alphabet_txt_file_name(self, width_mode):
        return f'alphabet-{self.size}px-{width_mode}.txt'

    def get_release_zip_file_name(self, width_mode, font_format):
        return f'{FontConfig.FAMILY_NAME.lower().replace(" ", "-")}-font-{self.size}px-{width_mode}-{font_format}-v{configs.version}.zip'

    def get_alphabet_html_file_name(self, width_mode):
        return f'alphabet-{self.size}px-{width_mode}.html'
