#!/usr/bin/env python3
"""掃描歪斜轉正（題本圖片用）：python3 tools/deskew.py 輸入.png 輸出.png

內容（照片/表格）是白底上的深色區塊：先用非白像素的 minAreaRect 抓傾斜角；
外緣軸對齊、內容卻歪的掃描（minAreaRect 會回 0°）退回霍夫直線，
取近水平長線的中位角。轉正後依內容範圍裁切、留 8px 白邊。
需要 opencv：pip install --break-system-packages opencv-python-headless
"""
import sys

import cv2
import numpy as np

WHITE = 235   # 灰階 >= 此值視為白底


def angle_min_area_rect(gray):
    mask = (gray < WHITE).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=2)
    _, (w, h), ang = cv2.minAreaRect(cv2.findNonZero(mask))
    if ang < -45:
        ang += 90
    elif ang > 45:
        ang -= 90
    return ang


def angle_hough(gray):
    edges = cv2.Canny(gray, 60, 160)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 720, threshold=40,
                            minLineLength=gray.shape[1] // 4, maxLineGap=6)
    if lines is None:
        return 0.0
    angs = [np.degrees(np.arctan2(y2 - y1, x2 - x1))
            for x1, y1, x2, y2 in lines.reshape(-1, 4)]
    angs = [a for a in angs if abs(a) < 20]
    return float(np.median(angs)) if angs else 0.0


def deskew(src, dst):
    img = cv2.imread(src)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ang = angle_min_area_rect(gray)
    how = 'minAreaRect'
    if abs(ang) < 0.8:   # 外緣軸對齊時 minAreaRect 測不到，改看表格/文字線
        ang, how = angle_hough(gray), 'hough'
    if abs(ang) < 0.8:
        print(f'{src}: 傾斜 {ang:.1f}° 忽略不轉')
        rot = img
    else:
        h, w = img.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
        rot = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
        print(f'{src}: 轉正 {ang:.2f}°（{how}）')
    g2 = cv2.cvtColor(rot, cv2.COLOR_BGR2GRAY)
    ys, xs = np.where(g2 < WHITE)
    pad = 8
    rot = rot[max(0, ys.min() - pad):min(rot.shape[0], ys.max() + pad),
              max(0, xs.min() - pad):min(rot.shape[1], xs.max() + pad)]
    cv2.imwrite(dst, rot)


if __name__ == '__main__':
    deskew(sys.argv[1], sys.argv[2])
