import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Arc

fig, axes = plt.subplots(1, 3, figsize=(18, 9), facecolor='#fdf8f0')
fig.suptitle('Фарфоровые Статуэтки Античности', fontsize=16,
             fontfamily='serif', color='#5a3e2b', y=0.97, fontstyle='italic')

for ax in axes:
    ax.set_facecolor('#fdf8f0')
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 4.5)
    ax.set_aspect('equal')
    ax.axis('off')

porcelain = '#f0e8dc'
shadow = '#d4c4b0'
blush = '#e8c0b0'
gold = '#c8a855'
gold_light = '#e8d090'
dark = '#3a2a1a'
olive_green = '#7a9a5a'
sky_blue = '#b8c8e0'
rose = '#d89090'
burgundy = '#7a3040'

t = np.linspace(0, 2*np.pi, 300)
t_side = np.linspace(0, np.pi, 200)

# ============================================================
# СТАТУЭТКА 1: АФИНА ПАЛЛАДА (богиня мудрости)
# ============================================================
ax = axes[0]

# Пьедестал — полиномиальная кривая
ped_t = np.linspace(-1.5, 1.5, 200)
ped_bot = -2.5
ped_top = -1.8
for y_off, w in [(0, 1.3), (0.15, 1.15), (0.3, 1.0)]:
    ax.fill_betweenx([ped_bot + y_off, ped_bot + y_off + 0.15],
                      -w, w, color='#e8dcd0', alpha=0.9)
    ax.plot([-w, w], [ped_bot + y_off]*2, color=shadow, linewidth=0.5)
    ax.plot([-w, w], [ped_bot + y_off + 0.15]*2, color=shadow, linewidth=0.5)

# Ноги — полиномы
leg_t = np.linspace(0, 1, 100)
# Левая нога
ll_x = -0.5 - 0.1*leg_t + 0.05*leg_t**2
ll_y = -1.35 + 0.55*leg_t - 0.6*leg_t**2
# Правая нога
rl_x = 0.5 + 0.15*leg_t - 0.08*leg_t**2
rl_y = -1.35 + 0.5*leg_t - 0.55*leg_t**2
ax.plot(ll_x, ll_y, color=porcelain, linewidth=6, solid_capstyle='round')
ax.plot(rl_x, rl_y, color=porcelain, linewidth=6, solid_capstyle='round')
ax.plot(ll_x, ll_y, color=shadow, linewidth=0.8, alpha=0.5)
ax.plot(rl_x, rl_y, color=shadow, linewidth=0.8, alpha=0.5)

# Хитон (платье) — полиномические складки
for i in range(7):
    x_off = -0.9 + i * 0.3
    fold_t = np.linspace(0, 1, 80)
    fold_x = x_off + 0.08 * np.sin(3 * np.pi * fold_t)
    fold_y = -1.35 + 0.8 * fold_t
    ax.plot(fold_x, fold_y, color=shadow, linewidth=0.6, alpha=0.4)

dress_t = np.linspace(-1, 1, 200)
dress_bot_y = -1.35
dress_top_y = 0.0
for dy in np.linspace(dress_bot_y, dress_top_y, 40):
    frac = (dy - dress_bot_y) / (dress_top_y - dress_bot_y)
    w = 0.9 - 0.35 * frac + 0.05 * np.sin(4 * np.pi * dress_t) * (1 - frac)
    ax.plot([-w, w], [dy]*2, color=porcelain, linewidth=2, alpha=0.3)

# Торс
torso_t = np.linspace(0, 1, 100)
torso_x_l = -0.35 - 0.1 * torso_t + 0.08 * torso_t**2
torso_x_r = 0.35 + 0.1 * torso_t - 0.08 * torso_t**2
torso_y = 0.0 + 0.8 * torso_t
ax.fill_betweenx(torso_y, torso_x_l, torso_x_r, color=porcelain, alpha=0.95)
ax.plot(torso_x_l, torso_y, color=shadow, linewidth=0.8, alpha=0.6)
ax.plot(torso_x_r, torso_y, color=shadow, linewidth=0.8, alpha=0.6)

