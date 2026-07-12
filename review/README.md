# 錯題複習 — 記錄格式

做模擬考（尤其 Part 5）時，把**做錯或不熟的題目**記在這個資料夾的任何 `.md` 檔
（README.md 不會被匯入）。之後跟 Claude 說「匯入錯題」，或自己跑：

```bash
cd /workspaces/toeic/toeic-review
python3 tools/import_mistakes.py --dry   # 先預覽
python3 tools/import_mistakes.py         # 寫入 data/mistakes.js
```

匯入後網站的「錯題複習」分頁就能反覆練習這些題目。

## 格式

```markdown
# 國學A 模擬考 2          ← 來源（一個檔案可以有多個來源標題）

## Q101                    ← 題號（可省略）
The marketing team's proposal was ______ approved by the board of directors.

- (A) unanimously
- (B) unanimous
- (C) unanimity
- (D) more unanimous

答案：A
解析：修飾動詞 approved 要用副詞。      ← 可省略
標籤：詞性, 副詞                        ← 可省略，逗號分隔
```

規則：

- `# 標題` 是題目來源（哪本書哪一回）；沒寫的話用檔名當來源。
- `## 題號` 開始一題；懶得寫題號也可以直接寫題目，會自動切題。
- 選項要從 (A) 開始依序列，`- (A) xxx`、`(A) xxx`、`A. xxx` 都可以。
- `答案：A` 必填（冒號全半形都行）；`解析：`、`標籤：` 選填。
- 檔案怎麼分隨意：可以一次考試一個檔、一個月一個檔，都行。

## 範例

見 `example.md`（會被匯入網站，開始記自己的錯題後可以刪掉它再重新匯入）。
