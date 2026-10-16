# -*- coding: utf-8 -*-
"""Append Lecturer's Closing Remarks (~420 words) to every chapter _b."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chapters_data import CHAPTERS
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CONTENT = os.path.join(ROOT, "book2", "content")
MARK = "## 21. Lecturer's Closing Remarks"

def main():
    with open(os.path.join(CONTENT, "manifest.json")) as fh:
        manifest = json.load(fh)
    titles = [c[1] for c in CHAPTERS]
    done = 0
    for part in manifest["parts"]:
        for ch in part["chapters"]:
            idx = int(ch["number"]) - 1
            title, subtitle, focus, concepts, lens = CHAPTERS[idx][1:6]
            nxt = titles[idx + 1] if idx + 1 < len(titles) else None
            fb = os.path.join(CONTENT, ch["files"][1])
            text = open(fb, encoding="utf-8").read()
            if MARK in text:
                continue
            if nxt:
                bridge = ("The next chapter, *%s*, takes up the story from here. Students will "
                          "understand it better for having mastered this chapter's account of %s, "
                          "because the two subjects interlock: development does not proceed domain by "
                          "domain in the adolescent, only in the textbook, and the lecturer's task in "
                          "the coming session is to restore the connections that the chapter structure "
                          "has necessarily separated. Come to that session with your consolidation "
                          "paragraphs written; they are the bridge on which the next chapter is built."
                          % (nxt, concepts[0]))
            else:
                bridge = ("This is the final chapter of the book. Its closing task is integration: to "
                          "hold the biological, cognitive, psychosocial, cultural and applied strands "
                          "of CAC. 702 together as a single developmental way of seeing adolescents, "
                          "and to carry that way of seeing into examination, portfolio, supervised "
                          "practice and the remainder of the programme. The book ends where "
                          "professional life begins: with an adolescent, a set of adults, a limited "
                          "amount of time, and a counsellor who can think developmentally under all "
                          "three pressures at once.")
            extra = """
%s and Bridge Forward

Let me close this chapter as I would close the lecture, by saying plainly what I most want you to carry out of the room. The subject of this chapter — %s — is not an examination topic that happens to have practical uses; it is a piece of the daily reality of every adolescent you will ever counsel, whether it arrives named in the referral or hidden inside some other complaint. %s. That is the claim of the chapter, and everything in it — the concepts of %s, the mechanisms, the case, the laboratory — was arranged to make that claim observable rather than merely assertable.

Notice, too, what the chapter has asked of you as a reader. It has asked you to hold a general pattern and an individual adolescent in mind at the same time, to prefer mechanisms to labels, trajectories to snapshots and predictions to impressions, and to treat families, schools, peers and digital worlds as part of the case rather than as background to it. Those habits are the course. A student who finishes CAC. 702 with the habits but imperfect recall of detail is well educated for practice, because detail can always be looked up in this book; a student with perfect recall and none of the habits has acquired a vocabulary, not a profession.

Two cautions before you turn the page. First, developmental knowledge is easily misused as a new way of sounding certain about adolescents, and certainty is the enemy this book has opposed from its first chapter: hold what you have learned here as a set of well-supported hypotheses, and let each real adolescent test them. Second, do not let the scale of adolescent need, which this chapter may have made more visible to you, become a reason for professional despair or for its opposite, heroic over-involvement. The evidence reviewed here points the other way: ordinary systems, steadily strengthened — one changed adult response, one repaired routine, one school condition adjusted, one adolescent who discovers that an adult can be trusted with the truth — are how development is actually helped.

%s

**For the seminar leader.** The closing discussion should return to the chapter's review questions, sample two consolidation entries from the group, and end by asking each student to state, in one sentence, the developmental idea from this chapter they expect to use soonest in practice. Record the sentences; revisited at the end of the course in Chapter 58, they make the growth of the group's developmental thinking visible to itself.
""" % (MARK, title.lower(), focus[0].upper() + focus[1:], ", ".join(concepts[:4]), bridge)
            open(fb, "w", encoding="utf-8").write(text.rstrip() + "\n" + extra)
            done += 1
    print("closing remarks added:", done)

if __name__ == "__main__":
    main()
