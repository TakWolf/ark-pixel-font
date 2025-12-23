from typing import Literal, get_args

type FontSize = Literal[
    10,
    12,
    16,
]
font_sizes = list[FontSize](get_args(FontSize.__value__))

type WidthMode = Literal[
    'monospaced',
    'proportional',
]
width_modes = list[WidthMode](get_args(WidthMode.__value__))

type LanguageFlavor = Literal[
    'latin',
    'zh_cn',
    'zh_hk',
    'zh_tw',
    'zh_tr',
    'ja',
    'ko',
]
language_flavors = list[LanguageFlavor](get_args(LanguageFlavor.__value__))

type FontFormat = Literal[
    'otf',
    'otf.woff',
    'otf.woff2',
    'ttf',
    'ttf.woff',
    'ttf.woff2',
    'bdf',
    'pcf',
]
font_formats = list[FontFormat](get_args(FontFormat.__value__))

type Attachment = Literal[
    'release',
    'info',
    'alphabet',
    'html',
    'image',
]
attachments = list[Attachment](get_args(Attachment.__value__))
