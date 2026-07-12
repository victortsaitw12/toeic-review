#!/usr/bin/env python3
"""Transcribe 國學 A/B 本 audio (repo audio/TestA*, TestB*) with faster-whisper."""
import json, pathlib, sys, time
from faster_whisper import WhisperModel

AUDIO = pathlib.Path('/workspaces/toeic/toeic-review/audio')
OUT = pathlib.Path('/workspaces/toeic/transcripts_new')
OUT.mkdir(exist_ok=True)

default = [f'Test{b}{t}' for b in 'AB' for t in range(1, 7)]
tests = sys.argv[1:] or default
model = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=5)

for test in tests:
    out_file = OUT / f'{test}.json'
    if out_file.exists():
        print(f'{test}: already done', flush=True)
        continue
    result = {}
    t0 = time.time()
    files = sorted((AUDIO / test).glob('*.mp3'))
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
