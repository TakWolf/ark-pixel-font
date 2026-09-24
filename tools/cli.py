import shutil
from typing import Literal

from cyclopts import App, Parameter
from loguru import logger
from pixel_font_knife.cmap.kerning.template import CmapKerningTemplate
from pixel_font_knife.cmap.mapping.mapping import CmapMapping

from tools.config import path_define, project, manifest, options
from tools.config.font import FontConfig
from tools.config.options import FontSize, WidthMode, FontFormat, Attachment
from tools.services import publish_service, info_service, template_service, image_service
from tools.services.font_service import FontBuildContext

app = App(
    version=project.VERSION,
    default_parameter=Parameter(consume_multiple=True),
)


@app.default
def main(
        cleanup: bool = False,
        font_sizes: set[FontSize] | None = None,
        width_modes: set[WidthMode] | None = None,
        font_formats: set[FontFormat] | None = None,
        attachments: set[Attachment | Literal['all']] | None = None,
) -> None:
    if font_sizes is None:
        font_sizes = options.FONT_SIZES
    else:
        font_sizes = sorted(font_sizes, key=lambda x: options.FONT_SIZES.index(x))

    if width_modes is None:
        width_modes = options.WIDTH_MODES
    else:
        width_modes = sorted(width_modes, key=lambda x: options.WIDTH_MODES.index(x))

    if font_formats is None:
        font_formats = options.FONT_FORMATS
    else:
        font_formats = sorted(font_formats, key=lambda x: options.FONT_FORMATS.index(x))

    if attachments is None:
        attachments = []
    elif 'all' in attachments:
        attachments = options.ATTACHMENTS
    else:
        attachments = sorted(attachments, key=lambda x: options.ATTACHMENTS.index(x))

    all_font_sizes = font_sizes == options.FONT_SIZES

    logger.info('cleanup = {}', cleanup)
    logger.info('font_sizes = {}', font_sizes)
    logger.info('width_modes = {}', width_modes)
    logger.info('font_formats = {}', font_formats)
    logger.info('attachments = {}', attachments)

    if cleanup and path_define.BUILD_DIR.exists():
        shutil.rmtree(path_define.BUILD_DIR)
        logger.info("Delete dir: '{}'", path_define.BUILD_DIR)

    scope_mappings = {
        glyph_scope: [
            CmapMapping.load_yaml(
                file_path,
                allowed_flavors=options.LANGUAGE_FLAVORS,
            )
            for file_path in file_paths
        ]
        for glyph_scope, file_paths in manifest.SCOPE_MAPPING_FILE_PATHS.items()
    }

    kerning_template = CmapKerningTemplate.load(manifest.KERNING_TEMPLATE_FILE_PATH)

    font_size_to_build_context = {}
    for font_size in font_sizes:
        font_config = FontConfig.load(font_size)
        build_context = FontBuildContext.load(font_config, scope_mappings, kerning_template)
        font_size_to_build_context[font_size] = build_context

        for width_mode in width_modes:
            build_context.make_fonts(width_mode, font_formats)

    font_size_to_alphabets = {
        font_size: {
            width_mode: build_context.get_alphabet(width_mode)
            for width_mode in options.WIDTH_MODES
        }
        for font_size, build_context in font_size_to_build_context.items()
    }

    if 'release' in attachments:
        for font_size in font_sizes:
            for width_mode in width_modes:
                publish_service.make_release_zips(font_size, width_mode, font_formats)

    if 'info' in attachments:
        for font_size in font_sizes:
            for width_mode in width_modes:
                alphabet = font_size_to_alphabets[font_size][width_mode]
                info_service.make_info(font_size, width_mode, alphabet)

    if 'alphabet' in attachments:
        for font_size in font_sizes:
            for width_mode in width_modes:
                alphabet = font_size_to_alphabets[font_size][width_mode]
                info_service.make_alphabet_txt(font_size, width_mode, alphabet)

    if 'html' in attachments:
        for font_size in font_sizes:
            font_config = font_size_to_build_context[font_size].font_config
            alphabets = font_size_to_alphabets[font_size]

            for width_mode in width_modes:
                template_service.make_alphabet_html(font_config, width_mode, alphabets[width_mode])
            template_service.make_demo_html(font_config, alphabets)

        if all_font_sizes:
            template_service.make_index_html()
            template_service.make_playground_html()

    if 'image' in attachments:
        for font_size in font_sizes:
            font_config = font_size_to_build_context[font_size].font_config
            image_service.make_preview_image(font_config)

        if all_font_sizes:
            font_config_12px = font_size_to_build_context[12].font_config
            alphabet_proportional_12px = font_size_to_alphabets[12]['proportional']
            image_service.make_readme_banner(font_config_12px, alphabet_proportional_12px)
            image_service.make_github_banner(font_config_12px, alphabet_proportional_12px)
            image_service.make_itch_io_banner(font_config_12px, alphabet_proportional_12px)
            image_service.make_itch_io_cover(font_config_12px)
            image_service.make_afdian_cover(font_config_12px)


if __name__ == '__main__':
    app()
