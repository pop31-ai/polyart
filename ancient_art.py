import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
import matplotlib.patches as mpatches

fig, ax = plt.subplots(1, 1, figsize=(14, 10), facecolor='#f5e6c8')
ax.set_facecolor('#f5e6c8')
ax.set_xlim(-2, 22)
ax.set_ylim(-1, 16)
ax.set_aspect('equal')
ax.axis('off')

# --- Sky gradient ---
sky_x = np.linspace(-2, 22, 300)
sky_y = np.linspace(8, 16, 100)
SX, SY = np.meshgrid(sky_x, sky_y)
colors_sky = plt.cm.Blues_r(np.linspace(0.15, 0.55, 100))
for i in range(99):
    ax.axhspan(SY[i,0], SY[i+1,0], color=colors_sky[i], alpha=0.7)

# --- Ground ---
ground_y = np.linspace(-1, 4, 50)
for i in range(49):
    c = plt.cm.YlOrBr(np.linspace(0.5, 0.7, 50))
    ax.axhspan(ground_y[i], ground_y[i+1], color=c[i], alpha=0.8)

# --- Sun (полином круга) ---
theta = np.linspace(0, 2*np.pi, 200)
sun_r = 1.2
sun_x = 18 + sun_r * np.cos(theta)
sun_y = 13.5 + sun_r * np.sin(theta)
ax.fill(sun_x, sun_y, color='#FFD700', alpha=0.9)
for r in np.linspace(0.3, 2.0, 8):
    ax.plot(18 + r*np.cos(theta), 13.5 + r*np.sin(theta),
            color='#FFD700', alpha=0.15, linewidth=2)

# --- Parthenon columns (полиномиальные кривые) ---
def draw_column(ax, x, y_base, width, height, n_flutes=6):
    t = np.linspace(0, 1, 200)
    profile = t + 0.03 * np.sin(np.pi * t)
    
    left_x = x - width/2 * (1 - 0.15*profile)
    right_x = x + width/2 * (1 - 0.15*profile)
    col_y = y_base + height * profile
    
    ax.fill_between(col_y, left_x, right_x, color='#e8dcc8', alpha=0.95)
    ax.plot(col_y, left_x, color='#b8a88a', linewidth=0.5)
    ax.plot(col_y, right_x, color='#b8a88a', linewidth=0.5)
    
    for f in range(n_flutes):
        frac = (f + 0.5) / n_flutes
        fx = x + width * 0.35 * (frac - 0.5) * (1 - 0.15*profile)
        ax.plot(col_y, fx, color='#c8b89a', linewidth=0.4, alpha=0.6)
    
    cap_t = np.linspace(-1, 1, 50)
    cap_x = x + width * 0.8 * (1 + 0.3*cap_t**2 - 0.1*cap_t**4)
    cap_y_bot = y_base + height
    cap_y = cap_y_bot + 0.3 + 0.2 * np.cos(np.pi * cap_t)
    ax.fill_betweenx(cap_x, cap_y_bot, cap_y, color='#e8dcc8', alpha=0.95)
    
    base_t = np.linspace(-1, 1, 50)
    base_x = x + width * 0.7 * (1 + 0.2*base_t**2)
    base_y = y_base + 0.3 * np.cos(np.pi * base_t)
    ax.fill_betweenx(base_x, y_base - 0.1, base_y, color='#e8dcc8', alpha=0.95)

col_positions = [2, 4, 6, 8, 10, 12, 14, 16, 18]
for cx in col_positions:
    draw_column(ax, cx, 2.5, 0.6, 7.5)

# --- Антаблемент ---
rect = FancyBboxPatch((1.3, 10), 17.4, 0.5, boxstyle="round,pad=0.05",
                        facecolor='#e8dcc8', edgecolor='#b8a88a', linewidth=1)
ax.add_patch(rect)

# Фриз с меандром
meander_y = 10.5
meander_h = 0.4
meander_x = np.arange(1.5, 18.5, 0.6)
for i, mx in enumerate(meander_x):
    if i % 2 == 0:
        ax.plot([mx, mx+0.3, mx+0.3, mx+0.6, mx+0.6],
                [meander_y, meander_y, meander_y+meander_h, meander_y+meander_h, meander_y],
                color='#8B7355', linewidth=1.2)

# Карниз
rect2 = FancyBboxPatch((1.1, 10.9), 17.8, 0.6, boxstyle="round,pad=0.05",
                         facecolor='#e8dcc8', edgecolor='#b8a88a', linewidth=1)
ax.add_patch(rect2)

# --- Фронтон (полином 2-й степени) ---
fronton_x = np.linspace(1.0, 18.0, 200)
fronton_y_top = 11.5 + 2.5 - 2.5 * ((fronton_x - 9.5) / 8.5)**2
fronton_y_bot = np.full_like(fronton_x, 11.5)
ax.fill_between(fronton_x, fronton_y_bot, fronton_y_top, color='#e8dcc8', alpha=0.95)
ax.plot(fronton_x, fronton_y_top, color='#8B7355', linewidth=2)

