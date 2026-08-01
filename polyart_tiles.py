"""
@file polyart_tiles.py
@brief Игровые тайлы и круглые композиции для PolyArt.
@author PolyArt Project
@version 1.0.0
@date 2026

@par Описание
Надстройка над polyart_api.py для создания круглых игровых компонентов:
коустеры, жетоны, фишки, спиннеры, поля. Всё строится на полиномиальном
холсте Canvas и золотом сечении — без PIL.

@par Возможности
- Сеть узлов по золотому углу 137.5° (golden_web);
- Золотая спираль из полиномиальных сегментов (golden_spiral_lines);
- Сектор-«клинышек» для спиннеров и колёс (sector);
- Декоративное кольцо из полигонов (ring);
- Круглый рендер без постобработки (render_round через Canvas.render(round=True));
- Готовый конструктор тайла с радиальным градиентом (make_tile).

@par Быстрый старт
@code
from polyart_api import Canvas
from polyart_tiles import make_tile, sector, ring, render_round

def content(c):
    sector(c, 0, 0, 2.4, 0, 3.14, fill=True, fill_color="#db323e")

tile = make_tile("#f2f6ff", "#9fb6d8", hue_offset=200, content_fn=content,
                 seed=7, name="Spinner")
render_round(tile, "spinner.png", dpi=300)
@endcode
"""

import math
import random
from typing import Callable, List, Optional, Tuple

import numpy as np

from polyart_api import Canvas, PHI, GOLDEN_ANGLE


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    """@brief Конвертация HSL в RGB (h в градусах, s и l в долях 0..1)."""
    c = (1 - abs(2 * l - 1)) * s
    hp = h / 60.0
    x = c * (1 - abs(hp % 2 - 1))
    if hp < 1:
        r, g, b = c, x, 0.0
    elif hp < 2:
        r, g, b = x, c, 0.0
    elif hp < 3:
        r, g, b = 0.0, c, x
    elif hp < 4:
        r, g, b = 0.0, x, c
    elif hp < 5:
        r, g, b = x, 0.0, c
    else:
        r, g, b = c, 0.0, x
    m = l - c / 2
    return (int(round((r + m) * 255)), int(round((g + m) * 255)),
            int(round((b + m) * 255)))


def rgb_to_hex(c: Tuple[int, int, int]) -> str:
    """@brief RGB-кортеж -> строка #rrggbb."""
    return "#%02x%02x%02x" % (c[0], c[1], c[2])


