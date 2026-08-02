# PolyArt Урок 09: Анимация масляных фонов

## Цель

Научиться делать анимированные масляные фоны: плавно менять цвета,
положение и настройки кисти кадр за кадром.

## Принцип

Параметры (`c1`, `c2`, `alpha`, `thickness`, положение) задаются
функцией времени. Каждый кадр — новая сцена, но с плавными
изменениями. Двойник кисти добавляет лёгкую «дрожь» фактуры.

## Пример: рассвет за 30 кадров

```python
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from polyart_painter import PainterCanvas

t = np.linspace(-6, 6, 180)

for frame in range(30):
    k = frame / 29  # 0..1
    c = PainterCanvas(name=f"Рассвет {frame}", xlim=(-6, 6), ylim=(-6, 6),
                      background="#1a2a3a")

    # небо медленно светлеет
    c.wet_on_wet(t, 3 - t*0.05,
                 c1=mix("#2a4a8a", "#f0c020", k),
                 c2=mix("#8a2a5a", "#d94a2a", k),
                 width=2.4, alpha=0.85)

    # солнце поднимается
    sun_y = -2 + 4.5 * k
    sun = np.linspace(0, 2*np.pi, 90)
    c.impasto(0.7*np.cos(sun), sun_y + 0.7*np.sin(sun),
              color="#ffe060", thickness=0.25 + 0.1*k)

    c.render(f"frames/dawn_{frame:02d}.png", dpi=100)
```

## Склейка в GIF

```python
from PIL import Image
frames = [Image.open(f"frames/dawn_{i:02d}.png") for i in range(30)]
frames[0].save("dawn.gif", save_all=True, append_images=frames[1:],
               duration=100, loop=0)
```

## Советы

- Меняйте `seed` двойника кисти каждый кадр — фактура будет «дышать».
- Держите `alpha` невысокой для плавных переходов.
- Используйте 100-150 dpi для веб-анимации.

## Задание

Сделайте анимацию «Закат в горах»: небо темнеет, солнце садится,
на горах зажигаются огни (dab жёлтым).

## Проверка

- Кадры образуют плавный переход.
- GIF циклический, без скачков.
