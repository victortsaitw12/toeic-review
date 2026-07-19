# 多益複習網站 TOEIC Review

純靜態網站，包含：

- **今天（儀表板）** — 首頁一眼看到：最近模擬考粗估分數與趨勢線（含目標分數線）、
  今天到期該複習的單字數、還沒答對的錯題數、正確率最弱的 Part，各附一鍵直達練習。
- **單字卡** — 多益單字（單字、詞性、中文釋義、例句），支援翻卡、
  發音、隨機排序、標記「認識／不熟」（存在 localStorage）。
  發音優先用國學 A/B 本單字 MP3 切出來的**真人錄音**（約 2,800 字，見下方），
  沒收錄的字與例句退回瀏覽器語音合成（TTS）。
  採 Leitner 5 盒**間隔複習排程**（0/1/3/7/21 天），可只練「今天到期」的字。
- **模擬考聽力解析** — 5 份模擬考聽力，已切成每題（Part 1/2）或每組對話（Part 3/4）一個音檔，
  可逐題選擇播放，支援變速（0.6×–1.15×）、單檔循環、A-B 區間循環、倒退 3 秒。
- **真題聽力（逐題快答）**（模擬考試分頁）— **EZ 模擬考 5 回＋國學聽力藍本 10 回**的
  真題音檔逐題練，可選系列/回數／Part／題數：Part 1 看題本圖片聽四個描述選字母；
  Part 2 沿用真人 Part 2 題庫；Part 3/4 播整段對話（一段連答三題，音檔只自動播一次、
  可手動重聽），**題目與四個選項印在畫面上**——題目句取自逐字稿、選項由 Claude 依對話
  撰寫（EZ：`data/exam_ez34.js` 的 `EZ_LQ` 345 題；藍本：`data/exam_blue.js` 的
  `BLUE_LQ` 690 題），正解內容放在**官方答案卷**（EZ：`data/exam_ez.js` 的
  `EZ_ANSWERS`，1–100 聽力、101–200 閱讀備用；藍本：`exam_blue.js` 的 `BLUE_ANSWERS`，
  皆為書末答案頁 OCR）的字母位置；圖表題選項為推測、解析有註記需對照題本。
  答完亮英中對照與解析，答錯可收進聽力練習本，成績計入首頁最弱 Part 統計。
- **真人聽力 Part 2 快答**（模擬考試分頁）— 27 回共 **675 題**真人音檔應答題：
  播原始音檔、按鈕只有 (A)(B)(C)（比照真實考試選項不印出來），答完亮出英中逐字稿，
  答錯可一鍵把該段音檔收進聽力練習本回去跟讀／聽寫。題庫在 `data/listen2.js`，
  由 `tools/extract_part2.py` 從逐字稿切出題目與三個回應（正確答案由 Claude 判定，
  存 `review/part2_ans/*.tsv`，`--merge` 併入；EZ 5 回 125 題已對過官方答案卷，全數一致）。
- **配速訓練**（模擬考閱讀）— 考試中即時顯示領先／落後（目標 Part 5 每題 20 秒、
  Part 6 每題 30 秒、Part 7 每題 60 秒），交卷後附各 Part 實際耗時 vs 目標的配速分析，
  指出最拖時間的段落。
- **TOEIC 核心搭配詞** — `tools/extract_colloc.py` 維護 117 條高頻商用搭配詞
  （make a reservation、be subject to、on short notice…），例句 9 成取自 27 回逐字稿的
  真實句子，產出 `vocab/` 的 md 後走 `import_vocab.py` 匯入，自動建「搭配詞」單字本，
  翻卡／測驗／間隔複習全部沿用單字卡機制。
- **錯題複習** — 做模擬考（尤其 Part 5）記錄下來的錯題／不熟題，可反覆練習並追蹤答對答錯。
  錯題記在 `review/*.md`（格式見 `review/README.md`），用 `tools/import_mistakes.py` 匯入
  `data/mistakes.js`（或請 Claude「匯入錯題」）。**模擬考結果頁可一鍵把答錯的題目
  自動加進錯題本**（Part 3/4/6/7 會連原文一起帶入），存在瀏覽器 localStorage。
  錯題和單字一樣走 Leitner 5 盒**間隔複習**（0/1/3/7/21 天，存 `toeic-mi-srs`）：
  答對往上一盒、答錯打回第 1 盒，沒練過的一律視為今天到期 —— 避免「猜對一次就消失」
  造成的假性掌握。篩選有「今天該複習／還沒答對過的／全部題目」三種模式。
  另附**考點診斷**面板：以每題 `tags` 的**第一個標籤**當考點（詞性、時態、代名詞、
  介系詞、連接詞、字彙、片語動詞、假設語氣…），統計各考點正確率並標出最弱的一項，
  點一列就只練那個考點；`tags` 的第二個之後是細分標籤（如 `despite`、`徵才`），
  會依所選考點連動篩選。首頁「最弱考點」卡片也直接深連到這裡。
  站上模擬考的 Part 5/6 題目在 `data/exam_r.js` 各自標了 `cat`（考點），答錯收進錯題本時
  會用它當第一個標籤、Part 別退居第二個，所以**模擬考錯題和紙本錯題會合併統計在同一個考點下**；
  聽力與 Part 7 沒有文法考點可分，仍用 Part 別當考點。新增 Part 5/6 題目時記得補 `cat`。

