"""Pompeii Eruption 3D GIF - Piranesi-style animated eruption.

Generates a dramatic animated GIF of Vesuvius erupting over Pompeii
with 3D perspective Piranesi architecture, fleeing citizens, and
volcanic effects. All in polynomial art style.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
import time


# ===========================================================================
# Color Palette
# ===========================================================================

BG_DARK = "#060408"
SKY_FIRE = "#1A0800"
ASH_GREY = "#4A4A4A"
DARK_GREY = "#2A2A2A"
VESUVIUS = "#3A2810"
VESUVIUS_DARK = "#1E1408"
POMPEIAN_RED = "#8B0000"
POMPEIAN_DARK_RED = "#5C0000"
POMPEIAN_OCHRE = "#C8A050"
POMPEIAN_GOLD = "#D4A843"
POMPEIAN_CREAM = "#F5F0E8"
POMPEIAN_BLUE = "#2E4A62"
POMPEIAN_GREEN = "#3A5F3A"
POMPEIAN_TERRACOTTA = "#C2703A"
POMPEIAN_BROWN = "#6B4226"
POMPEIAN_SAND = "#C8B89A"
LAVA_RED = "#CC2200"
LAVA_ORANGE = "#FF6600"
LAVA_YELLOW = "#FFAA00"
EMBER = "#FF4400"
FIRE_GLOW = "#FF8800"


def _polyval(xs, coeffs):
    return np.polyval(coeffs, xs)


# ===========================================================================
# 3D Perspective Helpers
# ===========================================================================

class Perspective3D:
    """Simple 3D to 2D projection for Piranesi-style scenes."""

    def __init__(self, vanishing_x=0.5, vanishing_y=0.65, depth_factor=0.7):
        self.vx = vanishing_x
        self.vy = vanishing_y
        self.df = depth_factor

    def project(self, x3, y3, z3, width=1, height=1):
        """Project 3D point to 2D. z3 goes from 0 (near) to 1 (far)."""
        scale = 1.0 - z3 * self.df
        px = self.vx * width + (x3 - self.vx) * scale * width
        py = self.vy * height + (y3 - self.vy) * scale * height
        return px, py

    def project_line(self, x1_3, y1_3, z1, x2_3, y2_3, z2, width=1, height=1):
        """Project a 3D line to 2D."""
        p1 = self.project(x1_3, y1_3, z1, width, height)
        p2 = self.project(x2_3, y2_3, z2, width, height)
        return p1, p2


# ===========================================================================
# Piranesi 3D Architecture
# ===========================================================================

class PiranesiArchitecture3D:
    """3D Piranesi-style ancient architecture with perspective."""

    def __init__(self):
        self.persp = Perspective3D(vanishing_x=0.5, vanishing_y=0.62, depth_factor=0.65)

    def column_3d(self, ax, x_base, y_base, z, height, radius=0.015, n_segments=8, width=1, height_fig=1, lw=0.2):
        """Draw a 3D column with perspective."""
        # base
        bx, by = self.persp.project(x_base, y_base, z, width, height_fig)
        # top
        tx, ty = self.persp.project(x_base, y_base + height, z, width, height_fig)
        # column shaft
        ax.plot([bx, tx], [by, ty], color=POMPEIAN_CREAM, lw=lw, alpha=0.4)
        # capital
        cap_w = radius * 2.5
        cx1, cy1 = self.persp.project(x_base - cap_w, y_base + height, z, width, height_fig)
        cx2, cy2 = self.persp.project(x_base + cap_w, y_base + height, z, width, height_fig)
        ax.plot([cx1, cx2], [cy1, cy2], color=POMPEIAN_CREAM, lw=lw * 0.8, alpha=0.35)
        # capital detail
        cx3, cy3 = self.persp.project(x_base - cap_w * 0.7, y_base + height * 0.96, z, width, height_fig)
        cx4, cy4 = self.persp.project(x_base + cap_w * 0.7, y_base + height * 0.96, z, width, height_fig)
        ax.plot([cx3, cx4], [cy3, cy4], color=POMPEIAN_CREAM, lw=lw * 0.5, alpha=0.3)
        # base plate
        bx1, by1 = self.persp.project(x_base - cap_w, y_base, z, width, height_fig)
        bx2, by2 = self.persp.project(x_base + cap_w, y_base, z, width, height_fig)
        ax.plot([bx1, bx2], [by1, by2], color=POMPEIAN_CREAM, lw=lw * 0.6, alpha=0.3)
        # fluting (vertical lines on shaft)
        for i in range(-1, 2, 2):
            fx1, fy1 = self.persp.project(x_base + i * radius * 0.5, y_base, z, width, height_fig)
            fx2, fy2 = self.persp.project(x_base + i * radius * 0.5, y_base + height, z, width, height_fig)
            ax.plot([fx1, fx2], [fy1, fy2], color=POMPEIAN_CREAM, lw=lw * 0.3, alpha=0.2)

    def arch_3d(self, ax, x1, y_base, z, span, height, width=1, height_fig=1, lw=0.2):
        """Draw a 3D arch with perspective."""
        # left column
        self.column_3d(ax, x1, y_base, z, height * 0.7, radius=0.012, width=width, height_fig=height_fig, lw=lw)
        # right column
        self.column_3d(ax, x1 + span, y_base, z, height * 0.7, radius=0.012, width=width, height_fig=height_fig, lw=lw)
        # arch curve
        arch_t = np.linspace(0, np.pi, 60)
        arch_xs = []
        arch_ys = []
        for t in arch_t:
            ax3d = x1 + span / 2 + span * 0.45 * np.cos(t)
            ay3d = y_base + height * 0.7 + height * 0.25 * np.sin(t)
            px, py = self.persp.project(ax3d, ay3d, z, width, height_fig)
            arch_xs.append(px)
            arch_ys.append(py)
        ax.plot(arch_xs, arch_ys, color=POMPEIAN_CREAM, lw=lw, alpha=0.35)
        # keystone
        kx, ky = self.persp.project(x1 + span / 2, y_base + height * 0.95, z, width, height_fig)
        ax.plot(kx, ky, "o", color=POMPEIAN_OCHRE, markersize=1.5, alpha=0.3)

    def entablature_3d(self, ax, x1, x2, y_base, z, height, width=1, height_fig=1, lw=0.2):
        """Draw entablature (horizontal beam) in 3D."""
        lx1, ly1 = self.persp.project(x1, y_base + height, z, width, height_fig)
        lx2, ly2 = self.persp.project(x2, y_base + height, z, width, height_fig)
        ax.plot([lx1, lx2], [ly1, ly2], color=POMPEIAN_CREAM, lw=lw, alpha=0.35)
        # frieze
        fx1, fy1 = self.persp.project(x1, y_base + height * 0.92, z, width, height_fig)
        fx2, fy2 = self.persp.project(x2, y_base + height * 0.92, z, width, height_fig)
        ax.plot([fx1, fx2], [fy1, fy2], color=POMPEIAN_CREAM, lw=lw * 0.6, alpha=0.25)
        # decorative triglyphs
        n_trig = max(2, int(abs(x2 - x1) * 15))
        for i in range(n_trig):
            tx = x1 + (x2 - x1) * (i + 0.5) / n_trig
            for dx in [-0.003, 0, 0.003]:
                tx1, ty1 = self.persp.project(tx + dx, y_base + height, z, width, height_fig)
                tx2, ty2 = self.persp.project(tx + dx, y_base + height * 0.92, z, width, height_fig)
                ax.plot([tx1, tx2], [ty1, ty2], color=POMPEIAN_CREAM, lw=lw * 0.2, alpha=0.2)

    def pediment_3d(self, ax, x1, x2, y_base, z, peak_height, width=1, height_fig=1, lw=0.25):
        """Draw a triangular pediment in 3D."""
        mid_x = (x1 + x2) / 2
        # left slope
        p1 = self.persp.project(x1, y_base, z, width, height_fig)
        p2 = self.persp.project(mid_x, y_base + peak_height, z, width, height_fig)
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=POMPEIAN_CREAM, lw=lw, alpha=0.4)
        # right slope
        p3 = self.persp.project(x2, y_base, z, width, height_fig)
        ax.plot([p2[0], p3[0]], [p2[1], p3[1]], color=POMPEIAN_CREAM, lw=lw, alpha=0.4)
        # base
        ax.plot([p1[0], p3[0]], [p1[1], p3[1]], color=POMPEIAN_CREAM, lw=lw * 0.8, alpha=0.35)
        # tympanum decoration (small circle)
        cx, cy = self.persp.project(mid_x, y_base + peak_height * 0.5, z, width, height_fig)
        r = abs(p2[0] - p1[0]) * 0.12
        theta = np.linspace(0, 2 * np.pi, 40)
        ax.plot(cx + r * np.cos(theta), cy + r * np.sin(theta),
                color=POMPEIAN_OCHRE, lw=lw * 0.5, alpha=0.25)

    def temple_3d(self, ax, x_center, y_base, z, width_t, height_t, n_cols=6, width=1, height_fig=1, lw=0.2):
        """Draw a full 3D temple with columns, entablature, pediment."""
        x1 = x_center - width_t / 2
        x2 = x_center + width_t / 2
        col_h = height_t * 0.55
        # podium
        pod1 = self.persp.project(x1 - width_t * 0.05, y_base, z, width, height_fig)
        pod2 = self.persp.project(x2 + width_t * 0.05, y_base + height_t * 0.06, z, width, height_fig)
        ax.add_patch(mpatches.Rectangle(
            (min(pod1[0], pod2[0]), min(pod1[1], pod2[1])),
            abs(pod2[0] - pod1[0]), abs(pod2[1] - pod1[1]),
            facecolor=POMPEIAN_SAND, edgecolor=POMPEIAN_CREAM,
            linewidth=lw * 0.5, alpha=0.15))
        # columns
        for i in range(n_cols):
            cx = x1 + width_t * 0.08 + i * (width_t * 0.84) / (n_cols - 1)
            self.column_3d(ax, cx, y_base + height_t * 0.06, z, col_h,
                          radius=0.01, width=width, height_fig=height_fig, lw=lw)
        # entablature
        self.entablature_3d(ax, x1, x2, y_base + height_t * 0.06, z, col_h,
                           width=width, height_fig=height_fig, lw=lw)
        # pediment
        self.pediment_3d(ax, x1, x2, y_base + height_t * 0.06 + col_h, z,
                        height_t * 0.15, width=width, height_fig=height_fig, lw=lw)

    def building_row_3d(self, ax, x_start, y_base, z, n_buildings, width=1, height_fig=1, lw=0.15):
        """Row of Roman buildings along a street in perspective."""
        building_w = 0.06
        for i in range(n_buildings):
            bx = x_start + i * building_w * 1.1
            bh = 0.08 + 0.04 * np.sin(i * 1.7)
            # building box
            corners = [
                self.persp.project(bx, y_base, z, width, height_fig),
                self.persp.project(bx + building_w, y_base, z, width, height_fig),
                self.persp.project(bx + building_w, y_base + bh, z, width, height_fig),
                self.persp.project(bx, y_base + bh, z, width, height_fig),
            ]
            # walls
            for j in range(4):
                p1 = corners[j]
                p2 = corners[(j + 1) % 4]
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                        color=POMPEIAN_CREAM, lw=lw, alpha=0.25)
            # roof
            roof_peak = self.persp.project(bx + building_w / 2, y_base + bh + 0.02, z, width, height_fig)
            ax.plot([corners[2][0], roof_peak[0]], [corners[2][1], roof_peak[1]],
                    color=POMPEIAN_TERRACOTTA, lw=lw, alpha=0.25)
            ax.plot([corners[3][0], roof_peak[0]], [corners[3][1], roof_peak[1]],
                    color=POMPEIAN_TERRACOTTA, lw=lw, alpha=0.25)
            # windows
            if bh > 0.08:
                for wy in [y_base + bh * 0.3, y_base + bh * 0.6]:
                    win = self.persp.project(bx + building_w * 0.35, wy, z, width, height_fig)
                    win2 = self.persp.project(bx + building_w * 0.65, wy + bh * 0.15, z, width, height_fig)
                    ax.add_patch(mpatches.Rectangle(
                        (min(win[0], win2[0]), min(win[1], win2[1])),
                        abs(win2[0] - win[0]), abs(win2[1] - win[1]),
                        facecolor=POMPEIAN_OCHRE, edgecolor="none", alpha=0.08))
            # door
            door = self.persp.project(bx + building_w * 0.35, y_base, z, width, height_fig)
            door2 = self.persp.project(bx + building_w * 0.65, y_base + bh * 0.45, z, width, height_fig)
            ax.add_patch(mpatches.Rectangle(
                (min(door[0], door2[0]), min(door[1], door2[1])),
                abs(door2[0] - door[0]), abs(door2[1] - door[1]),
                facecolor=POMPEIAN_DARK_RED, edgecolor="none", alpha=0.1))


# ===========================================================================
# Volcanic Effects
# ===========================================================================

class VolcanicEffects:
    """Animated volcanic eruption effects."""

    def draw_mountain(self, ax, width, height, intensity=0.0):
        """Draw Vesuvius mountain with eruption effects."""
        # mountain profile
        mt_x = np.linspace(width * 0.25, width * 0.75, 300)
        mt_y = height * 0.45 + height * 0.35 * np.exp(-((mt_x - width * 0.5) ** 2) / (0.008 * width ** 2))
        # add roughness
        mt_y += 0.01 * height * np.sin(mt_x * 40 / width)
        ax.fill_between(mt_x, height * 0.35, mt_y, color=VESUVIUS, alpha=0.3)
        ax.plot(mt_x, mt_y, color=POMPEIAN_BROWN, lw=0.3, alpha=0.45)
        # crater
        crater_l = width * 0.46
        crater_r = width * 0.54
        crater_y = height * 0.8
        ax.plot([crater_l, crater_r], [crater_y, crater_y],
                color=POMPEIAN_BROWN, lw=0.3, alpha=0.4)
        return crater_l, crater_r, crater_y

    def draw_eruption_plume(self, ax, crater_cx, crater_y, width, height, intensity, frame, n_layers=25):
        """Draw volcanic plume that grows with intensity."""
        for i in range(n_layers):
            layer_intensity = intensity * (1 - i / n_layers)
            if layer_intensity < 0.02:
                continue
            np.random.seed(i * 100 + frame % 5)
            # plume rises and spreads
            spread = 0.02 + i * 0.008 * intensity
            rise = i * 0.012 * intensity
            cx = crater_cx + 0.01 * width * np.sin(i * 0.7 + frame * 0.1)
            cy = crater_y + rise * height
            cr = (0.02 + i * 0.004) * width * intensity
            theta = np.linspace(0, 2 * np.pi, 50)
            # color: dark near base, lighter higher
            grey_val = 0.15 + 0.1 * (i / n_layers)
            ax.fill(cx + cr * np.cos(theta),
                    cy + cr * 0.5 * np.sin(theta),
                    color=(grey_val, grey_val * 0.9, grey_val * 0.8),
                    alpha=0.06 * layer_intensity)

    def draw_fire_glow(self, ax, crater_cx, crater_y, width, height, intensity, frame):
        """Draw fire/lava glow at crater."""
        if intensity < 0.2:
            return
        # inner glow
        for i in range(8):
            r = 0.015 * width * (1 + i * 0.3) * intensity
            theta = np.linspace(0, 2 * np.pi, 40)
            flicker = 1 + 0.3 * np.sin(frame * 0.5 + i)
            glow_alpha = 0.08 * intensity * flicker / (1 + i * 0.3)
            # color shifts from yellow to red
            t = i / 8
            color = (1, 0.5 * (1 - t), 0)  # orange to red
            ax.fill(crater_cx + r * np.cos(theta),
                    crater_y + r * 0.4 * np.sin(theta),
                    color=color, alpha=glow_alpha)

    def draw_lava_flows(self, ax, crater_cx, crater_y, width, height, intensity, frame):
        """Draw lava streams flowing down the mountain."""
        if intensity < 0.4:
            return
        n_flows = int(3 * intensity)
        for flow_i in range(n_flows):
            np.random.seed(flow_i * 77 + 7)
            start_side = 1 if flow_i % 2 == 0 else -1
            flow_t = np.linspace(0, 1, 80)
            # lava path follows mountain slope
            flow_x = crater_cx + start_side * 0.02 * width * flow_t + \
                     start_side * 0.08 * width * flow_t ** 1.5
            flow_y = crater_y - 0.15 * height * flow_t ** 1.2
            # animate flow progress
            progress = min(1.0, intensity * 1.2 + 0.3 * np.sin(frame * 0.2 + flow_i))
            visible = flow_t < progress
            # draw lava with glow
            for layer in range(3):
                offset = layer * 0.003 * width
                alpha_val = 0.3 * intensity / (1 + layer * 0.5)
                if layer == 0:
                    color = LAVA_YELLOW
                elif layer == 1:
                    color = LAVA_ORANGE
                else:
                    color = LAVA_RED
                ax.plot(flow_x[visible] + offset * np.sin(flow_t[visible] * 5),
                        flow_y[visible],
                        color=color, lw=0.3 - layer * 0.05, alpha=alpha_val)

    def draw_falling_ash(self, ax, width, height, intensity, frame, n_particles=80):
        """Draw falling ash and pumice."""
        np.random.seed(42)
        for _ in range(int(n_particles * intensity)):
            px = np.random.rand() * width
            # ash falls slowly
            py_base = np.random.rand() * height
            py = (py_base + frame * 0.005 * height) % height
            ash_size = 0.001 + np.random.rand() * 0.002
            ash_alpha = 0.15 * intensity * (0.5 + 0.5 * np.random.rand())
            ax.plot([px, px + 0.003 * width * np.random.randn()],
                    [py, py - 0.01 * height],
                    color=ASH_GREY, lw=0.1, alpha=ash_alpha)

    def draw_lightning(self, ax, width, height, intensity, frame):
        """Draw volcanic lightning."""
        if intensity < 0.6:
            return
        np.random.seed(frame * 3)
        if np.random.rand() > 0.3:  # only 70% of frames have lightning
            return
        # lightning bolt
        n_segments = 8
        bolt_x = [width * 0.45 + 0.05 * width * np.random.randn()]
        bolt_y = [height * 0.85]
        for seg in range(n_segments):
            bolt_x.append(bolt_x[-1] + 0.01 * width * np.random.randn())
            bolt_y.append(bolt_y[-1] + 0.03 * height)
        ax.plot(bolt_x, bolt_y, color=POMPEIAN_CREAM, lw=0.2, alpha=0.4)
        # glow
        mid_x = np.mean(bolt_x)
        mid_y = np.mean(bolt_y)
        theta = np.linspace(0, 2 * np.pi, 30)
        ax.fill(mid_x + 0.03 * width * np.cos(theta),
                mid_y + 0.03 * height * np.sin(theta),
                color=POMPEIAN_CREAM, alpha=0.03)


# ===========================================================================
# Fleeing Citizens
# ===========================================================================

class FleeingCitizens:
    """Small 3D-perspective figures fleeing the eruption."""

    def __init__(self):
        self.persp = Perspective3D(vanishing_x=0.5, vanishing_y=0.62, depth_factor=0.65)

    def draw_figure_3d(self, ax, x, y, z, height, lean=0, arm_up=False, width=1, height_fig=1, lw=0.15):
        """Draw a single figure with 3D perspective."""
        h = height * (1 - z * 0.5)
        # body
        bx, by = self.persp.project(x, y, z, width, height_fig)
        tx, ty = self.persp.project(x + lean * 0.02, y + h, z, width, height_fig)
        ax.plot([bx, tx], [by, ty], color=POMPEIAN_CREAM, lw=lw, alpha=0.25)
        # head
        head = self.persp.project(x + lean * 0.01, y + h + h * 0.15, z, width, height_fig)
        hr = max(1, 2 * (1 - z))
        ax.plot(head[0], head[1], "o", color=POMPEIAN_CREAM, markersize=hr, alpha=0.2)
        # legs (running pose)
        if lean != 0:
            leg1 = self.persp.project(x - lean * 0.015, y - h * 0.1, z, width, height_fig)
            leg2 = self.persp.project(x + lean * 0.025, y - h * 0.15, z, width, height_fig)
            ax.plot([bx, leg1[0]], [by, leg1[1]], color=POMPEIAN_CREAM, lw=lw * 0.7, alpha=0.2)
            ax.plot([bx, leg2[0]], [by, leg2[1]], color=POMPEIAN_CREAM, lw=lw * 0.7, alpha=0.2)
        # arms
        if arm_up:
            arm = self.persp.project(x + lean * 0.02, y + h * 0.7, z, width, height_fig)
            hand = self.persp.project(x + lean * 0.03, y + h * 1.1, z, width, height_fig)
            ax.plot([arm[0], hand[0]], [arm[1], hand[1]], color=POMPEIAN_CREAM, lw=lw * 0.7, alpha=0.2)

    def draw_crowd(self, ax, width, height, frame, intensity):
        """Draw a crowd of fleeing citizens."""
        n_people = int(12 * intensity)
        np.random.seed(123)
        for i in range(n_people):
            # spread along street
            x = 0.1 + np.random.rand() * 0.8
            y = 0.35 + np.random.rand() * 0.1
            z = 0.1 + np.random.rand() * 0.4
            lean = np.random.choice([-1, 1]) * (0.5 + 0.5 * np.random.rand())
            h = 0.04 + np.random.rand() * 0.03
            arm_up = np.random.rand() > 0.6
            self.draw_figure_3d(ax, x, y, z, h, lean, arm_up, width, height)


# ===========================================================================
# Scene Compositor
# ===========================================================================

class PompeiiEruption3D:
    """Compose the full 3D eruption scene."""

    def __init__(self):
        self.arch = PiranesiArchitecture3D()
        self.volcano = VolcanicEffects()
        self.citizens = FleeingCitizens()

    def render_frame(self, width, height, frame, total_frames, fps=12):
        """Render a single frame of the eruption animation."""
        fig, ax = plt.subplots(figsize=(12, 9), dpi=100)
        fig.set_facecolor(BG_DARK)
        ax.set_facecolor(BG_DARK)
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.axis("off")

        # eruption intensity ramps up over time
        t = frame / total_frames
        intensity = min(1.0, t * 1.5)  # reaches full at 67% of animation
        # slight pulsing
        pulse = 1 + 0.1 * np.sin(frame * 0.3)
        intensity *= pulse

        # === SKY ===
        # dark sky with fire glow that intensifies
        sky_r = 0.04 + 0.08 * intensity
        sky_g = 0.02 + 0.02 * intensity
        sky_b = 0.06 + 0.01 * intensity
        ax.add_patch(mpatches.Rectangle((0, 0), width, height,
                                        facecolor=(sky_r, sky_g, sky_b), alpha=0.5))
        # fire glow in sky near crater
        if intensity > 0.3:
            glow_theta = np.linspace(0, 2 * np.pi, 60)
            glow_r = 0.15 * width * intensity
            glow_cx = width * 0.5
            glow_cy = height * 0.78
            ax.fill(glow_cx + glow_r * np.cos(glow_theta),
                    glow_cy + glow_r * 0.5 * np.sin(glow_theta),
                    color=(1, 0.4, 0), alpha=0.04 * intensity)

        # === GROUND ===
        ground_xs = np.linspace(0, width, 200)
        ground_ys = height * 0.35 + 0.005 * height * np.sin(ground_xs * 15 / width)
        ax.fill_between(ground_xs, 0, ground_ys, color=POMPEIAN_SAND, alpha=0.12)
        ax.plot(ground_xs, ground_ys, color=POMPEIAN_BROWN, lw=0.15, alpha=0.25)

        # === VOLCANO ===
        crater_l, crater_r, crater_y = self.volcano.draw_mountain(ax, width, height, intensity)
        crater_cx = (crater_l + crater_r) / 2

        # === ERUPTION EFFECTS ===
        self.volcano.draw_eruption_plume(ax, crater_cx, crater_y, width, height, intensity, frame)
        self.volcano.draw_fire_glow(ax, crater_cx, crater_y, width, height, intensity, frame)
        self.volcano.draw_lava_flows(ax, crater_cx, crater_y, width, height, intensity, frame)

        # === ARCHITECTURE (back to front) ===
        # Far buildings (z=0.7)
        self.arch.building_row_3d(ax, 0.05, 0.36, 0.7, 12, width, height, lw=0.1)
        self.arch.building_row_3d(ax, 0.55, 0.36, 0.65, 10, width, height, lw=0.12)

        # Temple in mid-ground (z=0.5)
        self.arch.temple_3d(ax, 0.5, 0.33, 0.5, 0.2, 0.18, n_cols=6, width=width, height_fig=height, lw=0.15)

        # Colonnade left (z=0.35)
        for i in range(5):
            cx = 0.02 + i * 0.06
            self.arch.column_3d(ax, cx, 0.33, 0.35, 0.15, radius=0.008, width=width, height_fig=height, lw=0.15)
        # entablature
        self.arch.entablature_3d(ax, 0.02, 0.32, 0.33, 0.35, 0.15, width, height, lw=0.12)

        # Colonnade right (z=0.3)
        for i in range(5):
            cx = 0.68 + i * 0.06
            self.arch.column_3d(ax, cx, 0.33, 0.3, 0.15, radius=0.008, width=width, height_fig=height, lw=0.15)
        self.arch.entablature_3d(ax, 0.68, 0.98, 0.33, 0.3, 0.15, width, height, lw=0.12)

        # Foreground arch (z=0.15)
        self.arch.arch_3d(ax, 0.3, 0.2, 0.15, 0.4, 0.2, width, height, lw=0.2)

        # Large foreground columns (z=0.05)
        self.arch.column_3d(ax, 0.08, 0.15, 0.05, 0.35, radius=0.018, width=width, height_fig=height, lw=0.25)
        self.arch.column_3d(ax, 0.92, 0.15, 0.05, 0.35, radius=0.018, width=width, height_fig=height, lw=0.25)

        # === FLEEING CITIZENS ===
        self.citizens.draw_crowd(ax, width, height, frame, intensity)

        # === ASH AND EMBER ===
        self.volcano.draw_falling_ash(ax, width, height, intensity, frame)

        # === LIGHTNING ===
        self.volcano.draw_lightning(ax, width, height, intensity, frame)

        # === VIGNETTE ===
        # dark edges for dramatic effect
        vignette = plt.Rectangle((0, 0), width, height, facecolor="black", alpha=0.3)
        ax.add_patch(vignette)
        # lighter center
        center_theta = np.linspace(0, 2 * np.pi, 100)
        ax.fill(width * 0.5 + width * 0.6 * np.cos(center_theta),
                height * 0.5 + height * 0.6 * np.sin(center_theta),
                facecolor="black", alpha=0.25)

        # === FRAME COUNTER ===
        ax.text(width * 0.02, height * 0.02,
                "VESUVIUS 79 AD  |  Frame {}/{}".format(frame + 1, total_frames),
                fontsize=5, color=POMPEIAN_OCHRE, alpha=0.3, fontfamily="serif")

        return fig


# ===========================================================================
# GIF Generator
# ===========================================================================

class PompeiiEruptionGIF:
    """Generate the animated GIF."""

    def __init__(self, width=1.0, height=0.75, n_frames=30, fps=8):
        self.width = width
        self.height = height
        self.n_frames = n_frames
        self.fps = fps
        self.scene = PompeiiEruption3D()

    def generate(self, output_path="pompeii_eruption_3d.gif"):
        """Generate the animated GIF."""
        frames = []
        print("Rendering {} frames...".format(self.n_frames))
        start = time.time()

        for i in range(self.n_frames):
            if i % 5 == 0:
                print("  Frame {}/{}...".format(i + 1, self.n_frames))
            fig = self.scene.render_frame(self.width, self.height, i, self.n_frames, self.fps)
            fig.canvas.draw()
            # convert to image array
            buf = fig.canvas.buffer_rgba()
            img = np.asarray(buf)[:, :, :3]  # drop alpha
            frames.append(img)
            plt.close(fig)

        elapsed = time.time() - start
        print("Rendering done in {:.1f}s".format(elapsed))

        # save as GIF
        print("Saving GIF...")
        from PIL import Image
        pil_frames = [Image.fromarray(f) for f in frames]
        pil_frames[0].save(
            output_path,
            save_all=True,
            append_images=pil_frames[1:],
            duration=int(1000 / self.fps),
            loop=0,
            optimize=True,
        )
        file_size = os.path.getsize(output_path)
        print("Saved: {} ({:.1f} KB, {} frames, {} fps)".format(
            output_path, file_size / 1024, self.n_frames, self.fps))

        return output_path


# ===========================================================================
# Main
# ===========================================================================

if __name__ == "__main__":
    output_dir = "pompeii_output"
    os.makedirs(output_dir, exist_ok=True)

    print("=== Pompeii Eruption 3D Animated GIF ===")
    print("")
    print("Scene elements:")
    print("  - Piranesi-style 3D architecture with perspective")
    print("  - Columns, arches, temples, colonnades")
    print("  - Vesuvius erupting with plume, lava, fire")
    print("  - Fleeing citizens in perspective")
    print("  - Falling ash, volcanic lightning")
    print("  - Dramatic lighting and vignette")
    print("")

    gif = PompeiiEruptionGIF(width=1.0, height=0.75, n_frames=30, fps=8)
    output_path = os.path.join(output_dir, "pompeii_eruption_3d.gif")
    gif.generate(output_path)

    print("")
    print("Done! Output: {}".format(output_path))
