import logging
import os

import configs
from configs import path_define
from utils import unidata_util, gb2312_util, big5_util, shift_jis_util, ks_x_1001_util, fs_util

logger = logging.getLogger('info-service')


def _get_unicode_char_count_infos(alphabet):
    count_map = {}
    for c in alphabet:
        code_point = ord(c)
        unicode_block = configs.unidata_db.get_block_by_code_point(code_point)
        if not c.isprintable() and unicode_block.char_count > 0:
            continue
        count = count_map.get(unicode_block.begin, 0)
        count += 1
        count_map[unicode_block.begin] = count
    begins = list(count_map.keys())
    begins.sort()
    return [(configs.unidata_db.get_block_by_code_point(begin), count_map[begin]) for begin in begins]


def _get_locale_char_count_map(alphabet, query_block_func):
    count_map = {}
    for c in alphabet:
        block_name = query_block_func(c)
        if block_name is not None:
            block_count = count_map.get(block_name, 0)
            block_count += 1
            count_map[block_name] = block_count
            total_count = count_map.get('total', 0)
            total_count += 1
            count_map['total'] = total_count
    return count_map


def _get_gb2312_char_count_infos(alphabet):
    count_map = _get_locale_char_count_map(alphabet, gb2312_util.query_block)
    return [
        ('一级汉字', count_map.get('level-1', 0), gb2312_util.alphabet_level_1_count),
        ('二级汉字', count_map.get('level-2', 0), gb2312_util.alphabet_level_2_count),
        ('其他字符', count_map.get('other', 0), gb2312_util.alphabet_other_count),
        ('总计', count_map.get('total', 0), gb2312_util.alphabet_count),
    ]


def _get_big5_char_count_infos(alphabet):
    count_map = _get_locale_char_count_map(alphabet, big5_util.query_block)
    return [
        ('常用汉字', count_map.get('level-1', 0), big5_util.alphabet_level_1_count),
        ('次常用汉字', count_map.get('level-2', 0), big5_util.alphabet_level_2_count),
        ('其他字符', count_map.get('other', 0), big5_util.alphabet_other_count),
        ('总计', count_map.get('total', 0), big5_util.alphabet_count),
    ]


def _get_shift_jis_char_count_infos(alphabet):
    count_map = _get_locale_char_count_map(alphabet, shift_jis_util.query_block)
    return [
        ('单字节-ASCII字符', count_map.get('single-ascii', 0), shift_jis_util.alphabet_single_ascii_count),
        ('单字节-半角标点和片假名', count_map.get('single-other', 0), shift_jis_util.alphabet_single_other_count),
        ('双字节-假名和其他字符', count_map.get('double-basic', 0), shift_jis_util.alphabet_double_basic_count),
        ('双字节-汉字', count_map.get('double-word', 0), shift_jis_util.alphabet_double_word_count),
        ('总计', count_map.get('total', 0), shift_jis_util.alphabet_count),
    ]


def _get_ks_x_1001_char_count_infos(alphabet):
    count_map = _get_locale_char_count_map(alphabet, ks_x_1001_util.query_block)
    return [
        ('谚文音节', count_map.get('syllable', 0), ks_x_1001_util.alphabet_syllable_count),
        ('汉字', count_map.get('word', 0), ks_x_1001_util.alphabet_word_count),
        ('其他字符', count_map.get('other', 0), ks_x_1001_util.alphabet_other_count),
        ('总计', count_map.get('total', 0), ks_x_1001_util.alphabet_count),
    ]


def _write_unicode_char_count_infos_table(file, infos):
    file.write('| 区块范围 | 区块名称 | 区块含义 | 覆盖数 | 覆盖率 |\n')
    file.write('|---|---|---|---:|---:|\n')
    for unicode_block, count in infos:
        code_point_range = f'{unicode_block.begin:04X} ~ {unicode_block.end:04X}'
        if unicode_block.char_count > 0:
            progress = count / unicode_block.char_count
        else:
            progress = 1
        finished_emoji = '🚩' if progress == 1 else '🚧'
        file.write(f'| {code_point_range} | {unicode_block.name} | {unicode_block.name_cn if unicode_block.name_cn is not None else ""} | {count} / {unicode_block.char_count} | {progress:.2%} {finished_emoji} |\n')


def _write_locale_char_count_infos_table(file, infos):
    file.write('| 区块名称 | 覆盖数 | 覆盖率 |\n')
    file.write('|---|---:|---:|\n')
    for title, count, total in infos:
        progress = count / total
        finished_emoji = '🚩' if progress == 1 else '🚧'
        file.write(f'| {title} | {count} / {total} | {progress:.2%} {finished_emoji} |\n')


def make_info_file(font_config, alphabet):
    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    info_file_path = os.path.join(path_define.outputs_dir, font_config.info_file_name)
    with open(info_file_path, 'w', encoding='utf-8') as file:
        file.write(f'# {configs.font_name} {font_config.px}px\n')
        file.write('\n')
        file.write('## 基本信息\n')
        file.write('\n')
        file.write('| 属性 | 值 |\n')
        file.write('|---|---|\n')
        file.write(f'| 版本号 | {configs.font_version} |\n')
        file.write(f'| 字符总数 | {len(alphabet)} |\n')
        file.write('\n')
        file.write('## Unicode 字符分布\n')
        file.write('\n')
        file.write(f'区块定义参考：[{unidata_util.blocks_doc_url}]({unidata_util.blocks_doc_url})\n')
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
    logger.info(f'make {info_file_path}')


def make_alphabet_txt_file(font_config, alphabet):
    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    txt_file_path = os.path.join(path_define.outputs_dir, font_config.alphabet_txt_file_name)
    with open(txt_file_path, 'w', encoding='utf-8') as file:
        file.write(''.join(alphabet))
    logger.info(f'make {txt_file_path}')
