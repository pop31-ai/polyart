import sys, io, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\e\Desktop\6756756756756756")

import numpy as np

PI = np.pi

from polyart_api import Canvas, PolyObj, PolyCoeffs, TWO_PI, PHI, GreekLines
from polyart_sculpture import LatheBody

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "08_greek_amphora_gallery.png")
c = Canvas(name="GreekAmphoraGallery", width=16, height=10,
           xlim=(-8, 8), ylim=(-5, 5), background="#1a1a24")

c.layer("bg_columns")
for i in range(17):
    x = -8 + i
    c.line(x, -5, x, 5, color="#22222e", linewidth=0.3, alpha=0.4)
for j in range(11):
    y = -5 + j
    c.line(-8, y, 8, y, color="#22222e", linewidth=0.3, alpha=0.4)

c.layer("pedestal")
for px in [-5.5, -2.5, 0, 2.5, 5.5]:
    c.polygon([(px - 0.6, -4.5), (px + 0.6, -4.5),
               (px + 0.5, -4.2), (px - 0.5, -4.2)],
              fill=True, fill_color="#3a3a4a", fill_alpha=0.7,
              color="#5a5a6a", linewidth=0.8)

vessels = [
    ("amphora", LatheBody.amphora(height=4.0, belly_width=0.8, neck_width=0.2)),
    ("krater", LatheBody.greek_krater(height=3.5, rim_width=1.0, body_width=0.75)),
    ("oinochoe", LatheBody.oinochoe(height=3.0)),
    ("column", LatheBody.column_fluted(height=4.5, radius=0.25, n_flutes=18)),
    ("amphora", LatheBody.amphora(height=3.8, belly_width=0.7, neck_width=0.22)),
]
vessel_x = [-5.5, -2.5, 0, 2.5, 5.5]
vessel_colors = [
    ("#c8a088", "#f0e0d0", "#6a4a3a"),
    ("#d4b898", "#f5efe0", "#7a6a5a"),
    ("#c89878", "#e8d8c0", "#5a4a3a"),
    ("#e8dcc8", "#ffffff", "#8a7a6a"),
    ("#d0b898", "#f0e8d8", "#6a5a4a"),
]

c.layer("vessels")
for (name, body), vx, (base, high, shad) in zip(vessels, vessel_x, vessel_colors):
    LatheBody.render_lathe(c, body, cx=vx, cy=-4.2, n_shades=9,
                           base_color=base, highlight=high, shadow=shad)

c.layer("meander_borders")
for vx in vessel_x:
    GreekLines.meander(vx - 0.6, -4.0, n_segments=4, step=0.15, height=0.05)

c.layer("labels")
labels = ["Amphora", "Krater", "Oinochoe", "Column", "Amphora II"]
for vx, label in zip(vessel_x, labels):
    c.add_formula(label, vx - 0.5, -4.8, fontsize=7, color="#8a8a9a")

c.layer("spotlights")
for vx in vessel_x:
    for i in range(5):
        r = 0.3 + i * 0.15
        c.circle(vx, 1, r, fill=True, fill_color="#c8a040",
                 fill_alpha=0.02, color="#c8a040", linewidth=0.1)

c.layer("handles")
for vx in [-5.5, -2.5, 0, 2.5]:
    for side in [-1, 1]:
        t = np.linspace(0, 1, 40)
        hx = vx + side * (0.5 + 0.3 * np.sin(np.pi * t))
        hy = 0.5 + 1.5 * t
        deg = min(5, 39)
        cx_l = np.polyfit(t, hx, deg).tolist()
        cy_l = np.polyfit(t, hy, deg).tolist()
        c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                      t_range=[0, 1], color="#8a7a6a", linewidth=1.5, alpha=0.6))

c.add_formula("Greek Vessel Gallery", -7.5, 4.5, fontsize=11, color="#c8a040")
c.add_formula("Lathe-Shaded Pottery", -7.5, 4.0, fontsize=8, color="#8a8a9a")

print("[OK] Greek Amphora Gallery complete")
c.render(OUT, dpi=200)
c.info()
