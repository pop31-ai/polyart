import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import warnings, time
warnings.filterwarnings("ignore")

PHI = (1 + np.sqrt(5)) / 2
GOLD = "#c8a040"
STEM = "#2a6a1a"
STEM2 = "#3a8a2a"
LEAF = "#1e5a12"


# ============================================================
#  FLOWER CURVES v2 - Original + 12 new flowers
# ============================================================

class FlowerCurves:

    @staticmethod
    def rose(ax, cx=0, cy=0, s=1.0, petals=5, color="#c83060",
             ec="#801830", lw=0.6, al=0.9):
        for p in range(petals):
            ang = p * 2 * np.pi / petals
            th = np.linspace(0, 2 * np.pi, 120)
            r = s * (0.3 + 0.55 * (1 + np.cos(petals * th)) / 2)
            px = cx + r * np.cos(th + ang)
            py = cy + r * np.sin(th + ang)
            ax.fill(px, py, color=color, alpha=al * (0.6 + 0.4 * np.random.rand()),
                    edgecolor=ec, linewidth=lw * 0.5)
        for p in range(petals):
            ang = p * 2 * np.pi / petals + np.pi / petals
            th = np.linspace(0, 2 * np.pi, 100)
            r = s * (0.15 + 0.3 * (1 + np.cos(petals * th)) / 2)
            px = cx + r * np.cos(th + ang)
            py = cy + r * np.sin(th + ang)
            ax.fill(px, py, color=color, alpha=al * 0.5, edgecolor=ec, linewidth=lw * 0.3)
        spiral_th = np.linspace(0, 4 * np.pi, 200)
        spiral_r = s * 0.25 * (1 - spiral_th / (4 * np.pi))
        sx = cx + spiral_r * np.cos(spiral_th)
        sy = cy + spiral_r * np.sin(spiral_th)
        ax.plot(sx, sy, color=GOLD, linewidth=lw * 0.8, alpha=al * 0.7)
        circ = plt.Circle((cx, cy), s * 0.08, color=GOLD, alpha=al * 0.9)
        ax.add_patch(circ)

    @staticmethod
    def lily(ax, cx=0, cy=0, s=1.0, color="#f0e0c0",
             ec="#c0a060", lw=0.6, al=0.9):
        for p in range(6):
            ang = p * np.pi / 3
            th = np.linspace(-np.pi / 2, np.pi / 2, 80)
            r = s * 0.6 * (1 + 0.3 * np.cos(2 * th))
            px = cx + r * np.sin(th) * np.cos(ang) - s * 0.15 * np.sin(ang) * (1 - np.cos(th))
            py = cy + r * np.sin(th) * np.sin(ang) + s * 0.15 * np.cos(ang) * (1 - np.cos(th))
            ax.fill(px, py, color=color, alpha=al, edgecolor=ec, linewidth=lw * 0.5)
        for p in range(6):
            ang = p * np.pi / 3
            th = np.linspace(0, np.pi * 0.6, 40)
            st = s * 0.55
            sx = cx + st * th / np.pi * np.cos(ang) * (1 + 0.4 * np.sin(3 * th))
            sy = cy + st * th / np.pi * np.sin(ang) * (1 + 0.4 * np.sin(3 * th))
            ax.plot(sx, sy, color="#b09030", linewidth=lw * 0.5, alpha=al * 0.6)
        circ = plt.Circle((cx, cy), s * 0.12, color="#f0d870", alpha=al * 0.8)
        ax.add_patch(circ)

    @staticmethod
    def daisy(ax, cx=0, cy=0, s=1.0, petals=12, color="#ffffff",
              ec="#d0d0d0", lw=0.5, al=0.9):
        for p in range(petals):
            ang = p * 2 * np.pi / petals
            th = np.linspace(0, 2 * np.pi, 60)
            lx = s * 0.55
            pw = s * 0.08
            px = cx + (lx * (1 + np.cos(th)) / 2) * np.cos(ang) + pw * np.sin(th) * np.cos(ang + np.pi / 2)
            py = cy + (lx * (1 + np.cos(th)) / 2) * np.sin(ang) + pw * np.sin(th) * np.sin(ang + np.pi / 2)
            ax.fill(px, py, color=color, alpha=al * (0.8 + 0.2 * (p % 2)),
                    edgecolor=ec, linewidth=lw * 0.3)
        for r_val in [0.2, 0.14, 0.08]:
            circ = plt.Circle((cx, cy), s * r_val, color="#e8c020", alpha=al * 0.85)
            ax.add_patch(circ)
        for i in range(20):
            a = np.random.uniform(0, 2 * np.pi)
            r = np.random.uniform(0, s * 0.18)
            dx = plt.Circle((cx + r * np.cos(a), cy + r * np.sin(a)),
                            s * 0.015, color="#805010", alpha=al * 0.6)
            ax.add_patch(dx)

    @staticmethod
    def tulip(ax, cx=0, cy=0, s=1.0, color="#d03060",
              ec="#901840", lw=0.6, al=0.9):
        for side in [-1, 1]:
            th = np.linspace(0, np.pi, 80)
            px = cx + side * s * 0.3 * np.sin(th) * (1 + 0.4 * np.cos(th))
            py = cy + s * 0.45 * np.cos(th * 0.8) + s * 0.1 * np.sin(th)
            ax.fill(px, py, color=color, alpha=al, edgecolor=ec, linewidth=lw * 0.4)
        th = np.linspace(0, np.pi, 80)
        px = cx + s * 0.08 * np.sin(2 * th)
        py = cy + s * 0.5 * np.cos(th * 0.7)
        ax.fill(px, py, color=color, alpha=al * 0.95, edgecolor=ec, linewidth=lw * 0.3)
        stem_th = np.linspace(0, 1, 40)
        sx = cx + s * 0.1 * np.sin(np.pi * stem_th * 0.5)
        sy = np.linspace(cy - s * 0.1, cy - s * 1.2, 40)
        ax.plot(sx, sy, color=STEM, linewidth=lw * 1.5, alpha=al)
        leaf_th = np.linspace(0, 1, 40)
        lx = cx + s * 0.1 + s * 0.35 * leaf_th * (1 - leaf_th * 0.6)
        ly = cy - s * 0.6 - s * 0.5 * leaf_th ** 2 + s * 0.15 * np.sin(np.pi * leaf_th)
        ax.fill(lx, ly, color=LEAF, alpha=al * 0.8, edgecolor=STEM, linewidth=lw * 0.3)

    @staticmethod
    def sunflower(ax, cx=0, cy=0, s=1.0, color="#f0c810",
                  ec="#a08008", lw=0.5, al=0.9):
        for p in range(24):
            ang = p * 2 * np.pi / 24
            th = np.linspace(0, 2 * np.pi, 60)
            lx = s * 0.7
            pw = s * 0.06
            px = cx + (lx * (1 + np.cos(th)) / 2) * np.cos(ang) + pw * np.sin(th) * np.cos(ang + np.pi / 2)
            py = cy + (lx * (1 + np.cos(th)) / 2) * np.sin(ang) + pw * np.sin(th) * np.sin(ang + np.pi / 2)
            ax.fill(px, py, color=color, alpha=al * (0.85 + 0.15 * (p % 2)),
                    edgecolor=ec, linewidth=lw * 0.3)
        n_pts = 150
        for i in range(n_pts):
            r = s * 0.28 * np.sqrt(i / n_pts)
            theta = 2 * np.pi * i / PHI ** 2
            dx = plt.Circle((cx + r * np.cos(theta), cy + r * np.sin(theta)),
                            s * 0.02, color="#503010", alpha=al * 0.7)
            ax.add_patch(dx)
        circ = plt.Circle((cx, cy), s * 0.28, color="#403010", alpha=al * 0.3)
        ax.add_patch(circ)

    @staticmethod
    def orchid(ax, cx=0, cy=0, s=1.0, color="#c070d0",
               ec="#8040a0", lw=0.6, al=0.9):
        for p in range(3):
            ang = p * 2 * np.pi / 3 + np.pi / 6
            th = np.linspace(0, 2 * np.pi, 80)
            r = s * 0.4 * (1 + 0.3 * np.cos(3 * th))
            px = cx + r * np.cos(th) * np.cos(ang)
            py = cy + r * np.sin(th) * np.sin(ang)
            ax.fill(px, py, color=color, alpha=al * 0.8, edgecolor=ec, linewidth=lw * 0.4)
        lip_th = np.linspace(0, 2 * np.pi, 100)
        lr = s * 0.25 * (1 + 0.6 * np.cos(lip_th) + 0.3 * np.cos(2 * lip_th))
        lpx = cx + lr * np.cos(lip_th)
        lpy = cy - s * 0.1 + lr * np.sin(lip_th) * 0.7
        ax.fill(lpx, lpy, color="#e0a0f0", alpha=al * 0.9, edgecolor=ec, linewidth=lw * 0.3)
        for i in range(5):
            da = i * 2 * np.pi / 5
            dx = cx + s * 0.08 * np.cos(da)
            dy = cy + s * 0.08 * np.sin(da)
            dot = plt.Circle((dx, dy), s * 0.02, color="#f0d060", alpha=al * 0.8)
            ax.add_patch(dot)
        stem_th = np.linspace(0, 1, 50)
        stx = cx + s * 0.3 * np.sin(np.pi * stem_th * 0.7)
        sty = np.linspace(cy - s * 0.1, cy - s * 1.5, 50)
        ax.plot(stx, sty, color=STEM, linewidth=lw * 1.2, alpha=al)

    @staticmethod
    def lotus(ax, cx=0, cy=0, s=1.0, color="#f0b0c0",
              ec="#c08090", lw=0.5, al=0.9):
        for layer, (n, r_scale, y_off, a_scale) in enumerate([
            (12, 0.7, -0.05, 0.9), (10, 0.55, 0.1, 0.8),
            (8, 0.4, 0.2, 0.7), (6, 0.25, 0.28, 0.6),
        ]):
            for p in range(n):
                ang = p * 2 * np.pi / n + layer * np.pi / n
                th = np.linspace(0, np.pi, 60)
                pw = s * r_scale * 0.15
                pr = s * r_scale * (1 - 0.3 * np.cos(th))
                px = cx + pr * np.sin(th) * np.cos(ang) + pw * np.sin(th) * np.sin(ang)
                py = cy + y_off * s + s * r_scale * 0.4 * np.cos(th * 0.5) * np.sin(ang)
                c_val = max(0, min(1, 0.95 - layer * 0.08))
                ax.fill(px, py, color=color, alpha=al * a_scale * c_val,
                        edgecolor=ec, linewidth=lw * 0.3)
        circ = plt.Circle((cx, cy + s * 0.32), s * 0.06, color="#f0d060", alpha=al * 0.7)
        ax.add_patch(circ)

    # ---- NEW FLOWERS (12) ----

    @staticmethod
    def chrysanthemum(ax, cx=0, cy=0, s=1.0, color="#e08020",
                      ec="#a05010", lw=0.5, al=0.9):
        n = 21
        for p in range(n):
            ang = p * 2 * np.pi * PHI
            r = s * 0.08 * np.sqrt(p + 1)
            if r > s * 0.7:
                continue
            th = np.linspace(0, 2 * np.pi, 50)
            pw = s * 0.03 * (1 - r / (s * 0.7))
            px = cx + r * np.cos(th) * np.cos(ang) + pw * np.sin(th) * np.cos(ang + np.pi / 2)
            py = cy + r * np.sin(th) * np.sin(ang) + pw * np.sin(th) * np.sin(ang + np.pi / 2)
            ax.fill(px, py, color=color, alpha=al * 0.7, edgecolor=ec, linewidth=lw * 0.2)
        for layer in range(3):
            cr = plt.Circle((cx, cy), s * (0.15 - layer * 0.04),
                            color="#f0a030", alpha=al * 0.8)
            ax.add_patch(cr)

    @staticmethod
    def peony(ax, cx=0, cy=0, s=1.0, color="#e87090",
              ec="#b05060", lw=0.5, al=0.9):
        for layer in range(4):
            n = 10 - layer * 2
            r_base = s * (0.6 - layer * 0.1)
            alpha_scale = 0.9 - layer * 0.1
            for p in range(n):
                ang = p * 2 * np.pi / n + layer * 0.2
                th = np.linspace(0, np.pi, 50)
                pw = r_base * 0.2
                pr = r_base * (1 + 0.3 * np.cos(th))
                px = cx + pr * np.sin(th) * np.cos(ang) + pw * np.sin(th) * np.sin(ang)
                py = cy + r_base * 0.3 * np.cos(th * 0.6)
                ax.fill(px, py, color=color, alpha=al * alpha_scale,
                        edgecolor=ec, linewidth=lw * 0.3)
        circ = plt.Circle((cx, cy), s * 0.08, color="#f0d060", alpha=al * 0.8)
        ax.add_patch(circ)

    @staticmethod
    def hibiscus(ax, cx=0, cy=0, s=1.0, color="#d02040",
                 ec="#801020", lw=0.5, al=0.9):
        for p in range(5):
            ang = p * 2 * np.pi / 5
            th = np.linspace(0, np.pi, 80)
            r = s * 0.65 * (1 + 0.2 * np.sin(3 * th))
            px = cx + r * np.sin(th) * np.cos(ang)
            py = cy + r * np.sin(th) * np.sin(ang)
            ax.fill(px, py, color=color, alpha=al * 0.8,
                    edgecolor=ec, linewidth=lw * 0.4)
        for i in range(8):
            ang = i * 2 * np.pi / 8
            stamen = np.linspace(0, 1, 30)
            sx = cx + s * 0.4 * stamen * np.cos(ang)
            sy = cy + s * 0.4 * stamen * np.sin(ang)
            ax.plot(sx, sy, color="#f0d040", linewidth=lw * 0.6, alpha=al * 0.7)
            ax.plot(sx[-1], sy[-1], "o", color="#f0d040", markersize=2, alpha=al * 0.9)
        circ = plt.Circle((cx, cy), s * 0.06, color="#f0d040", alpha=al * 0.9)
        ax.add_patch(circ)

    @staticmethod
    def lavender(ax, cx=0, cy=0, s=1.0, color="#9060c0",
                 ec="#6040a0", lw=0.4, al=0.85):
        stem_x = [cx, cx]
        stem_y = [cy - s * 1.0, cy + s * 0.3]
        ax.plot(stem_x, stem_y, color=STEM, linewidth=lw * 1.2, alpha=al)
        for i in range(12):
            t = i / 12
            by = cy + s * 0.3 - t * s * 0.5
            br = s * 0.06 * (1 - 0.5 * abs(t - 0.5))
            b = plt.Circle((cx, by), br, color=color, alpha=al * (0.7 + 0.3 * t))
            ax.add_patch(b)
        for side in [-1, 1]:
            leaf_th = np.linspace(0, 1, 30)
            lx = cx + side * s * 0.25 * leaf_th * (1 - leaf_th * 0.5)
            ly = cy - s * 0.5 + s * 0.1 * np.sin(np.pi * leaf_th)
            ax.fill(lx, ly, color=LEAF, alpha=al * 0.7, edgecolor=STEM, linewidth=lw * 0.2)

    @staticmethod
    def forget_me_not(ax, cx=0, cy=0, s=1.0, color="#4080e0",
                      ec="#2060b0", lw=0.4, al=0.85):
        positions = [
            (0, 0), (0.3, 0.2), (-0.25, 0.15), (0.1, 0.35),
            (-0.15, 0.3), (0.25, -0.1), (-0.3, -0.05), (0.05, -0.2),
        ]
        for ox, oy in positions:
            fx = cx + ox * s
            fy = cy + oy * s
            for p in range(5):
                ang = p * 2 * np.pi / 5 + np.pi / 2
                th = np.linspace(0, np.pi, 30)
                pw = s * 0.04
                pr = s * 0.06 * (1 - 0.3 * np.cos(th))
                px = fx + pr * np.sin(th) * np.cos(ang)
                py = fy + pr * np.sin(th) * np.sin(ang)
                ax.fill(px, py, color=color, alpha=al * 0.8,
                        edgecolor=ec, linewidth=lw * 0.2)
            center = plt.Circle((fx, fy), s * 0.015, color="#f0e040", alpha=al * 0.9)
            ax.add_patch(center)

    @staticmethod
    def cherry_blossom(ax, cx=0, cy=0, s=1.0, color="#f8b0c8",
                       ec="#d090a0", lw=0.5, al=0.9):
        for p in range(5):
            ang = p * 2 * np.pi / 5 + np.pi / 10
            th = np.linspace(0, 2 * np.pi, 80)
            r = s * 0.35 * (1 + 0.4 * np.cos(2 * th) + 0.2 * np.cos(3 * th))
            px = cx + r * np.cos(th + ang)
            py = cy + r * np.sin(th + ang)
            notch_r = s * 0.08
            for k in range(len(px)):
                notch_ang = np.arctan2(py[k] - cy, px[k] - cx)
                notch_d = np.sqrt((px[k] - cx)**2 + (py[k] - cy)**2)
                if abs(notch_ang - ang) < 0.3 and notch_d > s * 0.25:
                    px[k] = cx + (notch_d - notch_r) * np.cos(notch_ang)
                    py[k] = cy + (notch_d - notch_r) * np.sin(notch_ang)
            ax.fill(px, py, color=color, alpha=al * 0.85,
                    edgecolor=ec, linewidth=lw * 0.3)
        circ = plt.Circle((cx, cy), s * 0.06, color="#f0d060", alpha=al * 0.9)
        ax.add_patch(circ)
        for i in range(6):
            a = i * np.pi / 3
            st = np.linspace(0, 1, 15)
            sx = cx + s * 0.06 * st * np.cos(a)
            sy = cy + s * 0.06 * st * np.sin(a)
            ax.plot(sx, sy, color="#d0a040", linewidth=lw * 0.4, alpha=al * 0.6)

    @staticmethod
    def cactus_flower(ax, cx=0, cy=0, s=1.0, color="#e03060",
                      ec="#a01840", lw=0.5, al=0.9):
        for p in range(8):
            ang = p * 2 * np.pi / 8
            th = np.linspace(0, np.pi, 60)
            r = s * 0.5 * np.sin(th) * (1 + 0.15 * np.cos(3 * th))
            px = cx + r * np.cos(ang) * (1 - np.cos(th)) + s * 0.05 * np.cos(ang) * np.sin(th)
            py = cy + r * np.sin(ang) * (1 - np.cos(th)) + s * 0.05 * np.sin(ang) * np.sin(th)
            ax.fill(px, py, color=color, alpha=al * 0.7,
                    edgecolor=ec, linewidth=lw * 0.3)
        for i in range(12):
            a = i * np.pi / 6
            stamen = np.linspace(0, 1, 20)
            sx = cx + s * 0.3 * stamen * np.cos(a)
            sy = cy + s * 0.3 * stamen * np.sin(a)
            ax.plot(sx, sy, color="#f0f080", linewidth=lw * 0.3, alpha=al * 0.6)
            ax.plot(sx[-1], sy[-1], "o", color="#f0e040", markersize=1.5, alpha=al * 0.8)

    @staticmethod
    def camellia(ax, cx=0, cy=0, s=1.0, color="#e02040",
                 ec="#a01030", lw=0.5, al=0.9):
        for layer in range(3):
            n = 8 + layer * 4
            r = s * (0.5 - layer * 0.1)
            for p in range(n):
                ang = p * 2 * np.pi / n + layer * 0.15
                th = np.linspace(0, np.pi, 40)
                pw = r * 0.2
                px = cx + r * np.sin(th) * np.cos(ang) + pw * np.sin(th) * np.sin(ang)
                py = cy + r * np.cos(th * 0.5) * 0.3
                ax.fill(px, py, color=color, alpha=al * (0.85 - layer * 0.1),
                        edgecolor=ec, linewidth=lw * 0.2)
        circ = plt.Circle((cx, cy), s * 0.05, color="#f0d040", alpha=al * 0.8)
        ax.add_patch(circ)

    @staticmethod
    def pansy(ax, cx=0, cy=0, s=1.0, color="#6030a0",
              ec="#4020a0", lw=0.5, al=0.9):
        for p in range(5):
            ang = p * 2 * np.pi / 5 + np.pi / 2
            th = np.linspace(0, 2 * np.pi, 80)
            r = s * 0.35 * (1 + 0.3 * np.cos(3 * th))
            px = cx + r * np.cos(th + ang)
            py = cy + r * np.sin(th + ang)
            ax.fill(px, py, color=color, alpha=al * 0.8,
                    edgecolor=ec, linewidth=lw * 0.3)
        for i in range(3):
            ang = -np.pi / 2 + (i - 1) * 0.3
            streak_th = np.linspace(0, 0.4, 20)
            sx = cx + s * 0.3 * streak_th * np.cos(ang)
            sy = cy + s * 0.3 * streak_th * np.sin(ang)
            ax.plot(sx, sy, color="#f0e040", linewidth=lw * 0.8, alpha=al * 0.7)
        circ = plt.Circle((cx, cy), s * 0.06, color="#f0e040", alpha=al * 0.85)
        ax.add_patch(circ)

    @staticmethod
    def snowdrop(ax, cx=0, cy=0, s=1.0, color="#e0f0f0",
                 ec="#a0c0c0", lw=0.4, al=0.85):
        for p in range(3):
            ang = p * 2 * np.pi / 3 - np.pi / 2
            th = np.linspace(0, np.pi, 40)
            r = s * 0.2 * np.sin(th)
            px = cx + r * np.cos(ang)
            py = cy + r * np.sin(ang) + s * 0.1 * np.cos(th)
            ax.fill(px, py, color=color, alpha=al * 0.9,
                    edgecolor=ec, linewidth=lw * 0.3)
        for p in range(3):
            ang = p * 2 * np.pi / 3 - np.pi / 2
            inner = plt.Circle((cx + s * 0.05 * np.cos(ang),
                               cy + s * 0.05 * np.sin(ang)),
                              s * 0.03, color="#f0e040", alpha=al * 0.7)
            ax.add_patch(inner)
        stem_x = [cx, cx, cx + s * 0.05]
        stem_y = [cy, cy - s * 0.8, cy - s * 1.0]
        ax.plot(stem_x, stem_y, color=STEM, linewidth=lw * 1.0, alpha=al * 0.8)
        for side in [-1, 1]:
            leaf = np.linspace(0, 1, 30)
            lx = cx + side * s * 0.15 * leaf
            ly = cy - s * 0.3 + s * 0.6 * leaf * (1 - leaf * 0.7)
            ax.fill(lx, ly, color=LEAF, alpha=al * 0.6, edgecolor=STEM, linewidth=lw * 0.2)


