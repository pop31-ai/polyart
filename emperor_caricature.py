import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings("ignore")

# ============================================================
#  IMPERATOR MATHEMATICUS MAXIMUS
#  Emperor of the Mathematics of Rome
# ============================================================

fig, ax = plt.subplots(1, 1, figsize=(14, 18), dpi=200)
ax.set_xlim(-7, 7)
ax.set_ylim(-11, 17)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("#0d0a1a")
ax.set_facecolor("#0d0a1a")

def oval(cx, cy, rx, ry, n=100):
    th = np.linspace(0, 2*np.pi, n)
    return cx + rx*np.cos(th), cy + ry*np.sin(th)

def bezier_chain(ax, pts, color, lw, alpha=1.0, **kw):
    codes = [mpath.Path.MOVETO]
    verts = [pts[0]]
    for i in range(1, len(pts)):
        if i % 3 == 1:
            codes.append(mpath.Path.CURVE3)
            verts.append(pts[i])
        elif i % 3 == 2:
            codes.append(mpath.Path.CURVE3)
            verts.append(pts[i])
        else:
            codes.append(mpath.Path.CURVE3)
            verts.append(pts[i])
    codes.append(mpath.Path.CURVE3)
    verts.append(pts[-1])
    path = mpath.Path(verts, codes)
    patch = mpath.PathPatch(path, facecolor="none", edgecolor=color,
                            linewidth=lw, alpha=alpha, **kw)
    ax.add_patch(patch)

# ============================================================
#  GOLDEN RAYS from behind head
# ============================================================
for ang in np.linspace(0, 2*np.pi, 28, endpoint=False):
    x0, y0 = 0.3, 10.5
    x1 = x0 + 10*np.cos(ang)
    y1 = y0 + 10*np.sin(ang)
    ax.plot([x0, x1], [y0, y1], color="#c8a040", linewidth=0.3, alpha=0.12)

# Concentric golden rings
for r in np.linspace(14, 2, 40):
    circ_x, circ_y = oval(0.3, 10, r, r)
    ax.plot(circ_x, circ_y, color="#c8a040", linewidth=0.15, alpha=0.06)

# ============================================================
#  TORSO / TOGA
# ============================================================
toga_x = [-3.2, -2.8, -2.0, -1.2, -0.5, 0.3, 1.1, 1.8, 2.5, 3.0, 3.2,
           2.8, 2.2, 1.5, 0.7, 0, -0.7, -1.5, -2.2, -2.8, -3.2]
toga_y = [-3.5, -2.0, -0.8, -0.1, 0.3, 0.5, 0.3, -0.1, -0.8, -2.0, -3.5,
           -6.0, -7.0, -7.4, -7.6, -7.7, -7.6, -7.4, -7.0, -6.0, -3.5]
ax.fill(toga_x, toga_y, color="#1a1a5a", alpha=0.95, zorder=2)
ax.plot(toga_x, toga_y, color="#c8a040", linewidth=1.2, alpha=0.8, zorder=3)

# Toga folds
for fx in [-2.2, -1.2, -0.2, 0.8, 1.8]:
    ax.plot([fx*0.9, fx*0.7, fx*0.4, fx*0.2], [-0.5, -2.5, -5.0, -7.5],
            color="#c8a040", linewidth=0.3, alpha=0.25, zorder=3)

# Purple imperial stripe
ax.plot([-3.2, -2.8, -2.2], [-3.5, -5.5, -7.0], color="#6a00aa",
        linewidth=3.5, alpha=0.85, zorder=4)
ax.plot([3.2, 2.8, 2.2], [-3.5, -5.5, -7.0], color="#6a00aa",
        linewidth=3.5, alpha=0.85, zorder=4)

# ============================================================
#  NECK
# ============================================================
neck_x, neck_y = oval(0.3, 3.2, 1.2, 1.8)
ax.fill(neck_x, neck_y, color="#d4a574", zorder=5)
ax.plot(neck_x, neck_y, color="#c8a040", linewidth=0.8, zorder=6)

