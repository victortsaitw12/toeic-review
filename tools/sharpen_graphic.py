#!/usr/bin/env python3
"""圖表題圖強化（文字/數字清晰化）：python3 tools/sharpen_graphic.py 輸入.png 輸出.png

題本 Part 3/4 的圖表掃描原生只有 ~240px 寬，網站放大後文字糊掉。
線稿（黑字白底）用：Lanczos 3x 升採樣 → 非銳化遮罩銳化 → 溫和對比拉伸
（灰底壓白、灰字壓深），保留抗鋸齒不做二值化以免斷筆畫。
需要 opencv：pip install --break-system-packages opencv-python-headless
"""
import sys

import cv2
import numpy as np

SCALE = 3            # 升採樣倍率
BLACK, WHITE = 40, 215   # 對比拉伸的黑點/白點（灰階）


def enhance(src, dst):
    img = cv2.imread(src, cv2.IMREAD_GRAYSCALE)
    up = cv2.resize(img, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_LANCZOS4)
    # 非銳化遮罩：高斯模糊當低頻，原圖減去低頻放大高頻邊緣
    blur = cv2.GaussianBlur(up, (0, 0), sigmaX=1.8)
    sharp = cv2.addWeighted(up, 1.45, blur, -0.45, 0)
    # 溫和對比拉伸：<BLACK→0、>WHITE→255，中間線性；不硬二值化保留灰階邊緣
    lut = np.clip((np.arange(256) - BLACK) * 255.0 / (WHITE - BLACK), 0, 255).astype(np.uint8)
    out = cv2.LUT(sharp, lut)
    cv2.imwrite(dst, out)
    print(f'{src}: {img.shape[1]}x{img.shape[0]} → {out.shape[1]}x{out.shape[0]}')


if __name__ == '__main__':
    enhance(sys.argv[1], sys.argv[2])
