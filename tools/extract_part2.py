#!/usr/bin/env python3
"""從逐字稿抽出 Part 2 的題目與三個回應，產生真人音檔聽力測驗的題庫骨架。

Part 2 的音檔本身就是完整一題（題目 + A/B/C 三個回應），逐字稿也全都有，
所以不用重新出題，只要把段落切成「題幹 / A / B / C」四塊即可。
唯一缺的是正確答案 —— 出版社沒附答案卷，由 Claude 依逐字稿判定後
寫進 review/part2_ans/*.tsv，再用 --merge 併入 data/listen2.js。

用法：
  python3 tools/extract_part2.py            # 解析並輸出待判定的題目（給 Claude 讀）
  python3 tools/extract_part2.py --stats    # 只看解析成功率
  python3 tools/extract_part2.py --merge    # 併入答案，寫出 data/listen2.js
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
ANSDIR = ROOT / 'review' / 'part2_ans'
OUT = DATA / 'listen2.js'
VERSION_TXT = DATA / 'version.txt'


def load_js(name, var):
    """data/*.js 是 `const VAR = {...};` 的單行 JSON。

    有些檔案（audio.js）在同一個檔裡宣告多個變數，所以不能直接吃到檔尾，
    用 raw_decode 只取出第一個完整的 JSON 值。
    """
    src = (DATA / name).read_text(encoding='utf-8')
    i = src.index('=', src.index('const ' + var)) + 1
    obj, _ = json.JSONDecoder().raw_decode(src[i:].strip())
    return obj


# 題號有幾種寫法：「Number 7.」「Number nine.」「Number 7 Does…」（無標點）、裸數字「8.」。
# 有 Number 開頭時標點可省；只有裸數字時一定要有標點，否則會誤吃到 "$30 for..." 這種回應。
NUM_RE = re.compile(r'^\s*(?:Number\s+[\w-]+\s*[.,:]?|\d{1,3}\s*[.,:])\s*', re.I)
# 一段裡塞了多個選項時用來切開："a. Report to X b. It helps Y"
SPLIT_RE = re.compile(r'(?:(?<=^)|(?<=\s))\(?([ABC])\)?[.)]\s+', re.I)
# 單獨一段的 "A." / "(A)" / "A" 是選項標記（大小寫都有）
OPT_RE = re.compile(r'^\s*\(?([ABC])\)?\s*[.,:]?\s*$', re.I)
# 選項標記和內容黏在同一段："A. It's right around the corner." / "a. By 10%"
OPT_INLINE_RE = re.compile(r'^\s*\(?([ABC])\)?\s*[.,:]\s*(\S.*)$', re.I)


def parse_clip(segs):
    """把一題 Part 2 的逐字稿段落切成 {q, opts[3]}；解析不出來回 None。"""
    texts = [s['t'].strip() for s in segs if s.get('t', '').strip()]
    zhs = [s.get('z', '').strip() for s in segs if s.get('t', '').strip()]

    # 找題號那一段當起點，前面的作答說明全部丟掉
    start = None
    for i, t in enumerate(texts):
        if NUM_RE.match(t):
            start = i
            break
    if start is None:
        return None

    q_txt = NUM_RE.sub('', texts[start]).strip()
    q_zh = re.sub(r'^第\s*\d+\s*題[。．,，]?\s*', '', zhs[start]).strip()

    # 選項標記常被 whisper 切在段落中間甚至跨段（"…A. I didn't know he was" / "visiting. B. …"），
    # 所以把題號之後的文字全部接成一條再切，不要逐段判斷。
    rest = ' '.join(texts[start + 1:]).strip()
    rest_zh = ''.join(zhs[start + 1:]).strip()
    body = (q_txt + ' ' + rest).strip() if q_txt else rest
    body_zh = (q_zh + rest_zh).strip() if q_zh else rest_zh

    opts, qhead = split_options(body)
    if not opts:
        return None
    opts_zh, qhead_zh = split_options(body_zh, zh=True)

    q_txt = qhead.strip()
    q_zh = (qhead_zh or '').strip()
    if not q_txt or not all(opts):
        return None
    return {'q': q_txt, 'qz': q_zh, 'opts': opts,
            'optsz': opts_zh if opts_zh else ['', '', '']}


def split_options(body, zh=False):
    """把「題幹 A… B… C…」切成 (三個選項, 題幹)；切不出來回 (None, body)。

    先找有標點的標記（A. / (B) / c)），這種最明確；找不到才退而求其次找
    沒有標點的大寫字母（"A White I think"）。後者只認大寫，否則像
    "Where can I buy a sofa?" 裡的 "a " 會被誤判成選項 A 的標記。
    """
    # 中文逐字稿無空格（「…哪裡？A。就在轉角處。」），標記前的界線改看標點；
    # 英文仍要求前面是行首或空白，免得單字裡的字母被誤認。
    if zh:
        pats = ((r'(?:(?<=^)|(?<=[。．？！?!，,：:）)\s]))\(?{L}\)?[.)。．、，:,]\s*', 0),)
    else:
        pats = ((r'(?:(?<=^)|(?<=\s))\(?{L}\)?[.)]\s*', re.I),
                (r'(?:(?<=^)|(?<=\s)){L}\s+', 0))
    for pat, flags in pats:
        pos, spans = 0, []
        for letter in 'ABC':
            m = re.compile(pat.replace('{L}', letter), flags).search(body, pos)
            if not m:
                spans = []
                break
            spans.append(m)
            pos = m.end()
        if len(spans) == 3:
            parts = []
            for i, m in enumerate(spans):
                end = spans[i + 1].start() if i + 1 < len(spans) else len(body)
                parts.append(trim_repeat(body[m.end():end].strip()))
            if all(parts):
                return parts, body[:spans[0].start()]
    return None, body


# whisper 偶爾把同一段重念一次（見 validate_transcripts.py 抓的幻覺重複），
# 表現成選項內容裡又冒出一組 A./B./C. 標記。標記後面必須還有內容才算重複，
# 這樣結尾是 "At terminal B." 這種正常內容就不會被誤砍。
REPEAT_RE = re.compile(r'(?:(?<=^)|(?<=\s))\(?[ABC]\)?[.)]\s+\S', re.I)


def trim_repeat(text):
    m = REPEAT_RE.search(text)
    return text[:m.start()].strip() if m else text


def collect():
    tests = load_js('audio.js', 'TESTS')
    trans = load_js('transcripts.js', 'TRANSCRIPTS')
    items, failed = [], []
    for tk in tests:
        for clip in tests[tk]:
            if clip.get('part') != 'Part 2':
                continue
            segs = trans.get(tk, {}).get(clip['f'])
            if not segs:
                failed.append((tk, clip['f'], '沒有逐字稿'))
                continue
            p = parse_clip(segs)
            if not p:
                failed.append((tk, clip['f'], '解析失敗'))
                continue
            p['id'] = f"{tk}/{clip['f']}"
            p['test'] = tk
            p['f'] = clip['f']
            p['dur'] = clip.get('dur', 0)
            items.append(p)
    return items, failed


def load_answers():
    """review/part2_ans/*.tsv：每行 `id<TAB>A|B|C`（# 開頭是註解）。"""
    ans = {}
    if not ANSDIR.exists():
        return ans
    for f in sorted(ANSDIR.glob('*.tsv')):
        for line in f.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            key, a = parts[0].strip(), parts[1].strip().upper()
            if a in 'ABC' and len(a) == 1:
                ans[key] = 'ABC'.index(a)
    return ans


def bump_version():
    import time
    VERSION_TXT.write_text(time.strftime('%Y%m%d%H%M%S'), encoding='utf-8')


def main():
    args = sys.argv[1:]
    items, failed = collect()

    if '--stats' in args or not args:
        # 統計走 stderr，stdout 才能直接導成純資料檔
        w = sys.stderr.write
        w(f'解析成功 {len(items)} 題 / 失敗 {len(failed)} 題\n')
        by = {}
        for it in items:
            by[it['test']] = by.get(it['test'], 0) + 1
        w('各回: ' + ' '.join(f'{k}:{v}' for k, v in by.items()) + '\n')
        for t, f, why in failed[:20]:
            w(f'  ✗ {t}/{f} — {why}\n')
        if '--stats' in args:
            return

    if '--merge' in args:
        ans = load_answers()
        keep = [it for it in items if it['id'] in ans]
        for it in keep:
            it['ans'] = ans[it['id']]
            for k in ('test', 'f'):
                it.pop(k, None)
        missing = len(items) - len(keep)
        OUT.write_text(
            '// 真人音檔 Part 2 題庫：題目與選項取自逐字稿，答案由 Claude 判定。\n'
            '// 由 tools/extract_part2.py --merge 產生，勿手改。\n'
            'const LISTEN2 = ' + json.dumps(keep, ensure_ascii=False) + ';\n',
            encoding='utf-8')
        bump_version()
        print(f'寫出 {OUT}：{len(keep)} 題（還缺答案 {missing} 題）')
        return

    # 預設：把待判定的題目印出來給 Claude 讀
    for it in items:
        print(f"{it['id']}\t{it['q']}\tA) {it['opts'][0]}\tB) {it['opts'][1]}\tC) {it['opts'][2]}")


if __name__ == '__main__':
    main()
