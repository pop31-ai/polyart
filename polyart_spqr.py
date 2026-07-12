import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyBboxPatch, Circle, Arc, Wedge, FancyArrowPatch

DARK_BG = "#0d0a1a"
STONE = "#c8b898"
STONE_DARK = "#a09070"
STONE_LIGHT = "#d8c8a8"
GOLD = "#c8a040"
SHADOW = "#2a2030"
DEEP_SHADOW = "#18102a"
HIGHLIGHT = "#e8d8b8"

def _etch_line(ax, x1, y1, x2, y2, color=STONE, passes=3, spread=0.002, lw=0.3, alpha=0.5):
    for i in range(passes):
        off = (i - passes / 2) * spread
        ax.plot([x1 + off, x2 + off], [y1 + off * 0.7, y2 + off * 0.7],
                color=color, linewidth=lw, alpha=alpha / (1 + abs(i - passes / 2) * 0.3),
                solid_capstyle="round")

def _etch_poly(ax, verts, facecolor=SHADOW, edgecolor=STONE, lw=0.3, alpha=0.6):
    poly = Polygon(verts, closed=True, facecolor=facecolor, edgecolor=edgecolor,
                   linewidth=lw, alpha=alpha, zorder=1)
    ax.add_patch(poly)

def _fill_arch(ax, cx, cy, w, h, color=SHADOW, alpha=0.4):
    theta = np.linspace(0, np.pi, 40)
    x = cx + w / 2 * np.cos(theta)
    y = cy + h * np.sin(theta)
    verts = list(zip(x, y))
    _etch_poly(ax, verts, facecolor=color, edgecolor=STONE_DARK, alpha=alpha)

def _hatch_area(ax, x0, y0, x1, y1, n=8, color=STONE_DARK, alpha=0.3, lw=0.2):
    for i in range(n + 1):
        t = i / n
        _etch_line(ax, x0 + t * (x1 - x0), y0, x0 + t * (x1 - x0), y1,
                   color=color, passes=2, spread=0.001, lw=lw, alpha=alpha)

def _cross_hatch(ax, x0, y0, x1, y1, n=6, color=SHADOW, alpha=0.25):
    for i in range(n + 1):
        t = i / n
        _etch_line(ax, x0 + t * (x1 - x0), y0, x1, y0 + t * (y1 - y0),
                   color=color, passes=1, spread=0.001, lw=0.15, alpha=alpha)
        _etch_line(ax, x1 - t * (x1 - x0), y0, x0, y1 - t * (y1 - y0),
                   color=color, passes=1, spread=0.001, lw=0.15, alpha=alpha)


