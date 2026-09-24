from tools import build_fonts, build_site, build_artwork


def main() -> None:
    build_fonts.main(cleanup=True)
    build_site.main()
    build_artwork.main()


if __name__ == '__main__':
    main()
