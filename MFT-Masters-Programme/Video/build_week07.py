#!/usr/bin/env python3
"""
MFT 701 Week 7 — The Postmodern Schools (Compare & Contrast, continued).
Same grid as Week 6 with three new columns, a ghost 'Classic' column and a sixth row
("Who is the expert?"); the 2x2 map gains a third axis; three doors for the Adebayos.
Usage: python3 build_week07.py
"""
import os, subprocess
from PIL import Image, ImageDraw
from mutagen.mp3 import MP3
import imageio_ffmpeg
import build_video as E
import build_week06 as G
from build_video import (W, H, TEAL, TEAL_DARK, TEAL_LIGHT, SAND, SAND_DARK, TERRA, CREAM, INK, MUTED, WHITE,
                         font, draw_text, text_height, footer, heading, base)
from build_week06 import PLUM, GREEN, GREY, SOFT, tint

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "..", "Audio", "MFT-701-W07")
SLIDES = os.path.join(HERE, "slides-w07")
OUT = os.path.join(HERE, "MFT-701-Week-07-Lecture.mp4")
os.makedirs(SLIDES, exist_ok=True)

GOLD = (168, 118, 34)
SCHOOLS = [
    ("Solution-Focused", "de Shazer · Berg", GOLD),
    ("Narrative", "White · Epston", PLUM),
    ("Collaborative", "Anderson · Goolishian", GREEN),
    ("Classic schools", "Week 6 — for contrast", (120, 130, 134)),
]
G.SCHOOLS = SCHOOLS  # so G.s_spotlight picks up this week's schools

def s_spotlight(idx, era, facts, idea):
    name, who, col = SCHOOLS[idx]
    img, d = base(True)
    d.rectangle([0, 0, 18, H], fill=col)
    d.text((110, 90), f"COLUMN {idx + 1} OF 3", font=font(24, bold=True), fill=SAND_DARK)
    d.text((110, 130), name, font=font(96, bold=True), fill=SAND)
    d.text((110, 250), who, font=font(40), fill=SAND_DARK)
    draw_text(d, (110, 310), era, font(28), SAND_DARK, 860, 1.25)
    y = 400
    for f_ in facts:
        d.rounded_rectangle([110, y + 14, 126, y + 30], radius=4, fill=TERRA)
        y = draw_text(d, (150, y), f_, font(30), CREAM, 760, 1.3) + 22
    d.rounded_rectangle([1020, 220, 1810, 880], radius=28, fill=col)
    d.text((1070, 260), "THE BIG IDEA", font=font(24, bold=True), fill=WHITE)
    draw_text(d, (1070, 320), idea, font(44, bold=True), WHITE, 690, 1.25)
    footer(d, True, f"Column {idx + 1} of 3")
    return img
CRITERIA = ["View of the problem", "Goal of therapy", "Therapist's role", "Signature techniques", "Time and pace", "Who is the expert?"]
CELLS = [
    ["Need not be understood; solution talk moves; exceptions exist",
     "A problem-saturated story crowds out other stories; propped up by culture",
     "Problems exist in language; a system organized around a problem",
     "An anxious, misstructured or stuck system"],
    ["A small, client-defined goal: a described future and a first step",
     "Re-authoring: a preferred story thick enough to live in",
     "New meaning in conversation, until the problem dissolves",
     "A restructured, differentiated or solved system"],
    ["Leading from one step behind; curious, respectful of competence",
     "De-centred but influential co-editor; transparent; awake to power",
     "Not-knowing conversational partner; present with, not acting on",
     "Coach · director · strategist · present self"],
    ["Miracle question · exceptions · scaling · coping · do more of what works",
     "Externalizing · relative influence · unique outcomes · letters",
     "Dialogue · questions from inside the story · reflecting team",
     "Genogram · enactment · directives · sculpting"],
    ["Brief by design (3–6 sessions) · future-focused",
     "The past re-read · moderate length",
     "Present · open-ended · unhurried",
     "Multigenerational to brief; present-focused"],
    ["The client, on life and goals; therapist on useful questions",
     "The person, on their life; therapist on the craft of conversation",
     "Shared — responsible for the dialogue, not its outcome",
     "The therapist, on patterns and structure"],
]

