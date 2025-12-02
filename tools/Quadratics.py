from LinearEquations import *

# ===== quadratic helpers for linear_plane.py =====
import numpy as np

def format_quadratic_label(a: float, b: float, c: float) -> str:
    """
    Return a nice string like 'y = 2x^2 - 3x + 1' with special casing:
      - hide 1 and -1 coefficients where appropriate
      - suppress +0 terms
      - handle signs cleanly
    """
    parts = []

    # a x^2 term
    a0 = np.isclose(a, 0.0)
    a1 = np.isclose(a, 1.0)
    a_1 = np.isclose(a, -1.0)

    if not a0:
        if a1:
            parts.append("x^2")
        elif a_1:
            parts.append("-x^2")
        else:
            parts.append(f"{a:g}x^2")

    # b x term
    b0 = np.isclose(b, 0.0)
    if not b0:
        sign = "+" if b > 0 else "-"
        mag = abs(b)
        if np.isclose(mag, 1.0):
            piece = "x"
        else:
            piece = f"{mag:g}x"
        if parts:
            parts.append(f" {sign} {piece}")
        else:
            # first term, keep sign
            parts.append(f"{b:g}x" if not np.isclose(mag, 1.0) else ("x" if b > 0 else "-x"))

    # constant term
    c0 = np.isclose(c, 0.0)
    if not c0:
        sign = "+" if c > 0 else "-"
        mag = abs(c)
        if parts:
            parts.append(f" {sign} {mag:g}")
        else:
            parts.append(f"{c:g}")

    # if everything vanished, it's y = 0
    if not parts:
        rhs = "0"
    else:
        rhs = "".join(parts)

    return f"y = {rhs}"


def format_quadratic_ineq_label(a: float, b: float, c: float, comp: str) -> str:
    """
    Same as format_quadratic_label but with inequalities like y ≤ ax^2 + bx + c.
    """
    sym = {'<': '<', '<=': '≤', '>': '>', '>=': '≥'}.get(comp, comp)
    eq = format_quadratic_label(a, b, c)      # 'y = ...'
    return eq.replace('=', sym, 1)            # 'y ≤ ...'


