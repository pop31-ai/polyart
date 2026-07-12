import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

fig, ax = plt.subplots(1, 1, figsize=(11, 14), facecolor='#f5efe0')
ax.set_facecolor('#f5efe0')
ax.set_xlim(-4, 4)
ax.set_ylim(-6, 7)
ax.set_aspect('equal')
ax.axis('off')

phi = (1 + np.sqrt(5)) / 2

skin = '#e0c8a8'
skin_shadow = '#c8a888'
skin_deep = '#b09878'
skin_light = '#f0dcc8'
hair_dark = '#3a2a18'
hair_mid = '#5a4028'
eye_color = '#5a7888'
lip_color = '#b86858'
lip_shadow = '#a05848'
brow_color = '#3a2818'
dark = '#1a1008'
gold = '#c8a040'
gold_dark = '#8a6820'
toga_white = '#ede8de'
toga_shadow = '#d0c8b8'
hollow = '#8a7060'
fat_shadow = '#b8a080'

# ============================================================
# ТОГА
# ============================================================
body_contour_x = np.concatenate([
    np.linspace(-3.0, -3.3, 30),
    [-3.4, -3.3, -3.0, -2.5, -2.0],
    np.linspace(-1.5, 1.5, 50),
    [2.0, 2.5, 3.0, 3.3, 3.4],
    np.linspace(3.3, 3.0, 30),
])
body_contour_y = np.concatenate([
    np.linspace(-2.5, -3.5, 30),
    [-3.8, -4.2, -4.8, -5.3, -5.8],
    np.linspace(-6.0, -6.0, 50),
    [-5.8, -5.3, -4.8, -4.2, -3.8],
    np.linspace(-3.5, -2.5, 30),
])
ax.fill(body_contour_x, body_contour_y, color=toga_white, alpha=0.9)

# Складки тоги
for i in range(10):
    fold_t = np.linspace(0, 1, 80)
    fl_x = -2.0 + 1.0 * fold_t + 0.1 * np.sin(2 * np.pi * fold_t + i)
    fl_y = -2.8 - 2.8 * fold_t**1.2
    ax.plot(fl_x, fl_y, color=toga_shadow, linewidth=0.6, alpha=0.35)
    fr_x = 2.0 - 1.0 * fold_t - 0.1 * np.sin(2 * np.pi * fold_t + i)
    ax.plot(fr_x, fl_y, color=toga_shadow, linewidth=0.6, alpha=0.35)

# Диагональная складка
drape_t = np.linspace(0, 1, 200)
drape_x = 2.2 - 4.0 * drape_t + 0.2 * np.sin(3 * np.pi * drape_t)
drape_y = -2.5 - 3.2 * drape_t**0.8
ax.plot(drape_x, drape_y, color=toga_shadow, linewidth=1.2, alpha=0.4)

# Фибула
fib_t = np.linspace(0, 2*np.pi, 100)
ax.fill(2.2 + 0.18*np.cos(fib_t), -2.6 + 0.18*np.sin(fib_t), color=gold, alpha=0.9)
ax.plot(2.2 + 0.18*np.cos(fib_t), -2.6 + 0.18*np.sin(fib_t), color=gold_dark, linewidth=1.5)

# ============================================================
# ШЕЯ — толстая, с двойным подбородком, обвислая
# ============================================================
neck_t = np.linspace(0, 1, 100)

# Толстая шея
neck_l_x = -0.7 - 0.15 * neck_t + 0.05 * neck_t**2
neck_l_y = -1.7 - 0.8 * neck_t
neck_r_x = 0.7 + 0.15 * neck_t - 0.05 * neck_t**2
neck_r_y = neck_l_y

# Заливка шеи
neck_fill_y = np.linspace(-1.7, -2.5, 80)
neck_fill_l = -0.7 - 0.15 * (neck_fill_y + 1.7) / 0.8
neck_fill_r = 0.7 + 0.15 * (neck_fill_y + 1.7) / 0.8
ax.fill_betweenx(neck_fill_y, neck_fill_l, neck_fill_r, color=skin, alpha=0.9)

