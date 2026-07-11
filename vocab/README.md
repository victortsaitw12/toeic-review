# 單字目錄 vocab/

把要新增的單字和單字本放進這裡，匯入後就會出現在網站的單字卡與單字本。

```
vocab/
  words/   ← 放「新單字」的 markdown（表格格式）
  books/   ← 放「單字本」（網站匯出的 .md，或手寫的 .md／.json）
```

## 一、新增單字（words/）

在 `vocab/words/` 建立任意檔名的 `.md`（例如 `2026-07-work.md`），內容用表格：

```markdown
| 單字 | 詞性 | 中文釋義 | 級距 | 英文例句 | 例句翻譯 |
| --- | --- | --- | --- | --- | --- |
| synergy | n. | 綜效；協同作用 | 3 | The merger created synergy. | 合併創造了綜效。 |
```

- **單字**、**中文釋義** 必填，其餘可留空。
- **級距** 填 1–4（1 基礎 / 2 中級 / 3 中高 / 4 高階），留空預設 3。
- 已存在的單字會被覆蓋更新，不會重複。

## 二、新增單字本（books/）

**做法 A — 從網站匯出（推薦，可跨裝置）：**
1. 在任一裝置的網站「單字管理 → 單字本管理」，點該單字本的「匯出 .md」。
2. 把下載的 `<單字本名>.md` 放進 `vocab/books/`。

**做法 B — 手寫：** 第一行 `# 單字本名稱`，下面用清單列出單字：

```markdown
# 常錯字
- synergy
- leverage
```

> 單字本裡的單字必須是單字卡已有的字（可先在 `words/` 新增再放進單字本）。

## 三、匯入 & 部署

把檔案放好後，在這個 workspace 對 Claude Code 說 **`/toeic-vocab`**，
它會自動執行匯入、驗證並部署上線。

或手動執行：

```bash
cd toeic-review
python3 tools/import_vocab.py      # 匯入到 data/words.js、data/books.js
git add -A && git commit -m "新增單字" && git push
```
