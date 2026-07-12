import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Arc
from matplotlib.path import Path
import matplotlib.patches as mpatches

fig, ax = plt.subplots(1, 1, figsize=(11, 14), facecolor='#f5efe0')
ax.set_facecolor('#f5efe0')
ax.set_xlim(-4, 4)
ax.set_ylim(-6, 7)
ax.set_aspect('equal')
ax.axis('off')

phi = (1 + np.sqrt(5)) / 2

skin = '#e0c8a8'
skin_shadow = '#c8a888'
skin_mid = '#d8b898'
skin_cheek = '#d8a890'
skin_light = '#f0dcc8'
hair_dark = '#3a2a18'
hair_mid = '#5a4028'
eye_color = '#4a6878'
lip_color = '#b86858'
lip_shadow = '#a05848'
brow_color = '#3a2818'
dark = '#1a1008'
gold = '#c8a040'
gold_dark = '#8a6820'
toga_white = '#ede8de'
toga_shadow = '#d0c8b8'
toga_fold = '#c0b8a8'

phi_inv = 1 / phi

# ============================================================
# ТОГА — классическая римская
# ============================================================
body_t = np.linspace(0, 1, 200)

# Плечи — широкие, по-мужски
shoulder_l_x = -2.8 + 0.5 * body_t
shoulder_l_y = -2.5 - 0.3 * body_t + 0.1 * np.sin(np.pi * body_t)
shoulder_r_x = 2.8 - 0.5 * body_t
shoulder_r_y = -2.5 - 0.3 * body_t + 0.1 * np.sin(np.pi * body_t)

# Контур тела
body_contour_x = np.concatenate([
    np.linspace(-2.5, -2.8, 30),  # левое плечо
    [-2.9, -2.8, -2.5, -2.2, -1.8],  # левый бок
    np.linspace(-1.5, 1.5, 50),  # низ
    [1.8, 2.2, 2.5, 2.8, 2.9],  # правый бок
    np.linspace(2.8, 2.5, 30),  # правое плечо
])
body_contour_y = np.concatenate([
    np.linspace(-2.5, -3.2, 30),
    [-3.5, -4.0, -4.5, -5.0, -5.5],
    np.linspace(-5.8, -5.8, 50),
    [-5.5, -5.0, -4.5, -4.0, -3.5],
    np.linspace(-3.2, -2.5, 30),
])
ax.fill(body_contour_x, body_contour_y, color=toga_white, alpha=0.9)

# V-образный вырез тоги
decollete_t = np.linspace(0, 1, 100)
decollete_l_x = -0.8 - 0.5 * decollete_t
decollete_l_y = -2.3 + 0.3 * decollete_t - 2.5 * decollete_t**2
decollete_r_x = 0.8 + 0.5 * decollete_t
decollete_r_y = decollete_l_y
ax.fill_between(decollete_l_x, decollete_l_y, -5, color=toga_white, alpha=0.9)
ax.fill_between(decollete_r_x, decollete_r_y, -5, color=toga_white, alpha=0.9)

# Видимая грудь (над тогой)
chest_y = np.linspace(-2.3, -3.5, 80)
chest_x = 0.3 * np.sin(np.pi * (chest_y + 2.3) / 1.2)
ax.fill_betweenx(chest_y, -0.6 + chest_x, 0.6 + chest_x, color=skin, alpha=0.7)

# Складки тоги — полиномиальные кривые (натяжение от плеча)
for i in range(12):
    fold_t = np.linspace(0, 1, 80)
    # Левая сторона
    fl_x = -1.8 + 0.8 * fold_t + 0.1 * np.sin(2 * np.pi * fold_t + i)
    fl_y = -2.8 - 2.5 * fold_t**1.2
    ax.plot(fl_x, fl_y, color=toga_shadow, linewidth=0.6, alpha=0.4)
    # Правая сторона
    fr_x = 1.8 - 0.8 * fold_t - 0.1 * np.sin(2 * np.pi * fold_t + i)
    fr_y = fl_y
    ax.plot(fr_x, fr_y, color=toga_shadow, linewidth=0.6, alpha=0.4)

