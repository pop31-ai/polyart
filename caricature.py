import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch, Circle
import matplotlib.patches as mpatches

fig, ax = plt.subplots(1, 1, figsize=(12, 14), facecolor='#f5efe0')
ax.set_facecolor('#f5efe0')
ax.set_xlim(-4, 4)
ax.set_ylim(-5, 6)
ax.set_aspect('equal')
ax.axis('off')

phi = (1 + np.sqrt(5)) / 2

skin = '#e8d0b8'
skin_shadow = '#d0b8a0'
skin_light = '#f5e0d0'
hair_color = '#5a3a1a'
eye_color = '#4a6a7a'
lip_color = '#c07060'
brow_color = '#5a3a1a'
dark = '#2a1a0a'
gold = '#c8a040'
toga_white = '#f0ece4'
toga_shadow = '#d8d0c0'

t = np.linspace(0, 2*np.pi, 500)

# ===== ТОГА / ПЛАЩ РИМСКОГО ПАТРИЦИЯ =====
# Плечи и торс
body_x = np.array([-2.5, -2.2, -1.5, -1.0, -0.6, 0.6, 1.0, 1.5, 2.2, 2.5,
                     2.3, 1.8, 1.2, 0.8, -0.8, -1.2, -1.8, -2.3])
body_y = np.array([-3.5, -3.0, -2.5, -2.2, -2.0, -2.0, -2.2, -2.5, -3.0, -3.5,
                     -4.0, -4.5, -4.8, -5.0, -5.0, -4.8, -4.5, -4.0])
ax.fill(body_x, body_y, color=toga_white, alpha=0.9)
ax.plot(body_x, body_y, color=toga_shadow, linewidth=1.5)

# Складки тоги — полиномиальные кривые
for i in range(8):
    fold_t = np.linspace(0, 1, 80)
    fx = -1.5 + i * 0.4 + 0.15 * np.sin(3 * np.pi * fold_t)
    fy = -2.5 - 2.0 * fold_t
    ax.plot(fx, fy, color=toga_shadow, linewidth=0.8, alpha=0.5)

# Золотая фибула (булавка) на плече
fib_t = np.linspace(0, 2*np.pi, 100)
fib_x = -1.5 + 0.15 * np.cos(fib_t)
fib_y = -2.3 + 0.15 * np.sin(fib_t)
ax.fill(fib_x, fib_y, color=gold, alpha=0.9)
ax.plot(fib_x, fib_y, color='#8a6020', linewidth=1.5)
# Лучи фибулы
for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
    ax.plot([-1.5, -1.5 + 0.25*np.cos(angle)],
            [-2.3, -2.3 + 0.25*np.sin(angle)],
            color=gold, linewidth=1.0, alpha=0.5)

# ===== ШЕЯ — мощная, шаржированно толстая =====
neck_t = np.linspace(0, 1, 100)
for ns in [-1, 1]:
    nx = ns * (0.35 + 0.15 * neck_t)
    ny = -1.8 - 0.5 * neck_t
    ax.plot(nx, ny, color=skin_shadow, linewidth=1.2, alpha=0.5)

# Заливка шеи
neck_fill_l = -0.35 - 0.15 * neck_t
neck_fill_r = 0.35 + 0.15 * neck_t
neck_fill_y = -1.8 - 0.5 * neck_t
ax.fill_betweenx(neck_fill_y, neck_fill_l, neck_fill_r, color=skin, alpha=0.9)

# Складки на шее
for i in range(3):
    wrinkle_y = -2.0 - i * 0.12
    wrinkle_t = np.linspace(-0.3, 0.3, 50)
    ax.plot(wrinkle_t, wrinkle_y + 0.01 * np.sin(5 * wrinkle_t),
            color=skin_shadow, linewidth=0.8, alpha=0.4)

# ===== ГОЛОВА — ГРАНДИОЗНЫЙ ЛЫСЫЙ КУПОЛ =====
# Основной овал — шаржированно увеличенный
head_a = 1.3  # полуось ширины (增大)
head_b = 1.5  # полуось высоты