class RomanOrders:
    @staticmethod
    def doric_column(ax, x, y, h, s):
        base_w = s * 0.35
        capital_h = s * 0.08
        shaft_bot = y
        shaft_top = y + h * 0.88
        capital_top = shaft_top + capital_h
        base_bot = y - s * 0.02

        for dx in [-0.001, 0.001]:
            _etch_line(ax, x - base_w / 2 - dx * s, base_bot, x - base_w * 0.45, shaft_bot,
                       color=STONE_DARK, passes=3, lw=0.25, alpha=0.6)
            _etch_line(ax, x + base_w / 2 + dx * s, base_bot, x + base_w * 0.45, shaft_bot,
                       color=STONE_DARK, passes=3, lw=0.25, alpha=0.6)
        _etch_poly(ax, [(x - base_w / 2, base_bot), (x + base_w / 2, base_bot),
                        (x + base_w * 0.48, shaft_bot), (x - base_w * 0.48, shaft_bot)],
                   facecolor=STONE_DARK, edgecolor=STONE, lw=0.3, alpha=0.55)

        n_flutes = 8
        for i in range(n_flutes):
            fx = x - base_w * 0.42 + (i + 0.5) / n_flutes * base_w * 0.84
            fw = base_w * 0.04
            _etch_poly(ax, [(fx - fw / 2, shaft_bot + 0.005), (fx + fw / 2, shaft_bot + 0.005),
                            (fx + fw * 0.4, shaft_top - 0.005), (fx - fw * 0.4, shaft_top - 0.005)],
                       facecolor=DEEP_SHADOW, edgecolor=STONE_DARK, lw=0.15, alpha=0.35)

        shaft_verts = [(x - base_w * 0.45, shaft_bot), (x + base_w * 0.45, shaft_bot),
                       (x + base_w * 0.42, shaft_top), (x - base_w * 0.42, shaft_top)]
        _etch_poly(ax, shaft_verts, facecolor=SHADOW, edgecolor=STONE, lw=0.3, alpha=0.4)

        _etch_poly(ax, [(x - base_w * 0.5, shaft_top), (x + base_w * 0.5, shaft_top),
                        (x + base_w * 0.52, shaft_top + capital_h * 0.4),
                        (x - base_w * 0.52, shaft_top + capital_h * 0.4)],
                   facecolor=STONE_DARK, edgecolor=STONE, lw=0.3, alpha=0.6)
        _etch_poly(ax, [(x - base_w * 0.55, shaft_top + capital_h * 0.4),
                        (x + base_w * 0.55, shaft_top + capital_h * 0.4),
                        (x + base_w * 0.58, capital_top), (x - base_w * 0.58, capital_top)],
                   facecolor=STONE, edgecolor=STONE_LIGHT, lw=0.3, alpha=0.55)
        for i in range(5):
            _etch_line(ax, x - base_w * 0.52 + i * base_w * 0.26, shaft_top,
                       x - base_w * 0.52 + i * base_w * 0.26, capital_top,
                       color=SHADOW, passes=1, lw=0.15, alpha=0.3)

    @staticmethod
    def ionic_column(ax, x, y, h, s):
        base_w = s * 0.38
        capital_h = s * 0.14
        shaft_bot = y
        shaft_top = y + h * 0.82
        capital_top = shaft_top + capital_h
        base_bot = y - s * 0.03

        _etch_poly(ax, [(x - base_w * 0.55, base_bot), (x + base_w * 0.55, base_bot),
                        (x + base_w * 0.5, shaft_bot), (x - base_w * 0.5, shaft_bot)],
                   facecolor=STONE_DARK, edgecolor=STONE, lw=0.3, alpha=0.55)
        _etch_poly(ax, [(x - base_w * 0.5, base_bot + s * 0.02),
                        (x + base_w * 0.5, base_bot + s * 0.02),
                        (x + base_w * 0.48, base_bot + s * 0.04),
                        (x - base_w * 0.48, base_bot + s * 0.04)],
                   facecolor=STONE, edgecolor=STONE_LIGHT, lw=0.25, alpha=0.45)

        shaft_verts = [(x - base_w * 0.44, shaft_bot), (x + base_w * 0.44, shaft_bot),
                       (x + base_w * 0.4, shaft_top), (x - base_w * 0.4, shaft_top)]
        _etch_poly(ax, shaft_verts, facecolor=SHADOW, edgecolor=STONE, lw=0.3, alpha=0.4)

        n_flutes = 10
        for i in range(n_flutes):
            fx = x - base_w * 0.38 + (i + 0.5) / n_flutes * base_w * 0.76
            _etch_line(ax, fx, shaft_bot + 0.01, fx * 0.98 + x * 0.02, shaft_top - 0.01,
                       color=DEEP_SHADOW, passes=2, spread=0.0008, lw=0.15, alpha=0.3)

        volute_r = capital_h * 0.38
        for side in [-1, 1]:
            vx = x + side * base_w * 0.42
            vy = shaft_top + capital_h * 0.5
            for pass_i in range(3):
                offset = (pass_i - 1) * 0.002
                theta = np.linspace(0, 4.5 * np.pi, 100)
                r = volute_r * (0.3 + 0.7 * theta / (4.5 * np.pi))
                vtheta = theta * side
                px = vx + offset + r * np.cos(vtheta) * 0.5
                py = vy + r * np.sin(vtheta) * 0.3 + offset * 0.5
                ax.plot(px, py, color=STONE, linewidth=0.2, alpha=0.55 - abs(pass_i - 1) * 0.1)

        _etch_poly(ax, [(x - base_w * 0.5, shaft_top), (x + base_w * 0.5, shaft_top),
                        (x + base_w * 0.52, shaft_top + capital_h * 0.3),
                        (x - base_w * 0.52, shaft_top + capital_h * 0.3)],
                   facecolor=SHADOW, edgecolor=STONE, lw=0.3, alpha=0.5)

        _etch_poly(ax, [(x - base_w * 0.55, capital_top - s * 0.03),
                        (x + base_w * 0.55, capital_top - s * 0.03),
                        (x + base_w * 0.55, capital_top),
                        (x - base_w * 0.55, capital_top)],
                   facecolor=STONE, edgecolor=STONE_LIGHT, lw=0.3, alpha=0.55)

    @staticmethod
    def corinthian_column(ax, x, y, h, s):
        base_w = s * 0.4
        capital_h = s * 0.22
        shaft_bot = y
        shaft_top = y + h * 0.72
        capital_top = shaft_top + capital_h
        base_bot = y - s * 0.03

        for layer in range(3):
            lw_ = base_w * (0.6 + layer * 0.15)
            lh = s * 0.015
            ly = base_bot + layer * lh
            _etch_poly(ax, [(x - lw_ / 2, ly), (x + lw_ / 2, ly),
                            (x + lw_ * 0.47, ly + lh), (x - lw_ * 0.47, ly + lh)],
                       facecolor=STONE if layer % 2 == 0 else STONE_DARK,
                       edgecolor=STONE_LIGHT, lw=0.2, alpha=0.55)

        shaft_verts = [(x - base_w * 0.44, base_bot + s * 0.04), (x + base_w * 0.44, base_bot + s * 0.04),
                       (x + base_w * 0.4, shaft_top), (x - base_w * 0.4, shaft_top)]
        _etch_poly(ax, shaft_verts, facecolor=SHADOW, edgecolor=STONE, lw=0.3, alpha=0.4)

        n_flutes = 12
        for i in range(n_flutes):
            fx = x - base_w * 0.38 + (i + 0.5) / n_flutes * base_w * 0.76
            _etch_line(ax, fx, base_bot + s * 0.05, fx * 0.97 + x * 0.03, shaft_top - 0.005,
                       color=DEEP_SHADOW, passes=2, spread=0.0006, lw=0.13, alpha=0.28)

        _etch_poly(ax, [(x - base_w * 0.38, shaft_top), (x + base_w * 0.38, shaft_top),
                        (x + base_w * 0.42, shaft_top + s * 0.04),
                        (x - base_w * 0.42, shaft_top + s * 0.04)],
                   facecolor=STONE_DARK, edgecolor=STONE, lw=0.3, alpha=0.5)

        for row in range(4):
            for col in range(5):
                lx = x - base_w * 0.45 + col * base_w * 0.225
                ly = shaft_top + s * 0.04 + row * capital_h * 0.22
                leaf_size = capital_h * 0.12 * (1 + 0.3 * (3 - row) / 3)
                n_pts = 7
                angles = np.linspace(0, 2 * np.pi, n_pts, endpoint=False)
                pts = []
                for a in angles:
                    r = leaf_size * (0.5 + 0.5 * (1 + np.cos(a * 3)) / 2)
                    pts.append((lx + r * np.cos(a) * 0.6, ly + r * np.sin(a) * 0.4))
                _etch_poly(ax, pts, facecolor=SHADOW if (row + col) % 2 == 0 else DEEP_SHADOW,
                           edgecolor=STONE, lw=0.18, alpha=0.45)
                _etch_line(ax, lx, ly - leaf_size * 0.3, lx, ly + leaf_size * 0.3,
                           color=STONE_DARK, passes=2, lw=0.12, alpha=0.4)

        _etch_poly(ax, [(x - base_w * 0.52, capital_top - s * 0.03),
                        (x + base_w * 0.52, capital_top - s * 0.03),
                        (x + base_w * 0.55, capital_top), (x - base_w * 0.55, capital_top)],
                   facecolor=STONE, edgecolor=STONE_LIGHT, lw=0.3, alpha=0.55)