for wy in [2.5, 2.9, 3.3]:
    ax.plot([-0.7, 1.3], [wy, wy], color="#b08050", linewidth=0.4, alpha=0.5, zorder=6)

# ============================================================
#  FACE: fleshy, saggy, emperor authority
# ============================================================
face_x, face_y = oval(0.3, 10.5, 2.6, 3.2, n=120)
face_y += 0.3*np.cos(2*np.linspace(0, 2*np.pi, 120))
face_x += 0.2*np.sin(np.linspace(0, 2*np.pi, 120))*np.exp(-((np.linspace(0,2*np.pi,120)-np.pi/2)**2)/2)
ax.fill(face_x, face_y, color="#d4a574", zorder=7)
ax.plot(face_x, face_y, color="#c8a040", linewidth=1.0, zorder=8)

# Jowls
jl_x, jl_y = oval(-0.6, 8.3, 1.1, 0.6)
jr_x, jr_y = oval(1.2, 8.3, 1.1, 0.6)
ax.fill(jl_x, jl_y, color="#c89868", alpha=0.85, zorder=7)
ax.fill(jr_x, jr_y, color="#c89868", alpha=0.85, zorder=7)
ax.plot(jl_x, jl_y, color="#b08050", linewidth=0.4, alpha=0.6, zorder=8)
ax.plot(jr_x, jr_y, color="#b08050", linewidth=0.4, alpha=0.6, zorder=8)

# ============================================================
#  HAIR: receding, dark, thinning
# ============================================================
hair_x, hair_y = oval(0.3, 13.0, 2.9, 1.6)
# Recede at forehead
recede_mask = (hair_y > 12.0) & (np.abs(hair_x - 0.3) < 2.2)
hair_y[recede_mask] *= 0.65
hair_x[recede_mask] *= 1.1
ax.fill(hair_x, hair_y, color="#1a0f05", zorder=9)
ax.plot(hair_x, hair_y, color="#c8a040", linewidth=0.5, zorder=10)

# Sideburns
sl_x, sl_y = oval(-2.3, 11.2, 0.7, 1.8)
sr_x, sr_y = oval(2.9, 11.2, 0.7, 1.8)
ax.fill(sl_x, sl_y, color="#1a0f05", zorder=9)
ax.fill(sr_x, sr_y, color="#1a0f05", zorder=9)

# Hair strands
for i in range(25):
    th = np.linspace(-1.8, 0.3, 30) + i*0.12
    hx = 0.3 + 2.8*np.cos(th)*np.exp(-0.3*th)
    hy = 12.8 + 1.2*np.sin(th)*np.exp(-0.2*th)
    ax.plot(hx, hy, color="#2a1a0a", linewidth=0.3, alpha=0.5, zorder=10)

# ============================================================
#  EARS
# ============================================================
ear_l_x, ear_l_y = oval(-2.4, 10.5, 0.45, 0.85)
ear_r_x, ear_r_y = oval(3.0, 10.5, 0.45, 0.85)
ax.fill(ear_l_x, ear_l_y, color="#d4a574", zorder=8)
ax.fill(ear_r_x, ear_r_y, color="#d4a574", zorder=8)
ax.plot(ear_l_x, ear_l_y, color="#c8a040", linewidth=0.6, zorder=9)
ax.plot(ear_r_x, ear_r_y, color="#c8a040", linewidth=0.6, zorder=9)

