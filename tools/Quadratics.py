import numpy as np
import matplotlib.pyplot as plt


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def parse_quadratic(quad):
    """
    Accepts:
    - (a, b, c)
    - (a, h, k, "vertex")
    - a function f(x)

    Returns: function f, and inferred standard (a, b, c) if possible
    """

    if callable(quad):
        # cannot infer coefficients
        return quad, None

    if len(quad) == 3:
        a, b, c = quad
        def f(x): return a * x**2 + b * x + c
        return f, (a, b, c)

    if len(quad) == 4 and quad[3] == "vertex":
        a, h, k, _ = quad
        def f(x): return a * (x - h)**2 + k
        # convert to standard form for labels
        A = a
        B = -2 * a * h
        C = a * h**2 + k
        return f, (A, B, C)

    raise ValueError("Invalid quadratic format.")
    

def quadratic_latex(a, b, c, func_name="f"):
    """
    Produce a LaTeX equation like:
    $f(x) = x^2 - 4x + 3$
    """
    var = "x"
    pieces = []

    # ax^2
    if a == 1:
        pieces.append(f"{var}^2")
    elif a == -1:
        pieces.append(f"-{var}^2")
    else:
        pieces.append(f"{a}{var}^2")

    # bx
    if b != 0:
        sign = "+" if b > 0 else ""
        if b == 1:
            pieces.append(f"{sign}{var}")
        elif b == -1:
            pieces.append(f"-{var}")
        else:
            pieces.append(f"{sign}{b}{var}")

    # constant term
    if c != 0:
        sign = "+" if c > 0 else ""
        pieces.append(f"{sign}{c}")

    rhs = " ".join(pieces)
    return rf"${func_name}({var}) = {rhs}$"


def plot_quadratic(
    quad,
    *,
    x_range=(-10, 10),
    y_range=None,
    aspect=1,
    points=None,
    axis_of_symmetry=None,
    equation_label=None,
    grid=None,
    figsize=(4, 4),
):
    """
    Clean, textbook style quadratic plotter.

    Parameters
    ----------
    quad:
        (a, b, c)
        (a, h, k, "vertex")
        callable f(x)

    x_range:
        Tuple (xmin, xmax)

    y_range:
        Tuple (ymin, ymax) or None for auto

    aspect:
        Numeric aspect ratio. 1 gives a square plot area.

    points:
        List of (x, y, style_dict) where style_dict may contain:
          - "label": text
          - "color": marker color
          - "size": marker size
          - "offset": (dx, dy) in points for the label

    axis_of_symmetry:
        Dict or None. Example:
          {
            "x": value,
            "color": "red",
            "linestyle": "--",
            "linewidth": 1.5,
            "label": "x = 2.0",
            "label_offset": (0, 0)
          }

    equation_label:
        Dict or None. Example:
          {
            "location": "top-right",
            "func_name": "f",
            "fontsize": 12,
            "offset": (-5, -5)   # in points
          }

    grid:
        Dict or None. Example:
          {
            "major": True,
            "minor": True,
            "x_major_step": 1,
            "y_major_step": 1
          }
    """

    # parse the quadratic info
    f, coeffs = parse_quadratic(quad)
    a = b = c = None
    if coeffs is not None:
        a, b, c = coeffs

    # sample points
    xs = np.linspace(x_range[0], x_range[1], 400)
    ys = f(xs)

    fig, ax = plt.subplots(figsize=figsize)

    # main curve
    ax.plot(xs, ys, color="C0", linewidth=2)

    # axes
    ax.axhline(0, color="#CCCCCC", linewidth=1)
    ax.axvline(0, color="#CCCCCC", linewidth=1)

    # grid with major and minor ticks
    if grid:
        major = grid.get("major", True)
        minor = grid.get("minor", False)

        if "x_major_step" in grid:
            ax.xaxis.set_major_locator(MultipleLocator(grid["x_major_step"]))
        if "y_major_step" in grid:
            ax.yaxis.set_major_locator(MultipleLocator(grid["y_major_step"]))

        if major:
            ax.grid(True, which="major", linestyle=":", linewidth=0.8, color="#DDDDDD")
        if minor:
            ax.minorticks_on()
            ax.grid(True, which="minor", linestyle=":", linewidth=0.5, color="#EEEEEE")

    # optional points
    if points:
        for (px, py, style) in points:
            label = style.get("label")
            color = style.get("color", "black")
            size = style.get("size", 40)
            offset = style.get("offset", (6, 6))

            ax.scatter(px, py, color=color, s=size, zorder=5)
            if label:
                ax.annotate(
                    label,
                    xy=(px, py),
                    xytext=offset,
                    textcoords="offset points",
                    fontsize=10,
                )

    # axis of symmetry
    if axis_of_symmetry:
        x0 = axis_of_symmetry.get("x")
        color = axis_of_symmetry.get("color", "red")
        ls = axis_of_symmetry.get("linestyle", "--")
        lw = axis_of_symmetry.get("linewidth", 1.4)
        ax.axvline(x0, color=color, linestyle=ls, linewidth=lw)

        if "label" in axis_of_symmetry:
            label_offset = axis_of_symmetry.get("label_offset", (0, 0))
            # place label at top of plot above the line
            ax.annotate(
                axis_of_symmetry["label"],
                xy=(x0, ax.get_ylim()[1]),
                xycoords=("data", "data"),
                xytext=label_offset,
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=10,
                color=color,
            )

    # equation label
    if equation_label and coeffs is not None:
        loc = equation_label.get("location", "top-right")
        fontsize = equation_label.get("fontsize", 12)
        func_name = equation_label.get("func_name", "f")
        offset = equation_label.get("offset", (0, 0))

        eq_text = quadratic_latex(a, b, c, func_name=func_name)

        loc_map = {
            "top-right": (0.98, 0.98),
            "top-left": (0.02, 0.98),
            "bottom-left": (0.02, 0.02),
            "bottom-right": (0.98, 0.02),
        }
        xloc, yloc = loc_map[loc]

        # use annotate so we can nudge by points
        ha = "right" if "right" in loc else "left"
        va = "top" if "top" in loc else "bottom"

        ax.annotate(
            eq_text,
            xy=(xloc, yloc),
            xycoords="axes fraction",
            xytext=offset,
            textcoords="offset points",
            ha=ha,
            va=va,
            fontsize=fontsize,
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.25"),
        )

    # aspect and ranges
    ax.set_xlim(x_range)
    if y_range:
        ax.set_ylim(y_range)
    else:
        ymin, ymax = np.min(ys), np.max(ys)
        pad = 0.1 * (ymax - ymin if ymax > ymin else 1)
        ax.set_ylim(ymin - pad, ymax + pad)

    ax.set_aspect(aspect, adjustable="box")

    ax.set_xlabel("x")
    ax.set_ylabel("y")

    plt.tight_layout()
    return fig, ax
