import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, Ellipse, Arc
from matplotlib.path import Path
import matplotlib.patches as mpatches

fig, axes = plt.subplots(1, 3, figsize=(20, 10), facecolor='#f5e6c8')
fig.suptitle('Амфорное Искусство Античности', fontsize=18,
             fontfamily='serif', color='#3a1a0a', y=0.97, fontstyle='italic')

terracotta = '#c45a30'
terracotta_light = '#d87850'
black_fig = '#1a1008'
black_bg = '#2a1a0a'
cream = '#f0e0c0'
gold = '#c8a040'
white_clay = '#e8d8c0'

def draw_amphora_frame(ax, style='black'):
    """Контур амфоры — параметрические кривые"""
    t = np.linspace(0, 2*np.pi, 500)
    
    # Тело амфоры — модифицированный эллипс с полиномиальными поправками
    body_r = 1.0 + 0.15*np.cos(2*t) - 0.08*np.cos(4*t) + 0.03*np.sin(t)
    body_x = body_r * np.cos(t)
    body_y = -0.2 + 1.4 * np.sin(t)
    
    # Горлышко
    neck_t = np.linspace(0, 1, 100)
    neck_x_l = -0.28 - 0.05*np.sin(np.pi*neck_t)
    neck_x_r = 0.28 + 0.05*np.sin(np.pi*neck_t)
    neck_y = 1.2 + 0.8*neck_t
    
    # Крышка
    rim_t = np.linspace(-1, 1, 100)
    rim_x = 0.35 * (1 + 0.3*rim_t**2)
    
    # Ножка
    foot_t = np.linspace(-1, 1, 80)
    foot_x = 0.3 * (1 + 0.15*foot_t**2)
    
    return body_x, body_y, neck_x_l, neck_x_r, neck_y, rim_x, foot_t, foot_x

def draw_meander_band(ax, y, width, length, color):
    """Меандр — греческий ключ"""
    step = 0.15
    n = int(length / step)
    for i in range(n):
        x = -length/2 + i * step
        if i % 2 == 0:
            ax.plot([x, x+step, x+step, x+2*step, x+2*step],
                    [y, y, y+width, y+width, y],
                    color=color, linewidth=1.2)
        # вертикальные перемычки
        ax.plot([x, x], [y, y+width], color=color, linewidth=0.6, alpha=0.5)

def draw_palmette(ax, cx, cy, scale=1.0, color=black_fig):
    """Пальметта — орнамент"""
    t = np.linspace(0, np.pi, 100)
    for i in range(7):
        angle = -np.pi/2 + i * np.pi/6
        r = 0.3 * scale
        px = cx + r * np.cos(angle) * np.cos(t*0.5)
        py = cy + r * np.sin(angle) * (1 + 0.3*np.sin(t))
        # Лепестки как полиномы
        leaf_t = np.linspace(0, 1, 50)
        lx = cx + (0.05 + 0.25*leaf_t) * np.cos(angle)
        ly = cy + (0.05 + 0.25*leaf_t) * np.sin(angle)
        leaf_w = 0.08 * np.sin(np.pi * leaf_t) * scale
        ax.fill(lx + leaf_w*np.cos(angle+np.pi/2),
                ly + leaf_w*np.sin(angle+np.pi/2),
                color=color, alpha=0.85)
    
    # Стебель
    stem_t = np.linspace(0, 1, 50)
    ax.plot(cx + 0.15*stem_t, cy - 0.2*stem_t, color=color, linewidth=1.5)

