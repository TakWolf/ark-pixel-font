import logging
import math
import os

import minify_html
from PIL import Image, ImageFont, ImageDraw

import configs
from configs import font_define, workspace_define
from utils import unicode_util, gb2312_util, big5_util, shift_jis_util, ks_x_1001_util

logger = logging.getLogger('info-service')


def _get_unicode_char_count_infos(alphabet):
    count_map = {}
    for c in alphabet:
        code_point = ord(c)
        i, _ = unicode_util.index_block_by_code_point(configs.unicode_blocks, code_point)
        count = count_map.get(i, 0)
        count += 1
        count_map[i] = count
    positions = list(count_map.keys())
    positions.sort()
    return [(configs.unicode_blocks[i], count_map[i]) for i in positions]


def _get_gb2312_char_count_infos(alphabet):
    count_map = {}
    total_count = 0
    for c in alphabet:
        block_name = gb2312_util.query_block(c)
        if block_name:
            block_count = count_map.get(block_name, 0)
            block_count += 1
            count_map[block_name] = block_count
            total_count += 1
    return [
        ('一级汉字', count_map.get('level-1', 0), gb2312_util.alphabet_level_1_count),
        ('二级汉字', count_map.get('level-2', 0), gb2312_util.alphabet_level_2_count),
        ('其他字符', count_map.get('other', 0), gb2312_util.alphabet_other_count),
        ('总计', total_count, gb2312_util.alphabet_count)
    ]


def _get_big5_char_count_infos(alphabet):
    count_map = {}
    total_count = 0
    for c in alphabet:
        block_name = big5_util.query_block(c)
        if block_name:
            block_count = count_map.get(block_name, 0)
            block_count += 1
            count_map[block_name] = block_count
            total_count += 1
    return [
        ('常用汉字', count_map.get('level-1', 0), big5_util.alphabet_level_1_count),
        ('次常用汉字', count_map.get('level-2', 0), big5_util.alphabet_level_2_count),
        ('标点符号、希腊字母、特殊符号，九个计量用汉字', count_map.get('other', 0), big5_util.alphabet_other_count),
        ('总计', total_count, big5_util.alphabet_count)
    ]


def _get_shift_jis_char_count_infos(alphabet):
    count_map = {}
    total_count = 0
    for c in alphabet:
        block_name = shift_jis_util.query_block(c)
        if block_name:
            block_count = count_map.get(block_name, 0)
            block_count += 1
            count_map[block_name] = block_count
            total_count += 1
    return [
        ('单字节-ASCII字符', count_map.get('single-ascii', 0), shift_jis_util.alphabet_single_ascii_count),
        ('单字节-半角标点和片假名', count_map.get('single-other', 0), shift_jis_util.alphabet_single_other_count),
        ('双字节-假名和其他字符', count_map.get('double-basic', 0), shift_jis_util.alphabet_double_basic_count),
        ('双字节-汉字', count_map.get('double-word', 0), shift_jis_util.alphabet_double_word_count),
        ('总计', total_count, shift_jis_util.alphabet_count)
    ]


def _get_ks_x_1001_char_count_infos(alphabet):
    count_map = {}
    total_count = 0
    for c in alphabet:
        block_name = ks_x_1001_util.query_block(c)
        if block_name:
            block_count = count_map.get(block_name, 0)
            block_count += 1
            count_map[block_name] = block_count
            total_count += 1
    return [
        ('谚文音节', count_map.get('syllable', 0), ks_x_1001_util.alphabet_syllable_count),
        ('汉字', count_map.get('word', 0), ks_x_1001_util.alphabet_word_count),
        ('其他字符', count_map.get('other', 0), ks_x_1001_util.alphabet_other_count),
        ('总计', total_count, ks_x_1001_util.alphabet_count)
    ]


