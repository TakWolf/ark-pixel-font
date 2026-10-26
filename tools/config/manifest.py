from tools.config import paths
from tools.config.options import LanguageFlavor

SCOPE_MAPPING_FILE_PATHS = {
    'common': [
        paths.CONFIGS_MAPPINGS_DIR.joinpath('common', '2E80-2EFF CJK Radicals Supplement.yaml'),
        paths.CONFIGS_MAPPINGS_DIR.joinpath('common', '2F00-2FDF Kangxi Radicals.yaml'),
        paths.CONFIGS_MAPPINGS_DIR.joinpath('common', 'F900-FAFF CJK Compatibility Ideographs.yaml'),
    ],
    'other': [
        paths.CONFIGS_MAPPINGS_DIR.joinpath('other', '0080-00FF Latin-1 Supplement.yaml'),
    ],
}

KERNING_TEMPLATE_FILE_PATH = paths.CONFIGS_KERNING_DIR.joinpath('default.yaml')

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
