#!/usr/bin/env python3
"""
MFT 701 Week 4 — Core Systems Concepts I (Whiteboard / hand-drawn style).
Reuses build_video.py for title/objective/review slides; adds a whiteboard engine.
Usage: python3 build_week04.py
"""
import os, math, random, subprocess
from PIL import Image, ImageDraw, ImageFont
from mutagen.mp3 import MP3
import imageio_ffmpeg
import build_video as E

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "..", "Audio", "MFT-701-W04")
SLIDES = os.path.join(HERE, "slides-w04")
OUT = os.path.join(HERE, "MFT-701-Week-04-Lecture.mp4")
FONTS = os.path.join(E.ASSETS, "fonts")
os.makedirs(SLIDES, exist_ok=True)
W, H = E.W, E.H

BOARD = (251, 250, 246)
GRID = (226, 228, 224)
MARK = (18, 70, 82)       # teal marker
RED = (196, 86, 48)       # terracotta marker
GREEN = (72, 120, 96)
GREY = (120, 130, 134)
INK = (40, 50, 54)

def hf(size, bold=False):
    return ImageFont.truetype(os.path.join(FONTS, "Caveat-Bold.ttf" if bold else "Caveat-Regular.ttf"), int(size * 1.12))

def _glyphs(t):
    return t.replace("→", "->").replace("←", "<-").replace("↑", "").replace("·", "-")

# ---------- marker primitives (deterministic jitter) ----------
def _j(seed, amp=2.2):
    r = random.Random(seed)
    return lambda: r.uniform(-amp, amp)

def mline(d, pts, col=MARK, w=7, seed=1):
    j = _j(seed)
    out = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 18))
        for t in range(n):
            k = t / n
            out.append((x0 + (x1 - x0) * k + j(), y0 + (y1 - y0) * k + j()))
    out.append(pts[-1])
    d.line(out, fill=col, width=w, joint="curve")

def mellipse(d, cx, cy, rx, ry, col=MARK, w=7, seed=2, fill=None, a0=0, a1=360):
    j = _j(seed)
    pts = [(cx + rx * math.cos(math.radians(a)) + j(), cy + ry * math.sin(math.radians(a)) + j()) for a in range(a0, a1 + 1, 4)]
    if fill:
        d.polygon(pts, fill=fill)
    d.line(pts + ([pts[0]] if a1 - a0 >= 360 else []), fill=col, width=w, joint="curve")
    return pts

def mrect(d, box, col=MARK, w=7, seed=3, dashed=False):
    x0, y0, x1, y1 = box
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    if not dashed:
        mline(d, corners, col, w, seed)
        return
    for i in range(4):
        (ax, ay), (bx, by) = corners[i], corners[i + 1]
        L = math.hypot(bx - ax, by - ay); n = int(L / 34)
        for k in range(0, n, 2):
            t0, t1 = k / n, min((k + 1) / n, 1)
            mline(d, [(ax + (bx - ax) * t0, ay + (by - ay) * t0), (ax + (bx - ax) * t1, ay + (by - ay) * t1)], col, w, seed + k)

def marrow(d, p0, p1, col=MARK, w=7, seed=4, head=26):
    mline(d, [p0, p1], col, w, seed)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (-0.5, 0.5):
        d.line([p1, (p1[0] - head * math.cos(ang + s), p1[1] - head * math.sin(ang + s))], fill=col, width=w)

def marc_arrow(d, cx, cy, rx, ry, a0, a1, col=RED, w=7, seed=5):
    pts = mellipse(d, cx, cy, rx, ry, col, w, seed, a0=a0, a1=a1)
    (xa, ya), (xb, yb) = pts[-3], pts[-1]
    ang = math.atan2(yb - ya, xb - xa)
    for s in (-0.5, 0.5):
        d.line([(xb, yb), (xb - 28 * math.cos(ang + s), yb - 28 * math.sin(ang + s))], fill=col, width=w)

