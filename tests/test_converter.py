import base64
import json
import unittest

from convert.converter import convert_to_rtg, extract_colors_from_asset


class ConverterTests(unittest.TestCase):
    def test_transparent_pixels_use_selected_color(self) -> None:
        pixels = [
            [(0, 0, 0, 0), (255, 0, 0, 255)],
            [(10, 20, 30, 255), (0, 0, 0, 0)],
        ]

        result = convert_to_rtg(pixels, transparent_color=(0, 0, 0, 255))
        decoded = base64.b64decode(result).decode("utf-8")

        self.assertIn('"RGB":[0,0,0]', decoded)
        self.assertNotIn("transparent", decoded)

    def test_extract_colors_from_asset(self) -> None:
        payload = [{"RGB": [255, 0, 0]}, {"Part": [{"RGB": [0, 0, 0]}]}]
        encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")

        colors = extract_colors_from_asset(encoded)

        self.assertEqual(colors, [(255, 0, 0, 255), (0, 0, 0, 255)])

    def test_default_template_uses_project_assets(self) -> None:
        pixels = [[(255, 0, 0, 255)]]

        result = convert_to_rtg(pixels, transparent_color=(0, 0, 0, 255))
        decoded = base64.b64decode(result).decode("utf-8")

        self.assertIn("\"EphemeralAttachments\"", decoded)


if __name__ == "__main__":
    unittest.main()
