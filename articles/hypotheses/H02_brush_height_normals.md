# H02 — Карта высоты мазка: нормали импасто без растровых текстур

**Статус:** idea · **Каталог:** внешние гипотезы PolyArt

## Abstract

`OilBrushTwin` already simulates bristles, pressure and paint depletion
as vectors. If we additionally accumulate every stroke into a scalar
*height field*, we get normals for free — enabling impasto shading in
any renderer (including Canvas2D) while shipping zero bitmaps.

---

## 1. Гипотеза

Высота мазка — известная функция его параметров (ширина, давление,
истощение). Значит рельеф `impasto` можно **вычислять**, а не хранить:
`.polyart` остаётся коэффициентами, а светотень становится производным
рендером — в полном согласии с философией «упоминание с координатами».

## 2. Упоминания

- `docs/ARCHITECTURE_brush_twin.md` → физическая модель: ширина
  `0.6 + 0.8*p`, поворот `0.55 + 0.45*|cos(angle)|`, истощение
  `load * (1 - spent)` — всё это уже скалярные поля вдоль кривой;
- `polyart_brush_twin.py:260` → `impasto()` рисует тень/бороздки/блик
  вручную; H02 заменяет эвристики единым рельефом;
- `articles/procedural_texture_synthesis.md` → принцип: текстура как
  функция, бесконечное разрешение бесплатно.

## 3. Подходы

1. **Аналитический**: для каждой щетины высота
   `z(t) = thickness * profile(s_perp) * depletion(t)`, где
   `profile` — гауссов бугорок поперёк мазка. Складываем вклады в сетку.
2. **Сплайн-тени** (быстрый): нормаль только вдоль нормали кривой,
   рендерим градиентной лентой — годится для Canvas2D без сетки.
3. **Полный рельеф**: сетка 256², накапливаем max-композитинг,
   Собелом получаем нормали — путь к WebGL позже.

## 4. Код (референс подхода 1)

```python
def stroke_height_field(strokes, res=256, domain=((-5,5),(-5,5))):
    """strokes: [(px, py, width, pressure, load)] — полиномы brush_twin."""
    Z = np.zeros((res, res))
    xs = np.linspace(*domain[0], res); ys = np.linspace(*domain[1], res)
    X, Y = np.meshgrid(xs, ys)
    for px, py, w, p, load in strokes:
        t = np.linspace(0, 1, 200)
        cx, cy = np.polyval(px[::-1], t), np.polyval(py[::-1], t)   # центр
        dx, dy = np.gradient(cx), np.gradient(cy)
        L = np.hypot(dx, dy) + 1e-9
        nx, ny = -dy/L, dx/L                                        # нормаль
        halfw = (0.6 + 0.8*p) * w / 2
        for j in range(len(t)):
            s = (X-cx[j])*nx[j] + (Y-cy[j])*ny[j]                   # поперёк
            g = np.exp(-(s/halfw)**2)                               # бугорок
            Z += 0.05 * g * (load * (1 - t[j]))                     # истощение
    return Z

def normals_from_height(Z):
    gy, gx = np.gradient(Z)
    n = np.dstack([-gx, -gy, np.ones_like(Z)])
    return n / np.linalg.norm(n, axis=2, keepdims=True)
```

## 5. Как проверить

```
1. render impasto-сцены текущим impasto()           -> A.png
2. render той же сцены плоским цветом + свет из
   normals_from_height                              -> B.png
3. PolyArtCVTest.analyze_image на оба
гипотеза подтверждена, если rarity(B) >= rarity(A) - 2
при отсутствии растр-зависимостей в B
```

Дополнительно: A/B-тест «на глаз» у 5+ зрителей на предмет
«где краска гуще».

## 6. Риски

- Сетка 256² на сотни мазков — секунды CPU; нужен композитинг по bbox;
- Перекрытие мазков через `max`, а не сумму (краска не складывается);
- В SVG-экспорте рельеф вырождается в градиенты — печатать с оговоркой.

## См. также

- [H01](H01_texture_field_objects.md) — тот же принцип для заливок
- `docs/lessons/02_impasto.md`, `05_paint_depletion.md`
