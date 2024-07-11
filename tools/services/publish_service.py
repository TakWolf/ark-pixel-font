import re
import shutil
import zipfile

from loguru import logger

from tools import configs
from tools.configs import path_define, FontSize, WidthMode, FontFormat, FontCollectionFormat


def make_release_zip(font_size: FontSize, width_mode: WidthMode, font_format: FontFormat | FontCollectionFormat):
    path_define.releases_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.releases_dir.joinpath(f'ark-pixel-font-{font_size}px-{width_mode}-{font_format}-v{configs.version}.zip')
    with zipfile.ZipFile(file_path, 'w') as file:
        file.write(path_define.project_root_dir.joinpath('LICENSE-OFL'), 'OFL.txt')
        if font_format in configs.font_formats:
            for language_flavor in configs.language_flavors:
                font_file_name = f'ark-pixel-{font_size}px-{width_mode}-{language_flavor}.{font_format}'
                file.write(path_define.outputs_dir.joinpath(font_file_name), font_file_name)
        else:
            font_file_name = f'ark-pixel-{font_size}px-{width_mode}.{font_format}'
            file.write(path_define.outputs_dir.joinpath(font_file_name), font_file_name)
    logger.info("Make release zip: '{}'", file_path)


def update_docs():
    for file_dir, _, file_names in path_define.outputs_dir.walk():
        for file_name in file_names:
            if re.match(r'font-info-.*px-.*\.md|preview-.*px\.png', file_name) is None and file_name != 'readme-banner.png':
                continue
            path_from = file_dir.joinpath(file_name)
            path_to = path_define.docs_dir.joinpath(path_from.relative_to(path_define.outputs_dir))
            path_to.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path_from, path_to)
            logger.info("Copy file: '{}' -> '{}'", path_from, path_to)
