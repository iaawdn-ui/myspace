#!/usr/bin/env python3
"""
MFT 701 Week 6 — Overview of the Major Schools (Compare & Contrast).
A 4-column × 5-criteria grid fills column by column, is read row by row,
then the same family is seen through four doors. Reuses build_video.py.
Usage: python3 build_week06.py
"""
import os, subprocess
from PIL import Image, ImageDraw
from mutagen.mp3 import MP3
import imageio_ffmpeg
import build_video as E
from build_video import (W, H, TEAL, TEAL_DARK, TEAL_LIGHT, SAND, SAND_DARK, TERRA, CREAM, INK, MUTED, WHITE,
                         font, draw_text, text_height, footer, heading, base)

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "..", "Audio", "MFT-701-W06")
SLIDES = os.path.join(HERE, "slides-w06")
OUT = os.path.join(HERE, "MFT-701-Week-06-Lecture.mp4")
os.makedirs(SLIDES, exist_ok=True)

PLUM = (104, 72, 118)
GREEN = (66, 118, 92)
GREY = (205, 208, 206)
SOFT = (236, 230, 220)

SCHOOLS = [
    ("Bowen", "Murray Bowen", TEAL),
    ("Structural", "Salvador Minuchin", TERRA),
    ("Strategic", "Haley · Madanes · MRI", PLUM),
    ("Experiential", "Satir · Whitaker", GREEN),
]
CRITERIA = ["View of the problem", "Goal of therapy", "Therapist's role", "Signature techniques", "Time and pace"]
CELLS = [
    ["Chronic anxiety in a family with low differentiation of self; carried in triangles across generations",
     "A structure that has failed to adapt: diffuse or rigid boundaries, unclear hierarchy, coalitions",
     "A stuck sequence: the attempted solution keeps the problem going; symptom as a move",
     "Emotional suppression and incongruent communication; avoidance of experience"],
    ["Raise differentiation — a calmer, more thoughtful self in a calmer system",
     "Restructure: clear boundaries, a working executive subsystem",
     "Solve the presenting problem; interrupt the sequence — insight not required",
     "Growth: congruence, authentic feeling, self-esteem"],
    ["Calm coach and researcher; stays out of the triangles",
     "Active stage director; joins, then challenges and unbalances",
     "Strategist responsible for change; planful, directive, sometimes indirect",
     "Warm, spontaneous, personally present; the self as instrument"],
    ["Genogram · process questions · I-position · coaching · going home",
     "Joining · mapping · enactment · boundary making · unbalancing",
     "Directives · tasks · reframing · paradox · pretend techniques",
     "Sculpting · reconstruction · parts party · humour · self-disclosure"],
    ["Multigenerational · slow · often one motivated adult",
     "Present · action in the session · months",
     "Present · brief (MRI: 10 sessions) · change between sessions",
     "Here and now · intense · the experience in the room"],
]

def tint(col, k=0.12):
    return tuple(int(c * k + 255 * (1 - k)) for c in col)

# ---------------- the grid ----------------
def s_grid(cols_filled=0, active_col=None, active_row=None, title="The comparison grid", badge=None):
    img, d = base(False)
    heading(d, title, size=48)
    x0, y0 = 110, 215
    lw = 250                      # criteria label column
    cw = (W - 2 * x0 - lw) // 4   # 377
    hh = 92                       # header height
    rh = (H - 130 - y0 - hh) // 5 # row height
    # header row
    for j, (name, who, col) in enumerate(SCHOOLS):
        x = x0 + lw + j * cw
        filled = j < cols_filled
        dim = active_col is not None and j != active_col
        bg = col if filled else GREY
        if filled and dim: bg = tint(col, 0.45)
        d.rounded_rectangle([x + 4, y0, x + cw - 4, y0 + hh - 6], radius=16, fill=bg)
        d.text((x + 20, y0 + 12), name, font=font(34, bold=True), fill=WHITE)
        d.text((x + 20, y0 + 54), who, font=font(22), fill=WHITE)
    # rows
    for i, crit in enumerate(CRITERIA):
        y = y0 + hh + i * rh
        row_active = active_row == i
        row_dim = active_row is not None and not row_active
        d.rounded_rectangle([x0, y + 4, x0 + lw - 10, y + rh - 4], radius=14, fill=TERRA if row_active else (WHITE if not row_dim else SOFT))
        draw_text(d, (x0 + 16, y + 16), crit, font(26, bold=True), WHITE if row_active else (TEAL if not row_dim else MUTED), lw - 40, 1.15)
        for j, (name, who, col) in enumerate(SCHOOLS):
            x = x0 + lw + j * cw
            filled = j < cols_filled
            col_dim = active_col is not None and j != active_col
            cell_bg = WHITE
            if filled and (row_active or j == active_col): cell_bg = tint(col, 0.14)
            d.rounded_rectangle([x + 4, y + 4, x + cw - 4, y + rh - 4], radius=14, fill=cell_bg, outline=SAND_DARK if filled else GREY, width=2)
            if filled:
                txt_col = INK
                if col_dim or row_dim: txt_col = (150, 158, 160)
                draw_text(d, (x + 16, y + 9), CELLS[i][j], font(24), txt_col, cw - 32, 1.13)
    footer(d, False, badge)
    return img

