#!/usr/bin/env python
"""Additional diagrams for the manuscript.

Generates the supplementary figures that were not part of the original
86-diagram set.  Run from the repository root:

    .venv/bin/python book/build/make_extra_figures.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIGDIR = os.path.join(ROOT, "book", "figures")
os.makedirs(FIGDIR, exist_ok=True)

NAVY = "#173A5E"
TEAL = "#1F7A72"
OCHRE = "#C08A2E"
PLUM = "#7A3E7A"
SLATE = "#4A5A6A"
LIGHT = "#EDF2F5"
RULE = "#9AAAB8"

plt.rcParams["font.family"] = "DejaVu Sans"


def _box(ax, x, y, w, h, label, fc=LIGHT, ec=NAVY, fs=8.6, tc=NAVY, lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor=fc, edgecolor=ec, linewidth=lw,
                                zorder=3))
    ax.text(x + w / 2.0, y + h / 2.0, label, ha="center", va="center",
            fontsize=fs, color=tc, zorder=4, linespacing=1.35)


def _line(ax, p0, p1, color=SLATE, lw=1.3, ls="-"):
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=color, lw=lw,
            linestyle=ls, zorder=2, solid_capstyle="round")


def fig87_genogram():
    """A three-generation genogram with the standard relationship symbols."""
    fig, ax = plt.subplots(figsize=(9.2, 5.9))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 88)
    ax.axis("off")

    ax.text(50, 85.5, "A Three-Generation Genogram", ha="center", va="center",
            fontsize=13, color=NAVY, fontweight="bold")
    ax.text(50, 80.2, "structure, relationships, and emotional process",
            ha="center", va="center", fontsize=8.6, color=SLATE)

    # ---- generation I -------------------------------------------------
    _box(ax, 33, 66, 15, 7.5, "GRANDMOTHER", fc="#F3E9F3", ec=PLUM, fs=7.6)
    _box(ax, 52, 66, 15, 7.5, "GRANDFATHER", fc="#F3E9F3", ec=PLUM, fs=7.6)
    _line(ax, (48, 69.7), (52, 69.7), color=PLUM, lw=1.8)      # marriage
    ax.text(50, 71.4, "△", ha="center", va="bottom", fontsize=8, color=PLUM)

    # ---- generation II ------------------------------------------------
    _box(ax, 22, 45, 16, 7.5, "MOTHER", fc=LIGHT, ec=NAVY)
    _box(ax, 43, 45, 16, 7.5, "FATHER", fc=LIGHT, ec=NAVY)
    _line(ax, (38, 48.7), (43, 48.7), color=NAVY, lw=1.8)
    ax.text(40.5, 50.4, "△", ha="center", va="bottom", fontsize=8, color=NAVY)

    # ---- generation III -----------------------------------------------
    _box(ax, 8, 24, 15, 7.5, "YOUNG PERSON\n(identified)", fc="#DCEAF2",
         ec=NAVY, fs=7.4)
    _box(ax, 28, 24, 15, 7.5, "SIBLING", fc=LIGHT, ec=NAVY)
    _box(ax, 48, 24, 15, 7.5, "SIBLING", fc=LIGHT, ec=NAVY)
    _box(ax, 68, 24, 15, 7.5, "SIBLING", fc=LIGHT, ec=NAVY)

    # descent: grandparents -> parental couple
    _line(ax, (50, 66), (50, 60.0), color=SLATE, lw=1.2)
    _line(ax, (40.5, 60.0), (50, 60.0), color=SLATE, lw=1.2)
    _line(ax, (40.5, 60.0), (40.5, 52.5), color=SLATE, lw=1.2)

    # transmission arrow (grandparent generation -> parental generation)
    ax.annotate("", xy=(40.5, 54.0), xytext=(40.5, 60.0),
                arrowprops=dict(arrowstyle="-|>", color=OCHRE, lw=1.9))
    ax.text(42.2, 57.0, "transmission", fontsize=7.8, color=OCHRE, va="center")

    # descent: parental couple -> children
    _line(ax, (40.5, 45), (40.5, 38.0), color=SLATE, lw=1.2)
    _line(ax, (15.5, 38.0), (75.5, 38.0), color=SLATE, lw=1.2)
    for cx in (15.5, 35.5, 55.5, 75.5):
        _line(ax, (cx, 38.0), (cx, 31.5), color=SLATE, lw=1.2)

    # projection arrow (mother -> identified young person)
    ax.annotate("", xy=(16.5, 31.8), xytext=(26.0, 44.6),
                arrowprops=dict(arrowstyle="-|>", color=PLUM, lw=1.9,
                                connectionstyle="arc3,rad=-0.18"))
    ax.text(25.0, 39.0, "projection", fontsize=7.8, color=PLUM, va="center",
            ha="left")

    # ---- relationship symbols between siblings -------------------------
    # close: sibling 2 <-> sibling 3
    ax.plot([43.0, 48.0], [35.4, 35.4], color=TEAL, lw=2.2)
    ax.plot([43.0, 48.0], [33.6, 33.6], color=TEAL, lw=2.2)
    ax.text(45.5, 36.6, "close", fontsize=6.9, color=TEAL, ha="center")

    # conflict: sibling 3 <-> sibling 4
    for k in range(5):
        ax.plot([63.0 + k * 1.2, 64.2 + k * 1.2], [33.4, 35.6],
                color="#9A4A2A", lw=1.1)
    ax.text(65.6, 36.6, "conflict", fontsize=6.9, color="#9A4A2A", ha="center")

    # cut-off: sibling 3 cut off from the family
    ax.plot([55.5, 55.5], [31.5, 33.2], color=PLUM, lw=2.2)
    ax.plot([54.2, 56.8], [33.2, 33.2], color=PLUM, lw=2.2)
    ax.text(55.5, 30.0, "cut-off", fontsize=6.9, color=PLUM, ha="center")

    # ---- legend -------------------------------------------------------
    ax.add_patch(Rectangle((4, 2), 92, 12.5, facecolor="#FAFBFC",
                           edgecolor=RULE, lw=0.9, zorder=1))
    ax.text(7, 11.6, "KEY", fontsize=7.6, color=NAVY, fontweight="bold")
    ax.add_patch(Rectangle((17.5, 10.3), 2.6, 2.6, facecolor=LIGHT,
                           edgecolor=NAVY, lw=1.2))
    ax.text(21.2, 11.6, "square — male", fontsize=7.3, color=SLATE, va="center")
    ax.add_patch(Circle((43.0, 11.6), 1.3, facecolor="#F3E9F3",
                        edgecolor=PLUM, lw=1.2))
    ax.text(46.2, 11.6, "circle — female", fontsize=7.3, color=SLATE, va="center")
    ax.plot([65.0, 70.0], [11.6, 11.6], color=SLATE, lw=1.4)
    ax.text(71.4, 11.6, "marital / descent", fontsize=7.3, color=SLATE,
            va="center")
    ax.text(7, 5.6, "━━  close        ╱╱  conflict        ┬  cut-off"
                    "        △  triangle (a third person joins)",
            fontsize=7.3, color=SLATE)

    fig.savefig(os.path.join(FIGDIR, "fig87_genogram.png"), dpi=190,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig88_genogram_levels():
    """The three concentric levels of information recorded on a genogram."""
    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 52)
    ax.axis("off")
    ax.text(50, 48.5, "The Three Concentric Levels of the Genogram",
            ha="center", va="center", fontsize=12.5, color=NAVY,
            fontweight="bold")
    ax.text(50, 43.6, "each member is recorded on three bands of data",
            ha="center", va="center", fontsize=8.4, color=SLATE)

    levels = [
        ("SOCIAL", TEAL, "education, occupation, ethnicity, migration,\n"
                         "socio-economic status, and membership of\n"
                         "communities and institutions"),
        ("PSYCHOLOGICAL", PLUM, "significant emotional events, mental illness,\n"
                                "substance use, losses, abuse, relationship\n"
                                "ruptures, and the quality of the alliances"),
        ("MEDICAL", OCHRE, "illnesses, genetic conditions, mental and physical\n"
                           "health, and the causes and dates of death"),
    ]
    y = 33.0
    for name, col, body in levels:
        ax.add_patch(FancyBboxPatch((6, y - 9.6), 88, 10.4,
                                    boxstyle="round,pad=0.012,rounding_size=0.03",
                                    facecolor="#F7F9FA", edgecolor=col, lw=1.5,
                                    zorder=2))
        ax.add_patch(Rectangle((6, y - 9.6), 4.2, 10.4, facecolor=col,
                               edgecolor=col, zorder=3))
        ax.text(14, y - 4.4, name, fontsize=9.6, color=col, va="center",
                fontweight="bold")
        ax.text(35, y - 4.4, body, fontsize=7.6, color=INK if False else "#2A3A48",
                va="center", linespacing=1.5)
        y -= 12.0

    fig.savefig(os.path.join(FIGDIR, "fig88_genogram_levels.png"), dpi=190,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    fig87_genogram()
    fig88_genogram_levels()
    print("extra figures written: 2")
