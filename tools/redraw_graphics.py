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
