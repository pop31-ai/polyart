# PolyArt Урок 01: Цифровой двойник кисти

## Цель

Познакомиться с `OilBrushTwin` — цифровым двойником живописной кисти
с масляной краской. Научиться наносить первые мазки.

## Что понадобится

- Python 3.8+
- `numpy`, `matplotlib` (см. `requirements.txt`)
- модуль `polyart_brush_twin.py` из репозитория

## Шаг 1. Холст

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.set_aspect("equal")
ax.axis("off")
```

## Шаг 2. Первый мазок двойником кисти

```python
import numpy as np
from polyart_brush_twin import OilBrushTwin

brush = OilBrushTwin(size="flat", paint="#c8a040", load=0.9)

t = np.linspace(-4, 4, 120)
x = t
y = 0.5 * np.sin(t)

brush.stroke(ax, x, y, pressure=0.7)
```

Мазок нанесён пучком щетин: вы увидите несколько параллельных тонких
линий — это щетины цифрового двойника.

## Шаг 3. Разные типы кисти

```python
kinds = ["round", "flat", "filbert", "fan", "liner"]
for i, kind in enumerate(kinds):
    bx = OilBrushTwin(size=kind, paint="#3a5a8a", load=0.8)
    yy = 4 - i * 1.8
    bx.stroke(ax, np.linspace(-4, 4, 100), yy + 0.2 * np.sin(np.linspace(0, 4, 100)),
              pressure=0.6)
```

- `round` — круглая, тонкий след
- `flat` — плоская, широкий мазок
- `filbert` — средняя, скруглённая
- `fan` — веерная, широчайшая
- `liner` — линейная, самая тонкая

## Шаг 4. Давление и поворот

```python
brush.stroke(ax, x, y, pressure=0.9, angle=0.0)   # сильный нажим
brush.stroke(ax, x, y - 1, pressure=0.3, angle=0.0)  # лёгкий нажим
brush.stroke(ax, x, y - 2, pressure=0.6, angle=np.pi/2)  # поворот
```

Чем больше давление — тем шире и плотнее мазок. Поворот кисти
меняет ширину следа (щетины встают ребром).

## Шаг 5. Сохранить результат

```python
plt.savefig("lesson01_first_strokes.png", dpi=150)
```

## Задание

Нарисуйте три горизонтальных мазка тремя разными кистями
(round, flat, fan) с разным давлением. Сохраните как PNG.

## Проверка

- В выводе видны следы отдельных щетин (не одна линия).
- Разные типы кисти дают заметно разную ширину мазка.