def draw_greek_vase_scene_black(ax):
    """Чёрнофигурная вазопись — Геракл и Немейский лев"""
    # Фон — терракота
    ax.set_facecolor(terracotta)
    
    # Тело амфоры
    t = np.linspace(0, 2*np.pi, 500)
    body_r = 1.0 + 0.15*np.cos(2*t) - 0.08*np.cos(4*t)
    bx = body_r * np.cos(t)
    by = -0.3 + 1.5 * np.sin(t)
    
    # Заливка тела
    ax.fill(bx, by, color=terracotta, alpha=0.95)
    ax.plot(bx, by, color=black_fig, linewidth=2)
    
    # Горлышко
    neck_t = np.linspace(0, 1, 100)
    neck_xl = -0.28 - 0.05*np.sin(np.pi*neck_t)
    neck_xr = 0.28 + 0.05*np.sin(np.pi*neck_t)
    neck_y = 1.2 + 0.8*neck_t
    ax.fill_betweenx(neck_y, neck_xl, neck_xr, color=terracotta, alpha=0.95)
    ax.plot(neck_xl, neck_y, color=black_fig, linewidth=1.5)
    ax.plot(neck_xr, neck_y, color=black_fig, linewidth=1.5)
    
    # Крышка
    rim_t = np.linspace(-1, 1, 100)
    rim_x = 0.38 * (1 + 0.3*rim_t**2)
    ax.fill(rim_x, [2.1]*100, color=black_fig, alpha=0.95)
    ax.fill(-rim_x, [2.1]*100, color=black_fig, alpha=0.95)
    ax.fill_between([-0.38, 0.38], 1.95, 2.1, color=black_fig, alpha=0.95)
    
    # Ножка
    ax.fill_between([-0.3, 0.3], -2.2, -1.8, color=terracotta)
    ax.plot([-0.35, 0.35], [-2.2, -2.2], color=black_fig, linewidth=2)
    ax.plot([-0.3, 0.3], [-1.8, -1.8], color=black_fig, linewidth=1.5)
    
    # Ручки
    handle_t = np.linspace(-1, 1, 100)
    for side, sign in [('l', -1), ('r', 1)]:
        hx = sign * (0.28 + 0.35*(1 - handle_t**2))
        hy = 0.8 + 0.7*handle_t**2
        ax.plot(hx, hy, color=black_fig, linewidth=3)
    
    # Декоративные полосы
    draw_meander_band(ax, 1.5, 0.08, 1.8, black_fig)
    draw_meander_band(ax, -1.3, 0.08, 1.8, black_fig)
    
    # Пальметты
    draw_palmette(ax, -0.7, 1.3, 0.6, black_fig)
    draw_palmette(ax, 0.7, 1.3, 0.6, black_fig)
    draw_palmette(ax, -0.7, -1.2, 0.5, black_fig)
    draw_palmette(ax, 0.7, -1.2, 0.5, black_fig)
    
    # === СЦЕНА: Геракл и лев ===
    # Геракл (чёрная фигура)
    # Тело
    hero_t = np.linspace(0, 1, 100)
    # Ноги
    for lx, la in [(-0.15, 0.1), (0.15, -0.15)]:
        leg_x = lx + 0.1*np.sin(la + hero_t*0.5)
        leg_y = -1.0 + 0.5*hero_t
        ax.plot(leg_x, leg_y, color=black_fig, linewidth=4, solid_capstyle='round')
    
    # Торс
    torso_t = np.linspace(0, 1, 80)
    tx_l = -0.2 - 0.05*torso_t
    tx_r = 0.2 + 0.05*torso_t
    ty = -0.5 + 0.7*torso_t
    ax.fill_betweenx(ty, tx_l, tx_r, color=black_fig, alpha=0.95)
    
    # Голова
    head_t = np.linspace(0, 2*np.pi, 80)
    ax.fill(-0.05 + 0.12*np.cos(head_t), 0.25 + 0.14*np.sin(head_t), color=black_fig)
    # Лев (чёрная фигура)
    # Тело льва — полиномиальная кривая
    lion_body_t = np.linspace(0, 2*np.pi, 200)
    lion_bx = 0.55 + 0.35*np.cos(lion_body_t) + 0.1*np.sin(2*lion_body_t)
    lion_by = -0.3 + 0.2*np.sin(lion_body_t)
    ax.fill(lion_bx, lion_by, color=black_fig, alpha=0.9)
    
    # Голова льва
    lion_head_t = np.linspace(0, 2*np.pi, 80)
    ax.fill(0.85 + 0.15*np.cos(lion_head_t), -0.1 + 0.15*np.sin(lion_head_t), color=black_fig)
    
    # Грива — полиномические лучи
    mane_t = np.linspace(0, 2*np.pi, 60)
    for angle in np.linspace(0, 2*np.pi, 12):
        mx = 0.85 + 0.2*np.cos(angle) * (1 + 0.3*np.sin(3*mane_t))
        my = -0.1 + 0.2*np.sin(angle) * (1 + 0.3*np.cos(3*mane_t))
        ax.plot(mx, my, color=black_fig, linewidth=1.5, alpha=0.7)
    
    # Лапы льва
    for lx_off in [0.4, 0.7]:
        leg_t = np.linspace(0, 1, 50)
        ax.plot(lx_off + 0.05*np.sin(leg_t*3), -0.5 - 0.2*leg_t,
                color=black_fig, linewidth=3, solid_capstyle='round')
    
    # Дубина Геракла
    club_t = np.linspace(0, 1, 50)
    ax.plot(-0.05 + 0.4*club_t, 0.1 + 0.3*club_t,
            color=black_fig, linewidth=3, solid_capstyle='round')
    
    # Лев (вырез на чёрном — терракота)
    eye_lion = Circle((0.9, -0.1), 0.03, color=terracotta)
    ax.add_patch(eye_lion)
    eye_hero = Circle((-0.07, 0.28), 0.02, color=terracotta)
    ax.add_patch(eye_hero)
    
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-2.8, 2.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Чёрнофигурная: Геракл и Немейский лев',
                 fontsize=10, fontfamily='serif', color='#3a1a0a', pad=8)