ax.plot(neck_l_x, neck_l_y, color=skin_shadow, linewidth=1.2, alpha=0.5)
ax.plot(neck_r_x, neck_r_y, color=skin_shadow, linewidth=1.2, alpha=0.5)

# Много складок на шее (обвислая кожа)
for i in range(5):
    wr_y = -1.9 - i * 0.1
    wr_t = np.linspace(-0.5, 0.5, 60)
    sag = 0.04 * i  # обвислость
    ax.plot(wr_t, wr_y + sag * np.cos(np.pi * wr_t / 0.5) + 0.01 * np.sin(6 * wr_t),
            color=skin_shadow, linewidth=0.7, alpha=0.35 + i * 0.03)

# Двойной подбородок — жировые складки
for i in range(3):
    chin_sag_t = np.linspace(-1, 1, 100)
    chin_sag_x = (0.9 + 0.1*i) * chin_sag_t
    chin_sag_y = -1.3 + 0.15 * np.cos(np.pi * chin_sag_t) + i * 0.08
    ax.plot(chin_sag_x, chin_sag_y, color=skin_shadow, linewidth=0.8, alpha=0.3 + i*0.05)

# Жировые мешки под подбородком
for side in [-1, 1]:
    fat_t = np.linspace(0, 1, 60)
    fat_x = side * (0.3 + 0.3 * fat_t)
    fat_y = -1.4 + 0.2 * np.sin(np.pi * fat_t)
    ax.fill_between(fat_x, fat_y - 0.05, fat_y, color=skin_shadow, alpha=0.15)

# ============================================================
# ГОЛОВА — ШИРОКАЯ, ЖИРНАЯ, ОБВИСЛАЯ
# ============================================================
head_t = np.linspace(0, 2*np.pi, 500)
# Широкий, полный овал — жирность
head_base_a = 1.35  # шире обычного
head_base_b = 1.45  # чуть меньше по высоте (лицо круглое)

# Полиномические деформации: жирные щёки, обвислый подбородок
head_r = (1.0 
          + 0.08 * np.cos(2*head_t)   # расширение на щеках
          + 0.04 * np.cos(4*head_t)   # неровность
          + 0.03 * np.sin(head_t)     # асимметрия
          - 0.06 * np.cos(6*head_t))  # мелкая неровность
hx = head_base_a * head_r * np.cos(head_t)
hy = head_base_b * np.sin(head_t)

# Обвислые щеки — расширение внизу
jowl_mask = (hy < -0.3) & (hy > -1.0)
hx[jowl_mask] *= 1.12

# Жирный подбородок
chin_mask = hy < -0.8
hx[chin_mask] *= 1.05

# Широкие скулы
cheek_mask = (hy > -0.1) & (hy < 0.4)
hx[cheek_mask] *= 1.06

# Заливка
ax.fill(hx, hy, color=skin, alpha=0.95)

# Тени — обвислость, жировые мешки
shadow_l = hx < -0.15
ax.fill(hx[shadow_l], hy[shadow_l], color=skin_shadow, alpha=0.1)
shadow_chin = hy < -0.7
ax.fill(hx[shadow_chin], hy[shadow_chin], color=skin_shadow, alpha=0.12)
shadow_jowl = (hy < -0.3) & (hy > -0.9) & (np.abs(hx) > 0.8)
ax.fill(hx[shadow_jowl], hy[shadow_jowl], color=skin_deep, alpha=0.08)

ax.plot(hx, hy, color=skin_shadow, linewidth=1.2)

# Линия подбородка — толстая, двойная
chin_t = np.linspace(-0.9, 0.9, 100)
ax.plot(1.1 * chin_t, -1.2 + 0.06 * np.cos(np.pi * chin_t / 0.9),
        color=skin_shadow, linewidth=0.8, alpha=0.35)

