import json
from pathlib import Path

path = Path('assets/default/output_converted_asset.txt')
with path.open('r', encoding='utf-8') as f:
    data = json.load(f)
parts = [item for item in data if isinstance(item, list) and item and item[0] == 'Part']
print('total parts', len(parts))
for i, item in enumerate(parts[:20]):
    print(i, item)
print('--- duplicate indices ---')
idxs = [int(item[1][0][2]) for item in parts]
dups = sorted(x for x in set(idxs) if idxs.count(x) > 1)
print('count dup idxs', len(dups))
print(dups[:50])
print('--- sample dup parts ---')
for d in dups[:10]:
    same = [item for item in parts if int(item[1][0][2]) == d]
    print('idx', d, 'count', len(same))
    for x in same[:3]:
        print(x)
        print()
