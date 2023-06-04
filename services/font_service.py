import logging
import os
import shutil
import unicodedata

import png
import unidata_blocks
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

import configs
from configs import path_define
from utils import glyph_util, fs_util

logger = logging.getLogger('font-service')


def _parse_glyph_file_name(glyph_file_name):
    tokens = glyph_file_name.removesuffix('.png').split(' ')
    assert 1 <= len(tokens) <= 2, glyph_file_name
    hex_name = tokens[0].upper()
    language_flavors = []
    if len(tokens) == 2:
        language_flavor_tokens = tokens[1].lower().split(',')
        for language_flavor in configs.language_flavors:
            if language_flavor in language_flavor_tokens:
                language_flavors.append(language_flavor)
        assert len(language_flavors) == len(language_flavor_tokens), glyph_file_name
    return hex_name, language_flavors


def _load_glyph_data_from_png(file_path):
    width, height, bitmap, _ = png.Reader(filename=file_path).read()
    data = []
    for bitmap_row in bitmap:
        data_row = []
        for x in range(0, width * 4, 4):
            alpha = bitmap_row[x + 3]
            if alpha > 127:
                data_row.append(1)
            else:
                data_row.append(0)
        data.append(data_row)
    return data, width, height


def _save_glyph_data_to_png(data, file_path):
    bitmap = []
    for data_row in data:
        bitmap_row = []
        for x in data_row:
            bitmap_row.append(0)
            bitmap_row.append(0)
            bitmap_row.append(0)
            if x == 0:
                bitmap_row.append(0)
            else:
                bitmap_row.append(255)
        bitmap.append(bitmap_row)
    png.from_array(bitmap, 'RGBA').save(file_path)


def format_glyph_files(font_config):
    tmp_dir = os.path.join(path_define.glyphs_tmp_dir, str(font_config.px))
    fs_util.delete_dir(tmp_dir)
    for width_mode_dir_name in configs.width_mode_dir_names:
        width_mode_dir = os.path.join(font_config.root_dir, width_mode_dir_name)
        if not os.path.isdir(width_mode_dir):
            continue
        width_mode_tmp_dir = os.path.join(tmp_dir, width_mode_dir_name)
        for glyph_file_from_dir, _, glyph_file_names in os.walk(width_mode_dir):
            for glyph_file_name in glyph_file_names:
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
                assert not os.path.exists(glyph_file_to_path), glyph_file_from_path

                glyph_data, glyph_width, glyph_height = _load_glyph_data_from_png(glyph_file_from_path)

                if width_mode_dir_name == 'common' or width_mode_dir_name == 'monospaced':
                    assert glyph_height == font_config.px, glyph_file_from_path

                    # H/Halfwidth or Na/Narrow
                    if east_asian_width == 'H' or east_asian_width == 'Na':
                        assert glyph_width == font_config.px / 2, glyph_file_from_path
                    # F/Fullwidth or W/Wide
                    elif east_asian_width == 'F' or east_asian_width == 'W':
                        assert glyph_width == font_config.px, glyph_file_from_path
                    # A/Ambiguous or N/Neutral
                    else:
                        assert glyph_width == font_config.px / 2 or glyph_width == font_config.px, glyph_file_from_path

                    if block is not None:
                        if block.code_start == 0x4E00:  # CJK Unified Ideographs
                            if any(alpha != 0 for alpha in glyph_data[0]):
                                raise AssertionError(glyph_file_from_path)
                            if any(glyph_data[i][-1] != 0 for i in range(0, len(glyph_data))):
                                raise AssertionError(glyph_file_from_path)

                if width_mode_dir_name == 'proportional':
                    assert glyph_height >= font_config.px, glyph_file_from_path
                    assert (glyph_height - font_config.px) % 2 == 0, glyph_file_from_path

                    if glyph_height > font_config.line_height_px:
                        for i in range(int((glyph_height - font_config.line_height_px) / 2)):
                            glyph_data.pop(0)
                            glyph_data.pop()
                    elif glyph_height < font_config.line_height_px:
                        for i in range(int((font_config.line_height_px - glyph_height) / 2)):
                            glyph_data.insert(0, [0 for _ in range(glyph_width)])
                            glyph_data.append([0 for _ in range(glyph_width)])

                fs_util.make_dirs(glyph_file_to_dir)
                _save_glyph_data_to_png(glyph_data, glyph_file_to_path)
                logger.info(f"Formatted glyph file: '{glyph_file_to_path}'")
        width_mode_old_dir = os.path.join(tmp_dir, f'{width_mode_dir_name}.old')
        os.rename(width_mode_dir, width_mode_old_dir)
        os.rename(width_mode_tmp_dir, width_mode_dir)
        shutil.rmtree(width_mode_old_dir)


