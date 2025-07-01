from pixel_font_knife import glyph_mapping_util

from tools import configs
from tools.configs import options
from tools.configs.font import FontConfig
from tools.services import check_service


def main():
    mappings = [glyph_mapping_util.load_mapping(file_path) for file_path in configs.mapping_file_paths]
    for font_size in options.font_sizes:
        font_config = FontConfig.load(font_size)
        check_service.check_glyph_files(font_config, mappings)


if __name__ == '__main__':
    main()
