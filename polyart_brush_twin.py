"""
@file polyart_brush_twin.py
@brief Цифровой двойник кисти с масляной краской для полиарта v1.0
@author PolyArt Project
@version 1.0.0
@date 2026

@par Описание
Виртуальный двойник живописной кисти, погружённой в масляную краску.
Моделирует физику настоящего художника:

- @b Щетина (bristles): пучок щетин, который расходится под давлением
  и оставляет фактурные следы.
- @b Импосто (impasto): густая краска, ложащаяся толстым рельефным слоем
  с рваными краями и бороздками.
- @b Лессировка (glazing): полупрозрачный тонкий слой краски поверх
  подсохшего нижнего слоя — классический приём старых мастеров.
- @b Wet-on-wet (алла прима): смешивание ещё не высохшей краски
  прямо на холсте, дающее мягкие переходы.
- @b Истощение краски (paint depletion): кисть отдаёт краску по мере мазка,
  к концу штриха остаётся сухая щетина (dry brush).
- @b Вращение кисти (rotation): поворот пучка щетин влияет на ширину мазка.

@par Пример
@code
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from polyart_brush_twin import OilBrushTwin, brush_stroke, impasto, glaze

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_xlim(-5, 5); ax.set_ylim(-5, 5); ax.axis("off")

brush = OilBrushTwin(size="flat", paint="#c8a040", load=0.95)
t = np.linspace(-4, 4, 120)
x = t
y = 0.6 * np.sin(t)
brush.stroke(ax, x, y, pressure=0.8)   # мазок двойником кисти
impasto(ax, x, y - 1.5, color="#8a2a2a", thickness=0.35)
glaze(ax, x, y + 1.5, color="#3a5a8a", alpha=0.35)
plt.savefig("oil_brush_demo.png", dpi=150)
@endcode

@see polyart_api.py   основной полиномиальный API
@see polyart_curves.py  библиотека кривых
"""

import numpy as np
import random

# ============================================================
#  Цветовые утилиты
# ============================================================