def s_grid(cols_filled=0, active_col=None, active_row=None, title="The comparison grid", badge=None, show_classic=True):
    img, d = base(False)
    heading(d, title, size=48)
    x0, y0, lw, hh = 110, 205, 250, 92
    cw = (W - 2 * x0 - lw) // 4
    rows = len(CRITERIA); rh = (H - 125 - y0 - hh) // rows
    for j, (name, who, col) in enumerate(SCHOOLS):
        x = x0 + lw + j * cw
        ghost = j == 3
        filled = (j < cols_filled) or (ghost and show_classic)
        dim = (active_col is not None and j != active_col) or ghost
        bg = col if filled else GREY
        if filled and dim: bg = tint(col, 0.45)
        d.rounded_rectangle([x + 4, y0, x + cw - 4, y0 + hh - 6], radius=16, fill=bg)
        d.text((x + 18, y0 + 12), name, font=font(31, bold=True), fill=WHITE)
        d.text((x + 18, y0 + 54), who, font=font(21), fill=WHITE)
    for i, crit in enumerate(CRITERIA):
        y = y0 + hh + i * rh
        row_active = active_row == i
        row_dim = active_row is not None and not row_active
        new_row = i == 5
        lab_bg = TERRA if row_active else (WHITE if not row_dim else SOFT)
        if new_row and not row_active: lab_bg = tint(TERRA, 0.18) if not row_dim else SOFT
        d.rounded_rectangle([x0, y + 4, x0 + lw - 10, y + rh - 4], radius=14, fill=lab_bg)
        draw_text(d, (x0 + 16, y + 12), crit, font(25, bold=True), WHITE if row_active else (TERRA if new_row and not row_dim else (TEAL if not row_dim else MUTED)), lw - 40, 1.12)
        for j, (name, who, col) in enumerate(SCHOOLS):
            x = x0 + lw + j * cw
            ghost = j == 3
            filled = (j < cols_filled) or (ghost and show_classic)
            col_dim = (active_col is not None and j != active_col) or ghost
            cell_bg = WHITE
            if filled and (row_active or j == active_col): cell_bg = tint(col, 0.14)
            if ghost: cell_bg = SOFT if not row_active else tint(col, 0.14)
            d.rounded_rectangle([x + 4, y + 4, x + cw - 4, y + rh - 4], radius=14, fill=cell_bg, outline=SAND_DARK if filled else GREY, width=2)
            if filled:
                txt_col = INK
                if (col_dim and not row_active) or row_dim: txt_col = (150, 158, 160)
                if ghost and row_active: txt_col = (90, 100, 104)
                draw_text(d, (x + 14, y + 8), CELLS[i][j], font(22), txt_col, cw - 28, 1.12)
    footer(d, False, badge)
    return img

def s_turn():
    img, d = base(True)
    heading(d, "The postmodern turn (1980s–90s)", dark=True)
    shifts = [("cybernetics", "language", "Social constructionism: the realities we live in are built in conversation."),
              ("observing the system", "part of the system", "Second-order cybernetics: the therapist is inside the system being created in the room."),
              ("therapist as expert", "client as expert", "Anderson & Goolishian: the system is organized around a problem in language. Dissolve the problem, and the system dissolves.")]
    for i, (a, b, body) in enumerate(shifts):
        y = 260 + i * 220
        d.rounded_rectangle([110, y, 1810, y + 180], radius=24, fill=TEAL_DARK, outline=TEAL_LIGHT, width=3)
        d.text((150, y + 30), "from", font=font(24), fill=SAND_DARK); d.text((150, y + 62), a, font=font(40, bold=True), fill=SAND)
        d.polygon([(720, y + 70), (720, y + 110), (770, y + 90)], fill=TERRA)
        d.text((810, y + 30), "to", font=font(24), fill=SAND_DARK); d.text((810, y + 64), b, font=font(36, bold=True), fill=TERRA)
        draw_text(d, (1260, y + 30), body, font(28), CREAM, 510, 1.3)
    footer(d, True)
    return img

