#!/usr/bin/env python3
"""
MFT 701 Week 5 — Core Systems Concepts II (Build-Up Diagram / Layered Reveal).
One diagram — the Adebayo structural map — gains five layers: members, subsystems,
boundaries, hierarchy, triangles. Reuses build_video.py for standard slides.
Usage: python3 build_week05.py
"""
import os, math, subprocess
from PIL import Image, ImageDraw
from mutagen.mp3 import MP3
import imageio_ffmpeg
import build_video as E
from build_video import (W, H, TEAL, TEAL_DARK, TEAL_LIGHT, SAND, SAND_DARK, TERRA, CREAM, INK, MUTED, WHITE,
                         font, draw_text, text_height, footer, heading, base)

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "..", "Audio", "MFT-701-W05")
SLIDES = os.path.join(HERE, "slides-w05")
OUT = os.path.join(HERE, "MFT-701-Week-05-Lecture.mp4")
os.makedirs(SLIDES, exist_ok=True)

LAYERS = ["Members", "Subsystems", "Boundaries", "Hierarchy", "Triangles"]
GREY = (190, 196, 198)
SOFT = (236, 230, 220)

# ---------------- notation primitives ----------------
def dashed(d, p0, p1, col, w=5, dash=22, gap=16):
    x0, y0, x1, y1 = *p0, *p1
    L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / (dash + gap)))
    for k in range(n + 1):
        t0 = k * (dash + gap) / L; t1 = min((k * (dash + gap) + dash) / L, 1)
        if t0 >= 1: break
        d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)], fill=col, width=w)

def dotted(d, p0, p1, col, w=7, gap=20):
    x0, y0, x1, y1 = *p0, *p1
    L = math.hypot(x1 - x0, y1 - y0); n = int(L / gap)
    for k in range(n + 1):
        t = k * gap / L
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=col)

def zigzag(d, p0, p1, col, w=5, amp=14, n=10):
    x0, y0, x1, y1 = *p0, *p1
    dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    pts = [p0]
    for k in range(1, n):
        t = k / n; s = amp if k % 2 else -amp
        pts.append((x0 + dx * t + nx * s, y0 + dy * t + ny * s))
    pts.append(p1); d.line(pts, fill=col, width=w, joint="curve")

def triple(d, p0, p1, col, w=5, sep=12):
    x0, y0, x1, y1 = *p0, *p1
    dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    for s in (-sep, 0, sep):
        d.line([(x0 + nx * s, y0 + ny * s), (x1 + nx * s, y1 + ny * s)], fill=col, width=w)

def arrow(d, p0, p1, col, w=5, head=20):
    d.line([p0, p1], fill=col, width=w)
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    d.polygon([p1, (p1[0] - head * math.cos(a - 0.45), p1[1] - head * math.sin(a - 0.45)),
               (p1[0] - head * math.cos(a + 0.45), p1[1] - head * math.sin(a + 0.45))], fill=col)

def person(d, x, y, letter, name=None, r=46, col=TEAL, fill=WHITE, ghost=False, sub=None):
    if ghost:
        dashed_circle(d, x, y, r, GREY); return
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=col, width=5)
    f = font(int(r * 0.9), bold=True)
    d.text((x - d.textlength(letter, font=f) / 2, y - r * 0.55), letter, font=f, fill=col)
    if name:
        f2 = font(28); d.text((x - d.textlength(name, font=f2) / 2, y + r + 10), name, font=f2, fill=INK)
    if sub:
        f3 = font(24); d.text((x - d.textlength(sub, font=f3) / 2, y + r + 46), sub, font=f3, fill=MUTED)

def dashed_circle(d, x, y, r, col, w=4):
    for a in range(0, 360, 24):
        d.arc([x - r, y - r, x + r, y + r], a, a + 12, fill=col, width=w)

def box(d, b, label=None, col=TEAL_LIGHT, fill=None, w=4, style="dashed", lcol=None):
    x0, y0, x1, y1 = b
    if fill: d.rounded_rectangle(b, radius=30, fill=fill)
    if style == "solid":
        d.rounded_rectangle(b, radius=30, outline=col, width=w)
    else:
        for p, q in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
            dashed(d, p, q, col, w, 18, 12)
    if label:
        f = font(26, bold=True); d.text((x0 + 18, y0 + 10), label, font=f, fill=lcol or col)

