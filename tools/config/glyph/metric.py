from typing import Any

import unidata_blocks
import yaml
from pixel_font_knife.cmap.file import CmapGlyphFile
from pixel_font_knife.glyph.file import GlyphFile
from pixel_font_knife.named.file import NamedGlyphFile

from tools.config import paths
from tools.config.glyph.selector import CmapSelector, NamedSelector, FileIdSelector
from tools.config.options import FontSize, WidthMode


class CmapMetricGlobalRules:
    @staticmethod
    def parse(data: Any) -> CmapMetricGlobalRules:
        vertical_em_scales = data['vertical-em-scales']
        skip_vertical_adjustment = CmapSelector.parse(data['skip-vertical-adjustment'])
        return CmapMetricGlobalRules(
            vertical_em_scales,
            skip_vertical_adjustment,
        )

    vertical_em_scales: dict[int, int]
    skip_vertical_adjustment: CmapSelector

    def __init__(
            self,
            vertical_em_scales: dict[int, int],
            skip_vertical_adjustment: CmapSelector,
    ) -> None:
        self.vertical_em_scales = vertical_em_scales
        self.skip_vertical_adjustment = skip_vertical_adjustment


class NamedMetricGlobalRules:
    @staticmethod
    def parse(data: Any) -> NamedMetricGlobalRules:
        skip_vertical_adjustment = NamedSelector.parse(data['skip-vertical-adjustment'])
        return NamedMetricGlobalRules(
            skip_vertical_adjustment,
        )

    skip_vertical_adjustment: NamedSelector

    def __init__(
            self,
            skip_vertical_adjustment: NamedSelector,
    ) -> None:
        self.skip_vertical_adjustment = skip_vertical_adjustment


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

    def should_skip_vertical_adjustment(self, glyph_file: GlyphFile) -> bool:
        if isinstance(glyph_file, CmapGlyphFile):
            code_point = glyph_file.code_point
            block = unidata_blocks.get_block_by_code_point(code_point)
            if (
                    block.name in self.cmap_global_rules.skip_vertical_adjustment.blocks or
                    code_point in self.cmap_global_rules.skip_vertical_adjustment.code_points
            ):
                return True

        if isinstance(glyph_file, NamedGlyphFile):
            if glyph_file.name_key in self.named_global_rules.skip_vertical_adjustment.name_keys:
                return True

        return False


class CmapMetricSizeRules:
    @staticmethod
    def parse(data: Any) -> CmapMetricSizeRules:
        skip_vertical_adjustment = FileIdSelector.parse(data['skip-vertical-adjustment'])
        return CmapMetricSizeRules(
            skip_vertical_adjustment,
        )

    skip_vertical_adjustment: FileIdSelector

    def __init__(
            self,
            skip_vertical_adjustment: FileIdSelector,
    ) -> None:
        self.skip_vertical_adjustment = skip_vertical_adjustment


class NamedMetricSizeRules:
    @staticmethod
    def parse(data: Any) -> NamedMetricSizeRules:
        skip_vertical_adjustment = FileIdSelector.parse(data['skip-vertical-adjustment'])
        return NamedMetricSizeRules(
            skip_vertical_adjustment,
        )

    skip_vertical_adjustment: FileIdSelector

    def __init__(
            self,
            skip_vertical_adjustment: FileIdSelector,
    ) -> None:
        self.skip_vertical_adjustment = skip_vertical_adjustment


class MetricSizeRules:
    @staticmethod
    def load(font_size: FontSize) -> MetricSizeRules:
        data = yaml.safe_load(paths.CONFIGS_GLYPHS_DIR.joinpath('metrics', f'{font_size}px.yaml').read_bytes())
        cmap_size_rules = CmapMetricSizeRules.parse(data['cmap'])
        named_size_rules = NamedMetricSizeRules.parse(data['named'])
        return MetricSizeRules(
            cmap_size_rules,
            named_size_rules,
        )

    cmap_size_rules: CmapMetricSizeRules
    named_size_rules: NamedMetricSizeRules

    def __init__(
            self,
            cmap_size_rules: CmapMetricSizeRules,
            named_size_rules: NamedMetricSizeRules,
    ) -> None:
        self.cmap_size_rules = cmap_size_rules
        self.named_size_rules = named_size_rules

    def should_skip_vertical_adjustment(self, width_mode: WidthMode, glyph_file: GlyphFile) -> bool:
        if isinstance(glyph_file, CmapGlyphFile):
            file_id = f'0x{glyph_file.code_point:04X}'
            if glyph_file.flavors:
                file_id = f'{file_id} {','.join(glyph_file.flavors)}'

            if (
                    f'{width_mode}/{file_id}' in self.cmap_size_rules.skip_vertical_adjustment.file_ids or
                    f'common/{file_id}' in self.cmap_size_rules.skip_vertical_adjustment.file_ids
            ):
                return True

        if isinstance(glyph_file, NamedGlyphFile):
            file_id = glyph_file.name_key
            if glyph_file.flavors:
                file_id = f'{file_id} {','.join(glyph_file.flavors)}'

            if (
                    f'{width_mode}/{file_id}' in self.named_size_rules.skip_vertical_adjustment.file_ids or
                    f'common/{file_id}' in self.named_size_rules.skip_vertical_adjustment.file_ids
            ):
                return True

        return False
