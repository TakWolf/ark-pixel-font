import logging
import os

import math
from PIL import Image, ImageFont, ImageDraw

import configs
from configs import path_define
from services import info_service
from utils import fs_util

logger = logging.getLogger('image-service')


def _load_font(px, width_mode, language_specific, px_scale=1):
    font_file_path = os.path.join(path_define.outputs_dir, configs.font_config_map[px].get_font_file_name(width_mode, language_specific, 'woff2'))
    return ImageFont.truetype(font_file_path, px * px_scale)


def _draw_text(image, xy, text, font, text_color=(0, 0, 0), shadow_color=None, line_height=None, line_gap=0, is_horizontal_centered=False, is_vertical_centered=False):
    draw = ImageDraw.Draw(image)
    x, y = xy
    default_line_height = sum(font.getmetrics())
    if line_height is None:
        line_height = default_line_height
    y += (line_height - default_line_height) / 2
    spacing = line_height + line_gap - font.getsize('A')[1]
    if is_horizontal_centered:
        x -= draw.textbbox((0, 0), text, font=font)[2] / 2
    if is_vertical_centered:
        y -= line_height / 2
    if shadow_color is not None:
        draw.text((x + 1, y + 1), text, fill=shadow_color, font=font, spacing=spacing)
    draw.text((x, y), text, fill=text_color, font=font, spacing=spacing)


def _draw_text_background(image, alphabet, step, box_size, font, text_color):
    draw = ImageDraw.Draw(image)
    alphabet_index = 0
    for index, c in enumerate(alphabet):
        code_point = ord(c)
        if code_point >= 0x4E00:
            alphabet_index = index
            break
    x_count = math.ceil(image.width / box_size)
    y_count = math.ceil(image.height / box_size)
    x_offset = (image.width - x_count * box_size) / 2 + (box_size - font.size) / 2
    y_offset = (image.height - y_count * box_size) / 2 + (box_size - sum(font.getmetrics())) / 2
    for y in range(y_count):
        for x in range(x_count):
            draw.text((x_offset + x * box_size, y_offset + y * box_size), alphabet[alphabet_index], fill=text_color, font=font)
            alphabet_index += step


