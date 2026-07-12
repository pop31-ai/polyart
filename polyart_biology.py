"""
polyart_biology.py - Biological polynomial laws for PolyArt

Mathematical foundations:
- Growth curves (logistic, allometric, von Bertalanffy)
- Fibonacci phyllotaxis, branching, L-systems
- Joint envelopes, bone angles, tendon attachment
- Wolff's law, diffusion-reaction (Turing)
- Variant generator for parametric biological forms
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from polyart_api import Canvas, PolyObj, PolyCoeffs, PHI, PHI_INV, TWO_PI, GOLDEN_ANGLE, SQRT2

PI = np.pi
E = np.e


# ============================================================
# Growth Curves
# ============================================================

class GrowthCurves:
    """Polynomial approximations of biological growth laws."""

    @staticmethod
    def logistic(t, L=1.0, k=5.0, t0=0.5):
        """Logistic: P(t) = L / (1 + exp(-k*(t-t0)))"""
        return L / (1 + np.exp(-k * (t - t0)))

    @staticmethod
    def logistic_poly(L=1.0, k=5.0, t0=0.5, degree=12, n_pts=200):
        t = np.linspace(0, 1, n_pts)
        y = GrowthCurves.logistic(t, L, k, t0)
        coeffs = np.polyfit(t, y, degree)
        return list(reversed(coeffs.tolist())), [0, 1]

    @staticmethod
    def von_bertalanffy(t, Linf=1.0, K=0.3, t0=0.0):
        """Von Bertalanffy: L(t) = Linf * (1 - exp(-K*(t-t0)))^(1/3)"""
        return Linf * (1 - np.exp(-K * (t - t0))) ** (1/3)

    @staticmethod
    def von_bertalanffy_poly(Linf=1.0, K=0.3, degree=10, n_pts=200):
        t = np.linspace(0, 1, n_pts)
        y = GrowthCurves.von_bertalanffy(t, Linf, K)
        coeffs = np.polyfit(t, y, degree)
        return list(reversed(coeffs.tolist())), [0, 1]

    @staticmethod
    def power_allometry(x, a=1.0, b=0.75):
        """Allometric: Y = a * X^b (Kleiber's law b=3/4)"""
        return a * np.power(np.maximum(x, 1e-10), b)

    @staticmethod
    def allometric_poly(a=1.0, b=0.75, degree=8, n_pts=200):
        x = np.linspace(0.01, 1, n_pts)
        y = GrowthCurves.power_allometry(x, a, b)
        coeffs = np.polyfit(x, y, degree)
        return list(reversed(coeffs.tolist())), [0, 1]

    @staticmethod
    def gompertz(t, a=1.0, b=5.0, k=10.0):
        """Gompertz: a * exp(-b * exp(-k*t))"""
        return a * np.exp(-b * np.exp(-k * t))

    @staticmethod
    def gompertz_poly(a=1.0, b=5.0, k=10.0, degree=10, n_pts=200):
        t = np.linspace(0, 1, n_pts)
        y = GrowthCurves.gompertz(t, a, b, k)
        coeffs = np.polyfit(t, y, degree)
        return list(reversed(coeffs.tolist())), [0, 1]

    @staticmethod
    def diffuse_growth(cx, cy, t_max=1.0, n_rings=8, rate=0.3):
        """Concentric growth rings (tree rings, coral)."""
        rings = []
        for i in range(1, n_rings + 1):
            r = rate * i * t_max / n_rings
            squeeze = 1 + 0.05 * np.sin(i * PHI)
            rings.append({"cx": cx, "cy": cy, "r": r,
                          "squeeze_x": squeeze, "squeeze_y": 1.0 / squeeze,
                          "age": i / n_rings})
        return rings


# ============================================================
# Fibonacci & Phyllotaxis
# ============================================================

class Phyllotaxis:
    """Fibonacci spirals, leaf arrangements, seed patterns."""

    @staticmethod
    def golden_points(n=100, scale=1.0, cx=0, cy=0, twist=0):
        """Sunflower seed pattern: angle = n * GOLDEN_ANGLE."""
        angles = np.arange(n) * GOLDEN_ANGLE + twist
        r = scale * np.sqrt(np.arange(n) / max(n, 1))
        x = cx + r * np.cos(angles)
        y = cy + r * np.sin(angles)
        return x.tolist(), y.tolist()

    @staticmethod
    def fibonacci_spiral(n=200, a=0.1, scale=1.0, cx=0, cy=0):
        """Fibonacci log-spiral approximated by polynomial."""
        t = np.linspace(0, 4 * PI, n)
        r = a * np.exp(t * np.log(PHI) / (PI / 2))
        r = r / np.max(r) * scale
        x = cx + r * np.cos(t)
        y = cy + r * np.sin(t)
        deg = min(15, n - 1)
        cx_list = np.polyfit(t / (4*PI), x, deg).tolist()
        cy_list = np.polyfit(t / (4*PI), y, deg).tolist()
        return list(reversed(cx_list)), list(reversed(cy_list)), [0, 1]

    @staticmethod
    def leaf_shape(length=2.0, width=0.6, tip_sharpness=3.0, asymmetry=0.0,
                   n_pts=150):
        """Polynomial leaf: parametric from petiole to tip."""
        t = np.linspace(0, 1, n_pts)
        x = length * t
        w = width * np.sin(PI * t) * (1 - t ** tip_sharpness)
        w *= (1 + asymmetry * np.sin(3 * PI * t))
        upper = w
        lower = -w * 0.8
        x_all = np.concatenate([x, x[::-1]])
        y_all = np.concatenate([upper, lower[::-1]])
        t_norm = np.linspace(0, 1, len(x_all))
        deg = min(10, len(x_all) - 1)
        cx = np.polyfit(t_norm, x_all, deg).tolist()
        cy = np.polyfit(t_norm, y_all, deg).tolist()
        return list(reversed(cx)), list(reversed(cy)), [0, 1]

    @staticmethod
    def petal_shape(length=1.0, width=0.5, curl=0.1, n_pts=100):
        """Single petal with curl."""
        t = np.linspace(0, 1, n_pts)
        x = length * t
        y = width * np.sin(PI * t) * (1 - 0.3 * t)
        y += curl * t ** 2
        x_all = np.concatenate([x, x[::-1]])
        y_all = np.concatenate([y, -y[::-1] * 0.9])
        t_norm = np.linspace(0, 1, len(x_all))
        deg = min(8, len(x_all) - 1)
        cx = np.polyfit(t_norm, x_all, deg).tolist()
        cy = np.polyfit(t_norm, y_all, deg).tolist()
        return list(reversed(cx)), list(reversed(cy)), [0, 1]

    @staticmethod
    def flower_radial(n_petals=5, petal_len=1.0, petal_w=0.4,
                      cx=0, cy=0, curl=0.05):
        """Full flower from radial petal placement."""
        petals = []
        for i in range(n_petals):
            angle = i * TWO_PI / n_petals
            px, py, tr = Phyllotaxis.petal_shape(petal_len, petal_w, curl)
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            rx = [cx + v * cos_a - py_j * sin_a for v, py_j in zip(px, py)]
            ry = [cy + v * sin_a + py_j * cos_a for v, py_j in zip(px, py)]
            deg = min(8, len(rx) - 1)
            t_n = np.linspace(0, 1, len(rx))
            petals.append({
                "poly_x": np.polyfit(t_n, rx, deg).tolist(),
                "poly_y": np.polyfit(t_n, ry, deg).tolist(),
                "t_range": [0, 1], "petal_index": i})
        return petals

    @staticmethod
    def branching_tree(cx=0, cy=0, length=2.0, angle=PI/2,
                       depth=6, spread=0.4, decay=0.72, seed=42):
        """Fractal branching: each branch spawns 2-3 sub-branches."""
        rng = np.random.RandomState(seed)
        branches = []

        def _branch(x, y, l, a, d):
            if d <= 0 or l < 0.05:
                return
            x2 = x + l * np.cos(a)
            y2 = y + l * np.sin(a)
            w = 0.02 + 0.06 * (d / depth)
            branches.append({
                "poly_x": [x, x2], "poly_y": [y, y2],
                "width": w, "depth": d, "age": 1 - d / depth})
            n_child = rng.choice([2, 3], p=[0.6, 0.4])
            for _ in range(n_child):
                new_a = a + rng.uniform(-spread, spread)
                _branch(x2, y2, l * decay, new_a, d - 1)

        _branch(cx, cy, length, angle, depth)
        return branches

    @staticmethod
    def vein_network(n_main=5, length=2.0, cx=0, cy=0, seed=42):
        """Leaf vein network: main veins + secondary branches."""
        rng = np.random.RandomState(seed)
        veins = []
        for i in range(n_main):
            angle = PI * 0.2 + (PI * 0.6) * i / max(n_main - 1, 1)
            n_pts = 50
            t = np.linspace(0, 1, n_pts)
            x = cx + length * t * np.cos(angle)
            y = cy + length * t * np.sin(angle) * 0.4
            curviness = rng.uniform(-0.1, 0.1)
            y += curviness * np.sin(PI * t)
            deg = min(5, n_pts - 1)
            veins.append({
                "poly_x": np.polyfit(t, x, deg).tolist(),
                "poly_y": np.polyfit(t, y, deg).tolist(),
                "t_range": [0, 1], "type": "main"})
            for j in range(3):
                frac = 0.3 + 0.2 * j
                bx = x[int(frac * n_pts)]
                by = y[int(frac * n_pts)]
                sub_len = length * 0.3 * (1 - frac)
                sub_angle = angle + rng.choice([-1, 1]) * rng.uniform(0.3, 0.8)
                st = np.linspace(0, 1, 20)
                sx = bx + sub_len * st * np.cos(sub_angle)
                sy = by + sub_len * st * np.sin(sub_angle) * 0.4
                deg2 = min(3, 19)
                veins.append({
                    "poly_x": np.polyfit(st, sx, deg2).tolist(),
                    "poly_y": np.polyfit(st, sy, deg2).tolist(),
                    "t_range": [0, 1], "type": "secondary"})
        return veins


# ============================================================
# Joint Envelopes & Biomechanics
# ============================================================

class Biomechanics:
    """Joint mobility, bone angles, tendon attachment, Wolff's law."""

    @staticmethod
    def joint_envelope(cx, cy, r, flexion_range=(-30, 150),
                       abduction_range=(-45, 45), n_rays=36):
        """Joint range of motion envelope (filled area)."""
        angles = []
        for i in range(n_rays):
            t = i / n_rays
            flex = np.radians(flexion_range[0] +
                              (flexion_range[1] - flexion_range[0]) * t)
            abd = np.radians(abduction_range[0] +
                             (abduction_range[1] - abduction_range[0]) *
                             (0.5 + 0.5 * np.sin(2 * PI * t)))
            rx = r * (1 + 0.2 * np.cos(flex)) * np.cos(abd)
            ry = r * (1 + 0.2 * np.cos(flex)) * np.sin(abd)
            angles.append((cx + rx, cy + ry))
        angles.append(angles[0])
        px = [a[0] for a in angles]
        py = [a[1] for a in angles]
        t_n = np.linspace(0, 1, len(px))
        deg = min(10, len(px) - 1)
        return (np.polyfit(t_n, px, deg).tolist(),
                np.polyfit(t_n, py, deg).tolist())

    @staticmethod
    def bone_profile(length=3.0, head_r=0.3, shaft_r=0.15,
                     condyle_r=0.25, n_pts=100):
        """Long bone profile: head, shaft, condyle."""
        t = np.linspace(0, 1, n_pts)
        r = np.where(t < 0.1, head_r * np.sin(PI * t / 0.1),
                     np.where(t < 0.2, shaft_r + (head_r - shaft_r) * (0.2 - t) / 0.1,
                              np.where(t < 0.8, shaft_r,
                                       np.where(t < 0.95,
                                                shaft_r + (condyle_r - shaft_r) * (t - 0.8) / 0.15,
                                                condyle_r * np.sin(PI * (1 - t) / 0.05)))))
        r = np.maximum(r, 0.01)
        x = length * t
        upper = r
        lower = -r
        x_all = np.concatenate([x, x[::-1]])
        y_all = np.concatenate([upper, lower[::-1]])
        t_n = np.linspace(0, 1, len(x_all))
        deg = min(10, len(x_all) - 1)
        cx_l = np.polyfit(t_n, x_all, deg).tolist()
        cy_l = np.polyfit(t_n, y_all, deg).tolist()
        return list(reversed(cx_l)), list(reversed(cy_l)), [0, 1]

    @staticmethod
    def tendon_line(origin, insertion, slack=0.15, n_pts=50):
        """Tendon path: catenary-like curve between attachment points."""
        ox, oy = origin
        ix, iy = insertion
        t = np.linspace(0, 1, n_pts)
        x = ox + (ix - ox) * t
        mid_y = (oy + iy) / 2
        sag = slack * abs(ix - ox)
        y = oy + (iy - oy) * t - sag * np.sin(PI * t)
        deg = min(5, n_pts - 1)
        cx_l = np.polyfit(t, x, deg).tolist()
        cy_l = np.polyfit(t, y, deg).tolist()
        return list(reversed(cx_l)), list(reversed(cy_l))

    @staticmethod
    def muscle_force_vector(origin, insertion, belly_offset=0.3):
        """Muscle line of action: origin -> belly -> insertion."""
        ox, oy = origin
        ix, iy = insertion
        mx = (ox + ix) / 2 + belly_offset * abs(iy - oy)
        my = (oy + iy) / 2
        points = [(ox, oy), (mx, my), (ix, iy)]
        px = [p[0] for p in points]
        py = [p[1] for p in points]
        t_n = np.linspace(0, 1, 3)
        deg = 2
        cx_l = np.polyfit(t_n, px, deg).tolist()
        cy_l = np.polyfit(t_n, py, deg).tolist()
        return list(reversed(cx_l)), list(reversed(cy_l))

    @staticmethod
    def spine_curve(cx=0, cy=0, height=4.0, lordosis=0.3,
                    kyphosis=0.2, n_pts=100):
        """Spinal curvature: cervical lordosis, thoracic kyphosis, lumbar lordosis."""
        t = np.linspace(0, 1, n_pts)
        x = cx + lordosis * np.sin(PI * t) + kyphosis * np.sin(3 * PI * t)
        y = cy + height * t
        deg = min(8, n_pts - 1)
        cx_l = np.polyfit(t, x, deg).tolist()
        cy_l = np.polyfit(t, y, deg).tolist()
        return list(reversed(cx_l)), list(reversed(cy_l))

    @staticmethod
    def rib_profile(cx, cy, width=1.5, height=0.8, twist=0.1, n_pts=80):
        """Single rib cross-section."""
        t = np.linspace(0, PI, n_pts)
        x = cx + (width / 2) * np.cos(t)
        y = cy + height * np.sin(t) + twist * np.sin(2 * t)
        deg = min(6, n_pts - 1)
        cx_l = np.polyfit(t / PI, x, deg).tolist()
        cy_l = np.polyfit(t / PI, y, deg).tolist()
        return list(reversed(cx_l)), list(reversed(cy_l))

    @staticmethod
    def pelvis_profile(cx=0, cy=0, width=2.0, height=1.5, n_pts=120):
        """Pelvis silhouette: iliac crests, sacrum, pubis."""
        t = np.linspace(0, TWO_PI, n_pts)
        r_x = width / 2 * (1 + 0.15 * np.cos(2 * t) + 0.08 * np.cos(4 * t))
        r_y = height / 2 * (1 + 0.1 * np.sin(3 * t))
        x = cx + r_x * np.cos(t)
        y = cy + r_y * np.sin(t)
        deg = min(10, n_pts - 1)
        cx_l = np.polyfit(t / TWO_PI, x, deg).tolist()
        cy_l = np.polyfit(t / TWO_PI, y, deg).tolist()
        return list(reversed(cx_l)), list(reversed(cy_l)), [0, TWO_PI]

    @staticmethod
    def scapula_outline(cx=0, cy=0, width=1.2, height=1.5, n_pts=100):
        """Scapula: triangular bone with spine."""
        t = np.linspace(0, TWO_PI, n_pts)
        x = cx + (width / 2) * np.cos(t) * (1 + 0.2 * np.cos(t))
        y = cy + (height / 2) * np.sin(t) * (1 + 0.15 * np.sin(2 * t))
        deg = min(8, n_pts - 1)
        cx_l = np.polyfit(t / TWO_PI, x, deg).tolist()
        cy_l = np.polyfit(t / TWO_PI, y, deg).tolist()
        return list(reversed(cx_l)), list(reversed(cy_l)), [0, TWO_PI]

    @staticmethod
    def wolff_bone_adapt(stress_map, n_points=100):
        """Wolff's law: bone density follows stress trajectories."""
        trajectories = []
        for i, (sx, sy, s_val) in enumerate(stress_map):
            n = n_points
            t = np.linspace(0, 1, n)
            angle = np.arctan2(sy, sx)
            density = abs(s_val)
            x = sx * t * 2
            y = sy * t * 2
            width = 0.02 + 0.08 * density
            thickness = width * (1 + 0.3 * np.sin(4 * PI * t))
            trajectories.append({
                "poly_x": np.polyfit(t, x, min(4, n-1)).tolist(),
                "poly_y": np.polyfit(t, y + thickness * np.sin(PI * t), min(4, n-1)).tolist(),
                "t_range": [0, 1], "density": density})
        return trajectories


# ============================================================
# Turing / Diffusion-Reaction Patterns
# ============================================================

class TuringPatterns:
    """Reaction-diffusion pattern generation."""

    @staticmethod
    def spot_pattern(cx, cy, size=3.0, n_spots=15, spot_r=0.15,
                     seed=42):
        """Leopard/cheetah spots."""
        rng = np.random.RandomState(seed)
        spots = []
        for i in range(n_spots):
            x = cx + rng.uniform(-size/2, size/2)
            y = cy + rng.uniform(-size/2, size/2)
            r = spot_r * rng.uniform(0.5, 1.5)
            deform = rng.uniform(0.8, 1.2)
            spots.append({"cx": x, "cy": y, "r": r, "deform_x": deform,
                          "deform_y": 1.0/deform, "angle": rng.uniform(0, PI)})
        return spots

    @staticmethod
    def stripe_pattern(cx, cy, width=3.0, height=3.0,
                       n_stripes=8, waviness=0.3, seed=42):
        """Tiger/zebra stripes."""
        rng = np.random.RandomState(seed)
        stripes = []
        for i in range(n_stripes):
            t_val = i / n_stripes
            y_base = cy - height/2 + height * t_val
            n_pts = 80
            t = np.linspace(0, 1, n_pts)
            x = cx - width/2 + width * t
            y = y_base + waviness * np.sin(2 * PI * t * 3 + rng.uniform(0, PI))
            deg = min(6, n_pts - 1)
            stripes.append({
                "poly_x": np.polyfit(t, x, deg).tolist(),
                "poly_y": np.polyfit(t, y, deg).tolist(),
                "t_range": [0, 1], "width": 0.05 + 0.03 * np.sin(t_val * PI)})
        return stripes

    @staticmethod
    def spiral_pattern(cx, cy, n_arms=3, r_max=2.0, turns=2,
                       n_pts=200):
        """Nautilus/fingerprint spiral."""
        t = np.linspace(0, turns * TWO_PI, n_pts)
        arms = []
        for arm in range(n_arms):
            offset = arm * TWO_PI / n_arms
            r = r_max * t / (turns * TWO_PI)
            x = cx + r * np.cos(t + offset)
            y = cy + r * np.sin(t + offset)
            deg = min(12, n_pts - 1)
            t_norm = t / (turns * TWO_PI)
            arms.append({
                "poly_x": np.polyfit(t_norm, x, deg).tolist(),
                "poly_y": np.polyfit(t_norm, y, deg).tolist(),
                "t_range": [0, 1], "arm": arm})
        return arms

    @staticmethod
    def voronoi_cells(centers, bounds=(-3, 3, -3, 3)):
        """Approximate Voronoi cell boundaries."""
        cells = []
        for i, (cx, cy) in enumerate(centers):
            angles = np.linspace(0, TWO_PI, 20)
            r_cell = 0.5
            x = cx + r_cell * np.cos(angles)
            y = cy + r_cell * np.sin(angles)
            for j, (ox, oy) in enumerate(centers):
                if i == j:
                    continue
                dx, dy = ox - cx, oy - cy
                dist = np.sqrt(dx**2 + dy**2)
                mid_x = (cx + ox) / 2
                mid_y = (cy + oy) / 2
                r_cell = min(r_cell, dist / 2 * 1.1)
            x = cx + r_cell * np.cos(angles)
            y = cy + r_cell * np.sin(angles)
            deg = min(6, 19)
            cells.append({
                "poly_x": np.polyfit(angles / TWO_PI, x, deg).tolist(),
                "poly_y": np.polyfit(angles / TWO_PI, y, deg).tolist(),
                "t_range": [0, 1], "center": (cx, cy)})
        return cells

    @staticmethod
    def hexagonal_packing(cx, cy, size=3.0, cell_r=0.3, seed=42):
        """Biological hexagonal packing (honeycomb, epithelium)."""
        cells = []
        row = 0
        y = cy - size / 2
        while y < cy + size / 2:
            offset = (row % 2) * cell_r * SQRT2 / 2
            x = cx - size / 2 + offset
            while x < cx + size / 2:
                cells.append({"cx": x, "cy": y, "r": cell_r * 0.9})
                x += cell_r * SQRT2
            y += cell_r * 1.5
            row += 1
        return cells


# ============================================================
# Variant Generator
# ============================================================

class VariantGenerator:
    """Parametric variant generation for biological forms."""

    @staticmethod
    def vary_params(base_params, variations=5, sigma=0.1, seed=42):
        """Generate N variant parameter sets from base."""
        rng = np.random.RandomState(seed)
        variants = []
        for _ in range(variations):
            v = {}
            for k, val in base_params.items():
                if isinstance(val, (int, float)):
                    v[k] = val * (1 + rng.normal(0, sigma))
                else:
                    v[k] = val
            variants.append(v)
        return variants

    @staticmethod
    def generate_leaf_variants(n=5, seed=42):
        """Variants of leaf shapes."""
        base = {"length": 2.0, "width": 0.6, "tip_sharpness": 3.0,
                "asymmetry": 0.0}
        variants = VariantGenerator.vary_params(base, n, sigma=0.15, seed=seed)
        results = []
        for v in variants:
            px, py, tr = Phyllotaxis.leaf_shape(
                length=v["length"], width=v["width"],
                tip_sharpness=v["tip_sharpness"], asymmetry=v["asymmetry"])
            results.append({"params": v, "poly_x": px, "poly_y": py,
                            "t_range": tr})
        return results

    @staticmethod
    def generate_flower_variants(n=5, seed=42):
        """Variants of flower forms."""
        rng = np.random.RandomState(seed)
        results = []
        for i in range(n):
            n_petals = rng.choice([4, 5, 6, 7, 8])
            petal_len = rng.uniform(0.5, 1.5)
            petal_w = rng.uniform(0.2, 0.6)
            curl = rng.uniform(0, 0.2)
            petals = Phyllotaxis.flower_radial(n_petals, petal_len, petal_w, curl=curl)
            results.append({"n_petals": n_petals, "petal_len": petal_len,
                            "petal_w": petal_w, "curl": curl,
                            "petals": petals})
        return results

    @staticmethod
    def generate_tree_variants(n=3, seed=42):
        """Variants of branching trees."""
        rng = np.random.RandomState(seed)
        results = []
        for i in range(n):
            spread = rng.uniform(0.2, 0.6)
            decay = rng.uniform(0.6, 0.8)
            depth = rng.choice([4, 5, 6, 7])
            branches = Phyllotaxis.branching_tree(
                length=2.0, spread=spread, decay=decay,
                depth=depth, seed=seed + i)
            results.append({"spread": spread, "decay": decay,
                            "depth": depth, "branches": branches})
        return results

    @staticmethod
    def generate_bone_variants(n=3, seed=42):
        """Variants of bone profiles."""
        rng = np.random.RandomState(seed)
        results = []
        for i in range(n):
            length = rng.uniform(2.0, 4.0)
            head_r = rng.uniform(0.2, 0.4)
            shaft_r = rng.uniform(0.1, 0.2)
            condyle_r = rng.uniform(0.2, 0.35)
            px, py, tr = Biomechanics.bone_profile(length, head_r, shaft_r, condyle_r)
            results.append({"length": length, "head_r": head_r,
                            "shaft_r": shaft_r, "condyle_r": condyle_r,
                            "poly_x": px, "poly_y": py, "t_range": tr})
        return results

    @staticmethod
    def generate_skin_texture(width=4.0, height=4.0, density=0.3,
                              pattern="spots", seed=42):
        """Generate skin/fur texture patterns."""
        if pattern == "spots":
            n = int(density * 50)
            return TuringPatterns.spot_pattern(0, 0, min(width, height), n,
                                               spot_r=0.1, seed=seed)
        elif pattern == "stripes":
            n = int(density * 12)
            return TuringPatterns.stripe_pattern(0, 0, width, height, n,
                                                 waviness=0.2, seed=seed)
        elif pattern == "spiral":
            return TuringPatterns.spiral_pattern(0, 0, n_arms=3,
                                                 r_max=min(width, height)/2)
        elif pattern == "hexagonal":
            return TuringPatterns.hexagonal_packing(0, 0, min(width, height),
                                                    cell_r=0.2, seed=seed)
        return []


# ============================================================
# Composite Biological Scenes
# ============================================================

class BioScenes:
    """Complete biological demonstration scenes."""

    @staticmethod
    def growth_study():
        """Growth curves and phyllotaxis study."""
        c = Canvas(name="GrowthStudy", xlim=(-6, 6), ylim=(-6, 6),
                   background="#f8f4ec")

        c.layer("grid")
        for i in range(-5, 6):
            c.line(i, -6, i, 6, color="#e0d8c8", linewidth=0.2)
            c.line(-6, i, 6, i, color="#e0d8c8", linewidth=0.2)

        c.layer("logistic")
        px, tr = GrowthCurves.logistic_poly(L=4, k=8, t0=0.5, degree=10)
        py_dummy = np.polyval(list(reversed(px)), np.linspace(tr[0], tr[1], 100))
        c.add(PolyObj(px, [0]*len(px), t_range=tr, color="#2d5a1e", linewidth=2))

        c.layer("sunflower")
        xs, ys = Phyllotaxis.golden_points(n=120, scale=2.0, cx=2.5, cy=2.5)
        for x, y in zip(xs, ys):
            r = 0.03 + 0.02 * np.sqrt((x-2.5)**2 + (y-2.5)**2)
            c.circle(x, y, r, fill=True, fill_color="#c8a040",
                     fill_alpha=0.7, color="#8a6a20", linewidth=0.3)

        c.layer("leaf_variants")
        leaves = VariantGenerator.generate_leaf_variants(n=4, seed=42)
        colors = ["#2d5a1e", "#3a7a2a", "#4a8a3a", "#1a4a10"]
        for i, leaf in enumerate(leaves):
            offset_x = -4 + i * 1.8
            offset_y = -3.5
            px = [offset_x + v for v in leaf["poly_x"]]
            py = [offset_y + v for v in leaf["poly_y"]]
            deg = min(8, len(px)-1)
            cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
            cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
            c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                          t_range=[0, 1], fill=True, fill_color=colors[i],
                          fill_alpha=0.5, color=colors[i], linewidth=0.8))

        c.layer("veins")
        veins = Phyllotaxis.vein_network(n_main=7, length=3.5, cx=0, cy=-1, seed=7)
        for v in veins:
            lw = 1.2 if v["type"] == "main" else 0.5
            alpha = 0.7 if v["type"] == "main" else 0.4
            c.add(PolyObj(v["poly_x"], v["poly_y"], t_range=[0, 1],
                          color="#2d5a1e", linewidth=lw, alpha=alpha))

        c.add_formula("\\phi = 1.618...", -5.5, 5.5, fontsize=9, color="#8a6a20")
        c.add_formula("Fibonacci Phyllotaxis", 0.5, 5.5, fontsize=8, color="#2d5a1e")
        return c

    @staticmethod
    def anatomy_biomech():
        """Biomechanical study: bones, joints, tendons."""
        c = Canvas(name="Biomechanics", xlim=(-7, 7), ylim=(-7, 7),
                   background="#f5efe0")

        c.layer("grid")
        for i in range(-6, 7):
            c.line(i, -7, i, 7, color="#e8e0d0", linewidth=0.2)

        c.layer("spine")
        sx, sy = Biomechanics.spine_curve(cx=0, cy=-3, height=6,
                                          lordosis=0.4, kyphosis=0.3)
        c.add(PolyObj(sx, sy, t_range=[0, 1], color="#5a4a3a", linewidth=3))
        for i in range(8):
            ry = -3 + i * 0.75
            rx = 0.4 * np.sin(PI * (ry + 3) / 6) + 0.3 * np.sin(3 * PI * (ry + 3) / 6)
            c.circle(rx, ry, 0.08, fill=True, fill_color="#d4c4a8",
                     color="#5a4a3a", linewidth=0.5)

        c.layer("bone")
        bx, by, tr = Biomechanics.bone_profile(length=3.0, head_r=0.25,
                                                shaft_r=0.12, condyle_r=0.2)
        c.add(PolyObj(bx, by, t_range=tr, fill=True, fill_color="#e8dcc8",
                      fill_alpha=0.5, color="#5a4a3a", linewidth=1.5))

        c.layer("joint")
        jx, jy = Biomechanics.joint_envelope(cx=-4, cy=0, r=1.2,
                                             flexion_range=(-20, 140),
                                             abduction_range=(-30, 30))
        deg = min(10, len(jx)-1)
        jx_l = np.polyfit(np.linspace(0, 1, len(jx)), jx, deg).tolist()
        jy_l = np.polyfit(np.linspace(0, 1, len(jy)), jy, deg).tolist()
        c.add(PolyObj(list(reversed(jx_l)), list(reversed(jy_l)),
                      t_range=[0, 1], fill=True, fill_color="#a0c0e0",
                      fill_alpha=0.3, color="#4a6a8a", linewidth=1.5))
        c.circle(-4, 0, 0.15, fill=True, fill_color="#5a4a3a")

        c.layer("tendons")
        tx, ty = Biomechanics.tendon_line((-3, 2), (3, 2), slack=0.3)
        c.add(PolyObj(tx, ty, t_range=[0, 1], color="#c8a040", linewidth=1.5))
        mx, my = Biomechanics.muscle_force_vector((-3, 1), (3, 1), belly_offset=0.5)
        c.add(PolyObj(mx, my, t_range=[0, 1], color="#cc4444", linewidth=2))
        c.line(-3, 2, 3, 2, color="#4a6a8a", linewidth=1, linestyle="dotted")
        c.line(-3, 1, 3, 1, color="#4a6a8a", linewidth=1, linestyle="dotted")

        c.layer("pelvis")
        px, py, tr = Biomechanics.pelvis_profile(cx=0, cy=-4, width=3, height=2)
        c.add(PolyObj(px, py, t_range=tr, fill=True, fill_color="#e8dcc8",
                      fill_alpha=0.3, color="#5a4a3a", linewidth=1.5))

        c.layer("ribs")
        for i in range(6):
            ry = 1 + i * 0.6
            rw = 2.0 - 0.2 * i
            rh = 0.4 - 0.03 * i
            rx, ry_p = Biomechanics.rib_profile(cx=0, cy=ry, width=rw, height=rh)
            c.add(PolyObj(rx, ry_p, t_range=[0, 1], color="#8a7a6a",
                          linewidth=1, alpha=0.6))

        c.add_formula("Wolff's Law", -6.5, 6.5, fontsize=9, color="#5a4a3a")
        c.add_formula("Polykleitos Canon \\phi", 2, 6.5, fontsize=8, color="#8a6a20")
        return c

    @staticmethod
    def turing_study():
        """Diffusion-reaction patterns: spots, stripes, spirals."""
        c = Canvas(name="Turing", xlim=(-8, 8), ylim=(-6, 6),
                   background="#1a1a2e")

        c.layer("spots")
        spots = TuringPatterns.spot_pattern(cx=-4, cy=2, size=4, n_spots=20,
                                            spot_r=0.2, seed=42)
        for s in spots:
            t = np.linspace(0, TWO_PI, 30)
            x = s["cx"] + s["r"] * s["deform_x"] * np.cos(t + s["angle"])
            y = s["cy"] + s["r"] * s["deform_y"] * np.sin(t + s["angle"])
            deg = min(5, 29)
            c.add(PolyObj(np.polyfit(t/TWO_PI, x, deg).tolist(),
                          np.polyfit(t/TWO_PI, y, deg).tolist(),
                          t_range=[0, TWO_PI], fill=True,
                          fill_color="#c8a040", fill_alpha=0.6,
                          color="#8a6a20", linewidth=0.5))

        c.layer("stripes")
        stripes = TuringPatterns.stripe_pattern(cx=3, cy=2, width=4, height=4,
                                                n_stripes=10, waviness=0.3, seed=7)
        for s in stripes:
            c.add(PolyObj(s["poly_x"], s["poly_y"], t_range=[0, 1],
                          color="#d94a6e", linewidth=s["width"] * 8, alpha=0.6))

        c.layer("spirals")
        arms = TuringPatterns.spiral_pattern(cx=-4, cy=-2.5, n_arms=5,
                                             r_max=2, turns=3)
        for arm in arms:
            c.add(PolyObj(arm["poly_x"], arm["poly_y"], t_range=[0, 1],
                          color="#4ad9a0", linewidth=1.5, alpha=0.7))

        c.layer("hex")
        hex_cells = TuringPatterns.hexagonal_packing(cx=3, cy=-2.5, size=3.5,
                                                     cell_r=0.25, seed=42)
        for h in hex_cells:
            t = np.linspace(0, TWO_PI, 7)
            x = h["cx"] + h["r"] * np.cos(t)
            y = h["cy"] + h["r"] * np.sin(t)
            deg = min(5, 6)
            c.add(PolyObj(np.polyfit(t/TWO_PI, x, deg).tolist(),
                          np.polyfit(t/TWO_PI, y, deg).tolist(),
                          t_range=[0, TWO_PI], fill=True,
                          fill_color="#3a6a9a", fill_alpha=0.3,
                          color="#5a8aba", linewidth=0.5))

        c.add_formula("Reaction-Diffusion", -7.5, 5.5, fontsize=10, color="#c8b898")
        c.add_formula("Turing 1952", -7.5, 4.8, fontsize=8, color="#a09878")
        return c

    @staticmethod
    def variant_showcase():
        """Side-by-side variants of biological forms."""
        c = Canvas(name="Variants", xlim=(-8, 8), ylim=(-6, 6),
                   background="#f8f4ec")

        c.layer("leaf_variants")
        leaves = VariantGenerator.generate_leaf_variants(n=5, seed=99)
        colors_l = ["#1a4a10", "#2d5a1e", "#3a7a2a", "#4a8a3a", "#5a9a4a"]
        for i, lf in enumerate(leaves):
            ox = -6 + i * 2.5
            oy = 3
            px = [ox + v for v in lf["poly_x"]]
            py = [oy + v for v in lf["poly_y"]]
            deg = min(8, len(px)-1)
            cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
            cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
            c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                          t_range=[0, 1], fill=True, fill_color=colors_l[i],
                          fill_alpha=0.5, color=colors_l[i], linewidth=1))
            c.add_formula(f"#{i+1}", ox, oy - 1.2, fontsize=7, color="#5a4a3a")

        c.layer("flower_variants")
        flowers = VariantGenerator.generate_flower_variants(n=3, seed=88)
        f_colors = ["#d94a6e", "#c8a040", "#4a90d9"]
        for i, fl in enumerate(flowers):
            ox = -3 + i * 3
            oy = -1
            for petal in fl["petals"]:
                px = [ox + v for v in petal["poly_x"]]
                py = [oy + v for v in petal["poly_y"]]
                deg = min(6, len(px)-1)
                cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
                cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
                c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                              t_range=[0, 1], fill=True,
                              fill_color=f_colors[i], fill_alpha=0.4,
                              color=f_colors[i], linewidth=0.8))
            c.circle(ox, oy, 0.15, fill=True, fill_color="#c8a040")
            c.add_formula(f"{fl['n_petals']}p", ox, oy - 1.8, fontsize=7, color="#5a4a3a")

        c.layer("tree_variants")
        trees = VariantGenerator.generate_tree_variants(n=3, seed=77)
        t_colors = ["#2d5a1e", "#5a3a1a", "#3a6a2a"]
        for i, tv in enumerate(trees):
            ox = -3 + i * 3
            oy = -5
            for br in tv["branches"]:
                px = [ox + v for v in br["poly_x"]]
                py = [oy + v for v in br["poly_y"]]
                lw = br["width"] * 20
                alpha = 0.4 + 0.6 * br["age"]
                c.add(PolyObj(px, py, t_range=[0, 1],
                              color=t_colors[i], linewidth=lw, alpha=alpha))

        c.add_formula("Parametric Variants", -7.5, 5.5, fontsize=10, color="#5a4a3a")
        return c


if __name__ == "__main__":
    print("[PolyArt Biology v1.0 - Demo]")

    print("1/4 Growth Study...")
    c1 = BioScenes.growth_study()
    c1.save("bio_growth.polyart")
    c1.render("bio_growth.png", dpi=200)
    c1.info()

    print("2/4 Biomechanics...")
    c2 = BioScenes.anatomy_biomech()
    c2.save("bio_biomech.polyart")
    c2.render("bio_biomech.png", dpi=200)
    c2.info()

    print("3/4 Turing Patterns...")
    c3 = BioScenes.turing_study()
    c3.save("bio_turing.polyart")
    c3.render("bio_turing.png", dpi=200)
    c3.info()

    print("4/4 Variant Showcase...")
    c4 = BioScenes.variant_showcase()
    c4.save("bio_variants.polyart")
    c4.render("bio_variants.png", dpi=200)
    c4.info()

    print("[OK] All biology demos saved!")
