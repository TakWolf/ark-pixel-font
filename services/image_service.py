import logging
import os

import math
from PIL import Image, ImageFont, ImageDraw

import configs
from configs import path_define
from utils import fs_util

logger = logging.getLogger('image-service')


def make_preview_image_file(font_config):
    image_fonts = {}
    for language_specific in configs.language_specifics:
        font_file_path = os.path.join(path_define.outputs_dir, font_config.get_font_file_name(language_specific, 'otf'))
        image_fonts[language_specific] = ImageFont.truetype(font_file_path, font_config.px)

    image = Image.new('RGBA', (font_config.px * 35, font_config.px * 17), (255, 255, 255))
    ImageDraw.Draw(image).text((font_config.px, font_config.px), '方舟像素字体 / Ark Pixel Font', fill=(0, 0, 0), font=image_fonts['zh_cn'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 3), '我们每天度过的称之为日常的生活，其实是一个个奇迹的连续也说不定。', fill=(0, 0, 0), font=image_fonts['zh_cn'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 5), '我們每天度過的稱之為日常的生活，其實是一個個奇跡的連續也說不定。', fill=(0, 0, 0), font=image_fonts['zh_tr'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 7), '日々、私たちが過ごしている日常は、実は奇跡の連続なのかもしれない。', fill=(0, 0, 0), font=image_fonts['ja'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 9), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', fill=(0, 0, 0), font=image_fonts['latin'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 11), 'the quick brown fox jumps over a lazy dog.', fill=(0, 0, 0), font=image_fonts['latin'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 13), '0123456789', fill=(0, 0, 0), font=image_fonts['latin'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 15), '★☆☺☹♠♡♢♣♤♥♦♧☀☼♩♪♫♬☂☁⚓✈⚔☯', fill=(0, 0, 0), font=image_fonts['latin'])
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, font_config.preview_image_file_name)
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def _load_alphabet_from_outputs(px):
    txt_file_path = os.path.join(path_define.outputs_dir, configs.font_config_map[px].alphabet_txt_file_name)
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    alphabet = list(text)
    return alphabet


def _load_image_font_from_outputs(px, language_specific, size):
    font_file_path = os.path.join(path_define.outputs_dir, configs.font_config_map[px].get_font_file_name(language_specific, 'otf'))
    return ImageFont.truetype(font_file_path, size)


def _image_draw_text_background(image, alphabet, step, box_size, text_color, font):
    alphabet_index = 0
    for index, c in enumerate(alphabet):
        code_point = ord(c)
        if code_point >= 0x4E00:
            alphabet_index = index
            break
    x_count = math.ceil(image.width / box_size)
    y_count = math.ceil(image.height / box_size)
    x_offset = (image.width - x_count * box_size) / 2 + (box_size - font.size) / 2
    y_offset = (image.height - y_count * box_size) / 2 + (box_size - font.size) / 2
    for y in range(y_count):
        for x in range(x_count):
            alphabet_index += step
            ImageDraw.Draw(image).text((x_offset + x * box_size, y_offset + y * box_size), alphabet[alphabet_index], fill=text_color, font=font)


def _image_draw_text_with_shadow(image, xy, text, text_color, shadow_color, font):
    x, y = xy
    ImageDraw.Draw(image).text((x + 1, y + 1), text, fill=shadow_color, font=font)
    ImageDraw.Draw(image).text((x, y), text, fill=text_color, font=font)


