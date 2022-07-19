import logging
import os
import shutil
import unicodedata

import configs
from configs import workspace_define
from utils import glyph_util

logger = logging.getLogger('design-service')


def _parse_design_file_name(design_file_name):
    """
    解析设计文件名称
    例如：'0030 zh_cn,ja.png'
    """
    params = design_file_name.removesuffix('.png').split(' ')
    assert 1 <= len(params) <= 2, design_file_name
    uni_hex_name = params[0].lower() if params[0] == 'notdef' else params[0].upper()
    language_specifics = []
    if len(params) >= 2:
        array = params[1].lower().split(',')
        for language_specific in configs.language_specifics:
            if language_specific in array:
                language_specifics.append(language_specific)
        assert len(language_specifics) == len(array), design_file_name
    return uni_hex_name, language_specifics


def classify_px_design_files(font_config):
    """
    按照 Unicode 区块分类设计文件
    """
    px_dir = os.path.join(workspace_define.design_dir, str(font_config.px))
    px_tmp_dir = os.path.join(workspace_define.design_tmp_dir, str(font_config.px))
    if os.path.exists(px_tmp_dir):
        shutil.rmtree(px_tmp_dir)
    for design_file_from_dir, _, design_file_names in os.walk(px_dir):
        for design_file_name in design_file_names:
            if not design_file_name.endswith('.png'):
                continue
            design_file_from_path = os.path.join(design_file_from_dir, design_file_name)
            uni_hex_name, language_specifics = _parse_design_file_name(design_file_name)
            if uni_hex_name == 'notdef':
                design_file_to_dir = px_tmp_dir
            else:
                code_point = int(uni_hex_name, 16)
                unicode_block = configs.unidata_db.get_block_by_code_point(code_point)
                block_dir_name = f'{unicode_block.begin:04X}-{unicode_block.end:04X} {unicode_block.name}'
                design_file_to_dir = os.path.join(px_tmp_dir, block_dir_name)
                if unicode_block.name == 'CJK Unified Ideographs':
                    design_file_to_dir = os.path.join(design_file_to_dir, f'{uni_hex_name[0:-2]}-')
            if not os.path.exists(design_file_to_dir):
                os.makedirs(design_file_to_dir)
            design_file_name = f'{uni_hex_name}{" " if len(language_specifics) > 0 else ""}{",".join(language_specifics)}.png'
            design_file_to_path = os.path.join(design_file_to_dir, design_file_name)
            assert not os.path.exists(design_file_to_path), design_file_from_path
            shutil.copyfile(design_file_from_path, design_file_to_path)
            logger.info(f'classify design file {design_file_to_path}')
    shutil.rmtree(px_dir)
    os.rename(px_tmp_dir, px_dir)


def verify_px_design_files(font_config):
    """
    校验并格式化设计文件
    """
    px_dir = os.path.join(workspace_define.design_dir, str(font_config.px))
    for design_file_dir, _, design_file_names in os.walk(px_dir):
        for design_file_name in design_file_names:
            if not design_file_name.endswith('.png'):
                continue
            design_file_path = os.path.join(design_file_dir, design_file_name)
            design_data, width, height = glyph_util.load_design_data_from_png(design_file_path)
            uni_hex_name, _ = _parse_design_file_name(design_file_name)
            if uni_hex_name == 'notdef':
                code_point = -1
                c = None
            else:
                code_point = int(uni_hex_name, 16)
                c = chr(code_point)

            # 校验宽度
            east_asian_width_status = unicodedata.east_asian_width(c) if c else 'N'
            if east_asian_width_status == 'H' or east_asian_width_status == 'Na':
                assert width == font_config.px / 2, design_file_path
            elif east_asian_width_status == 'F' or east_asian_width_status == 'W':
                assert width == font_config.px, design_file_path
            else:  # 'A' or 'N'
                assert width == font_config.px / 2 or width == font_config.px, design_file_path

            # 校验高度
            assert height == font_config.px, design_file_path

            # 校验间距
            if 0x4E00 <= code_point <= 0x9FFF:
                for alpha in design_data[0]:
                    assert alpha == 0, design_file_path
                for i in range(0, len(design_data)):
                    assert design_data[i][-1] == 0, design_file_path

            # 格式化设计文件
            glyph_util.save_design_data_to_png(design_data, design_file_path)
            logger.info(f'format design file {design_file_path}')


def collect_px_design_files(font_config):
    """
    收集可用字母表，生成设计文件映射表
    """
    # 遍历文件并分组
    alphabet = set()
    default_design_file_paths = {}
    special_design_file_paths_map = {}
    px_dir = os.path.join(workspace_define.design_dir, str(font_config.px))
    for design_file_dir, _, design_file_names in os.walk(px_dir):
        for design_file_name in design_file_names:
            if not design_file_name.endswith('.png'):
                continue
            design_file_path = os.path.join(design_file_dir, design_file_name)
            uni_hex_name, language_specifics = _parse_design_file_name(design_file_name)
            if uni_hex_name == 'notdef':
                default_design_file_paths['.notdef'] = design_file_path
            else:
                code_point = int(uni_hex_name, 16)
                if len(language_specifics) > 0:
                    for language_specific in language_specifics:
                        if language_specific in special_design_file_paths_map:
                            special_design_file_paths = special_design_file_paths_map[language_specific]
                        else:
                            special_design_file_paths = {}
                            special_design_file_paths_map[language_specific] = special_design_file_paths
                        special_design_file_paths[code_point] = design_file_path
                else:
                    default_design_file_paths[code_point] = design_file_path
                    alphabet.add(chr(code_point))
    # 字母表排序
    alphabet = list(alphabet)
    alphabet.sort(key=lambda c: ord(c))
    # 合并设计文件路径组
    design_file_paths_map = {}
    for language_specific in configs.language_specifics:
        design_file_paths = dict(default_design_file_paths)
        if language_specific in special_design_file_paths_map:
            design_file_paths.update(special_design_file_paths_map[language_specific])
        design_file_paths_map[language_specific] = design_file_paths
    return alphabet, design_file_paths_map
