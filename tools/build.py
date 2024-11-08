from tools import cli


def main():
    cli.main(
        cleanup=True,
        attachments={'all'},
    )


if __name__ == '__main__':
    main()
