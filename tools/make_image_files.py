from tools.configs.font import FontConfig
from tools.services import image_service


def main():
    font_configs = FontConfig.load_all()
    for font_config in font_configs.values():
        image_service.make_preview_image(font_config)
    image_service.make_readme_banner(font_configs)
    image_service.make_github_banner(font_configs)
    image_service.make_itch_io_banner(font_configs)
    image_service.make_itch_io_background(font_configs)
    image_service.make_itch_io_cover(font_configs)
    image_service.make_afdian_cover(font_configs)


if __name__ == '__main__':
    main()
