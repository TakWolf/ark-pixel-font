from collections.abc import Callable
from functools import cache

import pytest

from tools.config.options import FontSize
from tools.configs import FontConfig


@pytest.fixture(scope='session')
def load_font_config() -> Callable[[FontSize], FontConfig]:
    @cache
    def load(font_size: FontSize) -> FontConfig:
        return FontConfig.load(font_size)

    return load