def _write_unicode_char_count_infos_table(file, infos):
    file.write('| 区块范围 | 区块名称 | 区块含义 | 覆盖数 | 覆盖率 |\n')
    file.write('|---|---|---|---:|---:|\n')
    for unicode_block, count in infos:
        code_point_range = f'0x{unicode_block.begin:04X}~0x{unicode_block.end:04X}'
        progress = count / unicode_block.char_count
        finished_emoji = "🚩" if count == unicode_block.char_count else "🚧"
        file.write(f'| {code_point_range} | {unicode_block.name} | {unicode_block.name_cn if unicode_block.name_cn else ""} | {count} / {unicode_block.char_count} | {progress:.2%} {finished_emoji} |\n')


def _write_locale_char_count_infos_table(file, infos):
    file.write('| 区块名称 | 覆盖数 | 覆盖率 |\n')
    file.write('|---|---:|---:|\n')
    for title, count, total in infos:
        progress = count / total
        finished_emoji = "🚩" if count == total else "🚧"
        file.write(f'| {title} | {count} / {total} | {progress:.2%} {finished_emoji} |\n')


def make_info_file(font_config, alphabet):
    file_output_path = os.path.join(workspace_define.outputs_dir, font_config.info_file_name)
    with open(file_output_path, 'w', encoding='utf-8') as file:
        file.write(f'# {font_config.display_name}\n')
        file.write('\n')
        file.write('## 基本信息\n')
        file.write('\n')
        file.write('| 属性 | 值 |\n')
        file.write('|---|---|\n')
        file.write(f'| 字体名称 | {font_config.display_name} |\n')
        file.write(f'| 像素尺寸 | {font_config.px}px |\n')
        file.write(f'| 版本号 | {font_define.version} |\n')
        file.write(f'| 字符总数 | {len(alphabet)} |\n')
        file.write('\n')
        file.write('## Unicode 字符分布\n')
        file.write('\n')
        file.write(f'区块定义参考：[{unicode_util.blocks_doc_url}]({unicode_util.blocks_doc_url})\n')
        file.write('\n')
        _write_unicode_char_count_infos_table(file, _get_unicode_char_count_infos(alphabet))
        file.write('\n')
        file.write('## GB2312 字符分布\n')
        file.write('\n')
        file.write('简体中文参考字符集。统计范围不包含 ASCII。\n')
        file.write('\n')
        _write_locale_char_count_infos_table(file, _get_gb2312_char_count_infos(alphabet))
        file.write('\n')
        file.write('## Big5 字符分布\n')
        file.write('\n')
        file.write('繁体中文参考字符集。统计范围不包含 ASCII。\n')
        file.write('\n')
        _write_locale_char_count_infos_table(file, _get_big5_char_count_infos(alphabet))
        file.write('\n')
        file.write('## Shift-JIS 字符分布\n')
        file.write('\n')
        file.write('日语参考字符集。\n')
        file.write('\n')
        _write_locale_char_count_infos_table(file, _get_shift_jis_char_count_infos(alphabet))
        file.write('\n')
        file.write('## KS X 1001 字符分布\n')
        file.write('\n')
        file.write('韩语参考字符集。统计范围不包含 ASCII。\n')
        file.write('\n')
        _write_locale_char_count_infos_table(file, _get_ks_x_1001_char_count_infos(alphabet))
    logger.info(f'make {file_output_path}')


