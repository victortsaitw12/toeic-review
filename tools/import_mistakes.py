#!/usr/bin/env python3
"""把 review/*.md 的錯題匯入 data/mistakes.js（錯題複習分頁的資料）。

Markdown 格式（見 review/README.md）：
  # 來源標題（例：國學A 模擬考 2）
  ## Q101              ← 題號（可省略，會用內容 hash 當 id）
  題目句子，空格用 ______
  - (A) 選項一
  - (B) 選項二
  - (C) 選項三
  - (D) 選項四
  答案：A
  解析：為什麼（可省略）
  標籤：詞性, 介系詞（可省略）

用法：
  python3 tools/import_mistakes.py         # 匯入並寫 data/mistakes.js
  python3 tools/import_mistakes.py --dry   # 只預覽不寫檔
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / 'review'
OUT = ROOT / 'data' / 'mistakes.js'
VERSION_TXT = ROOT / 'data' / 'version.txt'


def bump_version():
    """更新部署版本號，讓前端強制重抓 data/*.js（破手機快取）。"""
    import datetime
    VERSION_TXT.write_text(datetime.datetime.now().strftime('%Y%m%d%H%M%S'), encoding='utf-8')

OPT_RE = re.compile(r'^[-*]?\s*\(?([A-E])[.)、）]?\s+(.+?)\s*$')
ANS_RE = re.compile(r'^答案\s*[:：]\s*\(?([A-E])\)?\s*$')
EXP_RE = re.compile(r'^解析\s*[:：]\s*(.*)$')
TAG_RE = re.compile(r'^標籤\s*[:：]\s*(.*)$')


def flush(cur, out, warns, fname):
    if cur is None:
        return
    label = f"{fname} {cur['src']}#{cur['no'] or '?'}"
    q = ' '.join(cur['qlines']).strip()
    if not q and not cur['opts']:
        return  # 空題（例如只有標題）
    if not q:
        warns.append(f'{label}：沒有題目文字，略過')
        return
    if len(cur['opts']) < 2:
        warns.append(f'{label}：選項不足（{len(cur["opts"])} 個），略過')
        return
    if len(cur['opts']) != 4:
        warns.append(f'{label}：選項 {len(cur["opts"])} 個（Part 5 通常 4 個），仍匯入')
    if cur['ans'] is None:
        warns.append(f'{label}：缺「答案：X」，略過')
        return
    ai = ord(cur['ans']) - ord('A')
    if ai >= len(cur['opts']):
        warns.append(f'{label}：答案 {cur["ans"]} 超出選項範圍，略過')
        return
    no = cur['no'] or hashlib.sha1(q.encode()).hexdigest()[:8]
    item = {'id': f"{cur['src']}#{no}", 'src': cur['src'], 'no': cur['no'] or '',
            'q': q, 'opts': cur['opts'], 'ans': ai}
    if cur['exp']:
        item['exp'] = ' '.join(cur['exp']).strip()
    if cur['tags']:
        item['tags'] = cur['tags']
    out.append(item)


def parse_file(path, out, warns):
    src = path.stem
    cur = None
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if line.startswith('# ') and not line.startswith('## '):
            flush(cur, out, warns, path.name)
            cur = None
            src = re.sub(r'^來源\s*[:：]\s*', '', line[2:].strip())
            continue
        if line.startswith('## '):
            flush(cur, out, warns, path.name)
            cur = {'src': src, 'no': line[3:].strip(), 'qlines': [], 'opts': [],
                   'ans': None, 'exp': None, 'tags': [], 'in_exp': False}
            continue
        if cur is None:
            if line and not line.startswith('#'):
                # 沒寫 ## 題號就直接開始題目：自動開一題
                cur = {'src': src, 'no': '', 'qlines': [], 'opts': [],
                       'ans': None, 'exp': None, 'tags': [], 'in_exp': False}
            else:
                continue
        m = ANS_RE.match(line)
        if m:
            cur['ans'] = m.group(1)
            cur['in_exp'] = False
            continue
        m = EXP_RE.match(line)
        if m:
            cur['exp'] = [m.group(1)] if m.group(1) else []
            cur['in_exp'] = True
            continue
        m = TAG_RE.match(line)
        if m:
            cur['tags'] = [t.strip() for t in re.split(r'[,，、]', m.group(1)) if t.strip()]
            cur['in_exp'] = False
            continue
        m = OPT_RE.match(line)
        if m and (cur['opts'] or not cur['qlines'] or m.group(1) == 'A'):
            # 選項需從 A 開始連續出現，避免把題目裡的 "(a) ..." 誤判成選項
            expect = chr(ord('A') + len(cur['opts']))
            if m.group(1) == expect:
                cur['opts'].append(m.group(2))
                cur['in_exp'] = False
                continue
        if not line:
            cur['in_exp'] = False
            continue
        if cur['in_exp']:
            cur['exp'].append(line)
        elif not cur['opts']:
            cur['qlines'].append(line)
        else:
            # 選項之後、又不是答案/解析/標籤的文字：當成題目補充（例如兩行題幹寫在後面）
            cur['qlines'].append(line)
    flush(cur, out, warns, path.name)


def main():
    dry = '--dry' in sys.argv
    files = sorted(p for p in REVIEW.glob('*.md') if p.name.lower() != 'readme.md')
    out, warns = [], []
    for p in files:
        parse_file(p, out, warns)
    seen = {}
    for it in out:
        if it['id'] in seen:
            warns.append(f'重複題目 id「{it["id"]}」，保留後者')
        seen[it['id']] = it
    items = list(seen.values())
    for w in warns:
        print('⚠', w)
    by_src = {}
    for it in items:
        by_src.setdefault(it['src'], 0)
        by_src[it['src']] += 1
    print(f'共 {len(items)} 題（{len(files)} 個檔案）：'
          + '、'.join(f'{s} {n} 題' for s, n in by_src.items()))
    if dry:
        print('（--dry 預覽，未寫入）')
        return
    js = ('// 錯題複習資料，由 tools/import_mistakes.py 從 review/*.md 產生，勿手改\n'
          'const MISTAKES = ' + json.dumps(items, ensure_ascii=False) + ';\n')
    OUT.write_text(js, encoding='utf-8')
    bump_version()
    print(f'已寫入 {OUT.relative_to(ROOT)}（版本號已更新）')


if __name__ == '__main__':
    main()
