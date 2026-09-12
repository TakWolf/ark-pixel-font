from tools import cli


def main() -> None:
    cli.main(
        cleanup=True,
        attachments={'all'},
    )


if __name__ == '__main__':
    main()
