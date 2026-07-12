import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Arc, FancyArrowPatch

phi = (1 + np.sqrt(5)) / 2
phi_inv = 1 / phi
phi2_inv = 1 / phi**2

fig, axes = plt.subplots(1, 3, figsize=(20, 10), facecolor='#f5efe0')
fig.suptitle('Аполонические Лица: Математика Красоты Древней Греции',
             fontsize=16, fontfamily='serif', color='#2a1a0a', y=0.97, fontstyle='italic')

for ax in axes:
    ax.set_facecolor('#f5efe0')
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.4, 1.4)
    ax.set_aspect('equal')
    ax.axis('off')

skin = '#e8d0b8'
skin_shadow = '#d0b8a0'
skin_light = '#f0dcc8'
hair_color = '#6a4a2a'
eye_color = '#4a6a7a'
lip_color = '#c07060'
brow_color = '#5a3a1a'
line_color = '#8a6a4a'
dark = '#2a1a0a'

def draw_apollonian_face(ax, mood='serene', tilt=0):
    """Аполоническое лицо по канонам Поликлета и Лизиппа"""
    
    # === ОВАЛ ЛИЦА — эллипс по золотому сечению ===
    face_a = 0.5   # полуось ширины
    face_b = face_a * phi  # полуось высоты = φ
    
    face_t = np.linspace(0, 2*np.pi, 500)
    fx = face_a * np.cos(face_t)
    fy = face_b * np.sin(face_t)
    
    # Поворот лица
    cos_t, sin_t = np.cos(tilt), np.sin(tilt)
    fx_r = fx * cos_t - fy * sin_t
    fy_r = fx * sin_t + fy * cos_t
    
    ax.fill(fx_r, fy_r, color=skin, alpha=0.95)
    ax.plot(fx_r, fy_r, color=skin_shadow, linewidth=1.2)
    
    # Тень на лице (левая сторона — полиномиальная огибающая)
    shadow_t = np.linspace(-np.pi*0.8, np.pi*0.8, 300)
    sh_a = face_a * 0.95
    sh_b = face_b * 0.95
    sh_x = sh_a * np.cos(shadow_t)
    sh_y = sh_b * np.sin(shadow_t)
    sh_mask = sh_x < -0.1
    ax.fill(sh_x[sh_mask], sh_y[sh_mask], color=skin_shadow, alpha=0.2)
    
    # === ГЛАЗА — миндалевидные (два пересекающихся эллиптических дуги) ===
    eye_w = phi2_inv * 0.5  # ширина глаза
    eye_h = eye_w * 0.4     # высота глаза
    
    for ex_sign in [-1, 1]:
        ex_center = ex_sign * phi_inv * 0.25  # межглазовое расстояние = 1/φ
        ey_center = phi_inv * 0.25  # высота центра глаза
        
        # Верхнее веко — дуга эллипса
        eye_t = np.linspace(0, np.pi, 100)
        upper_x = ex_center + eye_w * np.cos(eye_t)
        upper_y = ey_center + eye_h * np.sin(eye_t)
        ax.plot(upper_x, upper_y, color=brow_color, linewidth=1.5)
        
        # Нижнее веко — более плоская дуга
        lower_x = ex_center + eye_w * np.cos(eye_t)
        lower_y = ey_center - eye_h * 0.55 * np.sin(eye_t)
        ax.plot(lower_x, lower_y, color=brow_color, linewidth=1.0, alpha=0.7)
        
        # Заливка белка
        full_eye_t = np.linspace(0, 2*np.pi, 100)
        white_x = ex_center + eye_w * np.cos(full_eye_t)
        white_upper = ey_center + eye_h * np.sin(full_eye_t)
        white_lower = ey_center - eye_h * 0.55 * np.sin(full_eye_t)
        ax.fill_between(white_x, white_lower, white_upper, color='white', alpha=0.9)
        
        # Радужка — круг
        iris_t = np.linspace(0, 2*np.pi, 80)
        iris_r = eye_h * 0.45
        iris_x = ex_center + iris_r * np.cos(iris_t)
        iris_y = ey_center + iris_r * 0.9 * np.sin(iris_t)
        ax.fill(iris_x, iris_y, color=eye_color, alpha=0.9)
        
        # Зрачок
        pupil_r = iris_r * 0.45
        pupil_x = ex_center + pupil_r * np.cos(iris_t)
        pupil_y = ey_center + pupil_r * 0.9 * np.sin(iris_t)
        ax.fill(pupil_x, pupil_y, color=dark, alpha=0.95)
        
        # Блик
        ax.plot(ex_center + pupil_r*0.3, ey_center + pupil_r*0.3,
                'o', color='white', markersize=2, alpha=0.8)
        
        # === ВЕРХНЕЕ ВЕКО — линия ===
        lid_t = np.linspace(-0.2, np.pi+0.2, 100)
        lid_x = ex_center + (eye_w + 0.01) * np.cos(lid_t)
        lid_y = ey_center + (eye_h + 0.015) * np.sin(lid_t)
        ax.plot(lid_x, lid_y, color=brow_color, linewidth=1.8)
    
    # === БРОВИ — параболы ===
    brow_t = np.linspace(-1, 1, 100)
    brow_y_center = phi_inv * 0.4  # высота бровей
    
    for bx_sign in [-1, 1]:
        bx_center = bx_sign * phi_inv * 0.25
        # Парабола: y = a*x^2 + k
        if mood == 'serene':
            brow_a = -0.08
        elif mood == 'pathos':
            brow_a = 0.12  # нахмуренные
        else:
            brow_a = -0.05
        
        brow_x = bx_center + 0.2 * brow_t
        brow_y = brow_y_center + brow_a * brow_t**2
        
        # Наклон бровей
        if mood == 'pathos':
            brow_y += bx_sign * 0.03 * brow_t
        
        ax.plot(brow_x, brow_y, color=brow_color, linewidth=2.0,
                solid_capstyle='round')
    
    # === НОС — полиномиальные кривые ===
    nose_bridge_t = np.linspace(0, 1, 80)
    # Переносица — слегка изогнутая линия
    nose_x = -0.02 * nose_bridge_t**2
    nose_y = phi_inv * 0.35 - 0.27 * nose_bridge_t  # длина носа = 1/3 лица
    ax.plot(nose_x, nose_y, color=skin_shadow, linewidth=1.2, alpha=0.6)
    
    # Кончик носа — полиномиальная кривая
    nose_tip_t = np.linspace(-1, 1, 60)
    nose_tip_x = 0.06 * nose_tip_t
    nose_tip_y = -0.27 + 0.02 * np.cos(np.pi * nose_tip_t)
    ax.plot(nose_tip_x, nose_tip_y, color=skin_shadow, linewidth=1.0, alpha=0.5)
    
    # Ноздри — маленькие дуги
    for ns in [-1, 1]:
        nostril_t = np.linspace(0, np.pi, 30)
        ns_x = ns * 0.04 + 0.025 * np.cos(nostril_t)
        ns_y = -0.27 + 0.015 * np.sin(nostril_t)
        ax.plot(ns_x, ns_y, color=skin_shadow, linewidth=0.8, alpha=0.4)
    
    # === РТУБ — "Лук Купидона" (две параболы) ===
    mouth_y = -0.433  # позиция рта по φ
    mouth_w = phi2_inv * 0.5  # ширина рта
    
    # Верхняя губа — две параболы (Cupid's bow)
    mouth_t = np.linspace(-1, 1, 100)
    
    # Левая половина верхней губы
    upper_l_x = -mouth_w/2 * mouth_t
    if mood == 'serene':
        upper_l_y = mouth_y + 0.035 * (1 - mouth_t**2)
    elif mood == 'pathos':
        upper_l_y = mouth_y + 0.02 * (1 - mouth_t**2) - 0.01 * mouth_t
    else:
        upper_l_y = mouth_y + 0.03 * (1 - mouth_t**2)
    
    # Верхняя губа — с вырезом
    upper_x = np.concatenate([
        -mouth_w/2 * mouth_t[::-1],
        mouth_w/2 * mouth_t
    ])
    upper_y = np.concatenate([
        mouth_y + 0.035 * (1 - mouth_t[::-1]**2) - 0.015 * mouth_t[::-1],
        mouth_y + 0.035 * (1 - mouth_t**2) + 0.015 * mouth_t
    ])
    ax.plot(upper_x, upper_y, color=lip_color, linewidth=1.5)
    ax.fill(upper_x, upper_y, color=lip_color, alpha=0.5)
    
    # Нижняя губа — одна парабола
    lower_x = mouth_w * mouth_t
    lower_y = mouth_y - 0.04 * (1 - mouth_t**2)
    ax.plot(lower_x, lower_y, color=lip_color, linewidth=1.5)
    ax.fill_between(lower_x, mouth_y, lower_y, color=lip_color, alpha=0.4)
    
    # Линия рта
    mouth_line_x = mouth_w * mouth_t
    mouth_line_y = mouth_y + 0.005 * np.sin(2 * np.pi * mouth_t)
    ax.plot(mouth_line_x, mouth_line_y, color='#8a4a3a', linewidth=1.0)
    
    # === ЛИНИИ МИМИКИ ===
    if mood == 'pathos':
        # Межбровная складка — две параболы к глаголище
        furrow_t = np.linspace(-0.08, 0.08, 30)
        ax.plot(furrow_t, 0.35 + 80 * furrow_t**2, color=skin_shadow, linewidth=1.0, alpha=0.5)
        ax.plot(furrow_t, 0.38 + 60 * furrow_t**2, color=skin_shadow, linewidth=0.8, alpha=0.4)
        
        # Носогубные складки — катenary/кубические
        nas_t = np.linspace(0, 1, 60)
        for ns_sign in [-1, 1]:
            nas_x = ns_sign * (0.06 + 0.12 * nas_t**1.5)
            nas_y = -0.27 - 0.12 * nas_t - 0.03 * nas_t**2
            ax.plot(nas_x, nas_y, color=skin_shadow, linewidth=0.8, alpha=0.4)
        
        # Складки под глазами
        for ex_sign in [-1, 1]:
            ex_c = ex_sign * phi_inv * 0.25
            bag_t = np.linspace(-0.15, 0.15, 40)
            bag_x = ex_c + bag_t
            bag_y = 0.25 - 0.02 - 0.08 * bag_t**2
            ax.plot(bag_x, bag_y, color=skin_shadow, linewidth=0.6, alpha=0.3)
    else:
        # Спокойные носогубные — лёгкие
        nas_t = np.linspace(0, 1, 60)
        for ns_sign in [-1, 1]:
            nas_x = ns_sign * (0.05 + 0.08 * nas_t**2)
            nas_y = -0.27 - 0.1 * nas_t
            ax.plot(nas_x, nas_y, color=skin_shadow, linewidth=0.5, alpha=0.3)
    
    # === ВОЛОСЫ — золотая спираль (logarithmic spiral на основе φ) ===
    # Локоны Аполлона
    hair_t = np.linspace(0, 2*np.pi, 500)
    hair_base_r = face_a + 0.05
    
    # Внешний контур волос
    hair_r = hair_base_r + 0.15 + 0.05 * np.cos(3*hair_t)
    hair_x = hair_r * np.cos(hair_t)
    hair_y = hair_r * np.sin(hair_t)
    
    # Обрезаем по лицу
    mask_top = hair_y > -0.1
    mask_sides = np.abs(hair_x) > face_a * 0.8
    mask = mask_top | mask_sides
    mask = mask & (hair_y < face_b + 0.25)
    
    ax.fill(hair_x[mask], hair_y[mask], color=hair_color, alpha=0.85)
    
    # Спиральные локоны (золотая спираль r = a * φ^(2θ/π))
    spiral_params = [
        (-0.35, 0.7, 0.02, 0),
        (0.35, 0.7, 0.02, np.pi),
        (-0.4, 0.3, 0.015, 0.5),
        (0.4, 0.3, 0.015, np.pi-0.5),
        (-0.3, -0.1, 0.02, 1.0),
        (0.3, -0.1, 0.02, np.pi-1.0),
        (-0.15, 0.9, 0.02, 0.3),
        (0.15, 0.9, 0.02, np.pi-0.3),
    ]
    
    for sx, sy, sa, s_offset in spiral_params:
        spir_t = np.linspace(0, 3*np.pi, 200)
        spir_r = sa * phi**(2*spir_t/np.pi)
        spir_x = sx + spir_r * np.cos(spir_t + s_offset)
        spir_y = sy - spir_r * np.sin(spir_t + s_offset) * 0.7
        ax.plot(spir_x, spir_y, color=hair_color, linewidth=1.2, alpha=0.7)
    
    # Чёлка — полиномиальные волны
    bang_t = np.linspace(-0.4, 0.4, 100)
    bang_y = face_b - 0.05 + 0.08 * np.cos(4 * np.pi * bang_t)
    ax.fill_between(bang_t, face_b + 0.2, bang_y, color=hair_color, alpha=0.75)
    
    # === УШИ — полиномиальные спирали ===
    for ear_sign in [-1, 1]:
        ear_x = ear_sign * (face_a - 0.02)
        ear_y_center = 0.05
        
        # Контур уха
        ear_t = np.linspace(-np.pi*0.7, np.pi*0.7, 100)
        ear_r = 0.12 + 0.02 * np.cos(2*ear_t)
        ear_contour_x = ear_x + ear_sign * ear_r * np.cos(ear_t)
        ear_contour_y = ear_y_center + 0.15 * np.sin(ear_t)
        ax.plot(ear_contour_x, ear_contour_y, color=skin_shadow, linewidth=1.0, alpha=0.6)
        
        # Внутренняя спираль уха
        ear_spir_t = np.linspace(0, 2*np.pi, 80)
        ear_spir_r = 0.04 + 0.01 * ear_spir_t / (2*np.pi)
        ear_spir_x = ear_x + ear_sign * ear_spir_r * np.cos(ear_spir_t)
        ear_spir_y = ear_y_center + ear_spir_r * np.sin(ear_spir_t)
        ax.plot(ear_spir_x, ear_spir_y, color=skin_shadow, linewidth=0.6, alpha=0.4)
    
    # === ШЕЯ — полиномиальные кривые ===
    neck_t = np.linspace(0, 1, 80)
    for ns in [-1, 1]:
        neck_x = ns * (0.12 + 0.03 * neck_t)
        neck_y = -face_b + 0.1 - 0.3 * neck_t
        ax.plot(neck_x, neck_y, color=skin_shadow, linewidth=1.0, alpha=0.5)
    
    # === СВЕЧЕНИЕ (нимб Аполлона) ===
    nimbus_t = np.linspace(0, 2*np.pi, 300)
    nimbus_r = 0.7 + 0.03 * np.sin(12*nimbus_t)
    nimbus_x = nimbus_r * np.cos(nimbus_t)
    nimbus_y = nimbus_r * np.sin(nimbus_t) + 0.1
    ax.plot(nimbus_x, nimbus_y, color='#e8c860', linewidth=1.5, alpha=0.4)
    for nr in np.linspace(0.72, 0.85, 5):
        nr_t = np.linspace(0, 2*np.pi, 200)
        ax.plot(nr * np.cos(nr_t), nr * np.sin(nr_t) + 0.1,
                color='#e8c860', linewidth=0.5, alpha=0.15)

