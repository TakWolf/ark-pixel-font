import logging

from services import publish_service

logging.basicConfig(level=logging.DEBUG)


def main():
    publish_service.update_docs()


if __name__ == '__main__':
    main()
