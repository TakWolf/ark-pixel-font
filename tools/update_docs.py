from tools import cli
from tools.services import publish_service


def main():
    cli.main(
        font_formats=[],
        info=True,
        image=True,
    )
    publish_service.update_docs()


if __name__ == '__main__':
    main()
