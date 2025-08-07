import unicodedata

from pixel_font_knife.glyph_file_util import GlyphFlavorGroup


def calculate_kerning_pairs(context: dict[int, GlyphFlavorGroup]) -> dict[tuple[str, str], int]:



    for code_point in context:
        c = chr(code_point)
        category = unicodedata.category(c)

        print(category)

















    kerning_pairs = {}



    return kerning_pairs