# ============================================================
#  PLANT CURVES v2 - Original + new plants
# ============================================================

class PlantCurves:

    @staticmethod
    def vine(ax, x0=0, y0=0, x1=2, y1=3, s=1.0, c=STEM,
             lw=0.6, al=0.85):
        n = 80
        t = np.linspace(0, 1, n)
        vx = x0 + (x1 - x0) * t + s * 0.4 * np.sin(2 * np.pi * t)
        vy = y0 + (y1 - y0) * t + s * 0.2 * np.cos(np.pi * t * 1.5)
        ax.plot(vx, vy, color=c, linewidth=lw, alpha=al)
        for i in range(0, n, 8):
            leaf_side = 1 if i % 16 < 8 else -1
            th = np.linspace(0, 1, 30)
            lx = vx[i] + leaf_side * s * 0.15 * th * (1 - th)
            ly = vy[i] + s * 0.08 * np.sin(np.pi * th) + s * 0.05 * th
            ax.fill(lx, ly, color=LEAF, alpha=al * 0.7, edgecolor=c, linewidth=lw * 0.2)

    @staticmethod
    def branch(ax, x0=0, y0=0, angle=np.pi / 2, length=1.5,
               depth=4, s=1.0, c="#6a4020", lw=0.8, al=0.85):
        if depth <= 0 or length < 0.05:
            return
        x1 = x0 + length * s * np.cos(angle)
        y1 = y0 + length * s * np.sin(angle)
        w = lw * depth / 4
        ax.plot([x0, x1], [y0, y1], color=c, linewidth=w, alpha=al)
        if depth <= 2:
            cr = plt.Circle((x1, y1), s * 0.04 * depth,
                             color=LEAF, alpha=al * 0.5)
            ax.add_patch(cr)
        spread = 0.5 + 0.1 * depth
        PlantCurves.branch(ax, x1, y1, angle + spread,
                           length * 0.65, depth - 1, s, c, lw, al)
        PlantCurves.branch(ax, x1, y1, angle - spread,
                           length * 0.65, depth - 1, s, c, lw, al)

    @staticmethod
    def fern(ax, cx=0, cy=0, s=1.0, c="#1a7a1a",
             lw=0.5, al=0.85):
        n_pairs = 14
        for i in range(n_pairs):
            t = i / n_pairs
            r = s * 0.6 * (1 - t * 0.3)
            pair_y = cy + s * 1.2 * t
            for side in [-1, 1]:
                leaf_th = np.linspace(0, 1, 30)
                lx = cx + side * r * leaf_th * (1 - 0.3 * leaf_th)
                ly = pair_y + s * 0.12 * np.sin(np.pi * leaf_th * 0.8)
                ax.fill(lx, ly, color=c, alpha=al * (0.7 + 0.3 * (1 - t)),
                        edgecolor=LEAF, linewidth=lw * 0.2)
        stem_x = np.linspace(cx, cx, 40)
        stem_y = np.linspace(cy, cy + s * 1.2, 40)
        ax.plot(stem_x, stem_y, color=STEM, linewidth=lw * 1.2, alpha=al)

    @staticmethod
    def grass(ax, cx=0, cy=0, s=1.0, n=8, c=STEM,
              lw=0.5, al=0.8):
        for i in range(n):
            base_x = cx + s * (i - n / 2 + 0.5) * 0.12
            height = s * (0.4 + 0.4 * np.random.rand())
            sway = s * 0.1 * np.random.uniform(-1, 1)
            th = np.linspace(0, 1, 40)
            gx = base_x + sway * np.sin(np.pi * th * 0.7)
            gy = cy + height * th
            ax.plot(gx, gy, color=c, linewidth=lw, alpha=al)

    @staticmethod
    def tree_canopy(ax, cx=0, cy=0, s=1.0, c="#1a6a1a",
                    al=0.7):
        offsets = [
            (0, 0, 0.4), (-0.25, 0.1, 0.3), (0.25, 0.1, 0.3),
            (-0.1, 0.25, 0.28), (0.15, 0.2, 0.25), (0, 0.35, 0.22),
            (-0.3, -0.05, 0.2), (0.3, -0.05, 0.2),
        ]
        for ox, oy, r in offsets:
            cr = plt.Circle((cx + ox * s, cy + oy * s), r * s,
                             color=c, alpha=al * (0.6 + 0.4 * np.random.rand()))
            ax.add_patch(cr)
        highlight = plt.Circle((cx + s * 0.05, cy + s * 0.1), s * 0.2,
                                color="#2a9a3a", alpha=al * 0.3)
        ax.add_patch(highlight)

    @staticmethod
    def cactus(ax, cx=0, cy=0, s=1.0, color="#2a7a2a",
               lw=0.5, al=0.85):
        body = plt.Rectangle((cx - s * 0.15, cy - s * 0.5), s * 0.3, s * 1.0,
                              color=color, alpha=al * 0.8, edgecolor="#1a5a1a",
                              linewidth=lw * 0.5)
        ax.add_patch(body)
        for side in [-1, 1]:
            arm_y = cy + s * 0.1
            arm = plt.Rectangle((cx + side * s * 0.15, arm_y), side * s * 0.25, s * 0.15,
                                 color=color, alpha=al * 0.8, edgecolor="#1a5a1a",
                                 linewidth=lw * 0.3)
            ax.add_patch(arm)
            ax.add_patch(plt.Rectangle((cx + side * s * 0.15, arm_y + s * 0.15),
                                        s * 0.1, s * 0.3, color=color, alpha=al * 0.8))
        for i in range(8):
            ry = cy - s * 0.4 + i * s * 0.12
            ax.plot([cx - s * 0.15, cx + s * 0.15], [ry, ry],
                    color="#1a5a1a", linewidth=lw * 0.3, alpha=al * 0.5)
        spines = np.random.uniform(-0.15, 0.15, 12)
        for sx in spines:
            sy = np.random.uniform(-0.5, 0.5)
            ax.plot([cx + sx * s, cx + sx * s + s * 0.03],
                    [cy + sy * s, cy + sy * s + s * 0.03],
                    color="#a0a060", linewidth=lw * 0.2, alpha=al * 0.5)
        for side in [-1, 1]:
            flower_x = cx + side * s * 0.4
            flower_y = cy + s * 0.35
            FlowerCurves.cactus_flower(ax, flower_x, flower_y, s * 0.15, color="#e03060", al=al * 0.8)

    @staticmethod
    def bonsai(ax, cx=0, cy=0, s=1.0, c="#1a6a1a",
               lw=0.6, al=0.85):
        trunk_x = [cx - s * 0.1, cx + s * 0.05, cx - s * 0.15, cx - s * 0.3]
        trunk_y = [cy - s * 0.5, cy - s * 0.2, cy + s * 0.1, cy + s * 0.2]
        ax.plot(trunk_x, trunk_y, color="#6a4020", linewidth=lw * 2.5, alpha=al)
        ax.plot(trunk_x, trunk_y, color="#5a3018", linewidth=lw * 1.5, alpha=al * 0.5)
        clusters = [
            (-0.3, 0.3, 0.25), (0.0, 0.2, 0.3), (-0.5, 0.15, 0.18),
            (-0.1, 0.35, 0.2), (0.1, 0.25, 0.15),
        ]
        for ox, oy, r in clusters:
            cr = plt.Circle((cx + ox * s, cy + oy * s), r * s,
                             color=c, alpha=al * (0.7 + 0.2 * np.random.rand()))
            ax.add_patch(cr)
        pot = plt.Rectangle((cx - s * 0.25, cy - s * 0.7), s * 0.5, s * 0.2,
                             color="#8a5a30", alpha=al * 0.9, edgecolor="#6a4020",
                             linewidth=lw * 0.5)
        ax.add_patch(pot)

    @staticmethod
    def succulent(ax, cx=0, cy=0, s=1.0, color="#3a8a5a",
                  lw=0.5, al=0.85):
        for layer in range(4):
            n = 5 + layer * 2
            r = s * (0.15 + layer * 0.1)
            for p in range(n):
                ang = p * 2 * np.pi / n + layer * 0.3
                th = np.linspace(0, np.pi, 30)
                pw = r * 0.3
                px = cx + r * np.cos(ang) + pw * np.sin(th) * np.sin(ang)
                py = cy + r * np.sin(ang) + pw * np.sin(th) * np.cos(ang)
                ax.fill(px, py, color=color, alpha=al * (0.7 + 0.1 * layer),
                        edgecolor="#2a6a3a", linewidth=lw * 0.3)
        center = plt.Circle((cx, cy), s * 0.06, color="#5aaa7a", alpha=al * 0.8)
        ax.add_patch(center)

    @staticmethod
    def mushroom(ax, cx=0, cy=0, s=1.0, cap_color="#c04020",
                 lw=0.5, al=0.85):
        cap_th = np.linspace(0, np.pi, 80)
        cap_x = cx + s * 0.5 * np.cos(cap_th)
        cap_y = cy + s * 0.3 * np.sin(cap_th) * (1 + 0.2 * np.cos(3 * cap_th))
        ax.fill(cap_x, cap_y, color=cap_color, alpha=al * 0.85,
                edgecolor="#801810", linewidth=lw * 0.4)
        for i in range(8):
            spot_x = cx + s * 0.3 * np.cos(np.random.uniform(0.3, 2.8))
            spot_y = cy + s * 0.15 + s * 0.1 * np.random.uniform(0, 1)
            spot = plt.Circle((spot_x, spot_y), s * 0.04, color="#f0e0d0", alpha=al * 0.7)
            ax.add_patch(spot)
        stem_w = s * 0.12
        ax.add_patch(plt.Rectangle((cx - stem_w / 2, cy - s * 0.5), stem_w, s * 0.5,
                                    color="#f0e0c0", alpha=al * 0.85,
                                    edgecolor="#c0b090", linewidth=lw * 0.3))

    @staticmethod
    def seaweed(ax, cx=0, cy=0, s=1.0, n=3, c="#1a7a4a",
                lw=0.5, al=0.7):
        for k in range(n):
            offset_x = (k - n / 2 + 0.5) * s * 0.2
            t = np.linspace(0, 1, 60)
            sx = cx + offset_x + s * 0.15 * np.sin(3 * np.pi * t + k)
            sy = cy + s * 1.5 * t
            ax.plot(sx, sy, color=c, linewidth=lw, alpha=al)
            for i in range(0, 60, 8):
                leaf_side = 1 if i % 16 < 8 else -1
                lx = sx[i] + leaf_side * s * 0.06
                ly = sy[i]
                leaf_dot = plt.Circle((lx, ly), s * 0.02,
                                       color="#2aaa5a", alpha=al * 0.5)
                ax.add_patch(leaf_dot)


