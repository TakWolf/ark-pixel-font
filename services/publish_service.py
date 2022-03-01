import logging
import os.path
import shutil
import zipfile

import configs
from configs import workspace_define

logger = logging.getLogger('publish-service')


def make_px_release_zips(font_config):
    for font_format in ['otf', 'woff2', 'ttf']:
        zip_file_output_path = os.path.join(workspace_define.releases_dir, font_config.get_release_zip_file_name(font_format))
        with zipfile.ZipFile(zip_file_output_path, 'w') as zip_file:
            for language_specific in configs.language_specifics:
                font_file_name = font_config.get_output_font_file_name(language_specific, font_format)
                font_file_path = os.path.join(workspace_define.outputs_dir, font_file_name)
                zip_file.write(font_file_path, font_file_name)
            zip_file.write('LICENSE-OFL', 'OFL.txt')
        logger.info(f'make {zip_file_output_path}')


def _copy_file(file_name, from_dir, to_dir):
    from_path = os.path.join(from_dir, file_name)
    to_path = os.path.join(to_dir, file_name)
    shutil.copy(from_path, to_path)
    logger.info(f'copy from {from_path} to {to_path}')


def copy_px_docs_files(font_config):
    file_names = [
        font_config.info_file_name,
        font_config.preview_image_file_name,
    ]
    for file_name in file_names:
        _copy_file(file_name, workspace_define.outputs_dir, workspace_define.docs_dir)


def copy_px_www_files(font_config):
    for language_specific in configs.language_specifics:
        file_name = font_config.get_output_font_file_name(language_specific, 'woff2')
        _copy_file(file_name, workspace_define.outputs_dir, workspace_define.www_dir)
    file_names = [
        font_config.alphabet_html_file_name,
        font_config.demo_html_file_name,
    ]
    for file_name in file_names:
        _copy_file(file_name, workspace_define.outputs_dir, workspace_define.www_dir)


def copy_docs_files():
    _copy_file('itch-io-banner.png', workspace_define.outputs_dir, workspace_define.docs_dir)


def copy_www_files():
    file_names = [
        'index.html',
        'playground.html',
    ]
    for file_name in file_names:
        _copy_file(file_name, workspace_define.outputs_dir, workspace_define.www_dir)