def collect_glyph_files(font_config):
    alphabet_cellar = {}
    for width_mode in configs.width_modes:
        alphabet_cellar[width_mode] = set()
    glyph_file_paths_cellar = {}
    for width_mode_dir_name in configs.width_mode_dir_names:
        glyph_file_paths_cellar[width_mode_dir_name] = {'default': {}}
        for language_flavor in configs.language_flavors:
            glyph_file_paths_cellar[width_mode_dir_name][language_flavor] = {}

    px_dir = os.path.join(path_define.glyphs_dir, str(font_config.px))
    for width_mode_dir_name in configs.width_mode_dir_names:
        width_mode_dir = os.path.join(px_dir, width_mode_dir_name)
        if not os.path.isdir(width_mode_dir):
            continue
        for glyph_file_dir, _, glyph_file_names in os.walk(width_mode_dir):
            for glyph_file_name in glyph_file_names:
                if not glyph_file_name.endswith('.png'):
                    continue
                glyph_file_path = os.path.join(glyph_file_dir, glyph_file_name)
                if glyph_file_name == 'notdef.png':
                    glyph_file_paths_cellar[width_mode_dir_name]['default']['.notdef'] = glyph_file_path
                else:
                    hex_name, language_flavors = _parse_glyph_file_name(glyph_file_name)
                    code_point = int(hex_name, 16)
                    if len(language_flavors) > 0:
                        for language_flavor in language_flavors:
                            assert code_point not in glyph_file_paths_cellar[width_mode_dir_name][language_flavor], glyph_file_path
                            glyph_file_paths_cellar[width_mode_dir_name][language_flavor][code_point] = glyph_file_path
                    else:
                        assert code_point not in glyph_file_paths_cellar[width_mode_dir_name]['default'], glyph_file_path
                        glyph_file_paths_cellar[width_mode_dir_name]['default'][code_point] = glyph_file_path
                        c = chr(code_point)
                        if width_mode_dir_name == 'common' or width_mode_dir_name == 'monospaced':
                            alphabet_cellar['monospaced'].add(c)
                        if width_mode_dir_name == 'common' or width_mode_dir_name == 'proportional':
                            alphabet_cellar['proportional'].add(c)

    alphabet_group = {}
    glyph_file_paths_map_group = {}
    for width_mode in configs.width_modes:
        alphabet = list(alphabet_cellar[width_mode])
        alphabet.sort()
        alphabet_group[width_mode] = alphabet

        glyph_file_paths_map = {}
        for language_flavor in configs.language_flavors:
            glyph_file_paths = dict(glyph_file_paths_cellar['common']['default'])
            glyph_file_paths.update(glyph_file_paths_cellar['common'][language_flavor])
            glyph_file_paths.update(glyph_file_paths_cellar[width_mode]['default'])
            glyph_file_paths.update(glyph_file_paths_cellar[width_mode][language_flavor])
            glyph_file_paths_map[language_flavor] = glyph_file_paths
        glyph_file_paths_map_group[width_mode] = glyph_file_paths_map

    return alphabet_group, glyph_file_paths_map_group


def _get_glyph_name(code_point):
    if isinstance(code_point, int):
        return f'uni{code_point:04X}'
    else:
        return code_point


class GlyphInfoBuilder:
    def __init__(self, units_per_em, box_origin_y, px_units):
        self.units_per_em = units_per_em
        self.box_origin_y = box_origin_y
        self.px_units = px_units
        self.glyph_data_info_map = {}
        self.otf_glyph_info_map = {}
        self.ttf_glyph_info_map = {}

    def _get_glyph_data_info(self, glyph_file_path):
        if glyph_file_path in self.glyph_data_info_map:
            glyph_data_info = self.glyph_data_info_map[glyph_file_path]
        else:
            glyph_data, width_px, height_px = _load_glyph_data_from_png(glyph_file_path)
            outlines = glyph_util.get_outlines_from_glyph_data(glyph_data, self.px_units)
            glyph_data_info = outlines, width_px * self.px_units, height_px * self.px_units
            self.glyph_data_info_map[glyph_file_path] = glyph_data_info
        return glyph_data_info

    def _draw_glyph(self, outlines, width, height, is_ttf):
        if is_ttf:
            pen = TTGlyphPen(None)
        else:
            pen = T2CharStringPen(0, None)
        if len(outlines) > 0:
            for outline_index, outline in enumerate(outlines):
                for point_index, point in enumerate(outline):

                    # 转换左上角原点坐标系为 OpenType 坐标系
                    x, y = point
                    y = self.box_origin_y + (height - self.units_per_em) / 2 - y
                    point = x, y

                    if point_index == 0:
                        pen.moveTo(point)
                    else:
                        pen.lineTo(point)
                if outline_index < len(outlines) - 1:
                    pen.endPath()
                else:
                    pen.closePath()
        else:
            pen.moveTo((0, 0))
            pen.closePath()
        advance_width = width
        if is_ttf:
            return pen.glyph(), advance_width
        else:
            return pen.getCharString(), advance_width

    def _get_glyph_info(self, glyph_file_path, is_ttf):
        if is_ttf:
            glyph_info_map = self.ttf_glyph_info_map
        else:
            glyph_info_map = self.otf_glyph_info_map
        if glyph_file_path in glyph_info_map:
            glyph_info = glyph_info_map[glyph_file_path]
        else:
            outlines, width, height = self._get_glyph_data_info(glyph_file_path)
            glyph_info = self._draw_glyph(outlines, width, height, is_ttf)
            glyph_info_map[glyph_file_path] = glyph_info
        return glyph_info

    def build_glyph_info_map(self, glyph_file_paths, is_ttf):
        glyph_info_map = {}
        for code_point, glyph_file_path in glyph_file_paths.items():
            glyph_info = self._get_glyph_info(glyph_file_path, is_ttf)
            glyph_name = _get_glyph_name(code_point)
            glyph_info_map[glyph_name] = glyph_info
        return glyph_info_map


