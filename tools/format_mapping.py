from tools.configs import path_define
from tools.services import format_service


def main():
    format_service.format_mapping(path_define.assets_dir.joinpath('cjk-radicals-supplement-mapping.yml'))
    format_service.format_mapping(path_define.assets_dir.joinpath('kangxi-radicals-mapping.yml'))


if __name__ == '__main__':
    main()
