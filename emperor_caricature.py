import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import warnings
warnings.filterwarnings("ignore")

PHI = (1 + np.sqrt(5)) / 2

fig = plt.figure(figsize=(16, 20), dpi=250)
ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
ax.set_xlim(-8, 8)
ax.set_ylim(-12, 18)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("#080612")
ax.set_facecolor("#080612")

def oval(cx, cy, rx, ry, n=120):
    th = np.linspace(0, 2*np.pi, n)
    return cx + rx*np.cos(th), cy + ry*np.sin(th)

# ============================================================
#  BACKGROUND: Rich texture with golden ratio elements
# ============================================================
# Deep gradient
for r in np.linspace(18, 1, 80):
    alpha = 0.008 * (r / 18)
    circ_x, circ_y = oval(0, 3, r, r)
    ax.fill(circ_x, circ_y, color="#1a0a2e", alpha=alpha, zorder=0)

# Dense golden ratio grid (more lines = more edge density)
for i in range(40):
    y = -12 + i * 30/40
    ax.plot([-8, 8], [y, y], color="#c8a040", linewidth=0.12, alpha=0.12, zorder=0)
    ax.plot([y, y], [-12, 18], color="#c8a040", linewidth=0.12, alpha=0.12, zorder=0)

# Fibonacci spirals (multiple, overlapping)
for cx, cy, sgn, a in [(-6.5, 17, 1, 0.04), (6.5, 17, -1, 0.04),
                         (-6.5, -11, 1, 0.03), (6.5, -11, -1, 0.03),
                         (0, 3, 1, 0.02)]:
    th = np.linspace(0, 5*np.pi, 300)
    r = a * np.exp(0.3063 * th)
    mask = r < 14
    sx = cx + r[mask]*np.cos(th[mask])*sgn
    sy = cy + r[mask]*np.sin(th[mask])
    ax.plot(sx, sy, color="#c8a040", linewidth=0.3, alpha=0.2, zorder=1)

# Concentric golden rectangles (background texture)
for k in range(6):
    s = 1.5 * PHI**k
    if s > 15: break
    rect = plt.Rectangle((-s/2, 3-s/2), s, s, fill=False,
                          edgecolor="#c8a040", linewidth=0.15, alpha=0.08, zorder=0)
    ax.add_patch(rect)

# ============================================================
#  GOLDEN RAYS (denser, varying alpha)
# ============================================================
for i, ang in enumerate(np.linspace(0, 2*np.pi, 48, endpoint=False)):
    x0, y0 = 0.3, 11.0
    length = 12 + 2*np.sin(3*ang)
    x1 = x0 + length*np.cos(ang)
    y1 = y0 + length*np.sin(ang)
    alpha = 0.04 + 0.03*np.sin(i*PHI)
    ax.plot([x0, x1], [y0, y1], color="#c8a040", linewidth=0.2, alpha=alpha, zorder=1)

# Outward spirals from head
for k in range(6):
    th = np.linspace(0, 7*np.pi, 500)
    r = (2 + k*1.2) * np.exp(0.04*th)
    mask = r < 16
    sx = 0.3 + r[mask]*np.cos(th[mask])
    sy = 11.0 + r[mask]*np.sin(th[mask])
    ax.plot(sx, sy, color="#c8a040", linewidth=0.12, alpha=0.05, zorder=1)

# ============================================================
#  TORSO / TOGA
# ============================================================
toga_xp = [-3.5, -3.0, -2.2, -1.5, -0.8, 0, 0.8, 1.5, 2.2, 3.0, 3.5,
            3.2, 2.8, 2.2, 1.5, 0.8, 0, -0.8, -1.5, -2.2, -2.8, -3.2, -3.5]
toga_yp = [-4.0, -2.5, -1.2, -0.3, 0.3, 0.6, 0.3, -0.3, -1.2, -2.5, -4.0,
            -7.0, -8.0, -8.5, -8.8, -9.0, -9.1, -9.0, -8.8, -8.5, -8.0, -7.0, -4.0]
ax.fill(toga_xp, toga_yp, color="#141450", alpha=0.95, zorder=2)
ax.plot(toga_xp, toga_yp, color="#c8a040", linewidth=1.5, alpha=0.85, zorder=3)

# Many toga fold lines (more detail)
for fold_x in np.linspace(-2.8, 2.8, 12):
    t = np.linspace(0, 1, 60)
    fx = fold_x * (1 - 0.35*t**2)
    fy = -0.5 - 8.5*t**1.3
    ax.plot(fx, fy, color="#c8a040", linewidth=0.2, alpha=0.18, zorder=3)

