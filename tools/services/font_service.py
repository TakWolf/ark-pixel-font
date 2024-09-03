import datetime
import itertools
import math
from pathlib import Path

from loguru import logger
from pixel_font_builder import FontBuilder, FontCollectionBuilder, WeightName, SerifStyle, SlantStyle, WidthStyle, Glyph
from pixel_font_builder.opentype import Flavor
from pixel_font_knife import glyph_file_util
from pixel_font_knife.glyph_file_util import GlyphFile, GlyphFlavorGroup

from tools import configs
from tools.configs import path_define, FontSize, WidthMode, LanguageFlavor, FontFormat, FontCollectionFormat
from tools.configs.font import FontConfig


class DesignContext:
    @staticmethod
    def load(font_config: FontConfig) -> 'DesignContext':
        contexts = {}
        for width_mode_dir_name in itertools.chain(['common'], configs.width_modes):
            width_mode_dir = path_define.glyphs_dir.joinpath(str(font_config.font_size), width_mode_dir_name)
            contexts[width_mode_dir_name] = glyph_file_util.load_context(width_mode_dir)

        glyph_files = {}
        for width_mode in configs.width_modes:
            glyph_files[width_mode] = dict(contexts['common'])
            glyph_files[width_mode].update(contexts[width_mode])

        return DesignContext(font_config, glyph_files)

    font_config: FontConfig
    glyph_files: dict[WidthMode, dict[int, GlyphFlavorGroup]]
    _alphabet_cache: dict[str, set[str]]
    _character_mapping_cache: dict[str, dict[int, str]]
    _glyph_sequence_cache: dict[str, list[GlyphFile]]
    _glyph_pool_cache: dict[str, dict[Path, Glyph]]
    _builder_cache: dict[str, FontBuilder]
    _collection_builder_cache: dict[str, FontCollectionBuilder]

    def __init__(
            self,
            font_config: FontConfig,
            glyph_files: dict[WidthMode, dict[int, GlyphFlavorGroup]],
    ):
        self.font_config = font_config
        self.glyph_files = glyph_files
        self._alphabet_cache = {}
        self._character_mapping_cache = {}
        self._glyph_sequence_cache = {}
        self._glyph_pool_cache = {}
        self._builder_cache = {}
        self._collection_builder_cache = {}

    @property
    def font_size(self) -> FontSize:
        return self.font_config.font_size

    def get_alphabet(self, width_mode: WidthMode) -> set[str]:
        if width_mode in self._alphabet_cache:
            alphabet = self._alphabet_cache[width_mode]
        else:
            alphabet = {chr(code_point) for code_point in self.glyph_files[width_mode] if code_point >= 0}
            self._alphabet_cache[width_mode] = alphabet
        return alphabet

    def _get_character_mapping(self, width_mode: WidthMode, language_flavor: LanguageFlavor) -> dict[int, str]:
        key = f'{width_mode}#{language_flavor}'
        if key in self._character_mapping_cache:
            character_mapping = self._character_mapping_cache[key]
        else:
            character_mapping = glyph_file_util.get_character_mapping(self.glyph_files[width_mode], language_flavor)
            self._character_mapping_cache[key] = character_mapping
        return character_mapping

    def _get_glyph_sequence(self, width_mode: WidthMode, language_flavor: LanguageFlavor | None = None) -> list[GlyphFile]:
        key = f'{width_mode}#{'' if language_flavor is None else language_flavor}'
        if key in self._glyph_sequence_cache:
            glyph_sequence = self._glyph_sequence_cache[key]
        else:
            glyph_sequence = glyph_file_util.get_glyph_sequence(self.glyph_files[width_mode], configs.language_flavors if language_flavor is None else [language_flavor])
            self._glyph_sequence_cache[key] = glyph_sequence
        return glyph_sequence

    def _get_glyph_pool(self, width_mode: WidthMode) -> dict[Path, Glyph]:
        if width_mode in self._glyph_pool_cache:
            glyph_pool = self._glyph_pool_cache[width_mode]
        else:
            glyph_pool = {}
            self._glyph_pool_cache[width_mode] = glyph_pool
        return glyph_pool

    def _create_builder(self, width_mode: WidthMode, language_flavor: LanguageFlavor, is_collection: bool) -> FontBuilder:
        glyph_pool = self._get_glyph_pool(width_mode)
        layout_param = self.font_config.layout_params[width_mode]

        builder = FontBuilder()
        builder.font_metric.font_size = self.font_size
        builder.font_metric.horizontal_layout.ascent = layout_param.ascent
        builder.font_metric.horizontal_layout.descent = layout_param.descent
        builder.font_metric.vertical_layout.ascent = math.ceil(layout_param.line_height / 2)
        builder.font_metric.vertical_layout.descent = -math.floor(layout_param.line_height / 2)
        builder.font_metric.x_height = layout_param.x_height
        builder.font_metric.cap_height = layout_param.cap_height

        builder.meta_info.version = configs.version
        builder.meta_info.created_time = datetime.datetime.fromisoformat(f'{configs.version.replace('.', '-')}T00:00:00Z')
        builder.meta_info.modified_time = builder.meta_info.created_time
        builder.meta_info.family_name = f'Ark Pixel {self.font_size}px {width_mode.capitalize()} {language_flavor}'
        builder.meta_info.weight_name = WeightName.REGULAR
        builder.meta_info.serif_style = SerifStyle.SANS_SERIF
        builder.meta_info.slant_style = SlantStyle.NORMAL
        builder.meta_info.width_style = WidthStyle(width_mode.capitalize())
        builder.meta_info.manufacturer = 'TakWolf'
        builder.meta_info.designer = 'TakWolf'
        builder.meta_info.description = 'Open source Pan-CJK pixel font.'
        builder.meta_info.copyright_info = "Copyright (c) 2021, TakWolf (https://takwolf.com), with Reserved Font Name 'Ark Pixel'."
        builder.meta_info.license_info = 'This Font Software is licensed under the SIL Open Font License, Version 1.1.'
        builder.meta_info.vendor_url = 'https://ark-pixel-font.takwolf.com'
        builder.meta_info.designer_url = 'https://takwolf.com'
        builder.meta_info.license_url = 'https://openfontlicense.org'

        character_mapping = self._get_character_mapping(width_mode, language_flavor)
        builder.character_mapping.update(character_mapping)

        glyph_sequence = self._get_glyph_sequence(width_mode, None if is_collection else language_flavor)
        for glyph_file in glyph_sequence:
            if glyph_file.file_path in glyph_pool:
                glyph = glyph_pool[glyph_file.file_path]
            else:
                horizontal_origin_x = 0
                horizontal_origin_y = (layout_param.ascent + layout_param.descent - glyph_file.height) // 2
                vertical_origin_x = -math.ceil(glyph_file.width / 2)
                vertical_origin_y = (self.font_size - glyph_file.height) // 2 - 1
                glyph = Glyph(
                    name=glyph_file.glyph_name,
                    horizontal_origin=(horizontal_origin_x, horizontal_origin_y),
                    advance_width=glyph_file.width,
                    vertical_origin=(vertical_origin_x, vertical_origin_y),
                    advance_height=self.font_size,
                    bitmap=glyph_file.bitmap.data,
                )
                glyph_pool[glyph_file.file_path] = glyph
            builder.glyphs.append(glyph)

        return builder

    def _get_builder(self, width_mode: WidthMode, language_flavor: LanguageFlavor) -> FontBuilder:
        key = f'{width_mode}#{language_flavor}'
        if key in self._builder_cache:
            builder = self._builder_cache[key]
        else:
            builder = self._create_builder(width_mode, language_flavor, is_collection=False)
            self._builder_cache[key] = builder
        return builder

    def _get_collection_builder(self, width_mode: WidthMode) -> FontCollectionBuilder:
        if width_mode in self._collection_builder_cache:
            collection_builder = self._collection_builder_cache[width_mode]
        else:
            collection_builder = FontCollectionBuilder()
            for language_flavor in configs.language_flavors:
                builder = self._create_builder(width_mode, language_flavor, is_collection=True)
                collection_builder.append(builder)
            self._collection_builder_cache[width_mode] = collection_builder
        return collection_builder

    def make_fonts(self, width_mode: WidthMode, font_format: FontFormat | FontCollectionFormat):
        path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
        if font_format in configs.font_formats:
            for language_flavor in configs.language_flavors:
                builder = self._get_builder(width_mode, language_flavor)
                file_path = path_define.outputs_dir.joinpath(f'ark-pixel-{self.font_size}px-{width_mode}-{language_flavor}.{font_format}')
                if font_format == 'woff2':
                    builder.save_otf(file_path, flavor=Flavor.WOFF2)
                else:
                    getattr(builder, f'save_{font_format}')(file_path)
                logger.info("Make font: '{}'", file_path)
        else:
            collection_builder = self._get_collection_builder(width_mode)
            file_path = path_define.outputs_dir.joinpath(f'ark-pixel-{self.font_size}px-{width_mode}.{font_format}')
            getattr(collection_builder, f'save_{font_format}')(file_path)
            logger.info("Make font collection: '{}'", file_path)
