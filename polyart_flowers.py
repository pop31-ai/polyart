import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


# ============================================================
#  POLYART BOTANICAL / FLORAL ART MODULE
#  Polynomial curves for flowers, plants, and compositions
# ============================================================

PHI = (1 + np.sqrt(5)) / 2
GOLD = "#c8a040"
STEM = "#2a6a1a"
STEM2 = "#3a8a2a"
LEAF = "#1e5a12"


# ============================================================
#  FLOWER CURVES  -  Individual flower renderers
# ============================================================

class FlowerCurves:
    """Polynomial flower shapes: rose, lily, daisy, tulip, sunflower, orchid, lotus."""

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
        for r_val in [0.22, 0.15, 0.08]:
            c = plt.Circle((cx, cy), s * r_val, fill=False,
                           edgecolor="#806020", linewidth=lw * 0.4, alpha=al * 0.4)
            ax.add_patch(c)

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
            (12, 0.7, -0.05, 0.9),
            (10, 0.55, 0.1, 0.8),
            (8, 0.4, 0.2, 0.7),
            (6, 0.25, 0.28, 0.6),
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


# ============================================================
#  PLANT CURVES  -  Stems, branches, foliage
# ============================================================

class PlantCurves:
    """Vine, branch, fern, grass, tree canopy polynomial curves."""

    @staticmethod
    def vine(ax, x0=0, y0=0, x1=2, y1=3, s=1.0, c=STEM,
             lw=0.6, al=0.85):
        n = 80
        t = np.linspace(0, 1, n)
        mx = (x0 + x1) / 2 + s * 0.8 * np.sin(np.pi * t)
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


# ============================================================
#  COMPOSITION CURVES  -  Multi-element floral scenes
# ============================================================

class CompositionCurves:
    """Arrangements: bouquet, garden, wreath, border."""

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
        ax.fill_between(ground_x, cy - s * 1.2, ground_y,
                        color="#1a3a10", alpha=0.6)
        for gx in np.linspace(cx - s * 1.8, cx + s * 1.8, 12):
            PlantCurves.grass(ax, gx, cy - s * 0.5 + s * 0.02 * np.sin(gx),
                              s * 0.2, n=5, c=STEM2, lw=0.3, al=0.6)
        FlowerCurves.rose(ax, cx - s * 0.8, cy + s * 0.3, s * 0.35,
                          petals=6, color="#c83060", al=0.8)
        FlowerCurves.sunflower(ax, cx + s * 0.5, cy + s * 0.5, s * 0.4, al=0.8)
        FlowerCurves.lily(ax, cx - s * 0.2, cy + s * 0.6, s * 0.3, al=0.75)
        FlowerCurves.tulip(ax, cx + s * 1.0, cy + s * 0.2, s * 0.3, al=0.75)
        FlowerCurves.orchid(ax, cx - s * 1.2, cy + s * 0.15, s * 0.25, al=0.7)
        th = np.linspace(0, 2 * np.pi, 100)
        sun_x = cx + s * 1.5 + s * 0.15 * np.cos(th)
        sun_y = cy + s * 1.3 + s * 0.15 * np.sin(th)
        ax.fill(sun_x, sun_y, color="#f0c830", alpha=0.3)
        for i in range(8):
            ang = i * np.pi / 4
            ax.plot([cx + s * 1.5 + s * 0.18 * np.cos(ang),
                     cx + s * 1.5 + s * 0.3 * np.cos(ang)],
                    [cy + s * 1.3 + s * 0.18 * np.sin(ang),
                     cy + s * 1.3 + s * 0.3 * np.sin(ang)],
                    color="#f0c830", linewidth=0.5, alpha=0.3)

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
            FlowerCurves.daisy(ax, fx, fy, fs, petals=8, color=fc,
                               ec="#804050", lw=0.3, al=0.8)
        for i in range(n_flowers * 3):
            ang = np.random.uniform(0, 2 * np.pi)
            lr = ring_r + s * 0.08 * np.random.uniform(-1, 1)
            lx = cx + lr * np.cos(ang)
            ly = cy + lr * np.sin(ang)
            leaf_dot = plt.Circle((lx, ly), s * 0.025,
                                   color=LEAF, alpha=0.5)
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
            FlowerCurves.daisy(ax, fx, fy, fs, petals=6, color=fc,
                               ec="#804050", lw=0.3, al=0.7)
        vine_th = np.linspace(0, 1, 120)
        vx = x0 + (x1 - x0) * vine_th
        vy = y0 + (y1 - y0) * vine_th + s * 0.15 * np.sin(4 * np.pi * vine_th)
        ax.plot(vx, vy, color=STEM, linewidth=1.0, alpha=0.5)


# ============================================================
#  MAIN  -  Showcase demo
# ============================================================

if __name__ == "__main__":
    print("=== PolyArt Botanical / Floral Art Module ===")
    print("Creating 3x2 showcase figure...")

    fig, axes = plt.subplots(3, 2, figsize=(12, 18), dpi=150)
    fig.patch.set_facecolor("#0d0a1a")
    fig.suptitle("POLYART: Botanical Art - Polynomial Flowers",
                 fontsize=16, color=GOLD, fontweight="bold", fontfamily="serif")

    panels = [
        ("Rose", lambda ax: FlowerCurves.rose(ax, 0, 0.5, 1.5, petals=7, color="#c83060")),
        ("Lily & Daisy", lambda ax: (
            FlowerCurves.lily(ax, -0.8, 0.8, 1.0, color="#f0e0c0"),
            FlowerCurves.daisy(ax, 0.8, 0.6, 1.0, petals=14, color="#ffffff"),
        )),
        ("Sunflower & Lotus", lambda ax: (
            FlowerCurves.sunflower(ax, -0.6, 0.6, 1.2),
            FlowerCurves.lotus(ax, 0.7, 0.0, 1.0, color="#f0b0c0"),
        )),
        ("Tulip & Orchid", lambda ax: (
            FlowerCurves.tulip(ax, -0.6, 0.5, 1.0, color="#d03060"),
            FlowerCurves.orchid(ax, 0.7, 0.6, 1.0, color="#c070d0"),
        )),
        ("Garden Scene", lambda ax: CompositionCurves.garden_scene(ax, 0, 0, 1.5)),
        ("Wreath", lambda ax: CompositionCurves.wreath(ax, 0, 0, 1.5, n_flowers=12)),
    ]

    for idx, (name, func) in enumerate(panels):
        ax = axes.flatten()[idx]
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2.5, 2.5)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor("#0d0a1a")
        ax.set_title(name, fontsize=12, color=GOLD, fontfamily="serif")
        func(ax)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out = r"C:\Users\e\Desktop\6756756756756756\flowers_showcase.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0d0a1a")
    plt.close(fig)

    print(f"[OK] Saved: {out}")
    print("[DONE] All botanical curves complete.")
