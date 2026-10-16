#!/usr/bin/env python3
"""
MFT 701 Week 3 — The Systemic Paradigm Shift (Analogy style: a football team).
Reuses the slide engine from build_video.py. Usage: python3 build_week03.py
"""
import os, subprocess, math
from PIL import Image, ImageDraw
from mutagen.mp3 import MP3
import imageio_ffmpeg
import build_video as E

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "..", "Audio", "MFT-701-W03")
SLIDES = os.path.join(HERE, "slides-w03")
OUT = os.path.join(HERE, "MFT-701-Week-03-Lecture.mp4")
os.makedirs(SLIDES, exist_ok=True)
W, H = E.W, E.H
COACH = os.path.join(E.ASSETS, "football-coach.png")
FAMILY = os.path.join(E.ASSETS, "adebayo-family.png")

SHIFTS = ["Individual → System", "Linear → Circular", "Content → Process", "Why → What & How", "Observer → Participant", "System → Context"]

def s_pitch_family(title, pitch, family, badge=None):
    """Two-panel analogy slide: 'On the pitch' vs 'In the family'."""
    img, d = E.base(False)
    y = E.heading(d, title)
    cw = (W - 220 - 60) // 2
    for i, (lab, head, items, col, bg) in enumerate([
        ("ON THE PITCH", pitch[0], pitch[1], E.TEAL, E.WHITE),
        ("IN THE FAMILY", family[0], family[1], E.TERRA, E.CREAM)]):
        x0 = 110 + i * (cw + 60)
        d.rounded_rectangle([x0, y, x0 + cw, H - 130], radius=24, fill=bg, outline=col, width=4)
        d.rounded_rectangle([x0 + 30, y + 26, x0 + 30 + d.textlength(lab, font=E.font(22, bold=True)) + 36, y + 66], radius=20, fill=col)
        d.text((x0 + 48, y + 34), lab, font=E.font(22, bold=True), fill=E.WHITE)
        yy = E.draw_text(d, (x0 + 34, y + 96), head, E.font(44, bold=True), col, cw - 68, 1.15) + 30
        for it in items:
            d.rounded_rectangle([x0 + 36, yy + 18, x0 + 60, yy + 42], radius=6, fill=col)
            yy = E.draw_text(d, (x0 + 88, yy), it, E.font(37), E.INK, cw - 134, 1.3) + 26
    E.footer(d, False, badge)
    return img

def s_loop(title, steps, badge=None, caption=None):
    """Circular causality diagram: steps arranged on a ring with arrows."""
    img, d = E.base(True)
    E.heading(d, title, dark=True)
    cx, cy, RX, RY = 960, 560, 560, 215
    n = len(steps)
    pts = [(cx + RX * math.cos(-math.pi / 2 + i * 2 * math.pi / n), cy + RY * math.sin(-math.pi / 2 + i * 2 * math.pi / n)) for i in range(n)]
    # dashed-looking ellipse ring
    d.ellipse([cx - RX, cy - RY, cx + RX, cy + RY], outline=E.TEAL_LIGHT, width=5)
    # arrows along the ring between nodes (sampled arcs)
    for i in range(n):
        a0 = -math.pi / 2 + i * 2 * math.pi / n + 0.28
        a1 = -math.pi / 2 + (i + 1) * 2 * math.pi / n - 0.28
        arc = [(cx + RX * math.cos(a0 + (a1 - a0) * t / 20), cy + RY * math.sin(a0 + (a1 - a0) * t / 20)) for t in range(21)]
        d.line(arc, fill=E.TERRA, width=8, joint="curve")
        (xa, ya), (xb, yb) = arc[-2], arc[-1]
        ang = math.atan2(yb - ya, xb - xa)
        ah = 34
        d.polygon([(xb + 10 * math.cos(ang), yb + 10 * math.sin(ang)),
                   (xb - ah * math.cos(ang - 0.45), yb - ah * math.sin(ang - 0.45)),
                   (xb - ah * math.cos(ang + 0.45), yb - ah * math.sin(ang + 0.45))], fill=E.TERRA)
    for i, (x, y) in enumerate(pts):
        f = E.font(30, bold=True)
        th = E.text_height(d, steps[i], f, 330, 1.15)
        d.rounded_rectangle([x - 190, y - th / 2 - 24, x + 190, y + th / 2 + 24], radius=22, fill=E.SAND, outline=E.TERRA, width=4)
        E.draw_text(d, (x - 165, y - th / 2 + 2), steps[i], f, E.TEAL, 330, 1.15, align="center")
    if caption:
        E.draw_text(d, (210, 880), caption, E.font(31), E.SAND_DARK, 1500, 1.3, align="center")
    E.footer(d, True, badge)
    return img