# Аegis (эгида) — треугольник с полиномиальными краями
aegis_t = np.linspace(-1, 1, 100)
aegis_x = 0.0 + 0.4 * aegis_t
aegis_y = 0.2 + 0.6 * (1 - aegis_t**2)
ax.fill(aegis_x, aegis_y, color=sky_blue, alpha=0.3)
ax.plot(aegis_x, aegis_y, color=gold, linewidth=1.0)
# Змей на аэгиде
snake_t = np.linspace(0, 2*np.pi, 100)
sn_x = 0.0 + 0.15 * np.sin(3 * snake_t)
sn_y = 0.4 + 0.2 * np.cos(snake_t)
ax.plot(sn_x, sn_y, color=gold, linewidth=0.8)

# Руки
# Левая (щит)
arm_l_t = np.linspace(0, 1, 80)
arm_l_x = -0.35 - 0.3 * arm_l_t - 0.15 * arm_l_t**2
arm_l_y = 0.6 + 0.1 * arm_l_t - 0.3 * arm_l_t**2
ax.plot(arm_l_x, arm_l_y, color=porcelain, linewidth=4.5, solid_capstyle='round')
ax.plot(arm_l_x, arm_l_y, color=shadow, linewidth=0.7, alpha=0.4)

# Щит — полином окружности
shield_t = np.linspace(0, 2*np.pi, 100)
sh_x = -1.0 + 0.4 * np.cos(shield_t)
sh_y = 0.4 + 0.45 * np.sin(shield_t)
ax.fill(sh_x, sh_y, color=sky_blue, alpha=0.4)
ax.plot(sh_x, sh_y, color=gold, linewidth=1.5)
# Медуза на щите
med_t = np.linspace(0, 2*np.pi, 80)
ax.plot(-1.0 + 0.12*np.cos(med_t), 0.4 + 0.12*np.sin(med_t), color=gold, linewidth=0.8)

# Правая (копьё)
arm_r_t = np.linspace(0, 1, 80)
arm_r_x = 0.35 + 0.25 * arm_r_t
arm_r_y = 0.5 + 0.5 * arm_r_t - 0.1 * arm_r_t**2
ax.plot(arm_r_x, arm_r_y, color=porcelain, linewidth=4.5, solid_capstyle='round')

# Копьё
spear_x = [0.55, 0.7]
spear_y = [0.7, 2.8]
ax.plot(spear_x, spear_y, color=gold, linewidth=1.5)
ax.plot([0.7], [2.8], marker='^', color=gold, markersize=6)

# Шлем
helmet_t = np.linspace(0, 2*np.pi, 200)
helmet_x = 0.0 + 0.32 * np.cos(helmet_t)
helmet_y = 1.0 + 0.35 * np.sin(helmet_t)
ax.fill(helmet_x, helmet_y, color=porcelain, alpha=0.95)
ax.plot(helmet_x, helmet_y, color=shadow, linewidth=0.8)

# Гребень шлема
crest_t = np.linspace(0, np.pi, 100)
crest_x = 0.0 + 0.15 * np.sin(crest_t)
crest_y = 1.0 + 0.5 * np.cos(crest_t) + 0.1 * np.sin(2*crest_t)
ax.plot(crest_x, crest_y, color=rose, linewidth=3)

# Лицо
face_t = np.linspace(0, 2*np.pi, 100)
ax.fill(0.0 + 0.2*np.cos(face_t), 0.95 + 0.22*np.sin(face_t), color=porcelain)
# Глаза
ax.plot([-0.08, -0.04], [1.0, 1.0], color=dark, linewidth=1.5)
ax.plot([0.04, 0.08], [1.0, 1.0], color=dark, linewidth=1.5)
# Рот
mouth_t = np.linspace(0, np.pi, 30)
ax.plot(-0.06 + 0.06*np.cos(mouth_t), 0.85 + 0.02*np.sin(mouth_t), color=rose, linewidth=0.8)

ax.set_title('Афина Паллада', fontsize=11, fontfamily='serif', color='#5a3e2b', pad=10)

# ============================================================
# СТАТУЭТКА 2: АМФОРА С ВИНОГРАДНОЙ ЛОЗОЙ
# ============================================================
ax = axes[1]

# Пьедестал
for y_off, w in [(0, 1.2), (0.15, 1.05), (0.3, 0.9)]:
    ax.fill_betweenx([-2.5 + y_off, -2.5 + y_off + 0.15],
                      -w, w, color='#e8dcd0', alpha=0.9)
    ax.plot([-w, w], [-2.5 + y_off]*2, color=shadow, linewidth=0.5)
    ax.plot([-w, w], [-2.5 + y_off + 0.15]*2, color=shadow, linewidth=0.5)

