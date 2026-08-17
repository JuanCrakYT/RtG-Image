import base64
import json
from pathlib import Path
from typing import List, Tuple

import customtkinter as ctk
from PIL import Image
import tkinter as tk


Pixel = Tuple[int, int, int, int]


def _hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    h = h % 1.0
    c = v * s
    x = c * (1 - abs((h * 6) % 2 - 1))
    m = v - c

    if 0 <= h < 1 / 6:
        r1, g1, b1 = c, x, 0
    elif 1 / 6 <= h < 2 / 6:
        r1, g1, b1 = x, c, 0
    elif 2 / 6 <= h < 3 / 6:
        r1, g1, b1 = 0, c, x
    elif 3 / 6 <= h < 4 / 6:
        r1, g1, b1 = 0, x, c
    elif 4 / 6 <= h < 5 / 6:
        r1, g1, b1 = x, 0, c
    else:
        r1, g1, b1 = c, 0, x

    return tuple(int(round((r1 + m) * 255)) for r1 in (r1, g1, b1))


def generate_rainbow_pixels(size: int = 32) -> List[List[Pixel]]:
    pixels: List[List[Pixel]] = []
    for row in range(size):
        row_pixels: List[Pixel] = []
        for col in range(size):
            index = row * size + col
            hue = index / (size * size)
            r, g, b = _hsv_to_rgb(hue, 0.95, 0.98)
            row_pixels.append((r, g, b, 255))
        pixels.append(row_pixels)
    return pixels


def export_pixels_to_text(path: str | Path, pixels: List[List[Pixel]]) -> None:
    output_path = Path(path)
    output_path.write_text(json.dumps(pixels, indent=2), encoding="utf-8")


def export_pixels_to_index_file(path: str | Path, pixels: List[List[Pixel]], count: int = 32) -> None:
    output_path = Path(path)
    lines: List[str] = []
    for row in pixels:
        for pixel in row:
            r, g, b, a = pixel
            if a == 0:
                r, g, b = 0, 0, 0
            payload = [["Part", [], {"RGB": [r, g, b]}]]
            encoded = base64.b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")).decode("ascii")
            lines.append(encoded)
            if len(lines) >= count:
                break
        if len(lines) >= count:
            break
    output_path.write_text("\n".join(lines), encoding="utf-8")


