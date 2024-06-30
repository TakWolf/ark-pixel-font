import datetime
import logging
import math
import re
import shutil
import unicodedata
from pathlib import Path

import unidata_blocks
from pixel_font_builder import FontBuilder, FontCollectionBuilder, WeightName, SerifStyle, SlantStyle, WidthMode, Glyph
from pixel_font_builder.opentype import Flavor
from pixel_font_knife import mono_bitmap_util

from tools import configs
from tools.configs import path_define, FontConfig
from tools.utils import fs_util

logger = logging.getLogger(__name__)


class GlyphFile:
    @staticmethod
    def load(file_path: Path) -> 'GlyphFile':
        tokens = re.split(r'\s+', file_path.stem, 1)

        if tokens[0] == 'notdef':
            code_point = -1
        else:
            code_point = int(tokens[0], 16)

        language_flavors = []
        if len(tokens) > 1:
            for language_flavor in tokens[1].lower().split(','):
                if language_flavor in language_flavors:
                    continue
                assert language_flavor in configs.language_flavors, f"Language flavor '{language_flavor}' undefined: '{file_path}'"
                language_flavors.append(language_flavor)
            language_flavors.sort(key=lambda x: configs.language_flavors.index(x))

        return GlyphFile(file_path, code_point, language_flavors)

    file_path: Path
    bitmap: list[list[int]]
    width: int
    height: int
    code_point: int
    language_flavors: list[str]

    def __init__(self, file_path: Path, code_point: int, language_flavors: list[str]):
        self.file_path = file_path
        self.bitmap, self.width, self.height = mono_bitmap_util.load_png(file_path)
        self.code_point = code_point
        self.language_flavors = language_flavors

    @property
    def glyph_name(self) -> str:
        if self.code_point == -1:
            _glyph_name = '.notdef'
        else:
            _glyph_name = f'{self.code_point:04X}'
        if len(self.language_flavors) > 0:
            _glyph_name = f'{_glyph_name}-{''.join([str(configs.language_flavors.index(language_flavor)) for language_flavor in self.language_flavors])}'
        return _glyph_name


