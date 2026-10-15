#!/usr/bin/env python3
"""
Build the MFT 701 Week 1 presentation-styled lecture video.

Renders 1920x1080 slides with Pillow, times them against the narrated audio
segments in ../Audio/MFT-701-W01, and assembles an MP4 with ffmpeg
(bundled via imageio-ffmpeg).

Usage:  python3 build_video.py
"""
import glob
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont
from mutagen.mp3 import MP3
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "..", "Audio", "MFT-701-W01")
ASSETS = os.path.join(HERE, "assets")
SLIDES = os.path.join(HERE, "slides")
OUT = os.path.join(HERE, "MFT-701-Week-01-Lecture.mp4")
os.makedirs(SLIDES, exist_ok=True)

W, H = 1920, 1080

# ---------- Palette ----------
TEAL = (15, 58, 68)
TEAL_DARK = (10, 42, 50)
TEAL_LIGHT = (30, 95, 108)
SAND = (245, 239, 230)
SAND_DARK = (228, 197, 144)
TERRA = (201, 105, 63)
CREAM = (250, 247, 241)
INK = (27, 42, 47)
MUTED = (110, 128, 134)
WHITE = (255, 255, 255)

# ---------- Fonts ----------
FD = "/usr/share/fonts/truetype/dejavu/"
def font(size, bold=False, serif=False):
    if serif:
        name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
    else:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(FD + name, size)

COURSE = "MFT 701 · Fundamentals of Marriage and Family Therapy"
UNI = "Triune Biblical University Global Extension"

# ---------- Text helpers ----------
def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_text(draw, xy, text, fnt, fill, max_w, line_gap=1.25, align="left"):
    x, y = xy
    lh = int(fnt.size * line_gap)
    for para in text.split("\n"):
        for ln in wrap(draw, para, fnt, max_w) or [""]:
            if align == "center":
                tw = draw.textlength(ln, font=fnt)
                draw.text((x + (max_w - tw) / 2, y), ln, font=fnt, fill=fill)
            else:
                draw.text((x, y), ln, font=fnt, fill=fill)
            y += lh
    return y

def text_height(draw, text, fnt, max_w, line_gap=1.25):
    n = sum(len(wrap(draw, p, fnt, max_w) or [""]) for p in text.split("\n"))
    return n * int(fnt.size * line_gap)

# ---------- Chrome ----------
def base(dark=False):
    img = Image.new("RGB", (W, H), TEAL if dark else SAND)
    d = ImageDraw.Draw(img)
    # left accent bar
    d.rectangle([0, 0, 18, H], fill=TERRA)
    return img, d

def footer(d, dark=False, badge=None):
    col = SAND_DARK if dark else MUTED
    d.line([(60, H - 78), (W - 60, H - 78)], fill=col, width=2)
    d.text((60, H - 62), COURSE, font=font(22), fill=col)
    t = UNI
    d.text((W - 60 - d.textlength(t, font=font(22)), H - 62), t, font=font(22), fill=col)
    if badge:
        f = font(22, bold=True)
        tw = d.textlength(badge, font=f)
        d.rounded_rectangle([W - 60 - tw - 36, 40, W - 60, 92], radius=26, fill=TERRA)
        d.text((W - 60 - tw - 18, 52), badge, font=f, fill=WHITE)

def heading(d, title, dark=False, y=90, size=58):
    d.text((110, y), title, font=font(size, bold=True), fill=SAND if dark else TEAL)
    d.rectangle([110, y + size + 22, 110 + 140, y + size + 30], fill=TERRA)
    return y + size + 70

def paste_fit(img, path, box, mode="contain", radius=28):
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    im = Image.open(path).convert("RGB")
    iw, ih = im.size
    s = (max if mode == "cover" else min)(bw / iw, bh / ih)
    im = im.resize((int(iw * s), int(ih * s)), Image.LANCZOS)
    if mode == "cover":
        l = (im.width - bw) // 2
        t = (im.height - bh) // 2
        im = im.crop((l, t, l + bw, t + bh))
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=radius, fill=255)
    px = x0 + (bw - im.width) // 2
    py = y0 + (bh - im.height) // 2
    img.paste(im, (px, py), mask)