def s_rings(title, rings, badge=None):
    """Nested-context diagram (Bronfenbrenner-style concentric rings)."""
    img, d = E.base(False)
    E.heading(d, title)
    cx, cy = 700, 610
    n = len(rings)
    cols = [E.TEAL, E.TEAL_LIGHT, (90, 140, 150), E.SAND_DARK, E.TERRA]
    for i in range(n - 1, -1, -1):
        r = 72 + i * 64
        d.ellipse([cx - r * 1.35, cy - r, cx + r * 1.35, cy + r], fill=cols[i % len(cols)], outline=E.SAND, width=4)
    for i, (lab, _) in enumerate(rings):
        r = 72 + i * 64
        f = E.font(26, bold=True)
        col = E.WHITE if i < 3 else E.INK
        tw = d.textlength(lab, font=f)
        yy = (cy - 16) if i == 0 else (cy - r + 22)
        d.text((cx - tw / 2, yy), lab, font=f, fill=col)
    # legend right
    yy = 300
    for i, (lab, desc) in enumerate(rings):
        d.rounded_rectangle([1260, yy + 6, 1290, yy + 36], radius=8, fill=cols[i % len(cols)])
        d.text((1310, yy), lab, font=E.font(32, bold=True), fill=E.TEAL)
        yy = E.draw_text(d, (1310, yy + 44), desc, E.font(27), E.INK, 540, 1.25) + 22
    E.footer(d, False, badge)
    return img

