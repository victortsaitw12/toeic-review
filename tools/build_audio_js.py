#!/usr/bin/env python3
"""把 gx_tests.json（import_gx.py 的輸出）併入 data/audio.js。

保留既有 TESTS（EZ Test1..5），接上國學 TestA1..A6、TestB1..B6，
並在 TEST_META 加上對應名稱。可重複執行（冪等）。
"""
import json, pathlib, re

REPO = pathlib.Path('/workspaces/toeic/toeic-review')
src = (REPO / 'data' / 'audio.js').read_text()

m = re.search(r'const TESTS = (\{.*?\});\n', src, re.S)
tests = json.loads(m.group(1))
tests = {k: v for k, v in tests.items() if not re.match(r'Test[ABC]\d', k)}


def key_order(k):  # TestA1..A6, TestB1..B6, TestC1..C10（數字自然排序）
    m2 = re.match(r'Test([A-Z])(\d+)', k)
    return (m2.group(1), int(m2.group(2)))

for path in ('/workspaces/toeic/gx_tests.json', '/workspaces/toeic/blue_tests.json'):
    gx = json.load(open(path))
    for key in sorted(gx, key=key_order):
        for it in gx[key]:  # 去掉題號前導零：第 01 題 → 第 1 題
            it['label'] = re.sub(r'\d+', lambda m: str(int(m.group())), it['label'])
        tests[key] = gx[key]

meta_lines = [
    '// 各模擬考的出處註記；未來新增其他出版社考題時在此加入',
    '// 命名慣例：name 用「出版社縮寫 + 模擬考 N」（如 "EZ 模擬考 1"、"國學A 模擬考 1"），全站顯示都取自這裡',
    'const TEST_META = {',
]
for t in range(1, 6):
    meta_lines.append(f'  "Test{t}": {{"name": "EZ 模擬考 {t}", "source": "EZ出版社 NEW TOEIC"}},')
for book, zh in (('A', 'A本'), ('B', 'B本')):
    for t in range(1, 7):
        meta_lines.append(f'  "Test{book}{t}": {{"name": "國學{book} 模擬考 {t}", "source": "國學多益模擬題{zh}"}},')
for t in range(1, 11):
    comma = '' if t == 10 else ','
    meta_lines.append(f'  "TestC{t}": {{"name": "國學藍 模擬考 {t}", "source": "國學多益聽力藍本"}}{comma}')
meta_lines.append('};')

out = 'const TESTS = ' + json.dumps(tests, ensure_ascii=False) + ';\n' + '\n'.join(meta_lines) + '\n'
(REPO / 'data' / 'audio.js').write_text(out)
print('audio.js updated:', len(tests), 'tests,', sum(len(v) for v in tests.values()), 'files')
