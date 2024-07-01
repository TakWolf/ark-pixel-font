from tools import configs
from tools.configs.font import FontConfig
from tools.services import template_service
from tools.services.font_service import DesignContext, FontContext


def main():
    font_configs = FontConfig.load_all()
    for font_config in font_configs.values():
        design_context = DesignContext.load(font_config)
        design_context.standardized()
        for width_mode in configs.width_modes:
            font_context = FontContext(design_context, width_mode)
            font_context.make_fonts('woff2')
            template_service.make_alphabet_html(design_context, width_mode)
        template_service.make_demo_html(design_context)
    template_service.make_index_html(font_configs)
    template_service.make_playground_html(font_configs)


if __name__ == '__main__':
    main()
