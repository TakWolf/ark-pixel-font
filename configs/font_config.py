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
    def __init__(self, config_data):
        self.box_origin_y_px = config_data['box_origin_y_px']
        self.x_height_px = config_data['x_height_px']
        self.cap_height_px = config_data['cap_height_px']


class VerticalMetrics:
    def __init__(self, ascent, descent, x_height, cap_height):
        self.ascent = ascent
        self.descent = descent
        self.x_height = x_height
        self.cap_height = cap_height


class FontConfig:
    def __init__(self, px, px_units=100):
        config_file_path = os.path.join(path_define.glyphs_dir, str(px), 'config.toml')
        with open(config_file_path, 'rb') as config_file:
            config_data = tomllib.load(config_file)['font']
        assert px == config_data['px'], config_file_path

        self.px = px
        self.line_height_px = config_data['line_height_px']
        assert (self.line_height_px - px) % 2 == 0, f'font_config {px}px with incorrect line_height_px {self.line_height_px}px'
        self.monospaced_attrs = FontAttrs(config_data['monospaced'])
        self.proportional_attrs = FontAttrs(config_data['proportional'])
        self.px_units = px_units

        self.demo_html_file_name = f'demo-{px}px.html'
        self.preview_image_file_name = f'preview-{px}px.png'

    def get_name_strings(self, width_mode, language_flavor):
        display_name = f'{display_name_prefix} {self.px}px {width_mode} {language_flavor}'
        unique_name = f'{unique_name_prefix}-{self.px}px-{width_mode}-{language_flavor}-{style_name}'
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

    def get_units_per_em(self):
        return self.px * self.px_units

    def get_box_origin_y(self, width_mode):
        if width_mode == 'monospaced':
            attrs = self.monospaced_attrs
        else:  # proportional
            attrs = self.proportional_attrs
        return attrs.box_origin_y_px * self.px_units

    def get_vertical_metrics(self, width_mode):
        if width_mode == 'monospaced':
            line_height_px = self.px
            attrs = self.monospaced_attrs
        else:  # proportional
            line_height_px = self.line_height_px
            attrs = self.proportional_attrs
        ascent = (attrs.box_origin_y_px + int((line_height_px - self.px) / 2)) * self.px_units
        descent = ascent - line_height_px * self.px_units
        x_height = attrs.x_height_px * self.px_units
        cap_height = attrs.cap_height_px * self.px_units
        return VerticalMetrics(ascent, descent, x_height, cap_height)

    def get_font_file_name(self, width_mode, language_flavor, font_format):
        return f'{output_name_prefix}-{self.px}px-{width_mode}-{language_flavor}.{font_format}'

    def get_info_file_name(self, width_mode):
        return f'font-info-{self.px}px-{width_mode}.md'

    def get_alphabet_txt_file_name(self, width_mode):
        return f'alphabet-{self.px}px-{width_mode}.txt'

    def get_release_zip_file_name(self, width_mode, font_format):
        return f'{output_name_prefix}-font-{self.px}px-{width_mode}-{font_format}-v{version}.zip'

    def get_alphabet_html_file_name(self, width_mode):
        return f'alphabet-{self.px}px-{width_mode}.html'
