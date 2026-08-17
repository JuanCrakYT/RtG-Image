import base64
import pathlib

p = pathlib.Path(r"assets/default/output_asset.txt")
data = p.read_text().strip()
raw = base64.b64decode(data)
print(raw.decode("utf-8")[:4000])
