import logging
import os
from collections.abc import Callable
from typing import IO

import unidata_blocks
from character_encoding_utils import gb2312, big5, shiftjis, ksx1001
from unidata_blocks import UnicodeBlock

from configs import path_define, FontConfig
from services.font_service import DesignContext
from utils import fs_util

logger = logging.getLogger('info-service')


def _get_unicode_chr_count_infos(alphabet: set[str]) -> list[tuple[UnicodeBlock, int]]:
    count_infos = {}
    for c in alphabet:
        code_point = ord(c)
        block = unidata_blocks.get_block_by_code_point(code_point)
        if not c.isprintable() and block.printable_count > 0:
            continue
        count = count_infos.get(block.code_start, 0)
        count += 1
        count_infos[block.code_start] = count
    code_starts = list(count_infos.keys())
    code_starts.sort()
    return [(unidata_blocks.get_block_by_code_point(code_start), count_infos[code_start]) for code_start in code_starts]


def _get_locale_chr_count_infos(alphabet: set[str], query_category_func: Callable[[str], str | None]) -> dict[str, int]:
    count_infos = {}
    for c in alphabet:
        category = query_category_func(c)
        if category is not None:
            category_count = count_infos.get(category, 0)
            category_count += 1
            count_infos[category] = category_count
            total_count = count_infos.get('total', 0)
            total_count += 1
            count_infos['total'] = total_count
    return count_infos


def _get_gb2312_chr_count_infos(alphabet: set[str]) -> list[tuple[str, int, int]]:
    count_infos = _get_locale_chr_count_infos(alphabet, gb2312.query_category)
    return [
        ('一级汉字', count_infos.get('level-1', 0), gb2312.get_level_1_count()),
        ('二级汉字', count_infos.get('level-2', 0), gb2312.get_level_2_count()),
        ('其他字符', count_infos.get('other', 0), gb2312.get_other_count()),
        ('总计', count_infos.get('total', 0), gb2312.get_count()),
    ]


def _get_big5_chr_count_infos(alphabet: set[str]) -> list[tuple[str, int, int]]:
    count_infos = _get_locale_chr_count_infos(alphabet, big5.query_category)
    return [
        ('常用汉字', count_infos.get('level-1', 0), big5.get_level_1_count()),
        ('次常用汉字', count_infos.get('level-2', 0), big5.get_level_2_count()),
        ('其他字符', count_infos.get('other', 0), big5.get_other_count()),
        ('总计', count_infos.get('total', 0), big5.get_count()),
    ]


def _get_shiftjis_chr_count_infos(alphabet: set[str]) -> list[tuple[str, int, int]]:
    count_infos = _get_locale_chr_count_infos(alphabet, shiftjis.query_category)
    return [
        ('单字节-ASCII可打印字符', count_infos.get('single-byte-ascii-printable', 0), shiftjis.get_single_byte_ascii_printable_count()),
        ('单字节-半角片假名', count_infos.get('single-byte-half-width-katakana', 0), shiftjis.get_single_byte_half_width_katakana_count()),
        ('双字节-其他字符', count_infos.get('double-byte-other', 0), shiftjis.get_double_byte_other_count()),
        ('双字节-汉字', count_infos.get('double-byte-kanji', 0), shiftjis.get_double_byte_kanji_count()),
        ('总计', count_infos.get('total', 0) - count_infos.get('single-byte-ascii-control', 0), shiftjis.get_count() - shiftjis.get_single_byte_ascii_control_count()),
    ]


def _get_ksx1001_chr_count_infos(alphabet: set[str]) -> list[tuple[str, int, int]]:
    count_infos = _get_locale_chr_count_infos(alphabet, ksx1001.query_category)
    return [
        ('谚文音节', count_infos.get('syllable', 0), ksx1001.get_syllable_count()),
        ('汉字', count_infos.get('hanja', 0), ksx1001.get_hanja_count()),
        ('其他字符', count_infos.get('other', 0), ksx1001.get_other_count()),
        ('总计', count_infos.get('total', 0), ksx1001.get_count()),
    ]


