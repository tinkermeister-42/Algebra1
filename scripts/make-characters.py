#!/usr/bin/env python3
"""Stick-figure scenes for the lessons, in the style of the stairs and the
Cookie Caper: plain black outlines, circle head, straight limbs, no fill.

SVG rather than PNG so they stay crisp in print and stay small - the same
choice already made for the pizzas in 1.5.

Run from the repo root:  python3 scripts/make-characters.py
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
INK = "#111"
# Measured off the originals: the stroke is about 2.5% of the head's width,
# and it is the same everywhere - body, limbs and head alike.
LW = 1.3
# The originals were hand-lettered.  No such face is guaranteed on a printing
# machine, so these use the same serif as the handout body and let the figures
# carry the character instead of a font imitation.
FONT = "Georgia,'Times New Roman',serif"


def line(x1, y1, x2, y2, w=LW):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{INK}" stroke-width="{w}" stroke-linecap="round"/>')


def circle(cx, cy, r, w=LW, fill="none"):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{INK}" stroke-width="{w}"/>')


def head(cx, cy, rx, ry, tilt=0, w=LW):
    """A slightly oval head, tilted into the direction of travel."""
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'transform="rotate({tilt} {cx:.1f} {cy:.1f})" fill="#fff" '
            f'stroke="{INK}" stroke-width="{w}"/>')


def text(x, y, s, size=20, anchor="middle", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{INK}">{s}</text>')


def arc(x1, y1, x2, y2, bow=0.0, w=LW):
    """A line with a slight bow to it.

    Nothing in a body is straight in silhouette.  A rigid segment reads as a
    stick; the same segment bowed a couple of percent of its length reads as an
    arm.  This is most of the difference between a stick figure and a stick
    figure that looks alive, and it is deliberately small - too much and it
    stops looking like a stick figure at all."""
    if not bow:
        return line(x1, y1, x2, y2, w)
    dx, dy = x2 - x1, y2 - y1
    L = (dx * dx + dy * dy) ** 0.5 or 1.0
    cx = (x1 + x2) / 2 - dy / L * bow
    cy = (y1 + y2) / 2 + dx / L * bow
    return (f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round"/>')


def limb(jx, jy, segs, s):
    """A limb as a run of segments from the junction, each optionally bowed.

    A segment is (dx, dy) or (dx, dy, bow); the corner at the joint stays sharp."""
    x, y, out = jx, jy, []
    for seg in segs:
        dx, dy = seg[0], seg[1]
        bow = seg[2] if len(seg) > 2 else 0.0
        nx, ny = jx + dx * s, jy + dy * s
        out.append(arc(x, y, nx, ny, bow * s))
        x, y = nx, ny
    return "".join(out), (x, y)


def person(x, y, arms, spine_leg, other_leg, tilt=0, head_r=(25, 23),
           spine_bow=None, s=1.0):
    """A figure built the way the originals are.

    `spine_leg` is the single continuous run from the neck, down the back and
    on into one leg - given as (dx, dy) offsets from the neck.  `other_leg`
    branches off it at `branch`, an index into that run.  Both arms leave the
    neck point.  There is no shoulder and no hip: the neck is the only junction
    and the hip is just a bend.

    Every line is the same width.  What is distinctive is only how it is
    constructed - one unbroken run from head to foot with a leg branching off -
    not any difference in weight.

    (x, y) is the neck.  Returns the drawing, the top of the head, and where
    each hand ended up."""
    segs, branch = spine_leg
    pts = [(x, y)]
    for dx, dy in segs:
        pts.append((x + dx * s, y + dy * s))
    # one uniform stroke the whole way, head to foot; the far leg branches off it
    bows = spine_bow if spine_bow else [0] * (len(pts) - 1)
    parts = [arc(*pts[k], *pts[k + 1], bows[k] * s) for k in range(len(pts) - 1)]

    bx, by = pts[branch]
    px_, py_ = bx, by
    for dx, dy in other_leg:
        nx, ny = bx + dx * s, by + dy * s
        parts.append(line(px_, py_, nx, ny))
        px_, py_ = nx, ny

    hands = []
    for a in arms:
        d, hand = limb(x, y, a, s)
        parts.append(d); hands.append(hand)

    rx, ry = head_r[0] * s, head_r[1] * s
    hcy = y - ry + 2 * s
    parts.append(head(x, hcy, rx, ry, tilt))
    return "".join(parts), hcy - ry, hands


def bubble(x, y, w, h, tail_to, lines, size=17):
    """A rounded speech bubble with a straight tail."""
    tx, ty = tail_to
    parts = [f'<rect x="{x-w/2:.1f}" y="{y-h/2:.1f}" width="{w}" height="{h}" rx="10" '
             f'fill="#fff" stroke="{INK}" stroke-width="{LW}"/>',
             line(x, y + h / 2, tx, ty, LW)]
    n = len(lines)
    for i, s in enumerate(lines):
        parts.append(text(x, y - (n - 1) * (size * .62) + i * (size * 1.24) + size * .34, s, size))
    return "".join(parts)


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
            f'<rect width="{w}" height="{h}" fill="#fff"/>{body}</svg>\n')


def write(rel, content):
    p = os.path.normpath(os.path.join(OUT, rel))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(content)
    print("wrote images/%s  (%d bytes)" % (rel, len(content)))


# ---------------------------------------------------------------- scenes ----

def sheet(x, y, w=17, h=22, tilt=0):
    """A worksheet: a small page with two ruled lines."""
    g = (f'<g transform="rotate({tilt} {x} {y})">'
         f'<rect x="{x-w/2:.1f}" y="{y-h/2:.1f}" width="{w}" height="{h}" fill="#fff" '
         f'stroke="{INK}" stroke-width="1.3"/>')
    for k in (0.34, 0.62):
        g += line(x - w * .3, y - h / 2 + h * k, x + w * .3, y - h / 2 + h * k, 0.9)
    return g + "</g>"


def distribute():
    """2.4 - the lesson's own opening story: the teacher hands one worksheet to
    every student, which is exactly what a(b + c) does to each term.

    Three attitudes rather than three copies: one offering, one taking, one
    already reading hers.  The bows and leans are deliberately small - just
    enough to stop a correct pose reading as a mannequin, not so much that it
    turns into mime."""
    W, H = 520, 292
    FLOOR = 250
    b = []

    # --- offering ------------------------------------------------------------
    fig, head_top, hands = person(
        104, 100,
        arms=[[(-9, 33, 1.2), (-7, 63, 0.8)],
              [(18, 22, -1.4), (46, 16, -1.8)]],
        spine_leg=([(3, 32), (8, 62), (3, 104), (-2, 146)], 2),
        other_leg=[(20, 44), (25, 84)],
        spine_bow=[1.4, 1.6, -0.9, -0.5], tilt=7, s=1.0)
    b.append(fig)
    b.append(bubble(240, 30, 258, 38, (114, head_top - 2), ["Distribute these, please."], size=15))
    gx, gy = hands[1]
    b.append(sheet(gx + 8, gy + 1, tilt=-9, w=18, h=24))     # held in the giving hand

    # --- taking it -----------------------------------------------------------
    f, _, hs = person(
        226, 106,
        arms=[[(10, 33, -1.1), (8, 63, -0.7)],
              [(-17, 22, 1.4), (-42, 17, 1.8)]],
        spine_leg=([(-3, 32), (-8, 62), (-3, 104), (2, 146)], 2),
        other_leg=[(-20, 44), (-25, 84)],
        spine_bow=[-1.3, -1.5, 0.8, 0.5], tilt=-6, s=0.95)
    b.append(f)

    # --- already has one, reading it ----------------------------------------
    f, _, hs = person(
        392, 110,
        arms=[[(-13, 32, 1.3), (-14, 61, 0.9)],      # hanging, swung clear of the back
              [(17, 17, -1.0), (33, 15, -1.3)]],      # up in front, holding it to read
        spine_leg=([(3, 32), (7, 62), (2, 104), (-3, 146)], 2),
        other_leg=[(19, 44), (24, 84)],
        spine_bow=[1.4, 1.6, -0.8, -0.4], tilt=9, s=0.93)
    b.append(f)
    b.append(sheet(hs[1][0] + 6, hs[1][1] - 3, tilt=6, w=19, h=25))

    b.append(line(30, FLOOR, W - 24, FLOOR, 1.3))
    return svg(W, H, "".join(b),
               "A teacher handing a worksheet to one student while another reads hers")


if __name__ == "__main__":
    write("Unit_2/Lesson_4/distribute_worksheets.svg", distribute())
