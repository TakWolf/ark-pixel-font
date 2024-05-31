import datetime
import logging
import os
import re
import shutil
import zipfile

import git

from scripts import configs
from scripts.configs import path_define, FontConfig, GitDeployConfig

logger = logging.getLogger('publish_service')


def make_release_zips(font_config: FontConfig, width_mode: str):
    path_define.releases_dir.mkdir(parents=True, exist_ok=True)

    for font_format in configs.font_formats:
        file_path = path_define.releases_dir.joinpath(font_config.get_release_zip_file_name(width_mode, font_format))
        with zipfile.ZipFile(file_path, 'w') as file:
            file.write(path_define.project_root_dir.joinpath('LICENSE-OFL'), 'OFL.txt')
            for language_flavor in configs.language_flavors:
                font_file_name = font_config.get_font_file_name(width_mode, language_flavor, font_format)
                font_file_path = path_define.outputs_dir.joinpath(font_file_name)
                file.write(font_file_path, font_file_name)
        logger.info("Make release zip: '%s'", file_path)

    for font_format in configs.font_collection_formats:
        file_path = path_define.releases_dir.joinpath(font_config.get_release_zip_file_name(width_mode, font_format))
        with zipfile.ZipFile(file_path, 'w') as file:
            file.write(path_define.project_root_dir.joinpath('LICENSE-OFL'), 'OFL.txt')
            font_file_name = font_config.get_font_collection_file_name(width_mode, font_format)
            font_file_path = path_define.outputs_dir.joinpath(font_file_name)
            file.write(font_file_path, font_file_name)
        logger.info("Make release zip: '%s'", file_path)


def update_docs():
    for file_dir, _, file_names in path_define.outputs_dir.walk():
        for file_name in file_names:
            if re.match(r'font-info-.*px-.*\.md|preview-.*px\.png', file_name) is None and file_name != 'readme-banner.png':
                continue
            path_from = file_dir.joinpath(file_name)
            path_to = path_define.docs_dir.joinpath(path_from.relative_to(path_define.outputs_dir))
            path_to.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path_from, path_to)
            logger.info("Copy file: '%s' -> '%s'", path_from, path_to)


def update_www():
    if path_define.www_dir.exists():
        for path in path_define.www_dir.iterdir():
            if path.name == '.git':
                continue
            if path.is_file():
                os.remove(path)
            elif path.is_dir():
                shutil.rmtree(path)

    for file_dir, _, file_names in path_define.www_static_dir.walk():
        for file_name in file_names:
            if file_name == '.DS_Store':
                continue
            path_from = file_dir.joinpath(file_name)
            path_to = path_define.www_dir.joinpath(path_from.relative_to(path_define.www_static_dir))
            path_to.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path_from, path_to)
            logger.info("Copy file: '%s' -> '%s'", path_from, path_to)

    for file_dir, _, file_names in path_define.outputs_dir.walk():
        for file_name in file_names:
            if not file_name.endswith(('.html', '.woff2')):
                continue
            path_from = file_dir.joinpath(file_name)
            path_to = path_define.www_dir.joinpath(path_from.relative_to(path_define.outputs_dir))
            path_to.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path_from, path_to)
            logger.info("Copy file: '%s' -> '%s'", path_from, path_to)


def deploy_www(config: GitDeployConfig):
    if path_define.www_dir.joinpath('.git').exists():
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
