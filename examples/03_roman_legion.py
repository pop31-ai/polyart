import sys, io, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\e\Desktop\6756756756756756")

import numpy as np

PI = np.pi

from polyart_api import Canvas, PolyObj, PolyCoeffs, TWO_PI
from polyart_sculpture import RomanSymbols

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "03_roman_legion.png")
c = Canvas(name="RomanLegion", width=14, height=10,
           xlim=(-7, 7), ylim=(-5, 5), background="#5a0a0a")

c.layer("bg_pattern")
for i in range(15):
    x = -7 + i
    c.line(x, -5, x, 5, color="#6a1a1a", linewidth=0.3, alpha=0.4)
for j in range(11):
    y = -5 + j
    c.line(-7, y, 7, y, color="#6a1a1a", linewidth=0.3, alpha=0.4)

c.layer("testudo_formation")
for row in range(4):
    for col in range(5):
        sx = -4.5 + col * 1.2
        sy = -2.5 + row * 1.0
        for el in RomanSymbols.shield(sx, sy, width=0.9, height=1.1):
            px, py = el["poly_x"], el["poly_y"]
            deg = min(6, len(px) - 1) if len(px) > 2 else 1
            cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
            cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
            c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                          t_range=[0, 1], fill=True, fill_color="#8b0000",
                          fill_alpha=0.6, color="#c8a040", linewidth=0.8))

c.layer("eagle_center")
for el in RomanSymbols.eagle(cx=0, cy=3.2, wingspan=4.0):
    px, py = el["poly_x"], el["poly_y"]
    deg = min(6, len(px) - 1) if len(px) > 2 else 1
    cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
    cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
    c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                  t_range=[0, 1], fill=True, fill_color="#c8a040",
                  fill_alpha=0.4, color="#e8c860", linewidth=2.0))

c.layer("laurel_wreath")
for el in RomanSymbols.laurel_wreath(cx=0, cy=3.2, radius=2.5, n_leaves=28):
    px, py = el["poly_x"], el["poly_y"]
    deg = min(6, len(px) - 1) if len(px) > 2 else 1
    cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
    cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
    c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                  t_range=[0, 1], color="#2d5a1e", linewidth=1.0))

c.layer("spqr_banners")
for el in RomanSymbols.spqr_banner(cx=-5.5, cy=1.5, width=2.5, height=1.5):
    px, py = el["poly_x"], el["poly_y"]
    deg = min(5, len(px) - 1) if len(px) > 2 else 1
    cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
    cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
    c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                  t_range=[0, 1], fill=True, fill_color="#8b0000",
                  fill_alpha=0.5, color="#c8a040", linewidth=1.5))

for el in RomanSymbols.spqr_banner(cx=5.5, cy=1.5, width=2.5, height=1.5):
    px, py = el["poly_x"], el["poly_y"]
    deg = min(5, len(px) - 1) if len(px) > 2 else 1
    cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
    cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
    c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                  t_range=[0, 1], fill=True, fill_color="#8b0000",
                  fill_alpha=0.5, color="#c8a040", linewidth=1.5))

c.layer("gladii")
for el in RomanSymbols.gladius(cx=-5.5, cy=-2.5, length=2.0):
    px, py = el["poly_x"], el["poly_y"]
    deg = min(6, len(px) - 1) if len(px) > 2 else 1
    cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
    cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
    c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                  t_range=[0, 1], color="#c0c0d0", linewidth=1.2))

for el in RomanSymbols.gladius(cx=5.5, cy=-2.5, length=2.0):
    px, py = el["poly_x"], el["poly_y"]
    deg = min(6, len(px) - 1) if len(px) > 2 else 1
    cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
    cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
    c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                  t_range=[0, 1], color="#c0c0d0", linewidth=1.2))

c.add_formula("SPQR", -0.5, 4.5, fontsize=18, color="#c8a040")
c.add_formula("LEGIO VII GEMINA", -2, -4.5, fontsize=9, color="#e8c860")

print("[OK] Roman Legion complete")
c.render(OUT, dpi=200)
c.info()
