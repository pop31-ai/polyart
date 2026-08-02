# PolyArt Статья 08: Арт-образование и демонстрация техник

## Проблема

Преподавателям живописи нужны наглядные демонстрации техник
(импосто, лессировка, алла прима) без затрат на материалы.

## Решение

Двойник кисти показывает технику пошагово и с параметрами.
Студент видит не только результат, но и «почему так».

## Плакат «Три техники»

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from polyart_brush_twin import impasto, glaze, wet_on_wet

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
x = np.linspace(-4, 4, 120)

impasto(axes[0], x, 0.5*np.sin(x), color="#8a2a2a", thickness=0.4)
axes[0].set_title("Импосто (густой слой)")

glaze(axes[1], x, 0.5*np.sin(x), color="#4a90d9", alpha=0.3)
axes[1].set_title("Лессировка (прозрачный слой)")

wet_on_wet(axes[2], x, 0.5*np.sin(x), c1="#d94a6e", c2="#4a90d9")
axes[2].set_title("Wet-on-wet (смешивание)")

for ax in axes:
    ax.set_xlim(-5, 5); ax.set_ylim(-2, 2); ax.axis("off")
plt.tight_layout()
plt.savefig("techniques_poster.png", dpi=150)
```

## Пошаговая демонстрация

Покажите наращивание лессировки:

```python
from polyart_brush_twin import glaze

for i in range(1, 11):
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.set_xlim(-5, 5); ax.set_ylim(-1, 1); ax.axis("off")
    ax.plot([-4, 4], [0, 0], color="#c8a888", linewidth=2.5)
    for _ in range(i):
        glaze(ax, np.linspace(-4, 4, 100), np.zeros(100),
              color="#c8a040", alpha=0.2)
    ax.set_title(f"Слоёв: {i}")
    plt.savefig(f"glaze/step_{i:02d}.png", dpi=100)
    plt.close()
```

## Итог

Полиарт-живопись — готовый инструмент для арт-образования:
наглядность, параметры, воспроизводимость, ноль расхода красок.

См. также: Урок 02 (импосто), Урок 03 (лессировка), Урок 04 (wet-on-wet).
