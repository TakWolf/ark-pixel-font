from scripts import configs
from scripts.configs import path_define
from scripts.utils import fs_util


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
        file_path = path_define.glyphs_dir.joinpath(str(font_size), 'config.toml')
        config_data = fs_util.read_toml(file_path)['font']
        assert font_size == config_data['size'], f"Config 'size' error: '{file_path}'"

        layout_params = {}
        for width_mode in configs.width_modes:
            layout_param_data = config_data[width_mode]
            layout_param = LayoutParam(
                layout_param_data['ascent'],
                layout_param_data['descent'],
                layout_param_data['x_height'],
                layout_param_data['cap_height'],
            )
            if width_mode == 'monospaced':
                assert layout_param.line_height == font_size, f"Config 'monospaced.line_height' error: '{file_path}'"
            else:
                assert (layout_param.line_height - font_size) % 2 == 0, f"Config 'proportional.line_height' error: '{file_path}'"
            layout_params[width_mode] = layout_param

        return FontConfig(font_size, layout_params)

    font_size: int
    layout_params: dict[str, LayoutParam]

    def __init__(self, font_size: int, layout_params: dict[str, LayoutParam]):
        self.font_size = font_size
        self.layout_params = layout_params

    @property
    def line_height(self) -> int:
        return self.layout_params['proportional'].line_height
