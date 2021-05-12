import logging

from configs import workspace_define, font_configs
from services import design_service, font_service, info_service
from utils import fs_util

logging.basicConfig(level=logging.DEBUG)


def main():
    fs_util.cleanup_dir(workspace_define.outputs_dir)
    for font_config in font_configs:
        design_service.classify_design_files(font_config)
        design_service.verify_design_files(font_config)
        whole_alphabet, language_flavor_alphabet_map, design_file_paths_map = design_service.collect_available_design(font_config)
        font_service.make_fonts(font_config, language_flavor_alphabet_map, design_file_paths_map)
        info_service.make_info_file(font_config, whole_alphabet)


if __name__ == '__main__':
    main()