def mtext(d, xy, text, size=44, col=INK, bold=False, max_w=None, align="left", gap=1.12):
    text = _glyphs(text)
    f = hf(size, bold)
    if max_w:
        return E.draw_text(d, xy, text, f, col, max_w, gap, align)
    d.text(xy, text, font=f, fill=col)
    return xy[1] + int(size * gap)

def dot(d, x, y, r=16, col=MARK, seed=6, label=None, lsize=34):
    mellipse(d, x, y, r, r, col, 5, seed, fill=col)
    if label:
        f = hf(lsize, True)
        d.text((x - d.textlength(label, font=f) / 2, y + r + 6), label, font=f, fill=INK)

def stick(d, x, y, col=MARK, scale=1.0):
    s = scale
    mellipse(d, x, y, 22 * s, 22 * s, col, 5, 7)
    mline(d, [(x, y + 22 * s), (x, y + 95 * s)], col, 5, 8)
    mline(d, [(x - 36 * s, y + 55 * s), (x + 36 * s, y + 55 * s)], col, 5, 9)
    mline(d, [(x, y + 95 * s), (x - 28 * s, y + 150 * s)], col, 5, 10)
    mline(d, [(x, y + 95 * s), (x + 28 * s, y + 150 * s)], col, 5, 11)

def board(title=None, subtitle=None):
    img = Image.new("RGB", (W, H), BOARD)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 64):
        d.line([(x, 0), (x, H)], fill=GRID, width=1)
    for y in range(0, H, 64):
        d.line([(0, y), (W, y)], fill=GRID, width=1)
    d.rectangle([0, 0, W, 14], fill=(150, 160, 165)); d.rectangle([0, H - 14, W, H], fill=(150, 160, 165))
    d.rectangle([0, 0, 14, H], fill=(150, 160, 165)); d.rectangle([W - 14, 0, W, H], fill=(150, 160, 165))
    if title:
        mtext(d, (90, 40), title, 78, MARK, True)
        mline(d, [(92, 136), (92 + min(900, 22 * len(title)), 140)], RED, 6, 12)
    if subtitle:
        mtext(d, (100, 150), subtitle, 40, GREY)
    E.footer(d, False)
    return img, d

# ---------- whiteboard diagrams (step = how much is drawn) ----------
def wb_system(step):
    img, d = board("What is a system?", "von Bertalanffy: a set of elements standing in interaction")
    ax, ay, bx, by, cx, cy = 560, 560, 940, 560, 750, 300
    dot(d, ax, ay, label="person"); dot(d, bx, by, label="person")
    if step >= 2:
        mline(d, [(ax, ay), (bx, by)], RED, 8, 20)
        mtext(d, (640, 470), "a relationship", 42, RED, True)
    if step >= 3:
        dot(d, cx, cy, label=None, seed=21)
        mline(d, [(ax, ay), (cx, cy)], RED, 8, 22); mline(d, [(bx, by), (cx, cy)], RED, 8, 23)
        mtext(d, (1060, 380), "3 people → 3 lines", 46, INK, True)
    if step >= 4:
        # K5 and the counts
        px, py, R = 1500, 560, 150
        pts = [(px + R * math.cos(-math.pi / 2 + i * 2 * math.pi / 5), py + R * math.sin(-math.pi / 2 + i * 2 * math.pi / 5)) for i in range(5)]
        for i in range(5):
            for k in range(i + 1, 5):
                mline(d, [pts[i], pts[k]], RED, 4, 30 + i * 5 + k)
        for i, p in enumerate(pts):
            dot(d, p[0], p[1], 12, seed=40 + i)
        mtext(d, (1060, 450), "5 people → 10 lines", 46, INK, True)
        mtext(d, (1060, 520), "7 people → 21 lines", 46, INK, True)
        mtext(d, (300, 800), "Family therapy treats the lines.", 56, MARK, True)
    return img

