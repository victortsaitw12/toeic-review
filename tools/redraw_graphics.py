#!/usr/bin/env python3
"""依原始掃描內容重繪 Part 3/4 圖表題為乾淨 SVG（向量、任意縮放不糊）。
輸出到 out_dir，檔名同題組（q62-64.svg…）。內容以原掃描為準逐一定義。
用法：python3 tools/redraw_graphics.py <out_dir>
"""
import os
import sys
import math

FONT = 'font-family="Arial, Helvetica, sans-serif"'
STROKE = "#111"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class SVG:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.parts = []

    def rect(self, x, y, w, h, fill="none", sw=2, stroke=STROKE, rx=0, dash=None):
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'
        if sw:
            s += f' stroke="{stroke}" stroke-width="{sw}"'
        if rx:
            s += f' rx="{rx}"'
        if dash:
            s += f' stroke-dasharray="{dash}"'
        self.parts.append(s + "/>")

    def line(self, x1, y1, x2, y2, sw=2, stroke=STROKE, dash=None):
        s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            s += f' stroke-dasharray="{dash}"'
        self.parts.append(s + "/>")

    def poly(self, pts, fill="none", sw=2, stroke=STROKE, closed=True):
        p = " ".join(f"{x},{y}" for x, y in pts)
        tag = "polygon" if closed else "polyline"
        self.parts.append(f'<{tag} points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def circle(self, cx, cy, r, fill="white", sw=2, stroke=STROKE):
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def path(self, d, fill="none", sw=2, stroke=STROKE):
        self.parts.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=17, anchor="middle", weight="normal", italic=False, fill=STROKE):
        st = f' font-style="italic"' if italic else ""
        self.parts.append(
            f'<text x="{x}" y="{y}" {FONT} font-size="{size}" font-weight="{weight}"{st} '
            f'text-anchor="{anchor}" fill="{fill}">{esc(s)}</text>')

    def dump(self):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">')
        bg = f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="white"/>'
        return head + bg + "".join(self.parts) + "</svg>"


def draw_table(colw, rows, rowh=40, pad=16, title_size=18, cell_size=16):
    """rows: list of rows; each row = list of cells.
    cell = str  OR  dict(t=text, span=int, bold=bool, align='c'|'l', fill=color, size=int, italic=bool)"""
    tw = sum(colw)
    th = rowh * len(rows)
    W, H = tw + pad * 2, th + pad * 2
    g = SVG(W, H)
    x0, y0 = pad, pad
    # cells + text
    for r, row in enumerate(rows):
        cy = y0 + r * rowh
        cx = x0
        ci = 0
        for cell in row:
            if isinstance(cell, str):
                cell = {"t": cell}
            span = cell.get("span", 1)
            cw = sum(colw[ci:ci + span])
            fill = cell.get("fill", "white")
            g.rect(cx, cy, cw, rowh, fill=fill, sw=1.6)
            t = cell.get("t", "")
            if t != "":
                align = cell.get("align", "c")
                size = cell.get("size", cell_size)
                weight = "bold" if cell.get("bold") else "normal"
                ital = cell.get("italic", False)
                ty = cy + rowh / 2 + size * 0.35
                if align == "l":
                    g.text(cx + 12, ty, t, size=size, anchor="start", weight=weight, italic=ital)
                else:
                    g.text(cx + cw / 2, ty, t, size=size, anchor="middle", weight=weight, italic=ital)
            cx += cw
            ci += span
    # outer border
    g.rect(x0, y0, tw, th, sw=2.4)
    return g


HDR = "#e9e9e9"


def h(t, **k):  # header cell
    d = {"t": t, "bold": True, "fill": HDR}
    d.update(k)
    return d


# ============================ Test1 ============================

def t1_62_64():  # 劇院座位圖
    g = SVG(360, 260)
    # 舞台（弧形簾幕）
    g.path("M30 30 Q180 -6 330 30 L330 92 Q180 74 30 92 Z", fill="#efefef", sw=2)
    g.text(180, 66, "Stage", size=22, weight="bold")
    # 走道分左右，各兩排座位 B(前) C(後)
    seats = [("B3", 60, 130), ("B4", 120, 130), ("B5", 220, 130), ("B6", 280, 130),
             ("C3", 60, 195), ("C4", 120, 195), ("C5", 220, 195), ("C6", 280, 195)]
    for lb, cx, cy in seats:
        g.rect(cx - 26, cy - 24, 52, 48, fill="white", sw=2, rx=4)
        g.text(cx, cy + 6, lb, size=17)
    return g


def t1_65_67():
    rows = [
        [h("Office", align="l"), h("Location")],
        [{"t": "Dawson Dental Clinic", "align": "l"}, "Suite 1022"],
        [{"t": "Jasmine Hair Salon", "align": "l"}, "Suite 1013"],
        [{"t": "Silver Linings Counseling", "align": "l"}, "Suite 2020"],
        [{"t": "LGB Construction", "align": "l"}, "Suite 2023"],
    ]
    g = draw_table([280, 180], rows, rowh=42)
    # 標題
    out = SVG(g.w, g.h + 34)
    out.text(out.w / 2, 24, "Edmonton Building Directory", size=18, weight="bold")
    out.parts.append(f'<g transform="translate(0,34)">{"".join(g.parts)}</g>')
    return out


def t1_68_70():  # 捷運四線路線圖
    g = SVG(452, 300)
    g.rect(20, 18, 412, 30, fill="#e0e0e0", sw=2, rx=14)
    g.text(226, 38, "Express Bus Terminal", size=15, weight="bold")
    lines = [
        ("Green Line", 122, ["George", "Bay", "Central Park"]),
        ("Yellow Line", 208, ["Leslie", "Victoria"]),
        ("Red Line", 294, []),
        ("Blue Line", 378, ["Yorkdale", "Wilbert", "Grand"]),
    ]
    top, bot = 78, 232
    for name, x, stops in lines:
        g.text(x, 66, name, size=13, weight="bold")
        # 往終點的箭頭線
        g.line(x, bot, x, top, sw=2.4)
        g.poly([(x, top - 8), (x - 5, top + 4), (x + 5, top + 4)], fill=STROKE, sw=0)
        n = len(stops)
        for i, st in enumerate(stops):
            sy = top + 24 + i * 46
            g.circle(x, sy, 6)
            g.text(x - 12, sy + 5, st, size=12, anchor="end")
    g.rect(20, 252, 412, 30, fill="#e0e0e0", sw=2, rx=4)
    g.text(226, 272, "Wilson Station", size=15, weight="bold")
    return g


def t1_95_97():  # 折線圖 New Customers
    g = SVG(420, 260)
    ox, oy = 78, 200
    ax_top, ax_right = 40, 390
    g.text(210, 30, "New Customers", size=17, weight="bold")
    g.line(ox, oy, ax_right, oy, sw=2)   # x
    g.line(ox, oy, ox, ax_top, sw=2)     # y
    yvals = [20000, 30000, 40000, 50000]
    ymin, ymax = 15000, 55000

    def py(v):
        return oy - (v - ymin) / (ymax - ymin) * (oy - ax_top)
    for v in yvals:
        yy = py(v)
        g.line(ox - 5, yy, ox, yy, sw=1.5)
        g.text(ox - 10, yy + 5, f"{v:,}", size=12, anchor="end")
    months = ["May", "June", "July", "Aug"]
    data = [20000, 30000, 50000, 40000]
    xs = [ox + 40 + i * 95 for i in range(4)]
    pts = [(xs[i], py(data[i])) for i in range(4)]
    for i, m in enumerate(months):
        g.text(xs[i], oy + 22, m, size=13)
    g.poly(pts, closed=False, sw=2.6)
    return g


