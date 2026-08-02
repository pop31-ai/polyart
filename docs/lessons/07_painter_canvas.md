# PolyArt Урок 07: Живописный холст PainterCanvas

## Цель

Познакомиться с `PainterCanvas` — живописным холстом, который
объединяет полиномиальный API и двойник кисти в одном классе.

## Идея

`PainterCanvas` наследует `Canvas` из `polyart_api`. Все объекты
полиарта (кривые, суперформулы, орнаменты) доступны, а поверх
кладются мазки масляной кисти.

## Минимальный пример

```python
from polyart_painter import PainterCanvas

c = PainterCanvas(name="Закат", xlim=(-6, 6), ylim=(-6, 6),
                  background="#f0e0c0")

t = np.linspace(-6, 6, 200)
c.wet_on_wet(t, 3 - t*0.08, c1="#f0c020", c2="#d94a2a", width=2.4)
c.impasto(0.7*np.cos(np.linspace(0, 6.28, 100)),
          1.8 + 0.7*np.sin(np.linspace(0, 6.28, 100)),
          color="#ffe060", thickness=0.3)

c.save("zakat.polyart")
c.render("zakat.png", dpi=150)
```

## Методы живописи

| Метод | Техника |
|-------|---------|
| `stroke(x, y, ...)` | мазок текущей кистью |
| `dab(cx, cy, radius)` | отпечаток щетин |
| `fan(cx, cy, radius)` | веер щетин |
| `impasto(x, y, color)` | густой рельефный мазок |
| `glaze(x, y, color)` | лессировка |
| `wet_on_wet(x, y, c1, c2)` | смешивание на холсте |
| `dry_brush(x, y, color)` | сухая кисть |
| `brush(size, paint, load)` | выбрать кисть |

## Совмещение с полиарт-объектами

```python
c.circle(0, 0, 1, fill=True, fill_color="#c8a040", fill_alpha=0.5)
c.flower(2, 2, scale=0.8, fill=False, color="#d94a6e")
```

Полиномиальные объекты и мазки живут на одном холсте.

## Задание

Создайте сцену «Поле с цветами»: небо wet-on-wet, холм impasto,
цветы dab поверх. Сохраните в `.polyart` и `.png`.

## Проверка

- Файл `.polyart` открывается, объекты сохраняются.
- Мазки накладываются поверх объектов в правильном порядке.
- Сцена уникальна при разных seed.