def make_preview_image_file(font_config):
    font_latin = _load_font(font_config.px, 'proportional', 'latin')
    font_zh_cn = _load_font(font_config.px, 'proportional', 'zh_cn')
    font_zh_tr = _load_font(font_config.px, 'proportional', 'zh_tr')
    font_ja = _load_font(font_config.px, 'proportional', 'ja')

    image = Image.new('RGBA', (font_config.px * 35, font_config.px * 2 + font_config.line_height_px * 8), (255, 255, 255))
    _draw_text(image, (font_config.px, font_config.px), '方舟像素字体 / Ark Pixel Font', font_zh_cn)
    _draw_text(image, (font_config.px, font_config.px + font_config.line_height_px), '我们每天度过的称之为日常的生活，其实是一个个奇迹的连续也说不定。', font_zh_cn)
    _draw_text(image, (font_config.px, font_config.px + font_config.line_height_px * 2), '我們每天度過的稱之為日常的生活，其實是一個個奇跡的連續也說不定。', font_zh_tr)
    _draw_text(image, (font_config.px, font_config.px + font_config.line_height_px * 3), '日々、私たちが過ごしている日常は、実は奇跡の連続なのかもしれない。', font_ja)
    _draw_text(image, (font_config.px, font_config.px + font_config.line_height_px * 4), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_latin)
    _draw_text(image, (font_config.px, font_config.px + font_config.line_height_px * 5), 'the quick brown fox jumps over a lazy dog.', font_latin)
    _draw_text(image, (font_config.px, font_config.px + font_config.line_height_px * 6), '0123456789', font_latin)
    _draw_text(image, (font_config.px, font_config.px + font_config.line_height_px * 7), '★☆☺☹♠♡♢♣♤♥♦♧☀☼♩♪♫♬☂☁⚓✈⚔☯', font_latin)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, font_config.preview_image_file_name)
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_readme_banner():
    alphabet = info_service.read_alphabet_txt_file(configs.font_config_map[12], 'proportional')
    font_x1 = _load_font(12, 'proportional', 'zh_cn')
    font_x2 = _load_font(12, 'proportional', 'zh_cn', 2)
    box_size = 14
    line_height = configs.font_config_map[12].line_height_px
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)

    image_background = Image.open(os.path.join(path_define.images_dir, 'readme-banner-background.png'))
    image = Image.new('RGBA', (image_background.width, image_background.height), (255, 255, 255, 0))
    _draw_text_background(image, alphabet, 12, box_size, font_x1, (200, 200, 200))
    image.paste(image_background, mask=image_background)
    _draw_text(image, (image.width / 2, 28), '方舟像素字体', font_x2, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 28 + line_height * 2 + 4), '★ 开源的泛中日韩像素字体 ★', font_x1, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'readme-banner.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_github_banner():
    alphabet = info_service.read_alphabet_txt_file(configs.font_config_map[12], 'proportional')
    font_title = _load_font(12, 'proportional', 'zh_cn', 2)
    font_latin = _load_font(12, 'proportional', 'latin')
    font_zh_cn = _load_font(12, 'proportional', 'zh_cn')
    font_zh_tr = _load_font(12, 'proportional', 'zh_tr')
    font_ja = _load_font(12, 'proportional', 'ja')
    box_size = 14
    line_height = configs.font_config_map[12].line_height_px
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)

    image_background = Image.open(os.path.join(path_define.images_dir, 'github-banner-background.png'))
    image = Image.new('RGBA', (image_background.width, image_background.height), (255, 255, 255, 0))
    _draw_text_background(image, alphabet, 6, box_size, font_zh_cn, (200, 200, 200))
    image.paste(image_background, mask=image_background)
    _draw_text(image, (image.width / 2, 40 + line_height), '方舟像素字体 / Ark Pixel Font', font_title, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 3), '★ 开源的泛中日韩像素字体 ★', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 5), '我们每天度过的称之为日常的生活，其实是一个个奇迹的连续也说不定。', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 6), '我們每天度過的稱之為日常的生活，其實是一個個奇跡的連續也說不定。', font_zh_tr, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 7), '日々、私たちが過ごしている日常は、実は奇跡の連続なのかもしれない。', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 8), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 9), 'the quick brown fox jumps over a lazy dog.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 10), '0123456789', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + line_height * 11), '★☆☺☹♠♡♢♣♤♥♦♧☀☼♩♪♫♬☂☁⚓✈⚔☯', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'github-banner.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_itch_io_banner():
    alphabet = info_service.read_alphabet_txt_file(configs.font_config_map[12], 'proportional')
    font_x1 = _load_font(12, 'proportional', 'zh_cn')
    font_x2 = _load_font(12, 'proportional', 'zh_cn', 2)
    box_size = 14
    line_height = configs.font_config_map[12].line_height_px
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)

    image_background = Image.open(os.path.join(path_define.images_dir, 'itch-io-banner-background.png'))
    image = Image.new('RGBA', (image_background.width, image_background.height), (255, 255, 255, 0))
    _draw_text_background(image, alphabet, 12, box_size, font_x1, (200, 200, 200))
    image.paste(image_background, mask=image_background)
    _draw_text(image, (image.width / 2, 32), '方舟像素字体 / Ark Pixel Font', font_x2, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 32 + line_height * 2 + 4), '★ 开源的泛中日韩像素字体 ★', font_x1, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'itch-io-banner.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_itch_io_background():
    alphabet = info_service.read_alphabet_txt_file(configs.font_config_map[12], 'proportional')
    font = _load_font(12, 'proportional', 'zh_cn')
    box_size = 14

    image = Image.new('RGBA', (box_size * 50, box_size * 50), (255, 255, 255, 0))
    _draw_text_background(image, alphabet, 2, box_size, font, (30, 30, 30))
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'itch-io-background.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_itch_io_cover():
    font_title = _load_font(12, 'proportional', 'zh_cn', 2)
    font_latin = _load_font(12, 'proportional', 'latin')
    font_zh_cn = _load_font(12, 'proportional', 'zh_cn')
    font_zh_tr = _load_font(12, 'proportional', 'zh_tr')
    font_ja = _load_font(12, 'proportional', 'ja')
    line_height = configs.font_config_map[12].line_height_px
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)

    image = Image.open(os.path.join(path_define.images_dir, 'itch-io-cover-background.png'))
    _draw_text(image, (image.width / 2, 6), '方舟像素字体', font_title, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 2), '我们每天度过的称之为日常的生活，', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 3), '其实是一个个奇迹的连续也说不定。', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 4), '我們每天度過的稱之為日常的生活，', font_zh_tr, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 5), '其實是一個個奇跡的連續也說不定。', font_zh_tr, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 6), '日々、私たちが過ごしている日常は、', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 7), '実は奇跡の連続なのかもしれない。', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 8), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 9), 'the quick brown fox jumps over a lazy dog.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 10), '0123456789', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 11), '★☆☺☹♠♡♢♣♤♥♦♧', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + line_height * 12), '☀☼♩♪♫♬☂☁⚓✈⚔☯', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'itch-io-cover.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_afdian_cover():
    font_title = _load_font(12, 'proportional', 'zh_cn', 2)
    font_latin = _load_font(12, 'proportional', 'latin')
    font_zh_cn = _load_font(12, 'proportional', 'zh_cn')
    font_zh_tr = _load_font(12, 'proportional', 'zh_tr')
    font_ja = _load_font(12, 'proportional', 'ja')
    line_height = configs.font_config_map[12].line_height_px
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)

    image = Image.open(os.path.join(path_define.images_dir, 'afdian-cover-background.png'))
    _draw_text(image, (image.width / 2, 12), '方舟像素字体', font_title, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 12 + line_height * 2), 'Ark Pixel Font', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 3), '★ 开源的泛中日韩像素字体 ★', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 5), '我们每天度过的称之为日常的生活，', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 6), '其实是一个个奇迹的连续也说不定。', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 7), '我們每天度過的稱之為日常的生活，', font_zh_tr, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 8), '其實是一個個奇跡的連續也說不定。', font_zh_tr, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 9), '日々、私たちが過ごしている日常は、', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 10), '実は奇跡の連続なのかもしれない。', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 11), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 12), 'the quick brown fox jumps over a lazy dog.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 13), '0123456789', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 14), '★☆☺☹♠♡♢♣♤♥♦♧', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + line_height * 15), '☀☼♩♪♫♬☂☁⚓✈⚔☯', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'afdian-cover.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')
