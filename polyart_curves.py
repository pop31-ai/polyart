import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


# ============================================================
#  POLYART CURVES LIBRARY OF ELEGANCE
#  Polynomial curves for every body system
# ============================================================

PHI = (1 + np.sqrt(5)) / 2


class SkeletalCurves:
    """Bone and skeleton polynomial curves."""

    @staticmethod
    def skull(ax, cx=0, cy=0, s=1.0, c="#e8dcc8", lw=0.6, al=0.9):
        th = np.linspace(0, 2*np.pi, 120)
        cranium_x = cx + s*0.85*np.cos(th) * (1 + 0.15*np.cos(2*th))
        cranium_y = cy + s*1.1*np.sin(th)
        ax.plot(cranium_x, cranium_y, color=c, linewidth=lw, alpha=al)
        jaw_x = cx + s*0.6*np.cos(th[20:100])
        jaw_y = cy - s*0.3 + s*0.45*np.sin(th[20:100])
        ax.plot(jaw_x, jaw_y, color=c, linewidth=lw*0.8, alpha=al*0.8)
        for ex in [-0.28, 0.28]:
            orb_x, orb_y = cx + s*ex, cy + s*0.1
            orbit = plt.Circle((orb_x, orb_y), s*0.15, fill=False, edgecolor=c, linewidth=lw*0.7, alpha=al*0.8)
            ax.add_patch(orbit)

    @staticmethod
    def spine(ax, x0, y0, length=4.0, s=1.0, c="#e8dcc8", lw=0.5, al=0.85):
        n = 24
        t = np.linspace(0, 1, n)
        curve_x = x0 + s*0.15*np.sin(np.pi*t*1.5)
        curve_y = np.linspace(y0, y0 - length*s, n)
        for i in range(n - 1):
            w = lw * (1.0 - 0.3*t[i])
            ax.plot([curve_x[i], curve_x[i+1]], [curve_y[i], curve_y[i+1]],
                    color=c, linewidth=w, alpha=al)
        for i in range(0, n, 2):
            rib_w = s*0.4*(1 - t[i]*0.5)
            side = 1 if i % 4 == 0 else -1
            ax.plot([curve_x[i], curve_x[i] + side*rib_w],
                    [curve_y[i], curve_y[i] - s*0.1],
                    color=c, linewidth=lw*0.6, alpha=al*0.7)

    @staticmethod
    def ribcage(ax, cx=0, cy=0, s=1.0, c="#e8dcc8", lw=0.4, al=0.8):
        for i in range(8):
            ry = cy - i*s*0.25
            w = s*1.2*(1 - 0.08*i)
            th = np.linspace(0, np.pi, 40)
            rx = cx + w*np.cos(th)
            ryy = ry + s*0.3*np.sin(th)
            ax.plot(rx, ryy, color=c, linewidth=lw, alpha=al*(1 - 0.05*i))

    @staticmethod
    def pelvis(ax, cx=0, cy=0, s=1.0, c="#e8dcc8", lw=0.5, al=0.85):
        th = np.linspace(0, np.pi, 60)
        outer_x = cx + s*1.0*np.cos(th)
        outer_y = cy + s*0.5*np.sin(th)
        ax.plot(outer_x, outer_y, color=c, linewidth=lw, alpha=al)
        inner_x = cx + s*0.6*np.cos(th)
        inner_y = cy + s*0.3*np.sin(th)
        ax.plot(inner_x, inner_y, color=c, linewidth=lw*0.7, alpha=al*0.7)

    @staticmethod
    def long_bone(ax, x1, y1, x2, y2, s=1.0, c="#e8dcc8", lw=0.5, al=0.85):
        dx, dy = x2 - x1, y2 - y1
        length = np.sqrt(dx**2 + dy**2)
        angle = np.arctan2(dy, dx)
        t = np.linspace(0, 1, 60)
        w = s*0.08*(1 + 2*np.exp(-((t-0.08)/0.05)**2) + 2*np.exp(-((t-0.92)/0.05)**2))
        nx = -np.sin(angle)
        ny = np.cos(angle)
        sx = x1 + dx*t + w*nx
        sy = y1 + dy*t + w*ny
        sx2 = x1 + dx*t - w*nx
        sy2 = y1 + dy*t - w*ny
        ax.plot(sx, sy, color=c, linewidth=lw*0.5, alpha=al)
        ax.plot(sx2, sy2, color=c, linewidth=lw*0.5, alpha=al)

    @staticmethod
    def hand_skeleton(ax, cx=0, cy=0, s=1.0, c="#e8dcc8", lw=0.3, al=0.8):
        palm_x, palm_y = SkeletalCurves._oval_points(cx, cy, s*0.35, s*0.4)
        ax.plot(palm_x, palm_y, color=c, linewidth=lw, alpha=al)
        for i, (angle, length) in enumerate([
            (-0.4, 0.7), (-0.15, 0.85), (0.05, 0.9), (0.25, 0.8), (0.5, 0.6)
        ]):
            bx = cx + s*0.25*np.cos(angle - np.pi/2)
            by = cy + s*0.35 + s*0.05
            for j in range(3):
                seg = length * s * 0.3
                nx = bx + seg*np.cos(angle - np.pi/2)
                ny = by + seg*np.sin(angle - np.pi/2)
                ax.plot([bx, nx], [by, ny], color=c, linewidth=lw*0.7, alpha=al*0.8)
                bx, by = nx, ny

    @staticmethod
    def foot_skeleton(ax, cx=0, cy=0, s=1.0, c="#e8dcc8", lw=0.3, al=0.8):
        sole_x, sole_y = SkeletalCurves._oval_points(cx, cy, s*0.5, s*0.25)
        ax.plot(sole_x, sole_y, color=c, linewidth=lw, alpha=al)
        for i in range(5):
            tx = cx + s*(0.3 - i*0.12)
            ty = cy + s*0.25
            for j in range(3):
                nx = tx + s*0.08
                ny = ty + s*0.06
                ax.plot([tx, nx], [ty, ny], color=c, linewidth=lw*0.6, alpha=al*0.7)
                tx, ty = nx, ny

    @staticmethod
    def _oval_points(cx, cy, rx, ry, n=60):
        th = np.linspace(0, 2*np.pi, n)
        return cx + rx*np.cos(th), cy + ry*np.sin(th)