def deck():
    D = []
    B = lambda i: f"Shift {i} of 6 · {SHIFTS[i-1]}"
    # 1
    D.append(("01-welcome-analogy.mp3", [
        (1.6, E.s_title("The Systemic Paradigm Shift",
                        "Week 3 — From Individual Pathology to Relational Patterns",
                        "MFT 701 · Master of Marriage and Family Therapy")),
        (2.6, E.s_bullets("Learning Objectives", [
            "Explain what a paradigm is and why the shift to systemic thinking was so radical.",
            "Describe six specific shifts in how a systemic therapist thinks.",
            "Apply those shifts to a family case.",
            "Recognize the limits of systemic thinking — including when it must not be used to excuse harm.",
        ], nums=True, intro="By the end of this lecture you will be able to…")),
        (3.2, E.s_image("One Analogy for the Whole Lecture", COACH,
                        quote="Eight matches without a win. The striker hasn't scored in two months. Drop him. Sell him.",
                        caption="The team that stopped scoring — and two coaches watching the same replay.")),
        (2.6, E.s_compare("Two Coaches, One Replay",
                          ("The first coach watches the striker", ["His touches", "His movement", "His confidence", "Thinking individually"]),
                          ("The second coach watches the whole pitch", ["Where the midfield is positioned", "Who passes to whom", "How the shape changes after conceding", "Thinking systemically"]))),
    ]))
    # 2
    D.append(("02-paradigm.mp3", [
        (2.2, E.s_quote("A paradigm is the set of assumptions a community takes for granted — the lens through which it sees, so familiar it is almost invisible.", "after Thomas Kuhn, The Structure of Scientific Revolutions (1962)")),
        (3.2, E.s_bullets("The Individual Paradigm — Four Assumptions", [
            ("The problem is inside the person", "In their biology, their thoughts, or their unconscious."),
            ("Causality is linear", "Something caused the problem; treat the cause and it will be fixed."),
            ("Diagnose and treat the one person", "The clinician's task is defined by the individual."),
            ("The clinician stands outside", "An objective observer of the problem."),
        ], nums=True)),
        (1.6, s_pitch_family("The Individual Paradigm on the Pitch",
                             ("The problem is in the striker", ["Fitness, confidence, technique", "Fix the striker and the team wins again"]),
                             ("The problem is in the patient", ["Diagnose, treat, medicate", "Fix the person and the family is fine"]))),
        (2.4, E.s_cards("Real Strengths — and a Limit", [
            ("What it gave us", "Psychopharmacology, cognitive therapy, most of what we know about individual disorders. The systemic therapist does not throw it away."),
            ("Where it runs out", "The striker is sold… and the new striker also stops scoring."),
        ], dark=True)),
    ]))
    # 3 — Shift 1
    D.append(("03-shift1-system.mp3", [
        (1.2, E.s_statement("Shift 1: From the Individual to the System", "The unit of analysis moves from the player to the team.", badge=B(1))),
        (3.2, s_pitch_family("Shift 1 — Unit of Analysis",
                             ("He is not failing. He is starved.", ["The creative midfielder was sold", "Few passes reach dangerous areas", "The ‘problem’ in one player is a property of the whole team"]),
                             ("The identified patient", ["The family says: “fix our son”", "Respect the distress — widen the frame", "What is the whole team doing, such that this player struggles?"]), badge=B(1))),
        (2.6, E.s_image("The Adebayos: Tunde as the Striker", FAMILY,
                        quote="The family came to have him fixed.",
                        caption="The therapist watched the whole pitch: a father who had withdrawn, a mother who was exhausted, a sister who had gone silent. Tunde's symptom was the family's symptom, carried by one member.", badge=B(1))),
        (1.4, E.s_statement("The individual does not disappear.", "Bowen: a differentiated self within the system is the goal. The player still matters — but you cannot understand the player without the team.", dark=False, badge=B(1))),
    ]))
    # 4 — Shift 2
    D.append(("04-shift2-circular.mp3", [
        (1.0, E.s_statement("Shift 2: From Linear to Circular Causality", "A causes B… or does B also cause A?", badge=B(2))),
        (2.6, s_loop("The Slump Is a Loop", [
            "Striker stops scoring", "Stops making runs", "Midfield has no target — passes sideways", "Striker isolated and discouraged",
        ], badge=B(2), caption="Who caused the slump? Everyone — and no one.")),
        (2.6, s_pitch_family("Shift 2 — Punctuation",
                             ("Every player tells it differently", ["“They never pass to me”", "“He never makes a run”", "Each punctuates the same loop from their own position"]),
                             ("Watzlawick's classic loop", ["She pursues because he withdraws", "He withdraws because she pursues", "The therapist doesn't judge who started it — she asks how each move invites the next"]), badge=B(2))),
        (2.0, s_loop("The Adebayo Loop", [
            "Father withdraws", "Mother over-functions", "Tunde acts out", "Father feels a failure — withdraws further",
        ], badge=B(2), caption="No single cause — so no single place where change must begin. Any member who changes their move can change the pattern.")),
    ]))
    # 5 — Shift 3
    D.append(("05-shift3-process.mp3", [
        (1.0, E.s_statement("Shift 3: From Content to Process", "What is argued about — versus the pattern that repeats.", badge=B(3))),
        (2.6, s_pitch_family("Shift 3 — Content vs Process",
                             ("Content: the stray pass, the missed goal", ["Process: every time they concede…", "defenders blame midfield → midfield blames striker → shape collapses", "The good coach studies the recurring shape"]),
                             ("Content: money, in-laws, school, who forgot what", ["Process: who speaks first, who interrupts, who goes quiet, who rescues whom", "Minuchin called this tracking"]), badge=B(3))),
        (2.4, E.s_bullets("A Simple Exercise (MFT 706)", [
            "When a family describes an argument, don't ask only what it was about.",
            "Ask: “And then what happened?” … “And then?” … “And then?”",
            "Within five steps you will usually see the loop.",
            "The content changes every week. The process rarely does — and process is where the therapy happens.",
        ], nums=True, badge=B(3))),
    ]))
    # 6 — Shift 4
    D.append(("06-shift4-function.mp3", [
        (1.0, E.s_statement("Shift 4: From Why to What and How", "What is this symptom doing in the system right now — and how is the system keeping it going?", badge=B(4))),
        (1.8, s_pitch_family("Shift 4 — Homeostasis",
                             ("The team that sits back after scoring", ["Drops deep… concedes the equaliser… every time", "Nobody decided this", "The automatic return to a familiar state — anxious, cautious, level"]),
                             ("The family's accustomed balance", ["Systems return to what they know", "Even when that balance is losing"]), badge=B(4))),
        (2.4, E.s_cards("Feedback Keeps the Balance", [
            ("Negative feedback — reduces change", "A teenager grows independent → a parent's anxiety rises → rules tighten → the family is pulled back to the old pattern."),
            ("Positive feedback — amplifies change", "A small criticism → a sharper reply → a shout → a slammed door. Escalation."),
        ], badge=B(4))),
        (2.2, E.s_statement("The symptom serves a function.", "Tunde's school refusal may be the only thing that has put both parents in the same room. It holds the system together while hurting the one who carries it — and understanding that is the first step to meeting the same need in a healthier way.", badge=B(4))),
    ]))
    # 7 — Shift 5
    D.append(("07-shift5-participant.mp3", [
        (1.0, E.s_statement("Shift 5: From Observer to Participant", "The coach is on the pitch too.", badge=B(5))),
        (2.6, s_pitch_family("Shift 5 — You Are in the Loop",
                             ("A coach is not outside the team", ["Her substitutions, her shouting, her mood after a defeat", "All of it shapes how the players play", "She is part of the system she is trying to change"]),
                             ("First- to second-order cybernetics (1980s)", ["Who you look at first, whose story you believe, what you find interesting", "The family responds to all of it", "A new system in the room: the therapeutic system — which includes you"]), badge=B(5))),
        (2.6, E.s_bullets("Humbling — and Useful", [
            ("Your reactions are information", "Wanting to rescue the mother or discipline the son? The family may be inviting you into a role someone at home already plays."),
            ("Curiosity rather than certainty", "The systemic stance that follows."),
            ("Multipartiality", "On everyone's side at once — rather than a neutrality that pretends to stand nowhere."),
        ], nums=True, badge=B(5))),
    ]))
    # 8 — Shift 6
    D.append(("08-shift6-context.mp3", [
        (1.0, E.s_statement("Shift 6: From the System to Its Context", "No team plays in a vacuum.", badge=B(6))),
        (2.2, s_rings("Nested Systems — Bronfenbrenner", [
            ("Person", "Tunde"),
            ("Family", "Parents, sister, extended kin"),
            ("Community", "School, church, neighbours"),
            ("Economy", "The father's job loss is an economic event"),
            ("Culture", "Beliefs about what a father should be"),
        ], badge=B(6))),
        (2.4, E.s_cards("Context for the Adebayos — and for Us", [
            ("Not a private failure", "The job loss is an economic event; the silence around it is shaped by cultural beliefs about fatherhood."),
            ("The church", "May be a source of shame — or of support. The systemic therapist asks."),
            ("Systems thinking, two thousand years early", "“If one member suffers, all the members suffer with it.” Scripture never imagines a person apart from relationship."),
        ], dark=True, badge=B(6))),
        (2.4, E.s_compare("Where the Analogy Breaks — and a Warning",
                          ("Families are not teams", ["No league table", "The goal is not winning but flourishing"]),
                          ("Circular causality must never excuse abuse", ["When one person is hitting another, we do not say “you both contribute”", "Safety first. Responsibility is individual.", "The systemic lens is set aside until it is safe to use"]), vs="!")),
    ]))
    # 9 — both lenses
    D.append(("09-both-lenses.mp3", [
        (1.2, E.s_statement("Putting It Together", "Two formulations of the same case.", dark=False)),
        (2.0, E.s_bullets("Individual Formulation", [
            "Tunde, 14: school refusal, irritability, social withdrawal — four months' duration.",
            "Possible adjustment disorder or depressive episode.",
            "Plan: individual therapy; possible medication referral; parent guidance.",
        ], nums=True)),
        (3.6, E.s_bullets("Systemic Formulation", [
            "A family in transition after the father's job loss four months ago.",
            "Father withdrawn · mother over-functioning · daughter invisible · Tunde's symptoms organizing the family around him.",
            "Function: brings the parents into shared concern while the real issue — the father's loss and shame — stays unspoken.",
            "Maintained by a loop of withdrawal → over-functioning → acting out.",
            "Plan: conjoint sessions including the father; track and interrupt the loop; speak directly about the job loss; support return to school as the family reorganizes.",
        ], nums=True)),
        (2.2, E.s_statement("The two lenses are not enemies.", "Tunde may well be depressed and need individual care. The systemic formulation places that in context and opens the door through which the father walks back into the room. The best therapists hold both lenses — and know which to lift when.")),
    ]))
    # 10 — close
    D.append(("10-summary-close.mp3", [
        (2.6, E.s_cards("Summary — The Six Shifts", [
            ("1 · Individual → System", "From the player to the team; the identified patient"),
            ("2 · Linear → Circular", "Loops and punctuation"),
            ("3 · Content → Process", "Track the recurring sequence"),
            ("4 · Why → What & How", "Function, feedback, homeostasis"),
            ("5 · Observer → Participant", "The therapeutic system includes you"),
            ("6 · System → Context", "Community, economy, culture, faith"),
        ], cols=3)),
        (2.6, E.s_bullets("Review Questions", [
            "Explain punctuation in your own words, with an example from a family you know or have read about.",
            "What does it mean that a symptom serves a function — and why does this not mean the family wants the symptom?",
            "Name one situation in which circular causality must not be applied, and explain why.",
        ], nums=True, intro="Pause the video and write your answers.")),
        (2.2, E.s_cards("Looking Ahead", [
            ("Next Week", "Core systems concepts I — wholeness, circular causality, homeostasis and feedback."),
            ("Assignment", "Choose a family interaction (film, novel, or — with permission — your own family). Write two half-page descriptions: one through the individual lens, one through the systemic lens. Note which questions each lens makes you ask."),
        ], dark=True)),
        (0.8, E.s_title("Thank you.", "End of Week 3\nSee you next week.", "MFT 701 · Week 3")),
    ]))
    return D

