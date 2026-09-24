from tools.config import path_define, options
from tools.config.font import FontConfig
from tools.services import template_service


def main() -> None:
    for font_size in options.FONT_SIZES:
        font_config = FontConfig.load(font_size)

        alphabets = {}
        for width_mode in options.WIDTH_MODES:
            alphabet = list(path_define.OUTPUTS_DIR.joinpath(f'alphabet-{font_size}px-{width_mode}.txt').read_text('utf-8'))
            alphabets[width_mode] = alphabet

            template_service.make_alphabet_html(font_config, width_mode, alphabets[width_mode])
        template_service.make_demo_html(font_config, alphabets)

    template_service.make_index_html()
    template_service.make_playground_html()


if __name__ == '__main__':
    main()
