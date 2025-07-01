from pixel_font_knife import glyph_mapping_util

from tools import configs
from tools.configs.font import FontConfig
from tools.services import check_service


def main():
    mappings = [glyph_mapping_util.load_mapping(mapping_file_path) for mapping_file_path in configs.mapping_file_paths]
    for font_size in configs.font_sizes:
        font_config = FontConfig.load(font_size)
        check_service.check_glyph_files(font_config, mappings)


if __name__ == '__main__':
    main()