class MuscleCurves:
    """Muscle fiber and volume polynomial curves."""

    @staticmethod
    def bicep(ax, cx=0, cy=0, s=1.0, c="#b04040", lw=0.4, al=0.6):
        th = np.linspace(0, np.pi, 50)
        outer_x = cx + s*0.4*np.sin(th)
        outer_y = cy + s*1.5*th/np.pi
        inner_x = cx + s*0.15*np.sin(th)*np.sin(th)
        inner_y = cy + s*1.5*th/np.pi
        ax.fill_betweenx(outer_y, inner_x, outer_x, color=c, alpha=al*0.4)
        ax.plot(outer_x, outer_y, color=c, linewidth=lw, alpha=al)
        ax.plot(inner_x, inner_y, color=c, linewidth=lw*0.7, alpha=al*0.8)
        for i in range(8):
            t = i/8
            fx = cx + s*(0.15 + 0.25*np.sin(np.pi*t))*np.array([1, 0.8, 0.4])
            fy = cy + s*t*1.5 + np.array([0, 0, 0])
            ax.plot(fx, fy, color=c, linewidth=lw*0.3, alpha=al*0.4)

    @staticmethod
    def quadricep(ax, cx=0, cy=0, s=1.0, c="#a03535", lw=0.5, al=0.6):
        th = np.linspace(0, 1, 80)
        outer_x = cx + s*0.5*np.sin(np.pi*th)*np.exp(-0.5*th)
        outer_y = cy - s*2.0*th
        inner_x = cx + s*0.2*np.sin(np.pi*th)*np.exp(-0.3*th)
        inner_y = cy - s*2.0*th
        ax.fill_betweenx(outer_y, inner_x, outer_x, color=c, alpha=al*0.35)
        ax.plot(outer_x, outer_y, color=c, linewidth=lw, alpha=al)
        ax.plot(inner_x, inner_y, color=c, linewidth=lw*0.8, alpha=al*0.8)
        for i in range(12):
            t = i/12
            mx = cx + s*(0.2 + 0.3*np.sin(np.pi*t))*0.7
            my = cy - s*t*2.0
            ax.plot(mx, my, ".", color=c, markersize=0.8, alpha=al*0.3)

    @staticmethod
    def pectoral(ax, cx=0, cy=0, s=1.0, c="#b04040", lw=0.4, al=0.55):
        th = np.linspace(0, np.pi*0.8, 60)
        x = cx + s*0.8*np.cos(th)
        y = cy + s*0.4*np.sin(th)
        ax.fill(x, y, color=c, alpha=al*0.3)
        ax.plot(x, y, color=c, linewidth=lw, alpha=al)
        for i in range(6):
            t = i/6
            fx = cx + s*0.7*np.cos(t*np.pi*0.8)
            fy = cy + s*0.35*np.sin(t*np.pi*0.8)
            ax.plot([cx, fx], [cy, fy], color=c, linewidth=lw*0.3, alpha=al*0.35)

    @staticmethod
    def deltoid(ax, cx=0, cy=0, s=1.0, c="#a03535", lw=0.4, al=0.6):
        th = np.linspace(0, np.pi, 50)
        x = cx + s*0.5*np.cos(th)
        y = cy + s*0.4*np.sin(th)
        ax.fill(x, y, color=c, alpha=al*0.3)
        ax.plot(x, y, color=c, linewidth=lw, alpha=al)

    @staticmethod
    def abdominal(ax, cx=0, cy=0, s=1.0, c="#b04040", lw=0.3, al=0.5):
        for row in range(4):
            for col in range(2):
                bx = cx + s*(col - 0.5)*0.35
                by = cy - s*row*0.3
                seg_x, seg_y = MuscleCurves._oval_pts(bx, by, s*0.15, s*0.12)
                ax.fill(seg_x, seg_y, color=c, alpha=al*0.3)
                ax.plot(seg_x, seg_y, color=c, linewidth=lw, alpha=al*0.7)

    @staticmethod
    def calf(ax, cx=0, cy=0, s=1.0, c="#a03535", lw=0.4, al=0.6):
        t = np.linspace(0, 1, 80)
        outer_x = cx + s*0.35*np.sin(np.pi*t*0.6)*np.exp(-0.8*(t-0.3)**2)
        outer_y = cy - s*1.8*t
        inner_x = cx + s*0.1*np.sin(np.pi*t*0.5)
        inner_y = cy - s*1.8*t
        ax.fill_betweenx(outer_y, inner_x, outer_x, color=c, alpha=al*0.3)
        ax.plot(outer_x, outer_y, color=c, linewidth=lw, alpha=al)
        ax.plot(inner_x, inner_y, color=c, linewidth=lw*0.8, alpha=al*0.8)

    @staticmethod
    def gluteus(ax, cx=0, cy=0, s=1.0, c="#b04040", lw=0.4, al=0.55):
        for side in [-1, 1]:
            th = np.linspace(0, np.pi, 50)
            x = cx + side*s*0.3 + s*0.45*np.cos(th)
            y = cy + s*0.35*np.sin(th)
            ax.fill(x, y, color=c, alpha=al*0.3)
            ax.plot(x, y, color=c, linewidth=lw, alpha=al)

    @staticmethod
    def _oval_pts(cx, cy, rx, ry, n=40):
        th = np.linspace(0, 2*np.pi, n)
        return cx + rx*np.cos(th), cy + ry*np.sin(th)