## 部署到 GitHub Pages

1. 在 GitHub 建立一個新的 repository（例如 `toeic-review`，Public）。
2. 在本資料夾執行：

   ```bash
   git init
   git add .
   git commit -m "TOEIC review site"
   git branch -M main
   git remote add origin https://github.com/<你的帳號>/toeic-review.git
   git push -u origin main
   ```

3. 到 repo 的 **Settings → Pages**，Source 選 **Deploy from a branch**，
   Branch 選 `main` / `/ (root)`，儲存。
4. 一兩分鐘後網站會出現在 `https://<你的帳號>.github.io/toeic-review/`。

> 音檔約 156 MB，第一次 push 需要一點時間。GitHub 免費方案的容量限制（單檔 100 MB、
> repo 建議 1 GB 以內）都在範圍內。

## 檔案結構

```
index.html        # 網站本體（單頁應用，無外部相依）
data/words.js     # 1000 個單字資料
data/wordaudio.js # 單字 → 真人發音片段的對照表
data/audio.js     # 音檔清單（各模擬考、各題、時長）
audio/Test1..5/   # 切割好的聽力音檔（每題／每組一個 mp3）
audio/word/       # 單字發音片段（依首字母分資料夾）
```

## 單字真人發音（audio/word/）

單字發音片段有兩個來源，切割與產生對照表都是同一支腳本：

```
python3 tools/build_word_audio.py --dry-run   # 先看覆蓋率
python3 tools/build_word_audio.py             # 實際切割＋產生 data/wordaudio.js
```

**國學 A/B 本**的「04 單字MP3」是英文、中文交錯朗讀，而 whisper 轉錄的 TSV
（各教材資料夾的 `04_單字MP3_轉錄/`）英文、中文各自獨立一行，英文那行的起訖秒數
就是單字邊界，直接依時間戳切段即可。

**綠本**（`國學多益寫作綠本單字/`）的英中是**連著唸**的、段級時間戳不可靠
（單段長達 29 秒），所以要先重跑一次字級時間戳轉錄：

```
python3 tools/transcribe_green_words.py       # 產生 ../green_words/*.json（40 檔，CPU 約 1 小時）
```

綠本每個字唸兩次（英文、英文、中文），腳本偵測到重複就把兩次一起收進片段。

注意事項：

- whisper 偶爾會把整個檔切成**等長格點**（例如每段都剛好 2.0 秒），那種時間戳不是
  真實語音邊界，切出來會頭尾吃字。腳本用 `is_grid_snapped()` 自動整檔剔除
  （A/B 本 96 個檔中有 8 個），這些字就退回 TTS。
- 綠本片段的結尾要卡在**下一個 token 的起點**（不管它是中文翻譯還是別的英文字）：
  英中貼著唸，延伸過頭會吃到中文；而像「formal attire」這種相鄰的兩個單字，
  只擋中文會讓 `formal` 的片段把 `attire` 一起吃進去。
- 同一個字有多個候選片段時保留**最短**的，最不容易夾到隔壁的字。
  A/B 本的段級邊界比綠本的字級邊界保險，所以綠本只補 A/B 本沒有的字。
- 重跑會依 `audio/word/.manifest.json` 只重切來源或時間戳有變的字，並清掉過期片段。

## 登入密碼

網站有前端密碼閘門，預設密碼：`toeic1000`。

修改密碼：執行 `echo -n '新密碼' | sha256sum`，把結果取代 `index.html` 裡的
`PASS_HASH` 值後 push。
（注意：這只是前端保護，擋得住一般訪客，但 repo 是公開的，音檔網址仍可被直接存取。
需要真正的存取控制請改用 Cloudflare Pages + Cloudflare Access，見下方。）

## 單字管理（新增／修改／刪除）

網站的「單字管理」分頁可以直接新增、編輯、刪除單字與例句：

