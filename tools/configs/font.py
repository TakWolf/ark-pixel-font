import yaml

from tools.configs import path_define, FontSize, WidthMode


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
    def load(font_size: FontSize) -> 'FontConfig':
        file_path = path_define.glyphs_dir.joinpath(str(font_size), 'config.yml')
        config_data = yaml.safe_load(file_path.read_bytes())

        layout_params = {}
        for width_mode, layout_param_data in config_data.items():
            layout_params[width_mode] = LayoutParam(
                layout_param_data['ascent'],
                layout_param_data['descent'],
                layout_param_data['x-height'],
                layout_param_data['cap-height'],
            )

        return FontConfig(font_size, layout_params)

    font_size: FontSize
    layout_params: dict[WidthMode, LayoutParam]

    def __init__(self, font_size: FontSize, layout_params: dict[WidthMode, LayoutParam]):
        self.font_size = font_size
        self.layout_params = layout_params

    @property
    def line_height(self) -> int:
        return self.layout_params['proportional'].line_height
