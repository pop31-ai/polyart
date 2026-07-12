import sys, io, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\e\Desktop\6756756756756756")

import numpy as np

PI = np.pi

from polyart_api import Canvas, PolyObj, PolyCoeffs, TWO_PI, PHI
from polyart_biology import Phyllotaxis, TuringPatterns

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "05_procedural_forest.png")
c = Canvas(name="ProceduralForest", width=14, height=10,
           xlim=(-7, 7), ylim=(-5, 5), background="#87CEEB")

c.layer("sky_gradient")
for i in range(12):
    y_top = 5 - i * 0.8
    r_val = int(135 + i * 5)
    g_val = int(206 - i * 8)
    b_val = int(235 - i * 10)
    col = f"#{min(r_val,255):02x}{max(g_val,80):02x}{max(b_val,60):02x}"
    c.line(-7, y_top, 7, y_top, color=col, linewidth=15, alpha=0.4)

c.layer("sun")
c.circle(5, 4, 0.8, fill=True, fill_color="#FFE44D", fill_alpha=0.9,
         color="#FFD700", linewidth=0.5)
for i in range(12):
    a = i * TWO_PI / 12
    c.line(5 + 1.0 * np.cos(a), 4 + 1.0 * np.sin(a),
           5 + 1.8 * np.cos(a), 4 + 1.8 * np.sin(a),
           color="#FFD700", linewidth=0.8, alpha=0.5)
    c.line(5 + 2.0 * np.cos(a), 4 + 2.0 * np.sin(a),
           5 + 2.6 * np.cos(a), 4 + 2.6 * np.sin(a),
           color="#FFE44D", linewidth=0.4, alpha=0.3)

c.layer("clouds")
for cx_c, cy_c in [(-4, 3.5), (1, 4.2), (-1, 3.0)]:
    for dx, dy in [(0, 0), (0.4, 0.1), (-0.3, 0.05), (0.15, 0.15)]:
        c.circle(cx_c + dx, cy_c + dy, 0.4, fill=True,
                 fill_color="#ffffff", fill_alpha=0.6)

c.layer("ground")
for i in range(20):
    y = -3.5 + i * 0.15
    x_off = np.random.uniform(-0.2, 0.2)
    green = int(80 + i * 4)
    c.line(-7 + x_off, y, 7 + x_off, y,
           color=f"#2a{green:02x}1a", linewidth=2, alpha=0.5)

c.layer("grass")
for i in range(80):
    x = np.random.uniform(-6.5, 6.5)
    y = -3.5 + np.random.uniform(-0.3, 0.1)
    h = np.random.uniform(0.15, 0.4)
    lean = np.random.uniform(-0.1, 0.1)
    c.line(x, y, x + lean, y + h,
           color="#3a6a2a", linewidth=0.5, alpha=0.6)

c.layer("trees")
tree_x_positions = [-5.5, -3.8, -2.0, -0.5, 0.8, 2.2, 3.5, 4.8, 5.8, 6.5]
tree_seeds = [42, 73, 17, 99, 55, 31, 88, 14, 66, 111]
tree_heights = [2.5, 3.2, 2.0, 2.8, 3.5, 2.2, 3.0, 2.6, 3.3, 2.1]

for idx, (tx, seed, th) in enumerate(zip(tree_x_positions, tree_seeds, tree_heights)):
    base_y = -3.5
    branches = Phyllotaxis.branching_tree(
        cx=tx, cy=base_y, length=th * 0.4, angle=PI / 2,
        depth=5, spread=0.35 + 0.1 * np.sin(idx),
        decay=0.7 + 0.05 * np.cos(idx * PHI), seed=seed)
    for br in branches:
        lw = br["width"] * 18
        alpha = 0.3 + 0.7 * br["age"]
        c.add(PolyObj(br["poly_x"], br["poly_y"], t_range=[0, 1],
                      color="#3a2210", linewidth=lw, alpha=alpha))

c.layer("canopy")
for tx, th in zip(tree_x_positions, tree_heights):
    base_y = -3.5 + th * 0.6
    for j in range(5):
        cx_l = tx + np.random.uniform(-0.6, 0.6)
        cy_l = base_y + np.random.uniform(-0.3, 0.5)
        r = np.random.uniform(0.3, 0.7)
        g = int(50 + np.random.randint(0, 40))
        c.circle(cx_l, cy_l, r, fill=True,
                 fill_color=f"#2a{g:02x}1a", fill_alpha=0.5,
                 color=f"#1a{g-10:02x}10", linewidth=0.3)

c.layer("flowers")
for i in range(15):
    x = np.random.uniform(-6, 6)
    y = -3.5 + np.random.uniform(0, 0.2)
    c.flower(x, y, scale=0.06, n=np.random.choice([4, 5, 6]),
             fill=True, fill_color=np.random.choice(["#e84060", "#e8e040", "#e060e0"]),
             fill_alpha=0.7)

c.add_formula("Procedural Generation", -6.5, 4.5, fontsize=10, color="#1a3a10")
c.add_formula("10 Unique Seeds", -6.5, 4.0, fontsize=7, color="#2a4a20")

print("[OK] Procedural Forest complete")
c.render(OUT, dpi=200)
c.info()
