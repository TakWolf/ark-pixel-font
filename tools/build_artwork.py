from tools.config import path_define, options
from tools.config.font import FontConfig
from tools.services import image_service


def main() -> None:
    for font_size in options.FONT_SIZES:
        font_config = FontConfig.load(font_size)

        image_service.make_preview_image(font_config)

        if font_size == 12:
            alphabet = list(path_define.OUTPUTS_DIR.joinpath('alphabet-12px-proportional.txt').read_text('utf-8'))

            image_service.make_readme_banner(font_config, alphabet)
            image_service.make_github_banner(font_config, alphabet)
            image_service.make_itch_io_banner(font_config, alphabet)
            image_service.make_itch_io_cover(font_config)
            image_service.make_afdian_cover(font_config)


if __name__ == '__main__':
    main()