head_t = np.linspace(0, 2*np.pi, 500)
hx = head_a * np.cos(head_t)
hy = head_b * np.sin(head_t) - 0.3  # смещение вниз

# Заливка головы
ax.fill(hx, hy, color=skin, alpha=0.95)

# ===== БЛЕСК ЛЫСИНЫ — математическое свечение =====
# Концентрические эллипсы блика
for i in range(8):
    shine_r = 0.9 - i * 0.08
    shine_a = shine_r * 0.7
    shine_b = shine_r * 0.5
    shine_t = np.linspace(0, 2*np.pi, 200)
    sx = -0.1 + shine_a * np.cos(shine_t)
    sy = 0.3 + shine_b * np.sin(shine_t) - 0.3
    alpha = 0.08 + i * 0.01
    ax.fill(sx, sy, color='white', alpha=alpha)

# Главный блик — эллипс
blik = Ellipse((-0.1, 0.0), 0.6, 0.35, angle=15,
               facecolor='white', alpha=0.25, edgecolor='none')
ax.add_patch(blik)
blik2 = Ellipse((-0.05, 0.05), 0.3, 0.18, angle=10,
                facecolor='white', alpha=0.3, edgecolor='none')
ax.add_patch(blik2)

# Контур головы
ax.plot(hx, hy, color=skin_shadow, linewidth=1.5)

# Тень справа и снизу
shadow_mask = (hx > 0) | (hy < -0.8)
ax.fill(hx[shadow_mask], hy[shadow_mask], color=skin_shadow, alpha=0.15)

# ===== УШИ — шаржированно большие =====
for ear_sign in [-1, 1]:
    ear_x = ear_sign * (head_a - 0.05)
    ear_y_center = -0.1
    
    # Внешний контур уха — увеличенный
    ear_t = np.linspace(-np.pi*0.75, np.pi*0.75, 100)
    ear_r = 0.35 + 0.05 * np.cos(2*ear_t)  # большие уши!
    ear_cx = ear_x + ear_sign * ear_r * np.cos(ear_t)
    ear_cy = ear_y_center + 0.45 * np.sin(ear_t)
    ax.fill(ear_cx, ear_cy, color=skin, alpha=0.95)
    ax.plot(ear_cx, ear_cy, color=skin_shadow, linewidth=1.2)
    
    # Мочка уха — увеличенная
    mouch_t = np.linspace(0, np.pi, 50)
    mx = ear_x + ear_sign * 0.35 * np.cos(mouch_t)
    my = ear_y_center - 0.3 + 0.15 * np.sin(mouch_t)
    ax.plot(mx, my, color=skin_shadow, linewidth=1.0)
    
    # Внутренняя спираль
    ear_spir_t = np.linspace(0, 2.5*np.pi, 150)
    esr = 0.06 + 0.03 * ear_spir_t / (2.5*np.pi)
    esx = ear_x + ear_sign * esr * np.cos(ear_spir_t)
    esy = ear_y_center + esr * np.sin(ear_spir_t)
    ax.plot(esx, esy, color=skin_shadow, linewidth=0.8, alpha=0.5)

# ===== БРОВИ — густые, шаржированно выразительные =====
brow_t = np.linspace(-1, 1, 100)
for bx_sign in [-1, 1]:
    bx_c = bx_sign * 0.55
    brow_x = bx_c + 0.3 * brow_t
    brow_y = 0.35 - 0.06 * brow_t**2 + bx_sign * 0.04 * brow_t
    ax.plot(brow_x, brow_y, color=brow_color, linewidth=3.0,
            solid_capstyle='round')
    # Второй слой — густота
    ax.plot(brow_x, brow_y + 0.02, color=brow_color, linewidth=1.5,
            solid_capstyle='round', alpha=0.5)

# Морщинки на лбу — от удивления лысиной
for i in range(4):
    fw_t = np.linspace(-0.3, 0.3, 40)
    fw_x = fw_t
    fw_y = 0.8 + 0.04*i + 0.02 * np.sin(8*fw_t)
    ax.plot(fw_x, fw_y, color=skin_shadow, linewidth=0.7, alpha=0.35)

