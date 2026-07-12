import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import warnings
warnings.filterwarnings("ignore")


# ============================================================
#  POLYART HUMAN EMOTIONS, FEELINGS & STATES
#  Polynomial body templates for every human condition
# ============================================================


class EmotionTemplates:
    """Templates for human emotions expressed through body language."""

    @staticmethod
    def joy(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Joy: raised arms, wide smile, open posture."""
        s = scale
        # Head (slightly tilted back)
        hx, hy = _oval(cx, cy + 5.5*s, 0.8*s, 1.0*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=1.0,
                   edge_color="#c8a040", edge_width=0.04)
        # Wide smile
        smile_x = np.linspace(cx - 0.4*s, cx + 0.4*s, 30)
        smile_y = cy + 5.1*s + 0.15*s*np.sin(np.pi*(smile_x - cx)/(0.8*s))
        canvas.line(smile_x, smile_y, color="#8b4020", linewidth=0.04)
        # Eyes (bright, open)
        for ex in [cx - 0.25*s, cx + 0.25*s]:
            canvas.circle(ex, cy + 5.7*s, 0.08*s, fill=True,
                          fill_color="#2a1a0a", fill_alpha=0.9)
            canvas.circle(ex + 0.02*s, cy + 5.75*s, 0.03*s, fill=True,
                          fill_color="#ffffff", fill_alpha=0.5)
        # Raised arms (V shape)
        canvas.line(cx - 0.5*s, cy + 4.5*s, cx - 2.0*s, cy + 7.0*s,
                    color="#d4a574", linewidth=0.08, alpha=0.9)
        canvas.line(cx + 0.5*s, cy + 4.5*s, cx + 2.0*s, cy + 7.0*s,
                    color="#d4a574", linewidth=0.08, alpha=0.9)
        # Open hands
        for hx, hy in [(cx - 2.0*s, cy + 7.0*s), (cx + 2.0*s, cy + 7.0*s)]:
            for finger in range(5):
                ang = np.pi/2 + (finger - 2)*0.2
                canvas.line(hx, hy, hx + 0.3*s*np.cos(ang), hy + 0.3*s*np.sin(ang),
                            color="#d4a574", linewidth=0.03)
        # Torso (upright, confident)
        canvas.line(cx, cy + 4.5*s, cx, cy + 2.0*s,
                    color="#d4a574", linewidth=0.15, alpha=0.9)
        # Legs (slightly apart, stable)
        canvas.line(cx, cy + 2.0*s, cx - 0.5*s, cy,
                    color="#d4a574", linewidth=0.1)
        canvas.line(cx, cy + 2.0*s, cx + 0.5*s, cy,
                    color="#d4a574", linewidth=0.1)

    @staticmethod
    def sorrow(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Sorrow: slumped posture, hanging head, tears."""
        s = scale
        # Head (hanging down)
        hx, hy = _oval(cx, cy + 4.5*s, 0.8*s, 1.0*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=0.9,
                   edge_color="#c8a040", edge_width=0.04)
        # Downturned mouth
        sad_x = np.linspace(cx - 0.3*s, cx + 0.3*s, 30)
        sad_y = cy + 4.1*s - 0.1*s*np.sin(np.pi*(sad_x - cx)/(0.6*s))
        canvas.line(sad_x, sad_y, color="#8b4020", linewidth=0.04)
        # Closed/downcast eyes
        for ex in [cx - 0.25*s, cx + 0.25*s]:
            canvas.line(ex - 0.1*s, cy + 4.7*s, ex + 0.1*s, cy + 4.7*s,
                        color="#5a3a20", linewidth=0.03)
        # Tears
        canvas.circle(cx - 0.15*s, cy + 4.5*s, 0.03*s, fill=True,
                      fill_color="#4a90d9", fill_alpha=0.6)
        canvas.circle(cx + 0.35*s, cy + 4.55*s, 0.03*s, fill=True,
                      fill_color="#4a90d9", fill_alpha=0.6)
        # Slumped torso (curved spine)
        t = np.linspace(0, 1, 40)
        spine_x = cx + 0.3*s*t**2
        spine_y = cy + 4.5*s - 2.5*s*t
        canvas.line(spine_x, spine_y, color="#d4a574", linewidth=0.12, alpha=0.85)
        # Arms hanging down
        canvas.line(cx - 0.3*s, cy + 4.0*s, cx - 0.6*s, cy + 1.5*s,
                    color="#d4a574", linewidth=0.06, alpha=0.8)
        canvas.line(cx + 0.3*s, cy + 4.0*s, cx + 0.5*s, cy + 1.5*s,
                    color="#d4a574", linewidth=0.06, alpha=0.8)
        # Legs
        canvas.line(cx + 0.3*s, cy + 2.0*s, cx - 0.1*s, cy,
                    color="#d4a574", linewidth=0.08)
        canvas.line(cx + 0.3*s, cy + 2.0*s, cx + 0.7*s, cy,
                    color="#d4a574", linewidth=0.08)

    @staticmethod
    def anger(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Anger: tense posture, clenched fists, furrowed brow."""
        s = scale
        # Head (forward, aggressive)
        hx, hy = _oval(cx + 0.2*s, cy + 5.5*s, 0.8*s, 1.0*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=1.0,
                   edge_color="#c8a040", edge_width=0.04)
        # Furrowed brow
        canvas.line(cx - 0.3*s, cy + 5.9*s, cx + 0.0*s, cy + 5.7*s,
                    color="#5a3a20", linewidth=0.04)
        canvas.line(cx + 0.7*s, cy + 5.9*s, cx + 0.4*s, cy + 5.7*s,
                    color="#5a3a20", linewidth=0.04)
        # Angry eyes
        for ex in [cx - 0.1*s, cx + 0.5*s]:
            canvas.circle(ex, cy + 5.6*s, 0.07*s, fill=True,
                          fill_color="#1a0a05", fill_alpha=0.95)
        # Gritted teeth
        teeth_x = np.linspace(cx - 0.2*s, cx + 0.6*s, 20)
        canvas.line(teeth_x, cy + 5.1*s, teeth_x + 0.01, cy + 5.1*s,
                    color="#ffffff", linewidth=0.03, alpha=0.8)
        # Clenched fists (forward)
        canvas.line(cx - 0.3*s, cy + 4.5*s, cx - 1.0*s, cy + 3.5*s,
                    color="#d4a574", linewidth=0.08)
        canvas.circle(cx - 1.0*s, cy + 3.5*s, 0.15*s, fill=True,
                      fill_color="#d4a574", fill_alpha=0.9)
        canvas.line(cx + 0.7*s, cy + 4.5*s, cx + 1.2*s, cy + 3.5*s,
                    color="#d4a574", linewidth=0.08)
        canvas.circle(cx + 1.2*s, cy + 3.5*s, 0.15*s, fill=True,
                      fill_color="#d4a574", fill_alpha=0.9)
        # Tense torso
        canvas.line(cx + 0.2*s, cy + 4.5*s, cx + 0.2*s, cy + 2.0*s,
                    color="#d4a574", linewidth=0.15, alpha=0.9)
        # Wide stance
        canvas.line(cx + 0.2*s, cy + 2.0*s, cx - 0.7*s, cy,
                    color="#d4a574", linewidth=0.1)
        canvas.line(cx + 0.2*s, cy + 2.0*s, cx + 1.1*s, cy,
                    color="#d4a574", linewidth=0.1)

    @staticmethod
    def fear(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Fear: recoiling, hands up defensively, wide eyes."""
        s = scale
        # Head (pulled back)
        hx, hy = _oval(cx - 0.3*s, cy + 5.5*s, 0.8*s, 1.0*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=0.95,
                   edge_color="#c8a040", edge_width=0.04)
        # Wide frightened eyes
        for ex in [cx - 0.5*s, cx - 0.1*s]:
            eye_x, eye_y = _oval(ex, cy + 5.7*s, 0.12*s, 0.1*s)
            canvas.add(eye_x, eye_y, fill_color="#ffffff", fill_alpha=0.9,
                       edge_color="#5a3a20", edge_width=0.02)
            canvas.circle(ex, cy + 5.7*s, 0.04*s, fill=True,
                          fill_color="#1a0a05", fill_alpha=0.95)
        # Open mouth (scream)
        mouth_x, mouth_y = _oval(cx - 0.3*s, cy + 5.1*s, 0.15*s, 0.1*s)
        canvas.add(mouth_x, mouth_y, fill_color="#3a1010", fill_alpha=0.9,
                   edge_color="#8b4020", edge_width=0.02)
        # Defensive hands (in front of face)
        canvas.line(cx - 0.3*s, cy + 4.5*s, cx - 1.2*s, cy + 5.5*s,
                    color="#d4a574", linewidth=0.07)
        canvas.circle(cx - 1.2*s, cy + 5.5*s, 0.12*s, fill=True,
                      fill_color="#d4a574", fill_alpha=0.85)
        canvas.line(cx + 0.3*s, cy + 4.5*s, cx + 0.8*s, cy + 5.5*s,
                    color="#d4a574", linewidth=0.07)
        canvas.circle(cx + 0.8*s, cy + 5.5*s, 0.12*s, fill=True,
                      fill_color="#d4a574", fill_alpha=0.85)
        # Recoiling torso (leaning back)
        t = np.linspace(0, 1, 40)
        spine_x = cx - 0.3*s - 0.5*s*t**2
        spine_y = cy + 4.5*s - 2.5*s*t
        canvas.line(spine_x, spine_y, color="#d4a574", linewidth=0.12, alpha=0.85)
        # Legs (ready to flee)
        canvas.line(cx - 0.3*s, cy + 2.0*s, cx - 0.8*s, cy,
                    color="#d4a574", linewidth=0.08)
        canvas.line(cx - 0.3*s, cy + 2.0*s, cx + 0.3*s, cy,
                    color="#d4a574", linewidth=0.08)

    @staticmethod
    def love(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Love: gentle lean, hands on heart, soft expression."""
        s = scale
        # Head (slightly tilted)
        hx, hy = _oval(cx + 0.1*s, cy + 5.5*s, 0.8*s, 1.0*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=1.0,
                   edge_color="#c8a040", edge_width=0.04)
        # Gentle smile
        smile_x = np.linspace(cx - 0.2*s, cx + 0.4*s, 30)
        smile_y = cy + 5.1*s + 0.1*s*np.sin(np.pi*(smile_x - cx)/(0.6*s))
        canvas.line(smile_x, smile_y, color="#a06040", linewidth=0.03)
        # Soft eyes (half-closed)
        for ex in [cx - 0.15*s, cx + 0.35*s]:
            canvas.line(ex - 0.08*s, cy + 5.65*s, ex + 0.08*s, cy + 5.65*s,
                        color="#5a3a20", linewidth=0.03, alpha=0.7)
        # Hand on heart
        canvas.line(cx + 0.3*s, cy + 4.5*s, cx + 0.2*s, cy + 3.8*s,
                    color="#d4a574", linewidth=0.07)
        canvas.circle(cx + 0.2*s, cy + 3.8*s, 0.12*s, fill=True,
                      fill_color="#d4a574", fill_alpha=0.9)
        # Heart symbol
        heart_x = [cx + 0.2*s, cx + 0.05*s, cx - 0.1*s, cx + 0.05*s, cx + 0.2*s, cx + 0.35*s, cx + 0.5*s, cx + 0.35*s, cx + 0.2*s]
        heart_y = [cy + 3.5*s, cy + 3.7*s, cy + 3.5*s, cy + 3.3*s, cy + 3.1*s, cy + 3.3*s, cy + 3.5*s, cy + 3.7*s, cy + 3.5*s]
        canvas.line(heart_x, heart_y, color="#ff4060", linewidth=0.04, alpha=0.7)
        # Other arm (gentle gesture)
        canvas.line(cx - 0.3*s, cy + 4.5*s, cx - 1.0*s, cy + 3.5*s,
                    color="#d4a574", linewidth=0.06, alpha=0.8)
        # Torso
        canvas.line(cx, cy + 4.5*s, cx, cy + 2.0*s,
                    color="#d4a574", linewidth=0.12, alpha=0.85)
        # Legs
        canvas.line(cx, cy + 2.0*s, cx - 0.3*s, cy,
                    color="#d4a574", linewidth=0.08)
        canvas.line(cx, cy + 2.0*s, cx + 0.3*s, cy,
                    color="#d4a574", linewidth=0.08)

    @staticmethod
    def surprise(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Surprise: jump, hands up, wide eyes, open mouth."""
        s = scale
        # Head (slightly up)
        hx, hy = _oval(cx, cy + 6.0*s, 0.8*s, 1.0*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=1.0,
                   edge_color="#c8a040", edge_width=0.04)
        # Very wide eyes
        for ex in [cx - 0.25*s, cx + 0.25*s]:
            eye_x, eye_y = _oval(ex, cy + 6.2*s, 0.12*s, 0.1*s)
            canvas.add(eye_x, eye_y, fill_color="#ffffff", fill_alpha=0.95,
                       edge_color="#5a3a20", edge_width=0.02)
            canvas.circle(ex, cy + 6.2*s, 0.05*s, fill=True,
                          fill_color="#1a0a05", fill_alpha=0.95)
        # Open mouth (O shape)
        mouth_x, mouth_y = _oval(cx, cy + 5.7*s, 0.12*s, 0.15*s)
        canvas.add(mouth_x, mouth_y, fill_color="#3a1010", fill_alpha=0.9,
                   edge_color="#8b4020", edge_width=0.02)
        # Hands shooting up
        canvas.line(cx - 0.5*s, cy + 4.5*s, cx - 1.5*s, cy + 7.0*s,
                    color="#d4a574", linewidth=0.07)
        canvas.circle(cx - 1.5*s, cy + 7.0*s, 0.1*s, fill=True,
                      fill_color="#d4a574", fill_alpha=0.85)
        canvas.line(cx + 0.5*s, cy + 4.5*s, cx + 1.5*s, cy + 7.0*s,
                    color="#d4a574", linewidth=0.07)
        canvas.circle(cx + 1.5*s, cy + 7.0*s, 0.1*s, fill=True,
                      fill_color="#d4a574", fill_alpha=0.85)
        # Torso (jumping, slightly off ground)
        canvas.line(cx, cy + 5.0*s, cx, cy + 2.5*s,
                    color="#d4a574", linewidth=0.12, alpha=0.85)
        # Legs (tucked)
        canvas.line(cx, cy + 2.5*s, cx - 0.5*s, cy + 1.5*s,
                    color="#d4a574", linewidth=0.08)
        canvas.line(cx - 0.5*s, cy + 1.5*s, cx - 0.3*s, cy + 0.5*s,
                    color="#d4a574", linewidth=0.07)
        canvas.line(cx, cy + 2.5*s, cx + 0.5*s, cy + 1.5*s,
                    color="#d4a574", linewidth=0.08)
        canvas.line(cx + 0.5*s, cy + 1.5*s, cx + 0.3*s, cy + 0.5*s,
                    color="#d4a574", linewidth=0.07)

    @staticmethod
    def calm(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Calm: seated meditation, crossed legs, peaceful face."""
        s = scale
        # Head (straight, centered)
        hx, hy = _oval(cx, cy + 5.0*s, 0.8*s, 1.0*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=1.0,
                   edge_color="#c8a040", edge_width=0.04)
        # Closed eyes (peaceful)
        for ex in [cx - 0.25*s, cx + 0.25*s]:
            canvas.line(ex - 0.08*s, cy + 5.2*s, ex + 0.08*s, cy + 5.2*s,
                        color="#5a3a20", linewidth=0.03)
        # Gentle smile
        smile_x = np.linspace(cx - 0.15*s, cx + 0.15*s, 20)
        smile_y = cy + 4.8*s + 0.05*s*np.sin(np.pi*(smile_x - cx)/(0.3*s))
        canvas.line(smile_x, smile_y, color="#a06040", linewidth=0.025)
        # Hands on knees (mudra)
        canvas.line(cx - 0.3*s, cy + 4.2*s, cx - 1.0*s, cy + 2.5*s,
                    color="#d4a574", linewidth=0.06)
        canvas.line(cx + 0.3*s, cy + 4.2*s, cx + 1.0*s, cy + 2.5*s,
                    color="#d4a574", linewidth=0.06)
        # Mudra fingers
        for side in [-1, 1]:
            mx = cx + side*1.0*s
            my = cy + 2.5*s
            canvas.circle(mx, my, 0.06*s, fill=True,
                          fill_color="#d4a574", fill_alpha=0.8)
        # Torso (straight, upright)
        canvas.line(cx, cy + 4.2*s, cx, cy + 2.5*s,
                    color="#d4a574", linewidth=0.12, alpha=0.85)
        # Crossed legs
        canvas.line(cx, cy + 2.5*s, cx - 0.8*s, cy + 1.8*s,
                    color="#d4a574", linewidth=0.08)
        canvas.line(cx - 0.8*s, cy + 1.8*s, cx + 0.3*s, cy + 1.5*s,
                    color="#d4a574", linewidth=0.07)
        canvas.line(cx, cy + 2.5*s, cx + 0.8*s, cy + 1.8*s,
                    color="#d4a574", linewidth=0.08)
        canvas.line(cx + 0.8*s, cy + 1.8*s, cx - 0.3*s, cy + 1.5*s,
                    color="#d4a574", linewidth=0.07)

    @staticmethod
    def pride(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Pride: chest out, chin up, hands on hips."""
        s = scale
        # Head (chin up)
        hx, hy = _oval(cx, cy + 5.8*s, 0.8*s, 1.0*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=1.0,
                   edge_color="#c8a040", edge_width=0.04)
        # Confident smirk
        smirk_x = np.linspace(cx - 0.1*s, cx + 0.3*s, 20)
        smirk_y = cy + 5.4*s + 0.08*s*(smirk_x - cx + 0.1*s)/(0.4*s)
        canvas.line(smirk_x, smirk_y, color="#8b4020", linewidth=0.03)
        # Eyes (looking slightly up)
        for ex in [cx - 0.2*s, cx + 0.2*s]:
            canvas.circle(ex, cy + 5.9*s, 0.06*s, fill=True,
                          fill_color="#2a1a0a", fill_alpha=0.9)
        # Chest out (wide torso)
        chest_x = [cx - 0.8*s, cx - 0.3*s, cx + 0.3*s, cx + 0.8*s,
                   cx + 0.3*s, cx - 0.3*s, cx - 0.8*s]
        chest_y = [cy + 4.5*s, cy + 4.2*s, cy + 4.2*s, cy + 4.5*s,
                   cy + 3.5*s, cy + 3.5*s, cy + 4.5*s]
        canvas.line(chest_x, chest_y, color="#d4a574", linewidth=0.1, alpha=0.85)
        # Hands on hips
        canvas.line(cx - 0.8*s, cy + 4.5*s, cx - 1.2*s, cy + 3.0*s,
                    color="#d4a574", linewidth=0.07)
        canvas.line(cx - 1.2*s, cy + 3.0*s, cx - 0.8*s, cy + 2.8*s,
                    color="#d4a574", linewidth=0.06)
        canvas.line(cx + 0.8*s, cy + 4.5*s, cx + 1.2*s, cy + 3.0*s,
                    color="#d4a574", linewidth=0.07)
        canvas.line(cx + 1.2*s, cy + 3.0*s, cx + 0.8*s, cy + 2.8*s,
                    color="#d4a574", linewidth=0.06)
        # Torso
        canvas.line(cx, cy + 4.2*s, cx, cy + 2.0*s,
                    color="#d4a574", linewidth=0.12, alpha=0.85)
        # Legs (wide, powerful stance)
        canvas.line(cx, cy + 2.0*s, cx - 0.8*s, cy,
                    color="#d4a574", linewidth=0.1)
        canvas.line(cx, cy + 2.0*s, cx + 0.8*s, cy,
                    color="#d4a574", linewidth=0.1)

    @staticmethod
    def exhaustion(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Exhaustion: collapsed, head down, limbs limp."""
        s = scale
        # Head (drooping)
        hx, hy = _oval(cx + 0.5*s, cy + 4.0*s, 0.8*s, 1.0*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=0.85,
                   edge_color="#c8a040", edge_width=0.03)
        # Closed eyes, mouth slightly open
        for ex in [cx + 0.3*s, cx + 0.7*s]:
            canvas.line(ex - 0.06*s, cy + 4.2*s, ex + 0.06*s, cy + 4.2*s,
                        color="#5a3a20", linewidth=0.025)
        canvas.line(cx + 0.3*s, cy + 3.7*s, cx + 0.7*s, cy + 3.7*s,
                    color="#8b4020", linewidth=0.02, alpha=0.6)
        # Collapsed torso (crumpled)
        t = np.linspace(0, 1, 50)
        spine_x = cx + 0.5*s*t**3
        spine_y = cy + 4.0*s - 2.0*s*t
        canvas.line(spine_x, spine_y, color="#d4a574", linewidth=0.1, alpha=0.7)
        # Limp arms
        canvas.line(cx + 0.3*s, cy + 3.5*s, cx - 0.5*s, cy + 1.5*s,
                    color="#d4a574", linewidth=0.05, alpha=0.6)
        canvas.line(cx + 0.7*s, cy + 3.5*s, cx + 1.2*s, cy + 1.0*s,
                    color="#d4a574", linewidth=0.05, alpha=0.6)
        # Legs (buckled)
        canvas.line(cx + 0.5*s, cy + 2.0*s, cx - 0.2*s, cy + 0.8*s,
                    color="#d4a574", linewidth=0.07, alpha=0.7)
        canvas.line(cx + 0.5*s, cy + 2.0*s, cx + 1.0*s, cy + 0.5*s,
                    color="#d4a574", linewidth=0.07, alpha=0.7)

    @staticmethod
    def determination(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Determination: forward lean, clenched fist, focused gaze."""
        s = scale
        # Head (forward, focused)
        hx, hy = _oval(cx + 0.3*s, cy + 5.5*s, 0.8*s, 1.0*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=1.0,
                   edge_color="#c8a040", edge_width=0.04)
        # Focused eyes (narrowed)
        for ex in [cx + 0.1*s, cx + 0.5*s]:
            canvas.line(ex - 0.08*s, cy + 5.7*s, ex + 0.08*s, cy + 5.7*s,
                        color="#4a2a10", linewidth=0.04)
            canvas.circle(ex, cy + 5.65*s, 0.05*s, fill=True,
                          fill_color="#1a0a05", fill_alpha=0.95)
        # Set jaw
        canvas.line(cx + 0.0*s, cy + 5.1*s, cx + 0.6*s, cy + 5.1*s,
                    color="#8b4020", linewidth=0.03, alpha=0.7)
        # Forward-leaning torso
        t = np.linspace(0, 1, 40)
        spine_x = cx + 0.3*s + 0.5*s*t**2
        spine_y = cy + 5.0*s - 2.5*s*t
        canvas.line(spine_x, spine_y, color="#d4a574", linewidth=0.12, alpha=0.9)
        # One fist forward
        canvas.line(cx + 0.5*s, cy + 4.5*s, cx + 1.5*s, cy + 3.5*s,
                    color="#d4a574", linewidth=0.08)
        canvas.circle(cx + 1.5*s, cy + 3.5*s, 0.15*s, fill=True,
                      fill_color="#d4a574", fill_alpha=0.9)
        # Other arm back
        canvas.line(cx + 0.1*s, cy + 4.5*s, cx - 0.8*s, cy + 3.0*s,
                    color="#d4a574", linewidth=0.07)
        # Legs (wide, pushing forward)
        canvas.line(cx + 0.5*s, cy + 2.0*s, cx - 0.3*s, cy,
                    color="#d4a574", linewidth=0.1)
        canvas.line(cx + 0.5*s, cy + 2.0*s, cx + 1.3*s, cy,
                    color="#d4a574", linewidth=0.1)


class StateTemplates:
    """Templates for human physical/mental states."""

    @staticmethod
    def sleeping(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Sleeping: lying down, relaxed limbs."""
        s = scale
        # Head (on pillow)
        hx, hy = _oval(cx - 2.0*s, cy + 1.0*s, 0.8*s, 0.7*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=0.9,
                   edge_color="#c8a040", edge_width=0.03)
        # Closed eyes
        canvas.line(cx - 2.2*s, cy + 1.1*s, cx - 1.8*s, cy + 1.1*s,
                    color="#5a3a20", linewidth=0.03)
        # Zzz
        for i, (zx, zy, zfs) in enumerate([
            (cx - 1.5*s, cy + 2.0*s, 0.06),
            (cx - 1.2*s, cy + 2.5*s, 0.08),
            (cx - 0.9*s, cy + 3.0*s, 0.10)
        ]):
            canvas.text(zx, zy, "z", fontsize=int(zfs*100), color="#c8a040", alpha=0.4)
        # Body (horizontal)
        canvas.line(cx - 2.0*s, cy + 0.5*s, cx + 2.0*s, cy + 0.5*s,
                    color="#d4a574", linewidth=0.12, alpha=0.85)
        # Arms (relaxed at sides)
        canvas.line(cx - 1.0*s, cy + 0.8*s, cx - 1.5*s, cy - 0.3*s,
                    color="#d4a574", linewidth=0.06, alpha=0.7)
        canvas.line(cx + 1.0*s, cy + 0.8*s, cx + 1.5*s, cy - 0.3*s,
                    color="#d4a574", linewidth=0.06, alpha=0.7)
        # Legs
        canvas.line(cx + 2.0*s, cy + 0.5*s, cx + 2.8*s, cy + 0.3*s,
                    color="#d4a574", linewidth=0.08)
        canvas.line(cx + 2.0*s, cy + 0.5*s, cx + 2.6*s, cy - 0.2*s,
                    color="#d4a574", linewidth=0.08)

    @staticmethod
    def running(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Running: dynamic stride, arms pumping."""
        s = scale
        # Head (forward)
        hx, hy = _oval(cx + 0.5*s, cy + 5.0*s, 0.7*s, 0.9*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=1.0,
                   edge_color="#c8a040", edge_width=0.04)
        # Focused eyes
        canvas.circle(cx + 0.7*s, cy + 5.1*s, 0.04*s, fill=True,
                      fill_color="#1a0a05", fill_alpha=0.9)
        # Leaning torso
        t = np.linspace(0, 1, 40)
        spine_x = cx + 0.5*s + 0.3*s*t
        spine_y = cy + 4.5*s - 2.5*s*t
        canvas.line(spine_x, spine_y, color="#d4a574", linewidth=0.12, alpha=0.9)
        # Pumping arms
        canvas.line(cx + 0.3*s, cy + 4.0*s, cx + 1.2*s, cy + 3.0*s,
                    color="#d4a574", linewidth=0.07)
        canvas.line(cx + 0.7*s, cy + 4.0*s, cx - 0.2*s, cy + 3.5*s,
                    color="#d4a574", linewidth=0.07)
        # Dynamic stride legs
        canvas.line(cx + 0.5*s, cy + 2.0*s, cx + 1.5*s, cy + 0.5*s,
                    color="#d4a574", linewidth=0.1)
        canvas.line(cx + 1.5*s, cy + 0.5*s, cx + 1.8*s, cy,
                    color="#d4a574", linewidth=0.08)
        canvas.line(cx + 0.5*s, cy + 2.0*s, cx - 0.8*s, cy + 0.8*s,
                    color="#d4a574", linewidth=0.1)
        canvas.line(cx - 0.8*s, cy + 0.8*s, cx - 1.0*s, cy,
                    color="#d4a574", linewidth=0.08)

    @staticmethod
    def thinking(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Thinking: hand on chin, distant gaze."""
        s = scale
        # Head
        hx, hy = _oval(cx, cy + 5.5*s, 0.8*s, 1.0*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=1.0,
                   edge_color="#c8a040", edge_width=0.04)
        # Distant gaze (looking to side)
        canvas.circle(cx + 0.3*s, cy + 5.7*s, 0.06*s, fill=True,
                      fill_color="#2a1a0a", fill_alpha=0.9)
        # Hand on chin
        canvas.line(cx + 0.3*s, cy + 4.5*s, cx + 0.1*s, cy + 5.0*s,
                    color="#d4a574", linewidth=0.07)
        canvas.circle(cx + 0.1*s, cy + 5.0*s, 0.08*s, fill=True,
                      fill_color="#d4a574", fill_alpha=0.85)
        # Thought bubble
        for i, (bx, by, br) in enumerate([
            (cx + 1.5*s, cy + 6.5*s, 0.15),
            (cx + 2.0*s, cy + 7.0*s, 0.25),
            (cx + 2.8*s, cy + 7.5*s, 0.4)
        ]):
            bub_x, bub_y = _oval(bx, by, br, br*0.7)
            canvas.add(bub_x, bub_y, fill_color="#ffffff", fill_alpha=0.15,
                       edge_color="#c8a040", edge_width=0.02)
        # Torso (slouched)
        canvas.line(cx, cy + 4.5*s, cx - 0.2*s, cy + 2.0*s,
                    color="#d4a574", linewidth=0.12, alpha=0.85)
        # Other arm (resting)
        canvas.line(cx - 0.3*s, cy + 4.0*s, cx - 0.8*s, cy + 2.5*s,
                    color="#d4a574", linewidth=0.06, alpha=0.7)
        # Legs
        canvas.line(cx - 0.2*s, cy + 2.0*s, cx - 0.4*s, cy,
                    color="#d4a574", linewidth=0.08)
        canvas.line(cx - 0.2*s, cy + 2.0*s, cx + 0.3*s, cy,
                    color="#d4a574", linewidth=0.08)

    @staticmethod
    def dancing(canvas, cx=0, cy=0, scale=1.0, **kw):
        """Dancing: dynamic pose, one arm up, leg raised."""
        s = scale
        # Head (tilted)
        hx, hy = _oval(cx - 0.2*s, cy + 5.5*s, 0.7*s, 0.9*s)
        canvas.add(hx, hy, fill_color="#d4a574", fill_alpha=1.0,
                   edge_color="#c8a040", edge_width=0.04)
        # Joyful smile
        smile_x = np.linspace(cx - 0.4*s, cx + 0.1*s, 20)
        smile_y = cy + 5.1*s + 0.1*s*np.sin(np.pi*(smile_x - cx + 0.15*s)/(0.5*s))
        canvas.line(smile_x, smile_y, color="#8b4020", linewidth=0.03)
        # One arm up (spinning)
        canvas.line(cx - 0.3*s, cy + 4.5*s, cx + 0.5*s, cy + 7.5*s,
                    color="#d4a574", linewidth=0.07)
        canvas.circle(cx + 0.5*s, cy + 7.5*s, 0.08*s, fill=True,
                      fill_color="#d4a574", fill_alpha=0.85)
        # Other arm out
        canvas.line(cx + 0.3*s, cy + 4.5*s, cx + 1.5*s, cy + 4.0*s,
                    color="#d4a574", linewidth=0.07)
        # Torso (twisted)
        t = np.linspace(0, 1, 40)
        spine_x = cx - 0.2*s + 0.3*s*np.sin(2*np.pi*t)
        spine_y = cy + 4.5*s - 2.5*s*t
        canvas.line(spine_x, spine_y, color="#d4a574", linewidth=0.12, alpha=0.9)
        # One leg raised (dance step)
        canvas.line(cx - 0.2*s, cy + 2.0*s, cx - 1.0*s, cy + 1.0*s,
                    color="#d4a574", linewidth=0.09)
        canvas.line(cx - 1.0*s, cy + 1.0*s, cx - 1.2*s, cy + 1.5*s,
                    color="#d4a574", linewidth=0.07)
        # Standing leg
        canvas.line(cx - 0.2*s, cy + 2.0*s, cx + 0.3*s, cy,
                    color="#d4a574", linewidth=0.09)


# ============================================================
#  HELPER
# ============================================================

def _oval(cx, cy, rx, ry, n=60):
    th = np.linspace(0, 2*np.pi, n)
    return (cx + rx*np.cos(th)).tolist(), (cy + ry*np.sin(th)).tolist()


# ============================================================
#  DEMO
# ============================================================

if __name__ == "__main__":
    print("[START] Generating human emotions & states showcase...")

    emotions = [
        ("Joy", EmotionTemplates.joy, (0.0, 12, 1.0)),
        ("Sorrow", EmotionTemplates.sorrow, (0.0, 8, 1.0)),
        ("Anger", EmotionTemplates.anger, (0.0, 4, 1.0)),
        ("Fear", EmotionTemplates.fear, (0.0, 0, 1.0)),
        ("Love", EmotionTemplates.love, (0.0, -4, 1.0)),
        ("Surprise", EmotionTemplates.surprise, (0.0, -8, 1.0)),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(18, 14), dpi=150)
    fig.patch.set_facecolor("#0d0a1a")
    fig.suptitle("POLYART: Human Emotions - Polynomial Body Templates",
                 fontsize=16, color="#c8a040", fontweight="bold", fontfamily="serif")

    for idx, (name, func, (ox, oy, sc)) in enumerate(emotions):
        ax = axes[idx // 3][idx % 3]
        ax.set_xlim(-3, 3)
        ax.set_ylim(-1, 8)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor("#0d0a1a")
        ax.set_title(name, fontsize=14, color="#c8a040", fontfamily="serif")

        class MockCanvas:
            def add(self, x, y, **kw): ax.fill(x, y, color=kw.get("fill_color", "#d4a574"), alpha=kw.get("fill_alpha", 1))
            def line(self, *args, **kw):
                if len(args) == 2:
                    ax.plot(args[0], args[1], color=kw.get("color", "#d4a574"), linewidth=kw.get("linewidth", 1)*10, alpha=kw.get("alpha", 1))
                elif len(args) == 4:
                    ax.plot([args[0], args[2]], [args[1], args[3]], color=kw.get("color", "#d4a574"), linewidth=kw.get("linewidth", 1)*10, alpha=kw.get("alpha", 1))
            def circle(self, x, y, r, **kw):
                if kw.get("fill"):
                    circ = plt.Circle((x, y), r, color=kw.get("fill_color", "#d4a574"), alpha=kw.get("fill_alpha", 1))
                    ax.add_patch(circ)
                else:
                    th = np.linspace(0, 2*np.pi, 20)
                    ax.plot(x + r*np.cos(th), y + r*np.sin(th), color=kw.get("color", "#d4a574"), linewidth=1)
            def text(self, x, y, t, **kw): ax.text(x, y, t, fontsize=kw.get("fontsize", 12), color=kw.get("color", "#c8a040"), alpha=kw.get("alpha", 1), ha="center")

        mc = MockCanvas()
        func(mc, cx=ox, cy=oy, scale=sc)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out = r"C:\Users\e\Desktop\6756756756756756\emotions_showcase.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0d0a1a")
    plt.close(fig)
    print(f"[OK] Saved: {out}")

    # States
    states = [
        ("Sleeping", StateTemplates.sleeping, (0, 1, 1.0)),
        ("Running", StateTemplates.running, (0, 1, 1.0)),
        ("Thinking", StateTemplates.thinking, (0, 1, 1.0)),
        ("Dancing", StateTemplates.dancing, (0, 1, 1.0)),
    ]

    fig2, axes2 = plt.subplots(1, 4, figsize=(20, 6), dpi=150)
    fig2.patch.set_facecolor("#0d0a1a")
    fig2.suptitle("POLYART: Human States",
                  fontsize=14, color="#c8a040", fontweight="bold", fontfamily="serif")

    for idx, (name, func, (ox, oy, sc)) in enumerate(states):
        ax = axes2[idx]
        ax.set_xlim(-3, 4)
        ax.set_ylim(-1, 8)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor("#0d0a1a")
        ax.set_title(name, fontsize=12, color="#c8a040", fontfamily="serif")

        mc = MockCanvas()
        func(mc, cx=ox, cy=oy, scale=sc)

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    out2 = r"C:\Users\e\Desktop\6756756756756756\states_showcase.png"
    fig2.savefig(out2, dpi=150, bbox_inches="tight", facecolor="#0d0a1a")
    plt.close(fig2)
    print(f"[OK] Saved: {out2}")
    print("[DONE] All human emotion/state demos complete.")
