import subprocess
import sys
from pathlib import Path

repo = Path(r"C:\Users\User\Desktop\Created programs\RtG Converter (Draw)")
result = subprocess.run(
    [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q"],
    cwd=repo,
    capture_output=True,
    text=True,
)
print(result.stdout)
print(result.stderr)
print(f"EXIT={result.returncode}")
