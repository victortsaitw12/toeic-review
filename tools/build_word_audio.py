#!/usr/bin/env python3
"""把國學 A/B 本的單字 MP3 依轉錄時間戳切成單字級片段，供單字卡/單字測驗真人發音。

來源：../國學多益模擬題{A,B}本/04_單字MP3_轉錄/*.tsv（英文、中文各自獨立一行，
英文那行的起訖秒數就是單字的邊界）。只收純英文且對得上 data/words.js 的片段。

產出：audio/word/<首字母>/<slug>.mp3（48kbps 單聲道）＋ data/wordaudio.js

用法：python3 tools/build_word_audio.py [--dry-run]
"""
import json, re, glob, os, subprocess, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.dirname(ROOT)                      # /workspaces/toeic
OUT = os.path.join(ROOT, 'audio', 'word')
PAD = 0.15                                       # 前後緩衝秒數
MAX_DUR = 5.0                                    # 超過視為時間戳有問題，跳過
MIN_DUR = 0.3

# TSV 檔名 → MP3 路徑
def a_mp3(stem):        # L-Test_01-A  →  04_單字MP3/Test_01/L-Test_01-A.mp3
    test = stem.split('-')[1]
    return os.path.join(SRC, '國學多益模擬題A本', '04_單字MP3', test, stem + '.mp3')

def b_mp3(stem):        # B-L-Test_1-A  →  04 單字MP3/Test 1/L-Test 1-A.mp3
    rest = stem[2:].replace('_', ' ')            # L-Test 1-A
    test = rest.split('-')[1]                    # Test 1
    return os.path.join(SRC, '國學多益模擬題B本', '04 單字MP3', test, rest + '.mp3')

SOURCES = [
    ('A', os.path.join(SRC, '國學多益模擬題A本', '04_單字MP3_轉錄', '*.tsv'), a_mp3),
    ('B', os.path.join(SRC, '國學多益模擬題B本', '04_單字MP3_轉錄', '*.tsv'), b_mp3),
]

CJK = re.compile(r'[一-鿿]')

def is_grid_snapped(path):
    """whisper 偶爾會整檔切成等長格點（例如每段都剛好 2.0 秒），那種時間戳不是真的
    語音邊界，切出來會頭尾吃字。同一個時長佔七成以上就視為整檔不可用。"""
    durs = []
    for line in open(path, encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) >= 3:
            try: durs.append(round(float(p[1]) - float(p[0]), 1))
            except ValueError: pass
    if len(durs) < 10: return False
    return collections.Counter(durs).most_common(1)[0][1] / len(durs) > 0.7

def slug(w):
    return re.sub(r'_+', '_', re.sub(r"[^a-z0-9]+", '_', w.lower())).strip('_')

def main():
    dry = '--dry-run' in sys.argv
    src = open(os.path.join(ROOT, 'data', 'words.js'), encoding='utf-8').read()
    words = json.loads(src[src.index('['):src.rindex(']') + 1])
    wset = {w['w'].lower(): w['w'] for w in words}

    picked = {}                                  # word → (mp3, start, end, tag)
    stats = collections.Counter()
    for tag, pat, tomp3 in SOURCES:
        for f in sorted(glob.glob(pat)):
            stem = os.path.basename(f)[:-4]
            mp3 = tomp3(stem)
            if not os.path.exists(mp3):
                print('！找不到音檔:', mp3); stats['missing_mp3'] += 1; continue
            if is_grid_snapped(f):
                # whisper 在這個檔沒抓到真實邊界、整檔切成等長格點，切出來會頭尾吃字
                stats['grid_files'] += 1; continue
            for line in open(f, encoding='utf-8'):
                p = line.rstrip('\n').split('\t')
                if len(p) < 3: continue
                try: s, e = float(p[0]), float(p[1])
                except ValueError: continue
                txt = p[2].strip().strip('.,')
                if not txt or CJK.search(txt): continue
                key = txt.lower()
                if key not in wset: continue
                stats['hit'] += 1
                if not (MIN_DUR <= e - s <= MAX_DUR): stats['bad_dur'] += 1; continue
                # 同一個字出現多次時保留最短的（最乾淨、最不可能夾到別的字）
                if key in picked and picked[key][2] - picked[key][1] <= e - s: continue
                picked[key] = (mp3, s, e, tag)

    print(f'單字卡 {len(words)} 字；對到片段 {stats["hit"]} 次；'
          f'可切片單字 {len(picked)} 字（{len(picked)/len(words)*100:.1f}%）'
          f'；時間戳異常跳過 {stats["bad_dur"]}')
    print('來源分布:', dict(collections.Counter(v[3] for v in picked.values())))
    if dry: return

    os.makedirs(OUT, exist_ok=True)
    # 記錄每個片段的來源，重跑時只重切「來源或時間戳有變」的字（全部重切要十幾分鐘）
    mf = os.path.join(OUT, '.manifest.json')
    old = json.load(open(mf, encoding='utf-8')) if os.path.exists(mf) else {}
    manifest = {}
    index, done, fail = {}, 0, 0
    for key, (mp3, s, e, tag) in sorted(picked.items()):
        name = slug(key)
        sub = name[0] if name[:1].isalpha() else '_'
        rel = f'{sub}/{name}.mp3'
        dst = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        sig = [os.path.basename(mp3), s, e]
        manifest[rel] = sig
        if not os.path.exists(dst) or old.get(rel) != sig:
            ss = max(0, s - PAD)
            r = subprocess.run(
                ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f'{ss:.2f}',
                 '-to', f'{e + PAD:.2f}', '-i', mp3, '-ac', '1', '-b:a', '48k', dst],
                capture_output=True)
            if r.returncode != 0 or not os.path.exists(dst):
                print('！切割失敗', key, r.stderr.decode()[:120]); fail += 1; continue
        index[wset[key]] = rel
        done += 1
        if done % 500 == 0: print(f'  ... {done}/{len(picked)}')

    # 清掉這次沒選中的舊片段（來源被判定不可用、或單字被改名/刪除）
    keep = set(manifest)
    orphan = 0
    for d, _, fs in os.walk(OUT):
        for fn in fs:
            if not fn.endswith('.mp3'): continue
            rel = os.path.relpath(os.path.join(d, fn), OUT)
            if rel not in keep:
                os.remove(os.path.join(OUT, rel)); orphan += 1
    if orphan: print(f'清掉 {orphan} 個過期片段')
    json.dump(manifest, open(mf, 'w', encoding='utf-8'))

    with open(os.path.join(ROOT, 'data', 'wordaudio.js'), 'w', encoding='utf-8') as f:
        f.write('const WORD_AUDIO = ' + json.dumps(index, ensure_ascii=False,
                                                   sort_keys=True) + ';\n')
    # 更新部署版本號，讓前端強制重抓 data/*.js（破手機快取）
    import datetime
    with open(os.path.join(ROOT, 'data', 'version.txt'), 'w', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    total = sum(os.path.getsize(os.path.join(OUT, r)) for r in index.values())
    print(f'完成 {done} 個片段（失敗 {fail}），共 {total/1024/1024:.1f} MB → audio/word/')

if __name__ == '__main__':
    main()