def draw_profile_face(ax, mood='noble'):
    """Профиль — как на монетах и камеях"""
    
    # Контур профиля — полиномиальная кривая
    profile_t = np.linspace(0, 1, 500)
    
    # Лоб → переносица → нос → губы → подбородок
    # Сплайн из полиномов
    seg1_t = np.linspace(0, 0.2, 100)  # лоб
    seg2_t = np.linspace(0.2, 0.35, 100)  # переносица
    seg3_t = np.linspace(0.35, 0.55, 100)  # нос
    seg4_t = np.linspace(0.55, 0.75, 100)  # губы
    seg5_t = np.linspace(0.75, 1.0, 100)  # подбородок
    
    # Лоб — выпуклая дуга
    p1x = -0.05 - 0.1 * seg1_t + 0.05 * seg1_t**2
    p1y = 0.8 - 0.4 * seg1_t
    
    # Переносица — впадина
    p2x = -0.1 + 0.03 * np.sin(np.pi * (seg2_t-0.2)/0.15)
    p2y = 0.8 - 0.4*0.2 - 0.4*(seg2_t-0.2)/0.15
    
    # Нос — выпуклый полином
    p3x = -0.07 + 0.25 * (seg3_t-0.35)/0.2 + 0.05*((seg3_t-0.35)/0.2)**2
    p3y = 0.8 - 0.4*0.35 - 0.35*(seg3_t-0.35)/0.2
    
    # Губы — лук купидона
    p4x = 0.18 + 0.02 * np.sin(3*np.pi*(seg4_t-0.55)/0.2)
    p4y = 0.8 - 0.4*0.55 - 0.25*(seg4_t-0.55)/0.2
    
    # Подбородок — выпуклый
    p5x = 0.2 - 0.05*((seg5_t-0.75)/0.25)**2 - 0.15*((seg5_t-0.75)/0.25)
    p5y = 0.8 - 0.4*0.75 - 0.35*(seg5_t-0.75)/0.25
    
    all_x = np.concatenate([p1x, p2x, p3x, p4x, p5x])
    all_y = np.concatenate([p1y, p2y, p3y, p4y, p5y])
    
    # Заливка лица
    face_back_x = np.concatenate([all_x, [0.2, 0.2], all_x[::-1]])
    face_back_y = np.concatenate([all_y, [-0.6, 0.9], all_y[::-1]])
    ax.fill(face_back_x, face_back_y, color=skin, alpha=0.95)
    ax.plot(all_x, all_y, color=skin_shadow, linewidth=1.5)
    
    # Глаз — вид сбоку (треугольник/мигдалина)
    eye_cx = -0.02
    eye_cy = 0.4
    eye_t = np.linspace(0, np.pi, 80)
    eye_upper_x = eye_cx + 0.08 * np.cos(eye_t)
    eye_upper_y = eye_cy + 0.035 * np.sin(eye_t)
    eye_lower_x = eye_cx + 0.08 * np.cos(eye_t)
    eye_lower_y = eye_cy - 0.02 * np.sin(eye_t)
    ax.fill_between(eye_upper_x, eye_lower_y, eye_upper_y, color='white', alpha=0.9)
    ax.plot(eye_upper_x, eye_upper_y, color=brow_color, linewidth=1.5)
    ax.plot(eye_lower_x, eye_lower_y, color=brow_color, linewidth=1.0, alpha=0.7)
    
    # Радужка (вид сбоку — узкий эллипс)
    iris_t = np.linspace(0, 2*np.pi, 60)
    iris_x = eye_cx + 0.025 + 0.03 * np.cos(iris_t)
    iris_y = eye_cy + 0.03 * np.sin(iris_t)
    ax.fill(iris_x, iris_y, color=eye_color, alpha=0.9)
    
    # Зрачок
    pupil_x = eye_cx + 0.025 + 0.012 * np.cos(iris_t)
    pupil_y = eye_cy + 0.012 * np.sin(iris_t)
    ax.fill(pupil_x, pupil_y, color=dark, alpha=0.95)
    
    # Бровь — парабола
    brow_t = np.linspace(-1, 1, 80)
    brow_x = -0.04 + 0.12 * brow_t
    brow_y = 0.48 - 0.03 * brow_t**2 + 0.02 * brow_t
    ax.plot(brow_x, brow_y, color=brow_color, linewidth=2.0)
    
    # Волосы — спиральные локоны
    hair_base_x = np.concatenate([[-0.05], all_x[:50], [-0.05]])
    hair_base_y = np.concatenate([[0.95], all_y[:50], [0.95]])
    
    # Объём волос
    hair_fill_x = np.concatenate([
        np.linspace(-0.3, -0.05, 50),
        all_x[:80],
        np.linspace(0.2, 0.2, 10),
        np.linspace(0.2, -0.3, 50)
    ])
    hair_fill_y = np.concatenate([
        np.linspace(0.95, 0.85, 50),
        all_y[:80] + 0.08,
        np.linspace(0.7, 0.7, 10),
        np.linspace(0.8, 0.95, 50)
    ])
    ax.fill(hair_fill_x, hair_fill_y, color=hair_color, alpha=0.8)
    
    # Спиральные локоны на затылке
    for si in range(5):
        s_offset = si * 0.6
        s_scale = 0.015 + 0.005 * si
        spir_t = np.linspace(0, 3*np.pi, 150)
        sr = s_scale * phi**(2*spir_t/np.pi)
        sx = -0.15 - 0.05*si + sr * np.cos(spir_t + s_offset)
        sy = 0.6 - 0.1*si - sr * np.sin(spir_t + s_offset)
        ax.plot(sx, sy, color=hair_color, linewidth=1.0, alpha=0.6)
    
    # Ухо
    ear_t = np.linspace(-np.pi*0.6, np.pi*0.6, 80)
    ear_x = 0.18 + 0.04 * np.cos(ear_t)
    ear_y = 0.38 + 0.1 * np.sin(ear_t)
    ax.plot(ear_x, ear_y, color=skin_shadow, linewidth=1.0, alpha=0.6)
    
    # Нимб
    nim_t = np.linspace(0, 2*np.pi, 200)
    nim_r = 0.55 + 0.02*np.sin(10*nim_t)
    ax.plot(nim_r*np.cos(nim_t)+0.05, nim_r*np.sin(nim_t)+0.5,
            color='#e8c860', linewidth=1.5, alpha=0.35)
    
    # Линии мимики — профиль
    if mood == 'pathos':
        # Складка на лбу
        for i in range(3):
            ft = np.linspace(-0.1, 0.1, 30)
            ax.plot(-0.05 + ft, 0.65 + i*0.02 + 3*ft**2,
                    color=skin_shadow, linewidth=0.6, alpha=0.4)
    
    # Носогубная складка
    nas_t = np.linspace(0, 1, 40)
    ax.plot(-0.02 + 0.06*nas_t, 0.15 - 0.08*nas_t, color=skin_shadow, linewidth=0.7, alpha=0.3)
    
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.7, 1.1)
    ax.set_aspect('equal')
    ax.axis('off')

