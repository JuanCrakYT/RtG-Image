import base64
import json
import math
import uuid
from pathlib import Path


def _camera_distance_for_canvas(width: int, height: int) -> float:
    diagonal = math.hypot(width - 1, height - 1)
    fov_radians = math.radians(90)
    distance = (diagonal / 2.0) / math.tan(fov_radians / 2.0)
    return max(6.0, distance)


def generate_canvas_files(size: int | None = None, width: int | None = None, height: int | None = None, output_dir: Path | str | None = None) -> None:
    if output_dir is None:
        raise ValueError("output_dir is required")

    if size is not None:
        width = size if width is None else width
        height = size if height is None else height

    width = int(width if width is not None else 32)
    height = int(height if height is not None else width)

    if width < 5 or height < 5:
        raise ValueError("width and height must be at least 5")
    if width > 128 or height > 128:
        raise ValueError("width and height must be at most 128")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    spacing = 1.0
    part_color = [0, 0, 0]
    y_offset = -20
    down_offset = -5

    origin_x = -((width - 1) * spacing) / 2
    origin_y = (-((height - 1) * spacing) / 2) + y_offset + down_offset

    attachments: dict[str, dict] = {}
    build: list[dict] = []
    pixel_index: list[tuple[str, int, int]] = []
    attachment_ids: list[str] = []

    for y in range(height):
        for x in range(width):
            uid = "{" + str(uuid.uuid4()).upper() + "}"
            pos_x = origin_x + x * spacing
            pos_y = origin_y + (height - 1 - y) * spacing
            pos_z = 0

            attachments[uid] = {
                "partName": "Base",
                "cframe": [
                    pos_x,
                    pos_y,
                    pos_z,
                    1,
                    0,
                    0,
                    0,
                    1,
                    0,
                    0,
                    0,
                    1,
                ],
            }

            pixel_index.append((uid, x, y))
            attachment_ids.append(uid)

    camera_uuid = "{" + str(uuid.uuid4()).upper() + "}"
    camera_rel_x = 0.0
    camera_rel_y = (-((height - 1) * spacing) / 2) + y_offset + down_offset + ((height - 1) * spacing) / 2
    camera_rel_z = _camera_distance_for_canvas(width, height)
    attachments[camera_uuid] = {
        "partName": "Base",
        "cframe": [
            camera_rel_x,
            camera_rel_y,
            camera_rel_z,
            1,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            1,
        ],
    }

    build.append([
        "Base",
        [],
        {"EphemeralAttachments": attachments},
    ])
    build.append(["Camera", [["1", camera_uuid, 1]], {"OrientationY": -90}])
    build.append(["Gyro", [["1", "4", 1]], {"Activated": True, "RGB": [73, 26, 112]}])

    for index, (uid, x, y) in enumerate(pixel_index):
        attachment_uid = attachment_ids[index]
        build.append(
            [
                "Part",
                [["1", attachment_uid, 1]],
                {"RGB": part_color},
            ]
        )

    output_file = output_dir / "canvas.json"
    base64_file = output_dir / "canvas_base64.txt"
    index_file = output_dir / "canvas_index.txt"

    with output_file.open("w", encoding="utf-8") as output_handle:
        json.dump(build, output_handle, separators=(",", ":"))

    with index_file.open("w", encoding="utf-8") as index_handle:
        line_index = 2
        for _, x, y in pixel_index:
            index_handle.write(f"{x},{y}={line_index}\n")
            line_index += 1

    with output_file.open("rb") as output_handle:
        json_bytes = output_handle.read()

    base64_string = base64.b64encode(json_bytes).decode("utf-8")
    with base64_file.open("w", encoding="utf-8") as base64_handle:
        base64_handle.write(base64_string)