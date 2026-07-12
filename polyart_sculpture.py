"""
polyart_sculpture.py - Sculpture, Architecture & Game Asset API for PolyArt
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from polyart_api import Canvas, PolyObj, PolyCoeffs, PHI, PHI_INV, TWO_PI, GOLDEN_ANGLE, SQRT2

PI = np.pi


def _lerp_color(c1, c2, t):
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def _muscle_shape(cx, cy, half_w, half_h, name, n_points=8):
    angles = np.linspace(0, TWO_PI, n_points)
    wobble_funcs = {
        "pec_major": lambda a: 1 + 0.15 * np.cos(2*a) + 0.1 * np.sin(3*a),
        "abs_rect": lambda a: 0.9 + 0.1 * np.cos(4*a),
        "oblique": lambda a: 1 + 0.2 * np.cos(a - 0.5),
        "iliac": lambda a: 1.1 + 0.15 * np.cos(3*a),
        "neck_base": lambda a: 1 + 0.1 * np.cos(2*a),
        "biceps": lambda a: 1 + 0.2 * np.cos(a - 0.3) + 0.1 * np.sin(2*a),
        "triceps": lambda a: 0.95 + 0.15 * np.cos(a + 0.4),
        "forearm": lambda a: 0.85 + 0.15 * np.cos(2*a),
        "quad": lambda a: 1 + 0.2 * np.cos(a - 0.2) + 0.1 * np.sin(3*a),
        "hamstring": lambda a: 0.9 + 0.15 * np.cos(a + 0.3),
        "calf": lambda a: 0.9 + 0.2 * np.cos(2*a - 0.5),
    }
    wf = wobble_funcs.get(name, lambda a: 1 + 0.1 * np.cos(2*a))
    r = wf(angles)
    x_pts = cx + half_w * r * np.cos(angles)
    y_pts = cy + half_h * r * np.sin(angles)
    return {"poly_x": x_pts.tolist(), "poly_y": y_pts.tolist(), "name": name}


class LatheBody:
    """Turned/lathed bodies: amphorae, columns, torsos."""

    @staticmethod
    def amphora(height=4.0, belly_width=1.0, neck_width=0.25, n_points=200):
        t = np.linspace(0, height, n_points)
        ratio = t / height
        belly_r = belly_width * np.sin(np.pi * ratio)
        neck_r = neck_width + (belly_width - neck_width) * (1 - ratio) ** 3
        r = np.where(ratio < 0.1, neck_r * ratio / 0.1,
                     np.where(ratio < 0.3, neck_r + (belly_r - neck_r) * (ratio - 0.1) / 0.2,
                              np.where(ratio < 0.7, belly_r,
                                       belly_r * (1 - (ratio - 0.7) / 0.3) ** 1.5)))
        r[0] = neck_width * 0.8
        r[-1] = neck_width * 0.6
        deg = min(15, n_points - 1)
        rx = np.polyfit(t / height, r, deg).tolist()
        ry = np.polyfit(t / height, t, deg).tolist()
        return {"poly_x": list(reversed(rx)), "poly_y": list(reversed(ry)),
                "t_range": [0, 1], "height": height, "max_r": belly_width}

    @staticmethod
    def column_fluted(height=5.0, radius=0.3, n_flutes=20, flutes_depth=0.05):
        t = np.linspace(0, height, 300)
        r = radius * np.ones_like(t)
        for i in range(len(t)):
            flute_angle = n_flutes * 2 * PI * t[i] / height
            flute_mod = 1 - flutes_depth * (1 + np.cos(flute_angle)) / 2
            r[i] *= flute_mod
        entasis = 1 + 0.02 * np.sin(np.pi * t / height)
        r *= entasis
        deg = min(20, 299)
        rx = np.polyfit(t / height, r, deg).tolist()
        ry = np.polyfit(t / height, t, deg).tolist()
        return {"poly_x": list(reversed(rx)), "poly_y": list(reversed(ry)), "t_range": [0, 1]}

    @staticmethod
    def human_torso(height=5.0, gender="male", shoulder_ratio=0.4,
                    hip_ratio=0.25, waist_ratio=0.2):
        phi_shoulder = shoulder_ratio * PHI_INV
        phi_hip = hip_ratio * PHI_INV
        phi_waist = waist_ratio * PHI_INV
        t = np.linspace(0, height, 300)
        r = np.zeros_like(t)
        for i, ti in enumerate(t):
            n = ti / height
            if n < 0.05:
                r[i] = phi_hip * (1 - n / 0.05) + phi_hip * 0.8 * (n / 0.05)
            elif n < 0.15:
                r[i] = phi_hip * 0.8 - (phi_hip * 0.8 - phi_waist) * ((n - 0.05) / 0.1)
            elif n < 0.35:
                r[i] = phi_waist + (phi_shoulder - phi_waist) * ((n - 0.15) / 0.2) ** 0.7
            elif n < 0.55:
                t_local = (n - 0.35) / 0.2
                r[i] = phi_shoulder * (1 + 0.05 * np.sin(PI * t_local))
            elif n < 0.7:
                r[i] = phi_shoulder * (1 - (n - 0.55) / 0.15 * 0.3)
            else:
                r[i] = phi_shoulder * 0.7 * (1 - (n - 0.7) / 0.3)
        if gender == "female":
            shoulder_shrink = np.where(t / height > 0.35, 0.85, 1.0)
            hip_expand = np.where(t / height < 0.2, 1.15, 1.0)
            r *= shoulder_shrink * hip_expand
        r = np.maximum(r, 0.01)
        deg = min(20, 299)
        rx = np.polyfit(t / height, r, deg).tolist()
        ry = np.polyfit(t / height, t, deg).tolist()
        return {"poly_x": list(reversed(rx)), "poly_y": list(reversed(ry)), "t_range": [0, 1]}

    @staticmethod
    def greek_krater(height=3.5, rim_width=1.2, body_width=0.9):
        t = np.linspace(0, height, 250)
        n = t / height
        r = np.where(n < 0.05, rim_width * 0.9,
                     np.where(n < 0.15, rim_width,
                              np.where(n < 0.3, rim_width - (rim_width - body_width) * (n - 0.15) / 0.15,
                                       np.where(n < 0.6, body_width + 0.1 * np.sin(PI * (n - 0.3) / 0.3),
                                                body_width * (1 - (n - 0.6) / 0.4 * 0.4)))))
        r[-1] = body_width * 0.5
        deg = min(18, 249)
        rx = np.polyfit(t / height, r, deg).tolist()
        ry = np.polyfit(t / height, t, deg).tolist()
        return {"poly_x": list(reversed(rx)), "poly_y": list(reversed(ry)), "t_range": [0, 1]}

    @staticmethod
    def oinochoe(height=3.0):
        t = np.linspace(0, height, 200)
        n = t / height
        r = np.where(n < 0.1, 0.15,
                     np.where(n < 0.2, 0.15 + 0.4 * (n - 0.1) / 0.1,
                              np.where(n < 0.6, 0.55 + 0.1 * np.sin(PI * (n - 0.2) / 0.4),
                                       np.where(n < 0.8, 0.55 * (1 - (n - 0.6) / 0.2 * 0.6),
                                                0.55 * 0.4 * (1 - (n - 0.8) / 0.2)))))
        r[-1] = 0.1
        deg = min(15, 199)
        rx = np.polyfit(t / height, r, deg).tolist()
        ry = np.polyfit(t / height, t, deg).tolist()
        return {"poly_x": list(reversed(rx)), "poly_y": list(reversed(ry)), "t_range": [0, 1]}

    @staticmethod
    def render_lathe(canvas, body, cx=0, cy=0, n_shades=7,
                     base_color="#d4c4a8", highlight="#f5efe0",
                     shadow="#8a7a6a", **kw):
        px = body["poly_x"]
        py = body["poly_y"]
        for i in range(n_shades):
            t = i / max(n_shades - 1, 1)
            shade = _lerp_color(shadow, highlight, t)
            squeeze = 0.3 + 0.7 * (1 - abs(t - 0.5) * 2)
            scaled_px = [cx + v * squeeze for v in px]
            scaled_py = [cy + v for v in py]
            deg = min(15, len(scaled_px) - 1)
            coeffs_x = np.polyfit(np.linspace(0, 1, len(scaled_px)), scaled_px, deg).tolist()
            coeffs_y = np.polyfit(np.linspace(0, 1, len(scaled_py)), scaled_py, deg).tolist()
            canvas.add(PolyObj(list(reversed(coeffs_x)), list(reversed(coeffs_y)),
                               t_range=[0, 1], color=shade, linewidth=0.3,
                               fill=True, fill_color=shade,
                               fill_alpha=0.4 + 0.3 * t, **kw))
        for side in [-1, 1]:
            contour_x = [cx + side * v for v in px]
            contour_y = [cy + v for v in py]
            deg = min(12, len(contour_x) - 1)
            cx_l = np.polyfit(np.linspace(0, 1, len(contour_x)), contour_x, deg).tolist()
            cy_l = np.polyfit(np.linspace(0, 1, len(contour_y)), contour_y, deg).tolist()
            canvas.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                               t_range=[0, 1], color=shadow, linewidth=0.8, alpha=0.6))
        return canvas


class MuscleRelief:
    """Relief muscles: anatomical contours using polynomial curves."""

    @staticmethod
    def torso_front(cx=0, cy=0, scale=1.0, detail="full"):
        s = scale
        muscles = []
        muscles.append(_muscle_shape(cx, cy + 1.5*s, 1.8*s, 0.6*s, "pec_major", 8))
        muscles.append(_muscle_shape(cx - 0.8*s, cy + 0.3*s, 0.5*s, 1.2*s, "abs_rect", 6))
        muscles.append(_muscle_shape(cx + 0.8*s, cy + 0.3*s, 0.5*s, 1.2*s, "abs_rect", 6))
        muscles.append(_muscle_shape(cx - 0.3*s, cy - 0.2*s, 0.4*s, 0.3*s, "oblique", 5))
        muscles.append(_muscle_shape(cx + 0.3*s, cy - 0.2*s, 0.4*s, 0.3*s, "oblique", 5))
        if detail == "full":
            muscles.append(_muscle_shape(cx, cy - 1.5*s, 0.6*s, 0.8*s, "iliac", 5))
            muscles.append(_muscle_shape(cx, cy + 2.5*s, 0.3*s, 0.4*s, "neck_base", 6))
        return muscles

    @staticmethod
    def arm_relief(cx=0, cy=0, scale=1.0, side="left"):
        s = scale
        d = 1 if side == "left" else -1
        muscles = []
        muscles.append(_muscle_shape(cx + d*0.3*s, cy + 1.0*s, 0.4*s, 0.8*s, "biceps", 7))
        muscles.append(_muscle_shape(cx - d*0.2*s, cy + 0.8*s, 0.3*s, 0.7*s, "triceps", 6))
        muscles.append(_muscle_shape(cx + d*0.1*s, cy - 0.2*s, 0.3*s, 1.0*s, "forearm", 5))
        return muscles

    @staticmethod
    def leg_relief(cx=0, cy=0, scale=1.0, side="left"):
        s = scale
        d = 1 if side == "left" else -1
        muscles = []
        muscles.append(_muscle_shape(cx + d*0.2*s, cy + 1.5*s, 0.5*s, 1.2*s, "quad", 7))
        muscles.append(_muscle_shape(cx - d*0.1*s, cy + 0.5*s, 0.35*s, 1.0*s, "hamstring", 6))
        muscles.append(_muscle_shape(cx + d*0.1*s, cy - 1.0*s, 0.25*s, 0.8*s, "calf", 6))
        return muscles

    @staticmethod
    def render_muscles(canvas, muscles, base_color="#d4c4a8",
                       shadow_color="#a09080", highlight_color="#f0e8d8"):
        for m in muscles:
            px = m["poly_x"]
            py = m["poly_y"]
            deg = min(10, len(px) - 1)
            coeffs_x = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
            coeffs_y = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
            canvas.add(PolyObj(
                list(reversed(coeffs_x)), list(reversed(coeffs_y)),
                t_range=[0, 1], fill=True, fill_color=base_color,
                fill_alpha=0.6, color=shadow_color, linewidth=0.8))
            offset_x = [v + 0.02 for v in px[:-1]] + [px[0] + 0.02]
            offset_y = [v + 0.03 for v in py[:-1]] + [py[0] + 0.03]
            cx2 = np.polyfit(np.linspace(0, 1, len(offset_x)), offset_x, deg).tolist()
            cy2 = np.polyfit(np.linspace(0, 1, len(offset_y)), offset_y, deg).tolist()
            canvas.add(PolyObj(
                list(reversed(cx2)), list(reversed(cy2)),
                t_range=[0, 1], fill=True, fill_color=highlight_color,
                fill_alpha=0.2, color="none", linewidth=0))
        return canvas


class PiranesiArch:
    """Impossible architecture: nested arches, staircases, colonnades."""

    @staticmethod
    def arch(cx, cy, w, h, depth=0.3, n_arches=3):
        arches = []
        for i in range(n_arches):
            s = 1 - i * depth
            arch_w = w * s
            arch_h = h * s
            y_off = cy - i * depth * h * 0.3
            t = np.linspace(0, PI, 100)
            ax = cx + (arch_w / 2) * np.cos(t)
            ay = y_off + arch_h * np.sin(t)
            deg = min(8, 99)
            arches.append({
                "poly_x": np.polyfit(t / PI, ax, deg).tolist(),
                "poly_y": np.polyfit(t / PI, ay, deg).tolist(),
                "t_range": [0, 1], "depth": i})
            arches.append({
                "poly_x": [cx - arch_w/2, cx + arch_w/2],
                "poly_y": [y_off, y_off],
                "t_range": [0, 1], "depth": i})
        return arches

    @staticmethod
    def staircase(cx, cy, width, height, n_steps=12, perspective=0.3):
        lines = []
        for i in range(n_steps + 1):
            t = i / n_steps
            scale = 1 - perspective * t
            step_w = width * scale
            step_x = cx - step_w / 2
            step_y = cy - t * height
            lines.append({
                "poly_x": [step_x, step_x + step_w],
                "poly_y": [step_y, step_y],
                "t_range": [0, 1], "depth": t})
        for side in [-1, 1]:
            px = [cx + side * width/2 * (1 - perspective * i/n_steps) for i in range(n_steps + 1)]
            py = [cy - i * height / n_steps for i in range(n_steps + 1)]
            deg = min(5, n_steps)
            lines.append({
                "poly_x": np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist(),
                "poly_y": np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist(),
                "t_range": [0, 1], "depth": 1})
        return lines

    @staticmethod
    def colonnade(cx, cy, n_cols=8, spacing=0.8, col_h=3.0,
                  col_r=0.08, perspective=0.2):
        elements = []
        for i in range(n_cols):
            t = i / max(n_cols - 1, 1)
            x = cx - (n_cols - 1) * spacing / 2 + i * spacing
            scale = 1 - perspective * abs(t - 0.5) * 2
            h = col_h * scale
            r = col_r * scale
            elements.append({"poly_x": [x - r, x + r], "poly_y": [cy, cy + h],
                             "t_range": [0, 1], "depth": scale})
            elements.append({"poly_x": [x - r*1.5, x + r*1.5], "poly_y": [cy+h, cy+h+r*0.5],
                             "t_range": [0, 1], "depth": scale})
            elements.append({"poly_x": [x - r*1.5, x + r*1.5], "poly_y": [cy, cy-r*0.3],
                             "t_range": [0, 1], "depth": scale})
        return elements

    @staticmethod
    def vault(cx, cy, w, h, n_ribs=5):
        ribs = []
        for i in range(n_ribs):
            t = i / max(n_ribs - 1, 1)
            depth = 0.3 + 0.7 * t
            rw = w * depth
            rh = h * (1 - 0.3 * t)
            oy = cy + t * h * 0.5
            theta = np.linspace(0, PI, 80)
            rx = cx + (rw / 2) * np.cos(theta)
            ry = oy + rh * np.sin(theta)
            deg = min(8, 79)
            ribs.append({
                "poly_x": np.polyfit(theta / PI, rx, deg).tolist(),
                "poly_y": np.polyfit(theta / PI, ry, deg).tolist(),
                "t_range": [0, 1], "depth": depth})
        return ribs

    @staticmethod
    def impossible_stairs(cx, cy, size=3.0, loops=3):
        lines = []
        n_steps = int(loops * 16)
        for i in range(n_steps):
            angle = i * TWO_PI / 16
            r = size * (0.3 + 0.7 * (i / n_steps))
            x1 = cx + r * np.cos(angle)
            y1 = cy + r * np.sin(angle) * 0.6
            angle2 = (i + 1) * TWO_PI / 16
            r2 = size * (0.3 + 0.7 * ((i + 1) / n_steps))
            x2 = cx + r2 * np.cos(angle2)
            y2 = cy + r2 * np.sin(angle2) * 0.6
            lines.append({"poly_x": [x1, x2], "poly_y": [y1, y2],
                          "t_range": [0, 1], "depth": i / n_steps})
        return lines

    @staticmethod
    def render_piranesi(canvas, elements, line_color="#c8b898", depth_shade=True):
        max_depth = max((e.get("depth", 0) for e in elements), default=1)
        for e in elements:
            px = e["poly_x"]
            py = e["poly_y"]
            d = e.get("depth", 0)
            t = d / max(max_depth, 0.01) if depth_shade else 0.5
            alpha = 0.3 + 0.7 * (1 - t)
            lw = 0.3 + 1.5 * (1 - t)
            deg = min(8, len(px) - 1) if len(px) > 2 else 1
            cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
            cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
            canvas.add(PolyObj(
                list(reversed(cx_l)), list(reversed(cy_l)),
                t_range=[0, 1], color=line_color, linewidth=lw, alpha=alpha))
        return canvas


class RomanSymbols:
    """Roman symbols: eagle, laurel, SPQR, gladius, shield."""

    @staticmethod
    def eagle(cx=0, cy=0, wingspan=3.0):
        hw = wingspan / 2
        elements = []
        t = np.linspace(0, 1, 80)
        for side in [-1, 1]:
            wing_x = cx + side * hw * t
            wing_y = cy + 0.5 * np.sin(PI * t) * (1 - 0.3 * t)
            wing_y += 0.3 * np.sin(3 * PI * t) * (1 - t)
            deg = min(6, 79)
            elements.append({
                "poly_x": np.polyfit(t, wing_x, deg).tolist(),
                "poly_y": np.polyfit(t, wing_y, deg).tolist(),
                "t_range": [0, 1]})
        head_x = [cx, cx, cx, cx]
        head_y = [cy + 1.2, cy + 1.0, cy + 0.6, cy + 0.3]
        elements.append({
            "poly_x": list(head_x), "poly_y": list(head_y), "t_range": [0, 1]})
        t_body = np.linspace(0, 1, 40)
        body_x = cx + 0.1 * np.sin(2 * PI * t_body)
        body_y = cy - 0.8 * t_body
        deg = min(4, 39)
        elements.append({
            "poly_x": np.polyfit(t_body, body_x, deg).tolist(),
            "poly_y": np.polyfit(t_body, body_y, deg).tolist(),
            "t_range": [0, 1]})
        for side in [-1, 1]:
            elements.append({
                "poly_x": [cx + side*0.1, cx + side*0.4, cx + side*0.3],
                "poly_y": [cy - 0.8, cy - 1.0, cy - 1.2],
                "t_range": [0, 1]})
        return elements

    @staticmethod
    def laurel_wreath(cx=0, cy=0, radius=1.5, n_leaves=24):
        elements = []
        t = np.linspace(0, TWO_PI, 300)
        circle_x = cx + radius * np.cos(t)
        circle_y = cy + radius * np.sin(t)
        deg = min(15, 299)
        elements.append({
            "poly_x": np.polyfit(t / TWO_PI, circle_x, deg).tolist(),
            "poly_y": np.polyfit(t / TWO_PI, circle_y, deg).tolist(),
            "t_range": [0, 1]})
        for i in range(n_leaves):
            angle = i * TWO_PI / n_leaves
            lx = cx + radius * np.cos(angle)
            ly = cy + radius * np.sin(angle)
            leaf_len = 0.2 * (1 + 0.2 * np.sin(i * PHI))
            leaf_angle = angle + PI / 6
            for tip in [-1, 1]:
                dx = tip * leaf_len * np.cos(leaf_angle)
                dy = leaf_len * np.sin(leaf_angle)
                points = [(lx, ly), (lx + dx*0.5, ly + dy*0.5 + 0.05*tip), (lx + dx, ly + dy)]
                elements.append({
                    "poly_x": [p[0] for p in points],
                    "poly_y": [p[1] for p in points],
                    "t_range": [0, 1]})
        return elements

    @staticmethod
    def spqr_banner(cx=0, cy=0, width=4.0, height=2.0):
        elements = []
        m = 0.1
        elements.append({
            "poly_x": [cx-width/2, cx+width/2, cx+width/2, cx-width/2, cx-width/2],
            "poly_y": [cy-height/2, cy-height/2, cy+height/2, cy+height/2, cy-height/2],
            "t_range": [0, 1]})
        elements.append({
            "poly_x": [cx-width/2+m, cx+width/2-m, cx+width/2-m, cx-width/2+m, cx-width/2+m],
            "poly_y": [cy-height/2+m, cy-height/2+m, cy+height/2-m, cy+height/2-m, cy-height/2+m],
            "t_range": [0, 1]})
        for side in [-1, 1]:
            sx = cx + side * width * 0.3
            elements.append({"poly_x": [sx, sx], "poly_y": [cy-0.3, cy+0.3], "t_range": [0, 1]})
        elements.append({"poly_x": [cx-0.15, cx+0.15], "poly_y": [cy, cy], "t_range": [0, 1]})
        return elements

    @staticmethod
    def gladius(cx=0, cy=0, length=3.0):
        elements = []
        blade_x = [cx, cx+0.05, cx+0.08, cx+0.05, cx, cx-0.05, cx-0.08, cx-0.05, cx]
        blade_y = [cy, cy+length*0.1, cy+length*0.4, cy+length*0.7, cy+length,
                   cy+length*0.7, cy+length*0.4, cy+length*0.1, cy]
        elements.append({"poly_x": blade_x, "poly_y": blade_y, "t_range": [0, 1]})
        gw = 0.5
        elements.append({"poly_x": [cx-gw/2, cx+gw/2], "poly_y": [cy, cy], "t_range": [0, 1]})
        grip_x = [cx, cx+0.03, cx+0.03, cx-0.03, cx-0.03, cx]
        grip_y = [cy, cy-0.05, cy-0.3, cy-0.3, cy-0.05, cy]
        elements.append({"poly_x": grip_x, "poly_y": grip_y, "t_range": [0, 1]})
        return elements

    @staticmethod
    def shield(cx=0, cy=0, width=1.5, height=2.0):
        elements = []
        hw = width / 2
        hh = height / 2
        sx = [cx-hw, cx-hw*0.9, cx-hw*0.5, cx, cx+hw*0.5, cx+hw*0.9, cx+hw,
              cx+hw*0.9, cx+hw*0.5, cx, cx-hw*0.5, cx-hw*0.9, cx-hw]
        sy = [cy, cy+hh*0.3, cy+hh*0.8, cy+hh, cy+hh*0.8, cy+hh*0.3, cy,
              cy-hh*0.3, cy-hh*0.8, cy-hh, cy-hh*0.8, cy-hh*0.3, cy]
        elements.append({"poly_x": sx, "poly_y": sy, "t_range": [0, 1]})
        elements.append({"poly_x": [cx-hw*0.6, cx+hw*0.6], "poly_y": [cy, cy], "t_range": [0, 1]})
        elements.append({"poly_x": [cx, cx], "poly_y": [cy-hh*0.7, cy+hh*0.7], "t_range": [0, 1]})
        return elements


class GameAssets:
    """Procedural game assets: sprites, tilemaps, UI, trees."""

    @staticmethod
    def character_sprite(char_class="warrior", cx=0, cy=0, scale=1.0):
        s = scale
        parts = []
        if char_class == "warrior":
            parts.append({"type": "circle", "cx": cx, "cy": cy+1.7*s, "r": 0.3*s,
                          "fill": True, "color": "#d4b896"})
            parts.append({"type": "line", "poly_x": [cx-0.4*s, cx+0.4*s],
                          "poly_y": [cy+1.0*s, cy+1.0*s], "color": "#8B7355", "lw": 3})
            parts.append({"type": "line", "poly_x": [cx, cx], "poly_y": [cy+1.4*s, cy+0.3*s],
                          "color": "#8B7355", "lw": 4})
            parts.append({"type": "line", "poly_x": [cx-0.3*s, cx+0.3*s],
                          "poly_y": [cy+0.3*s, cy-0.8*s], "color": "#8B7355", "lw": 3})
            parts.append({"type": "line", "poly_x": [cx+0.4*s, cx+0.8*s],
                          "poly_y": [cy+1.0*s, cy+1.5*s], "color": "#a0a0b0", "lw": 2})
        elif char_class == "mage":
            parts.append({"type": "circle", "cx": cx, "cy": cy+1.8*s, "r": 0.25*s,
                          "fill": True, "color": "#d4b896"})
            parts.append({"type": "poly", "poly_x": [cx-0.3*s, cx, cx+0.3*s],
                          "poly_y": [cy+1.9*s, cy+2.8*s, cy+1.9*s],
                          "color": "#2a1a4a", "fill": True})
            parts.append({"type": "line", "poly_x": [cx, cx], "poly_y": [cy+1.5*s, cy+0.2*s],
                          "color": "#2a1a4a", "lw": 3})
            parts.append({"type": "line", "poly_x": [cx-0.3*s, cx+0.3*s],
                          "poly_y": [cy+0.2*s, cy-0.9*s], "color": "#2a1a4a", "lw": 3})
            parts.append({"type": "line", "poly_x": [cx+0.3*s, cx+0.9*s],
                          "poly_y": [cy+0.8*s, cy+0.3*s], "color": "#c8a040", "lw": 2})
        elif char_class == "archer":
            parts.append({"type": "circle", "cx": cx, "cy": cy+1.7*s, "r": 0.25*s,
                          "fill": True, "color": "#d4b896"})
            parts.append({"type": "line", "poly_x": [cx, cx], "poly_y": [cy+1.4*s, cy+0.3*s],
                          "color": "#2d5a1e", "lw": 3})
            parts.append({"type": "poly", "poly_x": [cx-0.1*s, cx-0.5*s, cx-0.1*s],
                          "poly_y": [cy+1.6*s, cy+1.0*s, cy+0.4*s],
                          "color": "#8B6914", "lw": 2})
            parts.append({"type": "line", "poly_x": [cx-0.1*s, cx+0.5*s],
                          "poly_y": [cy+1.0*s, cy+1.0*s], "color": "#8a7a6a", "lw": 1})
        return parts

    @staticmethod
    def tilemap(rows=8, cols=8, tile_size=1.0, cx=0, cy=0,
                ground_color="#4a7a3a", wall_color="#7a6a5a",
                water_color="#3a6a9a", seed=42):
        rng = np.random.RandomState(seed)
        elements = []
        for r in range(rows):
            for c in range(cols):
                x = cx + (c - cols/2) * tile_size
                y = cy + (r - rows/2) * tile_size
                tile_type = rng.choice(["ground", "ground", "ground", "wall", "water"],
                                       p=[0.5, 0.2, 0.15, 0.1, 0.05])
                color = {"ground": ground_color, "wall": wall_color,
                         "water": water_color}[tile_type]
                elements.append({
                    "poly_x": [x, x+tile_size, x+tile_size, x, x],
                    "poly_y": [y, y, y+tile_size, y+tile_size, y],
                    "t_range": [0, 1], "fill": True, "fill_color": color,
                    "tile_type": tile_type})
        return elements

    @staticmethod
    def health_bar(cx=0, cy=0, width=3.0, height=0.3, value=0.7, color="#cc3333"):
        elements = []
        elements.append({"poly_x": [cx, cx+width, cx+width, cx, cx],
                         "poly_y": [cy, cy, cy+height, cy+height, cy],
                         "t_range": [0, 1], "fill": True, "fill_color": "#2a2a2a"})
        fw = width * max(0, min(1, value))
        elements.append({"poly_x": [cx, cx+fw, cx+fw, cx, cx],
                         "poly_y": [cy+0.02, cy+0.02, cy+height-0.02, cy+height-0.02, cy+0.02],
                         "t_range": [0, 1], "fill": True, "fill_color": color})
        elements.append({"poly_x": [cx, cx+width, cx+width, cx, cx],
                         "poly_y": [cy, cy, cy+height, cy+height, cy],
                         "t_range": [0, 1], "fill": False, "color": "#ffffff", "lw": 1})
        return elements

    @staticmethod
    def minimap(cx=0, cy=0, size=2.0, explored_pct=0.4, seed=42):
        rng = np.random.RandomState(seed)
        elements = []
        n = 16
        ts = size / n
        for r in range(n):
            for c in range(n):
                x = cx - size/2 + c * ts
                y = cy - size/2 + r * ts
                dist = np.sqrt((r - n/2)**2 + (c - n/2)**2) / (n/2)
                explored = dist < explored_pct + rng.uniform(-0.1, 0.1)
                if explored:
                    tile = rng.choice(["g", "g", "g", "w", "m"], p=[0.6, 0.15, 0.1, 0.1, 0.05])
                    color = {"g": "#4a7a3a", "w": "#3a6a9a", "m": "#7a6a5a"}[tile]
                    alpha = max(0.3, 1 - dist)
                else:
                    color = "#1a1a2e"
                    alpha = 0.8
                elements.append({
                    "poly_x": [x, x+ts, x+ts, x, x],
                    "poly_y": [y, y, y+ts, y+ts, y],
                    "t_range": [0, 1], "fill": True, "fill_color": color,
                    "fill_alpha": alpha})
        return elements

    @staticmethod
    def compass_rose(cx=0, cy=0, size=1.0, color="#c8a040"):
        elements = []
        for i in range(8):
            angle = i * PI / 4
            length = size if i % 2 == 0 else size * 0.5
            elements.append({"poly_x": [cx, cx + length*np.cos(angle)],
                             "poly_y": [cy, cy + length*np.sin(angle)],
                             "t_range": [0, 1], "color": color,
                             "lw": 2 if i % 2 == 0 else 1})
        t = np.linspace(0, TWO_PI, 100)
        cr_x = cx + size * 0.15 * np.cos(t)
        cr_y = cy + size * 0.15 * np.sin(t)
        deg = min(6, 99)
        elements.append({
            "poly_x": np.polyfit(t/TWO_PI, cr_x, deg).tolist(),
            "poly_y": np.polyfit(t/TWO_PI, cr_y, deg).tolist(),
            "t_range": [0, 1], "fill": True, "fill_color": color})
        return elements

    @staticmethod
    def tree(cx=0, cy=0, height=2.0, seed=42):
        rng = np.random.RandomState(seed)
        elements = []

        def _branch(x, y, h, angle, depth):
            if depth <= 0 or h < 0.1:
                return
            x2 = x + h * np.cos(angle)
            y2 = y + h * np.sin(angle)
            w = 0.08 * (depth / 5)
            elements.append({
                "poly_x": [x-w, x+w, x2+w*0.5, x2-w*0.5, x-w],
                "poly_y": [y, y, y2, y2, y],
                "t_range": [0, 1], "fill": True,
                "fill_color": _lerp_color("#5a3a1a", "#2d5a1e", 1 - depth/5)})
            n_b = rng.randint(2, 4)
            for _ in range(n_b):
                _branch(x2, y2, h * rng.uniform(0.6, 0.8),
                        angle + rng.uniform(-0.6, 0.6), depth - 1)

        _branch(cx, cy, height, PI / 2, 5)
        return elements

    @staticmethod
    def render_game_assets(canvas, assets):
        for a in assets:
            if a.get("type") == "circle":
                canvas.circle(a["cx"], a["cy"], a["r"],
                              fill=a.get("fill", False),
                              fill_color=a.get("fill_color", "#888"),
                              color=a.get("color", "#333"),
                              linewidth=a.get("lw", 1.5))
            elif a.get("type") == "line":
                px, py = a["poly_x"], a["poly_y"]
                canvas.line(px[0], py[0], px[1], py[1],
                            color=a.get("color", "#333"),
                            linewidth=a.get("lw", 1.5))
            elif a.get("type") == "poly":
                canvas.polygon(list(zip(a["poly_x"], a["poly_y"])),
                               fill=a.get("fill", False),
                               fill_color=a.get("fill_color", "#888"),
                               color=a.get("color", "#333"))
            else:
                px, py = a["poly_x"], a["poly_y"]
                deg = min(8, len(px) - 1) if len(px) > 2 else 1
                cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
                cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
                canvas.add(PolyObj(
                    list(reversed(cx_l)), list(reversed(cy_l)),
                    t_range=[0, 1],
                    fill=a.get("fill", False),
                    fill_color=a.get("fill_color", a.get("color", "#888")),
                    fill_alpha=a.get("fill_alpha", 0.5),
                    color=a.get("color", "#333"),
                    linewidth=a.get("lw", 1.5)))
        return canvas


class SculptureScenes:
    """Ready-made demo scenes."""

    @staticmethod
    def roman_gallery():
        c = Canvas(name="RomanGallery", xlim=(-8, 8), ylim=(-6, 6), background="#1a1a2e")
        c.layer("grid")
        for i in range(-7, 8):
            c.line(i, -6, i, 6, color="#2a2a3e", linewidth=0.2, alpha=0.3)
        for j in range(-5, 7):
            c.line(-8, j, 8, j, color="#2a2a3e", linewidth=0.2, alpha=0.3)

        c.layer("amphora")
        body = LatheBody.amphora(height=4, belly_width=0.8)
        LatheBody.render_lathe(c, body, cx=-5, cy=-2, n_shades=9,
                               base_color="#c8a088", highlight="#f0e0d0", shadow="#6a4a3a")

        c.layer("column")
        col = LatheBody.column_fluted(height=5, radius=0.25, n_flutes=16)
        LatheBody.render_lathe(c, col, cx=-2, cy=-2.5, n_shades=7,
                               base_color="#e8dcc8", highlight="#ffffff", shadow="#8a7a6a")

        c.layer("eagle")
        for el in RomanSymbols.eagle(cx=2, cy=1, wingspan=3):
            px, py = el["poly_x"], el["poly_y"]
            deg = min(6, len(px)-1) if len(px) > 2 else 1
            cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
            cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
            c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                          t_range=[0, 1], color="#c8a040", linewidth=2,
                          fill=True, fill_color="#c8a040", fill_alpha=0.3))

        c.layer("laurel")
        for el in RomanSymbols.laurel_wreath(cx=2, cy=1, radius=2.0, n_leaves=20):
            px, py = el["poly_x"], el["poly_y"]
            deg = min(6, len(px)-1) if len(px) > 2 else 1
            cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
            cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
            c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                          t_range=[0, 1], color="#2d5a1e", linewidth=1.2))

        c.layer("spqr")
        for el in RomanSymbols.spqr_banner(cx=5.5, cy=2, width=3, height=1.5):
            px, py = el["poly_x"], el["poly_y"]
            deg = min(5, len(px)-1) if len(px) > 2 else 1
            cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
            cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
            c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                          t_range=[0, 1], color="#c8a040", linewidth=2,
                          fill=True, fill_color="#8b0000", fill_alpha=0.5))

        c.layer("gladius")
        for el in RomanSymbols.gladius(cx=5.5, cy=-3, length=2.5):
            px, py = el["poly_x"], el["poly_y"]
            deg = min(6, len(px)-1) if len(px) > 2 else 1
            cx_l = np.polyfit(np.linspace(0, 1, len(px)), px, deg).tolist()
            cy_l = np.polyfit(np.linspace(0, 1, len(py)), py, deg).tolist()
            c.add(PolyObj(list(reversed(cx_l)), list(reversed(cy_l)),
                          t_range=[0, 1], color="#a0a0b0", linewidth=1.5))

        c.add_formula("SPQR", 5.5, 3.5, fontsize=20, color="#c8a040")
        return c

    @staticmethod
    def piranesi_scene():
        c = Canvas(name="Piranesi", xlim=(-8, 8), ylim=(-6, 6), background="#0a0a15")
        c.layer("stars")
        for i in range(30):
            c.circle(np.random.uniform(-7.5, 7.5), np.random.uniform(-5.5, 5.5),
                     0.015, fill=True, fill_color="#ffffff",
                     fill_alpha=np.random.uniform(0.1, 0.4))

        c.layer("arches")
        for i in range(5):
            arches = PiranesiArch.arch(0, -1, 14-i*2, 10-i*1.5, depth=0.25, n_arches=3)
            PiranesiArch.render_piranesi(c, arches, line_color="#c8b898")

        c.layer("colonnades")
        PiranesiArch.render_piranesi(c, PiranesiArch.colonnade(-5, -4, 6, 0.6, 4, perspective=0.3),
                                     line_color="#a09878")
        PiranesiArch.render_piranesi(c, PiranesiArch.colonnade(5, -4, 6, 0.6, 4, perspective=0.3),
                                     line_color="#a09878")

        c.layer("stairs")
        PiranesiArch.render_piranesi(c, PiranesiArch.staircase(0, -4, 6, 4, 15, 0.4),
                                     line_color="#d8c8a8")

        c.layer("vault")
        PiranesiArch.render_piranesi(c, PiranesiArch.vault(0, 2, 10, 4, 8),
                                     line_color="#b8a888")

        c.layer("impossible")
        PiranesiArch.render_piranesi(c, PiranesiArch.impossible_stairs(0, 0, 2.5, 2),
                                     line_color="#e8d8b8")

        c.add_formula("Carceri d'Invenzione", -7, 5.5, fontsize=10, color="#c8b898")
        return c

    @staticmethod
    def anatomy_study():
        c = Canvas(name="Anatomy", xlim=(-6, 6), ylim=(-8, 8), background="#2a2018")
        c.layer("torso")
        MuscleRelief.render_muscles(c, MuscleRelief.torso_front(0, 0, 2.0, "full"))
        c.layer("left_arm")
        MuscleRelief.render_muscles(c, MuscleRelief.arm_relief(-3, 2, 1.5, "left"))
        c.layer("right_arm")
        MuscleRelief.render_muscles(c, MuscleRelief.arm_relief(3, 2, 1.5, "right"))
        c.layer("left_leg")
        MuscleRelief.render_muscles(c, MuscleRelief.leg_relief(-1.5, -5, 1.5, "left"))
        c.layer("right_leg")
        MuscleRelief.render_muscles(c, MuscleRelief.leg_relief(1.5, -5, 1.5, "right"))
        c.add_formula("Polykleitos Canon", -5, 7.5, fontsize=10, color="#c8a040")
        return c

    @staticmethod
    def game_demo():
        c = Canvas(name="GameDemo", xlim=(-8, 8), ylim=(-8, 8), background="#1a1a2e")
        c.layer("tilemap")
        GameAssets.render_game_assets(c, GameAssets.tilemap(8, 8, 1.5, 0, 0, seed=42))
        c.layer("chars")
        GameAssets.render_game_assets(c, GameAssets.character_sprite("warrior", -6, 5, 1))
        GameAssets.render_game_assets(c, GameAssets.character_sprite("mage", -4, 5, 1))
        GameAssets.render_game_assets(c, GameAssets.character_sprite("archer", -2, 5, 1))
        c.layer("ui")
        GameAssets.render_game_assets(c, GameAssets.health_bar(-6, 6.5, 3, 0.3, 0.8, "#cc3333"))
        GameAssets.render_game_assets(c, GameAssets.health_bar(-6, 6.0, 3, 0.3, 0.5, "#3333cc"))
        c.layer("minimap")
        GameAssets.render_game_assets(c, GameAssets.minimap(6, 6, 3, 0.4, 42))
        c.layer("compass")
        GameAssets.render_game_assets(c, GameAssets.compass_rose(6, -6, 1.2))
        c.layer("tree")
        GameAssets.render_game_assets(c, GameAssets.tree(-6, -5, 3, 42))
        return c


if __name__ == "__main__":
    print("[PolyArt Sculpture v1.0 - Demo]")

    print("1/4 Roman Gallery...")
    c1 = SculptureScenes.roman_gallery()
    c1.save("scene_roman.polyart")
    c1.render("scene_roman.png", dpi=200)
    c1.info()

    print("2/4 Piranesi...")
    c2 = SculptureScenes.piranesi_scene()
    c2.save("scene_piranesi.polyart")
    c2.render("scene_piranesi.png", dpi=200)
    c2.info()

    print("3/4 Anatomy...")
    c3 = SculptureScenes.anatomy_study()
    c3.save("scene_anatomy.polyart")
    c3.render("scene_anatomy.png", dpi=200)
    c3.info()

    print("4/4 Game Demo...")
    c4 = SculptureScenes.game_demo()
    c4.save("scene_game.polyart")
    c4.render("scene_game.png", dpi=200)
    c4.info()

    print("[OK] All sculpture demos saved!")
