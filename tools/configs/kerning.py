from __future__ import annotations

import yaml

from tools.configs import path_define
from tools.configs.options import FontSize


class KerningConfig:
    @staticmethod
    def load(font_size: FontSize) -> KerningConfig:
        data = yaml.safe_load(path_define.configs_dir.joinpath(f'kerning-{font_size}px.yml').read_bytes())

        groups = {}
        for group_name, alphabet in data['groups'].items():
            groups[group_name] = list(alphabet)

        templates = {}
        for group_names, offset in data['templates'].items():
            group_names = group_names.split(',')
            left_group_name = group_names[0]
            right_group_name = group_names[1]
            templates[(left_group_name, right_group_name)] = offset

        return KerningConfig(
            groups,
            templates,
        )

    groups: dict[str, list[str]]
    templates: dict[tuple[str, str], int]

    def __init__(
            self,
            groups: dict[str, list[str]],
            templates: dict[tuple[str, str], int],
    ):
        self.groups = groups
        self.templates = templates
