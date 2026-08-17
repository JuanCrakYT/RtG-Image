from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import List, Tuple

from canvas import generate_rainbow_pixels

Pixel = Tuple[int, int, int, int]
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _resolve_project_path(path: Path | str | None, *default_parts: str) -> Path:
    if path is None:
        return PROJECT_ROOT.joinpath(*default_parts)

    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    return candidate.resolve()


def _resolve_default_asset_paths(asset_path: Path | str | None = None, asset_index_path: Path | str | None = None) -> tuple[Path, Path]:
    canvas_asset_path = PROJECT_ROOT / "assets" / "canvas" / "canvas.json"
    canvas_index_path = PROJECT_ROOT / "assets" / "canvas" / "canvas_index.txt"

    resolved_asset_path = _resolve_project_path(asset_path, "assets", "default", "output_converted_asset.txt")
    resolved_index_path = _resolve_project_path(asset_index_path, "assets", "index.txt")

    if asset_path is None and canvas_asset_path.exists():
        resolved_asset_path = canvas_asset_path
    if asset_index_path is None and canvas_index_path.exists():
        resolved_index_path = canvas_index_path

    return resolved_asset_path, resolved_index_path


def convert_to_rtg(pixel_matrix: List[List[Pixel]], transparent_color: Pixel | None = None, asset_path: Path | str | None = None, asset_index_path: Path | str | None = None) -> str:
    """Convert a 32x32 pixel matrix to an RtG-compatible base64 asset payload."""
    fallback_color = transparent_color or (0, 0, 0, 255)
    asset_path, asset_index_path = _resolve_default_asset_paths(asset_path, asset_index_path)
    try:
        template = load_rtg_template(asset_path)
        filled = apply_colors_to_rtg_template(template, pixel_matrix, fallback_color, asset_index_path=asset_index_path)
        return base64.b64encode(filled.encode("utf-8")).decode("ascii")
    except Exception:
        lines: List[str] = []
        for row in pixel_matrix:
            cells = []
            for r, g, b, a in row:
                if a == 0:
                    cells.append(f"{fallback_color[0]},{fallback_color[1]},{fallback_color[2]},{fallback_color[3]}")
                else:
                    cells.append(f"{r},{g},{b},{a}")
            lines.append(" | ".join(cells))
        return "\n".join(lines)


def load_rtg_template(path: Path | str) -> list:
    template_path = _resolve_project_path(path)
    with template_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_index_entries(path: Path | str | None) -> List[Tuple[int, int, int]]:
    if path is None:
        return []
    index_path = _resolve_project_path(path)
    if not index_path.exists():
        return []

    entries: List[Tuple[int, int, int]] = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            decoded = base64.b64decode(line).decode("utf-8")
            payload = json.loads(decoded)
        except Exception:
            continue

        if isinstance(payload, list) and payload and isinstance(payload[0], list):
            color = payload[0][2].get("RGB") if len(payload[0]) >= 3 and isinstance(payload[0][2], dict) else None
            if isinstance(color, list) and len(color) == 3:
                entries.append((int(color[0]), int(color[1]), int(color[2])))

    return entries


def apply_colors_to_rtg_template(template: list, pixel_matrix: List[List[Pixel]], transparent_color: Pixel, asset_index_path: Path | str | None = None) -> str:
    pixels: List[Pixel] = []
    for row in pixel_matrix:
        for r, g, b, a in row:
            if a == 0:
                pixels.append(transparent_color)
            else:
                pixels.append((r, g, b, 255))

    # Collect all Part nodes in template order.
    parts: List[list] = []

    def collect(node):
        if isinstance(node, list):
            if len(node) >= 3 and node[0] == "Part" and isinstance(node[2], dict):
                parts.append(node)
            else:
                for item in node:
                    collect(item)
        elif isinstance(node, dict):
            for value in node.values():
                collect(value)

    collect(template)

    index_entries = load_index_entries(asset_index_path)
    target_count = min(len(parts), len(pixels), len(index_entries) if index_entries else len(pixels))

    if index_entries:
        color_to_part_index: dict[Tuple[int, int, int], int] = {}
        for part_index, node in enumerate(parts):
            rgb = node[2].get("RGB")
            if isinstance(rgb, list) and len(rgb) == 3:
                color_to_part_index[(int(rgb[0]), int(rgb[1]), int(rgb[2]))] = part_index

        mapped_part_indices: List[int] = []
        for ref_color in index_entries:
            if ref_color in color_to_part_index:
                mapped_part_indices.append(color_to_part_index[ref_color])

        if mapped_part_indices:
            for pixel_index, part_index in enumerate(mapped_part_indices):
                if pixel_index < len(pixels) and part_index < len(parts):
                    color = pixels[pixel_index]
                    parts[part_index][2]["RGB"] = [color[0], color[1], color[2]]
        else:
            for i in range(target_count):
                node = parts[i]
                color = pixels[i]
                node[2]["RGB"] = [color[0], color[1], color[2]]
    else:
        for i, node in enumerate(parts):
            if i < len(pixels):
                color = pixels[i]
                node[2]["RGB"] = [color[0], color[1], color[2]]

    return json.dumps(template, separators=(",", ":"))


def extract_colors_from_asset(asset_payload: str) -> List[Pixel]:
    """Parse a base64 JSON payload from an RtG asset and return its colors.

    The structure may contain nested objects with a "RGB" entry, as used in the
    output asset file stored in the assets folder.
    """
    try:
        decoded = base64.b64decode(asset_payload)
        payload = json.loads(decoded.decode("utf-8"))
    except Exception:
        return []

    colors: List[Pixel] = []

    def visit(node) -> None:
        if isinstance(node, dict):
            rgb = node.get("RGB")
            if isinstance(rgb, list) and len(rgb) == 3:
                try:
                    r, g, b = rgb
                    candidate = (int(r), int(g), int(b), 255)
                    if candidate not in colors:
                        colors.append(candidate)
                except (ValueError, TypeError):
                    pass
            for value in node.values():
                if isinstance(value, (dict, list)):
                    visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(payload)

    text = decoded.decode("utf-8", errors="replace")
    for match in re.finditer(r'"?RGB"?\s*[:=]\s*\[\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\]', text, re.IGNORECASE):
        r, g, b = match.groups()
        candidate = (int(r), int(g), int(b), 255)
        if candidate not in colors:
            colors.append(candidate)

    return colors