# ---------------- spotlight ----------------
def s_spotlight(idx, era, facts, idea):
    name, who, col = SCHOOLS[idx]
    img, d = base(True)
    d.rectangle([0, 0, 18, H], fill=col)
    d.text((110, 90), f"COLUMN {idx + 1} OF 4", font=font(24, bold=True), fill=SAND_DARK)
    d.text((110, 130), name, font=font(96, bold=True), fill=SAND)
    d.text((110, 250), who, font=font(40), fill=SAND_DARK)
    draw_text(d, (110, 310), era, font(28), SAND_DARK, 860, 1.25)
    y = 400
    for f_ in facts:
        d.rounded_rectangle([110, y + 14, 126, y + 30], radius=4, fill=col if col != TEAL else TERRA)
        y = draw_text(d, (150, y), f_, font(30), CREAM, 760, 1.3) + 22
    # big idea card
    d.rounded_rectangle([1020, 220, 1810, 880], radius=28, fill=col)
    d.text((1070, 260), "THE BIG IDEA", font=font(24, bold=True), fill=WHITE)
    draw_text(d, (1070, 320), idea, font(44, bold=True), WHITE, 690, 1.25)
    footer(d, True, f"Column {idx + 1} of 4")
    return img

# ---------------- 2x2 map ----------------
def s_axes(show=4):
    img, d = base(False)
    heading(d, "A two-by-two map of the schools", size=50)
    cx, cy, hw, hh = 960, 600, 560, 300
    d.rectangle([cx - hw, cy - hh, cx + hw, cy + hh], fill=WHITE, outline=SAND_DARK, width=3)
    d.line([(cx - hw, cy), (cx + hw, cy)], fill=MUTED, width=3); d.line([(cx, cy - hh), (cx, cy + hh)], fill=MUTED, width=3)
    f = font(28, bold=True)
    d.text((cx - hw + 20, cy - hh - 44), "◀ looks to the PAST", font=f, fill=MUTED)
    t = "looks to the PRESENT ▶"; d.text((cx + hw - 20 - d.textlength(t, font=f), cy - hh - 44), t, font=f, fill=MUTED)
    d.text((cx - hw - 300, cy - hh + 10), "INSIGHT &\nEXPERIENCE ▲", font=f, fill=MUTED)
    d.text((cx - hw - 300, cy + hh - 70), "ACTION &\nDIRECTION ▼", font=f, fill=MUTED)
    pos = [(cx - 330, cy - 160, "past · insight"), (cx + 240, cy + 90, "present · action — in the room"),
           (cx + 300, cy + 220, "present · action — between sessions"), (cx + 150, cy - 190, "present · experience")]
    for j, (name, who, col) in enumerate(SCHOOLS[:show]):
        x, y, sub = pos[j]
        d.rounded_rectangle([x - 150, y - 36, x + 150, y + 36], radius=36, fill=col)
        d.text((x - d.textlength(name, font=font(32, bold=True)) / 2, y - 20), name, font=font(32, bold=True), fill=WHITE)
        d.text((x - d.textlength(sub, font=font(22)) / 2, y + 44), sub, font=font(22), fill=MUTED)
    footer(d, False)
    return img