def draw_greek_vase_scene_red(ax):
    """Краснофигурная вазопись — колесница Афины"""
    ax.set_facecolor(black_bg)
    
    t = np.linspace(0, 2*np.pi, 500)
    body_r = 1.0 + 0.15*np.cos(2*t) - 0.08*np.cos(4*t)
    bx = body_r * np.cos(t)
    by = -0.3 + 1.5 * np.sin(t)
    
    ax.fill(bx, by, color=black_bg, alpha=0.95)
    ax.plot(bx, by, color=terracotta, linewidth=2)
    
    # Горлышко
    neck_t = np.linspace(0, 1, 100)
    neck_xl = -0.28 - 0.05*np.sin(np.pi*neck_t)
    neck_xr = 0.28 + 0.05*np.sin(np.pi*neck_t)
    neck_y = 1.2 + 0.8*neck_t
    ax.fill_betweenx(neck_y, neck_xl, neck_xr, color=black_bg, alpha=0.95)
    ax.plot(neck_xl, neck_y, color=terracotta, linewidth=1.5)
    ax.plot(neck_xr, neck_y, color=terracotta, linewidth=1.5)
    
    # Крышка
    rim_t = np.linspace(-1, 1, 100)
    rim_x = 0.38 * (1 + 0.3*rim_t**2)
    ax.fill_between([-0.38, 0.38], 1.95, 2.1, color=terracotta, alpha=0.95)
    
    # Ножка
    ax.fill_between([-0.3, 0.3], -2.2, -1.8, color=black_bg)
    ax.plot([-0.35, 0.35], [-2.2, -2.2], color=terracotta, linewidth=2)
    ax.plot([-0.3, 0.3], [-1.8, -1.8], color=terracotta, linewidth=1.5)
    
    # Ручки
    handle_t = np.linspace(-1, 1, 100)
    for sign in [-1, 1]:
        hx = sign * (0.28 + 0.35*(1 - handle_t**2))
        hy = 0.8 + 0.7*handle_t**2
        ax.plot(hx, hy, color=terracotta, linewidth=3)
    
    # Декоративные полосы
    draw_meander_band(ax, 1.5, 0.08, 1.8, terracotta)
    draw_meander_band(ax, -1.3, 0.08, 1.8, terracotta)
    
    draw_palmette(ax, -0.7, 1.3, 0.6, terracotta)
    draw_palmette(ax, 0.7, 1.3, 0.6, terracotta)
    draw_palmette(ax, -0.7, -1.2, 0.5, terracotta)
    draw_palmette(ax, 0.7, -1.2, 0.5, terracotta)
    
    # === СЦЕНА: Колесница Афины ===
    # Колесница — тело
    char_x = [-0.5, 0.5]
    char_y = [-0.8, -0.8]
    ax.plot([-0.5, 0.5], [-0.8, -0.8], color=terracotta, linewidth=2)
    ax.plot([-0.5, -0.5], [-0.8, -0.5], color=terracotta, linewidth=2)
    ax.plot([0.5, 0.5], [-0.8, -0.5], color=terracotta, linewidth=2)
    ax.plot([-0.5, 0.5], [-0.5, -0.5], color=terracotta, linewidth=2)
    
    # Колесо — параметрическая окружность
    wheel_t = np.linspace(0, 2*np.pi, 100)
    wr = 0.18
    for wx in [-0.35, 0.35]:
        ax.plot(wx + wr*np.cos(wheel_t), -0.85 + wr*np.sin(wheel_t),
                color=terracotta, linewidth=1.5)
        # Спицы
        for s_a in np.linspace(0, 2*np.pi, 8, endpoint=False):
            ax.plot([wx, wx + wr*0.9*np.cos(s_a)],
                    [-0.85, -0.85 + wr*0.9*np.sin(s_a)],
                    color=terracotta, linewidth=0.8)
    
    # Кони (два) — полиномиальные силуэты
    for ci, cx_off in enumerate([-0.2, 0.2]):
        # Тело коня
        horse_t = np.linspace(0, 2*np.pi, 200)
        hx = cx_off + 0.2*np.cos(horse_t) + 0.15*np.sin(horse_t)
        hy = -0.3 + 0.1*np.sin(horse_t) + 0.05*np.cos(2*horse_t)
        ax.fill(hx, hy, color=terracotta, alpha=0.85)
        
        # Шея и голова
        neck_t = np.linspace(0, 1, 50)
        n_x = cx_off + 0.35 + 0.05*neck_t
        n_y = -0.15 + 0.35*neck_t
        ax.plot(n_x, n_y, color=terracotta, linewidth=3, solid_capstyle='round')
        # Голова
        head_t = np.linspace(0, 2*np.pi, 30)
        ax.fill(cx_off + 0.38 + 0.06*np.cos(head_t),
                0.25 + 0.05*np.sin(head_t), color=terracotta)
        
        # Ноги (бегущие)
        for li, la in enumerate([0.3, -0.2, 0.1, -0.3]):
            lx = cx_off + 0.15*li - 0.15 + 0.05*np.sin(la)
            ly_bot = -0.65
            ly_top = -0.45
            leg_t2 = np.linspace(0, 1, 30)
            l_x = lx + 0.03*np.sin(la*5 + leg_t2*3)
            l_y = ly_bot + (ly_top - ly_bot)*leg_t2
            ax.plot(l_x, l_y, color=terracotta, linewidth=2, solid_capstyle='round')
    
    # Афина на колеснице
    # Тело
    athena_t = np.linspace(0, 1, 80)
    ax.fill_betweenx(-0.5 + 0.5*athena_t, -0.08, 0.08, color=terracotta, alpha=0.85)
    # Голова
    head_t2 = np.linspace(0, 2*np.pi, 60)
    ax.fill(0.0 + 0.08*np.cos(head_t2), 0.05 + 0.09*np.sin(head_t2), color=terracotta)
    # Шлем
    helmet_t = np.linspace(0, np.pi, 50)
    ax.plot(0.0 + 0.1*np.cos(helmet_t), 0.05 + 0.12*np.sin(helmet_t),
            color=terracotta, linewidth=2)
    # Копьё
    ax.plot([0.05, 0.4], [0.0, 0.5], color=terracotta, linewidth=1.5)
    
    # Щит
    shield_t = np.linspace(0, 2*np.pi, 60)
    ax.fill(-0.15 + 0.1*np.cos(shield_t), -0.15 + 0.12*np.sin(shield_t),
            color=terracotta, alpha=0.7)
    
    # Лучи славы за колесницей
    for ray_i in range(5):
        rx = -0.7 - 0.1*ray_i
        ry = -0.5 + 0.1*ray_i
        ax.plot([rx, rx - 0.15], [ry, ry + 0.1], color=terracotta, linewidth=0.8, alpha=0.5)
    
    # Глаза — терракота на чёрном
    eye_hero = Circle((0.01, 0.07), 0.015, color=black_bg)
    ax.add_patch(eye_hero)
    
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-2.8, 2.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Краснофигурная: Колесница Афины',
                 fontsize=10, fontfamily='serif', color='#3a1a0a', pad=8)

