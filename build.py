import logging
import os
import shutil

import configs
from configs import workspace_define
from services import design_service, font_service, info_service, publish_service

logging.basicConfig(level=logging.DEBUG)


def main():
    if os.path.exists(workspace_define.build_dir):
        shutil.rmtree(workspace_define.build_dir)
    os.makedirs(workspace_define.outputs_dir)
    os.makedirs(workspace_define.releases_dir)

    for font_config in configs.font_configs:
        design_service.classify_px_glyph_files(font_config)
        design_service.verify_px_glyph_files(font_config)
        alphabet, glyph_file_paths_map = design_service.collect_px_glyph_files(font_config)
        font_service.make_px_fonts(font_config, alphabet, glyph_file_paths_map)
        publish_service.make_px_release_zips(font_config)
        info_service.make_px_info_file(font_config, alphabet)
        info_service.make_px_preview_image_file(font_config)
        info_service.make_px_alphabet_txt_file(font_config, alphabet)
        info_service.make_px_alphabet_html_file(font_config, alphabet)
        info_service.make_px_demo_html_file(font_config, alphabet)
    info_service.make_index_html_file()
    info_service.make_playground_html_file()
    info_service.make_github_banner()
    info_service.make_itch_io_banner()
    info_service.make_itch_io_background()
    info_service.make_itch_io_cover()
    info_service.make_afdian_cover()


if __name__ == '__main__':
    main()