def make_preview_image_file(font_config):
    image_fonts = {}
    for language_specific in configs.language_specifics:
        otf_file_path = os.path.join(workspace_define.outputs_dir, font_config.get_output_font_file_name(language_specific, 'otf'))
        image_fonts[language_specific] = ImageFont.truetype(otf_file_path, font_config.px)

    image = Image.new('RGBA', (font_config.px * 35, font_config.px * 17), (255, 255, 255))
    ImageDraw.Draw(image).text((font_config.px, font_config.px), '方舟像素字体 / Ark Pixel Font', fill=(0, 0, 0), font=image_fonts['zh_cn'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 3), '我们每天度过的称之为日常的生活，其实是一个个奇迹的连续也说不定。', fill=(0, 0, 0), font=image_fonts['zh_cn'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 5), '我們每天度過的稱之為日常的生活，其實是一個個奇跡的連續也說不定。', fill=(0, 0, 0), font=image_fonts['zh_hk'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 7), '日々、私たちが過ごしている日常は、実は奇跡の連続なのかもしれない。', fill=(0, 0, 0), font=image_fonts['ja'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 9), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', fill=(0, 0, 0), font=image_fonts['zh_cn'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 11), 'the quick brown fox jumps over a lazy dog.', fill=(0, 0, 0), font=image_fonts['zh_cn'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 13), '0123456789', fill=(0, 0, 0), font=image_fonts['zh_cn'])
    ImageDraw.Draw(image).text((font_config.px, font_config.px * 15), '★☆☺☹♠♡♢♣♤♥♦♧☀☼♩♪♫♬☂☁⚓✈⚔☯', fill=(0, 0, 0), font=image_fonts['zh_cn'])
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    file_output_path = os.path.join(workspace_define.outputs_dir, font_config.preview_image_file_name)
    image.save(file_output_path)
    logger.info(f'make {file_output_path}')


def make_alphabet_txt_file(font_config, alphabet):
    file_output_path = os.path.join(workspace_define.outputs_dir, font_config.alphabet_txt_file_name)
    with open(file_output_path, 'w', encoding='utf-8') as file:
        file.write(''.join(alphabet))
    logger.info(f'make {file_output_path}')


def make_alphabet_html_file(font_config, alphabet):
    template = configs.template_env.get_template('alphabet.html')
    html = template.render(
        font_config=font_config,
        language_specifics=configs.language_specifics,
        alphabet=''.join([c for c in alphabet if ord(c) >= 128])
    )
    html = minify_html.minify(html, minify_css=True, minify_js=True)
    file_output_path = os.path.join(workspace_define.outputs_dir, font_config.alphabet_html_file_name)
    with open(file_output_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info(f'make {file_output_path}')


def make_demo_html_file(font_config):
    template = configs.template_env.get_template('demo.html')
    html = template.render(
        font_config=font_config,
        language_specifics=configs.language_specifics
    )
    html = minify_html.minify(html, minify_css=True, minify_js=True)
    file_output_path = os.path.join(workspace_define.outputs_dir, font_config.demo_html_file_name)
    with open(file_output_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info(f'make {file_output_path}')


def make_index_html_file():
    template = configs.template_env.get_template('index.html')
    html = template.render(
        font_configs=configs.font_configs,
        language_specifics=configs.language_specifics
    )
    html = minify_html.minify(html, minify_css=True, minify_js=True)
    file_output_path = os.path.join(workspace_define.outputs_dir, 'index.html')
    with open(file_output_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info(f'make {file_output_path}')


def load_image_font_from_outputs(px, language_specific, size):
    otf_file_path = os.path.join(workspace_define.outputs_dir, configs.font_config_map[px].get_output_font_file_name(language_specific, 'otf'))
    return ImageFont.truetype(otf_file_path, size)


def image_draw_text_background(image, alphabet, step, box_size, text_color, font):
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


def image_draw_text_with_shadow(image, xy, text, text_color, shadow_color, font):
    x, y = xy
    ImageDraw.Draw(image).text((x + 1, y + 1), text, fill=shadow_color, font=font)
    ImageDraw.Draw(image).text((x, y), text, fill=text_color, font=font)


def make_github_banner(alphabet_12):
    image_font_24_zh_cn = load_image_font_from_outputs(12, 'zh_cn', 24)
    image_font_12_zh_cn = load_image_font_from_outputs(12, 'zh_cn', 12)
    image_font_12_zh_hk = load_image_font_from_outputs(12, 'zh_hk', 12)
    image_font_12_ja = load_image_font_from_outputs(12, 'ja', 12)

    image_template = Image.open(os.path.join(workspace_define.images_dir, 'github-banner-template.png'))
    image = Image.new('RGBA', (image_template.width, image_template.height), (255, 255, 255, 0))
    image_draw_text_background(image, alphabet_12, 2, 14, (200, 200, 200), image_font_12_zh_cn)
    image.paste(image_template, mask=image_template)
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)
    image_draw_text_with_shadow(image, ((image.width - 12 * 29) / 2, 40 + 12 * 2), '方舟像素字体 / Ark Pixel Font', text_color, shadow_color, image_font_24_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 28) / 2, 40 + 12 * 5), '★ 开源的中日韩文像素字体 ★', text_color, shadow_color, image_font_12_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 64) / 2 , 40 + 18 * 5), '我们每天度过的称之为日常的生活，其实是一个个奇迹的连续也说不定。', text_color, shadow_color, image_font_12_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 64) / 2 , 40 + 18 * 6), '我們每天度過的稱之為日常的生活，其實是一個個奇跡的連續也說不定。', text_color, shadow_color, image_font_12_zh_hk)
    image_draw_text_with_shadow(image, ((image.width - 6 * 66) / 2 , 40 + 18 * 7), '日々、私たちが過ごしている日常は、実は奇跡の連続なのかもしれない。', text_color, shadow_color, image_font_12_ja)
    image_draw_text_with_shadow(image, ((image.width - 6 * 42) / 2 , 40 + 18 * 8), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', text_color, shadow_color, image_font_12_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 42) / 2 , 40 + 18 * 9), 'the quick brown fox jumps over a lazy dog.', text_color, shadow_color, image_font_12_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 10) / 2 , 40 + 18 * 10), '0123456789', text_color, shadow_color, image_font_12_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 48) / 2, 40 + 18 * 11), '★☆☺☹♠♡♢♣♤♥♦♧☀☼♩♪♫♬☂☁⚓✈⚔☯', text_color, shadow_color, image_font_12_zh_cn)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    file_output_path = os.path.join(workspace_define.outputs_dir, 'github-banner.png')
    image.save(file_output_path)
    logger.info(f'make {file_output_path}')


def make_itch_io_banner(alphabet_12):
    image_font_24_zh_cn = load_image_font_from_outputs(12, 'zh_cn', 24)
    image_font_12_zh_cn = load_image_font_from_outputs(12, 'zh_cn', 12)

    image_template = Image.open(os.path.join(workspace_define.images_dir, 'itch-io-banner-template.png'))
    image = Image.new('RGBA', (image_template.width, image_template.height), (255, 255, 255, 0))
    image_draw_text_background(image, alphabet_12, 5, 14, (200, 200, 200), image_font_12_zh_cn)
    image.paste(image_template, mask=image_template)
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)
    image_draw_text_with_shadow(image, ((image.width - 12 * 29) / 2, 16 + 12 * 2), '方舟像素字体 / Ark Pixel Font', text_color, shadow_color, image_font_24_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 12 * 29) / 2, 16 + 12 * 5), '★ 开源的中日韩文像素字体 ★', text_color, shadow_color, image_font_12_zh_cn)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    file_output_path = os.path.join(workspace_define.outputs_dir, 'itch-io-banner.png')
    image.save(file_output_path)
    logger.info(f'make {file_output_path}')