def draw_amphora_ornament(ax):
    """Детальный орнамент амфоры — пальметты, лотосы, меандр"""
    ax.set_facecolor(terracotta)
    
    t = np.linspace(0, 2*np.pi, 500)
    body_r = 1.0 + 0.15*np.cos(2*t) - 0.08*np.cos(4*t)
    bx = body_r * np.cos(t)
    by = -0.3 + 1.5 * np.sin(t)
    
    ax.fill(bx, by, color=terracotta, alpha=0.95)
    ax.plot(bx, by, color=black_fig, linewidth=2)
    
    # Горлышко
    neck_t = np.linspace(0, 1, 100)
    neck_xl = -0.28 - 0.05*np.sin(np.pi*neck_t)
    neck_xr = 0.28 + 0.05*np.sin(np.pi*neck_t)
    neck_y = 1.2 + 0.8*neck_t
    ax.fill_betweenx(neck_y, neck_xl, neck_xr, color=terracotta, alpha=0.95)
    ax.plot(neck_xl, neck_y, color=black_fig, linewidth=1.5)
    ax.plot(neck_xr, neck_y, color=black_fig, linewidth=1.5)
    
    # Крышка
    rim_t = np.linspace(-1, 1, 100)
    rim_x = 0.38 * (1 + 0.3*rim_t**2)
    ax.fill_between([-0.38, 0.38], 1.95, 2.1, color=black_fig, alpha=0.95)
    
    # Ножка
    ax.fill_between([-0.3, 0.3], -2.2, -1.8, color=terracotta)
    ax.plot([-0.35, 0.35], [-2.2, -2.2], color=black_fig, linewidth=2)
    
    # Ручки
    handle_t = np.linspace(-1, 1, 100)
    for sign in [-1, 1]:
        hx = sign * (0.28 + 0.35*(1 - handle_t**2))
        hy = 0.8 + 0.7*handle_t**2
        ax.plot(hx, hy, color=black_fig, linewidth=3)
    
    # === МНОГОЯРУСНЫЙ ОРНАМЕНТ ===
    
    # Верхний меандр
    draw_meander_band(ax, 1.6, 0.06, 1.6, black_fig)
    
    # Верхний волютный фриз
    volut_t = np.linspace(0, 2*np.pi, 100)
    for vx_off in np.linspace(-0.8, 0.8, 8):
        vr = 0.12
        ax.plot(vx_off + vr*np.cos(volut_t), 1.35 + vr*np.sin(volut_t),
                color=black_fig, linewidth=1)
        # Спираль внутри
        spir_t = np.linspace(0, 3*np.pi, 100)
        sr = 0.02 + 0.03*spir_t/(3*np.pi)
        ax.plot(vx_off + sr*np.cos(spir_t), 1.35 + sr*np.sin(spir_t),
                color=black_fig, linewidth=0.8, alpha=0.7)
    
    # Центральная пальметта — крупная
    pal_t = np.linspace(0, np.pi, 100)
    for i in range(9):
        angle = -np.pi/2 + i * np.pi/8
        leaf_t = np.linspace(0, 1, 80)
        lx = 0.4*leaf_t * np.cos(angle)
        ly = 0.4*leaf_t * np.sin(angle)
        leaf_w = 0.12 * np.sin(np.pi * leaf_t)
        ax.fill(lx + leaf_w*np.cos(angle+np.pi/2),
                0.3 + ly + leaf_w*np.sin(angle+np.pi/2),
                color=black_fig, alpha=0.85)
    
    # Бутон лотоса — полиномиальные лепестки
    for side in [-1, 1]:
        lotus_t = np.linspace(0, 1, 80)
        for li in range(5):
            la = side * (0.3 + li*0.15)
            lpetal_x = side*0.1 + la * lotus_t**0.7
            lpetal_y = -0.2 + 0.15*np.sin(np.pi*lotus_t) + li*0.06
            lpetal_w = 0.04 * np.sin(np.pi*lotus_t)
            ax.fill(lpetal_x, lpetal_y + lpetal_w, color=black_fig, alpha=0.6)
    
    # Средний меандр
    draw_meander_band(ax, 0.0, 0.06, 1.6, black_fig)
    
    # Нижний меандр
    draw_meander_band(ax, -0.8, 0.06, 1.6, black_fig)
    
    # Стрелки внизу
    for sx in np.linspace(-0.6, 0.6, 6):
        ax.plot([sx, sx+0.08, sx], [-1.0, -0.9, -0.8],
                color=black_fig, linewidth=1)
    
    # Двойная линия
    for yy in [-1.1, -1.15]:
        circle_t = np.linspace(0, 2*np.pi, 300)
        cr = 1.0 + 0.15*np.cos(2*circle_t) - 0.08*np.cos(4*circle_t)
        cx = cr * np.cos(circle_t) * 0.85
        cy = yy + 0.02*np.sin(10*circle_t)
    
    # Нижний волютный фриз
    for vx_off in np.linspace(-0.6, 0.6, 6):
        vr = 0.08
        ax.plot(vx_off + vr*np.cos(volut_t), -1.05 + vr*np.sin(volut_t),
                color=black_fig, linewidth=0.8)
    
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-2.8, 2.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Орнаментальная: Волюты и Пальметты',
                 fontsize=10, fontfamily='serif', color='#3a1a0a', pad=8)

draw_greek_vase_scene_black(axes[0])
draw_greek_vase_scene_red(axes[1])
draw_amphora_ornament(axes[2])

# Формулы внизу
formulas = (
    "Полиномы тела:  r(θ) = 1.0 + 0.15cos(2θ) − 0.08cos(4θ)    |    "
    "Пальметта:  ρ(t) = at · sin(πt)    |    "
    "Спираль:  r(φ) = a + bφ"
)
fig.text(0.5, 0.01, formulas, ha='center', va='bottom',
         fontsize=9, fontfamily='serif', color='#6a5a4a', fontstyle='italic')

plt.tight_layout(rect=[0, 0.04, 1, 0.94])
plt.savefig('amphora_art.png', dpi=200, bbox_inches='tight', facecolor='#f5e6c8')
print("Сохранено: amphora_art.png")
