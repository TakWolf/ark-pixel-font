from typing import Any


class CmapSelector:
    @staticmethod
    def parse(data: Any) -> CmapSelector:
        blocks = set(data.get('blocks', ()))
        code_points = set(data.get('code-points', ()))
        return CmapSelector(blocks, code_points)

    blocks: set[str]
    code_points: set[int]

    def __init__(
            self,
            blocks: set[str],
            code_points: set[int],
    ) -> None:
        self.blocks = blocks
        self.code_points = code_points


class NamedSelector:
    @staticmethod
    def parse(data: Any) -> NamedSelector:
        name_keys = set(data.get('name-keys', ()))
        return NamedSelector(name_keys)

    name_keys: set[str]

    def __init__(
            self,
            name_keys: set[str],
    ) -> None:
        self.name_keys = name_keys


class FileIdSelector:
    @staticmethod
    def parse(data: Any) -> FileIdSelector:
        file_ids = set(data.get('file-ids', ()))
        return FileIdSelector(file_ids)

    file_ids: set[str]

    def __init__(
            self,
            file_ids: set[str],
    ) -> None:
        self.file_ids = file_ids
