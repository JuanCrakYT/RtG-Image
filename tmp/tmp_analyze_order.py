import json
from collections import defaultdict
from pathlib import Path

path = Path('assets/default/output_converted_asset.txt')
data = json.loads(path.read_text(encoding='utf-8'))

parts = [item for item in data if isinstance(item, list) and len(item) >= 3 and item[0] == 'Part']
print('total parts', len(parts))

counts = defaultdict(int)
idxs = []
idx_to_positions = defaultdict(list)
for pos, part in enumerate(parts):
    info = part[1]
    if isinstance(info, list) and info and isinstance(info[0], list) and len(info[0]) >= 3:
        a, b, c = info[0][0], info[0][1], info[0][2]
        counts[(a, b)] += 1
        idxs.append(c)
        idx_to_positions[c].append(pos)

print('counts by type prefix:')
for key in sorted(counts.keys()):
    print(' ', key, counts[key])
print('min idx', min(idxs), 'max idx', max(idxs), 'unique idx total', len(set(idxs)))
print('repeated numeric idx count', sum(1 for c, ps in idx_to_positions.items() if len(ps) > 1))
print('missing count', len([x for x in range(min(idxs), max(idxs) + 1) if x not in set(idxs)]))

# Inspect positions for first 200 indices
print('\nfirst 40 parts with idx and pos:')
for pos, part in enumerate(parts[:40]):
    info = part[1]
    idx = info[0][2]
    print(pos, idx, info)

# examine delta in sorted idx order
sorted_keys = sorted(set(idxs))
print('\nfirst 50 sorted idx values:', sorted_keys[:50])
print('last 50 sorted idx values:', sorted_keys[-50:])

# See if idx order in the asset has some regular pattern by grouping every 32
print('\nassets grouped by 32 positions (idx values):')
for group in range(0, 128):
    subset = [parts[i][1][0][2] for i in range(group * 8, min((group + 1) * 8, len(parts)))]
    if group < 10 or group >= 120:
        print(group, subset)
    if group == 11:
        break

# Check relationship between original position and idx order
sorted_by_idx = sorted([(idx, pos) for pos, idx in enumerate(idxs)])
print('\nfirst 20 sorted by idx (idx,pos):', sorted_by_idx[:20])
print('last 20 sorted by idx (idx,pos):', sorted_by_idx[-20:])

# Are positions of sorted idx ascending roughly contiguous?
runs = []
current_run = [sorted_by_idx[0][1]]
for _, pos in sorted_by_idx[1:]:
    if pos == current_run[-1] + 1:
        current_run.append(pos)
    else:
        runs.append(current_run)
        current_run = [pos]
runs.append(current_run)
print('number of contiguous runs in sorted idx positions:', len(runs))
print('first 10 run lengths:', [len(r) for r in runs[:10]])
print('sample run starts:', [(r[0], r[-1]) for r in runs[:10]])

# Count parts between Base entries in top-level data
base_gaps = []
count = 0
for item in data:
    if isinstance(item, list) and item and item[0] == 'Base':
        base_gaps.append(count)
        count = 0
    elif isinstance(item, list) and item and item[0] == 'Part':
        count += 1
    else:
        count += 1
base_gaps.append(count)
print('\nBase gaps counts:', base_gaps[:20], '... total groups', len(base_gaps))
print('sum gaps', sum(base_gaps))

# Print some top-level sections around Base entries
for i, item in enumerate(data[:120]):
    if isinstance(item, list) and item and item[0] == 'Base':
        print('TOP Base at', i, item)
    elif isinstance(item, list) and item and item[0] == 'Part' and i < 20:
        print('TOP Part', i, item[1])

# Show stats about 1,5 vs 1,6 groups and repeated idx values
print('\nGroup counts and sample indices:')
for key in sorted(counts.keys()):
    sample = sorted([c for c in idxs if (parts[idx_to_positions[c][0]][1][0][0], parts[idx_to_positions[c][0]][1][0][1]) == key])[:20]
    print(' ', key, counts[key], 'sample idxs', sample)

repeated = {c: idx_to_positions[c] for c, positions in idx_to_positions.items() if len(positions) > 1}
print('\nRepeated numeric idx values:', len(repeated), 'sample', list(repeated.items())[:20])

print('\nPositions of first 32 1,5 parts:')
for pos, part in enumerate(parts):
    info = part[1]
    if isinstance(info, list) and info and isinstance(info[0], list) and len(info[0]) >= 3:
        if info[0][0] == '1' and info[0][1] == '5':
            print(pos, info[0][2])
            if pos >= 31:
                break

# Check if part indices have any correlation with top-level position modulo 32 or 64
print('\nCorrelation of idx modulo 32 for first 100 parts:')
for pos in range(32):
    idx = parts[pos][1][0][2]
    print(pos, idx, idx % 32)
