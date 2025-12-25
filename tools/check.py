from tools.configs import options
from tools.services import check_service


def main():
    for font_size in options.font_sizes:
        check_service.check_glyphs(font_size)


if __name__ == '__main__':
    main()
