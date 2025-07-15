from __future__ import annotations

import itertools
import math
from datetime import datetime

from loguru import logger
from pixel_font_builder import FontBuilder, FontCollectionBuilder, WeightName, SerifStyle, SlantStyle, WidthStyle, Glyph
from pixel_font_builder.opentype import Flavor
from pixel_font_knife import glyph_file_util, glyph_mapping_util
from pixel_font_knife.glyph_file_util import GlyphFile, GlyphFlavorGroup
from pixel_font_knife.glyph_mapping_util import SourceFlavorGroup

from tools import configs
from tools.configs import path_define, options
from tools.configs.options import FontSize, WidthMode, LanguageFlavor, FontFormat


class DesignContext:
    @staticmethod
    def load(font_size: FontSize, mappings: list[dict[int, SourceFlavorGroup]]) -> DesignContext:
        contexts = {}
        for width_mode_dir_name in itertools.chain(['common'], options.width_modes):
            context = glyph_file_util.load_context(path_define.glyphs_dir.joinpath(str(font_size), width_mode_dir_name))
            for mapping in mappings:
                glyph_mapping_util.apply_mapping(context, mapping)
            contexts[width_mode_dir_name] = context

        glyph_files = {}
        for width_mode in options.width_modes:
            glyph_files[width_mode] = dict(contexts['common'])
            glyph_files[width_mode].update(contexts[width_mode])

        return DesignContext(font_size, glyph_files)

    font_size: FontSize
    _glyph_files: dict[WidthMode, dict[int, GlyphFlavorGroup]]
    _alphabet_cache: dict[str, set[str]]
    _character_mapping_cache: dict[str, dict[int, str]]
    _glyph_sequence_cache: dict[str, list[GlyphFile]]

    def __init__(
            self,
            font_size: FontSize,
            glyph_files: dict[WidthMode, dict[int, GlyphFlavorGroup]],
    ):
        self.font_size = font_size
        self._glyph_files = glyph_files
        self._alphabet_cache = {}
        self._character_mapping_cache = {}
        self._glyph_sequence_cache = {}

    def get_alphabet(self, width_mode: WidthMode) -> set[str]:
        if width_mode in self._alphabet_cache:
            alphabet = self._alphabet_cache[width_mode]
        else:
            alphabet = {chr(code_point) for code_point in self._glyph_files[width_mode] if code_point >= 0}
            self._alphabet_cache[width_mode] = alphabet
        return alphabet

    def _get_character_mapping(self, width_mode: WidthMode, language_flavor: LanguageFlavor) -> dict[int, str]:
        key = f'{width_mode}#{language_flavor}'
        if key in self._character_mapping_cache:
            character_mapping = self._character_mapping_cache[key]
        else:
            character_mapping = glyph_file_util.get_character_mapping(self._glyph_files[width_mode], language_flavor)
            self._character_mapping_cache[key] = character_mapping
        return character_mapping

    def _get_glyph_sequence(self, width_mode: WidthMode, language_flavor: LanguageFlavor | None = None) -> list[GlyphFile]:
        key = f'{width_mode}#{'' if language_flavor is None else language_flavor}'
        if key in self._glyph_sequence_cache:
            glyph_sequence = self._glyph_sequence_cache[key]
        else:
            glyph_sequence = glyph_file_util.get_glyph_sequence(self._glyph_files[width_mode], options.language_flavors if language_flavor is None else [language_flavor])
            self._glyph_sequence_cache[key] = glyph_sequence
        return glyph_sequence

    def _create_builder(self, width_mode: WidthMode, language_flavor: LanguageFlavor, is_collection: bool) -> FontBuilder:
        layout_metric = configs.font_configs[self.font_size].layout_metrics[width_mode]

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

        builder.meta_info.version = configs.version
        builder.meta_info.created_time = datetime.fromisoformat(f'{configs.version.replace('.', '-')}T00:00:00Z')
        builder.meta_info.modified_time = builder.meta_info.created_time
        builder.meta_info.family_name = f'Ark Pixel {self.font_size}px {width_mode[0].upper()} {language_flavor}'
        builder.meta_info.weight_name = WeightName.REGULAR
        builder.meta_info.serif_style = SerifStyle.SANS_SERIF
        builder.meta_info.slant_style = SlantStyle.NORMAL
        builder.meta_info.width_style = WidthStyle(width_mode.capitalize())
        builder.meta_info.manufacturer = 'TakWolf'
        builder.meta_info.designer = 'TakWolf'
        builder.meta_info.description = 'Open source Pan-CJK pixel font'
        builder.meta_info.copyright_info = 'Copyright (c) 2021, TakWolf (https://takwolf.com), with Reserved Font Name "Ark Pixel"'
        builder.meta_info.license_info = 'This Font Software is licensed under the SIL Open Font License, Version 1.1'
        builder.meta_info.vendor_url = 'https://ark-pixel-font.takwolf.com'
        builder.meta_info.designer_url = 'https://takwolf.com'
        builder.meta_info.license_url = 'https://github.com/TakWolf/ark-pixel-font/blob/master/LICENSE-OFL'

        character_mapping = self._get_character_mapping(width_mode, language_flavor)
        builder.character_mapping.update(character_mapping)

        glyph_sequence = self._get_glyph_sequence(width_mode, None if is_collection else language_flavor)
        for glyph_file in glyph_sequence:
            horizontal_offset_x = 0
            horizontal_offset_y = layout_metric.baseline - self.font_size - (glyph_file.height - self.font_size) // 2
            vertical_offset_x = -math.ceil(glyph_file.width / 2)
            vertical_offset_y = (self.font_size - glyph_file.height) // 2 - 1
            builder.glyphs.append(Glyph(
                name=glyph_file.glyph_name,
                horizontal_offset=(horizontal_offset_x, horizontal_offset_y),
                advance_width=glyph_file.width,
                vertical_offset=(vertical_offset_x, vertical_offset_y),
                advance_height=self.font_size,
                bitmap=glyph_file.bitmap.data,
            ))

        return builder

    def _create_collection_builder(self, width_mode: WidthMode) -> FontCollectionBuilder:
        collection_builder = FontCollectionBuilder()
        for language_flavor in options.language_flavors:
            builder = self._create_builder(width_mode, language_flavor, is_collection=True)
            collection_builder.append(builder)
        return collection_builder

    def make_fonts(self, width_mode: WidthMode, font_formats: list[FontFormat]):
        path_define.outputs_dir.mkdir(parents=True, exist_ok=True)

        font_single_formats = [font_format for font_format in font_formats if font_format in options.font_single_formats]
        if len(font_single_formats) > 0:
            for language_flavor in options.language_flavors:
                builder = self._create_builder(width_mode, language_flavor, is_collection=False)
                for font_format in font_single_formats:
                    file_path = path_define.outputs_dir.joinpath(f'ark-pixel-{self.font_size}px-{width_mode}-{language_flavor}.{font_format}')
                    if font_format == 'otf.woff':
                        builder.save_otf(file_path, flavor=Flavor.WOFF)
                    elif font_format == 'otf.woff2':
                        builder.save_otf(file_path, flavor=Flavor.WOFF2)
                    elif font_format == 'ttf.woff':
                        builder.save_ttf(file_path, flavor=Flavor.WOFF)
                    elif font_format == 'ttf.woff2':
                        builder.save_ttf(file_path, flavor=Flavor.WOFF2)
                    else:
                        getattr(builder, f'save_{font_format}')(file_path)
                    logger.info("Make font: '{}'", file_path)

        font_collection_formats = [font_format for font_format in font_formats if font_format in options.font_collection_formats]
        if len(font_collection_formats) > 0:
            builder = self._create_collection_builder(width_mode)
            for font_format in font_collection_formats:
                file_path = path_define.outputs_dir.joinpath(f'ark-pixel-{self.font_size}px-{width_mode}.{font_format}')
                getattr(builder, f'save_{font_format}')(file_path)
                logger.info("Make font collection: '{}'", file_path)


def load_mappings() -> list[dict[int, SourceFlavorGroup]]:
    mappings = [glyph_mapping_util.load_mapping(file_path) for file_path in configs.mapping_file_paths]
    return mappings


def load_design_contexts(font_sizes: list[FontSize]) -> dict[FontSize, DesignContext]:
    mappings = load_mappings()
    design_contexts = {font_size: DesignContext.load(font_size, mappings) for font_size in font_sizes}
    return design_contexts
