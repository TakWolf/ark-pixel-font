from typing import Any

import unidata_blocks
import yaml
from pixel_font_knife.cmap.file import CmapGlyphFile
from pixel_font_knife.glyph.file import GlyphFile
from pixel_font_knife.named.file import NamedGlyphFile

from tools.config import path_define


class CmapGlyphMetricRules:
    @staticmethod
    def parse(data: Any) -> CmapGlyphMetricRules:
        vertical_em_size_scales = data['vertical-em-size-scales']
        no_vertical_offset_y_adjustment_blocks = set(data['no-vertical-offset-y-adjustment']['blocks'])
        no_vertical_offset_y_adjustment_code_points = set(data['no-vertical-offset-y-adjustment']['code-points'])
        return CmapGlyphMetricRules(
            vertical_em_size_scales,
            no_vertical_offset_y_adjustment_blocks,
            no_vertical_offset_y_adjustment_code_points,
        )

    vertical_em_size_scales: dict[int, int]
    no_vertical_offset_y_adjustment_blocks: set[str]
    no_vertical_offset_y_adjustment_code_points: set[int]

    def __init__(
            self,
            vertical_em_size_scales: dict[int, int],
            no_vertical_offset_y_adjustment_blocks: set[str],
            no_vertical_offset_y_adjustment_code_points: set[int],
    ) -> None:
        self.vertical_em_size_scales = vertical_em_size_scales
        self.no_vertical_offset_y_adjustment_blocks = no_vertical_offset_y_adjustment_blocks
        self.no_vertical_offset_y_adjustment_code_points = no_vertical_offset_y_adjustment_code_points


class NamedGlyphMetricRules:
    @staticmethod
    def parse(data: Any) -> NamedGlyphMetricRules:
        no_vertical_offset_y_adjustment = set(data['no-vertical-offset-y-adjustment'])
        return NamedGlyphMetricRules(
            no_vertical_offset_y_adjustment,
        )

    no_vertical_offset_y_adjustment: set[str]

    def __init__(
            self,
            no_vertical_offset_y_adjustment: set[str],
    ) -> None:
        self.no_vertical_offset_y_adjustment = no_vertical_offset_y_adjustment


class GlyphMetricRules:
    @staticmethod
    def load() -> GlyphMetricRules:
        data = yaml.safe_load(path_define.CONFIGS_GLYPHS_DIR.joinpath('metrics.yaml').read_bytes())
        cmap_rules = CmapGlyphMetricRules.parse(data['cmap'])
        named_rules = NamedGlyphMetricRules.parse(data['named'])
        return GlyphMetricRules(
            cmap_rules,
            named_rules,
        )

    cmap_rules: CmapGlyphMetricRules
    named_rules: NamedGlyphMetricRules

    def __init__(
            self,
            cmap_rules: CmapGlyphMetricRules,
            named_rules: NamedGlyphMetricRules,
    ) -> None:
        self.cmap_rules = cmap_rules
        self.named_rules = named_rules

    def vertical_em_size_scale(self, glyph_file: GlyphFile) -> int:
        if isinstance(glyph_file, CmapGlyphFile):
            return self.cmap_rules.vertical_em_size_scales.get(glyph_file.code_point, 1)

        return 1

    def should_adjust_vertical_offset_y(self, glyph_file: GlyphFile) -> bool:
        if glyph_file.canvas.is_blank:
            return False

        if isinstance(glyph_file, CmapGlyphFile):
            code_point = glyph_file.code_point
            block = unidata_blocks.get_block_by_code_point(code_point)

            if (
                    block.name not in self.cmap_rules.no_vertical_offset_y_adjustment_blocks and
                    code_point not in self.cmap_rules.no_vertical_offset_y_adjustment_code_points
            ):
                return True

        if isinstance(glyph_file, NamedGlyphFile):
            if glyph_file.name_key not in self.named_rules.no_vertical_offset_y_adjustment:
                return True

        return False