def t1_98_100():  # 4 樓平面圖（Cafe + Gallery1-4）
    g = SVG(420, 250)
    g.text(210, 24, "4th floor", size=17, weight="bold")
    ox, oy, W, H = 24, 40, 372, 190
    g.rect(ox, oy, W, H, sw=2.4)
    # 內部分隔
    g.line(ox + 150, oy, ox + 150, oy + 120)          # cafe 右牆
    g.line(ox + 150, oy + 120, ox + 150, oy + H)      # gallery1 右牆延伸
    g.line(ox, oy + 120, ox + 150, oy + 120)          # cafe 下牆
    g.line(ox + 150, oy + 63, ox + W, oy + 63)        # gallery4/3 分界
    g.line(ox + 150, oy + 126, ox + W, oy + 126)      # gallery3/2 分界
    # Cafe 家具示意
    g.rect(ox + 30, oy + 22, 60, 34, sw=1.6)
    for cx in (ox + 40, ox + 60, ox + 80):
        g.circle(cx, oy + 74, 5, sw=1.4)
    g.text(ox + 100, oy + 100, "CAFE", size=14, weight="bold")
    g.text(ox + 273, oy + 36, "Gallery4", size=14)
    g.text(ox + 273, oy + 99, "Gallery3", size=14)
    g.text(ox + 273, oy + 162, "Gallery2", size=14)
    g.text(ox + 75, oy + 162, "Gallery1", size=14)
    return g


# ============================ Test2 ============================

def t2_65_67():
    rows = [
        [h("ITEM", align="l"), h("PRICE")],
        [{"t": "4X Smartphone", "align": "l"}, "$300"],
        [{"t": "Plan 30 (monthly)", "align": "l"}, "$40"],
        [{"t": "Insurance (monthly)", "align": "l"}, "$10"],
        [{"t": "Bluetooth headset", "align": "l"}, "$50"],
        [{"t": "TOTAL", "align": "l", "bold": True}, {"t": "$400", "bold": True}],
    ]
    return draw_table([260, 150], rows, rowh=40)


def t2_68_70():  # 圓餅圖 Top 4 Semiconductor Sales Leaders
    g = SVG(360, 300)
    g.text(180, 28, "The Top 4 Semiconductor Sales Leaders", size=13, weight="bold")
    cx, cy, r = 180, 170, 105
    slices = [("CNS", 44, "#cfcfcf"), ("Sona", 26, "#9a9a9a"),
              ("Xtreme", 17, "#bdbdbd"), ("TSD", 13, "#7d7d7d")]
    ang = -90.0
    for name, pct, col in slices:
        sweep = pct / 100 * 360
        a0 = math.radians(ang)
        a1 = math.radians(ang + sweep)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        large = 1 if sweep > 180 else 0
        g.path(f"M{cx} {cy} L{x0:.1f} {y0:.1f} A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f} Z",
               fill=col, sw=2)
        mid = math.radians(ang + sweep / 2)
        lx, ly = cx + r * 0.62 * math.cos(mid), cy + r * 0.62 * math.sin(mid)
        g.text(lx, ly + 4, name, size=13, weight="bold")
        ang += sweep
    return g


def t2_92_94():
    rows = [
        [h("ITEM", align="l"), h("QUANTITY")],
        [{"t": "Cookie Tray", "align": "l"}, "20"],
        [{"t": "Dozen Mini-Cupcakes", "align": "l"}, "100"],
        [{"t": "Fruit Tart", "align": "l"}, "50"],
        [{"t": "Classic Brownie", "align": "l"}, "150"],
    ]
    g = draw_table([280, 160], rows, rowh=40)
    out = SVG(g.w, g.h + 34)
    out.text(out.w / 2, 24, "Order Form", size=18, weight="bold")
    out.parts.append(f'<g transform="translate(0,34)">{"".join(g.parts)}</g>')
    return out


def t2_95_97():  # 街廓地圖：Formosa Plastics
    g = SVG(420, 280)
    # 街道
    g.text(210, 40, "Maple Road", size=14, weight="bold")
    g.line(60, 52, 360, 52, sw=2.4)
    g.text(210, 268, "Smith Road", size=14, weight="bold")
    g.line(60, 236, 360, 236, sw=2.4)
    g.text(34, 150, "12th", size=13, weight="bold", anchor="middle")
    g.text(34, 166, "Ave.", size=13, weight="bold", anchor="middle")
    g.line(52, 60, 52, 228, sw=2.4)
    g.text(392, 150, "13th", size=13, weight="bold", anchor="middle")
    g.text(392, 166, "Ave.", size=13, weight="bold", anchor="middle")
    g.line(368, 60, 368, 228, sw=2.4)
    # 建物
    g.rect(130, 110, 160, 90, fill="#eee", sw=2)
    g.text(210, 100, "Rear Entrance", size=12, weight="bold")
    g.line(190, 108, 230, 108, sw=3)   # 後門開口
    g.text(210, 160, "Formosa Plastics", size=14, weight="bold")
    return g


def t2_98_100():
    rows = [
        [h("Workshops", align="l"), h("Date")],
        [{"t": "Communication Skills", "align": "l"}, "March 10"],
        [{"t": "Resume Clinic", "align": "l"}, "April 7"],
        [{"t": "Second Career Information", "align": "l"}, "May 12"],
        [{"t": "Using Social Networking", "align": "l"}, "June 9"],
    ]
    return draw_table([300, 150], rows, rowh=42)


# ============================ Test3 ============================

def t3_62_64():
    rows = [
        [h("Company"), h("Location")],
        ["Avon Brochure", "Dallas"],
        ["Eddie", "Houston"],
        ["Wave Design", "New Orleans"],
        ["Vista Print", "Phoenix"],
    ]
    return draw_table([220, 200], rows, rowh=42)


def t3_65_67():
    rows = [
        [{"t": "Argos Bedding", "span": 3, "bold": True, "fill": HDR}],
        [{"t": ""}, {"t": ""}, {"t": "Order No. 8901"}],
        [h("Item"), h("Quantity"), h("Total Price")],
        ["Blanket", "1", "$15"],
        ["Pillow", "1", "$50"],
        ["Pillowcase", "4", "$12"],
        ["Curtain", "2", "$80"],
    ]
    return draw_table([170, 150, 150], rows, rowh=40)


def t3_68_70():
    rows = [
        [{"t": "Schedule", "span": 2, "bold": True, "fill": HDR}],
        ["Stage 1", "Suites"],
        ["Stage 2", "Ballroom"],
        ["Stage 3", "Pools"],
        ["Stage 4", "Building Exterior"],
    ]
    return draw_table([160, 220], rows, rowh=40)


def t3_95_97():  # 長條圖 Results by the number of votes
    g = SVG(460, 280)
    ox, oy = 60, 210
    top = 40
    g.text(230, 26, "Results by the number of votes", size=15, weight="bold")
    g.line(ox, oy, 440, oy, sw=2)
    g.line(ox, oy, ox, top, sw=2)
    ymax = 300
    for v in range(50, 300, 50):
        yy = oy - v / ymax * (oy - top)
        g.line(ox - 5, yy, ox, yy, sw=1.5)
        g.text(ox - 10, yy + 5, str(v), size=12, anchor="end")
    bars = [("More\nProfessional\nSeminars", 90), ("Support for\nExercise", 155),
            ("Flexible\nWork\nSchedule", 205), ("More\nPaid\nVacation", 265)]
    bw = 58
    gap = (440 - ox - 20 - bw * 4) / 4
    for i, (lb, v) in enumerate(bars):
        bx = ox + 18 + i * (bw + gap)
        bh = v / ymax * (oy - top)
        g.rect(bx, oy - bh, bw, bh, fill="#cccccc", sw=1.6)
        for j, ln in enumerate(lb.split("\n")):
            g.text(bx + bw / 2, oy + 18 + j * 13, ln, size=11)
    return g


