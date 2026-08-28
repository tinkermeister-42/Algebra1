#!/usr/bin/env python3
"""Stick-figure scenes for the lessons, in the style of the stairs and the
Cookie Caper: plain black outlines, circle head, straight limbs, no fill.

SVG rather than PNG so they stay crisp in print and stay small - the same
choice already made for the pizzas in 1.5.

Run from the repo root:

    python3 scripts/make-characters.py            # write every scene's SVG
    python3 scripts/make-characters.py --sheet    # ...and open a contact sheet

The poses are hand-tuned coordinates, so drawing is write-numbers, look,
adjust, repeat.  --sheet renders every scene into one PNG so a pass over the
whole set is one look instead of one screenshot per file.

Needs Pillow: the 6.7 scene reuses the thrower drawn for 6.1 rather than
redrawing him, which means cropping that PNG and embedding it.
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

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


SANS = "'Open Sans',Helvetica,Arial,sans-serif"


def text(x, y, s, size=20, anchor="middle", weight="normal", family=None):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family or FONT}" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
            f'fill="{INK}">{s}</text>')


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


def bubble(x, y, w, h, tail_to, lines, size=17, side=None):
    """A rounded balloon with a short wedge tail - the book's own convention,
    as in the cliff drawing in 4.2.

    The tail is a stubby triangle off the underside of the balloon, not a long
    needle reaching across the panel: it should read as attached to the balloon
    and merely pointing, so it starts wide and ends near the speaker."""
    tx, ty = tail_to
    bx = side if side is not None else max(x - w / 2 + 16, min(x + w / 2 - 16, tx))
    by = y + h / 2
    half = 9
    parts = [f'<rect x="{x-w/2:.1f}" y="{y-h/2:.1f}" width="{w}" height="{h}" rx="10" '
             f'fill="#fff" stroke="{INK}" stroke-width="{LW}"/>',
             f'<path d="M{bx-half:.1f},{by:.1f} L{tx:.1f},{ty:.1f} '
             f'L{bx+half:.1f},{by:.1f} Z" fill="#fff" stroke="{INK}" '
             f'stroke-width="{LW}" stroke-linejoin="round"/>',
             # hide the balloon edge the tail now opens into
             f'<line x1="{bx-half+1.4:.1f}" y1="{by:.1f}" x2="{bx+half-1.4:.1f}" '
             f'y2="{by:.1f}" stroke="#fff" stroke-width="{LW+1.2}"/>']
    n = len(lines)
    for i, ln in enumerate(lines):
        parts.append(text(x, y - (n - 1) * (size * .62) + i * (size * 1.24) + size * .34,
                          ln, size, weight="bold", family=SANS))
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


def dot(x, y, r=3.2):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{INK}"/>'


def dashed(d, w=LW, dash="5 4"):
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w}" '
            f'stroke-dasharray="{dash}"/>')


def card(x, y, w, h, inner, tilt=0):
    """A held card - a coupon, a sign, a formula on an index card.

    `inner` is drawn in the card's own space, centred on (x, y), so the box and
    what is written on it tilt together."""
    g = f'<g transform="rotate({tilt} {x:.1f} {y:.1f})">' if tilt else "<g>"
    return (g + f'<rect x="{x-w/2:.1f}" y="{y-h/2:.1f}" width="{w}" height="{h}" '
            f'fill="#fff" stroke="{INK}" stroke-width="{LW}"/>' + inner + "</g>")


def frac(x, y, num, den, size=15):
    """A stacked fraction, since that is how the book writes them."""
    half = size * .62
    return (text(x, y - size * .28, num, size, family=SANS, weight="bold") +
            line(x - half, y, x + half, y, 1.1) +
            text(x, y + size * .95, den, size, family=SANS, weight="bold"))


def label(x, y, s, size=15):
    """A caption under a panel - the same bold sans the balloons use."""
    return text(x, y, s, size, weight="bold", family=SANS)


def distribute():
    """2.4 - the lesson's own opening story: the teacher hands one worksheet to
    every student, which is exactly what a(b + c) does to each term.

    Three attitudes rather than three copies: one offering, one taking, one
    already reading hers.  The bows and leans are deliberately small - just
    enough to stop a correct pose reading as a mannequin, not so much that it
    turns into mime."""
    # The bubble is the top of the drawing, and it sat all but on the edge of
    # the frame.  Everything is laid out from the floor up, so the room is made
    # by growing the frame and dropping the whole scene into it.
    TOP = 14
    W, H = 520, 292 + TOP
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
    b.append(bubble(206, 24, 196, 32, (116, head_top - 3),
                    ["Distribute these, please."], size=15))
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
    return svg(W, H, f'<g transform="translate(0,{TOP})">' + "".join(b) + "</g>",
               "A teacher handing a worksheet to one student while another reads hers")


def coupon_order(blank=False):
    """1.8 - the lesson's own Coupons and Gift Cards box.  Same $40 item, same
    coupon, same card, two orders, two totals.  The point of order of
    operations in one look, and the arithmetic is already in the callout.

    `blank` leaves the two totals as ruled blanks: in the handout this same
    comparison is EX 12, so the printed figure must not answer it."""
    TOP = 14
    W, H = 660, 300 + TOP
    FLOOR = 252
    b = []

    # the second balloon hangs off the figure's inside shoulder, or it would
    # run off the edge of the frame
    # one holds his coupon up and stands square; the other has the card down
    # and the free hand thrown out, mid-objection.  Mirrored they would read as
    # one drawing twice.
    coupon_pose = dict(arms=[[(-10, 32, 1.2), (-8, 61, 0.8)],
                        [(17, 18, -1.3), (34, 6, -1.5)]],
                  spine_leg=[(3, 32), (8, 62), (3, 104), (-2, 146)],
                  other_leg=[(20, 44), (25, 84)],
                  spine_bow=[1.4, 1.6, -0.9, -0.5], tilt=6)
    card_pose = dict(arms=[[(-16, 12, 1.6), (-34, 2, 2.0)],
                      [(15, 30, -1.1), (32, 26, -1.3)]],
                spine_leg=[(5, 32), (11, 62), (12, 104), (10, 146)],
                other_leg=[(-14, 46), (-22, 84)],
                spine_bow=[1.0, 1.2, -1.4, -1.0], tilt=11)

    for x, said, tag, total, sgn, pose in (
            (140, "Coupon first.", "25% off", "$20.00", 1, coupon_pose),
            (500, "Gift card first.", "$10 card", "$22.50", -1, card_pose)):
        # sgn turns the second one to face the first, so they square off
        def mx(seq):
            return [tuple([v[0] * sgn] + list(v[1:])) if len(v) == 2 else
                    (v[0] * sgn, v[1], v[2] * sgn) for v in seq]

        f, head_top, hands = person(
            x, 120,
            arms=[mx(a) for a in pose["arms"]],
            spine_leg=(mx(pose["spine_leg"]), 2),
            other_leg=mx(pose["other_leg"]),
            spine_bow=[v * sgn for v in pose["spine_bow"]],
            tilt=pose["tilt"] * sgn, s=0.86)
        b.append(f)
        b.append(bubble(x + sgn * 62, 40, 152, 30, (x + sgn * 12, head_top - 3),
                        [said], size=14))
        hx, hy = hands[1]
        b.append(card(hx + 24 * sgn, hy - 4, 54, 26,
                      text(hx + 24 * sgn, hy + 1, tag, 12, family=SANS,
                           weight="bold"), tilt=-7 * sgn))
        if blank:
            b.append(line(x - 46, FLOOR + 34, x + 46, FLOOR + 34, LW))
        else:
            b.append(label(x, FLOOR + 34, total, 26))

    b.append(line(40, FLOOR, W - 40, FLOOR, LW))
    return svg(W, H, f'<g transform="translate(0,{TOP})">' + "".join(b) + "</g>",
               "The same item bought two ways: coupon first costs $20, gift card first costs $22.50")


def special_cases():
    """3.5 - what you are left holding when the variables cancel.  One ends up
    with something that is never true, the other with something always true;
    students routinely swap the two, and the difference is easier to feel as
    two attitudes than to read as two paragraphs."""
    TOP = 14
    W, H = 540, 290 + TOP
    FLOOR = 244
    b = []

    # nothing works - arms out, holding up the contradiction
    f, head_top, hands = person(
        132, 116,
        arms=[[(-24, 14, 1.4), (-46, 26, 1.6)],
              [(20, 16, -1.2), (38, 4, -1.4)]],
        spine_leg=([(2, 32), (6, 62), (2, 104), (-3, 142)], 2),
        other_leg=[(19, 44), (24, 82)], spine_bow=[1.3, 1.5, -0.8, -0.4],
        tilt=-8, s=0.88)
    b.append(f)
    b.append(bubble(186, 38, 140, 30, (146, head_top - 3), ["Nothing works."], size=14))
    hx, hy = hands[1]
    b.append(card(hx + 26, hy - 6, 62, 30,
                  text(hx + 26, hy, "\u22129 = 3", 15, family=SANS, weight="bold"),
                  tilt=-6))
    b.append(label(132, FLOOR + 32, "no solution", 15))

    # everything works - an easy shrug
    f, head_top, hands = person(
        396, 116,
        arms=[[(24, 14, -1.4), (46, 26, -1.6)],
              [(-20, 16, 1.2), (-38, 4, 1.4)]],
        spine_leg=([(-2, 32), (-6, 62), (-2, 104), (3, 142)], 2),
        other_leg=[(-19, 44), (-24, 82)], spine_bow=[-1.3, -1.5, 0.8, 0.4],
        tilt=8, s=0.88)
    b.append(f)
    b.append(bubble(356, 38, 162, 30, (382, head_top - 3), ["Everything works."], size=14))
    hx, hy = hands[1]
    b.append(card(hx - 26, hy - 6, 62, 30,
                  text(hx - 26, hy, "5 = 5", 15, family=SANS, weight="bold"),
                  tilt=6))
    b.append(label(396, FLOOR + 32, "infinitely many solutions", 15))

    b.append(line(34, FLOOR, W - 34, FLOOR, LW))
    return svg(W, H, f'<g transform="translate(0,{TOP})">' + "".join(b) + "</g>",
               "One figure holding minus nine equals three, the other holding five equals five")


def three_ways(blank=False):
    """3.7 - the lesson opens on d = rt and asks what happens when the letter
    you want is not already alone.  Three cards, one formula.

    `blank` empties the two rearranged cards, since solving d = rt for t is
    the handout's own exercise."""
    TOP = 14
    W, H = 500, 280 + TOP
    FLOOR = 240
    b = []

    f, head_top, hands = person(
        118, 116,
        arms=[[(-10, 32, 1.2), (-8, 60, 0.8)],
              [(20, 12, -1.2), (42, 2, -1.5)]],
        spine_leg=([(3, 32), (8, 62), (3, 104), (-2, 138)], 2),
        other_leg=[(20, 42), (25, 80)],
        spine_bow=[1.4, 1.6, -0.9, -0.5], tilt=8, s=0.9)
    b.append(f)
    b.append(bubble(268, 38, 236, 30, (140, head_top - 3),
                    ["Same formula. Pick your letter."], size=14))

    cx, cy = 296, 138
    b.append(card(cx - 88, cy - 2, 76, 54,
                  text(cx - 88, cy + 4, "d = rt", 16, family=SANS, weight="bold"), tilt=-11))
    def rearranged(ox, oy, want, num, den, tilt):
        # "r =" and the fraction are one group, centred together: pushed apart
        # they leave a hole in the middle and crowd the fraction into the border
        inner = text(ox - 14, oy + 6, want + " =", 16, family=SANS, weight="bold")
        inner += (line(ox + 2, oy + 7, ox + 26, oy + 7, LW) if blank
                  else frac(ox + 14, oy + 1, num, den))
        return card(ox, oy, 76, 54, inner, tilt=tilt)

    b.append(rearranged(cx + 4, cy - 10, "r", "d", "t", -2))
    b.append(rearranged(cx + 96, cy - 2, "t", "d", "r", 9))

    b.append(line(30, FLOOR, W - 30, FLOOR, LW))
    return svg(W, H, f'<g transform="translate(0,{TOP})">' + "".join(b) + "</g>",
               "One figure holding three cards: d equals rt, r equals d over t, t equals d over r")


