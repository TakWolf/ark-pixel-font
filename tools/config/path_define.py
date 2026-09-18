from pathlib import Path

PROJECT_ROOT_DIR = Path(__file__).parents[2]

ASSETS_DIR = PROJECT_ROOT_DIR.joinpath('assets')

CONFIGS_DIR = ASSETS_DIR.joinpath('configs')
CONFIGS_FONTS_DIR = CONFIGS_DIR.joinpath('fonts')
CONFIGS_MAPPINGS_DIR = CONFIGS_DIR.joinpath('mappings')
CONFIGS_KERNING_DIR = CONFIGS_DIR.joinpath('kerning')
CONFIGS_FEATURES_DIR = CONFIGS_DIR.joinpath('features')

GLYPHS_DIR = ASSETS_DIR.joinpath('glyphs')
TEMPLATES_DIR = ASSETS_DIR.joinpath('templates')
IMAGES_DIR = ASSETS_DIR.joinpath('images')

BUILD_DIR = PROJECT_ROOT_DIR.joinpath('build')
OUTPUTS_DIR = BUILD_DIR.joinpath('outputs')
RELEASES_DIR = BUILD_DIR.joinpath('releases')

DOCS_DIR = PROJECT_ROOT_DIR.joinpath('docs')