def wb_wholeness(step):
    img, d = board("1. Wholeness  (nonsummativity)", "The whole is more than the sum of its parts — Aristotle")
    cs = [(520, 420), (700, 360), (760, 560), (560, 600)]
    if step >= 2:
        d.polygon(cs, fill=(240, 220, 200))
        mtext(d, (470, 470), "the pattern", 38, RED, True)
    for i, (x, y) in enumerate(cs):
        mellipse(d, x, y, 70, 70, MARK, 7, 50 + i, fill=BOARD)
        dot(d, x, y, 10, seed=60 + i)
    if step >= 2:
        marrow(d, (1000, 300), (790, 440), RED, 7, 70)
        mtext(d, (1010, 250), "emergent properties:", 44, RED, True)
        mtext(d, (1010, 310), "belong to the whole, not to any member", 36, INK)
    if step >= 3:
        mellipse(d, 1180, 560, 60, 60, GREEN, 6, 80); mtext(d, (1150, 540), "kind", 34, GREEN, True)
        mellipse(d, 1480, 560, 60, 60, GREEN, 6, 81); mtext(d, (1450, 540), "kind", 34, GREEN, True)
        zig = [(1240, 560)] + [(1240 + 20 * k, 560 + (18 if k % 2 else -18)) for k in range(1, 10)] + [(1420, 560)]
        mline(d, zig, RED, 7, 82)
        mtext(d, (1250, 600), "a cruel marriage?", 40, RED, True)
        mtext(d, (1140, 660), "Neither person is cruel. The cruelty is a property of the pattern.", 32, INK, max_w=560)
    if step >= 4:
        y = 720
        for i, t in enumerate(["1. You cannot understand a family by adding up individual interviews — see them together.",
                               "2. A change in any one member changes the whole.",
                               "3. The family has a character of its own: a mood, a rhythm, a climate."]):
            y = mtext(d, (200, y), t, 38, INK, max_w=1500) + 8
    return img

def wb_organization(step):
    img, d = board("Subsystems, boundaries, open & closed", "Wholes are organized — and every whole has an edge")
    mrect(d, (260, 230, 980, 760), GREY, 6, 90, dashed=True); mtext(d, (280, 236), "extended family · church · community", 34, GREY)
    mrect(d, (340, 300, 900, 720), MARK, 8, 91); mtext(d, (360, 306), "FAMILY", 40, MARK, True)
    mrect(d, (380, 380, 860, 500), MARK, 6, 92); mtext(d, (400, 392), "parental / spousal subsystem", 36, INK)
    mrect(d, (380, 560, 860, 680), MARK, 6, 93); mtext(d, (400, 572), "sibling subsystem", 36, INK)
    if step >= 2:
        mtext(d, (1080, 240), "the edge = a boundary", 46, RED, True)
        y = 320
        for lab, fn in [("clear / semi-permeable", lambda y: mline(d, [(1080, y), (1500, y)], MARK, 7, 94)),
                        ("diffuse / too open", lambda y: [mline(d, [(1080 + k * 50, y), (1105 + k * 50, y)], MARK, 7, 95 + k) for k in range(9)]),
                        ("rigid / too closed", lambda y: mline(d, [(1080, y), (1500, y)], MARK, 18, 96))]:
            fn(y); mtext(d, (1080, y + 14), lab, 36, INK); y += 110
    if step >= 3:
        mrect(d, (1080, 660, 1300, 820), MARK, 16, 97); mtext(d, (1090, 830), "too closed: rigid, isolated", 32, INK)
        for k in range(6):
            mline(d, [(1380 + k * 34, 660), (1395 + k * 34, 660)], MARK, 5, 98 + k); mline(d, [(1380 + k * 34, 820), (1395 + k * 34, 820)], MARK, 5, 105 + k)
        mtext(d, (1380, 830), "too open: no protected centre", 32, INK)
        mtext(d, (1080, 900), "Healthy families breathe: a clear edge and a working door.", 40, MARK, True, max_w=760)
    return img

