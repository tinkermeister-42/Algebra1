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
LW = 2.2                      # thin and uniform, as in the originals
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


def spine(x0, y0, x1, y1, bend=0.0, w_top=0.9, w_hip=2.5):
    """The torso, as a filled calligraphic wedge rather than a stroked line.

    In the originals it leaves the base of the head as a point and widens as it
    drops, thickest at the hip, with a gentle bend.  That taper is most of what
    makes the figure read as a body with mass instead of a stick."""
    dx, dy = x1 - x0, y1 - y0
    L = (dx * dx + dy * dy) ** 0.5 or 1.0
    px, py = -dy / L, dx / L                     # unit perpendicular
    mx, my = (x0 + x1) / 2 + px * bend, (y0 + y1) / 2 + py * bend
    return (f'<path d="M{x0 + px * w_top:.1f},{y0 + py * w_top:.1f} '
            f'Q{mx + px * w_hip * .6:.1f},{my + py * w_hip * .6:.1f} '
            f'{x1 + px * w_hip:.1f},{y1 + py * w_hip:.1f} '
            f'L{x1 - px * w_hip:.1f},{y1 - py * w_hip:.1f} '
            f'Q{mx - px * w_hip * .2:.1f},{my - py * w_hip * .2:.1f} '
            f'{x0 - px * w_top:.1f},{y0 - py * w_top:.1f} Z" fill="{INK}"/>')


def limb(jx, jy, segs, s):
    """A limb as a run of segments from the junction; sharp corners, no easing."""
    pts, x, y, out = [], jx, jy, []
    for dx, dy in segs:
        nx, ny = jx + dx * s, jy + dy * s
        out.append(line(x, y, nx, ny))
        x, y = nx, ny
    return "".join(out), (x, y)


def person(x, y, arms, legs, tilt=0, torso=(0, 46), head_r=(25, 23), bend=0.0, s=1.0):
    """A figure whose neck is the only joint that matters.

    The torso and both arms all leave one junction just under the head - there
    are no shoulders.  Every limb is a run of (dx, dy) segments from that
    junction (arms) or from the far end of the torso (legs), so poses are
    asymmetric by construction and the corners stay sharp.

    (x, y) is the junction.  Returns the drawing, the top of the head, and
    where each hand ended up."""
    tx, ty = x + torso[0] * s, y + torso[1] * s
    parts, hands = [spine(x, y, tx, ty, bend * s, 0.9 * s, 2.5 * s)], []
    for segs in arms:
        d, hand = limb(x, y, segs, s)
        parts.append(d); hands.append(hand)
    for segs in legs:
        d, _ = limb(tx, ty, segs, s)
        parts.append(d)
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
         f'stroke="{INK}" stroke-width="2"/>')
    for k in (0.34, 0.62):
        g += line(x - w * .3, y - h / 2 + h * k, x + w * .3, y - h / 2 + h * k, 1.4)
    return g + "</g>"


def distribute():
    """2.4 - the lesson's own opening story: the teacher hands one worksheet to
    every student, which is exactly what a(b + c) does to each term."""
    W, H = 520, 282
    FLOOR = 240
    b = []

    # Relaxed stand: weight on the near leg, which drops almost straight, while
    # the far one sets down a little wider.  Not a stride, not a wide stance.
    def stand(flip=1):
        return [[(-7 * flip, 36), (-11 * flip, 74)],
                [(11 * flip, 34), (17 * flip, 74)]]

    fig, head_top, hands = person(
        96, 108,
        arms=[[(-15, 27), (-27, 53)],           # trailing arm, relaxed
              [(36, 13), (68, 8)]],             # offering arm
        legs=stand(1), tilt=12, torso=(16, 56), bend=3.5, s=1.02)
    b.append(fig)
    b.append(sheet(*hands[1], tilt=-17, w=19, h=25))
    b.append(bubble(228, 30, 264, 40, (108, head_top - 2), ["Distribute these, please."], size=15))

    for kw, px, tilt in [
        (dict(arms=[[(-19, 29), (-32, 52)], [(29, 11), (53, 21)]],
              legs=stand(-1), tilt=-8, torso=(-11, 56), bend=-3.0), 302, 9),
        (dict(arms=[[(-23, 25), (-36, 50)], [(27, 15), (51, 13)]],
              legs=stand(1), tilt=9, torso=(8, 55), bend=2.8), 420, -8),
    ]:
        f, _, hs = person(px, 115, s=0.96, **kw)
        b.append(f)
        b.append(sheet(*hs[1], tilt=tilt, w=18, h=24))

    b.append(line(28, FLOOR, W - 22, FLOOR, 2.0))
    return svg(W, H, "".join(b),
               "A teacher handing one worksheet to each of two students")


if __name__ == "__main__":
    write("Unit_2/Lesson_4/distribute_worksheets.svg", distribute())
