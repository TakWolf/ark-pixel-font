import re
from zipfile import ZipFile

from loguru import logger

from tools import configs
from tools.configs import path_define, options
from tools.configs.options import FontSize, WidthMode, FontFormat


def make_release_zips(font_size: FontSize, width_mode: WidthMode, font_formats: list[FontFormat]) -> None:
    path_define.RELEASES_DIR.mkdir(parents=True, exist_ok=True)

    for font_format in font_formats:
        file_path = path_define.RELEASES_DIR.joinpath(f'ark-pixel-font-{font_size}px-{width_mode}-{font_format}-v{configs.VERSION}.zip')
        with ZipFile(file_path, 'w') as file:
            file.write(path_define.PROJECT_ROOT_DIR.joinpath('LICENSE-OFL'), 'OFL.txt')

            for language_flavor in options.LANGUAGE_FLAVORS:
                font_file_name = f'ark-pixel-{font_size}px-{width_mode}-{language_flavor}.{font_format}'
                file.write(path_define.OUTPUTS_DIR.joinpath(font_file_name), font_file_name)
        logger.info("Make release zip: '{}'", file_path)


def update_docs() -> None:
    path_define.DOCS_DIR.mkdir(parents=True, exist_ok=True)

    regex_file_name = re.compile(r'^(info-.*px-.*\.md|preview-.*px\.png)$')
    for path_from in path_define.OUTPUTS_DIR.iterdir():
        if regex_file_name.match(path_from.name) is None and path_from.name != 'readme-banner.png':
            continue
        path_to = path_from.copy_into(path_define.DOCS_DIR)
        logger.info("Copy file: '{}' -> '{}'", path_from, path_to)
