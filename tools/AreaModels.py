"""
algebra_tiles.py — Area Model / Algebra Tiles Generator

Usage:
    from algebra_tiles import Segment, draw_area_model

    draw_area_model(
        h_segments=[Segment("var", 1, "x"), Segment("const", 3)],
        v_segments=[Segment("const", 4)],
        title="4(x + 3) as an Area Model",
        title_pad=60,
        top_label_offset=0.12,
        save_path="area_model_4_(x+3).png",
        transparent=True
    )
"""

from dataclasses import dataclass
import math
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# ---------------------------
# Data structure for a side piece
# ---------------------------
@dataclass
class Segment:
    kind: str                  # 'const' or 'var'
    value: float               # const: length (in units); var: coefficient (e.g., 2 in 2x)
    var: Optional[str] = None  # variable name when kind == 'var' (e.g., 'x', 'y')
    label: Optional[str] = None  # optional text override for side label


# ---------------------------
# Formatting utilities
# ---------------------------
def _format_num(n: float) -> str:
    """Pretty-print numeric values without awkward trailing zeros."""
    if abs(n - round(n)) < 1e-9:
        return str(int(round(n)))
    return f"{n:.4g}"


def _mono_label(numeric: float, vars_dict: Dict[str, int]) -> str:
    """Build a product label like 12x^2y from numeric factor + variable powers."""
    var_part = ""
    for v in sorted(vars_dict.keys()):
        power = vars_dict[v]
        if power == 1:
            var_part += v
        else:
            var_part += f"{v}^{power}"

    if math.isclose(numeric, 1.0, rel_tol=1e-12, abs_tol=1e-12):
        return var_part if var_part else "1"
    if math.isclose(numeric, -1.0, rel_tol=1e-12, abs_tol=1e-12):
        return f"-{var_part}" if var_part else "-1"

    return f"{_format_num(numeric)}{var_part}"


def _segment_length(seg: Segment, unit: float, var_len: Dict[str, float]) -> float:
    """Compute the drawn length of a segment."""
    if seg.kind == "const":
        return seg.value * unit
    if seg.kind == "var":
        base = var_len.get(seg.var or "x", 3.0)
        return seg.value * base
    raise ValueError(f"Unknown segment kind: {seg.kind}")


def _segment_label(seg: Segment) -> str:
    """Choose a label for a side segment (respects custom overrides)."""
    if seg.label is not None:
        return seg.label

    if seg.kind == "const":
        return _format_num(seg.value)

    coeff = seg.value
    v = seg.var or "x"
    if math.isclose(coeff, 1.0):
        return f"{v}"
    if math.isclose(coeff, -1.0):
        return f"-{v}"
    return f"{_format_num(coeff)}{v}"


def _product_label(h: Segment, v: Segment) -> str:
    """Label inside each tile: multiply numeric factors; add variable powers."""
    numeric = 1.0
    vars_dict: Dict[str, int] = {}

    # Horizontal contribution
    if h.kind == "const":
        numeric *= h.value
    else:
        numeric *= h.value
        vars_dict[h.var or "x"] = vars_dict.get(h.var or "x", 0) + 1

    # Vertical contribution
    if v.kind == "const":
        numeric *= v.value
    else:
        numeric *= v.value
        vars_dict[v.var or "x"] = vars_dict.get(v.var or "x", 0) + 1

    return _mono_label(numeric, vars_dict)


