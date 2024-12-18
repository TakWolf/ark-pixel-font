from pixel_font_knife import glyph_file_util

from tools import configs
from tools.configs import path_define
from tools.services import kerning_service


def main():
    for font_size in configs.font_sizes:
        context = glyph_file_util.load_context(path_define.glyphs_dir.joinpath(str(font_size), 'proportional'))
        kerning_service.make_kerning_feature_files(font_size, context)


if __name__ == '__main__':
    main()
