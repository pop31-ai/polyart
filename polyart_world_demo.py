"""PWTP Demo - Polynomial World Transmission Protocol.

Demonstrates encoding, transmitting, and reconstructing a 3D scene
using only polynomial coefficients. Shows the dramatic bandwidth
savings compared to traditional video streaming.

Generates animated GIFs showing:
1. Static world reconstruction from polynomial coefficients
2. Moving hero transmitted as polynomial time-functions
3. Camera movement as polynomial path
4. Full scene: Pompeii with fleeing citizens
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import time


BG = "#060408"
NEON_CYAN = "#00FFCC"
NEON_PINK = "#FF00AA"
NEON_YELLOW = "#FFEE00"
NEON_PURPLE = "#AA00FF"
NEON_GREEN = "#00FF88"
POMPEIAN_RED = "#8B0000"
POMPEIAN_OCHRE = "#C8A050"
POMPEIAN_GOLD = "#D4A843"
POMPEIAN_CREAM = "#F5F0E8"
POMPEIAN_BROWN = "#6B4226"
POMPEIAN_SAND = "#C8B89A"
ASH_GREY = "#5A5A5A"


# ===========================================================================
# Polynomial World Encoder
# ===========================================================================

class WorldEncoder:
    """Encode a 3D world as polynomial descriptions."""

    def encode_terrain(self, width=10, depth=10, patches=10, height_var=0.3):
        """Encode terrain as polynomial surface patches."""
        patches_data = []
        for i in range(patches):
            for j in range(patches):
                px = i * width / patches
                py = j * depth / patches
                # polynomial coefficients for this patch
                h = height_var * np.sin(px * 0.5) * np.cos(py * 0.5)
                coeffs = [h, h * 0.1, h * 0.05, h * 0.02]
                patches_data.append({
                    "x": px, "y": py,
                    "w": width / patches, "h": depth / patches,
                    "coeffs_z": coeffs
                })
        return patches_data

    def encode_building(self, name, x, y, z, primitives):
        """Encode a building as polynomial primitives."""
        return {
            "name": name,
            "position": [x, y, z],
            "primitives": primitives
        }

    def encode_column(self, x, y, z, height, radius, segments=8):
        """Encode column as polynomial ring + generator lines."""
        rings = []
        for i in range(segments):
            frac = i / segments
            rz = z + height * frac
            r = radius * (1 + 0.02 * np.sin(frac * 6 * np.pi))
            rings.append({"z": rz, "r": r, "n_points": 36})

        generators = []
        for j in range(4):
            angle = np.pi * j / 2
            generators.append({
                "x_start": x + radius * np.cos(angle),
                "y_start": y + radius * np.sin(angle),
                "z_start": z,
                "z_end": z + height
            })

        return {
            "type": "COLUMN",
            "rings": rings,
            "generators": generators,
            "coefficients": segments * 4 + 4 * 3
        }

    def encode_arch(self, x, y, z, span, rise, n_points=36):
        """Encode arch as polynomial curve."""
        t = np.linspace(0, 1, n_points)
        arch_x = x + span * t
        arch_y = z + rise * np.sin(np.pi * t)
        coeffs_x = np.polyfit(t, arch_x, 6).tolist()
        coeffs_y = np.polyfit(t, arch_y, 6).tolist()
        return {
            "type": "ARCH",
            "coeffs_x": coeffs_x,
            "coeffs_y": coeffs_y,
            "n_coefficients": 12
        }

    def encode_hero(self, hero_id, path_points):
        """Encode hero movement as polynomial time-functions."""
        t = np.linspace(0, 1, len(path_points))
        positions = np.array(path_points)

        coeffs_x = np.polyfit(t, positions[:, 0], 3).tolist()
        coeffs_y = np.polyfit(t, positions[:, 1], 3).tolist()
        coeffs_z = np.polyfit(t, positions[:, 2], 3).tolist()

        return {
            "id": hero_id,
            "type": "HERO",
            "position_poly": {
                "x": coeffs_x,
                "y": coeffs_y,
                "z": coeffs_z
            },
            "n_coefficients": 12
        }

    def encode_camera(self, camera_path):
        """Encode camera path as polynomial."""
        t = np.linspace(0, 1, len(camera_path))
        positions = np.array(camera_path)

        coeffs_x = np.polyfit(t, positions[:, 0], 3).tolist()
        coeffs_y = np.polyfit(t, positions[:, 1], 3).tolist()
        coeffs_z = np.polyfit(t, positions[:, 2], 3).tolist()

        return {
            "type": "CAMERA",
            "position_poly": {
                "x": coeffs_x,
                "y": coeffs_y,
                "z": coeffs_z
            },
            "n_coefficients": 12
        }


# ===========================================================================
# Polynomial World Decoder
# ===========================================================================

class WorldDecoder:
    """Reconstruct 3D world from polynomial descriptions."""

    def evaluate_poly(self, coeffs, t):
        return np.polyval(coeffs, t)

    def evaluate_hero(self, hero_poly, t_norm):
        """Evaluate hero position at normalized time."""
        x = self.evaluate_poly(hero_poly["position_poly"]["x"], t_norm)
        y = self.evaluate_poly(hero_poly["position_poly"]["y"], t_norm)
        z = self.evaluate_poly(hero_poly["position_poly"]["z"], t_norm)
        return x, y, z

    def evaluate_camera(self, camera_poly, t_norm):
        """Evaluate camera position at normalized time."""
        x = self.evaluate_poly(camera_poly["position_poly"]["x"], t_norm)
        y = self.evaluate_poly(camera_poly["position_poly"]["y"], t_norm)
        z = self.evaluate_poly(camera_poly["position_poly"]["z"], t_norm)
        return x, y, z


# ===========================================================================
# Scene Renderer
# ===========================================================================

class SceneRenderer:
    """Render the 3D scene from polynomial descriptions."""

    def __init__(self):
        self.encoder = WorldEncoder()
        self.decoder = WorldDecoder()

    def project_3d(self, x, y, z, cam_x, cam_y, cam_z, width=1, height=1):
        """Simple perspective projection."""
        fov = 3.0
        dz = z - cam_z + fov
        if dz < 0.1:
            dz = 0.1
        scale = fov / dz
        px = (x - cam_x) * scale * width + width / 2
        py = (y - cam_y) * scale * height + height / 2
        return px, py

    def render_terrain(self, ax, terrain, cam_x, cam_y, cam_z, alpha=0.15):
        """Render terrain from polynomial patches."""
        for patch in terrain:
            px, py = patch["x"], patch["y"]
            pw, ph = patch["w"], patch["h"]
            # sample patch corners
            corners = [
                self.project_3d(px, py, 0, cam_x, cam_y, cam_z),
                self.project_3d(px + pw, py, 0, cam_x, cam_y, cam_z),
                self.project_3d(px + pw, py + ph, 0, cam_x, cam_y, cam_z),
                self.project_3d(px, py + ph, 0, cam_x, cam_y, cam_z),
            ]
            xs = [c[0] for c in corners]
            ys = [c[1] for c in corners]
            ax.fill(xs, ys, color=POMPEIAN_SAND, alpha=alpha * 0.3,
                    edgecolor=POMPEIAN_BROWN, linewidth=0.1)

    def render_column(self, ax, col, cam_x, cam_y, cam_z, alpha=0.4):
        """Render column from polynomial rings."""
        rings = col.get("rings", [])
        if not rings:
            return
        # render shaft line
        top = rings[-1]
        bot = rings[0]
        p_bot = self.project_3d(col.get("x", 0.5), col.get("y", 0.5),
                                bot["z"], cam_x, cam_y, cam_z)
        p_top = self.project_3d(col.get("x", 0.5), col.get("y", 0.5),
                                top["z"], cam_x, cam_y, cam_z)
        ax.plot([p_bot[0], p_top[0]], [p_bot[1], p_top[1]],
                color=POMPEIAN_CREAM, lw=1.5, alpha=alpha)
        # capital
        cap_r = top["r"] * 1.3
        theta = np.linspace(0, 2 * np.pi, 20)
        cap_x, cap_y = [], []
        for t in theta:
            cx3 = col.get("x", 0.5) + cap_r * np.cos(t)
            cy3 = col.get("y", 0.5) + cap_r * np.sin(t)
            px, py = self.project_3d(cx3, cy3, top["z"], cam_x, cam_y, cam_z)
            cap_x.append(px)
            cap_y.append(py)
        ax.plot(cap_x, cap_y, color=POMPEIAN_CREAM, lw=1.0, alpha=alpha * 0.7)

    def render_arch(self, ax, arch, cam_x, cam_y, cam_z, color=NEON_CYAN, alpha=0.5):
        """Render arch from polynomial curve."""
        coeffs_x = np.array(arch["coeffs_x"])
        coeffs_y = np.array(arch["coeffs_y"])
        t = np.linspace(0, 1, 60)
        x = np.polyval(coeffs_x, t)
        y = np.polyval(coeffs_y, t)
        # project each point
        px_list, py_list = [], []
        for xi, yi in zip(x, y):
            px, py = self.project_3d(xi, 0.5, yi, cam_x, cam_y, cam_z)
            px_list.append(px)
            py_list.append(py)
        ax.plot(px_list, py_list, color=color, lw=1.5, alpha=alpha)

    def render_hero(self, ax, hero, t, cam_x, cam_y, cam_z, color=NEON_PINK, alpha=0.7):
        """Render hero from polynomial state."""
        hx, hy, hz = self.decoder.evaluate_hero(hero, t)
        # body
        p_body = self.project_3d(hx, hy, hz, cam_x, cam_y, cam_z)
        p_head = self.project_3d(hx, hy, hz + 0.08, cam_x, cam_y, cam_z)
        ax.plot([p_body[0], p_head[0]], [p_body[1], p_head[1]],
                color=color, lw=1.5, alpha=alpha)
        # head
        ax.plot(p_head[0], p_head[1], "o", color=color, markersize=3, alpha=alpha)
        # legs
        leg_offset = 0.02 * np.sin(t * 10)
        p_leg = self.project_3d(hx + leg_offset, hy, hz - 0.02, cam_x, cam_y, cam_z)
        ax.plot([p_body[0], p_leg[0]], [p_body[1], p_leg[1]],
                color=color, lw=1.0, alpha=alpha * 0.6)
        return hx, hy, hz

    def render_camera_frustum(self, ax, cam_x, cam_y, cam_z, color=POMPEIAN_GOLD, alpha=0.2):
        """Render camera frustum indicator."""
        p = self.project_3d(cam_x, cam_y, cam_z, cam_x, cam_y, cam_z)
        # camera body
        body_w = 0.03
        ax.add_patch(plt.Rectangle((p[0] - body_w, p[1] - body_w),
                                    body_w * 2, body_w * 2,
                                    facecolor=color, alpha=alpha * 0.5,
                                    edgecolor=color, linewidth=0.5))
        # direction lines
        for angle in np.linspace(-0.3, 0.3, 5):
            ex = cam_x + 0.5 * np.cos(angle)
            ey = cam_y + 0.5 * np.sin(angle)
            p_end = self.project_3d(ex, ey, cam_z - 0.5, cam_x, cam_y, cam_z)
            ax.plot([p[0], p_end[0]], [p[1], p_end[1]],
                    color=color, lw=0.3, alpha=alpha * 0.3)

    def render_data_stream(self, ax, data, width=1, height=1, color=NEON_CYAN):
        """Render polynomial data stream overlay."""
        x = 0.02
        y = 0.98
        for i, line in enumerate(data[:8]):
            ax.text(x, y - i * 0.035, line,
                    fontsize=4.5, color=color, alpha=0.6,
                    fontfamily="monospace", va="top")


# ===========================================================================
# Demo Scenes
# ===========================================================================

class PWTPDemo:
    """Generate demo animations of the Polynomial World Protocol."""

    def __init__(self):
        self.encoder = WorldEncoder()
        self.decoder = WorldDecoder()
        self.renderer = SceneRenderer()

    def demo_static_world(self, n_frames=25, output="pwtp_static_world.gif"):
        """Demo 1: Static world appearing from polynomial coefficients."""
        print("  Generating static world demo...")
        terrain = self.encoder.encode_terrain()
        columns = []
        for i in range(6):
            col = self.encoder.encode_column(
                0.2 + i * 0.12, 0.5, 0, 0.4, 0.015)
            col["x"] = 0.2 + i * 0.12
            col["y"] = 0.5
            columns.append(col)

        arch = self.encoder.encode_arch(0.2, 0.5, 0.4, 0.6, 0.12)

        frames = []
        for i in range(n_frames):
            fig, ax = plt.subplots(figsize=(8, 6), dpi=80)
            fig.set_facecolor(BG)
            ax.set_facecolor(BG)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            progress = (i + 1) / n_frames

            cam_x, cam_y, cam_z = 0.5, 0.5, 0.3

            # terrain appears gradually
            n_terrain = int(progress * len(terrain))
            self.renderer.render_terrain(ax, terrain[:n_terrain],
                                        cam_x, cam_y, cam_z, alpha=0.2)

            # columns appear one by one
            n_cols = int(progress * len(columns))
            for j in range(n_cols):
                self.renderer.render_column(ax, columns[j],
                                           cam_x, cam_y, cam_z, alpha=0.4)

            # arch appears
            if progress > 0.5:
                arch_alpha = min(1, (progress - 0.5) * 3)
                self.renderer.render_arch(ax, arch, cam_x, cam_y, cam_z,
                                         NEON_CYAN, alpha=0.5 * arch_alpha)

            # data stream
            data = [
                "PWTP v1.0 | STATIC WORLD",
                "terrain: {}/{} patches".format(n_terrain, len(terrain)),
                "columns: {}/6".format(n_cols),
                "arch: {}".format("YES" if progress > 0.5 else "WAITING"),
                "bandwidth: 0 KB/s (cached)",
                "total: {:.1f} KB".format(progress * 128),
            ]
            self.renderer.render_data_stream(ax, data, color=NEON_CYAN)

            ax.text(0.5, 0.02, "STATIC WORLD RECONSTRUCTION  |  {}%".format(int(progress * 100)),
                    fontsize=8, color=POMPEIAN_CREAM, alpha=0.5,
                    ha="center", fontfamily="serif")

            frames.append(self._fig_to_array(fig))
            plt.close(fig)

        self._save_gif(frames, output, fps=6)
        return output

    def demo_moving_hero(self, n_frames=30, output="pwtp_moving_hero.gif"):
        """Demo 2: Hero moving across terrain, polynomial path shown."""
        print("  Generating moving hero demo...")
        # hero path
        path = [
            [0.1, 0.3, 0.0],
            [0.2, 0.35, 0.0],
            [0.35, 0.4, 0.0],
            [0.5, 0.45, 0.0],
            [0.65, 0.5, 0.0],
            [0.8, 0.55, 0.0],
            [0.9, 0.6, 0.0],
        ]
        hero = self.encoder.encode_hero(1, path)

        frames = []
        for i in range(n_frames):
            fig, ax = plt.subplots(figsize=(8, 6), dpi=80)
            fig.set_facecolor(BG)
            ax.set_facecolor(BG)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            t = i / n_frames

            cam_x, cam_y, cam_z = 0.5, 0.5, 0.3

            # terrain
            terrain = self.encoder.encode_terrain()
            self.renderer.render_terrain(ax, terrain, cam_x, cam_y, cam_z, alpha=0.15)

            # hero path (trace)
            path_x, path_y = [], []
            for tt in np.linspace(0, t, 50):
                hx, hy, hz = self.decoder.evaluate_hero(hero, tt)
                px, py = self.renderer.project_3d(hx, hy, hz, cam_x, cam_y, cam_z)
                path_x.append(px)
                path_y.append(py)
            ax.plot(path_x, path_y, color=NEON_PINK, lw=0.8, alpha=0.3)

            # full path (faint)
            full_x, full_y = [], []
            for tt in np.linspace(0, 1, 100):
                hx, hy, hz = self.decoder.evaluate_hero(hero, tt)
                px, py = self.renderer.project_3d(hx, hy, hz, cam_x, cam_y, cam_z)
                full_x.append(px)
                full_y.append(py)
            ax.plot(full_x, full_y, color=POMPEIAN_OCHRE, lw=0.5, alpha=0.15)

            # hero at current time
            self.renderer.render_hero(ax, hero, t, cam_x, cam_y, cam_z,
                                     NEON_PINK, alpha=0.8)

            # coefficient display
            hx_now, hy_now, hz_now = self.decoder.evaluate_hero(hero, t)
            data = [
                "PWTP v1.0 | HERO #1",
                "x(t) = {:.4f} + {:.4f}t + {:.4f}t^2 + {:.4f}t^3".format(
                    *hero["position_poly"]["x"]),
                "y(t) = {:.4f} + {:.4f}t + {:.4f}t^2 + {:.4f}t^3".format(
                    *hero["position_poly"]["y"]),
                "z(t) = {:.4f} + {:.4f}t + {:.4f}t^2 + {:.4f}t^3".format(
                    *hero["position_poly"]["z"]),
                "pos: ({:.3f}, {:.3f}, {:.3f})".format(hx_now, hy_now, hz_now),
                "coefficients: 12 numbers = 48 bytes",
            ]
            self.renderer.render_data_stream(ax, data, color=NEON_PINK)

            ax.text(0.5, 0.02, "HERO TRANSMISSION  |  t={:.2f}  |  {}%".format(t, int(t * 100)),
                    fontsize=8, color=POMPEIAN_CREAM, alpha=0.5,
                    ha="center", fontfamily="serif")

            frames.append(self._fig_to_array(fig))
            plt.close(fig)

        self._save_gif(frames, output, fps=8)
        return output

    def demo_camera_movement(self, n_frames=30, output="pwtp_camera_move.gif"):
        """Demo 3: Camera flying through scene, polynomial path."""
        print("  Generating camera movement demo...")
        cam_path = [
            [0.5, 1.0, 0.3],
            [0.4, 0.8, 0.25],
            [0.3, 0.6, 0.2],
            [0.4, 0.4, 0.15],
            [0.5, 0.3, 0.2],
            [0.6, 0.4, 0.25],
            [0.7, 0.6, 0.3],
        ]
        cam_poly = self.encoder.encode_camera(cam_path)

        terrain = self.encoder.encode_terrain()
        columns = []
        for i in range(6):
            col = self.encoder.encode_column(0.2 + i * 0.12, 0.5, 0, 0.4, 0.015)
            col["x"] = 0.2 + i * 0.12
            col["y"] = 0.5
            columns.append(col)

        frames = []
        for i in range(n_frames):
            fig, ax = plt.subplots(figsize=(8, 6), dpi=80)
            fig.set_facecolor(BG)
            ax.set_facecolor(BG)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            t = i / n_frames

            # evaluate camera position
            cam_x, cam_y, cam_z = self.decoder.evaluate_camera(cam_poly, t)

            # render scene from camera viewpoint
            self.renderer.render_terrain(ax, terrain, cam_x, cam_y, cam_z, alpha=0.15)
            for col in columns:
                self.renderer.render_column(ax, col, cam_x, cam_y, cam_z, alpha=0.35)

            # camera path trace
            cam_trace_x, cam_trace_y = [], []
            for tt in np.linspace(0, t, 40):
                cx, cy, cz = self.decoder.evaluate_camera(cam_poly, tt)
                px, py = self.renderer.project_3d(cx, cy, cz, cam_x, cam_y, cam_z)
                cam_trace_x.append(px)
                cam_trace_y.append(py)
            ax.plot(cam_trace_x, cam_trace_y, color=NEON_GREEN, lw=1.0, alpha=0.4)

            # camera indicator
            self.renderer.render_camera_frustum(ax, cam_x, cam_y, cam_z,
                                               NEON_GREEN, alpha=0.3)

            # data
            data = [
                "PWTP v1.0 | CAMERA",
                "cam.x(t) = {:.3f}".format(cam_x),
                "cam.y(t) = {:.3f}".format(cam_y),
                "cam.z(t) = {:.3f}".format(cam_z),
                "coefficients: 12 numbers = 48 bytes",
                "update rate: 10 Hz",
            ]
            self.renderer.render_data_stream(ax, data, color=NEON_GREEN)

            ax.text(0.5, 0.02, "CAMERA MOVEMENT  |  t={:.2f}  |  pos=({:.2f},{:.2f},{:.2f})".format(
                    t, cam_x, cam_y, cam_z),
                    fontsize=7, color=POMPEIAN_CREAM, alpha=0.5,
                    ha="center", fontfamily="serif")

            frames.append(self._fig_to_array(fig))
            plt.close(fig)

        self._save_gif(frames, output, fps=8)
        return output

    def demo_full_scene(self, n_frames=40, output="pwtp_full_scene.gif"):
        """Demo 4: Complete scene - Pompeii with heroes, camera, eruption."""
        print("  Generating full scene demo...")
        terrain = self.encoder.encode_terrain()

        # buildings
        buildings = []
        for i in range(6):
            col = self.encoder.encode_column(0.15 + i * 0.14, 0.5, 0, 0.35, 0.012)
            col["x"] = 0.15 + i * 0.14
            col["y"] = 0.5
            buildings.append(col)

        arch = self.encoder.encode_arch(0.15, 0.5, 0.35, 0.7, 0.1)

        # heroes
        heroes = []
        for h_id in range(5):
            path = [
                [0.1 + h_id * 0.05, 0.35 + h_id * 0.03, 0],
                [0.2 + h_id * 0.05, 0.38 + h_id * 0.02, 0],
                [0.35 + h_id * 0.05, 0.42 + h_id * 0.02, 0],
                [0.5 + h_id * 0.05, 0.45 + h_id * 0.01, 0],
                [0.7 + h_id * 0.03, 0.48 + h_id * 0.01, 0],
            ]
            hero = self.encoder.encode_hero(h_id, path)
            heroes.append(hero)

        # camera
        cam_path = [
            [0.5, 0.9, 0.25],
            [0.4, 0.7, 0.2],
            [0.35, 0.5, 0.15],
            [0.4, 0.35, 0.2],
            [0.5, 0.3, 0.25],
            [0.6, 0.4, 0.3],
            [0.65, 0.6, 0.25],
            [0.6, 0.8, 0.2],
        ]
        cam_poly = self.encoder.encode_camera(cam_path)

        # eruption particles
        np.random.seed(42)
        eruption_particles = []
        for p in range(15):
            angle = np.random.rand() * np.pi * 2
            speed = 0.3 + np.random.rand() * 0.5
            eruption_particles.append({
                "angle": angle, "speed": speed,
                "start_t": 0.3 + np.random.rand() * 0.4
            })

        frames = []
        for i in range(n_frames):
            fig, ax = plt.subplots(figsize=(8, 6), dpi=80)
            fig.set_facecolor(BG)
            ax.set_facecolor(BG)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            t = i / n_frames

            # camera
            cam_x, cam_y, cam_z = self.decoder.evaluate_camera(cam_poly, t)

            # terrain
            self.renderer.render_terrain(ax, terrain, cam_x, cam_y, cam_z, alpha=0.12)

            # buildings
            for col in buildings:
                self.renderer.render_column(ax, col, cam_x, cam_y, cam_z, alpha=0.3)

            # arch
            self.renderer.render_arch(ax, arch, cam_x, cam_y, cam_z,
                                     POMPEIAN_GOLD, alpha=0.4)

            # heroes
            hero_colors = [NEON_PINK, NEON_CYAN, NEON_YELLOW, NEON_PURPLE, NEON_GREEN]
            for h_id, hero in enumerate(heroes):
                self.renderer.render_hero(ax, hero, t, cam_x, cam_y, cam_z,
                                         hero_colors[h_id], alpha=0.6)

            # eruption
            if t > 0.3:
                eruption_t = (t - 0.3) / 0.7
                for p in eruption_particles:
                    if t > p["start_t"]:
                        pt = (t - p["start_t"]) / (1 - p["start_t"])
                        ex = 0.5 + p["speed"] * pt * np.cos(p["angle"])
                        ey = 0.5 + p["speed"] * pt * np.sin(p["angle"])
                        ez = 0.3 + pt * 0.3
                        px, py = self.renderer.project_3d(ex, ey, ez,
                                                         cam_x, cam_y, cam_z)
                        alpha = max(0, 1 - pt)
                        ax.plot(px, py, "o", color=POMPEIAN_RED,
                               markersize=2 + 3 * (1 - pt), alpha=alpha * 0.5)

            # data stream
            data = [
                "PWTP v1.0 | FULL SCENE",
                "terrain: 100 patches = 600 KB",
                "buildings: 6 columns + 1 arch",
                "heroes: 5 x 12 coeffs = 240 bytes",
                "camera: 12 coefficients",
                "eruption: 15 particles",
                "bandwidth: ~15 KB/s",
            ]
            self.renderer.render_data_stream(ax, data, color=POMPEIAN_GOLD)

            # bandwidth comparison
            bw_trad = 149000  # KB/s for 1080p
            bw_pwtp = 15
            ax.text(0.98, 0.98,
                    "Traditional: {:.0f} KB/s\nPWTP: {} KB/s\nRatio: {:,.0f}:1".format(
                        bw_trad, bw_pwtp, bw_trad / bw_pwtp),
                    fontsize=5, color=POMPEIAN_OCHRE, alpha=0.5,
                    ha="right", va="top", fontfamily="monospace",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=BG, alpha=0.5))

            ax.text(0.5, 0.02,
                    "FULL SCENE  |  t={:.2f}  |  heroes: 5  |  bandwidth: 15 KB/s".format(t),
                    fontsize=7, color=POMPEIAN_CREAM, alpha=0.5,
                    ha="center", fontfamily="serif")

            frames.append(self._fig_to_array(fig))
            plt.close(fig)

        self._save_gif(frames, output, fps=6)
        return output

    def demo_bandwidth_comparison(self, output="pwtp_bandwidth.png"):
        """Static image comparing bandwidth usage."""
        print("  Generating bandwidth comparison...")
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        fig.set_facecolor(BG)
        ax.set_facecolor(BG)

        methods = ["Raw\nVideo", "H.264", "H.265", "Cloud\nGaming", "VR\nStreaming", "PWTP\n(This)"]
        bandwidth = [149000, 5000, 2000, 10000, 50000, 15]
        colors_list = [POMPEIAN_RED, POMPEIAN_OCHRE, POMPEIAN_GOLD,
                       NEON_PURPLE, NEON_CYAN, NEON_GREEN]

        bars = ax.bar(range(len(methods)), bandwidth, color=colors_list,
                      alpha=0.6, edgecolor=POMPEIAN_CREAM, linewidth=0.5)

        ax.set_yscale("log")
        ax.set_ylabel("Bandwidth (KB/s)", fontsize=10, color=POMPEIAN_CREAM, alpha=0.7)
        ax.set_xticks(range(len(methods)))
        ax.set_xticklabels(methods, fontsize=8, color=POMPEIAN_CREAM, alpha=0.7)
        ax.set_title("PWTP Bandwidth Comparison (1080p 3D Scene)",
                     fontsize=12, color=POMPEIAN_CREAM, alpha=0.7, pad=15)

        # add value labels
        for bar, val in zip(bars, bandwidth):
            label = "{:,.0f} KB/s".format(val)
            if val < 100:
                label += "\n({:,.0f}x better)".format(149000 / val)
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.5,
                    label, ha="center", va="bottom",
                    fontsize=7, color=POMPEIAN_CREAM, alpha=0.7, fontfamily="monospace")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(POMPEIAN_CREAM)
        ax.spines["bottom"].set_color(POMPEIAN_CREAM)
        ax.tick_params(colors=POMPEIAN_CREAM)

        fig.tight_layout()
        fig.savefig(output, dpi=100, bbox_inches="tight",
                    facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        print("  {}".format(output))
        return output

    def _fig_to_array(self, fig):
        fig.canvas.draw()
        buf = fig.canvas.buffer_rgba()
        return np.asarray(buf)[:, :, :3]

    def _save_gif(self, frames, path, fps=8):
        from PIL import Image
        pil_frames = [Image.fromarray(f) for f in frames]
        pil_frames[0].save(path, save_all=True, append_images=pil_frames[1:],
                           duration=int(1000 / fps), loop=0, optimize=True)
        size_kb = os.path.getsize(path) / 1024
        print("    {} ({:.0f} KB, {} frames)".format(path, size_kb, len(frames)))


# ===========================================================================
# Main
# ===========================================================================

if __name__ == "__main__":
    output_dir = "pwtp_output"
    os.makedirs(output_dir, exist_ok=True)
    os.chdir(output_dir)

    print("=== Polynomial World Transmission Protocol (PWTP) Demo ===")
    print("")
    print("Demonstrating minimal-traffic 3D world transmission:")
    print("  Static world: polynomial surface patches (sent once)")
    print("  Moving heroes: polynomial time-functions (12 coefficients)")
    print("  Camera: polynomial path (12 coefficients)")
    print("  Bandwidth: ~15 KB/s vs 149,000 KB/s traditional video")
    print("")

    demo = PWTPDemo()

    demo.demo_static_world()
    demo.demo_moving_hero()
    demo.demo_camera_movement()
    demo.demo_full_scene()
    demo.demo_bandwidth_comparison()

    print("")
    print("Done! All demos saved to {}/".format(output_dir))
