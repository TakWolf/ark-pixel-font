import logging

from scripts import configs
from scripts.services import font_service, template_service

logging.basicConfig(level=logging.DEBUG)


def main():
    for font_config in configs.font_configs:
        context = font_service.collect_glyph_files(font_config)
        for width_mode in configs.width_modes:
            template_service.make_alphabet_html_file(font_config, context, width_mode)
        template_service.make_demo_html_file(font_config, context)
    template_service.make_index_html_file()
    template_service.make_playground_html_file()


if __name__ == '__main__':
    main()
