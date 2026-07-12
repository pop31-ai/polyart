import sys, io, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\e\Desktop\6756756756756756")

import numpy as np

PI = np.pi

from polyart_api import Canvas, PolyObj, PolyCoeffs, TWO_PI
from polyart_biology import VariantGenerator, Phyllotaxis

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "09_flower_variants.png")
c = Canvas(name="FlowerVariants", width=14, height=10,
           xlim=(-7, 7), ylim=(-5, 5), background="#f8f4ec")

c.layer("grid")
for i in range(-6, 7):
    c.line(i, -5, i, 5, color="#e8e0d0", linewidth=0.15, alpha=0.3)
for j in range(-4, 5):
    c.line(-7, j, 7, j, color="#e8e0d0", linewidth=0.15, alpha=0.3)

flowers = VariantGenerator.generate_flower_variants(n=8, seed=42)
f_colors = ["#d94a6e", "#c8a040", "#4a90d9", "#6ab84a",
            "#d46ab8", "#e88040", "#40c8c8", "#8a60d4"]

grid_positions = [
    (-5.0, 2.5), (-1.8, 2.5), (1.4, 2.5), (4.6, 2.5),
    (-5.0, -1.5), (-1.8, -1.5), (1.4, -1.5), (4.6, -1.5),
]

c.layer("flowers")
for idx, (fl, (gx, gy)) in enumerate(zip(flowers, grid_positions)):
    for petal in fl["petals"]:
        px = [gx + v for v in petal["poly_x"]]
        py = [gy + v for v in petal["poly_y"]]
        deg = min(6, len(px) - 1) if len(px) > 2 else 1
        cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
        cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
        c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                      t_range=[0, 1], fill=True,
                      fill_color=f_colors[idx], fill_alpha=0.45,
                      color=f_colors[idx], linewidth=0.8))
    c.circle(gx, gy, 0.12, fill=True, fill_color="#c8a040",
             color="#8a6a20", linewidth=0.5)

c.layer("labels")
for idx, (fl, (gx, gy)) in enumerate(zip(flowers, grid_positions)):
    label = f"{fl['n_petals']}p L={fl['petal_len']:.1f}"
    c.add_formula(label, gx - 0.6, gy - 1.6, fontsize=6, color="#5a4a3a")

c.layer("title_frame")
c.polygon([(-6.8, 4.8), (6.8, 4.8), (6.8, 3.5), (-6.8, 3.5)],
          fill=True, fill_color="#f0e8d8", fill_alpha=0.8,
          color="#c8a040", linewidth=1.0)

c.add_formula("Botanical Flower Variants", -6.3, 4.3, fontsize=12, color="#3a2a1a")
c.add_formula("Parametric Generation - 8 Forms", -6.3, 3.8, fontsize=8, color="#6a5a4a")

c.add_formula("VariantGenerator", -6.3, -4.3, fontsize=7, color="#8a7a6a")

print("[OK] Flower Variants complete")
c.render(OUT, dpi=200)
c.info()
