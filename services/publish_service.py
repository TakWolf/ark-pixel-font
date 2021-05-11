import logging
import zipfile

logger = logging.getLogger('publish-service')


def make_release_zips(font_config):
    for language_flavor_config in font_config.language_flavor_configs.values():
        zip_file_path = language_flavor_config.zip_file_release_path
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.write(language_flavor_config.otf_file_output_path, language_flavor_config.otf_file_name)
            zip_file.write(language_flavor_config.ttf_file_output_path, language_flavor_config.ttf_file_name)
            zip_file.write('LICENSE-OFL', 'OFL.txt')
        logger.info(f'make {zip_file_path}')