def wb_circular(step):
    img, d = board("2. Circular causality", "each step is both effect and cause")
    # linear crossed out
    marrow(d, (200, 260), (520, 260), GREY, 7, 110); mtext(d, (200, 190), "A", 50, GREY, True); mtext(d, (520, 190), "B", 50, GREY, True)
    mline(d, [(330, 220), (400, 300)], RED, 8, 111); mline(d, [(400, 220), (330, 300)], RED, 8, 112)
    if step >= 2:
        cx, cy, rx, ry = 1060, 560, 380, 220
        for i in range(4):
            marc_arrow(d, cx, cy, rx, ry, -80 + i * 90, -10 + i * 90, RED, 7, 120 + i)
        labels = ["1. He comes home late, says little", "2. She feels shut out — asks questions", "3. He hears interrogation — goes quiet", "4. She hears rejection — raises her voice"]
        pos = [(cx - 220, cy - ry - 80), (cx + rx + 20, cy + 10), (cx - 200, cy + ry + 20), (cx - rx - 430, cy + 10)]
        for (x, y), t in zip(pos, labels):
            mtext(d, (x, y), t, 36, INK, True, max_w=420)
    if step >= 3:
        mtext(d, (1460, 430), "<- his story starts here", 34, GREEN, True)
        mtext(d, (1130, 850), "<- her story starts here", 34, GREEN, True)
        mtext(d, (200, 330), "punctuation:", 44, GREEN, True); mtext(d, (200, 385), "where each person begins the story", 34, INK, max_w=380)
    if step >= 4:
        dot(d, 330, 820, 18, RED, 130, "a third person", 32)
        for k in range(8):
            mline(d, [(370 + k * 40, 800 - k * 14), (390 + k * 40, 793 - k * 14)], RED, 5, 131 + k)
        mtext(d, (200, 700), "anxiety pulls in a third: a triangle", 34, RED, True, max_w=400)
    if step >= 5:
        mtext(d, (200, 915), "Circular question: “When he goes quiet, what do you do? And then what does he do next?”", 38, MARK, True, max_w=1540)
    return img

def wb_homeostasis(step):
    img, d = board("3. Homeostasis", "Cannon 1932 (the body) → Jackson 1957 (the family)")
    cx, cy = 560, 540
    mellipse(d, cx, cy, 150, 150, MARK, 8, 140)
    for a in range(-150, 151, 30):
        mline(d, [(cx + 125 * math.cos(math.radians(a - 90)), cy + 125 * math.sin(math.radians(a - 90))), (cx + 145 * math.cos(math.radians(a - 90)), cy + 145 * math.sin(math.radians(a - 90)))], MARK, 4, 141 + a)
    mline(d, [(cx, cy), (cx + 100 * math.cos(math.radians(-60)), cy + 100 * math.sin(math.radians(-60)))], RED, 8, 150)
    lab = ["set point 22°", "sensor", "heater"] if step < 2 else ["set point = family RULES", "sensor = ANXIETY", "heater = CORRECTIVE behaviour"]
    mtext(d, (cx - 110, cy + 170), lab[0], 40, RED, True)
    # thermometer
    mrect(d, (900, 380, 950, 700), MARK, 6, 160); mellipse(d, 925, 720, 40, 40, MARK, 6, 161, fill=(230, 120, 90))
    d.rectangle([912, 520, 938, 700], fill=(230, 120, 90)); mtext(d, (860, 300), lab[1], 40, RED, True)
    # heater
    mrect(d, (1100, 560, 1360, 700), MARK, 6, 162)
    for k in range(5):
        mline(d, [(1130 + k * 50, 580), (1130 + k * 50, 680)], MARK, 4, 163 + k)
    mtext(d, (1080, 720), lab[2], 40, RED, True)
    # cycle arrows
    marrow(d, (960, 460), (1120, 540), GREY, 6, 170); marrow(d, (1230, 540), (1180, 420), GREY, 6, 171)
    mtext(d, (1200, 400), "too cold -> heater on", 32, GREY); mtext(d, (1200, 445), "too warm -> heater off", 32, GREY)
    marrow(d, (1100, 520), (800, 500), GREY, 6, 172)
    if step >= 2:
        mtext(d, (1480, 260), "rules about how close, how loud, how honest, how independent people may be", 34, INK, max_w=380)
    if step >= 3:
        stick(d, 1540, 640, GREEN, 0.8); mtext(d, (1490, 780), "sober", 36, GREEN, True)
        stick(d, 1740, 640, RED, 0.8); mtext(d, (1680, 780), "depressed", 36, RED, True)
        marrow(d, (1600, 700), (1700, 700), RED, 6, 180)
        mtext(d, (200, 860), "The family organized itself around the drinking. When it stopped, the system worked to restore a familiar balance.", 36, MARK, True, max_w=1300)
        mtext(d, (200, 950), "Homeostasis is not malice — it is stability doing its job in the wrong direction.", 34, INK, max_w=1300)
    return img