# === РИСУЕМ ТРИ ЛИЦА ===

# 1. Аполлон — фронт, спокойствие (аполоническое начало)
draw_apollonian_face(axes[0], mood='serene', tilt=0)
axes[0].set_title('Аполлон Олимпийский\nЗолотое сечение φ = 1.618',
                  fontsize=10, fontfamily='serif', color='#2a1a0a', pad=10)

# 2. Лицо с пафосом (гелленетический стиль)
draw_apollonian_face(axes[1], mood='pathos', tilt=0.08)
axes[1].set_title('Пафос: Бог страдающий\nЛинии мимики и экспрессия',
                  fontsize=10, fontfamily='serif', color='#2a1a0a', pad=10)

# 3. Профиль — как на монетах
draw_profile_face(axes[2], mood='noble')
axes[2].set_title('Профиль: Камея и Монета\nКонические сечения Аполлония',
                  fontsize=10, fontfamily='serif', color='#2a1a0a', pad=10)

# Пропорциональная сетка (справа от первого лица)
ax_grid = fig.add_axes([0.03, 0.08, 0.15, 0.35])
ax_grid.set_xlim(-0.8, 0.8)
ax_grid.set_ylim(-1.3, 1.3)
ax_grid.set_aspect('equal')
ax_grid.axis('off')
ax_grid.set_title('Канон φ', fontsize=8, fontfamily='serif', color='#8a6a4a')