# Diagonal drape lines
for i in range(8):
    t = np.linspace(0, 1, 40)
    sx = -2.5 + i*0.7 + 0.5*t
    sy = -1.0 - 7.0*t**0.9
    ax.plot(sx, sy, color="#c8a040", linewidth=0.15, alpha=0.12, zorder=3)

# Purple imperial stripes
for stripe in [-3.3, 3.3]:
    t = np.linspace(0, 1, 80)
    sx = stripe * (1 - 0.1*t)
    sy = -4.0 - 5.0*t**0.8
    ax.plot(sx, sy, color="#6a00aa", linewidth=3.0, alpha=0.85, zorder=4)

# Brooch fibula with chain
brooch_x, brooch_y = oval(-2.8, -1.5, 0.35, 0.35)
ax.fill(brooch_x, brooch_y, color="#ffd700", alpha=0.9, zorder=5)
ax.plot(brooch_x, brooch_y, color="#c8a040", linewidth=0.8, zorder=6)
for i in range(10):
    cx = -2.8 + 0.4*i*0.12
    cy = -1.5 - 0.25*i
    c_x, c_y = oval(cx, cy, 0.07, 0.05)
    ax.fill(c_x, c_y, color="#ffd700", alpha=0.6, zorder=5)

# Embroidered mathematical pattern on toga
# Small golden spirals on fabric
for cx, cy in [(-1.5, -5), (-0.5, -6), (0.5, -5.5), (1.5, -6.5), (0, -7.5)]:
    th = np.linspace(0, 3*np.pi, 60)
    r = 0.03 * np.exp(0.2*th)
    sx = cx + r*np.cos(th)
    sy = cy + r*np.sin(th)
    ax.plot(sx, sy, color="#c8a040", linewidth=0.15, alpha=0.3, zorder=4)

# ============================================================
#  NECK
# ============================================================
neck_x, neck_y = oval(0.3, 3.8, 1.3, 2.2)
ax.fill(neck_x, neck_y, color="#d4a574", zorder=5)
ax.plot(neck_x, neck_y, color="#c8a040", linewidth=0.6, zorder=6)

for i, wy in enumerate([2.8, 3.2, 3.6, 4.0]):
    t = np.linspace(-1, 1, 50)
    wx = 0.3 + 1.1*t
    wy_arr = wy + 0.04*np.sin(3*np.pi*t)*np.exp(-t**2)
    ax.plot(wx, wy_arr, color="#b08050", linewidth=0.35, alpha=0.4+i*0.05, zorder=6)

# Sternocleidomastoid
ax.plot([-0.5, -0.2, 0.3], [2.5, 3.5, 5.0], color="#b08050", linewidth=0.6, alpha=0.4, zorder=6)
ax.plot([1.1, 0.8, 0.3], [2.5, 3.5, 5.0], color="#b08050", linewidth=0.6, alpha=0.4, zorder=6)

# Adam's apple
adam_x, adam_y = oval(0.3, 3.5, 0.2, 0.3)
ax.fill(adam_x, adam_y, color="#c89868", alpha=0.5, zorder=6)

# ============================================================
#  FACE
# ============================================================
face_x, face_y = oval(0.3, 11.0, 2.7, 3.4, n=150)
face_y += 0.25*np.cos(2*np.linspace(0, 2*np.pi, 150))
face_x += 0.15*np.sin(np.linspace(0, 2*np.pi, 150))*np.exp(-((np.linspace(0,2*np.pi,150)-np.pi/2)**2)/1.5)
ax.fill(face_x, face_y, color="#d4a574", zorder=7)
ax.plot(face_x, face_y, color="#c8a040", linewidth=0.8, zorder=8)

# Jowls
jl_x, jl_y = oval(-0.5, 8.8, 1.2, 0.7)
jr_x, jr_y = oval(1.1, 8.8, 1.2, 0.7)
ax.fill(jl_x, jl_y, color="#c89868", alpha=0.85, zorder=7)
ax.fill(jr_x, jr_y, color="#c89868", alpha=0.85, zorder=7)
ax.plot(jl_x, jl_y, color="#b08050", linewidth=0.35, alpha=0.5, zorder=8)
ax.plot(jr_x, jr_y, color="#b08050", linewidth=0.35, alpha=0.5, zorder=8)

