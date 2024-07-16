from tools import cli


def main():
    cli.main(
        cleanup=True,
        release=True,
        all_attachments=True,
    )


if __name__ == '__main__':
    main()
