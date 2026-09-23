from tools.config import options
from tools.services import format_service


def main() -> None:
    for font_size in options.FONT_SIZES:
        format_service.normalize_cmap_glyphs(font_size)
        format_service.normalize_named_glyphs(font_size)

    format_service.format_glyphs()
    format_service.format_mappings()


if __name__ == '__main__':
    main()
