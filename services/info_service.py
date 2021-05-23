import logging

import minify_html

import configs
from utils import unicode_util, gb2312_util, shift_jis_util

logger = logging.getLogger('info-service')

unicode_blocks_doc_url = 'https://www.unicode.org/Public/UNIDATA/Blocks.txt'


def _get_unicode_char_count_infos(alphabet):
    count_map = {}
    for c in alphabet:
        code_point = ord(c)
        i, _ = unicode_util.index_code_point_in_blocks(configs.unicode_blocks, code_point)
        count = count_map.get(i, 0)
        count += 1
        count_map[i] = count
    positions = list(count_map.keys())
    positions.sort()
    return [(configs.unicode_blocks[i], count_map[i]) for i in positions]


def _get_gb2312_char_count_infos(alphabet):
    level_1_count = 0
    level_2_count = 0
    other_count = 0
    total_count = 0
    for c in alphabet:
        block_name = gb2312_util.query_block(c)
        if block_name == 'level-1':
            level_1_count += 1
            total_count += 1
        elif block_name == 'level-2':
            level_2_count += 1
            total_count += 1
        elif block_name == 'other':
            other_count += 1
            total_count += 1
    return [
        ('一级汉字', level_1_count, gb2312_util.alphabet_level_1_count),
        ('二级汉字', level_2_count, gb2312_util.alphabet_level_2_count),
        ('其他字符', other_count, gb2312_util.alphabet_other_count),
        ('总计', total_count, gb2312_util.alphabet_count)
    ]


def _get_shift_jis_char_count_infos(alphabet):
    count = 0
    for c in alphabet:
        if shift_jis_util.is_chr_include(c):
            count += 1
    total = len(shift_jis_util.get_alphabet())
    return count, total


def _write_unicode_char_count_infos_table(file, infos):
    file.write('| 区块范围 | 区块名称 | 区块含义 | 覆盖情况 |\n')
    file.write('|---|---|---|---:|\n')
    for unicode_block, count in infos:
        code_point_range = f'0x{unicode_block.begin:04X}~0x{unicode_block.end:04X}'
        finished_emoji = "🏆" if count == unicode_block.char_count else "🚧"
        file.write(f'| {code_point_range} | {unicode_block.name} | {configs.unicode_block_name_translations.get(unicode_block.name, "")} | {count} / {unicode_block.char_count} {finished_emoji} |\n')


def _write_gb2312_char_count_infos_table(file, infos):
    file.write('| 区块名称 | 覆盖情况 |\n')
    file.write('|---|---:|\n')
    for title, count, total in infos:
        finished_emoji = "🏆" if count == total else "🚧"
        file.write(f'| {title} | {count} / {total} {finished_emoji} |\n')


def _write_shift_jis_char_count_infos_table(file, infos):
    file.write('| 覆盖情况 |\n')
    file.write('|---:|\n')
    count, total = infos
    finished_emoji = "🏆" if count == total else "🚧"
    file.write(f'| {count} / {total} {finished_emoji} |\n')


def make_info_file(font_config, alphabet):
    file_path = font_config.info_file_output_path
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f'# {font_config.display_name}\n')
        file.write('\n')
        file.write('## 基本信息\n')
        file.write('\n')
        file.write('| 属性 | 值 |\n')
        file.write('|---|---|\n')
        file.write(f'| 字体名称 | {font_config.display_name} |\n')
        file.write(f'| 字体风格 | {font_config.style_name} |\n')
        file.write(f'| 像素尺寸 | {font_config.px}px |\n')
        file.write(f'| 版本号 | {configs.version} |\n')
        file.write(f'| 字符总数 | {len(alphabet)} |\n')
        file.write(f'| 语言变种 | {"、".join([locale_flavor_config.locale_flavor for locale_flavor_config in font_config.locale_flavor_configs])} |\n')
        file.write('\n')
        file.write('## Unicode 字符分布\n')
        file.write('\n')
        file.write(f'区块定义参考：[{unicode_blocks_doc_url}]({unicode_blocks_doc_url})\n')
        file.write('\n')
        _write_unicode_char_count_infos_table(file, _get_unicode_char_count_infos(alphabet))
        file.write('\n')
        file.write('## GB2312 字符分布\n')
        file.write('\n')
        file.write('简体中文参考字符集。统计不包含 ASCII，和 Unicode 有交集。\n')
        file.write('\n')
        _write_gb2312_char_count_infos_table(file, _get_gb2312_char_count_infos(alphabet))
        file.write('\n')
        file.write('## Shift-JIS 字符分布\n')
        file.write('\n')
        file.write('日语参考字符集。统计仅包含可打印字符，包含 ASCII，和 Unicode 有交集。\n')
        file.write('\n')
        _write_shift_jis_char_count_infos_table(file, _get_shift_jis_char_count_infos(alphabet))
    logger.info(f'make {file_path}')


def make_preview_html_files(font_config, locale_flavor_alphabet_map):
    template = configs.template_env.get_template('preview.html')
    for locale_flavor_config in font_config.locale_flavor_configs:
        display_name = locale_flavor_config.display_name
        font_file_name = locale_flavor_config.otf_file_name
        font_px = font_config.px
        alphabet = locale_flavor_alphabet_map[locale_flavor_config.locale_flavor]
        html = template.render(
            display_name=display_name,
            font_file_name=font_file_name,
            font_px=font_px,
            content=''.join([c for c in alphabet if ord(c) >= 128])
        )
        html = minify_html.minify(html, minify_css=True, minify_js=True)
        file_path = locale_flavor_config.preview_html_file_output_path
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html)
        logger.info(f'make {file_path}')


def make_demo_html_file(font_config):
    template = configs.template_env.get_template('demo.html')
    html = template.render(font_config=font_config)
    html = minify_html.minify(html, minify_css=True, minify_js=True)
    file_path = font_config.demo_html_file_output_path
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info(f'make {file_path}')
