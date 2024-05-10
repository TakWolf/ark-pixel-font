import datetime
import logging
import os
import zipfile

import git

from scripts import configs
from scripts.configs import path_define, FontConfig, GitDeployConfig
from scripts.utils import fs_util

logger = logging.getLogger('publish_service')


def make_release_zips(font_config: FontConfig, width_mode: str, special_folder: bool = False):
    if special_folder:
        releases_dir = f'{path_define.releases_dir}-{font_config.font_size}px-{width_mode}'
    else:
        releases_dir = path_define.releases_dir
    fs_util.make_dir(releases_dir)

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
    fs_util.make_dir(path_define.docs_dir)

    fs_util.copy_the_file('readme-banner.png', path_define.outputs_dir, path_define.docs_dir)
    for font_config in configs.font_configs.values():
        fs_util.copy_the_file(font_config.preview_image_file_name, path_define.outputs_dir, path_define.docs_dir)
        for width_mode in configs.width_modes:
            fs_util.copy_the_file(font_config.get_info_file_name(width_mode), path_define.outputs_dir, path_define.docs_dir)


def update_www():
    fs_util.make_dir(path_define.www_dir)
    for name in os.listdir(path_define.www_dir):
        if name == '.git':
            continue
        fs_util.delete_item(os.path.join(path_define.www_dir, name))

    for name in os.listdir(path_define.www_static_dir):
        fs_util.copy_the_item(name, path_define.www_static_dir, path_define.www_dir)

    fs_util.copy_the_file('index.html', path_define.outputs_dir, path_define.www_dir)
    fs_util.copy_the_file('playground.html', path_define.outputs_dir, path_define.www_dir)
    for font_config in configs.font_configs.values():
        fs_util.copy_the_file(font_config.demo_html_file_name, path_define.outputs_dir, path_define.www_dir)
        for width_mode in configs.width_modes:
            fs_util.copy_the_file(font_config.get_alphabet_html_file_name(width_mode), path_define.outputs_dir, path_define.www_dir)
            for language_flavor in configs.language_flavors:
                fs_util.copy_the_file(font_config.get_font_file_name(width_mode, language_flavor, 'woff2'), path_define.outputs_dir, path_define.www_dir)


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