# ============================================================
#  EYES: heavy lids, hollow sockets
# ============================================================
for ex in [-0.6, 1.2]:
    # Dark socket
    sock_x, sock_y = oval(ex, 10.8, 0.95, 0.75)
    ax.fill(sock_x, sock_y, color="#3a2010", alpha=0.7, zorder=11)

    # Heavy upper lid
    lx = np.linspace(ex-0.75, ex+0.75, 60)
    ly_up = 10.8 + 0.4*np.cos(np.pi*(lx-ex)/0.75)*(1 - 0.4*np.exp(-((lx-ex)/0.35)**2))
    ly_dn = 10.8 - 0.35*np.cos(np.pi*(lx-ex)/0.75)*(1 - 0.3*np.exp(-((lx-ex)/0.4)**2))
    ax.fill_between(lx, ly_dn, ly_up, color="#d4a574", alpha=0.9, zorder=12)
    ax.plot(lx, ly_up, color="#5a3a20", linewidth=2.0, zorder=13)
    ax.plot(lx, ly_dn, color="#8b6040", linewidth=1.2, zorder=13)

    # Droopy outer corner (tired look)
    ax.plot([ex+0.7, ex+0.9], [10.8, 10.6], color="#8b6040", linewidth=0.8, alpha=0.7, zorder=13)

    # Iris + pupil
    iris_x, iris_y = oval(ex, 10.8, 0.32, 0.38)
    ax.fill(iris_x, iris_y, color="#3a2510", zorder=14)
    pup_x, pup_y = oval(ex, 10.8, 0.12, 0.14)
    ax.fill(pup_x, pup_y, color="#0a0505", zorder=15)
    # Highlight
    ax.plot(ex+0.12, 10.92, "o", color="white", markersize=2, alpha=0.5, zorder=16)

    # Brow ridge
    bx = np.linspace(ex-0.85, ex+0.7, 50)
    by = 11.4 + 0.25*np.exp(-((bx-ex)/0.45)**2)
    ax.plot(bx, by, color="#5a3a20", linewidth=2.5, alpha=0.75, zorder=13)

# ============================================================
#  NOSE: Aquiline Roman - straight with bump
# ============================================================
# Bridge
nose_xs = [0.3, 0.2, 0.1, 0.05, 0.1, 0.2, 0.3]
nose_ys = [11.0, 10.6, 10.1, 9.6, 9.4, 9.35, 9.4]
ax.plot(nose_xs, nose_ys, color="#b08050", linewidth=1.5, alpha=0.8, zorder=12)

# Bridge highlight
ax.plot([0.15, 0.2], [10.8, 10.0], color="#e8c898", linewidth=0.6, alpha=0.4, zorder=12)

# Nose bump (the aquiline hook)
bump_x, bump_y = oval(0.12, 9.7, 0.35, 0.25)
ax.fill(bump_x, bump_y, color="#d4a574", zorder=12)
ax.plot(bump_x, bump_y, color="#b08050", linewidth=0.6, zorder=13)

# Nose tip
tip_x, tip_y = oval(0.18, 9.25, 0.48, 0.38)
ax.fill(tip_x, tip_y, color="#d4a574", zorder=12)
ax.plot(tip_x, tip_y, color="#b08050", linewidth=0.8, zorder=13)

# Nostrils
nl_x, nl_y = oval(-0.18, 9.05, 0.22, 0.17)
nr_x, nr_y = oval(0.54, 9.05, 0.22, 0.17)
ax.fill(nl_x, nl_y, color="#3a2010", alpha=0.8, zorder=13)
ax.fill(nr_x, nr_y, color="#3a2010", alpha=0.8, zorder=13)

# Nose shadow
ax.plot([0.0, 0.0], [10.5, 9.3], color="#8b6040", linewidth=0.6, alpha=0.35, zorder=12)

# ============================================================
#  MOUTH: thin lips, emperor's frown
# ============================================================
mx = np.linspace(-0.8, 1.4, 80)
mu = 8.55 + 0.08*np.sin(np.pi*(mx-0.3)/1.1) + 0.04*np.exp(-((mx-0.3)/0.3)**2)
ml = 8.40 - 0.10*np.sin(np.pi*(mx-0.3)/1.0)
ax.fill_between(mx, ml, mu, color="#c08060", alpha=0.7, zorder=12)
ax.plot(mx, mu, color="#a06040", linewidth=1.0, zorder=13)
ax.plot(mx, ml, color="#a06040", linewidth=1.2, zorder=13)
# Mouth line with slight downturn
mouth_x = np.linspace(-0.6, 1.2, 60)
mouth_y = 8.48 - 0.04*np.sin(np.pi*mouth_x/1.8)
ax.plot(mouth_x, mouth_y, color="#8b6040", linewidth=0.6, alpha=0.7, zorder=13)

