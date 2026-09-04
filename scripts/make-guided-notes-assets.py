#!/usr/bin/env python3
"""Generate the shared SVG graphics used by the guided-notes handouts.

Run from the repo root:  python3 scripts/make-guided-notes-assets.py
Writes into guided_notes/assets/. The handouts reference these with <img>
(not CSS backgrounds) so they still print when "background graphics" is off.
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "guided_notes", "assets")
FONT = "Georgia, 'Times New Roman', serif"


def number_line(labels=None, n_ticks=21, width=700, height=58):
    """Horizontal number line. `labels` is a list of tick labels, or None for blank."""
    x0, x1, y = 22, width - 22, 24
    step = (x1 - x0) / (n_ticks - 1)
    mid = (n_ticks - 1) / 2
    parts = [
        f'<line x1="{x0-14}" y1="{y}" x2="{x1+14}" y2="{y}" stroke="#111" stroke-width="1.8"/>',
        f'<polygon points="{x0-20},{y} {x0-8},{y-5} {x0-8},{y+5}" fill="#111"/>',
        f'<polygon points="{x1+20},{y} {x1+8},{y-5} {x1+8},{y+5}" fill="#111"/>',
    ]
    for i in range(n_ticks):
        x = x0 + i * step
        big = (i == mid)
        h, sw = (9, 2.5) if big else (6, 1.6)
        parts.append(f'<line x1="{x:.1f}" y1="{y-h}" x2="{x:.1f}" y2="{y+h}" '
                     f'stroke="#111" stroke-width="{sw}"/>')
        if labels:
            parts.append(f'<text x="{x:.1f}" y="{y+24}" text-anchor="middle" font-size="12" '
                         f'font-family="{FONT}" fill="#111">{labels[i]}</text>')
    return svg(width, height, parts)


def grid(width=340, half=10, labelled=True, axis_step=5):
    """Square coordinate plane from -half to +half on both axes."""
    pad = 16
    span = width - 2 * pad
    cell = span / (2 * half)
    cx = cy = pad + span / 2
    parts = []
    # minor grid
    for i in range(2 * half + 1):
        p = pad + i * cell
        parts.append(f'<line x1="{p:.2f}" y1="{pad}" x2="{p:.2f}" y2="{pad+span}" '
                     f'stroke="#c9d2da" stroke-width="0.6"/>')
        parts.append(f'<line x1="{pad}" y1="{p:.2f}" x2="{pad+span}" y2="{p:.2f}" '
                     f'stroke="#c9d2da" stroke-width="0.6"/>')
    # axes with arrowheads
    parts.append(f'<line x1="{pad-6}" y1="{cy:.2f}" x2="{pad+span+6}" y2="{cy:.2f}" '
                 f'stroke="#111" stroke-width="1.4"/>')
    parts.append(f'<line x1="{cx:.2f}" y1="{pad-6}" x2="{cx:.2f}" y2="{pad+span+6}" '
                 f'stroke="#111" stroke-width="1.4"/>')
    for pts in (f'{pad+span+11},{cy:.2f} {pad+span+2},{cy-4:.2f} {pad+span+2},{cy+4:.2f}',
                f'{pad-11},{cy:.2f} {pad-2},{cy-4:.2f} {pad-2},{cy+4:.2f}',
                f'{cx:.2f},{pad-11} {cx-4:.2f},{pad-2} {cx+4:.2f},{pad-2}',
                f'{cx:.2f},{pad+span+11} {cx-4:.2f},{pad+span+2} {cx+4:.2f},{pad+span+2}'):
        parts.append(f'<polygon points="{pts}" fill="#111"/>')
    if labelled:
        for v in range(-half, half + 1, axis_step):
            if v == 0:
                continue
            x = cx + v * cell
            y = cy - v * cell
            parts.append(f'<text x="{x:.2f}" y="{cy+13:.2f}" text-anchor="middle" font-size="9" '
                         f'font-family="{FONT}" fill="#333">{v}</text>')
            parts.append(f'<text x="{cx-5:.2f}" y="{y+3:.2f}" text-anchor="end" font-size="9" '
                         f'font-family="{FONT}" fill="#333">{v}</text>')
        parts.append(f'<text x="{pad+span+4}" y="{cy-6:.2f}" font-size="10" font-style="italic" '
                     f'font-family="{FONT}" fill="#333">x</text>')
        parts.append(f'<text x="{cx+6:.2f}" y="{pad+2}" font-size="10" font-style="italic" '
                     f'font-family="{FONT}" fill="#333">y</text>')
    return svg(width, width, parts)


def quadrant1(width=340, nx=10, ny=10):
    """First-quadrant grid - for tables of values, growth models, projectile heights."""
    pad_l, pad_b, pad_t, pad_r = 24, 24, 12, 12
    w = width - pad_l - pad_r
    h = width - pad_t - pad_b
    cw, ch = w / nx, h / ny
    parts = []
    for i in range(nx + 1):
        x = pad_l + i * cw
        parts.append(f'<line x1="{x:.2f}" y1="{pad_t}" x2="{x:.2f}" y2="{pad_t+h}" '
                     f'stroke="#c9d2da" stroke-width="0.6"/>')
    for j in range(ny + 1):
        y = pad_t + j * ch
        parts.append(f'<line x1="{pad_l}" y1="{y:.2f}" x2="{pad_l+w}" y2="{y:.2f}" '
                     f'stroke="#c9d2da" stroke-width="0.6"/>')
    parts.append(f'<line x1="{pad_l}" y1="{pad_t+h}" x2="{pad_l+w+8}" y2="{pad_t+h}" '
                 f'stroke="#111" stroke-width="1.4"/>')
    parts.append(f'<line x1="{pad_l}" y1="{pad_t-8}" x2="{pad_l}" y2="{pad_t+h}" '
                 f'stroke="#111" stroke-width="1.4"/>')
    parts.append(f'<polygon points="{pad_l+w+13},{pad_t+h} {pad_l+w+4},{pad_t+h-4} '
                 f'{pad_l+w+4},{pad_t+h+4}" fill="#111"/>')
    parts.append(f'<polygon points="{pad_l},{pad_t-13} {pad_l-4},{pad_t-4} '
                 f'{pad_l+4},{pad_t-4}" fill="#111"/>')
    return svg(width, width, parts)


def tree(node, width=360, level_h=54, rx=17):
    """Factor tree.  `node` is (label, [children]); use "?" for a blank to fill in.

    Leaves are laid out evenly across the width and each parent is centred over
    its children, so the drawing matches the mermaid trees used in the lessons.
    """
    leaves = []

    def count(n):
        label, kids = n
        if not kids:
            leaves.append(n)
            return 1
        return sum(count(k) for k in kids)

    total = count(node)
    depth = [0]

    def place(n, level, cursor):
        depth[0] = max(depth[0], level)
        label, kids = n
        if not kids:
            x = pad + (cursor + 0.5) * slot
            return {"label": label, "x": x, "y": pad_t + level * level_h,
                    "kids": [], "n": 1}
        placed, used = [], 0
        for k in kids:
            c = place(k, level + 1, cursor + used)
            placed.append(c)
            used += c["n"]
        x = sum(c["x"] for c in placed) / len(placed)
        return {"label": label, "x": x, "y": pad_t + level * level_h,
                "kids": placed, "n": used}

    pad, pad_t = 10, 16
    slot = (width - 2 * pad) / total
    root = place(node, 0, 0)
    height = pad_t + depth[0] * level_h + 24

    edges, nodes = [], []

    def draw(n):
        for c in n["kids"]:
            edges.append(f'<line x1="{n["x"]:.1f}" y1="{n["y"]+rx-2:.1f}" '
                         f'x2="{c["x"]:.1f}" y2="{c["y"]-rx+2:.1f}" '
                         f'stroke="#111" stroke-width="1.2"/>')
            draw(c)
        blank = n["label"] == "?"
        dash = ' stroke-dasharray="3 2"' if blank else ''
        nodes.append(f'<circle cx="{n["x"]:.1f}" cy="{n["y"]:.1f}" r="{rx}" fill="#fff" '
                     f'stroke="#111" stroke-width="{1.6 if blank else 1.1}"{dash}/>')
        if not blank:
            nodes.append(f'<text x="{n["x"]:.1f}" y="{n["y"]+4:.1f}" text-anchor="middle" '
                         f'font-size="14" font-family="{FONT}" fill="#111">{n["label"]}</text>')

    draw(root)
    return svg(width, int(height), edges + nodes)


def svg(w, h, parts):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n  '
            % (w, h, w, h)) + "\n  ".join(parts) + "\n</svg>\n"


def write(name, content):
    path = os.path.normpath(os.path.join(OUT, name))
    with open(path, "w") as f:
        f.write(content)
    print("wrote", os.path.relpath(path))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    write("nl.svg",        number_line(labels=[str(v) for v in range(-10, 11)]))
    write("nl-blank.svg",  number_line(labels=None, n_ticks=21))
    write("nl-blank-11.svg", number_line(labels=None, n_ticks=11))
    write("grid.svg",      grid(labelled=True))
    write("grid-blank.svg", grid(labelled=False))
    write("grid-q1.svg",   quadrant1())

    # lesson figures that the textbook draws with mermaid
    write("u1l2-tree-4a.svg", tree(
        ("36", [("?", [("?", []), ("3", [])]), ("6", [("2", []), ("?", [])])])))
    write("u1l2-tree-4b.svg", tree(
        ("-120", [("-1", []),
                  ("?", [("2", []),
                         ("?", [("6", [("2", []), ("?", [])]),
                                ("?", [("2", []), ("5", [])])])])]), width=400))