# Cheekbone highlights
ax.plot([-1.8, -1.5, -1.0], [11.2, 11.0, 10.8], color="#e8c898", linewidth=0.4, alpha=0.3, zorder=9)
ax.plot([2.4, 2.1, 1.6], [11.2, 11.0, 10.8], color="#e8c898", linewidth=0.4, alpha=0.3, zorder=9)

# Skin texture (stipple dots)
np.random.seed(42)
for _ in range(200):
    angle = np.random.uniform(0, 2*np.pi)
    r_face = np.random.uniform(0, 2.5)
    px = 0.3 + r_face*np.cos(angle)
    py = 11.0 + r_face*1.2*np.sin(angle)
    if abs(r_face) < 2.6:
        ax.plot(px, py, ".", color="#b08050", markersize=0.3, alpha=0.15, zorder=8)

# ============================================================
#  HAIR
# ============================================================
hair_x, hair_y = oval(0.3, 13.5, 3.0, 1.8)
recede = (hair_y > 12.3) & (np.abs(hair_x - 0.3) < 2.5)
hair_y[recede] *= 0.6
hair_x[recede] *= 1.15
ax.fill(hair_x, hair_y, color="#1a0f05", zorder=9)
ax.plot(hair_x, hair_y, color="#c8a040", linewidth=0.4, zorder=10)

sl_x, sl_y = oval(-2.4, 11.5, 0.8, 2.0)
sr_x, sr_y = oval(3.0, 11.5, 0.8, 2.0)
ax.fill(sl_x, sl_y, color="#1a0f05", zorder=9)
ax.fill(sr_x, sr_y, color="#1a0f05", zorder=9)

# More hair strands
for i in range(40):
    th = np.linspace(-2.0, 0.2, 40) + i*0.08
    hx = 0.3 + 3.0*np.cos(th)*np.exp(-0.25*th)
    hy = 13.3 + 1.5*np.sin(th)*np.exp(-0.15*th)
    ax.plot(hx, hy, color="#2a1a0a", linewidth=0.25, alpha=0.45, zorder=10)

# Widow's peak
ax.plot([-0.5, 0.3, 1.1], [12.0, 11.8, 12.0], color="#1a0f05", linewidth=1.5, alpha=0.6, zorder=10)

# ============================================================
#  EARS
# ============================================================
for ex, side in [(-2.5, -1), (3.1, 1)]:
    ear_x, ear_y = oval(ex, 11.0, 0.5, 0.9)
    ax.fill(ear_x, ear_y, color="#d4a574", zorder=8)
    ax.plot(ear_x, ear_y, color="#c8a040", linewidth=0.5, zorder=9)
    inner_x, inner_y = oval(ex + side*0.05, 11.0, 0.25, 0.5)
    ax.plot(inner_x, inner_y, color="#b08050", linewidth=0.3, alpha=0.5, zorder=9)
    lobe_x, lobe_y = oval(ex, 10.1, 0.3, 0.3)
    ax.fill(lobe_x, lobe_y, color="#d4a574", zorder=8)

# ============================================================
#  EYES: Heavy lids, hollow sockets, tired gaze
# ============================================================
for ex in [-0.7, 1.3]:
    sock_x, sock_y = oval(ex, 11.3, 1.0, 0.8)
    ax.fill(sock_x, sock_y, color="#2a1508", alpha=0.65, zorder=11)
    depx, depy = oval(ex, 11.3, 0.85, 0.65)
    ax.fill(depx, depy, color="#3a2515", alpha=0.5, zorder=11)

    lx = np.linspace(ex-0.8, ex+0.8, 80)
    lid_up = 11.3 + 0.42*np.cos(np.pi*(lx-ex)/0.8)
    droop = 0.15*np.exp(-((lx-ex-0.5)/0.3)**2)
    lid_up -= droop
    lid_dn = 11.3 - 0.35*np.cos(np.pi*(lx-ex)/0.8)
    lid_dn += 0.08*np.exp(-((lx-ex)/0.4)**2)
    ax.fill_between(lx, lid_dn, lid_up, color="#d4a574", alpha=0.95, zorder=12)
    ax.plot(lx, lid_up, color="#4a2a10", linewidth=2.2, zorder=13)
    ax.plot(lx, lid_dn, color="#7a5030", linewidth=1.0, zorder=13)

    # Crow's feet
    for k in range(5):
        s = 1 if ex > 0 else -1
        ax.plot([ex+s*0.75, ex+s*(1.1+0.08*k)],
                [11.3+0.03*k, 11.3+0.12*k-0.05*k],
                color="#b08050", linewidth=0.25, alpha=0.35, zorder=11)

    iris_x, iris_y = oval(ex, 11.3, 0.33, 0.38)
    ax.fill(iris_x, iris_y, color="#2a1a0a", zorder=14)
    pup_x, pup_y = oval(ex, 11.3, 0.13, 0.15)
    ax.fill(pup_x, pup_y, color="#0a0505", zorder=15)
    ax.plot(ex+0.1, 11.42, "o", color="white", markersize=2.5, alpha=0.55, zorder=16)
    ax.plot(ex-0.05, 11.25, "o", color="white", markersize=1.2, alpha=0.3, zorder=16)

    # Brow ridge
    bx = np.linspace(ex-0.9, ex+0.8, 60)
    by = 11.85 + 0.28*np.exp(-((bx-ex)/0.5)**2)
    ax.plot(bx, by, color="#4a2a10", linewidth=2.8, alpha=0.7, zorder=13)

