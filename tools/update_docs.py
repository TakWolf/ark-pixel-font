from tools import cli
from tools.services import publish_service


def main():
    cli.main(
        font_formats=set(),
        attachments={'info', 'image'},
    )
    publish_service.update_docs()


if __name__ == '__main__':
    main()
