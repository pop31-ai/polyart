import sys, io, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\e\Desktop\6756756756756756")

import numpy as np

PI = np.pi

from polyart_api import Canvas, PolyObj, PolyCoeffs, TWO_PI
from polyart_sculpture import PiranesiArch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "02_piranesi_carcere.png")
c = Canvas(name="PiranesiCarcere", width=14, height=10,
           xlim=(-7, 7), ylim=(-5, 5), background="#08080f")

c.layer("deep_bg")
for i in range(20):
    x = np.random.uniform(-6.5, 6.5)
    y = np.random.uniform(-4.5, 4.5)
    c.circle(x, y, 0.012, fill=True, fill_color="#ffffff",
             fill_alpha=np.random.uniform(0.05, 0.25))

c.layer("outer_arches")
for i in range(6):
    scale = 1.0 - i * 0.12
    arches = PiranesiArch.arch(0, -2, 13 * scale, 9 * scale,
                               depth=0.2, n_arches=4)
    PiranesiArch.render_piranesi(c, arches, line_color="#58506a")

c.layer("colonnade_left")
PiranesiArch.render_piranesi(c, PiranesiArch.colonnade(
    -5, -4.5, n_cols=10, spacing=0.7, col_h=4.5,
    col_r=0.07, perspective=0.35), line_color="#706888")

c.layer("colonnade_right")
PiranesiArch.render_piranesi(c, PiranesiArch.colonnade(
    5, -4.5, n_cols=10, spacing=0.7, col_h=4.5,
    col_r=0.07, perspective=0.35), line_color="#706888")

c.layer("staircase_main")
PiranesiArch.render_piranesi(c, PiranesiArch.staircase(
    0, -4.5, 8, 5, n_steps=18, perspective=0.35), line_color="#9890a8")

c.layer("staircase_left")
PiranesiArch.render_piranesi(c, PiranesiArch.staircase(
    -4, -2, 4, 3, n_steps=10, perspective=0.25), line_color="#787088")

c.layer("staircase_right")
PiranesiArch.render_piranesi(c, PiranesiArch.staircase(
    4, -2, 4, 3, n_steps=10, perspective=0.25), line_color="#787088")

c.layer("vaults")
PiranesiArch.render_piranesi(c, PiranesiArch.vault(
    0, 1, 12, 3, n_ribs=8), line_color="#6860a0")
PiranesiArch.render_piranesi(c, PiranesiArch.vault(
    -3, 2, 6, 2.5, n_ribs=5), line_color="#5850a0")
PiranesiArch.render_piranesi(c, PiranesiArch.vault(
    3, 2, 6, 2.5, n_ribs=5), line_color="#5850a0")

c.layer("impossible_stairs")
PiranesiArch.render_piranesi(c, PiranesiArch.impossible_stairs(
    0, 0, size=2.0, loops=3), line_color="#b8b0d0")

c.layer("chains")
for k in range(4):
    cx_k = -3 + k * 2
    for i in range(8):
        y = 3.5 - i * 0.25
        r = 0.08 + 0.02 * np.sin(i * 0.7)
        c.circle(cx_k + 0.05 * np.sin(i), y, r,
                 fill=False, color="#8888a8", linewidth=0.6, alpha=0.5)

c.layer("fg_detail")
for i in range(30):
    x = np.random.uniform(-6, 6)
    y = np.random.uniform(-4.5, -3)
    c.line(x, y, x + np.random.uniform(-0.3, 0.3), y + np.random.uniform(0.1, 0.4),
           color="#504868", linewidth=0.3, alpha=0.4)

c.add_formula("Carceri d'Invenzione", -6.5, 4.5, fontsize=11, color="#8878a8")
c.add_formula("G.B. Piranesi", -6.5, 4.0, fontsize=8, color="#685888")

print("[OK] Piranesi Carcere complete")
c.render(OUT, dpi=200)
c.info()