# ============================================================
# ПРИЧЁСКА — тонкая, редкая (облысение)
# ============================================================
# Волосы по бокам и сзади
for side in [-1, 1]:
    for strand in range(8):
        strand_t = np.linspace(0, 1, 60)
        sx_base = side * (1.05 + 0.12 * strand_t)
        sy_base = 0.6 - 0.9 * strand_t + 0.05 * np.sin(3*np.pi*strand_t + strand)
        off = (strand - 4) * 0.02
        sx = sx_base + off * np.cos(strand_t * np.pi)
        sy = sy_base + off
        ax.plot(sx, sy, color=hair_dark, linewidth=1.3, alpha=0.5 - strand*0.03)

# Редкие пряди на макушке
np.random.seed(42)
for i in range(20):
    sa = np.random.uniform(-1.2, 1.2)
    sl = np.random.uniform(0.3, 0.7)
    st = np.linspace(0, 1, 40)
    sx = sl * st * np.cos(sa) * 0.6
    sy = 1.1 + sl * st * np.sin(sa) * 0.3 + 0.02 * np.sin(5*np.pi*st)
    ax.plot(sx, sy, color=hair_mid, linewidth=0.8, alpha=0.35)

# Затылочные волосы
for bi in range(6):
    bt = np.linspace(-1, 1, 80)
    bx = bt * (0.7 + 0.08*bi/6)
    by = 1.0 + 0.12*bi/6 + 0.04 * np.sin(4*np.pi*bt + bi)
    ax.plot(bx, by, color=hair_dark, linewidth=0.8, alpha=0.3 + bi*0.03)

# ============================================================
# УШИ — большие, обвислые мочки
# ============================================================
for ear_sign in [-1, 1]:
    ear_x = ear_sign * (head_base_a - 0.05)
    ear_y_center = -0.05

    ear_t = np.linspace(-np.pi*0.65, np.pi*0.65, 100)
    ear_r = 0.25 + 0.04 * np.cos(2*ear_t)  # больше обычного
    ear_cx = ear_x + ear_sign * ear_r * np.cos(ear_t)
    ear_cy = ear_y_center + 0.32 * np.sin(ear_t)
    ax.fill(ear_cx, ear_cy, color=skin, alpha=0.95)
    ax.plot(ear_cx, ear_cy, color=skin_shadow, linewidth=1.0)

    # Обвислая мочка — длинная
    mouch_t = np.linspace(0, np.pi, 40)
    mx = ear_x + ear_sign * 0.22 * np.cos(mouch_t)
    my = ear_y_center - 0.28 + 0.12 * np.sin(mouch_t)  # длиннее
    ax.plot(mx, my, color=skin_shadow, linewidth=0.8, alpha=0.6)

    # Раковина
    inner_t = np.linspace(0.3, 2.5, 80)
    ir = 0.06 + 0.03 * np.sin(inner_t * 2)
    ix = ear_x + ear_sign * ir * np.cos(inner_t + np.pi/2)
    iy = ear_y_center + ir * np.sin(inner_t + np.pi/2)
    ax.plot(ix, iy, color=skin_shadow, linewidth=0.6, alpha=0.4)

# ============================================================
# МОРЩИНЫ НА ЛБУ — глубокие горизонтальные + вертикальные межбровные
# ============================================================
# Горизонтальные морщины (5-6 штук)
for i in range(6):
    fw_t = np.linspace(-0.6, 0.6, 80)
    # Полином: волнистая линия, глубже к центру
    depth = 0.015 + 0.005 * (1 - (fw_t/0.6)**2)  # глубина морщины
    fw_x = fw_t
    fw_y = 0.95 + 0.06 * i + depth * np.sin(4 * np.pi * fw_t + i * 0.5)
    ax.plot(fw_x, fw_y, color=skin_deep, linewidth=0.8, alpha=0.4 + i * 0.02)
    # Тень морщины
    ax.plot(fw_x, fw_y - 0.008, color=skin_shadow, linewidth=0.5, alpha=0.25)

