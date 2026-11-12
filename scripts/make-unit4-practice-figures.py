#!/usr/bin/env python3
"""Figures for the 4.4 Writing Linear Equations extra practice sheet.

The two graphs copy the look of the lesson's own practice graphs
(images/Unit_4/Lesson_4/Question*.png): a -7 to 7 grid, every unit labelled,
one blue line.  They are SVG so they print sharp.  The rectangle for the
parallel and perpendicular part is a plain sketch with no grid, so a student
has to find side BC from the slopes, not read corner C off the picture.

    python3 scripts/make-unit4-practice-figures.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "chapters", "Assessments", "Unit_4", "images")
plt.rcParams["svg.fonttype"] = "path"


def graph(path, m, b, lim=7):
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_xticks(range(-lim, lim + 1))
    ax.set_yticks(range(-lim, lim + 1))
    ax.grid(True, color="#d0d0d0", linewidth=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(1.2)
    ax.tick_params(labelsize=8, length=3)
    # keep 0 off both axes: one "0" at the origin is clutter, two is worse
    ax.set_xticklabels(["" if v == 0 else str(v).replace("-", "−")
                        for v in range(-lim, lim + 1)])
    ax.set_yticklabels(["" if v == 0 else str(v).replace("-", "−")
                        for v in range(-lim, lim + 1)])
    ax.plot(lim, 0, ">k", ms=5, clip_on=False)
    ax.plot(-lim, 0, "<k", ms=5, clip_on=False)
    ax.plot(0, lim, "^k", ms=5, clip_on=False)
    ax.plot(0, -lim, "vk", ms=5, clip_on=False)
    ax.text(lim + 0.5, 0.3, "x", fontsize=10, style="italic")
    ax.text(0.3, lim + 0.4, "y", fontsize=10, style="italic")
    xs = [-lim, lim]
    ax.plot(xs, [m * x + b for x in xs], color="#1f77b4", linewidth=2.2)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print("wrote", os.path.relpath(path))


def rectangle(path):
    pts = {"A": (0, 1), "B": (4, 3), "C": (3, 5), "D": (-1, 3)}
    fig, ax = plt.subplots(figsize=(2.6, 1.9))
    ring = [pts[k] for k in "ABCDA"]
    ax.plot([p[0] for p in ring], [p[1] for p in ring], color="#111", linewidth=1.6)
    for k, p in pts.items():
        ax.plot(*p, "o", color="#111", ms=3.5)
    # right-angle mark at B, along BA and BC
    u = (-0.4 * 2 / 2.236, -0.4 * 1 / 2.236)     # toward A
    v = (-0.4 * 1 / 2.236, 0.4 * 2 / 2.236)      # toward C
    bx, by = pts["B"]
    ax.plot([bx + u[0], bx + u[0] + v[0], bx + v[0]],
            [by + u[1], by + u[1] + v[1], by + v[1]], color="#111", linewidth=1)
    font = dict(fontsize=10, family="serif")
    ax.text(-0.3, 0.35, "A(0, 1)", **font)
    ax.text(4.2, 2.75, "B(4, 3)", **font)
    ax.text(3.15, 5.15, "C", **font)
    ax.text(-1.55, 3.1, "D", **font)
    ax.set_xlim(-2, 6.2)
    ax.set_ylim(0, 6)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(path, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print("wrote", os.path.relpath(path))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    graph(os.path.join(OUT, "wle_graph_a.svg"), -3, 2)
    graph(os.path.join(OUT, "wle_graph_b.svg"), 0.75, -2)
    rectangle(os.path.join(OUT, "wle_rectangle.svg"))
