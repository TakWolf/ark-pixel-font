import logging
import os
import shutil

from configs import path_define
from services import publish_service

logging.basicConfig(level=logging.DEBUG)


def main():
    if os.path.exists(path_define.www_dir):
        shutil.rmtree(path_define.www_dir)
    shutil.copytree(path_define.www_static_dir, path_define.www_dir)

    publish_service.update_www()
    publish_service.deploy_www()


if __name__ == '__main__':
    main()