def hex_to_rgb(color):
    """Преобразование '#rrggbb' в кортеж (r, g, b) в диапазоне 0..1."""
    if isinstance(color, (tuple, list)):
        c = [float(v) for v in color]
        if max(c) > 1.0:
            c = [v / 255.0 for v in c]
        return tuple(c)
    s = color.lstrip("#")
    return tuple(int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def rgb_to_hex(color):
    """Преобразование (r, g, b) в '#rrggbb'."""
    c = [max(0.0, min(1.0, float(v))) for v in color]
    return "#" + "".join(f"{int(v * 255):02x}" for v in c)


def mix(c1, c2, t):
    """Линейное смешивание двух RGB-цветов с коэффициентом t."""
    a = np.asarray(hex_to_rgb(c1))
    b = np.asarray(hex_to_rgb(c2))
    return rgb_to_hex(a * (1 - t) + b * t)


def shade(color, factor):
    """Осветлить (factor > 0) или затемнить (factor < 0) цвет."""
    c = np.asarray(hex_to_rgb(color))
    if factor >= 0:
        return rgb_to_hex(c + (1.0 - c) * factor)
    return rgb_to_hex(c * (1.0 + factor))


# ============================================================
#  Двойник кисти
# ============================================================


class OilBrushTwin:
    """
    @brief Цифровой двойник живописной кисти.

    Хранит состояние настоящей кисти: размер и форму пучка щетин,
    загрузку краски, давление, угол поворота и остаток краски.
    Мазки наносятся с учётом физики масляной краски.
    """

    SIZES = {
        "round": {"bristles": 14, "taper": 0.9, "spread": 0.35},
        "flat":  {"bristles": 22, "taper": 0.55, "spread": 0.75},
        "filbert": {"bristles": 18, "taper": 0.7, "spread": 0.55},
        "fan":   {"bristles": 30, "taper": 0.2, "spread": 1.0},
        "liner": {"bristles": 6, "taper": 1.0, "spread": 0.1},
    }

    def __init__(self, size="flat", paint="#c8a040", load=0.9,
                 width=1.0, oiliness=0.6, pressure=0.5, angle=0.0, seed=None):
        """
        @param size Тип кисти: round / flat / filbert / fan / liner
        @param paint Цвет краски (#hex)
        @param load Загрузка краски 0..1 (1 — полная кисть)
        @param width Базовая ширина мазка (в единицах данных)
        @param oiliness Маслянистость 0..1 (больше — жирнее, дольше сохнет)
        @param pressure Давление 0..1
        @param angle Поворот кисти в радианах
        @param seed Сид для воспроизводимости фактуры
        """
        cfg = self.SIZES.get(size, self.SIZES["flat"])
        self.size = size
        self.bristles = cfg["bristles"]
        self.taper = cfg["taper"]
        self.spread = cfg["spread"]
        self.paint = paint
        self.load = load
        self.width = width
        self.oiliness = oiliness
        self.pressure = pressure
        self.angle = angle
        self.rng = random.Random(seed)
        self._spent = 0.0

    def _remaining(self):
        """Сколько краски осталось на кисти (0..1)."""
        return max(0.0, self.load * (1.0 - self._spent))

    def reset_paint(self, load=None):
        """Перезарядить кисть краской."""
        self._spent = 0.0
        if load is not None:
            self.load = load

    def _bristle_offsets(self, pressure):
        """Смещения щетин относительно оси мазка."""
        p = max(0.05, min(1.0, pressure))
        fan = self.spread * (0.5 + 0.5 * p)
        n = self.bristles
        offs = np.linspace(-fan, fan, n)
        # щетины слегка разбегаются по-разному (фактура)
        jitter = np.array([self.rng.uniform(-0.02, 0.02) for _ in range(n)])
        return offs + jitter

    def stroke(self, ax, x, y, color=None, pressure=None, angle=None,
               paint_percent=None, dry_brush=False, lw_mult=1.0, alpha=1.0,
               zorder=2):
        """
        @brief Нанести мазок двойником кисти по кривой (x, y).

        @param ax   matplotlib Axes
        @param x, y массивы точек кривой
        @param color цвет краски (по умолчанию — из кисти)
        @param pressure давление 0..1 (переопределяет кисть)
        @param angle поворот кисти (переопределяет кисть)
        @param paint_percent доля краски, которую кисть отдаст за мазок
        @param dry_brush разрешить эффект сухой кисти к концу мазка
        @param lw_mult множитель ширины
        @param alpha прозрачность слоя
        """
        col = color or self.paint
        p = pressure if pressure is not None else self.pressure
        ang = angle if angle is not None else self.angle
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        n = len(x)
        if n < 2:
            return

        remaining = self._remaining()
        if paint_percent is not None:
            give = min(paint_percent, remaining)
        else:
            give = remaining
        self._spent += give * 0.5

        # ширина мазка зависит от давления, поворота кисти и остатка краски
        rot_w = 0.55 + 0.45 * abs(np.cos(ang))
        w = self.width * lw_mult * rot_w * (0.6 + 0.8 * p)

        offs = self._bristle_offsets(p)
        theta = np.arctan2(np.gradient(y), np.gradient(x))
        nx = -np.sin(theta)
        ny = np.cos(theta)

        # длина каждого участка для учёта истощения краски
        seg = np.sqrt(np.gradient(x) ** 2 + np.gradient(y) ** 2)
        cum = np.cumsum(seg)
        total = cum[-1] if cum[-1] > 0 else 1.0

        for k, off in enumerate(offs):
            bx = x + nx * off * w
            by = y + ny * off * w
            # тонкость щетины
            bw = w * 0.28 * self.taper
            # истощение краски: к концу мазка краски меньше
            dep = 1.0 - 0.85 * (cum / total) * (1.0 - give)
            if dry_brush:
                # сухая кисть: щетины процарапывают прерывистые следы
                breaky = 1.0 - 0.9 * (cum / total)
                for i in range(1, n):
                    if self.rng.random() < breaky[i] * 0.85:
                        ax.plot([bx[i - 1], bx[i]], [by[i - 1], by[i]],
                                color=col, linewidth=max(0.15, bw * dep[i] * p),
                                alpha=alpha * dep[i], solid_capstyle="round",
                                zorder=zorder)
            else:
                ax.plot(bx, by, color=col,
                        linewidth=max(0.15, bw * p),
                        alpha=alpha * float(dep.mean()),
                        solid_capstyle="round",
                        zorder=zorder)

    def dab(self, ax, cx, cy, radius=0.3, color=None, pressure=1.0):
        """Одиночный отпечаток кисти (тычок) — для цветов и листвы."""
        col = color or self.paint
        r = radius * (0.6 + 0.6 * pressure)
        n = self.bristles
        for _ in range(n):
            a = self.rng.uniform(0, 2 * np.pi)
            rr = r * self.rng.uniform(0.3, 1.0)
            px = cx + rr * np.cos(a)
            py = cy + rr * np.sin(a)
            ax.plot([px], [py], marker="o", markersize=r * 9,
                    color=col, alpha=0.85, zorder=3)
        self._spent += 0.02

    def fan_out(self, ax, cx, cy, radius=1.2, spread_angle=np.pi / 3,
                color=None, n_rays=9):
        """Веер щетин (веерная кисть) — для травы, волос, сияния."""
        col = color or self.paint
        base = -np.pi / 2
        for i in range(n_rays):
            a = base - spread_angle / 2 + spread_angle * i / max(1, n_rays - 1)
            jitter = self.rng.uniform(-0.03, 0.03)
            xs = [cx, cx + radius * np.cos(a + jitter)]
            ys = [cy, cy + radius * np.sin(a + jitter)]
            ax.plot(xs, ys, color=col, linewidth=0.6, alpha=0.7,
                    solid_capstyle="round", zorder=2)


# ============================================================
#  Масляные техники
# ============================================================


def impasto(ax, x, y, color, thickness=0.4, width=1.0, alpha=0.95,
            rng=None, seed=None):
    """
    @brief Густой рельефный мазок (импосто).

    Краска ложится толстым слоем: основной мазок, бороздки щетин и
    свето-теневой рельеф по краям. Рваные края дают живую фактуру.
    """
    rng = rng or random.Random(seed)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)

    theta = np.arctan2(np.gradient(y), np.gradient(x))
    nx = -np.sin(theta)
    ny = np.cos(theta)

    t = np.linspace(0, 1, n)
    # толщина рельефа колеблется вдоль мазка
    thick = thickness * (0.55 + 0.45 * np.abs(np.sin(t * (4 + rng.randint(2, 5)))))

    # нижний тёмный слой (тень рельефа)
    for off in (0.75, 0.5):
        bx = x + nx * off * thick
        by = y + ny * off * thick
        ax.plot(bx, by, color=shade(color, -0.35), linewidth=width * 0.7,
                alpha=alpha, solid_capstyle="round", zorder=1)
        ax.plot(x - nx * off * thick, y - ny * off * thick,
                color=shade(color, -0.35), linewidth=width * 0.7,
                alpha=alpha, solid_capstyle="round", zorder=1)

    # основной густой слой
    ax.plot(x, y, color=color, linewidth=width * 2.2, alpha=alpha,
            solid_capstyle="round", zorder=2)

    # бороздки щетин на поверхности
    for k in range(4):
        off = (k - 1.5) * thick * 0.25
        bx = x + nx * off
        by = y + ny * off
        ax.plot(bx, by, color=shade(color, 0.12), linewidth=width * 0.3,
                alpha=alpha * 0.6, solid_capstyle="round", zorder=3)

    # светлая бликовая кромка сверху
    bx = x + nx * thick * 0.55
    by = y + ny * thick * 0.55
    ax.plot(bx, by, color=shade(color, 0.4), linewidth=width * 0.5,
            alpha=alpha * 0.8, solid_capstyle="round", zorder=3)


