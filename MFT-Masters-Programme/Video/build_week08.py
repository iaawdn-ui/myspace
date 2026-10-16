#!/usr/bin/env python3
"""
MFT 701 Week 8 — Mid-Term Review and Synthesis (Recap & Synthesis style).
Seven weekly nodes around a centre that is filled with the 'one big idea' at the end.
Usage: python3 build_week08.py
"""
import os, math, subprocess
from PIL import Image, ImageDraw
from mutagen.mp3 import MP3
import imageio_ffmpeg
import build_video as E
from build_video import (W, H, TEAL, TEAL_DARK, TEAL_LIGHT, SAND, SAND_DARK, TERRA, CREAM, INK, MUTED, WHITE,
                         font, draw_text, text_height, footer, heading, base)
from build_week06 import PLUM, GREEN, GREY, SOFT, tint

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "..", "Audio", "MFT-701-W08")
SLIDES = os.path.join(HERE, "slides-w08")
OUT = os.path.join(HERE, "MFT-701-Week-08-Lecture.mp4")
os.makedirs(SLIDES, exist_ok=True)

NODES = [("1", "What MFT is"), ("2", "History"), ("3", "The paradigm shift"), ("4", "Core concepts I — dynamics"),
         ("5", "Core concepts II — structure"), ("6", "Classic schools"), ("7", "Postmodern schools")]
BIG = "The problem lives between people — and so does the solution."

def node_pos():
    cx, cy = 960, 590
    return [(cx + 620 * math.cos(-math.pi / 2 + i * 2 * math.pi / 7), cy + 292 * math.sin(-math.pi / 2 + i * 2 * math.pi / 7)) for i in range(7)]

def s_map(active=(), lit=(), centre=False, title="The map of the field so far", badge=None, bracket=None):
    img, d = base(True)
    heading(d, title, dark=True)
    cx, cy = 960, 590
    pts = node_pos()
    for i, (x, y) in enumerate(pts):
        on = i in active or i in lit
        d.line([(cx, cy), (x, y)], fill=TERRA if i in active else (SAND_DARK if on else TEAL_LIGHT), width=6 if i in active else 3)
    if bracket:
        a, b = bracket
        (x1, y1), (x2, y2) = pts[a], pts[b]
        d.line([(x1, y1 + 80), (x2, y2 + 80)], fill=TERRA, width=5)
        d.text(((x1 + x2) / 2 - 70, max(y1, y2) + 86), "the concepts", font=font(22, bold=True), fill=TERRA)
    # centre
    d.ellipse([cx - 250, cy - 105, cx + 250, cy + 105], fill=TERRA if centre else TEAL_DARK, outline=TERRA, width=5)
    if centre:
        draw_text(d, (cx - 225, cy - 62), BIG, font(30, bold=True), WHITE, 450, 1.2, align="center")
    else:
        d.text((cx - d.textlength("?", font=font(90, bold=True)) / 2, cy - 62), "?", font=font(90, bold=True), fill=TERRA)
        d.text((cx - d.textlength("the one big idea", font=font(22)) / 2, cy + 40), "the one big idea", font=font(22), fill=SAND_DARK)
    for i, (x, y) in enumerate(pts):
        act = i in active; on = act or i in lit
        fill = SAND if on else TEAL_DARK
        d.ellipse([x - 150, y - 66, x + 150, y + 66], fill=fill, outline=TERRA if act else (SAND_DARK if on else TEAL_LIGHT), width=6 if act else 4)
        d.ellipse([x - 150 + 14, y - 66 + 14, x - 150 + 52, y - 66 + 52], fill=TERRA if on else TEAL_LIGHT)
        d.text((x - 150 + 33 - d.textlength(NODES[i][0], font=font(22, bold=True)) / 2, y - 66 + 21), NODES[i][0], font=font(22, bold=True), fill=WHITE)
        f = font(26, bold=True)
        th = text_height(d, NODES[i][1], f, 220, 1.1)
        draw_text(d, (x - 110 + 10, y - th / 2 + 2), NODES[i][1], f, TEAL if on else SAND_DARK, 220, 1.1, align="center")
    footer(d, True, badge)
    return img