# Сетка пропорций
grid_lines = {
    'Волосы': 0.809,
    'Брови': 0.405,
    'Глаза': 0.270,
    'Нос': -0.270,
    'Рот': -0.433,
    'Подбородок': -0.809
}
for name, y_val in grid_lines.items():
    ax_grid.axhline(y_val, color='#c0a080', linewidth=0.5, linestyle='--', alpha=0.5)
    ax_grid.text(0.6, y_val, name, fontsize=6, color='#8a6a4a', va='center')

# Пропорции
phi_text = (
    "φ = 1.618...\n"
    "1/φ = 0.618...\n"
    "1/φ² = 0.382...\n\n"
    "Высота/Ширина = φ\n"
    "Межглазовое = W/φ\n"
    "Ширина глаза = W/φ²\n"
    "Длина носа = H/3\n"
    "Ширина рта = W/φ\n\n"
    "Кривые:\n"
    "• Эллипсы (глаза, лицо)\n"
    "• Параболы (брови, губы)\n"
    "• Спираль φ (волосы)\n"
    "• Катenary (носогубные)"
)
fig.text(0.88, 0.15, phi_text, fontsize=8, fontfamily='serif',
         color='#6a5a4a', fontstyle='italic', va='center',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#f0e8d8', edgecolor='#c0a880', alpha=0.8))

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig('apollonian_faces.png', dpi=200, bbox_inches='tight', facecolor='#f5efe0')
print("Сохранено: apollonian_faces.png")
