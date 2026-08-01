"""
@file 11_polyyolka.py
@brief Пример 11: ПолиЁлка — игровые тайлы и спиннер на чистом полиарте.

Демонстрирует polyart_tiles.py:
  * круглый тайл-коустер с лицом по золотому сечению, сетью узлов
    по золотому углу и золотой спиралью;
  * круглый спиннер из секторов с кольцом и стрелкой.

Оба изображения рендерятся с круглой маской (Canvas.render(round=True))
и прозрачным фоном вне круга — без постобработки PIL.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from polyart_api import PHI, TWO_PI
from polyart_tiles import (make_tile, render_round, render_spinner,
                           rgb_to_hex, hsl_to_rgb)

OUT = os.path.dirname(os.path.abspath(__file__))


def face(c):
    """Лицо-сеть по золотым пропорциям: голова, глаза, брови, рот, шапка."""
    W = 2.3
    H = W * PHI
    # голова
    c.ellipse(0, 0.0, W / 2, H / 2, fill=True, fill_color="#e8c8a0",
              color="#c8a888", linewidth=0.6)
    # глаза на золотом расстоянии
    ex = W / (2 * PHI)
    ey = H * 0.12
    for sgn in (-1, 1):
        c.ellipse(sgn * ex, ey, 0.20, 0.11, fill=True, fill_color="#ffffff",
                  color="#3a2818", linewidth=0.5)
        c.circle(sgn * ex, ey, 0.055, fill=True, fill_color="#1a1008")
    # брови — полиномы через три узла
    brow_col = rgb_to_hex(hsl_to_rgb(-20, 0.6, 0.35))
    for sgn in (-1, 1):
        c.polyline([(sgn * ex * 1.35, ey + 0.34), (sgn * ex * 0.9, ey + 0.40),
                    (sgn * ex * 0.45, ey + 0.35)],
                   color=brow_col, linewidth=1.0)
    # нос
    c.polygon([(-0.12, -0.05), (0.12, -0.05), (0.0, 0.45)],
              fill=True, fill_color="#d8b088", color="#b89068", linewidth=0.4)
    # рот-улыбка — полином
    mw = W / PHI / 2
    my = -H * 0.28
    mouth = [(x, my - 0.18 * ((x / mw) ** 2) * mw)
             for x in [-mw + 2 * mw * i / 12 for i in range(13)]]
    c.polyline(mouth, color="#8b4020", linewidth=1.2)
    # шапка Деда Мороза
    c.polygon([(-1.05, H * 0.28), (1.05, H * 0.28), (0.0, H * 0.85)],
              fill=True, fill_color="#db323e", fill_alpha=0.95,
              color="#a02630", linewidth=0.5)
    c.circle(0.0, H * 0.85, 0.12, fill=True, fill_color="#fafbfc")
    c.polygon([(-1.25, H * 0.24), (1.25, H * 0.24),
               (1.25, H * 0.36), (-1.25, H * 0.36)],
              fill=True, fill_color="#fafbfc", color="#d8dee8", linewidth=0.4)


print("[OK] ПолиЁлка: сборка тайла-коустера ...")
tile = make_tile("#f2f6ff", "#9fb6d8", hue_offset=200, content_fn=face,
                 seed=7, name="PolyyolkaTile", ring_color="#8ca8c8")
render_round(tile, os.path.join(OUT, "11_polyyolka_tile.png"), dpi=300)
tile.info()

print("[OK] ПолиЁлка: сборка спиннера ...")
spinner_colors = ["#db323e", "#29aae2", "#2eb44a", "#ff912c",
                  "#f1c40f", "#9646d6", "#d2dceb", "#ffd700"]
render_spinner(spinner_colors, os.path.join(OUT, "11_polyyolka_spinner.png"),
               dpi=300, seed=99)

print("[OK] Готово: 11_polyyolka_tile.png, 11_polyyolka_spinner.png")
print("     Тайл и спиннер — круглые, с прозрачным фоном вне круга,")
print("     сеть узлов по золотому углу 137.5°, цвет дуги = угол касательной.")
