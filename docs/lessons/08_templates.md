# PolyArt Урок 08: Готовые сцены PaintTemplates

## Цель

Научиться использовать готовые сцены `PaintTemplates` и адаптировать
их под свою задачу.

## Три готовых сцены

```python
from polyart_painter import PaintTemplates

PaintTemplates.sunset_sea().render("sunset.png", dpi=150)
PaintTemplates.autumn_forest().render("forest.png", dpi=150)
PaintTemplates.winter_sunset().render("winter.png", dpi=150)
```

- `sunset_sea` — закат над морем (wet-on-wet небо и вода, импосто солнце).
- `autumn_forest` — осенний лес (стволы liner, кроны dab, блики fan).
- `winter_sunset` — зимний закат (холодное небо, лёд, сугробы).

## Кастомизация цветов

```python
c = PaintTemplates.sunset_sea()
# перекрасить в «лунный» вариант
c2 = PaintTemplates.winter_sunset()
c2.data["canvas"]["background"] = "#1a2a3a"
c2.render("moon.png", dpi=150)
```

## Своя сцена на основе шаблона

```python
import numpy as np
from polyart_painter import PainterCanvas

def my_scene():
    c = PainterCanvas(name="Мой пейзаж", xlim=(-6, 6), ylim=(-6, 6))
    t = np.linspace(-6, 6, 200)
    c.wet_on_wet(t, 3, c1="#c8a040", c2="#8a5a2a", width=2.2)
    c.brush(size="flat", paint="#4a6a3a", load=0.8)
    c.stroke(t, -3 + 0.3*np.sin(t), pressure=0.6)
    return c

my_scene().render("mine.png", dpi=150)
```

## Задание

Создайте свою сцену по мотивам `sunset_sea`, добавив 2-3 детали:
птиц (dry_brush), парусник (liner), звёзды (dab).

## Проверка

- Готовые сцены рендерятся без правок.
- Своя сцена сохраняется в `.polyart` и открывается.