def s_axes7(third=False):
    img, d = base(False)
    heading(d, "The map — and the axis it was missing" if third else "The map, with the postmodern schools added", size=50)
    cx, cy, hw, hh = (720 if third else 960), 600, (500 if third else 560), 290
    d.rectangle([cx - hw, cy - hh, cx + hw, cy + hh], fill=WHITE, outline=SAND_DARK, width=3)
    d.line([(cx - hw, cy), (cx + hw, cy)], fill=MUTED, width=3); d.line([(cx, cy - hh), (cx, cy + hh)], fill=MUTED, width=3)
    f = font(26, bold=True)
    d.text((cx - hw + 16, cy - hh - 40), "◀ PAST", font=f, fill=MUTED)
    t = "PRESENT / FUTURE ▶"; d.text((cx + hw - 16 - d.textlength(t, font=f), cy - hh - 40), t, font=f, fill=MUTED)
    d.text((cx - hw - 190, cy - hh + 6), "MEANING ▲", font=f, fill=MUTED)
    d.text((cx - hw - 190, cy + hh - 40), "ACTION ▼", font=f, fill=MUTED)
    pills = [("Bowen", TEAL, cx - 300, cy - 150, False), ("Experiential", GREEN, cx + 120, cy - 190, False),
             ("Structural", TERRA, cx + 150, cy + 90, False), ("Strategic", PLUM, cx + 330, cy + 220, False),
             ("Solution-Focused", GOLD, cx + 330, cy - 40, True), ("Narrative", PLUM, cx + 60, cy - 60, True), ("Collaborative", GREEN, cx + 340, cy - 230, True)]
    for name, col, x, y, pm in pills:
        fnt = font(26, bold=True); tw = d.textlength(name, font=fnt) + 50
        if pm:
            d.rounded_rectangle([x - tw / 2, y - 26, x + tw / 2, y + 26], radius=26, fill=WHITE, outline=col, width=4)
            d.text((x - tw / 2 + 25, y - 15), name, font=fnt, fill=col)
        else:
            d.rounded_rectangle([x - tw / 2, y - 26, x + tw / 2, y + 26], radius=26, fill=tint(col, 0.75 if not third else 0.5))
            d.text((x - tw / 2 + 25, y - 15), name, font=fnt, fill=WHITE)
    d.text((cx - hw, cy + hh + 20), "filled = classic (Week 6)   ·   outlined = postmodern (Week 7)", font=font(24), fill=MUTED)
    if third:
        ax = 1560
        d.line([(ax, 300), (ax, 900)], fill=TERRA, width=6)
        d.polygon([(ax - 16, 320), (ax + 16, 320), (ax, 290)], fill=TERRA); d.polygon([(ax - 16, 880), (ax + 16, 880), (ax, 910)], fill=TERRA)
        d.text((ax - 120, 240), "THE THIRD AXIS", font=font(24, bold=True), fill=TERRA)
        d.text((ax + 30, 330), "EXPERT", font=font(28, bold=True), fill=INK)
        d.text((ax + 30, 840), "NOT-KNOWING", font=font(28, bold=True), fill=INK)
        for k, (n, c) in enumerate([("Bowen", TEAL), ("Structural", TERRA), ("Strategic", PLUM), ("Experiential", GREEN)]):
            y = 390 + k * 46; d.rounded_rectangle([ax - 180, y, ax - 20, y + 36], radius=18, fill=c); d.text((ax - 168, y + 6), n, font=font(22, bold=True), fill=WHITE)
        for k, (n, c) in enumerate([("Solution-Focused", GOLD), ("Narrative", PLUM), ("Collaborative", GREEN)]):
            y = 690 + k * 46; d.rounded_rectangle([ax - 220, y, ax - 20, y + 36], radius=18, fill=WHITE, outline=c, width=3); d.text((ax - 208, y + 6), n, font=font(22, bold=True), fill=c)
    footer(d, False)
    return img

DOORS = [
    ("Solution-Focused", "The miracle question — to everyone, including Bisi. “Tomorrow Tunde would get up without a fight.” “Has there been any morning, even one, a little like that?” The Tuesday his father drove him. Scaling: where are we today, out of ten — and what would one point higher look like? Compliments, and a task: notice what is already working."),
    ("Narrative", "“What would you call the thing that keeps you home?” — “the Heaviness.” How long has it been around? Before or after Father's job ended? Does it visit anyone else in the house? — and the father is nodding. How much of the week does the Heaviness run, and when has Tunde outwitted it? A letter follows, documenting the morning the Heaviness lost."),
    ("Collaborative", "No agenda, no intake form. “Where would you like to begin?” The therapist asks only from inside what each person says and resists forming a hypothesis. Slowly the conversation moves from Tunde's school to the morning Mr. Adebayo was told not to come back. A reflecting team speaks about what moved them — and the family listens to themselves being heard."),
]
def s_doors(active=None):
    img, d = base(False)
    heading(d, "The same family, three doors", size=50)
    for j, (name, body) in enumerate(DOORS):
        col = SCHOOLS[j][2]; x = 110 + j * 580
        on = active is None or active == j
        d.rounded_rectangle([x, 230, x + 540, 930], radius=26, fill=WHITE if on else SOFT, outline=col if on else GREY, width=5 if active == j else 3)
        d.rounded_rectangle([x, 230, x + 540, 300], radius=26, fill=col if on else GREY); d.rectangle([x, 270, x + 540, 300], fill=col if on else GREY)
        d.text((x + 24, 244), f"Door {j + 1} · {name}", font=font(30, bold=True), fill=WHITE)
        draw_text(d, (x + 28, 330), body, font(29), INK if on else MUTED, 484, 1.32)
    footer(d, False)
    return img