# Ножка амфоры
ax.fill_betweenx([-2.0, -1.7], -0.25, 0.25, color=porcelain, alpha=0.95)

# Тело амфоры — эллипс + полиномы
amph_t = np.linspace(0, 2*np.pi, 300)
# Основная форма — комбинация эллипса и полинома
amph_r = 0.8 + 0.15 * np.cos(2*amph_t) + 0.05 * np.cos(3*amph_t)
amph_x = amph_r * np.cos(amph_t)
amph_y = -1.0 + 1.3 * np.sin(amph_t)
ax.fill(amph_x, amph_y, color=porcelain, alpha=0.95)

# Рисунок на амфоре — виноградная лоза
vine_t = np.linspace(0, 4*np.pi, 300)
vine_x = 0.4 * np.cos(vine_t) * (1 - 0.3 * vine_t / (4*np.pi))
vine_y = -0.5 + 0.15 * vine_t
ax.plot(vine_x, vine_y, color=olive_green, linewidth=1.2, alpha=0.7)

# Виноградины
grape_positions = [(0.35, 0.0), (-0.2, 0.3), (0.15, -0.1), (-0.35, 0.5), (0.3, 0.55)]
for gx, gy in grape_positions:
    gr_t = np.linspace(0, 2*np.pi, 30)
    for dx, dy in [(0, 0), (0.06, 0.04), (-0.06, 0.04), (0, 0.08)]:
        ax.fill(gx+dx+0.04*np.cos(gr_t), gy+dy+0.04*np.sin(gr_t),
                color=burgundy, alpha=0.7)

# Листья
for lx, ly, la in [(0.5, 0.2, 0.3), (-0.4, 0.6, -0.5), (0.2, -0.2, 0.8)]:
    leaf_t = np.linspace(0, 2*np.pi, 50)
    leaf_x = lx + 0.12*np.cos(leaf_t)*np.cos(la) - 0.06*np.sin(leaf_t)*np.sin(la)
    leaf_y = ly + 0.12*np.cos(leaf_t)*np.sin(la) + 0.06*np.sin(leaf_t)*np.cos(la)
    ax.fill(leaf_x, leaf_y, color=olive_green, alpha=0.6)

# Горлышко амфоры
neck_t = np.linspace(0, 1, 50)
neck_x_l = -0.25 + 0.05 * neck_t
neck_x_r = 0.25 - 0.05 * neck_t
neck_y = 0.3 + 0.7 * neck_t
ax.fill_betweenx(neck_y, neck_x_l, neck_x_r, color=porcelain, alpha=0.95)

# Ручки — полиномиальные дуги
handle_t = np.linspace(-1, 1, 100)
# Левая ручка
lh_x = -0.25 - 0.35 * (1 - handle_t**2)
lh_y = 0.5 + 0.5 * handle_t**2
ax.plot(lh_x, lh_y, color=porcelain, linewidth=4, solid_capstyle='round')
ax.plot(lh_x, lh_y, color=shadow, linewidth=0.8, alpha=0.5)
# Правая ручка
rh_x = 0.25 + 0.35 * (1 - handle_t**2)
ax.plot(rh_x, lh_y, color=porcelain, linewidth=4, solid_capstyle='round')
ax.plot(rh_x, lh_y, color=shadow, linewidth=0.8, alpha=0.5)

# Крышка/горлышко — расширение
rim_t = np.linspace(-1, 1, 100)
rim_x = 0.25 * (1 + 0.4*rim_t**2)
rim_y_bot = np.linspace(1.0, 1.0, 100)
rim_y_top = np.linspace(1.15, 1.15, 100)
ax.fill_betweenx(rim_y_bot, -rim_x, rim_x, color=porcelain, alpha=0.95)
ax.fill_betweenx(rim_y_top, -0.25, 0.25, color=porcelain, alpha=0.95)

# Золотая полоса
gold_band_t = np.linspace(0, 2*np.pi, 300)
gb_r = 0.85 + 0.15 * np.cos(2*gold_band_t) + 0.05 * np.cos(3*gold_band_t)
ax.plot(gb_r * np.cos(gold_band_t), -0.2 + 1.3 * np.sin(gold_band_t),
        color=gold, linewidth=1.5, alpha=0.7)