# ===== ГЛАЗА — шаржированно большие, выразительные =====
eye_w = 0.28  # увеличенные
eye_h = 0.12

for ex_sign in [-1, 1]:
    ex_c = ex_sign * 0.55
    ey_c = 0.2
    
    # Верхнее веко
    eye_t = np.linspace(0, np.pi, 100)
    upper_x = ex_c + eye_w * np.cos(eye_t)
    upper_y = ey_c + eye_h * np.sin(eye_t)
    ax.plot(upper_x, upper_y, color=brow_color, linewidth=2.0)
    
    # Нижнее веко
    lower_x = ex_c + eye_w * np.cos(eye_t)
    lower_y = ey_c - eye_h * 0.5 * np.sin(eye_t)
    ax.plot(lower_x, lower_y, color=brow_color, linewidth=1.2, alpha=0.7)
    
    # Белок
    full_t = np.linspace(0, 2*np.pi, 100)
    white_x = ex_c + eye_w * np.cos(full_t)
    white_upper = ey_c + eye_h * np.sin(full_t)
    white_lower = ey_c - eye_h * 0.5 * np.sin(full_t)
    ax.fill_between(white_x, white_lower, white_upper, color='white', alpha=0.95)
    
    # Радужка — большая
    iris_r = eye_h * 0.55
    iris_x = ex_c + iris_r * np.cos(full_t)
    iris_y = ey_c + iris_r * 0.85 * np.sin(full_t)
    ax.fill(iris_x, iris_y, color=eye_color, alpha=0.9)
    
    # Зрачок
    pupil_r = iris_r * 0.45
    pupil_x = ex_c + pupil_r * np.cos(full_t)
    pupil_y = ey_c + pupil_r * 0.85 * np.sin(full_t)
    ax.fill(pupil_x, pupil_y, color=dark, alpha=0.95)
    
    # Блик — яркий!
    ax.plot(ex_c + 0.04, ey_c + 0.04, 'o', color='white', markersize=4, alpha=0.9)
    ax.plot(ex_c - 0.02, ey_c + 0.06, 'o', color='white', markersize=2, alpha=0.7)
    
    # Морщинки «гусиные лапки» — шарж
    for i in range(3):
        crow_t = np.linspace(0, 1, 30)
        crow_x = ex_c + ex_sign * (eye_w + 0.02 + 0.06*crow_t)
        crow_y = ey_c - 0.02 + (i-1)*0.04 - 0.03*crow_t
        ax.plot(crow_x, crow_y, color=skin_shadow, linewidth=0.6, alpha=0.35)

# ===== НОС — шаржированно крупный, круглый =====
# Переносица
nose_bridge_t = np.linspace(0, 1, 80)
nose_bx = 0.02 * nose_bridge_t**2
nose_by = 0.25 - 0.35 * nose_bridge_t
ax.plot(nose_bx, nose_by, color=skin_shadow, linewidth=1.2, alpha=0.5)

# Кончик носа — большой, круглый
nose_tip_t = np.linspace(0, 2*np.pi, 100)
nose_tip_r = 0.18  # шаржированно большой
nt_x = 0.03 + nose_tip_r * np.cos(nose_tip_t)
nt_y = -0.12 + nose_tip_r * 0.7 * np.sin(nose_tip_t)
ax.fill(nt_x, nt_y, color=skin, alpha=0.9)
ax.plot(nt_x, nt_y, color=skin_shadow, linewidth=1.0, alpha=0.6)

# Ноздри — большие
for ns in [-1, 1]:
    nostril_t = np.linspace(0, 2*np.pi, 50)
    ns_x = ns * 0.1 + 0.06 * np.cos(nostril_t)
    ns_y = -0.15 + 0.04 * np.sin(nostril_t)
    ax.fill(ns_x, ns_y, color=skin_shadow, alpha=0.3)

# Блик на носу
nose_blik = Ellipse((0.05, -0.05), 0.1, 0.06, angle=20,
                     facecolor='white', alpha=0.2, edgecolor='none')
ax.add_patch(nose_blik)