# Лавровый венок в тимпане
t_laur = np.linspace(0, 2*np.pi, 300)
for offset in [-0.3, 0, 0.3]:
    r_wreath = 1.0 + 0.15 * np.sin(8 * t_laur)
    wx = 9.5 + r_wreath * np.cos(t_laur) * 0.8 + offset
    wy = 12.8 + r_wreath * np.sin(t_laur) * 0.5
    ax.plot(wx, wy, color='#5a7a3a', linewidth=1.5, alpha=0.7)

# --- Ступени ---
for step in range(5):
    sy = 2.5 - step * 0.35
    sx_l = 1.0 - step * 0.2
    sx_r = 19.0 + step * 0.2
    ax.fill_between([sx_l, sx_r], sy - 0.35, sy, color='#d4c4a8', alpha=0.8)
    ax.plot([sx_l, sx_r], [sy, sy], color='#b8a88a', linewidth=0.5)

# --- Оливковое дерево ---
def olive_branch(ax, x0, y0, angle, length, depth, width):
    if depth == 0 or length < 0.1:
        return
    dx = length * np.cos(angle)
    dy = length * np.sin(angle)
    ax.plot([x0, x0+dx], [y0, y0+dy], color='#5a4a3a', linewidth=width, solid_capstyle='round')
    if depth <= 2:
        leaf_t = np.linspace(0, 2*np.pi, 30)
        for lfrac in [0.3, 0.6, 0.9]:
            lx = x0 + dx*lfrac
            ly = y0 + dy*lfrac
            leaf_x = lx + 0.15 * np.cos(leaf_t) * np.cos(angle+0.5) - 0.08 * np.sin(leaf_t) * np.sin(angle+0.5)
            leaf_y = ly + 0.15 * np.cos(leaf_t) * np.sin(angle+0.5) + 0.08 * np.sin(leaf_t) * np.cos(angle+0.5)
            ax.fill(leaf_x, leaf_y, color='#6a8a4a', alpha=0.7)
    
    olive_branch(ax, x0+dx, y0+dy, angle+0.5, length*0.65, depth-1, width*0.7)
    olive_branch(ax, x0+dx, y0+dy, angle-0.4, length*0.7, depth-1, width*0.7)
    if depth > 2:
        olive_branch(ax, x0+dx*0.5, y0+dy*0.5, angle+0.2, length*0.4, depth-1, width*0.5)

olive_branch(ax, -0.5, 5, 1.3, 2.5, 5, 2.5)

# --- Горы (полиномы высшей степени) ---
mount_x = np.linspace(-2, 22, 500)
mount1 = 8.5 + 2.5*((mount_x-5)/6)**2 * np.exp(-((mount_x-5)/4)**2)
mount2 = 9.0 + 3.0*((mount_x-15)/5)**2 * np.exp(-((mount_x-15)/3.5)**2)
mount3 = 8.0 + 1.8*((mount_x-0)/4)**2 * np.exp(-((mount_x-0)/3)**2)
mount_y = np.minimum(np.minimum(mount1, mount2), mount3)
ax.fill_between(mount_x, 8, mount_y, color='#c8b090', alpha=0.4)

# --- Облака ---
def draw_cloud(ax, cx, cy, scale):
    t_c = np.linspace(0, 2*np.pi, 100)
    for dx, dy, r in [(-0.5, 0, 0.6), (0.3, 0.1, 0.5), (0.9, -0.05, 0.55), (-0.1, 0.15, 0.45)]:
        cx_p = cx + dx*scale
        cy_p = cy + dy*scale
        rx = r * scale
        ry = r * scale * 0.5
        ax.fill(cx_p + rx*np.cos(t_c), cy_p + ry*np.sin(t_c), 
                color='white', alpha=0.6)

draw_cloud(ax, 5, 14, 1.5)
draw_cloud(ax, 12, 14.5, 1.2)
draw_cloud(ax, 3, 13, 0.8)

# --- Надпись ---
ax.text(9.5, 0.5, 'ΠΑΡΘΕΝΩΝ  ·  AETERNA GLORIA ROMAE', 
        fontsize=11, ha='center', va='center',
        fontfamily='serif', color='#6B4226',
        fontstyle='italic', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#f5e6c8', edgecolor='#8B7355', alpha=0.8))

# Рамка
for i, lw in enumerate([3, 1.5, 0.5]):
    offset = i * 0.15
    rect_border = plt.Rectangle((-2+offset, -1+offset), 24-2*offset, 17-2*offset,
                                 fill=False, edgecolor='#8B7355', linewidth=lw, alpha=0.6-i*0.15)
    ax.add_patch(rect_border)

plt.tight_layout()
plt.savefig('parthenon_art.png', dpi=200, bbox_inches='tight', facecolor='#f5e6c8')
print("Картина сохранена как parthenon_art.png")
