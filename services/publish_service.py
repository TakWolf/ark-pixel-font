import logging
import zipfile

logger = logging.getLogger('publish-service')


def _make_otf_release_zip(font_config):
    with zipfile.ZipFile(font_config.otf_zip_file_release_path, 'w') as zip_file:
        for locale_flavor_config in font_config.locale_flavor_configs:
            zip_file.write(locale_flavor_config.otf_file_output_path, locale_flavor_config.otf_file_name)
        zip_file.write('LICENSE-OFL', 'OFL.txt')
    logger.info(f'make {font_config.otf_zip_file_release_path}')


def _make_woff2_release_zip(font_config):
    with zipfile.ZipFile(font_config.woff2_zip_file_release_path, 'w') as zip_file:
        for locale_flavor_config in font_config.locale_flavor_configs:
            zip_file.write(locale_flavor_config.woff2_file_output_path, locale_flavor_config.woff2_file_name)
        zip_file.write('LICENSE-OFL', 'OFL.txt')
    logger.info(f'make {font_config.woff2_zip_file_release_path}')


def _make_ttf_release_zip(font_config):
    with zipfile.ZipFile(font_config.ttf_zip_file_release_path, 'w') as zip_file:
        for locale_flavor_config in font_config.locale_flavor_configs:
            zip_file.write(locale_flavor_config.ttf_file_output_path, locale_flavor_config.ttf_file_name)
        zip_file.write('LICENSE-OFL', 'OFL.txt')
    logger.info(f'make {font_config.ttf_zip_file_release_path}')


def make_release_zips(font_config):
    _make_otf_release_zip(font_config)
    _make_woff2_release_zip(font_config)
    _make_ttf_release_zip(font_config)
