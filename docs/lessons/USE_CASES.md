# PolyArt Кейсы применения: цифровой двойник кисти

Готовые сценарии использования `OilBrushTwin` — от простых к сложным.

---

## Кейс 1. Пейзаж за 10 строк

```python
import numpy as np
from polyart_brush_twin import wet_on_wet, impasto, OilBrushTwin

t = np.linspace(-5, 5, 160)
wet_on_wet(ax, t, 3 - t*0.05, c1="#2a4a8a", c2="#c8a040", width=2.5)  # небо
ridge = np.array([-5, -3, -1, 1, 3, 5]); ry = np.array([-1, 1, 0, 1.5, 0, -1])
impasto(ax, ridge, ry, color="#4a6a5a", thickness=0.4, width=1.5)     # горы
b = OilBrushTwin(size="liner", paint="#1a0a0a")
b.stroke(ax, [0, 0], [-2, 2])                                        # ствол
```

Результат: небо, горы и дерево — полноценный эскиз пейзажа.

---

## Кейс 2. Натюрморт (готовая сцена)

```python
from polyart_brush_twin import oil_scene_demo
oil_scene_demo(ax, seed=7, title="Натюрморт")
```

Готовая сцена: ваза, фрукты, виноград, листва. Показывает все техники.

---

## Кейс 3. Морской закат

```python
from polyart_brush_twin import wet_on_wet, impasto
t = np.linspace(-5, 5, 180)
wet_on_wet(ax, t, 2 - t*0.05, c1="#ffd060", c2="#e06030", width=2.2)  # небо
impasto(ax, 0.6*np.cos(np.linspace(0, 6.28, 80)),
        1 + 0.6*np.sin(np.linspace(0, 6.28, 80)),
        color="#ffe060", thickness=0.3)                                # солнце
wet_on_wet(ax, t, -2 - t*0.02, c1="#2a4a8a", c2="#e06030", width=2.2)  # море
```

---

## Кейс 4. Весенний луг

- Трава: `dry_brush` 30 стеблей зелёным.
- Цветы: `dab` красным, жёлтым, белым.
- Небо: `glaze` светло-голубым в 2 слоя.

```python
from polyart_brush_twin import OilBrushTwin, dry_brush
g = OilBrushTwin(size="liner", paint="#5a8a2a")
for i in range(30):
    x0 = -4 + i * 0.27
    dry_brush(ax, [x0, x0 + 0.1], [-3.5, -3.5 - 0.4*(i % 5)], color="#5a8a2a")
f = OilBrushTwin(size="round", paint="#d94a6e", seed=5)
for fx in [-2.5, -1, 0.8, 2.3]:
    for _ in range(5):
        f.dab(ax, fx + np.random.uniform(-0.2, 0.2), -3.4, radius=0.12)
```

---

## Кейс 5. Фрактальное сияние веером

```python
from polyart_brush_twin import OilBrushTwin
fan = OilBrushTwin(size="fan", paint="#c8a020", seed=3)
for r in [0.8, 1.4, 2.0, 2.6]:
    fan.fan_out(ax, 0, 0, radius=r, spread_angle=2*np.pi, n_rays=int(6*r))
```

Получается «солнце» с расходящимися кольцами лучей.

---

## Кейс 6. Портрет маслом

Комбинируйте `polyart_curves` (анатомия) и двойник кисти (фактура):

```python
from polyart_curves import SkeletalCurves
from polyart_brush_twin import OilBrushTwin, glaze
SkeletalCurves.skull(ax, 0, 0, s=2.0, al=0.3)
glaze(ax, np.linspace(-1, 1, 60), -0.4*np.ones(60), color="#8a6a4a", alpha=0.3)
h = OilBrushTwin(size="fan", paint="#2a1a0a")
for a in np.linspace(0, np.pi, 8):
    h.fan_out(ax, -1.0, 0.4, radius=1.2, spread_angle=0.8, n_rays=4)
```

---

## Кейс 7. Текстура старой стены

