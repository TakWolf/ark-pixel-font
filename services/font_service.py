import logging
import os

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

import configs
from configs import path_define
from utils import glyph_util, fs_util

logger = logging.getLogger('font-service')


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
            glyph_data, width_px, height_px = glyph_util.load_glyph_data_from_png(glyph_file_path)
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
            logger.info(f'draw {"ttf" if is_ttf else "otf"} glyph {glyph_file_path}')
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


def make_fonts(font_config, width_mode, alphabet, glyph_file_paths_map, language_flavors=None, font_formats=None):
    if language_flavors is None:
        language_flavors = configs.language_flavors
    if font_formats is None:
        font_formats = configs.font_formats

    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)

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
                font_file_path = os.path.join(path_define.outputs_dir, font_config.get_font_file_name(width_mode, language_flavor, 'otf'))
                font_builder.save(font_file_path)
                logger.info(f'make {font_file_path}')
            if 'woff2' in font_formats:
                font_builder.font.flavor = 'woff2'
                font_file_path = os.path.join(path_define.outputs_dir, font_config.get_font_file_name(width_mode, language_flavor, 'woff2'))
                font_builder.save(font_file_path)
                logger.info(f'make {font_file_path}')
        if 'ttf' in font_formats:
            glyph_info_map = glyph_info_builder.build_glyph_info_map(glyph_file_paths, True)
            font_builder = _create_font_builder(name_strings, units_per_em, vertical_metrics, glyph_order, character_map, glyph_info_map, True)
            font_file_path = os.path.join(path_define.outputs_dir, font_config.get_font_file_name(width_mode, language_flavor, 'ttf'))
            font_builder.save(font_file_path)
            logger.info(f'make {font_file_path}')
