import matplotlib.pyplot as plt
import numpy as np

def norm(val, start, end):
    return (val - start) / (end - start)
    
def plot_number_line_with_points(
    line_range=(-10, 10, 1),
    orientation="horizontal",
    figsize=8,
    title=None,
    line_thickness=None,
    tick_length=None,
    tick_fontsize=None,
    point_size=None,
    points=None,
    inequalities=None,
    compound_inequalities=None,
    distances=None,
    arrow=True,
    output=None,
    unit_label="units"
):
    points = points or []
    inequalities = inequalities or []
    compound_inequalities = compound_inequalities or []
    distances = distances or []

    # Unpack and compute
    start = 0
    end = 1
    
    _t0, _t1, _s = line_range
    tick_labels = np.arange(_t0, _t1 + _s, _s)

    t0 = norm(_t0, _t0, _t1)
    t1 = norm(_t1, _t0, _t1)
    step = (t1 - t0) / ((_t1 - _t0) / _s)
    
    ticks = np.arange(t0, t1 + step, step)

    
    # Dynamic visuals
    line_thickness = line_thickness or max(figsize * 0.1, 1.5)
    tick_length = tick_length or max(figsize * 0.02, 0.1)
    tick_fontsize = tick_fontsize or int(figsize * 1.5)
    point_size = point_size or max(figsize * 1.5, 6)

    # Figure size
    vertical_space = 1 + len(distances)
    fig_dims = (figsize, vertical_space) if orientation == "horizontal" else (vertical_space, figsize)
    fig, ax = plt.subplots(figsize=fig_dims)
    ax.axis("off")

    # Axes limits
    margin = 0.05

    if orientation == "horizontal":
        ax.set_xlim(-margin, 1 + margin)
        ax.set_ylim(-vertical_space / 2, vertical_space / 2)
    else:
        ax.set_ylim(-margin, 1 + margin)
        ax.set_xlim(-vertical_space / 2, vertical_space / 2)

    # Draw main line
    _draw_number_line(ax, orientation, arrow, line_thickness)

    # Ticks and labels
    _draw_ticks(ax, orientation, ticks, tick_labels, tick_length, tick_fontsize)

    # Points
    for point in points:#val, closed, color in points:
        
        if not hasattr(point, '__len__'):
            point = [point]
            
        val, *args = point
        
        if args:
            closed, *args = args
        else:
            closed = True
            
        if args:
            color, *args = args
        else:
            color = "blue"

        if args:
            alpha = args[0]
        else:
            alpha = 1

        val = norm(val, _t0, _t1)
        
        _draw_point(ax, orientation, val, closed, color, point_size, alpha)

    # Inequalities
    for ineq in inequalities:
        op, val, *args = ineq
        val = norm(val, _t0, _t1)
        
        if args:
            color, *args = args
        else:
            color = "blue"

        if args:
            alpha = args[0]
        else:
            alpha = 1
            
        _draw_inequality(ax, orientation, op, val, color, line_thickness, point_size, alpha)
        
    # Ranges
    for cineq in compound_inequalities:
        low, high, *args = cineq
        if args:
            closed_low, *args = args
        else:
            closed_low = True
            
        if args:
            closed_high, *args = args
        else:
            closed_high = True

        if args:
            color, *args = args
        else:
            color = "blue"

        if args:
            alpha = args[0]
        else:
            alpha = 1
            
        low = norm(low, _t0, _t1)
        high = norm(high, _t0, _t1)
        _draw_range(ax, orientation, low, high, closed_low, closed_high, color, point_size, alpha)

    # Distances
    for i, (a, b, *maybe_dir) in enumerate(distances):
        direction = maybe_dir[0] if maybe_dir else None
        distance = abs(b - a)
        a = norm(a, _t0, _t1)
        b = norm(b, _t0, _t1)
        
        label = f"{'+' if b > a else '-'}{distance} {unit_label}" if direction else f"{distance} {unit_label}"
        _draw_distance_bracket(
            ax,
            orientation,
            a,
            b,
            label=label,
            flip=(i % 2 == 1),
            tick_length=tick_length,
            tick_fontsize=tick_fontsize,
            spacing= (i // 2) * 1.5,
            direction=direction
        )

    if title:
        ax.set_title(title, fontsize=tick_fontsize + 4)

    plt.tight_layout()
    
    if output:
        plt.savefig(output)

    return fig, ax


# === Subcomponents ===

def _draw_number_line(ax, orientation, arrow, lw):
    props = dict(arrowstyle="<|-|>,head_width=0.5,head_length=1.25", color="black")
    if arrow:
        if orientation == "horizontal":
            ax.annotate("", (-0.05, 0), (1.05, 0), arrowprops=props, zorder=2)
        else:
            ax.annotate("", (0.0, -0.05), (0, 1.05), arrowprops=props, zorder=2)
    else:
        if orientation == "horizontal":
            ax.plot([1, 0], [0, 0], color="black", lw=lw, zorder=2)
        else:
            ax.plot([0, 0], [1, 0], color="black", lw=lw, zorder=2)


def _draw_ticks(ax, orientation, ticks, labels, length, fontsize):
    for tick, label in zip(ticks, labels):
        if orientation == "horizontal":
            ax.plot([tick, tick], [-length / 2, length / 2], color="black", lw=1.5)
            ax.text(tick, -length, str(label), ha="center", va="top", fontsize=fontsize)
        else:
            ax.plot([-length / 2, length / 2], [tick, tick], color="black", lw=1.5)
            ax.text(-length * 1.5, tick, str(label), ha="right", va="center", fontsize=fontsize)


def _draw_point(ax, orientation, val, closed, color, size, alpha=1, z=4):
    face = color if closed else "white"
    coords = (val, 0) if orientation == "horizontal" else (0, val)
    ax.plot(*coords, "o", markersize=size, markeredgewidth=2.5,
            markerfacecolor=face, markeredgecolor=color, alpha=alpha, zorder=z)


def _draw_inequality(ax, orientation, op, val, color, lw, size, alpha):
    closed = "=" in op
    head = "<|-" if "<" in op else "-|>"
    head += ",head_width=0.5,head_length=1.25"
    if orientation == "horizontal":
        coords = ((-0.05, 0), (val, 0)) if "<" in op else ((val, 0), (1.05, 0))
    else:
        coords = ((0, -0.05), (0, val)) if "<" in op else ((0, val), (0, 1.05))
    ax.annotate("", coords[1], coords[0], arrowprops=dict(arrowstyle=head, color=color, lw=2 * lw, alpha=alpha), zorder=3)
    _draw_point(ax, orientation, val, closed, color, size, 4, 1)


def _draw_range(ax, orientation, a, b, ca, cb, color, size, alpha):
    x = np.linspace(a, b, 300)
    if orientation == "horizontal":
        ax.plot(x, np.zeros_like(x), color=color, lw=4, zorder=3, alpha=alpha)
    else:
        ax.plot(np.zeros_like(x), x, color=color, lw=4, zorder=3, alpha=alpha)
    _draw_point(ax, orientation, a, ca, color, size, 3, 1)
    _draw_point(ax, orientation, b, cb, color, size, 3, 1)


def _draw_distance_bracket(ax, orientation, x0, x1, label, flip, tick_length, tick_fontsize, spacing, direction=None):
    x0, x1 = sorted([x0, x1])
    mid = (x0 + x1) / 2
    direction_sign = -1 if flip else 1
    base_offset  = 0.25 * direction_sign
    arrow_offset = 0.2 if direction else 0
    
    # Padding based on tick size and label font
    vertical_offset = tick_length + tick_fontsize * 0.08 + spacing * 2 + arrow_offset
    base_y = base_offset * vertical_offset - 0.1
    top_y = base_y + direction_sign * 0.2
    spike_y = top_y + direction_sign * 0.15
    label_y = spike_y + direction_sign * 0.05

    lw = 1.25

    if orientation == "horizontal":
        # Draw uprights
        ax.vlines([x0, x1], base_y, top_y, color="black", lw=lw)
        # Draw top bar
        ax.hlines(top_y, x0, x1, color="black", lw=lw)
        # Draw center spike
        ax.vlines(mid, top_y, spike_y, color="black", lw=lw)
        # Draw label
        ax.text(mid, label_y, label, ha="center", va="bottom" if direction_sign > 0 else "top", fontsize=12)
        # Optional arrows
        if direction == "left":
            ax.annotate("", (x0, base_y - 0.1 * direction_sign), (x0, base_y),
                        arrowprops=dict(arrowstyle="-|>", color="black", lw=lw))
        elif direction == "right":
            ax.annotate("", (x1, base_y - 0.1 * direction_sign), (x1, base_y),
                        arrowprops=dict(arrowstyle="-|>", color="black", lw=lw))
    else:
        raise NotImplementedError("Vertical bracket not supported yet.")
