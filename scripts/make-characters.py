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
# Measured off the originals: the limb stroke is about 2.5% of the head's
# width, and the spine at its thickest is about 2.5 times the limb.
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


def ribbon(pts, w0, w1):
    """A filled stroke of varying width along a polyline.

    The body is one of these: it starts as a point at the base of the head,
    widens down the back and carries straight on into a leg without stopping at
    a hip.  The hip is a bend in the line, not a junction."""
    n = len(pts) - 1
    norms = []
    for k, (x, y) in enumerate(pts):
        ax, ay = pts[max(k - 1, 0)]
        bx, by = pts[min(k + 1, n)]
        dx, dy = bx - ax, by - ay
        L = (dx * dx + dy * dy) ** 0.5 or 1.0
        norms.append((-dy / L, dx / L))
    w = [w0 + (w1 - w0) * (k / n) for k in range(n + 1)]
    left = [(x + nx * w[k], y + ny * w[k]) for k, ((x, y), (nx, ny)) in enumerate(zip(pts, norms))]
    right = [(x - nx * w[k], y - ny * w[k]) for k, ((x, y), (nx, ny)) in enumerate(zip(pts, norms))]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in left)
    d += " L" + " L".join(f"{x:.1f},{y:.1f}" for x, y in reversed(right)) + " Z"
    return f'<path d="{d}" fill="{INK}"/>'


def limb(jx, jy, segs, s):
    """A limb as a run of segments from the junction; sharp corners, no easing."""
    pts, x, y, out = [], jx, jy, []
    for dx, dy in segs:
        nx, ny = jx + dx * s, jy + dy * s
        out.append(line(x, y, nx, ny))
        x, y = nx, ny
    return "".join(out), (x, y)


def person(x, y, arms, spine_leg, other_leg, tilt=0, head_r=(25, 23), s=1.0):
    """A figure built the way the originals are.

    `spine_leg` is the single continuous run from the neck, down the back and
    on into one leg - given as (dx, dy) offsets from the neck.  `other_leg`
    branches off it at `branch`, an index into that run.  Both arms leave the
    neck point.  There is no shoulder and no hip: the neck is the only junction
    and the hip is just a bend.

    (x, y) is the neck.  Returns the drawing, the top of the head, and where
    each hand ended up."""
    segs, branch = spine_leg
    pts = [(x, y)]
    for dx, dy in segs:
        pts.append((x + dx * s, y + dy * s))
    parts = [ribbon(pts, 0.45 * s, 1.6 * s)]

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
    every student, which is exactly what a(b + c) does to each term."""
    W, H = 520, 282
    FLOOR = 240
    b = []

    # neck -> down the back -> hip -> knee -> foot, all one stroke; the second
    # leg branches at the hip, which is index 1 in that run
    def body(lean, kick):
        # points: mid-back, hip, knee, foot - the far leg branches at the hip
        return ([(lean, 30), (lean + 6, 58), (lean + 1, 96), (lean + 5, 132)], 2)

    def far_leg(kick):
        return [(kick * 13, 34), (kick * 20, 74)]

    fig, head_top, hands = person(
        96, 108,
        arms=[[(-15, 27), (-27, 53)],
              [(36, 13), (68, 8)]],
        spine_leg=body(9, 1), other_leg=far_leg(1), tilt=12, s=1.02)
    b.append(fig)
    b.append(sheet(*hands[1], tilt=-17, w=19, h=25))
    b.append(bubble(228, 30, 264, 40, (108, head_top - 2), ["Distribute these, please."], size=15))

    for kw, px, tilt in [
        (dict(arms=[[(-19, 29), (-32, 52)], [(29, 11), (53, 21)]],
              spine_leg=body(-7, -1), other_leg=far_leg(-1), tilt=-8), 302, 9),
        (dict(arms=[[(-23, 25), (-36, 50)], [(27, 15), (51, 13)]],
              spine_leg=body(6, 1), other_leg=far_leg(1), tilt=9), 420, -8),
    ]:
        f, _, hs = person(px, 115, s=0.96, **kw)
        b.append(f)
        b.append(sheet(*hs[1], tilt=tilt, w=18, h=24))

    b.append(line(28, FLOOR, W - 22, FLOOR, 1.3))
    return svg(W, H, "".join(b),
               "A teacher handing one worksheet to each of two students")


if __name__ == "__main__":
    write("Unit_2/Lesson_4/distribute_worksheets.svg", distribute())
