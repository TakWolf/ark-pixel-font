from tools import configs
from tools.configs.font import FontConfig
from tools.services import template_service
from tools.services.font_service import DesignContext


def main():
    font_configs = {font_size: FontConfig.load(font_size) for font_size in configs.font_sizes}
    for font_config in font_configs.values():
        design_context = DesignContext.load(font_config)
        for width_mode in configs.width_modes:
            design_context.make_fonts(width_mode, 'woff2')
            template_service.make_alphabet_html(design_context, width_mode)
        template_service.make_demo_html(design_context)
    template_service.make_index_html(font_configs)
    template_service.make_playground_html(font_configs)


if __name__ == '__main__':
    main()
