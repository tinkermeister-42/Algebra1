#!/usr/bin/env python3
"""The blank circle for EX 1 of the 1.4 handout.

The lesson's own figure (fourth_of_a_half.png, from tools/PieCharts.ipynb)
has the half shaded grey and the answering eighth shaded blue, which is right
there - the prose points at that blue slice.  On the handout the same picture
asks the student to shade it, so it has to arrive empty: eight equal pieces,
nothing filled, and the student shades a half and then a fourth of that half.

    python3 scripts/make-lesson-1-4-figures.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..", "images", "Unit_1", "Lesson_4")


def blank_eighths(path):
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie([1] * 8, colors=["#ffffff"] * 8, startangle=90,
           wedgeprops={"linewidth": 1.4, "edgecolor": "#555555"})
    ax.axis("equal")
    plt.tight_layout()
    fig.savefig(path, dpi=300, transparent=False)
    plt.close(fig)
    print("wrote", os.path.relpath(path, os.path.join(OUT, "..", "..", "..")))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    blank_eighths(os.path.join(OUT, "eighths_blank.png"))
