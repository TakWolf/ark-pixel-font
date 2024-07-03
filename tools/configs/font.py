from tools import configs
from tools.configs import path_define
from tools.utils import fs_util


class LayoutParam:
    ascent: int
    descent: int
    x_height: int
    cap_height: int

    def __init__(self, ascent: int, descent: int, x_height: int, cap_height: int):
        self.ascent = ascent
        self.descent = descent
        self.x_height = x_height
        self.cap_height = cap_height

    @property
    def line_height(self) -> int:
        return self.ascent - self.descent


class FontConfig:
    @staticmethod
    def load_all() -> dict[int, 'FontConfig']:
        return {font_size: FontConfig.load(font_size) for font_size in configs.font_sizes}

    @staticmethod
    def load(font_size: int) -> 'FontConfig':
        file_path = path_define.glyphs_dir.joinpath(str(font_size), 'config.yml')
        config_data = fs_util.read_yaml(file_path)

        layout_params = {}
        for width_mode, layout_param_data in config_data.items():
            layout_params[width_mode] = LayoutParam(
                layout_param_data['ascent'],
                layout_param_data['descent'],
                layout_param_data['x-height'],
                layout_param_data['cap-height'],
            )

        return FontConfig(font_size, layout_params)

    font_size: int
    layout_params: dict[str, LayoutParam]

    def __init__(self, font_size: int, layout_params: dict[str, LayoutParam]):
        self.font_size = font_size
        self.layout_params = layout_params

    @property
    def line_height(self) -> int:
        return self.layout_params['proportional'].line_height
