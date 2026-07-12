import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os, time, traceback

PHI = (1 + np.sqrt(5)) / 2
DARK = "#0d0a1a"
GOLD = "#c8a040"


def _save_gif(fig, update_fn, path, frames=72, fps=24):
    anim = FuncAnimation(fig, update_fn, frames=frames, interval=1000//fps)
    try:
        anim.save(path, writer="pillow", fps=fps)
    except Exception:
        try:
            anim.save(path, writer="ffmpeg", fps=fps)
        except Exception:
            os.makedirs(path + "_frames", exist_ok=True)
            for i in range(frames):
                fig.clear()
                update_fn(i)
                fig.savefig(os.path.join(path + "_frames", "f%03d.png" % i), dpi=72)
            print("    [WARN] saved as frame sequence")
    plt.close(fig)


# ============================================================
#  20 ANIMATED CLIPS
# ============================================================

def video_golden_spiral(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-2.25, 2.25)
        ax.axis("off")
        n = int(10 + frame * 1.5)
        th = np.linspace(0, frame * 0.09, n)
        r = 0.05 * np.exp(0.3 * th)
        x = r * np.cos(th)
        y = r * np.sin(th)
        ax.plot(x, y, color=GOLD, linewidth=2)
        if len(x) > 0:
            ax.plot(x[-1], y[-1], "o", color=GOLD, markersize=4)
    _save_gif(fig, update, path)


def video_flower_bloom(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-2, 2)
        ax.set_ylim(-1.5, 1.5)
        ax.axis("off")
        n_petals = min(frame // 3 + 1, 12)
        for i in range(n_petals):
            ang = i * 2 * np.pi / 12
            th = np.linspace(0, np.pi, 40)
            spread = min(1.0, (frame - i * 3) / 20.0)
            if spread <= 0:
                continue
            r = 0.8 * spread * np.sin(th)
            px = r * np.cos(th + ang)
            py = r * np.sin(th + ang)
            ax.fill(px, py, color="#d94a6e", alpha=0.6)
            ax.plot(px, py, color="#c8a040", linewidth=0.5, alpha=0.8)
        if frame > 36:
            cr = min(0.15, (frame - 36) / 80.0)
            c = plt.Circle((0, 0), cr, color="#ffd700", alpha=0.9)
            ax.add_patch(c)
    _save_gif(fig, update, path)


def video_column_build(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-2, 2)
        ax.set_ylim(-1.5, 2.5)
        ax.axis("off")
        if frame > 0:
            ax.add_patch(plt.Rectangle((-0.6, -1.2), 1.2, 0.3, color="#a09070", alpha=0.8))
        if frame > 6:
            h = min(2.0, (frame - 6) * 0.06)
            ax.add_patch(plt.Rectangle((-0.35, -0.9), 0.7, h, color="#c8b898", alpha=0.7))
            for i in range(5):
                lx = -0.3 + i * 0.15
                ax.plot([lx, lx], [-0.9, -0.9 + h], color="#8a7a60", linewidth=0.5, alpha=0.5)
        if frame > 40:
            cap_h = min(0.4, (frame - 40) * 0.02)
            cy = -0.9 + min(2.0, 34 * 0.06)
            ax.add_patch(plt.Rectangle((-0.5, cy), 1.0, cap_h, color="#c8b898", alpha=0.8))
    _save_gif(fig, update, path)


def video_piranesi_stairs(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-2, 2.5)
        ax.axis("off")
        n = min(frame, 50)
        for i in range(n):
            x = -2.5 + i * 0.1
            y = -1.5 + i * 0.08
            w = 0.5 + 0.02 * i
            h = 0.12
            ax.add_patch(plt.Rectangle((x, y), w, h, color="#c8b898", alpha=0.3 + 0.01*i))
            ax.plot([x, x], [y, y + 0.3], color="#a09070", linewidth=0.5, alpha=0.4)
        for i in range(min(n, 30)):
            ax.plot([-2 + i*0.15, -2 + i*0.15 + 0.3], [2 - i*0.06, 2 - i*0.06 - 0.15],
                    color="#c8b898", linewidth=0.8, alpha=0.3)
    _save_gif(fig, update, path)


def video_turing_pattern(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    np.random.seed(42)
    grid = np.random.rand(60, 80)
    def update(frame):
        nonlocal grid
        ax.clear()
        ax.axis("off")
        kernel = np.ones((3, 3)) / 9
        for _ in range(3):
            conv = np.zeros_like(grid)
            for i in range(1, grid.shape[0]-1):
                for j in range(1, grid.shape[1]-1):
                    conv[i, j] = np.sum(grid[i-1:i+2, j-1:j+2] * kernel)
            grid = conv + 0.02 * np.random.randn(*grid.shape)
            grid = np.clip(grid, 0, 1)
        ax.imshow(grid, cmap="magma", vmin=0, vmax=1, aspect="auto")
    _save_gif(fig, update, path, frames=48)


def video_dna_helix(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.axis("off")
        phase = frame * 0.1
        t = np.linspace(-1.8, 1.8, 80)
        x1 = 0.8 * np.sin(t * 3 + phase)
        x2 = 0.8 * np.sin(t * 3 + phase + np.pi)
        ax.plot(x1, t, color="#4a90d9", linewidth=1.5, alpha=0.8)
        ax.plot(x2, t, color="#d94a6e", linewidth=1.5, alpha=0.8)
        for i in range(0, 80, 6):
            ax.plot([x1[i], x2[i]], [t[i], t[i]], color=GOLD, linewidth=0.8, alpha=0.5)
    _save_gif(fig, update, path)


def video_fractal_tree(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    branches = []
    def build_tree(x, y, angle, length, depth):
        if depth <= 0 or length < 0.05:
            return
        ex = x + length * np.cos(angle)
        ey = y + length * np.sin(angle)
        branches.append((x, y, ex, ey, depth))
        build_tree(ex, ey, angle - 0.5, length * 0.72, depth - 1)
        build_tree(ex, ey, angle + 0.5, length * 0.72, depth - 1)
    build_tree(0, -1.5, np.pi/2, 1.2, 8)
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2, 2)
        ax.axis("off")
        n = min(frame * 3, len(branches))
        for i in range(n):
            x1, y1, x2, y2, d = branches[i]
            c = "#2a6a1a" if d > 2 else "#3a8a2a"
            lw = d * 0.3
            ax.plot([x1, x2], [y1, y2], color=c, linewidth=lw, alpha=0.8)
            if d <= 2 and i < frame * 2:
                ax.plot(x2, y2, "o", color="#ffd700", markersize=1.5, alpha=0.7)
    _save_gif(fig, update, path)


def video_mandala_spin(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-2, 2)
        ax.set_ylim(-1.5, 1.5)
        ax.axis("off")
        for layer in range(5):
            n = 6 + layer * 3
            r = 0.3 + layer * 0.3
            rot = frame * 0.02 * (1 + layer * 0.3)
            for i in range(n):
                ang = i * 2 * np.pi / n + rot
                x = r * np.cos(ang)
                y = r * np.sin(ang)
                sz = 0.08 + 0.02 * np.sin(frame * 0.1 + layer)
                c = plt.Circle((x, y), sz, color=GOLD, alpha=0.4 + layer * 0.08, fill=False, linewidth=0.8)
                ax.add_patch(c)
    _save_gif(fig, update, path)


def video_wave_interference(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-2, 2)
        ax.set_ylim(-1.5, 1.5)
        ax.axis("off")
        xg = np.linspace(-2, 2, 120)
        yg = np.linspace(-1.5, 1.5, 90)
        X, Y = np.meshgrid(xg, yg)
        t = frame * 0.15
        r1 = np.sqrt((X + 1)**2 + Y**2)
        r2 = np.sqrt((X - 1)**2 + Y**2)
        Z = np.sin(r1 * 5 - t) + np.sin(r2 * 5 - t)
        ax.imshow(Z, cmap="coolwarm", vmin=-2, vmax=2, aspect="auto", alpha=0.8)
    _save_gif(fig, update, path, frames=48)


def video_particle_burst(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    np.random.seed(7)
    n = 80
    angles = np.random.uniform(0, 2*np.pi, n)
    speeds = np.random.uniform(0.5, 2.0, n)
    colors = np.random.choice(["#ff4444", "#ff8800", "#ffdd00", "#ffffff"], n)
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-2.25, 2.25)
        ax.axis("off")
        t = frame / 24.0
        fade = max(0, 1 - t / 3.0)
        for i in range(n):
            r = speeds[i] * t
            if r > 3.5:
                continue
            x = r * np.cos(angles[i])
            y = r * np.sin(angles[i])
            sz = max(0.5, 3 * fade)
            ax.plot(x, y, "o", color=colors[i], markersize=sz, alpha=fade * 0.8)
    _save_gif(fig, update, path)


def video_sorting(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    np.random.seed(33)
    arr = np.random.permutation(30) + 1
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-1, 31)
        ax.set_ylim(0, 35)
        ax.axis("off")
        state = arr.copy()
        for i in range(min(frame, 450)):
            j = i % 29
            if state[j] > state[j+1]:
                state[j], state[j+1] = state[j+1], state[j]
        for i, v in enumerate(state):
            c = "#4a90d9" if abs(v - i - 1) > 3 else "#2a8a2a"
            ax.add_patch(plt.Rectangle((i, 0), 0.8, v, color=c, alpha=0.7))
    _save_gif(fig, update, path, frames=60)


def video_cell_divide(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-2, 2)
        ax.set_ylim(-1.5, 1.5)
        ax.axis("off")
        t = frame / 72.0
        if t < 0.4:
            w = 0.6 + t * 0.5
            c = plt.Circle((0, 0), w, color="#d94a6e", alpha=0.5, fill=False, linewidth=2)
            ax.add_patch(c)
        elif t < 0.7:
            progress = (t - 0.4) / 0.3
            sep = progress * 0.8
            w = 0.8 - progress * 0.2
            for sign in [-1, 1]:
                c = plt.Circle((sign * sep, 0), w, color="#d94a6e", alpha=0.5, fill=False, linewidth=2)
                ax.add_patch(c)
            ax.plot([0, 0], [-w, w], color="#d94a6e", linewidth=1, alpha=0.3)
        else:
            sep = 0.8
            for sign in [-1, 1]:
                c = plt.Circle((sign * sep, 0), 0.6, color="#d94a6e", alpha=0.5, fill=False, linewidth=2)
                ax.add_patch(c)
                n = plt.Circle((sign * sep, 0), 0.15, color="#ffd700", alpha=0.6)
                ax.add_patch(n)
    _save_gif(fig, update, path)


def video_morph_polygon(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    def get_shape(n_sides, n_pts=60):
        pts = []
        for i in range(n_pts):
            seg = int(i / n_pts * n_sides) % n_sides
            t = (i / n_pts * n_sides) % 1
            a1 = seg * 2 * np.pi / n_sides - np.pi/2
            a2 = (seg + 1) * 2 * np.pi / n_sides - np.pi/2
            r = 0.8
            x = r * ((1-t)*np.cos(a1) + t*np.cos(a2))
            y = r * ((1-t)*np.sin(a1) + t*np.sin(a2))
            pts.append([x, y])
        return np.array(pts)
    shapes = [get_shape(n) for n in [3, 4, 5, 6, 8, 20]]
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.2, 1.2)
        ax.axis("off")
        idx = frame / 72.0 * (len(shapes) - 1)
        i = int(idx) % len(shapes)
        j = (i + 1) % len(shapes)
        t = idx - int(idx)
        blended = (1 - t) * shapes[i] + t * shapes[j]
        ax.fill(blended[:, 0], blended[:, 1], color=GOLD, alpha=0.6)
        ax.plot(blended[:, 0], blended[:, 1], color=GOLD, linewidth=1.5, alpha=0.9)
    _save_gif(fig, update, path)


def video_constellation(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    np.random.seed(55)
    stars_x = np.random.uniform(-2, 2, 15)
    stars_y = np.random.uniform(-1.5, 1.5, 15)
    connections = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(1,8),(8,9),(9,10),(3,11),(11,12),(12,13),(13,14)]
    def update(frame):
        ax.clear()
        ax.set_facecolor("#050510")
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2, 2)
        ax.axis("off")
        n_stars = min(frame // 2 + 1, 15)
        for i in range(n_stars):
            ax.plot(stars_x[i], stars_y[i], "*", color="#ffffff", markersize=5, alpha=0.9)
        n_lines = min(max(0, (frame - 20) // 2), len(connections))
        for k in range(n_lines):
            i, j = connections[k]
            if i < n_stars and j < n_stars:
                ax.plot([stars_x[i], stars_x[j]], [stars_y[i], stars_y[j]],
                        color=GOLD, linewidth=0.8, alpha=0.6)
    _save_gif(fig, update, path)


def video_heartbeat(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    def ecg(x):
        y = np.zeros_like(x)
        mask = (x > 0.3) & (x < 0.35)
        y[mask] = 0.3
        mask2 = (x > 0.35) & (x < 0.4)
        y[mask2] = -0.5
        mask3 = (x > 0.4) & (x < 0.45)
        y[mask3] = 1.0
        mask4 = (x > 0.45) & (x < 0.5)
        y[mask4] = -0.2
        mask5 = (x > 0.55) & (x < 0.6)
        y[mask5] = 0.15
        return y
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(0, 4)
        ax.set_ylim(-1, 1.5)
        ax.axis("off")
        offset = frame * 0.04
        x = np.linspace(0, 4, 400)
        ecg_full = np.tile(ecg(np.linspace(0, 1, 100)), 4)
        y = ecg_full[:400]
        shift = int(offset * 100) % 100
        y_shifted = np.roll(y, -shift)
        visible = x < (frame / 72.0 * 4)
        ax.plot(x[visible], y_shifted[visible], color="#22ff44", linewidth=1.5, alpha=0.9)
    _save_gif(fig, update, path)


def video_ecosystem(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    np.random.seed(88)
    n_green = 40
    n_red = 8
    n_blue = 15
    gx = np.random.uniform(-2, 2, n_green)
    gy = np.random.uniform(-1.5, 1.5, n_green)
    rx = np.random.uniform(-2, 2, n_red)
    ry = np.random.uniform(-1.5, 1.5, n_red)
    bx = np.random.uniform(-2, 2, n_blue)
    by = np.random.uniform(-1.5, 1.5, n_blue)
    def update(frame):
        ax.clear()
        ax.set_facecolor("#0a1a0a")
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2, 2)
        ax.axis("off")
        t = frame * 0.05
        for x, y in zip(gx + 0.1*np.sin(t + gx*3), gy + 0.1*np.cos(t + gy*5)):
            ax.plot(x, y, "o", color="#22aa22", markersize=3, alpha=0.7)
        for x, y in zip(rx + 0.15*np.sin(t*1.3 + rx*2), ry + 0.15*np.cos(t*1.1 + ry*4)):
            ax.plot(x, y, "o", color="#dd2222", markersize=5, alpha=0.8)
        for x, y in zip(bx + 0.12*np.sin(t*0.8 + bx*4), by + 0.12*np.cos(t*0.9 + by*3)):
            ax.plot(x, y, "o", color="#2266dd", markersize=4, alpha=0.8)
    _save_gif(fig, update, path)


def video_neural_pulse(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    np.random.seed(22)
    nodes_x = np.random.uniform(-2, 2, 20)
    nodes_y = np.random.uniform(-1.5, 1.5, 20)
    edges = []
    for i in range(20):
        for j in range(i+1, 20):
            d = np.sqrt((nodes_x[i]-nodes_x[j])**2 + (nodes_y[i]-nodes_y[j])**2)
            if d < 1.2:
                edges.append((i, j))
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2, 2)
        ax.axis("off")
        pulse_pos = (frame / 72.0) % 1.0
        for i, j in edges:
            ax.plot([nodes_x[i], nodes_x[j]], [nodes_y[i], nodes_y[j]],
                    color="#334", linewidth=0.5, alpha=0.4)
        for i, (x, y) in enumerate(zip(nodes_x, nodes_y)):
            bright = 0.3 + 0.7 * max(0, 1 - abs(pulse_pos - i/20) * 5)
            c = plt.Circle((x, y), 0.06, color=GOLD, alpha=bright)
            ax.add_patch(c)
        for i, j in edges[:3]:
            px = nodes_x[i] + pulse_pos * (nodes_x[j] - nodes_x[i])
            py = nodes_y[i] + pulse_pos * (nodes_y[j] - nodes_y[i])
            ax.plot(px, py, "o", color="#ffffff", markersize=2, alpha=0.9)
    _save_gif(fig, update, path)


def video_orbits(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    def update(frame):
        ax.clear()
        ax.set_facecolor("#050510")
        ax.set_xlim(-2, 2)
        ax.set_ylim(-1.5, 1.5)
        ax.axis("off")
        c = plt.Circle((0, 0), 0.15, color="#ffaa00", alpha=0.9)
        ax.add_patch(c)
        speeds = [0.02, 0.015, 0.01, 0.007]
        radii = [0.4, 0.65, 0.95, 1.25]
        cs = ["#aaaaaa", "#4a90d9", "#22aa22", "#dd4444"]
        szs = [2, 4, 3.5, 3]
        for sp, r, c2, sz in zip(speeds, radii, cs, szs):
            ang = frame * sp
            orbit_th = np.linspace(0, 2*np.pi, 100)
            ax.plot(r*np.cos(orbit_th), r*np.sin(orbit_th), color=c2, linewidth=0.3, alpha=0.3)
            px = r * np.cos(ang)
            py = r * np.sin(ang)
            ax.plot(px, py, "o", color=c2, markersize=sz, alpha=0.9)
    _save_gif(fig, update, path)


def video_crystal_grow(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    np.random.seed(44)
    facets = []
    for i in range(60):
        ang = np.random.uniform(0, 2*np.pi)
        r = np.random.uniform(0.1, 1.5)
        facets.append((ang, r, np.random.uniform(0.2, 0.8)))
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-2, 2)
        ax.set_ylim(-1.5, 1.5)
        ax.axis("off")
        n = min(frame, len(facets))
        for i in range(n):
            ang, r, alpha = facets[i]
            grow = min(1.0, (frame - i) / 10.0) if frame > i else 0
            if grow <= 0:
                continue
            r2 = r * grow
            x1, y1 = 0, 0
            x2 = r2 * np.cos(ang)
            y2 = r2 * np.sin(ang)
            ax.plot([x1, x2], [y1, y2], color="#88ccff", linewidth=0.5, alpha=alpha * grow)
            if i < n - 1:
                ang2, r2_2, _ = facets[(i+1) % len(facets)]
                x3 = min(r2, r2_2) * np.cos(ang2)
                y3 = min(r2, r2_2) * np.sin(ang2)
                ax.fill([0, x2, x3], [0, y2, y3], color="#88ccff", alpha=0.1 * grow)
        c = plt.Circle((0, 0), 0.05, color="#ffffff", alpha=0.8)
        ax.add_patch(c)
    _save_gif(fig, update, path)


def video_title_sequence(path):
    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=72)
    letters = list("POLYART")
    starts = [(-3, 1), (3, -1), (-2, -2), (2, 2), (-1, 3), (1, -3), (0, 4)]
    def update(frame):
        ax.clear()
        ax.set_facecolor(DARK)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-2.25, 2.25)
        ax.axis("off")
        t = min(1.0, frame / 40.0)
        for i, (letter, start) in enumerate(zip(letters, starts)):
            delay = i * 0.08
            lt = max(0, min(1, (t - delay) / 0.5))
            x = start[0] * (1 - lt) + (i * 0.7 - 2.1) * lt
            y = start[1] * (1 - lt) + 0 * lt
            alpha = lt
            ax.text(x, y, letter, fontsize=24, color=GOLD, alpha=alpha,
                    ha="center", va="center", fontweight="bold",
                    fontfamily="monospace")
        if frame > 50:
            shine = (frame - 50) / 22.0
            ax.plot([-2.5, 2.5], [-0.5, -0.5], color=GOLD, linewidth=0.5, alpha=shine * 0.5)
    _save_gif(fig, update, path)


ALL_VIDEOS = [
    ("01_golden_spiral.gif", video_golden_spiral),
    ("02_flower_bloom.gif", video_flower_bloom),
    ("03_column_build.gif", video_column_build),
    ("04_piranesi_stairs.gif", video_piranesi_stairs),
    ("05_turing_pattern.gif", video_turing_pattern),
    ("06_dna_helix.gif", video_dna_helix),
    ("07_fractal_tree.gif", video_fractal_tree),
    ("08_mandala_spin.gif", video_mandala_spin),
    ("09_wave_interference.gif", video_wave_interference),
    ("10_particle_burst.gif", video_particle_burst),
    ("11_sorting.gif", video_sorting),
    ("12_cell_divide.gif", video_cell_divide),
    ("13_morph_polygon.gif", video_morph_polygon),
    ("14_constellation.gif", video_constellation),
    ("15_heartbeat.gif", video_heartbeat),
    ("16_ecosystem.gif", video_ecosystem),
    ("17_neural_pulse.gif", video_neural_pulse),
    ("18_orbits.gif", video_orbits),
    ("19_crystal_grow.gif", video_crystal_grow),
    ("20_title_sequence.gif", video_title_sequence),
]


if __name__ == "__main__":
    out_dir = "videos_output"
    os.makedirs(out_dir, exist_ok=True)
    print("[START] Generating %d animated clips..." % len(ALL_VIDEOS))
    t0 = time.time()
    ok = 0
    fail = 0
    for i, (name, fn) in enumerate(ALL_VIDEOS):
        path = os.path.join(out_dir, name)
        print("[%02d/%02d] %s ..." % (i+1, len(ALL_VIDEOS), name), end=" ", flush=True)
        try:
            fn(path)
            sz = os.path.getsize(path)
            print("[OK] %d KB" % (sz // 1024))
            ok += 1
        except Exception as e:
            print("[FAIL] %s" % str(e)[:60])
            traceback.print_exc()
            fail += 1
    elapsed = time.time() - t0
    print("[DONE] %d ok, %d fail, %.1fs total" % (ok, fail, elapsed))
    print("[DIR] %s/" % os.path.abspath(out_dir))