class DesignContext:
    @staticmethod
    def load(font_config: FontConfig) -> 'DesignContext':
        glyph_file_registry = {}

        root_dir = path_define.glyphs_dir.joinpath(str(font_config.font_size))
        for width_mode_dir in root_dir.iterdir():
            if not width_mode_dir.is_dir():
                continue
            width_mode_dir_name = width_mode_dir.name
            assert width_mode_dir_name == 'common' or width_mode_dir_name in configs.width_modes, f"Width mode '{width_mode_dir_name}' undefined: '{width_mode_dir}'"

            code_point_registry = {}
            for file_dir, _, file_names in width_mode_dir.walk():
                for file_name in file_names:
                    if not file_name.endswith('.png'):
                        continue
                    file_path = file_dir.joinpath(file_name)
                    glyph_file = GlyphFile.load(file_path)

                    if glyph_file.code_point not in code_point_registry:
                        language_flavor_registry = {}
                        code_point_registry[glyph_file.code_point] = language_flavor_registry
                    else:
                        language_flavor_registry = code_point_registry[glyph_file.code_point]

                    if len(glyph_file.language_flavors) > 0:
                        for language_flavor in glyph_file.language_flavors:
                            assert language_flavor not in language_flavor_registry, f"Language flavor '{language_flavor}' already exists: '{glyph_file.file_path}' -> '{language_flavor_registry[language_flavor].file_path}'"
                            language_flavor_registry[language_flavor] = glyph_file
                    else:
                        assert '' not in language_flavor_registry, f"Default language flavor already exists: '{glyph_file.file_path}' -> '{language_flavor_registry[''].file_path}'"
                        language_flavor_registry[''] = glyph_file

            for code_point, glyph_files in code_point_registry.items():
                assert '' in glyph_files, f'Missing default language flavor: {font_config.font_size}px {width_mode_dir_name} {code_point:04X}'
            glyph_file_registry[width_mode_dir_name] = code_point_registry

        return DesignContext(font_config, glyph_file_registry)

    font_config: FontConfig
    _glyph_file_registry: dict[str, dict[int, dict[str, GlyphFile]]]
    _sequence_pool: dict[str, list[int]]
    _alphabet_pool: dict[str, set[str]]
    _character_mapping_pool: dict[str, dict[int, str]]
    _glyph_files_pool: dict[str, list[GlyphFile]]

    def __init__(
            self,
            font_config: FontConfig,
            glyph_file_registry: dict[str, dict[int, dict[str, GlyphFile]]],
    ):
        self.font_config = font_config
        self._glyph_file_registry = glyph_file_registry
        self._sequence_pool = {}
        self._alphabet_pool = {}
        self._character_mapping_pool = {}
        self._glyph_files_pool = {}

    def standardized(self):
        root_dir = path_define.glyphs_dir.joinpath(str(self.font_config.font_size))
        for width_mode_dir_name, code_point_registry in self._glyph_file_registry.items():
            width_mode_dir = root_dir.joinpath(width_mode_dir_name)
            for language_flavor_registry in code_point_registry.values():
                for glyph_file in set(language_flavor_registry.values()):
                    if glyph_file.code_point == -1:
                        east_asian_width = 'F'
                        block = None
                        file_name = 'notdef.png'
                        file_dir = width_mode_dir
                    else:
                        east_asian_width = unicodedata.east_asian_width(chr(glyph_file.code_point))
                        block = unidata_blocks.get_block_by_code_point(glyph_file.code_point)
                        hex_name = f'{glyph_file.code_point:04X}'
                        file_name = f'{hex_name}{' ' if len(glyph_file.language_flavors) > 0 else ''}{','.join(glyph_file.language_flavors)}.png'
                        file_dir = width_mode_dir.joinpath(f'{block.code_start:04X}-{block.code_end:04X} {block.name}')
                        if block.code_start == 0x4E00:  # CJK Unified Ideographs
                            file_dir = file_dir.joinpath(f'{hex_name[0:-2]}-')

                    if width_mode_dir_name == 'common' or width_mode_dir_name == 'monospaced':
                        assert glyph_file.height == self.font_config.font_size, f"Glyph data error: '{glyph_file.file_path}'"

                        # H/Halfwidth or Na/Narrow
                        if east_asian_width == 'H' or east_asian_width == 'Na':
                            assert glyph_file.width == self.font_config.font_size / 2, f"Glyph data error: '{glyph_file.file_path}'"
                        # F/Fullwidth or W/Wide
                        elif east_asian_width == 'F' or east_asian_width == 'W':
                            assert glyph_file.width == self.font_config.font_size, f"Glyph data error: '{glyph_file.file_path}'"
                        # A/Ambiguous or N/Neutral
                        else:
                            assert glyph_file.width == self.font_config.font_size / 2 or glyph_file.width == self.font_config.font_size, f"Glyph data error: '{glyph_file.file_path}'"

                        if block is not None:
                            if 'CJK Unified Ideographs' in block.name:
                                assert all(alpha == 0 for alpha in glyph_file.bitmap[0]), f"Glyph data error: '{glyph_file.file_path}'"
                                assert all(glyph_file.bitmap[i][-1] == 0 for i in range(0, len(glyph_file.bitmap))), f"Glyph data error: '{glyph_file.file_path}'"

                    if width_mode_dir_name == 'proportional':
                        assert glyph_file.height == self.font_config.line_height, f"Glyph data error: '{glyph_file.file_path}'"

                    mono_bitmap_util.save_png(glyph_file.bitmap, glyph_file.file_path)

                    file_path = file_dir.joinpath(file_name)
                    if glyph_file.file_path != file_path:
                        assert not file_path.exists(), f"Glyph file duplication: '{glyph_file.file_path}' -> '{file_path}'"
                        file_dir.mkdir(parents=True, exist_ok=True)
                        glyph_file.file_path.rename(file_path)
                        glyph_file.file_path = file_path
                        logger.info("Standardize glyph file path: '%s'", glyph_file.file_path)

        for file_dir, _, _ in root_dir.walk(top_down=False):
            if fs_util.is_empty_dir(file_dir):
                shutil.rmtree(file_dir)

    def _get_sequence(self, width_mode: str) -> list[int]:
        if width_mode in self._sequence_pool:
            sequence = self._sequence_pool[width_mode]
        else:
            sequence = set(self._glyph_file_registry['common'])
            sequence.update(self._glyph_file_registry[width_mode])
            sequence = list(sequence)
            sequence.sort()
            self._sequence_pool[width_mode] = sequence
        return sequence

    def get_alphabet(self, width_mode: str) -> set[str]:
        if width_mode in self._alphabet_pool:
            alphabet = self._alphabet_pool[width_mode]
        else:
            alphabet = set([chr(code_point) for code_point in self._get_sequence(width_mode) if code_point >= 0])
            self._alphabet_pool[width_mode] = alphabet
        return alphabet

    def get_character_mapping(self, width_mode: str, language_flavor: str) -> dict[int, str]:
        key = f'{width_mode}#{language_flavor}'
        if key in self._character_mapping_pool:
            character_mapping = self._character_mapping_pool[key]
        else:
            character_mapping = {}
            for code_point in self._get_sequence(width_mode):
                if code_point < 0:
                    continue
                language_flavor_registry = self._glyph_file_registry[width_mode].get(code_point, None)
                if language_flavor_registry is None:
                    language_flavor_registry = self._glyph_file_registry['common'][code_point]
                glyph_file = language_flavor_registry.get(language_flavor, language_flavor_registry[''])
                character_mapping[code_point] = glyph_file.glyph_name
            self._character_mapping_pool[key] = character_mapping
        return character_mapping

    def get_glyph_files(self, width_mode: str, language_flavor: str | None = None) -> list[GlyphFile]:
        key = f'{width_mode}#{'' if language_flavor is None else language_flavor}'
        if key in self._glyph_files_pool:
            glyph_files = self._glyph_files_pool[key]
        else:
            glyph_files = []
            if language_flavor is None:
                language_flavors = configs.language_flavors
            else:
                language_flavors = [language_flavor]
            sequence = self._get_sequence(width_mode)
            for language_flavor in language_flavors:
                for code_point in sequence:
                    language_flavor_registry = self._glyph_file_registry[width_mode].get(code_point, None)
                    if language_flavor_registry is None:
                        language_flavor_registry = self._glyph_file_registry['common'][code_point]
                    glyph_file = language_flavor_registry.get(language_flavor, language_flavor_registry[''])
                    if glyph_file not in glyph_files:
                        glyph_files.append(glyph_file)
            self._glyph_files_pool[key] = glyph_files
        return glyph_files


