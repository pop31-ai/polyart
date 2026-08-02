# PolyArt Урок 05: Истощение краски и сухая кисть

## Цель

Научиться управлять истощением краски на кисти и приёмом «сухой кисти»
(dry brush) — процарапыванием прерывистых следов.

## Теория

Настоящая кисть отдаёт краску по мере мазка: чем дальше штрих — тем
суше след. Двойник кисти хранит остаток краски в `_spent` и ослабляет
мазок к концу. При `dry_brush=True` щетины оставляют прерывистые следы.

## Простой пример

```python
import numpy as np
from polyart_brush_twin import OilBrushTwin, dry_brush

x = np.linspace(-4, 4, 140)
y = np.zeros_like(x)

brush = OilBrushTwin(size="flat", paint="#5a7a2a", load=0.9)
brush.stroke(ax, x, y, pressure=0.6, dry_brush=True)
```

В начале мазок плотный, к концу — редкие щетины на белом фоне.

## Управление загрузкой

```python
# Полная кисть
b1 = OilBrushTwin(size="flat", paint="#8a3a1a", load=1.0)
b1.stroke(ax, x, y + 1.5, pressure=0.6, dry_brush=False)

# Наполовину истощённая кисть
b2 = OilBrushTwin(size="flat", paint="#8a3a1a", load=0.45)
b2.stroke(ax, x, y, pressure=0.6, dry_brush=False)

# Почти пустая кисть
b3 = OilBrushTwin(size="flat", paint="#8a3a1a", load=0.15)
b3.stroke(ax, x, y - 1.5, pressure=0.6, dry_brush=False)
```

## Сухая кисть как техника

Функция `dry_brush` создаёт тонкие прерывистые процарапывания —
отлично для травы, меха, старых досок:

```python
from polyart_brush_twin import dry_brush

for i in range(20):
    gx = np.array([-4 + i * 0.4, -4 + i * 0.4 + 0.2])
    gy = np.array([-3.5, -3.5 - 0.3 * (i % 3)])
    dry_brush(ax, gx, gy, color="#5a8a2a", width=0.5, alpha=0.7)
```

## Задание

Нарисуйте пучок травы: 15-25 стеблей, начиная плотными (кисть с load
0.9), к краям — сухой кистью (load 0.2, dry_brush=True).

## Проверка

- Плотность мазка падает от начала к концу.
- При `dry_brush=True` след прерывистый, из отдельных штрихов.
- Разная загрузка кисти даёт ощутимо разный результат.