# ============================================================
#  COMPOSITION CURVES v2 - Original + new compositions
# ============================================================

class CompositionCurves:

    @staticmethod
    def bouquet(ax, cx=0, cy=0, s=1.0):
        stem_base_x = cx
        stem_base_y = cy - s * 0.8
        flower_defs = [
            (cx - s * 0.3, cy + s * 0.1, s * 0.3, "#c83060", 5),
            (cx + s * 0.25, cy + s * 0.15, s * 0.28, "#f0b0c0", 6),
            (cx, cy + s * 0.35, s * 0.35, "#d03060", 5),
            (cx - s * 0.15, cy + s * 0.25, s * 0.25, "#f0e0c0", 12),
            (cx + s * 0.1, cy + s * 0.3, s * 0.22, "#c070d0", 5),
        ]
        for fx, fy, fs, fc, npet in flower_defs:
            PlantCurves.branch(ax, stem_base_x, stem_base_y,
                               np.pi / 2 + (fx - cx) * 0.3,
                               np.sqrt((fx - cx) ** 2 + (fy - stem_base_y) ** 2) * 0.5,
                               depth=2, s=s * 0.3, c=STEM, lw=0.6, al=0.7)
        for fx, fy, fs, fc, npet in flower_defs:
            FlowerCurves.daisy(ax, fx, fy, fs, petals=npet, color=fc,
                               ec="#804050", lw=0.4, al=0.85)
        bow_th = np.linspace(0, 2 * np.pi, 80)
        bx = cx + s * 0.15 * np.cos(bow_th)
        by = cy - s * 0.3 + s * 0.08 * np.sin(bow_th)
        ax.plot(bx, by, color=GOLD, linewidth=1.5, alpha=0.8)

    @staticmethod
    def garden_scene(ax, cx=0, cy=0, s=1.0):
        ground_x = np.linspace(cx - s * 2, cx + s * 2, 100)
        ground_y = cy - s * 0.5 + s * 0.05 * np.sin(3 * ground_x)
        ax.fill_between(ground_x, cy - s * 1.2, ground_y, color="#1a3a10", alpha=0.6)
        for gx in np.linspace(cx - s * 1.8, cx + s * 1.8, 12):
            PlantCurves.grass(ax, gx, cy - s * 0.5 + s * 0.02 * np.sin(gx),
                              s * 0.2, n=5, c=STEM2, lw=0.3, al=0.6)
        FlowerCurves.rose(ax, cx - s * 0.8, cy + s * 0.3, s * 0.35, petals=6, al=0.8)
        FlowerCurves.sunflower(ax, cx + s * 0.5, cy + s * 0.5, s * 0.4, al=0.8)
        FlowerCurves.lily(ax, cx - s * 0.2, cy + s * 0.6, s * 0.3, al=0.75)
        FlowerCurves.tulip(ax, cx + s * 1.0, cy + s * 0.2, s * 0.3, al=0.75)
        FlowerCurves.orchid(ax, cx - s * 1.2, cy + s * 0.15, s * 0.25, al=0.7)

    @staticmethod
    def wreath(ax, cx=0, cy=0, s=1.0, n_flowers=10):
        ring_r = s * 0.8
        th = np.linspace(0, 2 * np.pi, 200)
        ring_x = cx + ring_r * np.cos(th)
        ring_y = cy + ring_r * np.sin(th)
        ax.plot(ring_x, ring_y, color=STEM, linewidth=2.5, alpha=0.7)
        ax.plot(ring_x, ring_y, color=LEAF, linewidth=4.0, alpha=0.3)
        for i in range(n_flowers):
            ang = i * 2 * np.pi / n_flowers
            fx = cx + ring_r * np.cos(ang)
            fy = cy + ring_r * np.sin(ang)
            fs = s * 0.12
            colors = ["#c83060", "#f0b0c0", "#c070d0", "#f0e0c0", "#f0c810"]
            fc = colors[i % len(colors)]
            FlowerCurves.daisy(ax, fx, fy, fs, petals=8, color=fc, lw=0.3, al=0.8)
        for i in range(n_flowers * 3):
            ang = np.random.uniform(0, 2 * np.pi)
            lr = ring_r + s * 0.08 * np.random.uniform(-1, 1)
            lx = cx + lr * np.cos(ang)
            ly = cy + lr * np.sin(ang)
            leaf_dot = plt.Circle((lx, ly), s * 0.025, color=LEAF, alpha=0.5)
            ax.add_patch(leaf_dot)

    @staticmethod
    def floral_border(ax, x0=0, y0=0, x1=4, y1=0, s=1.0):
        n = 8
        for i in range(n):
            t = i / (n - 1)
            fx = x0 + (x1 - x0) * t
            fy = y0 + (y1 - y0) * t + s * 0.05 * np.sin(2 * np.pi * t * 3)
            fs = s * 0.1
            colors = ["#c83060", "#f0b0c0", "#c070d0", "#f0c810"]
            fc = colors[i % len(colors)]
            FlowerCurves.daisy(ax, fx, fy, fs, petals=6, color=fc, lw=0.3, al=0.7)
        vine_th = np.linspace(0, 1, 120)
        vx = x0 + (x1 - x0) * vine_th
        vy = y0 + (y1 - y0) * vine_th + s * 0.15 * np.sin(4 * np.pi * vine_th)
        ax.plot(vx, vy, color=STEM, linewidth=1.0, alpha=0.5)

    @staticmethod
    def terrarium(ax, cx=0, cy=0, s=1.0):
        dome_th = np.linspace(0, np.pi, 100)
        dome_x = cx + s * 0.8 * np.cos(dome_th)
        dome_y = cy + s * 0.1 + s * 0.8 * np.sin(dome_th)
        ax.plot(dome_x, dome_y, color="#a0c0d0", linewidth=0.8, alpha=0.5)
        ax.fill_between(dome_x, cy - s * 0.3, dome_y, color="#a0c0d0", alpha=0.05)
        base = plt.Rectangle((cx - s * 0.7, cy - s * 0.4), s * 1.4, s * 0.15,
                              color="#8a7a60", alpha=0.8)
        ax.add_patch(base)
        soil_x = np.linspace(cx - s * 0.65, cx + s * 0.65, 80)
        soil_y = cy - s * 0.3 + s * 0.03 * np.sin(5 * soil_x)
        ax.fill_between(soil_x, cy - s * 0.5, soil_y, color="#3a2a10", alpha=0.7)
        PlantCurves.succulent(ax, cx - s * 0.3, cy - s * 0.1, s * 0.3, al=0.8)
        PlantCurves.mushroom(ax, cx + s * 0.2, cy - s * 0.15, s * 0.25, al=0.8)
        PlantCurves.grass(ax, cx, cy - s * 0.25, s * 0.15, n=5, al=0.6)
        FlowerCurves.cherry_blossom(ax, cx + s * 0.1, cy + s * 0.2, s * 0.15, al=0.7)

    @staticmethod
    def ikebana(ax, cx=0, cy=0, s=1.0):
        PlantCurves.branch(ax, cx, cy - s * 0.5, np.pi / 2 + 0.3,
                           s * 0.8, depth=3, s=s * 0.4, lw=0.8, al=0.8)
        PlantCurves.branch(ax, cx, cy - s * 0.5, np.pi / 2 - 0.5,
                           s * 0.6, depth=2, s=s * 0.3, lw=0.6, al=0.7)
        FlowerCurves.rose(ax, cx + s * 0.3, cy + s * 0.4, s * 0.25,
                          petals=5, color="#c83060", al=0.9)
        FlowerCurves.lily(ax, cx - s * 0.4, cy + s * 0.5, s * 0.2,
                          color="#f0e0c0", al=0.8)
        pot = plt.Polygon([
            (cx - s * 0.2, cy - s * 0.5),
            (cx + s * 0.2, cy - s * 0.5),
            (cx + s * 0.15, cy - s * 0.7),
            (cx - s * 0.15, cy - s * 0.7),
        ], color="#6a4a30", alpha=0.9, edgecolor="#4a3020", linewidth=0.8)
        ax.add_patch(pot)

    @staticmethod
    def flower_crown(ax, cx=0, cy=0, s=1.0, n=12):
        ring_r = s * 0.7
        th = np.linspace(0, 2 * np.pi, 200)
        ring_x = cx + ring_r * np.cos(th)
        ring_y = cy + ring_r * np.sin(th) * 0.6
        ax.plot(ring_x, ring_y, color=STEM, linewidth=1.5, alpha=0.7)
        for i in range(n):
            ang = i * 2 * np.pi / n
            fx = cx + ring_r * np.cos(ang)
            fy = cy + ring_r * np.sin(ang) * 0.6
            fs = s * 0.08
            flower_fns = [
                lambda a, f, fc: FlowerCurves.cherry_blossom(a, f[0], f[1], fc, color="#f8b0c8", al=0.8),
                lambda a, f, fc: FlowerCurves.daisy(a, f[0], f[1], fc, petals=6, color="#ffffff", al=0.8),
                lambda a, f, fc: FlowerCurves.forget_me_not(a, f[0], f[1], fc, al=0.8),
                lambda a, f, fc: FlowerCurves.snowdrop(a, f[0], f[1], fc, al=0.8),
            ]
            flower_fns[i % len(flower_fns)](ax, (fx, fy), fs)
        for i in range(n * 2):
            ang = np.random.uniform(0, 2 * np.pi)
            lr = ring_r + s * 0.06 * np.random.uniform(-1, 1)
            lx = cx + lr * np.cos(ang)
            ly = cy + lr * np.sin(ang) * 0.6
            leaf = plt.Circle((lx, ly), s * 0.015, color=LEAF, alpha=0.5)
            ax.add_patch(leaf)

    @staticmethod
    def vertical_garden(ax, cx=0, cy=0, s=1.0):
        wall = plt.Rectangle((cx - s * 1.0, cy - s * 1.0), s * 2.0, s * 2.5,
                              color="#3a3a3a", alpha=0.6)
        ax.add_patch(wall)
        for row in range(5):
            for col in range(4):
                wx = cx - s * 0.7 + col * s * 0.5
                wy = cy - s * 0.8 + row * s * 0.5
                box = plt.Rectangle((wx - s * 0.05, wy - s * 0.05), s * 0.3, s * 0.2,
                                     color="#5a4a30", alpha=0.7)
                ax.add_patch(box)
                plant_fns = [
                    lambda: PlantCurves.grass(ax, wx + s * 0.1, wy, s * 0.1, n=3, al=0.7),
                    lambda: PlantCurves.succulent(ax, wx + s * 0.1, wy + s * 0.05, s * 0.1, al=0.7),
                    lambda: FlowerCurves.forget_me_not(ax, wx + s * 0.1, wy + s * 0.05, s * 0.08, al=0.7),
                    lambda: PlantCurves.fern(ax, wx + s * 0.1, wy, s * 0.08, al=0.7),
                ]
                plant_fns[(row + col) % len(plant_fns)]()

    @staticmethod
    def forest_floor(ax, cx=0, cy=0, s=1.0):
        ground_x = np.linspace(cx - s * 2, cx + s * 2, 100)
        ground_y = cy + s * 0.05 * np.sin(3 * ground_x)
        ax.fill_between(ground_x, cy - s * 0.5, ground_y, color="#1a2a10", alpha=0.7)
        PlantCurves.mushroom(ax, cx - s * 0.5, cy + s * 0.1, s * 0.3, al=0.8)
        PlantCurves.mushroom(ax, cx + s * 0.3, cy + s * 0.05, s * 0.2, cap_color="#8a6a20", al=0.7)
        PlantCurves.mushroom(ax, cx + s * 0.6, cy + s * 0.15, s * 0.15, cap_color="#c0a040", al=0.7)
        PlantCurves.fern(ax, cx - s * 1.0, cy, s * 0.5, al=0.7)
        PlantCurves.fern(ax, cx + s * 1.2, cy + s * 0.1, s * 0.4, al=0.6)
        for i in range(6):
            lx = cx - s * 1.5 + i * s * 0.6
            ly = cy - s * 0.1 + s * 0.05 * np.random.uniform(-1, 1)
            dead_leaf = plt.Circle((lx, ly), s * 0.03, color="#8a6a30", alpha=0.4)
            ax.add_patch(dead_leaf)