def _create_builder(
        design_context: DesignContext,
        glyph_pool: dict[Path, Glyph],
        width_mode: str,
        language_flavor: str,
        is_collection: bool,
) -> FontBuilder:
    layout_param = design_context.font_config.layout_params[width_mode]

    builder = FontBuilder()
    builder.font_metric.font_size = design_context.font_config.font_size
    builder.font_metric.horizontal_layout.ascent = layout_param.ascent
    builder.font_metric.horizontal_layout.descent = layout_param.descent
    builder.font_metric.vertical_layout.ascent = math.ceil(layout_param.line_height / 2)
    builder.font_metric.vertical_layout.descent = math.floor(layout_param.line_height / 2)
    builder.font_metric.x_height = layout_param.x_height
    builder.font_metric.cap_height = layout_param.cap_height

    builder.meta_info.version = configs.font_version
    builder.meta_info.created_time = datetime.datetime.fromisoformat(f'{configs.font_version.replace('.', '-')}T00:00:00Z')
    builder.meta_info.modified_time = builder.meta_info.created_time
    builder.meta_info.family_name = f'Ark Pixel {design_context.font_config.font_size}px {width_mode.capitalize()} {language_flavor}'
    builder.meta_info.weight_name = WeightName.REGULAR
    builder.meta_info.serif_style = SerifStyle.SANS_SERIF
    builder.meta_info.slant_style = SlantStyle.NORMAL
    builder.meta_info.width_mode = WidthMode(width_mode.capitalize())
    builder.meta_info.manufacturer = 'TakWolf'
    builder.meta_info.designer = 'TakWolf'
    builder.meta_info.description = 'Open source Pan-CJK pixel font.'
    builder.meta_info.copyright_info = "Copyright (c) 2021, TakWolf (https://takwolf.com), with Reserved Font Name 'Ark Pixel'."
    builder.meta_info.license_info = 'This Font Software is licensed under the SIL Open Font License, Version 1.1.'
    builder.meta_info.vendor_url = 'https://ark-pixel-font.takwolf.com'
    builder.meta_info.designer_url = 'https://takwolf.com'
    builder.meta_info.license_url = 'https://openfontlicense.org'

    character_mapping = design_context.get_character_mapping(width_mode, language_flavor)
    builder.character_mapping.update(character_mapping)

    glyph_files = design_context.get_glyph_files(width_mode, None if is_collection else language_flavor)
    for glyph_file in glyph_files:
        if glyph_file.file_path in glyph_pool:
            glyph = glyph_pool[glyph_file.file_path]
        else:
            horizontal_origin_y = math.floor((layout_param.ascent + layout_param.descent - glyph_file.height) / 2)
            vertical_origin_y = (design_context.font_config.font_size - glyph_file.height) // 2 - 1
            glyph = Glyph(
                name=glyph_file.glyph_name,
                advance_width=glyph_file.width,
                advance_height=design_context.font_config.font_size,
                horizontal_origin=(0, horizontal_origin_y),
                vertical_origin_y=vertical_origin_y,
                bitmap=glyph_file.bitmap,
            )
            glyph_pool[glyph_file.file_path] = glyph
        builder.glyphs.append(glyph)

    return builder


