"""Draw a mixed number as whole circles plus a part circle, then again with the
whole ones divided, so the count of equal pieces is visible.

Matches the Lesson 5 pizza figures: flat fill, black stroke, white for the
part that is not there.
"""
import math

FILL   = "#f6d87a"   # same yellow as the pizza cheese
EMPTY  = "#ffffff"
STROKE = "#000000"

def _circle(cx, cy, r, denom=None, shaded=None):
    """One circle. denom=None draws a plain whole. shaded = number of parts filled."""
    out = []
    if denom is None:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{FILL}" stroke="{STROKE}" stroke-width="2"/>')
        return out
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{EMPTY}" stroke="{STROKE}" stroke-width="2"/>')
    if shaded == denom:
        # fill once; tiling every wedge leaves anti-aliased seams along the shared edges
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{FILL}" stroke="none"/>')
    elif shaded:
        step = 360.0 / denom
        for k in range(shaded):
            a0, a1 = math.radians(-90 + k*step), math.radians(-90 + (k+1)*step)
            x0, y0 = cx + r*math.cos(a0), cy + r*math.sin(a0)
            x1, y1 = cx + r*math.cos(a1), cy + r*math.sin(a1)
            large = 1 if step > 180 else 0
            out.append(f'<path d="M{cx},{cy} L{x0:.2f},{y0:.2f} '
                       f'A{r},{r} 0 {large},1 {x1:.2f},{y1:.2f} Z" fill="{FILL}" stroke="none"/>')
    for k in range(denom):
        a = math.radians(-90 + k*(360.0/denom))
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+r*math.cos(a):.2f}" y2="{cy+r*math.sin(a):.2f}" '
                   f'stroke="{STROKE}" stroke-width="2"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{STROKE}" stroke-width="2"/>')
    return out

def mixed_number_svg(whole, num, denom, path, divided, alt):
    """One row of circles. divided=False draws the wholes plain, True cuts them
    into denom pieces so the total count of equal pieces can be seen."""
    r, gap, pad = 46, 26, 14
    n = whole + 1
    w = pad*2 + n*(2*r) + (n-1)*gap
    h = pad*2 + 2*r
    cy = pad + r
    s = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
         f'role="img" aria-label="{alt}">']
    cx = pad + r
    for _ in range(whole):
        s += _circle(cx, cy, r, denom if divided else None, denom if divided else None)
        cx += 2*r + gap
    s += _circle(cx, cy, r, denom, num)
    s.append('</svg>')
    open(path,'w').write('\n'.join(s))
    return path

if __name__ == "__main__":
    # 1.4.2 introduces the conversion with 4 2/3
    mixed_number_svg(4, 2, 3, "images/Unit_1/Lesson_4/mixed_4_and_2_thirds_wholes.svg", False,
                     "Four whole circles and two thirds of a circle")
    mixed_number_svg(4, 2, 3, "images/Unit_1/Lesson_4/mixed_4_and_2_thirds_divided.svg", True,
                     "The same amount with every whole cut into thirds, showing fourteen thirds")
