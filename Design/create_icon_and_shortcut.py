from pathlib import Path
import os
import subprocess
import sys

from PIL import Image


PROJECT_DIR = Path(__file__).resolve().parent.parent
SOURCE_IMAGE = PROJECT_DIR / "Design" / "logotipe.png"
OUTPUT_ICON = PROJECT_DIR / "Design" / "logotipe.ico"
DESKTOP_PATH = Path(os.path.expanduser("~")) / "Desktop" / "RtG Converter (Draw).lnk"
PYTHON_EXE = sys.executable
MAIN_SCRIPT = PROJECT_DIR / "main.py"


def create_icon(input_path: Path, output_path: Path, size: int = 256) -> None:
    image = Image.open(input_path).convert("RGBA")
    image = image.resize((size, size), Image.Resampling.LANCZOS)
    image.save(output_path, format="ICO", sizes=[(size, size)])


def create_shortcut(target_script: Path, shortcut_path: Path, icon_path: Path) -> None:
    icon_line = f"$Shortcut.IconLocation = '{icon_path},0'"
    ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{PYTHON_EXE}'
$Shortcut.Arguments = '"{target_script}"'
$Shortcut.WorkingDirectory = '{PROJECT_DIR}'
if (Test-Path '{icon_path}') {{ {icon_line} }}
$Shortcut.Save()
"""
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)


if __name__ == "__main__":
    if SOURCE_IMAGE.exists():
        create_icon(SOURCE_IMAGE, OUTPUT_ICON, size=256)
        print(f"Icono creado en: {OUTPUT_ICON}")
    else:
        print(f"No se encontró la imagen fuente: {SOURCE_IMAGE}")

    create_shortcut(MAIN_SCRIPT, DESKTOP_PATH, OUTPUT_ICON)
    print(f"Acceso directo creado en: {DESKTOP_PATH}")
