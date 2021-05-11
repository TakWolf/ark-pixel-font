import logging

from configs import workspace_define, font_configs
from services import design_service
from utils import fs_util

logging.basicConfig(level=logging.DEBUG)


def main():
    fs_util.cleanup_dir(workspace_define.outputs_dir)
    for font_config in font_configs:
        design_service.classify_design_files(font_config)
        design_service.verify_design_files(font_config)


if __name__ == '__main__':
    main()
