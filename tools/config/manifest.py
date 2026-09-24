from tools.config import path_define
from tools.config.options import LanguageFlavor

SCOPE_MAPPING_FILE_PATHS = {
    'common': [
        path_define.CONFIGS_MAPPINGS_DIR.joinpath('common', '2E80-2EFF CJK Radicals Supplement.yaml'),
        path_define.CONFIGS_MAPPINGS_DIR.joinpath('common', '2F00-2FDF Kangxi Radicals.yaml'),
        path_define.CONFIGS_MAPPINGS_DIR.joinpath('common', 'F900-FAFF CJK Compatibility Ideographs.yaml'),
    ],
    'other': [
        path_define.CONFIGS_MAPPINGS_DIR.joinpath('other', '0080-00FF Latin-1 Supplement.yaml'),
    ],
}

KERNING_TEMPLATE_FILE_PATH = path_define.CONFIGS_KERNING_DIR.joinpath('default.yaml')

LANGUAGE_FLAVOR_TO_FONT_NAME: dict[LanguageFlavor, str] = {
    'latin': 'latin',
    'zh_hans': 'zh-Hans',
    'zh_hant': 'zh-Hant',
    'zh_hk': 'zh-HK',
    'zh_tw': 'zh-TW',
    'ja': 'ja',
    'ko': 'ko',
}

LANGUAGE_FLAVOR_TO_LOCALE: dict[LanguageFlavor, str] = {
    'latin': 'en',
    'zh_hans': 'zh-Hans',
    'zh_hant': 'zh-Hant',
    'zh_hk': 'zh-Hant-HK',
    'zh_tw': 'zh-Hant-TW',
    'ja': 'ja',
    'ko': 'ko',
}
