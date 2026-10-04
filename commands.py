"""Program command interface for RtG Image addon."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

# Add tools/RtG Image to path
TOOLS_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_ROOT))

from convert.converter import convert_to_rtg, load_rtg_template
from load_img.image_loader import load_image_to_pixels


def get_commands() -> List[str]:
    """Return list of available program commands."""
    return ["convert", "help"]


def get_help(command: str, lang: str | None = None) -> str | None:
    """Return help text for a command in given language."""
    help_texts = {
        "en": {
            "convert": "Convert an image to RtG-Format asset.\n\nUsage: rtg image convert <input_image> [--output <file>] [--template <template>] [--index <index>] [--transparent <r,g,b,a>]\n\nOptions:\n  --output, -o     Output file path (default: stdout)\n  --template, -t   RtG template JSON file\n  --index, -i      Index file for color mapping\n  --transparent    Transparent color as r,g,b,a (default: 0,0,0,255)\n  --size           Resize image to WIDTHxHEIGHT (default: 32x32)\n  --help           Show this help",
            "help": "Show help for commands.\n\nUsage: rtg image help [command]",
        },
        "es": {
            "convert": "Convierte una imagen a asset de RtG-Format.\n\nUso: rtg image convert <imagen_entrada> [--output <archivo>] [--template <plantilla>] [--index <indice>] [--transparent <r,g,b,a>]\n\nOpciones:\n  --output, -o     Archivo de salida (por defecto: stdout)\n  --template, -t   Archivo JSON de plantilla RtG\n  --index, -i      Archivo de índice para mapeo de colores\n  --transparent    Color transparente como r,g,b,a (por defecto: 0,0,0,255)\n  --size           Redimensionar imagen a ANCHOxALTO (por defecto: 32x32)\n  --help           Mostrar esta ayuda",
            "help": "Muestra ayuda para comandos.\n\nUso: rtg image help [comando]",
        },
    }
    lang = lang or "en"
    if lang not in help_texts:
        lang = "en"
    return help_texts[lang].get(command)


def execute(args: List[str]) -> int:
    """Execute the program with arguments. Returns exit code."""
    if not args:
        print("RtG Image - Image to RtG-Format converter")
        print()
        print("Commands:")
        print("  convert   Convert an image to RtG asset")
        print("  help      Show help")
        print()
        print("Use 'rtg image help <command>' for more information.")
        return 0

    command = args[0]
    cmd_args = args[1:]

    if command == "help":
        if cmd_args:
            help_text = get_help(cmd_args[0], None)
            if help_text:
                print(help_text)
            else:
                print(f"No help available for '{cmd_args[0]}'")
        else:
            print("RtG Image - Image to RtG-Format converter")
            print()
            print("Commands:")
            print("  convert   Convert an image to RtG asset")
            print("  help      Show help")
        return 0

    elif command == "convert":
        parser = argparse.ArgumentParser(
            prog="rtg image convert",
            description="Convert an image to RtG-Format asset",
            add_help=False,
        )
        parser.add_argument("input", help="Input image file")
        parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
        parser.add_argument("--template", "-t", help="RtG template JSON file")
        parser.add_argument("--index", "-i", help="Index file for color mapping")
        parser.add_argument("--transparent", help="Transparent color as r,g,b,a (default: 0,0,0,255)")
        parser.add_argument("--size", help="Resize image to WIDTHxHEIGHT (default: 32x32)")
        parser.add_argument("--help", action="store_true", help="Show help")

        try:
            parsed = parser.parse_args(cmd_args)
        except SystemExit as e:
            return e.code

        if parsed.help:
            help_text = get_help("convert", None)
            if help_text:
                print(help_text)
            return 0

        # Parse transparent color
        transparent_color = None
        if parsed.transparent:
            try:
                parts = [int(x.strip()) for x in parsed.transparent.split(",")]
                if len(parts) != 4:
                    raise ValueError
                transparent_color = tuple(parts)  # type: ignore
            except ValueError:
                print("Error: --transparent must be in format r,g,b,a", file=sys.stderr)
                return 1

        # Parse size
        size = (32, 32)
        if parsed.size:
            try:
                w, h = parsed.size.lower().split("x")
                size = (int(w), int(h))
            except ValueError:
                print("Error: --size must be in format WIDTHxHEIGHT", file=sys.stderr)
                return 1

        # Load image
        try:
            pixels = load_image_to_pixels(parsed.input, size=size[0] if size[0] == size[1] else None, width=size[0], height=size[1])
        except Exception as e:
            print(f"Error loading image: {e}", file=sys.stderr)
            return 1

        # Convert to RtG
        try:
            result = convert_to_rtg(
                pixels,
                transparent_color=transparent_color,
                asset_path=parsed.template,
                asset_index_path=parsed.index,
            )
        except Exception as e:
            print(f"Error converting image: {e}", file=sys.stderr)
            return 1

        # Output result
        if parsed.output:
            try:
                Path(parsed.output).write_text(result, encoding="utf-8")
                print(f"Output written to {parsed.output}")
            except Exception as e:
                print(f"Error writing output: {e}", file=sys.stderr)
                return 1
        else:
            print(result)

        return 0

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print("Available commands: convert, help")
        return 1


if __name__ == "__main__":
    sys.exit(execute(sys.argv[1:]))