def s_node(i, sentence, terms, relation, title_extra=""):
    num, name = NODES[i]
    img, d = base(False)
    heading(d, f"Node {num} — Week {num}: {name}{title_extra}", size=46)
    d.rounded_rectangle([110, 210, 1810, 370], radius=24, fill=TEAL)
    d.text((150, 232), "THE SENTENCE", font=font(22, bold=True), fill=SAND_DARK)
    draw_text(d, (150, 268), sentence, font(34, bold=True), SAND, 1620, 1.2)
    d.text((110, 410), "KEY TERMS", font=font(22, bold=True), fill=TERRA)
    x, y = 110, 450
    for t in terms:
        f = font(26); tw = d.textlength(t, font=f) + 40
        if x + tw > 1810: x = 110; y += 60
        d.rounded_rectangle([x, y, x + tw, y + 46], radius=23, fill=WHITE, outline=SAND_DARK, width=2)
        d.text((x + 20, y + 9), t, font=f, fill=INK); x += tw + 14
    y += 90
    d.text((110, y), "HOW IT CONNECTS", font=font(22, bold=True), fill=TERRA)
    draw_text(d, (110, y + 40), relation, font(33), INK, 1700, 1.3)
    footer(d, False, f"Node {num} of 7")
    return img

def s_two_nodes(i, j, s1, s2, relation, title):
    img, d = base(False)
    heading(d, title, size=46)
    for k, (idx, s) in enumerate([(i, s1), (j, s2)]):
        x = 110 + k * 870
        d.rounded_rectangle([x, 210, x + 830, 560], radius=24, fill=WHITE, outline=SAND_DARK, width=3)
        d.rounded_rectangle([x, 210, x + 830, 280], radius=24, fill=TEAL); d.rectangle([x, 250, x + 830, 280], fill=TEAL)
        d.text((x + 28, 226), f"Node {NODES[idx][0]} — {NODES[idx][1]}", font=font(30, bold=True), fill=SAND)
        draw_text(d, (x + 28, 310), s, font(31), INK, 774, 1.3)
    d.text((110, 610), "HOW THEY CONNECT", font=font(22, bold=True), fill=TERRA)
    draw_text(d, (110, 650), relation, font(33), INK, 1700, 1.3)
    footer(d, False)
    return img

def s_contradictions(active=None):
    img, d = base(False)
    heading(d, "Five apparent contradictions — resolved", size=48)
    rows = [("homeostasis", "change", "Every living system does both. Therapy changes what the thermostat is set to."),
            ("circular causality", "responsibility", "A tool for patterns, not a theory of morality. Where there is harm, responsibility is named."),
            ("expert", "not-knowing", "Content expertise belongs to the family; process expertise belongs to the therapist."),
            ("structure", "story", "Both are maps; neither is the territory. Use the one that opens doors; hold it as a hypothesis."),
            ("brief", "multigenerational", "It depends on the goal: a solved problem can be brief; a changed self is slow. Say which you offer.")]
    for k, (a, b, res) in enumerate(rows):
        y = 215 + k * 140
        on = active is None or active == k
        col = TERRA if on else GREY
        d.rounded_rectangle([110, y, 440, y + 60], radius=30, fill=TEAL if on else GREY)
        d.text((110 + 165 - d.textlength(a, font=font(26, bold=True)) / 2, y + 15), a, font=font(26, bold=True), fill=WHITE)
        d.text((455, y + 10), "vs", font=font(28, bold=True), fill=col)
        d.rounded_rectangle([510, y, 840, y + 60], radius=30, fill=PLUM if on else GREY)
        d.text((510 + 165 - d.textlength(b, font=font(26, bold=True)) / 2, y + 15), b, font=font(26, bold=True), fill=WHITE)
        d.polygon([(870, y + 15), (870, y + 45), (900, y + 30)], fill=col)
        draw_text(d, (920, y + 2), res, font(27), INK if on else MUTED, 890, 1.25)
    footer(d, False)
    return img