# Диагональная складка (правое плечо → левое бедро)
drape_t = np.linspace(0, 1, 200)
drape_x = 2.0 - 3.5 * drape_t + 0.2 * np.sin(3 * np.pi * drape_t)
drape_y = -2.5 - 3.0 * drape_t**0.8
ax.plot(drape_x, drape_y, color=toga_shadow, linewidth=1.5, alpha=0.5)

# Золотая фибула (булавка)
fib_t = np.linspace(0, 2*np.pi, 100)
fib_x = 2.0 + 0.18 * np.cos(fib_t)
fib_y = -2.5 + 0.18 * np.sin(fib_t)
ax.fill(fib_x, fib_y, color=gold, alpha=0.9)
ax.plot(fib_x, fib_y, color=gold_dark, linewidth=1.5)
# Голова орла на фибуле
eagle_t = np.linspace(0, 2*np.pi, 60)
ax.fill(2.0 + 0.08*np.cos(eagle_t), -2.5 + 0.08*np.sin(eagle_t)*1.3,
        color=gold_dark, alpha=0.6)

# ============================================================
# ШЕЯ — реалистичная, мускулистая
# ============================================================
neck_t = np.linspace(0, 1, 100)

# Левая сторона шеи
neck_l_x = -0.55 - 0.1 * neck_t + 0.05 * neck_t**2
neck_l_y = -1.8 - 0.7 * neck_t
ax.plot(neck_l_x, neck_l_y, color=skin_shadow, linewidth=1.5, alpha=0.6)

# Правая сторона шеи
neck_r_x = 0.55 + 0.1 * neck_t - 0.05 * neck_t**2
neck_r_y = neck_l_y
ax.plot(neck_r_x, neck_r_y, color=skin_shadow, linewidth=1.5, alpha=0.6)

# Заливка шеи
neck_fill_y = np.linspace(-1.8, -2.5, 80)
neck_fill_l = -0.55 - 0.1 * (neck_fill_y + 1.8) / 0.7
neck_fill_r = 0.55 + 0.1 * (neck_fill_y + 1.8) / 0.7
ax.fill_betweenx(neck_fill_y, neck_fill_l, neck_fill_r, color=skin, alpha=0.9)

# Адамово яблоко
adam_t = np.linspace(0, np.pi, 50)
adam_x = 0.05 * np.cos(adam_t)
adam_y = -2.0 + 0.08 * np.sin(adam_t)
ax.plot(adam_x, adam_y, color=skin_shadow, linewidth=0.8, alpha=0.4)

# Сухожилия шеи
for ns in [-1, 1]:
    tend_t = np.linspace(0, 1, 60)
    tx = ns * (0.15 + 0.2 * tend_t)
    ty = -1.85 - 0.55 * tend_t
    ax.plot(tx, ty, color=skin_shadow, linewidth=0.7, alpha=0.3)

# Складки шеи
for i in range(2):
    wr_y = -2.0 - i * 0.12
    wr_t = np.linspace(-0.25, 0.25, 40)
    ax.plot(wr_t, wr_y + 0.008 * np.sin(6 * wr_t),
            color=skin_shadow, linewidth=0.6, alpha=0.35)

# ============================================================
# ГОЛОВА — реалистичный овал, слегка удлинённый
# ============================================================
# Лицевой овал — не идеальный эллипс, а полиномическая деформация
head_t = np.linspace(0, 2*np.pi, 500)
head_base_a = 1.05
head_base_b = 1.3

# Полиномические поправки для реалистичности:
# - slightly wider cheekbones
# - narrower chin
head_r = 1.0 + 0.03 * np.cos(2*head_t) - 0.05 * np.cos(4*head_t) + 0.02 * np.sin(head_t)
hx = head_base_a * head_r * np.cos(head_t)
hy = head_base_b * np.sin(head_t)

