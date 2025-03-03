import shutil
from typing import Literal

from cyclopts import App, Parameter
from loguru import logger
from pixel_font_knife import glyph_mapping_util

from tools import configs
from tools.configs import path_define, FontSize, WidthMode, FontFormat, Attachment
from tools.configs.font import FontConfig
from tools.services import publish_service, info_service, template_service, image_service
from tools.services.font_service import DesignContext

app = App(
    version=configs.version,
    default_parameter=Parameter(consume_multiple=True),
)


@app.default
def main(
        cleanup: bool = False,
        font_sizes: set[FontSize] | None = None,
        width_modes: set[WidthMode] | None = None,
        font_formats: set[FontFormat] | None = None,
        attachments: set[Attachment | Literal['all']] | None = None,
):
    if font_sizes is None:
        font_sizes = configs.font_sizes
    else:
        font_sizes = sorted(font_sizes, key=lambda x: configs.font_sizes.index(x))
    if width_modes is None:
        width_modes = configs.width_modes
    else:
        width_modes = sorted(width_modes, key=lambda x: configs.width_modes.index(x))
    if font_formats is None:
        font_formats = configs.font_formats
    else:
        font_formats = sorted(font_formats, key=lambda x: configs.font_formats.index(x))
    if attachments is None:
        attachments = []
    elif 'all' in attachments:
        attachments = configs.attachments
    else:
        attachments = sorted(attachments, key=lambda x: configs.attachments.index(x))
    all_font_sizes = font_sizes == configs.font_sizes

    logger.info('cleanup = {}', cleanup)
    logger.info('font_sizes = {}', font_sizes)
    logger.info('width_modes = {}', width_modes)
    logger.info('font_formats = {}', font_formats)
    logger.info('attachments = {}', attachments)

    if cleanup and path_define.build_dir.exists():
        shutil.rmtree(path_define.build_dir)
        logger.info("Delete dir: '{}'", path_define.build_dir)

    mappings = [glyph_mapping_util.load_mapping(mapping_file_path) for mapping_file_path in configs.mapping_file_paths]
    font_configs = {}
    design_contexts = {}
    for font_size in font_sizes:
        font_config = FontConfig.load(font_size)
        font_configs[font_size] = font_config
        design_context = DesignContext.load(font_config, mappings)
        design_contexts[font_size] = design_context
        for width_mode in width_modes:
            design_context.make_fonts(width_mode, font_formats)

    if 'release' in attachments:
        for font_size in font_sizes:
            for width_mode in width_modes:
                publish_service.make_release_zips(font_size, width_mode, font_formats)

    if 'info' in attachments:
        for font_size in font_sizes:
            design_context = design_contexts[font_size]
            for width_mode in width_modes:
                info_service.make_info(design_context, width_mode)

    if 'alphabet' in attachments:
        for font_size in font_sizes:
            design_context = design_contexts[font_size]
            for width_mode in width_modes:
                info_service.make_alphabet_txt(design_context, width_mode)

    if 'html' in attachments:
        for font_size in font_sizes:
            design_context = design_contexts[font_size]
            for width_mode in width_modes:
                template_service.make_alphabet_html(design_context, width_mode)
            template_service.make_demo_html(design_context)
        if all_font_sizes:
            template_service.make_index_html(font_configs)
            template_service.make_playground_html(font_configs)

    if 'image' in attachments:
        for font_size in font_sizes:
            font_config = font_configs[font_size]
            image_service.make_preview_image(font_config)
        if all_font_sizes:
            image_service.make_readme_banner(design_contexts)
            image_service.make_github_banner(design_contexts)
            image_service.make_itch_io_banner(design_contexts)
            image_service.make_itch_io_background(design_contexts)
            image_service.make_itch_io_cover(font_configs)
            image_service.make_afdian_cover(font_configs)


if __name__ == '__main__':
    app()
