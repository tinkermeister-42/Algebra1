import matplotlib.pyplot as plt
import numpy as np


def plot_number_line_with_points(
    line_range=(-10, 10, 1),
    orientation="horizontal",
    figsize=10,
    title=None,
    line_thickness=None,
    tick_length=None,
    tick_fontsize=None,
    point_size=None,
    points=None,
    inequalities=None,
    compound_inequalities=None,
    distances=None,  # NEW FEATURE
    arrow=True,
    output=None,
):
    points = points or []
    inequalities = inequalities or []
    compound_inequalities = compound_inequalities or []

    fig_height = 2 + len(distances or [0, 0]) / 2

    fig_dims = (
        (figsize, fig_height) if orientation == "horizontal" else (fig_height, figsize)
    )
    fig, ax = plt.subplots(figsize=fig_dims)
    ax.set_aspect("equal")
    ax.axis("off")

    start, end, tick_interval = line_range
    ticks = np.arange(start, end + tick_interval, tick_interval)

    margin = (end - start) * 0.05
    arrow_start = start - margin
    arrow_end = end + margin
    arrowprops = dict(
        arrowstyle="<|-|>, head_width=0.5, head_length=1.25", color="black"
    )

    # Dynamic styling
    line_thickness = (
        line_thickness if line_thickness is not None else max(figsize * 0.1, 1.5)
    )
    tick_length = tick_length if tick_length is not None else max(figsize * 0.025, 0.1)
    tick_fontsize = tick_fontsize if tick_fontsize is not None else int(figsize * 1.2)
    point_size = point_size if point_size is not None else max(figsize * 1.2, 6)

    # Tick mark labels
    def draw_tick_labels():
        for t in ticks:
            if orientation == "horizontal":
                ax.plot(
                    [t, t],
                    [-tick_length / 2, tick_length / 2],
                    color="black",
                    lw=1.5,
                    zorder=2,
                )
                ax.text(
                    t,
                    -tick_length * 1.8,
                    str(t),
                    ha="center",
                    va="top",
                    fontsize=tick_fontsize,
                )
            else:
                ax.plot(
                    [-tick_length / 2, tick_length / 2],
                    [t, t],
                    color="black",
                    lw=1.5,
                    zorder=2,
                )
                ax.text(
                    -tick_length * 3.0,
                    t,
                    str(t),
                    ha="right",
                    va="center",
                    fontsize=tick_fontsize,
                )

    def plot_dot(val, closed, color, zorder=4):
        face = color if closed else "white"
        edge = color
        if orientation == "horizontal":
            ax.plot(
                val,
                0,
                "o",
                markersize=point_size,
                markeredgewidth=2.5,
                markerfacecolor=face,
                markeredgecolor=edge,
                zorder=zorder,
            )
        else:
            ax.plot(
                0,
                val,
                "o",
                markersize=point_size,
                markeredgewidth=2.5,
                markerfacecolor=face,
                markeredgecolor=edge,
                zorder=zorder,
            )

    def plot_ray(op, val, color):
        closed = "=" in op
        style = f"head_width=0.5, head_length=1.25"

        if orientation == "horizontal":
            if "<" in op:
                style = "<|-, " + style
                start_xy, end_xy = (arrow_start, 0), (val, 0)
            else:
                style = "-|>, " + style
                start_xy, end_xy = (val, 0), (arrow_end, 0)
        else:
            if "<" in op:
                style = "<|-, " + style
                start_xy, end_xy = (0, arrow_start), (0, val)
            else:
                style = "-|>, " + style
                start_xy, end_xy = (0, val), (0, arrow_end)

        ax.annotate(
            "",
            xy=end_xy,
            xytext=start_xy,
            arrowprops=dict(arrowstyle=style, color=color, lw=2 * line_thickness),
            zorder=3,
        )
        plot_dot(val, closed, color, zorder=3)

    def plot_range(a, b, closed_a, closed_b, color):
        x = np.linspace(a, b, 300)
        if orientation == "horizontal":
            y = np.zeros_like(x)
            ax.plot(x, y, color=color, lw=4, zorder=3)
            plot_dot(a, closed_a, color)
            plot_dot(b, closed_b, color)
        else:
            y = np.linspace(a, b, 300)
            x = np.zeros_like(y)
            ax.plot(x, y, color=color, lw=4, zorder=3)
            plot_dot(a, closed_a, color, zorder=3)
            plot_dot(b, closed_b, color, zorder=3)

    def draw_goalpost_distance(
        ax,
        x0,
        x1,
        base_y=0.4,
        height=0.6,
        color="black",
        label=None,
        flip=False,
        distance_arrows=None,
    ):
        direction = -1 if flip else 1
        top_y = base_y + height * direction
        spike_y = top_y + 0.25 * direction
        label_y = spike_y + 0.15 * direction
        mid = (x0 + x1) / 2
        lw = 2.2
    
        # Draw uprights
        ax.vlines([x0, x1], ymin=base_y, ymax=top_y, color=color, lw=lw, zorder=5)
        ax.hlines(y=top_y, xmin=x0, xmax=x1, color=color, lw=lw, zorder=5)
        ax.vlines(mid, ymin=top_y, ymax=spike_y, color=color, lw=lw, zorder=5)
    
        # Draw directional arrow at base (optional)
        arrow_length = 0.3
        arrow_dir = -direction  # Always point away from number line
    
        if distance_arrows == "left":
            ax.annotate(
                "",
                xy=(x0, base_y + arrow_length * arrow_dir),
                xytext=(x0, base_y),
                arrowprops=dict(arrowstyle="->", color=color, lw=lw),
                zorder=6,
            )
        elif distance_arrows == "right":
            ax.annotate(
                "",
                xy=(x1, base_y + arrow_length * arrow_dir),
                xytext=(x1, base_y),
                arrowprops=dict(arrowstyle="->", color=color, lw=lw),
                zorder=6,
            )
    
        # Draw label
        va = "bottom" if direction > 0 else "top"
        if label:
            ax.text(
                mid,
                label_y,
                label,
                ha="center",
                va=va,
                fontsize=12,
                color=color,
                zorder=6,
            )

        # Draw center spike
        ax.vlines(mid, ymin=top_y, ymax=spike_y, color=color, lw=lw, zorder=5)

        # Draw label
        va = "bottom" if direction > 0 else "top"
        if label:
            ax.text(
                mid,
                label_y,
                label,
                ha="center",
                va=va,
                fontsize=12,
                color=color,
                zorder=6,
            )

    # Draw number line
    if orientation == "horizontal":
        if arrow:
            ax.annotate(
                "",
                xy=(arrow_end, 0),
                xytext=(arrow_start, 0),
                arrowprops=arrowprops,
                zorder=2,
            )
        else:
            ax.plot([start, end], [0, 0], color="black", lw=line_thickness, zorder=2)
        ax.set_xlim(arrow_start - 0.5, arrow_end + 0.5)
        extra_y = len(distances) if distances else 1
        ax.set_ylim(-extra_y, extra_y + 2)
    else:
        if arrow:
            ax.annotate(
                "",
                xy=(0, arrow_end),
                xytext=(0, arrow_start),
                arrowprops=arrowprops,
                zorder=2,
            )
        else:
            ax.plot([0, 0], [start, end], color="black", lw=line_thickness, zorder=2)
            
        ax.set_ylim(arrow_start - 0.5, arrow_end + 0.5)
        ax.set_xlim(-2.5, 1.5)

    if title:
        ax.set_title(title, fontsize=tick_fontsize + 4, pad=10)  # was 30

    draw_tick_labels()

    for val, closed, color in points:
        plot_dot(val, closed, color)

    for op, val, color in inequalities:
        plot_ray(op, val, color)

    for low, high, closed_low, closed_high, color in compound_inequalities:
        plot_range(low, high, closed_low, closed_high, color)

    if distances:
        for i, (a, b, *args) in enumerate(distances):
            x0, x1 = sorted([a, b])
            if args:
                distance_arrows = args[0]
            else:
                distance_arrows = None
                
            flip = i % 2 == 1
            base_y = 0.5 if not flip else -1.1
            if distance_arrows:
                sgn = "+" if b > a else "-"
            else:
                sgn = ""
            
            label = f"{sgn}{abs(a - b)} units"
            draw_goalpost_distance(
                ax,
                x0,
                x1,
                base_y=base_y,
                height=0.5,
                label=label,
                flip=flip,
                distance_arrows=distance_arrows,
            )

    plt.tight_layout()

    if output:
        plt.savefig(output)

    plt.show()