# Смещение: подбородок уже, скулы шире
chin_mask = hy < -0.5
hx[chin_mask] *= 0.85  # подбородок уже
cheek_mask = (hy > -0.2) & (hy < 0.3)
hx[cheek_mask] *= 1.05  # скулы шире

# Заливка лица
ax.fill(hx, hy, color=skin, alpha=0.95)

# Тени на лице — левая сторона и под скулами
shadow_mask_l = hx < -0.2
ax.fill(hx[shadow_mask_l], hy[shadow_mask_l], color=skin_shadow, alpha=0.12)
shadow_mask_chin = hy < -0.8
ax.fill(hx[shadow_mask_chin], hy[shadow_mask_chin], color=skin_shadow, alpha=0.1)

# Контур лица
ax.plot(hx, hy, color=skin_shadow, linewidth=1.2)

# Линия подбородка
chin_line_t = np.linspace(-0.8, 0.8, 100)
chin_line_x = 0.9 * chin_line_t
chin_line_y = -1.25 + 0.05 * np.cos(np.pi * chin_line_t / 0.8)
ax.plot(chin_line_x, chin_line_y, color=skin_shadow, linewidth=0.6, alpha=0.3)

# ============================================================
# ПРИЧЁСКА — римская, как у Цезаря/Августа
# Тонкие волосы сверху, лысина, но волосы по бокам и сзади
# ============================================================

# Объём волос — верх и бока
hair_fill_x = np.concatenate([
    np.linspace(-1.2, -1.1, 30),
    [-1.0, -0.8, -0.5, -0.2, 0.0, 0.2, 0.5, 0.8, 1.0],
    np.linspace(1.1, 1.2, 30),
    np.linspace(1.15, -1.15, 50)
])
hair_fill_y = np.concatenate([
    np.linspace(0.8, 1.15, 30),
    [1.25, 1.35, 1.45, 1.5, 1.52, 1.5, 1.45, 1.35, 1.25],
    np.linspace(1.15, 0.8, 30),
    np.linspace(1.2, 1.2, 50)
])
ax.fill(hair_fill_x, hair_fill_y, color=hair_dark, alpha=0.85)

# Боковые волосы (от висков к ушам)
for side in [-1, 1]:
    side_t = np.linspace(0, 1, 100)
    side_x = side * (0.95 + 0.15 * side_t)
    side_y = 0.5 - 0.8 * side_t + 0.1 * np.sin(2 * np.pi * side_t)
    
    for strand in range(6):
        strand_off = (strand - 3) * 0.03
        sx = side_x + strand_off * np.cos(side_t * np.pi)
        sy = side_y + strand_off * np.sin(side_t * np.pi)
        ax.plot(sx, sy, color=hair_dark, linewidth=1.5, alpha=0.6 - strand*0.05)

# Пробор — тонкая линия, лысина заметна
# Волосы прядями от центра
for strand_i in range(15):
    strand_angle = -np.pi/3 + strand_i * np.pi / 22
    strand_len = 0.6 + 0.2 * np.random.random()  # разная длина
    
    strand_t = np.linspace(0, 1, 50)
    # Прядь идёт от макушки вперёд/назад
    sx = strand_len * strand_t * np.cos(strand_angle) * 0.8
    sy = 1.2 + strand_len * strand_t * np.sin(strand_angle) * 0.5
    
    # Немного волнистости
    sx += 0.03 * np.sin(3 * np.pi * strand_t)
    
    ax.plot(sx, sy, color=hair_mid, linewidth=1.2, alpha=0.5)

# Затылочные волосы
back_hair_t = np.linspace(-1, 1, 100)
for bi in range(8):
    bx = back_hair_t * (0.8 + 0.1*bi/8)
    by = 1.1 + 0.15*bi/8 + 0.05 * np.sin(4 * np.pi * back_hair_t + bi)
    ax.plot(bx, by, color=hair_dark, linewidth=1.0, alpha=0.4 + bi*0.03)

