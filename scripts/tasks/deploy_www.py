import logging

from scripts.services import publish_service

logging.basicConfig(level=logging.DEBUG)


def main():
    publish_service.update_www()
    publish_service.deploy_www()


if __name__ == '__main__':
    main()
