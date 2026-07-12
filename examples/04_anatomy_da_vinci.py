import sys, io, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\e\Desktop\6756756756756756")

import numpy as np

PI = np.pi

from polyart_api import Canvas, PolyObj, PolyCoeffs, TWO_PI, PHI
from polyart_biology import Biomechanics

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "04_anatomy_da_vinci.png")
c = Canvas(name="AnatomyDaVinci", width=12, height=14,
           xlim=(-6, 6), ylim=(-7, 7), background="#e8dcc0")

c.layer("parchment_texture")
for i in range(40):
    x = np.random.uniform(-5.5, 5.5)
    y = np.random.uniform(-6.5, 6.5)
    c.circle(x, y, np.random.uniform(0.02, 0.08),
             fill=True, fill_color="#d8cca8", fill_alpha=0.3)

c.layer("grid_lines")
for i in range(-5, 6):
    c.line(i, -7, i, 7, color="#d0c4a0", linewidth=0.15, alpha=0.3)
for j in range(-6, 7):
    c.line(-6, j, 6, j, color="#d0c4a0", linewidth=0.15, alpha=0.3)

c.layer("spine")
sx, sy = Biomechanics.spine_curve(cx=0, cy=-5, height=10,
                                   lordosis=0.5, kyphosis=0.35, n_pts=150)
c.add(PolyObj(sx, sy, t_range=[0, 1], color="#3a2a1a", linewidth=2.5))
for i in range(12):
    ry = -5 + i * (10 / 12)
    rx = 0.5 * np.sin(PI * (ry + 5) / 10) + 0.35 * np.sin(3 * PI * (ry + 5) / 10)
    c.ellipse(rx, ry, 0.15, 0.08, fill=True, fill_color="#c8b898",
              color="#3a2a1a", linewidth=0.5)

c.layer("rib_cage")
for i in range(8):
    ry = 1.0 + i * 0.55
    rw = 2.5 - 0.25 * i
    rh = 0.5 - 0.04 * i
    rx, ry_p = Biomechanics.rib_profile(cx=0, cy=ry, width=rw, height=rh, twist=0.08)
    c.add(PolyObj(rx, ry_p, t_range=[0, 1], color="#4a3a2a",
                  linewidth=1.2, alpha=0.7))

c.layer("pelvis")
px, py, tr = Biomechanics.pelvis_profile(cx=0, cy=-4.5, width=3.5, height=2.5)
c.add(PolyObj(px, py, t_range=tr, fill=True, fill_color="#d8c8a8",
              fill_alpha=0.3, color="#3a2a1a", linewidth=1.5))

c.layer("scapulae")
for side in [-1, 1]:
    sx_l, sy_l, tr = Biomechanics.scapula_outline(
        cx=side * 2.5, cy=3.5, width=1.8, height=2.0)
    c.add(PolyObj(sx_l, sy_l, t_range=tr, fill=True, fill_color="#d0c0a0",
                  fill_alpha=0.2, color="#4a3a2a", linewidth=1.0))

c.layer("joint_envelopes")
for side in [-1, 1]:
    jx, jy = Biomechanics.joint_envelope(
        cx=side * 3.8, cy=2.0, r=0.8,
        flexion_range=(-20, 130), abduction_range=(-25, 25), n_rays=24)
    deg = min(8, len(jx) - 1)
    jx_l = np.polyfit(np.linspace(0, 1, len(jx)), jx, deg).tolist()
    jy_l = np.polyfit(np.linspace(0, 1, len(jy)), jy, deg).tolist()
    c.add(PolyObj(list(reversed(jx_l)), list(reversed(jy_l)),
                  t_range=[0, 1], fill=True, fill_color="#b0a080",
                  fill_alpha=0.25, color="#5a4a3a", linewidth=0.8))
    c.circle(side * 3.8, 2.0, 0.1, fill=True, fill_color="#5a4a3a")

c.layer("bone_profiles")
bx, by, tr = Biomechanics.bone_profile(length=4.0, head_r=0.3, shaft_r=0.12, condyle_r=0.22)
c.add(PolyObj(bx, by, t_range=tr, fill=True, fill_color="#e0d0b8",
              fill_alpha=0.4, color="#3a2a1a", linewidth=1.2))

c.add_formula("De Humani Corporis Fabrica", -5.5, 6.5, fontsize=11, color="#3a2a1a")
c.add_formula("Homo Vitruvianus - Canon Proportionalis", -5.5, 5.9, fontsize=8, color="#5a4a3a")

print("[OK] Anatomy Da Vinci complete")
c.render(OUT, dpi=200)
c.info()