def wb_feedback(step):
    img, d = board("4. Feedback", "output that returns as input")
    # negative loop
    mellipse(d, 420, 470, 170, 120, MARK, 8, 190, a0=20, a1=340); marc_arrow(d, 420, 470, 170, 120, 300, 350, MARK, 8, 191)
    mtext(d, (395, 430), "–", 90, MARK, True); mtext(d, (220, 620), "NEGATIVE = deviation-reducing", 40, MARK, True)
    if step >= 2:
        pts = [(220 + k * 12, 810 + 42 * math.exp(-k / 14) * math.cos(k / 3)) for k in range(45)]
        mline(d, pts, MARK, 6, 192); mtext(d, (220, 870), "settles back to the set point — stability", 34, INK, max_w=440)
        mtext(d, (220, 680), "teen home late → parents respond → home on time", 32, GREY, max_w=460)
    # positive loop
    mellipse(d, 1100, 470, 170, 120, RED, 8, 193, a0=20, a1=340); marc_arrow(d, 1100, 470, 170, 120, 300, 350, RED, 8, 194)
    mtext(d, (1078, 430), "+", 90, RED, True); mtext(d, (900, 620), "POSITIVE = deviation-amplifying", 40, RED, True)
    if step >= 3:
        pts = [(1200 + 3.2 * k * math.cos(k / 4), 860 + 2 * k * math.sin(k / 4)) for k in range(45)]
        mline(d, pts, RED, 6, 195); mtext(d, (900, 760), "runaway — crisis… or growth", 34, INK)
        mtext(d, (900, 680), "criticism → sharper reply → shout → slammed door", 32, GREY, max_w=460)
    if step >= 4:
        stick(d, 1560, 300, GREEN, 1.0); mline(d, [(1596, 355), (1660, 320)], GREEN, 6, 196)
        mtext(d, (1420, 480), "the therapist uses both:", 40, GREEN, True)
        mtext(d, (1420, 540), "escalation in session → become negative feedback: slow the pace, lower your voice", 32, INK, max_w=440)
        mtext(d, (1420, 690), "a small improvement → become positive feedback: notice it, enlarge it, ask what made it possible", 32, INK, max_w=440)
    return img