# The thrower in 6.1's BallArc, lifted rather than redrawn.  It already has the
# stance - the arm angled up and away with the hand at about head height, which
# is what a throw looks like - and it is the book's own artwork.
BALLARC = ("Unit_6/Lesson_1/BallArc.png", (28, 458, 228, 676))
BALLARC_HAND = (193, 37)      # where the ball leaves, in crop coordinates
BALLARC_FEET = 213            # the lower foot, same coordinates


def lifted_figure():
    """The cropped thrower as a data URI, so the SVG stays self-contained -
    an SVG shown through <img>, as the handouts do, cannot fetch anything."""
    import base64
    import io
    from PIL import Image
    rel, box = BALLARC
    im = Image.open(os.path.join(OUT, *rel.split("/"))).convert("RGBA").crop(box)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode(), im.size


def thrown_ball():
    """6.7 Example 1 - h(t) = -16t^2 + 40t + 5.  The example asks two questions
    that sound unrelated until you see they are two points on one arc: where it
    lands, and how high it gets.

    The thrower is the one from 6.1, scaled so his hand really is at the five
    feet the example starts from and his feet really are on the ground.  The
    arc is the example's own function sampled at one scale with the figure,
    15px to the foot, so thirty feet towers over him the way it should."""
    TOP = 26
    W, H = 880, 540 + TOP
    FLOOR = 498
    PX_PER_FT = 15.0

    def h(t):
        return -16 * t * t + 40 * t + 5
    t_peak = 40 / 32.0
    t_land = (40 + 1920 ** .5) / 32
    # far enough downrange to give the frame a landscape shape: portrait, it
    # has to be printed small, and small is where the labels stop being legible
    RANGE_FT = 46.0
    X0 = 96

    def pt(t):
        return (X0 + (t / t_land) * RANGE_FT * PX_PER_FT,
                FLOOR - h(t) * PX_PER_FT)

    b = []
    rx, ry = pt(0)

    # scale him by the one measurement that has to be right: hand to feet is
    # the release height, five feet
    data, (iw, ih) = lifted_figure()
    hx, hy = BALLARC_HAND
    k = (5 * PX_PER_FT) / (BALLARC_FEET - hy)
    x = rx - hx * k
    y = FLOOR - BALLARC_FEET * k
    b.append(f'<image x="{x:.1f}" y="{y:.1f}" width="{iw * k:.1f}" '
             f'height="{ih * k:.1f}" href="data:image/png;base64,{data}"/>')

    n = 64
    b.append(dashed("M" + " L".join("%.1f,%.1f" % pt(t_land * k2 / n)
                                    for k2 in range(n + 1))))

    b.append(dashed(f"M{rx:.1f},{ry:.1f} L{rx:.1f},{FLOOR:.1f}", 1.0, "3 4"))
    b.append(text(rx + 11, (ry + FLOOR) / 2 + 6, "5 ft", 20, anchor="start",
                  weight="bold", family=SANS))

    px, py = pt(t_peak)
    b.append(dot(px, py))
    b.append(text(px, py - 15, "maximum height", 22, weight="bold", family=SANS))

    lx, ly = pt(t_land)
    b.append(dot(lx, ly, 4.4))            # the ball itself, where it lands
    b.append(text(lx - 10, ly + 26, "hits the ground", 22, anchor="end",
                  weight="bold", family=SANS))

    b.append(line(10, FLOOR, W - 26, FLOOR, LW))
    return svg(W, H, f'<g transform="translate(0,{TOP})">' + "".join(b) + "</g>",
               "A thrown ball on its parabolic path, released at five feet, "
               "with the maximum height and the landing point marked")