# ============================================================
#  NOSE: Aquiline Roman
# ============================================================
t = np.linspace(0, 1, 80)
nose_bridge_x = 0.3 - 0.25*t + 0.05*t**3
nose_bridge_y = 11.5 - 2.2*t**0.8
ax.plot(nose_bridge_x, nose_bridge_y, color="#b08050", linewidth=1.8, alpha=0.85, zorder=12)
ax.plot([0.18, 0.22], [11.3, 10.5], color="#e8c898", linewidth=0.5, alpha=0.35, zorder=12)

bump_x, bump_y = oval(0.12, 10.2, 0.38, 0.28)
ax.fill(bump_x, bump_y, color="#d4a574", zorder=12)
ax.plot(bump_x, bump_y, color="#b08050", linewidth=0.5, zorder=13)

tip_x, tip_y = oval(0.2, 9.3, 0.52, 0.42)
ax.fill(tip_x, tip_y, color="#d4a574", zorder=12)
ax.plot(tip_x, tip_y, color="#b08050", linewidth=0.7, zorder=13)

nl_x, nl_y = oval(-0.15, 9.1, 0.24, 0.18)
nr_x, nr_y = oval(0.55, 9.1, 0.24, 0.18)
ax.fill(nl_x, nl_y, color="#2a1508", alpha=0.85, zorder=13)
ax.fill(nr_x, nr_y, color="#2a1508", alpha=0.85, zorder=13)

ax.plot([0.0, -0.05, 0.0], [10.8, 10.0, 9.3], color="#8b6040", linewidth=0.5, alpha=0.3, zorder=12)

# ============================================================
#  MOUTH
# ============================================================
mx = np.linspace(-0.85, 1.45, 100)
mu = 8.7 + 0.06*np.sin(np.pi*(mx-0.3)/1.15) + 0.03*np.exp(-((mx-0.3)/0.25)**2)
mu += 0.04*(np.abs(mx-0.3)/1.15)**3
ml = 8.52 - 0.12*np.sin(np.pi*(mx-0.3)/1.05)
ax.fill_between(mx, ml, mu, color="#c08060", alpha=0.65, zorder=12)
ax.plot(mx, mu, color="#a06040", linewidth=1.2, zorder=13)
ax.plot(mx, ml, color="#a06040", linewidth=1.4, zorder=13)
mouth_x = np.linspace(-0.65, 1.25, 80)
mouth_y = 8.62 - 0.03*np.sin(np.pi*mouth_x/1.9) + 0.02*(mouth_x/1.9)**4
ax.plot(mouth_x, mouth_y, color="#7a4020", linewidth=0.6, alpha=0.65, zorder=13)

# ============================================================
#  WRINKLES (detailed)
# ============================================================
for wy in [12.1, 12.4, 12.7]:
    wx = np.linspace(-1.6, 2.2, 60)
    wy_arr = wy + 0.025*np.sin(4*wx)*np.exp(-wx**2/8)
    ax.plot(wx, wy_arr, color="#b08050", linewidth=0.35, alpha=0.3, zorder=11)

ax.plot([0.0, 0.1, 0.2], [11.8, 11.5, 11.2], color="#b08050", linewidth=0.4, alpha=0.4, zorder=11)
ax.plot([0.6, 0.5, 0.4], [11.8, 11.5, 11.2], color="#b08050", linewidth=0.4, alpha=0.4, zorder=11)

