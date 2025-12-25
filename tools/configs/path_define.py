from pathlib import Path

project_root_dir = Path(__file__).parent.joinpath('..', '..').resolve()

assets_dir = project_root_dir.joinpath('assets')
configs_dir = assets_dir.joinpath('configs')
glyphs_dir = assets_dir.joinpath('glyphs')
mappings_dir = assets_dir.joinpath('mappings')
kernings_dir = assets_dir.joinpath('kernings')
templates_dir = assets_dir.joinpath('templates')
images_dir = assets_dir.joinpath('images')

build_dir = project_root_dir.joinpath('build')
outputs_dir = build_dir.joinpath('outputs')
releases_dir = build_dir.joinpath('releases')

docs_dir = project_root_dir.joinpath('docs')
