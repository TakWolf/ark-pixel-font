import logging
import os

from configs import workspace_define
from services import publish_service

logging.basicConfig(level=logging.DEBUG)


def main():
    if not os.path.exists(workspace_define.docs_dir):
        os.makedirs(workspace_define.docs_dir)

    publish_service.update_docs()


if __name__ == '__main__':
    main()
