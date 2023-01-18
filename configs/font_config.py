import os
import time
import tomllib

from configs import path_define

display_name_prefix = 'Ark Pixel'
unique_name_prefix = 'Ark-Pixel'
output_name_prefix = 'ark-pixel'
style_name = 'Regular'
version = f'{time.strftime("%Y.%m.%d")}'
copyright_string = 'Copyright (c) 2021, TakWolf (https://takwolf.com), with Reserved Font Name "Ark Pixel".'
designer = 'TakWolf'
description = 'Open source Pan-CJK pixel font.'
vendor_url = 'https://ark-pixel-font.takwolf.com'
designer_url = 'https://takwolf.com'
license_description = 'This Font Software is licensed under the SIL Open Font License, Version 1.1.'
license_info_url = 'https://scripts.sil.org/OFL'


class FontAttrs:
    def __init__(self, config_data):
        # 盒子中基准线像素位置，即以字面框左上角原点计算，基线所处的像素位置
        self.box_origin_y_px = config_data['box_origin_y_px']
        # 小写字母像素高度
        self.x_height_px = config_data['x_height_px']
        # 大写字母像素高度
        self.cap_height_px = config_data['cap_height_px']


class VerticalMetrics:
    """
    竖向量度值
    可以参考：https://glyphsapp.com/zh/learn/vertical-metrics
    """
    def __init__(self, line_height, ascent, descent, x_height, cap_height):
        self.line_height = line_height
        self.ascent = ascent
        self.descent = descent
        self.x_height = x_height
        self.cap_height = cap_height


class FontConfig:
    def __init__(self, px, dot_em_units=100):
        config_file_path = os.path.join(path_define.glyphs_dir, str(px), 'config.toml')
        with open(config_file_path, 'rb') as config_file:
            config_data = tomllib.load(config_file)['font']
        assert px == config_data['px'], config_file_path

        # 字体像素尺寸，也是等宽模式的像素行高
        self.px = px
        # 比例模式的像素行高
        self.line_height_px = config_data['line_height_px']
        # 等宽模式属性
        self.monospaced_attrs = FontAttrs(config_data['monospaced'])
        # 比例模式属性
        self.proportional_attrs = FontAttrs(config_data['proportional'])
        # 每个像素对应的 EM 单位数
        self.dot_em_units = dot_em_units

        self.demo_html_file_name = f'demo-{px}px.html'
        self.preview_image_file_name = f'preview-{px}px.png'

    def get_name_strings(self, width_mode, language_specific):
        display_name = f'{display_name_prefix} {self.px}px {width_mode} {language_specific}'
        unique_name = f'{unique_name_prefix}-{self.px}px-{width_mode}-{language_specific}-{style_name}'
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
        return self.px * self.dot_em_units

    def get_box_origin_y(self, width_mode):
        if width_mode == 'monospaced':
            attrs = self.monospaced_attrs
        else:  # proportional
            attrs = self.proportional_attrs
        return attrs.box_origin_y_px * self.dot_em_units

    def get_vertical_metrics(self, width_mode):
        if width_mode == 'monospaced':
            line_height_px = self.px
            attrs = self.monospaced_attrs
        else:  # proportional
            line_height_px = self.line_height_px
            attrs = self.proportional_attrs
        line_height = line_height_px * self.dot_em_units
        ascent = (attrs.box_origin_y_px + int((line_height_px - self.px) / 2)) * self.dot_em_units
        descent = ascent - line_height
        x_height = attrs.x_height_px * self.dot_em_units
        cap_height = attrs.cap_height_px * self.dot_em_units
        return VerticalMetrics(line_height, ascent, descent, x_height, cap_height)

    def get_font_file_name(self, width_mode, language_specific, font_format):
        return f'{output_name_prefix}-{self.px}px-{width_mode}-{language_specific}.{font_format}'

    def get_info_file_name(self, width_mode):
        return f'font-info-{self.px}px-{width_mode}.md'

    def get_alphabet_txt_file_name(self, width_mode):
        return f'alphabet-{self.px}px-{width_mode}.txt'

    def get_release_zip_file_name(self, width_mode, font_format):
        return f'{output_name_prefix}-font-{self.px}px-{width_mode}-{font_format}-v{version}.zip'

    def get_alphabet_html_file_name(self, width_mode):
        return f'alphabet-{self.px}px-{width_mode}.html'