def _parse_hex(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def shade_hex(h: str, f: float) -> str:
    """@brief Затемнить/осветлить цвет-строку на коэффициент f."""
    c = _parse_hex(h)
    return rgb_to_hex(tuple(max(0, min(255, int(round(ch * f)))) for ch in c))


def lerp_hex(h1: str, h2: str, t: float) -> str:
    """@brief Линейная интерполяция двух цветов-строк."""
    c1, c2 = _parse_hex(h1), _parse_hex(h2)
    return rgb_to_hex(tuple(int(round(c1[i] + (c2[i] - c1[i]) * t))
                            for i in range(3)))


def golden_web(c: Canvas, R: float, n: int = 70, seed: int = 0,
               hue_offset: float = 0.0, max_len_frac: float = 0.15) -> List[Tuple[float, float]]:
    """
    @brief Сеть узлов по золотому углу (филлотаксис Фибоначчи).

    Узлы расставляются по золотому углу 137.5°, соединения — полиномиальные
    линии (PolyCoeffs.line). Цвет каждой линии = угол касательной + сдвиг
    оттенка эмоции. Возвращает список узлов (их можно использовать как точки
    фичи для отрисовки поверх).
    """
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        t = (i + 0.5) / n
        rr = R * math.sqrt(t)
        ang = math.radians(math.degrees(GOLDEN_ANGLE) + rnd.uniform(-1.2, 1.2))
        pts.append((rr * math.cos(ang), rr * math.sin(ang)))
    max_len = R * max_len_frac
    dot_col = rgb_to_hex(hsl_to_rgb(hue_offset % 360, 0.9, 0.62))
    for i, (xi, yi) in enumerate(pts):
        for k in (1, round(PHI), round(PHI * PHI)):
            j = (i + k) % n
            xj, yj = pts[j]
            dx, dy = xj - xi, yj - yi
            if dx * dx + dy * dy > max_len * max_len:
                continue
            ang = math.degrees(math.atan2(dy, dx))
            col = rgb_to_hex(hsl_to_rgb((ang + hue_offset) % 360, 0.75, 0.6))
            c.line(xi, yi, xj, yj, color=col, linewidth=0.5, alpha=0.85)
    for (x, y) in pts:
        c.circle(x, y, R * 0.008, fill=True, fill_color=dot_col,
                 color=dot_col, linewidth=0)
    return pts


def golden_spiral_lines(c: Canvas, R: float, seed: int = 0,
                        hue_offset: float = 0.0, turns: float = 2.6) -> None:
    """
    @brief Золотая спираль из полиномиальных сегментов.

    Каждый сегмент — PolyObj степени 1 (line) с цветом по углу касательной.
    Радиус спирали подчинён золотой спирали, ограничен круговой областью R.
    """
    rnd = random.Random(seed)
    steps = 260
    prev = None
    for i in range(steps):
        k = i / steps
        rr = R * (0.05 + 0.8 * (1 - math.pow(0.618, k * 4)))
        ang = math.radians(k * 360 * turns + rnd.uniform(-0.4, 0.4))
        x, y = rr * math.cos(ang), rr * math.sin(ang)
        if prev:
            dx, dy = x - prev[0], y - prev[1]
            a = math.degrees(math.atan2(dy, dx))
            col = rgb_to_hex(hsl_to_rgb((a + hue_offset) % 360, 0.85, 0.55))
            c.line(prev[0], prev[1], x, y, color=col, linewidth=0.8, alpha=0.9)
        prev = (x, y)


def sector(c: Canvas, cx: float, cy: float, r: float,
           a0: float, a1: float, n_points: int = 60, **kw) -> Canvas:
    """
    @brief Сектор круга (клинышек спиннера) как замкнутый полигон.

    @param c Холст
    @param cx,cy Центр
    @param r Радиус
    @param a0,a1 Начальный и конечный угол (радианы)
    @param n_points Количество точек дуги
    @param kw Свойства полигона (fill_color, fill_alpha, color, ...)
    """
    pts = [(cx, cy)]
    for i in range(n_points + 1):
        a = a0 + (a1 - a0) * i / n_points
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return c.polygon(pts, **kw)


def ring(c: Canvas, cx: float, cy: float, r_out: float, r_in: float,
         n: int = 36, color: str = "#c8a040", seed: int = 0) -> Canvas:
    """
    @brief Декоративное кольцо из полигонов (крапчатый обод тайла).

    Между внешним и внутренним радиусом строится n трапеций-полигонов
    со случайными оттенками базового цвета.
    """
    rnd = random.Random(seed)
    for i in range(n):
        a = 2 * math.pi * i / n
        b = 2 * math.pi * (i + 1) / n
        pts = [(cx + r_out * math.cos(a), cy + r_out * math.sin(a)),
               (cx + r_out * math.cos(b), cy + r_out * math.sin(b)),
               (cx + r_in * math.cos(b), cy + r_in * math.sin(b)),
               (cx + r_in * math.cos(a), cy + r_in * math.sin(a))]
        col = shade_hex(color, rnd.uniform(0.75, 1.25))
        c.polygon(pts, fill=True, fill_color=col, fill_alpha=0.95,
                  color=col, linewidth=0)
    return c


def make_tile(bg_top: str, bg_bottom: str, hue_offset: float,
              content_fn: Optional[Callable[[Canvas], None]] = None,
              seed: int = 0, name: str = "Tile",
              radius: float = 3.0, web: bool = True,
              spiral: bool = True, ring_color: Optional[str] = None) -> Canvas:
    """
    @brief Конструктор круглого тайла (коустера, жетона).

    @param bg_top, bg_bottom Цвета радиального градиента фона (#hex)
    @param hue_offset Сдвиг оттенка эмоции (градусы) для сети и спирали
    @param content_fn Функция отрисовки контента: content_fn(canvas) -> None
    @param seed Семя случайности
    @param name Имя холста
    @param radius Радиус холста в условных единицах
    @param web Рисовать сеть узлов по золотому углу
    @param spiral Рисовать золотую спираль
    @param ring_color Цвет обода (None — не рисовать)

    @return Холст Canvas (рендер — через render_round / Canvas.render(round=True))
    """
    c = Canvas(name=name, width=4.0, height=4.0, background=bg_top,
               xlim=(-radius, radius), ylim=(-radius, radius))
    n = 26
    for i in range(n):
        t = i / (n - 1)
        col = lerp_hex(bg_bottom, bg_top, t)
        c.circle(0, 0, radius * (0.02 + 0.98 * t), fill=True, fill_color=col,
                 fill_alpha=1.0, color=col, linewidth=0)
    if web:
        golden_web(c, radius * 0.9, 70, seed + 40, hue_offset)
    if spiral:
        golden_spiral_lines(c, radius * 0.9, seed + 41, hue_offset)
    if content_fn:
        content_fn(c)
    if ring_color:
        ring(c, 0, 0, radius * 0.99, radius * 0.88, 36, ring_color, seed + 7)
    return c


def render_round(c: Canvas, path: str, dpi: int = 300) -> Canvas:
    """
    @brief Круглый рендер тайла: обрезка по вписанной окружности,
    прозрачный фон вне круга.
    """
    return c.render(path, dpi=dpi, round=True)


def render_spinner(sector_colors: List[str], path: str, dpi: int = 300,
                   radius: float = 3.0, gap_deg: float = 2.0,
                   bg: str = "#0a1220", seed: int = 0) -> Canvas:
    """
    @brief Готовый круглый спиннер: цветные секторы + кольцо + стрелка.

    @param sector_colors Цвета секторов (#hex)
    @param path Куда сохранить PNG
    @param dpi Разрешение
    @param radius Радиус холста
    @param gap_deg Зазор между секторами (градусы)
    @param bg Цвет фона
    @param seed Семя
    """
    c = Canvas(name="Spinner", width=4.0, height=4.0, background=bg,
               xlim=(-radius, radius), ylim=(-radius, radius))
    n = len(sector_colors)
    step = 2 * math.pi / n
    gap = math.radians(gap_deg)
    for i, col in enumerate(sector_colors):
        a0 = i * step + gap / 2
        a1 = (i + 1) * step - gap / 2
        sector(c, 0, 0, radius * 0.94, a0, a1,
               fill=True, fill_color=col, fill_alpha=0.9,
               color=shade_hex(col, 0.75), linewidth=0.4)
    ring(c, 0, 0, radius * 0.99, radius * 0.945, 48, "#e8ecf4", seed)
    hub = radius * 0.28
    c.circle(0, 0, hub, fill=True, fill_color="#f2f6ff", color="#c8ced8",
             linewidth=0.6)
    c.star(0, 0, scale=hub * 0.72, n=8, fill=True, fill_color="#2a5aa8",
           fill_alpha=0.85, color="#1e3f78", linewidth=0.6)
    c.circle(0, 0, hub * 0.18, fill=True, fill_color="#ffd700")
    y0 = radius * 0.94
    c.polygon([(-radius * 0.06, y0 - radius * 0.05),
               (radius * 0.06, y0 - radius * 0.05),
               (0.0, y0 + radius * 0.12)],
              fill=True, fill_color="#f04040", fill_alpha=0.95,
              color="#a02828", linewidth=0.5)
    c.circle(0, y0 - radius * 0.05, radius * 0.02, fill=True, fill_color="#ffffff")
    return c.render(path, dpi=dpi, round=True)