# ===== ЩЁКИ — румяные шаржи =====
for cs in [-1, 1]:
    cheek = Ellipse((cs * 0.7, -0.15), 0.4, 0.25, angle=0,
                     facecolor='#e0a090', alpha=0.2, edgecolor='none')
    ax.add_patch(cheek)

# ===== РОТ — шаржированно выразительный, улыбка =====
mouth_y = -0.55
mouth_w = 0.55  # широкая улыбка

# Верхняя губа — лук Купидона
mouth_t = np.linspace(-1, 1, 100)
upper_lip_x = mouth_w * mouth_t
upper_lip_y = mouth_y + 0.06 * (1 - mouth_t**2) - 0.025 * np.abs(mouth_t)
ax.plot(upper_lip_x, upper_lip_y, color=lip_color, linewidth=2.0)
ax.fill_between(upper_lip_x, mouth_y, upper_lip_y, color=lip_color, alpha=0.4)

# Нижняя губа — полная
lower_lip_x = mouth_w * mouth_t
lower_lip_y = mouth_y - 0.08 * (1 - mouth_t**2)
ax.plot(lower_lip_x, lower_lip_y, color=lip_color, linewidth=2.0)
ax.fill_between(lower_lip_x, mouth_y, lower_lip_y, color=lip_color, alpha=0.35)

# Линия рта — улыбка
smile_x = mouth_w * mouth_t
smile_y = mouth_y + 0.01 * np.sin(np.pi * mouth_t)
ax.plot(smile_x, smile_y, color='#8a4a3a', linewidth=1.5)

# Зубы — видны от улыбки!
teeth_t = np.linspace(-0.7, 0.7, 100)
teeth_x = (mouth_w - 0.05) * teeth_t
teeth_y_top = mouth_y + 0.04
teeth_y_bot = mouth_y - 0.02
ax.fill_between(teeth_x, teeth_y_bot, teeth_y_top, color='white', alpha=0.8)
ax.plot(teeth_x, [teeth_y_top]*100, color='#e0d0c0', linewidth=0.5)

# Носогубные складки — глубокие от улыбки
for ns in [-1, 1]:
    nas_t = np.linspace(0, 1, 60)
    nas_x = ns * (0.12 + 0.2 * nas_t**1.3)
    nas_y = -0.15 - 0.2 * nas_t - 0.05 * nas_t**2
    ax.plot(nas_x, nas_y, color=skin_shadow, linewidth=1.0, alpha=0.45)

# Морщинки вокруг рта
for i in range(2):
    smile_w_t = np.linspace(0, 1, 40)
    for ws in [-1, 1]:
        sw_x = ws * (mouth_w + 0.05 + 0.05*smile_w_t)
        sw_y = mouth_y + 0.01 + (i*0.03 - 0.01) * smile_w_t
        ax.plot(sw_x, sw_y, color=skin_shadow, linewidth=0.5, alpha=0.3)

# ===== ПОДБОРОДОК — двойной, шарж =====
chin_t = np.linspace(0, np.pi, 100)
chin_x = 0.5 * np.cos(chin_t)
chin_y = -1.3 + 0.15 * np.sin(chin_t)
ax.fill(chin_x, chin_y, color=skin, alpha=0.9)

# Второй подбородок
chin2_t = np.linspace(0, np.pi, 80)
chin2_x = 0.4 * np.cos(chin2_t)
chin2_y = -1.15 + 0.1 * np.sin(chin2_t)
ax.plot(chin2_x, chin2_y, color=skin_shadow, linewidth=0.8, alpha=0.4)

# Складка под подбородком
ax.plot([-0.3, 0.3], [-1.15, -1.15], color=skin_shadow, linewidth=0.8, alpha=0.4)

# ===== КОРОНА / ВЕНОК ИЗ ЛАВРА =====
# Лавровый венок поверх лысины
wreath_t = np.linspace(0, 2*np.pi, 300)
wreath_r = 1.15 + 0.05 * np.sin(10 * wreath_t)
wx = wreath_r * np.cos(wreath_t)
wy = wreath_r * np.sin(wreath_t) * 0.85 - 0.3

