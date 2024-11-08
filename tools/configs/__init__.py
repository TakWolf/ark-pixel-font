from typing import Literal, get_args

version = '2024.11.04'

type FontSize = Literal[10, 12, 16]
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

type FontFormat = Literal['otf', 'ttf', 'woff2', 'bdf', 'pcf', 'otc', 'ttc']
font_formats = list[FontFormat](get_args(FontFormat.__value__))

font_collection_formats = ['otc', 'ttc']

type Attachment = Literal[
    'release',
    'info',
    'alphabet',
    'html',
    'image',
]
attachments = list[Attachment](get_args(Attachment.__value__))
