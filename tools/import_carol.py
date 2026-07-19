#!/usr/bin/env python3
"""把 Carol Bai YouTube Part 2 題庫（/workspaces/toeic/carol_p2/）匯入網站。

輸入：carol_p2/questions.json（parse_questions.py 產出）＋ carol_p2/zh.json（Claude 翻譯，
鍵 "day-qn"，值 {"q": 中文題目, "opts": [中文A, B, C], "fixq": 修正英文題目?, "fixopts": [...]?)}。
動作（冪等，可重跑）：
  1. 依 cut_s/cut_e 從 raw/dayNN.mp3 切出 audio/TestD{t}/Part2_QNN.mp3（64kbps 單聲道）
     分回：5 天一回、每回 25 題（Day1–5 → TestD1 …），最後一回不足 25 題
  2. 更新 data/audio.js（TESTS/TEST_META 加 TestD*，經 carol_tests.json）
  3. 產出 data/listen2_carol.js（LISTEN2_CAROL，形狀同 LISTEN2）
  4. 把逐字稿（題目＋A/B/C，含中文）併入 data/transcripts.js
  5. bump version.txt
"""
import json, pathlib, re, subprocess, sys

REPO = pathlib.Path('/workspaces/toeic/toeic-review')
SRC = pathlib.Path('/workspaces/toeic/carol_p2')

def test_of(day):
    return f'TestD{(day - 1) // 5 + 1}'

def qnum_of(day, qn):
    return ((day - 1) % 5) * 5 + qn

def cut_clips(qs):
    tests = {}
    for q in qs:
        t, n = test_of(q['day']), qnum_of(q['day'], q['qn'])
        f = f'Part2_Q{n:02d}.mp3'
        out = REPO / 'audio' / t / f
        out.parent.mkdir(parents=True, exist_ok=True)
        dur = round(q['cut_e'] - q['cut_s'], 1)
        if not out.exists():
            r = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(SRC / 'raw' / f'day{q["day"]:02d}.mp3'),
                                '-ss', str(q['cut_s']), '-to', str(q['cut_e']),
                                '-ac', '1', '-b:a', '64k', '-y', str(out)],
                               capture_output=True, text=True)
            if r.returncode:
                sys.exit(f'ffmpeg failed for {t}/{f}: {r.stderr}')
        lvl = q['lvl']
        tests.setdefault(t, []).append(
            {'f': f, 'part': 'Part 2', 'label': f'第 {n} 題（Day{q["day"]} {lvl}）', 'dur': dur})
        q['_test'], q['_f'], q['_dur'] = t, f, dur
    for t in tests:
        tests[t].sort(key=lambda it: int(re.search(r'Q(\d+)', it['f']).group(1)))
    json.dump(tests, open('/workspaces/toeic/carol_tests.json', 'w'), ensure_ascii=False)
    return tests

def update_audio_js(tests):
    src = (REPO / 'data' / 'audio.js').read_text()
    m = re.search(r'const TESTS = (\{.*?\});\n', src, re.S)
    all_tests = json.loads(m.group(1))
    all_tests = {k: v for k, v in all_tests.items() if not re.match(r'TestD\d', k)}
    for k in sorted(tests, key=lambda x: int(x[5:])):
        all_tests[k] = tests[k]
    meta_m = re.search(r'(// 各模擬考的出處註記.*?const TEST_META = \{)(.*?)(\n\};)', src, re.S)
    meta_body = re.sub(r',?\n  "TestD\d+".*?\}', '', meta_m.group(2), flags=re.S).rstrip()
    if not meta_body.endswith(','):
        meta_body += ','
    days = {k: sorted(int(re.search(r'Day(\d+)', it['label']).group(1)) for it in v)
            for k, v in tests.items()}
    for k in sorted(tests, key=lambda x: int(x[5:])):
        d = days[k]
        meta_body += (f'\n  "{k}": {{"name": "Carol P2 第 {k[5:]} 回", '
                      f'"source": "Carol Bai YouTube Part 2（Day {d[0]}–{d[-1]}）"}},')
    meta_body = meta_body.rstrip(',')
    out = ('const TESTS = ' + json.dumps(all_tests, ensure_ascii=False) + ';\n'
           + meta_m.group(1) + meta_body + meta_m.group(3) + '\n')
    (REPO / 'data' / 'audio.js').write_text(out)

