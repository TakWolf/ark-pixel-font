import os

import png


def load_png(file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes]) -> tuple[list[list[int]], int, int]:
    width, height, pixels, _ = png.Reader(filename=file_path).read()
    data = []
    for pixels_row in pixels:
        data_row = []
        for x in range(0, width * 4, 4):
            alpha = pixels_row[x + 3]
            if alpha > 127:
                data_row.append(1)
            else:
                data_row.append(0)
        data.append(data_row)
    return data, width, height


def save_png(
        data: list[list[int]],
        file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
):
    pixels = []
    for data_row in data:
        pixels_row = []
        for x in data_row:
            pixels_row.append(0)
            pixels_row.append(0)
            pixels_row.append(0)
            if x == 0:
                pixels_row.append(0)
            else:
                pixels_row.append(255)
        pixels.append(pixels_row)
    png.from_array(pixels, 'RGBA').save(file_path)


class CroppedBitmap:
    @staticmethod
    def load(file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes]) -> 'CroppedBitmap':
        data, width, height = load_png(file_path)

        cropped_left = 0
        cropped_right = 0
        cropped_top = 0
        cropped_bottom = 0
        # Top
        while height > 1:
            if any(alpha != 0 for alpha in data[0]):
                break
            data.pop(0)
            cropped_top += 1
            height -= 1
        # Bottom
        while height > 1:
            if any(alpha != 0 for alpha in data[-1]):
                break
            data.pop()
            cropped_bottom += 1
            height -= 1
        # Right
        while width > 1:
            if any(data_row[-1] != 0 for data_row in data):
                break
            for data_row in data:
                data_row.pop()
            cropped_right += 1
            width -= 1
        # Left
        while width > 1:
            if any(data_row[0] != 0 for data_row in data):
                break
            for data_row in data:
                data_row.pop(0)
            cropped_left += 1
            width -= 1

        return CroppedBitmap(data, width, height, cropped_left, cropped_right, cropped_top, cropped_bottom)

    def __init__(
            self,
            data: list[list[int]],
            width: int,
            height: int,
            cropped_left: int,
            cropped_right: int,
            cropped_top: int,
            cropped_bottom: int,
    ):
        self.data = data
        self.width = width
        self.height = height
        self.cropped_left = cropped_left
        self.cropped_right = cropped_right
        self.cropped_top = cropped_top
        self.cropped_bottom = cropped_bottom

    @property
    def raw_width(self) -> int:
        return self.width + self.cropped_left + self.cropped_right

    @property
    def raw_height(self) -> int:
        return self.height + self.cropped_top + self.cropped_bottom

    def index_raw_data(self, raw_x: int, raw_y: int) -> int:
        if raw_x < 0:
            raw_x += self.raw_width
        if raw_y < 0:
            raw_y += self.raw_height
        x = raw_x - self.cropped_left
        y = raw_y - self.cropped_top
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y][x]
        else:
            return 0

    def save(self, file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
        data = []
        for _ in range(self.cropped_top):
            data.append([0] * (self.width + self.cropped_left + self.cropped_right))
        for data_row in self.data:
            data_row = [0] * self.cropped_left + data_row + [0] * self.cropped_right
            data.append(data_row)
        for _ in range(self.cropped_bottom):
            data.append([0] * (self.width + self.cropped_left + self.cropped_right))

        save_png(data, file_path)
