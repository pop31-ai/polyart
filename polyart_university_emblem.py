#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@brief Эмблема университета полиарта (круглая печать).

Официальная эмблема университета: кольца-ободы с греческим меандром,
в центре — римская арка с колоннами (аудитория-кафедра), над ней —
звезда по золотому сечению, внизу — кодекс «свобода и цели».

Стиль — «polyart»: каждая форма — параметрический/полиномиальный объект
(окружность, меандр, арка, колонны, звезда, спираль).

Запуск:
    python polyart_university_emblem.py
  Сохраняет:
    university_emblem.png  (круглая печать, прозрачный фон)
    university_emblem.svg  (векторная версия)
    university_emblem.polyart (данные формата .polyart)
"""

import os
import numpy as np

from polyart_api import Canvas, PolyObj, GreekLines, RomanLines, GoldenRatio, PHI, TWO_PI


def emblem() -> Canvas:
    c = Canvas(name="Эмблема университета полиарта", author="PolyArt University",
               background="#f5efe0", xlim=(-5.0, 5.0), ylim=(-5.0, 5.0))

    INK = "#1a2733"      # чернила (главный цвет универ-палитры)
    GOLD = "#b8860b"     # золото (универ-золото)
    RED = "#9e2b25"      # кафедра-красный

    # ---- 1. Ободы печати ----
    # Внешнее кольцо
    c.circle(0, 0, 4.85, color=INK, linewidth=2.5)
    c.circle(0, 0, 2.55, color=INK, linewidth=2.0)

    # ---- 2. Греческий меандр между ободами (классический знак учёности) ----
    # Меандр идёт по восьми дугам в кольце между 3.0 и 3.9
    ring_r = 3.45
    seg_angle = TWO_PI / 24
    for i in range(24):
        a0 = i * seg_angle
        t = np.linspace(a0, a0 + seg_angle, 40)
        x = ring_r * np.cos(t)
        y = ring_r * np.sin(t)
        deg = min(10, 39)
        px = list(reversed(np.polyfit(t / np.pi, x, deg).tolist()))
        py = list(reversed(np.polyfit(t / np.pi, y, deg).tolist()))
        c.add(PolyObj(px, py, t_range=[0, 1], color=GOLD, linewidth=1.3, alpha=0.9))

    # Пунктир-подсказки меандра: короткие радиальные чёрточки
    for i in range(24):
        a = i * (TWO_PI / 24)
        r0, r1 = 3.0, 3.9
        x = [r0 * np.cos(a), r1 * np.cos(a)]
        y = [r0 * np.sin(a), r1 * np.sin(a)]
        deg = 1
        px = list(reversed(np.polyfit(np.array([0.0, 1.0]), np.array(x), deg).tolist()))
        py = list(reversed(np.polyfit(np.array([0.0, 1.0]), np.array(y), deg).tolist()))
        c.add(PolyObj(px, py, t_range=[0, 1], color=INK, linewidth=1.0, alpha=0.5))

    # ---- 3. Центральная сцена: римская арка с колоннами ----
    arch_w, arch_h = 1.7, 2.4
    ax_, ay_ = 0.0, -0.85   # арка (основание близко к низу печати)

    # Две колонны по бокам арки
    col_h = 1.7
    for cx in (-1.35, 1.35):
        col = RomanLines.column(cx, -0.9, col_h, base_width=0.18,
                                capital_width=0.24, order="ionic")
        for part in (col["shaft_left"], col["shaft_right"], col["base"], col["capital"]):
            px, py = part
            c.add(PolyObj(px, py, t_range=[0, 1], color=INK, linewidth=1.1))

    # Полукруглая арка
    px, py = RomanLines.arch(0.0, ay_, arch_w, arch_h)
    c.add(PolyObj(px, py, t_range=[0, 1], color=INK, linewidth=2.2))

    # Внутренняя дверь-арка (перспектива кафедры)
    px, py = RomanLines.arch(0.0, ay_, arch_w * 0.55, arch_h * 0.62)
    c.add(PolyObj(px, py, t_range=[0, 1], color=GOLD, linewidth=1.4))

    # ---- 4. Звезда (золотое сечение) над аркой ----
    c.star(0.0, 1.45, scale=0.62, n=5, color=GOLD, linewidth=1.6)

    # Золотая спираль — знак полиарта
    c.golden_spiral(0.0, -0.1, a=0.11, turns=1.6,
                    color=RED, linewidth=1.2, alpha=0.7)

    # ---- 5. Лента-бюст с кодексом ----
    draw_banner(c, 0.0, -2.15, width=3.0, color=RED, fill_color=INK)
    c.add_formula("СВОБОДА И ЦЕЛИ", 0.0, -2.15,
                  fontsize=11, color="#f5efe0")

    # Подпись темы тонкой линией-дугой не нужна — кодекс уже на ленте.

    return c


def draw_banner(c, cx, cy, width=3.0, height=0.34, color="#9e2b25", fill_color="#1a2733"):
    """Простая горизонтальная лента-перемычка с выемками по краям."""
    hh = height / 2
    w = width / 2
    seg = 0.22
    xs = [-w, -w + seg, -w + 2 * seg, w - 2 * seg, w - seg, w]
    xs = [x for x in xs] + [x for x in reversed(xs)]
    ys = [hh, hh, -hh, -hh, hh, hh] + [-hh, -hh, hh, hh, -hh, -hh]
    # замкнутый многоугольник ленты
    xs += [xs[0]]
    ys += [ys[0]]
    # полиномиальная аппроксимация
    s = np.linspace(0, 1, len(xs))
    deg = min(10, len(xs) - 1)
    px = list(reversed(np.polyfit(s, np.array(xs) + cx, deg).tolist()))
    py = list(reversed(np.polyfit(s, np.array(ys) + cy, deg).tolist()))
    c.add(PolyObj(px, py, t_range=[0, 1], color=color, linewidth=1.2,
                  fill=True, fill_color=fill_color, fill_alpha=1.0))


def main():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    c = emblem()
    c.save(os.path.join(base, "university_emblem.polyart"))
    # Круглая печать (прозрачный фон) + векторная версия
    c.render(os.path.join(base, "university_emblem.png"), dpi=220, figsize=(8, 8), round=True)
    c.render(os.path.join(base, "university_emblem.svg"), dpi=300, figsize=(8, 8), round=True)
    c.info()


if __name__ == "__main__":
    main()