def s_big_idea_thread():
    img, d = base(True)
    heading(d, "One idea, seven weeks", dark=True)
    d.rounded_rectangle([110, 200, 1810, 290], radius=24, fill=TERRA)
    f = font(36, bold=True); d.text((960 - d.textlength(BIG, font=f) / 2, 222), BIG, font=f, fill=WHITE)
    lines = ["a symptom is a signal from a family under strain, not a defect in a boy", "a field was founded when researchers saw that the patient was the relationship",
             "the second coach wins because she treats the passing, not the striker", "we treat the lines between the dots",
             "boundaries, hierarchies and triangles — all of them between people", "four classic schools, each intervening in the space between members",
             "even the story is told between people, in conversation — and changed there"]
    for i, t in enumerate(lines):
        y = 320 + i * 86
        d.ellipse([110, y + 6, 160, y + 56], fill=SAND); d.text((135 - d.textlength(str(i + 1), font=font(26, bold=True)) / 2, y + 16), str(i + 1), font=font(26, bold=True), fill=TEAL)
        d.text((180, y + 2), NODES[i][1], font=font(26, bold=True), fill=SAND_DARK)
        draw_text(d, (560, y + 4), t, font(28), CREAM, 1240, 1.2)
    footer(d, True)
    return img

FORM = [("Presenting problem", "Tunde, 14, has refused school for several weeks; mother requests that he be “fixed.”", "Wk 1"),
        ("System", "Father — unemployed four months, out most evenings · Mother — two jobs, exhausted · Tunde · Bisi, 10, quiet · Grandmother, active by telephone", "Wk 1 · 5"),
        ("Pattern", "Father withdraws → mother over-functions → Tunde acts out → father withdraws further", "Wk 3 · 4"),
        ("Structure", "Diffuse boundary mother–son; rigid boundary around father; Tunde in a coalition with mother against father; Bisi isolated; marital anxiety settled on the mother–son side of the triangle", "Wk 5"),
        ("Hypothesis", "The family reorganized around the job loss; Tunde's symptom keeps the parents in the same room and holds the structure in place — expect symptoms elsewhere if he improves", "Wk 4"),
        ("Story", "A problem-saturated account — “a difficult boy” — competing with unique outcomes: the Tuesday his father drove him to school", "Wk 7"),
        ("First moves", "See the whole family · join the father · an enactment between the parents about tomorrow morning · amplify the exception · name “the Heaviness”", "Wk 6 · 7")]
def s_formulation(upto=7):
    img, d = base(False)
    heading(d, "A one-page formulation — the Adebayos", size=48)
    y = 205
    for i, (lab, body, wk) in enumerate(FORM):
        on = i < upto
        h = 98 if i in (1, 3, 4) else 84
        d.rounded_rectangle([110, y, 1810, y + h], radius=16, fill=WHITE if on else SOFT, outline=SAND_DARK if on else GREY, width=2)
        d.rounded_rectangle([110, y, 360, y + h], radius=16, fill=TEAL if on else GREY); d.rectangle([330, y, 360, y + h], fill=TEAL if on else GREY)
        draw_text(d, (128, y + 14), lab, font(24, bold=True), WHITE, 220, 1.1)
        if on:
            draw_text(d, (384, y + 10), body, font(24), INK, 1300, 1.22)
            d.text((1700, y + 10), wk, font=font(20, bold=True), fill=TERRA)
        y += h + 10
    footer(d, False, "7 lines")
    return img

def s_glossary():
    img, d = base(False)
    heading(d, "Twenty-five terms to write from memory", size=48)
    terms = ["systemic lens", "circular causality", "punctuation", "wholeness", "emergent property", "homeostasis", "set point", "negative feedback", "positive feedback", "equifinality",
             "family rules", "subsystem", "boundary", "enmeshment", "disengagement", "hierarchy", "cross-generational coalition", "triangle", "detriangling", "differentiation",
             "enactment", "directive", "externalizing", "miracle question", "not-knowing stance"]
    for i, t in enumerate(terms):
        c, r = i % 5, i // 5
        x, y = 110 + c * 345, 220 + r * 130
        d.rounded_rectangle([x, y, x + 325, y + 110], radius=18, fill=WHITE, outline=SAND_DARK, width=2)
        d.text((x + 16, y + 10), f"{i + 1:02d}", font=font(20, bold=True), fill=TERRA)
        draw_text(d, (x + 16, y + 40), t, font(26, bold=True), TEAL, 295, 1.1)
    draw_text(d, (110, 880), "Two sentences each, with an example. Then redraw your Week 5 map and write its seven-line formulation.", font(28), MUTED, 1700, 1.3)
    footer(d, False)
    return img