def make_itch_io_background(alphabet_12):
    image_font_12_zh_cn = load_image_font_from_outputs(12, 'zh_cn', 12)

    image = Image.new('RGBA', (14 * 50, 14 * 50), (255, 255, 255, 0))
    image_draw_text_background(image, alphabet_12, 1, 14, (30, 30, 30), image_font_12_zh_cn)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    file_output_path = os.path.join(workspace_define.outputs_dir, 'itch-io-background.png')
    image.save(file_output_path)
    logger.info(f'make {file_output_path}')


def make_itch_io_cover():
    image_font_24_zh_cn = load_image_font_from_outputs(12, 'zh_cn', 24)
    image_font_12_zh_cn = load_image_font_from_outputs(12, 'zh_cn', 12)
    image_font_12_zh_hk = load_image_font_from_outputs(12, 'zh_hk', 12)
    image_font_12_ja = load_image_font_from_outputs(12, 'ja', 12)

    image = Image.open(os.path.join(workspace_define.images_dir, 'itch-io-cover-template.png'))
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)
    image_draw_text_with_shadow(image, ((image.width - 12 * 12) / 2, 12), '方舟像素字体', text_color, shadow_color, image_font_24_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 32) / 2 , 12 * 4), '我们每天度过的称之为日常的生活，\n其实是一个个奇迹的连续也说不定。', text_color, shadow_color, image_font_12_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 32) / 2 , 12 * 7), '我們每天度過的稱之為日常的生活，\n其實是一個個奇跡的連續也說不定。', text_color, shadow_color, image_font_12_zh_hk)
    image_draw_text_with_shadow(image, ((image.width - 6 * 34) / 2 , 12 * 10), '日々、私たちが過ごしている日常は、\n 実は奇跡の連続なのかもしれない。', text_color, shadow_color, image_font_12_ja)
    image_draw_text_with_shadow(image, ((image.width - 6 * 42) / 2 , 12 * 13), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.\nthe quick brown fox jumps over a lazy dog.\n                0123456789', text_color, shadow_color, image_font_12_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 24) / 2, 12 * 17), '★☆☺☹♠♡♢♣♤♥♦♧\n☀☼♩♪♫♬☂☁⚓✈⚔☯', text_color, shadow_color, image_font_12_zh_cn)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    file_output_path = os.path.join(workspace_define.outputs_dir, 'itch-io-cover.png')
    image.save(file_output_path)
    logger.info(f'make {file_output_path}')


def make_afdian_cover():
    image_font_24_zh_cn = load_image_font_from_outputs(12, 'zh_cn', 24)
    image_font_12_zh_cn = load_image_font_from_outputs(12, 'zh_cn', 12)
    image_font_12_zh_hk = load_image_font_from_outputs(12, 'zh_hk', 12)
    image_font_12_ja = load_image_font_from_outputs(12, 'ja', 12)

    image = Image.open(os.path.join(workspace_define.images_dir, 'afdian-cover-template.png'))
    text_color = (255, 255, 255)
    shadow_color = (80, 80, 80)
    image_draw_text_with_shadow(image, ((image.width - 12 * 12) / 2, 12), '方舟像素字体', text_color, shadow_color, image_font_24_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 14) / 2, 12 * 4), 'Ark Pixel Font', text_color, shadow_color, image_font_12_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 28) / 2, 12 * 7), '★ 开源的中日韩文像素字体 ★', text_color, shadow_color, image_font_12_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 32) / 2 , 12 * 10), '我们每天度过的称之为日常的生活，\n其实是一个个奇迹的连续也说不定。', text_color, shadow_color, image_font_12_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 32) / 2 , 12 * 13), '我們每天度過的稱之為日常的生活，\n其實是一個個奇跡的連續也說不定。', text_color, shadow_color, image_font_12_zh_hk)
    image_draw_text_with_shadow(image, ((image.width - 6 * 34) / 2 , 12 * 16), '日々、私たちが過ごしている日常は、\n 実は奇跡の連続なのかもしれない。', text_color, shadow_color, image_font_12_ja)
    image_draw_text_with_shadow(image, ((image.width - 6 * 42) / 2 , 12 * 19), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.\nthe quick brown fox jumps over a lazy dog.\n                0123456789', text_color, shadow_color, image_font_12_zh_cn)
    image_draw_text_with_shadow(image, ((image.width - 6 * 24) / 2, 12 * 23), '★☆☺☹♠♡♢♣♤♥♦♧\n☀☼♩♪♫♬☂☁⚓✈⚔☯', text_color, shadow_color, image_font_12_zh_cn)
    image = image.resize((image.width * 2, image.height * 2), Image.NEAREST)

    file_output_path = os.path.join(workspace_define.outputs_dir, 'afdian-cover.png')
    image.save(file_output_path)
    logger.info(f'make {file_output_path}')