class RomanArch:
    @staticmethod
    def semicircular_arch(ax, cx, cy, w, h, s):
        thickness = s * 0.06
        theta = np.linspace(0, np.pi, 50)
        x_out = cx + w / 2 * np.cos(theta)
        y_out = cy + h * np.sin(theta)
        x_in = cx + (w / 2 - thickness) * np.cos(theta)
        y_in = cy + (h - thickness) * np.sin(theta)

        verts_outer = list(zip(x_out, y_out))
        verts_inner = list(zip(x_in[::-1], y_in[::-1]))
        all_verts = verts_outer + verts_inner
        _etch_poly(ax, all_verts, facecolor=SHADOW, edgecolor=STONE, lw=0.4, alpha=0.5)

        for i in range(len(theta) - 1):
            j = i + 1
            for pass_i in range(3):
                off = (pass_i - 1) * 0.003
                ax.plot([x_out[i] + off, x_out[j] + off], [y_out[i], y_out[j]],
                        color=STONE, linewidth=0.25, alpha=0.55)
                ax.plot([x_in[i] + off, x_in[j] + off], [y_in[i], y_in[j]],
                        color=STONE_DARK, linewidth=0.2, alpha=0.45)

        for i in range(8):
            t = i / 7
            mx = cx + (w / 2 - thickness / 2) * np.cos(t * np.pi)
            my = cy + (h - thickness / 2) * np.sin(t * np.pi)
            _etch_line(ax, mx, my, mx, my - h * 0.02,
                       color=STONE_DARK, passes=2, lw=0.15, alpha=0.3)

        pillar_w = w * 0.15
        for side in [-1, 1]:
            px = cx + side * (w / 2 - pillar_w / 2)
            _etch_poly(ax, [(px - pillar_w / 2, cy), (px + pillar_w / 2, cy),
                            (px + pillar_w / 2 * 0.9, cy - h * 0.6),
                            (px - pillar_w / 2 * 0.9, cy - h * 0.6)],
                       facecolor=SHADOW, edgecolor=STONE, lw=0.3, alpha=0.45)
            _hatch_area(ax, px - pillar_w * 0.45, cy - h * 0.6,
                        px + pillar_w * 0.45, cy, n=4, alpha=0.25)

    @staticmethod
    def pointed_arch(ax, cx, cy, w, h, s):
        thickness = s * 0.05
        theta = np.linspace(0, np.pi, 50)
        sharpness = 1.6
        x_out = cx + w / 2 * np.sin(theta)
        y_out = cy + h * (np.sin(theta)) ** (1 / sharpness)
        inner_theta = np.linspace(0, np.pi, 50)
        x_in = cx + (w / 2 - thickness) * np.sin(inner_theta)
        y_in = cy + (h - thickness) * (np.sin(inner_theta)) ** (1 / sharpness)

        for pass_i in range(3):
            off = (pass_i - 1) * 0.002
            ax.plot(x_out + off, y_out, color=STONE, linewidth=0.3, alpha=0.6 - abs(pass_i) * 0.1)
            ax.plot(x_in + off, y_in, color=STONE_DARK, linewidth=0.25, alpha=0.5 - abs(pass_i) * 0.1)

        verts = list(zip(x_out, y_out)) + list(zip(x_in[::-1], y_in[::-1]))
        _etch_poly(ax, verts, facecolor=SHADOW, edgecolor=STONE, lw=0.3, alpha=0.45)

        pillar_w = w * 0.12
        for side in [-1, 1]:
            px = cx + side * (w / 2 - pillar_w / 2)
            _etch_poly(ax, [(px - pillar_w / 2, cy), (px + pillar_w / 2, cy),
                            (px + pillar_w * 0.4, cy - h * 0.5),
                            (px - pillar_w * 0.4, cy - h * 0.5)],
                       facecolor=SHADOW, edgecolor=STONE, lw=0.3, alpha=0.4)

    @staticmethod
    def aqueduct_segment(ax, cx, cy, w, h, n_arches, s):
        total_w = w
        arch_w = total_w / n_arches * 0.75
        gap_w = total_w / n_arches * 0.25
        start_x = cx - total_w / 2

        wall_h = h * 0.25
        _etch_poly(ax, [(start_x, cy), (start_x + total_w, cy),
                        (start_x + total_w, cy + wall_h), (start_x, cy + wall_h)],
                   facecolor=SHADOW, edgecolor=STONE, lw=0.3, alpha=0.5)
        _hatch_area(ax, start_x, cy, start_x + total_w, cy + wall_h, n=12, alpha=0.2)

        for tier in range(2):
            tier_y = cy - tier * h * 0.35
            tier_h = h * 0.35 if tier == 0 else h * 0.3
            tier_arch_w = arch_w * (1 - tier * 0.15)
            n = n_arches + tier
            seg_w = total_w / n
            aw = seg_w * 0.7
            for i in range(n):
                arch_cx = start_x + seg_w * (i + 0.5)
                RomanArch.semicircular_arch(ax, arch_cx, tier_y, aw, tier_h, s)

        top_w = total_w * 0.95
        _etch_poly(ax, [(cx - top_w / 2, cy + wall_h), (cx + top_w / 2, cy + wall_h),
                        (cx + top_w / 2, cy + wall_h + h * 0.05),
                        (cx - top_w / 2, cy + wall_h + h * 0.05)],
                   facecolor=STONE_DARK, edgecolor=STONE, lw=0.3, alpha=0.55)

    @staticmethod
    def triumphal_arch(ax, cx, cy, w, h, s):
        main_w = w * 0.45
        main_h = h * 0.65
        RomanArch.semicircular_arch(ax, cx, cy, main_w, main_h, s)

        _etch_poly(ax, [(cx - w / 2, cy - h * 0.3), (cx + w / 2, cy - h * 0.3),
                        (cx + w / 2, cy + main_h * 0.15), (cx - w / 2, cy + main_h * 0.15)],
                   facecolor=SHADOW, edgecolor=STONE, lw=0.4, alpha=0.45)

        for i in range(12):
            _etch_line(ax, cx - w / 2, cy - h * 0.3 + i * h * 0.04,
                       cx + w / 2, cy - h * 0.3 + i * h * 0.04,
                       color=STONE_DARK, passes=1, lw=0.12, alpha=0.2)

        for side in [-1, 1]:
            px = cx + side * (w / 2 * 0.75)
            RomanOrders.doric_column(ax, px, cy - h * 0.3, h * 0.45, s)

        attic_h = h * 0.2
        _etch_poly(ax, [(cx - w / 2, cy + main_h * 0.15), (cx + w / 2, cy + main_h * 0.15),
                        (cx + w / 2, cy + main_h * 0.15 + attic_h),
                        (cx - w / 2, cy + main_h * 0.15 + attic_h)],
                   facecolor=STONE_DARK, edgecolor=STONE, lw=0.4, alpha=0.55)

        pediment = [(cx - w * 0.45, cy + main_h * 0.15 + attic_h),
                    (cx, cy + main_h * 0.15 + attic_h + h * 0.12),
                    (cx + w * 0.45, cy + main_h * 0.15 + attic_h)]
        _etch_poly(ax, pediment, facecolor=SHADOW, edgecolor=STONE, lw=0.4, alpha=0.5)

        text_y = cy + main_h * 0.15 + attic_h * 0.5
        for dx in [-0.002, 0, 0.002]:
            ax.text(cx + dx, text_y, "SPQR", fontsize=s * 0.08, color=GOLD,
                    ha="center", va="center", alpha=0.7, fontweight="bold",
                    fontfamily="serif")

        for side in [-1, 1]:
            small_x = cx + side * (w / 2 * 0.92)
            small_arch_h = main_h * 0.35
            RomanArch.semicircular_arch(ax, small_x, cy - h * 0.1, main_w * 0.3, small_arch_h, s * 0.5)


