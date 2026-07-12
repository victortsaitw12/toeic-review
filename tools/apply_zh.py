#!/usr/bin/env python3
"""把翻譯檔套到 whisper 逐字稿並併入 data/transcripts.js。

用法：apply_zh.py TestA1
讀 /workspaces/toeic/transcripts_new/TestA1.zh.*.txt，每行三欄（TAB 分隔）：
  file<TAB>idx<TAB>中文翻譯
若第一欄是 FIX 則為修正英文原文：FIX<TAB>file<TAB>idx<TAB>corrected text
若第一欄是 DEL 則刪除該 segment（whisper 幻覺）：DEL<TAB>file<TAB>idx，免翻譯
idx 一律指原始 JSON 的索引。驗證每個 segment 都有翻譯後，
寫回 data/transcripts.js（同 key 覆蓋、冪等）。
"""
import glob, json, pathlib, re, sys

test = sys.argv[1]
NEW = pathlib.Path('/workspaces/toeic/transcripts_new')
d = json.load(open(NEW / f'{test}.json'))

zh, fixes, dels = {}, {}, set()
for path in sorted(glob.glob(str(NEW / f'{test}.zh.*.txt'))):
    for ln, line in enumerate(open(path), 1):
        line = line.rstrip('\n')
        if not line.strip():
            continue
        cols = line.split('\t')
        if cols[0] == 'FIX':
            _, f, i, t = cols
            fixes[(f, int(i))] = t
        elif cols[0] == 'DEL':
            dels.add((cols[1], int(cols[2])))
        else:
            f, i, z = cols[0], int(cols[1]), cols[2]
            assert (f, i) not in zh, f'{path}:{ln} 重複翻譯 {f} #{i}'
            zh[(f, i)] = z

missing = [(f, i) for f in d for i in range(len(d[f]))
           if (f, i) not in zh and (f, i) not in dels]
extra = [k for k in zh if k[0] not in d or k[1] >= len(d[k[0]])]
assert not missing, f'缺 {len(missing)} 句翻譯，如 {missing[:5]}'
assert not extra, f'多出對不上的翻譯 {extra[:5]}'

for (f, i), t in fixes.items():
    d[f][i]['t'] = t
for (f, i), z in zh.items():
    d[f][i]['z'] = z
for f in d:
    d[f] = [s for i, s in enumerate(d[f]) if (f, i) not in dels]

repo = pathlib.Path('/workspaces/toeic/toeic-review')
tp = repo / 'data' / 'transcripts.js'
src = tp.read_text()
m = re.search(r'const TRANSCRIPTS = (\{.*\});', src, re.S)
data = json.loads(m.group(1))
data[test] = d
tp.write_text('const TRANSCRIPTS = ' + json.dumps(data, ensure_ascii=False) + ';\n')
print(f'{test}: {len(d)} files, {sum(len(v) for v in d.values())} segs merged; '
      f'transcripts.js tests = {", ".join(data)}')
