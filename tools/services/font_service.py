import math
from collections.abc import Sequence
from datetime import datetime

import unidata_blocks
from loguru import logger
from pixel_font_builder import FontBuilder, WeightName, SerifStyle, SlantStyle, WidthStyle, Glyph
from pixel_font_knife.cmap.context import CmapContext
from pixel_font_knife.cmap.file import CmapGlyphFile
from pixel_font_knife.named.context import NamedContext
from pixel_font_knife.named.file import NamedGlyphFile

from tools import configs
from tools.config import project
from tools.configs import path_define, options
from tools.configs.options import FontSize, WidthMode, LanguageFlavor, FontFormat


class FontBuildContext:
    @staticmethod
    def load(font_size: FontSize) -> FontBuildContext:
        notdef_glyph_file = NamedGlyphFile.load_notdef(path_define.GLYPHS_DIR.joinpath(str(font_size), 'notdef.png'))

        cmap_scope_contexts = {
            glyph_scope: CmapContext.load(
                path_define.GLYPHS_DIR.joinpath(str(font_size), 'cmap', glyph_scope),
                allowed_flavors=options.LANGUAGE_FLAVORS,
            )
            for glyph_scope in options.GLYPH_SCOPES
        }

        cmap_contexts = {
            width_mode: CmapContext().merge_by_code_point(
                cmap_scope_contexts['common'],
                cmap_scope_contexts[width_mode],
            ).apply_mapping_by_flavor(*configs.MAPPINGS)
            for width_mode in options.WIDTH_MODES
        }

        named_scope_contexts = {
            glyph_scope: NamedContext.load(
                path_define.GLYPHS_DIR.joinpath(str(font_size), 'named', glyph_scope),
                allowed_flavors=options.LANGUAGE_FLAVORS,
            )
            for glyph_scope in options.GLYPH_SCOPES
        }

        named_contexts = {
            width_mode: NamedContext().merge_by_name_key(
                named_scope_contexts['common'],
                named_scope_contexts[width_mode],
            )
            for width_mode in options.WIDTH_MODES
        }

        return FontBuildContext(font_size, notdef_glyph_file, cmap_contexts, named_contexts)

    font_size: FontSize
    notdef_glyph_file: NamedGlyphFile
    cmap_contexts: dict[WidthMode, CmapContext]
    named_contexts: dict[WidthMode, NamedContext]

    def __init__(
            self,
            font_size: FontSize,
            notdef_glyph_file: NamedGlyphFile,
            cmap_contexts: dict[WidthMode, CmapContext],
            named_contexts: dict[WidthMode, NamedContext],
    ) -> None:
        self.font_size = font_size
        self.notdef_glyph_file = notdef_glyph_file
        self.cmap_contexts = cmap_contexts
        self.named_contexts = named_contexts

    def get_alphabet(self, width_mode: WidthMode) -> Sequence[str]:
        return [chr(code_point) for code_point in sorted(self.cmap_contexts[width_mode].get_character_mapping().keys())]

    def create_builder(self, width_mode: WidthMode, language_flavor: LanguageFlavor) -> FontBuilder:
        layout_metric = configs.FONT_CONFIGS[self.font_size].layout_metrics[width_mode]

        builder = FontBuilder()
        builder.font_metric.font_size = self.font_size
        builder.font_metric.horizontal_layout.ascent = layout_metric.ascent
        builder.font_metric.horizontal_layout.descent = layout_metric.descent
        builder.font_metric.vertical_layout.ascent = math.ceil(layout_metric.line_height / 2)
        builder.font_metric.vertical_layout.descent = -math.floor(layout_metric.line_height / 2)
        builder.font_metric.x_height = layout_metric.x_height
        builder.font_metric.cap_height = layout_metric.cap_height
        builder.font_metric.underline_position = layout_metric.underline_position
        builder.font_metric.underline_thickness = 1
        builder.font_metric.strikeout_position = layout_metric.strikeout_position
        builder.font_metric.strikeout_thickness = 1

        builder.meta_info.version = project.VERSION
        builder.meta_info.created_time = datetime.fromisoformat(f'{project.VERSION.replace('.', '-')}T00:00:00Z')
        builder.meta_info.modified_time = builder.meta_info.created_time
        builder.meta_info.family_name = f'{project.FAMILY_NAME_PREFIX} {self.font_size}px {width_mode[:4].capitalize()} {configs.LANGUAGE_FLAVOR_TO_FONT_NAME[language_flavor]}'
        builder.meta_info.weight_name = WeightName.REGULAR
        builder.meta_info.serif_style = SerifStyle.SANS_SERIF
        builder.meta_info.slant_style = SlantStyle.NORMAL
        builder.meta_info.width_style = WidthStyle(width_mode.capitalize())
        builder.meta_info.manufacturer = project.MANUFACTURER
        builder.meta_info.designer = project.DESIGNER
        builder.meta_info.description = project.DESCRIPTION
        builder.meta_info.copyright_info = project.COPYRIGHT_INFO
        builder.meta_info.license_info = project.LICENSE_INFO
        builder.meta_info.vendor_url = project.VENDOR_URL
        builder.meta_info.designer_url = project.DESIGNER_URL
        builder.meta_info.license_url = project.LICENSE_URL

        glyph_sequence = [self.notdef_glyph_file] + self.cmap_contexts[width_mode].get_glyph_sequence(language_flavor) + self.named_contexts[width_mode].get_glyph_sequence(language_flavor)
        for glyph_file in glyph_sequence:
            vertical_em_size = self.font_size
            vertical_offset_y_delta = 0

            if isinstance(glyph_file, CmapGlyphFile):
                code_point = glyph_file.code_point
                block = unidata_blocks.get_block_by_code_point(code_point)

                if code_point in (
                        0x3031, 0x3032,
                ):
                    vertical_em_size = self.font_size * 2

                if not glyph_file.canvas.is_blank and block.name not in (
                        'Box Drawing',
                        'Block Elements',
                ) and code_point not in (
                        0x25D8, 0x25D9, 0x25DA, 0x25DB,
                        0x25E2, 0x25E3, 0x25E4, 0x25E5,
                        0x25F8, 0x25F9, 0x25FA, 0x25FF,
                        0x3031, 0x3032, 0x3033, 0x3034, 0x3035,
                ):
                    vertical_offset_y_delta = -1

            if isinstance(glyph_file, NamedGlyphFile):
                if glyph_file.name_key != '.notdef':
                    vertical_offset_y_delta = -1

            horizontal_offset_x, horizontal_offset_y = glyph_file.canvas.horizontal_offset_for_trimmed(self.font_size, layout_metric.baseline)
            advance_width = glyph_file.canvas.advance_width()

            vertical_offset_x, vertical_offset_y = glyph_file.canvas.vertical_offset_for_trimmed(vertical_em_size)
            vertical_offset_y += vertical_offset_y_delta
            advance_height = glyph_file.canvas.advance_height(vertical_em_size)

            builder.glyphs.append(Glyph(
                name=glyph_file.glyph_name,
                horizontal_offset=(horizontal_offset_x, horizontal_offset_y),
                advance_width=advance_width,
                vertical_offset=(vertical_offset_x, vertical_offset_y),
                advance_height=advance_height,
                bitmap=glyph_file.canvas.trimmed_bitmap.data,
            ))

        character_mapping = self.cmap_contexts[width_mode].get_character_mapping(language_flavor)
        builder.character_mapping.update(character_mapping)

        if width_mode == 'proportional':
            kerning_values = configs.KERNING_TEMPLATE_DEFAULT.calculate_kerning_values(self.cmap_contexts['proportional'], language_flavor)
            builder.kerning_values.update(kerning_values)

        builder.opentype_config.field_overrides.head_y_max = layout_metric.ascent
        builder.opentype_config.field_overrides.head_y_min = layout_metric.descent

        return builder

    def make_fonts(self, width_mode: WidthMode, font_formats: Sequence[FontFormat]) -> None:
        path_define.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

        if len(font_formats) > 0:
            for language_flavor in options.LANGUAGE_FLAVORS:
                builder = self.create_builder(width_mode, language_flavor)
                for font_format in font_formats:
                    file_path = path_define.OUTPUTS_DIR.joinpath(f'{project.FILE_NAME_PREFIX}-{self.font_size}px-{width_mode}-{language_flavor}.{font_format}')
                    getattr(builder, f'save_{font_format.replace('.', '_')}')(file_path)
                    logger.info("Make font: '{}'", file_path)
