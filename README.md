# 多益複習網站 TOEIC Review

純靜態網站，包含：

- **今天（儀表板）** — 首頁一眼看到：最近模擬考粗估分數與趨勢線（含目標分數線）、
  今天到期該複習的單字數、還沒答對的錯題數、正確率最弱的 Part，各附一鍵直達練習。
- **單字卡** — 多益單字（單字、詞性、中文釋義、例句），支援翻卡、
  瀏覽器發音（TTS）、隨機排序、標記「認識／不熟」（存在 localStorage）。
  採 Leitner 5 盒**間隔複習排程**（0/1/3/7/21 天），可只練「今天到期」的字。
- **模擬考聽力解析** — 5 份模擬考聽力，已切成每題（Part 1/2）或每組對話（Part 3/4）一個音檔，
  可逐題選擇播放，支援變速（0.6×–1.15×）、單檔循環、A-B 區間循環、倒退 3 秒。
- **錯題複習** — 做模擬考（尤其 Part 5）記錄下來的錯題／不熟題，可反覆練習並追蹤答對答錯。
  錯題記在 `review/*.md`（格式見 `review/README.md`），用 `tools/import_mistakes.py` 匯入
  `data/mistakes.js`（或請 Claude「匯入錯題」）。**模擬考結果頁可一鍵把答錯的題目
  自動加進錯題本**（Part 3/4/6/7 會連原文一起帶入），存在瀏覽器 localStorage。

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
data/audio.js     # 音檔清單（各模擬考、各題、時長）
audio/Test1..5/   # 切割好的聽力音檔（每題／每組一個 mp3）
```

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
  - 新增**「今天」儀表板首頁**：分數趨勢線＋目標線、今日到期單字、未解錯題、最弱 Part 建議。
  - 單字卡改用 **Leitner 5 盒間隔複習排程**（0/1/3/7/21 天），可只練今日到期字；
    舊有的「認識／不熟」標記自動遷移成盒子與到期日，資料不遺失。
  - **模擬考結果頁一鍵「加入錯題複習」**：把答錯的題目自動灌進錯題本，
    Part 3/4/6/7 連對話／文章原文一起帶入，存本機 localStorage。