class PiranesiArchitecture:
    @staticmethod
    def infinite_staircase(ax, cx, cy, s):
        n_steps = 18
        step_w = s * 0.08
        step_h = s * 0.025
        for i in range(n_steps):
            t = i / n_steps
            angle = t * np.pi * 1.2 - np.pi * 0.6
            radius = s * (0.12 + t * 0.25)
            sx = cx + radius * np.cos(angle)
            sy = cy + radius * np.sin(angle) * 0.5 + t * s * 0.15
            sw = step_w * (1 - t * 0.3)
            sh = step_h * (0.8 + 0.2 * (1 - t))

            _etch_poly(ax, [(sx - sw / 2, sy), (sx + sw / 2, sy),
                            (sx + sw / 2, sy + sh), (sx - sw / 2, sy + sh)],
                       facecolor=SHADOW if i % 2 == 0 else DEEP_SHADOW,
                       edgecolor=STONE, lw=0.25, alpha=0.6 - t * 0.2)

            for pass_i in range(2):
                off = (pass_i - 0.5) * 0.001
                _etch_line(ax, sx - sw / 2, sy + sh, sx - sw / 2 + sw * 0.3, sy + sh + s * 0.03,
                           color=STONE_DARK, passes=1, lw=0.15, alpha=0.35)
                _etch_line(ax, sx + sw / 2, sy + sh, sx + sw / 2, sy + sh + s * 0.03,
                           color=STONE_DARK, passes=1, lw=0.15, alpha=0.3)

        for ring in range(3):
            r = s * (0.08 + ring * 0.12)
            arch_theta = np.linspace(0, np.pi * 2, 60)
            for pass_i in range(2):
                off = (pass_i - 0.5) * 0.002
                ax.plot(cx + r * np.cos(arch_theta) + off,
                        cy + s * 0.3 + r * 0.3 * np.sin(arch_theta) + off,
                        color=STONE, linewidth=0.2, alpha=0.35 - ring * 0.08)

        pillar_h = s * 0.35
        for side in [-1, 1]:
            px = cx + side * s * 0.35
            _etch_poly(ax, [(px - s * 0.02, cy + s * 0.15), (px + s * 0.02, cy + s * 0.15),
                            (px + s * 0.015, cy + s * 0.15 + pillar_h),
                            (px - s * 0.015, cy + s * 0.15 + pillar_h)],
                       facecolor=SHADOW, edgecolor=STONE, lw=0.3, alpha=0.5)
            _hatch_area(ax, px - s * 0.015, cy + s * 0.15,
                        px + s * 0.015, cy + s * 0.15 + pillar_h, n=5, alpha=0.2)

        chain_pts = []
        for i in range(20):
            t = i / 19
            chain_pts.append((cx - s * 0.15 + t * s * 0.3, cy + s * 0.4 + np.sin(t * 6) * s * 0.02))
        for pass_i in range(3):
            off = (pass_i - 1) * 0.001
            xs = [p[0] + off for p in chain_pts]
            ys = [p[1] + off * 0.3 for p in chain_pts]
            ax.plot(xs, ys, color=STONE_DARK, linewidth=0.4, alpha=0.5, linestyle="-")

        for i in range(8):
            tx = cx + (i - 3.5) * s * 0.03
            ty = cy - s * 0.05 - i * s * 0.04
            _etch_line(ax, tx, ty, tx + s * 0.01, ty - s * 0.03,
                       color=STONE_DARK, passes=1, lw=0.1, alpha=0.25)

    @staticmethod
    def impossible_corridor(ax, cx, cy, s):
        depth = s * 0.3
        width = s * 0.5
        height = s * 0.25

        for layer in range(4):
            t = layer / 3
            shr = 1 - t * 0.6
            sw = width * shr
            sh = height * shr
            sd = depth * t
            ox = cx + sd * 0.15
            oy = cy + sd * 0.08

            floor_verts = [(ox - sw / 2, oy - sh / 2), (ox + sw / 2, oy - sh / 2),
                           (ox + sw / 2 + depth * 0.08, oy - sh / 2 - depth * 0.05),
                           (ox - sw / 2 - depth * 0.08, oy - sh / 2 - depth * 0.05)]
            _etch_poly(ax, floor_verts, facecolor=DEEP_SHADOW, edgecolor=STONE_DARK, lw=0.2, alpha=0.35 - t * 0.05)

            ceil_verts = [(ox - sw / 2, oy + sh / 2), (ox + sw / 2, oy + sh / 2),
                          (ox + sw / 2 + depth * 0.08, oy + sh / 2 + depth * 0.04),
                          (ox - sw / 2 - depth * 0.08, oy + sh / 2 + depth * 0.04)]
            _etch_poly(ax, ceil_verts, facecolor=SHADOW, edgecolor=STONE, lw=0.2, alpha=0.35 - t * 0.05)

            left_verts = [(ox - sw / 2, oy - sh / 2), (ox - sw / 2, oy + sh / 2),
                          (ox - sw / 2 - depth * 0.08, oy + sh / 2 + depth * 0.04),
                          (ox - sw / 2 - depth * 0.08, oy - sh / 2 - depth * 0.05)]
            _etch_poly(ax, left_verts, facecolor=SHADOW, edgecolor=STONE_DARK, lw=0.2, alpha=0.3)

            right_verts = [(ox + sw / 2, oy - sh / 2), (ox + sw / 2, oy + sh / 2),
                           (ox + sw / 2 + depth * 0.08, oy + sh / 2 + depth * 0.04),
                           (ox + sw / 2 + depth * 0.08, oy - sh / 2 - depth * 0.05)]
            _etch_poly(ax, right_verts, facecolor=DEEP_SHADOW, edgecolor=STONE_DARK, lw=0.2, alpha=0.3)

        for i in range(6):
            t = i / 5
            px = cx - width * 0.4 + t * width * 0.8
            _etch_line(ax, px, cy - height * 0.5, px - s * 0.02, cy + height * 0.5,
                       color=STONE_DARK, passes=2, lw=0.2, alpha=0.35)

        for row in range(3):
            for col in range(5):
                bx = cx - s * 0.2 + col * s * 0.1
                by = cy + s * 0.05 - row * s * 0.03
                _etch_line(ax, bx, by, bx + s * 0.01, by, color=STONE_DARK, passes=1, lw=0.1, alpha=0.25)
                _etch_line(ax, bx + s * 0.01, by, bx + s * 0.01, by - s * 0.02,
                           color=STONE_DARK, passes=1, lw=0.1, alpha=0.25)

    @staticmethod
    def spiral_tower(ax, cx, cy, s):
        n_turns = 4
        n_pts = 100
        for layer in range(8):
            t = layer / 7
            base_r = s * (0.05 + t * 0.2)
            tower_h = s * (0.4 - t * 0.15)
            theta = np.linspace(0, n_turns * 2 * np.pi, n_pts)
            r = base_r + theta / (n_turns * 2 * np.pi) * s * 0.05

            for pass_i in range(3):
                off = (pass_i - 1) * 0.002
                x_spiral = cx + r * np.cos(theta + layer * 0.5) + off
                y_spiral = cy + theta / (n_turns * 2 * np.pi) * tower_h * 0.5 + off * 0.5
                ax.plot(x_spiral, y_spiral, color=STONE, linewidth=0.18,
                        alpha=0.5 - abs(pass_i - 1) * 0.1)

        wall_h = s * 0.35
        wall_w = s * 0.12
        for side in [-1, 1]:
            wx = cx + side * s * 0.15
            _etch_poly(ax, [(wx - wall_w / 2, cy - s * 0.05),
                            (wx + wall_w / 2, cy - s * 0.05),
                            (wx + wall_w / 2 * 0.8, cy + wall_h),
                            (wx - wall_w / 2 * 0.8, cy + wall_h)],
                       facecolor=SHADOW, edgecolor=STONE, lw=0.3, alpha=0.4)
            _hatch_area(ax, wx - wall_w * 0.4, cy - s * 0.05,
                        wx + wall_w * 0.4, cy + wall_h, n=5, alpha=0.2)

        for i in range(12):
            angle = i * np.pi / 6
            r = s * 0.18
            bx = cx + r * np.cos(angle)
            by = cy + s * 0.15 + r * 0.3 * np.sin(angle)
            _etch_line(ax, bx, by, bx, by + s * 0.04,
                       color=STONE_DARK, passes=2, lw=0.15, alpha=0.3)

    @staticmethod
    def nested_arches(ax, cx, cy, s):
        n_levels = 6
        for i in range(n_levels):
            t = i / (n_levels - 1)
            shrink = 1 - t * 0.7
            arch_w = s * 0.5 * shrink
            arch_h = s * 0.4 * shrink
            alpha_val = 0.6 - t * 0.25
            lw_val = 0.35 - t * 0.03

            theta = np.linspace(0, np.pi, 40)
            x_out = cx + arch_w / 2 * np.cos(theta)
            y_out = cy + arch_h * np.sin(theta)

            pillar_w = arch_w * 0.12
            verts = list(zip(x_out, y_out))
            verts += [(cx + arch_w / 2, cy - arch_h * 0.3)]
            verts += [(cx + arch_w / 2 - pillar_w, cy - arch_h * 0.3)]
            verts += [(cx + arch_w / 2 - pillar_w, cy)]
            inner_theta = np.linspace(0, np.pi, 40)
            x_in = cx + (arch_w / 2 - pillar_w) * np.cos(inner_theta)
            y_in = cy + (arch_h - pillar_w) * np.sin(inner_theta)
            verts += list(zip(x_in[::-1], y_in[::-1]))
            verts += [(cx - arch_w / 2 + pillar_w, cy)]
            verts += [(cx - arch_w / 2 + pillar_w, cy - arch_h * 0.3)]
            verts += [(cx - arch_w / 2, cy - arch_h * 0.3)]

            _etch_poly(ax, verts, facecolor=DEEP_SHADOW if i % 2 == 0 else SHADOW,
                       edgecolor=STONE if i < n_levels // 2 else STONE_DARK,
                       lw=lw_val, alpha=alpha_val)

            for pass_i in range(2):
                off = (pass_i - 0.5) * 0.002 * (i + 1)
                ax.plot(x_out + off, y_out, color=STONE, linewidth=lw_val, alpha=alpha_val * 0.8)

            if i < n_levels - 1:
                for j in range(6):
                    jt = j / 5
                    rx = cx + (arch_w / 2 - pillar_w) * 0.5 * np.cos(jt * np.pi)
                    ry = cy + (arch_h - pillar_w) * 0.5 * np.sin(jt * np.pi)
                    _etch_line(ax, rx, ry, rx + s * 0.003, ry - s * 0.005,
                               color=STONE_DARK, passes=1, lw=0.1, alpha=0.25)