# Орнамент сверху и снизу
for band_y in [0.6, -0.7]:
    dot_t = np.linspace(0, 2*np.pi, 300)
    dot_r = 0.3 + 0.05 * np.cos(2*dot_t)
    for angle in np.linspace(0, 2*np.pi, 20):
        dx = 0.28 * np.cos(angle)
        dy = band_y + 0.03 * np.sin(angle)
        ax.plot(dx, dy, 'o', color=gold, markersize=1.5, alpha=0.6)

ax.set_title('Амфора Диониса', fontsize=11, fontfamily='serif', color='#5a3e2b', pad=10)

# ============================================================
# СТАТУЭТКА 3: АФРОДИТА (Венера Милосская)
# ============================================================
ax = axes[2]

# Пьедестал
for y_off, w in [(0, 1.4), (0.15, 1.25), (0.3, 1.1)]:
    ax.fill_betweenx([-2.8 + y_off, -2.8 + y_off + 0.15],
                      -w, w, color='#e8dcd0', alpha=0.9)
    ax.plot([-w, w], [-2.8 + y_off]*2, color=shadow, linewidth=0.5)
    ax.plot([-w, w], [-2.8 + y_off + 0.15]*2, color=shadow, linewidth=0.5)

# Драпировка у ног — полиномические складки
drape_t = np.linspace(-1, 1, 200)
for i in range(12):
    x_off = -0.8 + i * 0.14
    fold_y = np.linspace(-2.3, -1.0, 80)
    fold_x = x_off + 0.06 * np.sin(5 * np.pi * (fold_y + 2.3) / 1.3)
    ax.plot(fold_x, fold_y, color=shadow, linewidth=0.4, alpha=0.3)

# Тело — плавные полиномиальные кривые
# Бёдра
hip_t = np.linspace(0, 1, 150)
hip_x_l = -0.45 + 0.15 * np.sin(np.pi * hip_t)
hip_x_r = 0.45 - 0.1 * np.sin(np.pi * hip_t)
hip_y = -2.3 + 1.3 * hip_t
ax.fill_betweenx(hip_y, hip_x_l, hip_x_r, color=porcelain, alpha=0.95)
ax.plot(hip_x_l, hip_y, color=shadow, linewidth=0.6, alpha=0.5)
ax.plot(hip_x_r, hip_y, color=shadow, linewidth=0.6, alpha=0.5)

# Талия
waist_t = np.linspace(0, 1, 100)
waist_x_l = -0.3 - 0.05 * waist_t
waist_x_r = 0.3 + 0.05 * waist_t
waist_y = -1.0 + 0.6 * waist_t
ax.fill_betweenx(waist_y, waist_x_l, waist_x_r, color=porcelain, alpha=0.95)
ax.plot(waist_x_l, waist_y, color=shadow, linewidth=0.6, alpha=0.5)
ax.plot(waist_x_r, waist_y, color=shadow, linewidth=0.6, alpha=0.5)

# Грудь
chest_t = np.linspace(0, 2*np.pi, 100)
for cx, cy in [(-0.15, -0.3), (0.15, -0.3)]:
    cr = 0.12 + 0.02 * np.cos(chest_t)
    ax.fill(cx + cr*np.cos(chest_t), cy + cr*0.7*np.sin(chest_t),
            color=porcelain, alpha=0.9)
    ax.plot(cx + cr*np.cos(chest_t), cy + cr*0.7*np.sin(chest_t),
            color=shadow, linewidth=0.5, alpha=0.4)

# Плечи
for sx, sdir in [(-0.35, -1), (0.35, 1)]:
    sh_t = np.linspace(0, 1, 80)
    sh_x = sx + sdir * 0.2 * sh_t**2
    sh_y = 0.3 + 0.15 * sh_t - 0.1 * sh_t**2
    ax.plot(sh_x, sh_y, color=porcelain, linewidth=5, solid_capstyle='round')
    ax.plot(sh_x, sh_y, color=shadow, linewidth=0.6, alpha=0.4)

# Левая рука (у бедра)
arm_l_t = np.linspace(0, 1, 80)
arm_l_x = -0.55 - 0.1 * arm_l_t
arm_l_y = -0.5 - 0.5 * arm_l_t + 0.3 * arm_l_t**2
ax.plot(arm_l_x, arm_l_y, color=porcelain, linewidth=4, solid_capstyle='round')
ax.plot(arm_l_x, arm_l_y, color=shadow, linewidth=0.6, alpha=0.4)

