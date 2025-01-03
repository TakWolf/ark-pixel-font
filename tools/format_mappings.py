from tools.configs import path_define
from tools.services import format_service


def main():
    for file_path in path_define.mappings_dir.iterdir():
        if file_path.suffix != '.yml':
            continue
        format_service.format_mapping(file_path)


if __name__ == '__main__':
    main()
