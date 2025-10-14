from typing import Any

import yaml

from tools.configs import path_define, options
from tools.configs.options import FontSize, WidthMode


class LayoutMetric:
    @staticmethod
    def parse(data: Any) -> LayoutMetric:
        baseline = data['baseline']
        ascent = data['ascent']
        descent = data['descent']
        x_height = data['x-height']
        cap_height = data['cap-height']
        underline_position = data['underline-position']
        strikeout_position = data['strikeout-position']
        return LayoutMetric(
            baseline,
            ascent,
            descent,
            x_height,
            cap_height,
            underline_position,
            strikeout_position,
        )

    baseline: int
    ascent: int
    descent: int
    x_height: int
    cap_height: int
    underline_position: int
    strikeout_position: int

    def __init__(
            self,
            baseline: int,
            ascent: int,
            descent: int,
            x_height: int,
            cap_height: int,
            underline_position: int,
            strikeout_position: int,
    ):
        self.baseline = baseline
        self.ascent = ascent
        self.descent = descent
        self.x_height = x_height
        self.cap_height = cap_height
        self.underline_position = underline_position
        self.strikeout_position = strikeout_position

    @property
    def line_height(self) -> int:
        return self.ascent - self.descent


class FontConfig:
    @staticmethod
    def load(font_size: FontSize) -> FontConfig:
        data = yaml.safe_load(path_define.configs_dir.joinpath(f'font-{font_size}px.yml').read_bytes())
        assert font_size == data['font-size']
        canvas_size = data['canvas-size']
        layout_metrics = {width_mode: LayoutMetric.parse(data[width_mode]) for width_mode in options.width_modes}
        return FontConfig(
            font_size,
            canvas_size,
            layout_metrics,
        )

    font_size: FontSize
    canvas_size: int
    layout_metrics: dict[WidthMode, LayoutMetric]

    def __init__(
            self,
            font_size: FontSize,
            canvas_size: int,
            layout_metrics: dict[WidthMode, LayoutMetric],
    ):
        self.font_size = font_size
        self.canvas_size = canvas_size
        self.layout_metrics = layout_metrics

    @property
    def line_height(self) -> int:
        return self.layout_metrics['proportional'].line_height
