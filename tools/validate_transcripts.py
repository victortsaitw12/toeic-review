#!/usr/bin/env python3
"""檢查 whisper 逐字稿品質：題號缺漏、連續重複（幻覺）。

用法：validate_transcripts.py TestA1 [TestA2 ...]
- 每個檔案應含檔名範圍內的所有題號（"Number NN" / "NN." 開頭）
- 連續兩段文字相同 → 疑似幻覺
輸出需要人工處理／重轉錄的檔案清單。
"""
import json, pathlib, re, sys

NEW = pathlib.Path('/workspaces/toeic/transcripts_new')

def qnums(fname):
    m = re.search(r'_Q(\d+)(?:-(\d+))?\.mp3$', fname)
    a = int(m.group(1))
    b = int(m.group(2)) if m.group(2) else a
    return list(range(a, b + 1))

for test in sys.argv[1:]:
    d = json.load(open(NEW / f'{test}.json'))
    for f in sorted(d):
        txt = ' '.join(s['t'] for s in d[f])
        missing = [n for n in qnums(f)
                   if not re.search(rf'(number|no\.?)\s*{n}\b|(^|[.?!]\s*){n}[.\-]', txt, re.I)]
        dups = sum(1 for i in range(1, len(d[f])) if d[f][i]['t'] == d[f][i-1]['t'])
        flags = []
        if missing:
            flags.append(f'缺題號 {missing}')
        if dups:
            flags.append(f'{dups} 段連續重複')
        if flags:
            print(f'{test}/{f}: {"；".join(flags)}')
print('validate done')
