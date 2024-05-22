import datetime
import logging
import os
import shutil
import zipfile

import git

from scripts import configs
from scripts.configs import path_define, FontConfig, GitDeployConfig

logger = logging.getLogger('publish_service')


def make_release_zips(font_config: FontConfig, width_mode: str, special_folder: bool = False):
    if special_folder:
        releases_dir = f'{path_define.releases_dir}-{font_config.font_size}px-{width_mode}'
    else:
        releases_dir = path_define.releases_dir
    os.makedirs(releases_dir, exist_ok=True)

    for font_format in configs.font_formats:
        file_path = os.path.join(releases_dir, font_config.get_release_zip_file_name(width_mode, font_format))
        with zipfile.ZipFile(file_path, 'w') as file:
            file.write(os.path.join(path_define.project_root_dir, 'LICENSE-OFL'), 'OFL.txt')
            for language_flavor in configs.language_flavors:
                font_file_name = font_config.get_font_file_name(width_mode, language_flavor, font_format)
                font_file_path = os.path.join(path_define.outputs_dir, font_file_name)
                file.write(font_file_path, font_file_name)
        logger.info("Make release zip: '%s'", file_path)

    for font_format in configs.font_collection_formats:
        file_path = os.path.join(releases_dir, font_config.get_release_zip_file_name(width_mode, font_format))
        with zipfile.ZipFile(file_path, 'w') as file:
            file.write(os.path.join(path_define.project_root_dir, 'LICENSE-OFL'), 'OFL.txt')
            font_file_name = font_config.get_font_collection_file_name(width_mode, font_format)
            font_file_path = os.path.join(path_define.outputs_dir, font_file_name)
            file.write(font_file_path, font_file_name)
        logger.info("Make release zip: '%s'", file_path)


def update_docs():
    os.makedirs(path_define.docs_dir, exist_ok=True)

    shutil.copyfile(os.path.join(path_define.outputs_dir, 'readme-banner.png'), os.path.join(path_define.docs_dir, 'readme-banner.png'))
    for font_config in configs.font_configs.values():
        shutil.copyfile(os.path.join(path_define.outputs_dir, font_config.preview_image_file_name), os.path.join(path_define.docs_dir, font_config.preview_image_file_name))
        for width_mode in configs.width_modes:
            info_file_name = font_config.get_info_file_name(width_mode)
            shutil.copyfile(os.path.join(path_define.outputs_dir, info_file_name), os.path.join(path_define.docs_dir, info_file_name))


def update_www():
    os.makedirs(path_define.www_dir, exist_ok=True)
    for name in os.listdir(path_define.www_dir):
        if name == '.git':
            continue
        path = os.path.join(path_define.www_dir, name)
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    for name in os.listdir(path_define.www_static_dir):
        path_from = os.path.join(path_define.www_static_dir, name)
        path_to = os.path.join(path_define.www_dir, name)
        if os.path.isfile(path_from):
            shutil.copyfile(path_from, path_to)
        elif os.path.isdir(path_from):
            shutil.copytree(path_from, path_to)

    shutil.copyfile(os.path.join(path_define.outputs_dir, 'index.html'), os.path.join(path_define.www_dir, 'index.html'))
    shutil.copyfile(os.path.join(path_define.outputs_dir, 'playground.html'), os.path.join(path_define.www_dir, 'playground.html'))
    for font_config in configs.font_configs.values():
        shutil.copyfile(os.path.join(path_define.outputs_dir, font_config.demo_html_file_name), os.path.join(path_define.www_dir, font_config.demo_html_file_name))
        for width_mode in configs.width_modes:
            alphabet_html_file_name = font_config.get_alphabet_html_file_name(width_mode)
            shutil.copyfile(os.path.join(path_define.outputs_dir, alphabet_html_file_name), os.path.join(path_define.www_dir, alphabet_html_file_name))
            for language_flavor in configs.language_flavors:
                font_file_name = font_config.get_font_file_name(width_mode, language_flavor, 'woff2')
                shutil.copyfile(os.path.join(path_define.outputs_dir, font_file_name), os.path.join(path_define.www_dir, font_file_name))


def deploy_www(config: GitDeployConfig):
    if os.path.exists(os.path.join(path_define.www_dir, '.git')):
        repo = git.Repo(path_define.www_dir)
    else:
        repo = git.Repo.init(path_define.www_dir)

    if config.remote_name in repo.git.remote().splitlines():
        repo.git.remote('rm', config.remote_name)
    repo.git.remote('add', config.remote_name, config.url)

    if len(repo.git.status('-s').splitlines()) > 0:
        repo.git.add(all=True)
        repo.git.commit(m=f'deployed at {datetime.datetime.now(datetime.UTC).isoformat()}')

    current_branch_name = repo.git.branch(show_current=True)
    repo.git.push(config.remote_name, f'{current_branch_name}:{config.branch_name}', '-f')
