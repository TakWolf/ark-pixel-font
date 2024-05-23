from pathlib import Path

import png


def load_png(file_path: Path) -> tuple[list[list[int]], int, int]:
    width, height, pixels, _ = png.Reader(filename=file_path).read()
    bitmap = []
    for pixels_row in pixels:
        bitmap_row = []
        for i in range(0, width * 4, 4):
            alpha = pixels_row[i + 3]
            bitmap_row.append(1 if alpha > 127 else 0)
        bitmap.append(bitmap_row)
    return bitmap, width, height


def save_png(bitmap: list[list[int]], file_path: Path):
    pixels = []
    for bitmap_row in bitmap:
        pixels_row = []
        for alpha in bitmap_row:
            pixels_row.append(0)
            pixels_row.append(0)
            pixels_row.append(0)
            pixels_row.append(255 if alpha != 0 else 0)
        pixels.append(pixels_row)
    png.from_array(pixels, 'RGBA').save(file_path)
