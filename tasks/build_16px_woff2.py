import logging
import os

import configs
from configs import workspace_define
from services import design_service, font_service, info_service

logging.basicConfig(level=logging.DEBUG)


def main():
    if not os.path.exists(workspace_define.outputs_dir):
        os.makedirs(workspace_define.outputs_dir)

    font_config = configs.font_config_map[16]
    design_service.classify_px_design_files(font_config)
    design_service.verify_px_design_files(font_config)
    alphabet, design_file_paths_map = design_service.collect_px_design_files(font_config)
    font_service.make_px_fonts(font_config, alphabet, design_file_paths_map, ['woff2'])
    info_service.make_px_info_file(font_config, alphabet)
    info_service.make_px_alphabet_txt_file(font_config, alphabet)


if __name__ == '__main__':
    main()
