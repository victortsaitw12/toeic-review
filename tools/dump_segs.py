#!/usr/bin/env python3
"""列出某回逐字稿的所有 segment，供翻譯用：file<TAB>idx<TAB>text"""
import json, sys
d = json.load(open(f'/workspaces/toeic/transcripts_new/{sys.argv[1]}.json'))
for f in sorted(d, key=lambda x: (x.split('_')[0], x)):
    for i, s in enumerate(d[f]):
        print(f'{f}\t{i}\t{s["t"]}')
