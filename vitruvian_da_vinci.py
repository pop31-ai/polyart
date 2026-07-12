import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Arc, FancyBboxPatch
import matplotlib.colors as mcolors

fig, axes = plt.subplots(1, 3, figsize=(20, 12), facecolor='#f5efe0')
fig.suptitle('Человек по Линиям Да Винчи: Математический Витрувианец',
             fontsize=15, fontfamily='serif', color='#2a1a0a', y=0.97, fontstyle='italic')

phi = (1 + np.sqrt(5)) / 2
phi_inv = 1 / phi

skin = '#e0c8a8'
skin_shadow = '#c8a888'
skin_deep = '#b09878'
skin_light = '#f0dcc8'
dark = '#1a1008'
cloth_blue = '#3a5a8a'
cloth_blue_l = '#5a7aaa'
cloth_blue_d = '#2a4060'
cloth_red = '#8a3030'
cloth_red_l = '#aa5050'
cloth_gold = '#c8a040'
line_da_vinci = '#6a4a2a'
parchment = '#f0e8d8'

# ============================================================
# ПАНЕЛЬ 1: ВИТРУВИАНСКИЙ ЧЕЛОВЕК — пропорции по Да Винчи
# ============================================================
ax = axes[0]
ax.set_facecolor(parchment)
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-3.5, 4)
ax.set_aspect('equal')
ax.axis('off')

# Пропорции Витрувиана:
# Высота тела = 8 голов
# Голова = 1 единица
# Пупек = центр окружности
head_h = 0.8  # высота головы
body_h = 8 * head_h  # 6.4

# Круг и квадрат (как у Да Винчи)
circle_r = body_h / 2  # 3.2
circle_t = np.linspace(0, 2*np.pi, 300)
ax.plot(circle_r * np.cos(circle_t), circle_r * np.sin(circle_t) - 0.2,
        color=line_da_vinci, linewidth=1.5, linestyle='--', alpha=0.6)

sq = body_h / 2
ax.plot([-sq, sq, sq, -sq, -sq],
        [-sq-0.2, -sq-0.2, sq-0.2, sq-0.2, -sq-0.2],
        color=line_da_vinci, linewidth=1.5, linestyle='--', alpha=0.6)

# Центр = пупок
ax.plot(0, 0, 'o', color=dark, markersize=3)
ax.text(0.15, 0, 'пупок = центр', fontsize=6, color=line_da_vinci, fontstyle='italic')

# ===== ЧЕЛОВЕК — стоя с раскинутыми руками (как Витрувиан) =====
# Голова
head_cy = 3.0  # центр головы
head_t = np.linspace(0, 2*np.pi, 200)
hx = 0.35 * np.cos(head_t)
hy = head_cy + 0.4 * np.sin(head_t)
ax.fill(hx, hy, color=skin, alpha=0.9)
ax.plot(hx, hy, color=skin_shadow, linewidth=1)

# Глаза
for ex in [-0.12, 0.12]:
    ax.plot(ex, head_cy + 0.05, 'o', color=dark, markersize=2)

# Брови
for bx in [-0.12, 0.12]:
    bt = np.linspace(-1, 1, 30)
    ax.plot(bx + 0.08*bt, head_cy + 0.15 - 0.02*bt**2, color=dark, linewidth=1.2)

# Нос
ax.plot([0, 0.02], [head_cy, head_cy - 0.1], color=skin_shadow, linewidth=0.8)

# Рот
mt3 = np.linspace(-1, 1, 30)
ax.plot(0.1*mt3, np.full_like(mt3, head_cy - 0.2), color='#b06050', linewidth=0.8)

# Причёска
hair_t = np.linspace(0, np.pi, 100)
ax.fill(0.38*np.cos(hair_t), head_cy + 0.35 + 0.15*np.sin(hair_t),
        color='#4a3a1a', alpha=0.7)

# Шея
ax.plot([0, 0], [head_cy - 0.4, head_cy - 0.55], color=skin_shadow, linewidth=2)
ax.plot([0, 0], [head_cy - 0.4, head_cy - 0.55], color=skin, linewidth=4)

