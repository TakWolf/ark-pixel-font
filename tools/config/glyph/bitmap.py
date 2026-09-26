from typing import Any

import yaml

from tools.config import path_define
from tools.config.options import GlyphScope


class CmapGlyphFlavorRules:
    @staticmethod
    def parse(data: Any) -> CmapGlyphFlavorRules:
        allow_missing_default = {
            glyph_scope: set(code_points)
            for glyph_scope, code_points in data['allow-missing-default'].items()
        }
        return CmapGlyphFlavorRules(
            allow_missing_default,
        )

    allow_missing_default: dict[GlyphScope, set[int]]

    def __init__(
            self,
            allow_missing_default: dict[GlyphScope, set[int]],
    ) -> None:
        self.allow_missing_default = allow_missing_default


class CmapGlyphPaddingRules:
    @staticmethod
    def parse(data: Any) -> CmapGlyphPaddingRules:
        allow_no_top_blocks = set()
        allow_no_top_blocks.update(data['allow-no-top-and-right'].get('blocks', ()))
        allow_no_top_blocks.update(data['allow-no-top-only'].get('blocks', ()))

        allow_no_top_code_points = set()
        allow_no_top_code_points.update(data['allow-no-top-and-right'].get('code-points', ()))
        allow_no_top_code_points.update(data['allow-no-top-only'].get('code-points', ()))

        allow_no_right_blocks = set()
        allow_no_right_blocks.update(data['allow-no-top-and-right'].get('blocks', ()))
        allow_no_right_blocks.update(data['allow-no-right-only'].get('blocks', ()))

        allow_no_right_code_points = set()
        allow_no_right_code_points.update(data['allow-no-top-and-right'].get('code-points', ()))
        allow_no_right_code_points.update(data['allow-no-right-only'].get('code-points', ()))

        return CmapGlyphPaddingRules(
            allow_no_top_blocks,
            allow_no_top_code_points,
            allow_no_right_blocks,
            allow_no_right_code_points,
        )

    allow_no_top_blocks: set[str]
    allow_no_top_code_points: set[int]
    allow_no_right_blocks: set[str]
    allow_no_right_code_points: set[int]

    def __init__(
            self,
            allow_no_top_blocks: set[str],
            allow_no_top_code_points: set[int],
            allow_no_right_blocks: set[str],
            allow_no_right_code_points: set[int],
    ) -> None:
        self.allow_no_top_blocks = allow_no_top_blocks
        self.allow_no_top_code_points = allow_no_top_code_points
        self.allow_no_right_blocks = allow_no_right_blocks
        self.allow_no_right_code_points = allow_no_right_code_points


class CmapGlyphDimensionsRules:
    @staticmethod
    def parse(data: Any) -> CmapGlyphDimensionsRules:
        east_asian_width_treated_as = data['east-asian-width-treated-as']
        return CmapGlyphDimensionsRules(
            east_asian_width_treated_as,
        )

    east_asian_width_treated_as: dict[int, str]

    def __init__(
            self,
            east_asian_width_treated_as: dict[int, str],
    ) -> None:
        self.east_asian_width_treated_as = east_asian_width_treated_as


class CmapGlyphBitmapRules:
    @staticmethod
    def parse(data: Any) -> CmapGlyphBitmapRules:
        flavor_rules = CmapGlyphFlavorRules.parse(data['flavor'])
        padding_rules = CmapGlyphPaddingRules.parse(data['padding'])
        dimensions_rules = CmapGlyphDimensionsRules.parse(data['dimensions'])
        return CmapGlyphBitmapRules(
            flavor_rules,
            padding_rules,
            dimensions_rules,
        )

    flavor_rules: CmapGlyphFlavorRules
    padding_rules: CmapGlyphPaddingRules
    dimensions_rules: CmapGlyphDimensionsRules

    def __init__(
            self,
            flavor_rules: CmapGlyphFlavorRules,
            padding_rules: CmapGlyphPaddingRules,
            dimensions_rules: CmapGlyphDimensionsRules,
    ) -> None:
        self.flavor_rules = flavor_rules
        self.padding_rules = padding_rules
        self.dimensions_rules = dimensions_rules


class GlyphBitmapRules:
    @staticmethod
    def load() -> GlyphBitmapRules:
        data = yaml.safe_load(path_define.CONFIGS_GLYPHS_DIR.joinpath('bitmaps.yaml').read_bytes())
        cmap_rules = CmapGlyphBitmapRules.parse(data['cmap'])
        return GlyphBitmapRules(
            cmap_rules,
        )

    cmap_rules: CmapGlyphBitmapRules

    def __init__(
            self,
            cmap_rules: CmapGlyphBitmapRules,
    ) -> None:
        self.cmap_rules = cmap_rules
