from tools.configs import options
from tools.services import format_service


def main():
    for font_size in options.font_sizes:
        format_service.format_glyphs(font_size)

    format_service.format_mappings()


if __name__ == '__main__':
    main()
