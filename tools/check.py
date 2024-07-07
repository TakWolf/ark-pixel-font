from tools import configs
from tools.configs.font import FontConfig
from tools.services import check_service


def main():
    for font_size in configs.font_sizes:
        font_config = FontConfig.load(font_size)
        check_service.check_font_config(font_config)
        check_service.check_glyph_files(font_config)


if __name__ == '__main__':
    main()