def wb_supporting(step):
    img, d = board("Supporting concepts", "equifinality · rules · redundancy")
    for i, (sx, sy) in enumerate([(200, 300), (200, 420), (200, 540)]):
        dot(d, sx, sy, 12, seed=200 + i); marrow(d, (sx + 20, sy), (520, 420), MARK, 6, 210 + i)
    dot(d, 540, 420, 16, RED, 220); mtext(d, (240, 600), "EQUIFINALITY: many starts → same end", 36, MARK, True, max_w=400)
    dot(d, 700, 420, 16, RED, 221)
    for i, (ex, ey) in enumerate([(1000, 300), (1000, 420), (1000, 540)]):
        marrow(d, (720, 420), (ex, ey), MARK, 6, 230 + i); dot(d, ex + 20, ey, 12, seed=240 + i)
    mtext(d, (700, 600), "EQUIPOTENTIALITY: same start → many ends", 36, MARK, True, max_w=400)
    mtext(d, (200, 700), "→ not “where did this begin?” but “what keeps it going now?”", 40, RED, True, max_w=900)
    if step >= 2:
        mtext(d, (1180, 230), "FAMILY RULES (Jackson)", 44, MARK, True)
        mtext(d, (1180, 290), "overt — stated:", 36, GREEN, True); mtext(d, (1200, 335), "“no phones at dinner”", 34, INK)
        mtext(d, (1180, 395), "covert — lived:", 36, RED, True)
        y = 440
        for t in ["“we don't mention Father's drinking”", "“Mother's feelings come first”", "“boys don't cry”"]:
            y = mtext(d, (1200, y), t, 34, INK)
        mtext(d, (1180, 600), "covert rules = the thermostat's set point", 34, GREY, max_w=600)
    if step >= 3:
        mtext(d, (1180, 700), "REDUNDANCY", 44, MARK, True)
        r = random.Random(7)
        for k in range(40):
            x, y = 1190 + r.randint(0, 640), 770 + r.randint(0, 120)
            col = RED if k % 8 == 0 else GRID
            mellipse(d, x, y, 9, 9, col, 3, 300 + k, fill=col)
        mtext(d, (1180, 910), "families use a small repeating set of behaviours — 20 minutes shows the pattern", 32, INK, max_w=680)
    return img

def wb_fieldguide(step):
    img, d = board("Field guide: what it looks like in the room")
    rows = [("Wholeness", "a family mood you can feel before anyone speaks — heavy, brittle, jokey, frozen"),
            ("Circular causality", "“he always…”  “she never…”  — one person's punctuation of a loop"),
            ("Homeostasis", "improvement… then a new problem somewhere else. The thermostat switched on. Warn families in advance."),
            ("Feedback", "voices rising turn by turn — or a small change the family has noticed and begun to repeat")]
    mline(d, [(760, 200), (760, 700)], GREY, 4, 400)
    y = 210
    for i, (a, b) in enumerate(rows):
        mtext(d, (120, y), a, 46, MARK, True)
        yy = mtext(d, (800, y + 4), b, 36, INK, max_w=980)
        y = max(yy, y + 60) + 36
        mline(d, [(120, y - 14), (1800, y - 10)], GRID, 3, 401 + i)
    if step >= 2:
        mtext(d, (120, 760), "The Adebayos:", 46, RED, True)
        pts = {"F": (420, 870), "M": (560, 820), "T": (700, 870), "S": (560, 940)}
        for k, (x, y) in pts.items():
            dot(d, x, y, 14, seed=410 + ord(k), label=k, lsize=30)
        for a, b in [("F", "M"), ("M", "T"), ("T", "F"), ("M", "S")]:
            mline(d, [pts[a], pts[b]], GRID, 4, 420 + ord(a))
        marc_arrow(d, 560, 870, 150, 60, 200, 340, RED, 6, 430); marc_arrow(d, 560, 870, 150, 60, 20, 160, RED, 6, 431)
        mtext(d, (800, 790), "shared heaviness · withdraw → over-function → act out · reorganized around Father's silence", 34, INK, max_w=980)
        mtext(d, (800, 880), "amplify the first moment Father speaks of his loss → a new pattern can grow", 34, GREEN, True, max_w=980)
    return img