# Торс — полиномический контур
torso_t = np.linspace(0, 1, 200)
# Левая сторона
tl_x = -0.3 - 0.15 * torso_t + 0.1 * torso_t**2 + 0.05 * np.sin(np.pi * torso_t)
tl_y = 2.4 - 2.2 * torso_t
# Правая сторона
tr_x = 0.3 + 0.15 * torso_t - 0.1 * torso_t**2 - 0.05 * np.sin(np.pi * torso_t)
tr_y = tl_y

# Заливка торса
ax.fill_betweenx(tl_y, tl_x, tr_x, color=skin, alpha=0.85)

# Линия позвоночника — S-образная кривая Да Винчи
spine_t = np.linspace(0, 1, 100)
spine_x = 0.03 * np.sin(3 * np.pi * spine_t)
spine_y = 2.4 - 2.2 * spine_t
ax.plot(spine_x, spine_y, color=line_da_vinci, linewidth=0.8, linestyle='--', alpha=0.4)

# Плечи
for side in [-1, 1]:
    shoulder_t = np.linspace(0, 1, 80)
    sh_x = side * (0.3 + 0.5 * shoulder_t)
    sh_y = 2.3 - 0.1 * np.sin(np.pi * shoulder_t)
    ax.plot(sh_x, sh_y, color=skin_shadow, linewidth=1)

# Руки — вытянуты в стороны (как Витрувиан)
for side in [-1, 1]:
    # Плечо
    arm_upper_t = np.linspace(0, 1, 80)
    au_x = side * (0.8 + 1.2 * arm_upper_t)
    au_y = 2.2 - 0.3 * arm_upper_t
    ax.plot(au_x, au_y, color=skin, linewidth=5, solid_capstyle='round')
    ax.plot(au_x, au_y, color=skin_shadow, linewidth=1, alpha=0.4)
    
    # Предплечье
    arm_lower_t = np.linspace(0, 1, 80)
    al_x = side * (2.0 + 0.6 * arm_lower_t)
    al_y = 1.9 - 0.4 * arm_lower_t
    ax.plot(al_x, al_y, color=skin, linewidth=4.5, solid_capstyle='round')
    ax.plot(al_x, al_y, color=skin_shadow, linewidth=1, alpha=0.4)
    
    # Кисть
    hand_t = np.linspace(0, 2*np.pi, 50)
    ax.fill(side * 2.65 + 0.12*np.cos(hand_t), 1.5 + 0.1*np.sin(hand_t),
            color=skin, alpha=0.9)

# Ноги
for side in [-1, 1]:
    # Бедро
    leg_upper_t = np.linspace(0, 1, 80)
    lu_x = side * (0.15 + 0.05 * side * leg_upper_t)
    lu_y = 0.2 - 1.3 * leg_upper_t
    ax.plot(lu_x, lu_y, color=skin, linewidth=6, solid_capstyle='round')
    ax.plot(lu_x, lu_y, color=skin_shadow, linewidth=1, alpha=0.4)
    
    # Голень
    leg_lower_t = np.linspace(0, 1, 80)
    ll_x = side * (0.2 + 0.02 * side * leg_lower_t)
    ll_y = -1.1 - 1.2 * leg_lower_t
    ax.plot(ll_x, ll_y, color=skin, linewidth=5, solid_capstyle='round')
    ax.plot(ll_x, ll_y, color=skin_shadow, linewidth=1, alpha=0.4)
    
    # Стопа
    foot_t = np.linspace(-1, 1, 50)
    ax.fill(side * 0.22 + 0.15 * foot_t, -2.35 - 0.04 * (1 - foot_t**2),
            color=skin, alpha=0.9)

