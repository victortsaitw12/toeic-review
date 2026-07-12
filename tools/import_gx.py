#!/usr/bin/env python3
"""匯入國學多益模擬題 A/B 本的單題分割 MP3。

來源資料夾命名不一致（TEST1_Part1 / TEST 2_Part1 / TEST 1_Part 1），
一律用 glob 找 *Part* 子資料夾並從名稱抓 Part 編號。
轉成 64kbps 單聲道 mp3，檔名統一為 PartN_Qxx[-yy].mp3，
輸出到 repo 的 audio/TestA1..A6 / TestB1..B6，
並印出 audio.js 用的 TESTS 條目 JSON。
"""
import json, pathlib, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path('/workspaces/toeic')
REPO = ROOT / 'toeic-review'
BOOKS = {
    'A': ROOT / '國學多益模擬題A本' / '03_單題分割MP3',
    'B': ROOT / '國學多益模擬題B本' / '03 單題分割MP3',
}

jobs = []          # (src, dst)
manifest = {}      # key -> [(part_no, qlabel, dst_path)]

for book, base in BOOKS.items():
    for t in range(1, 7):
        key = f'Test{book}{t}'
        src_test = base / f'TEST {t}'
        out_dir = REPO / 'audio' / key
        out_dir.mkdir(parents=True, exist_ok=True)
        entries = []
        part_dirs = sorted(src_test.glob('*Part*'))
        assert len(part_dirs) == 4, f'{src_test}: {part_dirs}'
        for pd in part_dirs:
            m = re.search(r'Part\s*(\d)', pd.name)
            part_no = int(m.group(1))
            for f in sorted(pd.glob('*.mp3')):
                q = re.search(r'_(\d+(?:-\d+)?)\.mp3$', f.name).group(1)
                dst = out_dir / f'Part{part_no}_Q{q}.mp3'
                jobs.append((f, dst))
                entries.append((part_no, q, dst))
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
    for part_no, q, dst in entries:
        label = '第 ' + q.replace('-', '–') + ' 題'
        items.append({'f': dst.name, 'part': f'Part {part_no}', 'label': label, 'dur': dur(dst)})
    tests[key] = items
    print(key, len(items), 'files', flush=True)

json.dump(tests, open(ROOT / 'gx_tests.json', 'w'), ensure_ascii=False)
print('WROTE', ROOT / 'gx_tests.json')