class SkinCurves:
    """Skin contour, wrinkles, texture polynomial curves."""

    @staticmethod
    def face_contour(ax, cx=0, cy=0, s=1.0, c="#d4a574", lw=0.8, al=0.9):
        th = np.linspace(0, 2*np.pi, 150)
        x = cx + s*2.5*np.cos(th) * (1 + 0.08*np.cos(3*th))
        y = cy + s*3.2*np.sin(th) * (1 + 0.05*np.sin(2*th))
        ax.fill(x, y, color=c, alpha=al*0.3)
        ax.plot(x, y, color=c, linewidth=lw, alpha=al)

    @staticmethod
    def wrinkle_lines(ax, cx, cy, s=1.0, c="#b08050", lw=0.2, al=0.35, n_wrinkles=5):
        for i in range(n_wrinkles):
            t = np.linspace(0, 1, 40)
            offset = (i - n_wrinkles/2) * s*0.08
            wx = cx + offset + s*0.3*np.sin(4*np.pi*t + i)*np.exp(-2*(t-0.5)**2)
            wy = cy + s*1.5*(t - 0.5)
            ax.plot(wx, wy, color=c, linewidth=lw, alpha=al)

    @staticmethod
    def skin_texture_stipple(ax, cx, cy, rx, ry, n=150, c="#b08050", al=0.12):
        np.random.seed(42)
        angles = np.random.uniform(0, 2*np.pi, n)
        radii = np.random.uniform(0, 1, n)
        px = cx + rx*radii*np.cos(angles)
        py = cy + ry*radii*np.sin(angles)
        ax.plot(px, py, ".", color=c, markersize=0.4, alpha=al)

    @staticmethod
    def neck_skin(ax, cx=0, cy=0, s=1.0, c="#d4a574", lw=0.5, al=0.85):
        neck_x = [cx - s*0.8, cx - s*0.6, cx - s*0.5, cx + s*0.5, cx + s*0.6, cx + s*0.8]
        neck_y = [cy + s*0.5, cy + s*0.2, cy - s*0.5, cy - s*0.5, cy + s*0.2, cy + s*0.5]
        ax.plot(neck_x, neck_y, color=c, linewidth=lw, alpha=al)
        for i in range(3):
            wy = cy - s*0.1 - i*s*0.15
            ax.plot([cx - s*0.4, cx + s*0.4], [wy, wy], color="#b08050", linewidth=0.3, alpha=0.3)

    @staticmethod
    def ear_contour(ax, cx=0, cy=0, s=1.0, c="#d4a574", lw=0.5, al=0.85):
        th = np.linspace(0, 2*np.pi, 80)
        x = cx + s*0.4*np.cos(th) * (1 + 0.3*np.sin(th))
        y = cy + s*0.8*np.sin(th)
        ax.plot(x, y, color=c, linewidth=lw, alpha=al)
        inner_th = np.linspace(0.3, 2*np.pi - 0.3, 60)
        ix = cx + s*0.2*np.cos(inner_th)
        iy = cy + s*0.5*np.sin(inner_th)
        ax.plot(ix, iy, color=c, linewidth=lw*0.6, alpha=al*0.6)