# Вертикальные морщины между бровями (11-22)
for i in range(5):
    vb_x = -0.06 + i * 0.03
    vb_t = np.linspace(0, 1, 40)
    vb_xx = vb_x + 0.005 * np.sin(3*np.pi*vb_t)
    vb_y = 0.55 + 0.3 * vb_t
    ax.plot(vb_xx, vb_y, color=skin_deep, linewidth=0.6, alpha=0.35)

# Морщины «гусиные лапки» — глубокие
for side in [-1, 1]:
    for i in range(5):
        crow_t = np.linspace(0, 1, 30)
        crow_x = side * 0.48 + side * (0.22 + 0.06*crow_t + 0.01*i)
        crow_y = 0.15 - 0.04 + (i-2)*0.025 - 0.04*crow_t
        ax.plot(crow_x, crow_y, color=skin_deep, linewidth=0.6, alpha=0.3 + i*0.02)

# Морщины вокруг рта
for i in range(4):
    for ws in [-1, 1]:
        mw_t = np.linspace(0, 1, 30)
        mw_x = ws * (0.38 + 0.06*mw_t + 0.02*i)
        mw_y = -0.58 + 0.01*i - 0.03*mw_t
        ax.plot(mw_x, mw_y, color=skin_deep, linewidth=0.5, alpha=0.25)

# ============================================================
# БРОВИ — тяжёлые, нависающие
# ============================================================
brow_t = np.linspace(-1, 1, 100)
for bx_sign in [-1, 1]:
    bx_c = bx_sign * 0.52
    # Нависающие — тяжёлые, с выражением усталости
    brow_x = bx_c + 0.28 * brow_t
    brow_y = 0.32 - 0.06 * brow_t**2 - bx_sign * 0.03 * brow_t  # нависают
    ax.plot(brow_x, brow_y, color=brow_color, linewidth=3.0, solid_capstyle='round')
    ax.plot(brow_x, brow_y - 0.018, color=brow_color, linewidth=1.5,
            solid_capstyle='round', alpha=0.35)

# Складка кожи над бровями (нависание)
for bx_sign in [-1, 1]:
    hood_t = np.linspace(-1, 1, 80)
    hood_x = bx_sign * 0.52 + 0.3 * hood_t
    hood_y = 0.40 - 0.04 * hood_t**2
    ax.plot(hood_x, hood_y, color=skin_shadow, linewidth=0.8, alpha=0.35)

# ============================================================
# ГЛАЗА — ПУСТЫЕ ГЛУБОКИЕ ГЛУБОКИЕ ГЛАЗНИЦЫ, ТЯЖЁЛЫЕ ВЕКИ
# ============================================================
eye_w = 0.2
eye_h = 0.07  # уже, тяжелее