def s_from_to():
    img, d = base(False)
    heading(d, "Classic → Postmodern: what changed", size=50)
    pairs = [("system", "story"), ("pattern", "meaning"), ("therapist as expert", "therapist as collaborator"), ("homeostasis", "possibility"), ("what is wrong", "what is strong")]
    for i, (a, b) in enumerate(pairs):
        y = 240 + i * 118
        d.rounded_rectangle([110, y, 840, y + 90], radius=20, fill=WHITE, outline=SAND_DARK, width=3)
        d.text((150, y + 24), a, font=font(38, bold=True), fill=MUTED)
        d.polygon([(900, y + 25), (900, y + 65), (960, y + 45)], fill=TERRA)
        d.rounded_rectangle([1010, y, 1810, y + 90], radius=20, fill=TEAL)
        d.text((1050, y + 24), b, font=font(38, bold=True), fill=SAND)
    draw_text(d, (110, 850), "What stayed: the problem is relational · present-focused and brief · nobody is blamed · the therapist is active — asking is as active as directing.", font(30, bold=True), TEAL, 1700, 1.3)
    footer(d, False)
    return img

def s_choose():
    img, d = base(False)
    heading(d, "Lean toward … when …", size=50)
    whens = [["the family wants brief, goal-oriented work", "clients are mandated or reluctant — treat them as competent", "schools and agencies with few sessions", "problem talk is spiralling and needs interrupting", "— strongest research base of the three"],
             ["the problem has become an identity: “I am a failure”", "shame is heavy", "cultural or religious discourse is doing damage", "working with children — externalizing comes naturally"],
             ["the stuck system includes professionals — school, services, church", "the hierarchy of expertise is itself the obstacle", "consultation and organizational work"]]
    for j in range(3):
        name, who, col = SCHOOLS[j]; x = 110 + j * 580
        d.rounded_rectangle([x, 220, x + 540, 800], radius=26, fill=WHITE, outline=col, width=3)
        d.rounded_rectangle([x, 220, x + 540, 290], radius=26, fill=col); d.rectangle([x, 260, x + 540, 290], fill=col)
        d.text((x + 24, 234), name, font=font(32, bold=True), fill=WHITE)
        y = 320
        for w_ in whens[j]:
            d.ellipse([x + 24, y + 10, x + 40, y + 26], fill=col)
            y = draw_text(d, (x + 56, y), w_, font(27), INK, 460, 1.3) + 22
    d.rounded_rectangle([110, 830, 1810, 920], radius=20, fill=tint(TERRA, 0.15), outline=TERRA, width=3)
    draw_text(d, (140, 850), "Boundary: where safety is at stake — violence, abuse, suicide risk — the therapist's expertise does not dissolve. Humility is about meaning, not duty of care.", font(28, bold=True), TERRA, 1640, 1.25)
    footer(d, False)
    return img