def add_quadratics_to_axes(
    ax,
    quadratics=None,
    inequalities=None,
    show_vertex: bool = False,
    show_roots: bool = False,
    quad_line_defaults: Optional[dict] = None,
    quad_inequality_defaults: Optional[dict] = None,
    samples: int = 1000,
    legend: bool = True,
):
    """
    Draw quadratics on an existing axes (e.g. from linear_function_coordinate_plane).

    Parameters
    ----------
    ax : matplotlib Axes
        The axes to draw on.
    quadratics : list of (a, b, c) or (a, b, c, style_dict)
        Curves y = ax^2 + bx + c. Optional style dict merged over quad_line_defaults.
    inequalities : list of (a, b, c, comp) or (a, b, c, comp, style_dict)
        Quadratic inequalities with comp in {'<','<=','>','>='}.
        Region is shaded above/below the curve.
    show_vertex : bool
        If True, mark the vertex of each quadratic that lies in view.
    show_roots : bool
        If True, mark real roots of each quadratic that lie in view.
    quad_line_defaults : dict
        Default matplotlib style for quadratic curves.
    quad_inequality_defaults : dict
        Default style for inequality boundaries and fills.
    samples : int
        Number of x samples across the visible x-range.
    legend : bool
        If True, call ax.legend() at the end. Note: this will only show artists
        that have labels; your existing linear_function_coordinate_plane does not
        set labels by default, so usually only the quadratics will appear.
    """
    if quadratics is None and inequalities is None:
        return ax

    if quad_line_defaults is None:
        quad_line_defaults = {'linewidth': 2.0}
    if quad_inequality_defaults is None:
        quad_inequality_defaults = {'alpha': 0.15, 'linewidth': 1.5}

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    xs = np.linspace(xmin, xmax, samples)

    # --- helper for vertex & roots ---
    def _vertex(a, b, c):
        if np.isclose(a, 0.0):
            return None
        h = -b / (2 * a)
        k = a * h * h + b * h + c
        return h, k

    def _roots(a, b, c):
        if np.isclose(a, 0.0):
            # Degenerate to linear
            if np.isclose(b, 0.0):
                return []
            x = -c / b
            return [x]
        disc = b * b - 4 * a * c
        if disc < 0:
            return []
        if np.isclose(disc, 0.0):
            return [-b / (2 * a)]
        r = disc ** 0.5
        return [(-b - r) / (2 * a), (-b + r) / (2 * a)]

    # --- curves y = ax^2 + bx + c ---
    if quadratics:
        for item in quadratics:
            if len(item) == 3:
                a, b, c = item
                style = {}
            else:
                a, b, c, style = item

            style = (style or {}).copy()
            label = style.pop('label', None) or format_quadratic_label(a, b, c)
            line_style = {**quad_line_defaults, **style, 'label': label}

            ys = a * xs**2 + b * xs + c
            ax.plot(xs, ys, **line_style)

            # vertex marker
            if show_vertex:
                v = _vertex(a, b, c)
                if v is not None:
                    vx, vy = v
                    if xmin <= vx <= xmax and ymin <= vy <= ymax:
                        ax.scatter([vx], [vy], s=30, zorder=5, color=line_style.get('color', None))

            # root markers
            if show_roots:
                rs = _roots(a, b, c)
                for r in rs:
                    if xmin <= r <= xmax:
                        yr = 0.0
                        if ymin <= yr <= ymax:
                            ax.scatter([r], [yr], s=30, zorder=5, color=line_style.get('color', None))

    # --- inequalities y ⋚ ax^2 + bx + c ---
    if inequalities:
        for item in inequalities:
            if len(item) == 4:
                a, b, c, comp = item
                style = {}
            else:
                a, b, c, comp, style = item

            style = (style or {}).copy()
            boundary_ls = (0, (4, 4)) if comp in ('<', '>') else '-'

            boundary_style = {
                **quad_inequality_defaults,
                'linestyle': boundary_ls,
            }
            # allow user overrides
            for k in ['color', 'linewidth', 'linestyle']:
                if k in style:
                    boundary_style[k] = style[k]

            label = style.pop('label', None) or format_quadratic_ineq_label(a, b, c, comp)
            ys = a * xs**2 + b * xs + c

            ax.plot(xs, ys, label=label, **boundary_style)

            fill_kwargs = quad_inequality_defaults.copy()
            fill_kwargs.update({k: v for k, v in style.items() if k not in ['linestyle']})

            if comp in ('<', '<='):
                ax.fill_between(xs, ymin, ys, **fill_kwargs)
            else:
                ax.fill_between(xs, ys, ymax, **fill_kwargs)

    if legend:
        ax.legend()

    return ax


def quadratic_function_coordinate_plane(
    *,
    quadratics=None,
    inequalities=None,
    show_vertex: bool = False,
    show_roots: bool = False,
    quad_line_defaults: Optional[dict] = None,
    quad_inequality_defaults: Optional[dict] = None,
    samples: int = 1000,
    legend: bool = True,
    **plane_kwargs,
):
    """
    Convenience wrapper around linear_function_coordinate_plane that also draws
    quadratics.

    Usage example
    -------------
    fig, ax = quadratic_function_coordinate_plane(
        x_axis=(-10, 10, "x", {}),
        y_axis=(-10, 10, "y", {}),
        quadratics=[(1, 0, -4), (-0.5, 2, 3)],
        show_vertex=True,
        show_roots=True,
        chart_axis_labels={
            "bottom": ("Time (seconds)", {}),
            "left": ("Height (meters)", {}),
        }
    )

    Any extra keyword arguments are passed directly through to
    linear_function_coordinate_plane (ticks, points, lines, etc).

    Note
    ----
    The built-in legend logic of linear_function_coordinate_plane is disabled
    in this wrapper so that we can use standard Matplotlib legend behavior.
    If you want a legend, set legend=True (default), and only the artists with
    labels (quadratics, or anything else you explicitly label) will appear.
    """
    # We deliberately disable the internal legend logic and handle it here
    plane_kwargs = plane_kwargs.copy()
    plane_kwargs['legend'] = False

    fig, ax = linear_function_coordinate_plane(**plane_kwargs)

    add_quadratics_to_axes(
        ax,
        quadratics=quadratics,
        inequalities=inequalities,
        show_vertex=show_vertex,
        show_roots=show_roots,
        quad_line_defaults=quad_line_defaults,
        quad_inequality_defaults=quad_inequality_defaults,
        samples=samples,
        legend=legend,
    )

    return fig, ax

def convert_to_standard_form(a, h, k):
    return (
        a,
        -2*a*h,
        a*h**2 + k
    )
# ===== end quadratic helpers =====

