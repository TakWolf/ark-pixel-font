import logging
import os.path
import shutil
import zipfile

import configs
from configs import workspace_define

logger = logging.getLogger('publish-service')


def make_release_zips(font_config):
    for font_format in ['otf', 'woff2', 'ttf']:
        zip_file_output_path = os.path.join(workspace_define.releases_dir, font_config.get_release_zip_file_name(font_format))
        with zipfile.ZipFile(zip_file_output_path, 'w') as zip_file:
            for language_specific in configs.language_specifics:
                font_file_name = font_config.get_output_font_file_name(language_specific, font_format)
                font_file_path = os.path.join(workspace_define.outputs_dir, font_file_name)
                zip_file.write(font_file_path, font_file_name)
            zip_file.write('LICENSE-OFL', 'OFL.txt')
        logger.info(f'make {zip_file_output_path}')


def copy_font_related_files(font_config):
    for language_specific in configs.language_specifics:
        file_name = font_config.get_output_font_file_name(language_specific, 'woff2')
        file_path = os.path.join(workspace_define.outputs_dir, file_name)
        file_docs_path = os.path.join(workspace_define.docs_dir, file_name)
        shutil.copy(file_path, file_docs_path)
        logger.info(f'copy from {file_path} to {file_docs_path}')

    docs_ext_file_names = [
        font_config.info_file_name,
        font_config.preview_image_file_name,
        font_config.alphabet_html_file_name,
        font_config.demo_html_file_name
    ]
    for file_name in docs_ext_file_names:
        file_path = os.path.join(workspace_define.outputs_dir, file_name)
        file_docs_path = os.path.join(workspace_define.docs_dir, file_name)
        shutil.copy(file_path, file_docs_path)
        logger.info(f'copy from {file_path} to {file_docs_path}')


def copy_other_files():
    docs_ext_file_names = [
        'index.html',
        'playground.html',
        'itch-io-banner.png'
    ]
    for file_name in docs_ext_file_names:
        file_path = os.path.join(workspace_define.outputs_dir, file_name)
        file_docs_path = os.path.join(workspace_define.docs_dir, file_name)
        shutil.copy(file_path, file_docs_path)
        logger.info(f'copy from {file_path} to {file_docs_path}')