# ---------- Slide types ----------
def s_title(title, subtitle, small):
    img, d = base(dark=True)
    d.rectangle([0, 0, W, H], fill=TEAL)
    d.rectangle([0, 0, 18, H], fill=TERRA)
    # decorative circles
    for cx, cy, r, c in [(1650, 220, 260, TEAL_LIGHT), (1750, 820, 180, TERRA), (1450, 900, 90, SAND_DARK)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    d.text((120, 300), small, font=font(30), fill=SAND_DARK)
    y = draw_text(d, (120, 360), title, font(92, bold=True), SAND, 1250, 1.1)
    d.rectangle([120, y + 20, 360, y + 30], fill=TERRA)
    draw_text(d, (120, y + 70), subtitle, font(44), CREAM, 1250, 1.3)
    d.text((120, H - 110), UNI, font=font(26), fill=SAND_DARK)
    return img

def s_statement(text, sub=None, dark=True, badge=None):
    img, d = base(dark)
    f = font(72, bold=True, serif=True)
    th = text_height(d, text, f, 1500, 1.2)
    y = (H - th) // 2 - (40 if sub else 0)
    draw_text(d, (210, y), text, f, SAND if dark else TEAL, 1500, 1.2, align="center")
    if sub:
        draw_text(d, (210, y + th + 40), sub, font(36), SAND_DARK if dark else MUTED, 1500, 1.3, align="center")
    footer(d, dark, badge)
    return img

def s_bullets(title, bullets, badge=None, dark=False, intro=None, nums=False, active=None):
    img, d = base(dark)
    y0 = heading(d, title, dark)
    fcol = SAND if dark else INK
    fb = font(46)
    fbb = font(46, bold=True)
    fbody = font(38)
    def render(d, y, measure=False):
        if intro:
            y = draw_text(d, (110, y), intro, font(36), SAND_DARK if dark else MUTED, 1700) + 34
        for i, b in enumerate(bullets):
            dim = active is not None and i > active
            col = (MUTED if not dark else TEAL_LIGHT) if dim else fcol
            head, body = b if isinstance(b, tuple) else (None, b)
            bx = 110
            if not measure:
                if nums:
                    d.ellipse([bx, y + 4, bx + 58, y + 62], fill=(MUTED if dim else TERRA))
                    n = str(i + 1)
                    d.text((bx + 29 - d.textlength(n, font=font(32, bold=True)) / 2, y + 13), n, font=font(32, bold=True), fill=WHITE)
                else:
                    d.rounded_rectangle([bx + 8, y + 20, bx + 34, y + 46], radius=7, fill=(MUTED if dim else TERRA))
            tx = bx + 90
            if head:
                if not measure:
                    d.text((tx, y), head, font=fbb, fill=col)
                y = draw_text(d, (tx, y + 62), body, fbody, col, 1620, 1.25) + 34
            else:
                y = draw_text(d, (tx, y), body, fb, col, 1620, 1.28) + 34
        return y
    scratch = ImageDraw.Draw(Image.new("RGB", (W, H)))
    end = render(scratch, y0, measure=True)
    avail = (H - 110) - y0
    used = end - y0
    start = y0 + max(0, (avail - used) // 2) - 10
    render(d, start)
    footer(d, dark, badge)
    return img

def s_cards(title, cards, badge=None, dark=False, cols=None):
    img, d = base(dark)
    y = heading(d, title, dark)
    n = len(cards)
    cols = cols or n
    rows = math.ceil(n / cols)
    gap = 36
    cw = (W - 220 - gap * (cols - 1)) // cols
    ch = (H - y - 130 - gap * (rows - 1)) // rows
    fh, fbd = font(42, bold=True), font(34)
    for i, (head, body) in enumerate(cards):
        r, c = divmod(i, cols)
        x0 = 110 + c * (cw + gap)
        y0 = y + r * (ch + gap)
        d.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], radius=24, fill=TEAL_DARK if dark else WHITE,
                            outline=TEAL_LIGHT if dark else SAND_DARK, width=3)
        d.rectangle([x0, y0, x0 + cw, y0 + 12], fill=TERRA)
        hh = text_height(d, head, fh, cw - 72, 1.15)
        bh = text_height(d, body, fbd, cw - 72, 1.32)
        block = hh + 22 + bh
        ty = y0 + 12 + max(36, ((ch - 12) - block) // 2)
        yy = draw_text(d, (x0 + 36, ty), head, fh, SAND if dark else TEAL, cw - 72, 1.15)
        draw_text(d, (x0 + 36, yy + 22), body, fbd, CREAM if dark else INK, cw - 72, 1.32)
    footer(d, dark, badge)
    return img

def s_compare(title, left, right, badge=None, vs="vs"):
    img, d = base(False)
    y = heading(d, title)
    cw = (W - 220 - 120) // 2
    for i, (head, items, col) in enumerate([(left[0], left[1], MUTED), (right[0], right[1], TERRA)]):
        x0 = 110 + i * (cw + 120)
        d.rounded_rectangle([x0, y, x0 + cw, H - 130], radius=24, fill=WHITE, outline=col, width=4)
        yy = draw_text(d, (x0 + 40, y + 40), head, font(46, bold=True), col if i else TEAL, cw - 80, 1.15) + 36
        for it in items:
            d.rounded_rectangle([x0 + 40, yy + 18, x0 + 62, yy + 40], radius=6, fill=col)
            yy = draw_text(d, (x0 + 92, yy), it, font(40), INK, cw - 140, 1.3) + 28
    mid = 110 + cw + 60
    d.ellipse([mid - 44, (y + H - 130) // 2 - 44, mid + 44, (y + H - 130) // 2 + 44], fill=TEAL)
    d.text((mid - d.textlength(vs, font=font(30, bold=True)) / 2, (y + H - 130) // 2 - 20), vs, font=font(30, bold=True), fill=SAND)
    footer(d, False, badge)
    return img

def s_image(title, path, caption=None, quote=None, badge=None, dark=True, side="left"):
    img, d = base(dark)
    y = heading(d, title, dark)
    paste_fit(img, path, (110, y, 1180, H - 130), "cover")
    tx = 1240
    if quote:
        d.text((tx, y - 10), "\u201c", font=font(140, serif=True, bold=True), fill=TERRA)
        yy = draw_text(d, (tx, y + 120), quote, font(40, serif=True), SAND if dark else TEAL, 560, 1.3)
    else:
        yy = y
    if caption:
        draw_text(d, (tx, yy + 40), caption, font(30), SAND_DARK if dark else MUTED, 560, 1.35)
    footer(d, dark, badge)
    return img

NODES = ["Definition", "The Systemic\nLens", "History", "Major\nSchools", "Professional\nIdentity & Scope", "Person of the\nTherapist"]

def s_concept_map(active=None, all_on=False, title="The Course Map", badge=None):
    img, d = base(dark=True)
    heading(d, title, dark=True)
    cx, cy, R = 960, 590, 330
    # lines
    pts = []
    for i in range(6):
        a = -math.pi / 2 + i * math.pi / 3
        pts.append((cx + R * 1.5 * math.cos(a), cy + R * 0.85 * math.sin(a)))
    for i, (x, y) in enumerate(pts):
        on = all_on or active == i
        d.line([(cx, cy), (x, y)], fill=TERRA if on else TEAL_LIGHT, width=6 if on else 3)
    # centre
    d.ellipse([cx - 230, cy - 95, cx + 230, cy + 95], fill=TERRA)
    draw_text(d, (cx - 220, cy - 46), "Marriage & Family\nTherapy", font(38, bold=True), WHITE, 440, 1.15, align="center")
    # nodes
    for i, (x, y) in enumerate(pts):
        on = all_on or active == i
        fill = SAND if on else TEAL_DARK
        outline = TERRA if on else TEAL_LIGHT
        d.ellipse([x - 150, y - 72, x + 150, y + 72], fill=fill, outline=outline, width=5)
        d.ellipse([x - 150 + 14, y - 72 + 14, x - 150 + 54, y - 72 + 54], fill=TERRA if on else TEAL_LIGHT)
        d.text((x - 150 + 34 - d.textlength(str(i + 1), font=font(24, bold=True)) / 2, y - 72 + 22), str(i + 1), font=font(24, bold=True), fill=WHITE)
        f = font(28, bold=True)
        th = text_height(d, NODES[i], f, 240, 1.1)
        draw_text(d, (x - 120, y - th / 2 + 4), NODES[i], f, TEAL if on else SAND_DARK, 240, 1.1, align="center")
    footer(d, True, badge)
    return img

def s_timeline(title, events, badge=None):
    img, d = base(False)
    y = heading(d, title)
    ly = 560
    d.line([(280, ly), (W - 280, ly)], fill=TEAL, width=8)
    n = len(events)
    step = (W - 560) / (n - 1)
    for i, (when, what) in enumerate(events):
        x = 280 + i * step
        d.ellipse([x - 22, ly - 22, x + 22, ly + 22], fill=TERRA, outline=SAND, width=5)
        f = font(40, bold=True)
        tw = d.textlength(when, font=f)
        d.text((x - tw / 2, ly - 100), when, font=f, fill=TEAL)
        draw_text(d, (x - 165, ly + 56), what, font(30), INK, 330, 1.3, align="center")
    footer(d, False, badge)
    return img

def s_quote(text, attribution=None, badge=None):
    img, d = base(dark=True)
    d.text((180, 180), "\u201c", font=font(220, serif=True, bold=True), fill=TERRA)
    f = font(56, serif=True)
    th = text_height(d, text, f, 1420, 1.3)
    y = (H - th) // 2
    draw_text(d, (260, y), text, f, SAND, 1420, 1.3)
    if attribution:
        d.text((260, y + th + 30), "— " + attribution, font=font(32), fill=SAND_DARK)
    footer(d, True, badge)
    return img

# ---------- Deck definition: (segment_audio_file, [(weight, slide_image), ...]) ----------
MOBILE = os.path.join(ASSETS, "mobile.png")
FAMILY = os.path.join(ASSETS, "adebayo-family.png")

def build_deck():
    deck = []

    # Segment 1 — welcome & objectives
    deck.append(("01-welcome.mp3", [
        (2.0, s_title("Fundamentals of Marriage and Family Therapy",
                      "Week 1 — What is Marriage and Family Therapy?\nScope, Identity and Distinctives of the Profession",
                      "MFT 701 · Master of Marriage and Family Therapy")),
        (4.0, s_cards("Course Roadmap — 16 Weeks", [
            ("Weeks 1–7 · Foundations", "What the profession is, where it came from, how systemic thinking works, and the major schools of therapy."),
            ("Week 8 · Mid-term", "Synthesis and review — mapping the field so far."),
            ("Weeks 9–15 · Practice", "The therapist's role, the therapeutic process, the genogram, presenting problems, licensure, research evidence, and faith integration."),
            ("Week 16 · Final Integration", "Your personal philosophy of family therapy."),
        ], cols=2)),
        (1.5, s_statement("What is Marriage and Family Therapy?", "A deceptively simple question — and today's focus.")),
        (4.0, s_bullets("Learning Objectives", [
            "Define Marriage and Family Therapy and explain what makes it distinct from other mental health professions.",
            "Describe the systemic lens — the core way of thinking that defines the field.",
            "Identify the main components of the profession: history, major schools, professional identity, and scope of practice.",
            "Begin to reflect on who you are as a person entering this work — including how your faith and worldview shape how you see families.",
        ], nums=True, intro="By the end of this lecture you will be able to…")),
        (1.0, s_statement("Let's begin not with a definition,\nbut with a family.", dark=False)),
    ]))

    # Segment 2 — the hook
    deck.append(("02-the-hook.mp3", [
        (4.0, s_image("The Adebayo Family", FAMILY,
                      quote="Please, help me fix him. He has stopped going to school. He shouts at me. He locks himself in his room.",
                      caption="Mrs. Adebayo and her son Tunde, 14 — Tuesday afternoon, first session.")),
        (3.0, s_compare("Two Very Different First Questions",
                        ("The instinctive question", ["What is wrong with Tunde?", "Is he depressed? Bullied? Defiant?", "Is it a spiritual problem?"]),
                        ("The systemic question", ["What is happening in the relationships around Tunde…", "…such that his behaviour makes sense?"]))),
        (3.0, s_bullets("As the Session Unfolds…", [
            "Mr. Adebayo lost his job four months ago.",
            "He now spends most evenings out of the house.",
            "Mrs. Adebayo has taken on extra work and is exhausted.",
            "Tunde's younger sister has become very quiet and very obedient.",
            "Tunde's school refusal began when his father stopped coming home for dinner.",
        ])),
        (1.5, s_statement("A symptom is real — and it is also a signal.", "A message from a family under strain.")),
    ]))

    # Segment 3 — map + node 1
    deck.append(("03-map-and-definition.mp3", [
        (3.0, s_concept_map()),
        (1.0, s_concept_map(active=0, title="Node 1 — Definition")),
        (3.5, s_quote("Marriage and Family Therapy is the diagnosis and treatment of mental, emotional and relational problems, in which human difficulties are understood and treated within the context of relationships — especially the family.",
                      "Working definition", badge="Node 1 of 6 · Definition")),
        (4.0, s_bullets("Notice Three Things", [
            ("We diagnose and treat", "Depression, anxiety, trauma, psychosis, substance use — the full range of mental and emotional disorders."),
            ("“Relational”", "Our unit of attention is not only the person in front of us, but the relationships that person lives inside."),
            ("It's how the therapist thinks", "Systemic work is not defined by how many people are in the room. Many MFTs see individuals."),
        ], nums=True, badge="Node 1 of 6 · Definition")),
    ]))

    # Segment 4 — systemic lens
    core = [
        ("Wholeness", "The family is more than the sum of its members. You cannot understand Tunde by studying Tunde alone."),
        ("Circular causality", "Not “who started it,” but how each person's behaviour feeds the next — round and round."),
        ("Homeostasis", "Systems resist change and seek balance — even an unhealthy balance."),
        ("The symptom serves a function", "Tunde's crisis may be the one thing forcing his parents into the same room again."),
    ]
    deck.append(("04-systemic-lens.mp3", [
        (3.0, s_image("Node 2 — The Systemic Lens", MOBILE,
                      quote="Push just one piece. Every other piece moves.",
                      caption="A family is like a hanging mobile: when one member shifts, the whole system swings, adjusts, and finds a new balance.",
                      badge="Node 2 of 6")),
        (2.0, s_bullets("One Piece Moved — Everyone Shifted", [
            "Mr. Adebayo loses his job → withdraws in the evenings",
            "Mrs. Adebayo → over-functions, exhausted",
            "Tunde → refuses school, shouts, withdraws",
            "His sister → becomes silent and compliant",
            "Not four separate problems — one system finding a new, painful balance.",
        ], badge="Node 2 of 6 · Systemic Lens")),
        (1.2, s_bullets("Core Ideas of the Systemic Lens", core, nums=True, active=0, badge="Node 2 of 6 · Systemic Lens")),
        (1.2, s_bullets("Core Ideas of the Systemic Lens", core, nums=True, active=1, badge="Node 2 of 6 · Systemic Lens")),
        (1.2, s_bullets("Core Ideas of the Systemic Lens", core, nums=True, active=2, badge="Node 2 of 6 · Systemic Lens")),
        (1.4, s_bullets("Core Ideas of the Systemic Lens", core, nums=True, active=3, badge="Node 2 of 6 · Systemic Lens")),
        (2.0, s_statement("The family therapist thinks in patterns and relationships — not only in individuals and diagnoses.", "If you take one idea from today, take this one.")),
    ]))

    # Segment 5 — history
    deck.append(("05-history.mp3", [
        (1.0, s_concept_map(active=2, title="Node 3 — History")),
        (4.5, s_timeline("A Young Profession — History in Brief", [
            ("1940s", "Marriage counselling movement and child guidance clinics"),
            ("1950s", "Palo Alto: Gregory Bateson studies family communication"),
            ("1960s–70s", "Founding schools: Bowen, Minuchin, Haley, Satir, Whitaker"),
            ("1980s–90s", "Postmodern turn: narrative and solution-focused therapy"),
            ("Today", "Evidence-based, global profession — growing across Africa"),
        ], badge="Node 3 of 6 · History")),
        (2.0, s_quote("The patient's symptoms made a strange kind of sense once you watched the whole family interact.",
                      "The Palo Alto insight", badge="Node 3 of 6 · History")),
    ]))

    # Segment 6 — major schools
    deck.append(("06-major-schools.mp3", [
        (2.0, s_compare("Node 4 — The Major Schools",
                        ("First generation", ["Bowenian", "Structural", "Strategic", "Experiential"]),
                        ("Postmodern & integrative", ["Solution-Focused", "Narrative", "Collaborative", "Emotionally Focused (attachment-based)"]),
                        vs="&", badge="Node 4 of 6")),
        (2.5, s_cards("Each School Looks at the Adebayos", [
            ("Bowenian", "Patterns across generations — did Mr. Adebayo's own father withdraw under stress?"),
            ("Structural", "Boundaries and hierarchy — has Tunde been pulled into a parental role? Is there a mother–son alliance that excludes the father?"),
            ("Strategic", "Map the repeating cycle and design a task to interrupt it."),
        ], badge="Node 4 of 6 · Major Schools")),
        (2.5, s_cards("Each School Looks at the Adebayos", [
            ("Experiential", "The feelings no one is saying aloud — the father's shame, the mother's fear."),
            ("Solution-Focused", "The days Tunde did go to school — what was different on those days?"),
            ("Narrative", "Separate Tunde from “the problem” — school refusal as something the family fights together."),
        ], badge="Node 4 of 6 · Major Schools")),
        (1.0, s_statement("None is simply right or wrong. They are tools.", "Part of your journey is discovering which ones fit your hands.")),
    ]))

    # Segment 7 — professional identity
    deck.append(("07-professional-identity.mp3", [
        (3.0, s_cards("Node 5 — Professional Identity & Scope (USA)", [
            ("AAMFT", "American Association for Marriage and Family Therapy — the professional body. Publishes the Code of Ethics (studied in MFT 704)."),
            ("COAMFTE", "Commission on Accreditation for Marriage and Family Therapy Education — sets training standards."),
            ("State Licensing Boards", "Define scope of practice and the supervised hours required before independent practice."),
        ], badge="Node 5 of 6")),
        (4.0, s_cards("How Is an MFT Different?", [
            ("Marriage & Family Therapist", "Trained from day one to see and treat relationships as the primary focus — the systemic lens."),
            ("Psychologist", "Trained primarily in individual assessment and treatment."),
            ("Social Worker", "Strong focus on social systems and resources."),
            ("Pastor / Counsellor", "Spiritual authority, community, and broad supportive counselling. Overlap is real — we often work side by side."),
        ], cols=2, badge="Node 5 of 6 · Identity & Scope")),
        (2.0, s_statement("Licensure differs by country.\nProfessional identity travels with you.", "International pathways — including Nigeria — are covered in Week 13.")),
    ]))

    # Segment 8 — person of the therapist
    deck.append(("08-person-of-therapist.mp3", [
        (3.0, s_bullets("Node 6 — The Person of the Therapist", [
            ("You walk in carrying your own family", "Your experiences of marriage, parents, conflict and forgiveness shape what you notice — and what you miss."),
            ("“Use of self” — Virginia Satir", "The therapist's own presence and humanity are instruments of change."),
            ("Differentiation — Murray Bowen", "Work on your own differentiation before helping others. Family-of-origin work will not always be comfortable."),
        ], nums=True, badge="Node 6 of 6")),
        (3.0, s_cards("Faith as a Resource", [
            ("Covenant", "A deep respect for commitment and the sacredness of marriage and family."),
            ("Reconciliation", "A conviction that broken relationships can be restored."),
            ("Dignity", "Every family member — including the one labelled “the problem” — bears the image of God."),
        ], dark=True, badge="Node 6 of 6 · Person of the Therapist")),
        (3.0, s_bullets("Faith Also Carries Responsibilities", [
            "Never impose our values on clients.",
            "Serve families of every faith — and none — with equal care.",
            "Hold theology and clinical training in honest conversation, rather than letting one silence the other.",
            "Reflect: how did your own story and faith shape the way you saw the Adebayo family?",
        ], badge="Node 6 of 6 · Person of the Therapist", intro="Integration is the focus of Week 15.")),
    ]))

    # Segment 9 — zoom out and return
    deck.append(("09-zoom-out-and-return.mp3", [
        (4.0, s_concept_map(all_on=True, title="Zooming Back Out — The Full Map")),
        (3.0, s_image("Returning to the Adebayos", FAMILY,
                      quote="What happens next?",
                      caption="Widen the frame: invite Mr. Adebayo. Notice aloud when the trouble began. Let the family speak about the job loss, the shame, the fear — not only about Tunde.", dark=False)),
        (1.5, s_statement("Nothing is “fixed” yet.\nBut the mobile has started to move.", "That is the beginning of family therapy.")),
    ]))

    # Segment 10 — summary & close
    deck.append(("10-summary-and-close.mp3", [
        (3.0, s_bullets("Summary", [
            "MFT is a distinct mental health profession that treats individuals, couples and families from a relational, systemic perspective.",
            "The systemic lens means thinking in patterns, circular causality and whole systems — like a mobile.",
            "The profession has its own history, schools, ethics and licensure — and deep respect for the person and worldview of the therapist.",
        ], nums=True)),
        (3.5, s_bullets("Review Questions", [
            "What is the difference between asking “What is wrong with Tunde?” and “What is happening around Tunde?”",
            "Name and briefly explain two core ideas of the systemic lens.",
            "How might your own family history or faith influence how you see a family like the Adebayos — and why does awareness matter?",
        ], nums=True, intro="Pause the video and write your answers before moving on.")),
        (2.5, s_cards("Looking Ahead", [
            ("Next Week", "Historical roots of MFT — Bateson, Palo Alto, and the birth of a profession."),
            ("This Week's Assignment", "One page: “Why do I want to become a marriage and family therapist?” Be honest. Include your family story and faith where relevant. You will revisit it in Week 16."),
        ], dark=True)),
        (1.0, s_title("Thank you — welcome to the profession.", "End of Week 1\nSee you next week.", "MFT 701 · Week 1")),
    ]))
    return deck

# ---------- Assemble ----------
def main():
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    deck = build_deck()
    vid_list, aud_list = [], []
    idx = 0
    total = 0.0
    for audio, slides in deck:
        apath = os.path.abspath(os.path.join(AUDIO_DIR, audio))
        dur = MP3(apath).info.length
        total += dur
        aud_list.append(f"file '{apath}'")
        wsum = sum(w for w, _ in slides)
        for w, im in slides:
            idx += 1
            p = os.path.join(SLIDES, f"slide-{idx:03d}.png")
            im.save(p)
            vid_list.append((p, dur * w / wsum))
    print(f"{idx} slides, {total/60:.1f} min of narration")

    with open(os.path.join(SLIDES, "video.txt"), "w") as f:
        for p, d in vid_list:
            f.write(f"file '{p}'\nduration {d:.3f}\n")
        f.write(f"file '{vid_list[-1][0]}'\nduration 0.04\n")  # concat quirk: repeat last frame
    with open(os.path.join(SLIDES, "audio.txt"), "w") as f:
        f.write("\n".join(aud_list) + "\n")

    cmd = [ffmpeg, "-y", "-loglevel", "error", "-stats",
           "-f", "concat", "-safe", "0", "-i", os.path.join(SLIDES, "video.txt"),
           "-f", "concat", "-safe", "0", "-i", os.path.join(SLIDES, "audio.txt"),
           "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-tune", "stillimage",
           "-r", "25", "-pix_fmt", "yuv420p", "-vf", "scale=1920:1080,format=yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", OUT]
    subprocess.run(cmd, check=True)
    print("Wrote", OUT)

if __name__ == "__main__":
    main()
