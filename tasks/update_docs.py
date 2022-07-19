import logging
import os

import configs
from configs import workspace_define
from services import publish_service

logging.basicConfig(level=logging.DEBUG)


def main():
    if not os.path.exists(workspace_define.docs_dir):
        os.makedirs(workspace_define.docs_dir)

    for font_config in configs.font_configs:
        publish_service.copy_px_docs_files(font_config)
    publish_service.copy_docs_files()


if __name__ == '__main__':
    main()
