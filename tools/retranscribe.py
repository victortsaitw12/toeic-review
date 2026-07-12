#!/usr/bin/env python3
"""用較高品質設定（beam_size=5 + VAD）重新轉錄指定檔案，更新 transcripts_new JSON。

用法：retranscribe.py TestA3 Part4_Q95-97.mp3 [Part4_Q98-100.mp3 ...]
whisper beam_size=1 偶爾會漏整段或在靜音處鬼打牆，對可疑檔案用這支修復。
"""
import json, pathlib, sys
from faster_whisper import WhisperModel

test, files = sys.argv[1], sys.argv[2:]
path = pathlib.Path('/workspaces/toeic/transcripts_new') / f'{test}.json'
d = json.load(open(path))
model = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=5)
for f in files:
    segs, _ = model.transcribe(f'/workspaces/toeic/toeic-review/audio/{test}/{f}',
                               language='en', beam_size=5, vad_filter=True)
    d[f] = [{'s': round(s.start, 2), 'e': round(s.end, 2), 't': s.text.strip()}
            for s in segs if s.text.strip()]
    print(f'{f}: {len(d[f])} segs', flush=True)
json.dump(d, open(path, 'w'), ensure_ascii=False)
print('updated', path)