def main():
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    vid, aud, idx, total = [], [], 0, 0.0
    for audio, slides in deck():
        apath = os.path.abspath(os.path.join(AUDIO_DIR, audio))
        dur = MP3(apath).info.length
        total += dur
        aud.append(f"file '{apath}'")
        wsum = sum(w for w, _ in slides)
        for w, im in slides:
            idx += 1
            p = os.path.join(SLIDES, f"slide-{idx:03d}.png")
            im.save(p)
            vid.append((p, dur * w / wsum))
    print(f"{idx} slides, {total/60:.1f} min")
    with open(os.path.join(SLIDES, "video.txt"), "w") as f:
        for p, d in vid:
            f.write(f"file '{p}'\nduration {d:.3f}\n")
        f.write(f"file '{vid[-1][0]}'\nduration 0.04\n")
    with open(os.path.join(SLIDES, "audio.txt"), "w") as f:
        f.write("\n".join(aud) + "\n")
    cmd = [ffmpeg, "-y", "-loglevel", "error",
           "-f", "concat", "-safe", "0", "-i", os.path.join(SLIDES, "video.txt"),
           "-f", "concat", "-safe", "0", "-i", os.path.join(SLIDES, "audio.txt"),
           "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-tune", "stillimage",
           "-r", "25", "-pix_fmt", "yuv420p", "-vf", "scale=1920:1080,format=yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", OUT]
    subprocess.run(cmd, check=True)
    print("Wrote", OUT)

if __name__ == "__main__":
    main()