class VeinCurves:
    """Venous network polynomial curves."""

    @staticmethod
    def arm_veins(ax, cx=0, cy=0, s=1.0, c="#2040a0", lw=0.25, al=0.5):
        for offset, wav in [(-0.15, 2.5), (0.05, 3.0), (0.2, 1.8)]:
            t = np.linspace(0, 1, 80)
            vx = cx + s*offset + s*0.08*np.sin(wav*np.pi*t)
            vy = cy + s*2.0*(1 - t)
            ax.plot(vx, vy, color=c, linewidth=lw, alpha=al)
            for branch in range(3):
                bt = 0.2 + branch*0.3
                bx = cx + s*offset + s*0.08*np.sin(wav*np.pi*bt)
                by = cy + s*2.0*(1 - bt)
                angle = np.random.uniform(-0.8, 0.8)
                bl = s*0.2*np.random.uniform(0.5, 1)
                ax.plot([bx, bx + bl*np.cos(angle)], [by, by + bl*np.sin(angle)],
                        color=c, linewidth=lw*0.5, alpha=al*0.6)

    @staticmethod
    def leg_veins(ax, cx=0, cy=0, s=1.0, c="#2040a0", lw=0.25, al=0.45):
        for offset in [-0.2, 0.0, 0.15]:
            t = np.linspace(0, 1, 100)
            vx = cx + s*offset + s*0.06*np.sin(4*np.pi*t) + s*0.03*np.sin(7*np.pi*t)
            vy = cy - s*3.0*t
            ax.plot(vx, vy, color=c, linewidth=lw, alpha=al)
            for branch in range(4):
                bt = 0.15 + branch*0.22
                bx = cx + s*offset + s*0.06*np.sin(4*np.pi*bt)
                by = cy - s*3.0*bt
                side = 1 if branch % 2 == 0 else -1
                bl = s*0.15
                ax.plot([bx, bx + side*bl], [by, by - s*0.05],
                        color=c, linewidth=lw*0.5, alpha=al*0.5)

    @staticmethod
    def heart_vessels(ax, cx=0, cy=0, s=1.0, c="#c02020", lw=0.3, al=0.55):
        paths = [
            [(0, 0.8), (-0.3, 1.2), (-0.5, 1.5)],
            [(0, 0.8), (0.2, 1.3), (0.4, 1.6)],
            [(-0.2, 0.5), (-0.6, 0.8), (-0.9, 0.6)],
            [(0.2, 0.5), (0.6, 0.8), (0.9, 0.6)],
        ]
        for path in paths:
            xs = [cx + s*p[0] for p in path]
            ys = [cy + s*p[1] for p in path]
            ax.plot(xs, ys, color=c, linewidth=lw, alpha=al)

    @staticmethod
    def capillary_network(ax, cx, cy, r=1.0, n=30, c="#4060c0", lw=0.1, al=0.3):
        np.random.seed(7)
        for _ in range(n):
            ang = np.random.uniform(0, 2*np.pi)
            rad = np.random.uniform(0, r)
            x0 = cx + rad*np.cos(ang)
            y0 = cy + rad*np.sin(ang)
            t = np.linspace(0, 1, 20)
            nx = x0 + r*0.15*np.sin(5*np.pi*t + ang)
            ny = y0 + r*0.15*np.cos(3*np.pi*t + ang)
            ax.plot(nx, ny, color=c, linewidth=lw, alpha=al)


class NerveCurves:
    """Neural network and nerve pathway polynomial curves."""

    @staticmethod
    def nerve_fiber(ax, x1, y1, x2, y2, s=1.0, c="#e0c040", lw=0.2, al=0.5):
        t = np.linspace(0, 1, 80)
        dx, dy = x2 - x1, y2 - y1
        nx = x1 + dx*t + s*0.1*np.sin(8*np.pi*t)*np.exp(-2*(t-0.5)**2)
        ny = y1 + dy*t + s*0.05*np.cos(6*np.pi*t)*np.exp(-2*(t-0.5)**2)
        ax.plot(nx, ny, color=c, linewidth=lw, alpha=al)

    @staticmethod
    def brain_network(ax, cx=0, cy=0, s=1.0, c="#e0c040", lw=0.15, al=0.4, n_nodes=20):
        np.random.seed(99)
        angles = np.random.uniform(0, 2*np.pi, n_nodes)
        radii = np.random.uniform(0.2, 0.9, n_nodes)
        nodes_x = cx + s*radii*np.cos(angles)
        nodes_y = cy + s*radii*0.8*np.sin(angles)
        for i in range(n_nodes):
            for j in range(i+1, n_nodes):
                dist = np.sqrt((nodes_x[i]-nodes_x[j])**2 + (nodes_y[i]-nodes_y[j])**2)
                if dist < s*0.6:
                    t = np.linspace(0, 1, 30)
                    mx = (nodes_x[i]+nodes_x[j])/2 + s*0.05*np.sin(3*np.pi*t)
                    my = (nodes_y[i]+nodes_y[j])/2 + s*0.05*np.cos(4*np.pi*t)
                    ax.plot(np.linspace(nodes_x[i], nodes_x[j], 30) + s*0.03*np.sin(5*np.pi*t),
                            np.linspace(nodes_y[i], nodes_y[j], 30) + s*0.03*np.cos(4*np.pi*t),
                            color=c, linewidth=lw, alpha=al*(1 - dist/(s*0.6)))
        for x, y in zip(nodes_x, nodes_y):
            ax.plot(x, y, "o", color=c, markersize=1.5, alpha=al*1.5)

    @staticmethod
    def spinal_nerve(ax, cx=0, cy=0, s=1.0, c="#e0c040", lw=0.2, al=0.45):
        for i in range(10):
            ny = cy - i*s*0.3
            for side in [-1, 1]:
                t = np.linspace(0, 1, 40)
                nx = cx + side*s*(0.3*t + 0.2*t**2 + 0.1*np.sin(3*np.pi*t))
                nny = ny - s*0.15*t
                ax.plot(nx, nny, color=c, linewidth=lw, alpha=al*(1 - i*0.08))

    @staticmethod
    def dendrite(ax, cx, cy, s=1.0, c="#e0c040", lw=0.15, al=0.4):
        def branch(x, y, angle, length, depth):
            if depth <= 0 or length < 0.05:
                return
            ex = x + length*np.cos(angle)
            ey = y + length*np.sin(angle)
            ax.plot([x, ex], [y, ey], color=c, linewidth=lw*depth/4, alpha=al*depth/4)
            branch(ex, ey, angle - 0.4, length*0.7, depth - 1)
            branch(ex, ey, angle + 0.4, length*0.7, depth - 1)
        branch(cx, cy, -np.pi/2, s*0.5, 5)


