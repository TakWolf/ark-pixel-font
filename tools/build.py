import itertools

from tools import configs
from tools.configs import path_define
from tools.configs.font import FontConfig
from tools.services import publish_service, info_service, template_service, image_service
from tools.services.font_service import DesignContext, FontContext
from tools.utils import fs_util


def main():
    fs_util.delete_dir(path_define.outputs_dir)
    fs_util.delete_dir(path_define.releases_dir)

    font_configs = FontConfig.load_all()
    for font_size, font_config in font_configs.items():
        design_context = DesignContext.load(font_config)
        design_context.standardized()
        for width_mode in configs.width_modes:
            font_context = FontContext(design_context, width_mode)
            for font_format in itertools.chain(configs.font_formats, configs.font_collection_formats):
                font_context.make_fonts(font_format)
                publish_service.make_release_zip(font_size, width_mode, font_format)
            info_service.make_font_info(design_context, width_mode)
            info_service.make_alphabet_txt(design_context, width_mode)
            template_service.make_alphabet_html(design_context, width_mode)
        template_service.make_demo_html(design_context)
        image_service.make_preview_image(font_config)
    template_service.make_index_html(font_configs)
    template_service.make_playground_html(font_configs)
    image_service.make_readme_banner(font_configs)
    image_service.make_github_banner(font_configs)
    image_service.make_itch_io_banner(font_configs)
    image_service.make_itch_io_background(font_configs)
    image_service.make_itch_io_cover(font_configs)
    image_service.make_afdian_cover(font_configs)


if __name__ == '__main__':
    main()
