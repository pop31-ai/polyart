"""Pompeii-style polynomial art module.

Pure Python + numpy + matplotlib.
Generates PNG images inspired by Pompeian wall paintings,
architecture, daily life, mythology, and decorations.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Polygon, Ellipse, Arc
from matplotlib.collections import LineCollection
from matplotlib.path import Path


# ---------------------------------------------------------------------------
# Colour palettes
# ---------------------------------------------------------------------------

POMPEIAN_RED = "#8B0000"
POMPEIAN_DARK_RED = "#5C0000"
POMPEIAN_OCHRE = "#C8A050"
POMPEIAN_GOLD = "#D4A843"
POMPEIAN_BLACK = "#1A1A1A"
POMPEIAN_WHITE = "#F5F0E8"
POMPEIAN_CREAM = "#EDE4D3"
POMPEIAN_BLUE = "#2E4A62"
POMPEIAN_GREEN = "#3A5F3A"
POMPEIAN_TERRACOTTA = "#C2703A"
POMPEIAN_BROWN = "#6B4226"
POMPEIAN_SAND = "#C8B89A"
VESUVIUS_DARK = "#2C2C2C"
ASH_GREY = "#5A5A5A"
SKY_DARK = "#1C1428"

BG_DARK = "#0E0E0E"

SCHEMES = {
    "red": {"primary": POMPEIAN_RED, "secondary": POMPEIAN_OCHRE, "accent": POMPEIAN_GOLD, "bg": POMPEIAN_DARK_RED},
    "black": {"primary": POMPEIAN_BLACK, "secondary": POMPEIAN_RED, "accent": POMPEIAN_OCHRE, "bg": "#0A0A0A"},
    "white": {"primary": POMPEIAN_CREAM, "secondary": POMPEIAN_BLUE, "accent": POMPEIAN_RED, "bg": "#F0EAD6"},
    "blue": {"primary": POMPEIAN_BLUE, "secondary": POMPEIAN_GOLD, "accent": POMPEIAN_CREAM, "bg": "#162030"},
    "garden": {"primary": POMPEIAN_GREEN, "secondary": POMPEIAN_OCHRE, "accent": POMPEIAN_RED, "bg": "#0C1A0C"},
}


def _polyval(xs, coeffs):
    """Evaluate polynomial coefficients (numpy poly1d style)."""
    return np.polyval(coeffs, xs)


def _fig(facecolor=BG_DARK):
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.set_facecolor(facecolor)
    ax.set_facecolor(facecolor)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


# ======================================================================
# 1. PompeiiFrescoStyle
# ======================================================================

class PompeiiFrescoStyle:

    def pompeii_border(self, ax, width, height, color_scheme="red"):
        """Pompeii-style decorative border with meander / wave patterns."""
        sc = SCHEMES.get(color_scheme, SCHEMES["red"])
        c = sc["primary"]
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)

        for side in ["bottom", "top"]:
            y = 0 if side == "bottom" else height
            xs = np.linspace(0, width, 600)
            step = width / 30
            meander_y = np.zeros_like(xs)
            for i in range(30):
                x0 = i * step
                x1 = x0 + step
                mask = (xs >= x0) & (xs < x1)
                local = (xs[mask] - x0) / step
                pattern = np.where(
                    local < 0.25, 0,
                    np.where(local < 0.5, 1,
                    np.where(local < 0.75, 1, 0))
                )
                meander_y[mask] = pattern
            offset = 0.03 * height if side == "bottom" else -0.03 * height
            ax.plot(xs, meander_y * 0.02 * height + y + offset,
                    color=c, lw=0.2, alpha=0.5)

        for side in ["left", "right"]:
            x = 0 if side == "left" else width
            ys = np.linspace(0, height, 600)
            step = height / 30
            meander_x = np.zeros_like(ys)
            for i in range(30):
                y0 = i * step
                y1 = y0 + step
                mask = (ys >= y0) & (ys < y1)
                local = (ys[mask] - y0) / step
                pattern = np.where(
                    local < 0.25, 0,
                    np.where(local < 0.5, 1,
                    np.where(local < 0.75, 1, 0))
                )
                meander_x[mask] = pattern
            offset = 0.03 * width if side == "left" else -0.03 * width
            ax.plot(meander_x * 0.02 * width + x + offset, ys,
                    color=c, lw=0.2, alpha=0.5)

        # inner frame
        inset = 0.04
        rect = mpatches.FancyBboxPatch(
            (width * inset, height * inset),
            width * (1 - 2 * inset), height * (1 - 2 * inset),
            boxstyle="round,pad=0.01", linewidth=0.3,
            edgecolor=sc["secondary"], facecolor="none", alpha=0.4)
        ax.add_patch(rect)

    def pompeii_panel(self, ax, x, y, w, h, scene_type="garden"):
        """Framed fresco panel."""
        border_color = POMPEIAN_RED
        rect = mpatches.Rectangle((x, y), w, h, linewidth=0.3,
                                  edgecolor=border_color, facecolor="#0A0A0A",
                                  alpha=0.85)
        ax.add_patch(rect)
        inner = mpatches.Rectangle((x + w * 0.04, y + h * 0.04),
                                   w * 0.92, h * 0.92, linewidth=0.15,
                                   edgecolor=POMPEIAN_OCHRE, facecolor="none",
                                   alpha=0.4)
        ax.add_patch(inner)

        if scene_type == "garden":
            self.garden_scene(ax, x + w * 0.06, y + h * 0.06, w * 0.88, h * 0.88)
        elif scene_type == "still_life":
            self.still_life(ax, x + w * 0.06, y + h * 0.06, w * 0.88, h * 0.88)
        elif scene_type == "mythological":
            self.mythological_panel(ax, x + w * 0.06, y + h * 0.06, w * 0.88, h * 0.88)
        elif scene_type == "architectural":
            self.architectural_illusion(ax, x + w * 0.06, y + h * 0.06, w * 0.88, h * 0.88)

    def garden_scene(self, ax, x, y, w, h):
        """Pompeii garden fresco with fountain, birds, flowers, trees."""
        # ground
        xs = np.linspace(x, x + w, 200)
        ground = y + h * 0.15 + 0.02 * h * np.sin(xs * 8 / w)
        ax.fill_between(xs, y, ground, color=POMPEIAN_GREEN, alpha=0.25)
        ax.plot(xs, ground, color=POMPEIAN_GREEN, lw=0.2, alpha=0.4)

        # fountain basin
        fx, fy = x + w * 0.5, y + h * 0.25
        bw = w * 0.18
        t = np.linspace(-1, 1, 100)
        basin_x = fx + bw * t
        basin_y = fy + 0.04 * h * np.sqrt(np.clip(1 - t ** 2, 0, 1))
        ax.fill_between(basin_x, fy - 0.01 * h, basin_y, color=POMPEIAN_SAND, alpha=0.35)
        ax.plot(basin_x, basin_y, color=POMPEIAN_SAND, lw=0.2, alpha=0.5)
        # water jet
        jet_x = np.array([fx, fx + 0.01 * w, fx - 0.01 * w, fx])
        jet_y = np.array([fy + 0.04 * h, fy + 0.18 * h, fy + 0.18 * h, fy + 0.04 * h])
        ax.fill(jet_x, jet_y, color=POMPEIAN_BLUE, alpha=0.25)

        # cypress trees
        for tx, flip in [(x + w * 0.15, 1), (x + w * 0.85, -1)]:
            ty = y + h * 0.15
            tree_xs = np.linspace(tx - 0.02 * w, tx + 0.02 * w, 60)
            tree_h = h * 0.55
            tree_y = ty + tree_h * np.exp(-((tree_xs - tx) ** 2) / (0.003 * w ** 2))
            ax.fill_between(tree_xs, ty, tree_y, color=POMPEIAN_GREEN, alpha=0.3)
            ax.plot(tree_xs, tree_y, color="#1A3A1A", lw=0.2, alpha=0.5)

        # flowers
        np.random.seed(42)
        for _ in range(12):
            fx_ = x + np.random.rand() * w
            fy_ = y + h * 0.1 + np.random.rand() * h * 0.15
            petal_r = 0.008 * w
            theta = np.linspace(0, 2 * np.pi, 40)
            ax.plot(fx_ + petal_r * np.cos(theta),
                    fy_ + petal_r * np.sin(theta),
                    color=np.random.choice([POMPEIAN_RED, POMPEIAN_OCHRE, POMPEIAN_WHITE]),
                    lw=0.15, alpha=0.4)

        # birds
        for bx, by in [(x + w * 0.3, y + h * 0.7), (x + w * 0.65, y + h * 0.8)]:
            t_b = np.linspace(0, 1, 40)
            wing_l_x = bx - 0.04 * w * t_b
            wing_l_y = by + 0.02 * h * np.sin(np.pi * t_b)
            wing_r_x = bx + 0.04 * w * t_b
            wing_r_y = by + 0.02 * h * np.sin(np.pi * t_b)
            ax.plot(wing_l_x, wing_l_y, color=POMPEIAN_BLACK, lw=0.2, alpha=0.45)
            ax.plot(wing_r_x, wing_r_y, color=POMPEIAN_BLACK, lw=0.2, alpha=0.45)

    def still_life(self, ax, x, y, w, h):
        """Pompeian still life: fruit, vessels, bread."""
        # table surface
        txs = np.linspace(x, x + w, 100)
        ty = y + h * 0.3
        ax.fill_between(txs, y, ty, color=POMPEIAN_BROWN, alpha=0.2)
        ax.plot(txs, np.full_like(txs, ty), color=POMPEIAN_BROWN, lw=0.3, alpha=0.4)

        # vase
        vx = x + w * 0.35
        vt = np.linspace(0, 1, 120)
        vase_r = 0.04 * w * (1 + 1.5 * np.sin(np.pi * vt) + 0.3 * np.sin(2 * np.pi * vt))
        vase_x = np.concatenate([vx + vase_r, (vx - vase_r)[::-1]])
        vase_y = np.concatenate([ty + 0.25 * h * vt, (ty + 0.25 * h * vt)[::-1]])
        ax.fill(vase_x, vase_y, color=POMPEIAN_TERRACOTTA, alpha=0.35)
        ax.plot(vase_x, vase_y, color=POMPEIAN_BROWN, lw=0.25, alpha=0.5)

        # fruit (circles with polynomial deformation)
        for i, (fx_, fy_) in enumerate([(x + w * 0.55, ty + 0.06 * h),
                                        (x + w * 0.62, ty + 0.08 * h),
                                        (x + w * 0.58, ty + 0.12 * h)]):
            r = 0.025 * w
            theta = np.linspace(0, 2 * np.pi, 80)
            deform = 1 + 0.1 * np.sin(3 * theta + i)
            ax.fill(fx_ + r * deform * np.cos(theta),
                    fy_ + r * deform * np.sin(theta),
                    color=np.random.choice([POMPEIAN_OCHRE, POMPEIAN_RED, POMPEIAN_GREEN]),
                    alpha=0.35)

        # bread loaf
        bx = x + w * 0.72
        bt = np.linspace(0, 1, 80)
        bread_y = ty + 0.04 * h * np.sin(np.pi * bt)
        bread_x = bx + 0.06 * w * (bt - 0.5)
        ax.fill_between(bread_x, ty, ty + bread_y, color=POMPEIAN_OCHRE, alpha=0.3)
        ax.plot(bread_x, ty + bread_y, color=POMPEIAN_BROWN, lw=0.2, alpha=0.45)

    def mythological_panel(self, ax, x, y, w, h):
        """Simple mythological figure composition."""
        # central figure (simple polynomial silhouette)
        cx = x + w * 0.5
        cy = y + h * 0.35
        # body
        t = np.linspace(-1, 1, 200)
        body_x = cx + 0.06 * w * t
        body_y_top = cy + 0.2 * h * (1 - t ** 2)
        body_y_bot = cy - 0.15 * h * (1 - t ** 2)
        ax.fill_between(body_x, body_y_bot, body_y_top, color=POMPEIAN_CREAM, alpha=0.2)
        # head
        head_theta = np.linspace(0, 2 * np.pi, 60)
        ax.fill(cx + 0.025 * w * np.cos(head_theta),
                cy + 0.24 * h + 0.025 * w * np.sin(head_theta),
                color=POMPEIAN_CREAM, alpha=0.2)
        # arms
        arm_t = np.linspace(0, 1, 50)
        ax.plot(cx - 0.02 * w - 0.06 * w * arm_t, cy + 0.12 * h + 0.06 * h * arm_t,
                color=POMPEIAN_CREAM, lw=0.3, alpha=0.25)
        ax.plot(cx + 0.02 * w + 0.06 * w * arm_t, cy + 0.12 * h + 0.04 * h * arm_t,
                color=POMPEIAN_CREAM, lw=0.3, alpha=0.25)

    def architectural_illusion(self, ax, x, y, w, h):
        """Fourth Style architectural perspective illusion."""
        cx = x + w * 0.5
        cy = y + h * 0.5
        # vanishing point lines
        for angle in np.linspace(0.3, 2.84, 12):
            ex = cx + 0.45 * w * np.cos(angle)
            ey = cy + 0.45 * h * np.sin(angle)
            ax.plot([cx, ex], [cy, ey], color=POMPEIAN_OCHRE, lw=0.15, alpha=0.3)

        # columns
        for col_x_ratio in [0.15, 0.3, 0.7, 0.85]:
            col_x = x + w * col_x_ratio
            col_bot = y + 0.1 * h
            col_top = y + 0.85 * h
            # column shaft
            ax.plot([col_x, col_x], [col_bot, col_top], color=POMPEIAN_CREAM, lw=0.3, alpha=0.35)
            # capital
            cap_w = 0.02 * w
            ax.plot([col_x - cap_w, col_x + cap_w], [col_top, col_top],
                    color=POMPEIAN_CREAM, lw=0.3, alpha=0.35)
            ax.plot([col_x - cap_w, col_x - cap_w], [col_top, col_top - 0.02 * h],
                    color=POMPEIAN_CREAM, lw=0.2, alpha=0.3)
            ax.plot([col_x + cap_w, col_x + cap_w], [col_top, col_top - 0.02 * h],
                    color=POMPEIAN_CREAM, lw=0.2, alpha=0.3)

        # arches between columns
        arch_t = np.linspace(0, np.pi, 80)
        for lx, rx in [(0.15, 0.3), (0.3, 0.7), (0.7, 0.85)]:
            mid = (lx + rx) / 2
            half = (rx - lx) / 2
            arch_x = x + w * mid + w * half * 0.9 * np.cos(arch_t)
            arch_y = y + 0.82 * h + 0.06 * h * np.sin(arch_t)
            ax.plot(arch_x, arch_y, color=POMPEIAN_OCHRE, lw=0.2, alpha=0.3)


# ======================================================================
# 2. PompeiiArchitecture
# ======================================================================

class PompeiiArchitecture:

    def roman_temple(self, ax, base_x, base_y, width, height):
        """Roman temple with columns, pediment, steps."""
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.05, 1.05)
        # podium steps
        for i in range(3):
            sw = width * (1 - i * 0.02)
            sh = height * 0.04
            sx = base_x + (width - sw) / 2
            sy = base_y + i * sh
            ax.add_patch(mpatches.Rectangle((sx, sy), sw, sh, linewidth=0.2,
                                            edgecolor=POMPEIAN_CREAM,
                                            facecolor=POMPEIAN_SAND, alpha=0.3))

        podium_top = base_y + 3 * height * 0.04

        # columns
        n_cols = 6
        col_h = height * 0.45
        for i in range(n_cols):
            cx = base_x + width * 0.1 + i * (width * 0.8) / (n_cols - 1)
            cw = width * 0.03
            ax.plot([cx, cx], [podium_top, podium_top + col_h],
                    color=POMPEIAN_CREAM, lw=0.35, alpha=0.45)
            # capital
            ax.plot([cx - cw, cx + cw], [podium_top + col_h, podium_top + col_h],
                    color=POMPEIAN_CREAM, lw=0.3, alpha=0.4)
            ax.plot([cx - cw, cx + cw], [podium_top + col_h - 0.01 * height,
                    podium_top + col_h - 0.01 * height],
                    color=POMPEIAN_CREAM, lw=0.2, alpha=0.35)

        # pediment (triangle)
        ped_base = podium_top + col_h
        ped_x = np.array([base_x + width * 0.08, base_x + width * 0.5,
                          base_x + width * 0.92, base_x + width * 0.08])
        ped_y = np.array([ped_base, ped_base + height * 0.15,
                          ped_base, ped_base])
        ax.fill(ped_x, ped_y, color=POMPEIAN_CREAM, alpha=0.15)
        ax.plot(ped_x, ped_y, color=POMPEIAN_CREAM, lw=0.3, alpha=0.45)

        # cella wall
        cella_x = base_x + width * 0.25
        cella_w = width * 0.5
        cella_h = height * 0.35
        ax.add_patch(mpatches.Rectangle((cella_x, podium_top), cella_w, cella_h,
                                        linewidth=0.2, edgecolor=POMPEIAN_CREAM,
                                        facecolor=POMPEIAN_SAND, alpha=0.15))

    def domus(self, ax, base_x, base_y, width, height):
        """Pompeian house cross-section."""
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        # foundation
        ax.add_patch(mpatches.Rectangle((base_x, base_y), width, height * 0.08,
                                        linewidth=0.2, edgecolor=POMPEIAN_BROWN,
                                        facecolor=POMPEIAN_SAND, alpha=0.3))

        # outer walls
        wall_h = height * 0.85
        wall_lx = base_x + width * 0.05
        wall_rx = base_x + width * 0.95
        wall_y = base_y + height * 0.08
        ax.plot([wall_lx, wall_lx], [wall_y, wall_y + wall_h],
                color=POMPEIAN_CREAM, lw=0.4, alpha=0.5)
        ax.plot([wall_rx, wall_rx], [wall_y, wall_y + wall_h],
                color=POMPEIAN_CREAM, lw=0.4, alpha=0.5)
        ax.plot([wall_lx, wall_rx], [wall_y + wall_h, wall_y + wall_h],
                color=POMPEIAN_CREAM, lw=0.3, alpha=0.4)

        # rooms
        rooms = [
            ("atrium", 0.08, 0.1, 0.25, 0.5),
            ("tablinum", 0.35, 0.1, 0.2, 0.5),
            ("cubicula", 0.57, 0.1, 0.15, 0.4),
            ("peristyle", 0.74, 0.1, 0.2, 0.55),
        ]
        for name, rx, ry, rw, rh in rooms:
            room_x = base_x + width * rx
            room_y = wall_y + height * ry
            room_w = width * rw
            room_h = height * rh
            ax.add_patch(mpatches.Rectangle((room_x, room_y), room_w, room_h,
                                            linewidth=0.15,
                                            edgecolor=POMPEIAN_OCHRE,
                                            facecolor="none", alpha=0.35))
            ax.text(room_x + room_w / 2, room_y + room_h * 0.5,
                    name, fontsize=4, color=POMPEIAN_OCHRE, alpha=0.4,
                    ha="center", va="center", fontfamily="serif")

        # impluvium in atrium
        impl_x = base_x + width * 0.14
        impl_w = width * 0.12
        impl_y = wall_y + height * 0.1
        impl_h = height * 0.05
        ax.add_patch(mpatches.Rectangle((impl_x, impl_y), impl_w, impl_h,
                                        linewidth=0.15,
                                        edgecolor=POMPEIAN_BLUE,
                                        facecolor=POMPEIAN_BLUE, alpha=0.2))

    def street_scene(self, ax, width, height):
        """Pompeian street with shops, sidewalks, stepping stones."""
        # road surface
        road_y = height * 0.3
        road_h = height * 0.4
        ax.fill_between([0, width], road_y, road_y + road_h,
                        color=POMPEIAN_SAND, alpha=0.15)

        # stepping stones
        for sx in np.linspace(width * 0.15, width * 0.85, 5):
            stone_w = width * 0.06
            stone_h = height * 0.04
            ax.add_patch(mpatches.FancyBboxPatch(
                (sx - stone_w / 2, road_y + road_h * 0.3), stone_w, stone_h,
                boxstyle="round,pad=0.005", linewidth=0.2,
                edgecolor=POMPEIAN_CREAM, facecolor=POMPEIAN_CREAM, alpha=0.25))

        # sidewalks
        for sy, label in [(road_y + road_h + height * 0.02, "shop"),
                          (road_y - height * 0.18, "shop")]:
            ax.fill_between([0, width], sy, sy + height * 0.15,
                            color=POMPEIAN_BROWN, alpha=0.12)
            # shop fronts
            for fx in np.linspace(width * 0.05, width * 0.95, 8):
                fw = width * 0.08
                ax.add_patch(mpatches.Rectangle((fx, sy), fw, height * 0.12,
                                                linewidth=0.15,
                                                edgecolor=POMPEIAN_OCHRE,
                                                facecolor=POMPEIAN_RED,
                                                alpha=0.1))

        # basalt paving lines
        for py in np.linspace(road_y, road_y + road_h, 8):
            ax.plot([0, width], [py, py], color=POMPEIAN_BROWN, lw=0.1, alpha=0.2)

    def forum(self, ax, width, height):
        """Pompeii forum with colonnades and temples."""
        # open square
        sq_y = height * 0.2
        sq_h = height * 0.5
        ax.fill_between([0, width], sq_y, sq_y + sq_h,
                        color=POMPEIAN_SAND, alpha=0.12)

        # colonnade top and bottom
        for col_y in [sq_y + sq_h, sq_y]:
            for cx_ in np.linspace(width * 0.05, width * 0.95, 20):
                ax.plot([cx_, cx_], [col_y, col_y + height * 0.12],
                        color=POMPEIAN_CREAM, lw=0.2, alpha=0.35)
                ax.plot([cx_ - 0.01 * width, cx_ + 0.01 * width],
                        [col_y + height * 0.12, col_y + height * 0.12],
                        color=POMPEIAN_CREAM, lw=0.2, alpha=0.3)

        # temple at end
        self.roman_temple(ax, width * 0.35, sq_y + sq_h, width * 0.3, height * 0.2)

    def amphitheater(self, ax, center_x, center_y, radius):
        """Pompeii amphitheater - elliptical."""
        # arena floor
        arena_e = Ellipse((center_x, center_y), radius * 1.6, radius * 0.9,
                          linewidth=0.2, edgecolor=POMPEIAN_SAND,
                          facecolor=POMPEIAN_SAND, alpha=0.15)
        ax.add_patch(arena_e)

        # seating tiers
        for i in range(6):
            r_x = radius * (1.0 + i * 0.12)
            r_y = radius * 0.55 + i * radius * 0.07
            tier = Ellipse((center_x, center_y), r_x * 2, r_y * 2,
                           linewidth=0.15, edgecolor=POMPEIAN_CREAM,
                           facecolor="none", alpha=0.2 + i * 0.03)
            ax.add_patch(tier)

        # outer wall
        outer = Ellipse((center_x, center_y), radius * 2.4, radius * 1.5,
                        linewidth=0.3, edgecolor=POMPEIAN_CREAM,
                        facecolor="none", alpha=0.35)
        ax.add_patch(outer)

    def house_of_faun(self, ax, width, height):
        """House of the Faun floor plan."""
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        # outline
        ax.add_patch(mpatches.Rectangle((0.05, 0.05), 0.9, 0.9,
                                        linewidth=0.3, edgecolor=POMPEIAN_CREAM,
                                        facecolor="none", alpha=0.35))
        # rooms
        room_data = [
            (0.05, 0.05, 0.2, 0.3, "vestibule"),
            (0.27, 0.05, 0.18, 0.3, "atrium I"),
            (0.47, 0.05, 0.18, 0.3, "atrium II"),
            (0.67, 0.05, 0.28, 0.3, "peristyle"),
            (0.05, 0.37, 0.45, 0.28, "Alexander\nMosaic"),
            (0.52, 0.37, 0.43, 0.28, "garden"),
            (0.05, 0.67, 0.9, 0.28, "peristyle garden"),
        ]
        for rx, ry, rw, rh, name in room_data:
            ax.add_patch(mpatches.Rectangle((rx, ry), rw, rh,
                                            linewidth=0.15,
                                            edgecolor=POMPEIAN_OCHRE,
                                            facecolor=POMPEIAN_RED,
                                            alpha=0.08))
            ax.text(rx + rw / 2, ry + rh / 2, name,
                    fontsize=3.5, color=POMPEIAN_OCHRE, alpha=0.45,
                    ha="center", va="center", fontfamily="serif")


# ======================================================================
# 3. PompeiiDailyLife
# ======================================================================

class PompeiiDailyLife:

    def thermopolium(self, ax, x, y, w, h):
        """Roman fast-food counter."""
        # counter (L-shape)
        counter_pts = np.array([
            [x, y], [x + w * 0.7, y], [x + w * 0.7, y + h * 0.35],
            [x + w, y + h * 0.35], [x + w, y + h * 0.45],
            [x, y + h * 0.45],
        ])
        ax.fill(counter_pts[:, 0], counter_pts[:, 1],
                color=POMPEIAN_TERRACOTTA, alpha=0.3)
        ax.plot(counter_pts[:, 0], counter_pts[:, 1],
                color=POMPEIAN_BROWN, lw=0.3, alpha=0.5)

        # dolia (jars in counter)
        for dx in np.linspace(x + w * 0.08, x + w * 0.6, 4):
            jar_t = np.linspace(0, 1, 60)
            jar_r = 0.025 * w * (1 + 0.5 * np.sin(np.pi * jar_t))
            jar_x = np.concatenate([dx + jar_r, (dx - jar_r)[::-1]])
            jar_y = np.concatenate([y + h * 0.2 + h * 0.15 * jar_t,
                                    (y + h * 0.2 + h * 0.15 * jar_t)[::-1]])
            ax.fill(jar_x, jar_y, color=POMPEIAN_TERRACOTTA, alpha=0.25)
            ax.plot(jar_x, jar_y, color=POMPEIAN_BROWN, lw=0.2, alpha=0.4)

        # food items on counter
        for fx_ in [x + w * 0.78, x + w * 0.88]:
            theta = np.linspace(0, 2 * np.pi, 40)
            ax.fill(fx_ + 0.02 * w * np.cos(theta),
                    y + h * 0.4 + 0.015 * h * np.sin(theta),
                    color=POMPEIAN_OCHRE, alpha=0.25)

    def gladiator(self, ax, x, y, h):
        """Gladiator with shield and weapon."""
        # body
        t = np.linspace(-1, 1, 200)
        torso_x = x + 0.04 * h * t
        torso_y = y + h * 0.3 + h * 0.25 * (1 - t ** 2)
        ax.fill_between(torso_x, y + h * 0.1, torso_y,
                        color=POMPEIAN_CREAM, alpha=0.2)
        ax.plot(torso_x, torso_y, color=POMPEIAN_CREAM, lw=0.2, alpha=0.3)

        # head
        theta = np.linspace(0, 2 * np.pi, 50)
        ax.fill(x + 0.02 * h * np.cos(theta),
                y + h * 0.6 + 0.02 * h * np.sin(theta),
                color=POMPEIAN_CREAM, alpha=0.2)

        # helmet
        helmet_t = np.linspace(0, np.pi, 40)
        ax.plot(x + 0.03 * h * np.cos(helmet_t),
                y + h * 0.63 + 0.015 * h * np.sin(helmet_t),
                color=POMPEIAN_OCHRE, lw=0.3, alpha=0.35)

        # shield (large oval)
        sh_theta = np.linspace(0, 2 * np.pi, 80)
        ax.fill(x - 0.08 * h + 0.04 * h * np.cos(sh_theta),
                y + h * 0.35 + 0.07 * h * np.sin(sh_theta),
                color=POMPEIAN_RED, alpha=0.2)
        ax.plot(x - 0.08 * h + 0.04 * h * np.cos(sh_theta),
                y + h * 0.35 + 0.07 * h * np.sin(sh_theta),
                color=POMPEIAN_GOLD, lw=0.25, alpha=0.4)

        # sword
        ax.plot([x + 0.05 * h, x + 0.12 * h], [y + h * 0.4, y + h * 0.55],
                color=POMPEIAN_CREAM, lw=0.25, alpha=0.4)

        # legs
        ax.plot([x - 0.01 * h, x - 0.03 * h], [y + h * 0.1, y],
                color=POMPEIAN_CREAM, lw=0.25, alpha=0.3)
        ax.plot([x + 0.01 * h, x + 0.03 * h], [y + h * 0.1, y],
                color=POMPEIAN_CREAM, lw=0.25, alpha=0.3)

    def baker(self, ax, x, y, w, h):
        """Baker with bread and oven."""
        # oven arch
        arch_t = np.linspace(0, np.pi, 100)
        oven_x = x + w * 0.6 + 0.15 * w * np.cos(arch_t)
        oven_y = y + h * 0.2 + 0.12 * h * np.sin(arch_t)
        ax.fill_between(oven_x, y + h * 0.2, oven_y,
                        color=POMPEIAN_TERRACOTTA, alpha=0.25)
        ax.plot(oven_x, oven_y, color=POMPEIAN_BROWN, lw=0.3, alpha=0.45)
        # oven opening
        open_t = np.linspace(0, np.pi, 60)
        ax.fill(x + w * 0.6 + 0.06 * w * np.cos(open_t),
                y + h * 0.2 + 0.05 * h * np.sin(open_t),
                color=POMPEIAN_BLACK, alpha=0.3)

        # millstone
        ms_theta = np.linspace(0, 2 * np.pi, 80)
        ax.fill(x + w * 0.25 + 0.06 * w * np.cos(ms_theta),
                y + h * 0.35 + 0.06 * w * np.sin(ms_theta),
                color=POMPEIAN_SAND, alpha=0.2)
        ax.plot(x + w * 0.25 + 0.06 * w * np.cos(ms_theta),
                y + h * 0.35 + 0.06 * w * np.sin(ms_theta),
                color=POMPEIAN_BROWN, lw=0.2, alpha=0.35)

        # bread loaves
        for bx_ in np.linspace(x + w * 0.4, x + w * 0.55, 3):
            bt = np.linspace(0, 1, 40)
            bread_y = y + h * 0.15 + 0.02 * h * np.sin(np.pi * bt)
            bread_x = bx_ + 0.03 * w * (bt - 0.5)
            ax.fill_between(bread_x, y + h * 0.15, bread_y,
                            color=POMPEIAN_OCHRE, alpha=0.3)

    def election_notice(self, ax, x, y, w, h):
        """Electoral programmata painted notice."""
        # panel background
        ax.add_patch(mpatches.Rectangle((x, y), w, h,
                                        linewidth=0.2, edgecolor=POMPEIAN_WHITE,
                                        facecolor=POMPEIAN_WHITE, alpha=0.1))
        # decorative top
        top_t = np.linspace(x, x + w, 100)
        ax.plot(top_t, y + h * 0.9 + 0.01 * h * np.sin(top_t * 20 / w),
                color=POMPEIAN_RED, lw=0.2, alpha=0.35)
        # text lines (polynomial scribbles)
        for i in range(5):
            ly = y + h * (0.7 - i * 0.12)
            line_t = np.linspace(x + w * 0.1, x + w * 0.9, 100)
            line_y = ly + 0.003 * h * np.sin(line_t * 30 / w + i)
            ax.plot(line_t, line_y, color=POMPEIAN_BLACK, lw=0.2, alpha=0.3)

    def chariot(self, ax, x, y, w, h):
        """Chariot with horses."""
        # chariot body
        cx_ = x + w * 0.4
        cy_ = y + h * 0.3
        chariot_t = np.linspace(0, 1, 80)
        chariot_x = cx_ + 0.08 * w * np.cos(np.pi * chariot_t)
        chariot_y = cy_ + 0.06 * h * np.sin(np.pi * chariot_t)
        ax.fill(chariot_x, chariot_y, color=POMPEIAN_GOLD, alpha=0.25)
        ax.plot(chariot_x, chariot_y, color=POMPEIAN_GOLD, lw=0.25, alpha=0.4)

        # wheel
        wheel_theta = np.linspace(0, 2 * np.pi, 80)
        wr = 0.04 * h
        ax.plot(cx_ - 0.06 * w + wr * np.cos(wheel_theta),
                y + h * 0.15 + wr * np.sin(wheel_theta),
                color=POMPEIAN_BROWN, lw=0.25, alpha=0.4)
        # spokes
        for s_angle in np.linspace(0, 2 * np.pi, 8, endpoint=False):
            ax.plot([cx_ - 0.06 * w, cx_ - 0.06 * w + wr * 0.9 * np.cos(s_angle)],
                    [y + h * 0.15, y + h * 0.15 + wr * 0.9 * np.sin(s_angle)],
                    color=POMPEIAN_BROWN, lw=0.15, alpha=0.3)

        # horse
        horse_t = np.linspace(0, 1, 100)
        horse_x = x + w * 0.7 + 0.1 * w * horse_t
        horse_body = cy_ + 0.04 * h * np.sin(np.pi * horse_t * 2)
        ax.plot(horse_x, horse_body, color=POMPEIAN_BROWN, lw=0.3, alpha=0.35)
        # horse legs
        for lx_off in [0.02, 0.06, 0.1]:
            ax.plot([x + w * 0.7 + w * lx_off] * 2,
                    [horse_body[np.argmin(np.abs(horse_t - lx_off))] if lx_off < 1 else cy_,
                     y + h * 0.08],
                    color=POMPEIAN_BROWN, lw=0.2, alpha=0.3)

    def fountain(self, ax, x, y, w, h):
        """Public fountain with bronze statue."""
        # basin
        basin_t = np.linspace(-1, 1, 100)
        basin_x = x + w * 0.5 + w * 0.35 * basin_t
        basin_y = y + h * 0.2 + 0.08 * h * np.sqrt(np.clip(1 - basin_t ** 2, 0, 1))
        ax.fill_between(basin_x, y + h * 0.18, basin_y,
                        color=POMPEIAN_SAND, alpha=0.25)
        ax.plot(basin_x, basin_y, color=POMPEIAN_SAND, lw=0.25, alpha=0.4)

        # pedestal
        ax.add_patch(mpatches.Rectangle((x + w * 0.45, y + h * 0.28),
                                        w * 0.1, h * 0.12,
                                        linewidth=0.2, edgecolor=POMPEIAN_CREAM,
                                        facecolor=POMPEIAN_SAND, alpha=0.2))

        # statue (simple figure)
        stat_x = x + w * 0.5
        stat_t = np.linspace(-1, 1, 100)
        stat_body_x = stat_x + 0.02 * w * stat_t
        stat_body_y = y + h * 0.4 + h * 0.2 * (1 - stat_t ** 2)
        ax.fill_between(stat_body_x, y + h * 0.4, stat_body_y,
                        color=POMPEIAN_CREAM, alpha=0.15)

        # water spout
        spout_t = np.linspace(0, 1, 30)
        ax.plot(stat_x + 0.03 * w * spout_t,
                y + h * 0.45 - 0.08 * h * spout_t ** 2,
                color=POMPEIAN_BLUE, lw=0.2, alpha=0.3)


# ======================================================================
# 4. PompeiiMythology
# ======================================================================

class PompeiiMythology:

    def winged_victory(self, ax, x, y, h):
        """Winged Nike/Victoria."""
        # body
        t = np.linspace(-1, 1, 200)
        body_x = x + 0.03 * h * t
        body_y = y + h * 0.3 + h * 0.3 * (1 - t ** 2)
        ax.fill_between(body_x, y + h * 0.05, body_y,
                        color=POMPEIAN_CREAM, alpha=0.2)
        ax.plot(body_x, body_y, color=POMPEIAN_CREAM, lw=0.2, alpha=0.35)

        # head
        theta = np.linspace(0, 2 * np.pi, 50)
        head_cx = x
        head_cy = y + h * 0.68
        ax.fill(head_cx + 0.018 * h * np.cos(theta),
                head_cy + 0.018 * h * np.sin(theta),
                color=POMPEIAN_CREAM, alpha=0.2)

        # wings
        wing_t = np.linspace(0, 1, 80)
        for side in [-1, 1]:
            wing_x = x + side * 0.02 * h + side * 0.15 * h * wing_t
            wing_y = y + h * 0.6 + 0.08 * h * np.sin(np.pi * wing_t)
            ax.plot(wing_x, wing_y, color=POMPEIAN_GOLD, lw=0.2, alpha=0.35)
            # feather lines
            for ft in np.linspace(0.1, 0.9, 8):
                fx_ = x + side * 0.02 * h + side * 0.15 * h * ft
                fy_ = y + h * 0.6 + 0.08 * h * np.sin(np.pi * ft)
                ax.plot([fx_, fx_ + side * 0.02 * h],
                        [fy_, fy_ + 0.03 * h],
                        color=POMPEIAN_GOLD, lw=0.1, alpha=0.25)

        # flowing dress
        dress_t = np.linspace(0, 1, 100)
        for side in [-1, 1]:
            dx = x + side * 0.03 * h + side * 0.04 * h * dress_t
            dy = y + h * 0.15 + h * 0.25 * dress_t
            ax.plot(dx, dy, color=POMPEIAN_CREAM, lw=0.15, alpha=0.2)

    def theatrical_mask(self, ax, center_x, center_y, radius):
        """Comic or tragic theater mask."""
        theta = np.linspace(0, 2 * np.pi, 100)
        # face outline
        face_x = center_x + radius * np.cos(theta)
        face_y = center_y + radius * 0.85 * np.sin(theta)
        ax.fill(face_x, face_y, color=POMPEIAN_CREAM, alpha=0.15)
        ax.plot(face_x, face_y, color=POMPEIAN_CREAM, lw=0.3, alpha=0.4)

        # eyes
        for ex in [-0.35, 0.35]:
            eye_t = np.linspace(0, 2 * np.pi, 40)
            ax.plot(center_x + ex * radius + 0.1 * radius * np.cos(eye_t),
                    center_y + 0.15 * radius * np.sin(eye_t),
                    color=POMPEIAN_BLACK, lw=0.2, alpha=0.4)

        # mouth (large opening)
        mouth_t = np.linspace(0, np.pi, 60)
        mouth_x = center_x + 0.3 * radius * np.cos(mouth_t)
        mouth_y = center_y - 0.35 * radius + 0.15 * radius * np.sin(mouth_t)
        ax.fill(mouth_x, mouth_y, color=POMPEIAN_BLACK, alpha=0.3)
        ax.plot(mouth_x, mouth_y, color=POMPEIAN_BLACK, lw=0.2, alpha=0.4)

        # brow ridge
        for side in [-1, 1]:
            brow_t = np.linspace(0, 1, 30)
            bx = center_x + side * (0.15 + 0.2 * brow_t) * radius
            by = center_y + 0.3 * radius + 0.08 * radius * brow_t * side
            ax.plot(bx, by, color=POMPEIAN_BLACK, lw=0.2, alpha=0.35)

    def medusa(self, ax, center_x, center_y, radius):
        """Gorgoneion - Medusa head with snake hair."""
        theta = np.linspace(0, 2 * np.pi, 100)
        # face
        ax.fill(center_x + radius * 0.8 * np.cos(theta),
                center_y + radius * 0.7 * np.sin(theta),
                color=POMPEIAN_CREAM, alpha=0.15)
        ax.plot(center_x + radius * 0.8 * np.cos(theta),
                center_y + radius * 0.7 * np.sin(theta),
                color=POMPEIAN_GREEN, lw=0.25, alpha=0.4)

        # snake hair
        np.random.seed(77)
        for i in range(16):
            angle = i * 2 * np.pi / 16
            snake_t = np.linspace(0, 1, 60)
            sx = center_x + radius * 0.75 * np.cos(angle) + \
                 0.08 * radius * np.sin(snake_t * 6 * np.pi + i)
            sy = center_y + radius * 0.65 * np.sin(angle) + \
                 0.12 * radius * snake_t
            ax.plot(sx, sy, color=POMPEIAN_GREEN, lw=0.15, alpha=0.35)
            # snake heads
            ax.plot(sx[-1], sy[-1], "o", color=POMPEIAN_GREEN, markersize=1.5, alpha=0.3)

        # eyes
        for ex in [-0.25, 0.25]:
            eye_t = np.linspace(0, 2 * np.pi, 40)
            ax.fill(center_x + ex * radius + 0.06 * radius * np.cos(eye_t),
                    center_y + 0.1 * radius + 0.04 * radius * np.sin(eye_t),
                    color=POMPEIAN_GREEN, alpha=0.3)

        # fangs
        ax.plot([center_x - 0.08 * radius, center_x - 0.06 * radius],
                [center_y - 0.2 * radius, center_y - 0.35 * radius],
                color=POMPEIAN_WHITE, lw=0.2, alpha=0.35)
        ax.plot([center_x + 0.08 * radius, center_x + 0.06 * radius],
                [center_y - 0.2 * radius, center_y - 0.35 * radius],
                color=POMPEIAN_WHITE, lw=0.2, alpha=0.35)

    def satyr(self, ax, x, y, h):
        """Dancing satyr with grapes."""
        # body
        t = np.linspace(-1, 1, 200)
        body_x = x + 0.03 * h * t + 0.01 * h * np.sin(t * 3)
        body_y = y + h * 0.25 + h * 0.25 * (1 - t ** 2)
        ax.fill_between(body_x, y + h * 0.05, body_y,
                        color=POMPEIAN_CREAM, alpha=0.18)
        # head
        theta = np.linspace(0, 2 * np.pi, 50)
        ax.fill(x + 0.015 * h * np.cos(theta),
                y + h * 0.6 + 0.015 * h * np.sin(theta),
                color=POMPEIAN_CREAM, alpha=0.18)
        # goat legs
        ax.plot([x - 0.02 * h, x - 0.04 * h, x - 0.02 * h],
                [y + h * 0.1, y + h * 0.05, y],
                color=POMPEIAN_BROWN, lw=0.2, alpha=0.3)
        ax.plot([x + 0.02 * h, x + 0.04 * h, x + 0.02 * h],
                [y + h * 0.1, y + h * 0.05, y],
                color=POMPEIAN_BROWN, lw=0.2, alpha=0.3)
        # grapes
        for gx_off in [-0.02, 0, 0.02]:
            for gy_off in [0, 0.01]:
                ax.plot(x + 0.05 * h + gx_off * h, y + h * 0.5 + gy_off * h,
                        "o", color="#5B2C6F", markersize=2, alpha=0.3)

    def venus(self, ax, x, y, h):
        """Venus/Aphrodite figure."""
        # flowing body curves
        t = np.linspace(-1, 1, 300)
        body_x = x + 0.025 * h * t + 0.008 * h * np.sin(2 * np.pi * t)
        body_y = y + h * 0.3 + h * 0.28 * (1 - t ** 2)
        ax.fill_between(body_x, y + h * 0.08, body_y,
                        color=POMPEIAN_CREAM, alpha=0.18)
        ax.plot(body_x, body_y, color=POMPEIAN_CREAM, lw=0.18, alpha=0.3)

        # head
        theta = np.linspace(0, 2 * np.pi, 50)
        ax.fill(x + 0.015 * h * np.cos(theta),
                y + h * 0.66 + 0.015 * h * np.sin(theta),
                color=POMPEIAN_CREAM, alpha=0.18)

        # hair
        hair_t = np.linspace(0, 1, 60)
        for side in [-1, 1]:
            hx = x + side * 0.01 * h + side * 0.03 * h * hair_t
            hy = y + h * 0.65 + h * 0.06 * hair_t
            ax.plot(hx, hy, color=POMPEIAN_GOLD, lw=0.12, alpha=0.25)

        # arms
        arm_t = np.linspace(0, 1, 40)
        ax.plot(x + 0.03 * h + 0.05 * h * arm_t, y + h * 0.5 + 0.05 * h * arm_t,
                color=POMPEIAN_CREAM, lw=0.18, alpha=0.25)
        ax.plot(x - 0.03 * h - 0.04 * h * arm_t, y + h * 0.45 + 0.03 * h * arm_t,
                color=POMPEIAN_CREAM, lw=0.18, alpha=0.25)

    def poseidon(self, ax, x, y, h):
        """Neptune/Poseidon with trident."""
        # body
        t = np.linspace(-1, 1, 200)
        body_x = x + 0.035 * h * t
        body_y = y + h * 0.3 + h * 0.28 * (1 - t ** 2)
        ax.fill_between(body_x, y + h * 0.05, body_y,
                        color=POMPEIAN_CREAM, alpha=0.18)

        # head
        theta = np.linspace(0, 2 * np.pi, 50)
        ax.fill(x + 0.018 * h * np.cos(theta),
                y + h * 0.66 + 0.018 * h * np.sin(theta),
                color=POMPEIAN_CREAM, alpha=0.18)

        # beard
        for i in range(5):
            bx = x - 0.01 * h + i * 0.005 * h
            by_t = np.linspace(0, 1, 20)
            ax.plot(bx + 0.005 * h * np.sin(by_t * 4),
                    y + h * 0.6 - 0.04 * h * by_t,
                    color=POMPEIAN_SAND, lw=0.1, alpha=0.25)

        # trident
        trident_x = x + 0.08 * h
        ax.plot([trident_x, trident_x], [y + h * 0.1, y + h * 0.8],
                color=POMPEIAN_GOLD, lw=0.25, alpha=0.4)
        # prongs
        for px in [-0.02, 0, 0.02]:
            ax.plot([trident_x + px * h, trident_x + px * h],
                    [y + h * 0.8, y + h * 0.88],
                    color=POMPEIAN_GOLD, lw=0.2, alpha=0.35)

        # arms
        ax.plot([x + 0.03 * h, trident_x - 0.01 * h],
                [y + h * 0.5, y + h * 0.55],
                color=POMPEIAN_CREAM, lw=0.2, alpha=0.25)


# ======================================================================
# 5. PompeiiDecorations
# ======================================================================

class PompeiiDecorations:

    def meander_pattern(self, ax, x, y, w, h, color="#8B0000"):
        """Greek key / meander border."""
        xs = np.linspace(x, x + w, 400)
        step = w / 16
        meander_y = np.zeros_like(xs)
        for i in range(16):
            x0 = x + i * step
            x1 = x0 + step
            mask = (xs >= x0) & (xs < x1)
            if not np.any(mask):
                continue
            local = (xs[mask] - x0) / step
            # meander path: up, right, down, right
            pattern = np.where(
                local < 0.25, np.interp(local, [0, 0.25], [0, 1]),
                np.where(local < 0.5, 1,
                np.where(local < 0.75, np.interp(local, [0.5, 0.75], [1, 0]),
                0))
            )
            meander_y[mask] = pattern

        meander_y_scaled = y + h * meander_y
        ax.plot(xs, meander_y_scaled, color=color, lw=0.25, alpha=0.45)

    def guilloche(self, ax, x, y, length, amplitude, color="#C0A060"):
        """Interlaced band pattern."""
        t = np.linspace(0, 4 * np.pi, 300)
        xs = x + length * t / (4 * np.pi)
        y1 = y + amplitude * np.sin(t)
        y2 = y + amplitude * np.sin(t + np.pi)
        ax.plot(xs, y1, color=color, lw=0.2, alpha=0.4)
        ax.plot(xs, y2, color=color, lw=0.2, alpha=0.4)
        # crossing fills
        for i in range(0, len(t) - 20, 20):
            ax.fill_between(xs[i:i + 20], y1[i:i + 20], y2[i:i + 20],
                            color=color, alpha=0.06)

    def wave_pattern(self, ax, x, y, length, amplitude):
        """Running wave pattern."""
        t = np.linspace(0, 6 * np.pi, 300)
        xs = x + length * t / (6 * np.pi)
        wave_y = y + amplitude * np.sin(t)
        wave_y2 = y + amplitude * 0.6 * np.sin(t + 0.5)
        ax.plot(xs, wave_y, color=POMPEIAN_BLUE, lw=0.2, alpha=0.35)
        ax.plot(xs, wave_y2, color=POMPEIAN_BLUE, lw=0.15, alpha=0.25)

    def candelabra(self, ax, x, y, height):
        """Ornamental candelabra column."""
        # central stem
        ax.plot([x, x], [y, y + height], color=POMPEIAN_GOLD, lw=0.25, alpha=0.4)

        # stacked ornaments
        ornaments = np.linspace(0.1, 0.9, 6)
        for frac in ornaments:
            oy = y + height * frac
            orn_size = 0.02 * height
            # vase shape
            t = np.linspace(0, 1, 40)
            orn_x = orn_size * np.sin(np.pi * t)
            orn_y = oy + orn_size * 0.5 * t
            ax.plot(x + orn_x, orn_y, color=POMPEIAN_GOLD, lw=0.15, alpha=0.35)
            ax.plot(x - orn_x, orn_y, color=POMPEIAN_GOLD, lw=0.15, alpha=0.35)
            # flower at top of vase
            petal_theta = np.linspace(0, 2 * np.pi, 30)
            ax.plot(x + orn_size * 0.3 * np.cos(petal_theta),
                    oy + orn_size + orn_size * 0.3 * np.sin(petal_theta),
                    color=POMPEIAN_RED, lw=0.12, alpha=0.3)

    def garland(self, ax, x1, y1, x2, y2):
        """Flower and fruit garland/swag."""
        t = np.linspace(0, 1, 200)
        # drooping catenary-like curve
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2 - 0.05 * abs(x2 - x1)
        gx = x1 + (x2 - x1) * t
        gy = y1 + (y2 - y1) * t + 4 * (mid_y - (y1 + y2) / 2) * t * (1 - t)
        ax.plot(gx, gy, color=POMPEIAN_GREEN, lw=0.2, alpha=0.35)

        # flowers along garland
        for ft in np.linspace(0.1, 0.9, 10):
            fx_ = x1 + (x2 - x1) * ft
            fy_ = y1 + (y2 - y1) * ft + 4 * (mid_y - (y1 + y2) / 2) * ft * (1 - ft)
            petal_theta = np.linspace(0, 2 * np.pi, 20)
            pr = 0.008 * abs(x2 - x1)
            ax.fill(fx_ + pr * np.cos(petal_theta),
                    fy_ + pr * np.sin(petal_theta),
                    color=np.random.choice([POMPEIAN_RED, POMPEIAN_OCHRE, POMPEIAN_WHITE]),
                    alpha=0.25)

    def sphinx(self, ax, x, y, h):
        """Sphinx figure."""
        # lion body
        body_t = np.linspace(0, 1, 200)
        body_x = x + 0.12 * h * body_t
        body_y = y + h * 0.15 + 0.03 * h * np.sin(np.pi * body_t * 2)
        ax.plot(body_x, body_y, color=POMPEIAN_OCHRE, lw=0.25, alpha=0.4)

        # human head
        theta = np.linspace(0, 2 * np.pi, 40)
        head_x = x + 0.12 * h + 0.015 * h * np.cos(theta)
        head_y = y + h * 0.35 + 0.015 * h * np.sin(theta)
        ax.fill(head_x, head_y, color=POMPEIAN_CREAM, alpha=0.15)

        # wings
        wing_t = np.linspace(0, 1, 50)
        ax.plot(x + 0.04 * h + 0.08 * h * wing_t,
                y + h * 0.2 + 0.08 * h * np.sin(np.pi * wing_t),
                color=POMPEIAN_GOLD, lw=0.2, alpha=0.35)

        # legs
        for lx in [0.02, 0.06, 0.1]:
            ax.plot([x + lx * h, x + lx * h],
                    [y + h * 0.15, y],
                    color=POMPEIAN_OCHRE, lw=0.2, alpha=0.3)

    def centaur(self, ax, x, y, h):
        """Centaur figure."""
        # horse body
        body_t = np.linspace(0, 1, 200)
        body_x = x + 0.1 * h * body_t
        body_y = y + h * 0.2 + 0.03 * h * np.sin(np.pi * body_t)
        ax.plot(body_x, body_y, color=POMPEIAN_BROWN, lw=0.25, alpha=0.35)

        # human torso
        torso_x = np.array([x + 0.06 * h, x + 0.07 * h])
        torso_y = np.array([y + h * 0.2, y + h * 0.45])
        ax.plot(torso_x, torso_y, color=POMPEIAN_CREAM, lw=0.25, alpha=0.3)

        # head
        theta = np.linspace(0, 2 * np.pi, 40)
        ax.fill(x + 0.07 * h + 0.012 * h * np.cos(theta),
                y + h * 0.48 + 0.012 * h * np.sin(theta),
                color=POMPEIAN_CREAM, alpha=0.18)

        # horse legs
        for lx in [0.01, 0.04, 0.06, 0.09]:
            ax.plot([x + lx * h, x + lx * h + 0.005 * h],
                    [y + h * 0.18, y],
                    color=POMPEIAN_BROWN, lw=0.2, alpha=0.3)


# ======================================================================
# 6. PompeiiComposition
# ======================================================================

class PompeiiComposition:
    """Full composition scenes combining all elements."""

    def __init__(self):
        self.fresco = PompeiiFrescoStyle()
        self.arch = PompeiiArchitecture()
        self.life = PompeiiDailyLife()
        self.myth = PompeiiMythology()
        self.deco = PompeiiDecorations()

    def vesuvius_from_sea(self, width, height):
        """View of Vesuvius from the sea."""
        fig, ax = _fig()
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)

        # dark sky
        sky_xs = np.linspace(0, width, 200)
        sky_g = np.linspace(0, 0.15, 200)
        for i in range(199):
            ax.fill_between([sky_xs[i], sky_xs[i + 1]], 0, height,
                            color=(0.1 + 0.05 * sky_g[i], 0.08, 0.12 + 0.08 * sky_g[i]),
                            alpha=0.4)

        # sea
        sea_xs = np.linspace(0, width, 300)
        sea_ys = height * 0.35
        for i in range(5):
            wave_y = sea_ys - i * height * 0.02 + 0.01 * height * np.sin(sea_xs * 15 / width + i * 0.7)
            ax.plot(sea_xs, wave_y, color=POMPEIAN_BLUE, lw=0.15, alpha=0.2 + i * 0.03)

        ax.fill_between([0, width], 0, sea_ys - 0.08 * height,
                        color=POMPEIAN_BLUE, alpha=0.12)

        # Vesuvius mountain
        mt_x = np.array([width * 0.2, width * 0.42, width * 0.48,
                         width * 0.52, width * 0.58, width * 0.8])
        mt_y = np.array([sea_ys + height * 0.02, height * 0.65, height * 0.85,
                         height * 0.88, height * 0.82, sea_ys + height * 0.02])
        mt_t = np.linspace(0, 1, 200)
        mt_xs = np.interp(mt_t, np.linspace(0, 1, len(mt_x)), mt_x)
        mt_ys = np.interp(mt_t, np.linspace(0, 1, len(mt_y)), mt_y)
        # add polynomial roughness
        mt_ys += 0.02 * height * np.sin(mt_xs * 30 / width) * (mt_ys - sea_ys) / (height * 0.8)
        ax.fill_between(mt_xs, sea_ys, mt_ys, color=POMPEIAN_BROWN, alpha=0.2)
        ax.plot(mt_xs, mt_ys, color=POMPEIAN_BROWN, lw=0.3, alpha=0.4)

        # eruption plume
        plume_x = np.array([width * 0.46, width * 0.48, width * 0.52, width * 0.54])
        plume_y = np.array([height * 0.88, height * 0.92, height * 0.95, height * 0.93])
        for i in range(10):
            offset = i * 0.015 * width
            cloud_theta = np.linspace(0, 2 * np.pi, 60)
            cr = 0.04 * width + i * 0.005 * width
            cx_ = width * 0.5 + offset * (i % 2 * 2 - 1) * 0.3
            cy_ = height * 0.9 + i * 0.01 * height
            ax.fill(cx_ + cr * np.cos(cloud_theta),
                    cy_ + cr * 0.6 * np.sin(cloud_theta),
                    color=ASH_GREY, alpha=0.06)

        # small ship
        ship_x = width * 0.3
        ship_y = sea_ys - 0.02 * height
        ship_t = np.linspace(0, 1, 50)
        hull_x = ship_x + 0.04 * width * (ship_t - 0.5)
        hull_y = ship_y + 0.01 * height * np.sin(np.pi * ship_t)
        ax.plot(hull_x, hull_y, color=POMPEIAN_CREAM, lw=0.2, alpha=0.3)
        # mast
        ax.plot([ship_x, ship_x], [ship_y, ship_y + 0.06 * height],
                color=POMPEIAN_CREAM, lw=0.15, alpha=0.25)

        self.fresco.pompeii_border(ax, width, height, "red")
        return fig, ax

    def last_day(self, width, height):
        """Last day of Pompeii - eruption, fleeing people."""
        fig, ax = _fig()
        fig.set_facecolor("#0A0608")
        ax.set_facecolor("#0A0608")
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)

        # dark ash-filled sky
        for i in range(30):
            cx_ = np.random.rand() * width
            cy_ = height * 0.6 + np.random.rand() * height * 0.4
            cr = 0.05 * width + np.random.rand() * 0.08 * width
            theta = np.linspace(0, 2 * np.pi, 60)
            ax.fill(cx_ + cr * np.cos(theta),
                    cy_ + cr * 0.5 * np.sin(theta),
                    color=ASH_GREY, alpha=0.04)

        # ground
        ground_xs = np.linspace(0, width, 200)
        ground_ys = height * 0.25 + 0.02 * height * np.sin(ground_xs * 10 / width)
        ax.fill_between(ground_xs, 0, ground_ys, color="#1A1008", alpha=0.3)
        ax.plot(ground_xs, ground_ys, color=POMPEIAN_BROWN, lw=0.2, alpha=0.3)

        # Vesuvius in background (erupting)
        mt_x = np.linspace(width * 0.3, width * 0.7, 200)
        mt_profile = height * 0.6 + height * 0.25 * np.exp(-((mt_x - width * 0.5) ** 2) / (0.01 * width ** 2))
        ax.fill_between(mt_x, height * 0.25, mt_profile, color="#2A1A10", alpha=0.3)
        ax.plot(mt_x, mt_profile, color=POMPEIAN_BROWN, lw=0.2, alpha=0.35)

        # fire/lava from crater
        for i in range(8):
            flame_t = np.linspace(0, 1, 40)
            fx = width * 0.5 + 0.02 * width * np.sin(flame_t * 5 + i)
            fy = height * 0.85 + 0.1 * height * flame_t
            ax.plot(fx, fy, color=POMPEIAN_RED, lw=0.15, alpha=0.3 - i * 0.03)

        # fleeing figures
        for fig_x_ratio in [0.15, 0.35, 0.6, 0.8]:
            fx_ = width * fig_x_ratio
            fy_ = height * 0.28
            self._small_figure(ax, fx_, fy_, h=height * 0.08, lean=0.02)

        # falling ash
        np.random.seed(99)
        for _ in range(50):
            ax_ = np.random.rand() * width
            ay_ = np.random.rand() * height * 0.8 + height * 0.2
            ax.plot([ax_, ax_ + 0.005 * width], [ay_, ay_ - 0.02 * height],
                    color=ASH_GREY, lw=0.1, alpha=0.2)

        return fig, ax

    def _small_figure(self, ax, x, y, h, lean=0):
        """Helper: small fleeing figure."""
        t = np.linspace(-1, 1, 100)
        body_x = x + lean * h * t + 0.015 * h * t
        body_y = y + h * 0.2 + h * 0.2 * (1 - t ** 2)
        ax.fill_between(body_x, y, body_y, color=POMPEIAN_CREAM, alpha=0.12)
        # head
        theta = np.linspace(0, 2 * np.pi, 20)
        ax.fill(x + 0.01 * h * np.cos(theta),
                y + h * 0.45 + 0.01 * h * np.sin(theta),
                color=POMPEIAN_CREAM, alpha=0.12)
        # running legs
        ax.plot([x - 0.005 * h, x - 0.02 * h, x - 0.01 * h],
                [y, y - 0.02 * h, y - 0.04 * h],
                color=POMPEIAN_CREAM, lw=0.15, alpha=0.12)
        ax.plot([x + 0.005 * h, x + 0.02 * h, x + 0.03 * h],
                [y, y - 0.02 * h, y - 0.04 * h],
                color=POMPEIAN_CREAM, lw=0.15, alpha=0.12)

    def villa_of_mysteries(self, width, height):
        """Villa of the Mysteries frieze."""
        fig, ax = _fig()
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)

        # Pompeian red background
        ax.add_patch(mpatches.Rectangle((0, 0), width, height,
                                        linewidth=0, facecolor=POMPEIAN_DARK_RED,
                                        alpha=0.15))

        # frieze band
        frieze_y = height * 0.15
        frieze_h = height * 0.65
        ax.add_patch(mpatches.Rectangle((0, frieze_y), width, frieze_h,
                                        linewidth=0.3, edgecolor=POMPEIAN_GOLD,
                                        facecolor=POMPEIAN_DARK_RED, alpha=0.08))

        # dancing/initiation figures
        n_figs = 7
        for i in range(n_figs):
            fx = width * 0.1 + i * width * 0.12
            fy = frieze_y + frieze_h * 0.1
            fh = frieze_h * 0.7

            # body with motion
            t = np.linspace(-1, 1, 200)
            phase = i * 0.5
            body_x = fx + 0.04 * width * 0.1 * t + 0.01 * width * 0.1 * np.sin(t * 3 + phase)
            body_y_top = fy + fh * 0.6 + fh * 0.15 * (1 - t ** 2)
            body_y_bot = fy
            ax.fill_between(body_x, body_y_bot, body_y_top,
                            color=POMPEIAN_CREAM, alpha=0.12)

            # head
            theta = np.linspace(0, 2 * np.pi, 30)
            ax.fill(fx + 0.01 * width * 0.1 * np.cos(theta),
                    fy + fh * 0.7 + 0.01 * width * 0.1 * np.sin(theta),
                    color=POMPEIAN_CREAM, alpha=0.12)

            # arms in various poses
            arm_phase = phase + 0.5
            ax.plot([fx + 0.01 * width * 0.1, fx + 0.04 * width * 0.1 * np.cos(arm_phase)],
                    [fy + fh * 0.5, fy + fh * 0.5 + 0.02 * fh * np.sin(arm_phase)],
                    color=POMPEIAN_CREAM, lw=0.2, alpha=0.15)

        # decorative borders
        self.deco.guilloche(ax, 0, frieze_y - height * 0.02, width, height * 0.02, POMPEIAN_GOLD)
        self.deco.guilloche(ax, 0, frieze_y + frieze_h + height * 0.02, width, height * 0.02, POMPEIAN_GOLD)

        # top and bottom borders
        self.deco.meander_pattern(ax, 0, height * 0.95, width, height * 0.03, POMPEIAN_GOLD)
        self.deco.meander_pattern(ax, 0, height * 0.02, width, height * 0.03, POMPEIAN_GOLD)

        return fig, ax

    def pompeii_panorama(self, width, height):
        """Panoramic view of Pompeii ruins."""
        fig, ax = _fig()
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)

        # sky gradient
        sky_xs = np.linspace(0, width, 200)
        for i in range(199):
            frac = sky_xs[i] / width
            sky_r = 0.08 + 0.05 * frac
            sky_g = 0.06 + 0.04 * frac
            sky_b = 0.15 + 0.08 * frac
            ax.fill_between([sky_xs[i], sky_xs[i + 1]], height * 0.4, height,
                            color=(sky_r, sky_g, sky_b), alpha=0.3)

        # Vesuvius in background
        mt_x = np.linspace(width * 0.55, width * 0.95, 200)
        mt_y = height * 0.55 + height * 0.2 * np.exp(-((mt_x - width * 0.75) ** 2) / (0.008 * width ** 2))
        ax.fill_between(mt_x, height * 0.4, mt_y, color=POMPEIAN_BROWN, alpha=0.15)
        ax.plot(mt_x, mt_y, color=POMPEIAN_BROWN, lw=0.2, alpha=0.3)

        # ground
        ground_xs = np.linspace(0, width, 200)
        ground_ys = height * 0.4 + 0.01 * height * np.sin(ground_xs * 8 / width)
        ax.fill_between(ground_xs, 0, ground_ys, color=POMPEIAN_SAND, alpha=0.1)

        # ruins - columns
        np.random.seed(55)
        for _ in range(15):
            cx_ = np.random.rand() * width * 0.8 + width * 0.1
            ch = np.random.rand() * height * 0.15 + height * 0.05
            cy_ = height * 0.4 - ch
            cw = 0.008 * width
            # broken column
            top_y = cy_ + ch * (0.6 + np.random.rand() * 0.4)
            ax.plot([cx_, cx_], [cy_, top_y], color=POMPEIAN_CREAM, lw=0.3, alpha=0.3)
            # capital remnant
            ax.plot([cx_ - cw, cx_ + cw], [top_y, top_y],
                    color=POMPEIAN_CREAM, lw=0.2, alpha=0.25)

        # walls
        for _ in range(8):
            wx = np.random.rand() * width * 0.6 + width * 0.2
            wy = height * 0.4 - np.random.rand() * height * 0.05
            ww = np.random.rand() * width * 0.08 + width * 0.02
            wh = np.random.rand() * height * 0.08 + height * 0.02
            ax.add_patch(mpatches.Rectangle((wx, wy), ww, wh,
                                            linewidth=0.15, edgecolor=POMPEIAN_TERRACOTTA,
                                            facecolor=POMPEIAN_TERRACOTTA, alpha=0.08))

        # path/street
        path_xs = np.linspace(width * 0.1, width * 0.9, 200)
        path_y_base = height * 0.3
        path_y = path_y_base + 0.005 * height * np.sin(path_xs * 20 / width)
        ax.fill_between(path_xs, path_y - 0.02 * height, path_y + 0.02 * height,
                        color=POMPEIAN_SAND, alpha=0.1)

        return fig, ax

    def mosaic_floor(self, width, height):
        """Mosaic floor pattern."""
        fig, ax = _fig()
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)

        # dark background
        ax.add_patch(mpatches.Rectangle((0, 0), width, height,
                                        facecolor=POMPEIAN_BLACK, alpha=0.3))

        # geometric tessellation
        cell_size = min(width, height) / 12
        for row in range(14):
            for col in range(14):
                cx_ = col * cell_size
                cy_ = row * cell_size
                if (row + col) % 2 == 0:
                    color = POMPEIAN_WHITE
                else:
                    color = POMPEIAN_RED
                ax.add_patch(mpatches.Rectangle((cx_, cy_), cell_size, cell_size,
                                                facecolor=color, alpha=0.08,
                                                edgecolor=POMPEIAN_OCHRE,
                                                linewidth=0.08))

        # central medallion
        med_r = min(width, height) * 0.2
        med_cx = width / 2
        med_cy = height / 2
        theta = np.linspace(0, 2 * np.pi, 200)
        # outer ring
        for ring_r in [1.0, 0.9, 0.85, 0.7]:
            ring_color = np.random.choice([POMPEIAN_GOLD, POMPEIAN_RED, POMPEIAN_BLUE])
            ax.plot(med_cx + med_r * ring_r * np.cos(theta),
                    med_cy + med_r * ring_r * np.sin(theta),
                    color=ring_color, lw=0.2, alpha=0.35)

        # inner star pattern
        star_points = 8
        for i in range(star_points):
            angle = i * 2 * np.pi / star_points
            ax.plot([med_cx, med_cx + med_r * 0.6 * np.cos(angle)],
                    [med_cy, med_cy + med_r * 0.6 * np.sin(angle)],
                    color=POMPEIAN_GOLD, lw=0.2, alpha=0.3)

        # border meander
        self.deco.meander_pattern(ax, 0, height * 0.02, width, height * 0.04, POMPEIAN_GOLD)
        self.deco.meander_pattern(ax, 0, height * 0.96, width, height * 0.04, POMPEIAN_GOLD)

        return fig, ax

    def garden_of_fugitives(self, width, height):
        """Garden of the Fugitives with plaster casts."""
        fig, ax = _fig()
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)

        # garden background
        ax.add_patch(mpatches.Rectangle((0, 0), width, height,
                                        facecolor=POMPEIAN_GREEN, alpha=0.06))

        # vine supports (tree trunks)
        for tx in np.linspace(width * 0.1, width * 0.9, 6):
            trunk_h = height * 0.6 + np.random.rand() * height * 0.15
            ax.plot([tx, tx], [height * 0.15, height * 0.15 + trunk_h],
                    color=POMPEIAN_BROWN, lw=0.3, alpha=0.3)
            # branches
            for b in range(3):
                by = height * 0.15 + trunk_h * (0.4 + b * 0.2)
                blen = width * 0.08 + np.random.rand() * width * 0.05
                side = 1 if b % 2 == 0 else -1
                bx_t = np.linspace(0, 1, 40)
                bx = tx + side * blen * bx_t
                by_curve = by + 0.02 * height * np.sin(np.pi * bx_t)
                ax.plot(bx, by_curve, color=POMPEIAN_BROWN, lw=0.15, alpha=0.25)

        # ground
        ground_xs = np.linspace(0, width, 200)
        ground_ys = height * 0.15 + 0.005 * height * np.sin(ground_xs * 12 / width)
        ax.fill_between(ground_xs, 0, ground_ys, color=POMPEIAN_GREEN, alpha=0.08)

        # plaster cast figures (reclining)
        cast_positions = [(0.2, 0.16), (0.35, 0.17), (0.55, 0.16), (0.75, 0.18)]
        for cx_ratio, cy_ratio in cast_positions:
            cx_ = width * cx_ratio
            cy_ = height * cy_ratio
            # reclining figure
            t = np.linspace(-1, 1, 150)
            body_x = cx_ + 0.06 * width * 0.1 * t
            body_y = cy_ + 0.015 * height * np.sin(np.pi * (t + 1) / 2)
            ax.fill_between(body_x, cy_ - 0.005 * height, body_y,
                            color=POMPEIAN_CREAM, alpha=0.1)
            ax.plot(body_x, body_y, color=POMPEIAN_CREAM, lw=0.15, alpha=0.2)
            # head
            theta = np.linspace(0, 2 * np.pi, 20)
            ax.fill(cx_ + 0.05 * width * 0.1 + 0.006 * height * np.cos(theta),
                    cy_ + 0.006 * height * np.sin(theta),
                    color=POMPEIAN_CREAM, alpha=0.1)

        # Vesuvius in background
        mt_x = np.linspace(width * 0.6, width * 0.95, 150)
        mt_y = height * 0.7 + height * 0.15 * np.exp(-((mt_x - width * 0.8) ** 2) / (0.005 * width ** 2))
        ax.fill_between(mt_x, height * 0.65, mt_y, color=POMPEIAN_BROWN, alpha=0.1)

        return fig, ax


# ======================================================================
# 7. PompeiiArtGenerator
# ======================================================================

class PompeiiArtGenerator:
    def __init__(self):
        self.fresco = PompeiiFrescoStyle()
        self.arch = PompeiiArchitecture()
        self.life = PompeiiDailyLife()
        self.myth = PompeiiMythology()
        self.deco = PompeiiDecorations()
        self.comp = PompeiiComposition()

    def save(self, fig, name, dpi=150):
        """Save figure to PNG."""
        path = f"pompeii_{name}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight",
                    facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        return path

    def generate_gallery(self):
        """Generate full gallery of Pompeii art."""
        paths = []

        # 1 - Garden fresco
        fig, ax = _fig()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.fresco.pompeii_panel(ax, 0.05, 0.05, 0.9, 0.9, "garden")
        self.fresco.pompeii_border(ax, 1, 1, "red")
        paths.append(self.save(fig, "garden_fresco"))

        # 2 - Still life
        fig, ax = _fig()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.fresco.pompeii_panel(ax, 0.05, 0.05, 0.9, 0.9, "still_life")
        self.fresco.pompeii_border(ax, 1, 1, "black")
        paths.append(self.save(fig, "still_life"))

        # 3 - Roman temple
        fig, ax = _fig()
        self.arch.roman_temple(ax, 0.1, 0.05, 0.8, 0.8)
        paths.append(self.save(fig, "roman_temple"))

        # 4 - Domus cross-section
        fig, ax = _fig()
        self.arch.domus(ax, 0, 0, 1, 1)
        paths.append(self.save(fig, "domus"))

        # 5 - Street scene
        fig, ax = _fig()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.arch.street_scene(ax, 1, 1)
        paths.append(self.save(fig, "street_scene"))

        # 6 - Amphitheater
        fig, ax = _fig()
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.1)
        self.arch.amphitheater(ax, 0.5, 0.5, 0.4)
        paths.append(self.save(fig, "amphitheater"))

        # 7 - House of the Faun
        fig, ax = _fig()
        self.arch.house_of_faun(ax, 1, 1)
        paths.append(self.save(fig, "house_of_faun"))

        # 8 - Thermopolium
        fig, ax = _fig()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.life.thermopolium(ax, 0.05, 0.3, 0.9, 0.5)
        paths.append(self.save(fig, "thermopolium"))

        # 9 - Gladiator
        fig, ax = _fig()
        ax.set_xlim(-0.1, 0.3)
        ax.set_ylim(-0.05, 0.95)
        self.life.gladiator(ax, 0.1, 0.05, 0.8)
        paths.append(self.save(fig, "gladiator"))

        # 10 - Chariot
        fig, ax = _fig()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.life.chariot(ax, 0.05, 0.2, 0.9, 0.6)
        paths.append(self.save(fig, "chariot"))

        # 11 - Medusa gorgoneion
        fig, ax = _fig()
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.1)
        self.myth.medusa(ax, 0.5, 0.5, 0.35)
        paths.append(self.save(fig, "medusa"))

        # 12 - Theatrical mask
        fig, ax = _fig()
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.1)
        self.myth.theatrical_mask(ax, 0.5, 0.5, 0.35)
        paths.append(self.save(fig, "theatrical_mask"))

        # 13 - Winged victory
        fig, ax = _fig()
        ax.set_xlim(-0.1, 0.4)
        ax.set_ylim(-0.05, 0.95)
        self.myth.winged_victory(ax, 0.15, 0.05, 0.85)
        paths.append(self.save(fig, "winged_victory"))

        # 14 - Poseidon
        fig, ax = _fig()
        ax.set_xlim(-0.05, 0.35)
        ax.set_ylim(-0.05, 0.95)
        self.myth.poseidon(ax, 0.15, 0.05, 0.85)
        paths.append(self.save(fig, "poseidon"))

        # 15 - Meander and guilloche decoration
        fig, ax = _fig()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.deco.meander_pattern(ax, 0, 0.85, 1, 0.08, POMPEIAN_GOLD)
        self.deco.meander_pattern(ax, 0, 0.1, 1, 0.08, POMPEIAN_GOLD)
        self.deco.guilloche(ax, 0, 0.7, 1, 0.06, POMPEIAN_OCHRE)
        self.deco.guilloche(ax, 0, 0.25, 1, 0.06, POMPEIAN_OCHRE)
        self.deco.wave_pattern(ax, 0, 0.55, 1, 0.04)
        self.deco.candelabra(ax, 0.15, 0.3, 0.4)
        self.deco.candelabra(ax, 0.85, 0.3, 0.4)
        self.deco.garland(ax, 0.2, 0.45, 0.8, 0.45)
        paths.append(self.save(fig, "decorations"))

        # 16 - Sphinx and centaur
        fig, ax = _fig()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.deco.sphinx(ax, 0.1, 0.55, 0.4)
        self.deco.centaur(ax, 0.55, 0.55, 0.4)
        self.deco.garland(ax, 0.05, 0.9, 0.95, 0.9)
        paths.append(self.save(fig, "mythical_creatures"))

        # 17 - Vesuvius from sea
        fig, ax = self.comp.vesuvius_from_sea(1, 1)
        paths.append(self.save(fig, "vesuvius_from_sea"))

        # 18 - Last day
        fig, ax = self.comp.last_day(1, 1)
        paths.append(self.save(fig, "last_day"))

        # 19 - Villa of the Mysteries
        fig, ax = self.comp.villa_of_mysteries(1, 1)
        paths.append(self.save(fig, "villa_of_mysteries"))

        # 20 - Mosaic floor
        fig, ax = self.comp.mosaic_floor(1, 1)
        paths.append(self.save(fig, "mosaic_floor"))

        # 21 - Garden of Fugitives
        fig, ax = self.comp.garden_of_fugitives(1, 1)
        paths.append(self.save(fig, "garden_of_fugitives"))

        # 22 - Pompeii panorama
        fig, ax = self.comp.pompeii_panorama(1, 1)
        paths.append(self.save(fig, "pompeii_panorama"))

        # 23 - Architectural illusion
        fig, ax = _fig()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.fresco.pompeii_panel(ax, 0.05, 0.05, 0.9, 0.9, "architectural")
        self.fresco.pompeii_border(ax, 1, 1, "blue")
        paths.append(self.save(fig, "architectural_illusion"))

        # 24 - Mythological panel
        fig, ax = _fig()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.fresco.pompeii_panel(ax, 0.05, 0.05, 0.9, 0.9, "mythological")
        self.fresco.pompeii_border(ax, 1, 1, "black")
        paths.append(self.save(fig, "mythological_panel"))

        # 25 - Election notice
        fig, ax = _fig()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.life.election_notice(ax, 0.15, 0.2, 0.7, 0.6)
        self.deco.meander_pattern(ax, 0, 0.9, 1, 0.05, POMPEIAN_RED)
        self.deco.meander_pattern(ax, 0, 0.05, 1, 0.05, POMPEIAN_RED)
        paths.append(self.save(fig, "election_notice"))

        # 26 - Baker
        fig, ax = _fig()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.life.baker(ax, 0.05, 0.15, 0.9, 0.7)
        paths.append(self.save(fig, "baker"))

        # 27 - Fountain
        fig, ax = _fig()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.life.fountain(ax, 0.1, 0.1, 0.8, 0.8)
        paths.append(self.save(fig, "fountain"))

        # 28 - Venus
        fig, ax = _fig()
        ax.set_xlim(-0.05, 0.35)
        ax.set_ylim(-0.05, 0.95)
        self.myth.venus(ax, 0.15, 0.05, 0.85)
        paths.append(self.save(fig, "venus"))

        # 29 - Satyr
        fig, ax = _fig()
        ax.set_xlim(-0.05, 0.3)
        ax.set_ylim(-0.05, 0.95)
        self.myth.satyr(ax, 0.12, 0.05, 0.85)
        paths.append(self.save(fig, "satyr"))

        # 30 - Forum
        fig, ax = _fig()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        self.arch.forum(ax, 1, 1)
        paths.append(self.save(fig, "forum"))

        return paths


# ======================================================================
# Main
# ======================================================================

if __name__ == "__main__":
    import time

    output_dir = "pompeii_output"
    os.makedirs(output_dir, exist_ok=True)
    # save into subdirectory
    orig_cwd = os.getcwd()
    os.chdir(output_dir)

    print("=== Pompeii Polynomial Art Generator ===")
    print("")
    print("Initializing generator...")
    gen = PompeiiArtGenerator()

    start = time.time()
    print("Generating gallery of Pompeii art...")
    print("")

    paths = gen.generate_gallery()

    elapsed = time.time() - start
    print("")
    print("--- Generation Complete ---")
    print("")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    print(f"Total images generated: {len(paths)}")
    print("")
    print("Files saved to: {}/".format(output_dir))
    print("")
    for i, p in enumerate(paths, 1):
        print(f"  {i:2d}. {p}")
    print("")
    print("Done.")
