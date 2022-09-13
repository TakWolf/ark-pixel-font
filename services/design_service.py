import logging
import os
import shutil
import unicodedata

import configs
from configs import path_define
from utils import glyph_util, fs_util

logger = logging.getLogger('design-service')


def _parse_glyph_file_name(glyph_file_name):
    """
    解析字形源文件名称
    例子：'0030 zh_cn,ja.png'
    """
    params = glyph_file_name.removesuffix('.png').split(' ')
    assert 1 <= len(params) <= 2, glyph_file_name
    uni_hex_name = params[0].lower() if params[0] == 'notdef' else params[0].upper()
    language_specifics = []
    if len(params) >= 2:
        array = params[1].lower().split(',')
        for language_specific in configs.language_specifics:
            if language_specific in array:
                language_specifics.append(language_specific)
        assert len(language_specifics) == len(array), glyph_file_name
    return uni_hex_name, language_specifics


def classify_glyph_files(font_config):
    """
    按照 Unicode 区块分类字形源文件
    """
    px_dir = os.path.join(path_define.glyphs_dir, str(font_config.px))
    px_old_dir = os.path.join(path_define.glyphs_dir, f'{font_config.px}.old')
    assert not os.path.exists(px_old_dir), px_old_dir
    px_tmp_dir = os.path.join(path_define.glyphs_tmp_dir, str(font_config.px))
    fs_util.delete_dir(px_tmp_dir)
    for glyph_file_from_dir, _, glyph_file_names in os.walk(px_dir):
        for glyph_file_name in glyph_file_names:
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_from_path = os.path.join(glyph_file_from_dir, glyph_file_name)
            uni_hex_name, language_specifics = _parse_glyph_file_name(glyph_file_name)
            if uni_hex_name == 'notdef':
                glyph_file_to_dir = px_tmp_dir
            else:
                code_point = int(uni_hex_name, 16)
                unicode_block = configs.unidata_db.get_block_by_code_point(code_point)
                block_dir_name = f'{unicode_block.begin:04X}-{unicode_block.end:04X} {unicode_block.name}'
                glyph_file_to_dir = os.path.join(px_tmp_dir, block_dir_name)
                if unicode_block.begin == 0x4E00:  # CJK Unified Ideographs
                    glyph_file_to_dir = os.path.join(glyph_file_to_dir, f'{uni_hex_name[0:-2]}-')
            glyph_file_name = f'{uni_hex_name}{" " if len(language_specifics) > 0 else ""}{",".join(language_specifics)}.png'
            glyph_file_to_path = os.path.join(glyph_file_to_dir, glyph_file_name)
            assert not os.path.exists(glyph_file_to_path), glyph_file_from_path
            fs_util.make_dirs_if_not_exists(glyph_file_to_dir)
            shutil.copyfile(glyph_file_from_path, glyph_file_to_path)
            logger.info(f'classify glyph file {glyph_file_to_path}')
    os.rename(px_dir, px_old_dir)
    os.rename(px_tmp_dir, px_dir)
    shutil.rmtree(px_old_dir)


def verify_glyph_files(font_config):
    """
    校验并格式化字形源文件
    """
    px_dir = os.path.join(path_define.glyphs_dir, str(font_config.px))
    for glyph_file_dir, _, glyph_file_names in os.walk(px_dir):
        for glyph_file_name in glyph_file_names:
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
            glyph_data, width, height = glyph_util.load_glyph_data_from_png(glyph_file_path)
            uni_hex_name, _ = _parse_glyph_file_name(glyph_file_name)
            if uni_hex_name == 'notdef':
                code_point = -1
                c = None
            else:
                code_point = int(uni_hex_name, 16)
                c = chr(code_point)

            assert height == font_config.px, glyph_file_path

            east_asian_width = unicodedata.east_asian_width(c) if c is not None else 'F'
            # Halfwidth or Narrow
            if east_asian_width == 'H' or east_asian_width == 'Na':
                assert width == font_config.px / 2, glyph_file_path
            # Fullwidth or Wide
            elif east_asian_width == 'F' or east_asian_width == 'W':
                assert width == font_config.px, glyph_file_path
            else:  # A/Ambiguous or N/Neutral
                pass

            unicode_block = configs.unidata_db.get_block_by_code_point(code_point)
            if unicode_block is not None:
                if unicode_block.begin == 0x4E00:  # CJK Unified Ideographs
                    for alpha in glyph_data[0]:
                        assert alpha == 0, glyph_file_path
                    for i in range(0, len(glyph_data)):
                        assert glyph_data[i][-1] == 0, glyph_file_path

            glyph_util.save_glyph_data_to_png(glyph_data, glyph_file_path)
            logger.info(f'format glyph file {glyph_file_path}')


def collect_glyph_files(font_config):
    """
    收集可用字母表，生成字形源文件映射表
    """
    alphabet_cellar = set()
    glyph_file_paths_cellar = {'default': {}}
    for language_specific in configs.language_specifics:
        glyph_file_paths_cellar[language_specific] = {}

    px_dir = os.path.join(path_define.glyphs_dir, str(font_config.px))
    for glyph_file_dir, _, glyph_file_names in os.walk(px_dir):
        for glyph_file_name in glyph_file_names:
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
            uni_hex_name, language_specifics = _parse_glyph_file_name(glyph_file_name)
            if uni_hex_name == 'notdef':
                glyph_file_paths_cellar['default']['.notdef'] = glyph_file_path
            else:
                code_point = int(uni_hex_name, 16)
                if len(language_specifics) > 0:
                    for language_specific in language_specifics:
                        glyph_file_paths_cellar[language_specific][code_point] = glyph_file_path
                else:
                    glyph_file_paths_cellar['default'][code_point] = glyph_file_path
                    alphabet_cellar.add(chr(code_point))

    alphabet = list(alphabet_cellar)
    alphabet.sort()

    glyph_file_paths_map = {}
    for language_specific in configs.language_specifics:
        glyph_file_paths = dict(glyph_file_paths_cellar['default'])
        glyph_file_paths.update(glyph_file_paths_cellar[language_specific])
        glyph_file_paths_map[language_specific] = glyph_file_paths

    return alphabet, glyph_file_paths_map