def glaze(ax, x, y, color, alpha=0.3, width=1.0, wobble=0.02, seed=None):
    """
    @brief Лессировка — тонкий полупрозрачный слой.

    Краска наносится жидким полупрозрачным слоем поверх подсохшего низа.
    Используется для моделирования света и глубины.
    """
    rng = random.Random(seed)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    theta = np.arctan2(np.gradient(y), np.gradient(x))
    nx = -np.sin(theta)
    ny = np.cos(theta)
    # лёгкие колебания кисти
    w = np.linspace(0, 2 * np.pi, n)
    jx = 0.03 * np.sin(w * 3) + wobble * rng.uniform(-1, 1)
    jy = 0.03 * np.cos(w * 5) + wobble * rng.uniform(-1, 1)
    ax.plot(x + jx, y + jy, color=color, linewidth=width * 1.4,
            alpha=alpha, solid_capstyle="round", zorder=1)
    # второй проход усиливает прозрачный эффект
    ax.plot(x - jx, y - jy, color=color, linewidth=width * 1.0,
            alpha=alpha * 0.7, solid_capstyle="round", zorder=1)


def wet_on_wet(ax, x, y, c1, c2, width=1.2, steps=6, alpha=0.5, seed=None):
    """
    @brief Алла прима — смешивание краски прямо на холсте.

    Два цвета вводятся один в другой по длине мазка, давая мягкие
    переходы без видимых стыков (как на сыром холсте).
    """
    rng = random.Random(seed)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    for i in range(n - 1):
        t = i / (n - 1)
        seg_color = mix(c1, c2, t)
        w = width * (0.8 + 0.4 * np.sin(np.pi * t))
        ax.plot([x[i], x[i + 1]], [y[i], y[i + 1]],
                color=seg_color, linewidth=w, alpha=alpha,
                solid_capstyle="round", zorder=2)
    # смягчающие мазки вдоль краёв
    theta = np.arctan2(np.gradient(y), np.gradient(x))
    for off, al in ((0.3, 0.4), (-0.3, 0.4)):
        bx = x - np.sin(theta) * off * width
        by = y + np.cos(theta) * off * width
        ax.plot(bx, by, color=mix(c1, c2, 0.5), linewidth=width * 0.5,
                alpha=al * 0.6, solid_capstyle="round", zorder=1)