# Лысина сверху — полупрозрачный блик
bald_t = np.linspace(0, 2*np.pi, 200)
for i in range(5):
    br = 0.5 - i * 0.05
    bx = br * np.cos(bald_t) * 0.7
    by = 1.0 + br * np.sin(bald_t) * 0.3
    ax.fill(bx, by, color=skin_light, alpha=0.08 + i*0.01)

# Блик на лысине
blik = Ellipse((0.0, 0.95), 0.5, 0.2, angle=0,
               facecolor='white', alpha=0.15, edgecolor='none')
ax.add_patch(blik)

# ============================================================
# УШИ — реалистичные, пропорциональные
# ============================================================
for ear_sign in [-1, 1]:
    ear_x = ear_sign * (head_base_a - 0.02)
    ear_y_center = 0.0
    
    # Внешний контур уха
    ear_t = np.linspace(-np.pi*0.65, np.pi*0.65, 100)
    ear_r = 0.22 + 0.03 * np.cos(2*ear_t)
    ear_cx = ear_x + ear_sign * ear_r * np.cos(ear_t)
    ear_cy = ear_y_center + 0.3 * np.sin(ear_t)
    ax.fill(ear_cx, ear_cy, color=skin, alpha=0.95)
    ax.plot(ear_cx, ear_cy, color=skin_shadow, linewidth=1.0)
    
    # Мочка уха
    mouch_t = np.linspace(0, np.pi, 40)
    mx = ear_x + ear_sign * 0.2 * np.cos(mouch_t)
    my = ear_y_center - 0.22 + 0.1 * np.sin(mouch_t)
    ax.plot(mx, my, color=skin_shadow, linewidth=0.8, alpha=0.6)
    
    # Раковина уха — хрящевые изгибы (полиномические)
    inner_t = np.linspace(0.3, 2.5, 80)
    ir = 0.05 + 0.03 * np.sin(inner_t * 2)
    ix = ear_x + ear_sign * ir * np.cos(inner_t + np.pi/2)
    iy = ear_y_center + ir * np.sin(inner_t + np.pi/2)
    ax.plot(ix, iy, color=skin_shadow, linewidth=0.7, alpha=0.4)

# ============================================================
# БРОВИ — густые, мужественные, с характером
# ============================================================
brow_t = np.linspace(-1, 1, 100)

for bx_sign in [-1, 1]:
    bx_c = bx_sign * 0.48
    # Парабола с наклоном — вoward переносицы приподнимаются
    brow_x = bx_c + 0.28 * brow_t
    brow_y = 0.38 - 0.04 * brow_t**2 - bx_sign * 0.025 * brow_t
    
    ax.plot(brow_x, brow_y, color=brow_color, linewidth=2.8,
            solid_capstyle='round')
    # Объём брови
    ax.plot(brow_x, brow_y - 0.015, color=brow_color, linewidth=1.5,
            solid_capstyle='round', alpha=0.4)

# ============================================================
# ГЛАЗА — реалистичные, almond-shaped
# ============================================================
eye_w = 0.22
eye_h = 0.09