def _write_unicode_chr_count_infos_table(file: IO, infos: list[tuple[UnicodeBlock, int]]):
    file.write('| 区块范围 | 区块名称 | 区块含义 | 完成数 | 缺失数 | 进度 |\n')
    file.write('|---|---|---|---:|---:|---:|\n')
    for block, count in infos:
        code_point_range = f'{block.code_start:04X} ~ {block.code_end:04X}'
        name = block.name
        name_zh = block.name_localized('zh', '')
        total = block.printable_count
        missing = total - count if total > 0 else 0
        progress = count / total if total > 0 else 1
        finished_emoji = '🚩' if progress == 1 else '🚧'
        file.write(f'| {code_point_range} | {name} | {name_zh} | {count} / {total} | {missing} | {progress:.2%} {finished_emoji} |\n')


def _write_locale_chr_count_infos_table(file: IO, infos: list[tuple[str, int, int]]):
    file.write('| 区块名称 | 完成数 | 缺失数 | 进度 |\n')
    file.write('|---|---:|---:|---:|\n')
    for name, count, total in infos:
        missing = total - count
        progress = count / total
        finished_emoji = '🚩' if progress == 1 else '🚧'
        file.write(f'| {name} | {count} / {total} | {missing} | {progress:.2%} {finished_emoji} |\n')


def make_info_file(font_config: FontConfig, context: DesignContext, width_mode: str):
    alphabet = context.get_alphabet(width_mode)
    fs_util.make_dirs(path_define.outputs_dir)
    file_path = os.path.join(path_define.outputs_dir, font_config.get_info_file_name(width_mode))
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f'# {FontConfig.FAMILY_NAME} {font_config.size}px {"等宽模式" if width_mode == "monospaced" else "比例模式"}\n')
        file.write('\n')
        file.write('## 基本信息\n')
        file.write('\n')
        file.write('| 属性 | 值 |\n')
        file.write('|---|---|\n')
        file.write(f'| 版本号 | {FontConfig.VERSION} |\n')
        file.write(f'| 字符总数 | {len(alphabet)} |\n')
        file.write('\n')
        file.write('## Unicode 字符分布\n')
        file.write('\n')
        file.write(f'Unicode 版本：{unidata_blocks.unicode_version}\n')
        file.write('\n')
        _write_unicode_chr_count_infos_table(file, _get_unicode_chr_count_infos(alphabet))
        file.write('\n')
        file.write('## GB2312 字符分布\n')
        file.write('\n')
        file.write('简体中文参考字符集。统计范围不包含 ASCII。\n')
        file.write('\n')
        _write_locale_chr_count_infos_table(file, _get_gb2312_chr_count_infos(alphabet))
        file.write('\n')
        file.write('## Big5 字符分布\n')
        file.write('\n')
        file.write('繁体中文参考字符集。统计范围不包含 ASCII。\n')
        file.write('\n')
        _write_locale_chr_count_infos_table(file, _get_big5_chr_count_infos(alphabet))
        file.write('\n')
        file.write('## Shift-JIS 字符分布\n')
        file.write('\n')
        file.write('日语参考字符集。\n')
        file.write('\n')
        _write_locale_chr_count_infos_table(file, _get_shiftjis_chr_count_infos(alphabet))
        file.write('\n')
        file.write('## KS-X-1001 字符分布\n')
        file.write('\n')
        file.write('韩语参考字符集。统计范围不包含 ASCII。\n')
        file.write('\n')
        _write_locale_chr_count_infos_table(file, _get_ksx1001_chr_count_infos(alphabet))
    logger.info("Make info file: '%s'", file_path)


def make_alphabet_txt_file(font_config: FontConfig, context: DesignContext, width_mode: str):
    alphabet = list(context.get_alphabet(width_mode))
    alphabet.sort()
    fs_util.make_dirs(path_define.outputs_dir)
    file_path = os.path.join(path_define.outputs_dir, font_config.get_alphabet_txt_file_name(width_mode))
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(''.join(alphabet))
    logger.info("Make alphabet txt file: '%s'", file_path)
