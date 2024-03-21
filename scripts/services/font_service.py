import logging
import math
import os
import re
import unicodedata

import unidata_blocks
from pixel_font_builder import FontBuilder, FontCollectionBuilder, Glyph, StyleName, SerifMode
from pixel_font_builder.opentype import Flavor

from scripts import configs
from scripts.configs import path_define, FontConfig
from scripts.utils import fs_util, glyph_util

logger = logging.getLogger('font_service')


class GlyphFile:
    @staticmethod
    def load(file_path: str) -> 'GlyphFile':
        tokens = re.split(r'\s+', os.path.basename(file_path).removesuffix('.png'), 1)

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

    def __init__(self, file_path: str, code_point: int, language_flavors: list[str]):
        self.file_path = file_path
        self.glyph_data, self.glyph_width, self.glyph_height = glyph_util.load_glyph_data_from_png(file_path)
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

        root_dir = os.path.join(path_define.glyphs_dir, str(font_config.size))
        for width_mode_dir_name in os.listdir(root_dir):
            width_mode_dir = os.path.join(root_dir, width_mode_dir_name)
            if not os.path.isdir(width_mode_dir):
                continue
            assert width_mode_dir_name == 'common' or width_mode_dir_name in configs.width_modes, f"Width mode '{width_mode_dir_name}' undefined: '{width_mode_dir}'"

            code_point_registry = {}
            for file_dir, _, file_names in os.walk(width_mode_dir):
                for file_name in file_names:
                    if not file_name.endswith('.png'):
                        continue
                    file_path = os.path.join(file_dir, file_name)
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
                assert '' in glyph_files, f'Missing default language flavor: {font_config.size}px {width_mode_dir_name} {code_point:04X}'
            glyph_file_registry[width_mode_dir_name] = code_point_registry

        return DesignContext(font_config, glyph_file_registry)

    def __init__(
            self,
            font_config: FontConfig,
            glyph_file_registry: dict[str, dict[int, dict[str, GlyphFile]]],
    ):
        self.font_config = font_config
        self._glyph_file_registry = glyph_file_registry
        self._sequence_pool: dict[str, list[int]] = {}
        self._alphabet_pool: dict[str, set[str]] = {}
        self._character_mapping_pool: dict[str, dict[int, str]] = {}
        self._glyph_files_pool: dict[str, list[GlyphFile]] = {}

    def standardize(self):
        root_dir = os.path.join(path_define.glyphs_dir, str(self.font_config.size))
        for width_mode_dir_name, code_point_registry in self._glyph_file_registry.items():
            width_mode_dir = os.path.join(root_dir, width_mode_dir_name)
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
                        file_dir = os.path.join(width_mode_dir, f'{block.code_start:04X}-{block.code_end:04X} {block.name}')
                        if block.code_start == 0x4E00:  # CJK Unified Ideographs
                            file_dir = os.path.join(file_dir, f'{hex_name[0:-2]}-')

                    if width_mode_dir_name == 'common' or width_mode_dir_name == 'monospaced':
                        assert glyph_file.glyph_height == self.font_config.size, f"Glyph data error: '{glyph_file.file_path}'"

                        # H/Halfwidth or Na/Narrow
                        if east_asian_width == 'H' or east_asian_width == 'Na':
                            assert glyph_file.glyph_width == self.font_config.size / 2, f"Glyph data error: '{glyph_file.file_path}'"
                        # F/Fullwidth or W/Wide
                        elif east_asian_width == 'F' or east_asian_width == 'W':
                            assert glyph_file.glyph_width == self.font_config.size, f"Glyph data error: '{glyph_file.file_path}'"
                        # A/Ambiguous or N/Neutral
                        else:
                            assert glyph_file.glyph_width == self.font_config.size / 2 or glyph_file.glyph_width == self.font_config.size, f"Glyph data error: '{glyph_file.file_path}'"

                        if block is not None:
                            if block.code_start == 0x4E00:  # CJK Unified Ideographs
                                assert all(alpha == 0 for alpha in glyph_file.glyph_data[0]), f"Glyph data error: '{glyph_file.file_path}'"
                                assert all(glyph_file.glyph_data[i][-1] == 0 for i in range(0, len(glyph_file.glyph_data))), f"Glyph data error: '{glyph_file.file_path}'"

                    if width_mode_dir_name == 'proportional':
                        assert glyph_file.glyph_height == self.font_config.line_height, f"Glyph data error: '{glyph_file.file_path}'"

                    glyph_util.save_glyph_data_to_png(glyph_file.glyph_data, glyph_file.file_path)

                    file_path = os.path.join(file_dir, file_name)
                    if glyph_file.file_path != file_path:
                        assert not os.path.exists(file_path), f"Glyph file duplication: '{glyph_file.file_path}' -> '{file_path}'"
                        fs_util.make_dir(file_dir)
                        os.rename(glyph_file.file_path, file_path)
                        file_dir_from = os.path.dirname(glyph_file.file_path)
                        glyph_file.file_path = file_path
                        logger.info(f"Standardize glyph file path: '{glyph_file.file_path}'")

                        remained_file_names = os.listdir(file_dir_from)
                        if '.DS_Store' in remained_file_names:
                            remained_file_names.remove('.DS_Store')
                        if len(remained_file_names) == 0:
                            fs_util.delete_dir(file_dir_from)

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

    def get_glyph_files(self, width_mode: str, language_flavor: str = None) -> list[GlyphFile]:
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
        glyph_pool: dict[str, Glyph],
        width_mode: str,
        language_flavor: str,
        is_collection: bool,
) -> FontBuilder:
    builder = FontBuilder(design_context.font_config.size)

    builder.meta_info.version = FontConfig.VERSION
    builder.meta_info.family_name = f'{FontConfig.FAMILY_NAME} {design_context.font_config.size}px {width_mode.capitalize()} {language_flavor}'
    builder.meta_info.style_name = StyleName.REGULAR
    builder.meta_info.serif_mode = SerifMode.SANS_SERIF
    builder.meta_info.width_mode = width_mode.capitalize()
    builder.meta_info.manufacturer = FontConfig.MANUFACTURER
    builder.meta_info.designer = FontConfig.DESIGNER
    builder.meta_info.description = FontConfig.DESCRIPTION
    builder.meta_info.copyright_info = FontConfig.COPYRIGHT_INFO
    builder.meta_info.license_info = FontConfig.LICENSE_INFO
    builder.meta_info.vendor_url = FontConfig.VENDOR_URL
    builder.meta_info.designer_url = FontConfig.DESIGNER_URL
    builder.meta_info.license_url = FontConfig.LICENSE_URL

    if is_collection:
        builder.opentype_config.cff_family_name = f'{FontConfig.FAMILY_NAME} {design_context.font_config.size}px {width_mode.capitalize()}'

    layout_param = design_context.font_config.layout_params[width_mode]

    builder.horizontal_header.ascent = layout_param.ascent
    builder.horizontal_header.descent = layout_param.descent

    builder.vertical_header.ascent = layout_param.ascent
    builder.vertical_header.descent = layout_param.descent

    builder.os2_config.x_height = layout_param.x_height
    builder.os2_config.cap_height = layout_param.cap_height

    character_mapping = design_context.get_character_mapping(width_mode, language_flavor)
    builder.character_mapping.update(character_mapping)

    glyph_files = design_context.get_glyph_files(width_mode, None if is_collection else language_flavor)
    for glyph_file in glyph_files:
        if glyph_file.file_path in glyph_pool:
            glyph = glyph_pool[glyph_file.file_path]
        else:
            horizontal_origin_y = math.floor((layout_param.ascent + layout_param.descent - glyph_file.glyph_height) / 2)
            vertical_origin_y = (glyph_file.glyph_height - design_context.font_config.size) // 2
            glyph = Glyph(
                name=glyph_file.glyph_name,
                advance_width=glyph_file.glyph_width,
                advance_height=design_context.font_config.size,
                horizontal_origin=(0, horizontal_origin_y),
                vertical_origin_y=vertical_origin_y,
                data=glyph_file.glyph_data,
            )
            glyph_pool[glyph_file.file_path] = glyph
        builder.glyphs.append(glyph)

    return builder