# ============================================================
#  MAIN - Enhanced showcase
# ============================================================

if __name__ == "__main__":
    t0 = time.time()
    print("[START] Generating enhanced botanical showcase...")

    fig, axes = plt.subplots(4, 3, figsize=(18, 24), dpi=150)
    fig.patch.set_facecolor("#0d0a1a")
    fig.suptitle("POLYART: Botanical Art v2 - Flowers, Plants & Compositions",
                 fontsize=18, color=GOLD, fontweight="bold", fontfamily="serif", y=0.98)

    panels = [
        ("Rose", lambda ax: FlowerCurves.rose(ax, 0, 0.3, 1.2, petals=7)),
        ("Peony", lambda ax: FlowerCurves.peony(ax, 0, 0.3, 1.2)),
        ("Chrysanthemum", lambda ax: FlowerCurves.chrysanthemum(ax, 0, 0.3, 1.2)),
        ("Lily", lambda ax: FlowerCurves.lily(ax, 0, 0.3, 1.2, color="#f0e0c0")),
        ("Hibiscus", lambda ax: FlowerCurves.hibiscus(ax, 0, 0.3, 1.2)),
        ("Sunflower", lambda ax: FlowerCurves.sunflower(ax, 0, 0.3, 1.2)),
        ("Tulip", lambda ax: FlowerCurves.tulip(ax, 0, 0.3, 1.0)),
        ("Orchid", lambda ax: FlowerCurves.orchid(ax, 0, 0.3, 1.2)),
        ("Camellia", lambda ax: FlowerCurves.camellia(ax, 0, 0.3, 1.2)),
        ("Cherry Blossom", lambda ax: FlowerCurves.cherry_blossom(ax, 0, 0.3, 1.2)),
        ("Pansy", lambda ax: FlowerCurves.pansy(ax, 0, 0.3, 1.2)),
        ("Lavender", lambda ax: FlowerCurves.lavender(ax, 0, 0.2, 1.2)),
    ]

    for idx, (name, func) in enumerate(panels):
        ax = axes.flatten()[idx]
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor("#0d0a1a")
        ax.set_title(name, fontsize=11, color=GOLD, fontfamily="serif")
        func(ax)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out1 = r"C:\Users\e\Desktop\6756756756756756\flowers_v2_flowers.png"
    fig.savefig(out1, dpi=150, bbox_inches="tight", facecolor="#0d0a1a")
    plt.close(fig)
    print("[OK] Saved: flowers_v2_flowers.png")

    fig2, axes2 = plt.subplots(4, 3, figsize=(18, 24), dpi=150)
    fig2.patch.set_facecolor("#0d0a1a")
    fig2.suptitle("POLYART: Plants, Fungi & Compositions",
                  fontsize=18, color=GOLD, fontweight="bold", fontfamily="serif", y=0.98)

    panels2 = [
        ("Cactus", lambda ax: PlantCurves.cactus(ax, 0, 0, 1.0)),
        ("Bonsai", lambda ax: PlantCurves.bonsai(ax, 0, 0, 1.0)),
        ("Succulent", lambda ax: PlantCurves.succulent(ax, 0, 0.2, 1.0)),
        ("Mushroom", lambda ax: PlantCurves.mushroom(ax, 0, 0.2, 1.2)),
        ("Seaweed", lambda ax: PlantCurves.seaweed(ax, 0, -0.5, 1.0)),
        ("Fern", lambda ax: PlantCurves.fern(ax, 0, -0.5, 1.0)),
        ("Terrarium", lambda ax: CompositionCurves.terrarium(ax, 0, 0, 1.3)),
        ("Ikebana", lambda ax: CompositionCurves.ikebana(ax, 0, 0, 1.3)),
        ("Flower Crown", lambda ax: CompositionCurves.flower_crown(ax, 0, 0.3, 1.3)),
        ("Vertical Garden", lambda ax: CompositionCurves.vertical_garden(ax, 0, 0, 1.0)),
        ("Forest Floor", lambda ax: CompositionCurves.forest_floor(ax, 0, 0, 1.2)),
        ("Wreath", lambda ax: CompositionCurves.wreath(ax, 0, 0.2, 1.3, n_flowers=12)),
    ]

    for idx, (name, func) in enumerate(panels2):
        ax = axes2.flatten()[idx]
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor("#0d0a1a")
        ax.set_title(name, fontsize=11, color=GOLD, fontfamily="serif")
        func(ax)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out2 = r"C:\Users\e\Desktop\6756756756756756\flowers_v2_plants.png"
    fig2.savefig(out2, dpi=150, bbox_inches="tight", facecolor="#0d0a1a")
    plt.close(fig2)
    print("[OK] Saved: flowers_v2_plants.png")

    fig3, axes3 = plt.subplots(2, 3, figsize=(18, 12), dpi=150)
    fig3.patch.set_facecolor("#0d0a1a")
    fig3.suptitle("POLYART: Grand Compositions",
                  fontsize=18, color=GOLD, fontweight="bold", fontfamily="serif", y=0.98)

    panels3 = [
        ("Garden Scene", lambda ax: CompositionCurves.garden_scene(ax, 0, 0, 1.2)),
        ("Bouquet", lambda ax: CompositionCurves.bouquet(ax, 0, 0.3, 1.5)),
        ("Floral Border", lambda ax: (
            CompositionCurves.floral_border(ax, -2, 0, 2, 0, s=1.0),
            ax.set_xlim(-2.5, 2.5), ax.set_ylim(-1, 1)
        )),
        ("Forget-me-not", lambda ax: FlowerCurves.forget_me_not(ax, 0, 0.3, 1.5)),
        ("Snowdrop", lambda ax: FlowerCurves.snowdrop(ax, 0, 0.3, 1.5)),
        ("Lotus", lambda ax: FlowerCurves.lotus(ax, 0, 0.2, 1.5)),
    ]

    for idx, (name, func) in enumerate(panels3):
        ax = axes3.flatten()[idx]
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2, 2)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor("#0d0a1a")
        ax.set_title(name, fontsize=11, color=GOLD, fontfamily="serif")
        func(ax)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out3 = r"C:\Users\e\Desktop\6756756756756756\flowers_v2_compositions.png"
    fig3.savefig(out3, dpi=150, bbox_inches="tight", facecolor="#0d0a1a")
    plt.close(fig3)
    print("[OK] Saved: flowers_v2_compositions.png")

    elapsed = time.time() - t0
    print("[DONE] 3 showcase images generated in %.1fs" % elapsed)