def build_listen2(qs, zh):
    items = []
    for q in sorted(qs, key=lambda x: (x['day'], x['qn'])):
        z = zh[f"{q['day']}-{q['qn']}"]
        qtext = z.get('fixq') or q['q']
        # 題面不留 "Number N."／"number 48"／"4." 這類前綴，並確保首字大寫
        qtext = re.sub(r'^(number\s+\w+[.,]?\s*|\d{1,3}[.,]\s*)', '', qtext, flags=re.I).strip()
        qtext = qtext[:1].upper() + qtext[1:] if qtext else qtext
        opts = z.get('fixopts') or [q['optA'], q['optB'], q['optC']]
        items.append({'q': qtext, 'qz': z['q'], 'opts': opts, 'optsz': z['opts'],
                      'id': f"{q['_test']}/{q['_f']}", 'dur': q['_dur'], 'ans': q['ans'],
                      'lvl': q['lvl'], 'day': q['day']})
    (REPO / 'data' / 'listen2_carol.js').write_text(
        '// Carol Bai YouTube Part 2 題庫：題目/選項/答案取自影片口播（答案有原文重播驗證），\n'
        '// 中文由 Claude 翻譯。由 tools/import_carol.py 產生，勿手改。\n'
        'const LISTEN2_CAROL = ' + json.dumps(items, ensure_ascii=False) + ';\n')
    return items

def update_transcripts(qs, zh):
    path = REPO / 'data' / 'transcripts.js'
    src = path.read_text()
    data = json.loads(src[src.index('{'):src.rindex('}') + 1])
    for k in [k for k in data if re.match(r'TestD\d', k)]:
        del data[k]
    for q in qs:
        z = zh[f"{q['day']}-{q['qn']}"]
        qtext = z.get('fixq') or q['q']
        opts = z.get('fixopts') or [q['optA'], q['optB'], q['optC']]
        rel = lambda t: round(max(0.0, t - q['cut_s']), 2)
        segs = [{'s': rel(q['w_start']), 'e': rel(q['a_start']), 't': qtext, 'z': z['q']}]
        marks = [(q['a_start'], q['b_start']), (q['b_start'], q['c_start']),
                 (q['c_start'], q['cut_e'])]
        for i, (s, e) in enumerate(marks):
            segs.append({'s': rel(s), 'e': rel(e), 't': f'({"ABC"[i]}) {opts[i]}', 'z': z['opts'][i]})
        data.setdefault(q['_test'], {})[q['_f']] = segs
    path.write_text('const TRANSCRIPTS = ' + json.dumps(data, ensure_ascii=False) + ';')

def main():
    qs = json.load(open(SRC / 'questions.json'))
    zh = json.load(open(SRC / 'zh.json'))
    missing = [f"{q['day']}-{q['qn']}" for q in qs if f"{q['day']}-{q['qn']}" not in zh]
    if missing:
        sys.exit(f'zh.json 缺 {len(missing)} 題翻譯：{missing[:10]}')
    tests = cut_clips(qs)
    update_audio_js(tests)
    items = build_listen2(qs, zh)
    update_transcripts(qs, zh)
    (REPO / 'data' / 'version.txt').write_text(
        __import__('datetime').datetime.now().strftime('%Y%m%d%H%M%S'))
    from collections import Counter
    print(f'匯入 {len(items)} 題、{len(tests)} 回；答案分布 {Counter(i["ans"] for i in items)}；'
          f'等級 {Counter(i["lvl"] for i in items)}')

if __name__ == '__main__':
    main()