# ============================================================
#  WRINKLES
# ============================================================
# Forehead
for wy in [11.8, 12.1, 12.4]:
    wx = np.linspace(-1.5, 2.1, 40)
    wy_arr = wy + 0.03*np.sin(3*wx)
    ax.plot(wx, wy_arr, color="#b08050", linewidth=0.4, alpha=0.35, zorder=11)

# Crow's feet
for ex in [-0.6, 1.2]:
    s = 1 if ex > 0 else -1
    for k in range(4):
        ax.plot([ex+s*0.7, ex+s*(1.0+0.1*k)],
                [10.8+0.05*k, 10.8+0.15*k-0.08*k],
                color="#b08050", linewidth=0.3, alpha=0.35, zorder=11)

# Nasolabial folds
ax.plot([-0.35, -0.55, -0.75], [9.6, 9.0, 8.5], color="#b08050",
        linewidth=0.7, alpha=0.45, zorder=11)
ax.plot([0.95, 1.15, 1.35], [9.6, 9.0, 8.5], color="#b08050",
        linewidth=0.7, alpha=0.45, zorder=11)

# Double chin lines
for cl in [7.6, 7.8, 8.0]:
    cx_arr = np.linspace(-1.0, 1.6, 40)
    cy_arr = cl + 0.04*np.sin(2*cx_arr)
    ax.plot(cx_arr, cy_arr, color="#b08050", linewidth=0.3, alpha=0.3, zorder=8)

# ============================================================
#  CHIN: strong, cleft
# ============================================================
chin_x, chin_y = oval(0.3, 7.6, 1.3, 0.9)
ax.fill(chin_x, chin_y, color="#d4a574", alpha=0.95, zorder=7)
ax.plot([0.2, 0.4], [8.1, 7.6], color="#b08050", linewidth=0.4, alpha=0.4, zorder=8)

# ============================================================
#  LAUREL WREATH
# ============================================================
# Gold band
band_x, band_y = oval(0.3, 13.7, 3.1, 0.55)
ax.fill(band_x, band_y, color="#c8a040", alpha=0.9, zorder=15)
ax.plot(band_x, band_y, color="#ffd700", linewidth=1.0, zorder=16)

# Leaves
for i in range(28):
    ang = i * 2*np.pi/28
    lx = 0.3 + 3.1*np.cos(ang)
    ly = 13.7 + 0.55*np.sin(ang)
    la = ang + np.pi/2
    pts = [(lx, ly),
           (lx+0.25*np.cos(la)+0.08*np.cos(la+np.pi/2),
            ly+0.25*np.sin(la)+0.08*np.sin(la+np.pi/2)),
           (lx+0.5*np.cos(la), ly+0.5*np.sin(la)),
           (lx+0.25*np.cos(la)-0.08*np.cos(la+np.pi/2),
            ly+0.25*np.sin(la)-0.08*np.sin(la+np.pi/2)),
           (lx, ly)]
    lxs = [p[0] for p in pts]
    lys = [p[1] for p in pts]
    ax.fill(lxs, lys, color="#2a6a1a", alpha=0.85, zorder=16)
    ax.plot(lxs, lys, color="#c8a040", linewidth=0.3, zorder=17)

# Cross at top
ax.plot([-0.5, 1.1], [14.25, 14.25], color="#ffd700", linewidth=1.5, zorder=17)
ax.plot([0.3, 0.3], [14.1, 14.7], color="#ffd700", linewidth=1.5, zorder=17)

