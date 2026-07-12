import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


# ============================================================
#  POLYART ANIMAL BODY TEMPLATES
#  Polynomial-based animal silhouettes and poses
# ============================================================


def _oval(cx, cy, rx, ry, n=80):
    th = np.linspace(0, 2*np.pi, n)
    return (cx + rx*np.cos(th)).tolist(), (cy + ry*np.sin(th)).tolist()


class AnimalTemplates:
    """Templates for various animal bodies using polynomial curves."""

    @staticmethod
    def lion(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Lion: powerful body, mane, proud stance."""
        s = scale
        # Body
        bx, by = _oval(cx, cy + 2.0*s, 2.5*s, 1.2*s)
        canvas.add(bx, by, fill_color="#c8a040", fill_alpha=0.9,
                   edge_color="#8b6020", edge_width=0.04)
        # Mane (radiating circles)
        for i in range(16):
            ang = i * 2*np.pi/16
            mx = cx + 1.8*s + 0.8*s*np.cos(ang)
            my = cy + 2.8*s + 0.8*s*np.sin(ang)
            mnx, mny = _oval(mx, my, 0.5*s, 0.5*s)
            canvas.add(mnx, mny, fill_color="#b08030", fill_alpha=0.7,
                       edge_color="#8b6020", edge_width=0.02)
        # Head
        hx, hy = _oval(cx + 2.0*s, cy + 3.0*s, 0.7*s, 0.6*s)
        canvas.add(hx, hy, fill_color="#c8a040", fill_alpha=1.0,
                   edge_color="#8b6020", edge_width=0.03)
        # Eyes
        canvas.circle(cx + 2.2*s, cy + 3.1*s, 0.06*s, fill=True,
                      fill_color="#1a0a05", fill_alpha=0.9)
        # Nose
        canvas.circle(cx + 2.5*s, cy + 2.9*s, 0.04*s, fill=True,
                      fill_color="#3a2010", fill_alpha=0.9)
        # Legs
        for lx, ly in [(cx - 1.5*s, cy + 1.0*s), (cx - 0.5*s, cy + 1.0*s),
                        (cx + 0.5*s, cy + 1.0*s), (cx + 1.5*s, cy + 1.0*s)]:
            canvas.line(lx, ly, lx, cy, color="#c8a040", linewidth=0.08)
            canvas.line(lx, cy, lx + 0.1*s, cy - 0.1*s, color="#c8a040", linewidth=0.06)
        # Tail (curved upward)
        t = np.linspace(0, 1, 30)
        tail_x = cx - 2.5*s + 0.5*s*t
        tail_y = cy + 2.5*s + 1.5*s*t**2
        canvas.line(tail_x, tail_y, color="#c8a040", linewidth=0.04)
        # Tail tuft
        canvas.circle(cx - 2.0*s, cy + 4.0*s, 0.15*s, fill=True,
                      fill_color="#b08030", fill_alpha=0.8)

    @staticmethod
    def eagle(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Eagle: spread wings, sharp beak, talons."""
        s = scale
        # Body
        bx, by = _oval(cx, cy + 3.0*s, 1.0*s, 0.6*s)
        canvas.add(bx, by, fill_color="#3a2a1a", fill_alpha=0.95,
                   edge_color="#c8a040", edge_width=0.03)
        # Head
        hx, hy = _oval(cx + 1.0*s, cy + 3.3*s, 0.4*s, 0.35*s)
        canvas.add(hx, hy, fill_color="#f0f0f0", fill_alpha=0.95,
                   edge_color="#c8a040", edge_width=0.02)
        # Eye
        canvas.circle(cx + 1.2*s, cy + 3.4*s, 0.04*s, fill=True,
                      fill_color="#ffd700", fill_alpha=0.9)
        canvas.circle(cx + 1.2*s, cy + 3.4*s, 0.02*s, fill=True,
                      fill_color="#1a0a05", fill_alpha=0.95)
        # Beak (hooked)
        beak_x = [cx + 1.4*s, cx + 1.7*s, cx + 1.5*s, cx + 1.4*s]
        beak_y = [cy + 3.3*s, cy + 3.2*s, cy + 3.1*s, cy + 3.3*s]
        canvas.line(beak_x, beak_y, color="#ffd700", linewidth=0.04)
        # Left wing (spread)
        wing_l_x = np.linspace(cx - 0.5*s, cx - 3.5*s, 40)
        wing_l_y = cy + 3.5*s + 1.5*s*np.sin(np.pi*(wing_l_x - cx + 0.5*s)/(-3.0*s))
        canvas.line(wing_l_x, wing_l_y, color="#3a2a1a", linewidth=0.06, alpha=0.9)
        # Wing feather lines
        for i in range(8):
            fx = cx - 0.8*s - i*0.35*s
            fy = cy + 3.5*s + 1.2*s*np.sin(np.pi*i/8)
            canvas.line(fx, fy, fx - 0.2*s, fy - 0.8*s,
                        color="#3a2a1a", linewidth=0.03, alpha=0.7)
        # Right wing (spread)
        wing_r_x = np.linspace(cx + 0.5*s, cx + 3.5*s, 40)
        wing_r_y = cy + 3.5*s + 1.5*s*np.sin(np.pi*(wing_r_x - cx - 0.5*s)/(3.0*s))
        canvas.line(wing_r_x, wing_r_y, color="#3a2a1a", linewidth=0.06, alpha=0.9)
        for i in range(8):
            fx = cx + 0.8*s + i*0.35*s
            fy = cy + 3.5*s + 1.2*s*np.sin(np.pi*i/8)
            canvas.line(fx, fy, fx + 0.2*s, fy - 0.8*s,
                        color="#3a2a1a", linewidth=0.03, alpha=0.7)
        # Tail feathers
        for i in range(5):
            ang = np.pi + (i-2)*0.15
            canvas.line(cx - 1.0*s, cy + 3.0*s,
                        cx - 1.0*s + 0.8*s*np.cos(ang),
                        cy + 3.0*s + 0.8*s*np.sin(ang),
                        color="#3a2a1a", linewidth=0.04, alpha=0.8)
        # Talons
        for tx in [cx - 0.3*s, cx + 0.3*s]:
            canvas.line(tx, cy + 2.4*s, tx, cy + 2.0*s, color="#ffd700", linewidth=0.03)
            for j in range(3):
                canvas.line(tx, cy + 2.0*s,
                            tx + (j-1)*0.1*s, cy + 1.8*s,
                            color="#ffd700", linewidth=0.02)

    @staticmethod
    def wolf(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Wolf: lean body, alert posture, howling."""
        s = scale
        # Body (lean)
        bx, by = _oval(cx, cy + 2.5*s, 2.0*s, 0.8*s)
        canvas.add(bx, by, fill_color="#5a5a6a", fill_alpha=0.9,
                   edge_color="#3a3a4a", edge_width=0.03)
        # Head (tilted up - howling)
        hx, hy = _oval(cx + 1.8*s, cy + 3.8*s, 0.5*s, 0.5*s)
        canvas.add(hx, hy, fill_color="#6a6a7a", fill_alpha=0.95,
                   edge_color="#3a3a4a", edge_width=0.03)
        # Snout (pointed, upward)
        snout_x = [cx + 2.2*s, cx + 2.6*s, cx + 2.3*s, cx + 2.2*s]
        snout_y = [cy + 3.8*s, cy + 4.2*s, cy + 4.3*s, cy + 3.8*s]
        canvas.line(snout_x, snout_y, color="#6a6a7a", linewidth=0.05, alpha=0.9)
        # Eye
        canvas.circle(cx + 2.0*s, cy + 3.9*s, 0.04*s, fill=True,
                      fill_color="#ffd700", fill_alpha=0.9)
        # Ears (pointed)
        ear_l = [cx + 1.5*s, cx + 1.3*s, cx + 1.6*s]
        ear_ly = [cy + 4.3*s, cy + 4.8*s, cy + 4.3*s]
        canvas.line(ear_l, ear_ly, color="#5a5a6a", linewidth=0.04)
        ear_r = [cx + 2.0*s, cx + 2.2*s, cx + 1.9*s]
        ear_ry = [cy + 4.3*s, cy + 4.8*s, cy + 4.3*s]
        canvas.line(ear_r, ear_ry, color="#5a5a6a", linewidth=0.04)
        # Legs (lean)
        for lx in [cx - 1.2*s, cx - 0.4*s, cx + 0.4*s, cx + 1.2*s]:
            canvas.line(lx, cy + 1.7*s, lx, cy, color="#5a5a6a", linewidth=0.06)
            canvas.line(lx, cy, lx + 0.1*s, cy - 0.1*s, color="#5a5a6a", linewidth=0.04)
        # Tail (bushy, curved)
        t = np.linspace(0, 1, 30)
        tail_x = cx - 2.0*s - 0.5*s*t
        tail_y = cy + 2.8*s + 0.8*s*t**1.5
        canvas.line(tail_x, tail_y, color="#5a5a6a", linewidth=0.05, alpha=0.8)

    @staticmethod
    def horse(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Horse: galloping, flowing mane and tail."""
        s = scale
        # Body (muscular)
        bx, by = _oval(cx, cy + 3.0*s, 2.5*s, 1.0*s)
        canvas.add(bx, by, fill_color="#8b4513", fill_alpha=0.9,
                   edge_color="#5a2a0a", edge_width=0.04)
        # Neck (arched)
        neck_x = np.linspace(cx + 1.5*s, cx + 2.0*s, 30)
        neck_y = np.linspace(cy + 3.5*s, cy + 5.0*s, 30)
        canvas.line(neck_x, neck_y, color="#8b4513", linewidth=0.12, alpha=0.9)
        # Head
        hx, hy = _oval(cx + 2.0*s, cy + 5.2*s, 0.5*s, 0.35*s)
        canvas.add(hx, hy, fill_color="#8b4513", fill_alpha=0.95,
                   edge_color="#5a2a0a", edge_width=0.03)
        # Eye
        canvas.circle(cx + 2.2*s, cy + 5.3*s, 0.04*s, fill=True,
                      fill_color="#1a0a05", fill_alpha=0.9)
        # Nostril
        canvas.circle(cx + 2.4*s, cy + 5.1*s, 0.03*s, fill=True,
                      fill_color="#3a1a0a", fill_alpha=0.8)
        # Mane (flowing)
        for i in range(12):
            t = np.linspace(0, 1, 20)
            mane_x = cx + 1.7*s + 0.3*s*t - 0.5*s*np.sin(2*np.pi*i/12)*t
            mane_y = cy + 5.0*s - 1.5*s*t
            canvas.line(mane_x, mane_y, color="#5a2a0a", linewidth=0.025, alpha=0.6)
        # Legs (galloping - front extended, back tucked)
        canvas.line(cx - 1.0*s, cy + 2.0*s, cx - 1.8*s, cy + 0.5*s,
                    color="#8b4513", linewidth=0.07)
        canvas.line(cx - 1.8*s, cy + 0.5*s, cx - 2.0*s, cy,
                    color="#8b4513", linewidth=0.05)
        canvas.line(cx - 0.2*s, cy + 2.0*s, cx + 0.5*s, cy + 0.5*s,
                    color="#8b4513", linewidth=0.07)
        canvas.line(cx + 0.5*s, cy + 0.5*s, cx + 0.3*s, cy,
                    color="#8b4513", linewidth=0.05)
        canvas.line(cx + 1.0*s, cy + 2.0*s, cx + 1.5*s, cy + 0.3*s,
                    color="#8b4513", linewidth=0.07)
        canvas.line(cx + 1.5*s, cy + 0.3*s, cx + 1.3*s, cy,
                    color="#8b4513", linewidth=0.05)
        canvas.line(cx + 1.8*s, cy + 2.0*s, cx + 1.0*s, cy + 0.8*s,
                    color="#8b4513", linewidth=0.07)
        # Tail (flowing)
        t = np.linspace(0, 1, 40)
        tail_x = cx - 2.5*s - 1.0*s*t**2
        tail_y = cy + 3.0*s + 1.0*s*np.sin(3*np.pi*t)*t
        canvas.line(tail_x, tail_y, color="#5a2a0a", linewidth=0.04, alpha=0.7)

    @staticmethod
    def snake(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Snake: coiled body, raised head, forked tongue."""
        s = scale
        # Coiled body (S-curve)
        t = np.linspace(0, 4*np.pi, 200)
        r = 0.5*s + 0.3*s*t/(4*np.pi)
        snake_x = cx + r*np.cos(t)*0.8
        snake_y = cy + r*np.sin(t)*0.4 + t*0.15*s
        canvas.line(snake_x, snake_y, color="#2a6a1a", linewidth=0.08, alpha=0.9)
        # Pattern (darker spots)
        for i in range(0, len(snake_x), 15):
            canvas.circle(snake_x[i], snake_y[i], 0.04*s, fill=True,
                          fill_color="#1a4a0a", fill_alpha=0.5)
        # Raised head
        hx, hy = _oval(cx + 0.8*s, cy + 3.5*s, 0.3*s, 0.2*s)
        canvas.add(hx, hy, fill_color="#2a6a1a", fill_alpha=0.95,
                   edge_color="#1a4a0a", edge_width=0.02)
        # Eyes (slit pupils)
        canvas.circle(cx + 0.9*s, cy + 3.55*s, 0.03*s, fill=True,
                      fill_color="#ffd700", fill_alpha=0.9)
        canvas.line(cx + 0.88*s, cy + 3.55*s, cx + 0.92*s, cy + 3.55*s,
                    color="#1a0a05", linewidth=0.02)
        # Forked tongue
        canvas.line(cx + 1.1*s, cy + 3.5*s, cx + 1.4*s, cy + 3.4*s,
                    color="#ff2020", linewidth=0.02)
        canvas.line(cx + 1.4*s, cy + 3.4*s, cx + 1.5*s, cy + 3.3*s,
                    color="#ff2020", linewidth=0.015)
        canvas.line(cx + 1.4*s, cy + 3.4*s, cx + 1.5*s, cy + 3.5*s,
                    color="#ff2020", linewidth=0.015)

    @staticmethod
    def bear(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Bear: massive body, small ears, powerful paws."""
        s = scale
        # Massive body
        bx, by = _oval(cx, cy + 2.5*s, 2.5*s, 1.5*s)
        canvas.add(bx, by, fill_color="#5a3a1a", fill_alpha=0.95,
                   edge_color="#3a2a0a", edge_width=0.04)
        # Head
        hx, hy = _oval(cx + 2.0*s, cy + 3.5*s, 0.7*s, 0.6*s)
        canvas.add(hx, hy, fill_color="#5a3a1a", fill_alpha=0.95,
                   edge_color="#3a2a0a", edge_width=0.03)
        # Small round ears
        canvas.circle(cx + 1.7*s, cy + 4.1*s, 0.15*s, fill=True,
                      fill_color="#5a3a1a", fill_alpha=0.9)
        canvas.circle(cx + 2.3*s, cy + 4.1*s, 0.15*s, fill=True,
                      fill_color="#5a3a1a", fill_alpha=0.9)
        # Snout
        snout_x, snout_y = _oval(cx + 2.4*s, cy + 3.4*s, 0.25*s, 0.2*s)
        canvas.add(snout_x, snout_y, fill_color="#8b6a3a", fill_alpha=0.9,
                   edge_color="#3a2a0a", edge_width=0.02)
        # Nose
        canvas.circle(cx + 2.6*s, cy + 3.45*s, 0.05*s, fill=True,
                      fill_color="#1a0a05", fill_alpha=0.9)
        # Eyes
        canvas.circle(cx + 2.1*s, cy + 3.6*s, 0.04*s, fill=True,
                      fill_color="#1a0a05", fill_alpha=0.9)
        # Powerful paws
        for px, py in [(cx - 1.5*s, cy + 1.0*s), (cx - 0.5*s, cy + 1.0*s),
                        (cx + 0.5*s, cy + 1.0*s), (cx + 1.5*s, cy + 1.0*s)]:
            canvas.line(px, py, px, cy, color="#5a3a1a", linewidth=0.1)
            paw_x, paw_y = _oval(px, cy, 0.2*s, 0.12*s)
            canvas.add(paw_x, paw_y, fill_color="#5a3a1a", fill_alpha=0.9,
                       edge_color="#3a2a0a", edge_width=0.02)
            # Claws
            for j in range(3):
                canvas.line(px + (j-1)*0.08*s, cy - 0.1*s,
                            px + (j-1)*0.08*s, cy - 0.2*s,
                            color="#1a0a05", linewidth=0.015)
        # Short tail
        canvas.circle(cx - 2.3*s, cy + 2.5*s, 0.12*s, fill=True,
                      fill_color="#5a3a1a", fill_alpha=0.8)

    @staticmethod
    def dolphin(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Dolphin: sleek body, curved dorsal fin, jumping."""
        s = scale
        # Main body (curved)
        t = np.linspace(0, 1, 100)
        body_x = cx + 3.0*s*(t - 0.5)
        body_y = cy + 2.5*s + 0.8*s*np.sin(np.pi*t)
        body_upper = body_y + 0.5*s*np.sin(np.pi*t)
        body_lower = body_y - 0.4*s*np.sin(np.pi*t)
        canvas.line(body_x, body_upper, color="#4a6a8a", linewidth=0.08, alpha=0.9)
        canvas.line(body_x, body_lower, color="#4a6a8a", linewidth=0.08, alpha=0.9)
        # Fill body
        fill_x = np.concatenate([body_x, body_x[::-1]])
        fill_y = np.concatenate([body_upper, body_lower[::-1]])
        canvas.add(fill_x, fill_y, fill_color="#4a6a8a", fill_alpha=0.8,
                   edge_color="#2a4a6a", edge_width=0.03)
        # Dorsal fin
        fin_x = [cx - 0.2*s, cx + 0.1*s, cx + 0.3*s]
        fin_y = [cy + 3.3*s, cy + 4.0*s, cy + 3.3*s]
        canvas.line(fin_x, fin_y, color="#4a6a8a", linewidth=0.05)
        canvas.add(fin_x + [fin_x[0]], fin_y + [fin_y[0]],
                   fill_color="#4a6a8a", fill_alpha=0.7)
        # Tail fluke
        fluke_x = [cx - 1.5*s, cx - 2.0*s, cx - 1.8*s, cx - 1.5*s, cx - 1.2*s, cx - 1.0*s, cx - 1.5*s]
        fluke_y = [cy + 2.5*s, cy + 3.0*s, cy + 2.5*s, cy + 2.5*s, cy + 2.5*s, cy + 2.0*s, cy + 2.5*s]
        canvas.line(fluke_x, fluke_y, color="#4a6a8a", linewidth=0.04, alpha=0.8)
        # Snout
        canvas.line(cx + 1.5*s, cy + 2.7*s, cx + 2.2*s, cy + 2.8*s,
                    color="#4a6a8a", linewidth=0.05, alpha=0.9)
        # Eye
        canvas.circle(cx + 1.3*s, cy + 2.8*s, 0.04*s, fill=True,
                      fill_color="#1a0a05", fill_alpha=0.9)
        # Flipper
        flip_x = [cx + 0.5*s, cx + 0.2*s, cx + 0.8*s]
        flip_y = [cy + 2.3*s, cy + 1.8*s, cy + 2.0*s]
        canvas.line(flip_x, flip_y, color="#4a6a8a", linewidth=0.04, alpha=0.8)
        # Water splash
        for i in range(8):
            sx = cx - 1.5*s + i*0.3*s
            sy = cy + 1.5*s + 0.3*s*np.random.random()
            canvas.circle(sx, sy, 0.05*s, fill=True,
                          fill_color="#8ac0ff", fill_alpha=0.3)

    @staticmethod
    def owl(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Owl: round body, large eyes, ear tufts."""
        s = scale
        # Round body
        bx, by = _oval(cx, cy + 2.0*s, 1.2*s, 1.5*s)
        canvas.add(bx, by, fill_color="#8b7355", fill_alpha=0.95,
                   edge_color="#5a4a30", edge_width=0.04)
        # Head (large, round)
        hx, hy = _oval(cx, cy + 3.8*s, 0.9*s, 0.8*s)
        canvas.add(hx, hy, fill_color="#8b7355", fill_alpha=0.95,
                   edge_color="#5a4a30", edge_width=0.03)
        # Large eyes (discs)
        for ex in [cx - 0.35*s, cx + 0.35*s]:
            eye_disc_x, eye_disc_y = _oval(ex, cy + 3.9*s, 0.25*s, 0.25*s)
            canvas.add(eye_disc_x, eye_disc_y, fill_color="#f0e0c0", fill_alpha=0.9,
                       edge_color="#5a4a30", edge_width=0.02)
            canvas.circle(ex, cy + 3.9*s, 0.1*s, fill=True,
                          fill_color="#1a0a05", fill_alpha=0.95)
            canvas.circle(ex + 0.03*s, cy + 3.95*s, 0.03*s, fill=True,
                          fill_color="#ffffff", fill_alpha=0.5)
        # Ear tufts
        tuft_l = [cx - 0.6*s, cx - 0.8*s, cx - 0.5*s]
        tuft_ly = [cy + 4.5*s, cy + 5.0*s, cy + 4.5*s]
        canvas.line(tuft_l, tuft_ly, color="#8b7355", linewidth=0.04)
        tuft_r = [cx + 0.6*s, cx + 0.8*s, cx + 0.5*s]
        tuft_ry = [cy + 4.5*s, cy + 5.0*s, cy + 4.5*s]
        canvas.line(tuft_r, tuft_ry, color="#8b7355", linewidth=0.04)
        # Beak
        beak_x = [cx, cx - 0.08*s, cx, cx + 0.08*s, cx]
        beak_y = [cy + 3.6*s, cy + 3.5*s, cy + 3.4*s, cy + 3.5*s, cy + 3.6*s]
        canvas.line(beak_x, beak_y, color="#ffd700", linewidth=0.03)
        # Feather pattern (chest)
        for i in range(6):
            for j in range(4):
                fx = cx - 0.4*s + i*0.16*s
                fy = cy + 1.5*s + j*0.3*s
                canvas.line(fx - 0.05*s, fy, fx + 0.05*s, fy - 0.1*s,
                            color="#5a4a30", linewidth=0.015, alpha=0.5)
        # Wings (folded)
        canvas.line(cx - 1.2*s, cy + 3.0*s, cx - 1.3*s, cy + 1.0*s,
                    color="#8b7355", linewidth=0.06, alpha=0.8)
        canvas.line(cx + 1.2*s, cy + 3.0*s, cx + 1.3*s, cy + 1.0*s,
                    color="#8b7355", linewidth=0.06, alpha=0.8)
        # Talons
        for tx in [cx - 0.3*s, cx + 0.3*s]:
            canvas.line(tx, cy + 0.5*s, tx, cy + 0.3*s, color="#ffd700", linewidth=0.03)
            for j in range(3):
                canvas.line(tx, cy + 0.3*s,
                            tx + (j-1)*0.06*s, cy + 0.1*s,
                            color="#ffd700", linewidth=0.02)

    @staticmethod
    def dragon(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Dragon: mythical beast with wings, fire."""
        s = scale
        # Body (serpentine)
        t = np.linspace(0, 1, 80)
        body_x = cx + 2.0*s*(t - 0.5)
        body_y = cy + 2.5*s + 0.6*s*np.sin(4*np.pi*t)
        canvas.line(body_x, body_y, color="#8b2020", linewidth=0.1, alpha=0.9)
        # Scales pattern
        for i in range(0, 80, 5):
            canvas.circle(body_x[i], body_y[i], 0.04*s, fill=True,
                          fill_color="#6a1010", fill_alpha=0.5)
        # Head
        hx, hy = _oval(cx + 2.0*s, cy + 2.8*s, 0.5*s, 0.35*s)
        canvas.add(hx, hy, fill_color="#8b2020", fill_alpha=0.95,
                   edge_color="#5a1010", edge_width=0.03)
        # Horns
        canvas.line(cx + 1.8*s, cy + 3.1*s, cx + 1.6*s, cy + 3.6*s,
                    color="#5a1010", linewidth=0.03)
        canvas.line(cx + 2.2*s, cy + 3.1*s, cx + 2.4*s, cy + 3.6*s,
                    color="#5a1010", linewidth=0.03)
        # Eye
        canvas.circle(cx + 2.2*s, cy + 2.9*s, 0.04*s, fill=True,
                      fill_color="#ffd700", fill_alpha=0.9)
        canvas.circle(cx + 2.2*s, cy + 2.9*s, 0.02*s, fill=True,
                      fill_color="#ff2020", fill_alpha=0.9)
        # Fire breath
        for i in range(12):
            fx = cx + 2.5*s + i*0.15*s
            fy = cy + 2.8*s + 0.3*s*np.sin(2*np.pi*i/5)*np.exp(-i*0.15)
            fr = 0.08*s*(1 - i*0.08)
            canvas.circle(fx, fy, fr, fill=True,
                          fill_color="#ff6020" if i < 6 else "#ffd700",
                          fill_alpha=0.7 - i*0.05)
        # Wings (bat-like)
        wing_pts_x = [cx + 0.5*s, cx - 1.5*s, cx - 2.0*s, cx - 1.0*s, cx + 0.5*s]
        wing_pts_y = [cy + 3.0*s, cy + 4.5*s, cy + 4.0*s, cy + 3.5*s, cy + 3.0*s]
        canvas.line(wing_pts_x, wing_pts_y, color="#8b2020", linewidth=0.05, alpha=0.8)
        canvas.add(wing_pts_x + [wing_pts_x[0]], wing_pts_y + [wing_pts_y[0]],
                   fill_color="#8b2020", fill_alpha=0.3)
        # Spines along back
        for i in range(15):
            sx = cx - 1.5*s + i*0.25*s
            sy = cy + 2.5*s + 0.6*s*np.sin(4*np.pi*(sx - cx + 1.0*s)/(4.0*s))
            canvas.line(sx, sy, sx, sy + 0.2*s, color="#5a1010", linewidth=0.02)
        # Tail (with spike)
        t = np.linspace(0, 1, 30)
        tail_x = cx - 2.0*s - 1.0*s*t
        tail_y = cy + 2.5*s + 0.5*s*np.sin(3*np.pi*t)*t
        canvas.line(tail_x, tail_y, color="#8b2020", linewidth=0.04, alpha=0.8)
        # Tail spike
        canvas.line(cx - 3.0*s, cy + 2.5*s, cx - 3.2*s, cy + 2.8*s,
                    color="#5a1010", linewidth=0.03)
        canvas.line(cx - 3.0*s, cy + 2.5*s, cx - 3.3*s, cy + 2.3*s,
                    color="#5a1010", linewidth=0.03)


# ============================================================
#  DEMO
# ============================================================

if __name__ == "__main__":
    print("[START] Generating animal templates showcase...")

    animals = [
        ("Lion", AnimalTemplates.lion),
        ("Eagle", AnimalTemplates.eagle),
        ("Wolf", AnimalTemplates.wolf),
        ("Horse", AnimalTemplates.horse),
        ("Snake", AnimalTemplates.snake),
        ("Bear", AnimalTemplates.bear),
        ("Dolphin", AnimalTemplates.dolphin),
        ("Owl", AnimalTemplates.owl),
        ("Dragon", AnimalTemplates.dragon),
    ]

    fig, axes = plt.subplots(3, 3, figsize=(18, 18), dpi=150)
    fig.patch.set_facecolor("#0d0a1a")
    fig.suptitle("POLYART: Animal Templates - Polynomial Bodies",
                 fontsize=16, color="#c8a040", fontweight="bold", fontfamily="serif")

    class MockCanvas:
        def __init__(self, ax):
            self.ax = ax
        def add(self, x, y, **kw):
            if "fill_color" in kw:
                self.ax.fill(x, y, color=kw["fill_color"], alpha=kw.get("fill_alpha", 1))
        def line(self, *args, **kw):
            if len(args) == 2:
                self.ax.plot(args[0], args[1], color=kw.get("color", "#c8a040"),
                             linewidth=kw.get("linewidth", 1)*10, alpha=kw.get("alpha", 1))
            elif len(args) == 4:
                self.ax.plot([args[0], args[2]], [args[1], args[3]], color=kw.get("color", "#c8a040"),
                             linewidth=kw.get("linewidth", 1)*10, alpha=kw.get("alpha", 1))
        def circle(self, x, y, r, **kw):
            if kw.get("fill"):
                circ = plt.Circle((x, y), r, color=kw.get("fill_color", "#c8a040"),
                                  alpha=kw.get("fill_alpha", 1))
                self.ax.add_patch(circ)

    axes_flat = axes.flatten()

    for idx, (name, func) in enumerate(animals):
        ax = axes_flat[idx]
        ax.set_xlim(-4, 4)
        ax.set_ylim(-1, 6)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor("#0d0a1a")
        ax.set_title(name, fontsize=14, color="#c8a040", fontfamily="serif")
        mc = MockCanvas(ax)
        func(mc, cx=0, cy=2, scale=0.8)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out = r"C:\Users\e\Desktop\6756756756756756\animals_showcase.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0d0a1a")
    plt.close(fig)
    print(f"[OK] Saved: {out}")
    print("[DONE] All animal templates complete.")
