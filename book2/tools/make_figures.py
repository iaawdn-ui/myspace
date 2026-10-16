# -*- coding: utf-8 -*-
"""Generate all artwork for CAC. 702 Adolescent Development:
cover, 8 part plates, 58 chapter opener plates, 58 pathway diagrams."""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chapters_data import CHAPTERS, PARTS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FIG = os.path.join(ROOT, "book2", "figures")
os.makedirs(FIG, exist_ok=True)

NAVY = "#173A5E"
PALETTE = ["#173A5E", "#1F6F6B", "#6B3E75", "#9B2C2C",
           "#A9741F", "#2E5E8C", "#3E6B35", "#7A3B2E"]
CREAM = "#FBF9F4"


def save(fig, name):
    fig.savefig(os.path.join(FIG, name), dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(name)


def cover():
    fig, ax = plt.subplots(figsize=(7.5, 10))
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, 10); ax.set_ylim(0, 13.33); ax.axis("off")
    # rising growth arcs with nodes: three developmental trajectories
    import numpy as np
    for k, (col, y0, amp) in enumerate([("#E8A33D", 1.2, 2.6), ("#3FA7A0", 0.6, 3.4), ("#B98AC4", 1.8, 1.9)]):
        x = np.linspace(0.7, 9.3, 100)
        y = y0 + amp * (1 - np.exp(-x / 3.2)) * 2.0 + 0.25 * np.sin(x * 1.4 + k)
        ax.plot(x, y + 0.5, color=col, lw=3.2, solid_capstyle="round")
        for xi in [1.2, 3.4, 5.6, 7.8, 9.2]:
            yi = y0 + amp * (1 - np.exp(-xi / 3.2)) * 2.0 + 0.25 * np.sin(xi * 1.4 + k)
            ax.add_patch(Circle((xi, yi + 0.5), 0.16, color=col, zorder=5))
    for r, col in [(3.6, "#2A527C"), (2.7, "#22466C"), (1.8, "#2A527C")]:
        ax.add_patch(Circle((8.4, 2.0), r, fill=False, ec=col, lw=1.4, alpha=0.8))
    ax.text(5, 0.65, "", ha="center", color="white")
    save(fig, "cover.png")


def plate(name, big, title, subtitle, accent, number_line):
    """Abstract plate artwork. Deliberately text-free (except, for chapter
    plates, a single large number) because the renderer draws the part and
    chapter titles itself; lettering inside the art would ghost through."""
    import numpy as np
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.5, 0.5), 9.0, 6.0, boxstyle="round,pad=0.12",
                                fc="white", ec=accent, lw=2.2))
    for k, col in enumerate([accent, "#E8A33D", "#3FA7A0", "#B98AC4"]):
        x = np.linspace(0.9, 9.1, 80)
        yv = 1.15 + 0.62 * k + 0.34 * np.sin(x * 1.25 + k * 1.6) + x * 0.055
        ax.plot(x, yv, color=col, lw=2.6, alpha=0.8, solid_capstyle="round")
        for xi in [2.0, 4.6, 7.2, 8.9]:
            yi = 1.15 + 0.62 * k + 0.34 * np.sin(xi * 1.25 + k * 1.6) + xi * 0.055
            ax.add_patch(Circle((xi, yi), 0.13, color=col, zorder=5))
    for r in (2.6, 1.9, 1.2):
        ax.add_patch(Circle((8.55, 5.6), r, fill=False, ec=accent, lw=1.1, alpha=0.35))
    if big and len(big) <= 3:
        ax.add_patch(Circle((2.15, 5.15), 1.02, fc=accent, ec="none", zorder=6))
        ax.text(2.15, 5.15, big, ha="center", va="center", color="white",
                fontsize=27, weight="bold", family="serif", zorder=7)
    save(fig, name)


def diagram(num, title, concepts, accent):
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis("off")
    ax.text(5, 5.88, "Figure %d. Developmental pathway: %s" % (num, title[:52]),
            ha="center", fontsize=9.5, weight="bold", color="#173A5E")
    cols = [accent, "#1F6F6B", "#A9741F", "#6B3E75", "#2E5E8C", "#9B2C2C"]
    # contexts box (left)
    ax.add_patch(FancyBboxPatch((0.3, 3.55), 2.35, 1.75, boxstyle="round,pad=0.08",
                                fc="#EEF2F6", ec="#173A5E", lw=1.4))
    ax.text(1.47, 4.42, "CONTEXTS\nfamily - school\npeers - culture",
            ha="center", va="center", fontsize=8.2, color="#173A5E")
    # six concept nodes: two columns in the centre
    pos = [(3.05, 4.62), (5.45, 4.62), (3.05, 3.72), (5.45, 3.72), (3.05, 2.82), (5.45, 2.82)]
    for i, ((x, y), lab) in enumerate(zip(pos, list(concepts))):
        w = 2.2
        ax.add_patch(FancyBboxPatch((x, y), w, 0.72, boxstyle="round,pad=0.05",
                                    fc=cols[i % len(cols)], ec="none"))
        short = lab if len(lab) <= 24 else lab[:23] + "-"
        ax.text(x + w / 2, y + 0.36, short, ha="center", va="center",
                fontsize=6.8, color="white", weight="bold")
    # arrows from contexts to middle column, between nodes, and down to outcomes
    for (x1, y1, x2, y2) in [(2.65, 4.7, 3.05, 4.95), (2.65, 4.4, 3.05, 4.05),
                            (2.65, 4.1, 3.05, 3.15),
                            (4.15, 2.82, 4.15, 2.05), (6.55, 2.82, 6.55, 2.05),
                            (1.47, 3.55, 1.47, 2.05)]:
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="->",
                                     mutation_scale=11, color="#3F4A57", lw=1.1))
    # outcomes strip (bottom)
    ax.add_patch(FancyBboxPatch((0.3, 0.95), 9.35, 1.05, boxstyle="round,pad=0.08",
                                fc="#EEF2F6", ec="#173A5E", lw=1.4))
    ax.text(4.97, 1.48, "OUTCOMES\ncompetence - identity - wellbeing - belonging",
            ha="center", va="center", fontsize=8.4, color="#173A5E")
    ax.text(5, 0.22, "Contexts shape core processes; processes accumulate into outcomes; outcomes reshape contexts.",
            ha="center", fontsize=7.4, style="italic", color="#3F4A57")
    save(fig, "fig%02d_developmental_pathway_ch%02d.png" % (num, num))


def main():
    with open(os.path.join(ROOT, "book2", "content", "manifest.json")) as fh:
        manifest = json.load(fh)
    cover()
    for pi, part in enumerate(manifest["parts"]):
        plate(part["opener"], "", part["title"],
              "Part %s of CAC. 702 Adolescent Development" % part["number"],
              PALETTE[pi], "PART %s" % part["number"])
    for pi, part in enumerate(manifest["parts"]):
        for ch in part["chapters"]:
            num = int(ch["number"])
            data = CHAPTERS[num - 1]
            plate(ch["opener"], str(num), ch["title"], ch["subtitle"],
                  PALETTE[pi], "CHAPTER %s  |  PART %s" % (num, part["number"]))
            diagram(num, ch["title"], data[4], PALETTE[pi])
    print("figures done:", len(os.listdir(FIG)))


if __name__ == "__main__":
    main()