for ex_sign in [-1, 1]:
    ex_c = ex_sign * 0.52
    ey_c = 0.15  # глаза чуть ниже из-за нависших бровей

    # Глубокие глазницы — тёмные тени вокруг
    socket_t = np.linspace(0, 2*np.pi, 100)
    socket_r = 0.28
    socket_x = ex_c + socket_r * np.cos(socket_t) * 1.2
    socket_y = ey_c + socket_r * np.sin(socket_t) * 0.9
    ax.fill(socket_x, socket_y, color=skin_deep, alpha=0.2)

    # Ещё темнее — непосредственно вокруг глаза
    deep_socket_r = 0.2
    deep_x = ex_c + deep_socket_r * np.cos(socket_t) * 1.1
    deep_y = ey_c + deep_socket_r * np.sin(socket_t) * 0.8
    ax.fill(deep_x, deep_y, color=hollow, alpha=0.15)

    # Мешки под глазами — обвислая кожа
    bag_t = np.linspace(-1, 1, 80)
    bag_x = ex_c + (eye_w + 0.06) * bag_t
    bag_y_top = ey_c - eye_h * 0.3
    bag_y_bot = ey_c - eye_h * 0.3 - 0.06 * (1 - bag_t**2) - 0.02
    ax.fill_between(bag_x, bag_y_bot, bag_y_top, color=skin_shadow, alpha=0.25)
    ax.plot(bag_x, bag_y_bot, color=skin_deep, linewidth=0.7, alpha=0.35)

    # Нижнее веко — тяжёлое, обвисшее
    lower_x = ex_c + (eye_w + 0.02) * np.cos(np.linspace(0, np.pi, 100))
    lower_y = ey_c - eye_h * 0.6 * np.sin(np.linspace(0, np.pi, 100)) - 0.01
    ax.plot(lower_x, lower_y, color=brow_color, linewidth=1.2, alpha=0.6)

    # Верхнее веко — тяжёлое, НАВИСШЕЕ (закрывает часть глаза)
    upper_t = np.linspace(0, np.pi, 100)
    # Нависшее: верхняя граница ниже обычного, нависает на глаз
    upper_x = ex_c + eye_w * np.cos(upper_t)
    upper_y = ey_c + eye_h * 0.4 * np.sin(upper_t) + 0.015  # нависает!
    ax.plot(upper_x, upper_y, color=brow_color, linewidth=2.0)

    # Складка тяжёлого века (над глазом)
    lid_crease_x = ex_c + (eye_w + 0.04) * np.cos(upper_t)
    lid_crease_y = ey_c + (eye_h * 0.4 + 0.06) * np.sin(upper_t) + 0.02
    ax.plot(lid_crease_x, lid_crease_y, color=skin_shadow, linewidth=0.8, alpha=0.4)

    # Белок — маленький видимый кусочек
    full_t = np.linspace(0, 2*np.pi, 100)
    white_x = ex_c + eye_w * np.cos(full_t)
    white_upper = ey_c + eye_h * 0.4 * np.sin(full_t) + 0.015
    white_lower = ey_c - eye_h * 0.6 * np.sin(full_t) - 0.01
    ax.fill_between(white_x, white_lower, white_upper, color='white', alpha=0.85)

    # Радужка — частично закрыта верхним веком
    iris_r = eye_h * 0.48
    iris_x = ex_c + iris_r * np.cos(full_t)
    iris_y = ey_c + iris_r * 0.8 * np.sin(full_t) - 0.005
    ax.fill(iris_x, iris_y, color=eye_color, alpha=0.85)

    # Зрачок
    pupil_r = iris_r * 0.5
    pupil_x = ex_c + pupil_r * np.cos(full_t)
    pupil_y = ey_c + pupil_r * 0.8 * np.sin(full_t) - 0.005
    ax.fill(pupil_x, pupil_y, color=dark, alpha=0.95)

    # Блик — тусклый
    ax.plot(ex_c + 0.02, ey_c + 0.015, 'o', color='white', markersize=1.5, alpha=0.5)

    # Тёмные круги под глазами
    dark_circle_t = np.linspace(-0.8, 0.8, 60)
    dc_x = ex_c + 0.2 * dark_circle_t
    dc_y = ey_c - 0.12 - 0.04 * dark_circle_t**2
    ax.plot(dc_x, dc_y, color=hollow, linewidth=0.8, alpha=0.3)

# ============================================================
# НОС — прямой с горбинкой, толстый (жирность)
# ============================================================
nose_t = np.linspace(0, 1, 200)

# Переносица с горбинкой — кубический полином
nose_profile_x = (0.04 * nose_t 
                  + 0.1 * nose_t**2 * (nose_t - 0.4)
                  - 0.025 * nose_t**3)
nose_profile_y = 0.15 - 0.55 * nose_t

# Тени по бокам — толстый нос
nose_shadow_w = 0.1 + 0.05 * nose_t

ns_l_x = nose_profile_x - nose_shadow_w * (1 - 0.3*nose_t)
ns_r_x = nose_profile_x + nose_shadow_w * (1 - 0.3*nose_t)
ax.plot(ns_l_x, nose_profile_y, color=skin_shadow, linewidth=1.0, alpha=0.35)
ax.plot(ns_r_x, nose_profile_y, color=skin_shadow, linewidth=1.0, alpha=0.35)

