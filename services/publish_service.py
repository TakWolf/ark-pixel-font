import datetime
import logging
import os
import shutil
import zipfile

import git

import configs
from configs import path_define
from utils import fs_util

logger = logging.getLogger('publish-service')


def make_release_zips(font_config, width_mode):
    fs_util.make_dirs(path_define.releases_dir)
    for font_format in configs.font_formats:
        file_path = os.path.join(path_define.releases_dir, font_config.get_release_zip_file_name(width_mode, font_format))
        with zipfile.ZipFile(file_path, 'w') as file:
            file.write('LICENSE-OFL', 'OFL.txt')
            for language_flavor in configs.language_flavors:
                font_file_name = font_config.get_font_file_name(width_mode, language_flavor, font_format)
                font_file_path = os.path.join(path_define.outputs_dir, font_file_name)
                file.write(font_file_path, font_file_name)
        logger.info(f'make {file_path}')


def _copy_file(file_name, from_dir, to_dir):
    from_path = os.path.join(from_dir, file_name)
    to_path = os.path.join(to_dir, file_name)
    shutil.copyfile(from_path, to_path)
    logger.info(f'copy from {from_path} to {to_path}')


def update_docs():
    fs_util.make_dirs(path_define.docs_dir)
    _copy_file('readme-banner.png', path_define.outputs_dir, path_define.docs_dir)
    for font_config in configs.font_configs:
        _copy_file(font_config.preview_image_file_name, path_define.outputs_dir, path_define.docs_dir)
        for width_mode in configs.width_modes:
            _copy_file(font_config.get_info_file_name(width_mode), path_define.outputs_dir, path_define.docs_dir)


def update_www():
    fs_util.delete_dir(path_define.www_dir)
    shutil.copytree(path_define.www_static_dir, path_define.www_dir)
    _copy_file('index.html', path_define.outputs_dir, path_define.www_dir)
    _copy_file('playground.html', path_define.outputs_dir, path_define.www_dir)
    for font_config in configs.font_configs:
        _copy_file(font_config.demo_html_file_name, path_define.outputs_dir, path_define.www_dir)
        for width_mode in configs.width_modes:
            _copy_file(font_config.get_alphabet_html_file_name(width_mode), path_define.outputs_dir, path_define.www_dir)
            for language_flavor in configs.language_flavors:
                _copy_file(font_config.get_font_file_name(width_mode, language_flavor, 'woff2'), path_define.outputs_dir, path_define.www_dir)


def deploy_www():
    repo = git.Repo.init(path_define.www_dir)
    repo.git.add(all=True)
    repo.git.commit(m=f'deployed at {datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()}')
    current_branch_name = repo.git.branch(show_current=True)
    for git_deploy_config in configs.git_deploy_configs:
        repo.git.remote('add', git_deploy_config.remote_name, git_deploy_config.url)
        repo.git.push(git_deploy_config.remote_name, f'{current_branch_name}:{git_deploy_config.branch_name}', '-f')