1. 變更會立刻存在瀏覽器 localStorage（單字卡馬上可用）。
2. 按「⬆ 同步到 GitHub」會把整份單字表 commit 回 `data/words.js`，
   網站自動重新部署，其他裝置約 1 分鐘後也會看到。
3. 同步需要 GitHub fine-grained token：
   GitHub → Settings → Developer settings → Fine-grained tokens → Generate new token，
   Repository access 只選 `toeic-review`，Permissions 給 **Contents: Read and write**。
   Token 只存在瀏覽器 localStorage，不會進入 repo。

## 需要真正的登入保護？改用 Cloudflare Pages（免費）

1. 註冊 Cloudflare → Workers & Pages → Create → Pages → **Connect to Git** → 選這個 repo
   （Build 設定全部留空，直接 Deploy），會得到 `xxx.pages.dev` 網址。
2. Zero Trust → Access → Applications → Add application → Self-hosted，
   Domain 填你的 `xxx.pages.dev`，Policy 設定只允許你的 Email（一次性驗證碼登入）。
3. 之後每次 push GitHub，Cloudflare 會自動重新部署；「單字管理」同步功能照常可用。

## 音檔來源

- 模擬考 1–5（`Test1..5`）：**EZ出版社 NEW TOEIC 模擬試題**（版權屬原出版社，僅供個人學習）
- 國學A 模擬考 1–6（`TestA1..A6`）、國學B 模擬考 1–6（`TestB1..B6`）：
  **國學多益模擬題 A本/B本**，來源已切好單題 MP3（`03_單題分割MP3`），
  用 `tools/import_gx.py` 轉 64kbps 單聲道並統一檔名後匯入
- 國學藍 模擬考 1–10（`TestC1..C10`）：**國學多益聽力藍本**（`02單題分割音檔`，
  扁平檔名 TestNN_XX.mp3，Part 由題號推導），用 `tools/import_blue.py` 匯入
- 來源註記在 `data/audio.js` 的 `TEST_META`，網站的跟讀頁會顯示

## 未來新增其他出版社的考題（SOP）

1. 準備音檔：
   - 若是**整回未切割**的 mp3（如 EZ 的兩檔一回）：執行 `tools/split.py`
     （修改開頭的 `FILES` 對照表）→ 依靜音自動切成每題一檔
   - 若出版社**已提供單題分割 MP3**（如國學 A/B 本）：仿照 `tools/import_gx.py`
     轉 64kbps 單聲道、檔名統一為 `PartN_Qxx[-yy].mp3`，直接輸出到 `audio/<Key>/`
2. 音檔放到 `audio/<Key>/`（Key 命名如 `Test6`、`TestA1`），
   用 `tools/build_audio_js.py` 的模式更新 `data/audio.js` 的 `TESTS`，並在 `TEST_META` 加上
   `"<Key>": {"name": "○○ 模擬考 1", "source": "○○出版社"}`
   （`name` 慣例＝出版社縮寫＋模擬考編號，全站顯示與跟讀/聽寫的來源選單都取自這裡）
3. 執行 `tools/transcribe_gx.py <Key>` 產生逐字稿（需 `pip install faster-whisper`；
   舊版整回切割用 `tools/transcribe.py`），輸出在 `/workspaces/toeic/transcripts_new/`
4. 翻譯：每個 segment 加中文 `z` 欄位，用 `tools/merge_transcripts.py <翻譯後.json>`
   併入 `data/transcripts.js`
5. `git add . && git commit && git push` 部署

（最簡單的做法：把新音檔放進工作目錄後，直接請 Claude Code 照這個 SOP 跑一遍。）

## 更新紀錄

- **2026-07-18**
  - 錯題複習新增 **Carol Bai 多益 Part 5 題庫共 132 題**（YouTube 課程題卡 OCR 抽題、
    答案與中文解析由 Claude 判定）：文法 74 題（詞性/時態/代名詞/介系詞/連接詞）、
    字彙片語 58 題。可在錯題本用「來源／標籤」篩選。
  - 新增**「今天」儀表板首頁**：分數趨勢線＋目標線、今日到期單字、未解錯題、最弱 Part 建議。
  - 單字卡改用 **Leitner 5 盒間隔複習排程**（0/1/3/7/21 天），可只練今日到期字；
    舊有的「認識／不熟」標記自動遷移成盒子與到期日，資料不遺失。
  - **模擬考結果頁一鍵「加入錯題複習」**：把答錯的題目自動灌進錯題本，
    Part 3/4/6/7 連對話／文章原文一起帶入，存本機 localStorage。