# Листья венка
for i in range(24):
    angle = i * 2 * np.pi / 24
    leaf_x = 1.15 * np.cos(angle)
    leaf_y = (1.15 * 0.85) * np.sin(angle) - 0.3
    
    leaf_t = np.linspace(0, 1, 30)
    leaf_len = 0.15
    leaf_w = 0.04
    
    # Направление от центра
    nx = np.cos(angle)
    ny = np.sin(angle) * 0.85
    # Перпендикуляр
    px = -ny
    py = nx
    
    lx = leaf_x + leaf_len * leaf_t * nx + leaf_w * np.sin(np.pi*leaf_t) * px
    ly = leaf_y + leaf_len * leaf_t * ny + leaf_w * np.sin(np.pi*leaf_t) * py
    ax.fill(lx, ly, color='#5a8a3a', alpha=0.7)
    ax.plot(lx, ly, color='#3a6a2a', linewidth=0.5, alpha=0.5)

# ===== ШАРЖИРОВАННЫЕ ЭЛЕМЕНТЫ =====
# Монета в руке (как римский император)
coin_t = np.linspace(0, 2*np.pi, 100)
coin_x = 2.0 + 0.4 * np.cos(coin_t)
coin_y = -3.5 + 0.4 * np.sin(coin_t)
ax.fill(coin_x, coin_y, color=gold, alpha=0.85)
ax.plot(coin_x, coin_y, color='#8a6020', linewidth=1.5)

# Профиль на монете (миниатюрный)
mini_profile_t = np.linspace(0, 1, 50)
mp_x = 2.0 + 0.15 * np.cos(mini_profile_t * np.pi)
mp_y = -3.5 + 0.2 * np.sin(mini_profile_t * np.pi)
ax.plot(mp_x, mp_y, color='#8a6020', linewidth=1.0)

# Надпись "SPQR" на монете
ax.text(2.0, -3.85, 'SPQR', fontsize=6, ha='center', color='#8a6020',
        fontfamily='serif', fontweight='bold')

# ===== МАТЕМАТИЧЕСКИЕ ФОРМУЛЫ РЯДОМ =====
# Стрелка от формулы к лысине
ax.annotate('', xy=(-0.1, 0.8), xytext=(-2.5, 2.5),
            arrowprops=dict(arrowstyle='->', color='#c0a080', lw=1.2))

ax.text(-3.5, 2.8, 'r(θ) = R + ε·cos(nθ)\nКупол: эллипс\na = 1.3, b = 1.5',
        fontsize=8, fontfamily='serif', color='#8a6a4a',
        fontstyle='italic',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#f0e8d8',
                  edgecolor='#c0a880', alpha=0.8))

# Формула блеска
ax.annotate('', xy=(-0.05, 0.0), xytext=(-2.5, 0.5),
            arrowprops=dict(arrowstyle='->', color='#c0a080', lw=1.0))
ax.text(-3.5, 0.3, 'Блик: Σ αᵢ·e^(-r²/σᵢ²)\nГауссовы пики',
        fontsize=7, fontfamily='serif', color='#8a6a4a',
        fontstyle='italic',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#f0e8d8',
                  edgecolor='#c0a880', alpha=0.7))

# Подпись
ax.text(0, -4.7, 'ШАРЖ: «ИМПЕРАТОР МАТЕМАТИКУС»',
        fontsize=14, ha='center', fontfamily='serif', color='#3a2a1a',
        fontweight='bold', fontstyle='italic',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#f0e8d8',
                  edgecolor='#8a6a4a', linewidth=2))

ax.text(0, -5.0, 'φ = 1.618...  |  Полиномы и конические сечения  |  Канон Поликлета',
        fontsize=8, ha='center', fontfamily='serif', color='#8a6a4a',
        fontstyle='italic')

# Рамка
rect_border = plt.Rectangle((-3.8, -4.9), 7.6, 10.8,
                              fill=False, edgecolor='#c0a880',
                              linewidth=2, alpha=0.5)
ax.add_patch(rect_border)

plt.tight_layout()
plt.savefig('caricature.png', dpi=200, bbox_inches='tight', facecolor='#f5efe0')
print("Сохранено: caricature.png")
