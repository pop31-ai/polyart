import sys
import io
import math
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from polyart_api import Canvas, PolyObj, PHI, TWO_PI, SQRT2


class Rotations:
    @staticmethod
    def rotate_x(points, angle):
        c, s = math.cos(angle), math.sin(angle)
        return [(x, y * c - z * s, y * s + z * c) for x, y, z in points]

    @staticmethod
    def rotate_y(points, angle):
        c, s = math.cos(angle), math.sin(angle)
        return [(x * c + z * s, y, -x * s + z * c) for x, y, z in points]

    @staticmethod
    def rotate_z(points, angle):
        c, s = math.cos(angle), math.sin(angle)
        return [(x * c - y * s, x * s + y * c, z) for x, y, z in points]

    @staticmethod
    def rotate_all(points, rx, ry, rz):
        pts = Rotations.rotate_x(points, rx)
        pts = Rotations.rotate_y(pts, ry)
        pts = Rotations.rotate_z(pts, rz)
        return pts


class Wireframe3D:
    @staticmethod
    def _project(points, cx, cy, focal=5.0):
        result = []
        for x, y, z in points:
            denom = z + focal
            if abs(denom) < 0.01:
                denom = 0.01
            sx = cx + x * focal / denom
            sy = cy + y * focal / denom
            result.append((sx, sy, z))
        return result

    @staticmethod
    def _to_polydict(proj_pts):
        if len(proj_pts) < 2:
            return []
        xs = [p[0] for p in proj_pts]
        ys = [p[1] for p in proj_pts]
        n = len(xs)
        deg = min(n - 1, 6)
        if deg < 1:
            deg = 1
        t = np.linspace(0, 1, n)
        t_fine = np.linspace(0, 1, max(n * 4, 20))
        try:
            coeffs_x = np.polyfit(t, xs, deg)
            coeffs_y = np.polyfit(t, ys, deg)
            px = np.polyval(coeffs_x, t_fine).tolist()
            py = np.polyval(coeffs_y, t_fine).tolist()
        except Exception:
            px, py = xs, ys
        return [{"poly_x": px, "poly_y": py}]

    @staticmethod
    def sphere(cx, cy, r, n_rings=12, n_meridians=16, rotation=(0.3, 0.5, 0)):
        lines = []
        for i in range(n_rings + 1):
            phi = math.pi * i / n_rings
            ring = []
            for j in range(n_meridians + 1):
                theta = TWO_PI * j / n_meridians
                x = r * math.sin(phi) * math.cos(theta)
                y = r * math.sin(phi) * math.sin(theta)
                z = r * math.cos(phi)
                ring.append((x, y, z))
            ring = Rotations.rotate_all(ring, *rotation)
            proj = Wireframe3D._project(ring, cx, cy)
            lines.extend(Wireframe3D._to_polydict(proj))
        for j in range(n_meridians):
            theta = TWO_PI * j / n_meridians
            meridian = []
            for i in range(n_rings + 1):
                phi = math.pi * i / n_rings
                x = r * math.sin(phi) * math.cos(theta)
                y = r * math.sin(phi) * math.sin(theta)
                z = r * math.cos(phi)
                meridian.append((x, y, z))
            meridian = Rotations.rotate_all(meridian, *rotation)
            proj = Wireframe3D._project(meridian, cx, cy)
            lines.extend(Wireframe3D._to_polydict(proj))
        return lines

    @staticmethod
    def cube(cx, cy, size, rotation=(0.4, 0.6, 0)):
        h = size / 2
        verts = [
            (-h, -h, -h), (h, -h, -h), (h, h, -h), (-h, h, -h),
            (-h, -h, h), (h, -h, h), (h, h, h), (-h, h, h),
        ]
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]
        rot_verts = Rotations.rotate_all(verts, *rotation)
        lines = []
        for a, b in edges:
            pts = [rot_verts[a], rot_verts[b]]
            proj = Wireframe3D._project(pts, cx, cy)
            lines.extend(Wireframe3D._to_polydict(proj))
        return lines

    @staticmethod
    def cylinder(cx, cy, r, height, n_segments=16, rotation=(0.3, 0, 0)):
        lines = []
        hh = height / 2
        for ring_y in [hh, -hh]:
            circle = []
            for j in range(n_segments + 1):
                theta = TWO_PI * j / n_segments
                x = r * math.cos(theta)
                z = r * math.sin(theta)
                circle.append((x, ring_y, z))
            circle = Rotations.rotate_all(circle, *rotation)
            proj = Wireframe3D._project(circle, cx, cy)
            lines.extend(Wireframe3D._to_polydict(proj))
        for j in range(0, n_segments, max(1, n_segments // 8)):
            theta = TWO_PI * j / n_segments
            x = r * math.cos(theta)
            z = r * math.sin(theta)
            vline = [(x, hh, z), (x, -hh, z)]
            vline = Rotations.rotate_all(vline, *rotation)
            proj = Wireframe3D._project(vline, cx, cy)
            lines.extend(Wireframe3D._to_polydict(proj))
        return lines

    @staticmethod
    def torus(cx, cy, R, r, n_major=24, n_minor=12, rotation=(0.5, 0.3, 0)):
        lines = []
        for i in range(n_major):
            theta1 = TWO_PI * i / n_major
            theta2 = TWO_PI * (i + 1) / n_major
            ring = []
            for j in range(n_minor + 1):
                phi = TWO_PI * j / n_minor
                x = (R + r * math.cos(phi)) * math.cos(theta1)
                y = (R + r * math.cos(phi)) * math.sin(theta1)
                z = r * math.sin(phi)
                ring.append((x, y, z))
            ring = Rotations.rotate_all(ring, *rotation)
            proj = Wireframe3D._project(ring, cx, cy)
            lines.extend(Wireframe3D._to_polydict(proj))
        for j in range(n_minor):
            phi = TWO_PI * j / n_minor
            tube = []
            for i in range(n_major + 1):
                theta = TWO_PI * i / n_major
                x = (R + r * math.cos(phi)) * math.cos(theta)
                y = (R + r * math.cos(phi)) * math.sin(theta)
                z = r * math.sin(phi)
                tube.append((x, y, z))
            tube = Rotations.rotate_all(tube, *rotation)
            proj = Wireframe3D._project(tube, cx, cy)
            lines.extend(Wireframe3D._to_polydict(proj))
        return lines

    @staticmethod
    def icosahedron(cx, cy, size, rotation=(0.3, 0.5, 0)):
        t = (1.0 + math.sqrt(5.0)) / 2.0
        s = size / math.sqrt(1 + t * t)
        verts_raw = [
            (-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0),
            (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
            (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1),
        ]
        verts = [(x * s, y * s, z * s) for x, y, z in verts_raw]
        faces = [
            (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
            (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
            (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
            (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
        ]
        rot_v = Rotations.rotate_all(verts, *rotation)
        lines = []
        edge_set = set()
        for a, b, c in faces:
            for e in [(a, b), (b, c), (c, a)]:
                key = (min(e), max(e))
                if key not in edge_set:
                    edge_set.add(key)
                    pts = [rot_v[e[0]], rot_v[e[1]]]
                    proj = Wireframe3D._project(pts, cx, cy)
                    lines.extend(Wireframe3D._to_polydict(proj))
        return lines

    @staticmethod
    def dodecahedron(cx, cy, size, rotation=(0.4, 0.7, 0)):
        t = (1.0 + math.sqrt(5.0)) / 2.0
        r3 = 1.0 / t
        s = size * 0.5
        cube_verts = [
            (-1, -1, -1), (-1, -1, 1), (-1, 1, -1), (-1, 1, 1),
            (1, -1, -1), (1, -1, 1), (1, 1, -1), (1, 1, 1),
        ]
        phi_verts = [
            (0, -r3, t), (0, r3, t), (0, -r3, -t), (0, r3, -t),
            (-r3, t, 0), (r3, t, 0), (-r3, -t, 0), (r3, -t, 0),
            (t, 0, -r3), (t, 0, r3), (-t, 0, -r3), (-t, 0, r3),
        ]
        all_v = [(x * s, y * s, z * s) for x, y, z in cube_verts + phi_verts]
        pentagon_indices = [
            [1, 11, 5, 9, 13], [1, 9, 3, 15, 7], [1, 7, 19, 17, 11],
            [8, 12, 4, 14, 10], [2, 14, 4, 16, 6], [2, 6, 18, 0, 12],
            [2, 0, 8, 10, 14], [5, 11, 17, 19, 9], [3, 15, 7, 19, 3],
            [4, 12, 0, 8, 16], [6, 18, 10, 8, 16], [5, 13, 15, 3, 9],
        ]
        rot_v = Rotations.rotate_all(all_v, *rotation)
        lines = []
        edge_set = set()
        for face in pentagon_indices:
            n = len(face)
            for i in range(n):
                a = face[i]
                b = face[(i + 1) % n]
                key = (min(a, b), max(a, b))
                if key not in edge_set:
                    edge_set.add(key)
                    pts = [rot_v[a], rot_v[b]]
                    proj = Wireframe3D._project(pts, cx, cy)
                    lines.extend(Wireframe3D._to_polydict(proj))
        return lines


class Surface3D:
    @staticmethod
    def _project_point(x, y, z, cx, cy, focal=5.0):
        denom = z + focal
        if abs(denom) < 0.01:
            denom = 0.01
        return (cx + x * focal / denom, cy + y * focal / denom, z)

    @staticmethod
    def _fit_curve(xs, ys, n_fine=40):
        if len(xs) < 2:
            return xs, ys
        n = len(xs)
        deg = min(n - 1, 5)
        if deg < 1:
            deg = 1
        t = np.linspace(0, 1, n)
        t_fine = np.linspace(0, 1, n_fine)
        try:
            cx = np.polyfit(t, xs, deg)
            cy = np.polyfit(t, ys, deg)
            return np.polyval(cx, t_fine).tolist(), np.polyval(cy, t_fine).tolist()
        except Exception:
            return xs, ys

    @staticmethod
    def heightfield(cx, cy, size, func, n_lines=15, rotation=(0.5, 0.3, 0)):
        lines = []
        half = size / 2
        for i in range(n_lines):
            y_val = -half + size * i / (n_lines - 1)
            pts = []
            n_samples = 30
            for j in range(n_samples + 1):
                x_val = -half + size * j / n_samples
                z_val = func(x_val, y_val)
                pts.append((x_val, y_val, z_val))
            pts = Rotations.rotate_all(pts, *rotation)
            proj = [Surface3D._project_point(x, y, z, cx, cy) for x, y, z in pts]
            px = [p[0] for p in proj]
            py = [p[1] for p in proj]
            fx, fy = Surface3D._fit_curve(px, py)
            lines.append({"poly_x": fx, "poly_y": fy})
        return lines

    @staticmethod
    def parametric_surface(cx, cy, size, u_range, v_range, fu, fv, fz,
                           n_u=20, n_v=20, rotation=(0.4, 0.5, 0)):
        lines = []
        u_min, u_max = u_range
        v_min, v_max = v_range
        for i in range(n_u):
            u = u_min + (u_max - u_min) * i / (n_u - 1)
            pts = []
            for j in range(n_v + 1):
                v = v_min + (v_max - v_min) * j / n_v
                x = fu(u, v) * size * 0.4
                y = fv(u, v) * size * 0.4
                z = fz(u, v) * size * 0.4
                pts.append((x, y, z))
            pts = Rotations.rotate_all(pts, *rotation)
            proj = [Surface3D._project_point(x, y, z, cx, cy) for x, y, z in pts]
            px = [p[0] for p in proj]
            py = [p[1] for p in proj]
            fx, fy = Surface3D._fit_curve(px, py)
            lines.append({"poly_x": fx, "poly_y": fy})
        return lines

    @staticmethod
    def moebius_strip(cx, cy, size, twists=1, width=0.3, n_lines=20, rotation=(0.3, 0.5, 0)):
        def fu(u, v):
            return (1 + 0.5 * v * width * math.cos(twists * u / 2)) * math.cos(u)

        def fv(u, v):
            return (1 + 0.5 * v * width * math.cos(twists * u / 2)) * math.sin(u)

        def fz(u, v):
            return 0.5 * v * width * math.sin(twists * u / 2)

        return Surface3D.parametric_surface(
            cx, cy, size, (0, TWO_PI), (-1, 1), fu, fv, fz,
            n_u=n_lines, n_v=20, rotation=rotation
        )

    @staticmethod
    def klein_bottle(cx, cy, size, n_lines=25, rotation=(0.5, 0.3, 0)):
        def fu(u, v):
            if u < math.pi:
                return 3 * math.cos(u) * (1 + math.sin(u)) + 2 * (1 - math.cos(u) / 2) * math.cos(u) * math.cos(v)
            else:
                return 3 * math.cos(u) * (1 + math.sin(u)) + 2 * (1 - math.cos(u) / 2) * math.cos(v + math.pi)

        def fv(u, v):
            if u < math.pi:
                return 8 * math.sin(u) + 2 * (1 - math.cos(u) / 2) * math.sin(u) * math.cos(v)
            else:
                return 8 * math.sin(u)

        def fz(u, v):
            return 2 * (1 - math.cos(u) / 2) * math.sin(v)

        return Surface3D.parametric_surface(
            cx, cy, size, (0, TWO_PI), (0, TWO_PI), fu, fv, fz,
            n_u=n_lines, n_v=20, rotation=rotation
        )


class Scene3D:
    def __init__(self, xlim=(-5, 5), ylim=(-5, 5), background="#0a0a15"):
        self.xlim = xlim
        self.ylim = ylim
        self.background = background
        self.objects = []
        self.lights = [(1, 1, 1)]

    def add_wireframe(self, obj, color="#c8b898", linewidth=1.0, alpha=1.0):
        self.objects.append({
            "type": "wireframe", "data": obj, "color": color,
            "linewidth": linewidth, "alpha": alpha,
        })

    def add_surface(self, obj, fill_color="#4a6a8a", color="#2a3a4a", alpha=0.5):
        self.objects.append({
            "type": "surface", "data": obj, "fill_color": fill_color,
            "color": color, "alpha": alpha,
        })

    def add_light(self, direction=(1, 1, 1), intensity=1.0):
        mag = math.sqrt(sum(d * d for d in direction))
        self.lights = [(d / mag for d in direction)]

    def _compute_alpha(self, z_vals, z_min=-3, z_max=3):
        if not z_vals:
            return 1.0
        avg_z = sum(z_vals) / len(z_vals)
        depth = (avg_z - z_min) / (z_max - z_min)
        depth = max(0.0, min(1.0, depth))
        return 0.3 + 0.7 * (1.0 - depth)

    def render_to_canvas(self, canvas):
        for obj in self.objects:
            for item in obj["data"]:
                px = item.get("poly_x", [])
                py = item.get("poly_y", [])
                if not px or not py:
                    continue
                alpha = obj.get("alpha", 1.0)
                color = obj.get("color", obj.get("fill_color", "#c8b898"))
                lw = obj.get("linewidth", 1.0)
                p = PolyObj(px, py)
                p.color = color
                p.linewidth = lw
                p.alpha = alpha
                canvas.add(p)


class Demo3D:
    @staticmethod
    def geometric_primitives():
        canvas = Canvas(900, 700, background="#0a0a15")
        scene = Scene3D()
        sphere_lines = Wireframe3D.sphere(200, 200, 80, rotation=(0.4, 0.6, 0))
        scene.add_wireframe(sphere_lines, color="#7799cc", linewidth=1.0)
        cube_lines = Wireframe3D.cube(500, 200, 100, rotation=(0.5, 0.7, 0.2))
        scene.add_wireframe(cube_lines, color="#cc9977", linewidth=1.0)
        cyl_lines = Wireframe3D.cylinder(200, 500, 60, 120, rotation=(0.3, 0.4, 0))
        scene.add_wireframe(cyl_lines, color="#99cc77", linewidth=1.0)
        torus_lines = Wireframe3D.torus(500, 500, 60, 25, rotation=(0.6, 0.3, 0))
        scene.add_wireframe(torus_lines, color="#cc7799", linewidth=1.0)
        scene.render_to_canvas(canvas)
        canvas.save("demo_geometric_primitives.png")
        print("[OK] Saved demo_geometric_primitives.png")

    @staticmethod
    def mathematical_surfaces():
        canvas = Canvas(900, 700, background="#0a0a15")
        scene = Scene3D()
        hfield = Surface3D.heightfield(
            250, 250, 200,
            lambda x, y: 30 * math.sin(x * 0.05) * math.cos(y * 0.05),
            n_lines=15, rotation=(0.5, 0.3, 0),
        )
        scene.add_surface(hfield, fill_color="#4466aa", alpha=0.7)
        mobius = Surface3D.moebius_strip(650, 250, 120, twists=1, width=0.5, n_lines=15)
        scene.add_surface(mobius, fill_color="#aa6644", alpha=0.6)
        klein = Surface3D.klein_bottle(450, 550, 100, n_lines=20)
        scene.add_surface(klein, fill_color="#44aa66", alpha=0.6)
        scene.render_to_canvas(canvas)
        canvas.save("demo_mathematical_surfaces.png")
        print("[OK] Saved demo_mathematical_surfaces.png")

    @staticmethod
    def spqr_3d():
        canvas = Canvas(900, 700, background="#0a0a15")
        scene = Scene3D()
        body_lines = Wireframe3D.sphere(450, 350, 120, n_rings=10, n_meridians=12, rotation=(0.3, 0.5, 0))
        scene.add_wireframe(body_lines, color="#c8b898", linewidth=1.2)
        shield_lines = Wireframe3D.dodecahedron(250, 350, 90, rotation=(0.4, 0.7, 0))
        scene.add_wireframe(shield_lines, color="#aa8844", linewidth=1.0)
        gladius_lines = Wireframe3D.cylinder(650, 350, 8, 200, n_segments=8, rotation=(0, 0, 0.3))
        scene.add_wireframe(gladius_lines, color="#b0b0c0", linewidth=1.5)
        wing_l = Wireframe3D.torus(300, 200, 50, 10, n_major=16, n_minor=8, rotation=(0.8, 0.2, 0.5))
        scene.add_wireframe(wing_l, color="#8899bb", linewidth=0.8)
        wing_r = Wireframe3D.torus(600, 200, 50, 10, n_major=16, n_minor=8, rotation=(0.8, -0.2, -0.5))
        scene.add_wireframe(wing_r, color="#8899bb", linewidth=0.8)
        base = Surface3D.heightfield(
            450, 580, 250,
            lambda x, y: 10 * math.sin(x * 0.03) * math.cos(y * 0.03),
            n_lines=12, rotation=(0.6, 0.0, 0),
        )
        scene.add_surface(base, fill_color="#334455", alpha=0.4)
        scene.render_to_canvas(canvas)
        canvas.save("demo_spqr_3d.png")
        print("[OK] Saved demo_spqr_3d.png")


if __name__ == "__main__":
    print("[START] Running 3D demos...")
    Demo3D.geometric_primitives()
    Demo3D.mathematical_surfaces()
    Demo3D.spqr_3d()
    print("[DONE] All 3D demos completed.")
