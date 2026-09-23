from collections.abc import Sequence
from zipfile import ZipFile

from loguru import logger

from tools.config import project
from tools.configs import path_define, options
from tools.configs.options import FontSize, WidthMode, FontFormat


def make_release_zips(font_size: FontSize, width_mode: WidthMode, font_formats: Sequence[FontFormat]) -> None:
    path_define.RELEASES_DIR.mkdir(parents=True, exist_ok=True)

    for font_format in font_formats:
        zip_file_path = path_define.RELEASES_DIR.joinpath(f'{project.FILE_NAME_PREFIX}-font-{font_size}px-{width_mode}-{font_format}-v{project.VERSION}.zip')
        with ZipFile(zip_file_path, 'w') as file:
            file.write(path_define.PROJECT_ROOT_DIR.joinpath('LICENSE-OFL'), 'OFL.txt')

            for language_flavor in options.LANGUAGE_FLAVORS:
                font_file_path = path_define.OUTPUTS_DIR.joinpath(f'{project.FILE_NAME_PREFIX}-{font_size}px-{width_mode}-{language_flavor}.{font_format}')
                file.write(font_file_path, font_file_path.name)
        logger.info("Make release zip: '{}'", zip_file_path)


def update_docs() -> None:
    path_define.DOCS_DIR.mkdir(parents=True, exist_ok=True)

    for path_from in sorted((
            *path_define.OUTPUTS_DIR.glob('info-*px-*.md'),
            *path_define.OUTPUTS_DIR.glob('preview-*px.png'),
            *path_define.OUTPUTS_DIR.glob('readme-banner.png'),
    )):
        if not path_from.is_file():
            continue

        path_to = path_from.copy_into(path_define.DOCS_DIR)
        logger.info("Copy file: '{}' -> '{}'", path_from, path_to)
