import logging

import configs
from services import font_service, info_service

logging.basicConfig(level=logging.DEBUG)


def main():
    font_config = configs.font_size_to_config[12]
    font_service.classify_glyph_files(font_config)
    font_service.verify_glyph_files(font_config)
    alphabet_group, glyph_file_paths_map_group = font_service.collect_glyph_files(font_config)
    for width_mode in configs.width_modes:
        alphabet = alphabet_group[width_mode]
        glyph_file_paths_map = glyph_file_paths_map_group[width_mode]
        font_service.make_font_files(font_config, width_mode, alphabet, glyph_file_paths_map, font_formats=['woff2'])
        info_service.make_info_file(font_config, width_mode, alphabet)
        info_service.make_alphabet_txt_file(font_config, width_mode, alphabet)


if __name__ == '__main__':
    main()
