import logging
import zipfile

logger = logging.getLogger('publish-service')


def make_release_zips(font_config):
    otf_zip_file_path = font_config.otf_zip_file_release_path
    ttf_zip_file_path = font_config.ttf_zip_file_release_path
    with zipfile.ZipFile(otf_zip_file_path, 'w') as otf_zip_file, zipfile.ZipFile(ttf_zip_file_path, 'w') as ttf_zip_file:
        for locale_flavor_config in font_config.locale_flavor_configs:
            otf_zip_file.write(locale_flavor_config.otf_file_output_path, locale_flavor_config.otf_file_name)
            ttf_zip_file.write(locale_flavor_config.ttf_file_output_path, locale_flavor_config.ttf_file_name)
        otf_zip_file.write('LICENSE-OFL', 'OFL.txt')
        ttf_zip_file.write('LICENSE-OFL', 'OFL.txt')
    logger.info(f'make {otf_zip_file_path}')
    logger.info(f'make {ttf_zip_file_path}')