class FontContext:
    def __init__(self, design_context: DesignContext, width_mode: str):
        self.design_context = design_context
        self.width_mode = width_mode
        self._glyph_pool: dict[str, Glyph] = {}
        self._builders: dict[str, FontBuilder] = {}
        self._collection_builder: FontCollectionBuilder | None = None

    def _get_builder(self, language_flavor: str) -> FontBuilder:
        if language_flavor in self._builders:
            builder = self._builders[language_flavor]
        else:
            builder = _create_builder(self.design_context, self._glyph_pool, self.width_mode, language_flavor, is_collection=False)
            self._builders[language_flavor] = builder
        return builder

    def make_otf(self):
        fs_util.make_dir(path_define.outputs_dir)
        for language_flavor in configs.language_flavors:
            builder = self._get_builder(language_flavor)
            file_path = os.path.join(path_define.outputs_dir, self.design_context.font_config.get_font_file_name(self.width_mode, language_flavor, 'otf'))
            builder.save_otf(file_path)
            logger.info("Make font file: '%s'", file_path)

    def make_woff2(self):
        fs_util.make_dir(path_define.outputs_dir)
        for language_flavor in configs.language_flavors:
            builder = self._get_builder(language_flavor)
            file_path = os.path.join(path_define.outputs_dir, self.design_context.font_config.get_font_file_name(self.width_mode, language_flavor, 'woff2'))
            builder.save_otf(file_path, flavor=Flavor.WOFF2)
            logger.info("Make font file: '%s'", file_path)

    def make_ttf(self):
        fs_util.make_dir(path_define.outputs_dir)
        for language_flavor in configs.language_flavors:
            builder = self._get_builder(language_flavor)
            file_path = os.path.join(path_define.outputs_dir, self.design_context.font_config.get_font_file_name(self.width_mode, language_flavor, 'ttf'))
            builder.save_ttf(file_path)
            logger.info("Make font file: '%s'", file_path)

    def make_bdf(self):
        fs_util.make_dir(path_define.outputs_dir)
        for language_flavor in configs.language_flavors:
            builder = self._get_builder(language_flavor)
            file_path = os.path.join(path_define.outputs_dir, self.design_context.font_config.get_font_file_name(self.width_mode, language_flavor, 'bdf'))
            builder.save_bdf(file_path)
            logger.info("Make font file: '%s'", file_path)

    def _get_collection_builder(self) -> FontCollectionBuilder:
        if self._collection_builder is None:
            collection_builder = FontCollectionBuilder()
            for language_flavor in configs.language_flavors:
                builder = _create_builder(self.design_context, self._glyph_pool, self.width_mode, language_flavor, is_collection=True)
                collection_builder.font_builders.append(builder)
            self._collection_builder = collection_builder
        return self._collection_builder

    def make_otc(self):
        fs_util.make_dir(path_define.outputs_dir)
        collection_builder = self._get_collection_builder()
        file_path = os.path.join(path_define.outputs_dir, self.design_context.font_config.get_font_collection_file_name(self.width_mode, 'otc'))
        collection_builder.save_otc(file_path)
        logger.info("Make font collection file: '%s'", file_path)

    def make_ttc(self):
        fs_util.make_dir(path_define.outputs_dir)
        collection_builder = self._get_collection_builder()
        file_path = os.path.join(path_define.outputs_dir, self.design_context.font_config.get_font_collection_file_name(self.width_mode, 'ttc'))
        collection_builder.save_ttc(file_path)
        logger.info("Make font collection file: '%s'", file_path)