def shorthand():
    """5.1 - the lesson's first sentence: rather than writing x times x times x
    times x, write x to the fourth.  An exponent is shorthand before it is a
    rule, and that is easier to see than to say."""
    TOP = 14
    W, H = 530, 260 + TOP
    FLOOR = 224
    b = []

    f, head_top, hands = person(
        256, 106,
        arms=[[(-22, 30, 1.4), (-52, 40, 1.0)],
              [(20, 10, -1.2), (44, -2, -1.5)]],
        spine_leg=([(3, 32), (8, 62), (3, 100), (-2, 132)], 2),
        other_leg=[(20, 42), (25, 78)],
        spine_bow=[1.4, 1.6, -0.9, -0.5], tilt=9, s=0.86)
    b.append(f)
    b.append(bubble(382, 34, 216, 30, (278, head_top - 3),
                    ["Same thing. Less writing."], size=14))

    # the long way, drooping from the low hand
    lx, ly = hands[0]
    b.append(card(lx - 70, ly + 10, 150, 30,
                  text(lx - 70, ly + 16, "x \u00b7 x \u00b7 x \u00b7 x", 16,
                       family=SANS, weight="bold"), tilt=6))
    # the short way, held up
    rx, ry = hands[1]
    b.append(card(rx + 24, ry - 2, 50, 34,
                  text(rx + 24, ry + 5,
                       'x<tspan dy="-7" font-size="11">4</tspan>', 17,
                       family=SANS, weight="bold"), tilt=-6))

    b.append(line(40, FLOOR, W - 40, FLOOR, LW))
    return svg(W, H, f'<g transform="translate(0,{TOP})">' + "".join(b) + "</g>",
               "A figure holding x times x times x times x in one hand and x to the fourth in the other")