def wb_limits(step):
    img, d = board("Limits — lenses, not laws")
    mellipse(d, 420, 460, 120, 120, MARK, 8, 500)
    mline(d, [(420, 460), (480, 390)], RED, 8, 501)
    mtext(d, (560, 330), "?", 220, RED, True)
    mtext(d, (760, 260), "Families are not thermostats.", 48, MARK, True)
    y = mtext(d, (760, 330), "People have intentions, meanings and moral agency.", 36, INK, max_w=1000)
    y = mtext(d, (760, y + 20), "Dell (1982): “homeostasis” became a lazy explanation for non-change.", 36, INK, max_w=1000)
    y = mtext(d, (760, y + 20), "Feminist critique: talk of balance can hide power — and blame a victim for “participating”.", 36, INK, max_w=1000)
    mtext(d, (760, y + 30), "Where there is violence or abuse: circularity is set aside, responsibility is named.", 38, RED, True, max_w=1000)
    if step >= 2:
        cs = [(300, 800), (400, 760), (430, 880), (320, 900)]
        d.polygon(cs, fill=(240, 220, 200))
        for i, (x, y) in enumerate(cs):
            mellipse(d, x, y, 40, 40, MARK, 6, 510 + i, fill=BOARD)
        mtext(d, (520, 740), "“If one member suffers, all suffer together.”  — 1 Corinthians 12", 42, MARK, True, max_w=1300)
        mtext(d, (520, 810), "Covenant = a set point that steadies a family when anxiety rises.", 36, INK, max_w=1300)
        mtext(d, (520, 870), "“Be transformed” = permission for the set point itself to change.", 36, INK, max_w=1300)
    return img

