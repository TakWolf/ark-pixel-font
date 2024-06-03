import datetime

from scripts.configs.deploy import GitDeployConfig
from scripts.configs.font import FontConfig

font_version = '2024.05.12'

font_version_time = datetime.datetime.fromisoformat(f'{font_version.replace('.', '-')}T00:00:00Z')

font_sizes = [10, 12, 16]

font_formats = ['otf', 'woff2', 'ttf', 'bdf', 'pcf']

font_collection_formats = ['otc', 'ttc']

width_modes = [
    'monospaced',
    'proportional',
]

language_flavors = [
    'latin',
    'zh_cn',
    'zh_hk',
    'zh_tw',
    'zh_tr',
    'ja',
    'ko',
]

locale_to_language_flavor = {
    'en': 'latin',
    'zh-cn': 'zh_cn',
    'zh-hk': 'zh_hk',
    'zh-tw': 'zh_tw',
    'zh-tr': 'zh_tr',
    'ja': 'ja',
    'ko': 'ko',
}

git_deploy_configs = [GitDeployConfig(
    url='git@github.com:TakWolf/ark-pixel-font.git',
    remote_name='github',
    branch_name='gh-pages',
)]
