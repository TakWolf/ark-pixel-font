import logging

import configs
from services import info_service, template_service

logging.basicConfig(level=logging.DEBUG)


def main():
    for font_config in configs.font_configs:
        alphabet_group = {}
        for width_mode in configs.width_modes:
            alphabet = info_service.read_alphabet_txt_file(font_config, width_mode)
            alphabet_group[width_mode] = alphabet
            template_service.make_alphabet_html_file(font_config, width_mode, alphabet)
        template_service.make_demo_html_file(font_config, alphabet_group)
    template_service.make_index_html_file()
    template_service.make_playground_html_file()


if __name__ == '__main__':
    main()