class SPQRForum:
    @staticmethod
    def temple(ax, cx, cy, s):
        base_w = s * 0.5
        base_h = s * 0.04
        temple_h = s * 0.35
        pediment_h = s * 0.1

        _etch_poly(ax, [(cx - base_w / 2, cy), (cx + base_w / 2, cy),
                        (cx + base_w / 2, cy + base_h), (cx - base_w / 2, cy + base_h)],
                   facecolor=STONE_DARK, edgecolor=STONE, lw=0.4, alpha=0.55)
        for i in range(3):
            _etch_line(ax, cx - base_w / 2, cy + base_h * (i + 1) / 3,
                       cx + base_w / 2, cy + base_h * (i + 1) / 3,
                       color=STONE, passes=1, lw=0.15, alpha=0.3)

        n_cols = 6
        col_h = temple_h * 0.6
        for i in range(n_cols):
            col_x = cx - base_w * 0.4 + i * base_w * 0.8 / (n_cols - 1)
            RomanOrders.corinthian_column(ax, col_x, cy + base_h, col_h, s * 0.6)

        entab_w = base_w * 0.95
        entab_h = s * 0.03
        _etch_poly(ax, [(cx - entab_w / 2, cy + base_h + col_h),
                        (cx + entab_w / 2, cy + base_h + col_h),
                        (cx + entab_w / 2, cy + base_h + col_h + entab_h),
                        (cx - entab_w / 2, cy + base_h + col_h + entab_h)],
                   facecolor=STONE, edgecolor=STONE_LIGHT, lw=0.35, alpha=0.55)

        ped_top_y = cy + base_h + col_h + entab_h + pediment_h
        pediment = [(cx - entab_w / 2, cy + base_h + col_h + entab_h),
                    (cx, ped_top_y),
                    (cx + entab_w / 2, cy + base_h + col_h + entab_h)]
        _etch_poly(ax, pediment, facecolor=SHADOW, edgecolor=STONE, lw=0.4, alpha=0.55)

        for i in range(8):
            t = i / 7
            tx = cx - entab_w * 0.35 + t * entab_w * 0.7
            ty = cy + base_h + col_h + entab_h + t * pediment_h * 0.3
            _etch_line(ax, tx, ty, tx, ty + s * 0.005,
                       color=STONE_DARK, passes=1, lw=0.1, alpha=0.3)

        step_w = base_w * 1.1
        for i in range(4):
            sw = step_w + i * s * 0.02
            sh = s * 0.01
            _etch_poly(ax, [(cx - sw / 2, cy - i * sh), (cx + sw / 2, cy - i * sh),
                            (cx + sw / 2, cy - (i + 1) * sh), (cx - sw / 2, cy - (i + 1) * sh)],
                       facecolor=STONE_DARK if i % 2 else SHADOW, edgecolor=STONE, lw=0.2, alpha=0.45)

    @staticmethod
    def colosseum_wall(ax, cx, cy, s, n_levels=4):
        for level in range(n_levels):
            t = level / (n_levels - 1)
            y = cy + level * s * 0.08
            level_w = s * (0.45 - t * 0.05)
            level_h = s * 0.07
            _etch_poly(ax, [(cx - level_w / 2, y), (cx + level_w / 2, y),
                            (cx + level_w / 2, y + level_h), (cx - level_w / 2, y + level_h)],
                       facecolor=SHADOW if level % 2 == 0 else DEEP_SHADOW,
                       edgecolor=STONE, lw=0.3, alpha=0.5 - t * 0.1)

            n_openings = 8 - level
            opening_w = level_w / n_openings * 0.6
            for i in range(n_openings):
                ox = cx - level_w * 0.4 + i * level_w * 0.8 / (n_openings - 1) if n_openings > 1 else cx
                if level < n_levels - 1:
                    RomanArch.semicircular_arch(ax, ox, y + level_h * 0.5,
                                                opening_w, level_h * 0.8, s * 0.3)
                else:
                    _etch_poly(ax, [(ox - opening_w / 2, y), (ox + opening_w / 2, y),
                                    (ox + opening_w / 2, y + level_h),
                                    (ox - opening_w / 2, y + level_h)],
                               facecolor=DEEP_SHADOW, edgecolor=STONE_DARK, lw=0.2, alpha=0.4)

            if level < n_levels - 1:
                corb_h = s * 0.01
                _etch_poly(ax, [(cx - level_w / 2, y + level_h),
                                (cx + level_w / 2, y + level_h),
                                (cx + level_w / 2, y + level_h + corb_h),
                                (cx - level_w / 2, y + level_h + corb_h)],
                           facecolor=STONE, edgecolor=STONE_LIGHT, lw=0.25, alpha=0.5)

    @staticmethod
    def pantheon_dome(ax, cx, cy, s):
        dome_r = s * 0.28
        theta = np.linspace(0, np.pi, 60)
        x_dome = cx + dome_r * np.cos(theta)
        y_dome = cy + dome_r * np.sin(theta) * 0.7

        for pass_i in range(3):
            off = (pass_i - 1) * 0.002
            ax.plot(x_dome + off, y_dome, color=STONE, linewidth=0.3, alpha=0.6 - abs(pass_i - 1) * 0.1)

        base_w = dome_r * 2.2
        _etch_poly(ax, [(cx - base_w / 2, cy), (cx + base_w / 2, cy),
                        (cx + base_w / 2, cy + s * 0.08), (cx - base_w / 2, cy + s * 0.08)],
                   facecolor=SHADOW, edgecolor=STONE, lw=0.35, alpha=0.5)
        for i in range(8):
            _etch_line(ax, cx - base_w / 2, cy + s * 0.01 * (i + 1),
                       cx + base_w / 2, cy + s * 0.01 * (i + 1),
                       color=STONE_DARK, passes=1, lw=0.12, alpha=0.25)

        n_cols = 8
        for i in range(n_cols):
            col_x = cx - base_w * 0.4 + i * base_w * 0.8 / (n_cols - 1)
            RomanOrders.ionic_column(ax, col_x, cy + s * 0.08, s * 0.18, s * 0.4)

        oculus_r = dome_r * 0.18
        oculus_x = cx + dome_r * 0.1
        oculus_y = cy + dome_r * 0.55
        for pass_i in range(4):
            off = pass_i * 0.001
            circle = plt.Circle((oculus_x + off, oculus_y + off), oculus_r + off,
                                facecolor="none", edgecolor=GOLD, linewidth=0.3,
                                alpha=0.6 - pass_i * 0.1)
            ax.add_patch(circle)
        _etch_poly(ax, [(oculus_x - oculus_r * 0.3, oculus_y - oculus_r),
                        (oculus_x + oculus_r * 0.3, oculus_y - oculus_r),
                        (oculus_x + oculus_r * 0.1, oculus_y + oculus_r * 0.5),
                        (oculus_x - oculus_r * 0.1, oculus_y + oculus_r * 0.5)],
                   facecolor=GOLD, edgecolor="none", alpha=0.1)

        for ring in range(3):
            r = dome_r * (0.3 + ring * 0.2)
            ring_theta = np.linspace(0.2, np.pi - 0.2, 40)
            ax.plot(cx + r * np.cos(ring_theta), cy + r * np.sin(ring_theta) * 0.7,
                    color=STONE_DARK, linewidth=0.15, alpha=0.3)

        for ray in range(12):
            angle = ray * np.pi / 6
            ax.plot([oculus_x, cx + dome_r * 0.95 * np.cos(angle)],
                    [oculus_y, cy + dome_r * 0.65 * np.sin(angle)],
                    color=STONE_DARK, linewidth=0.1, alpha=0.2)

    @staticmethod
    def forum_pillars(ax, cx, cy, s, n):
        total_w = s * 0.6
        spacing = total_w / max(n - 1, 1)
        pillar_h = s * 0.25
        pillar_w = s * 0.03

        for i in range(n):
            px = cx - total_w / 2 + i * spacing
            _etch_poly(ax, [(px - pillar_w, cy), (px + pillar_w, cy),
                            (px + pillar_w * 0.8, cy + pillar_h),
                            (px - pillar_w * 0.8, cy + pillar_h)],
                       facecolor=SHADOW, edgecolor=STONE, lw=0.25, alpha=0.5)
            _hatch_area(ax, px - pillar_w * 0.7, cy, px + pillar_w * 0.7, cy + pillar_h,
                        n=3, alpha=0.2)

            cap_w = pillar_w * 2.5
            _etch_poly(ax, [(px - cap_w / 2, cy + pillar_h),
                            (px + cap_w / 2, cy + pillar_h),
                            (px + cap_w / 2, cy + pillar_h + s * 0.015),
                            (px - cap_w / 2, cy + pillar_h + s * 0.015)],
                       facecolor=STONE, edgecolor=STONE_LIGHT, lw=0.2, alpha=0.5)

        if n > 1:
            _etch_poly(ax, [(cx - total_w / 2 - s * 0.04, cy + pillar_h + s * 0.015),
                            (cx + total_w / 2 + s * 0.04, cy + pillar_h + s * 0.015),
                            (cx + total_w / 2 + s * 0.04, cy + pillar_h + s * 0.025),
                            (cx - total_w / 2 - s * 0.04, cy + pillar_h + s * 0.025)],
                       facecolor=STONE_DARK, edgecolor=STONE, lw=0.25, alpha=0.5)

        base_y = cy - s * 0.01
        _etch_poly(ax, [(cx - total_w / 2 - s * 0.05, base_y),
                        (cx + total_w / 2 + s * 0.05, base_y),
                        (cx + total_w / 2 + s * 0.05, base_y - s * 0.015),
                        (cx - total_w / 2 - s * 0.05, base_y - s * 0.015)],
                   facecolor=STONE_DARK, edgecolor=STONE, lw=0.25, alpha=0.45)


