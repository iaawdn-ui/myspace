# -*- coding: utf-8 -*-
"""Append Extended Developmental Analysis + Guided Case Conference
(~2,300 words) to every chapter _b file of CAC. 702. Idempotent."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chapters_data import CHAPTERS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CONTENT = os.path.join(ROOT, "book2", "content")
MARK = "## 19. Extended Developmental Analysis"

SETTINGS = [
 ("at home",
  "the evening hours, homework, meals, siblings, screens, sleep and the negotiation of rules",
  "parents and caregivers"),
 ("at school",
  "lessons, transitions between classes, group work, examinations, discipline systems and the public judgement of competence",
  "teachers and school leaders"),
 ("among peers",
  "friendship groups, status hierarchies, humour, loyalty, exclusion and the constant audience of equals",
  "friends, classmates and peer-group members"),
 ("in digital life",
  "group chats, social platforms, gaming worlds, shared images and the permanent, searchable record of adolescent experiments",
  "online friends, followers and platform systems"),
 ("in the community",
  "transport, work, sport, youth organisations, health services and the streets and public spaces adolescents actually inhabit",
  "coaches, youth workers, employers and community adults"),
 ("in the counselling room",
  "the bounded, confidential, attentive relationship in which disclosure, disagreement, reflection and repair can be practised",
  "the counsellor and, through the counsellor, the referring adults"),
]


def setting_para(idx, place, detail, actors, concepts, title):
    c1, c2, c3 = concepts[idx % 6], concepts[(idx + 2) % 6], concepts[(idx + 4) % 6]
    return (
        "Read %s, the processes at the heart of this chapter — above all %s, %s and %s — take a "
        "distinctive form. The relevant stage is %s, and the significant audience is %s. Three "
        "features of this setting decide how development proceeds here. First, its demands are "
        "specific: what counts as competence, maturity or trouble %s is defined by this setting's "
        "routines and values, not by adolescence in general, which is why the same adolescent can "
        "appear capable in one setting and chaotic in another without anyone being mistaken. Second, "
        "its feedback is differently timed and differently public: consequences arrive at particular "
        "speeds, before particular audiences, with particular possibilities of repair, and adolescents "
        "calibrate their behaviour to exactly those contingencies. Third, its adults hold different "
        "levers: %s control some of the conditions that maintain or relieve the difficulty, and a "
        "counselling plan that does not reach this setting is relying on the adolescent to out-perform "
        "an unchanged environment. The assessment question for this setting is therefore never only "
        "'how is the adolescent doing?' but 'what is this setting asking for, rewarding, punishing "
        "and making possible — and which single change here would most support the developmental "
        "work of %s?'"
        % (place, c1, c2, c3, detail, actors, place, actors, title.lower()))


def conference(idx, concepts, title):
    name = ["Amara", "Tunde", "Yetunde", "Chiamaka", "Ibrahim", "Funke",
            "Seun", "Ngozi", "Emeka", "Halima"][idx % 10]
    return """A case conference is where developmental reasoning is tested socially, because each participant sees a different adolescent. Convene, in imagination, the conference for a case in the territory of this chapter: %s is discussed by a parent, a teacher, a school counsellor and, crucially, with %s's own account read first and taken seriously. The exercise below reproduces the movement a well-run conference should make.

**The adolescent's account comes first, and it changes the meeting.** %s describes what the difficulty feels like from inside, what adults misunderstand, and what would actually help. Conferences that begin here make fewer attributional errors, because every later claim must survive comparison with the young person's own experience of %s and %s. The chair's first duty is protective: to ensure the account is heard as evidence rather than as an excuse to be managed.

**The parent's account supplies history and home process.** Parents contribute the developmental timeline, the family's values and constraints, what has been tried at home and what it cost. Skilled chairs listen here for process — how conflict is repaired, how rules change with age, where worry is highest at 2 a.m. — rather than adjudicating between the parent's and the adolescent's versions of events, since both are usually accurate reports of different settings.

**The teacher's account supplies trajectory and public competence.** School contributes attendance, attainment over time, peer standing, response to previous support and the classroom conditions under which the adolescent succeeds. The developmental question put to school is precise: under what conditions, which this school can actually arrange, does this adolescent do well — and how much of the week currently consists of those conditions?

**The counsellor integrates, predicts and assigns.** The conference closes not with shared concern but with a formulation, a prediction and named actions: the counsellor states the developmental reading in plain language, specifies what change is expected and by when, assigns one action to each setting, agrees what information will be shared with whom and on what consent basis, and fixes the review date before anyone leaves. Conferences that end this way convert goodwill into development; conferences that do not, however warm, mainly redistribute anxiety.

**Supervision questions arising.** What did each account make visible, and what did each conceal? Whose definition of the problem prevailed, and was that justified? What would disconfirm the agreed formulation, and who is responsible for noticing? What did the conference itself teach the adolescent, who will hear of it, about whether adults can think together on their behalf?""" % (
        name, name, name, concepts[0], concepts[1])


def main():
    import json
    with open(os.path.join(CONTENT, "manifest.json")) as fh:
        manifest = json.load(fh)
    done = 0
    for part in manifest["parts"]:
        for ch in part["chapters"]:
            idx = int(ch["number"]) - 1
            data = CHAPTERS[idx]
            title, concepts = data[1], data[4]
            fb = os.path.join(CONTENT, ch["files"][1])
            with open(fb, encoding="utf-8") as fh:
                text = fh.read()
            if MARK in text:
                continue
            settings_text = "\n\n".join(
                setting_para(idx + k, *SETTINGS[(idx + k) % len(SETTINGS)], concepts, title)
                for k in range(5))
            extra = ("\n%s: Reading %s Across Settings\n\nDevelopment does not happen in general; it "
                     "happens in places, at times of day, before audiences. This extended analysis "
                     "therefore reads the subject of this chapter — %s — across the five settings in "
                     "which adolescent life is actually lived, and asks of each setting the same four "
                     "questions: what does this setting demand, what does it reward, what does it make "
                     "difficult, and what one change within it would most help the adolescents this "
                     "chapter is about? Students should complete the analysis for one real (anonymised) "
                     "or composite adolescent before the seminar, because the exercise reliably "
                     "exposes how much of what is referred as individual difficulty is, in part, "
                     "setting difficulty wearing an adolescent's name.\n\n%s\n\n## 20. Guided Case Conference "
                     "and Chapter Consolidation\n\n%s\n\n**Consolidation task.** Before leaving this "
                     "chapter, write three short paragraphs in your developmental notebook: the "
                     "mechanism from this chapter you now understand best, stated without jargon; the "
                     "claim in this chapter you are least sure the evidence supports, with the study "
                     "that would settle it; and one thing you will do differently in your next "
                     "conversation with an adolescent, a parent or a teacher as a result of this "
                     "chapter. Dated entries of this kind, accumulated across all fifty-eight chapters, "
                     "constitute the reflective spine of the course portfolio described in Appendix B "
                     "and are sampled in the assessment described in Chapter 58.\n"
                     % (MARK, title, title.lower(), settings_text,
                        conference(idx, concepts, title)))
            with open(fb, "w", encoding="utf-8") as fh:
                fh.write(text.rstrip() + "\n" + extra)
            done += 1
    print("expanded chapters:", done)


if __name__ == "__main__":
    main()
