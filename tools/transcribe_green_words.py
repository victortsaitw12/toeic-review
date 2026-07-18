#!/usr/bin/env python3
"""綠本單字 MP3 的字級時間戳轉錄（給 build_word_audio.py 切單字發音用）。

綠本音檔是「英文單字＋中文翻譯」連著唸、中間停頓很短，既有的
國學多益寫作綠本單字/轉錄/*.tsv 是段級時間戳而且不可靠（單段長達 29 秒），
所以這裡用 word_timestamps=True 重轉一次，拿每個英文字自己的起訖秒數。

輸出 /workspaces/toeic/green_words/<檔名>.json：[{w, s, e, prob}, ...]
用法：python3 tools/transcribe_green_words.py [檔名...]（可分批、跳過已完成的）
"""
import json, pathlib, sys, time
from faster_whisper import WhisperModel

SRC = pathlib.Path('/workspaces/toeic/國學多益寫作綠本單字')
OUT = pathlib.Path('/workspaces/toeic/green_words')
OUT.mkdir(exist_ok=True)

files = [SRC / f'{a}.mp3' for a in sys.argv[1:]] or sorted(SRC.glob('*.mp3'))
model = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=3)

for i, f in enumerate(files):
    out_file = OUT / f'{f.stem}.json'
    if out_file.exists():
        print(f'{f.stem}: 已完成，跳過', flush=True); continue
    t0 = time.time()
    # language='en'：中文部分會被硬轉成亂七八糟的英文，但我們只取得出英文字的邊界，
    # 之後再用 data/words.js 的單字表過濾，轉錯的中文自然對不上、會被丟掉
    segs, _ = model.transcribe(str(f), language='en', beam_size=5,
                               word_timestamps=True, vad_filter=False)
    words = [{'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2),
              'prob': round(w.probability, 3)}
             for s in segs for w in (s.words or []) if w.word.strip()]
    json.dump(words, open(out_file, 'w'), ensure_ascii=False)
    print(f'{f.stem}: {len(words)} 字，{round(time.time()-t0)}s '
          f'({i+1}/{len(files)})', flush=True)
print('ALL DONE', flush=True)