class LimbCurves:
    """Arm, leg, hand, foot contour polynomial curves."""

    @staticmethod
    def arm_contour(ax, cx=0, cy=0, s=1.0, c="#d4a574", lw=0.6, al=0.85):
        t = np.linspace(0, 1, 100)
        outer_x = cx + s*(0.3 + 0.2*np.sin(np.pi*t*0.3))*np.exp(-0.3*t)
        outer_y = cy + s*2.0*(1 - t)
        inner_x = cx + s*(-0.15 + 0.1*np.sin(np.pi*t*0.4))
        inner_y = cy + s*2.0*(1 - t)
        ax.fill_betweenx(outer_y, inner_x, outer_x, color=c, alpha=al*0.3)
        ax.plot(outer_x, outer_y, color=c, linewidth=lw, alpha=al)
        ax.plot(inner_x, inner_y, color=c, linewidth=lw, alpha=al)

    @staticmethod
    def leg_contour(ax, cx=0, cy=0, s=1.0, c="#d4a574", lw=0.6, al=0.85):
        t = np.linspace(0, 1, 120)
        outer_x = cx + s*(0.35 + 0.15*np.sin(np.pi*t*0.4)*np.exp(-t))
        outer_y = cy - s*3.5*t
        inner_x = cx + s*(-0.15 - 0.05*np.sin(np.pi*t*0.3))
        inner_y = cy - s*3.5*t
        ax.fill_betweenx(outer_y, inner_x, outer_x, color=c, alpha=al*0.3)
        ax.plot(outer_x, outer_y, color=c, linewidth=lw, alpha=al)
        ax.plot(inner_x, inner_y, color=c, linewidth=lw, alpha=al)

    @staticmethod
    def hand_contour(ax, cx=0, cy=0, s=1.0, c="#d4a574", lw=0.5, al=0.85):
        palm_x, palm_y = SkeletalCurves._oval_points(cx, cy, s*0.4, s*0.5)
        ax.fill(palm_x, palm_y, color=c, alpha=al*0.3)
        ax.plot(palm_x, palm_y, color=c, linewidth=lw, alpha=al)
        for angle, length in [(-0.5, 0.55), (-0.2, 0.7), (0.05, 0.75), (0.3, 0.65), (0.55, 0.45)]:
            bx = cx + s*0.35*np.cos(angle - np.pi/2)
            by = cy + s*0.5
            finger_x = [bx, bx + s*length*0.4*np.cos(angle - np.pi/2)]
            finger_y = [by, by + s*length*0.4*np.sin(angle - np.pi/2) + s*length*0.5]
            ax.plot(finger_x, finger_y, color=c, linewidth=lw*0.8, alpha=al*0.9)
            t = np.linspace(0, 1, 10)
            tip_x = finger_x[-1] + s*0.06*np.cos(np.linspace(-0.5, 0.5, 10))
            tip_y = finger_y[-1] + s*0.06*np.sin(np.linspace(-0.5, 0.5, 10))
            ax.plot(tip_x, tip_y, color=c, linewidth=lw*0.5, alpha=al*0.8)

    @staticmethod
    def foot_contour(ax, cx=0, cy=0, s=1.0, c="#d4a574", lw=0.5, al=0.85):
        t = np.linspace(0, 1, 80)
        sole_x = cx + s*0.5*np.cos(np.pi*t)
        sole_y = cy + s*0.3*np.sin(np.pi*t) - s*0.2*np.exp(-3*(t-0.5)**2)
        ax.fill(sole_x, sole_y, color=c, alpha=al*0.3)
        ax.plot(sole_x, sole_y, color=c, linewidth=lw, alpha=al)

    @staticmethod
    def shoulder(ax, cx=0, cy=0, s=1.0, c="#d4a574", lw=0.6, al=0.85):
        th = np.linspace(0, np.pi, 60)
        x = cx + s*0.8*np.cos(th)
        y = cy + s*0.5*np.sin(th)
        ax.fill(x, y, color=c, alpha=al*0.3)
        ax.plot(x, y, color=c, linewidth=lw, alpha=al)