def make_github_banner():
    alphabet_12 = _load_alphabet_from_outputs(12)
    image_font_24_zh_cn = _load_image_font_from_outputs(12, 'zh_cn', 24)
    image_font_12_latin = _load_image_font_from_outputs(12, 'latin', 12)
    image_font_12_zh_cn = _load_image_font_from_outputs(12, 'zh_cn', 12)
    image_font_12_zh_tr = _load_image_font_from_outputs(12, 'zh_tr', 12)
    image_font_12_ja = _load_image_font_from_outputs(12, 'ja', 12)

    image_template = Image.open(os.path.join(path_define.images_dir, 'github-banner-background.png'))
    image = Image.new('RGBA', (image_template.width, image_template.height), (255, 255, 255, 0))
    _image_draw_text_background(image, alphabet_12, 2, 14, (200, 200, 200), image_font_12_zh_cn)
    image.paste(image_template, mask=image_template)
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)
    _image_draw_text_with_shadow(image, ((image.width - 12 * 29) / 2, 40 + 12 * 2), '方舟像素字体 / Ark Pixel Font', text_color, shadow_color, image_font_24_zh_cn)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 28) / 2, 40 + 12 * 5), '★ 开源的泛中日韩像素字体 ★', text_color, shadow_color, image_font_12_zh_cn)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 64) / 2, 40 + 18 * 5), '我们每天度过的称之为日常的生活，其实是一个个奇迹的连续也说不定。', text_color, shadow_color, image_font_12_zh_cn)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 64) / 2, 40 + 18 * 6), '我們每天度過的稱之為日常的生活，其實是一個個奇跡的連續也說不定。', text_color, shadow_color, image_font_12_zh_tr)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 66) / 2, 40 + 18 * 7), '日々、私たちが過ごしている日常は、実は奇跡の連続なのかもしれない。', text_color, shadow_color, image_font_12_ja)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 42) / 2, 40 + 18 * 8), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', text_color, shadow_color, image_font_12_latin)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 42) / 2, 40 + 18 * 9), 'the quick brown fox jumps over a lazy dog.', text_color, shadow_color, image_font_12_latin)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 10) / 2, 40 + 18 * 10), '0123456789', text_color, shadow_color, image_font_12_latin)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 48) / 2, 40 + 18 * 11), '★☆☺☹♠♡♢♣♤♥♦♧☀☼♩♪♫♬☂☁⚓✈⚔☯', text_color, shadow_color, image_font_12_latin)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'github-banner.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_itch_io_banner():
    alphabet_12 = _load_alphabet_from_outputs(12)
    image_font_24_zh_cn = _load_image_font_from_outputs(12, 'zh_cn', 24)
    image_font_12_zh_cn = _load_image_font_from_outputs(12, 'zh_cn', 12)

    image_template = Image.open(os.path.join(path_define.images_dir, 'itch-io-banner-background.png'))
    image = Image.new('RGBA', (image_template.width, image_template.height), (255, 255, 255, 0))
    _image_draw_text_background(image, alphabet_12, 5, 14, (200, 200, 200), image_font_12_zh_cn)
    image.paste(image_template, mask=image_template)
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)
    _image_draw_text_with_shadow(image, ((image.width - 12 * 29) / 2, 16 + 12 * 2), '方舟像素字体 / Ark Pixel Font', text_color, shadow_color, image_font_24_zh_cn)
    _image_draw_text_with_shadow(image, ((image.width - 12 * 29) / 2, 16 + 12 * 5), '★ 开源的泛中日韩像素字体 ★', text_color, shadow_color, image_font_12_zh_cn)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'itch-io-banner.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_itch_io_background():
    alphabet_12 = _load_alphabet_from_outputs(12)
    image_font_12_zh_cn = _load_image_font_from_outputs(12, 'zh_cn', 12)

    image = Image.new('RGBA', (14 * 50, 14 * 50), (255, 255, 255, 0))
    _image_draw_text_background(image, alphabet_12, 1, 14, (30, 30, 30), image_font_12_zh_cn)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'itch-io-background.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_itch_io_cover():
    image_font_24_zh_cn = _load_image_font_from_outputs(12, 'zh_cn', 24)
    image_font_12_latin = _load_image_font_from_outputs(12, 'latin', 12)
    image_font_12_zh_cn = _load_image_font_from_outputs(12, 'zh_cn', 12)
    image_font_12_zh_tr = _load_image_font_from_outputs(12, 'zh_tr', 12)
    image_font_12_ja = _load_image_font_from_outputs(12, 'ja', 12)

    image = Image.open(os.path.join(path_define.images_dir, 'itch-io-cover-background.png'))
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)
    _image_draw_text_with_shadow(image, ((image.width - 12 * 12) / 2, 12), '方舟像素字体', text_color, shadow_color, image_font_24_zh_cn)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 32) / 2, 12 * 4), '我们每天度过的称之为日常的生活，\n其实是一个个奇迹的连续也说不定。', text_color, shadow_color, image_font_12_zh_cn)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 32) / 2, 12 * 7), '我們每天度過的稱之為日常的生活，\n其實是一個個奇跡的連續也說不定。', text_color, shadow_color, image_font_12_zh_tr)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 34) / 2, 12 * 10), '日々、私たちが過ごしている日常は、\n 実は奇跡の連続なのかもしれない。', text_color, shadow_color, image_font_12_ja)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 42) / 2, 12 * 13), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.\nthe quick brown fox jumps over a lazy dog.\n                0123456789', text_color, shadow_color, image_font_12_latin)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 24) / 2, 12 * 17), '★☆☺☹♠♡♢♣♤♥♦♧\n☀☼♩♪♫♬☂☁⚓✈⚔☯', text_color, shadow_color, image_font_12_latin)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'itch-io-cover.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')


def make_afdian_cover():
    image_font_24_zh_cn = _load_image_font_from_outputs(12, 'zh_cn', 24)
    image_font_12_latin = _load_image_font_from_outputs(12, 'latin', 12)
    image_font_12_zh_cn = _load_image_font_from_outputs(12, 'zh_cn', 12)
    image_font_12_zh_tr = _load_image_font_from_outputs(12, 'zh_tr', 12)
    image_font_12_ja = _load_image_font_from_outputs(12, 'ja', 12)

    image = Image.open(os.path.join(path_define.images_dir, 'afdian-cover-background.png'))
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)
    _image_draw_text_with_shadow(image, ((image.width - 12 * 12) / 2, 12), '方舟像素字体', text_color, shadow_color, image_font_24_zh_cn)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 14) / 2, 12 * 4), 'Ark Pixel Font', text_color, shadow_color, image_font_12_zh_cn)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 28) / 2, 12 * 7), '★ 开源的泛中日韩像素字体 ★', text_color, shadow_color, image_font_12_zh_cn)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 32) / 2, 12 * 10), '我们每天度过的称之为日常的生活，\n其实是一个个奇迹的连续也说不定。', text_color, shadow_color, image_font_12_zh_cn)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 32) / 2, 12 * 13), '我們每天度過的稱之為日常的生活，\n其實是一個個奇跡的連續也說不定。', text_color, shadow_color, image_font_12_zh_tr)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 34) / 2, 12 * 16), '日々、私たちが過ごしている日常は、\n 実は奇跡の連続なのかもしれない。', text_color, shadow_color, image_font_12_ja)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 42) / 2, 12 * 19), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.\nthe quick brown fox jumps over a lazy dog.\n                0123456789', text_color, shadow_color, image_font_12_latin)
    _image_draw_text_with_shadow(image, ((image.width - 6 * 24) / 2, 12 * 23), '★☆☺☹♠♡♢♣♤♥♦♧\n☀☼♩♪♫♬☂☁⚓✈⚔☯', text_color, shadow_color, image_font_12_latin)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    image_file_path = os.path.join(path_define.outputs_dir, 'afdian-cover.png')
    image.save(image_file_path)
    logger.info(f'make {image_file_path}')