def deck():
    S1 = "MFT is a licensed mental health profession that treats people in the context of their relationships, using a systemic lens."
    S2 = "The field was born in the 1950s when researchers in several places, independently, began seeing whole families — and discovered that the family was the patient."
    S3 = "Systemic therapy is not a technique added to individual therapy; it is a different set of assumptions about where problems live."
    S4 = "The concepts of dynamics — how a system moves: wholeness, circular causality, homeostasis, feedback."
    S5 = "The concepts of structure — how a system is arranged: members, subsystems, boundaries, hierarchy, triangles."
    S6 = "Four classic schools, each building a practice on one or two of the core concepts."
    S7 = "Three postmodern schools that kept the first shift and radicalized the fifth: who defines the problem?"
    D = []
    D.append(("01-welcome-map.mp3", [
        (1.0, E.s_title("Mid-Term Review and Synthesis", "Week 8 — Mapping the field so far\nSeven weeks, one map, one idea", "MFT 701 · Master of Marriage and Family Therapy")),
        (1.3, s_map()),
        (1.6, E.s_bullets("Learning Objectives", ["State the main contribution of each of Weeks 1–7 in one sentence.", "Explain how the weeks depend on one another.", "Resolve five apparent contradictions in the material.", "Write a one-page systemic formulation of a family.", "Prepare for the mid-term with a clear strategy."], nums=True, intro="By the end of this lecture you will be able to…")),
        (0.8, E.s_statement("Say the sentence before I do.", "Synthesis you produce is worth ten times the synthesis you hear. Pause often.")),
    ]))
    D.append(("02-nodes-1-2.mp3", [
        (0.6, s_map(active=(0, 1))),
        (1.6, s_node(0, S1, ["the Adebayos", "the mobile", "six nodes of the profession", "AAMFT · COAMFTE · licensure", "“what is happening around Tunde?”"], "Node 1 tells you what the profession is — Node 2 tells you that it did not have to exist.")),
        (1.9, s_node(1, S2, ["streams before 1950", "marriage counselling, 1929", "Palo Alto 1952–62", "double bind", "MRI", "1960s coalescing", "1970s golden age", "1980s–90s postmodern turn", "evidence-based today"], "Every school you have learned is a descendant of someone on that timeline. Place a school on the timeline and you understand what problem it was trying to solve.")),
    ]))
    D.append(("03-node-3.mp3", [
        (0.5, s_map(active=(2,), lit=(0, 1))),
        (1.3, s_node(2, S3, ["two coaches", "individual → system", "linear → circular", "content → process", "why → what", "observer → participant", "context & meaning", "limits: where there is harm, circularity stops"], "The hinge of the course. Nodes 1 and 2 describe the profession; Node 3 gives it its mind. Everything after is the paradigm worked out in detail.")),
        (0.8, E.s_statement("Revise Week 3 first.", "Every exam question can be answered by asking: “which shift is this testing?”")),
    ]))
    D.append(("04-nodes-4-5.mp3", [
        (0.5, s_map(active=(3, 4), lit=(0, 1, 2), bracket=(3, 4))),
        (2.4, s_two_nodes(3, 4, "Wholeness — we treat the lines between the dots · circular causality & punctuation · homeostasis — rules as set point, anxiety as sensor · feedback — negative steadies, positive amplifies · equifinality, rules, redundancy", "Members · subsystems: spousal, parental, sibling · boundaries: clear, diffuse, rigid — judged by function · hierarchy & the cross-generational coalition · Bowen's triangle — the engine that keeps rearranging the structure", "Week 4 is the physics; Week 5 is the anatomy. A structural map is a snapshot; feedback and homeostasis explain why the snapshot keeps reproducing itself.", "Nodes 4 and 5 — dynamics and structure")),
        (1.0, E.s_statement("Structure + dynamics = a formulation.", "Either alone is a label. “Tunde is in a coalition with his mother — and the loop that maintains it runs like this, and the set point it protects is this.”")),
    ]))
    D.append(("05-nodes-6-7.mp3", [
        (0.5, s_map(active=(5, 6), lit=(0, 1, 2, 3, 4))),
        (1.6, s_two_nodes(5, 6, "Bowen — anxiety across generations, the calm coach · Structural — a structure that has not adapted, the stage director · Strategic — the stuck solution, the strategist · Experiential — suppressed feeling, the therapist's own self", "Solution-Focused — exceptions and a described future · Narrative — the problem-saturated story re-authored · Collaborative — problems in language, dissolved in dialogue · the sixth row: who is the expert?", "The schools are the concepts, specialized. Bowen → triangles; Minuchin → boundaries & hierarchy; the strategists → feedback & homeostasis; Satir & Whitaker → process and the participant therapist.", "Nodes 6 and 7 — the schools")),
        (1.2, E.s_statement("“If the therapist is a participant, who gave the therapist the right to define the problem?”", "The whole postmodern turn in one sentence — the first shift kept, the fifth radicalized.")),
    ]))
    D.append(("06-contradictions.mp3", [(0.5, s_contradictions(None)), (0.9, s_contradictions(0)), (1.0, s_contradictions(1)), (1.0, s_contradictions(2)), (0.8, s_contradictions(3)), (0.8, s_contradictions(4))]))
    D.append(("07-big-idea.mp3", [
        (0.8, s_map(active=tuple(range(7)), centre=True, title="The one big idea", badge="Centre")),
        (2.2, s_big_idea_thread()),
        (1.6, E.s_cards("If the big idea is true…", [("Assessment is relational", "You cannot formulate a case from one person's account."), ("Intervention is relational", "The smallest useful change is a change in a pattern, not in a person."), ("The therapist is in the room", "Part of the pattern, responsible for what their presence adds — next week's topic.")], dark=True)),
    ]))
    D.append(("08-formulation.mp3", [(0.5, s_formulation(0)), (0.5, s_formulation(1)), (0.7, s_formulation(2)), (0.5, s_formulation(3)), (0.9, s_formulation(4)), (0.8, s_formulation(5)), (0.6, s_formulation(6)), (1.0, s_formulation(7))]))
    D.append(("09-exam-prep.mp3", [
        (1.3, E.s_cards("The mid-term — three parts", [("Part 1 · Definitions", "Fifteen key terms; two sentences each, with an example."), ("Part 2 · Formulation", "A new vignette, in exactly the seven-line format."), ("Part 3 · Comparison essay", "Two schools on the five criteria, applied to the vignette.")])),
        (2.4, s_glossary()),
        (1.5, E.s_bullets("Five mistakes that cost marks", ["Confusing negative and positive feedback — negative is not bad, positive is not good.", "Calling every close family enmeshed — the test is function.", "Describing structure without dynamics.", "Treating hierarchy as a synonym for patriarchy.", "Listing techniques without the theory that explains why they should work."], nums=True)),
    ]))
    D.append(("10-summary-close.mp3", [
        (1.2, s_map(active=tuple(range(7)), centre=True, title="The map, complete")),
        (1.6, E.s_bullets("Review Questions — synthesis", ["Choose any two weeks and explain, in a paragraph, how the second depends on the first.", "Take one of the five contradictions and explain it to a sceptical friend, using the Adebayos.", "Write the seven-line formulation for a family you know well — in under 200 words."], nums=True, intro="Pause the video and write your answers.")),
        (1.3, E.s_cards("Looking Ahead", [("Next Week", "The role and stance of the family therapist — neutrality, curiosity, multipartiality — taught as a dialogue between two voices."), ("Assignment — the mid-term", "The 25-term glossary · the seven-line formulation of your own family · the five contradictions in your own words. Bring your questions.")], dark=True)),
        (0.6, E.s_title("Thank you.", "End of Week 8\nHalf the course is behind you — and it fits together.", "MFT 701 · Week 8")),
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