# Линии пропорций — деление по Да Винчи
dividers = [
    (2.6, 'линия бровей'),
    (2.2, 'линия подбородка'),
    (1.1, 'линия сосков'),
    (0.0, 'пупек'),
    (-1.1, 'линия бёдер'),
    (-2.3, 'линия стоп'),
]
for dy, label in dividers:
    ax.axhline(dy, color=line_da_vinci, linewidth=0.5, linestyle=':', alpha=0.4)
    ax.text(2.2, dy, label, fontsize=5.5, color=line_da_vinci, fontstyle='italic', va='center')

ax.set_title('Витрувианский Человек\nПропорции: 8 голов, φ, √2',
             fontsize=9, fontfamily='serif', color='#2a1a0a', pad=8)


# ============================================================
# ПАНЕЛЬ 2: СФУМАТО И МУСКУЛАТУРА — анатомия по полиномам
# ============================================================
ax = axes[1]
ax.set_facecolor(parchment)
ax.set_xlim(-2, 2)
ax.set_ylim(-3.5, 4)
ax.set_aspect('equal')
ax.axis('off')

# Профиль (как в анатомических чертежах Да Винчи)
# Контур — полиномический сплайн
profile_x = np.array([
    -0.05, -0.08, -0.12, -0.10, -0.06, -0.02,
    0.0, 0.05, 0.12, 0.18, 0.22, 0.20,
    0.15, 0.12, 0.15, 0.18, 0.22, 0.20,
    0.15, 0.08, 0.0, -0.08, -0.15
])
profile_y = np.array([
    3.2, 2.9, 2.6, 2.4, 2.2, 2.0,
    1.8, 1.6, 1.5, 1.45, 1.3, 1.1,
    0.9, 0.7, 0.5, 0.3, 0.1, -0.1,
    -0.3, -0.5, -0.7, -0.9, -1.1
])

# Сглаживание сплайном
from scipy.interpolate import make_interp_spline
try:
    t_smooth = np.linspace(0, 1, len(profile_x))
    t_fine = np.linspace(0, 1, 300)
    spl_x = make_interp_spline(t_smooth, profile_x, k=3)
    spl_y = make_interp_spline(t_smooth, profile_y, k=3)
    px = spl_x(t_fine)
    py = spl_y(t_fine)
except:
    px = profile_x
    py = profile_y

# Заливка тела
body_fill_x = np.concatenate([px, px[::-1]])
body_fill_y = np.concatenate([py, py[::-1] - np.linspace(0, 0.5, len(py))])
ax.fill(body_fill_x - 0.5, body_fill_y, color=skin, alpha=0.8)

# Контуры — линии Да Винчи (перо и тушь)
ax.plot(px - 0.5, py, color=line_da_vinci, linewidth=1.5)

# Мышцы — полиномические дуги
# Дельтовидная
delt_t = np.linspace(0, np.pi, 80)
delt_x = -0.7 + 0.3 * np.cos(delt_t)
delt_y = 1.8 + 0.15 * np.sin(delt_t)
ax.plot(delt_x, delt_y, color=line_da_vinci, linewidth=1.0, alpha=0.5)

# Бицепс
bicep_t = np.linspace(0, 1, 80)
bicep_x = -0.95 - 0.08 * np.sin(np.pi * bicep_t)
bicep_y = 1.7 - 0.6 * bicep_t
ax.plot(bicep_x, bicep_y, color=line_da_vinci, linewidth=0.8, alpha=0.4)

# Трицепс
tricep_x = -0.85 + 0.06 * np.sin(np.pi * bicep_t)
tricep_y = 1.7 - 0.6 * bicep_t
ax.plot(tricep_x, tricep_y, color=line_da_vinci, linewidth=0.8, alpha=0.4)

# Грудная мышца
pec_t = np.linspace(0, 1, 80)
pec_x = -0.5 + 0.25 * pec_t
pec_y = 1.3 + 0.1 * np.sin(np.pi * pec_t)
ax.plot(pec_x, pec_y, color=line_da_vinci, linewidth=1.0, alpha=0.5)

