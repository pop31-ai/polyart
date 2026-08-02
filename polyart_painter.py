"""
@file polyart_painter.py
@brief Живописный холст PainterCanvas — интеграция двойника кисти в Canvas API
@author PolyArt Project
@version 1.0.0
@date 2026

@par Описание
Расширяет базовый `Canvas` из `polyart_api` методами масляной живописи.
Все объекты полиарта (кривые, орнаменты, суперформулы) остаются доступны,
а поверх них можно класть мазки цифрового двойника кисти.

@par Пример
@code
from polyart_painter import PainterCanvas

c = PainterCanvas(name="Закат", xlim=(-6, 6), ylim=(-6, 6), background="#f0e8d8")
c.oil_layer("небо")
c.wet_on_wet(np.linspace(-6, 6, 200), 3 - np.linspace(-6, 6, 200)*0.1,
             c1="#2a4a8a", c2="#c8a040", width=2.2)
c.impasto(np.array([-5, -3, -1, 1, 3, 5]), np.array([-1, 1, 0, 1.5, 0, -1]),
          color="#4a6a5a", thickness=0.4)
c.save("zakat.polyart")
c.render("zakat.png")
@endcode
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from polyart_api import Canvas
except ImportError:
    from .polyart_api import Canvas

from polyart_brush_twin import (
    OilBrushTwin,
    impasto,
    glaze,
    wet_on_wet,
    dry_brush,
    hex_to_rgb,
    rgb_to_hex,
    mix,
    shade,
)


class PainterCanvas(Canvas):
    """
    @brief Живописный холст: Canvas + масляные техники.

    Наследует весь функционал полиарт-API и добавляет мазки кисти,
    записывая их в отдельный слой "paint" в структуре данных.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._paint_strokes = []

    # ------------------------------------------------------------
    #  Мазки кисти
    # ------------------------------------------------------------

    def brush(self, size="flat", paint="#c8a040", load=0.9, **kw) -> "PainterCanvas":
        """Создать двойник кисти и запомнить как текущий."""
        self._brush = OilBrushTwin(size=size, paint=paint, load=load, **kw)
        return self

    def stroke(self, x, y, **kw) -> "PainterCanvas":
        """Мазок текущей кистью (или созданной по умолчанию)."""
        brush = getattr(self, "_brush", None) or OilBrushTwin(size="flat", paint="#c8a040")
        self._paint_strokes.append(("stroke", brush, (np.asarray(x, dtype=float),
                                                      np.asarray(y, dtype=float)), dict(kw)))
        return self

    def dab(self, cx, cy, radius=0.3, **kw) -> "PainterCanvas":
        """Отпечаток кисти (тычок)."""
        brush = getattr(self, "_brush", None) or OilBrushTwin(size="round", paint="#c8a040")
        self._paint_strokes.append(("dab", brush, (cx, cy, radius), dict(kw)))
        return self

    def fan(self, cx, cy, radius=1.0, spread_angle=np.pi / 3, n_rays=8, **kw) -> "PainterCanvas":
        """Веер щетин."""
        brush = getattr(self, "_brush", None) or OilBrushTwin(size="fan", paint="#c8a040")
        self._paint_strokes.append(("fan", brush, (cx, cy, radius, spread_angle, n_rays), dict(kw)))
        return self

    # ------------------------------------------------------------
    #  Масляные техники
    # ------------------------------------------------------------

    def impasto(self, x, y, color="#8a2a2a", thickness=0.35, width=1.2,
                alpha=0.95, **kw) -> "PainterCanvas":
        """Густой рельефный мазок."""
        self._paint_strokes.append(("impasto", None,
                                    (np.asarray(x, dtype=float), np.asarray(y, dtype=float)),
                                    dict(color=color, thickness=thickness, width=width,
                                         alpha=alpha, **kw)))
        return self

    def glaze(self, x, y, color="#c8a040", alpha=0.3, width=1.0, **kw) -> "PainterCanvas":
        """Лессировка — полупрозрачный слой."""
        self._paint_strokes.append(("glaze", None,
                                    (np.asarray(x, dtype=float), np.asarray(y, dtype=float)),
                                    dict(color=color, alpha=alpha, width=width, **kw)))
        return self

    def wet_on_wet(self, x, y, c1="#d94a6e", c2="#4a90d9", width=1.2,
                   alpha=0.8, **kw) -> "PainterCanvas":
        """Алла прима — смешивание двух цветов на холсте."""
        self._paint_strokes.append(("wet_on_wet", None,
                                    (np.asarray(x, dtype=float), np.asarray(y, dtype=float)),
                                    dict(c1=c1, c2=c2, width=width, alpha=alpha, **kw)))
        return self

    def dry_brush(self, x, y, color="#5a8a2a", width=1.0, alpha=0.6, **kw) -> "PainterCanvas":
        """Сухая кисть — прерывистые процарапывания."""
        self._paint_strokes.append(("dry_brush", None,
                                    (np.asarray(x, dtype=float), np.asarray(y, dtype=float)),
                                    dict(color=color, width=width, alpha=alpha, **kw)))
        return self

    # ------------------------------------------------------------
    #  Рендер с мазками
    # ------------------------------------------------------------

    def render(self, save_to=None, dpi=200, figsize=None, round=False) -> "PainterCanvas":
        """
        @brief Рендер объектов Canvas + масляных мазков.
        """
        canvas = self.data["canvas"]
        w = figsize[0] if figsize else canvas.get("width", 10)
        h = figsize[1] if figsize else canvas.get("height", 10)
        fig, ax = plt.subplots(1, 1, figsize=(w, h),
                                facecolor=canvas.get("background", "#f5efe0"))
        ax.set_facecolor(canvas.get("background", "#f5efe0"))
        ax.set_xlim(canvas.get("xlim", [-5, 5]))
        ax.set_ylim(canvas.get("ylim", [-5, 5]))
        ax.set_aspect("equal")
        ax.axis("off")

        for layer in self.data.get("layers", []):
            for obj in layer.get("objects", []):
                self._draw(ax, obj)

        for f in self.data.get("formulas", []):
            ax.text(f["x"], f["y"], f["expr"],
                    fontsize=f.get("fontsize", 8),
                    fontfamily="serif", color=f.get("color", "#8a6a4a"),
                    fontstyle="italic")

        for stroke in self._paint_strokes:
            self._apply_paint(ax, stroke)

        if round:
            from matplotlib.patches import Circle as _ClipCircle
            xlim = canvas.get("xlim", [-5, 5])
            ylim = canvas.get("ylim", [-5, 5])
            cx = (xlim[0] + xlim[1]) / 2
            cy = (ylim[0] + ylim[1]) / 2
            radius = min(xlim[1] - xlim[0], ylim[1] - ylim[0]) / 2
            clip = _ClipCircle((cx, cy), radius, transform=ax.transData)
            for artist in list(ax.lines) + list(ax.collections):
                artist.set_clip_path(clip)
            ax.patch.set_alpha(0)
            fig.patch.set_alpha(0)

        if save_to:
            fig.savefig(save_to, dpi=dpi, bbox_inches="tight",
                        facecolor="none" if round else canvas.get("background", "#f5efe0"),
                        transparent=bool(round))
            print(f"[OK] Rendered: {save_to}")
        else:
            plt.show()
        plt.close(fig)
        return self

    def _apply_paint(self, ax, stroke):
        """Применить один зарегистрированный мазок к axes."""
        kind, brush, args, kw = stroke
        if kind == "stroke":
            x, y = args
            brush.stroke(ax, x, y, **kw)
        elif kind == "dab":
            cx, cy, radius = args
            brush.dab(ax, cx, cy, radius=radius, **kw)
        elif kind == "fan":
            cx, cy, radius, spread_angle, n_rays = args
            brush.fan_out(ax, cx, cy, radius=radius, spread_angle=spread_angle,
                          n_rays=n_rays, **kw)
        elif kind == "impasto":
            x, y = args
            impasto(ax, x, y, **kw)
        elif kind == "glaze":
            x, y = args
            glaze(ax, x, y, **kw)
        elif kind == "wet_on_wet":
            x, y = args
            wet_on_wet(ax, x, y, **kw)
        elif kind == "dry_brush":
            x, y = args
            dry_brush(ax, x, y, **kw)