def wb_overview():
    img, d = board("The whole board")
    tiles = [("1. Wholeness", "the pattern between the dots"), ("2. Circular causality", "effect and cause; punctuation"),
             ("3. Homeostasis", "rules = set point · anxiety = sensor"), ("4. Feedback", "– steadies · + amplifies")]
    for i, (t, s) in enumerate(tiles):
        x0 = 120 + (i % 2) * 880; y0 = 200 + (i // 2) * 330
        mrect(d, (x0, y0, x0 + 800, y0 + 290), GREY, 4, 600 + i, dashed=True)
        mtext(d, (x0 + 30, y0 + 20), t, 52, MARK, True); mtext(d, (x0 + 30, y0 + 90), s, 36, INK)
        if i == 0:
            cs = [(x0 + 560, y0 + 170), (x0 + 640, y0 + 140), (x0 + 660, y0 + 230), (x0 + 580, y0 + 250)]
            d.polygon(cs, fill=(240, 220, 200))
            for k, (x, y) in enumerate(cs): mellipse(d, x, y, 32, 32, MARK, 5, 620 + k, fill=BOARD)
        if i == 1:
            for k in range(4): marc_arrow(d, x0 + 620, y0 + 190, 120, 70, -80 + k * 90, -10 + k * 90, RED, 5, 630 + k)
        if i == 2:
            mellipse(d, x0 + 620, y0 + 190, 70, 70, MARK, 6, 640); mline(d, [(x0 + 620, y0 + 190), (x0 + 660, y0 + 150)], RED, 6, 641)
        if i == 3:
            mline(d, [(x0 + 480 + k * 6, y0 + 200 + 40 * math.exp(-k / 10) * math.cos(k / 2.5)) for k in range(30)], MARK, 5, 650)
            mline(d, [(x0 + 700 + 3 * k * math.cos(k / 4), y0 + 200 + 2 * k * math.sin(k / 4)) for k in range(40)], RED, 5, 651)
    mtext(d, (120, 880), "+ equifinality · family rules · redundancy", 44, GREY, True)
    return img

# ---------- deck ----------
def deck():
    D = []
    D.append(("01-welcome-system.mp3", [
        (1.4, E.s_title("Core Systems Concepts I", "Week 4 — Wholeness, Circular Causality, Homeostasis and Feedback\nA whiteboard lecture", "MFT 701 · Master of Marriage and Family Therapy")),
        (2.0, E.s_bullets("Learning Objectives", ["Define each of the four core concepts precisely.", "Draw a simple diagram of each.", "Recognize each one when it appears in a therapy session.", "Explain their limits."], nums=True, intro="By the end of this lecture you will be able to…")),
        (1.6, wb_system(1)), (1.6, wb_system(2)), (1.8, wb_system(3)), (2.4, wb_system(4)),
    ]))
    D.append(("02-wholeness.mp3", [(2.0, wb_wholeness(1)), (2.2, wb_wholeness(2)), (2.6, wb_wholeness(3)), (3.6, wb_wholeness(4))]))
    D.append(("03-organization.mp3", [(2.6, wb_organization(1)), (3.0, wb_organization(2)), (3.4, wb_organization(3))]))
    D.append(("04-circular.mp3", [(1.4, wb_circular(1)), (3.0, wb_circular(2)), (2.0, wb_circular(3)), (2.0, wb_circular(4)), (1.6, wb_circular(5))]))
    D.append(("05-homeostasis.mp3", [(3.2, wb_homeostasis(1)), (2.6, wb_homeostasis(2)), (3.4, wb_homeostasis(3))]))
    D.append(("06-feedback.mp3", [(1.6, wb_feedback(1)), (2.2, wb_feedback(2)), (2.6, wb_feedback(3)), (3.0, wb_feedback(4))]))
    D.append(("07-supporting.mp3", [(3.2, wb_supporting(1)), (3.0, wb_supporting(2)), (1.6, wb_supporting(3))]))
    D.append(("08-field-guide.mp3", [(4.0, wb_fieldguide(1)), (2.6, wb_fieldguide(2))]))
    D.append(("09-limits-reflection.mp3", [(3.4, wb_limits(1)), (3.6, wb_limits(2))]))
    D.append(("10-summary-close.mp3", [
        (3.0, wb_overview()),
        (2.6, E.s_bullets("Review Questions", [
            "Draw a four-step circular loop from a relationship you know, and mark where each person punctuates it.",
            "Explain the difference between negative and positive feedback, with one example of a therapist deliberately using each.",
            "What is one limitation of the homeostasis concept, and how would you guard against it in practice?",
        ], nums=True, intro="Pause the video and write your answers.")),
        (2.6, E.s_cards("Looking Ahead", [
            ("Next Week", "Core Systems Concepts II — boundaries, subsystems, hierarchy and triangles. Minuchin's family maps and Bowen's triangles."),
            ("Assignment — a drawing", "Map your family of origin (or a family you know well) as a system: members as dots, at least one circular loop, one covert rule, and the family boundary marked too open / too closed / semi-permeable. One page; pencil is fine."),
        ], dark=True)),
        (0.8, E.s_title("Thank you.", "End of Week 4\nPut the marker down — see you next week.", "MFT 701 · Week 4")),
    ]))
    return D

def main():
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    vid, aud, idx, total = [], [], 0, 0.0
    for audio, slides in deck():
        apath = os.path.abspath(os.path.join(AUDIO_DIR, audio))
        dur = MP3(apath).info.length; total += dur
        aud.append(f"file '{apath}'")
        wsum = sum(w for w, _ in slides)
        for w, im in slides:
            idx += 1; p = os.path.join(SLIDES, f"slide-{idx:03d}.png"); im.save(p); vid.append((p, dur * w / wsum))
    print(f"{idx} slides, {total/60:.1f} min")
    with open(os.path.join(SLIDES, "video.txt"), "w") as f:
        for p, d in vid: f.write(f"file '{p}'\nduration {d:.3f}\n")
        f.write(f"file '{vid[-1][0]}'\nduration 0.04\n")
    with open(os.path.join(SLIDES, "audio.txt"), "w") as f: f.write("\n".join(aud) + "\n")
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(SLIDES, "video.txt"),
           "-f", "concat", "-safe", "0", "-i", os.path.join(SLIDES, "audio.txt"),
           "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-tune", "stillimage", "-r", "25", "-pix_fmt", "yuv420p",
           "-vf", "scale=1920:1080,format=yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", OUT]
    subprocess.run(cmd, check=True); print("Wrote", OUT)

if __name__ == "__main__":
    main()