def t3_98_100():
    rows = [
        [{"t": "Expense Report", "span": 3, "bold": True, "fill": HDR}],
        [h("DATE"), h("DESCRIPTION"), h("AMOUNT")],
        ["November 8", "Air fare", "$1000"],
        ["November 9", "Restaurant", "$45"],
        ["November 10", "Accommodation", "$220"],
        ["November 12", "Car Rental", "$300"],
    ]
    return draw_table([170, 200, 130], rows, rowh=40)


# ============================ Test4 ============================

def t4_65_67():
    rows = [
        [{"t": "Choose the speed that suits your needs", "span": 4, "bold": True, "fill": HDR}],
        ["15\nMegabytes", "25\nMegabytes", "50\nMegabytes", "100\nMegabytes"],
        ["$70", "$90", "$100", "$150"],
    ]
    # 多行儲存格特別處理
    colw = [130, 130, 130, 130]
    g = SVG(sum(colw) + 32, 40 + 60 + 40 + 32)
    x0, y0 = 16, 16
    g.rect(x0, y0, sum(colw), 40, fill=HDR, sw=1.6)
    g.text(g.w / 2, y0 + 26, "Choose the speed that suits your needs", size=16, weight="bold")
    # 速度列（兩行）
    yy = y0 + 40
    labels = ["15\nMegabytes", "25\nMegabytes", "50\nMegabytes", "100\nMegabytes"]
    for i, lb in enumerate(labels):
        bx = x0 + sum(colw[:i])
        g.rect(bx, yy, colw[i], 60, sw=1.6)
        for j, ln in enumerate(lb.split("\n")):
            g.text(bx + colw[i] / 2, yy + 26 + j * 20, ln, size=16)
    # 價格列
    yy2 = yy + 60
    prices = ["$70", "$90", "$100", "$150"]
    for i, p in enumerate(prices):
        bx = x0 + sum(colw[:i])
        g.rect(bx, yy2, colw[i], 40, sw=1.6)
        g.text(bx + colw[i] / 2, yy2 + 26, p, size=16)
    g.rect(x0, y0, sum(colw), 140, sw=2.4)
    return g


def t4_68_70():
    rows = [
        [{"t": "Extension Number", "span": 2, "bold": True, "fill": HDR}],
        [{"t": "Information Desk", "align": "l"}, "120"],
        [{"t": "Printing Station", "align": "l"}, "130"],
        [{"t": "Lost and Found", "align": "l"}, "140"],
        [{"t": "Facilities", "align": "l"}, "150"],
    ]
    return draw_table([230, 130], rows, rowh=40)


def t4_92_94():  # 辦公室平面圖
    g = SVG(440, 250)
    ox, oy, W, H = 20, 24, 400, 200
    g.rect(ox, oy, W, H, sw=2.4)
    # 左側：Office1 / Rest Room / Office2
    g.line(ox, oy + 66, ox + 150, oy + 66)
    g.line(ox + 150, oy, ox + 150, oy + 132)
    g.line(ox, oy + 132, ox + 150, oy + 132)
    g.text(ox + 75, oy + 34, "Office 1", size=13)
    g.text(ox + 75, oy + 100, "Rest Room", size=13)
    g.text(ox + 75, oy + 170, "Office 2", size=13)
    # 右側：Employee Lounge / Supply Room / Office3 / Office4
    g.line(ox + 250, oy, ox + 250, oy + H)
    g.text(ox + 325, oy + 34, "Employee Lounge", size=12)
    g.line(ox + 250, oy + 66, ox + W, oy + 66)
    g.text(ox + 325, oy + 92, "Supply Room", size=12)
    g.line(ox + 250, oy + 112, ox + W, oy + 112)
    g.text(ox + 325, oy + 138, "Office 3", size=13)
    g.line(ox + 250, oy + 158, ox + W, oy + 158)
    g.text(ox + 325, oy + 186, "Office 4", size=13)
    # 中央樓梯
    g.rect(ox + 165, oy + 150, 70, 50, fill="#eee", sw=1.6)
    for k in range(1, 5):
        g.line(ox + 165, oy + 150 + k * 10, ox + 235, oy + 150 + k * 10, sw=1)
    g.text(ox + 200, oy + 142, "Staircase", size=12)
    return g


def t4_95_97():
    rows = [
        [{"t": "Jolly Doughnut Shop", "span": 2, "bold": True, "fill": HDR}],
        [h("Free Gift"), h("Location")],
        ["Sport Bottle", "Bowles"],
        ["Eco Bag", "Rivers Mall"],
        ["Key Holder", "Lindbergh"],
        ["Coffee Mug", "Florissant"],
    ]
    return draw_table([200, 200], rows, rowh=40)


def t4_98_100():  # Monday Schedule
    rows = [[{"t": "Monday Schedule", "span": 2, "bold": True, "fill": HDR}]]
    sched = {"9:00": "Court hearing", "10:00": "", "11:00": "Marketing meeting",
             "12:00": "Lunch", "13:00": "", "14:00": "Strategy meeting",
             "15:00": "", "16:00": "Client consultation"}
    for tm, act in sched.items():
        rows.append([{"t": tm}, {"t": act, "align": "l"}])
    return draw_table([90, 250], rows, rowh=34)


# ============================ Test5 ============================

def t5_62_64():
    rows = [
        [{"t": "Arrivals", "span": 3, "bold": True, "fill": HDR}],
        [h("From"), h("Status"), h("Estimated Time")],
        ["Moscow", "Canceled", "7:00"],
        ["London", "Delayed", "10:40"],
        ["Munich", "On Time", "14:00"],
        ["Philadelphia", "On Time", "15:30"],
    ]
    return draw_table([160, 160, 170], rows, rowh=40)


def t5_65_67():  # 公車環狀路線
    g = SVG(460, 300)
    g.rect(30, 18, 400, 28, fill="#d9d9d9", sw=2, rx=13)
    g.text(230, 37, "Bus Route", size=15, weight="bold")
    # 矩形路線：上邊(往左箭頭) 右邊 下邊 左邊
    L, R, T, B = 60, 400, 90, 250
    g.poly([(R, T), (L, T)], closed=False, sw=2.6)   # 上：往左
    g.poly([(L + 12, T - 7), (L, T), (L + 12, T + 7)], fill=STROKE, sw=0)
    g.line(R, T, R, 170, sw=2.6)
    g.line(L, 170, R, 170, sw=2.6)
    g.line(L, 170, L, B, sw=2.6)
    g.line(L, B, R, B, sw=2.6)
    stops = [("King George University", 150, T), ("Marine Drive Station", 330, T),
             ("Waterfront", 150, 170), ("Commercial Street", 330, 170),
             ("TRC Airport", 150, B)]
    for name, x, y in stops:
        g.circle(x, y, 6)
        g.text(x, y + 22, name, size=12)
    # 公車圖示（下邊靠右）
    bx, by = 350, B
    g.rect(bx, by - 14, 46, 22, fill="#eee", sw=1.6, rx=3)
    g.circle(bx + 12, by + 10, 5, fill="#333", sw=1.2)
    g.circle(bx + 34, by + 10, 5, fill="#333", sw=1.2)
    return g


def t5_68_70():  # 辦公室平面圖（Lounge/Meeting Room/Office1／下排 Office2-4，無樓梯）
    g = SVG(440, 230)
    ox, oy, W, H = 20, 20, 400, 190
    by = oy + 118            # 下排分界
    g.rect(ox, oy, W, H, sw=2.4)
    # Lounge（左上）
    g.line(ox + 150, oy, ox + 150, oy + 68)
    g.line(ox, oy + 68, ox + 150, oy + 68)
    g.line(ox, oy + 30, ox, oy + 52, stroke="white", sw=3)   # 左牆門開口
    g.text(ox + 75, oy + 40, "Lounge", size=13)
    # 右上：Meeting Room + Office 1
    g.line(ox + 258, oy, ox + 258, by)
    g.line(ox + 258, oy + 58, ox + W, oy + 58)
    g.text(ox + 329, oy + 26, "Meeting", size=12)
    g.text(ox + 329, oy + 44, "Room", size=12)
    g.text(ox + 329, oy + 92, "Office 1", size=12)
    # 下排三間 Office 2/3/4
    g.line(ox, by, ox + W, by)
    g.line(ox + 138, by, ox + 138, oy + H)
    g.line(ox + 268, by, ox + 268, oy + H)
    g.text(ox + 69, by + 42, "Office 2", size=13)
    g.text(ox + 203, by + 42, "Office 3", size=13)
    g.text(ox + 334, by + 42, "Office 4", size=13)
    return g