for ex_sign in [-1, 1]:
    ex_c = ex_sign * 0.48
    ey_c = 0.2
    
    # Верхнее веко — эллиптическая дуга
    eye_t = np.linspace(0, np.pi, 100)
    upper_x = ex_c + eye_w * np.cos(eye_t)
    upper_y = ey_c + eye_h * np.sin(eye_t)
    
    # Складка верхнего века (над глазом)
    lid_fold_x = ex_c + (eye_w + 0.03) * np.cos(eye_t)
    lid_fold_y = ey_c + (eye_h + 0.04) * np.sin(eye_t)
    ax.plot(lid_fold_x, lid_fold_y, color=skin_shadow, linewidth=0.7, alpha=0.4)
    
    ax.plot(upper_x, upper_y, color=brow_color, linewidth=1.8)
    
    # Нижнее веко — более плоская дуга
    lower_x = ex_c + eye_w * np.cos(eye_t)
    lower_y = ey_c - eye_h * 0.5 * np.sin(eye_t)
    ax.plot(lower_x, lower_y, color=skin_shadow, linewidth=1.0, alpha=0.6)
    
    # Белок
    full_t = np.linspace(0, 2*np.pi, 100)
    white_x = ex_c + eye_w * np.cos(full_t)
    white_upper = ey_c + eye_h * np.sin(full_t)
    white_lower = ey_c - eye_h * 0.5 * np.sin(full_t)
    ax.fill_between(white_x, white_lower, white_upper, color='white', alpha=0.95)
    
    # Радужка
    iris_r = eye_h * 0.5
    iris_x = ex_c + iris_r * np.cos(full_t)
    iris_y = ey_c + iris_r * 0.85 * np.sin(full_t) - 0.005
    ax.fill(iris_x, iris_y, color=eye_color, alpha=0.9)
    
    # Зрачок
    pupil_r = iris_r * 0.45
    pupil_x = ex_c + pupil_r * np.cos(full_t)
    pupil_y = ey_c + pupil_r * 0.85 * np.sin(full_t) - 0.005
    ax.fill(pupil_x, pupil_y, color=dark, alpha=0.95)
    
    # Блик
    ax.plot(ex_c + 0.03, ey_c + 0.025, 'o', color='white', markersize=2.5, alpha=0.9)
    
    # Нижние «гусиные лапки» — тонкие
    for i in range(3):
        crow_t = np.linspace(0, 1, 25)
        crow_x = ex_c + ex_sign * (eye_w + 0.01 + 0.04*crow_t)
        crow_y = ey_c - 0.03 + (i-1)*0.03 - 0.02*crow_t
        ax.plot(crow_x, crow_y, color=skin_shadow, linewidth=0.5, alpha=0.3)

# ============================================================
# НОС — прямой с горбинкой (римский, aquiline)
# ============================================================
# Переносица — полиномическая кривая с горбинкой
nose_t = np.linspace(0, 1, 200)

# Основная линия носа — кубический полином с горбинкой
# y(t) = a*t + b*t² + c*t³ — горбинка на 40% длины
nose_profile_x = (0.03 * nose_t 
                  + 0.08 * nose_t**2 * (nose_t - 0.4)  # горбинка
                  - 0.02 * nose_t**3)
nose_profile_y = 0.2 - 0.55 * nose_t

# Тень по бокам носа
nose_shadow_width = 0.08 + 0.03 * nose_t  # расширяется к кончику

# Левая тень носа
ns_l_x = nose_profile_x - nose_shadow_width * (1 - 0.3*nose_t)
ns_l_y = nose_profile_y
ax.plot(ns_l_x, ns_l_y, color=skin_shadow, linewidth=1.0, alpha=0.35)

# Правая тень носа
ns_r_x = nose_profile_x + nose_shadow_width * (1 - 0.3*nose_t)
ns_r_y = nose_profile_y
ax.plot(ns_r_x, ns_r_y, color=skin_shadow, linewidth=1.0, alpha=0.35)

# Световая линия переносицы (прямая, как просит пользователь)
nose_light_x = nose_profile_x + 0.01
nose_light_y = nose_profile_y
ax.plot(nose_light_x, nose_light_y, color=skin_light, linewidth=1.5, alpha=0.3)

# Кончик носа — полукруглый, с горбинкой
nose_tip_t = np.linspace(0, np.pi, 80)
nose_tip_x = 0.12 * np.cos(nose_tip_t) + 0.03  # слегка вправо
nose_tip_y = -0.35 + 0.1 * np.sin(nose_tip_t)
ax.fill(nose_tip_x, nose_tip_y, color=skin, alpha=0.9)
ax.plot(nose_tip_x, nose_tip_y, color=skin_shadow, linewidth=0.8, alpha=0.5)

