#!/usr/bin/env python3
"""Split TOEIC mock-test listening MP3s into per-question / per-set files.

Logic: answer pauses are long silences (>=2.5s). Silences separated by <10s
of audio (question readings, page-turn cues) are clustered into one item.
File 'a' (Q1-52): 6 Part1 + 25 Part2 questions + 7 Part3 sets.
File 'b' (Q53-100): 6 Part3 sets + 10 Part4 sets.
"""
import re, subprocess, sys, pathlib

SCRATCH = pathlib.Path('/tmp/claude-1000/-workspaces-toeic/34ceeff0-733f-49ef-bc00-5c8232b38a2b/scratchpad')
SRC = pathlib.Path('/workspaces/toeic')
OUT = SRC / 'split'

FILES = {
    '3a': ('TOIEC_MOCKTEST3a_1-52.mp3', 'Test3'),
    '3b': ('TOIEC_MOCKTEST3b_53-100.mp3', 'Test3'),
    '4a': ('TOIEC_MOCKTEST4a_1-52.mp3', 'Test4'),
    '4b': ('TOIEC_MOCKTEST4b_53-100.mp3', 'Test4'),
    '5a': ('TOIEC_MOCKTEST5a_1-52.mp3', 'Test5'),
    '5b': ('TOIEC_MOCKTEST5b_53-100.mp3', 'Test5'),
}

LONG = 2.5      # answer-pause silence threshold (s)
GAP = 10.0      # max audio gap inside one item's silence cluster (s)
PAD = 0.5       # cut this much before end of a pause, as lead-in for next item

def parse_silences(key):
    vals = []
    for line in open(SCRATCH / f'silence_{key}.txt'):
        m = re.match(r'silence_(start|end): ([0-9.]+)', line)
        vals.append((m.group(1), float(m.group(2))))
    pairs = []
    i = 0
    while i < len(vals):
        if vals[i][0] == 'start':
            if i + 1 < len(vals) and vals[i+1][0] == 'end':
                pairs.append((vals[i][1], vals[i+1][1]))
                i += 2
            else:  # trailing silence till EOF
                pairs.append((vals[i][1], vals[i][1] + 10.0))
                i += 1
        else:
            i += 1
    return pairs

def duration(path):
    out = subprocess.run(['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                          '-of', 'csv=p=0', str(path)], capture_output=True, text=True)
    return float(out.stdout.strip())

def clusters(silences, t_min):
    longs = [(s, e) for s, e in silences if e - s >= LONG and s >= t_min]
    groups = []
    for s, e in longs:
        if groups and s - groups[-1][-1][1] < GAP:
            groups[-1].append((s, e))
        else:
            groups.append([(s, e)])
    return [g[-1][1] for g in groups]   # end time of each item's final pause

def labels_a():
    lab = [f'Part1_Q{n:02d}' for n in range(1, 7)]
    lab += [f'Part2_Q{n:02d}' for n in range(7, 32)]
    lab += [f'Part3_Q{a}-{a+2}' for a in range(32, 52, 3)]
    return lab

def labels_b():
    lab = [f'Part3_Q{a}-{a+2}' for a in range(53, 70, 3)]
    lab += [f'Part4_Q{a}-{a+2}' for a in range(71, 100, 3)]
    return lab

def cut(src, start, end, dest):
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f'{start:.3f}']
    if end is not None:
        cmd += ['-t', f'{end - start:.3f}']
    cmd += ['-i', str(src), '-c', 'copy', str(dest)]
    subprocess.run(cmd, check=True)

for key, (fname, test) in FILES.items():
    src = SRC / fname
    dur = duration(src)
    sil = parse_silences(key)
    outdir = OUT / test
    outdir.mkdir(parents=True, exist_ok=True)

    segments = []  # (label, start, end|None)
    if key.endswith('a'):
        # Q1 starts after the short silence (~87-89s) that ends the Part 1
        # directions + example; everything before it is intro.
        q1 = [e for s, e in sil if 80 <= s <= 100 and 1.0 <= e - s <= 3.0]
        assert len(q1) == 1, f'{key}: Q1 start marker not found: {q1}'
        q1_start = q1[0]
        ends = clusters(sil, q1_start + 1)
        lab = labels_a()
        assert len(ends) == len(lab), f'{key}: expected {len(lab)} items, got {len(ends)}'
        segments.append(('00_Intro_Part1_Directions', 0.0, q1_start - PAD))
        prev = q1_start - PAD
    else:
        ends = clusters(sil, 0)
        lab = labels_b()
        assert len(ends) == len(lab), f'{key}: expected {len(lab)} items, got {len(ends)}'
        prev = 0.0

    for name, end in zip(lab, ends):
        e = None if end >= dur - 1.0 else end - PAD
        segments.append((name, prev, e))
        prev = e if e is not None else dur

    for name, s, e in segments:
        cut(src, s, e, outdir / f'{name}.mp3')
        shown = e if e is not None else dur
        print(f'{test}/{name}.mp3  [{s:7.1f} -> {shown:7.1f}]  {shown - s:6.1f}s')
    print()

print('done')