class HeadCurves:
    """Head, face features, hair polynomial curves."""

    @staticmethod
    def head_shape(ax, cx=0, cy=0, s=1.0, c="#d4a574", lw=0.7, al=0.9):
        th = np.linspace(0, 2*np.pi, 150)
        x = cx + s*2.7*np.cos(th)*(1 + 0.06*np.cos(2*th))
        y = cy + s*3.4*np.sin(th)*(1 + 0.03*np.sin(3*th))
        ax.fill(x, y, color=c, alpha=al*0.35)
        ax.plot(x, y, color=c, linewidth=lw, alpha=al)

    @staticmethod
    def eye(ax, cx=0, cy=0, s=1.0, c1="#d4a574", c2="#2a1a0a", lw=0.4, al=0.9):
        lid_x = np.linspace(cx - s*0.4, cx + s*0.4, 60)
        upper = cy + s*0.15*np.cos(np.pi*(lid_x - cx)/(s*0.4))
        lower = cy - s*0.1*np.cos(np.pi*(lid_x - cx)/(s*0.4))
        ax.fill_between(lid_x, lower, upper, color=c1, alpha=al*0.5)
        ax.plot(lid_x, upper, color=c1, linewidth=lw*2, alpha=al)
        ax.plot(lid_x, lower, color=c1, linewidth=lw, alpha=al*0.8)
        iris = plt.Circle((cx, cy), s*0.12, color=c2, alpha=al*0.9)
        ax.add_patch(iris)
        pupil = plt.Circle((cx, cy), s*0.05, color="#050505", alpha=al)
        ax.add_patch(pupil)
        highlight = plt.Circle((cx + s*0.04, cy + s*0.04), s*0.03, color="white", alpha=0.5)
        ax.add_patch(highlight)

    @staticmethod
    def nose(ax, cx=0, cy=0, s=1.0, c="#b08050", lw=0.5, al=0.8):
        bridge_x = [cx, cx - s*0.05, cx - s*0.08, cx - s*0.05, cx + s*0.1]
        bridge_y = [cy + s*1.0, cy + s*0.5, cy, cy - s*0.2, cy - s*0.4]
        ax.plot(bridge_x, bridge_y, color=c, linewidth=lw, alpha=al)
        tip_x, tip_y = MuscleCurves._oval_pts(cx + s*0.05, cy - s*0.5, s*0.2, s*0.15)
        ax.plot(tip_x, tip_y, color=c, linewidth=lw*0.7, alpha=al*0.8)
        for dx in [-0.15, 0.25]:
            nostril = plt.Circle((cx + s*dx, cy - s*0.6), s*0.06, color="#3a2010", alpha=0.6)
            ax.add_patch(nostril)

    @staticmethod
    def mouth(ax, cx=0, cy=0, s=1.0, c="#a06040", lw=0.4, al=0.8):
        t = np.linspace(-1, 1, 60)
        upper_y = cy + s*0.08*np.sin(np.pi*t)*np.exp(-t**2)
        lower_y = cy - s*0.1*np.sin(np.pi*t)
        ax.plot(cx + s*0.5*t, upper_y, color=c, linewidth=lw, alpha=al)
        ax.plot(cx + s*0.5*t, lower_y, color=c, linewidth=lw*1.2, alpha=al*0.9)

    @staticmethod
    def eyebrow(ax, cx=0, cy=0, s=1.0, c="#4a2a10", lw=0.8, al=0.7):
        t = np.linspace(-1, 1, 40)
        y = cy + s*0.08*np.exp(-2*t**2)
        ax.plot(cx + s*0.4*t, y, color=c, linewidth=lw, alpha=al)

    @staticmethod
    def hair_strands(ax, cx, cy, s=1.0, c="#2a1a0a", lw=0.2, al=0.5, n=30):
        for i in range(n):
            th = np.linspace(-2, 0.3, 40) + i*0.08
            hx = cx + s*3.0*np.cos(th)*np.exp(-0.25*th)
            hy = cy + s*1.5*np.sin(th)*np.exp(-0.15*th)
            ax.plot(hx, hy, color=c, linewidth=lw, alpha=al)


