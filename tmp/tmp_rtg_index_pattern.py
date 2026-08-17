import json
from pathlib import Path
path = Path('assets/default/output_converted_asset.txt')
with path.open('r', encoding='utf-8') as f:
    data = json.load(f)
idxs = [int(item[1][0][2]) for item in data if isinstance(item, list) and item and item[0] == 'Part']
uniq = sorted(set(idxs))
print('count', len(idxs))
print('unique', len(uniq), 'min', min(uniq), 'max', max(uniq))
print('duplicates', [x for x in uniq if idxs.count(x) > 1])
for mod in [32, 33, 34, 35, 36, 31, 30]:
    vals = [x % mod for x in idxs]
    print(f'mod {mod}: uniq {len(set(vals))}, min {min(vals)}, max {max(vals)}')
for base in [32, 33, 34, 35, 36]:
    rows = [x // base for x in idxs]
    print(f'base {base}: row min {min(rows)}, max {max(rows)}, uniq rows {len(set(rows))}')
print('first idxs', idxs[:20])
print('sorted idxs first 20', uniq[:20])
print('sorted idxs last 20', uniq[-20:])
PY
