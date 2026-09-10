from typing import Literal, get_args

type FontSize = Literal[
    10,
    12,
]
FONT_SIZES = list[FontSize](get_args(FontSize.__value__))

type WidthMode = Literal[
    'monospaced',
    'proportional',
]
WIDTH_MODES = list[WidthMode](get_args(WidthMode.__value__))

type LanguageFlavor = Literal[
    'latin',
    'zh_cn',
    'zh_hk',
    'zh_tw',
    'zh_tr',
    'ja',
    'ko',
]
LANGUAGE_FLAVORS = list[LanguageFlavor](get_args(LanguageFlavor.__value__))

type FontFormat = Literal[
    'otf',
    'otf.woff',
    'otf.woff2',
    'ttf',
    'ttf.woff',
    'ttf.woff2',
    'ms.bitmap.ttf',
    'otb',
    'dfont',
    'bdf',
    'pcf',
]
FONT_FORMATS = list[FontFormat](get_args(FontFormat.__value__))

type Attachment = Literal[
    'release',
    'info',
    'alphabet',
    'html',
    'image',
]
ATTACHMENTS = list[Attachment](get_args(Attachment.__value__))
