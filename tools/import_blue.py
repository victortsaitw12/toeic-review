#!/usr/bin/env python3
"""匯入國學多益聽力藍本的單題分割 MP3（10 回，扁平檔名 TestNN_XX[-YY].mp3）。

Part 由題號推導：1-6→Part1、7-31→Part2、32-70→Part3、71-100→Part4。
轉 64kbps 單聲道、檔名統一 PartN_Qxx[-yy].mp3，輸出到 audio/TestC1..C10，
時長寫入 /workspaces/toeic/build/blue_tests.json（格式同 gx_tests.json）。
"""
import json, pathlib, re, subprocess
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path('/workspaces/toeic')
REPO = ROOT / 'toeic-review'
BASE = ROOT / '國學多益聽力藍本' / '02單題分割音檔'

def part_of(q):
    q = int(q.split('-')[0])
    return 1 if q <= 6 else 2 if q <= 31 else 3 if q <= 70 else 4

jobs, manifest = [], {}
for t in range(1, 11):
    key = f'TestC{t}'
    src = BASE / f'TEST {t:02d}單題分割音檔'
    out_dir = REPO / 'audio' / key
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    files = sorted(src.glob('*.mp3'))
    assert len(files) == 54, f'{src}: {len(files)}'
    for f in files:
        q = re.search(r'_(\d+(?:-\d+)?)\.mp3$', f.name).group(1)
        p = part_of(q)
        dst = out_dir / f'Part{p}_Q{q}.mp3'
        jobs.append((f, dst))
        entries.append((p, q, dst))
    entries.sort(key=lambda e: (e[0], int(e[1].split('-')[0])))
    manifest[key] = entries

def convert(job):
    src, dst = job
    if dst.exists() and dst.stat().st_size > 0:
        return
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(src),
                    '-c:a', 'libmp3lame', '-b:a', '64k', '-ac', '1', str(dst)],
                   check=True)

with ThreadPoolExecutor(max_workers=4) as ex:
    for i, _ in enumerate(ex.map(convert, jobs)):
        if (i + 1) % 50 == 0:
            print(f'converted {i+1}/{len(jobs)}', flush=True)

def dur(p):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'csv=p=0', str(p)], capture_output=True, text=True, check=True)
    return round(float(out.stdout.strip()), 1)

tests = {}
for key, entries in manifest.items():
    items = []
    for p, q, dst in entries:
        label = '第 ' + re.sub(r'\d+', lambda m: str(int(m.group())), q).replace('-', '–') + ' 題'
        items.append({'f': dst.name, 'part': f'Part {p}', 'label': label, 'dur': dur(dst)})
    tests[key] = items
    print(key, len(items), 'files', flush=True)

json.dump(tests, open(ROOT / 'build' / 'blue_tests.json', 'w'), ensure_ascii=False)
print('WROTE', ROOT / 'build' / 'blue_tests.json')
