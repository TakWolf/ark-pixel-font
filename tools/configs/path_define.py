from pathlib import Path

PROJECT_ROOT_DIR = Path(__file__).parent.joinpath('..', '..').resolve()

ASSETS_DIR = PROJECT_ROOT_DIR.joinpath('assets')
CONFIGS_DIR = ASSETS_DIR.joinpath('configs')
GLYPHS_DIR = ASSETS_DIR.joinpath('glyphs')
MAPPINGS_DIR = ASSETS_DIR.joinpath('mappings')
KERNINGS_DIR = ASSETS_DIR.joinpath('kernings')
TEMPLATES_DIR = ASSETS_DIR.joinpath('templates')
IMAGES_DIR = ASSETS_DIR.joinpath('images')

BUILD_DIR = PROJECT_ROOT_DIR.joinpath('build')
OUTPUTS_DIR = BUILD_DIR.joinpath('outputs')
RELEASES_DIR = BUILD_DIR.joinpath('releases')

DOCS_DIR = PROJECT_ROOT_DIR.joinpath('docs')
