import logging
import os
import unicodedata

import unidata_blocks
from pixel_font_builder import FontBuilder, Glyph, StyleName, SerifMode

import configs
from configs import path_define, FontConfig
from utils import fs_util, glyph_util

logger = logging.getLogger('font-service')


def _parse_glyph_file_name(glyph_file_name: str) -> tuple[str, list[str]]:
    tokens = glyph_file_name.removesuffix('.png').split(' ')
    assert 1 <= len(tokens) <= 2, f"Glyph file name '{glyph_file_name}': illegal format"
    hex_name = tokens[0].upper()
    language_flavors = []
    if len(tokens) == 2:
        language_flavor_tokens = tokens[1].lower().split(',')
        for language_flavor in configs.language_flavors:
            if language_flavor in language_flavor_tokens:
                language_flavors.append(language_flavor)
        assert len(language_flavors) == len(language_flavor_tokens), f"Glyph file name '{glyph_file_name}': unknown language flavors"
    return hex_name, language_flavors


def format_glyph_files(font_config: FontConfig):
    root_dir = os.path.join(path_define.glyphs_dir, str(font_config.size))
    tmp_dir = os.path.join(path_define.glyphs_tmp_dir, str(font_config.size))
    fs_util.delete_dir(tmp_dir)
    for width_mode_dir_name in configs.width_mode_dir_names:
        width_mode_dir = os.path.join(root_dir, width_mode_dir_name)
        width_mode_tmp_dir = os.path.join(tmp_dir, width_mode_dir_name)
        for glyph_file_from_dir, glyph_file_name in fs_util.walk_files(width_mode_dir):
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_from_path = os.path.join(glyph_file_from_dir, glyph_file_name)
            if glyph_file_name == 'notdef.png':
                east_asian_width = 'F'
                block = None
                glyph_file_to_dir = width_mode_tmp_dir
            else:
                hex_name, language_flavors = _parse_glyph_file_name(glyph_file_name)
                code_point = int(hex_name, 16)
                c = chr(code_point)
                east_asian_width = unicodedata.east_asian_width(c)
                glyph_file_name = f'{hex_name}{" " if len(language_flavors) > 0 else ""}{",".join(language_flavors)}.png'
                block = unidata_blocks.get_block_by_code_point(code_point)
                block_dir_name = f'{block.code_start:04X}-{block.code_end:04X} {block.name}'
                glyph_file_to_dir = os.path.join(width_mode_tmp_dir, block_dir_name)
                if block.code_start == 0x4E00:  # CJK Unified Ideographs
                    glyph_file_to_dir = os.path.join(glyph_file_to_dir, f'{hex_name[0:-2]}-')
            glyph_file_to_path = os.path.join(glyph_file_to_dir, glyph_file_name)
            assert not os.path.exists(glyph_file_to_path), f"Glyph file duplication: '{glyph_file_from_path}'"

            glyph_data, glyph_width, glyph_height = glyph_util.load_glyph_data_from_png(glyph_file_from_path)

            if width_mode_dir_name == 'common' or width_mode_dir_name == 'monospaced':
                assert glyph_height == font_config.size, f"Incorrect glyph data: '{glyph_file_from_path}'"

                # H/Halfwidth or Na/Narrow
                if east_asian_width == 'H' or east_asian_width == 'Na':
                    assert glyph_width == font_config.size / 2, f"Incorrect glyph data: '{glyph_file_from_path}'"
                # F/Fullwidth or W/Wide
                elif east_asian_width == 'F' or east_asian_width == 'W':
                    assert glyph_width == font_config.size, f"Incorrect glyph data: '{glyph_file_from_path}'"
                # A/Ambiguous or N/Neutral
                else:
                    assert glyph_width == font_config.size / 2 or glyph_width == font_config.size, f"Incorrect glyph data: '{glyph_file_from_path}'"

                if block is not None:
                    if block.code_start == 0x4E00:  # CJK Unified Ideographs
                        if any(alpha != 0 for alpha in glyph_data[0]):
                            raise AssertionError(f"Incorrect glyph data: '{glyph_file_from_path}'")
                        if any(glyph_data[i][-1] != 0 for i in range(0, len(glyph_data))):
                            raise AssertionError(f"Incorrect glyph data: '{glyph_file_from_path}'")

            if width_mode_dir_name == 'proportional':
                assert glyph_height >= font_config.size, f"Incorrect glyph data: '{glyph_file_from_path}'"
                assert (glyph_height - font_config.size) % 2 == 0, f"Incorrect glyph data: '{glyph_file_from_path}'"

                if glyph_height > font_config.line_height:
                    for i in range((glyph_height - font_config.line_height) // 2):
                        glyph_data.pop(0)
                        glyph_data.pop()
                elif glyph_height < font_config.line_height:
                    for i in range((font_config.line_height - glyph_height) // 2):
                        glyph_data.insert(0, [0 for _ in range(glyph_width)])
                        glyph_data.append([0 for _ in range(glyph_width)])

            fs_util.make_dirs(glyph_file_to_dir)
            glyph_util.save_glyph_data_to_png(glyph_data, glyph_file_to_path)
            logger.info("Format glyph file: '%s'", glyph_file_to_path)
        fs_util.delete_dir(width_mode_dir)
        if os.path.exists(width_mode_tmp_dir):
            os.rename(width_mode_tmp_dir, width_mode_dir)


class DesignContext:
    def __init__(
            self,
            character_mapping_group: dict[str, dict[int, str]],
            glyph_file_paths_group: dict[str, dict[str, dict[str, str]]],
    ):
        self._character_mapping_group = character_mapping_group
        self._alphabet_group = dict[str, set[str]]()
        for width_mode, character_mapping in character_mapping_group.items():
            alphabet = {chr(code_point) for code_point in character_mapping}
            self._alphabet_group[width_mode] = alphabet
        self._glyph_file_paths_group = glyph_file_paths_group
        self._glyph_data_pool = dict[str, tuple[list[list[int]], int, int]]()

    def get_character_mapping(self, width_mode: str) -> dict[int, str]:
        return self._character_mapping_group[width_mode]

    def get_alphabet(self, width_mode: str) -> set[str]:
        return self._alphabet_group[width_mode]

    def get_glyph_file_paths(self, width_mode: str, language_flavor: str) -> dict[str, str]:
        return self._glyph_file_paths_group[width_mode][language_flavor]

    def load_glyph_data(self, glyph_file_path: str) -> tuple[list[list[int]], int, int]:
        if glyph_file_path in self._glyph_data_pool:
            glyph_data, glyph_width, glyph_height = self._glyph_data_pool[glyph_file_path]
        else:
            glyph_data, glyph_width, glyph_height = glyph_util.load_glyph_data_from_png(glyph_file_path)
            self._glyph_data_pool[glyph_file_path] = glyph_data, glyph_width, glyph_height
            logger.info("Load glyph file: '%s'", glyph_file_path)
        return glyph_data, glyph_width, glyph_height


def collect_glyph_files(font_config: FontConfig) -> DesignContext:
    root_dir = os.path.join(path_define.glyphs_dir, str(font_config.size))

    character_mapping_group = dict[str, dict[int, str]]()
    glyph_file_paths_group = dict[str, dict[str, dict[str, str]]]()
    for width_mode in configs.width_modes:
        character_mapping_group[width_mode] = {}
        glyph_file_paths_group[width_mode] = {}

    glyph_file_paths_cellar = dict[str, dict[str, dict[str, str]]]()
    for width_mode_dir_name in configs.width_mode_dir_names:
        glyph_file_paths_cellar[width_mode_dir_name] = {
            'default': {},
        }
        for language_flavor in configs.language_flavors:
            glyph_file_paths_cellar[width_mode_dir_name][language_flavor] = {}

        width_mode_dir = os.path.join(root_dir, width_mode_dir_name)
        for glyph_file_dir, glyph_file_name in fs_util.walk_files(width_mode_dir):
            if not glyph_file_name.endswith('.png'):
                continue
            glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
            if glyph_file_name == 'notdef.png':
                glyph_file_paths_cellar[width_mode_dir_name]['default']['.notdef'] = glyph_file_path
            else:
                hex_name, language_flavors = _parse_glyph_file_name(glyph_file_name)
                code_point = int(hex_name, 16)
                glyph_name = f'uni{code_point:04X}'
                if len(language_flavors) > 0:
                    for language_flavor in language_flavors:
                        assert glyph_name not in glyph_file_paths_cellar[width_mode_dir_name][language_flavor], f"Glyph name '{glyph_name}' already exists in language flavor '{language_flavor}'"
                        glyph_file_paths_cellar[width_mode_dir_name][language_flavor][glyph_name] = glyph_file_path
                else:
                    assert glyph_name not in glyph_file_paths_cellar[width_mode_dir_name]['default'], f"Glyph name '{glyph_name}' already exists"
                    glyph_file_paths_cellar[width_mode_dir_name]['default'][glyph_name] = glyph_file_path
                if width_mode_dir_name == 'common' or width_mode_dir_name == 'monospaced':
                    character_mapping_group['monospaced'][code_point] = glyph_name
                if width_mode_dir_name == 'common' or width_mode_dir_name == 'proportional':
                    character_mapping_group['proportional'][code_point] = glyph_name

    for width_mode in configs.width_modes:
        for language_flavor in configs.language_flavors:
            glyph_file_paths = dict(glyph_file_paths_cellar['common']['default'])
            glyph_file_paths.update(glyph_file_paths_cellar['common'][language_flavor])
            glyph_file_paths.update(glyph_file_paths_cellar[width_mode]['default'])
            glyph_file_paths.update(glyph_file_paths_cellar[width_mode][language_flavor])
            glyph_file_paths_group[width_mode][language_flavor] = glyph_file_paths

    return DesignContext(character_mapping_group, glyph_file_paths_group)


def _create_builder(
        font_config: FontConfig,
        context: DesignContext,
        glyph_cacher: dict[str, Glyph],
        width_mode: str,
        language_flavor: str,
) -> FontBuilder:
    font_attrs = font_config.get_attrs(width_mode)
    builder = FontBuilder(
        font_config.size,
        font_attrs.ascent,
        font_attrs.descent,
        font_attrs.x_height,
        font_attrs.cap_height,
    )

    builder.character_mapping.update(context.get_character_mapping(width_mode))
    for glyph_name, glyph_file_path in context.get_glyph_file_paths(width_mode, language_flavor).items():
        if glyph_file_path in glyph_cacher:
            glyph = glyph_cacher[glyph_file_path]
        else:
            glyph_data, glyph_width, glyph_height = context.load_glyph_data(glyph_file_path)
            offset_y = font_attrs.box_origin_y + (glyph_height - font_config.size) // 2 - glyph_height
            glyph = Glyph(
                name=glyph_name,
                advance_width=glyph_width,
                offset=(0, offset_y),
                data=glyph_data,
            )
            glyph_cacher[glyph_file_path] = glyph
        builder.add_glyph(glyph)

    builder.meta_infos.version = FontConfig.VERSION
    builder.meta_infos.family_name = f'{FontConfig.FAMILY_NAME} {font_config.size}px {width_mode.capitalize()} {language_flavor}'
    builder.meta_infos.style_name = StyleName.REGULAR
    builder.meta_infos.serif_mode = SerifMode.SANS_SERIF
    builder.meta_infos.width_mode = width_mode.capitalize()
    builder.meta_infos.manufacturer = FontConfig.MANUFACTURER
    builder.meta_infos.designer = FontConfig.DESIGNER
    builder.meta_infos.description = FontConfig.DESCRIPTION
    builder.meta_infos.copyright_info = FontConfig.COPYRIGHT_INFO
    builder.meta_infos.license_info = FontConfig.LICENSE_INFO
    builder.meta_infos.vendor_url = FontConfig.VENDOR_URL
    builder.meta_infos.designer_url = FontConfig.DESIGNER_URL
    builder.meta_infos.license_url = FontConfig.LICENSE_URL

    return builder


def make_font_files(
        font_config: FontConfig,
        context: DesignContext,
        width_mode: str,
        language_flavors: list[str] = None,
        font_formats: list[str] = None,
):
    if language_flavors is None:
        language_flavors = configs.language_flavors
    if font_formats is None:
        font_formats = configs.font_formats

    fs_util.make_dirs(path_define.outputs_dir)

    glyph_cacher = {}
    for language_flavor in language_flavors:
        builder = _create_builder(font_config, context, glyph_cacher, width_mode, language_flavor)
        if 'otf' in font_formats or 'woff2' in font_formats:
            otf_builder = builder.to_otf_builder()
            if 'otf' in font_formats:
                otf_file_path = os.path.join(path_define.outputs_dir, font_config.get_font_file_name(width_mode, language_flavor, 'otf'))
                otf_builder.save(otf_file_path)
                logger.info("Make font file: '%s'", otf_file_path)
            if 'woff2' in font_formats:
                otf_builder.font.flavor = 'woff2'
                woff2_file_path = os.path.join(path_define.outputs_dir, font_config.get_font_file_name(width_mode, language_flavor, 'woff2'))
                otf_builder.save(woff2_file_path)
                logger.info("Make font file: '%s'", woff2_file_path)
        if 'ttf' in font_formats:
            ttf_file_path = os.path.join(path_define.outputs_dir, font_config.get_font_file_name(width_mode, language_flavor, 'ttf'))
            builder.save_ttf(ttf_file_path)
            logger.info("Make font file: '%s'", ttf_file_path)
        if 'bdf' in font_formats:
            bdf_file_path = os.path.join(path_define.outputs_dir, font_config.get_font_file_name(width_mode, language_flavor, 'bdf'))
            builder.save_bdf(bdf_file_path)
            logger.info("Make font file: '%s'", bdf_file_path)
