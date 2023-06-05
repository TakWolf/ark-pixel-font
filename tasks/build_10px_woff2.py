import logging

import configs
from services import font_service, info_service

logging.basicConfig(level=logging.DEBUG)


def main():
    font_config = configs.font_size_to_config[10]
    font_service.format_glyph_files(font_config)
    context = font_service.collect_glyph_files(font_config)
    for width_mode in configs.width_modes:
        font_service.make_font_files(font_config, context, width_mode, font_formats=['woff2'])
        info_service.make_info_file(font_config, context, width_mode)
        info_service.make_alphabet_txt_file(font_config, context, width_mode)


if __name__ == '__main__':
    main()