# ============================================================
#  Готовые живописные сцены
# ============================================================


class PaintTemplates:
    """Готовые сцены масляной живописи на PainterCanvas."""

    @staticmethod
    def sunset_sea() -> PainterCanvas:
        """Закат над морем: wet-on-wet небо, импосто солнце, море."""
        c = PainterCanvas(name="Закат над морем", xlim=(-6, 6), ylim=(-6, 6),
                          background="#f0e0c0")
        t = np.linspace(-6, 6, 220)
        c.wet_on_wet(t, 3 - t * 0.08, c1="#f0c020", c2="#d94a2a", width=2.4, alpha=0.85)
        c.wet_on_wet(t, 1.5 - t * 0.05, c1="#d94a2a", c2="#8a2a5a", width=2.2, alpha=0.8)
        sun = np.linspace(0, 2 * np.pi, 100)
        c.impasto(0.7 * np.cos(sun), 1.8 + 0.7 * np.sin(sun),
                  color="#ffe060", thickness=0.3, width=1.2)
        c.wet_on_wet(t, -2 - t * 0.02, c1="#2a4a8a", c2="#8a2a5a", width=2.0, alpha=0.75)
        c.wet_on_wet(t, -3 - t * 0.02, c1="#4a90d9", c2="#2a4a8a", width=2.0, alpha=0.7)
        return c

    @staticmethod
    def autumn_forest() -> PainterCanvas:
        """Осенний лес: стволы, кроны отпечатками, листва веером."""
        c = PainterCanvas(name="Осенний лес", xlim=(-6, 6), ylim=(-6, 6),
                          background="#e8dcc0")
        # подлесок лессировкой
        t = np.linspace(-6, 6, 200)
        c.glaze(t, -4.5 + 0.2 * np.sin(t * 2), color="#8a6a3a", alpha=0.25, width=2.5)
        # стволы
        b = c.brush(size="liner", paint="#3a2a1a", load=0.9)
        for x0 in [-4.5, -2.5, -0.5, 1.5, 3.5]:
            c.stroke([x0, x0 + 0.15], [-4.5, 2.5], pressure=0.7, lw_mult=0.6)
        # кроны отпечатками
        leaf = c.brush(size="round", paint="#c8501a", load=0.85)
        for x0 in [-4.5, -2.5, -0.5, 1.5, 3.5]:
            for _ in range(20):
                import random
                c.dab(x0 + random.uniform(-0.6, 0.6), random.uniform(0.5, 2.6),
                      radius=random.uniform(0.12, 0.2),
                      pressure=random.uniform(0.6, 1.0))
        # жёлтые блики веером
        gold = c.brush(size="fan", paint="#f0c020", load=0.7)
        for x0 in [-4.5, -2.5, -0.5, 1.5, 3.5]:
            c.fan(x0, 2.6, radius=0.6, spread_angle=0.6, n_rays=5)
        return c

    @staticmethod
    def winter_sunset() -> PainterCanvas:
        """Зимний закат: холодное небо, ледяное море, сугробы."""
        c = PainterCanvas(name="Зимний закат", xlim=(-6, 6), ylim=(-6, 6),
                          background="#c0d8e8")
        t = np.linspace(-6, 6, 220)
        c.wet_on_wet(t, 4 - t * 0.05, c1="#3a5a8a", c2="#c8a040", width=2.3, alpha=0.8)
        c.glaze(t, 2 - t * 0.03, color="#d94a6e", alpha=0.25, width=2.4)
        sun = np.linspace(0, 2 * np.pi, 100)
        c.impasto(0.8 * np.cos(sun), 0.6 + 0.8 * np.sin(sun),
                  color="#ffe080", thickness=0.28, width=1.2)
        # лёд wet-on-wet
        c.wet_on_wet(t, -2 - t * 0.01, c1="#b0c8e0", c2="#d9e8f0", width=2.2, alpha=0.75)
        # сугробы dry_brush
        c.dry_brush(t, -4.2 + 0.2 * np.sin(t * 2.5), color="#e8f0f8", width=0.7, alpha=0.6)
        return c


if __name__ == "__main__":
    import sys, io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    PaintTemplates.sunset_sea().render("paint_demo_sunset.png", dpi=150)
    PaintTemplates.autumn_forest().render("paint_demo_forest.png", dpi=150)
    PaintTemplates.winter_sunset().render("paint_demo_winter.png", dpi=150)
    print("Готово: paint_demo_*.png")