# Крылья носа
for ns in [-1, 1]:
    wing_t = np.linspace(0, np.pi, 50)
    wing_x = ns * 0.12 + ns * 0.08 * np.cos(wing_t)
    wing_y = -0.35 + 0.06 * np.sin(wing_t)
    ax.plot(wing_x, wing_y, color=skin_shadow, linewidth=1.0, alpha=0.4)

# Ноздри
for ns in [-1, 1]:
    nostril_t = np.linspace(0, 2*np.pi, 40)
    ns_x = ns * 0.08 + 0.04 * np.cos(nostril_t)
    ns_y = -0.38 + 0.025 * np.sin(nostril_t)
    ax.fill(ns_x, ns_y, color=skin_shadow, alpha=0.25)

# Горбинка — акцент тени
bump_t = np.linspace(0.3, 0.5, 30)
bump_x = 0.03 * bump_t + 0.08 * bump_t**2 * (bump_t - 0.4)
bump_y = 0.2 - 0.55 * bump_t
ax.plot(bump_x, bump_y, color=skin_shadow, linewidth=1.5, alpha=0.4)

# ============================================================
# РЕЛЬЕФ СКУЛ И ЩЁК
# ============================================================
# Линия скулы
for side in [-1, 1]:
    sc_t = np.linspace(0, 1, 60)
    sc_x = side * (0.85 - 0.3 * sc_t)
    sc_y = 0.05 - 0.15 * sc_t
    ax.plot(sc_x, sc_y, color=skin_shadow, linewidth=0.6, alpha=0.25)

# Носогубные складки — реалистичные
for ns in [-1, 1]:
    nas_t = np.linspace(0, 1, 80)
    # Кубический полином — более естественная кривизна
    nas_x = ns * (0.08 + 0.15 * nas_t + 0.05 * nas_t**3)
    nas_y = -0.35 - 0.25 * nas_t - 0.03 * nas_t**2
    ax.plot(nas_x, nas_y, color=skin_shadow, linewidth=0.8, alpha=0.35)

# Лёгкий румянец на щеках
for cs in [-1, 1]:
    cheek = Ellipse((cs * 0.6, -0.1), 0.35, 0.2, angle=0,
                     facecolor='#d0a088', alpha=0.12, edgecolor='none')
    ax.add_patch(cheek)

# ============================================================
# РОТ — спокойное выражение, мужественное
# ============================================================
mouth_y = -0.55
mouth_w = 0.38

mouth_t = np.linspace(-1, 1, 100)

# Верхняя губа — «лук Купидона»
upper_lip_x = mouth_w * mouth_t
upper_lip_y = mouth_y + 0.04 * (1 - mouth_t**2) - 0.015 * np.abs(mouth_t)
ax.plot(upper_lip_x, upper_lip_y, color=lip_color, linewidth=1.5)
ax.fill_between(upper_lip_x, mouth_y - 0.005, upper_lip_y, color=lip_color, alpha=0.35)

# Нижняя губа
lower_lip_x = mouth_w * mouth_t
lower_lip_y = mouth_y - 0.035 * (1 - mouth_t**2)
ax.plot(lower_lip_x, lower_lip_y, color=lip_color, linewidth=1.5)
ax.fill_between(lower_lip_x, mouth_y, lower_lip_y, color=lip_color, alpha=0.3)

# Линия рта — спокойная
mouth_line_y = mouth_y + 0.003 * np.sin(np.pi * mouth_t)
ax.plot(mouth_w * mouth_t, mouth_line_y, color=lip_shadow, linewidth=1.0)

# Тень под нижней губой
shadow_under_lip_t = np.linspace(-0.3, 0.3, 50)
ax.plot(shadow_under_lip_t, mouth_y - 0.05 - 0.02 * np.cos(np.pi * shadow_under_lip_t / 0.3),
        color=skin_shadow, linewidth=0.6, alpha=0.3)

