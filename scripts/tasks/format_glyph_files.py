from scripts import configs
from scripts.services.font_service import DesignContext


def main():
    for font_config in configs.font_configs.values():
        design_context = DesignContext.load(font_config)
        design_context.standardize()


if __name__ == '__main__':
    main()