# ---------------- the Adebayo map ----------------
def draw_map(d, level, ox=0, oy=0, full=False, focus=True):
    """Draw the map at a given layer level. Flat layout for levels 1-3, hierarchical for 4-5."""
    hi = TERRA if focus else TEAL
    R = 56
    if level <= 3:
        y = 560 + oy
        P = {"F": (240 + ox, y), "M": (540 + ox, y), "T": (840 + ox, y), "B": (1140 + ox, y)}
        if level >= 2:
            box(d, (130 + ox, y - 130, 650 + ox, y + 150), "spousal / parental subsystem", hi if level == 2 else TEAL_LIGHT, fill=SOFT if level == 2 else None)
            box(d, (730 + ox, y - 130, 1250 + ox, y + 150), "sibling subsystem", hi if level == 2 else TEAL_LIGHT, fill=SOFT if level == 2 else None)
        if level >= 3:
            f = font(28, bold=True)
            d.line([(390 + ox, y - 170), (390 + ox, y + 180)], fill=hi, width=16); d.text((355 + ox, y + 190), "rigid", font=f, fill=hi)
            dotted(d, (690 + ox, y - 170), (690 + ox, y + 180), hi, 10, 22); d.text((640 + ox, y + 190), "diffuse", font=f, fill=hi)
            dashed(d, (990 + ox, y - 170), (990 + ox, y + 180), hi, 6, 22, 16); d.text((955 + ox, y + 190), "clear", font=f, fill=hi)
        person(d, *P["F"], "F", "Mr. Adebayo", r=R, sub="father · out of work")
        person(d, *P["M"], "M", "Mrs. Adebayo", r=R, sub="mother · two jobs")
        person(d, *P["T"], "T", "Tunde, 14", r=R, sub="school refusal")
        person(d, *P["B"], "B", "Bisi, 10", r=R, sub="quiet, obedient")
        return P
    # hierarchical layout
    gy = 630 + oy
    P = {"F": (260 + ox, 430 + oy), "M": (640 + ox, 390 + oy), "T": (920 + ox, 390 + oy), "B": (640 + ox, 830 + oy), "Tg": (1120 + ox, 830 + oy)}
    c4 = TERRA if level == 4 else TEAL
    dashed(d, (120 + ox, gy), (1230 + ox, gy), MUTED, 4, 26, 16)
    d.text((124 + ox, gy - 36), "executive / parental level", font=font(22), fill=MUTED)
    d.text((124 + ox, gy + 10), "child level", font=font(22), fill=MUTED)
    box(d, (150 + ox, 270 + oy, 1060 + ox, 600 + oy), "executive level — who is actually here?", TEAL_LIGHT)
    box(d, (520 + ox, 720 + oy, 1230 + ox, 930 + oy), "sibling subsystem — Bisi alone", TEAL_LIGHT)
    # ghost of T below the line + arrow up
    person(d, *P["Tg"], "T", ghost=True, r=R)
    arrow(d, (P["Tg"][0] - 30, P["Tg"][1] - 62), (P["T"][0] + 74, P["T"][1] + 28), c4, 5)
    d.text((P["Tg"][0] - 290, P["Tg"][1] - 200), "Tunde moves up", font=font(24, bold=True), fill=c4)
    # rigid wall around F
    fx, fy = P["F"]
    d.arc([fx - 100, fy - 100, fx + 100, fy + 100], -52, 52, fill=TEAL, width=14)
    d.text((fx - 78, fy + 102), "rigid boundary", font=font(22, bold=True), fill=TEAL)
    zigzag(d, (fx + 110, fy - 8), (P["M"][0] - 60, P["M"][1] + 10), c4, 5)
    d.text((fx + 150, fy - 70), "conflict", font=font(22, bold=True), fill=c4)
    triple(d, (P["M"][0] + 60, P["M"][1]), (P["T"][0] - 60, P["T"][1]), c4, 4, 11)
    d.text((P["M"][0] + 70, P["M"][1] - 62), "over-involved", font=font(22, bold=True), fill=c4)
    bx0, bx1, by = P["M"][0] - 80, P["T"][0] + 80, P["M"][1] + 108
    d.line([(bx0, by), (bx1, by)], fill=c4, width=5); d.line([(bx0, by - 18), (bx0, by)], fill=c4, width=5); d.line([(bx1, by - 18), (bx1, by)], fill=c4, width=5)
    d.text((bx0, by + 8), "coalition  M + T  against F", font=font(22, bold=True), fill=c4)
    person(d, *P["F"], "F", "Mr. Adebayo", r=R)
    person(d, *P["M"], "M", "Mrs. Adebayo", r=R)
    person(d, *P["T"], "T", "Tunde, 14", r=R, fill=(252, 236, 226) if level == 4 else WHITE, col=c4 if level == 4 else TEAL)
    person(d, *P["B"], "B", "Bisi, 10", r=R)
    if level >= 5:
        for k in ("F", "M", "T"):
            x, y = P[k]; d.ellipse([x - 72, y - 72, x + 72, y + 72], outline=TERRA, width=5)
        d.text((fx - 50, fy + 134), "outsider", font=font(24, bold=True), fill=TERRA)
        d.text((P["M"][0] + 90, P["M"][1] - 152), "insiders", font=font(24, bold=True), fill=TERRA)
    return P

