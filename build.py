import logging

import configs
from configs import path_define
from services import design_service, font_service, info_service, publish_service
from utils import fs_util

logging.basicConfig(level=logging.DEBUG)


def main():
    fs_util.delete_dir(path_define.build_dir)

    for font_config in configs.font_configs:
        design_service.classify_glyph_files(font_config)
        design_service.verify_glyph_files(font_config)
        alphabet, glyph_file_paths_map = design_service.collect_glyph_files(font_config)
        font_service.make_fonts(font_config, alphabet, glyph_file_paths_map)
        publish_service.make_release_zips(font_config)
        info_service.make_info_file(font_config, alphabet)
        info_service.make_alphabet_txt_file(font_config, alphabet)
        info_service.make_alphabet_html_file(font_config, alphabet)
        info_service.make_demo_html_file(font_config, alphabet)
        info_service.make_preview_image_file(font_config)
    info_service.make_index_html_file()
    info_service.make_playground_html_file()
    info_service.make_github_banner()
    info_service.make_itch_io_banner()
    info_service.make_itch_io_background()
    info_service.make_itch_io_cover()
    info_service.make_afdian_cover()


if __name__ == '__main__':
    main()
