# ===== linear_plane.py =====
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyArrowPatch, Rectangle
from typing import List, Tuple, Optional, Dict, Any, Union

# ---------- Label formatters ----------
def format_line_label(m: float, b: float) -> str:
    """Return 'y = mx + b' with nice special-casing:
       1x -> x, -1x -> -x, +0 suppressed, sign handled."""
    m1 = np.isclose(m, 1.0)
    m_1 = np.isclose(m, -1.0)
    b0 = np.isclose(b, 0.0)
    m_0 = np.isclose(m, 0.0)
    
    if m1:
        m_str = "x"
    elif m_1:
        m_str = "-x"
    elif m_0:
        m_str = "0"
    else:
        m_str = f"{m:g}x"

    if b0:
        return f"y = {m_str}"
    return f"y = {m_str} + {b:g}" if b > 0 else f"y = {m_str} - {abs(b):g}"

def format_ineq_label(m: float, b: float, comp: str) -> str:
    """Return 'y ≤ mx + b' etc. with the same nice special-casing."""
    sym = {'<':'<', '<=':'≤', '>':'>', '>=':'≥'}.get(comp, comp)
    # reuse the line formatter but swap the equality sign for the inequality
    eq = format_line_label(m, b)          # 'y = ...'
    return eq.replace('=', sym, 1)        # 'y ≤ ...'


# ---------- Tick utilities ----------
def _aligned_ticks(vmin: float, vmax: float, step: Optional[float]):
    """Return tick positions aligned to 'step', covering [vmin, vmax]."""
    if step is None or step <= 0:
        return None
    start = np.floor(vmin / step) * step
    end   = np.ceil (vmax  / step) * step
    ticks = np.arange(start, end + step*1e-9, step)
    return ticks[(ticks >= vmin - 1e-12) & (ticks <= vmax + 1e-12)]

def _apply_ticks(ax, axis: str, vmin: float, vmax: float, cfg: dict):
    """
    axis: 'x' or 'y'
    cfg keys:
      - ticks (list|None), major_step (float|None)
      - minor_ticks (list|None), minor_step (float|None)
      - format (str|None), rotate (deg|0), hide_zero_label (bool)
    """
    major = cfg.get('ticks', None)
    if major is None:
        major = _aligned_ticks(vmin, vmax, cfg.get('major_step', None))
    minor = cfg.get('minor_ticks', None)
    if minor is None:
        minor = _aligned_ticks(vmin, vmax, cfg.get('minor_step', None))

    if axis == 'x':
        if major is not None: ax.set_xticks(major)
        if minor is not None: ax.set_xticks(minor, minor=True)
        if cfg.get('format'):
            fmt = cfg['format']
            ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: fmt.format(v)))
        if cfg.get('rotate'):
            for lbl in ax.get_xticklabels(): lbl.set_rotation(cfg['rotate'])
        if cfg.get('hide_zero_label'):
            for lbl in ax.get_xticklabels():
                try:
                    if abs(float(lbl.get_text().replace(',', ''))) < 1e-12:
                        lbl.set_visible(False)
                except ValueError:
                    pass
    else:
        if major is not None: ax.set_yticks(major)
        if minor is not None: ax.set_yticks(minor, minor=True)
        if cfg.get('format'):
            fmt = cfg['format']
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: fmt.format(v)))
        if cfg.get('rotate'):
            for lbl in ax.get_yticklabels(): lbl.set_rotation(cfg['rotate'])
        if cfg.get('hide_zero_label'):
            for lbl in ax.get_yticklabels():
                try:
                    if abs(float(lbl.get_text().replace(',', ''))) < 1e-12:
                        lbl.set_visible(False)
                except ValueError:
                    pass


