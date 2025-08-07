from pixel_font_knife import glyph_file_util

from tools.configs import path_define
from tools.services import kerning_service


def main():
    context = glyph_file_util.load_context(path_define.glyphs_dir.joinpath('12', 'proportional'))
    kerning_pairs = kerning_service.calculate_kerning_pairs(context)
    print(kerning_pairs)


if __name__ == '__main__':
    main()