def layer_panel(d, level, adds, lacks, x0=1300):
    # chips
    d.text((x0, 120), "FIVE LAYERS", font=font(24, bold=True), fill=MUTED)
    for i, name in enumerate(LAYERS):
        y = 170 + i * 66
        done = i + 1 < level; active = i + 1 == level
        col = TERRA if active else (TEAL if done else GREY)
        d.rounded_rectangle([x0, y, x0 + 520, y + 52], radius=26, fill=col if (active or done) else WHITE, outline=col, width=3)
        f = font(28, bold=True)
        d.text((x0 + 24, y + 9), f"{i + 1}", font=f, fill=WHITE if (active or done) else GREY)
        d.text((x0 + 64, y + 9), name, font=f, fill=WHITE if (active or done) else MUTED)
    y = 530
    if adds:
        d.text((x0, y), "WHAT THIS LAYER ADDS", font=font(22, bold=True), fill=TERRA)
        y = draw_text(d, (x0, y + 36), adds, font(32), INK, 520, 1.3) + 36
    if lacks:
        d.text((x0, y), "WHY IT IS NOT ENOUGH", font=font(22, bold=True), fill=MUTED)
        draw_text(d, (x0, y + 36), lacks, font(32), INK, 520, 1.3)

def triangle_inset(d, x0=1300, y0=500, state="adebayo"):
    d.text((x0, y0), "LIFTED OUT OF THE MAP", font=font(22, bold=True), fill=TERRA)
    M, T, F = (x0 + 110, y0 + 110), (x0 + 410, y0 + 110), (x0 + 260, y0 + 330)
    d.polygon([M, T, F], outline=TERRA, fill=(252, 236, 226), width=5)
    d.line([M, T], fill=TERRA, width=12)
    d.line([M, F], fill=TERRA, width=4); d.line([T, F], fill=TERRA, width=4)
    for (x, y), L in ((M, "M"), (T, "T"), (F, "F")):
        person(d, x, y, L, r=36, col=TERRA if L != "F" else TEAL)
    d.text((x0 + 200, y0 + 40), "insiders", font=font(26, bold=True), fill=TERRA)
    d.text((x0 + 320, y0 + 312), "outsider", font=font(26, bold=True), fill=TEAL)
    # anxiety arrows
    arrow(d, (x0 + 180, y0 + 250), (x0 + 110, y0 + 170), TERRA, 4)
    arrow(d, (x0 + 330, y0 + 170), (x0 + 400, y0 + 250), TERRA, 4)
    draw_text(d, (x0, y0 + 385), "Marital anxiety relocates to the M–T side and surfaces as Tunde's symptom.", font(26), INK, 520, 1.25)

# ---------------- slides ----------------
def s_layer(level, adds, lacks, title):
    img, d = base(False)
    heading(d, title, size=50)
    draw_map(d, level)
    if level == 5:
        d.text((1300, 120), "FIVE LAYERS", font=font(24, bold=True), fill=MUTED)
        for i, name in enumerate(LAYERS):
            y = 170 + i * 66; active = i == 4; col = TERRA if active else TEAL
            d.rounded_rectangle([1300, y, 1820, y + 52], radius=26, fill=col)
            d.text((1324, y + 9), f"{i + 1}", font=font(28, bold=True), fill=WHITE); d.text((1364, y + 9), name, font=font(28, bold=True), fill=WHITE)
        triangle_inset(d)
    else:
        layer_panel(d, level, adds, lacks)
    footer(d, False, f"Layer {level} of 5")
    return img

