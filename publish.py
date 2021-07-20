import logging

from configs import workspace_define, font_configs
from services import publish_service
from utils import fs_util

logging.basicConfig(level=logging.DEBUG)


def main():
    fs_util.cleanup_dir(workspace_define.releases_dir)
    for font_config in font_configs:
        publish_service.make_release_zips(font_config)


if __name__ == '__main__':
    main()
