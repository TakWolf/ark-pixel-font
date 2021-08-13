import logging

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

import configs
from utils import glyph_util

logger = logging.getLogger('font-service')


def _convert_point_to_open_type(point, ascent):
    """
    转换左上角坐标系为 OpenType 坐标系
    """
    x, y = point
    y = ascent - y
    return x, y


def _draw_glyph(design_file_path, em_dot_size, ascent, is_ttf):
    logger.info(f'draw glyph by design file {design_file_path}')
    font_data, width, height = glyph_util.load_design_data_from_png(design_file_path)
    outlines = glyph_util.get_outlines_from_design_data(font_data, em_dot_size)
    if is_ttf:
        pen = TTGlyphPen(None)
    else:
        pen = T2CharStringPen(width * em_dot_size, None)
    if len(outlines) > 0:
        for outline_index, outline in enumerate(outlines):
            for point_index, point in enumerate(outline):
                point = _convert_point_to_open_type(point, ascent)
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
    advance_width = width * em_dot_size
    if is_ttf:
        return pen.glyph(), advance_width
    else:
        return pen.getCharString(), advance_width


def _draw_glyphs(glyph_infos_pool, design_file_paths, em_dot_size, ascent, is_ttf):
    glyph_infos_map = {}
    for code_point, design_file_path in design_file_paths.items():
        if design_file_path in glyph_infos_pool:
            glyph_infos = glyph_infos_pool[design_file_path]
        else:
            glyph_infos = _draw_glyph(design_file_path, em_dot_size, ascent, is_ttf)
            glyph_infos_pool[design_file_path] = glyph_infos
        glyph_infos_map[code_point] = glyph_infos
    return glyph_infos_map


def _make_font_file(name_strings, units_per_em, ascent, descent, glyph_order, character_map, glyph_infos_map, is_ttf, file_path):
    builder = FontBuilder(units_per_em, isTTF=is_ttf)
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(character_map)
    glyphs = {}
    advance_widths = {}
    glyphs['.notdef'], advance_widths['.notdef'] = glyph_infos_map['.notdef']
    for code_point, glyph_name in character_map.items():
        glyphs[glyph_name], advance_widths[glyph_name] = glyph_infos_map[code_point]
    if is_ttf:
        builder.setupGlyf(glyphs)
        metrics = {glyph_name: (advance_width, builder.font['glyf'][glyph_name].xMin) for glyph_name, advance_width in advance_widths.items()}
    else:
        builder.setupCFF(name_strings['psName'], {'FullName': name_strings['fullName']}, glyphs, {})
        metrics = {glyph_name: (advance_width, glyphs[glyph_name].calcBounds(None)[0]) for glyph_name, advance_width in advance_widths.items()}
    builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(ascent=ascent, descent=descent)
    builder.setupNameTable(name_strings)
    builder.setupOS2(sTypoAscender=ascent, usWinAscent=ascent, usWinDescent=-descent)
    builder.setupPost()
    builder.save(file_path)
    logger.info(f'make {file_path}')


def make_fonts(font_config, alphabet, design_file_paths_map):
    glyph_order = ['.notdef']
    character_map = {}
    for c in alphabet:
        code_point = ord(c)
        glyph_name = f'uni{code_point:04X}'
        glyph_order.append(glyph_name)
        character_map[code_point] = glyph_name
    glyph_infos_otf_pool = {}
    glyph_infos_ttf_pool = {}
    for locale_flavor_config in font_config.locale_flavor_configs:
        name_strings = {
            'copyright': configs.copyright_string,
            'familyName': locale_flavor_config.display_name,
            'styleName': font_config.style_name,
            'uniqueFontIdentifier': f'{locale_flavor_config.unique_name}-{font_config.style_name};{configs.version}',
            'fullName': locale_flavor_config.display_name,
            'version': configs.version,
            'psName': f'{locale_flavor_config.unique_name}-{font_config.style_name}',
            'designer': configs.designer,
            'description': configs.description,
            'vendorURL': configs.vendor_url,
            'designerURL': configs.designer_url,
            'licenseDescription': configs.license_description,
            'licenseInfoURL': configs.license_info_url
        }
        design_file_paths = design_file_paths_map[locale_flavor_config.locale_flavor]
        glyph_infos_otf_map = _draw_glyphs(glyph_infos_otf_pool, design_file_paths, font_config.em_dot_size, font_config.ascent, False)
        _make_font_file(name_strings, font_config.units_per_em, font_config.ascent, font_config.descent, glyph_order, character_map, glyph_infos_otf_map, False, locale_flavor_config.otf_file_output_path)
        glyph_infos_ttf_map = _draw_glyphs(glyph_infos_ttf_pool, design_file_paths, font_config.em_dot_size, font_config.ascent, True)
        _make_font_file(name_strings, font_config.units_per_em, font_config.ascent, font_config.descent, glyph_order, character_map, glyph_infos_ttf_map, True, locale_flavor_config.ttf_file_output_path)