# Световая линия
ax.plot(nose_profile_x + 0.01, nose_profile_y, color=skin_light, linewidth=1.2, alpha=0.25)

# Кончик носа — широкий, мясистый
nose_tip_t = np.linspace(0, np.pi, 80)
nose_tip_x = 0.16 * np.cos(nose_tip_t) + 0.04
nose_tip_y = -0.4 + 0.12 * np.sin(nose_tip_t)
ax.fill(nose_tip_x, nose_tip_y, color=skin, alpha=0.9)
ax.plot(nose_tip_x, nose_tip_y, color=skin_shadow, linewidth=0.8, alpha=0.45)

# Широкие крылья носа
for ns in [-1, 1]:
    wing_t = np.linspace(0, np.pi, 50)
    wing_x = ns * 0.15 + ns * 0.1 * np.cos(wing_t)
    wing_y = -0.4 + 0.07 * np.sin(wing_t)
    ax.plot(wing_x, wing_y, color=skin_shadow, linewidth=1.0, alpha=0.4)

# Ноздри — широкие
for ns in [-1, 1]:
    nostril_t = np.linspace(0, 2*np.pi, 40)
    ax.fill(ns * 0.1 + 0.05 * np.cos(nostril_t), -0.43 + 0.03 * np.sin(nostril_t),
            color=skin_shadow, alpha=0.25)

# Горбинка — тень
bump_t = np.linspace(0.3, 0.5, 30)
bump_x = 0.04 * bump_t + 0.1 * bump_t**2 * (bump_t - 0.4)
bump_y = 0.15 - 0.55 * bump_t
ax.plot(bump_x, bump_y, color=skin_deep, linewidth=1.5, alpha=0.4)

# ============================================================
# РЕЛЬЕФ — жирные щёки, носогубные складки глубокие
# ============================================================
# Носогубные — глубокие, тяжёлые
for ns in [-1, 1]:
    nas_t = np.linspace(0, 1, 80)
    nas_x = ns * (0.1 + 0.18 * nas_t + 0.06 * nas_t**3)
    nas_y = -0.4 - 0.3 * nas_t - 0.04 * nas_t**2
    ax.plot(nas_x, nas_y, color=skin_deep, linewidth=1.0, alpha=0.4)

# Жировые мешки на щеках
for cs in [-1, 1]:
    fat_cheek_t = np.linspace(0, 2*np.pi, 80)
    fc_x = cs * (0.7 + 0.25 * np.cos(fat_cheek_t))
    fc_y = -0.1 + 0.18 * np.sin(fat_cheek_t)
    ax.fill(fc_x, fc_y, color=skin_shadow, alpha=0.08)

# Складки вдоль челюсти (обвислость)
for js in [-1, 1]:
    jowl_t = np.linspace(0, 1, 60)
    jx = js * (1.0 - 0.15 * jowl_t)
    jy = -0.5 - 0.7 * jowl_t - 0.1 * jowl_t**2
    ax.plot(jx, jy, color=skin_deep, linewidth=0.7, alpha=0.3)

# ============================================================
# РОТ — тяжёлые губы, опущенные уголки (усталость)
# ============================================================
mouth_y = -0.6
mouth_w = 0.35

mouth_t = np.linspace(-1, 1, 100)

# Верхняя губа — тяжёлая, с «луком Купидона»
upper_lip_x = mouth_w * mouth_t
upper_lip_y = mouth_y + 0.035 * (1 - mouth_t**2) - 0.012 * np.abs(mouth_t)
ax.plot(upper_lip_x, upper_lip_y, color=lip_color, linewidth=1.5)
ax.fill_between(upper_lip_x, mouth_y - 0.005, upper_lip_y, color=lip_color, alpha=0.3)