class PixelCanvas(ctk.CTkFrame):
    def __init__(self, master, width: int = 640, height: int = 640, size: int = 32, size_x: int | None = None, size_y: int | None = None) -> None:
        super().__init__(master)
        if size_x is None:
            size_x = size
        if size_y is None:
            size_y = size
        self.size_x = int(size_x)
        self.size_y = int(size_y)
        self.size = self.size_x
        self.width = width
        self.height = height
        self.zoom = 16
        self.tool = "paint"
        self.color: Pixel = (255, 255, 255, 255)
        self.pixels: List[List[Pixel]] = [[(0, 0, 0, 0) for _ in range(self.size_x)] for _ in range(self.size_y)]
        self._canvas = None
        self._last_pos = None
        self._build_canvas()
        self._draw_grid()

    def set_size(self, size: int | None = None, height: int | None = None) -> None:
        if size is None:
            size = self.size_x
        if height is None:
            height = self.size_y
        if size < 1 or height < 1:
            raise ValueError("size must be a positive integer")
        self.size_x = int(size)
        self.size_y = int(height)
        self.size = self.size_x
        self.pixels = [[(0, 0, 0, 0) for _ in range(self.size_x)] for _ in range(self.size_y)]
        self.zoom = max(4, min(24, min(self.width // max(1, self.size_x), self.height // max(1, self.size_y))))
        self._draw_grid()

    def _build_canvas(self) -> None:
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="#1f1f1f", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

    def _draw_grid(self) -> None:
        self.canvas.delete("all")
        cell_size = self.zoom
        for x in range(0, self.size_x * cell_size + 1, cell_size):
            self.canvas.create_line(x, 0, x, self.size_y * cell_size, fill="#444444")
        for y in range(0, self.size_y * cell_size + 1, cell_size):
            self.canvas.create_line(0, y, self.size_x * cell_size, y, fill="#444444")
        for row in range(self.size_y):
            for col in range(self.size_x):
                pixel = self.pixels[row][col]
                if pixel[3] == 0:
                    continue
                x0 = col * cell_size
                y0 = row * cell_size
                self.canvas.create_rectangle(
                    x0,
                    y0,
                    x0 + cell_size,
                    y0 + cell_size,
                    fill=self._rgba_to_hex(pixel),
                    outline="",
                )

    def _on_left_click(self, event) -> None:
        self._last_pos = (event.x, event.y)
        self._apply_tool(event.x, event.y)

    def _on_drag(self, event) -> None:
        self._apply_tool(event.x, event.y)

    def _on_right_click(self, event) -> None:
        self._last_pos = (event.x, event.y)
        self._apply_tool(event.x, event.y, erase=True)

    def _on_release(self, event) -> None:
        self._last_pos = None

    def _apply_tool(self, x: int, y: int, erase: bool = False) -> None:
        if not self.canvas.winfo_exists():
            return
        cell_size = self.zoom
        col = x // cell_size
        row = y // cell_size
        if not (0 <= row < self.size_y and 0 <= col < self.size_x):
            return
        if self.tool == "paint":
            self._set_pixel(row, col, self.color if not erase else (0, 0, 0, 0))
        elif self.tool == "eraser":
            self._set_pixel(row, col, (0, 0, 0, 0))
        elif self.tool == "eyedropper":
            pixel = self.pixels[row][col]
            if pixel[3] != 0:
                self.color = pixel
                self._last_pos = None
        elif self.tool == "fill":
            self._fill_area(row, col, self.color if not erase else (0, 0, 0, 0))

    def _set_pixel(self, row: int, col: int, value: Pixel) -> None:
        if self.pixels[row][col] == value:
            return
        self.pixels[row][col] = value
        self._redraw_pixel(row, col)

    def _redraw_pixel(self, row: int, col: int) -> None:
        cell_size = self.zoom
        x0 = col * cell_size
        y0 = row * cell_size
        self.canvas.delete(f"pixel_{row}_{col}")
        pixel = self.pixels[row][col]
        if pixel[3] == 0:
            self.canvas.create_rectangle(
                x0,
                y0,
                x0 + cell_size,
                y0 + cell_size,
                fill="#1f1f1f",
                outline="#444444",
                tags=(f"pixel_{row}_{col}",),
            )
            return
        self.canvas.create_rectangle(
            x0,
            y0,
            x0 + cell_size,
            y0 + cell_size,
            fill=self._rgba_to_hex(pixel),
            outline="#444444",
            tags=(f"pixel_{row}_{col}",),
        )

    def _fill_area(self, row: int, col: int, fill_value: Pixel) -> None:
        target = self.pixels[row][col]
        if target == fill_value:
            return
        stack = [(row, col)]
        visited = set()
        while stack:
            r, c = stack.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            if not (0 <= r < self.size_y and 0 <= c < self.size_x):
                continue
            if self.pixels[r][c] != target:
                continue
            self.pixels[r][c] = fill_value
            self._redraw_pixel(r, c)
            stack.append((r + 1, c))
            stack.append((r - 1, c))
            stack.append((r, c + 1))
            stack.append((r, c - 1))

    def set_tool(self, tool: str) -> None:
        self.tool = tool

    def set_color(self, color: Pixel) -> None:
        self.color = color

    def load_pixels(self, pixels: List[List[Pixel]]) -> None:
        if not pixels:
            self.pixels = []
            self.size_y = 0
            self.size_x = 0
            self.size = 0
            self._draw_grid()
            return
        self.size_y = len(pixels)
        self.size_x = max(len(row) for row in pixels)
        self.size = self.size_x
        self.pixels = [list(row) for row in pixels]
        self._draw_grid()

    def clear(self) -> None:
        self.pixels = [[(0, 0, 0, 0) for _ in range(self.size_x)] for _ in range(self.size_y)]
        self._draw_grid()

    def get_pixels(self) -> List[List[Pixel]]:
        return [row[:] for row in self.pixels]

    def save_png(self, path: str, background_color: Pixel | None = None) -> None:
        fallback_color = background_color or (0, 0, 0, 255)
        image = Image.new("RGBA", (self.size_x, self.size_y), fallback_color)
        pixel_data = []
        for row in self.pixels:
            for pixel in row:
                if pixel[3] == 0:
                    pixel_data.append(fallback_color)
                else:
                    pixel_data.append(pixel)
        image.putdata(pixel_data)
        image = image.resize((self.size_x, self.size_y), Image.Resampling.NEAREST)
        image.save(path)

    def _rgba_to_hex(self, color: Pixel) -> str:
        r, g, b, a = color
        if a == 0:
            return "#1f1f1f"
        return f"#{r:02x}{g:02x}{b:02x}"