def t5_95_97():  # 流程圖
    g = SVG(360, 430)
    g.rect(14, 14, 332, 402, sw=2)
    steps = ["Idea Generation", "Idea Screening", "Feature Specification",
             "Development", "Testing", "Launching"]
    y = 50
    step = 66
    for i, s in enumerate(steps):
        g.text(180, y, s, size=16, weight="bold")
        if i < len(steps) - 1:
            ay = y + 16
            g.poly([(172, ay), (188, ay), (188, ay + 18), (197, ay + 18),
                    (180, ay + 36), (163, ay + 18), (172, ay + 18)], fill="white", sw=1.8)
        y += step
    return g


def t5_98_100():  # Alamo Steakhouse 折價券
    g = SVG(440, 210)
    g.rect(16, 16, 408, 178, sw=2.2, dash="7,5")
    # 條碼
    widths = [3, 2, 4, 2, 3, 5, 2, 3, 2, 4, 3, 2, 5, 2, 3, 2, 4, 2]
    bx = 40
    for i, w in enumerate(widths):
        if i % 2 == 0:
            g.rect(bx, 60, w, 90, fill="#111", sw=0)
        bx += w + 2
    # 文字
    g.text(255, 56, "Alamo Steakhouse", size=24, weight="bold")
    g.text(255, 84, "Lunch & Dinner", size=16)
    g.text(230, 126, "10% OFF", size=34, weight="bold")
    # 餐點圖示（右上，避開下方細字）
    g.circle(388, 66, 22, fill="#eee", sw=2)
    g.path("M372 66 Q388 50 404 66", fill="none", sw=2)
    g.text(220, 176, "Not valid with already discounted group rates. Valid through March 31.",
           size=11)
    return g


# ============================ 藍本 TestC3 ============================

def tc3_62_64():  # 庫存表 Inventory List
    rows = [
        [{"t": "Inventory List", "span": 2, "bold": True, "fill": HDR}],
        [{"t": "Item #3851", "span": 2, "bold": True}],
        [{"t": "Red Pullover Sweater", "span": 2}],
        [h("Size"), h("Units in Stock")],
        ["Extra Small", "6"],
        ["Small", "11"],
        ["Medium", "9"],
        ["Large", "15"],
    ]
    return draw_table([200, 200], rows, rowh=38)


