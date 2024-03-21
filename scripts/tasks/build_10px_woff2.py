from scripts import configs
from scripts.services import info_service
from scripts.services.font_service import DesignContext, FontContext


def main():
    font_config = configs.font_configs[10]
    design_context = DesignContext.load(font_config)
    design_context.standardize()
    for width_mode in configs.width_modes:
        font_context = FontContext(design_context, width_mode)
        font_context.make_woff2()
        info_service.make_info_file(design_context, width_mode)
        info_service.make_alphabet_txt_file(design_context, width_mode)


if __name__ == '__main__':
    main()
