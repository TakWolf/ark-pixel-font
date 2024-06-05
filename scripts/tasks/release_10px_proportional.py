import itertools

from scripts import configs
from scripts.configs import FontConfig
from scripts.services import publish_service, info_service
from scripts.services.font_service import DesignContext, FontContext


def main():
    font_size = 10
    width_mode = 'proportional'

    font_config = FontConfig.load(font_size)
    design_context = DesignContext.load(font_config)
    design_context.standardize()
    font_context = FontContext(design_context, width_mode)
    for font_format in itertools.chain(configs.font_formats, configs.font_collection_formats):
        font_context.make_fonts(font_format)
        publish_service.make_release_zip(font_size, width_mode, font_format)
    info_service.make_font_info(design_context, width_mode)
    info_service.make_alphabet_txt(design_context, width_mode)


if __name__ == '__main__':
    main()
