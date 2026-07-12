import sys, io, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\e\Desktop\6756756756756756")

import numpy as np

PI = np.pi

from polyart_api import Canvas, PolyObj, PolyCoeffs, TWO_PI, PHI, GOLDEN_ANGLE, SQRT3
from polyart_biology import TuringPatterns

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "06_turing_savanna.png")
c = Canvas(name="TuringSavanna", width=14, height=10,
           xlim=(-7, 7), ylim=(-5, 5), background="#1a1a2e")

c.layer("sky")
for i in range(10):
    y_top = 5 - i
    b = int(60 - i * 4)
    g = int(40 + i * 2)
    c.line(-7, y_top, 7, y_top, color=f"#2a{g:02x}{b:02x}", linewidth=8, alpha=0.5)

c.layer("hexagonal_earth")
hex_cells = TuringPatterns.hexagonal_packing(cx=0, cy=-3, size=6, cell_r=0.5, seed=42)
for h in hex_cells:
    t = np.linspace(0, TWO_PI, 7)
    x = h["cx"] + h["r"] * np.cos(t)
    y = h["cy"] + h["r"] * np.sin(t)
    deg = min(5, 6)
    c.add(PolyObj(np.polyfit(t / TWO_PI, x, deg).tolist(),
                  np.polyfit(t / TWO_PI, y, deg).tolist(),
                  t_range=[0, TWO_PI], fill=True,
                  fill_color="#4a3a1a", fill_alpha=0.4,
                  color="#6a5a2a", linewidth=0.5))

c.layer("leopard_spots")
spots = TuringPatterns.spot_pattern(cx=-3, cy=0, size=5, n_spots=25,
                                    spot_r=0.2, seed=42)
for s in spots:
    t = np.linspace(0, TWO_PI, 30)
    x = s["cx"] + s["r"] * s["deform_x"] * np.cos(t + s["angle"])
    y = s["cy"] + s["r"] * s["deform_y"] * np.sin(t + s["angle"])
    deg = min(5, 29)
    c.add(PolyObj(np.polyfit(t / TWO_PI, x, deg).tolist(),
                  np.polyfit(t / TWO_PI, y, deg).tolist(),
                  t_range=[0, TWO_PI], fill=True,
                  fill_color="#8a6a20", fill_alpha=0.6,
                  color="#6a4a10", linewidth=0.4))

c.layer("zebra_stripes")
stripes = TuringPatterns.stripe_pattern(cx=3, cy=0, width=5, height=5,
                                        n_stripes=12, waviness=0.4, seed=7)
for s in stripes:
    c.add(PolyObj(s["poly_x"], s["poly_y"], t_range=[0, 1],
                  color="#e0e0e0", linewidth=s["width"] * 10, alpha=0.5))

c.layer("golden_grass")
for i in range(60):
    x = np.random.uniform(-6.5, 6.5)
    y_base = -4.5 + np.random.uniform(0, 1.5)
    h = np.random.uniform(0.3, 0.8)
    lean = np.random.uniform(-0.15, 0.15)
    c.line(x, y_base, x + lean, y_base + h,
           color="#c8a040", linewidth=0.5, alpha=0.6)
    if np.random.random() > 0.7:
        c.circle(x + lean * 0.5, y_base + h, 0.03, fill=True,
                 fill_color="#dab848", fill_alpha=0.5)

c.layer("silhouette_animals")
for ax, ay, sz in [(-5, -1, 0.5), (-2, -1.5, 0.4), (4, -1.2, 0.6), (6, -2, 0.35)]:
    body_x = [ax - sz, ax - sz * 0.7, ax + sz * 0.7, ax + sz,
              ax + sz * 0.7, ax - sz * 0.7, ax - sz]
    body_y = [ay, ay + sz * 0.3, ay + sz * 0.3, ay,
              ay - sz * 0.2, ay - sz * 0.2, ay]
    c.polygon(list(zip(body_x, body_y)), fill=True,
              fill_color="#1a1028", fill_alpha=0.8, color="#2a2038", linewidth=0.5)
    c.line(ax + sz * 0.3, ay + sz * 0.3, ax + sz * 0.5, ay + sz * 0.8,
           color="#1a1028", linewidth=1.5)
    for dx in [-sz * 0.5, -sz * 0.2, sz * 0.2, sz * 0.5]:
        c.line(ax + dx, ay - sz * 0.2, ax + dx, ay - sz * 0.6,
               color="#1a1028", linewidth=0.8)

c.layer("spiral_pattern_center")
arms = TuringPatterns.spiral_pattern(cx=0, cy=1, n_arms=4, r_max=2, turns=2)
for arm in arms:
    c.add(PolyObj(arm["poly_x"], arm["poly_y"], t_range=[0, 1],
                  color="#c8a040", linewidth=1.0, alpha=0.4))

c.add_formula("Reaction-Diffusion Patterns", -6.5, 4.5, fontsize=10, color="#c8b898")
c.add_formula("A. Turing 1952", -6.5, 4.0, fontsize=7, color="#8878a8")

print("[OK] Turing Savanna complete")
c.render(OUT, dpi=200)
c.info()
