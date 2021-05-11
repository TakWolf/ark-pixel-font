import logging
import os.path
import shutil

import configs
from utils import unicode_util

logger = logging.getLogger('design-service')


def _parse_design_file_name(design_file_name):
    """
    解析设计文件名称
    :param design_file_name: 设计文件名称，例如：'0030 sc,jp.png'
    :return: uni_hex_name, language_flavor_string
    """
    params = design_file_name.replace('.png', '').split(' ')
    assert 1 <= len(params) <= 2
    uni_hex_name = params[0].lower() if params[0] == 'notdef' else params[0].upper()
    language_flavor_string = params[1].lower() if len(params) >= 2 else ''
    return uni_hex_name, language_flavor_string


def classify_design_files(font_config):
    """
    按照 Unicode 区块分类设计文件
    """
    if os.path.isdir(font_config.design_dir):
        for design_flavor_name in os.listdir(font_config.design_dir):
            design_flavor_dir = os.path.join(font_config.design_dir, design_flavor_name)
            if os.path.isdir(design_flavor_dir):
                design_flavor_tmp_dir = os.path.join(font_config.design_dir, f'{design_flavor_name}.tmp')
                os.rename(design_flavor_dir, design_flavor_tmp_dir)
                os.mkdir(design_flavor_dir)
                for design_file_parent_dir, _, design_file_names in os.walk(design_flavor_tmp_dir):
                    for design_file_name in design_file_names:
                        if design_file_name.endswith('.png'):
                            design_file_from_path = os.path.join(design_file_parent_dir, design_file_name)
                            uni_hex_name, language_flavor_string = _parse_design_file_name(design_file_name)
                            if uni_hex_name == 'notdef':
                                design_file_to_dir = design_flavor_dir
                            else:
                                code_point = int(uni_hex_name, 16)
                                _, unicode_block = unicode_util.index_code_point_in_blocks(configs.unicode_blocks, code_point)
                                block_dir_name = f'{unicode_block.begin:04X}-{unicode_block.end:04X} {unicode_block.name}'
                                design_file_to_dir = os.path.join(design_flavor_dir, block_dir_name)
                            if not os.path.exists(design_file_to_dir):
                                os.mkdir(design_file_to_dir)
                            design_file_name = f'{uni_hex_name}{"" if language_flavor_string == "" else " "}{language_flavor_string}.png'
                            design_file_to_path = os.path.join(design_file_to_dir, design_file_name)
                            shutil.move(design_file_from_path, design_file_to_path)
                            logger.info(f'classify design file: {design_file_to_path}')
                shutil.rmtree(design_flavor_tmp_dir)
