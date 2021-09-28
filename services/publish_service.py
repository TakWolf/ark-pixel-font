import logging
import os.path
import shutil
import zipfile

import configs
from configs import workspace_define

logger = logging.getLogger('publish-service')


def _make_otf_release_zip(font_config):
    file_output_path = os.path.join(workspace_define.releases_dir, font_config.get_release_zip_file_name('otf'))
    with zipfile.ZipFile(file_output_path, 'w') as zip_file:
        for locale_flavor in configs.locale_flavors:
            otf_file_name = font_config.get_output_font_file_name(locale_flavor, 'otf')
            otf_file_path = os.path.join(workspace_define.outputs_dir, otf_file_name)
            zip_file.write(otf_file_path, otf_file_name)
        zip_file.write('LICENSE-OFL', 'OFL.txt')
    logger.info(f'make {file_output_path}')


def _make_woff2_release_zip(font_config):
    file_output_path = os.path.join(workspace_define.releases_dir, font_config.get_release_zip_file_name('woff2'))
    with zipfile.ZipFile(file_output_path, 'w') as zip_file:
        for locale_flavor in configs.locale_flavors:
            woff2_file_name = font_config.get_output_font_file_name(locale_flavor, 'woff2')
            woff2_file_path = os.path.join(workspace_define.outputs_dir, woff2_file_name)
            zip_file.write(woff2_file_path, woff2_file_name)
        zip_file.write('LICENSE-OFL', 'OFL.txt')
    logger.info(f'make {file_output_path}')


def _make_ttf_release_zip(font_config):
    file_output_path = os.path.join(workspace_define.releases_dir, font_config.get_release_zip_file_name('ttf'))
    with zipfile.ZipFile(file_output_path, 'w') as zip_file:
        for locale_flavor in configs.locale_flavors:
            ttf_file_name = font_config.get_output_font_file_name(locale_flavor, 'ttf')
            ttf_file_path = os.path.join(workspace_define.outputs_dir, ttf_file_name)
            zip_file.write(ttf_file_path, ttf_file_name)
        zip_file.write('LICENSE-OFL', 'OFL.txt')
    logger.info(f'make {file_output_path}')


def make_release_zips(font_config):
    _make_otf_release_zip(font_config)
    _make_woff2_release_zip(font_config)
    _make_ttf_release_zip(font_config)


def copy_docs_files(font_config):
    for locale_flavor in configs.locale_flavors:
        woff2_file_name = font_config.get_output_font_file_name(locale_flavor, 'woff2')
        woff2_file_path = os.path.join(workspace_define.outputs_dir, woff2_file_name)
        woff2_file_docs_path = os.path.join(workspace_define.docs_dir, woff2_file_name)
        shutil.copy(woff2_file_path, woff2_file_docs_path)
        logger.info(f'copy from {woff2_file_path} to {woff2_file_docs_path}')

    info_file_path = os.path.join(workspace_define.outputs_dir, font_config.info_file_name)
    info_file_docs_path = os.path.join(workspace_define.docs_dir, font_config.info_file_name)
    shutil.copy(info_file_path, info_file_docs_path)
    logger.info(f'copy from {info_file_path} to {info_file_docs_path}')

    preview_image_file_path = os.path.join(workspace_define.outputs_dir, font_config.preview_image_file_name)
    preview_image_file_docs_path = os.path.join(workspace_define.docs_dir, font_config.preview_image_file_name)
    shutil.copy(preview_image_file_path, preview_image_file_docs_path)
    logger.info(f'copy from {preview_image_file_path} to {preview_image_file_docs_path}')

    alphabet_html_file_path = os.path.join(workspace_define.outputs_dir, font_config.alphabet_html_file_name)
    alphabet_html_file_docs_path = os.path.join(workspace_define.docs_dir, font_config.alphabet_html_file_name)
    shutil.copy(alphabet_html_file_path, alphabet_html_file_docs_path)
    logger.info(f'copy from {alphabet_html_file_path} to {alphabet_html_file_docs_path}')

    demo_html_file_path = os.path.join(workspace_define.outputs_dir, font_config.demo_html_file_name)
    demo_html_file_docs_path = os.path.join(workspace_define.docs_dir, font_config.demo_html_file_name)
    shutil.copy(demo_html_file_path, demo_html_file_docs_path)
    logger.info(f'copy from {demo_html_file_path} to {demo_html_file_docs_path}')
