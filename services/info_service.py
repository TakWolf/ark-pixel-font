import logging

import configs
from utils import gb2312_util, unicode_util

logger = logging.getLogger('info-service')


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
    alphabet_level_1 = gb2312_util.get_alphabet_level_1()
    alphabet_level_2 = gb2312_util.get_alphabet_level_2()
    alphabet_other = gb2312_util.get_alphabet_other()
    infos = [
        ('一级汉字', 0, len(alphabet_level_1)),
        ('二级汉字', 0, len(alphabet_level_2)),
        ('其他字符和标点符号', 0, len(alphabet_other)),
        ('总计', 0, len(alphabet_level_1) + len(alphabet_level_2) + len(alphabet_other))
    ]
    for c in alphabet:
        need_update_position = -1
        if alphabet_level_1.__contains__(c):
            need_update_position = 0
        elif alphabet_level_2.__contains__(c):
            need_update_position = 1
        elif alphabet_other.__contains__(c):
            need_update_position = 2
        if need_update_position >= 0:
            title, count, total = infos[need_update_position]
            count += 1
            infos[need_update_position] = (title, count, total)
            title, count, total = infos[3]
            count += 1
            infos[3] = (title, count, total)
    return infos


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
        file.write(f'| 语言变种 | {"、".join([language_flavor_config.language_flavor for language_flavor_config in font_config.language_flavor_configs])} |\n')
        file.write('\n')
        file.write('## Unicode 字符分布\n')
        file.write('\n')
        _write_unicode_char_count_infos_table(file, _get_unicode_char_count_infos(alphabet))
        file.write('\n')
        file.write('## GB2312 字符分布\n')
        file.write('\n')
        _write_gb2312_char_count_infos_table(file, _get_gb2312_char_count_infos(alphabet))
    logger.info(f'----> make {file_path}')