# Пресс — полиномические сегменты
for i in range(6):
    ab_y = 0.8 - 0.15 * i
    ab_t = np.linspace(-0.15, 0.15, 40)
    ax.plot(ab_t, ab_y + 0.02 * np.cos(np.pi * ab_t / 0.15),
            color=line_da_vinci, linewidth=0.6, alpha=0.35)

# Коленная чашечка
knee_t = np.linspace(0, 2*np.pi, 50)
ax.plot(-0.7 + 0.08*np.cos(knee_t), -1.3 + 0.06*np.sin(knee_t),
        color=line_da_vinci, linewidth=0.8, alpha=0.4)

# Сухожилия голени
for side_s in [-0.65, -0.55]:
    calf_t = np.linspace(0, 1, 60)
    cx = side_s + 0.05 * np.sin(np.pi * calf_t)
    cy = -1.5 - 0.7 * calf_t
    ax.plot(cx, cy, color=line_da_vinci, linewidth=0.7, alpha=0.35)

# Стрелки и подписи (как у Да Винчи — зеркальным письмом)
ax.annotate('', xy=(-0.5, 1.8), xytext=(-0.5, 1.3),
            arrowprops=dict(arrowstyle='<->', color=line_da_vinci, lw=0.8))
ax.text(-0.85, 1.55, 'дельта', fontsize=5.5, color=line_da_vinci, fontstyle='italic', rotation=90)

ax.annotate('', xy=(-0.95, 1.7), xytext=(-0.95, 1.1),
            arrowprops=dict(arrowstyle='<->', color=line_da_vinci, lw=0.8))
ax.text(-1.15, 1.4, 'бицепс', fontsize=5.5, color=line_da_vinci, fontstyle='italic', rotation=90)

ax.annotate('', xy=(-0.15, 0.8), xytext=(-0.15, -0.1),
            arrowprops=dict(arrowstyle='<->', color=line_da_vinci, lw=0.8))
ax.text(0.05, 0.35, 'прямая\nмышца\nживота', fontsize=5.5, color=line_da_vinci, fontstyle='italic')

ax.set_title('Анатомия: Сфумато\nМышцы = полиномические дуги',
             fontsize=9, fontfamily='serif', color='#2a1a0a', pad=8)


# ============================================================
# ПАНЕЛЬ 3: ЧЕЛОВЕК В ОДЕЖДЕ — драпировка по полиномам
# ============================================================
ax = axes[2]
ax.set_facecolor(parchment)
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-3.5, 4)
ax.set_aspect('equal')
ax.axis('off')

# Голова
head_t = np.linspace(0, 2*np.pi, 200)
ax.fill(0.35*np.cos(head_t), 3.0 + 0.4*np.sin(head_t), color=skin, alpha=0.9)
ax.plot(0.35*np.cos(head_t), 3.0 + 0.4*np.sin(head_t), color=skin_shadow, linewidth=1)

# Лицо
for ex in [-0.12, 0.12]:
    ax.plot(ex, 3.05, 'o', color=dark, markersize=2)
mt4 = np.linspace(-1, 1, 30)
ax.plot(0.1*mt4, np.full_like(mt4, 2.82), color='#b06050', linewidth=0.8)

# Причёска
ax.fill(0.38*np.cos(np.linspace(0, np.pi, 100)),
        3.35 + 0.15*np.sin(np.linspace(0, np.pi, 100)),
        color='#4a3a1a', alpha=0.7)

# Шея
ax.fill_betweenx([2.5, 2.6], -0.08, 0.08, color=skin, alpha=0.9)

# ===== ТУНИКА / ХИТОН — драпировка по полиномам =====
# Основная форма тела
tunic_t = np.linspace(0, 1, 300)

# Левый край ткани
tunic_l_x = -0.35 - 0.3 * tunic_t - 0.05 * np.sin(4*np.pi*tunic_t)
tunic_l_y = 2.5 - 4.5 * tunic_t

# Правый край ткани
tunic_r_x = 0.35 + 0.3 * tunic_t + 0.05 * np.sin(4*np.pi*tunic_t)
tunic_r_y = tunic_l_y