# ---------------------------
# Main drawing routine
# ---------------------------
def draw_area_model(
    h_segments: List[Segment],
    v_segments: List[Segment],
    var_lengths: Optional[Dict[str, float]] = None,
    const_unit: float = 1.0,
    tile_facecolors: Optional[Dict[str, str]] = None,
    edgecolor: str = "black",
    linewidth: float = 1.5,
    fontsize: int = 12,
    title: Optional[str] = None,
    title_pad: float = 50.0,           # moves title up away from labels
    annotate_sides: bool = True,
    top_label_offset: float = 0.10,    # fraction of total height for top labels
    save_path: Optional[str] = None,
    transparent: bool = True,
    fig_scale: float = 1.0,
):
    """
    Render an area model / algebra tiles diagram for
    (sum of h_segments) by (sum of v_segments).

    h_segments: list of Segment for the top side (e.g., [Segment('var',1,'x'), Segment('const',3)] for x+3)
    v_segments: list of Segment for the left side (e.g., [Segment('const',4)] for 4)
    var_lengths: visual length for variables, e.g., {'x': 3.0, 'y': 2.5}
    const_unit: visual length of constant "1"
    tile_facecolors: mapping type → color; keys:
        'const*const', 'const*var', 'var*const', 'var*var'
    """
    if var_lengths is None:
        var_lengths = {"x": 3.0, "y": 2.5}

    if tile_facecolors is None:
        tile_facecolors = {
            "const*const": "#fde0c5",  # peach
            "const*var":   "#e6f5d0",  # light green
            "var*const":   "#e6f5d0",  # light green
            "var*var":     "#cfe8ff",  # light blue
        }

    widths = [_segment_length(seg, const_unit, var_lengths) for seg in h_segments]
    heights = [_segment_length(seg, const_unit, var_lengths) for seg in v_segments]
    total_w = sum(widths)
    total_h = sum(heights)

    base_w = max(4.0, total_w * 0.8) * fig_scale
    base_h = max(3.0, total_h * 0.8) * fig_scale

    fig, ax = plt.subplots(figsize=(base_w, base_h), dpi=150)
    ax.set_xlim(0, total_w)
    ax.set_ylim(0, total_h)
    ax.set_aspect("equal")
    ax.axis("off")

    # Draw tiles
    y0 = 0.0
    for r, vseg in enumerate(v_segments):
        row_h = heights[r]
        x0 = 0.0
        for c, hseg in enumerate(h_segments):
            col_w = widths[c]
            key = f"{vseg.kind}*{hseg.kind}"
            facecolor = tile_facecolors.get(key, "#ffffff")

            rect = Rectangle((x0, y0), col_w, row_h,
                             facecolor=facecolor, edgecolor=edgecolor, linewidth=linewidth)
            ax.add_patch(rect)

            # Center label for the product
            label = _product_label(hseg, vseg)
            ax.text(x0 + col_w / 2, y0 + row_h / 2, label,
                    ha="center", va="center", fontsize=fontsize)

            x0 += col_w
        y0 += row_h

    # Outer border
    outer = Rectangle((0, 0), total_w, total_h, fill=False,
                      edgecolor=edgecolor, linewidth=linewidth + 0.5)
    ax.add_patch(outer)

    # Side annotations
    if annotate_sides:
        # Top labels
        x_center = 0.0
        for w, seg in zip(widths, h_segments):
            ax.text(x_center + w / 2, total_h + top_label_offset * total_h,
                    _segment_label(seg), ha="center", va="bottom", fontsize=fontsize)
            x_center += w

        # Left labels (rotated)
        y_center = 0.0
        for h, seg in zip(heights, v_segments):
            ax.text(-0.02 * total_w, y_center + h / 2, _segment_label(seg),
                    ha="right", va="center", rotation=90, fontsize=fontsize)
            y_center += h

    if title:
        ax.set_title(title, pad=title_pad)

    # Breathing room for title + labels
    plt.tight_layout()
    plt.subplots_adjust(top=0.84)

    out_path = None
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", transparent=transparent)
        out_path = save_path

    plt.show()
    return out_path


# ---------------------------
# Optional quick demo when run directly
# ---------------------------
if __name__ == "__main__":
    # 4(x+3)
    draw_area_model(
        h_segments=[Segment("var", 1, "x"), Segment("const", 3)],
        v_segments=[Segment("const", 4)],
        title="4(x + 3) as an Area Model",
        title_pad=60,
        top_label_offset=0.12,
        save_path="area_model_4_(x+3).png",
        transparent=True,
        fig_scale=1.1
    )

    # (x+2)(x+3)
    draw_area_model(
        h_segments=[Segment("var", 1, "x"), Segment("const", 2)],
        v_segments=[Segment("var", 1, "x"), Segment("const", 3)],
        title="(x + 2)(x + 3) Area Model",
        title_pad=60,
        top_label_offset=0.12,
        save_path="area_model_(x+2)(x+3).png",
        transparent=True,
        fig_scale=1.1
    )
