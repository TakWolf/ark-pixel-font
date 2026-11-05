from typing import Any

import unidata_blocks
import yaml
from pixel_font_knife.cmap.file import CmapGlyphFile
from pixel_font_knife.glyph.file import GlyphFile
from pixel_font_knife.named.file import NamedGlyphFile

from tools.config import paths
from tools.config.glyph.selector import CmapSelector, NamedSelector


class CmapMetricGlobalRules:
    @staticmethod
    def parse(data: Any) -> CmapMetricGlobalRules:
        vertical_em_scales = data['vertical-em-scales']
        no_vertical_adjustment = CmapSelector.parse(data['no-vertical-adjustment'])
        return CmapMetricGlobalRules(
            vertical_em_scales,
            no_vertical_adjustment,
        )

    vertical_em_scales: dict[int, int]
    no_vertical_adjustment: CmapSelector

    def __init__(
            self,
            vertical_em_scales: dict[int, int],
            no_vertical_adjustment: CmapSelector,
    ) -> None:
        self.vertical_em_scales = vertical_em_scales
        self.no_vertical_adjustment = no_vertical_adjustment


class NamedMetricGlobalRules:
    @staticmethod
    def parse(data: Any) -> NamedMetricGlobalRules:
        no_vertical_adjustment = NamedSelector.parse(data['no-vertical-adjustment'])
        return NamedMetricGlobalRules(
            no_vertical_adjustment,
        )

    no_vertical_adjustment: NamedSelector

    def __init__(
            self,
            no_vertical_adjustment: NamedSelector,
    ) -> None:
        self.no_vertical_adjustment = no_vertical_adjustment


class MetricGlobalRules:
    @staticmethod
    def load() -> MetricGlobalRules:
        data = yaml.safe_load(paths.CONFIGS_GLYPHS_DIR.joinpath('metrics', 'global.yaml').read_bytes())
        cmap_global_rules = CmapMetricGlobalRules.parse(data['cmap'])
        named_global_rules = NamedMetricGlobalRules.parse(data['named'])
        return MetricGlobalRules(
            cmap_global_rules,
            named_global_rules,
        )

    cmap_global_rules: CmapMetricGlobalRules
    named_global_rules: NamedMetricGlobalRules

    def __init__(
            self,
            cmap_global_rules: CmapMetricGlobalRules,
            named_global_rules: NamedMetricGlobalRules,
    ) -> None:
        self.cmap_global_rules = cmap_global_rules
        self.named_global_rules = named_global_rules

    def get_vertical_em_scale(self, glyph_file: GlyphFile) -> int:
        if isinstance(glyph_file, CmapGlyphFile):
            return self.cmap_global_rules.vertical_em_scales.get(glyph_file.code_point, 1)
        return 1

    def should_adjust_vertical_offset_y(self, glyph_file: GlyphFile) -> bool:
        if isinstance(glyph_file, CmapGlyphFile):
            code_point = glyph_file.code_point
            block = unidata_blocks.get_block_by_code_point(code_point)
            if (
                    block.name not in self.cmap_global_rules.no_vertical_adjustment.blocks and
                    code_point not in self.cmap_global_rules.no_vertical_adjustment.code_points
            ):
                return True

        if isinstance(glyph_file, NamedGlyphFile):
            if glyph_file.name_key not in self.named_global_rules.no_vertical_adjustment.name_keys:
                return True

        return False