def _create_font_builder(name_strings, units_per_em, vertical_metrics, glyph_order, character_map, glyph_info_map, is_ttf):
    builder = FontBuilder(units_per_em, isTTF=is_ttf)
    builder.setupNameTable(name_strings)
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(character_map)
    glyphs = {}
    advance_widths = {}
    for glyph_name in glyph_order:
        glyphs[glyph_name], advance_widths[glyph_name] = glyph_info_map[glyph_name]
    if is_ttf:
        builder.setupGlyf(glyphs)
        horizontal_metrics = {glyph_name: (advance_width, glyphs[glyph_name].xMin) for glyph_name, advance_width in advance_widths.items()}
    else:
        builder.setupCFF(name_strings['psName'], {'FullName': name_strings['fullName']}, glyphs, {})
        horizontal_metrics = {glyph_name: (advance_width, glyphs[glyph_name].calcBounds(None)[0]) for glyph_name, advance_width in advance_widths.items()}
    builder.setupHorizontalMetrics(horizontal_metrics)
    builder.setupHorizontalHeader(
        ascent=vertical_metrics.ascent,
        descent=vertical_metrics.descent,
    )
    builder.setupOS2(
        sTypoAscender=vertical_metrics.ascent,
        sTypoDescender=vertical_metrics.descent,
        usWinAscent=vertical_metrics.ascent,
        usWinDescent=-vertical_metrics.descent,
        sxHeight=vertical_metrics.x_height,
        sCapHeight=vertical_metrics.cap_height,
    )
    builder.setupPost()
    return builder


def make_font_files(font_config, width_mode, alphabet, glyph_file_paths_map, language_flavors=None, font_formats=None):
    if language_flavors is None:
        language_flavors = configs.language_flavors
    if font_formats is None:
        font_formats = configs.font_formats

    fs_util.make_dirs(path_define.outputs_dir)

    units_per_em = font_config.get_units_per_em()
    vertical_metrics = font_config.get_vertical_metrics(width_mode)
    glyph_order = ['.notdef']
    character_map = {}
    for c in alphabet:
        code_point = ord(c)
        glyph_name = _get_glyph_name(code_point)
        glyph_order.append(glyph_name)
        character_map[code_point] = glyph_name
    glyph_info_builder = GlyphInfoBuilder(units_per_em, font_config.get_box_origin_y(width_mode), font_config.px_units)

    for language_flavor in language_flavors:
        name_strings = font_config.get_name_strings(width_mode, language_flavor)
        glyph_file_paths = glyph_file_paths_map[language_flavor]

        if 'otf' in font_formats or 'woff2' in font_formats:
            glyph_info_map = glyph_info_builder.build_glyph_info_map(glyph_file_paths, False)
            font_builder = _create_font_builder(name_strings, units_per_em, vertical_metrics, glyph_order, character_map, glyph_info_map, False)
            if 'otf' in font_formats:
                otf_file_path = os.path.join(path_define.outputs_dir, font_config.get_font_file_name(width_mode, language_flavor, 'otf'))
                font_builder.save(otf_file_path)
                logger.info(f"Made font file: '{otf_file_path}'")
            if 'woff2' in font_formats:
                font_builder.font.flavor = 'woff2'
                woff2_file_path = os.path.join(path_define.outputs_dir, font_config.get_font_file_name(width_mode, language_flavor, 'woff2'))
                font_builder.save(woff2_file_path)
                logger.info(f"Made font file: '{woff2_file_path}'")
        if 'ttf' in font_formats:
            glyph_info_map = glyph_info_builder.build_glyph_info_map(glyph_file_paths, True)
            font_builder = _create_font_builder(name_strings, units_per_em, vertical_metrics, glyph_order, character_map, glyph_info_map, True)
            ttf_file_path = os.path.join(path_define.outputs_dir, font_config.get_font_file_name(width_mode, language_flavor, 'ttf'))
            font_builder.save(ttf_file_path)
            logger.info(f"Made font file: '{ttf_file_path}'")
