# 多益複習網站 TOEIC Review

純靜態網站，包含：

- **單字卡** — 刷刷鍋多益 1000 單字（單字、詞性、中文釋義、例句），支援翻卡、
  瀏覽器發音（TTS）、隨機排序、標記「認識／不熟」（存在 localStorage）、只複習不熟單字。
- **聽力跟讀** — 5 份模擬考聽力，已切成每題（Part 1/2）或每組對話（Part 3/4）一個音檔，
  可逐題選擇播放，支援變速（0.6×–1.15×）、單檔循環、A-B 區間循環、倒退 3 秒。

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
