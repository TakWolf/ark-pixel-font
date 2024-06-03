from scripts.configs import FontConfig
from scripts.services import publish_service, info_service
from scripts.services.font_service import DesignContext, FontContext


def main():
    font_size = 12
    width_mode = 'proportional'

    font_config = FontConfig.load(font_size)
    design_context = DesignContext.load(font_config)
    design_context.standardize()
    font_context = FontContext(design_context, width_mode)
    font_context.make_otf()
    font_context.make_woff2()
    font_context.make_ttf()
    font_context.make_bdf()
    font_context.make_pcf()
    font_context.make_otc()
    font_context.make_ttc()
    publish_service.make_release_zips(font_size, width_mode)
    info_service.make_info_file(design_context, width_mode)
    info_service.make_alphabet_txt_file(design_context, width_mode)


if __name__ == '__main__':
    main()