# ============================================================
# ПОДБОРОДОК — мужественный, с ямочкой
# ============================================================
# Ямочка
dimple_t = np.linspace(0, 2*np.pi, 30)
dimple_x = 0.04 * np.cos(dimple_t)
dimple_y = -1.05 + 0.03 * np.sin(dimple_t)
ax.plot(dimple_x, dimple_y, color=skin_shadow, linewidth=0.6, alpha=0.3)

# Линия челюсти
jaw_t = np.linspace(0, 1, 100)
for js in [-1, 1]:
    jx = js * (0.95 - 0.7 * jaw_t)
    jy = -0.6 - 0.65 * jaw_t
    ax.plot(jx, jy, color=skin_shadow, linewidth=0.7, alpha=0.3)

# ============================================================
# ВЕНЕЦ ИЗ ЛАВРА — римский императорский
# ============================================================
# Стебель венка — полумесяц
crown_t = np.linspace(-2.5, 2.5, 300)
crown_r = 1.15 + 0.05 * np.sin(3 * crown_t)
cx = crown_r * np.cos(crown_t * 0.8) * 0.9
cy = crown_r * np.sin(crown_t * 0.8) * 0.6 + 0.8

# Стебель
ax.plot(cx, cy, color='#4a7a2a', linewidth=1.5, alpha=0.6)

# Листья лавра
for i in range(28):
    ci = int(i * 299 / 27)
    angle = crown_t[ci] * 0.8
    leaf_cx = cx[ci]
    leaf_cy = cy[ci]
    
    leaf_t = np.linspace(0, 1, 30)
    leaf_len = 0.12
    leaf_w = 0.035
    
    # Направление вдоль стебля
    tangent = np.array([-np.sin(angle)*0.8, np.cos(angle)*0.6])
    tangent = tangent / np.linalg.norm(tangent)
    normal = np.array([-tangent[1], tangent[0]])
    
    lx = leaf_cx + leaf_len * leaf_t * tangent[0] + leaf_w * np.sin(np.pi*leaf_t) * normal[0]
    ly = leaf_cy + leaf_len * leaf_t * tangent[1] + leaf_w * np.sin(np.pi*leaf_t) * normal[1]
    
    color_choice = '#5a8a3a' if i % 3 != 0 else '#4a7a2a'
    ax.fill(lx, ly, color=color_choice, alpha=0.75)
    # Жилка листа
    ax.plot([leaf_cx, leaf_cx + leaf_len*tangent[0]],
            [leaf_cy, leaf_cy + leaf_len*tangent[1]],
            color='#3a6a1a', linewidth=0.4, alpha=0.4)

# ============================================================
# ПОДПИСЬ И РАМКА
# ============================================================
ax.text(0, -5.5, 'ПОРТРЕТ В СТИЛЕ РИМСКОГО ИМПЕРАТОРА',
        fontsize=13, ha='center', fontfamily='serif', color='#3a2a1a',
        fontweight='bold', fontstyle='italic',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#f0e8d8',
                  edgecolor='#8a6a4a', linewidth=1.5))

ax.text(0, -5.85,
        'φ = 1.618  |  Нос: кубический полином + горбинка  |  Волосы: полиномические пряди  |  Лавр: параметрический венец',
        fontsize=7, ha='center', fontfamily='serif', color='#8a6a4a', fontstyle='italic')

# Рамка
rect = plt.Rectangle((-3.8, -5.95), 7.6, 12.85,
                       fill=False, edgecolor='#c0a880', linewidth=2, alpha=0.5)
ax.add_patch(rect)

plt.tight_layout()
plt.savefig('emperor_portrait.png', dpi=200, bbox_inches='tight', facecolor='#f5efe0')
print("Сохранено: emperor_portrait.png")
