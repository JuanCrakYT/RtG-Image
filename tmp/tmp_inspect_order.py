import json, pathlib, re
p = pathlib.Path(r'assets/default/output_converted_asset.txt')
data = json.loads(p.read_text(encoding='utf-8'))
parts = [x for x in data if isinstance(x, dict) and x.get('type') == 'Part']
print('parts', len(parts))
for i, part in enumerate(parts[:8]):
    print('--- part', i, '---')
    print('keys', list(part.keys()))
    print('name', part.get('name'))
    props = part.get('properties', {})
    print('prop keys', list(props.keys())[:20])
    print('sample props', {k: props.get(k) for k in list(props.keys())[:8]})
    print('raw', json.dumps(part, ensure_ascii=False)[:1800])
    break
# inspect the first 30 parts for any numeric index-like values in the part object
idxs = []
for part in parts:
    for key, value in part.items():
        if isinstance(value, str):
            nums = re.findall(r'\d+', value)
            if nums:
                idxs.append((key, nums[:5]))
        elif isinstance(value, (int, float)):
            idxs.append((key, [value]))
    if len(idxs) > 50:
        break
print('numeric-ish fields sample', idxs[:40])
