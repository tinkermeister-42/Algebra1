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
LW = 3.2                      # one stroke weight everywhere, as in the originals
# The originals were hand-lettered.  No such face is guaranteed on a printing
# machine, so these use the same serif as the handout body and let the figures
# carry the character instead of a font imitation.
FONT = "Georgia,'Times New Roman',serif"


def line(x1, y1, x2, y2, w=LW):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{INK}" stroke-width="{w}" stroke-linecap="round"/>'


def circle(cx, cy, r, w=LW, fill="none"):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{w}"/>'


def text(x, y, s, size=20, anchor="middle", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{INK}">{s}</text>')


def person(x, y, arms=((-22, 14, -38, 26), (22, 14, 38, 26)),
           legs=((-17, 46, -14, 84), (17, 46, 14, 84)), s=1.0):
    """A figure with feet at (x, y).

    Limbs bend.  Each one is (elbow_dx, elbow_dy, hand_dx, hand_dy) measured
    from the shoulder or hip, so the joint is what gives the figure motion -
    straight single-segment limbs read as a scarecrow, not an xkcd person.
    No neck: the head sits on the shoulders.

    Returns the drawing, the top of the head (for a speech-bubble tail) and
    where each hand ended up (so a prop can be put in one)."""
    head_r = 19 * s
    # legs are about half the figure's height; short legs read as a toddler
    leg_h, torso = 84 * s, 54 * s
    hip_y = y - leg_h
    sh_y = hip_y - torso
    head_cy = sh_y - head_r + 3 * s
    # torso first, head last and filled, so the line cannot poke into the face
    p = [line(x, sh_y, x, hip_y)]
    hands = []
    for ex, ey, hx, hy in arms:
        jx, jy = x + ex * s, sh_y + (6 + ey) * s
        ax, ay = x + hx * s, sh_y + (6 + hy) * s
        p += [line(x, sh_y + 6 * s, jx, jy), line(jx, jy, ax, ay)]
        hands.append((ax, ay))
    for ex, ey, fx, fy in legs:
        jx, jy = x + ex * s, hip_y + ey * s
        p += [line(x, hip_y, jx, jy), line(jx, jy, x + fx * s, hip_y + fy * s)]
    p.append(circle(x, head_cy, head_r, fill="#fff"))
    return "".join(p), head_cy - head_r, hands


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
    W, H = 660, 276
    b = []

    fig, head_top, hands = person(
        96, 250,
        arms=((-20, 20, -30, 40), (30, 4, 58, -4)),      # left down, right offering
        legs=((-18, 46, -15, 84), (19, 46, 17, 84)), s=1.05)
    b.append(fig)
    b.append(sheet(*hands[1], tilt=-14))          # the sheet is in the outstretched hand
    b.append(bubble(214, 42, 300, 50, (head_top and 108, head_top - 6),
                    ["Distribute these, please."]))

    for x, tilt in ((336, 7), (456, -6), (576, 9)):
        f, _, hs = person(
            x, 256,
            arms=((-20, 14, -32, 26), (22, 10, 38, 2)),   # hand below the elbow, not hooked up
            legs=((-17, 46, -14, 84), (18, 46, 16, 84)), s=0.92)
        b.append(f)
        b.append(sheet(*hs[1], tilt=tilt))

    return svg(W, H, "".join(b),
               "A teacher handing one worksheet to each of three students")


if __name__ == "__main__":
    write("Unit_2/Lesson_4/distribute_worksheets.svg", distribute())
