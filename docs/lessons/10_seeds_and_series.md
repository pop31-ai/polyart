# PolyArt Урок 10: Seed, вариативность и серия картин

## Цель

Научиться управлять случайностью (`seed`) и создавать серии
уникальных картин одной темы.

## Как работает seed

Двойник кисти использует свой генератор случайных чисел. Задавая
`seed`, вы получаете воспроизводимую фактуру:

```python
from polyart_brush_twin import OilBrushTwin

b1 = OilBrushTwin(size="flat", paint="#c8a040", seed=42)
b2 = OilBrushTwin(size="flat", paint="#c8a040", seed=42)  # тот же результат
b3 = OilBrushTwin(size="flat", paint="#c8a040", seed=7)   # другая фактура
```

## Серия картин одной темы

```python
import numpy as np
from polyart_painter import PainterCanvas

def sea_sunset(seed):
    t = np.linspace(-6, 6, 200)
    c = PainterCanvas(name=f"Закат {seed}", xlim=(-6, 6), ylim=(-6, 6))
    c.wet_on_wet(t, 3, c1="#f0c020", c2="#d94a2a", width=2.4)
    c.brush(size="flat", paint="#2a4a8a", load=0.8, seed=seed)
    c.stroke(t, -2 + 0.3*np.sin(t + seed*0.5), pressure=0.6, lw_mult=1.2)
    return c

for seed in range(8):
    sea_sunset(seed).render(f"series/sunset_{seed}.png", dpi=150)
```

## Галерея

```python
# сетка 4x2 для презентации
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
for i, ax in enumerate(axes.flat):
    # отрисовать сцену в нужный ax (см. урок 09)
    ...
```

## Когда использовать seed

- **Фиксировать** результат для печати/тиража.
- **Подбирать** лучший из N вариантов (подбор seed).
- **Серии** для NFT, коллекций, стикерпаков.
- **Тесты** — воспроизводимость в CI.

## Задание

Сгенерируйте серию из 6 «Морских закатов» с разными seed. Выберите
лучший и зафиксируйте его seed в названии файла.

## Проверка

- Одинаковый seed даёт одинаковую картинку.
- Разные seed — заметно разные фактуры мазков.
