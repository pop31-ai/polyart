import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import numpy as np
from polyart_api import Canvas, PolyObj, GreekLines, GoldenRatio, PHI, TWO_PI, GOLDEN_ANGLE

c = Canvas(name="LinesComposition", xlim=(-6, 6), ylim=(-6, 6), background="#0d0d1a")

c.layer("background_stars")
for i in range(80):
    x = np.random.uniform(-5.8, 5.8)
    y = np.random.uniform(-5.8, 5.8)
    r = np.random.uniform(0.01, 0.04)
    c.circle(x, y, r, fill=True, fill_color="#ffffff", fill_alpha=np.random.uniform(0.2, 0.7))

c.layer("golden_spiral")
c.golden_spiral(0, 0, a=0.15, turns=5, color="#c8a040", linewidth=2.5)
c.golden_rectangle(-2.5, -2.5, 5, color="#c8a040", linewidth=1, alpha=0.4)

c.layer("radial_lines")
for i in range(24):
    angle = i * TWO_PI / 24
    x2 = 5.5 * np.cos(angle)
    y2 = 5.5 * np.sin(angle)
    c.line(0, 0, x2, y2, color="#ffffff", linewidth=0.3, alpha=0.15)

c.layer("concentric_circles")
for i in range(1, 12):
    r = i * 0.4
    c.circle(0, 0, r, color="#c8a040" if i % 3 == 0 else "#4a90d9" if i % 3 == 1 else "#d94a6e",
             linewidth=0.8, alpha=0.5)

c.layer("lissajous")
c.lissajous(3, 3, 3, 2, delta=np.pi/4, color="#d94a6e", linewidth=1.5, alpha=0.7, scale=0.8)
c.lissajous(-3, 3, 5, 4, delta=np.pi/4, color="#4ad9a0", linewidth=1.5, alpha=0.7, scale=0.8)
c.lissajous(3, -3, 5, 3, delta=np.pi/4, color="#a040c8", linewidth=1.5, alpha=0.7, scale=0.8)

c.layer("volute_ions")
for cx, cy in [(-3.5, -3.5), (3.5, -3.5), (-3.5, 3.5), (3.5, 3.5)]:
    c.volute(cx, cy, a=0.6, turns=2, color="#c8a040", linewidth=1.5, alpha=0.5)

c.layer("flowers")
c.flower(0, 0, scale=0.5, n=6, fill=False, color="#c8a040", linewidth=1.2, alpha=0.6)
c.flower(-3, 0, scale=0.5, n=5, fill=False, color="#d94a6e", linewidth=1.2, alpha=0.6)
c.flower(3, 0, scale=0.5, n=7, fill=False, color="#4a90d9", linewidth=1.2, alpha=0.6)
c.flower(0, -3, scale=0.5, n=8, fill=False, color="#4ad9a0", linewidth=1.2, alpha=0.6)
c.flower(0, 3, scale=0.5, n=4, fill=False, color="#a040c8", linewidth=1.2, alpha=0.6)

c.layer("stars_at_center")
c.star(0, 0, scale=0.8, n=5, fill=False, color="#c8a040", linewidth=0.8, alpha=0.4)
c.star(0, 0, scale=1.2, n=5, fill=False, color="#c8a040", linewidth=0.8, alpha=0.4)
c.star(0, 0, scale=1.6, n=5, fill=False, color="#c8a040", linewidth=0.8, alpha=0.4)

c.layer("wave_rings")
for r in [2.0, 3.0, 4.0]:
    pts = 300
    t = np.linspace(0, TWO_PI, pts)
    wobble = r + 0.1 * np.sin(6 * t)
    wx = wobble * np.cos(t)
    wy = wobble * np.sin(t)
    deg = 20
    cx_list = np.polyfit(t / TWO_PI, wx, deg).tolist()
    cy_list = np.polyfit(t / TWO_PI, wy, deg).tolist()
    c.add(PolyObj(list(reversed(cx_list)), list(reversed(cy_list)), color="#d94a6e", linewidth=0.8, alpha=0.3, t_range=[0, 1]))

c.layer("meander_border")
segs = GreekLines.greek_key_border(-5, -5, length=10, height=0.2, repeat=8)
for px, py in segs:
    c.add(PolyObj(list(reversed(px)), list(reversed(py)), color="#4a90d9", linewidth=1.2, alpha=0.6))
segs2 = GreekLines.greek_key_border(-5, 4.8, length=10, height=0.2, repeat=8)
for px, py in segs2:
    c.add(PolyObj(list(reversed(px)), list(reversed(py)), color="#4a90d9", linewidth=1.2, alpha=0.6))

c.save("lines_composition.polyart")
c.render("lines_composition.png", dpi=200)
c.info()
print("DONE: lines_composition.png")