t = np.linspace(0, 1, 40)
ax.plot(-0.35 - 0.3*t, 9.7 - 1.2*t**0.8, color="#b08050", linewidth=0.65, alpha=0.45, zorder=11)
ax.plot(0.95 + 0.3*t, 9.7 - 1.2*t**0.8, color="#b08050", linewidth=0.65, alpha=0.45, zorder=11)

ax.plot([-0.5, -0.6, -0.7], [8.6, 8.2, 7.8], color="#b08050", linewidth=0.3, alpha=0.35, zorder=11)
ax.plot([1.1, 1.2, 1.3], [8.6, 8.2, 7.8], color="#b08050", linewidth=0.3, alpha=0.35, zorder=11)

for ex in [-0.7, 1.3]:
    bx = np.linspace(ex-0.7, ex+0.7, 50)
    by = 10.6 - 0.12*np.exp(-((bx-ex)/0.35)**2)
    ax.plot(bx, by, color="#b08050", linewidth=0.35, alpha=0.35, zorder=11)

# ============================================================
#  CHIN
# ============================================================
chin_x, chin_y = oval(0.3, 7.7, 1.4, 1.0)
ax.fill(chin_x, chin_y, color="#d4a574", alpha=0.95, zorder=7)
ax.plot([0.15, 0.35], [8.3, 7.7], color="#b08050", linewidth=0.35, alpha=0.4, zorder=8)

# ============================================================
#  LAUREL WREATH
# ============================================================
band_x, band_y = oval(0.3, 14.2, 3.3, 0.55)
ax.fill(band_x, band_y, color="#c8a040", alpha=0.9, zorder=15)
ax.plot(band_x, band_y, color="#ffd700", linewidth=1.2, zorder=16)

for i in range(32):
    ang = i * 2*np.pi/32
    lx = 0.3 + 3.3*np.cos(ang)
    ly = 14.2 + 0.55*np.sin(ang)
    la = ang + np.pi/2
    pts = np.array([
        [lx, ly],
        [lx + 0.15*np.cos(la) + 0.06*np.cos(la+np.pi/2),
         ly + 0.15*np.sin(la) + 0.06*np.sin(la+np.pi/2)],
        [lx + 0.4*np.cos(la), ly + 0.4*np.sin(la)],
        [lx + 0.15*np.cos(la) - 0.06*np.cos(la+np.pi/2),
         ly + 0.15*np.sin(la) - 0.06*np.sin(la+np.pi/2)],
        [lx, ly]
    ])
    color = "#2a6a1a" if i % 3 != 0 else "#3a8a2a"
    ax.fill(pts[:,0], pts[:,1], color=color, alpha=0.85, zorder=16)
    ax.plot(pts[:,0], pts[:,1], color="#c8a040", linewidth=0.25, zorder=17)

ax.plot([-0.6, 1.2], [14.8, 14.8], color="#ffd700", linewidth=2.0, zorder=17)
ax.plot([0.3, 0.3], [14.65, 15.1], color="#ffd700", linewidth=2.0, zorder=17)

# ============================================================
#  SHOULDER DRAPES
# ============================================================
sl_t = np.linspace(0, 1, 60)
sl_x = -3.5 + 2.5*sl_t
sl_y = -0.3 + 1.5*np.exp(-((sl_x+2.2)/1.2)**2)
ax.fill_between(sl_x, -4.0, sl_y, color="#141450", alpha=0.9, zorder=2)
ax.plot(sl_x, sl_y, color="#c8a040", linewidth=0.7, alpha=0.5, zorder=3)

sr_x = 1.2 + 2.3*sl_t
sr_y = -0.3 + 1.5*np.exp(-((sr_x-2.2)/1.2)**2)
ax.fill_between(sr_x, -4.0, sr_y, color="#141450", alpha=0.9, zorder=2)
ax.plot(sr_x, sr_y, color="#c8a040", linewidth=0.7, alpha=0.5, zorder=3)

# ============================================================
#  SPQR BANNER
# ============================================================
bx = np.linspace(-5, 5, 120)
by = -9.5 + 0.25*np.sin(np.pi*bx/5)
ax.fill_between(bx, by-0.6, by+0.6, color="#0a0505", alpha=0.92, zorder=2)
ax.plot(bx, by+0.6, color="#c8a040", linewidth=1.0, zorder=3)
ax.plot(bx, by-0.6, color="#c8a040", linewidth=1.0, zorder=3)