class FigureCurves:
    """Complete human figure polynomial curves."""

    @staticmethod
    def full_body_front(ax, cx=0, cy=0, s=1.0, fc="#d4a574", ec="#c8a040", lw=0.5, al=0.85):
        HeadCurves.head_shape(ax, cx, cy + s*5.5, s*0.7, fc, lw)
        NeckCurves._draw_neck(ax, cx, cy + s*4.2, s)
        for side in [-1, 1]:
            LimbCurves.arm_contour(ax, cx + side*s*1.5, cy + s*3.5, s*0.7, fc, lw, al)
        torso_x = [cx - s*1.2, cx - s*0.8, cx - s*0.5, cx + s*0.5, cx + s*0.8, cx + s*1.2,
                   cx + s*0.8, cx + s*0.5, cx - s*0.5, cx - s*0.8, cx - s*1.2]
        torso_y = [cy + s*3.5, cy + s*2.5, cy + s*1.5, cy + s*1.5, cy + s*2.5, cy + s*3.5,
                   cy - s*0.5, cy - s*1.5, cy - s*1.5, cy - s*0.5, cy + s*3.5]
        ax.plot(torso_x, torso_y, color=ec, linewidth=lw, alpha=al*0.8)
        for side in [-1, 1]:
            LimbCurves.leg_contour(ax, cx + side*s*0.5, cy - s*1.5, s*0.8, fc, lw, al)

    @staticmethod
    def full_body_side(ax, cx=0, cy=0, s=1.0, fc="#d4a574", ec="#c8a040", lw=0.5, al=0.85):
        HeadCurves.head_shape(ax, cx + s*0.3, cy + s*5.5, s*0.65, fc, lw)
        t = np.linspace(0, 1, 80)
        spine_x = cx + s*0.15*np.sin(np.pi*t*1.2)
        spine_y = np.linspace(cy + s*4.0, cy - s*1.5, 80)
        ax.plot(spine_x, spine_y, color=ec, linewidth=lw*0.8, alpha=al*0.6)
        front_x = cx + s*(0.3 - 0.15*t**2)
        back_x = cx + s*(-0.2 + 0.1*t)
        ax.plot(front_x, spine_y, color=fc, linewidth=lw, alpha=al)
        ax.plot(back_x, spine_y, color=fc, linewidth=lw, alpha=al)
        LimbCurves.arm_contour(ax, cx + s*0.5, cy + s*3.0, s*0.6, fc, lw*0.8, al*0.8)
        LimbCurves.leg_contour(ax, cx - s*0.1, cy - s*1.5, s*0.7, fc, lw, al)

    @staticmethod
    def seated_figure(ax, cx=0, cy=0, s=1.0, fc="#d4a574", ec="#c8a040", lw=0.5, al=0.85):
        HeadCurves.head_shape(ax, cx, cy + s*4.5, s*0.65, fc, lw)
        t = np.linspace(0, 1, 50)
        torso_x = cx + s*0.1*np.sin(np.pi*t)
        torso_y = np.linspace(cy + s*3.5, cy + s*1.5, 50)
        ax.plot(torso_x, torso_y, color=ec, linewidth=lw, alpha=al)
        seat_y = cy + s*1.5
        ax.plot([cx - s*1.5, cx + s*1.5], [seat_y, seat_y], color=ec, linewidth=lw*2, alpha=al*0.5)
        for side in [-1, 1]:
            thigh_x = [cx + side*s*0.2, cx + side*s*0.8]
            thigh_y = [cy + s*1.5, cy + s*1.3]
            ax.plot(thigh_x, thigh_y, color=fc, linewidth=lw*2, alpha=al)
            shin_x = [cx + side*s*0.8, cx + side*s*0.8]
            shin_y = [cy + s*1.3, cy]
            ax.plot(shin_x, shin_y, color=fc, linewidth=lw*1.5, alpha=al*0.9)


class NeckCurves:
    @staticmethod
    def _draw_neck(ax, cx, cy, s=1.0, c="#d4a574", lw=0.5, al=0.85):
        ax.plot([cx - s*0.5, cx - s*0.4], [cy + s*0.5, cy], color=c, linewidth=lw, alpha=al)
        ax.plot([cx + s*0.5, cx + s*0.4], [cy + s*0.5, cy], color=c, linewidth=lw, alpha=al)


# ============================================================
#  DEMO
# ============================================================

def _oval_pts(cx, cy, rx, ry, n=60):
    th = np.linspace(0, 2*np.pi, n)
    return cx + rx*np.cos(th), cy + ry*np.sin(th)

MuscleCurves._oval_pts = staticmethod(_oval_pts)
SkeletalCurves._oval_points = staticmethod(_oval_pts)


