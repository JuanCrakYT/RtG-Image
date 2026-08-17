from typing import List, Tuple

from PIL import Image

Pixel = Tuple[int, int, int, int]


def load_image_to_pixels(path: str, size: int | None = None, width: int | None = None, height: int | None = None) -> List[List[Pixel]]:
    if size is None:
        size = 32
    if width is None:
        width = size
    if height is None:
        height = width

    image = Image.open(path).convert("RGBA")
    image = image.resize((width, height), Image.Resampling.NEAREST)
    pixels: List[List[Pixel]] = []
    for y in range(height):
        row: List[Pixel] = []
        for x in range(width):
            r, g, b, a = image.getpixel((x, y))
            row.append((r, g, b, a))
        pixels.append(row)
    return pixels
