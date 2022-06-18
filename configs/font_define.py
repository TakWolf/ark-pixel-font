import time

display_name = 'Ark Pixel'
unique_name = 'Ark-Pixel'
output_name = 'ark-pixel'
style_name = 'Regular'
version = f'{time.strftime("%Y.%m.%d")}'
copyright_string = "Copyright (c) 2021, TakWolf (https://ark-pixel-font.takwolf.com), with Reserved Font Name 'Ark Pixel'."
designer = 'TakWolf'
description = 'Ark pixel font.'
vendor_url = 'https://ark-pixel-font.takwolf.com'
designer_url = 'https://takwolf.com'
license_description = 'This Font Software is licensed under the SIL Open Font License, Version 1.1.'
license_info_url = 'https://scripts.sil.org/OFL'


class FontConfig:
    def __init__(self, px, origin_y_px, x_height_px, cap_height_px, dot_em_units=100):
        # 字体信息
        self.display_name = f'{display_name} {px}px'
        self.unique_name = f'{unique_name}-{px}px'
        # 字体参数
        self.px = px
        self.origin_y_px = origin_y_px
        self.x_height_px = x_height_px
        self.cap_height_px = cap_height_px
        self.dot_em_units = dot_em_units
        # 附加文件清单
        self.info_file_name = f'font-info-{px}px.md'
        self.preview_image_file_name = f'preview-{px}px.png'
        self.alphabet_txt_file_name = f'alphabet-{px}px.txt'
        self.alphabet_html_file_name = f'alphabet-{px}px.html'
        self.demo_html_file_name = f'demo-{px}px.html'

    def get_vertical_metrics(self):
        units_per_em = self.px * self.dot_em_units
        ascent = self.origin_y_px * self.dot_em_units
        descent = (self.origin_y_px - self.px) * self.dot_em_units
        x_height = self.x_height_px * self.dot_em_units
        cap_height = self.cap_height_px * self.dot_em_units
        return units_per_em, ascent, descent, x_height, cap_height

    def get_output_display_name(self, language_specific):
        return f'{self.display_name} {language_specific}'

    def get_output_unique_name(self, language_specific):
        return f'{self.unique_name}-{language_specific}'

    def get_output_font_file_name(self, language_specific, font_format):
        return f'{output_name}-{self.px}px-{language_specific}.{font_format}'

    def get_release_zip_file_name(self, font_format):
        return f'{output_name}-font-{self.px}px-{font_format}-v{version}.zip'
