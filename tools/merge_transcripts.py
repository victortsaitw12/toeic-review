#!/usr/bin/env python3
"""把翻譯好的逐字稿 JSON 併入 data/transcripts.js。

用法：merge_transcripts.py <translated1.json> [translated2.json ...]
每個 JSON 格式：{"TestA1": {"Part1_Q01.mp3": [{"s","e","t","z"}, ...], ...}}
同 key 覆蓋。可重複執行。
"""
import json, pathlib, re, sys

REPO = pathlib.Path('/workspaces/toeic/toeic-review')
path = REPO / 'data' / 'transcripts.js'
src = path.read_text()
m = re.search(r'const TRANSCRIPTS = (\{.*\});', src, re.S)
data = json.loads(m.group(1))

for arg in sys.argv[1:]:
    add = json.load(open(arg))
    for test, files in add.items():
        data[test] = files
        n = sum(len(v) for v in files.values())
        print(f'merged {test}: {len(files)} files, {n} segs')

path.write_text('const TRANSCRIPTS = ' + json.dumps(data, ensure_ascii=False) + ';\n')
print('transcripts.js now has tests:', ', '.join(data.keys()))
