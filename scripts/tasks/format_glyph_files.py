import logging

from scripts import configs
from scripts.services import font_service

logging.basicConfig(level=logging.DEBUG)


def main():
    for font_config in configs.font_configs:
        font_service.format_glyph_files(font_config)


if __name__ == '__main__':
    main()