```python
from polyart_brush_twin import impasto, dry_brush
x = np.linspace(-5, 5, 140)
for i in range(6):
    impasto(ax, x, -3 + i*1.2 + 0.2*np.sin(x*3 + i),
            color=["#8a7a6a", "#7a6a5a", "#9a8a7a", "#6a5a4a", "#8a6a5a", "#7a5a4a"][i],
            thickness=0.12, width=1.4, alpha=0.5)
for i in range(25):
    dry_brush(ax, [np.random.uniform(-5, 5), np.random.uniform(-5, 5)],
              [np.random.uniform(-3, 3), np.random.uniform(-3, 3)],
              color="#3a2a1a", alpha=0.25)
```

---

## Кейс 8. Сцена на живописном холсте (PainterCanvas)

Всё в одном объекте: полиарт-объекты + мазки кисти.

```python
from polyart_painter import PainterCanvas
import numpy as np

c = PainterCanvas(name="Пейзаж", xlim=(-6, 6), ylim=(-6, 6), background="#e8dcc0")
t = np.linspace(-6, 6, 180)
c.wet_on_wet(t, 3 - t*0.05, c1="#2a4a8a", c2="#c8a040", width=2.4)   # небо
c.impasto(np.array([-5, -3, -1, 1, 3, 5]), np.array([-1, 1, 0, 1.5, 0, -1]),
          color="#4a6a5a", thickness=0.4)                             # горы
c.brush(size="liner", paint="#2a1a0a", load=0.9)
c.stroke([0, 0], [-2, 2], pressure=0.7)                              # ствол
c.circle(4, 2, 0.5, fill=True, fill_color="#c8a040", fill_alpha=0.6)  # солнце
c.save("landscape.polyart")
c.render("landscape.png", dpi=150)
```

---

## Кейс 9. Анимированный фон (кадры)

```python
from polyart_painter import PainterCanvas

t = np.linspace(-6, 6, 160)
for frame in range(24):
    k = frame / 23
    c = PainterCanvas(name=f"Кадр {frame}", xlim=(-6, 6), ylim=(-6, 6),
                      background="#1a2a3a")
    c.wet_on_wet(t, 3 - t*0.05,
                 c1=mix("#2a4a8a", "#f0c020", k),
                 c2=mix("#8a2a5a", "#d94a2a", k),
                 width=2.4, alpha=0.8)
    c.render(f"frames/anim_{frame:02d}.png", dpi=100)
```

Склейте кадры в GIF (см. Урок 09).

---

## Кейс 10. Серия для коллекции (seed)

```python
from polyart_painter import PainterCanvas

def collectible(seed):
    t = np.linspace(-6, 6, 200)
    c = PainterCanvas(name=f"Закат #{seed}", xlim=(-6, 6), ylim=(-6, 6))
    c.wet_on_wet(t, 3, c1="#f0c020", c2="#d94a2a", width=2.4)
    c.brush(size="flat", paint="#d94a2a", load=0.8, seed=seed)
    c.stroke(t, -2 + 0.4*np.sin(t*0.7 + seed), pressure=0.6)
    return c

for seed in range(20):
    collectible(seed).render(f"collect/sunset_{seed:03d}.png", dpi=200)
```

---

## Кейс 11. Готовые сцены (PaintTemplates)

```python
from polyart_painter import PaintTemplates

PaintTemplates.sunset_sea().render("sunset.png", dpi=150)
PaintTemplates.autumn_forest().render("forest.png", dpi=150)
PaintTemplates.winter_sunset().render("winter.png", dpi=150)
```

Три темы за три вызова.

---

## Сводка

| Кейс | Техники | Сложность |
|------|---------|-----------|
| Пейзаж | wet_on_wet, impasto, liner | низкая |
| Натюрморт | всё (готовый сценарий) | готовая |
| Морской закат | wet_on_wet, impasto | низкая |
| Весенний луг | dry_brush, dab, glaze | средняя |
| Сияние | fan_out | низкая |
| Портрет | curves + glaze + fan | высокая |
| Стена | impasto, dry_brush | средняя |
| PainterCanvas | все + Canvas API | средняя |
| Анимация | кадры, mix() | средняя |
| Коллекция | seed, серии | низкая |
| Templates | готовые сцены | готовая |