# ============================================================
#  SHOULDER DRAPES
# ============================================================
sl_x = np.linspace(-3.2, -0.5, 50)
sl_y = -0.5 + 1.8*np.exp(-((sl_x+2.0)/1.1)**2)
ax.fill_between(sl_x, -3.5, sl_y, color="#1a1a5a", alpha=0.9, zorder=2)
ax.plot(sl_x, sl_y, color="#c8a040", linewidth=0.8, alpha=0.6, zorder=3)

sr_x = np.linspace(1.1, 3.2, 50)
sr_y = -0.5 + 1.8*np.exp(-((sr_x-2.0)/1.1)**2)
ax.fill_between(sr_x, -3.5, sr_y, color="#1a1a5a", alpha=0.9, zorder=2)
ax.plot(sr_x, sr_y, color="#c8a040", linewidth=0.8, alpha=0.6, zorder=3)

# ============================================================
#  SPQR BANNER
# ============================================================
bx = np.linspace(-4.5, 4.5, 100)
by = -8.5 + 0.2*np.sin(np.pi*bx/4.5)
ax.fill_between(bx, by-0.5, by+0.5, color="#1a0a0a", alpha=0.9, zorder=2)
ax.plot(bx, by, color="#c8a040", linewidth=1.5, zorder=3)
ax.plot(bx, by+0.5, color="#c8a040", linewidth=0.8, zorder=3)
ax.plot(bx, by-0.5, color="#c8a040", linewidth=0.8, zorder=3)

ax.text(0, -8.5, "S  P  Q  R", fontsize=14, color="#ffd700",
        ha="center", va="center", fontweight="bold", fontfamily="serif", zorder=4)

# ============================================================
#  MATHEMATICAL FORMULAS in background
# ============================================================
formulas = [
    (-5.5, 15, r"$\varphi = \frac{1+\sqrt{5}}{2}$", 11),
    (5.5, 15, r"$e^{i\pi}+1=0$", 11),
    (-5.5, 4, r"$\int_0^{\infty} e^{-x^2}dx = \frac{\sqrt{\pi}}{2}$", 9),
    (5.5, 4, r"$\sum_{n=0}^{\infty} \frac{1}{n!} = e$", 9),
    (-5.5, -3, r"$\nabla \times \mathbf{F}$", 10),
    (5.5, -3, r"$\zeta(2) = \frac{\pi^2}{6}$", 10),
]
for fx, fy, txt, fs in formulas:
    ax.text(fx, fy, txt, fontsize=fs, color="#c8a040", alpha=0.35,
            ha="center", va="center", fontfamily="serif", zorder=1)

# ============================================================
#  TITLE TEXT
# ============================================================
ax.text(0, -9.8, "IMP. MATHEMATICUS MAXIMUS",
        fontsize=20, color="#ffd700", alpha=0.95,
        ha="center", va="center", fontweight="bold", fontfamily="serif", zorder=4)

ax.text(0, -10.6, "Divus Imperator Matheseos Romae",
        fontsize=12, color="#c8a040", alpha=0.7,
        ha="center", va="center", fontstyle="italic", fontfamily="serif", zorder=4)

# ============================================================
#  CORNER DECORATIONS: Golden spirals
# ============================================================
for cx, cy, sgn in [(-6, 16, 1), (6, 16, -1)]:
    th = np.linspace(0, 4*np.pi, 200)
    r = 0.05 * np.exp(0.15*th)
    sx = cx + sgn*r*np.cos(th)
    sy = cy + r*np.sin(th)
    ax.plot(sx, sy, color="#c8a040", linewidth=0.5, alpha=0.4, zorder=1)

# ============================================================
#  SAVE
# ============================================================
out = r"C:\Users\e\Desktop\6756756756756756\emperor_mathematicus.png"
fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="#0d0a1a",
            edgecolor="none", pad_inches=0.3)
plt.close(fig)
print(f"[OK] Saved: {out}")
print("[DONE] Imperator Mathematicus Maximus")