# Нижняя губа — полная, тяжёлая
lower_lip_x = mouth_w * mouth_t
lower_lip_y = mouth_y - 0.04 * (1 - mouth_t**2)
ax.plot(lower_lip_x, lower_lip_y, color=lip_color, linewidth=1.5)
ax.fill_between(lower_lip_x, mouth_y, lower_lip_y, color=lip_color, alpha=0.25)

# Линия рта — опущенные уголки (печаль/усталость)
mouth_line_x = mouth_w * mouth_t
mouth_line_y = mouth_y - 0.015 * mouth_t**2  # вогнутая — уголки вниз
ax.plot(mouth_line_x, mouth_line_y, color=lip_shadow, linewidth=1.0)

# Опущенные уголки рта — «марионеточные» складки
for ms in [-1, 1]:
    mc_t = np.linspace(0, 1, 40)
    mc_x = ms * (mouth_w + 0.01 + 0.03 * mc_t)
    mc_y = mouth_y - 0.015 - 0.12 * mc_t - 0.02 * mc_t**2
    ax.plot(mc_x, mc_y, color=skin_deep, linewidth=0.8, alpha=0.35)

# Тень под нижней губой
ax.plot(np.linspace(-0.25, 0.25, 50), mouth_y - 0.05 - 0.015 * np.cos(np.pi*np.linspace(-0.25,0.25,50)/0.25),
        color=skin_shadow, linewidth=0.6, alpha=0.3)

# ============================================================
# ВЕНЕЦ ИЗ ЛАВРА
# ============================================================
crown_t = np.linspace(-2.5, 2.5, 300)
crown_r = 1.25 + 0.05 * np.sin(3 * crown_t)
crown_cx = crown_r * np.cos(crown_t * 0.8) * 0.9
crown_cy = crown_r * np.sin(crown_t * 0.8) * 0.6 + 0.75

ax.plot(crown_cx, crown_cy, color='#4a7a2a', linewidth=1.5, alpha=0.6)

for i in range(28):
    ci = int(i * 299 / 27)
    leaf_cx = crown_cx[ci]
    leaf_cy = crown_cy[ci]
    angle = crown_t[ci] * 0.8

    leaf_t = np.linspace(0, 1, 30)
    tangent = np.array([-np.sin(angle)*0.8, np.cos(angle)*0.6])
    tangent = tangent / (np.linalg.norm(tangent) + 1e-8)
    normal = np.array([-tangent[1], tangent[0]])

    lx = leaf_cx + 0.12 * leaf_t * tangent[0] + 0.035 * np.sin(np.pi*leaf_t) * normal[0]
    ly = leaf_cy + 0.12 * leaf_t * tangent[1] + 0.035 * np.sin(np.pi*leaf_t) * normal[1]
    ax.fill(lx, ly, color='#5a8a3a' if i % 3 else '#4a7a2a', alpha=0.7)

# ============================================================
# ПОДПИСЬ
# ============================================================
ax.text(0, -5.4, 'ПОРТРЕТ: УСТАЛЫЙ ИМПЕРАТОР',
        fontsize=13, ha='center', fontfamily='serif', color='#3a2a1a',
        fontweight='bold', fontstyle='italic',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#f0e8d8',
                  edgecolor='#8a6a4a', linewidth=1.5))

ax.text(0, -5.75,
        'Жирность: полином r(θ) + δ·cos(2θ)  |  Морщины: Σ sin(nθ+φ)  |  '
        'Тяжёлые веки: y = ey + h·sin(t) + δ  |  Глубокие глазницы: тёмные эллипсы',
        fontsize=6.5, ha='center', fontfamily='serif', color='#8a6a4a', fontstyle='italic')

rect = plt.Rectangle((-3.8, -5.9), 7.6, 12.85,
                       fill=False, edgecolor='#c0a880', linewidth=2, alpha=0.5)
ax.add_patch(rect)

plt.tight_layout()
plt.savefig('weary_emperor.png', dpi=200, bbox_inches='tight', facecolor='#f5efe0')
print("Сохранено: weary_emperor.png")
