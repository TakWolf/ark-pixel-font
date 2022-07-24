import logging
import os

from configs import path_define
from services import publish_service

logging.basicConfig(level=logging.DEBUG)


def main():
    if not os.path.exists(path_define.docs_dir):
        os.makedirs(path_define.docs_dir)

    publish_service.update_docs()


if __name__ == '__main__':
    main()
