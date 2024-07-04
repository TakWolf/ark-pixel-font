from tools import configs
from tools.configs.font import FontConfig
from tools.services.font_service import DesignContext


def main():
    for font_size in configs.font_sizes:
        font_config = FontConfig.load(font_size)
        design_context = DesignContext.load(font_config)
        design_context.standardized()


if __name__ == '__main__':
    main()
