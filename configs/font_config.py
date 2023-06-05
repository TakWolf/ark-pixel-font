import os
import time
import tomllib

from configs import path_define

display_name_prefix = 'Ark Pixel'
unique_name_prefix = 'Ark-Pixel'
output_name_prefix = 'ark-pixel'
style_name = 'Regular'
version = f'{time.strftime("%Y.%m.%d")}'
copyright_string = "Copyright (c) 2021, TakWolf (https://takwolf.com), with Reserved Font Name 'Ark Pixel'."
designer = 'TakWolf'
description = 'Open source Pan-CJK pixel font.'
vendor_url = 'https://ark-pixel-font.takwolf.com'
designer_url = 'https://takwolf.com'
license_description = 'This Font Software is licensed under the SIL Open Font License, Version 1.1.'
license_info_url = 'https://scripts.sil.org/OFL'


class FontAttrs:
    def __init__(self, config_data, size, line_height):
        self.box_origin_y = config_data['box_origin_y']
        self.ascent = self.box_origin_y + int((line_height - size) / 2)
        self.descent = self.ascent - line_height
        self.x_height = config_data['x_height']
        self.cap_height = config_data['cap_height']


class FontConfig:
    def __init__(self, size, px_to_units=100):
        self.root_dir = os.path.join(path_define.glyphs_dir, str(size))

        config_file_path = os.path.join(path_define.glyphs_dir, str(size), 'config.toml')
        with open(config_file_path, 'rb') as file:
            config_data = tomllib.load(file)['font']

        self.size = config_data['size']
        assert self.size == size, config_file_path
        self.line_height = config_data['line_height']
        assert (self.line_height - size) % 2 == 0, f'font_config {size}px with incorrect line_height_px {self.line_height}px'

        self._attrs_group = {
            'monospaced': FontAttrs(config_data['monospaced'], self.size, self.size),
            'proportional': FontAttrs(config_data['proportional'], self.size, self.line_height),
        }

        self.px_to_units = px_to_units

        self.demo_html_file_name = f'demo-{size}px.html'
        self.preview_image_file_name = f'preview-{size}px.png'

    def get_name_strings(self, width_mode, language_flavor):
        display_name = f'{display_name_prefix} {self.size}px {width_mode} {language_flavor}'
        unique_name = f'{unique_name_prefix}-{self.size}px-{width_mode}-{language_flavor}-{style_name}'
        return {
            'copyright': copyright_string,
            'familyName': display_name,
            'styleName': style_name,
            'uniqueFontIdentifier': f'{unique_name};{version}',
            'fullName': display_name,
            'version': version,
            'psName': unique_name,
            'designer': designer,
            'description': description,
            'vendorURL': vendor_url,
            'designerURL': designer_url,
            'licenseDescription': license_description,
            'licenseInfoURL': license_info_url,
        }

    def get_attrs(self, width_mode):
        return self._attrs_group[width_mode]

    def get_font_file_name(self, width_mode, language_flavor, font_format):
        return f'{output_name_prefix}-{self.size}px-{width_mode}-{language_flavor}.{font_format}'

    def get_info_file_name(self, width_mode):
        return f'font-info-{self.size}px-{width_mode}.md'

    def get_alphabet_txt_file_name(self, width_mode):
        return f'alphabet-{self.size}px-{width_mode}.txt'

    def get_release_zip_file_name(self, width_mode, font_format):
        return f'{output_name_prefix}-font-{self.size}px-{width_mode}-{font_format}-v{version}.zip'

    def get_alphabet_html_file_name(self, width_mode):
        return f'alphabet-{self.size}px-{width_mode}.html'