# Заливка ткани
ax.fill_betweenx(tunic_l_y, tunic_l_x, tunic_r_x,
                  color=cloth_blue, alpha=0.85)

# Складки ткани — кривые тяжести (катenary)
for i in range(10):
    fold_x_offset = -0.5 + i * 0.1
    fold_t = np.linspace(0, 1, 150)
    
    # Катenary: y = a*cosh(x/a) —.curve of hanging fabric
    # В.parametric form для складки:
    fold_x = fold_x_offset + 0.08 * np.sin(3 * np.pi * fold_t + i * 0.7)
    fold_y = 2.5 - 4.5 * fold_t
    
    # Глубина складки зависит от расстояния от центра
    depth = 0.3 + 0.1 * abs(fold_x_offset)
    alpha_fold = 0.3 + 0.15 * (1 - abs(fold_x_offset) / 0.5)
    
    ax.plot(fold_x, fold_y, color=cloth_blue_d, linewidth=0.8, alpha=alpha_fold)

# Пояс на талии — золотой
belt_t = np.linspace(-1, 1, 100)
belt_y_base = 0.8
belt_x = 0.45 * belt_t + 0.03 * np.sin(5 * np.pi * belt_t)
belt_y = belt_y_base + 0.03 * np.cos(np.pi * belt_t)
ax.plot(belt_x, belt_y, color=cloth_gold, linewidth=3)
ax.plot(belt_x, belt_y - 0.06, color=cloth_gold, linewidth=3)
# Узел пояса
knot_t = np.linspace(0, 2*np.pi, 30)
ax.fill(0.05 + 0.06*np.cos(knot_t), belt_y_base + 0.03 + 0.06*np.sin(knot_t),
        color=cloth_gold, alpha=0.9)
# Свободные концы пояса
for ks in [-1, 1]:
    end_t = np.linspace(0, 1, 50)
    ex = ks * 0.05 + ks * 0.15 * end_t**1.5
    ey = belt_y_base - 0.06 - 0.5 * end_t - 0.1 * end_t**2
    ax.plot(ex, ey, color=cloth_gold, linewidth=2)

# Плечевая накидка (палиум) — катenary-драпировка
# Через левое плечо
pallium_t = np.linspace(0, 1, 200)
# От левого плеча через спину к правому бедру
pallium_x = -0.6 + 1.2 * pallium_t + 0.15 * np.sin(3*np.pi*pallium_t)
pallium_y = 2.0 - 2.5 * pallium_t + 0.3 * np.sin(2*np.pi*pallium_t)
ax.plot(pallium_x, pallium_y, color=cloth_blue_d, linewidth=1.5, alpha=0.7)

# Катenary-драпировка палиума
for pi in range(6):
    poff = (pi - 3) * 0.08
    pcat_t = np.linspace(0, 1, 200)
    pc_x = pallium_x + poff * np.cos(np.pi * pcat_t)
    pc_y = pallium_y + poff * np.sin(np.pi * pcat_t) * 0.3
    ax.plot(pc_x, pc_y, color=cloth_blue_d, linewidth=0.6, alpha=0.3)

# ===== РУКИ В ТКАНИ =====
for side in [-1, 1]:
    # Рука
    arm_t = np.linspace(0, 1, 80)
    arm_x = side * (0.5 + 0.8 * arm_t)
    arm_y = 1.8 - 0.1 * arm_t - 0.3 * arm_t**2
    ax.plot(arm_x, arm_y, color=skin, linewidth=4, solid_capstyle='round')
    ax.plot(arm_x, arm_y, color=skin_shadow, linewidth=0.8, alpha=0.4)
    
    # Кисть
    hand_t = np.linspace(0, 2*np.pi, 30)
    ax.fill(side*1.3 + 0.1*np.cos(hand_t), 1.35 + 0.08*np.sin(hand_t),
            color=skin, alpha=0.9)
    
    # Ткань на предплечье — лёгкие складки
    sleeve_t = np.linspace(0, 0.4, 60)
    sleeve_x = side * (0.5 + 0.8 * sleeve_t)
    sleeve_y = 1.8 - 0.1 * sleeve_t - 0.3 * sleeve_t**2
    for si in range(3):
        s_off = (si - 1) * 0.04
        ax.plot(sleeve_x + s_off * np.sin(5*np.pi*sleeve_t),
                sleeve_y + s_off * np.cos(5*np.pi*sleeve_t),
                color=cloth_blue_l, linewidth=0.6, alpha=0.35)

