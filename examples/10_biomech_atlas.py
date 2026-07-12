import sys, io, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\e\Desktop\6756756756756756")

import numpy as np

PI = np.pi

from polyart_api import Canvas, PolyObj, PolyCoeffs, TWO_PI, PHI
from polyart_biology import Biomechanics, VariantGenerator

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "10_biomech_atlas.png")
c = Canvas(name="BiomechAtlas", width=14, height=10,
           xlim=(-7, 7), ylim=(-5, 5), background="#f5efe0")

c.layer("grid")
for i in range(-6, 7):
    c.line(i, -5, i, 5, color="#e8e0d0", linewidth=0.15, alpha=0.3)
for j in range(-4, 5):
    c.line(-7, j, 7, j, color="#e8e0d0", linewidth=0.15, alpha=0.3)

c.layer("bone_profiles")
bone_variants = VariantGenerator.generate_bone_variants(n=3, seed=42)
bone_x = [-5, -1.5, 2]
for idx, bv in enumerate(bone_variants):
    ox = bone_x[idx]
    oy = 3.5
    bx = [ox + v * 0.6 for v in bv["poly_x"]]
    by = [oy + v * 0.6 for v in bv["poly_y"]]
    deg = min(8, len(bx) - 1)
    cx_l = np.polyfit(np.linspace(0, 1, len(bx)), bx, deg).tolist()
    cy_l = np.polyfit(np.linspace(0, 1, len(by)), by, deg).tolist()
    c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                  t_range=[0, 1], fill=True, fill_color="#e8dcc8",
                  fill_alpha=0.4, color="#5a4a3a", linewidth=1.2))
    c.add_formula(f"Bone #{idx+1}", ox - 0.3, oy - 0.8, fontsize=6, color="#5a4a3a")

c.layer("muscle_force_vectors")
force_pairs = [
    ((-5.5, 1.5), (-3.5, 0.5), 0.3, "#cc4444"),
    ((-1.5, 2.0), (0.5, 0.8), 0.4, "#cc4444"),
    ((2.5, 1.8), (4.5, 0.6), 0.25, "#cc4444"),
    ((-4.5, -0.5), (-2.5, -1.5), 0.35, "#cc6644"),
    ((0.5, -0.3), (2.5, -1.3), 0.3, "#cc6644"),
]
for origin, insertion, belly, col in force_pairs:
    mx, my = Biomechanics.muscle_force_vector(origin, insertion, belly)
    c.add(PolyObj(mx, my, t_range=[0, 1], color=col, linewidth=2.0))
    ox, oy = origin
    ix, iy = insertion
    c.circle(ox, oy, 0.06, fill=True, fill_color=col)
    c.circle(ix, iy, 0.06, fill=True, fill_color=col)

c.layer("joint_rom_envelopes")
joint_data = [
    (-5, -2.5, 1.0, (-30, 150), (-40, 40)),
    (0, -2.5, 0.8, (-10, 120), (-30, 30)),
    (5, -2.5, 0.9, (-20, 140), (-35, 35)),
]
for jx, jy, jr, flex, abd in joint_data:
    env_x, env_y = Biomechanics.joint_envelope(
        cx=jx, cy=jy, r=jr, flexion_range=flex,
        abduction_range=abd, n_rays=30)
    deg = min(10, len(env_x) - 1)
    env_xl = np.polyfit(np.linspace(0, 1, len(env_x)), env_x, deg).tolist()
    env_yl = np.polyfit(np.linspace(0, 1, len(env_y)), env_y, deg).tolist()
    c.add(PolyObj(list(reversed(env_xl)), list(reversed(env_yl)),
                  t_range=[0, 1], fill=True, fill_color="#a0c0e0",
                  fill_alpha=0.3, color="#4a6a8a", linewidth=1.0))
    c.circle(jx, jy, 0.08, fill=True, fill_color="#4a6a8a")

c.layer("tendon_paths")
tendon_data = [
    ((-5.5, 1.5), (-3.5, -1.5), 0.2, "#c8a040"),
    ((-1.5, 2.0), (0.5, -1.0), 0.25, "#c8a040"),
    ((2.5, 1.8), (4.5, -1.2), 0.18, "#c8a040"),
]
for origin, insertion, slack, col in tendon_data:
    tx, ty = Biomechanics.tendon_line(origin, insertion, slack)
    c.add(PolyObj(tx, ty, t_range=[0, 1], color=col, linewidth=1.5,
                  style="dashed"))

c.layer("wolff_stress")
stress_map = [
    (1, 2, 0.8), (-1, 2.5, 0.6), (0, 3, 0.9),
    (-2, 1, 0.5), (2, 1.5, 0.7), (-0.5, -1, 0.4),
    (1.5, -0.5, 0.6), (-1.5, -1.5, 0.3),
]
trajectories = Biomechanics.wolff_bone_adapt(stress_map, n_points=60)
for traj in trajectories:
    d = traj["density"]
    c.add(PolyObj(traj["poly_x"], traj["poly_y"], t_range=[0, 1],
                  color="#5a4a3a", linewidth=0.5 + d * 2, alpha=0.3 + d * 0.4))

c.add_formula("Biomechanical Atlas", -6.5, 4.5, fontsize=11, color="#3a2a1a")
c.add_formula("Bones | Forces | ROM | Tendons | Wolff", -6.5, 4.0, fontsize=7, color="#6a5a4a")

print("[OK] Biomechanical Atlas complete")
c.render(OUT, dpi=200)
c.info()