if __name__ == "__main__":
    print("[START] Generating curves library showcase...")

    fig, axes = plt.subplots(3, 3, figsize=(20, 22), dpi=150)
    fig.patch.set_facecolor("#0d0a1a")
    fig.suptitle("POLYART: Curves Library of Elegance",
                 fontsize=18, color="#c8a040", fontweight="bold", fontfamily="serif")

    panels = [
        ("Skeletal System", lambda ax: (
            SkeletalCurves.skull(ax, 0, 4, 0.8),
            SkeletalCurves.ribcage(ax, 0, 2, 0.7),
            SkeletalCurves.spine(ax, 0, 4, 3, 0.6),
            SkeletalCurves.pelvis(ax, 0, 0.5, 0.7),
            SkeletalCurves.hand_skeleton(ax, 2.5, 2, 0.5),
            SkeletalCurves.foot_skeleton(ax, -2.5, 0, 0.5),
            ax.set_title("Skeletal", fontsize=12, color="#c8a040"),
        )),
        ("Muscular System", lambda ax: (
            MuscleCurves.pectoral(ax, 0, 3, 0.8),
            MuscleCurves.deltoid(ax, -1, 3.5, 0.6),
            MuscleCurves.deltoid(ax, 1, 3.5, 0.6),
            MuscleCurves.bicep(ax, -1.2, 2.5, 0.5),
            MuscleCurves.bicep(ax, 1.2, 2.5, 0.5),
            MuscleCurves.abdominal(ax, 0, 1.5, 0.7),
            MuscleCurves.quadricep(ax, -0.5, 0, 0.6),
            MuscleCurves.quadricep(ax, 0.5, 0, 0.6),
            MuscleCurves.calf(ax, -0.5, -2, 0.5),
            MuscleCurves.calf(ax, 0.5, -2, 0.5),
            MuscleCurves.gluteus(ax, 0, 0.5, 0.6),
            ax.set_title("Muscular", fontsize=12, color="#c8a040"),
        )),
        ("Skin & Surface", lambda ax: (
            SkinCurves.face_contour(ax, 0, 4, 0.7),
            SkinCurves.wrinkle_lines(ax, -0.3, 4.2, 0.3),
            SkinCurves.wrinkle_lines(ax, 0.3, 4.2, 0.3),
            SkinCurves.skin_texture_stipple(ax, 0, 4, 1.5, 2),
            SkinCurves.neck_skin(ax, 0, 2.5, 0.6),
            SkinCurves.ear_contour(ax, -1.5, 4, 0.4),
            SkinCurves.ear_contour(ax, 1.5, 4, 0.4),
            ax.set_title("Skin & Surface", fontsize=12, color="#c8a040"),
        )),
        ("Venous System", lambda ax: (
            VeinCurves.arm_veins(ax, -1.5, 3, 0.6),
            VeinCurves.arm_veins(ax, 1.5, 3, 0.6),
            VeinCurves.leg_veins(ax, -0.5, 0, 0.5),
            VeinCurves.leg_veins(ax, 0.5, 0, 0.5),
            VeinCurves.heart_vessels(ax, 0, 3, 0.8),
            VeinCurves.capillary_network(ax, 0, 3, 0.5, 40),
            ax.set_title("Venous System", fontsize=12, color="#c8a040"),
        )),
        ("Nervous System", lambda ax: (
            NerveCurves.brain_network(ax, 0, 5, 0.8),
            NerveCurves.spinal_nerve(ax, 0, 3, 0.7),
            [NerveCurves.nerve_fiber(ax, -1, 4+i*0.3, -2, 3+i*0.3, 0.3) for i in range(5)],
            [NerveCurves.nerve_fiber(ax, 1, 4+i*0.3, 2, 3+i*0.3, 0.3) for i in range(5)],
            NerveCurves.dendrite(ax, 0, 6, 0.4),
            ax.set_title("Nervous System", fontsize=12, color="#c8a040"),
        )),
        ("Limb Contours", lambda ax: (
            LimbCurves.arm_contour(ax, -2, 4, 0.7),
            LimbCurves.arm_contour(ax, 2, 4, 0.7),
            LimbCurves.hand_contour(ax, -2, 6, 0.5),
            LimbCurves.hand_contour(ax, 2, 6, 0.5),
            LimbCurves.leg_contour(ax, -0.5, 2, 0.7),
            LimbCurves.leg_contour(ax, 0.5, 2, 0.7),
            LimbCurves.foot_contour(ax, -0.5, -1.5, 0.5),
            LimbCurves.foot_contour(ax, 0.5, -1.5, 0.5),
            LimbCurves.shoulder(ax, -1, 5, 0.5),
            LimbCurves.shoulder(ax, 1, 5, 0.5),
            ax.set_title("Limb Contours", fontsize=12, color="#c8a040"),
        )),
        ("Head & Face", lambda ax: (
            HeadCurves.head_shape(ax, 0, 3, 0.8),
            HeadCurves.eye(ax, -0.4, 3.3, 0.3),
            HeadCurves.eye(ax, 0.4, 3.3, 0.3),
            HeadCurves.nose(ax, 0, 2.8, 0.4),
            HeadCurves.mouth(ax, 0, 2.2, 0.4),
            HeadCurves.eyebrow(ax, -0.4, 3.6, 0.3),
            HeadCurves.eyebrow(ax, 0.4, 3.6, 0.3),
            HeadCurves.hair_strands(ax, 0, 4.5, 0.6, n=20),
            ax.set_title("Head & Face", fontsize=12, color="#c8a040"),
        )),
        ("Full Body Front", lambda ax: (
            FigureCurves.full_body_front(ax, 0, 0, 0.5),
            ax.set_title("Full Body (Front)", fontsize=12, color="#c8a040"),
        )),
        ("Full Body Variants", lambda ax: (
            FigureCurves.full_body_side(ax, -1.5, 0, 0.4),
            FigureCurves.seated_figure(ax, 1.5, -0.5, 0.4),
            ax.set_title("Side View & Seated", fontsize=12, color="#c8a040"),
        )),
    ]

    for idx, (title, draw_fn) in enumerate(panels):
        ax = axes[idx // 3][idx % 3]
        ax.set_xlim(-4, 4)
        ax.set_ylim(-3.5, 7)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor("#0d0a1a")
        draw_fn(ax)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = r"C:\Users\e\Desktop\6756756756756756\curves_library_showcase.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0d0a1a")
    plt.close(fig)
    print(f"[OK] Saved: {out}")
    print("[DONE] Curves library showcase complete.")
