#!/usr/bin/env python3
"""Transcribe all split TOEIC audio files with segment timestamps."""
import json, pathlib, sys, time
from faster_whisper import WhisperModel

SPLIT = pathlib.Path('/workspaces/toeic/split')
OUT = pathlib.Path('/tmp/claude-1000/-workspaces-toeic/34ceeff0-733f-49ef-bc00-5c8232b38a2b/scratchpad/transcripts')
OUT.mkdir(exist_ok=True)

tests = sys.argv[1:] or [d.name for d in sorted(SPLIT.iterdir())]
model = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=5)

for test in tests:
    out_file = OUT / f'{test}.json'
    if out_file.exists():
        print(f'{test}: already done', flush=True)
        continue
    result = {}
    t0 = time.time()
    files = sorted((SPLIT / test).glob('*.mp3'))
    for i, f in enumerate(files):
        segs, _ = model.transcribe(str(f), language='en', beam_size=1, vad_filter=False)
        result[f.name] = [
            {'s': round(s.start, 2), 'e': round(s.end, 2), 't': s.text.strip()}
            for s in segs if s.text.strip()
        ]
        print(f'{test} {i+1}/{len(files)} {f.name} ({len(result[f.name])} segs)', flush=True)
    json.dump(result, open(out_file, 'w'), ensure_ascii=False)
    print(f'{test} DONE in {round(time.time()-t0)}s', flush=True)
print('ALL DONE', flush=True)