class SPQRComposition:
    @staticmethod
    def piranesi_prison(ax, s):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        for i in range(20):
            _etch_line(ax, 0.05 + i * 0.045, 0.05, 0.05 + i * 0.045, 0.95,
                       color=STONE_DARK, passes=1, spread=0.002, lw=0.1, alpha=0.15)
            _etch_line(ax, 0.05, 0.05 + i * 0.045, 0.95, 0.05 + i * 0.045,
                       color=STONE_DARK, passes=1, spread=0.002, lw=0.1, alpha=0.15)

        for layer in range(4):
            t = layer / 3
            shrink = 1 - t * 0.4
            x0 = 0.1 + t * 0.15
            y0 = 0.1 + t * 0.1
            w = 0.8 * shrink
            h = 0.8 * shrink

            _etch_poly(ax, [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)],
                       facecolor="none", edgecolor=STONE, lw=0.25, alpha=0.35 - t * 0.05)

        PiranesiArchitecture.infinite_staircase(ax, 0.3, 0.25, s * 0.9)
        PiranesiArchitecture.infinite_staircase(ax, 0.7, 0.55, s * 0.7)
        PiranesiArchitecture.nested_arches(ax, 0.5, 0.5, s * 0.8)

        for i in range(3):
            PiranesiArchitecture.impossible_corridor(ax, 0.5, 0.65 + i * 0.12, s * 0.6)

        for i in range(5):
            chain_x = 0.15 + i * 0.17
            chain_len = 0.15 + np.random.random() * 0.1
            pts = []
            for j in range(15):
                t = j / 14
                pts.append((chain_x + np.sin(t * 4) * 0.01, 0.85 - t * chain_len))
            for pass_i in range(2):
                off = (pass_i - 0.5) * 0.001
                xs = [p[0] + off for p in pts]
                ys = [p[1] for p in pts]
                ax.plot(xs, ys, color=STONE_DARK, linewidth=0.4, alpha=0.5)
            ax.plot(pts[-1][0], pts[-1][1], "o", color=STONE_DARK, markersize=3, alpha=0.4)

        RomanArch.semicircular_arch(ax, 0.15, 0.4, 0.2, 0.25, s * 0.4)
        RomanArch.semicircular_arch(ax, 0.85, 0.35, 0.18, 0.22, s * 0.35)
        RomanArch.pointed_arch(ax, 0.5, 0.3, 0.15, 0.2, s * 0.3)

        for i in range(15):
            dx = np.random.random() * 0.8 + 0.1
            dy = np.random.random() * 0.7 + 0.15
            length = np.random.random() * 0.08 + 0.02
            angle = np.random.random() * np.pi
            _etch_line(ax, dx, dy, dx + length * np.cos(angle), dy + length * np.sin(angle),
                       color=STONE_DARK, passes=1, lw=0.1, alpha=0.2)

        PiranesiArchitecture.spiral_tower(ax, 0.75, 0.7, s * 0.5)

        ax.text(0.5, 0.05, "CARCERI D'INVENZIONE", fontsize=s * 0.04, color=STONE,
                ha="center", va="center", alpha=0.5, fontfamily="serif",
                fontstyle="italic")

    @staticmethod
    def roman_city(ax, s):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        horizon_y = 0.35
        for i in range(15):
            _etch_line(ax, 0, horizon_y + i * 0.001, 1, horizon_y + i * 0.001,
                       color=STONE_DARK, passes=1, spread=0.003, lw=0.1, alpha=0.12)

        sky_pts_x = np.linspace(0, 1, 50)
        sky_pts_y = horizon_y + np.sin(sky_pts_x * 3) * 0.02 + np.sin(sky_pts_x * 7) * 0.01
        ax.fill_between(sky_pts_x, sky_pts_y, 1, color=SHADOW, alpha=0.2)

        SPQRForum.aqueduct_segment = RomanArch.aqueduct_segment
        RomanArch.aqueduct_segment(ax, 0.35, 0.65, 0.4, 0.18, 5, s * 0.5)

        SPQRForum.temple(ax, 0.15, 0.4, s * 0.7)

        SPQRForum.pantheon_dome(ax, 0.65, 0.5, s * 0.7)

        SPQRForum.colosseum_wall(ax, 0.85, 0.35, s * 0.8, n_levels=4)

        SPQRForum.forum_pillars(ax, 0.5, 0.25, s * 0.6, 7)

        ground_verts = [(0, 0), (1, 0), (1, 0.2), (0, 0.2)]
        _etch_poly(ax, ground_verts, facecolor=DEEP_SHADOW, edgecolor="none", alpha=0.3)

        for i in range(30):
            gx = np.random.random() * 0.9 + 0.05
            gy = np.random.random() * 0.18 + 0.02
            gw = np.random.random() * 0.04 + 0.01
            _etch_line(ax, gx - gw / 2, gy, gx + gw / 2, gy,
                       color=STONE_DARK, passes=1, lw=0.15, alpha=0.2)

        for i in range(8):
            fx = np.random.random() * 0.9 + 0.05
            fy = np.random.random() * 0.15 + 0.05
            fh = np.random.random() * 0.1 + 0.05
            _etch_line(ax, fx, fy, fx, fy + fh,
                       color=STONE_DARK, passes=1, lw=0.08, alpha=0.15)
            _etch_line(ax, fx, fy + fh * 0.7, fx + fh * 0.15, fy + fh * 0.9,
                       color=STONE_DARK, passes=1, lw=0.06, alpha=0.12)

        ax.text(0.5, 0.97, "ROMA AETERNA", fontsize=s * 0.05, color=GOLD,
                ha="center", va="top", alpha=0.6, fontfamily="serif",
                fontweight="bold")

    @staticmethod
    def spqr_glory(ax, s):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        for ring in range(5):
            r = 0.15 + ring * 0.06
            for pass_i in range(3):
                off = (pass_i - 1) * 0.002
                theta = np.linspace(0, 2 * np.pi, 80)
                ax.plot(0.5 + (r + off) * np.cos(theta), 0.5 + (r + off) * np.sin(theta),
                        color=STONE, linewidth=0.15, alpha=0.3 - ring * 0.04)

        n_pts_wreath = 60
        theta_wreath = np.linspace(0, 2 * np.pi, n_pts_wreath, endpoint=False)
        for i in range(n_pts_wreath):
            t = theta_wreath[i]
            wx = 0.5 + 0.2 * np.cos(t)
            wy = 0.5 + 0.2 * np.sin(t)
            leaf_angle = t + np.pi / 2
            for pass_i in range(2):
                off = (pass_i - 0.5) * 0.001
                lx1 = wx + 0.015 * np.cos(leaf_angle + 0.3)
                ly1 = wy + 0.015 * np.sin(leaf_angle + 0.3)
                lx2 = wx - 0.015 * np.cos(leaf_angle - 0.3)
                ly2 = wy - 0.015 * np.sin(leaf_angle - 0.3)
                _etch_line(ax, wx + off, wy + off, lx1, ly1,
                           color=STONE, passes=1, lw=0.2, alpha=0.55)
                _etch_line(ax, wx + off, wy + off, lx2, ly2,
                           color=STONE, passes=1, lw=0.2, alpha=0.55)
                _etch_line(ax, lx1, ly1, lx2, ly2,
                           color=STONE_DARK, passes=1, lw=0.15, alpha=0.4)

        for text_pass in range(3):
            off = (text_pass - 1) * 0.001
            ax.text(0.5 + off, 0.5 + off * 0.5, "SPQR", fontsize=s * 0.2,
                    color=GOLD, ha="center", va="center", alpha=0.75 - text_pass * 0.1,
                    fontweight="bold", fontfamily="serif")
        ax.text(0.5, 0.36, "SENATUS POPULUSQUE ROMANUS", fontsize=s * 0.03,
                color=STONE, ha="center", va="center", alpha=0.5, fontfamily="serif")

        eagle_y = 0.65
        body_verts = [(0.5, eagle_y), (0.5 - 0.03, eagle_y - 0.04),
                      (0.5 + 0.03, eagle_y - 0.04)]
        _etch_poly(ax, body_verts, facecolor=SHADOW, edgecolor=GOLD, lw=0.3, alpha=0.55)
        _etch_line(ax, 0.5, eagle_y + 0.01, 0.5, eagle_y - 0.03,
                   color=GOLD, passes=2, lw=0.2, alpha=0.5)

        for side in [-1, 1]:
            wing_pts = []
            for i in range(15):
                t = i / 14
                wx = 0.5 + side * (0.03 + t * 0.12)
                wy = eagle_y - 0.01 + t * 0.06 + np.sin(t * np.pi) * 0.02
                wing_pts.append((wx, wy))
            for pass_i in range(2):
                off = (pass_i - 0.5) * 0.001
                xs = [p[0] + off for p in wing_pts]
                ys = [p[1] for p in wing_pts]
                ax.plot(xs, ys, color=GOLD, linewidth=0.3, alpha=0.55 - pass_i * 0.05)
            for i in range(5):
                t = i / 4
                feather_x = 0.5 + side * (0.05 + t * 0.1)
                feather_y = eagle_y + t * 0.04
                _etch_line(ax, feather_x, feather_y, feather_x + side * 0.02, feather_y + 0.015,
                           color=GOLD, passes=1, lw=0.15, alpha=0.45)

        head_x, head_y = 0.5, eagle_y + 0.015
        head_circle = plt.Circle((head_x, head_y), 0.01, facecolor=SHADOW,
                                 edgecolor=GOLD, linewidth=0.25, alpha=0.55)
        ax.add_patch(head_circle)
        _etch_line(ax, head_x, head_y, head_x + 0.015, head_y + 0.005,
                   color=GOLD, passes=2, lw=0.2, alpha=0.5)

        for i in range(6):
            tx = 0.25 + i * 0.1
            ty = 0.18
            RomanOrders.doric_column(ax, tx, ty, 0.2, s * 0.35)

        arch_positions = [(0.15, 0.28), (0.45, 0.28), (0.75, 0.28)]
        for ax_pos, ay_pos in arch_positions:
            RomanArch.semicircular_arch(ax, ax_pos, ay_pos, 0.22, 0.12, s * 0.3)

        for corner_x, corner_y in [(0.08, 0.85), (0.92, 0.85), (0.08, 0.15), (0.92, 0.15)]:
            for pass_i in range(3):
                off = (pass_i - 1) * 0.002
                theta = np.linspace(0, np.pi * 2, 60)
                r = 0.04
                ax.plot(corner_x + r * np.cos(theta) + off,
                        corner_y + r * np.sin(theta) + off,
                        color=STONE, linewidth=0.2, alpha=0.3)
            inner_theta = np.linspace(0, np.pi * 2, 60)
            ix = corner_x + 0.025 * np.cos(inner_theta)
            iy = corner_y + 0.025 * np.sin(inner_theta)
            for i in range(8):
                t = i / 7
                angle = t * 2 * np.pi
                _etch_line(ax, corner_x + 0.015 * np.cos(angle), corner_y + 0.015 * np.sin(angle),
                           corner_x + 0.04 * np.cos(angle), corner_y + 0.04 * np.sin(angle),
                           color=STONE_DARK, passes=1, lw=0.15, alpha=0.3)

        corner_labels = ["X", "I", "V", "I"]
        for i, (cx, cy) in enumerate([(0.08, 0.85), (0.92, 0.85), (0.08, 0.15), (0.92, 0.15)]):
            ax.text(cx, cy, corner_labels[i], fontsize=s * 0.025, color=STONE,
                    ha="center", va="center", alpha=0.4, fontfamily="serif")


