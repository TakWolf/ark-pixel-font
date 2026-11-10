from collections.abc import Callable
from functools import cache

import pytest

from tools.config.glyph.bitmap import BitmapGlobalRules, BitmapSizeRules
from tools.config.glyph.metric import MetricSizeRules
from tools.config.options import FontSize


@pytest.fixture(scope='session')
def bitmap_global_rules() -> BitmapGlobalRules:
    return BitmapGlobalRules.load()


@pytest.fixture(scope='session')
def load_bitmap_size_rules() -> Callable[[FontSize], BitmapSizeRules]:
    @cache
    def load(font_size: FontSize) -> BitmapSizeRules:
        return BitmapSizeRules.load(font_size)

    return load


@pytest.fixture(scope='session')
def load_metric_size_rules() -> Callable[[FontSize], MetricSizeRules]:
    @cache
    def load(font_size: FontSize) -> MetricSizeRules:
        return MetricSizeRules.load(font_size)

    return load