def tc3_65_67():  # 路線圖：Hotel -> Airport，四條街環狀繞行
    g = SVG(430, 250)
    hx, hy = 55, 120
    ax = 375
    streets = [
        ("Dale Street – 33 minutes", -72),
        ("Lily Street – 27 minutes", -26),
        ("Pine Street – 31 minutes", 30),
        ("Red Street – 29 minutes", 74),
    ]
    for label, dy in streets:
        cy = hy + 2 * dy
        g.path(f"M{hx} {hy} Q{(hx + ax) // 2} {cy} {ax} {hy}", fill="none", sw=2)
        g.text((hx + ax) // 2, hy + dy + (15 if dy > 0 else -8), label, size=13, italic=True)
    g.circle(hx, hy, 15, fill="#cfcfcf", sw=2)
    g.text(hx, hy + 40, "Hotel", size=14, weight="bold")
    g.text(ax + 4, hy + 40, "Airport", size=14, weight="bold")
    # 簡易飛機圖示
    g.path(f"M{ax - 8} {hy - 10} l34 -6 l-11 10 l11 7 l-34 -5 z", fill="#8a8a8a", sw=1.2)
    return g


def _linechart(title, yvals, ymin, ymax, months, data, ylabel_fmt):
    g = SVG(480, 240)
    ox, oy = 100, 190
    top, right = 42, 420
    g.text(240, 28, title, size=16, weight="bold")
    g.line(ox, oy, right, oy, sw=2)
    g.line(ox, oy, ox, top, sw=2)

    def py(v):
        return oy - (v - ymin) / (ymax - ymin) * (oy - top)
    for v in yvals:
        yy = py(v)
        g.line(ox - 5, yy, ox, yy, sw=1.5)
        g.text(ox - 10, yy + 5, ylabel_fmt(v), size=11, anchor="end")
    n = len(months)
    xs = [ox + 40 + i * ((right - ox - 40) / (n - 1)) for i in range(n)]
    pts = [(xs[i], py(data[i])) for i in range(n)]
    for i, m in enumerate(months):
        g.text(xs[i], oy + 22, m, size=11)
    g.poly(pts, closed=False, sw=2.4)
    for x, y in pts:
        g.circle(x, y, 3, fill="white", sw=1.6)
    return g


def tc3_68_70():  # 折線圖 Delver Group Profits
    return _linechart("Delver Group Profits",
                      [60000, 80000, 100000, 120000], 55000, 125000,
                      ["February", "March", "April", "May"],
                      [88000, 101000, 95000, 78000],
                      lambda v: f"${v:,}")


def tc3_95_97():  # 訂閱折扣表
    rows = [
        [h("Length of Subscription"), h("Discount")],
        ["One month", "$50"],
        ["Three months", "$100"],
        ["Six months", "$200"],
        ["One Year", "$400"],
    ]
    return draw_table([240, 150], rows, rowh=40)


def tc3_98_100():  # 折價券 Quick Refresh（虛線框＋剪刀）
    g = SVG(400, 250)
    g.rect(16, 16, 368, 218, sw=2, dash="6,5")
    g.text(356, 36, "✂", size=22)   # 剪刀
    g.text(34, 58, "SAVE BIG on Quick Refresh!", size=19, weight="bold", anchor="start")
    lines = [
        "10% off travel-sized bottles",
        "15% off regular-sized bottles",
        "20% off deluxe-sized bottles",
        "25% off economy-sized bottles",
    ]
    for i, ln in enumerate(lines):
        g.text(40, 96 + i * 27, ln, size=15, anchor="start")
    g.text(200, 208, "Valid at all CityMart stores", size=14)
    g.text(200, 228, "Expires January 10", size=14)
    return g


# ============================ 藍本 TestC4 ============================

def tc4_62_64():  # 流程圖 Project Management Process（水平四階段）
    g = SVG(430, 170)
    g.text(215, 30, "Project Management Process", size=17, weight="bold")
    boxes = [
        ("Stage 1", "Review", "budget"),
        ("Stage 2", "Submit", "proposal"),
        ("Stage 3", "Choose", "candidates"),
        ("Stage 4", "Assign", "tasks"),
    ]
    bw, bh, gap, x0, y0 = 88, 74, 18, 16, 58
    for i, (a, b, c) in enumerate(boxes):
        bx = x0 + i * (bw + gap)
        g.rect(bx, y0, bw, bh, sw=2)
        g.text(bx + bw / 2, y0 + 26, a, size=15, weight="bold")
        g.text(bx + bw / 2, y0 + 47, b, size=13)
        g.text(bx + bw / 2, y0 + 63, c, size=13)
        if i < 3:
            axx = bx + bw
            g.line(axx, y0 + bh / 2, axx + gap, y0 + bh / 2, sw=2)
            g.poly([(axx + gap, y0 + bh / 2), (axx + gap - 7, y0 + bh / 2 - 5),
                    (axx + gap - 7, y0 + bh / 2 + 5)], fill=STROKE, sw=0)
    return g


def tc4_65_67():  # 樓層目錄 TechnoForce Directory
    rows = [
        [{"t": "TechnoForce Directory", "span": 2, "bold": True, "fill": HDR}],
        ["Floor 4", "Research and Development"],
        ["Floor 3", "Accounting"],
        ["Floor 2", "Human Resources"],
        ["Floor 1", "Marketing"],
    ]
    return draw_table([120, 250], rows, rowh=42)


def tc4_68_70():  # 公園步道地圖
    g = SVG(400, 240)
    g.rect(12, 12, 376, 216, sw=2)

    def box(x, y, w, ht, txt, size=13, bold=False, fill="white"):
        g.rect(x, y, w, ht, fill=fill, sw=2 if bold else 1.8)
        ls = txt.split("\n")
        for j, ln in enumerate(ls):
            g.text(x + w / 2, y + ht / 2 + 5 - (len(ls) - 1) * 8 + j * 16, ln,
                   size=size, weight="bold" if bold else "normal")
    box(34, 30, 92, 40, "Waterfall")
    box(150, 30, 74, 40, "Lake")
    box(292, 24, 84, 48, "Picnic\nArea")
    box(292, 108, 84, 40, "Campground")
    box(150, 168, 120, 42, "Park Entrance", size=14, bold=True, fill="#f0f0f0")

    def dtrail(x1, y1, x2, y2):
        g.line(x1, y1, x2, y2, sw=2.2, stroke="#999", dash="2,5")
    dtrail(165, 168, 82, 72)     # Trail A -> Waterfall
    dtrail(200, 168, 188, 72)    # Trail B -> Lake
    dtrail(250, 168, 296, 74)    # Trail C -> Picnic Area
    dtrail(270, 182, 300, 128)   # Trail D -> Campground
    g.text(52, 150, "Trail A", size=12, italic=True)
    g.text(152, 120, "Trail B", size=12, italic=True)
    g.text(250, 122, "Trail C", size=12, italic=True)
    g.text(336, 172, "Trail D", size=12, italic=True)
    return g


def tc4_95_97():  # 平面圖：上排 Area A/B/Manager，走廊，下排 Storage/Area C/D
    g = SVG(400, 210)
    ox, oy, W, H = 20, 20, 360, 170
    colw = W / 3
    top_h, corr_h = 62, 40
    bot_y = oy + top_h + corr_h
    g.rect(ox, oy, W, H, sw=2.4)
    g.rect(ox, oy + top_h, W, corr_h, fill="#dcdcdc", sw=1.4)   # 走廊
    for k in (1, 2):
        g.line(ox + k * colw, oy, ox + k * colw, oy + top_h)
        g.line(ox + k * colw, bot_y, ox + k * colw, oy + H)

    def door(cx, wy, dirn):   # dirn=+1 門開向下(走廊), -1 向上
        g.line(cx - 13, wy, cx + 13, wy, stroke="white", sw=3)
        g.line(cx - 13, wy, cx - 13, wy + dirn * 15, sw=1.2)
        g.path(f"M{cx - 13} {wy + dirn * 15} A15 15 0 0 {1 if dirn > 0 else 0} {cx + 13} {wy}",
               fill="none", sw=1.1)
    for k in range(3):
        cx = ox + (k + 0.5) * colw
        door(cx, oy + top_h, 1)          # 上排房間開向走廊
        door(cx, bot_y, -1)              # 下排房間開向走廊
    labels_top = ["Area A", "Area B", "Manager's\nOffice"]
    labels_bot = ["Storage\nCloset", "Area C", "Area D"]
    for k in range(3):
        cx = ox + (k + 0.5) * colw
        for grp, cy0 in ((labels_top, oy + 24), (labels_bot, bot_y + 24)):
            ls = grp[k].split("\n")
            for j, ln in enumerate(ls):
                g.text(cx, cy0 + j * 16, ln, size=13)
    return g


def tc4_98_100():  # 折線圖 Monthly Number of Readers
    return _linechart("Monthly Number of Readers",
                      [26000, 28000, 30000, 32000, 34000, 36000], 25500, 36500,
                      ["September", "October", "November", "December"],
                      [28000, 35000, 32000, 30000],
                      lambda v: f"{v:,}")


# ============================ 藍本 TestC5 ============================

def tc5_62_64():  # 公車站牌：Bus Number / Information 表格＋站牌圖示
    g = SVG(430, 250)
    # 站牌（圓形招牌內畫公車）＋立柱
    cx, cy, r = 215, 40, 27
    g.line(cx, cy + r, cx, 72, sw=3)
    g.circle(cx, cy, r, fill="white", sw=2)
    g.rect(cx - 17, cy - 9, 34, 17, fill="#555", sw=1.2, stroke="#555", rx=3)
    for k in range(4):                                     # 車窗
        g.rect(cx - 14 + k * 8, cy - 6, 5, 6, fill="white", sw=0, stroke="white")
    g.circle(cx - 10, cy + 9, 2.6, fill="#555", sw=0.8, stroke="#555")
    g.circle(cx + 10, cy + 9, 2.6, fill="#555", sw=0.8, stroke="#555")
    # 表格
    colw = [150, 248]
    rows = [
        [h("Bus Number"), h("Information")],
        ["180", {"t": "Express to Grayfield Station", "align": "l"}],
        ["195", {"t": "Express to Windsor Station", "align": "l"}],
        ["199", {"t": "Local to Windsor Station", "align": "l"}],
        ["210", {"t": "Local to Grayfield Station", "align": "l"}],
    ]
    x0, y0, rowh = 16, 74, 34
    for ri, row in enumerate(rows):
        cyr = y0 + ri * rowh
        cxx = x0
        for ci, cell in enumerate(row):
            if isinstance(cell, str):
                cell = {"t": cell}
            cw = colw[ci]
            g.rect(cxx, cyr, cw, rowh, fill=cell.get("fill", "white"), sw=1.6)
            ty = cyr + rowh / 2 + 6
            if cell.get("align") == "l":
                g.text(cxx + 14, ty, cell["t"], size=16, anchor="start",
                       weight="bold" if cell.get("bold") else "normal")
            else:
                g.text(cxx + cw / 2, ty, cell["t"], size=16,
                       weight="bold" if cell.get("bold") else "normal")
            cxx += cw
    g.rect(x0, y0, sum(colw), rowh * len(rows), sw=2.4)
    return g


def tc5_65_67():  # 使用手冊目錄（Styx Photo Editing Software）
    g = SVG(430, 240)
    g.rect(14, 14, 402, 212, sw=2)
    g.text(215, 52, "Styx Photo Editing Software", size=19, weight="bold")
    g.text(215, 78, "User Manual", size=19, weight="bold")
    g.text(215, 112, "Table of Contents", size=16)
    g.line(140, 118, 290, 118, sw=1.4)
    items = [("Installation", 1), ("Tools", 3), ("Techniques", 6), ("Exporting", 9)]
    for i, (name, page) in enumerate(items):
        yy = 146 + i * 24
        g.text(46, yy, name, size=16, anchor="start")
        g.line(150, yy - 4, 356, yy - 4, sw=1.4, stroke="#666", dash="2,4")
        g.text(378, yy, str(page), size=16, anchor="end")
    return g


def tc5_68_70():  # 顧客滿意度調查表（○ 標記評分）
    g = SVG(480, 284)
    g.text(240, 32, "Customer Survey on Mobile Telephone Plan", size=16, weight="bold")
    g.text(240, 54, "(Average ratings)", size=14)
    cats = [("Quality of calls", 1), ("Monthly rates", 0),
            ("Choice of calling\nplans", 3), ("Customer service", 2)]
    heads = ["Excellent", "Good", "Poor", "Very\nPoor"]
    x0, y0 = 18, 68
    lw, cw, rowh, hh = 150, 73, 38, 46
    g.rect(x0, y0, lw, hh, fill="white", sw=1.6)             # 左上空白
    for j, hd in enumerate(heads):
        hx = x0 + lw + j * cw
        g.rect(hx, y0, cw, hh, fill=HDR, sw=1.6)
        hl = hd.split("\n")
        for k, ln in enumerate(hl):
            g.text(hx + cw / 2, y0 + hh / 2 + 5 - (len(hl) - 1) * 8 + k * 15, ln,
                   size=13, weight="bold")
    for i, (name, mark) in enumerate(cats):
        ry = y0 + hh + i * rowh
        g.rect(x0, ry, lw, rowh, fill="white", sw=1.6)
        ls = name.split("\n")
        for j, ln in enumerate(ls):
            g.text(x0 + 12, ry + rowh / 2 + 5 - (len(ls) - 1) * 8 + j * 15, ln,
                   size=14, anchor="start")
        for j in range(4):
            bx = x0 + lw + j * cw
            g.rect(bx, ry, cw, rowh, fill="white", sw=1.6)
            if j == mark:
                g.circle(bx + cw / 2, ry + rowh / 2, 9, fill="white", sw=2)
    g.rect(x0, y0, lw + cw * 4, hh + rowh * 4, sw=2.4)
    return g


def tc5_95_97():  # Astor Conference Center 平面圖（Space 1–4／Seminar Room 1／Stage）
    g = SVG(440, 300)
    g.rect(10, 10, 420, 280, sw=1.4)
    g.text(220, 42, "Astor Conference Center", size=18, weight="bold")
    bx, by, bw, bh = 30, 58, 380, 190                        # 建築外牆（粗）
    g.rect(bx, by, bw, bh, sw=5)
    mid = bx + 130                                           # 左側區塊右界
    top_h = 52
    g.line(bx, by + top_h, mid, by + top_h)                  # Space 1 下牆
    g.line(mid, by, mid, by + bh)                            # 左側直牆
    g.text(bx + 65, by + 32, "Space 1", size=15)
    # 觀眾席（同心半圓，圓心在左牆）＋舞台
    scy = by + top_h + (bh - top_h) / 2
    for rr in (24, 35, 46, 57, 68):
        g.path(f"M{bx} {scy - rr} A{rr} {rr} 0 0 1 {bx} {scy + rr}", fill="none", sw=1.6)
    g.poly([(bx + 50, by + bh - 12), (bx + 42, by + bh - 2), (bx + 58, by + bh - 2)],
           fill=STROKE, sw=0)
    g.text(bx + 50, by + bh + 26, "Stage", size=15)
    # 上排 Space 2 / Space 3
    g.rect(mid + 40, by, 120, top_h + 12, sw=2)
    g.text(mid + 100, by + 36, "Space 2", size=15)
    g.rect(mid + 160, by, bx + bw - (mid + 160), top_h, sw=2)
    g.text((mid + 160 + bx + bw) / 2, by + 32, "Space 3", size=15)
    # 右側 Space 4 / Seminar Room 1
    rx = bx + bw - 110
    g.rect(rx, by + 82, 110, 60, sw=2)
    g.text(rx + 55, by + 118, "Space 4", size=15)
    g.rect(rx, by + 142, 110, bh - 142, sw=2)
    g.text(rx + 55, by + 163, "Seminar", size=14)
    g.text(rx + 55, by + 181, "Room 1", size=14)
    g.text((mid + rx) / 2, by + 128, "Exhibition Area", size=15)
    return g


def tc5_98_100():  # 長條圖 Live Chat Software Ratings（4.4–5.0）
    g = SVG(460, 260)
    ox, oy, top, right = 78, 200, 46, 434
    g.text(240, 30, "Live Chat Software Ratings", size=16, weight="bold")
    ymin, ymax = 4.4, 5.0

    def py(v):
        return oy - (v - ymin) / (ymax - ymin) * (oy - top)
    for i in range(7):                                       # 4.4 … 5.0 格線
        v = round(ymin + i * 0.1, 1)
        yy = py(v)
        g.line(ox, yy, right, yy, sw=1.2, stroke="#999")
        g.text(ox - 10, yy + 5, "5" if v == 5.0 else f"{v}", size=13, anchor="end")
    g.line(ox, oy, ox, top, sw=1.6)
    bars = [("Symilla", 4.9), ("ProChat", 4.6), ("FastStream", 4.8), ("Powerbot", 4.7)]
    bw = 46
    span = (right - ox) / len(bars)
    for i, (lb, v) in enumerate(bars):
        cx = ox + span * (i + 0.5)
        g.rect(cx - bw / 2, py(v), bw, oy - py(v), fill="#d9d9d9", sw=1.4)
        g.text(cx, oy + 26, lb, size=14)
    return g


# ============================ 藍本 TestC6 ============================

def tc6_62_64():  # 辦公用品訂購單 Order Form
    rows = [
        [{"t": "Order Form", "span": 2, "bold": True, "fill": HDR}],
        [h("Item"), h("Quantity")],
        [{"t": "Folders", "align": "l"}, "10 packs"],
        [{"t": "Printer paper", "align": "l"}, "8 packs"],
        [{"t": "Black ink cartridges", "align": "l"}, "5"],
        [{"t": "Color ink cartridges", "align": "l"}, "4"],
    ]
    return draw_table([230, 160], rows, rowh=38)


def tc6_65_67():  # 街廓地圖：Cannondale Street／Raymond Lane 與四個公車站 ①–④
    g = SVG(470, 320)
    ROAD = "#e4e4e4"
    g.rect(14, 14, 442, 292, sw=2)                          # 地圖外框
    # 兩條橫向道路、兩條縱向道路（灰底表示街道）
    g.rect(16, 96, 438, 34, fill=ROAD, sw=0)
    g.rect(16, 216, 438, 34, fill=ROAD, sw=0)
    g.rect(176, 16, 34, 288, fill=ROAD, sw=0)               # Cannondale Street
    g.rect(300, 16, 30, 288, fill=ROAD, sw=0)               # Raymond Lane
    g.text(198, 205, "Cannondale Street", size=13,
           anchor="middle")                                  # 直書用旋轉
    g.parts[-1] = g.parts[-1].replace('<text ', '<text transform="rotate(-90 198 205)" ')
    g.text(318, 200, "Raymond Lane", size=13, anchor="middle")
    g.parts[-1] = g.parts[-1].replace('<text ', '<text transform="rotate(-90 318 200)" ')
    # 上排：圖書館、②、Elmwood Park（三棵樹）
    g.text(34, 52, "Eastwood", size=14, anchor="start")
    g.text(34, 72, "Public Library", size=14, anchor="start")
    g.circle(150, 66, 11, fill="white", sw=1.6)
    g.text(150, 71, "1", size=13)
    g.circle(232, 66, 11, fill="white", sw=1.6)
    g.text(232, 71, "2", size=13)
    g.text(280, 68, "Elmwood Park", size=14, anchor="start")
    for i in range(3):                                       # 樹
        tx = 398 + i * 22
        g.line(tx, 62, tx, 78, sw=2.4)
        g.circle(tx, 52, 9, fill="#4a4a4a", sw=1.2, stroke="#4a4a4a")
    # 中排：郵局、會議中心、③
    g.text(250, 152, "Post Office", size=14)
    g.rect(236, 162, 28, 24, fill="#5a5a5a", sw=1.2, stroke="#333")
    g.path("M236 162 q14 -10 28 0", fill="#5a5a5a", sw=1.2)
    g.rect(340, 146, 20, 40, fill="#5a5a5a", sw=1.2, stroke="#333")
    g.text(370, 152, "Conference", size=14, anchor="start")
    g.text(370, 172, "Center", size=14, anchor="start")
    g.circle(352, 200, 11, fill="white", sw=1.6)
    g.text(352, 205, "3", size=13)
    # 下排：加油站、Bayview Hotel、④
    g.text(250, 272, "Gas Station", size=14)
    g.rect(38, 258, 20, 38, fill="#5a5a5a", sw=1.2, stroke="#333")
    g.text(66, 268, "Bayview", size=14, anchor="start")
    g.text(66, 290, "Hotel", size=14, anchor="start")
    g.circle(150, 288, 11, fill="white", sw=1.6)
    g.text(150, 293, "4", size=13)
    return g


def tc6_68_70():  # 五月行事曆（週一～週五兩週）
    g = SVG(500, 250)
    x0, y0 = 16, 44
    colw, rowh, hdrh = 96, 84, 30
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    weeks = [
        [("15", []), ("16", ["Buyer", "Appreciation", "Day"]), ("17", []),
         ("18", ["New Model", "Arriving"]), ("19", [])],
        [("22", []), ("23", ["Customer", "Service", "Workshop"]), ("24", []),
         ("25", []), ("26", ["End of", "Season Sale"])],
    ]
    g.text(x0 + colw * 2.5, 30, "MAY", size=18, weight="bold")
    for i, d in enumerate(days):                             # 星期標頭
        g.rect(x0 + i * colw, y0, colw, hdrh, fill=HDR, sw=1.6)
        g.text(x0 + i * colw + colw / 2, y0 + 21, d, size=13, weight="bold")
    for r, week in enumerate(weeks):
        cy = y0 + hdrh + r * rowh
        for i, (num, lines) in enumerate(week):
            cx = x0 + i * colw
            g.rect(cx, cy, colw, rowh, sw=1.6)
            g.text(cx + 8, cy + 20, num, size=14, anchor="start")
            for li, ln in enumerate(lines):
                g.text(cx + colw / 2, cy + 42 + li * 17, ln, size=12)
    g.rect(x0, y0, colw * 5, hdrh + rowh * 2, sw=2.4)
    return g


def tc6_95_97():  # 四格圖：鞋子／項鍊／外套／襪子
    g = SVG(440, 340)
    cw, ch = 206, 156
    ox, oy, gap = 14, 14, 4
    cells = ["Item 1", "Item 2", "Item 3", "Item 4"]
    for i, lb in enumerate(cells):
        cx = ox + (i % 2) * (cw + gap)
        cy = oy + (i // 2) * (ch + gap)
        g.rect(cx, cy, cw, ch, sw=2)
        g.text(cx + cw / 2, cy + ch - 16, lb, size=16)
    # Item 1：一雙運動鞋（側面，鞋頭朝右）
    for sx, sy in [(50, 48), (84, 80)]:
        g.path(f"M{sx} {sy+40} c0,-20 10,-30 26,-34 l14,-4 c8,-2 14,2 18,10 "
               f"l12,20 c6,8 4,14 -4,14 l-58,0 c-6,0 -8,-2 -8,-6 z", fill="white", sw=2)
        g.line(sx + 1, sy + 33, sx + 68, sy + 33, sw=1.6)    # 鞋底
        for j in range(3):                                   # 鞋帶
            g.line(sx + 20 + j * 8, sy + 14 - j * 4, sx + 32 + j * 8, sy + 22 - j * 4, sw=1.4)
    # Item 2：項鍊（鍊圈＋墜子）
    g.path("M300 52 q54 8 46 46 q-8 34 -46 34 q-38 0 -46 -34 q-8 -38 46 -46 z", sw=2)
    g.circle(300, 48, 6, fill="white", sw=2)
    g.path("M292 128 q8 12 16 0 q-8 -6 -16 0 z", fill="#5a5a5a", sw=1.6)
    # Item 3：外套（衣身＋領子＋袖子）
    jx, jy = 104, 200
    g.path(f"M{jx-40} {jy} l24 -14 l16 8 l16 -8 l24 14 l-8 26 l-10 -6 l0 62 "
           f"l-44 0 l0 -62 l-10 6 z", fill="#c9c9c9", sw=2)
    g.line(jx, jy - 6, jx, jy + 76, sw=1.6)
    g.path(f"M{jx-16} {jy-14} l16 20 l16 -20", fill="none", sw=1.6)
    # Item 4：一雙條紋襪（襪筒＋朝右的腳掌）
    for sx, sy in [(272, 184), (334, 206)]:
        g.path(f"M{sx} {sy} h26 v40 h14 q12 0 12 12 q0 10 -12 10 h-40 z", fill="white", sw=2)
        for j in range(3):                                   # 襪筒條紋
            yy = sy + 8 + j * 10
            g.line(sx, yy, sx + 26, yy, sw=1.6, stroke="#777")
    return g


def tc6_98_100():  # 市民大會議程 Town Hall Meeting Agenda
    rows = [
        [{"t": "Town Hall Meeting Agenda", "span": 2, "bold": True, "fill": HDR}],
        [h("Date"), h("Topic")],
        ["May 2", "Zoning and Land Use"],
        ["May 7", "School District Calendar"],
        ["May 9", "Water Conservation"],
        ["May 13", "Applying for Building Permits"],
    ]
    return draw_table([120, 280], rows, rowh=38)


# ============================ 藍本 TestC7 ============================

def tc7_62_64():  # 14 樓平面圖（上排四室／走廊／下排 儲藏室・電梯・1403・1404）
    g = SVG(620, 330)
    ox, oy, W, H = 20, 20, 580, 290
    g.rect(ox, oy, W, H, sw=5)                               # 外牆
    colw = W / 4
    top_b = oy + 118                                         # 上排房間下牆
    bot_t = oy + 168                                         # 下排房間上牆
    elev_t = oy + 210                                        # 電梯間上牆（比其他室退後）

    def door_h(x, y, w=34, flip=False):                      # 橫牆上的門（開口＋弧）
        g.line(x, y, x + w, y, stroke="white", sw=4)
        if flip:                                             # 往上開
            g.path(f"M{x} {y} a{w} {w} 0 0 1 {w} {-w}", sw=1.8)
            g.line(x + w, y, x + w, y - w, sw=1.8)
        else:                                                # 往下開
            g.path(f"M{x + w} {y} a{w} {w} 0 0 1 {-w} {w}", sw=1.8)
            g.line(x, y, x, y + w, sw=1.8)

    # 上排四間：Photocopier Room / Room 1401 / Room 1402 / Break Room
    g.line(ox, top_b, ox + W, top_b)
    for i in range(1, 4):
        g.line(ox + i * colw, oy, ox + i * colw, top_b)
    tops = [["Photocopier", "Room"], ["Room 1401"], ["Room 1402"], ["Break Room"]]
    for i, lines in enumerate(tops):
        cx = ox + i * colw + colw / 2
        for li, ln in enumerate(lines):
            g.text(cx, oy + 48 + li * 22 - (len(lines) - 1) * 11, ln, size=16)
        door_h(ox + i * colw + colw - 52, top_b)             # 門靠各室右側
    # 下排：儲藏室（左，門開在左牆）／電梯間／Room 1403／Room 1404
    g.line(ox, bot_t, ox + colw, bot_t)
    g.line(ox + 2 * colw, bot_t, ox + W, bot_t)
    g.line(ox + colw, elev_t, ox + 2 * colw, elev_t)         # 電梯間上牆
    for i in (1, 2, 3):
        g.line(ox + i * colw, bot_t if i != 1 else elev_t, ox + i * colw, oy + H)
    g.line(ox, bot_t + 4, ox, bot_t + 38, stroke="white", sw=5)   # 儲藏室門開口
    g.path(f"M{ox} {bot_t + 38} a34 34 0 0 1 34 -34", sw=1.8)
    g.line(ox, bot_t + 38, ox, bot_t + 4, sw=1.8)
    g.text(ox + colw / 2, oy + 216, "Storage", size=16)
    g.text(ox + colw / 2, oy + 238, "Closet", size=16)
    g.text(ox + 1.5 * colw, oy + 252, "Elevators", size=16)
    g.text(ox + 2.5 * colw, oy + 236, "Room 1403", size=16)
    g.text(ox + 3.5 * colw, oy + 236, "Room 1404", size=16)
    door_h(ox + 2 * colw + 12, bot_t, flip=True)
    door_h(ox + 3 * colw + 12, bot_t, flip=True)
    return g


def tc7_65_67():  # 音樂廳座位圖：舞台＋Section 1–4（各 2 排 5 位）
    g = SVG(560, 440)
    g.rect(20, 20, 520, 44, sw=2)                            # 舞台
    g.text(280, 50, "Stage", size=20, weight="bold")
    sw_, sh = 244, 140                                       # 各區塊
    for i in range(4):
        bx = 20 + (i % 2) * (sw_ + 32)
        by = 100 + (i // 2) * (sh + 32)
        # 上邊留缺口放標題
        g.line(bx, by, bx + 52, by)
        g.line(bx + sw_ - 52, by, bx + sw_, by)
        g.line(bx, by, bx, by + sh)
        g.line(bx + sw_, by, bx + sw_, by + sh)
        g.line(bx, by + sh, bx + sw_, by + sh)
        g.text(bx + sw_ / 2, by + 7, f"Section {i + 1}", size=18)
        for r in range(2):                                   # 座位 2×5
            for c in range(5):
                g.rect(bx + 16 + c * 44, by + 28 + r * 54, 36, 40, sw=2)
    return g


def tc7_68_70():  # 課程表 Class / Day
    rows = [
        [h("Class"), h("Day")],
        ["Oil Painting", "Thursday"],
        ["Figure Drawing", "Friday"],
        ["Watercolors", "Saturday"],
        ["Sculpting", "Sunday"],
    ]
    return draw_table([210, 180], rows, rowh=40)


def tc7_95_97():  # 一週行程（週一～週四）
    g = SVG(520, 150)
    x0, y0, colw, hdrh, rowh = 16, 20, 122, 34, 74
    days = ["Monday", "Tuesday", "Wednesday", "Thursday"]
    cells = [["Meeting with", "Professor", "Parker"], ["Convention", "Lecture"],
             ["Awards", "Banquet"], ["Writing", "Workshop"]]
    for i, d in enumerate(days):
        g.rect(x0 + i * colw, y0, colw, hdrh, fill=HDR, sw=1.6)
        g.text(x0 + i * colw + colw / 2, y0 + 23, d, size=15)
        g.rect(x0 + i * colw, y0 + hdrh, colw, rowh, sw=1.6)
        lines = cells[i]
        for li, ln in enumerate(lines):
            g.text(x0 + i * colw + colw / 2,
                   y0 + hdrh + rowh / 2 + 6 + (li - (len(lines) - 1) / 2) * 20, ln, size=14)
    g.rect(x0, y0, colw * 4, hdrh + rowh, sw=2.4)
    return g


def tc7_98_100():  # 四種家具擺設 Layout 1–4
    FUR = "#c9c9c9"

    def chair(g, cx, cy, w=42, h=38):                        # 單人扶手椅（俯視）
        g.rect(cx - w / 2, cy - h / 2, w, h, fill=FUR, sw=2, rx=5)
        g.line(cx - w / 2 + 6, cy - h / 2, cx + w / 2 - 6, cy - h / 2, sw=2.4)

    def couch(g, cx, cy, w=132, h=40, seats=3, vert=False):  # 多人沙發
        if vert:
            w, h = h, w
        g.rect(cx - w / 2, cy - h / 2, w, h, fill=FUR, sw=2, rx=5)
        for s in range(1, seats):
            if vert:
                yy = cy - h / 2 + s * h / seats
                g.line(cx - w / 2, yy, cx + w / 2, yy, sw=1.6)
            else:
                xx = cx - w / 2 + s * w / seats
                g.line(xx, cy - h / 2, xx, cy + h / 2, sw=1.6)

    def table(g, cx, cy, w, h):                              # 茶几
        g.rect(cx - w / 2, cy - h / 2, w, h, fill="#efefef", sw=2)

    g = SVG(520, 460)
    cw, ch = 250, 220
    for i in range(4):
        ox = 10 + (i % 2) * cw
        oy = 10 + (i // 2) * ch
        g.rect(ox, oy, cw, ch, sw=2)
        g.text(ox + cw / 2, oy + 30, f"Layout {i + 1}", size=18)
        cx, cy = ox + cw / 2, oy + 124
        if i == 0:                                           # 桌子橫放＋左右單椅＋下方沙發
            table(g, cx, cy - 26, 110, 52)
            chair(g, cx - 92, cy - 26)
            chair(g, cx + 92, cy - 26)
            couch(g, cx, cy + 52)
        elif i == 1:                                         # 桌子直放＋兩側各兩張單椅
            table(g, cx, cy, 62, 118)
            for dy in (-32, 32):
                chair(g, cx - 82, cy + dy)
                chair(g, cx + 82, cy + dy)
        elif i == 2:                                         # 桌子直放＋兩側直式沙發＋下方單椅
            table(g, cx, cy - 12, 60, 116)
            couch(g, cx - 84, cy - 12, seats=3, vert=True)
            couch(g, cx + 84, cy - 12, seats=3, vert=True)
            chair(g, cx, cy + 72)
        else:                                                # 上方單椅＋桌子＋左右單椅＋下方沙發
            chair(g, cx, cy - 62)
            table(g, cx, cy + 2, 118, 50)
            chair(g, cx - 92, cy + 2)
            chair(g, cx + 92, cy + 2)
            couch(g, cx, cy + 76)
    return g


IMAGES = {
    "Test1": {"q62-64": t1_62_64, "q65-67": t1_65_67, "q68-70": t1_68_70,
              "q95-97": t1_95_97, "q98-100": t1_98_100},
    "Test2": {"q65-67": t2_65_67, "q68-70": t2_68_70, "q92-94": t2_92_94,
              "q95-97": t2_95_97, "q98-100": t2_98_100},
    "Test3": {"q62-64": t3_62_64, "q65-67": t3_65_67, "q68-70": t3_68_70,
              "q95-97": t3_95_97, "q98-100": t3_98_100},
    "Test4": {"q65-67": t4_65_67, "q68-70": t4_68_70, "q92-94": t4_92_94,
              "q95-97": t4_95_97, "q98-100": t4_98_100},
    "Test5": {"q62-64": t5_62_64, "q65-67": t5_65_67, "q68-70": t5_68_70,
              "q95-97": t5_95_97, "q98-100": t5_98_100},
    "TestC3": {"q62-64": tc3_62_64, "q65-67": tc3_65_67, "q68-70": tc3_68_70,
               "q95-97": tc3_95_97, "q98-100": tc3_98_100},
    "TestC4": {"q62-64": tc4_62_64, "q65-67": tc4_65_67, "q68-70": tc4_68_70,
               "q95-97": tc4_95_97, "q98-100": tc4_98_100},
    "TestC5": {"q62-64": tc5_62_64, "q65-67": tc5_65_67, "q68-70": tc5_68_70,
               "q95-97": tc5_95_97, "q98-100": tc5_98_100},
    "TestC6": {"q62-64": tc6_62_64, "q65-67": tc6_65_67, "q68-70": tc6_68_70,
               "q95-97": tc6_95_97, "q98-100": tc6_98_100},
    "TestC7": {"q62-64": tc7_62_64, "q65-67": tc7_65_67, "q68-70": tc7_68_70,
               "q95-97": tc7_95_97, "q98-100": tc7_98_100},
}


def main():
    out = sys.argv[1]
    for test, imgs in IMAGES.items():
        d = os.path.join(out, test)
        os.makedirs(d, exist_ok=True)
        for name, fn in imgs.items():
            svg = fn().dump()
            with open(os.path.join(d, name + ".svg"), "w") as f:
                f.write(svg)
    print("generated", sum(len(v) for v in IMAGES.values()), "svg ->", out)


if __name__ == "__main__":
    main()