if __name__ == "__main__":
    print("=== PolyArt SPQR Module ===")
    print("Initializing Piranesi-style Roman architecture...")

    fig, axes = plt.subplots(2, 2, figsize=(20, 20), dpi=150)
    fig.patch.set_facecolor(DARK_BG)

    for row in axes:
        for ax in row:
            ax.set_facecolor(DARK_BG)
            ax.set_aspect("equal")
            ax.axis("off")

    print("Panel 1: Piranesi Prison (stairs, arches, chains, impossible geometry)...")
    SPQRComposition.piranesi_prison(axes[0, 0], s=1.0)

    print("Panel 2: Roman City (forum, temple, aqueduct, colosseum wall)...")
    SPQRComposition.roman_city(axes[0, 1], s=1.0)

    print("Panel 3: SPQR Glory (eagle, text, laurel, architectural frame)...")
    SPQRComposition.spqr_glory(axes[1, 0], s=1.0)

    print("Panel 4: Column Gallery (Doric, Ionic, Corinthian columns)...")
    ax_gallery = axes[1, 1]
    ax_gallery.set_xlim(0, 1)
    ax_gallery.set_ylim(0, 1)

    col_h = 0.55
    col_y = 0.15
    RomanOrders.doric_column(ax_gallery, 0.2, col_y, col_h, 0.8)
    ax_gallery.text(0.2, col_y - 0.04, "DORIC", fontsize=0.035, color=STONE,
                    ha="center", va="top", alpha=0.6, fontfamily="serif")

    RomanOrders.ionic_column(ax_gallery, 0.5, col_y, col_h, 0.8)
    ax_gallery.text(0.5, col_y - 0.04, "IONIC", fontsize=0.035, color=STONE,
                    ha="center", va="top", alpha=0.6, fontfamily="serif")

    RomanOrders.corinthian_column(ax_gallery, 0.8, col_y, col_h, 0.8)
    ax_gallery.text(0.8, col_y - 0.04, "CORINTHIAN", fontsize=0.035, color=STONE,
                    ha="center", va="top", alpha=0.6, fontfamily="serif")

    ax_gallery.text(0.5, 0.95, "ORDERS OF ARCHITECTURE", fontsize=0.04, color=GOLD,
                    ha="center", va="top", alpha=0.6, fontfamily="serif", fontweight="bold")

    for i in range(10):
        _etch_line(ax_gallery, 0.05 + i * 0.095, 0.12, 0.05 + i * 0.095, 0.9,
                   color=STONE_DARK, passes=1, lw=0.08, alpha=0.12)
        _etch_line(ax_gallery, 0.05, 0.12 + i * 0.088, 0.95, 0.12 + i * 0.088,
                   color=STONE_DARK, passes=1, lw=0.08, alpha=0.12)

    output_path = "spqr_piranesi_showcase.png"
    print("Saving to: " + output_path + " ...")
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor=DARK_BG, edgecolor="none", pad_inches=0.3)
    plt.close(fig)

    print("Done! 4 panels rendered successfully.")
    print("File: spqr_piranesi_showcase.png")