# S
sx = np.linspace(-3.5, -2.5, 30)
sy1 = -9.5 + 0.3*np.cos(np.pi*(sx+3)/0.5)
ax.plot(sx, sy1, color="#ffd700", linewidth=1.5, zorder=4)
# P
ax.plot([-1.8, -1.8], [-9.8, -9.2], color="#ffd700", linewidth=1.5, zorder=4)
px = np.linspace(-1.8, -1.3, 20)
py = -9.2 + 0.15*np.sin(np.pi*(px+1.8)/0.5)
ax.plot(px, py, color="#ffd700", linewidth=1.5, zorder=4)
# Q
qx, qy = oval(-0.3, -9.5, 0.25, 0.25)
ax.plot(qx, qy, color="#ffd700", linewidth=1.5, zorder=4)
ax.plot([-0.1, 0.1], [-9.7, -9.9], color="#ffd700", linewidth=1.5, zorder=4)
# R
ax.plot([0.8, 0.8], [-9.8, -9.2], color="#ffd700", linewidth=1.5, zorder=4)
rx = np.linspace(0.8, 1.3, 20)
ry = -9.2 + 0.15*np.sin(np.pi*(rx-0.8)/0.5)
ax.plot(rx, ry, color="#ffd700", linewidth=1.5, zorder=4)
ax.plot([0.8, 1.3], [-9.5, -9.8], color="#ffd700", linewidth=1.5, zorder=4)

# ============================================================
#  MATHEMATICAL FORMULAS (more, denser)
# ============================================================
formulas = [
    (-6.0, 16, r"$\varphi = \frac{1+\sqrt{5}}{2}$", 12),
    (6.0, 16, r"$e^{i\pi}+1=0$", 12),
    (-6.5, 5, r"$\int_0^{\infty} e^{-x^2}dx = \frac{\sqrt{\pi}}{2}$", 9),
    (6.5, 5, r"$\sum_{n=0}^{\infty} \frac{1}{n!} = e$", 9),
    (-6.5, -3, r"$\nabla \times \mathbf{F}$", 10),
    (6.5, -3, r"$\zeta(2) = \frac{\pi^2}{6}$", 10),
    (-6.5, -7, r"$\Gamma(z) = \int_0^\infty t^{z-1}e^{-t}dt$", 8),
    (6.5, -7, r"$\oint \mathbf{B}\cdot d\mathbf{l} = \mu_0 I$", 8),
    (-6, 8, r"$\sqrt[n]{x}$", 8),
    (6, 8, r"$\prod_{k=1}^{n} p_k$", 8),
]
for fx, fy, txt, fs in formulas:
    ax.text(fx, fy, txt, fontsize=fs, color="#c8a040", alpha=0.25,
            ha="center", va="center", fontfamily="serif", zorder=1)

# Golden ratio triangles
for cx, cy, r in [(-6, 12, 1.5), (6, 12, 1.5), (-6, -8, 1.2), (6, -8, 1.2)]:
    tri_angles = [0, 2*np.pi/3, 4*np.pi/3]
    tri_x = [cx + r*np.cos(a) for a in tri_angles] + [cx + r*np.cos(tri_angles[0])]
    tri_y = [cy + r*np.sin(a) for a in tri_angles] + [cy + r*np.sin(tri_angles[0])]
    ax.plot(tri_x, tri_y, color="#c8a040", linewidth=0.3, alpha=0.15, zorder=1)

# ============================================================
#  TITLE
# ============================================================
ax.text(0, -10.5, "IMP. MATHEMATICUS MAXIMUS",
        fontsize=22, color="#ffd700", alpha=0.95,
        ha="center", va="center", fontweight="bold", fontfamily="serif",
        zorder=4, bbox=dict(boxstyle="round,pad=0.3", facecolor="#0a0505",
                           edgecolor="#c8a040", linewidth=0.8, alpha=0.8))

ax.text(0, -11.3, "Divus Imperator Matheseos Romae  |  AETERNITAS IN MATHEMATICA",
        fontsize=10, color="#c8a040", alpha=0.65,
        ha="center", va="center", fontstyle="italic", fontfamily="serif", zorder=4)

# ============================================================
#  SAVE
# ============================================================
out = r"C:\Users\e\Desktop\6756756756756756\emperor_mathematicus.png"
fig.savefig(out, dpi=250, bbox_inches="tight", facecolor="#080612",
            edgecolor="none", pad_inches=0.3)
plt.close(fig)
print(f"[OK] Saved: {out}")