def s_plan():
    img, d = base(False)
    y = heading(d, "The plan: one diagram, five layers")
    qs = ["Who is in the system?", "How are they grouped?", "How open are the groupings?", "Who is in charge?", "How does anxiety move?"]
    who = ["Minuchin", "Minuchin", "Minuchin", "Minuchin", "Bowen"]
    for i, (n, q, w) in enumerate(zip(LAYERS, qs, who)):
        x = 110 + i * 345; yy = 330
        d.rounded_rectangle([x, yy, x + 310, yy + 420], radius=24, fill=WHITE, outline=SAND_DARK, width=3)
        d.ellipse([x + 110, yy + 30, x + 200, yy + 120], fill=TERRA)
        d.text((x + 155 - d.textlength(str(i + 1), font=font(48, bold=True)) / 2, yy + 48), str(i + 1), font=font(48, bold=True), fill=WHITE)
        d.text((x + 155 - d.textlength(n, font=font(38, bold=True)) / 2, yy + 150), n, font=font(38, bold=True), fill=TEAL)
        draw_text(d, (x + 30, yy + 220), q, font(32), INK, 250, 1.25, align="center")
        d.text((x + 155 - d.textlength(w, font=font(26)) / 2, yy + 360), w, font=font(26), fill=MUTED)
        if i < 4: arrow(d, (x + 316, yy + 210), (x + 340, yy + 210), MUTED, 4, 14)
    draw_text(d, (110, 800), "Each layer answers a question the previous layer could not. Draw along as we go.", font(34), MUTED, 1700, 1.3)
    footer(d, False)
    return img

def s_notation():
    img, d = base(False)
    y = heading(d, "Minuchin's notation — the lines you will draw")
    items = [("clear boundary", lambda x, yy: dashed(d, (x, yy), (x + 300, yy), TEAL, 6, 24, 16)),
             ("diffuse (enmeshed)", lambda x, yy: dotted(d, (x, yy), (x + 300, yy), TEAL, 9, 20)),
             ("rigid (disengaged)", lambda x, yy: d.line([(x, yy), (x + 300, yy)], fill=TEAL, width=16)),
             ("over-involvement", lambda x, yy: triple(d, (x, yy), (x + 300, yy), TEAL, 5, 12)),
             ("conflict", lambda x, yy: zigzag(d, (x, yy), (x + 300, yy), TEAL, 5)),
             ("coalition", lambda x, yy: (d.line([(x, yy), (x + 300, yy)], fill=TEAL, width=6), d.line([(x, yy - 22), (x, yy)], fill=TEAL, width=6), d.line([(x + 300, yy - 22), (x + 300, yy)], fill=TEAL, width=6)))]
    for i, (lab, fn) in enumerate(items):
        c, r = divmod(i, 3); x = 130 + c * 940; yy = y + 80 + r * 200
        fn(x, yy); d.text((x + 340, yy - 22), lab, font=font(36, bold=True), fill=INK)
    draw_text(d, (110, 880), "Structure is invisible — you infer it from repeated transactions: who speaks for whom, who sits by whom, who is interrupted, who is obeyed.", font(32), MUTED, 1700, 1.3)
    footer(d, False)
    return img