# ---------------- four doors ----------------
DOORS = [
    ("Bowen", "Parents, perhaps without the children. A genogram on the wall. “How did your own father handle it when work dried up? Who gets anxious first — and who gets the phone call?” Calm, curious, no instructions; refusing to join the triangles."),
    ("Structural", "Everyone in the room. Who sits where: Tunde beside mother, father nearest the door. Join each person; then ask the parents to decide between themselves what happens about school tomorrow. When Tunde interrupts — gently block him."),
    ("Strategic", "A precise description: days missed, what happens at 7 a.m., step by step. “What have you tried?” Pleading, shouting, the pastor, the phone — all more of the same. Directive: this week father, and only father, wakes Tunde and walks him to the gate."),
    ("Experiential", "Satir: “Tunde, place each person in the room as you experience them.” He puts his father facing the door. Whitaker, half-joking: “What would happen if nobody in this house ever went to work or school again?” — and watches who laughs."),
]
def s_doors(active=None):
    img, d = base(False)
    heading(d, "The same family, four doors", size=50)
    for j, (name, body) in enumerate(DOORS):
        col = SCHOOLS[j][2]
        x = 110 + j * 430
        on = active is None or active == j
        d.rounded_rectangle([x, 230, x + 400, 930], radius=26, fill=WHITE if on else SOFT, outline=col if on else GREY, width=5 if active == j else 3)
        d.rounded_rectangle([x, 230, x + 400, 300], radius=26, fill=col if on else GREY)
        d.rectangle([x, 270, x + 400, 300], fill=col if on else GREY)
        d.text((x + 24, 244), f"Door {j + 1} · {name}", font=font(30, bold=True), fill=WHITE)
        draw_text(d, (x + 24, 330), body, font(28), INK if on else MUTED, 352, 1.32)
    footer(d, False)
    return img

# ---------------- choose when ----------------
def s_choose():
    img, d = base(False)
    heading(d, "Lean toward … when …", size=50)
    whens = [["the pattern is clearly multigenerational", "one adult is motivated and the family will not attend", "the issue is cutoff from a family of origin"],
             ["the presenting problem is a child or adolescent", "hierarchy and boundaries are visibly confused", "the family is chaotic and needs organization"],
             ["there is one clear, specific symptom", "the family wants brief work", "every sensible piece of advice has already failed"],
             ["the family is emotionally frozen or over-rational", "grief is unspoken", "the words are fine and the feeling is absent"]]
    for j, (name, who, col) in enumerate(SCHOOLS):
        x = 110 + j * 430
        d.rounded_rectangle([x, 230, x + 400, 840], radius=26, fill=WHITE, outline=col, width=3)
        d.rounded_rectangle([x, 230, x + 400, 300], radius=26, fill=col); d.rectangle([x, 270, x + 400, 300], fill=col)
        d.text((x + 24, 244), name, font=font(32, bold=True), fill=WHITE)
        y = 330
        for w_ in whens[j]:
            d.ellipse([x + 24, y + 10, x + 40, y + 26], fill=col)
            y = draw_text(d, (x + 56, y), w_, font(27), INK, 320, 1.3) + 26
    draw_text(d, (110, 870), "Most experienced therapists are integrative: one home model, deliberate borrowing. The danger is borrowing without knowing why.", font(30, bold=True), TEAL, 1700, 1.3)
    footer(d, False)
    return img

def s_four_lines(title, lines, dark=False):
    img, d = base(dark)
    y = heading(d, title, dark)
    for j, ((name, who, col), body) in enumerate(zip(SCHOOLS, lines)):
        yy = y + 20 + j * 165
        d.rounded_rectangle([110, yy, 400, yy + 64], radius=32, fill=col)
        d.text((140, yy + 14), name, font=font(32, bold=True), fill=WHITE)
        draw_text(d, (440, yy + 4), body, font(32), SAND if dark else INK, 1360, 1.28)
    footer(d, dark)
    return img

