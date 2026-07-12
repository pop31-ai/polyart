"""PolyArt Transmission - Short demos of polynomial image transmission.

Encodes 2D flat and 3D volumetric images as polynomial lines,
transmits coefficients, and reconstructs. Generates animated GIFs
showing the transmission process.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
import time


BG_DARK = "#080808"
POMPEIAN_RED = "#8B0000"
POMPEIAN_OCHRE = "#C8A050"
POMPEIAN_GOLD = "#D4A843"
POMPEIAN_CREAM = "#F5F0E8"
POMPEIAN_BLUE = "#2E4A62"
POMPEIAN_GREEN = "#3A5F3A"
NEON_CYAN = "#00FFCC"
NEON_PINK = "#FF00AA"
NEON_YELLOW = "#FFEE00"
NEON_PURPLE = "#AA00FF"


# ===========================================================================
# 1. Polynomial Encoder - encodes shapes as poly coefficients
# ===========================================================================

class PolynomialEncoder:
    """Encode shapes as polynomial coefficients."""

    def encode_circle(self, cx, cy, r, n_points=60):
        """Encode circle as parametric polynomial."""
        t = np.linspace(0, 2 * np.pi, n_points)
        x = cx + r * np.cos(t)
        y = cy + r * np.sin(t)
        # fit polynomial to parametric curve
        t_norm = t / (2 * np.pi)
        coeffs_x = np.polyfit(t_norm, x, 8)
        coeffs_y = np.polyfit(t_norm, y, 8)
        return {"type": "circle", "cx": cx, "cy": cy, "r": r,
                "coeffs_x": coeffs_x.tolist(), "coeffs_y": coeffs_y.tolist(),
                "n_points": n_points}

    def encode_star(self, cx, cy, r_outer, r_inner, n_points=80):
        """Encode star as polynomial."""
        angles = np.linspace(0, 2 * np.pi, n_points, endpoint=False)
        radii = np.where(np.arange(n_points) % 2 == 0, r_outer, r_inner)
        # smooth with interpolation
        t_fine = np.linspace(0, 2 * np.pi, 500)
        angles_ext = np.append(angles, 2 * np.pi)
        radii_ext = np.append(radii, radii[0])
        radii_fine = np.interp(t_fine, angles_ext, radii_ext)
        x = cx + radii_fine * np.cos(t_fine)
        y = cy + radii_fine * np.sin(t_fine)
        t_norm = t_fine / (2 * np.pi)
        coeffs_x = np.polyfit(t_norm, x, 12)
        coeffs_y = np.polyfit(t_norm, y, 12)
        return {"type": "star", "cx": cx, "cy": cy, "r_outer": r_outer,
                "r_inner": r_inner, "coeffs_x": coeffs_x.tolist(),
                "coeffs_y": coeffs_y.tolist(), "n_points": 500}

    def encode_spiral(self, cx, cy, r_max, turns=3, n_points=200):
        """Encode spiral as polynomial."""
        t = np.linspace(0, turns * 2 * np.pi, n_points)
        r = r_max * t / (turns * 2 * np.pi)
        x = cx + r * np.cos(t)
        y = cy + r * np.sin(t)
        t_norm = t / (turns * 2 * np.pi)
        coeffs_x = np.polyfit(t_norm, x, 10)
        coeffs_y = np.polyfit(t_norm, y, 10)
        return {"type": "spiral", "cx": cx, "cy": cy, "r_max": r_max,
                "turns": turns, "coeffs_x": coeffs_x.tolist(),
                "coeffs_y": coeffs_y.tolist(), "n_points": n_points}

    def encode_wave(self, x_start, x_end, amplitude, frequency, n_points=200):
        """Encode wave as polynomial."""
        x = np.linspace(x_start, x_end, n_points)
        y = amplitude * np.sin(frequency * x)
        t_norm = np.linspace(0, 1, n_points)
        coeffs_x = np.polyfit(t_norm, x, 10)
        coeffs_y = np.polyfit(t_norm, y, 10)
        return {"type": "wave", "amplitude": amplitude,
                "frequency": frequency, "coeffs_x": coeffs_x.tolist(),
                "coeffs_y": coeffs_y.tolist(), "n_points": n_points}

    def encode_heart(self, cx, cy, size, n_points=200):
        """Encode heart shape as polynomial."""
        t = np.linspace(0, 2 * np.pi, n_points)
        x = size * 16 * np.sin(t) ** 3
        y = size * (13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))
        x = cx + x / 16
        y = cy + y / 16
        t_norm = t / (2 * np.pi)
        coeffs_x = np.polyfit(t_norm, x, 14)
        coeffs_y = np.polyfit(t_norm, y, 14)
        return {"type": "heart", "coeffs_x": coeffs_x.tolist(),
                "coeffs_y": coeffs_y.tolist(), "n_points": n_points}

    def encode_silhouette(self, points, degree=10):
        """Encode arbitrary silhouette as polynomial chain."""
        t = np.linspace(0, 1, len(points))
        t_fine = np.linspace(0, 1, 500)
        x_interp = np.interp(t_fine, t, points[:, 0])
        y_interp = np.interp(t_fine, t, points[:, 1])
        coeffs_x = np.polyfit(t_fine, x_interp, degree)
        coeffs_y = np.polyfit(t_fine, y_interp, degree)
        return {"type": "silhouette", "coeffs_x": coeffs_x.tolist(),
                "coeffs_y": coeffs_y.tolist(), "n_points": 500}

    def encode_3d_cube(self, cx, cy, cz, size, rotation=0):
        """Encode 3D cube edges as polynomial list."""
        s = size / 2
        # 8 corners of cube
        corners = np.array([
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s],
        ])
        # rotate around Y axis
        cos_r, sin_r = np.cos(rotation), np.sin(rotation)
        Ry = np.array([[cos_r, 0, sin_r], [0, 1, 0], [-sin_r, 0, cos_r]])
        corners_rot = corners @ Ry.T
        # project to 2D (simple perspective)
        fov = 3.0
        projected = []
        for c in corners_rot:
            z_proj = fov / (fov + c[2] + s)
            px = cx + c[0] * z_proj
            py = cy + c[1] * z_proj
            projected.append([px, py])
        # 12 edges
        edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
                 (0,4),(1,5),(2,6),(3,7)]
        polynomials = []
        for e in edges:
            p1 = np.array(projected[e[0]])
            p2 = np.array(projected[e[1]])
            t = np.linspace(0, 1, 100)
            x = p1[0] + (p2[0] - p1[0]) * t
            y = p1[1] + (p2[1] - p1[1]) * t
            coeffs_x = np.polyfit(t, x, 2)
            coeffs_y = np.polyfit(t, y, 2)
            polynomials.append({
                "coeffs_x": coeffs_x.tolist(), "coeffs_y": coeffs_y.tolist()
            })
        return polynomials

    def encode_3d_sphere(self, cx, cy, r, n_rings=8, n_points=60):
        """Encode 3D sphere as latitude/longitude polynomial lines."""
        polynomials = []
        # latitude rings
        for i in range(1, n_rings):
            phi = np.pi * i / n_rings
            ring_r = r * np.sin(phi)
            ring_y = cy + r * np.cos(phi)
            t = np.linspace(0, 2 * np.pi, n_points)
            x = cx + ring_r * np.cos(t)
            y = np.full_like(x, ring_y)
            coeffs_x = np.polyfit(t / (2 * np.pi), x, 8).tolist()
            coeffs_y = np.polyfit(t / (2 * np.pi), y, 8).tolist()
            polynomials.append({"coeffs_x": coeffs_x, "coeffs_y": coeffs_y,
                               "depth": np.cos(phi)})
        # longitude lines
        for i in range(n_rings):
            theta = np.pi * i / n_rings
            t = np.linspace(0, 2 * np.pi, n_points)
            x = cx + r * np.sin(t) * np.cos(theta)
            y = cy + r * np.cos(t)
            coeffs_x = np.polyfit(t / (2 * np.pi), x, 8).tolist()
            coeffs_y = np.polyfit(t / (2 * np.pi), y, 8).tolist()
            polynomials.append({"coeffs_x": coeffs_x, "coeffs_y": coeffs_y,
                               "depth": np.abs(np.sin(theta))})
        return polynomials

    def encode_3d_cone(self, cx, cy, radius, height, n_rings=6, n_points=60):
        """Encode 3D cone as polynomial lines."""
        polynomials = []
        for i in range(n_rings + 1):
            frac = i / n_rings
            ring_r = radius * (1 - frac)
            ring_y = cy + frac * height
            t = np.linspace(0, 2 * np.pi, n_points)
            x = cx + ring_r * np.cos(t)
            y = np.full_like(x, ring_y)
            coeffs_x = np.polyfit(t / (2 * np.pi), x, 8).tolist()
            coeffs_y = np.polyfit(t / (2 * np.pi), y, 8).tolist()
            polynomials.append({"coeffs_x": coeffs_x, "coeffs_y": coeffs_y,
                               "depth": 1 - frac})
        # vertical lines
        for i in range(8):
            theta = np.pi * i / 4
            t = np.linspace(0, 1, 100)
            x = cx + radius * (1 - t) * np.cos(theta)
            y = cy + t * height
            coeffs_x = np.polyfit(t, x, 3).tolist()
            coeffs_y = np.polyfit(t, y, 3).tolist()
            polynomials.append({"coeffs_x": coeffs_x, "coeffs_y": coeffs_y,
                               "depth": np.abs(np.sin(theta)) * 0.5})
        return polynomials

    def encode_3d_torus(self, cx, cy, R, r, n_rings=12, n_points=60):
        """Encode 3D torus as polynomial lines."""
        polynomials = []
        for i in range(n_rings):
            theta = 2 * np.pi * i / n_rings
            center_x = cx + R * np.cos(theta)
            t = np.linspace(0, 2 * np.pi, n_points)
            x = center_x + r * np.cos(t)
            y = np.full_like(t, cy + r * np.sin(0.0))
            coeffs_x = np.polyfit(t / (2 * np.pi), x, 8).tolist()
            coeffs_y = np.polyfit(t / (2 * np.pi), y, 8).tolist()
            polynomials.append({"coeffs_x": coeffs_x, "coeffs_y": coeffs_y,
                               "depth": np.cos(theta)})
        # meridian circles
        for i in range(6):
            phi = np.pi * i / 3
            t = np.linspace(0, 2 * np.pi, n_points)
            x = cx + (R + r * np.cos(phi)) * np.cos(t)
            y = cy + r * np.sin(phi) * np.ones_like(t)
            coeffs_x = np.polyfit(t / (2 * np.pi), x, 8).tolist()
            coeffs_y = np.polyfit(t / (2 * np.pi), y, 8).tolist()
            polynomials.append({"coeffs_x": coeffs_x, "coeffs_y": coeffs_y,
                               "depth": np.abs(np.sin(phi)) * 0.5})
        return polynomials


# ===========================================================================
# 2. Polynomial Decoder - reconstructs from coefficients
# ===========================================================================

class PolynomialDecoder:
    """Reconstruct shapes from polynomial coefficients."""

    def decode(self, poly_data, n_points=500):
        """Decode polynomial to x,y arrays."""
        coeffs_x = np.array(poly_data["coeffs_x"])
        coeffs_y = np.array(poly_data["coeffs_y"])
        t = np.linspace(0, 1, n_points)
        x = np.polyval(coeffs_x, t)
        y = np.polyval(coeffs_y, t)
        return x, y

    def decode_to_segment(self, poly_data, progress, n_points=200):
        """Decode up to a progress fraction (0 to 1)."""
        coeffs_x = np.array(poly_data["coeffs_x"])
        coeffs_y = np.array(poly_data["coeffs_y"])
        n = max(2, int(n_points * progress))
        t = np.linspace(0, progress, n)
        x = np.polyval(coeffs_x, t)
        y = np.polyval(coeffs_y, t)
        return x, y


# ===========================================================================
# 3. Transmission Animation Generator
# ===========================================================================

class TransmissionAnimator:
    """Generate animated GIFs of polynomial transmission."""

    def __init__(self):
        self.encoder = PolynomialEncoder()
        self.decoder = PolynomialDecoder()

    def _make_frame(self, fig, ax):
        """Convert figure to image array."""
        fig.canvas.draw()
        buf = fig.canvas.buffer_rgba()
        return np.asarray(buf)[:, :, :3]

    def transmit_flat_circle(self, n_frames=25, output="transmit_flat_circle.gif"):
        """2D: Circle transmitted as polynomial line."""
        frames = []
        enc = self.encoder.encode_circle(0.5, 0.5, 0.3)

        for i in range(n_frames):
            fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
            fig.set_facecolor(BG_DARK)
            ax.set_facecolor(BG_DARK)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")

            progress = (i + 1) / n_frames

            # source (faint)
            t_full = np.linspace(0, 2 * np.pi, 100)
            ax.plot(0.5 + 0.3 * np.cos(t_full), 0.5 + 0.3 * np.sin(t_full),
                    color=POMPEIAN_OCHRE, lw=0.5, alpha=0.1)

            # transmitted line (growing)
            x, y = self.decoder.decode_to_segment(enc, progress)
            ax.plot(x, y, color=NEON_CYAN, lw=1.5, alpha=0.8)

            # coefficient data stream
            n_coeffs = int(progress * len(enc["coeffs_x"]))
            data_x = 0.05
            data_y = 0.95
            for j in range(min(n_coeffs, 6)):
                ax.text(data_x, data_y - j * 0.04,
                        "cx[{}]={:.4f}".format(j, enc["coeffs_x"][j]),
                        fontsize=5, color=NEON_CYAN, alpha=0.6, fontfamily="monospace")

            # progress bar
            ax.plot([0.1, 0.1 + 0.8 * progress], [0.03, 0.03],
                    color=NEON_CYAN, lw=2, alpha=0.6)
            ax.plot([0.1, 0.9], [0.03, 0.03],
                    color=POMPEIAN_OCHRE, lw=0.5, alpha=0.2)

            # label
            ax.text(0.5, 0.98, "FLAT TRANSMISSION  |  Circle  |  {}%".format(int(progress * 100)),
                    fontsize=7, color=POMPEIAN_CREAM, alpha=0.5,
                    ha="center", va="top", fontfamily="serif")

            frames.append(self._make_frame(fig, ax))
            plt.close(fig)

        self._save_gif(frames, output, fps=8)
        return output

    def transmit_flat_star(self, n_frames=25, output="transmit_flat_star.gif"):
        """2D: Star transmitted as polynomial line."""
        frames = []
        enc = self.encoder.encode_star(0.5, 0.5, 0.35, 0.15)

        for i in range(n_frames):
            fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
            fig.set_facecolor(BG_DARK)
            ax.set_facecolor(BG_DARK)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            progress = (i + 1) / n_frames

            # source
            angles = np.linspace(0, 2 * np.pi, 10)
            radii = np.where(np.arange(10) % 2 == 0, 0.35, 0.15)
            sx = 0.5 + radii * np.cos(angles)
            sy = 0.5 + radii * np.sin(angles)
            sx = np.append(sx, sx[0])
            sy = np.append(sy, sy[0])
            ax.plot(sx, sy, color=POMPEIAN_OCHRE, lw=0.5, alpha=0.1)

            # transmitted
            x, y = self.decoder.decode_to_segment(enc, progress)
            ax.plot(x, y, color=NEON_PINK, lw=1.5, alpha=0.8)

            # data stream
            n_c = int(progress * 6)
            for j in range(min(n_c, 6)):
                ax.text(0.05, 0.95 - j * 0.04,
                        "cy[{}]={:.4f}".format(j, enc["coeffs_y"][j]),
                        fontsize=5, color=NEON_PINK, alpha=0.6, fontfamily="monospace")

            ax.plot([0.1, 0.1 + 0.8 * progress], [0.03, 0.03],
                    color=NEON_PINK, lw=2, alpha=0.6)
            ax.plot([0.1, 0.9], [0.03, 0.03],
                    color=POMPEIAN_OCHRE, lw=0.5, alpha=0.2)
            ax.text(0.5, 0.98, "FLAT TRANSMISSION  |  Star  |  {}%".format(int(progress * 100)),
                    fontsize=7, color=POMPEIAN_CREAM, alpha=0.5,
                    ha="center", va="top", fontfamily="serif")

            frames.append(self._make_frame(fig, ax))
            plt.close(fig)

        self._save_gif(frames, output, fps=8)
        return output

    def transmit_flat_heart(self, n_frames=25, output="transmit_flat_heart.gif"):
        """2D: Heart transmitted as polynomial."""
        frames = []
        enc = self.encoder.encode_heart(0.5, 0.5, 0.02)

        for i in range(n_frames):
            fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
            fig.set_facecolor(BG_DARK)
            ax.set_facecolor(BG_DARK)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            progress = (i + 1) / n_frames

            x, y = self.decoder.decode_to_segment(enc, progress)
            ax.plot(x, y, color=NEON_PINK, lw=1.8, alpha=0.8)

            n_c = int(progress * 8)
            for j in range(min(n_c, 6)):
                ax.text(0.05, 0.95 - j * 0.04,
                        "cx[{}]={:.6f}".format(j, enc["coeffs_x"][j]),
                        fontsize=5, color=NEON_PINK, alpha=0.6, fontfamily="monospace")

            ax.plot([0.1, 0.1 + 0.8 * progress], [0.03, 0.03],
                    color=NEON_PINK, lw=2, alpha=0.6)
            ax.plot([0.1, 0.9], [0.03, 0.03],
                    color=POMPEIAN_OCHRE, lw=0.5, alpha=0.2)
            ax.text(0.5, 0.98, "FLAT TRANSMISSION  |  Heart  |  {}%".format(int(progress * 100)),
                    fontsize=7, color=POMPEIAN_CREAM, alpha=0.5,
                    ha="center", va="top", fontfamily="serif")

            frames.append(self._make_frame(fig, ax))
            plt.close(fig)

        self._save_gif(frames, output, fps=8)
        return output

    def transmit_flat_spiral(self, n_frames=30, output="transmit_flat_spiral.gif"):
        """2D: Spiral transmitted as polynomial."""
        frames = []
        enc = self.encoder.encode_spiral(0.5, 0.5, 0.35, turns=3)

        for i in range(n_frames):
            fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
            fig.set_facecolor(BG_DARK)
            ax.set_facecolor(BG_DARK)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            progress = (i + 1) / n_frames

            x, y = self.decoder.decode_to_segment(enc, progress)
            ax.plot(x, y, color=NEON_YELLOW, lw=1.5, alpha=0.8)

            # trail glow
            if progress > 0.3:
                x_trail, y_trail = self.decoder.decode_to_segment(enc, progress - 0.3)
                ax.plot(x_trail, y_trail, color=NEON_YELLOW, lw=3, alpha=0.15)

            n_c = int(progress * 6)
            for j in range(min(n_c, 6)):
                ax.text(0.05, 0.95 - j * 0.04,
                        "cx[{}]={:.6f}".format(j, enc["coeffs_x"][j]),
                        fontsize=5, color=NEON_YELLOW, alpha=0.6, fontfamily="monospace")

            ax.plot([0.1, 0.1 + 0.8 * progress], [0.03, 0.03],
                    color=NEON_YELLOW, lw=2, alpha=0.6)
            ax.plot([0.1, 0.9], [0.03, 0.03],
                    color=POMPEIAN_OCHRE, lw=0.5, alpha=0.2)
            ax.text(0.5, 0.98, "FLAT TRANSMISSION  |  Spiral  |  {}%".format(int(progress * 100)),
                    fontsize=7, color=POMPEIAN_CREAM, alpha=0.5,
                    ha="center", va="top", fontfamily="serif")

            frames.append(self._make_frame(fig, ax))
            plt.close(fig)

        self._save_gif(frames, output, fps=8)
        return output

    def transmit_3d_cube(self, n_frames=30, output="transmit_3d_cube.gif"):
        """3D: Cube rotating, transmitted edge by edge."""
        frames = []
        enc = PolynomialEncoder()
        dec = PolynomialDecoder()

        for i in range(n_frames):
            fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
            fig.set_facecolor(BG_DARK)
            ax.set_facecolor(BG_DARK)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            progress = (i + 1) / n_frames
            rotation = progress * 2 * np.pi

            # encode rotated cube
            polys = enc.encode_3d_cube(0.5, 0.5, 0, 0.4, rotation)

            # draw edges with depth-based alpha
            n_edges = int(progress * len(polys))
            for j, p in enumerate(polys):
                if j >= n_edges:
                    break
                x, y = dec.decode(p, 100)
                depth = 0.3 + 0.5 * abs(np.sin(rotation + j * 0.5))
                ax.plot(x, y, color=NEON_PURPLE, lw=1.2, alpha=depth * 0.7)

            # data stream
            if n_edges > 0:
                p = polys[min(n_edges - 1, len(polys) - 1)]
                for k in range(min(4, len(p["coeffs_x"]))):
                    ax.text(0.05, 0.95 - k * 0.04,
                            "edge{}.cx[{}]={:.4f}".format(n_edges - 1, k, p["coeffs_x"][k]),
                            fontsize=4.5, color=NEON_PURPLE, alpha=0.6, fontfamily="monospace")

            ax.plot([0.1, 0.1 + 0.8 * progress], [0.03, 0.03],
                    color=NEON_PURPLE, lw=2, alpha=0.6)
            ax.plot([0.1, 0.9], [0.03, 0.03],
                    color=POMPEIAN_OCHRE, lw=0.5, alpha=0.2)
            ax.text(0.5, 0.98, "VOLUMETRIC TRANSMISSION  |  Cube 3D  |  {}%".format(int(progress * 100)),
                    fontsize=7, color=POMPEIAN_CREAM, alpha=0.5,
                    ha="center", va="top", fontfamily="serif")

            frames.append(self._make_frame(fig, ax))
            plt.close(fig)

        self._save_gif(frames, output, fps=8)
        return output

    def transmit_3d_sphere(self, n_frames=30, output="transmit_3d_sphere.gif"):
        """3D: Sphere transmitted as latitude/longitude polynomials."""
        frames = []
        enc = PolynomialEncoder()
        dec = PolynomialDecoder()

        for i in range(n_frames):
            fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
            fig.set_facecolor(BG_DARK)
            ax.set_facecolor(BG_DARK)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            progress = (i + 1) / n_frames

            polys = enc.encode_3d_sphere(0.5, 0.5, 0.3)
            n_lines = int(progress * len(polys))

            for j, p in enumerate(polys):
                if j >= n_lines:
                    break
                x, y = dec.decode(p, 200)
                depth = 0.2 + 0.6 * abs(p.get("depth", 0.5))
                ax.plot(x, y, color=NEON_CYAN, lw=1.0, alpha=depth * 0.6)

            # show outline
            t = np.linspace(0, 2 * np.pi, 100)
            ax.plot(0.5 + 0.3 * np.cos(t), 0.5 + 0.3 * np.sin(t),
                    color=POMPEIAN_OCHRE, lw=0.3, alpha=0.15)

            n_c = min(n_lines, len(polys))
            ax.text(0.05, 0.95, "lines transmitted: {}/{}".format(n_c, len(polys)),
                    fontsize=6, color=NEON_CYAN, alpha=0.6, fontfamily="monospace")
            ax.text(0.05, 0.91, "coeffs per line: {}".format(len(polys[0]["coeffs_x"])),
                    fontsize=6, color=NEON_CYAN, alpha=0.6, fontfamily="monospace")

            ax.plot([0.1, 0.1 + 0.8 * progress], [0.03, 0.03],
                    color=NEON_CYAN, lw=2, alpha=0.6)
            ax.plot([0.1, 0.9], [0.03, 0.03],
                    color=POMPEIAN_OCHRE, lw=0.5, alpha=0.2)
            ax.text(0.5, 0.98, "VOLUMETRIC TRANSMISSION  |  Sphere 3D  |  {}%".format(int(progress * 100)),
                    fontsize=7, color=POMPEIAN_CREAM, alpha=0.5,
                    ha="center", va="top", fontfamily="serif")

            frames.append(self._make_frame(fig, ax))
            plt.close(fig)

        self._save_gif(frames, output, fps=8)
        return output

    def transmit_3d_cone(self, n_frames=25, output="transmit_3d_cone.gif"):
        """3D: Cone transmitted ring by ring."""
        frames = []
        enc = PolynomialEncoder()
        dec = PolynomialDecoder()

        for i in range(n_frames):
            fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
            fig.set_facecolor(BG_DARK)
            ax.set_facecolor(BG_DARK)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            progress = (i + 1) / n_frames

            polys = enc.encode_3d_cone(0.5, 0.3, 0.25, 0.45)
            n_lines = int(progress * len(polys))

            for j, p in enumerate(polys):
                if j >= n_lines:
                    break
                x, y = dec.decode(p, 200)
                depth = 0.2 + 0.6 * abs(p.get("depth", 0.5))
                ax.plot(x, y,                         color=NEON_YELLOW if j < 7 else NEON_CYAN,
                        lw=1.0, alpha=depth * 0.6)

            ax.plot([0.1, 0.1 + 0.8 * progress], [0.03, 0.03],
                    color=NEON_YELLOW, lw=2, alpha=0.6)
            ax.plot([0.1, 0.9], [0.03, 0.03],
                    color=POMPEIAN_OCHRE, lw=0.5, alpha=0.2)
            ax.text(0.5, 0.98, "VOLUMETRIC TRANSMISSION  |  Cone 3D  |  {}%".format(int(progress * 100)),
                    fontsize=7, color=POMPEIAN_CREAM, alpha=0.5,
                    ha="center", va="top", fontfamily="serif")

            frames.append(self._make_frame(fig, ax))
            plt.close(fig)

        self._save_gif(frames, output, fps=8)
        return output

    def transmit_3d_torus(self, n_frames=30, output="transmit_3d_torus.gif"):
        """3D: Torus transmitted ring by ring."""
        frames = []
        enc = PolynomialEncoder()
        dec = PolynomialDecoder()

        for i in range(n_frames):
            fig, ax = plt.subplots(figsize=(6, 6), dpi=80)
            fig.set_facecolor(BG_DARK)
            ax.set_facecolor(BG_DARK)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            progress = (i + 1) / n_frames

            polys = enc.encode_3d_torus(0.5, 0.5, 0.2, 0.08)
            n_lines = int(progress * len(polys))

            for j, p in enumerate(polys):
                if j >= n_lines:
                    break
                x, y = dec.decode(p, 200)
                depth = 0.2 + 0.6 * abs(p.get("depth", 0.5))
                color = NEON_PINK if j < 12 else NEON_PURPLE
                ax.plot(x, y, color=color, lw=0.9, alpha=depth * 0.6)

            # outline
            t = np.linspace(0, 2 * np.pi, 100)
            ax.plot(0.5 + 0.28 * np.cos(t), 0.5 + 0.28 * np.sin(t),
                    color=POMPEIAN_OCHRE, lw=0.3, alpha=0.1)

            ax.plot([0.1, 0.1 + 0.8 * progress], [0.03, 0.03],
                    color=NEON_PINK, lw=2, alpha=0.6)
            ax.plot([0.1, 0.9], [0.03, 0.03],
                    color=POMPEIAN_OCHRE, lw=0.5, alpha=0.2)
            ax.text(0.5, 0.98, "VOLUMETRIC TRANSMISSION  |  Torus 3D  |  {}%".format(int(progress * 100)),
                    fontsize=7, color=POMPEIAN_CREAM, alpha=0.5,
                    ha="center", va="top", fontfamily="serif")

            frames.append(self._make_frame(fig, ax))
            plt.close(fig)

        self._save_gif(frames, output, fps=8)
        return output

    def _save_gif(self, frames, path, fps=8):
        """Save frames as GIF."""
        from PIL import Image
        pil_frames = [Image.fromarray(f) for f in frames]
        pil_frames[0].save(path, save_all=True, append_images=pil_frames[1:],
                           duration=int(1000 / fps), loop=0, optimize=True)
        size_kb = os.path.getsize(path) / 1024
        print("  {} ({:.0f} KB, {} frames)".format(path, size_kb, len(frames)))


# ===========================================================================
# 4. Comparison Image Generator
# ===========================================================================

class TransmissionComparison:
    """Generate comparison images showing original vs polynomial reconstruction."""

    def flat_comparison(self, output="transmit_comparison_flat.png"):
        """Side-by-side: original shapes and their polynomial reconstruction."""
        fig, axes = plt.subplots(2, 4, figsize=(16, 8), dpi=100)
        fig.set_facecolor(BG_DARK)
        for ax in axes.flat:
            ax.set_facecolor(BG_DARK)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")

        enc = PolynomialEncoder()
        dec = PolynomialDecoder()

        shapes = [
            ("Circle", enc.encode_circle(0.5, 0.5, 0.35), NEON_CYAN),
            ("Star", enc.encode_star(0.5, 0.5, 0.4, 0.15), NEON_PINK),
            ("Heart", enc.encode_heart(0.5, 0.5, 0.022), NEON_PINK),
            ("Spiral", enc.encode_spiral(0.5, 0.5, 0.35, 3), NEON_YELLOW),
        ]

        for col, (name, enc_data, color) in enumerate(shapes):
            # original
            axes[0, col].text(0.5, 0.95, "Original: {}".format(name),
                             fontsize=9, color=POMPEIAN_CREAM, alpha=0.6,
                             ha="center", va="top", fontfamily="serif")
            t = np.linspace(0, 2 * np.pi, 200)
            if name == "Circle":
                axes[0, col].plot(0.5 + 0.35 * np.cos(t), 0.5 + 0.35 * np.sin(t),
                                  color=POMPEIAN_OCHRE, lw=1.5, alpha=0.4)
            elif name == "Star":
                angles_s = np.linspace(0, 2 * np.pi, 10, endpoint=False)
                radii_s = np.where(np.arange(10) % 2 == 0, 0.4, 0.15)
                sx = np.append(0.5 + radii_s * np.cos(angles_s), 0.5 + 0.4 * np.cos(angles_s[0]))
                sy = np.append(0.5 + radii_s * np.sin(angles_s), 0.5 + 0.4 * np.sin(angles_s[0]))
                axes[0, col].plot(sx, sy, color=POMPEIAN_OCHRE, lw=1.5, alpha=0.4)
            elif name == "Heart":
                t_h = np.linspace(0, 2 * np.pi, 200)
                hx = 0.5 + 0.022 * 16 * np.sin(t_h) ** 3 / 16
                hy = 0.5 + 0.022 * (13 * np.cos(t_h) - 5 * np.cos(2 * t_h)) / 16
                axes[0, col].plot(hx, hy, color=POMPEIAN_OCHRE, lw=1.5, alpha=0.4)
            elif name == "Spiral":
                t_s = np.linspace(0, 3 * 2 * np.pi, 300)
                r_s = 0.35 * t_s / (3 * 2 * np.pi)
                axes[0, col].plot(0.5 + r_s * np.cos(t_s), 0.5 + r_s * np.sin(t_s),
                                  color=POMPEIAN_OCHRE, lw=1.5, alpha=0.4)

            # reconstructed
            axes[1, col].text(0.5, 0.95, "Reconstructed: {}".format(name),
                             fontsize=9, color=POMPEIAN_CREAM, alpha=0.6,
                             ha="center", va="top", fontfamily="serif")
            x, y = dec.decode(enc_data, 500)
            axes[1, col].plot(x, y, color=color, lw=2, alpha=0.8)
            # coefficient count
            n_c = len(enc_data["coeffs_x"]) + len(enc_data["coeffs_y"])
            axes[1, col].text(0.5, 0.05, "{} coefficients".format(n_c),
                             fontsize=7, color=color, alpha=0.5,
                             ha="center", fontfamily="monospace")

        fig.suptitle("POLYNOMIAL TRANSMISSION  |  Flat (2D) Shapes",
                     fontsize=14, color=POMPEIAN_CREAM, alpha=0.6, y=0.98,
                     fontfamily="serif")
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(output, dpi=100, bbox_inches="tight",
                    facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        print("  {}".format(output))
        return output

    def volumetric_comparison(self, output="transmit_comparison_3d.png"):
        """Side-by-side: 3D shapes transmitted as polynomial lines."""
        fig, axes = plt.subplots(2, 3, figsize=(14, 9), dpi=100)
        fig.set_facecolor(BG_DARK)
        for ax in axes.flat:
            ax.set_facecolor(BG_DARK)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")

        enc = PolynomialEncoder()
        dec = PolynomialDecoder()

        shapes_3d = [
            ("Cube", enc.encode_3d_cube(0.5, 0.5, 0, 0.4, 0.3), NEON_PURPLE),
            ("Sphere", enc.encode_3d_sphere(0.5, 0.5, 0.35), NEON_CYAN),
            ("Cone", enc.encode_3d_cone(0.5, 0.3, 0.25, 0.5), NEON_YELLOW),
        ]

        for col, (name, polys, color) in enumerate(shapes_3d):
            # wireframe
            axes[0, col].text(0.5, 0.95, "3D: {}".format(name),
                             fontsize=9, color=POMPEIAN_CREAM, alpha=0.6,
                             ha="center", va="top", fontfamily="serif")
            for p in polys:
                x, y = dec.decode(p, 200)
                depth = 0.2 + 0.6 * abs(p.get("depth", 0.5))
                axes[0, col].plot(x, y, color=POMPEIAN_OCHRE, lw=0.8, alpha=depth * 0.3)

            # polynomial reconstruction
            axes[1, col].text(0.5, 0.95, "Polynomial: {}".format(name),
                             fontsize=9, color=POMPEIAN_CREAM, alpha=0.6,
                             ha="center", va="top", fontfamily="serif")
            for p in polys:
                x, y = dec.decode(p, 200)
                depth = 0.2 + 0.6 * abs(p.get("depth", 0.5))
                axes[1, col].plot(x, y, color=color, lw=1.2, alpha=depth * 0.7)
            n_c = sum(len(p["coeffs_x"]) + len(p["coeffs_y"]) for p in polys)
            axes[1, col].text(0.5, 0.05, "{} polynomials, {} coefficients".format(len(polys), n_c),
                             fontsize=7, color=color, alpha=0.5,
                             ha="center", fontfamily="monospace")

        fig.suptitle("POLYNOMIAL TRANSMISSION  |  Volumetric (3D) Shapes",
                     fontsize=14, color=POMPEIAN_CREAM, alpha=0.6, y=0.98,
                     fontfamily="serif")
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(output, dpi=100, bbox_inches="tight",
                    facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        print("  {}".format(output))
        return output


# ===========================================================================
# Main
# ===========================================================================

if __name__ == "__main__":
    output_dir = "transmit_output"
    os.makedirs(output_dir, exist_ok=True)
    os.chdir(output_dir)

    print("=== PolyArt Polynomial Transmission ===")
    print("")
    print("Generating comparison images...")
    print("")

    comp = TransmissionComparison()
    comp.flat_comparison()
    comp.volumetric_comparison()

    print("")
    print("Generating animated GIFs...")
    print("")

    anim = TransmissionAnimator()

    print("FLAT (2D) transmissions:")
    anim.transmit_flat_circle()
    anim.transmit_flat_star()
    anim.transmit_flat_heart()
    anim.transmit_flat_spiral()

    print("")
    print("VOLUMETRIC (3D) transmissions:")
    anim.transmit_3d_cube()
    anim.transmit_3d_sphere()
    anim.transmit_3d_cone()
    anim.transmit_3d_torus()

    print("")
    print("Done!")
