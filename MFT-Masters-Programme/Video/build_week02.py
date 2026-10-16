#!/usr/bin/env python3
"""
MFT 701 Week 2 — Historical Roots (Timeline style).
Reuses the slide engine from build_video.py and adds a persistent era strip.
Usage: python3 build_week02.py
"""
import os, subprocess
from PIL import Image, ImageDraw
from mutagen.mp3 import MP3
import imageio_ffmpeg
import build_video as E  # slide engine

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "..", "Audio", "MFT-701-W02")
SLIDES = os.path.join(HERE, "slides-w02")
OUT = os.path.join(HERE, "MFT-701-Week-02-Lecture.mp4")
os.makedirs(SLIDES, exist_ok=True)
W, H = E.W, E.H

ERAS = ["Before 1950", "1950s · Palo Alto", "1950s · Pioneers", "1960s", "1970s", "1980s–90s", "2000s–Today"]

_orig_heading = E.heading
def _heading(d, title, dark=False, y=90, size=58):
    return _orig_heading(d, title, dark, y=max(y, 165), size=size)
E.heading = _heading  # all headed slides in this deck leave room for the era band

def strip(img, active, dark=None):
    """Draw the era strip as a full-width band at the top; `active` = index into ERAS (-1 = none yet)."""
    d = ImageDraw.Draw(img)
    if dark is None:
        dark = sum(img.getpixel((W - 30, 30))) < 300
    x0, x1, y = 200, W - 140, 62
    n = len(ERAS)
    step = (x1 - x0) / (n - 1)
    d.line([(x0, y), (x1, y)], fill=E.TEAL_LIGHT if dark else E.SAND_DARK, width=4)
    for i, e in enumerate(ERAS):
        x = x0 + i * step
        on = i == active
        done = i < active
        r = 16 if on else 10
        d.ellipse([x - r, y - r, x + r, y + r], fill=E.TERRA if (on or done) else (E.TEAL_DARK if dark else E.WHITE),
                  outline=E.TERRA if (on or done) else (E.TEAL_LIGHT if dark else E.SAND_DARK), width=3)
        f = E.font(24, bold=on)
        tw = d.textlength(e, font=f)
        col = (E.SAND if dark else E.TEAL) if on else (E.SAND_DARK if dark else E.MUTED)
        d.text((x - tw / 2, y + 26), e, font=f, fill=col)
    return img

def S(img, era):
    return strip(img, era)

HOSP = os.path.join(E.ASSETS, "hospital-1950s.png")