class FontContext:
    design_context: DesignContext
    width_mode: str
    _glyph_pool: dict[Path, Glyph]
    _builders: dict[str, FontBuilder]
    _collection_builder: FontCollectionBuilder | None

    def __init__(self, design_context: DesignContext, width_mode: str):
        self.design_context = design_context
        self.width_mode = width_mode
        self._glyph_pool = {}
        self._builders = {}
        self._collection_builder = None

    def _get_builder(self, language_flavor: str) -> FontBuilder:
        if language_flavor in self._builders:
            builder = self._builders[language_flavor]
        else:
            builder = _create_builder(self.design_context, self._glyph_pool, self.width_mode, language_flavor, is_collection=False)
            self._builders[language_flavor] = builder
        return builder

    def _get_collection_builder(self) -> FontCollectionBuilder:
        if self._collection_builder is None:
            collection_builder = FontCollectionBuilder()
            for language_flavor in configs.language_flavors:
                builder = _create_builder(self.design_context, self._glyph_pool, self.width_mode, language_flavor, is_collection=True)
                collection_builder.append(builder)
            self._collection_builder = collection_builder
        return self._collection_builder

    def make_fonts(self, font_format: str):
        path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
        if font_format in configs.font_formats:
            for language_flavor in configs.language_flavors:
                builder = self._get_builder(language_flavor)
                file_path = path_define.outputs_dir.joinpath(f'ark-pixel-{self.design_context.font_config.font_size}px-{self.width_mode}-{language_flavor}.{font_format}')
                if font_format == 'woff2':
                    builder.save_otf(file_path, flavor=Flavor.WOFF2)
                else:
                    getattr(builder, f'save_{font_format}')(file_path)
                logger.info("Make font: '%s'", file_path)
        else:
            collection_builder = self._get_collection_builder()
            file_path = path_define.outputs_dir.joinpath(f'ark-pixel-{self.design_context.font_config.font_size}px-{self.width_mode}.{font_format}')
            getattr(collection_builder, f'save_{font_format}')(file_path)
            logger.info("Make font collection: '%s'", file_path)
