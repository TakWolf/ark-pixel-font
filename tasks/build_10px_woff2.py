import logging

import configs
from services import design_service, font_service, info_service

logging.basicConfig(level=logging.DEBUG)


def main():
    font_config = configs.font_config_map[10]
    design_service.classify_glyph_files(font_config)
    design_service.verify_glyph_files(font_config)
    alphabet, glyph_file_paths_map = design_service.collect_glyph_files(font_config)
    font_service.make_fonts(font_config, alphabet, glyph_file_paths_map, font_formats=['woff2'])
    info_service.make_info_file(font_config, alphabet)
    info_service.make_alphabet_txt_file(font_config, alphabet)


if __name__ == '__main__':
    main()