# ---------------------------------------------------------- contact sheet ----

# Every scene in the file: where its SVG belongs under images/, and how to draw
# it.  Add a scene by writing the function and adding one line here - both the
# write and the contact sheet pick it up from this.
SCENES = [
    ("Unit_1/Lesson_8/coupon_order.svg", coupon_order),
    ("Unit_1/Lesson_8/coupon_order_blank.svg", lambda: coupon_order(blank=True)),
    ("Unit_2/Lesson_4/distribute_worksheets.svg", distribute),
    ("Unit_3/Lesson_5/no_solution_or_all.svg", special_cases),
    ("Unit_3/Lesson_7/formula_three_ways.svg", three_ways),
    ("Unit_3/Lesson_7/formula_three_ways_blank.svg", lambda: three_ways(blank=True)),
    ("Unit_5/Lesson_1/exponent_shorthand.svg", shorthand),
    ("Unit_6/Lesson_7/thrown_ball.svg", thrown_ball),
]


def find_chromium():
    """Whatever Chrome this machine has.  Quarto's own is the first guess
    because a machine that can render the book already has one."""
    cand = [os.environ.get("QUARTO_CHROMIUM")]
    cand += sorted(glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome"))
    cand += [shutil.which(n) for n in
             ("chromium", "chromium-browser", "google-chrome", "chrome")]
    cand += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    for c in cand:
        if c and os.path.exists(c):
            return c
    return None


def dims(svg_text):
    """The width and height off the <svg> tag."""
    def n(attr):
        i = svg_text.index(attr + '="') + len(attr) + 2
        return int(float(svg_text[i:svg_text.index('"', i)]))
    return n("width"), n("height")


# Headless Chrome still reserves room for browser UI it never draws: the
# viewport comes out exactly this much shorter than --window-size, and anything
# past it is cut.  Measured, not guessed - ask a page for its own innerHeight
# and the difference is the same at every window size.
CHROME_UI = 87


def contact_sheet(scenes, out, scale=2):
    """Render every scene into one PNG, captioned, one above the next.

    Chrome shoots the viewport, not the page, so the window is sized to the
    laid-out height (plus the UI it withholds) rather than trusting it to
    capture past the fold.  That leaves a blank band at the bottom, which is
    cropped back off if Pillow is around to do it."""
    chrome = find_chromium()
    if not chrome:
        print("no chrome found - set QUARTO_CHROMIUM to one", file=sys.stderr)
        return None

    PAD, GAP, CAP = 20, 26, 22
    blocks, width, height = [], 0, PAD
    for rel, content in scenes:
        w, h = dims(content)
        width = max(width, w)
        height += CAP + h + GAP
        blocks.append(
            f'<figure><figcaption>{rel}</figcaption>{content}</figure>')
    height += PAD - GAP
    width += 2 * PAD + 4          # slack so the frame's right edge isn't clipped

    html = (
        '<meta charset="utf-8"><style>'
        f'body{{margin:0;padding:{PAD}px;background:#fff;'
        "font:12px/1 ui-monospace,Menlo,Consolas,monospace;color:#666}}"
        f"figure{{margin:0 0 {GAP}px}}"
        f"figcaption{{height:{CAP}px}}"
        "svg{display:block;outline:1px solid #e3e3e3}"
        "</style>" + "".join(blocks))

    with tempfile.TemporaryDirectory() as d:
        page = os.path.join(d, "sheet.html")
        open(page, "w").write(html)
        subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-sandbox",
             "--hide-scrollbars", f"--force-device-scale-factor={scale}",
             f"--window-size={width},{height + CHROME_UI}",
             f"--screenshot={out}", "file://" + page],
            capture_output=True)
    if not os.path.exists(out):
        return None
    try:
        from PIL import Image
        im = Image.open(out)
        im.crop((0, 0, im.width, min(im.height, height * scale))).save(out)
    except ImportError:
        pass
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--sheet"]
    drawn = [(rel, fn()) for rel, fn in SCENES
             if not args or any(a in rel for a in args)]
    if not drawn:
        print("no scene matches %s" % " ".join(args), file=sys.stderr)
        raise SystemExit(1)
    for rel, content in drawn:
        write(rel, content)

    if "--sheet" in sys.argv[1:]:
        out = os.path.join(tempfile.gettempdir(), "characters-sheet.png")
        got = contact_sheet(drawn, out)
        if got:
            print("contact sheet: %s" % got)