# ---------------- deck ----------------
def deck():
    D = []
    D.append(("01-welcome-criteria.mp3", [
        (1.3, E.s_title("The Major Schools", "Week 6 — Bowen · Structural · Strategic · Experiential\nA compare-and-contrast lecture", "MFT 701 · Master of Marriage and Family Therapy")),
        (1.8, E.s_bullets("Learning Objectives", ["Compare the four classic schools on five criteria.", "Describe how each would open a first session with the same family.", "Explain what they share and where they genuinely differ.", "Begin to identify which fits a given family — and which fits you."], nums=True, intro="By the end of this lecture you will be able to…")),
        (2.6, s_grid(0, title="The comparison grid — four schools, five criteria")),
        (1.2, E.s_statement("Grids flatten.", "Every school is richer than four cells of text — each gets a full lecture in MFT 702. Today's purpose is contrast.")),
    ]))
    D.append(("02-bowen.mp3", [
        (1.6, s_spotlight(0, "Psychiatrist · NIMH family study 1954–59 · Georgetown Family Center", ["Admitted whole families to research wards to study schizophrenia in context", "Family Therapy in Clinical Practice (1978)", "Less a set of techniques than a theory of human emotional functioning"], "Anxiety travels through triangles and down the generations. Raise differentiation in one person, and the system calms.")),
        (4.0, s_grid(1, active_col=0, title="Column 1 — Bowen Family Systems", badge="Column 1 of 4")),
    ]))
    D.append(("03-structural.mp3", [
        (1.5, s_spotlight(1, "Child psychiatrist · Wiltwyck School · Philadelphia Child Guidance Clinic", ["Built with poor, multi-problem families in New York and Philadelphia", "Families and Family Therapy (1974)", "Insight-oriented talk had not helped; action in the room did"], "Symptoms come from a structure that has failed to adapt. Restructure the family and the symptom fades.")),
        (4.0, s_grid(2, active_col=1, title="Column 2 — Structural Family Therapy", badge="Column 2 of 4")),
    ]))
    D.append(("04-strategic.mp3", [
        (1.7, s_spotlight(2, "Haley & Madanes (Washington) · MRI Brief Therapy Center (Palo Alto) · Milan team", ["Roots in Bateson's project and the hypnotherapist Milton Erickson", "Watzlawick, Weakland & Fisch, Change (1974)", "People can be moved to change without understanding why"], "The problem is the problem — kept alive by the attempted solution. Interrupt the sequence.")),
        (4.0, s_grid(3, active_col=2, title="Column 3 — Strategic Family Therapy", badge="Column 3 of 4")),
    ]))
    D.append(("05-experiential.mp3", [
        (1.6, s_spotlight(3, "Humanistic movement of the 1960s · two very different founders", ["Virginia Satir — Conjoint Family Therapy (1964), Peoplemaking (1972)", "Carl Whitaker — symbolic-experiential therapy, 'the psychotherapy of the absurd'", "Satir's stances: placating · blaming · super-reasonable · irrelevant · congruent"], "Families suffer from feelings they are not allowed to have. Growth comes through experience in the room.")),
        (4.0, s_grid(4, active_col=3, title="Column 4 — Experiential Family Therapy", badge="Column 4 of 4")),
    ]))
    D.append(("06-across-the-rows.mp3", [
        (1.4, s_grid(4, active_row=0, title="Reading across the rows")),
        (1.2, s_grid(4, active_row=1, title="Reading across the rows")),
        (1.3, s_grid(4, active_row=2, title="Reading across the rows")),
        (0.8, s_grid(4, active_row=3, title="Reading across the rows")),
        (0.7, s_grid(4, active_row=4, title="Reading across the rows")),
        (2.4, s_axes()),
    ]))
    D.append(("07-four-doors.mp3", [(0.4, s_doors(None)), (1.6, s_doors(0)), (1.8, s_doors(1)), (1.9, s_doors(2)), (1.6, s_doors(3)), (0.5, s_doors(None))]))
    D.append(("08-shared-and-choosing.mp3", [
        (1.6, E.s_bullets("What the four share", ["The problem is in the pattern, not the person.", "All work with what is happening now — even Bowen reads the past to change the present.", "The therapist is active; none is a blank screen.", "A small change in one part can move the whole."], nums=True)),
        (3.6, s_choose()),
    ]))
    D.append(("09-critiques-reflection.mp3", [
        (2.4, s_four_lines("Fair criticisms", ["'Differentiation' can sound like a Western ideal of the autonomous individual — translate it, do not import it.", "A normative family ideal; hierarchy restored by restoring fathers (Hare-Mustin, 1978).", "Paradoxical directives raised questions of manipulation and informed consent; the field moved toward transparency.", "Depended on the charisma of its founders — hard to teach, harder to research."])),
        (2.4, s_four_lines("A brief reflection", ["Exodus 20 & 34 — consequences to the third and fourth generation; steadfast love to a thousand. Transmission, and its reversal.", "The Pastoral Epistles — order in the household as a mark of care.", "Proverbs — wisdom is what works; pragmatism in the service of the vulnerable.", "Psalm 51:6 — truth in the inner being; levelling as truth spoken with love."], dark=True)),
    ]))
    D.append(("10-summary-close.mp3", [
        (2.4, s_grid(4, title="The grid, complete", badge="Summary")),
        (2.2, E.s_bullets("Review Questions", ["For each school, write one sentence on its view of the problem — and show how that view predicts its main technique.", "Describe how a Structural and a Strategic therapist would each open a first session with the Adebayos, and name the key difference.", "Which school's therapist role feels most natural to you — and what does that say about your strengths and blind spots?"], nums=True, intro="Pause the video and write your answers.")),
        (2.2, E.s_cards("Looking Ahead", [("Next Week", "The postmodern schools — Solution-Focused, Narrative and Collaborative therapy — compared on the same five criteria."), ("Assignment — two pages", "Take the family you have been mapping. Choose two of today's four schools; describe how each would understand the problem and open the work. Close with a paragraph on which you would choose, and why.")], dark=True)),
        (0.7, E.s_title("Thank you.", "End of Week 6\nFour doors, one family — see you next week.", "MFT 701 · Week 6")),
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
