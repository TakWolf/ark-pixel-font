from scripts.configs import FontConfig
from scripts.services.font_service import DesignContext


def main():
    font_configs = FontConfig.load_all()
    for font_config in font_configs.values():
        design_context = DesignContext.load(font_config)
        design_context.standardized()


if __name__ == '__main__':
    main()
