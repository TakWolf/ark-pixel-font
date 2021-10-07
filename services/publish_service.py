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
            for locale_flavor in configs.locale_flavors:
                font_file_name = font_config.get_output_font_file_name(locale_flavor, font_format)
                font_file_path = os.path.join(workspace_define.outputs_dir, font_file_name)
                zip_file.write(font_file_path, font_file_name)
            zip_file.write('LICENSE-OFL', 'OFL.txt')
        logger.info(f'make {zip_file_output_path}')


def copy_docs_files(font_config):
    for locale_flavor in configs.locale_flavors:
        woff2_file_name = font_config.get_output_font_file_name(locale_flavor, 'woff2')
        woff2_file_path = os.path.join(workspace_define.outputs_dir, woff2_file_name)
        woff2_file_docs_path = os.path.join(workspace_define.docs_dir, woff2_file_name)
        shutil.copy(woff2_file_path, woff2_file_docs_path)
        logger.info(f'copy from {woff2_file_path} to {woff2_file_docs_path}')

    ext_file_names = [
        font_config.info_file_name,
        font_config.preview_image_file_name,
        font_config.alphabet_html_file_name,
        font_config.demo_html_file_name
    ]
    for ext_file_name in ext_file_names:
        ext_file_path = os.path.join(workspace_define.outputs_dir, ext_file_name)
        ext_file_docs_path = os.path.join(workspace_define.docs_dir, ext_file_name)
        shutil.copy(ext_file_path, ext_file_docs_path)
        logger.info(f'copy from {ext_file_path} to {ext_file_docs_path}')
