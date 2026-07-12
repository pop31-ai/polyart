import sys, io, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\e\Desktop\6756756756756756")

import numpy as np

PI = np.pi

from polyart_api import Canvas, PolyObj, PolyCoeffs, PHI, PHI_INV, TWO_PI, GOLDEN_ANGLE
from polyart_biology import Phyllotaxis, TuringPatterns

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "01_golden_mandala.png")
c = Canvas(name="GoldenMandala", width=12, height=12,
           xlim=(-6, 6), ylim=(-6, 6), background="#0a0812")

c.layer("bg_glow")
for i in range(12):
    r = 5.8 - i * 0.45
    c.circle(0, 0, r, fill=True, fill_color="#1a1028", fill_alpha=0.25 + i * 0.03,
             color="#2a1838", linewidth=0.3)

c.layer("concentric_circles")
for i in range(1, 30):
    r = i * 0.19
    gold = "#c8a040" if i % 3 == 0 else "#8a7040" if i % 2 == 0 else "#a08838"
    c.circle(0, 0, r, color=gold, linewidth=0.3, alpha=0.4 + 0.2 * (i % 2))

c.layer("dotted_rings")
for ring in range(8):
    r = 0.5 + ring * 0.65
    n_dots = 12 + ring * 6
    for j in range(n_dots):
        a = j * TWO_PI / n_dots
        dx = r * np.cos(a)
        dy = r * np.sin(a)
        sz = 0.025 + 0.01 * np.sin(j * 0.5)
        c.circle(dx, dy, sz, fill=True, fill_color="#dab848",
                 fill_alpha=min(0.9, 0.4 + 0.03 * ring), color="#c8a040", linewidth=0.1)

c.layer("golden_spirals")
for k in range(8):
    angle_off = k * TWO_PI / 8
    a_val = 0.04
    b_val = np.log(PHI) / (np.pi / 2)
    thetas = np.linspace(0, 5 * np.pi, 500)
    radii = a_val * np.exp(b_val * thetas)
    mask = radii < 5.5
    thetas_m = thetas[mask]
    radii_m = radii[mask]
    sx = radii_m * np.cos(thetas_m + angle_off)
    sy = radii_m * np.sin(thetas_m + angle_off)
    deg = min(16, len(sx) - 1)
    tn = np.linspace(0, 1, len(sx))
    cx_c = np.polyfit(tn, sx, deg)
    cy_c = np.polyfit(tn, sy, deg)
    c.add(PolyObj(list(reversed(cx_c)), list(reversed(cy_c)),
                  t_range=[0, 1], color="#d4a848", linewidth=0.8, alpha=0.6))

c.layer("fibonacci_flowers")
for ring in range(5):
    n_pts = 13 + ring * 8
    radius = 0.6 + ring * 0.9
    xs, ys = Phyllotaxis.golden_points(n=n_pts, scale=radius, cx=0, cy=0)
    for x, y in zip(xs, ys):
        sz = 0.04 + 0.02 * np.sin(ring * PHI)
        c.flower(x, y, scale=sz, n=5 + ring % 3,
                 fill=True, fill_color="#d4a860", fill_alpha=0.45,
                 color="#c8a040", linewidth=0.2)

c.layer("phi_circles")
for i in range(30):
    angle = i * GOLDEN_ANGLE
    r = 0.2 * np.sqrt(i + 1) * PHI
    if r < 5.5:
        cx_p = r * np.cos(angle)
        cy_p = r * np.sin(angle)
        sz = 0.08 + 0.05 * np.sin(i * 1.3)
        c.circle(cx_p, cy_p, sz, fill=True, fill_color="#e8c868",
                 fill_alpha=0.35, color="#c8a040", linewidth=0.3)

c.layer("mandala_petals")
for ring in range(4):
    n_petals = 6 + ring * 4
    r_base = 1.0 + ring * 1.0
    for i in range(n_petals):
        a = i * TWO_PI / n_petals
        px_l = r_base * 0.12
        py_l = 0.25 + ring * 0.08
        pts = []
        for t in np.linspace(0, 1, 30):
            x = t * px_l
            y = py_l * np.sin(np.pi * t)
            pts.append((x, y))
        for t in np.linspace(1, 0, 30):
            x = t * px_l
            y = -py_l * np.sin(np.pi * t) * 0.85
            pts.append((x, y))
        deg = min(8, len(pts) - 1)
        tn = np.linspace(0, 1, len(pts))
        px_arr = np.array([p[0] for p in pts])
        py_arr = np.array([p[1] for p in pts])
        cos_a, sin_a = np.cos(a), np.sin(a)
        rx = cos_a * px_arr - sin_a * py_arr
        ry = sin_a * px_arr + cos_a * py_arr
        cx_p = np.polyfit(tn, rx, deg)
        cy_p = np.polyfit(tn, ry, deg)
        c.add(PolyObj(list(reversed(cx_p)), list(reversed(cy_p)),
                      t_range=[0, 1], fill=True, fill_color="#c89838",
                      fill_alpha=0.25, color="#dab848", linewidth=0.4))

c.layer("radiating_lines")
for i in range(36):
    a = i * TWO_PI / 36
    c.line(0.3 * np.cos(a), 0.3 * np.sin(a),
           5.2 * np.cos(a), 5.2 * np.sin(a),
           color="#c8a040", linewidth=0.15, alpha=0.25)

c.layer("lotus_inner")
for k in range(3):
    n_lp = 8 + k * 4
    r_lp = 0.5 + k * 0.7
    for i in range(n_lp):
        a = i * TWO_PI / n_lp
        t = np.linspace(0, 1, 40)
        lx = r_lp * t * np.cos(a)
        ly = r_lp * t * np.sin(a) + 0.15 * np.sin(np.pi * t) * np.sin(a + PI / 2)
        deg = min(5, 39)
        cx_l = np.polyfit(t, lx, deg).tolist()
        cy_l = np.polyfit(t, ly, deg).tolist()
        c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                      t_range=[0, 1], color="#c8a040", linewidth=0.4, alpha=0.35))

c.layer("star_center")
c.star(0, 0, scale=0.35, n=8, fill=True, fill_color="#dab848",
       fill_alpha=0.6, color="#c8a040", linewidth=1.5)
c.star(0, 0, scale=0.25, n=5, fill=True, fill_color="#f0d870",
       fill_alpha=0.5, color="#c8a040", linewidth=1.0)
c.circle(0, 0, 0.08, fill=True, fill_color="#f0e8a0")
for i in range(8):
    a = i * TWO_PI / 8
    c.line(0, 0, 0.4 * np.cos(a), 0.4 * np.sin(a),
           color="#c8a040", linewidth=0.8)

c.layer("outer_ring_dots")
for ring in range(3):
    r_out = 4.5 + ring * 0.4
    n_out = 48 + ring * 12
    for j in range(n_out):
        a = j * TWO_PI / n_out
        dx = r_out * np.cos(a)
        dy = r_out * np.sin(a)
        c.circle(dx, dy, 0.02, fill=True, fill_color="#dab848",
                 fill_alpha=0.3)

print("[OK] Golden Mandala complete")
c.render(OUT, dpi=200)
c.info()