def deck():
    D = []
    D.append(("01-welcome-turn.mp3", [
        (1.2, E.s_title("The Postmodern Schools", "Week 7 — Solution-Focused · Narrative · Collaborative\nCompare and contrast, continued", "MFT 701 · Master of Marriage and Family Therapy")),
        (1.3, E.s_bullets("Learning Objectives", ["Explain the postmodern turn in family therapy.", "Compare the three schools on five criteria — plus one new one.", "Describe how each would open a first session with the Adebayos.", "Weigh their strengths and their critics fairly."], nums=True, intro="By the end of this lecture you will be able to…")),
        (3.0, s_turn()),
        (1.0, s_grid(0, title="The grid again — three new columns, one new row")),
    ]))
    D.append(("02-solution-focused.mp3", [
        (1.3, s_spotlight(0, "Brief Family Therapy Center, Milwaukee (1978) · out of the MRI tradition", ["Keys to Solution in Brief Therapy (1985)", "Ask about the times the problem does not happen", "Insoo Kim Berg: 'leading from one step behind'"], "You do not need to understand the problem to build the solution. Find the exceptions and do more of them.")),
        (4.2, s_grid(1, active_col=0, title="Column 1 — Solution-Focused Brief Therapy", badge="Column 1 of 3")),
    ]))
    D.append(("03-narrative.mp3", [
        (1.3, s_spotlight(1, "Dulwich Centre, Adelaide · Auckland · Narrative Means to Therapeutic Ends (1990)", ["Influences: Michel Foucault, Jerome Bruner", "Problem-saturated dominant stories, propped up by culture", "'The person is not the problem; the problem is the problem'"], "Lives are storied. Re-author the story — with enough evidence and witnesses to live in it.")),
        (4.2, s_grid(2, active_col=1, title="Column 2 — Narrative Therapy", badge="Column 2 of 3")),
    ]))
    D.append(("04-collaborative.mp3", [
        (1.3, s_spotlight(2, "Houston Galveston Institute · Conversation, Language, and Possibilities (1997)", ["Close kin: Tom Andersen's reflecting team (Tromsø, 1985)", "'Problem-organizing, problem-dissolving systems'", "The not-knowing stance"], "Problems exist in language. Host a conversation in which they dissolve.")),
        (4.2, s_grid(3, active_col=2, title="Column 3 — Collaborative Therapy", badge="Column 3 of 3")),
    ]))
    D.append(("05-across-and-map.mp3", [
        (1.0, s_grid(3, active_row=0, title="Reading across — against the classic column")),
        (0.8, s_grid(3, active_row=1, title="Reading across — against the classic column")),
        (0.8, s_grid(3, active_row=2, title="Reading across — against the classic column")),
        (0.8, s_grid(3, active_row=3, title="Reading across — against the classic column")),
        (0.6, s_grid(3, active_row=4, title="Reading across — against the classic column")),
        (1.0, s_grid(3, active_row=5, title="The new row — who is the expert?")),
        (1.4, s_axes7(False)),
        (1.4, s_axes7(True)),
    ]))
    D.append(("06-three-doors.mp3", [(2.0, s_doors(0)), (2.2, s_doors(1)), (2.0, s_doors(2)), (0.5, s_doors(None))]))
    D.append(("07-changed-stayed-choose.mp3", [(2.2, s_from_to()), (4.0, s_choose())]))
    D.append(("08-criticisms.mp3", [
        (3.0, E.s_bullets("Fair criticisms", ["Minuchin (1998): “Where is the family in narrative family therapy?” — the family as a living unit lost; the therapist off the hook for change.", "Relativism — is a story of abuse just one story among others? Construction stops where harm begins.", "Solution-Focused — the risk of superficiality: skipping grief and trauma on the way to a goal.", "Not-knowing can hide power rather than remove it — name your influence.", "Evidence — SFBT has a respectable literature; Narrative and Collaborative far less. A philosophical choice with a practical cost."], nums=True)),
    ]))
    D.append(("09-reflection.mp3", [
        (3.0, E.s_cards("A brief reflection: story, hope and truth", [("The gift", "Scripture is a re-authoring story — “if anyone is in Christ, there is a new creation.” Hope — “whatever is true… think on these things.” Dialogue — “come, let us reason together.”"), ("The question", "Postmodernism: all stories are constructed. Faith: some stories are true. Hold the therapist's humility without surrendering the conviction that some stories — “this child is worthless” — are simply false.")], dark=True)),
        (1.0, E.s_statement("The not-knowing stance is a discipline of listening, not a doctrine of relativism.", "Practise the discipline. Keep the conviction.")),
    ]))
    D.append(("10-summary-close.mp3", [
        (2.2, s_grid(3, title="The grid, complete", badge="Summary")),
        (2.2, E.s_bullets("Review Questions", ["State the three shifts of the postmodern turn, with one practical consequence of each for a first session.", "Write the miracle question as you would actually ask it — then an externalizing question about the same problem. What differs?", "Summarize Minuchin's 1998 critique, and give one way a narrative therapist might answer it."], nums=True, intro="Pause the video and write your answers.")),
        (2.4, E.s_cards("Looking Ahead", [("Next Week — Mid-term review", "A synthesis of Weeks 1–7: mapping the field so far. Bring your questions."), ("Assignment — three parts", "For the family you have been mapping: (1) the miracle question as you would ask it, with a plausible answer; (2) an externalized name for the problem and three relative-influence questions; (3) 150 words on what a not-knowing stance would change about your first ten minutes.")], dark=True)),
        (0.7, E.s_title("Thank you.", "End of Week 7\nThe person is not the problem — see you next week.", "MFT 701 · Week 7")),
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
