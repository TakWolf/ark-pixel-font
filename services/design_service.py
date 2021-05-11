import logging
import os.path
import shutil
import unicodedata

import configs
from utils import unicode_util, fs_util, glyph_util

logger = logging.getLogger('design-service')


def _parse_design_file_name(design_file_name):
    """
    解析设计文件名称
    :param design_file_name: 设计文件名称，例如：'0030 sc,jp.png'
    :return: uni_hex_name, language_flavor_string
    """
    params = design_file_name.replace('.png', '').split(' ')
    assert 1 <= len(params) <= 2, design_file_name
    uni_hex_name = params[0].lower() if params[0] == 'notdef' else params[0].upper()
    if len(params) >= 2:
        language_flavors = params[1].lower().split(',')
        for language_flavor in language_flavors:
            assert configs.language_flavors.__contains__(language_flavor), design_file_name
    else:
        language_flavors = []
    return uni_hex_name, language_flavors


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
                            uni_hex_name, language_flavors = _parse_design_file_name(design_file_name)
                            if uni_hex_name == 'notdef':
                                design_file_to_dir = design_flavor_dir
                            else:
                                code_point = int(uni_hex_name, 16)
                                _, unicode_block = unicode_util.index_code_point_in_blocks(configs.unicode_blocks, code_point)
                                block_dir_name = f'{unicode_block.begin:04X}-{unicode_block.end:04X} {unicode_block.name}'
                                design_file_to_dir = os.path.join(design_flavor_dir, block_dir_name)
                            fs_util.make_dirs_if_not_exists(design_file_to_dir)
                            design_file_name = f'{uni_hex_name}{" " if len(language_flavors) > 0 else ""}{",".join(language_flavors)}.png'
                            design_file_to_path = os.path.join(design_file_to_dir, design_file_name)
                            shutil.move(design_file_from_path, design_file_to_path)
                            logger.info(f'classify design file: {design_file_to_path}')
                shutil.rmtree(design_flavor_tmp_dir)


def verify_design_files(font_config):
    """
    校验设计文件，并生成 SVG
    """
    for design_flavor_name in ['final', 'draft']:
        design_flavor_dir = os.path.join(font_config.design_dir, design_flavor_name)
        if os.path.isdir(design_flavor_dir):
            for design_file_parent_dir, _, design_file_names in os.walk(design_flavor_dir):
                svg_file_parent_dir = design_file_parent_dir.replace(font_config.design_dir, font_config.svg_outputs_dir)
                fs_util.make_dirs_if_not_exists(svg_file_parent_dir)
                for design_file_name in design_file_names:
                    if design_file_name.endswith('.png'):
                        design_file_path = os.path.join(design_file_parent_dir, design_file_name)
                        design_data, width, height = glyph_util.load_design_data_from_png(design_file_path)
                        uni_hex_name, _ = _parse_design_file_name(design_file_name)

                        # 校验设计文件的半角和全角尺寸
                        if uni_hex_name == 'notdef':
                            east_asian_width_status = 'H'
                        else:
                            code_point = int(uni_hex_name, 16)
                            c = chr(code_point)
                            east_asian_width_status = unicodedata.east_asian_width(c)
                        if east_asian_width_status == 'H' or east_asian_width_status == 'Na':
                            assert width * 2 == height, design_file_path
                        elif east_asian_width_status == 'F' or east_asian_width_status == 'W':
                            assert width == height, design_file_path
                        else: # 'A' or 'N'
                            assert width * 2 == height or width == height, design_file_path
                        assert font_config.px == height, design_file_path

                        # 格式化设计文件
                        glyph_util.save_design_data_to_png(design_data, design_file_path)
                        logger.info(f'format design file: {design_file_path}')

                        # 生成 SVG
                        outlines = glyph_util.get_outlines_from_design_data(design_data, font_config.em_dot_size)
                        svg_file_path = os.path.join(svg_file_parent_dir, design_file_name.replace('.png', '.svg'))
                        glyph_util.save_outlines_to_svg(outlines, width * font_config.em_dot_size, height * font_config.em_dot_size, svg_file_path)
                        logger.info(f'make svg file: {svg_file_path}')