def deck():
    D = []
    # 1 — welcome / objectives / hook
    D.append(("01-welcome-hook.mp3", [
        (1.6, E.s_title("Historical Roots of Marriage and Family Therapy",
                        "Week 2 — Palo Alto, Bateson and the Birth of a Profession\n1900s to Today",
                        "MFT 701 · Master of Marriage and Family Therapy")),
        (1.2, S(E.s_concept_map(active=2, title="This Week: Node 3 — History"), -1)),
        (3.0, S(E.s_bullets("Learning Objectives", [
            "Trace the main streams that flowed together to form the profession.",
            "Explain what happened in Palo Alto in the 1950s and why it mattered.",
            "Name the founding pioneers and the schools that grew from them.",
            "Describe how critiques, research and professionalization shaped today's field.",
        ], nums=True, intro="By the end of this lecture you will be able to…"), -1)),
        (3.4, S(E.s_image("A Puzzle from the Early 1950s", HOSP,
                        quote="She got better in hospital. She went home. She relapsed. Again, and again.",
                        caption="For decades the explanation was simple: the illness lives inside the patient. A few clinicians asked a dangerous question — what if something at home is part of the pattern?"), -1)),
        (1.0, E.s_statement("That question is the seed from which our whole profession grew.")),
    ]))
    # 2 — streams
    D.append(("02-streams.mp3", [
        (1.0, S(E.s_statement("Before 1950: Streams Converging", "Before there was family therapy, there were several separate streams.", dark=False), 0)),
        (3.0, S(E.s_cards("Stream 1 — Psychoanalysis: The Individual Alone", [
            ("Freud and the inner life", "Early twentieth-century mental health focused entirely on the individual psyche."),
            ("Little Hans, 1909", "A five-year-old treated almost entirely through conversations with his father — yet never developed into family work."),
            ("A rule against relatives", "Analysts were trained not to see a patient's family, for fear of contaminating the treatment."),
        ]), 0)),
        (2.6, S(E.s_cards("Stream 2 — Child Guidance (1920s)", [
            ("Alfred Adler, Vienna", "Clinics where children were seen together with parents and teachers."),
            ("The American model", "Psychiatrist for the child, social worker for the mother — separately."),
            ("In the building, not in the room", "The family was present, but not yet treated as one unit."),
        ]), 0)),
        (3.4, S(E.s_timeline("Stream 3 — The Marriage Counselling Movement", [
            ("1929", "Abraham & Hannah Stone — marriage consultation centre, New York"),
            ("1930", "Paul Popenoe — American Institute of Family Relations, Los Angeles"),
            ("1932", "Emily Mudd — Marriage Council of Philadelphia"),
            ("1942", "American Association of Marriage Counselors founded — later the AAMFT"),
        ]), 0)),
    ]))
    # 3 — pastoral + systems ideas
    D.append(("03-pastoral-and-systems.mp3", [
        (3.6, S(E.s_cards("Stream 4 — Pastoral Care", [
            ("Clergy came first", "Long before psychiatry took interest, communities turned to pastors for marriage and family trouble."),
            ("Anton Boisen, 1925", "Clinical pastoral education — training ministers in hospitals. Many early marriage counsellors were pastors."),
            ("Part of our ancestry", "Faith-integrated family care is not a modern add-on; it is woven into the profession's origins."),
        ], dark=True), 0)),
        (3.6, S(E.s_cards("Stream 5 — Ideas from Outside Psychiatry (1940s)", [
            ("Kurt Lewin — Field theory", "Behaviour is a function of the person and the environment together."),
            ("Ludwig von Bertalanffy — General Systems Theory", "Living systems share common principles of organization."),
            ("Norbert Wiener — Cybernetics, 1948", "The science of feedback and self-regulation."),
            ("Macy Conferences, 1946–53", "Mathematicians, biologists and social scientists meet in New York. A regular participant: anthropologist Gregory Bateson."),
        ], cols=2), 0)),
        (1.4, S(E.s_bullets("Five Streams, About to Converge", [
            "Individual psychology", "Child guidance", "Marriage counselling", "Pastoral care", "Systems theory and cybernetics",
        ], nums=True), 0)),
    ]))
    # 4 — Palo Alto
    D.append(("04-palo-alto.mp3", [
        (2.6, S(E.s_cards("The Bateson Project — Palo Alto, 1952", [
            ("Gregory Bateson", "Anthropologist. Grant to study communication at the Veterans Administration hospital."),
            ("Jay Haley", "Young communications student."),
            ("John Weakland", "Chemical engineer turned anthropologist."),
            ("William Fry · Don Jackson", "Psychiatrists — Jackson had worked with families of patients with schizophrenia."),
        ], cols=2, dark=True), 1)),
        (3.4, S(E.s_quote("Toward a Theory of Schizophrenia — the double bind: contradictory messages at different levels, no way to comment, no way to leave.",
                          "Bateson, Jackson, Haley & Weakland, 1956"), 1)),
        (2.6, S(E.s_compare("The Double Bind — Then and Now",
                            ("What did not survive", ["The claim that double binds cause schizophrenia", "The blaming of mothers this era sometimes encouraged"]),
                            ("What endured", ["A symptom understood as the product of a communication system", "Not a defect inside one person"]),
                            vs="→"), 1)),
    ]))
    # 5 — MRI
    D.append(("05-mri.mp3", [
        (2.4, S(E.s_quote("Family homeostasis: when one member changes, others act — often without realizing it — to restore the old pattern.",
                          "Don Jackson, 1957 — and the answer to our relapsing patient"), 1)),
        (3.0, S(E.s_cards("The Mental Research Institute, 1959", [
            ("Don Jackson — founder", "Palo Alto becomes the field's laboratory."),
            ("Virginia Satir", "Social worker seeing whole families since the early 1950s; the field's most beloved teacher."),
            ("Paul Watzlawick, 1960", "Communication theory: “One cannot not communicate.”"),
        ]), 1)),
        (1.8, S(E.s_timeline("What Grew from the MRI", [
            ("1959", "MRI founded"),
            ("1967", "Brief Therapy Center"),
            ("1974", "Change — Watzlawick, Weakland & Fisch"),
            ("Later", "Brief and strategic therapy"),
        ]), 1)),
    ]))
    # 6 — pioneers
    D.append(("06-pioneers.mp3", [
        (3.4, S(E.s_cards("Pioneers of the 1950s — Independently, the Same Discovery", [
            ("Murray Bowen — Menninger, NIMH, Georgetown", "1954: hospitalized entire families. Triangles, fusion, multigenerational patterns → Bowen Family Systems Theory."),
            ("Theodore Lidz — Yale", "Marital schism and marital skew."),
            ("Lyman Wynne — NIMH", "Pseudomutuality: false harmony with no room for difference."),
        ]), 2)),
        (3.4, S(E.s_cards("Pioneers of the 1950s — Continued", [
            ("Nathan Ackerman — New York", "“The unity of the family” (1938). The Psychodynamics of Family Life, 1958 — first book on family therapy. Ackerman Institute, 1960."),
            ("Carl Whitaker — Atlanta", "Provocative, deeply personal style → Experiential family therapy."),
            ("Ivan Boszormenyi-Nagy — Philadelphia", "Contextual therapy: loyalty, fairness, the ledger across generations."),
        ], dark=True), 2)),
    ]))
    # 7 — 1960s
    D.append(("07-sixties.mp3", [
        (4.0, S(E.s_timeline("The 1960s — A Field Coalesces", [
            ("1962", "Family Process journal — Ackerman & Jackson; Haley editor"),
            ("1963", "California: first state licence"),
            ("1964", "Satir — Conjoint Family Therapy"),
            ("1965", "Minuchin — Philadelphia Child Guidance Clinic"),
            ("1967", "Families of the Slums; Haley joins Minuchin"),
        ]), 3)),
        (2.6, S(E.s_cards("Salvador Minuchin", [
            ("Wiltwyck School, New York", "Delinquent boys from poor families. Insight-based talk did little."),
            ("The discovery", "Change the structure of interactions in the room — boundaries, alliances, hierarchy — and real change follows."),
            ("Philadelphia Child Guidance Clinic", "Became the most influential family therapy training centre in the world."),
        ]), 3)),
        (1.2, S(E.s_statement("A journal. A licence. A textbook. A training institution.", "The signs of a profession being born."), 3)),
    ]))
    # 8 — 1970s
    D.append(("08-seventies.mp3", [
        (2.0, S(E.s_cards("The 1970s — Golden Age of the Schools", [
            ("1974 · Families and Family Therapy", "Minuchin — Structural Family Therapy"),
            ("1974 · Change", "Watzlawick, Weakland & Fisch — MRI brief therapy"),
            ("1976 · Problem-Solving Therapy", "Haley; Family Therapy Institute of Washington with Cloé Madanes — Strategic Family Therapy"),
        ]), 4)),
        (2.0, S(E.s_cards("The 1970s — Golden Age of the Schools", [
            ("1978 · Paradox and Counterparadox", "Selvini Palazzoli & the Milan team — circular questioning, systemic hypothesizing"),
            ("1978 · Family Therapy in Clinical Practice", "Murray Bowen gathers his life's work"),
            ("1978 · AAMFT & COAMFTE", "Association takes its present name; accreditation body recognized by the US government"),
        ]), 4)),
        (2.6, S(E.s_timeline("The Profession Organizes", [
            ("1942", "American Association of Marriage Counselors"),
            ("1970", "…of Marriage and Family Counselors"),
            ("1978", "American Association for Marriage and Family Therapy"),
            ("1978", "COAMFTE recognized by the US government"),
        ]), 4)),
    ]))
    # 9 — critique and postmodern
    D.append(("09-critique-postmodern.mp3", [
        (3.2, S(E.s_cards("The Critiques That Matured the Field", [
            ("Feminist critique", "Hare-Mustin (1978); the Women's Project — Walters, Carter, Papp, Silverstein. “Neutral” systems thinking ignored power and blamed mothers."),
            ("Multicultural critique", "McGoldrick et al., Ethnicity and Family Therapy (1982) — take culture seriously."),
            ("Second-order cybernetics", "The therapist is never a neutral observer, but a participant in the conversation."),
        ], dark=True), 5)),
        (3.4, S(E.s_cards("The Postmodern Models", [
            ("Solution-Focused Brief Therapy", "de Shazer & Berg, Milwaukee — exceptions and preferred futures"),
            ("Narrative Therapy", "White & Epston, 1990 — externalize problems, re-author stories"),
            ("Collaborative Therapy", "Anderson & Goolishian, Texas"),
            ("Research streams", "EFT — Johnson & Greenberg, 1985 · Gottman's couples laboratory"),
        ], cols=2), 5)),
    ]))
    # 10 — today + close
    D.append(("10-today-and-close.mp3", [
        (2.4, S(E.s_cards("2000s to Today", [
            ("Evidence-based practice", "Functional Family Therapy, Multisystemic Therapy, EFT — tested in rigorous trials"),
            ("Common factors", "What unites effective family therapists matters as much as what divides them"),
            ("A global profession", "IFTA founded 1987; training across Africa, Asia and Latin America"),
        ]), 6)),
        (2.4, S(E.s_bullets("Lessons from the Timeline", [
            "Born from careful observation — clinicians who refused to ignore what they saw when the patient went home.",
            "Its best ideas came from outside psychiatry: anthropology, biology, engineering and the pastoral tradition.",
            "Critique made the field stronger.",
            "The story is not finished — there is a space on this timeline for your contribution.",
        ], nums=True), 6)),
        (2.0, S(E.s_bullets("Review Questions", [
            "Name three streams that converged to form family therapy before 1950.",
            "What was the double bind, and what is its lasting contribution?",
            "How did the feminist and multicultural critiques change the field?",
        ], nums=True, intro="Pause the video and write your answers."), 6)),
        (1.8, E.s_cards("Looking Ahead", [
            ("Next Week", "The systemic paradigm shift — from individual pathology to relational patterns."),
            ("Assignment", "A one-page timeline of the profession with at least eight events — plus a final entry: the year you expect to graduate and the contribution you hope to make."),
        ], dark=True)),
        (0.6, E.s_title("Thank you.", "End of Week 2\nSee you next week.", "MFT 701 · Week 2")),
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
