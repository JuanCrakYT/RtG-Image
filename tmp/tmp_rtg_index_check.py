import json
from pathlib import Path

path = Path("assets/default/output_converted_asset.txt")
text = path.read_text("utf-8")
data = json.loads(text)
idxs = [int(item[1][0][2]) for item in data if isinstance(item, list) and item and item[0] == "Part"]
uniq = sorted(set(idxs))
print("count", len(idxs))
print("unique", len(uniq), "min", min(uniq), "max", max(uniq))
print("first20", uniq[:20])
print("last20", uniq[-20:])
print("duplicates", [x for x in uniq if idxs.count(x) > 1])
