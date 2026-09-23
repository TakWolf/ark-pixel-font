from pixel_font_knife.cmap.kerning.template import CmapKerningTemplate
from pixel_font_knife.cmap.mapping.mapping import CmapMapping

from tools.config import path_define, options
from tools.configs.font import FontConfig

FONT_CONFIGS = {font_size: FontConfig.load(font_size) for font_size in options.FONT_SIZES}

MAPPINGS = [
    CmapMapping.load_yaml(
        path_define.CONFIGS_MAPPINGS_DIR.joinpath('0080-00FF Latin-1 Supplement.yaml'),
        allowed_flavors=options.LANGUAGE_FLAVORS,
    ),
    CmapMapping.load_yaml(
        path_define.CONFIGS_MAPPINGS_DIR.joinpath('2E80-2EFF CJK Radicals Supplement.yaml'),
        allowed_flavors=options.LANGUAGE_FLAVORS,
    ),
    CmapMapping.load_yaml(
        path_define.CONFIGS_MAPPINGS_DIR.joinpath('2F00-2FDF Kangxi Radicals.yaml'),
        allowed_flavors=options.LANGUAGE_FLAVORS,
    ),
    CmapMapping.load_yaml(
        path_define.CONFIGS_MAPPINGS_DIR.joinpath('F900-FAFF CJK Compatibility Ideographs.yaml'),
        allowed_flavors=options.LANGUAGE_FLAVORS,
    ),
]

KERNING_TEMPLATE_DEFAULT = CmapKerningTemplate.load(path_define.CONFIGS_KERNING_DIR.joinpath('default.yaml'))
