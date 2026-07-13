#!/usr/bin/env python3
"""將 vocab/ 目錄裡的單字與單字本匯入網站資料檔。

- vocab/words/*.md  → 解析 markdown 表格 → 合併進 data/words.js（依單字去重、覆蓋更新）
- vocab/books/*.md  → 標題為單字本名、清單為單字 → 合併進 data/books.js
- vocab/books/*.json → 網站匯出的單字本 JSON → 合併進 data/books.js

用法：python3 tools/import_vocab.py       # 執行匯入
      python3 tools/import_vocab.py --dry # 只檢視不寫入
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORDS_JS = ROOT / 'data' / 'words.js'
BOOKS_JS = ROOT / 'data' / 'books.js'
VERSION_TXT = ROOT / 'data' / 'version.txt'
VOCAB = ROOT / 'vocab'
DRY = '--dry' in sys.argv

def bump_version():
    """更新部署版本號，讓前端強制重抓 data/*.js（破手機快取）。"""
    import datetime
    VERSION_TXT.write_text(datetime.datetime.now().strftime('%Y%m%d%H%M%S'), encoding='utf-8')

def load_js_array(path, varname):
    if not path.exists():
        return []
    text = path.read_text(encoding='utf-8')
    m = re.search(r'const\s+' + varname + r'\s*=\s*(\[.*\]);', text, re.S)
    return json.loads(m.group(1)) if m else []

def write_js_array(path, varname, data):
    path.write_text('const %s = %s;\n' % (varname, json.dumps(data, ensure_ascii=False, separators=(',', ':'))),
                    encoding='utf-8')

def is_sep(cells):
    return all(re.fullmatch(r'[\s:\-]+', c or '') for c in cells) and cells

def parse_word_md(path):
    """回傳該檔的單字 list。解析所有 | 開頭的表格列。"""
    out = []
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if is_sep(cells):
            continue
        w = cells[0] if len(cells) > 0 else ''
        if not w or w in ('單字', 'word', 'Word'):
            continue
        pos = cells[1] if len(cells) > 1 else ''
        zh = cells[2] if len(cells) > 2 else ''
        lv = cells[3] if len(cells) > 3 else ''
        ex = cells[4] if len(cells) > 4 else ''
        exzh = cells[5] if len(cells) > 5 else ''
        if not zh:
            print(f'  ⚠ 略過（缺中文釋義）: {w}  [{path.name}]')
            continue
        try:
            lvn = int(lv)
            if lvn not in (1, 2, 3, 4): lvn = 3
        except ValueError:
            lvn = 3
        out.append({'w': w, 'pos': pos, 'zh': zh, 'ex': ex, 'exzh': exzh, 'lv': lvn})
    return out

def parse_book_md(path):
    """回傳 (name, [words])。"""
    name, words = None, []
    for line in path.read_text(encoding='utf-8').splitlines():
        s = line.strip()
        m = re.match(r'#\s+(.*)', s)
        if m and name is None:
            name = m.group(1).strip()
            continue
        m = re.match(r'[-*]\s+(.*)', s)
        if m:
            w = m.group(1).strip()
            if w:
                words.append(w)
    if name is None:
        name = path.stem
    return name, words

def parse_book_json(path):
    """回傳 [(name, [words]), ...]。支援單一物件或陣列。"""
    data = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(data, dict):
        data = [data]
    return [(b['name'], list(b.get('words', []))) for b in data if b.get('name')]

# ---------- 匯入單字 ----------
words = load_js_array(WORDS_JS, 'WORDS')
by_key = {w['w'].lower(): i for i, w in enumerate(words)}
added = updated = 0
for f in sorted((VOCAB / 'words').glob('*.md')):
    if f.name == 'example.md':
        continue
    for e in parse_word_md(f):
        k = e['w'].lower()
        if k in by_key:
            words[by_key[k]] = e
            updated += 1
        else:
            by_key[k] = len(words)
            words.append(e)
            added += 1

# ---------- 匯入單字本 ----------
books = load_js_array(BOOKS_JS, 'BOOKS')
bidx = {b['name']: i for i, b in enumerate(books)}
valid = {w['w'] for w in words}
lower_map = {w['w'].lower(): w['w'] for w in words}
b_new = b_upd = 0
missing = []

def upsert_book(name, wlist):
    global b_new, b_upd
    clean = []
    for w in wlist:
        if w in valid:
            clean.append(w)
        elif w.lower() in lower_map:
            clean.append(lower_map[w.lower()])
        else:
            missing.append((name, w))
    if name in bidx:
        books[bidx[name]] = {'name': name, 'words': clean}
        b_upd += 1
    else:
        bidx[name] = len(books)
        books.append({'name': name, 'words': clean})
        b_new += 1

for f in sorted((VOCAB / 'books').glob('*.md')):
    if f.name == 'example.md':
        continue
    name, wlist = parse_book_md(f)
    upsert_book(name, wlist)
for f in sorted((VOCAB / 'books').glob('*.json')):
    for name, wlist in parse_book_json(f):
        upsert_book(name, wlist)

# ---------- 輸出 ----------
print(f'單字：新增 {added}、更新 {updated}，總計 {len(words)} 字')
print(f'單字本：新增 {b_new}、更新 {b_upd}，總計 {len(books)} 本')
if missing:
    print('⚠ 下列單字本引用了不存在的單字（已略過，請先在 vocab/words/ 新增該字）：')
    for name, w in missing:
        print(f'   [{name}] {w}')

if DRY:
    print('（--dry：未寫入檔案）')
else:
    write_js_array(WORDS_JS, 'WORDS', words)
    write_js_array(BOOKS_JS, 'BOOKS', books)
    bump_version()
    print('已寫入 data/words.js 與 data/books.js（版本號已更新）')