# ===== НОГИ В ТКАНИ =====
for side in [-1, 1]:
    # Нога сквозь ткань — контур
    leg_t = np.linspace(0, 1, 200)
    leg_x = side * (0.15 + 0.05 * side * leg_t) + 0.04 * np.sin(4*np.pi*leg_t)
    leg_y = -1.5 - 1.5 * leg_t
    
    # Ткань обтекает ногу — касательные складки
    for li in range(4):
        l_off = (li - 1.5) * 0.06
        leg_fold_x = leg_x + l_off * (1 + 0.3*leg_t) * np.sin(np.pi*leg_t*2 + li)
        ax.plot(leg_fold_x, leg_y, color=cloth_blue_l, linewidth=0.6, alpha=0.35)
    
    # Контуры ноги под тканью
    leg_contour_l = leg_x - 0.15 * (1 - 0.3*leg_t)
    leg_contour_r = leg_x + 0.15 * (1 - 0.3*leg_t)
    ax.plot(leg_contour_l, leg_y, color=skin_shadow, linewidth=0.8, alpha=0.3)
    ax.plot(leg_contour_r, leg_y, color=skin_shadow, linewidth=0.8, alpha=0.3)
    
    # Стопа
    foot_t = np.linspace(-1, 1, 30)
    ax.fill(side*0.22 + 0.15*foot_t, -3.05 - 0.04*(1-foot_t**2),
            color=skin, alpha=0.9)

# Нижний край тоги — волнистый (гравитация)
hem_t = np.linspace(-1, 1, 200)
hem_x = hem_t * 0.85
hem_y = -2.0 + 0.08 * np.sin(8 * np.pi * hem_t)
ax.plot(hem_x, hem_y, color=cloth_blue_d, linewidth=1.5)

# Катenary по краю тоги
for hi in range(4):
    hoff = hi * 0.03
    hcat_x = hem_x + hoff * np.cos(8*np.pi*hem_t)
    hcat_y = hem_y - hoff - 0.02 * np.sin(8*np.pi*hem_t)
    ax.plot(hcat_x, hcat_y, color=cloth_blue_d, linewidth=0.6, alpha=0.3 - hi*0.05)

# ===== ФОРМУЛЫ ДРАПИРОВКИ =====
formulas = [
    ("Катenary: y = a·cosh(x/a)", -2.0, -2.5),
    ("Складка: x(t) = x₀ + A·sin(nπt+φ)", -2.0, -2.7),
    ("Драпировка: F = -ρg·dl/ds", -2.0, -2.9),
]
for text, fx, fy in formulas:
    ax.text(fx, fy, text, fontsize=6, fontfamily='serif', color=line_da_vinci, fontstyle='italic')

ax.set_title('Одежда: Драпировка\nКатenary и полиномы складок',
             fontsize=9, fontfamily='serif', color='#2a1a0a', pad=8)

# Подпись внизу
fig.text(0.5, 0.01,
         'Da Vinci Lines: Sfumato (α-градиенты) | Катenary драпировки y=a·cosh(x/a) | '
         'Пропорции φ | Полиномические мышцы | Сплайны контуров',
         ha='center', fontsize=7, fontfamily='serif', color='#8a6a4a', fontstyle='italic')

plt.tight_layout(rect=[0, 0.03, 1, 0.93])
plt.savefig('vitruvian_da_vinci.png', dpi=200, bbox_inches='tight', facecolor='#f5efe0')
print("Сохранено: vitruvian_da_vinci.png")
