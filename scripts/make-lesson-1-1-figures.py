#!/usr/bin/env python3
"""Number-line figures for lesson 1.1.

Ordering figures deliberately carry no distance brackets: a bracket labelled
"7 units" next to a question about which number is greater teaches magnitude,
which is the opposite of the point.  Distance annotation belongs only on the
absolute-value figure.

Run from the repo root:  python3 scripts/make-lesson-1-1-figures.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..", "images", "Unit_1", "Lesson_1")
LO, HI = -10, 10
BLUE, RED = "#0000ff", "#ff0000"


def base(ax):
    ax.set_xlim(LO - 1.6, HI + 1.6)
    ax.set_ylim(-1.15, 1.25)
    ax.axis("off")
    ax.annotate("", xy=(HI + 1.5, 0), xytext=(LO - 1.5, 0),
                arrowprops=dict(arrowstyle="<|-|>", color="black", lw=1.8,
                                mutation_scale=22, shrinkA=0, shrinkB=0))
    for v in range(LO, HI + 1):
        ax.plot([v, v], [-0.16, 0.16], color="black", lw=1.6, solid_capstyle="butt")
        ax.text(v, -0.42, str(v), ha="center", va="top", fontsize=13)


def dot(ax, v, color):
    ax.plot([v], [0], "o", color=color, markersize=15, zorder=3)


def figure(name, marks, arrow=None):
    fig, ax = plt.subplots(figsize=(10, 2.6), dpi=100)
    base(ax)
    for v, c in marks:
        dot(ax, v, c)
    if arrow:
        # a "greater this way" rail above the line
        ax.annotate("", xy=(HI - 0.4, 0.82), xytext=(LO + 0.4, 0.82),
                    arrowprops=dict(arrowstyle="-|>", color="#2c5f8a", lw=2.2,
                                    mutation_scale=20))
        ax.text(0, 1.0, arrow, ha="center", va="bottom", fontsize=13.5,
                color="#2c5f8a", style="italic")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    p = os.path.join(OUT, name)
    fig.savefig(p, transparent=False, facecolor="white")
    plt.close(fig)
    print("wrote", os.path.relpath(p))


if __name__ == "__main__":
    figure("order_2_and_neg7.png",  [(-7, RED), (2, BLUE)],  "greater this way")
    figure("order_neg4_and_neg5.png", [(-5, RED), (-4, BLUE)], "greater this way")
