from typing import Any

import yaml

from tools.config import paths
from tools.config.glyph.selector import CmapSelector, NamedSelector
from tools.config.options import GlyphScope


class CmapFlavorGlobalRules:
    @staticmethod
    def parse(data: Any) -> CmapFlavorGlobalRules:
        allow_missing_default = {
            glyph_scope: set(code_points)
            for glyph_scope, code_points in data['allow-missing-default'].items()
        }
        return CmapFlavorGlobalRules(
            allow_missing_default,
        )

    allow_missing_default: dict[GlyphScope, set[int]]

    def __init__(
            self,
            allow_missing_default: dict[GlyphScope, set[int]],
    ) -> None:
        self.allow_missing_default = allow_missing_default


class CmapPaddingGlobalRules:
    @staticmethod
    def parse(data: Any) -> CmapPaddingGlobalRules:
        allow_no_top_and_right = CmapSelector.parse(data.get('allow-no-top-and-right', {}))
        allow_no_top_only = CmapSelector.parse(data.get('allow-no-top-only', {}))
        allow_no_right_only = CmapSelector.parse(data.get('allow-no-right-only', {}))
        return CmapPaddingGlobalRules(
            allow_no_top_and_right,
            allow_no_top_only,
            allow_no_right_only,
        )

    allow_no_top_and_right: CmapSelector
    allow_no_top_only: CmapSelector
    allow_no_right_only: CmapSelector

    def __init__(
            self,
            allow_no_top_and_right: CmapSelector,
            allow_no_top_only: CmapSelector,
            allow_no_right_only: CmapSelector,
    ) -> None:
        self.allow_no_top_and_right = allow_no_top_and_right
        self.allow_no_top_only = allow_no_top_only
        self.allow_no_right_only = allow_no_right_only


class CmapDimensionsGlobalRules:
    @staticmethod
    def parse(data: Any) -> CmapDimensionsGlobalRules:
        east_asian_width_treated_as = data['east-asian-width-treated-as']
        return CmapDimensionsGlobalRules(
            east_asian_width_treated_as,
        )

    east_asian_width_treated_as: dict[int, str]

    def __init__(
            self,
            east_asian_width_treated_as: dict[int, str],
    ) -> None:
        self.east_asian_width_treated_as = east_asian_width_treated_as


class CmapBitmapGlobalRules:
    @staticmethod
    def parse(data: Any) -> CmapBitmapGlobalRules:
        flavor_global_rules = CmapFlavorGlobalRules.parse(data['flavor'])
        padding_global_rules = CmapPaddingGlobalRules.parse(data['padding'])
        dimensions_global_rules = CmapDimensionsGlobalRules.parse(data['dimensions'])
        return CmapBitmapGlobalRules(
            flavor_global_rules,
            padding_global_rules,
            dimensions_global_rules,
        )

    flavor_global_rules: CmapFlavorGlobalRules
    padding_global_rules: CmapPaddingGlobalRules
    dimensions_global_rules: CmapDimensionsGlobalRules

    def __init__(
            self,
            flavor_global_rules: CmapFlavorGlobalRules,
            padding_global_rules: CmapPaddingGlobalRules,
            dimensions_global_rules: CmapDimensionsGlobalRules,
    ) -> None:
        self.flavor_global_rules = flavor_global_rules
        self.padding_global_rules = padding_global_rules
        self.dimensions_global_rules = dimensions_global_rules


class NamedPaddingGlobalRules:
    @staticmethod
    def parse(data: Any) -> NamedPaddingGlobalRules:
        allow_no_top_and_right = NamedSelector.parse(data.get('allow-no-top-and-right', {}))
        allow_no_top_only = NamedSelector.parse(data.get('allow-no-top-only', {}))
        allow_no_right_only = NamedSelector.parse(data.get('allow-no-right-only', {}))
        return NamedPaddingGlobalRules(
            allow_no_top_and_right,
            allow_no_top_only,
            allow_no_right_only,
        )

    allow_no_top_and_right: NamedSelector
    allow_no_top_only: NamedSelector
    allow_no_right_only: NamedSelector

    def __init__(
            self,
            allow_no_top_and_right: NamedSelector,
            allow_no_top_only: NamedSelector,
            allow_no_right_only: NamedSelector,
    ) -> None:
        self.allow_no_top_and_right = allow_no_top_and_right
        self.allow_no_top_only = allow_no_top_only
        self.allow_no_right_only = allow_no_right_only


class NamedBitmapGlobalRules:
    @staticmethod
    def parse(data: Any) -> NamedBitmapGlobalRules:
        padding_global_rules = NamedPaddingGlobalRules.parse(data['padding'])
        return NamedBitmapGlobalRules(
            padding_global_rules,
        )

    padding_global_rules: NamedPaddingGlobalRules

    def __init__(
            self,
            padding_global_rules: NamedPaddingGlobalRules,
    ) -> None:
        self.padding_global_rules = padding_global_rules


class BitmapGlobalRules:
    @staticmethod
    def load() -> BitmapGlobalRules:
        data = yaml.safe_load(paths.CONFIGS_GLYPHS_DIR.joinpath('bitmaps', 'global.yaml').read_bytes())
        cmap_global_rules = CmapBitmapGlobalRules.parse(data['cmap'])
        named_global_rules = NamedBitmapGlobalRules.parse(data['named'])
        return BitmapGlobalRules(
            cmap_global_rules,
            named_global_rules,
        )

    cmap_global_rules: CmapBitmapGlobalRules
    named_global_rules: NamedBitmapGlobalRules

    def __init__(
            self,
            cmap_global_rules: CmapBitmapGlobalRules,
            named_global_rules: NamedBitmapGlobalRules,
    ) -> None:
        self.cmap_global_rules = cmap_global_rules
        self.named_global_rules = named_global_rules