def dry_brush(ax, x, y, color, width=1.0, alpha=0.6, seed=None):
    """
    @brief Сухая кисть — процарапывание тонкими прерывистыми щетинами.
    """
    rng = random.Random(seed)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    theta = np.arctan2(np.gradient(y), np.gradient(x))
    for k in range(5):
        off = (k - 2) * width * 0.18
        bx = x - np.sin(theta) * off
        by = y + np.cos(theta) * off
        for i in range(1, n):
            if rng.random() < 0.8:
                ax.plot([bx[i - 1], bx[i]], [by[i - 1], by[i]],
                        color=color, linewidth=width * 0.15, alpha=alpha,
                        solid_capstyle="round", zorder=2)


# ============================================================
#  Композиционные сцены (демо-рецепты)
# ============================================================


def oil_scene_demo(ax=None, seed=None, title="Масляный натюрморт"):
    """
    @brief Готовая демо-сцена: масляный натюрморт двойником кисти.

    Показывает все техники: импосто, лессировку, wet-on-wet, сухую кисть,
    веер и отпечатки щетин.
    """
    import matplotlib.pyplot as plt
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("#e8dcc0")

    rng = random.Random(seed)
    t = np.linspace(0, 1, 120)

    # --- фон: лессировка неба/стены ---
    sky_y = 4.5 - t * 2.0
    glaze(ax, t * 10 - 5, sky_y, color="#b0a888", alpha=0.25, width=2.5)

    # --- стол: импосто деревянной поверхности ---
    table_x = np.linspace(-5, 5, 140)
    table_y = -3.6 + 0.15 * np.sin(table_x * 2 + rng.random())
    impasto(ax, table_x, table_y, color="#6a4522", thickness=0.25, width=1.2)

    # --- ваза: wet-on-wet из двух цветов ---
    v = np.linspace(0, np.pi, 80)
    vase_x = 0.5 * np.cos(v)
    vase_y = -3.5 + 3.2 * np.sin(v)
    wet_on_wet(ax, vase_x, vase_y, c1="#3a2a1a", c2="#7a5a3a",
               width=1.0, steps=8, alpha=0.85)

    # --- горлышко вазы: сухая кисть ---
    neck_x = np.array([-0.25, 0.0, 0.25])
    neck_y = np.array([-0.2, 0.3, -0.2])
    dry_brush(ax, neck_x, neck_y, color="#2a1a0a", width=0.4)

    # --- груша: импосто мазок ---
    pr = np.linspace(0, 2 * np.pi, 100)
    pear_x = 2.6 + 0.55 * np.cos(pr)
    pear_y = -2.4 + 0.75 * np.sin(pr)
    ax.plot(pear_x, pear_y, color="#8a7a20", linewidth=2.2, zorder=1)
    impasto(ax, pear_x * 0.98, pear_y * 0.98, color="#c8a020",
            thickness=0.18, width=0.8, alpha=0.9)
    # блик
    ax.plot([2.6, 2.6 + 0.2], [-2.1, -1.95], color="#f0e8c0",
            linewidth=0.6, alpha=0.9, zorder=4)

    # --- яблоко: wet-on-wet красно-жёлтый ---
    ar = np.linspace(0, 2 * np.pi, 100)
    app_x = -1.8 + 0.6 * np.cos(ar)
    app_y = -2.3 + 0.6 * np.sin(ar)
    wet_on_wet(ax, app_x, app_y, c1="#8a1a10", c2="#c8a020",
               width=0.7, alpha=0.9)

    # --- виноград: отпечатки кисти ---
    brush = OilBrushTwin(size="round", paint="#5a2a6a", load=0.9, seed=seed)
    for i in range(14):
        gx = 2.3 - (i % 5) * 0.32
        gy = -3.2 + (i // 5) * 0.3 - (i % 2) * 0.1
        brush.dab(ax, gx, gy, radius=0.16, pressure=0.9)

    # --- сияние / листва: веерная кисть ---
    fan_brush = OilBrushTwin(size="fan", paint="#6a8a2a", load=0.8, seed=seed)
    for fx, fy in [(-3.6, 2.8), (3.8, 2.5), (-4.2, 0.8), (4.0, 0.2)]:
        fan_brush.fan_out(ax, fx, fy, radius=0.8,
                          spread_angle=np.pi / 2.5, n_rays=7)

    # --- стебли: линейная кисть ---
    liner = OilBrushTwin(size="liner", paint="#3a6a2a", load=0.9, seed=seed)
    for s in range(4):
        sx = -3.6 + s * 0.25
        sy = np.linspace(-3.4, 2.8, 60)
        sxx = sx + 0.05 * np.sin(np.linspace(0, 6, 60))
        liner.stroke(ax, sxx, sy, pressure=0.5, lw_mult=0.4)

    ax.set_title(title, fontsize=12, color="#3a2a1a")
    return ax


def oil_scene_still_life(save_to=None, dpi=150, seed=None):
    """
    @brief Скомпоновать и сохранить масляный натюрморт.
    """
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(8, 8),
                           facecolor="#e8dcc0")
    oil_scene_demo(ax, seed=seed, title="Натюрморт — цифровой двойник кисти")
    if save_to:
        fig.savefig(save_to, dpi=dpi, bbox_inches="tight",
                    facecolor="#e8dcc0")
        print(f"[OK] Saved: {save_to}")
    else:
        plt.show()
    plt.close(fig)
    return ax


if __name__ == "__main__":
    import sys, io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                      errors="replace")
    oil_scene_still_life("oil_brush_twin_demo.png", dpi=150, seed=42)
    print("Готово: oil_brush_twin_demo.png")