def s_continuum():
    img, d = base(False)
    heading(d, "The enmeshment–disengagement continuum")
    x0, x1, y = 340, 1580, 520
    for k in range(0, 1241, 4):
        t = k / 1240; col = tuple(int(TERRA[i] * (1 - abs(t - 0.5) * 2) + TEAL[i] * abs(t - 0.5) * 2) for i in range(3))
        d.line([(x0 + k, y - 14), (x0 + k, y + 14)], fill=col)
    for xx, lab, sub, style in [(x0, "ENMESHED", "diffuse boundaries · too open", "dotted"), ((x0 + x1) // 2, "CLEAR", "firm enough to protect, open enough for contact", "dashed"), (x1, "DISENGAGED", "rigid boundaries · too closed", "solid")]:
        d.ellipse([xx - 22, y - 22, xx + 22, y + 22], fill=WHITE, outline=INK, width=4)
        f = font(40, bold=True); d.text((xx - d.textlength(lab, font=f) / 2, y + 50), lab, font=f, fill=TEAL)
        draw_text(d, (xx - 220, y + 110), sub, font(28), MUTED, 440, 1.25, align="center")
        if style == "dotted": dotted(d, (xx - 120, y - 80), (xx + 120, y - 80), TEAL, 9, 20)
        elif style == "dashed": dashed(d, (xx - 120, y - 80), (xx + 120, y - 80), TEAL, 6, 24, 16)
        else: d.line([(xx - 120, y - 80), (xx + 120, y - 80)], fill=TEAL, width=16)
    d.rounded_rectangle([260, 760, 1660, 900], radius=24, fill=WHITE, outline=SAND_DARK, width=3)
    draw_text(d, (300, 782), "A continuum, not a diagnosis. Closeness ≠ enmeshment. The test is function: does the boundary let each subsystem do its job?", font(34, bold=True), TEAL, 1320, 1.3, align="center")
    footer(d, False)
    return img

def tri(d, cx, cy, size, labels, close, outsider_col=TEAL, fill=None, anxious=False):
    A = (cx - size, cy + size * 0.6); B = (cx + size, cy + size * 0.6); C = (cx, cy - size * 0.9)
    pts = {"A": A, "B": B, "C": C}
    d.polygon([A, B, C], outline=TEAL, fill=fill or WHITE, width=4)
    a, b = close
    d.line([pts[a], pts[b]], fill=TERRA, width=12)
    if anxious:
        zigzag(d, pts[a], pts[b], WHITE, 3, 8, 12)
    for k, (x, y) in pts.items():
        person(d, x, y, labels[k], r=34, col=TERRA if k in close else outsider_col)

def s_triangle_states():
    img, d = base(False)
    heading(d, "Bowen's emotional triangle — the smallest stable unit")
    for i, (title, body, anx, close) in enumerate([
        ("Calm", "Two insiders enjoy closeness; the outsider feels a little left out — and is comfortable enough.", False, ("A", "B")),
        ("Anxious", "Insiders become uncomfortable; one moves toward the outsider; the conflict shifts to a new side. Anxiety travels — it does not disappear.", True, ("A", "C")),
    ]):
        x = 110 + i * 880
        d.rounded_rectangle([x, 260, x + 820, 920], radius=24, fill=WHITE, outline=SAND_DARK, width=3)
        d.text((x + 40, 290), title, font=font(44, bold=True), fill=TERRA if anx else TEAL)
        tri(d, x + 410, 560, 170, {"A": "A", "B": "B", "C": "C"}, close, anxious=anx)
        draw_text(d, (x + 40, 760), body, font(30), INK, 740, 1.3)
    footer(d, False, "Layer 5 of 5")
    return img

def s_interlocking():
    img, d = base(False)
    heading(d, "Triangles interlock — pull one and the others move")
    tri(d, 620, 540, 200, {"A": "F", "B": "M", "C": "T"}, ("B", "C"))
    d.text((520, 790), "the central triangle", font=font(28, bold=True), fill=TEAL)
    # Father's triangle with evenings out
    d.ellipse([140, 300, 220, 380], fill=SOFT, outline=MUTED, width=3); d.text((110, 390), "evenings out", font=font(24), fill=MUTED)
    d.line([(220, 340), (420, 640)], fill=MUTED, width=4); d.line([(180, 380), (420, 660)], fill=MUTED, width=4)
    # Mother's triangle with grandmother
    d.ellipse([1040, 300, 1120, 380], fill=SOFT, outline=MUTED, width=3); d.text((1000, 390), "her mother (phone)", font=font(24), fill=MUTED)
    d.line([(1040, 340), (820, 640)], fill=MUTED, width=4); d.line([(1080, 380), (840, 660)], fill=MUTED, width=4)
    # therapist pulled in
    d.ellipse([1060, 790, 1160, 890], fill=(252, 236, 226), outline=TERRA, width=4); d.text((1180, 820), "you — the therapist", font=font(26, bold=True), fill=TERRA)
    dashed(d, (1070, 800), (860, 680), TERRA, 4, 18, 14); dashed(d, (1060, 850), (470, 690), TERRA, 4, 18, 14)
    d.rounded_rectangle([1240, 300, 1820, 600], radius=24, fill=WHITE, outline=SAND_DARK, width=3)
    draw_text(d, (1270, 330), "Detriangling: stay connected to each person without taking a side. Lower the anxiety in the room. One of the hardest skills you will learn.", font(30), INK, 520, 1.3)
    footer(d, False, "Layer 5 of 5")
    return img

def s_complete_map():
    img, d = base(False)
    heading(d, "The complete map — read it as a hypothesis", size=50)
    draw_map(d, 5, focus=False)
    triangle_inset(d, 1300, 160)
    d.rounded_rectangle([1300, 640, 1820, 900], radius=24, fill=WHITE, outline=SAND_DARK, width=3)
    draw_text(d, (1330, 665), "A hypothesis, not a diagnosis. An arrangement, not a villain. Revise it the moment the family surprises you.", font(30), INK, 460, 1.3)
    footer(d, False, "All 5 layers")
    return img

def mini_map(d, x, y, kind):
    """Small structural map in a 500x380 box at (x,y)."""
    gy = y + 200
    dashed(d, (x + 20, gy), (x + 480, gy), MUTED, 3, 18, 12)
    if kind == "detoured":
        F, M, C = (x + 150, y + 110), (x + 350, y + 110), (x + 250, y + 300)
        dashed(d, (F[0] + 40, F[1]), (M[0] - 40, M[1]), TEAL, 5, 18, 12)
        arrow(d, (F[0] + 10, F[1] + 50), (C[0] - 30, C[1] - 45), TERRA, 5); arrow(d, (M[0] - 10, M[1] + 50), (C[0] + 30, C[1] - 45), TERRA, 5)
        person(d, *F, "F", r=36); person(d, *M, "M", r=36); person(d, *C, "C", r=36, col=TERRA, fill=(252, 236, 226))
        d.text((x + 300, y + 250), "the project", font=font(22), fill=TERRA)
    elif kind == "coalition":
        F, M, C, G = (x + 110, y + 130), (x + 300, y + 100), (x + 420, y + 100), (x + 420, y + 300)
        zigzag(d, (F[0] + 40, F[1]), (M[0] - 40, M[1] + 10), TERRA, 4, 8, 8)
        triple(d, (M[0] + 38, M[1]), (C[0] - 38, C[1]), TERRA, 3, 8)
        person(d, *G, "C", ghost=True); arrow(d, (G[0], G[1] - 40), (C[0], C[1] + 42), MUTED, 3, 14)
        person(d, *F, "F", r=36); person(d, *M, "M", r=36); person(d, *C, "C", r=36, col=TERRA, fill=(252, 236, 226))
    elif kind == "disengaged":
        F, M, C1, C2 = (x + 90, y + 110), (x + 330, y + 110), (x + 270, y + 300), (x + 400, y + 300)
        d.line([(x + 170, y + 50), (x + 170, y + 350)], fill=TEAL, width=12)
        dotted(d, (M[0], M[1] + 40), (C1[0], C1[1] - 40), TEAL, 7, 16); dotted(d, (M[0] + 20, M[1] + 40), (C2[0], C2[1] - 40), TEAL, 7, 16)
        dotted(d, (C1[0] + 38, C1[1]), (C2[0] - 38, C2[1]), TEAL, 7, 16)
        person(d, *F, "F", r=36); person(d, *M, "M", r=36); person(d, *C1, "C", r=32); person(d, *C2, "C", r=32)
        d.text((x + 20, y + 320), "visitor", font=font(22), fill=MUTED)
    else:  # healthy
        F, M, C1, C2, G = (x + 170, y + 110), (x + 330, y + 110), (x + 200, y + 300), (x + 320, y + 300), (x + 60, y + 40)
        box(d, (x + 110, y + 50, x + 400, y + 170), None, TEAL_LIGHT, w=3)
        dashed(d, (F[0] + 40, F[1]), (M[0] - 40, M[1]), TEAL, 5, 18, 12)
        dashed(d, (C1[0] + 36, C1[1]), (C2[0] - 36, C2[1]), TEAL, 5, 18, 12)
        dashed(d, (G[0] + 30, G[1] + 20), (F[0] - 36, F[1] - 20), MUTED, 3, 14, 10)
        person(d, *F, "F", r=36); person(d, *M, "M", r=36); person(d, *C1, "C", r=32); person(d, *C2, "C", r=32)
        d.ellipse([G[0] - 26, G[1] - 26, G[0] + 26, G[1] + 26], fill=SOFT, outline=MUTED, width=3); d.text((G[0] - 14, G[1] - 14), "G", font=font(24, bold=True), fill=MUTED)

def s_three_maps(show_healthy=False):
    img, d = base(False)
    heading(d, "Maps you will meet again and again" if not show_healthy else "…and a healthy-enough map, for contrast")
    items = [("1 · Detoured conflict", "detoured", "Parents unite in worry or anger about a child instead of facing their own disagreement. Every arrow points at the child."),
             ("2 · Cross-generational coalition", "coalition", "One parent and one child against the other parent. Look for a child who knows too much about the marriage."),
             ("3 · Disengaged father, enmeshed mother", "disengaged", "Father provides and withdraws; mother and children form a dense unit. Works — until adolescence.")]
    if show_healthy:
        items = items[:2] + [("Healthy enough", "healthy", "Parents together above the line with protected space; children together below, able to reach them; grandparents connected but not in charge.")]
    for i, (t, kind, body) in enumerate(items):
        x = 110 + i * 580
        hl = show_healthy and kind == "healthy"
        d.rounded_rectangle([x, 230, x + 540, 930], radius=24, fill=WHITE, outline=TERRA if hl else SAND_DARK, width=5 if hl else 3)
        draw_text(d, (x + 24, 250), t, font(32, bold=True), TERRA if hl else TEAL, 500, 1.15)
        mini_map(d, x + 20, 320, kind)
        draw_text(d, (x + 24, 740), body, font(26), INK, 492, 1.3)
    footer(d, False)
    return img

def s_summary_chips():
    img, d = base(True)
    heading(d, "The whole diagram", dark=True)
    rows = [("Members", "who is in the system — decided by function"), ("Subsystems", "spousal · parental · sibling — each asks for different skills"),
            ("Boundaries", "clear · diffuse · rigid — judged by function, not closeness"), ("Hierarchy", "a clear generational boundary; the cross-generational coalition as its breakdown"),
            ("Triangles", "anxiety moving between insiders and outsider; stay out of the triangle")]
    for i, (n, s) in enumerate(rows):
        y = 250 + i * 128
        d.rounded_rectangle([110, y, 560, y + 86], radius=43, fill=TERRA)
        d.text((150, y + 20), f"{i + 1}", font=font(40, bold=True), fill=WHITE); d.text((210, y + 20), n, font=font(40, bold=True), fill=WHITE)
        draw_text(d, (620, y + 18), s, font(36), SAND, 1200, 1.2)
    footer(d, True)
    return img

# ---------------- deck ----------------
def deck():
    D = []
    D.append(("01-welcome-plan.mp3", [
        (1.2, E.s_title("Core Systems Concepts II", "Week 5 — Boundaries, Subsystems, Hierarchy and Triangles\nOne diagram, built in five layers", "MFT 701 · Master of Marriage and Family Therapy")),
        (2.4, E.s_bullets("Learning Objectives", ["Describe the three family subsystems and what each requires.", "Classify boundaries as clear, diffuse or rigid, and locate a family on the enmeshment–disengagement continuum.", "Explain hierarchy and recognize a cross-generational coalition.", "Define Bowen's emotional triangle and identify one in a case."], nums=True, intro="By the end of this lecture you will be able to…")),
        (3.0, s_plan()),
        (1.4, E.s_cards("Two map-makers", [("Salvador Minuchin", "Structural Family Therapy. Layers 1–4: members, subsystems, boundaries, hierarchy — and the notation we draw with."), ("Murray Bowen", "Bowen Family Systems Theory. Layer 5: the emotional triangle — how anxiety moves between people.")], dark=True)),
    ]))
    D.append(("02-layer1-members.mp3", [
        (2.2, s_layer(1, "Who is in the system. Four people — and a judgement about who counts.", None, "Layer 1 — Members")),
        (1.6, s_layer(1, "Membership is functional: anyone whose behaviour regularly shapes the pattern — the household is not always the family.", None, "Layer 1 — Members")),
        (1.6, E.s_quote("Family structure is the invisible set of functional demands that organizes the ways in which family members interact.", "Salvador Minuchin, Families and Family Therapy (1974)")),
        (1.0, s_layer(1, "Who is in the system.", "Four circles tell us who — nothing about how they are organized. A census, not a map.", "Layer 1 — Members")),
    ]))
    D.append(("03-layer2-subsystems.mp3", [
        (3.2, s_layer(2, "How the members are grouped: the spousal, parental and sibling subsystems — each with its own task.", None, "Layer 2 — Subsystems")),
        (1.4, E.s_cards("Three subsystems every family must carry", [("Spousal", "The adults as partners: support, intimacy, negotiating difference. Needs protection from children and in-laws."), ("Parental", "The same people in their executive role: nurture, guidance, limits. Trouble when the two hats become one."), ("Sibling", "The first social laboratory: negotiating, competing, allying, losing gracefully.")])),
        (1.6, s_layer(2, "One person belongs to many subsystems at once — and each asks for different skills.", "A box tells us membership, not how open the box is. For that we need boundaries.", "Layer 2 — Subsystems")),
    ]))
    D.append(("04-layer3-boundaries.mp3", [
        (1.2, s_layer(3, "The edges: rules about who participates in a subsystem, and how.", None, "Layer 3 — Boundaries")),
        (2.4, s_notation()),
        (2.2, s_continuum()),
        (1.4, s_layer(3, "A dotted (diffuse) line between mother and son; a heavy wall (rigid) around father.", "A boundary tells us permeability, not authority. Who is actually in charge?", "Layer 3 — Boundaries")),
    ]))
    D.append(("05-layer4-hierarchy.mp3", [
        (2.2, s_layer(4, "Who is in charge: the generational boundary and the executive subsystem.", None, "Layer 4 — Hierarchy")),
        (2.4, s_layer(4, "Tunde has moved up: over-involvement with mother, a coalition against father, open conflict between the parents.", None, "Layer 4 — Hierarchy")),
        (1.8, E.s_statement("The symptom often appears in the child who is holding the structure together.", "Haley: the cross-generational coalition — a parent and a child joined against the other parent, usually covertly.")),
        (1.0, s_layer(4, "Hierarchy inverted — a parentified child; Bisi alone below the line.", "A structure is a snapshot. It shows the arrangement, not the engine. We need Bowen.", "Layer 4 — Hierarchy")),
    ]))
    D.append(("06-layer5-triangles.mp3", [
        (1.4, s_layer(5, None, None, "Layer 5 — Triangles")),
        (1.8, s_triangle_states()),
        (1.6, s_layer(5, None, None, "Layer 5 — Triangles")),
        (2.2, s_interlocking()),
    ]))
    D.append(("07-reading-the-map.mp3", [
        (3.0, s_complete_map()),
        (3.2, E.s_compare("What would you do with it?", ("Structural (Minuchin)", ["Joining — earn the right to intervene", "Enactment — parents talk about school; Tunde stays out of it", "Boundary-making — chairs, interruptions, parent-only tasks", "Unbalancing — side briefly with father to pull him back in"]), ("Bowenian (Bowen)", ["Lower the anxiety in the room", "Stay in contact with each person without taking sides", "Coach the parents — often one at a time — to deal directly with each other", "Different routes — the same map"]), vs="&")),
    ]))
    D.append(("08-three-maps.mp3", [(3.4, s_three_maps(False)), (2.0, s_three_maps(True))]))
    D.append(("09-limits-reflection.mp3", [
        (3.0, E.s_bullets("Limits of the map", ["Culture — enmeshment in Philadelphia may be ordinary interdependence in Ibadan or Manila. Ask what is normative for this family's community first.", "Gender and power — Hare-Mustin (1978): hierarchy was often restored by restoring the father; 'enmeshed mother' given to women doing all the caregiving. Hierarchy = a functional executive subsystem, not a particular person on top.", "The therapist — you have a map of your own; the family that triangles you most easily resembles yours. That is what supervision is for."], nums=True)),
        (2.2, E.s_cards("A brief reflection", [("Genesis 2:24 — leave and cleave", "Leaving and cleaving is a generational boundary drawn long before Minuchin. Many marital triangles are failures of leaving."), ("Ephesians 6:1–4 — hierarchy inside reciprocity", "Children honour; fathers do not exasperate. Authority as responsibility turned toward the weaker member — a good definition of a healthy executive subsystem.")], dark=True)),
    ]))
    D.append(("10-summary-close.mp3", [
        (2.4, s_summary_chips()),
        (2.2, E.s_bullets("Review Questions", ["Draw the Minuchin notation for clear, diffuse and rigid boundaries, and give a clinical example of each.", "Describe a cross-generational coalition and explain why the symptom so often appears in the child.", "Define an emotional triangle, and describe one thing a therapist can do to avoid being triangled by a couple."], nums=True, intro="Pause the video and write your answers.")),
        (2.4, E.s_cards("Looking Ahead", [("Next Week", "Overview of the major schools — Bowen, Structural, Strategic and Experiential family therapy, side by side."), ("Assignment", "Redraw last week's family as a Minuchin structural map: every boundary marked clear / diffuse / rigid, the generational line shown, one triangle overlaid. Add a 150-word hypothesis linking structure and presenting concern.")], dark=True)),
        (0.7, E.s_title("Thank you.", "End of Week 5\nThe map is complete — see you next week.", "MFT 701 · Week 5")),
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