# Правая рука (отсутствует — как у Венеры Милосской, облом)
arm_r_t = np.linspace(0, 0.6, 50)
arm_r_x = 0.55 + 0.15 * arm_r_t
arm_r_y = 0.0 - 0.3 * arm_r_t
ax.plot(arm_r_x, arm_r_y, color=porcelain, linewidth=4, solid_capstyle='round')
ax.plot(arm_r_x, arm_r_y, color=shadow, linewidth=0.6, alpha=0.4)

# Шея
neck_t = np.linspace(0, 1, 50)
neck_x_l = -0.1 - 0.03 * neck_t
neck_x_r = 0.1 + 0.03 * neck_t
neck_y = 0.4 + 0.3 * neck_t
ax.fill_betweenx(neck_y, neck_x_l, neck_x_r, color=porcelain, alpha=0.95)

# Голова
head_t = np.linspace(0, 2*np.pi, 200)
head_x = 0.0 + 0.25 * np.cos(head_t)
head_y = 0.85 + 0.28 * np.sin(head_t)
ax.fill(head_x, head_y, color=porcelain, alpha=0.95)
ax.plot(head_x, head_y, color=shadow, linewidth=0.8)

# Волосы — полиномиальные спирали
hair_t = np.linspace(0, 3*np.pi, 200)
for side, sign in [('l', -1), ('r', 1)]:
    h_x = sign * 0.15 + 0.2 * np.cos(hair_t) * np.exp(-0.08 * hair_t)
    h_y = 1.1 + 0.3 * np.sin(hair_t) * np.exp(-0.08 * hair_t) - 0.03 * hair_t
    ax.plot(h_x, h_y, color='#8a6a4a', linewidth=1.5, alpha=0.6)

# Чёлка
bang_t = np.linspace(0, np.pi, 50)
ax.plot(-0.2 + 0.35*np.cos(bang_t), 1.1 + 0.08*np.sin(bang_t),
        color='#8a6a4a', linewidth=2, alpha=0.5)

# Лицо
face_detail_t = np.linspace(0, 2*np.pi, 100)
ax.fill(0.0 + 0.17*np.cos(face_detail_t), 0.88 + 0.18*np.sin(face_detail_t),
        color=porcelain, alpha=0.95)

# Глаза
eye_t = np.linspace(0, 2*np.pi, 30)
for ex in [-0.08, 0.08]:
    ax.fill(ex + 0.04*np.cos(eye_t), 0.92 + 0.025*np.sin(eye_t),
            color='white', alpha=0.9)
    ax.plot(ex + 0.04*np.cos(eye_t), 0.92 + 0.025*np.sin(eye_t),
            color=dark, linewidth=0.5)
    ax.plot(ex, 0.92, 'o', color=dark, markersize=2)

# Нос
ax.plot([0.0, 0.02], [0.92, 0.85], color=shadow, linewidth=0.8, alpha=0.5)

# Рот
mouth_t2 = np.linspace(0, np.pi, 30)
ax.plot(-0.05 + 0.05*np.cos(mouth_t2), 0.79 + 0.015*np.sin(mouth_t2),
        color=rose, linewidth=1.0)

# Драпировка на левом плече
drape_sh_t = np.linspace(0, 1, 100)
drape_sh_x = -0.35 - 0.3 * drape_sh_t + 0.1 * drape_sh_t**2
drape_sh_y = 0.2 - 0.1 * drape_sh_t - 0.2 * drape_sh_t**2
ax.plot(drape_sh_x, drape_sh_y, color='#e0d8d0', linewidth=3, alpha=0.6)

ax.set_title('Афродита', fontsize=11, fontfamily='serif', color='#5a3e2b', pad=10)

# ============================================================
# Подписи полиномов
# ============================================================
formula_text = (
    "Полиномы:  y = a₀ + a₁x + a₂x² + a₃x³ + ...\n"
    "Параметрические:  x(t) = Σaᵢtⁱ,  y(t) = Σbᵢtⁱ\n"
    "Суперпозиция:  r(θ) = Σ Aₙcos(nθ + φₙ)"
)
fig.text(0.5, 0.02, formula_text, ha='center', va='bottom',
         fontsize=9, fontfamily='serif', color='#8a7a6a', fontstyle='italic')

plt.tight_layout(rect=[0, 0.06, 1, 0.94])
plt.savefig('porcelain_figurines.png', dpi=200, bbox_inches='tight', facecolor='#fdf8f0')
print("Сохранено: porcelain_figurines.png")