# ---- Quadrant Labels ----
def add_quadrant_labels(
    ax,
    show=False,
    short=False,
    fontsize=24,
    fontcolor='gray',
    fontweight='bold',
    xmax=None,
    ymax=None,
    **text_kwargs
):
    """Optional quadrant labeling: 'Quadrant I' or 'I'."""
    if not show:
        return

    labels = ["I", "II", "III", "IV"] if short else \
             ["Quadrant I", "Quadrant II", "Quadrant III", "Quadrant IV"]

    xmid = 0.5 * xmax
    ymid = 0.5 * ymax

    positions = [
        (xmid,  ymid),    # I
        (-xmid, ymid),    # II
        (-xmid,-ymid),    # III
        (xmid, -ymid)     # IV
    ]

    for (xpos, ypos), label in zip(positions, labels):
        ax.text(
            xpos, ypos, label,
            color=fontcolor,
            fontsize=fontsize,
            fontweight=fontweight,
            fontfamily='DejaVu Serif',
            ha='center', va='center',
            alpha=0.5, zorder=0,
            **text_kwargs
        )


# ---------- Main helper ----------
def linear_function_coordinate_plane(
    x_axis: Tuple[float, float, str, dict] = (-10, 10, "x", {}),
    y_axis: Tuple[float, float, str, dict] = (-10, 10, "y", {}),
    grid_labels: Optional[Dict[str, List[Tuple[float, str, dict]]]] = None,
    points: Optional[List[Union[Tuple[float, float],
                                Tuple[float, float, str],
                                Tuple[float, float, str, dict]]]] = None,
    lines: Optional[List[Union[Tuple[float, float],
                               Tuple[float, float, dict]]]] = None,
    inequalities: Optional[List[Union[Tuple[float, float, str],
                                      Tuple[float, float, str, dict]]]] = None,
    title: Optional[str] = None,
    outfile: Optional[str] = None,

    # Outside, chart-style axis labels (e.g., Hours / Cost)
    chart_axis_labels: Optional[Dict[str, Tuple[str, dict]]] = None,

    # --- Grid & ticks ---
    show_grid: bool = True,
    grid_kwargs: Optional[dict] = None,

    # Unified tick config (with per-axis overrides via x_axis[3]/y_axis[3])
    tick_config: Optional[dict] = None,

    # --- Styles & sizes ---
    spine_kwargs: Optional[dict] = None,
    tick_params: Optional[dict] = None,
    label_fontsize: int = 12,
    title_fontsize: int = 14,
    scatter_defaults: Optional[dict] = None,
    line_defaults: Optional[dict] = None,
    inequality_defaults: Optional[dict] = None,
    figsize: Tuple[float, float] = (6, 6),

    # End-of-axis 'x'/'y' label offsets (fractions of data span)
    x_end_label_offset: Tuple[float, float] = (0.025, 0),
    y_end_label_offset: Tuple[float, float] = (0, 0.025),

    # Axis arrows & baselines
    axis_arrows: bool = False,
    axis_arrow_ends: Optional[Dict[str, str]] = None,   # {'x': 'pos'|'neg'|'both'|'none', 'y': ...}
    arrow_kwargs: Optional[dict] = None,
    axis_baseline: bool = True,                          # draw full-axis neutral baseline when replacing spines
    baseline_kwargs: Optional[dict] = None,

    # Aspect ratio: 'equal' (default), 'auto', numeric, or None (leave as-is)
    aspect: Union[str, float, None] = 'equal',

    # Algebra-style centered axes vs classic chart spines
    centered_axes: bool = True,

    # --- Frame (box) around the plane ---
    frame_box: bool = False,
    frame_inset: float = 0.0,        # fraction of axis span inset on each side
    frame_kwargs: Optional[dict] = None,

    # Quadrant labels
    show_quadrants: bool = False,
    quadrant_label_style: str = "full",  # "full" or "short"

    # Projections from points to axes
    project_to_axes: bool = False,              # global toggle
    projection_kwargs: Optional[dict] = None,   # style for the dashed guides

    # Legend
    legend: Union[bool, dict] = False,          # True/False or dict as shortcut for legend_config
    legend_config: Optional[dict] = None
):
    """
    Clean, textbook-like coordinate plane generator.

    • Centered axes (Algebra look) or classic chart spines.
    • Arrowheads on pos/neg/both ends (with full-length baselines).
    • End-of-axis labels; outside chart labels; edge labels at data positions.
    • Ticks by step or explicit lists; formatted labels; rotation; hide-zero.
    • Lines y = m x + b, shaded inequalities, points (with optional projections).
    • Configurable aspect; optional framed box; legend; file save.
    """
    # ---- unpack axes ----
    xmin, xmax, xlabel, xstyle = x_axis
    ymin, ymax, ylabel, ystyle = y_axis

    # ---- defaults ----
    if grid_kwargs is None:
        grid_kwargs = {'linewidth': 0.6, 'alpha': 0.4}
    if spine_kwargs is None:
        spine_kwargs = {'linewidth': 1.25}
    if tick_params is None:
        tick_params = {'labelsize': 10}
    if scatter_defaults is None:
        scatter_defaults = {'s': 24}
    if line_defaults is None:
        line_defaults = {'linewidth': 2.0}
    if inequality_defaults is None:
        inequality_defaults = {'alpha': 0.15, 'linewidth': 1.5}
    if arrow_kwargs is None:
        arrow_kwargs = dict(arrowstyle='-|>', lw=spine_kwargs.get('linewidth', 1.25), mutation_scale=12)
    if baseline_kwargs is None:
        baseline_kwargs = {'linewidth': spine_kwargs.get('linewidth', 1.25), 'alpha': 0.95}
    if axis_arrow_ends is None:
        axis_arrow_ends = {'x': 'pos', 'y': 'pos'}
    if frame_kwargs is None:
        frame_kwargs = {'linewidth': 1.25, 'linestyle': '-'}
    if projection_kwargs is None:
        projection_kwargs = {
            'linestyle': (0, (2, 4)),
            'linewidth': 1.0,
            'alpha': 0.5,
            'zorder': 3,
        }

    # Legend config defaults
    if isinstance(legend, dict):
        legend_config = {**(legend_config or {}), **legend}
        legend = True
    if legend_config is None:
        legend_config = {}
    _legend_defaults = {
        'loc': 'upper right',
        'ncol': 1,
        'frameon': True,
        'fancybox': True,
        'framealpha': 0.9,
        'title': None,
        'bbox_to_anchor': None,
        'borderpad': 0.6,
        'handlelength': 2.0,
        'handletextpad': 0.6,
        'markerscale': 1.2
    }
    _legend_cfg = {**_legend_defaults, **legend_config}

    # ---- figure/axes ----
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    if aspect is not None:
        ax.set_aspect(aspect, adjustable='box')

    # ---- spines: centered vs chart ----
    if centered_axes:
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')
        for side in ['right', 'top']:
            ax.spines[side].set_visible(False)
        for side in ['left', 'bottom']:
            ax.spines[side].set(**spine_kwargs)
    else:
        for side in ['right', 'top']:
            ax.spines[side].set_visible(False)
        for side in ['left', 'bottom']:
            ax.spines[side].set_visible(True)
            ax.spines[side].set(**spine_kwargs)

    # ---- ticks: unified config with per-axis overrides ----
    tick_defaults = {
        'major_step': None, 'minor_step': None,
        'ticks': None, 'minor_ticks': None,
        'format': None, 'rotate': 0, 'hide_zero_label': False
    }
    tick_config = tick_config or {}
    x_cfg = {**tick_defaults, **tick_config.get('x', {})}
    y_cfg = {**tick_defaults, **tick_config.get('y', {})}
    x_cfg.update({k: xstyle.get(k, x_cfg[k]) for k in tick_defaults})
    y_cfg.update({k: ystyle.get(k, y_cfg[k]) for k in tick_defaults})

    _apply_ticks(ax, 'x', xmin, xmax, x_cfg)
    _apply_ticks(ax, 'y', ymin, ymax, y_cfg)

    # ---- grid ----
    ax.grid(show_grid, which='major', **grid_kwargs)
    for line in ax.get_xgridlines() + ax.get_ygridlines():
        line.set_clip_on(False)

    if x_cfg.get('minor_step') or x_cfg.get('minor_ticks') or y_cfg.get('minor_step') or y_cfg.get('minor_ticks'):
        ax.grid(True, which='minor',
                **{**grid_kwargs,
                   'linewidth': grid_kwargs.get('linewidth', 0.6) * 0.7,
                   'alpha': grid_kwargs.get('alpha', 0.4) * 0.7})

    ax.tick_params(axis='both', which='both', **tick_params)

    # ---- arrows & baselines (only when requested) ----
    if axis_arrows and (axis_arrow_ends.get('x', 'pos') != 'none' or axis_arrow_ends.get('y', 'pos') != 'none'):
        if centered_axes:
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            if axis_baseline:
                spine_color = spine_kwargs.get('color', ax.spines['left'].get_edgecolor())
                bs = {**baseline_kwargs, 'color': spine_color}
                ax.axhline(0, **bs, zorder=1)
                ax.axvline(0, **bs, zorder=1)

        def add_arrow(p0, p1):
            ax.add_patch(FancyArrowPatch(p0, p1, **arrow_kwargs))

        xm = axis_arrow_ends.get('x', 'pos')
        if xm in ('pos', 'both'):
            add_arrow(((0 if centered_axes else xmin), 0), (xmax, 0))
        if xm in ('neg', 'both'):
            add_arrow(((0 if centered_axes else xmax), 0), (xmin, 0))

        ym = axis_arrow_ends.get('y', 'pos')
        if ym in ('pos', 'both'):
            add_arrow((0, (0 if centered_axes else ymin)), (0, ymax))
        if ym in ('neg', 'both'):
            add_arrow((0, (0 if centered_axes else ymax)), (0, ymin))

    # ---- end-of-axis labels (data-coord placement) ----
    if centered_axes:
        x_base = (xmax, 0)
        y_base = (0, ymax)
    else:
        x_base = (xmax, ymin)  # bottom-right
        y_base = (xmin, ymax)  # top-left

    dx_x = x_end_label_offset[0] * (xmax - xmin)
    dy_x = x_end_label_offset[1] * (ymax - ymin)
    ax.text(x_base[0] + dx_x, x_base[1] + dy_x, xlabel, fontsize=label_fontsize, ha='left', va='center')

    dx_y = y_end_label_offset[0] * (xmax - xmin)
    dy_y = y_end_label_offset[1] * (ymax - ymin)
    ax.text(y_base[0] + dx_y, y_base[1] + dy_y, ylabel, fontsize=label_fontsize, ha='center', va='bottom')

    # ---- outside chart-style labels (axes fraction coords) ----
    if chart_axis_labels:
        if 'bottom' in chart_axis_labels:
            txt, kw = chart_axis_labels['bottom']
            kw = kw.copy() if kw else {}
            ax.text(0.5, -0.10, txt, transform=ax.transAxes, ha='center', va='top', **kw)
        if 'left' in chart_axis_labels:
            txt, kw = chart_axis_labels['left']
            kw = kw.copy() if kw else {}
            kw.setdefault('rotation', 90)
            ax.text(-0.10, 0.5, txt, transform=ax.transAxes, ha='right', va='center', **kw)

    # ---- edge data labels ----
    if grid_labels:
        if 'bottom' in grid_labels:
            for pos, text, kw in grid_labels['bottom']:
                ax.text(pos, ymin, text, ha='center', va='top', **kw)
        if 'top' in grid_labels:
            for pos, text, kw in grid_labels['top']:
                ax.text(pos, ymax, text, ha='center', va='bottom', **kw)
        if 'left' in grid_labels:
            for pos, text, kw in grid_labels['left']:
                ax.text(xmin, pos, text, ha='right', va='center', **kw)
        if 'right' in grid_labels:
            for pos, text, kw in grid_labels['right']:
                ax.text(xmax, pos, text, ha='left', va='center', **kw)

    # ---- optional frame (box) around the plane ----
    if frame_box:
        xmin_cur, xmax_cur = ax.get_xlim()
        ymin_cur, ymax_cur = ax.get_ylim()
        dx = frame_inset * (xmax_cur - xmin_cur)
        dy = frame_inset * (ymax_cur - ymin_cur)
        rect = Rectangle(
            (xmin_cur + 0.25*dx, ymin_cur + 0.25*dy),
            (xmax_cur - xmin_cur) - 0.5*dx,
            (ymax_cur - ymin_cur) - 0.5*dy,
            fill=False,
            linewidth=frame_kwargs.get('linewidth', 1.25),
            edgecolor=frame_kwargs.get('edgecolor', None),
            linestyle=frame_kwargs.get('linestyle', '-'),
            zorder=frame_kwargs.get('zorder', 10)
        )
        ax.add_patch(rect)

    # ---- sample xs for lines/inequalities ----
    xs = np.linspace(xmin, xmax, 1000)

    # ---- Legend collector ----
    legend_items: List[Tuple[Any, str]] = []
    seen_labels: set = set()

    def _add_legend_item(artist, label: Optional[str]):
        if not legend or not label:
            return
        if label in seen_labels:
            return
        seen_labels.add(label)
        legend_items.append((artist, label))

    # ---- Lines: y = m x + b ----
    # ---- Lines: y = m x + b ----
    if lines:
        for item in lines:
            if len(item) == 2:
                m, b = item
                style = {}
            else:
                m, b, style = item
    
            style = (style or {}).copy()
            explicit_label = style.pop('label', None)
    
            # --- Vertical line case: (None, x0) means x = x0 ---
            if m is None:
                x0 = b
                ymin_cur, ymax_cur = ax.get_ylim()
    
                # style for vertical line
                line_style = {**(line_defaults or {}), **style}
    
                # plot vertical line
                ln, = ax.plot([x0, x0], [ymin_cur, ymax_cur], **line_style)
    
                # legend label
                if legend:
                    auto_label = explicit_label or f"x = {x0:g}"
                    _add_legend_item(ln, auto_label)
    
                continue
            # --- End vertical line handling ---
    
            # Regular non-vertical line
            ys = m * xs + b
            line_style = {**(line_defaults or {}), **style}
    
            ln, = ax.plot(xs, ys, **line_style)
    
            if legend:
                auto_label = explicit_label or format_line_label(m, b)
                _add_legend_item(ln, auto_label)

                
    # ---- Inequalities: shaded half-planes + boundary style ----
    if inequalities:
        fill_once_keys = set()  # to avoid repeated fill entries

        for item in inequalities:
            if len(item) == 3:
                m, b, comp = item; style = {}
            else:
                m, b, comp, style = item

            ys = m * xs + b
            boundary = {'linestyle': (0, (4, 4))} if comp in ('<', '>') else {'linestyle': '-'}

            style = (style or {}).copy()
            explicit_label = style.get('label', None)

            # draw boundary
            ln, = ax.plot(
                xs, ys,
                **{
                    **(line_defaults or {}),
                    **boundary,
                    **{k: v for k, v in style.items() if k in ['linewidth', 'linestyle', 'color']}
                }
            )

            # fill region
            if comp in ('<', '<='):
                fill = ax.fill_between(
                    xs, ymin, ys,
                    **{k: v for k, v in style.items() if k != 'linestyle'},
                    alpha=style.get('alpha', (inequality_defaults or {}).get('alpha', 0.15))
                )
            else:
                fill = ax.fill_between(
                    xs, ys, ymax,
                    **{k: v for k, v in style.items() if k != 'linestyle'},
                    alpha=style.get('alpha', (inequality_defaults or {}).get('alpha', 0.15))
                )

            if legend:
                boundary_label = explicit_label or format_ineq_label(m, b, comp)
                _add_legend_item(ln, boundary_label)
                
                # optional fill entry once per style key if user opts in
                key = (comp, style.get('color'), style.get('hatch'), style.get('alpha'))
                if key not in fill_once_keys and style.get('legend_fill', False):
                    fill_once_keys.add(key)
                    _add_legend_item(fill, style.get('legend_fill_label', 'Shaded region'))

    # ---- Points ----
    if points:
        for p in points:
            if len(p) == 2:
                x, y = p
                label = None
                pstyle = {}
            elif len(p) == 3:
                x, y, label = p
                pstyle = {}
            else:
                x, y, label, pstyle = p

            pstyle = (pstyle or {}).copy()
            sc = ax.scatter([x], [y], **{**(scatter_defaults or {}), **pstyle})

            # text label next to the point (only if provided)
            dx = 0.02 * (ax.get_xlim()[1] - ax.get_xlim()[0])
            dy = 0.02 * (ax.get_ylim()[1] - ax.get_ylim()[0])
            ax.text(x - dx, y + dy, label, fontsize=12, ha='right', va='bottom', zorder=6)

            # Optional dashed projections from the point to the axes
            wants_proj = pstyle.pop('project', None)  # allow per-point override
            if (project_to_axes or wants_proj) is not None:
                do_proj = bool(project_to_axes) if wants_proj is None else bool(wants_proj)
            else:
                do_proj = False

            if do_proj:
                base_proj = {
                    'linestyle': (0, (2, 4)),
                    'linewidth': 1.0,
                    'alpha': 0.5,
                    'zorder': 3,
                }
                proj_style = (projection_kwargs or base_proj).copy()

                # choose a subtle color; fall back to gray if the point didn't set one
                color = pstyle.get('color', None)
                if color is None and scatter_defaults is not None:
                    color = scatter_defaults.get('color', None)
                proj_style.setdefault('color', color if color is not None else '0.3')

                # Only draw toward an axis if that axis actually crosses the view
                xmin_cur, xmax_cur = ax.get_xlim()
                ymin_cur, ymax_cur = ax.get_ylim()

                # vertical drop to x-axis (y=0)
                if ymin_cur < 0 < ymax_cur:
                    ax.plot([x, x], [0, y], **proj_style)

                # horizontal over to y-axis (x=0)
                if xmin_cur < 0 < xmax_cur:
                    ax.plot([0, x], [y, y], **proj_style)

            # Legend entry for points only if they have a label or explicit opt-in
            if legend:
                point_label = pstyle.get('label', None) or label
                if point_label or pstyle.get('legend_show', False):
                    if not point_label:
                        point_label = f"({x:g}, {y:g})"
                    _add_legend_item(sc, point_label)

    # ---- Title ----
    if title:
        extra_pad = 15 if (ylabel and len(ylabel) > 0) else 0
        ax.set_title(title, fontsize=title_fontsize, pad=14 + extra_pad)

    # ---- Quadrants ----
    add_quadrant_labels(
        ax,
        show=show_quadrants,
        short=(quadrant_label_style == "short"),
        xmax=xmax,
        ymax=ymax
    )

    # ---- Render legend ----
    if legend and legend_items:
        handles, labels = zip(*legend_items)
        uniq: Dict[str, Any] = {}
        for h, lab in zip(handles, labels):
            if lab not in uniq:
                uniq[lab] = h
        ax.legend(
            list(uniq.values()),
            list(uniq.keys()),
            loc=_legend_cfg['loc'],
            ncol=_legend_cfg['ncol'],
            frameon=_legend_cfg['frameon'],
            fancybox=_legend_cfg['fancybox'],
            framealpha=_legend_cfg['framealpha'],
            title=_legend_cfg['title'],
            bbox_to_anchor=_legend_cfg['bbox_to_anchor'],
            borderpad=_legend_cfg['borderpad'],
            handlelength=_legend_cfg['handlelength'],
            handletextpad=_legend_cfg['handletextpad'],
            markerscale=_legend_cfg['markerscale']
        )

    plt.tight_layout()
    if outfile:
        fig.savefig(outfile, dpi=300, bbox_inches='tight')
    return fig, ax


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
# ===== end quadratic helpers =====
