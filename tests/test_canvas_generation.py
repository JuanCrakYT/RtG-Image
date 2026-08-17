import json
import unittest
from pathlib import Path

from assets.canvas.canvas import _camera_distance_for_canvas, generate_canvas_files


class CanvasGenerationTests(unittest.TestCase):
    def test_generate_canvas_files_respects_selected_size(self) -> None:
        output_dir = Path("tmp_test_output")
        generate_canvas_files(size=24, output_dir=output_dir)

        json_path = output_dir / "canvas.json"
        base64_path = output_dir / "canvas_base64.txt"
        index_path = output_dir / "canvas_index.txt"

        self.assertTrue(json_path.exists())
        self.assertTrue(base64_path.exists())
        self.assertTrue(index_path.exists())

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(len(payload), 3 + 24 * 24)

        camera_nodes = [node for node in payload if isinstance(node, list) and len(node) == 3 and node[0] == "Camera"]
        self.assertEqual(len(camera_nodes), 1)

        lines = index_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 24 * 24)

    def test_generate_canvas_files_supports_independent_dimensions_and_camera_attachment(self) -> None:
        output_dir = Path("tmp_test_output_rect")
        generate_canvas_files(width=12, height=18, output_dir=output_dir)

        payload = json.loads((output_dir / "canvas.json").read_text(encoding="utf-8"))
        base_node = payload[0]
        camera_node = next(node for node in payload if isinstance(node, list) and len(node) == 3 and node[0] == "Camera")

        self.assertEqual(camera_node[0], "Camera")
        self.assertEqual(camera_node[2], {"OrientationY": -90})
        self.assertEqual(len(camera_node[1]), 1)
        self.assertEqual(camera_node[1][0][0], "1")
        self.assertEqual(camera_node[1][0][2], 1)

        attachments = base_node[2]["EphemeralAttachments"]
        camera_uuid = camera_node[1][0][1]
        self.assertIn(camera_uuid, attachments)
        self.assertEqual(attachments[camera_uuid]["partName"], "Base")
        self.assertEqual(len(attachments[camera_uuid]["cframe"]), 12)
        self.assertGreater(attachments[camera_uuid]["cframe"][2], 0)
        self.assertEqual(len(payload), 3 + 12 * 18)

    def test_camera_distance_scales_with_canvas_size(self) -> None:
        small = _camera_distance_for_canvas(5, 5)
        medium = _camera_distance_for_canvas(32, 32)
        wide = _camera_distance_for_canvas(64, 32)
        large = _camera_distance_for_canvas(128, 128)

        self.assertLess(small, medium)
        self.assertLess(medium, wide)
        self.assertLess(wide, large)
        self.assertGreater(large, 30)
        self.assertLess(small, 10)
