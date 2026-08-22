# H01 — Текстурное поле как объект формата: `texture_field`

**Статус:** idea + sketch · **Каталог:** внешние гипотезы PolyArt

## Abstract

Every visual form in PolyArt is a *mention with coordinates*. Flat fills
are the cheapest mentions, but they are also the poorest: a typical scene
scores `texture_complexity ≈ 0.0025` while `RarityScorer` weights texture
at 0.10. We propose one **additive** object type — `texture_field` — that
carries procedural texture as coefficients, not pixels.

---

## 1. Гипотеза

Если добавить в `.polyart` объект `texture_field`, задаваемый процедурой
(шум / реакция-диффузия / штриховка) и областью действия, то:

1. размер файла вырастет на ~200 байт на объект, а воспринимаемая
   плотность картины — качественно;
2. `texture_complexity` и `color_diversity` в `polyart_cv_test`
   вырастут достаточно, чтобы сдвинуть rarity на 5–15 пунктов;
3. старые файлы останутся валидными (аддитивность: неизвестные типы
   рендерер пропускает).

## 2. Упоминания

- `articles/procedural_texture_synthesis.md` → `polynomial_noise_field`,
  `fbm_noise`, `reaction_diffusion_step` — готовые поля, переносим как есть;
- `polyart_cv_test.py:265` → `RarityScorer.WEIGHTS["texture"] = 0.10`;
- `polyart_format.py:50..160` → семейство `make_*` конструкторов, куда
  аддитивно встаёт `make_texture_field`;
- `polyart_lang.py:844` → команда `turing_spots` (точки) — эскиз того,
  что полем стало бы полноценной фактурой.

## 3. Подходы

| Вариант | Суть | Плюсы | Минусы |
|---|---|---|---|
| A. Поле-заливка | fBm/Грей–Скот в прямоугольном домене, маскируется заливками | тривиальный рендер (`imshow` под контурами) | не следует за формой |
| B. Поле-обводка | поле в кольце вокруг параметрической кривой (dist-to-curve < w) | текстура «прилипает» к телу | дороже: нужен dist-запрос |
| C. Векторная фактура | hatch/stipple: семена детерминированным RNG, штрихи по градиенту поля | остаётся чистым вектором, печатается без муара | больше объектов |

Рекомендация: **A + C вместе**. A даёт дешёвый тон, C — структуру;
оба описываются одним JSON-типом с разными `kind`.

## 4. Код (референс)

```json
{
  "type": "texture_field",
  "kind": "fbm",                    // fbm | gray_scott | hatch | stipple
  "domain": [-5, 5, -5, 5],
  "seed": 42,
  "octaves": 5,
  "lacunarity": 2.0,
  "colormap": ["#141233", "#7a4a2a", "#c8a040"],
  "alpha": 0.55,
  "mask": "fills_below"             // fills_below | none | object_id
}
```

```python
def make_texture_field(kind, domain, seed=42, colormap=("#141233", "#c8a040"),
                       alpha=0.55, mask="fills_below", **kw):
    """Additive constructor, mirrors polyart_format.make_* style."""
    return {"type": "texture_field", "kind": kind, "domain": list(domain),
            "seed": seed, "colormap": list(colormap), "alpha": alpha,
            "mask": mask, **kw}

# рендер (вариант A): поле -> RGBA -> imshow под контурами
def render_texture_field(ax, obj, resolution=(400, 400)):
    x = np.linspace(*obj["domain"][0::2], resolution[0])
    y = np.linspace(*obj["domain"][1::2], resolution[1])
    xx, yy = np.meshgrid(x, y)
    field = fbm_noise(polynomial_noise_field(obj["seed"]), obj.get("octaves", 5))(xx, yy)
    cmap = LinearSegmentedColormap.from_list("pa", obj["colormap"])
    ax.imshow(field, extent=obj["domain"], cmap=cmap,
              alpha=obj["alpha"], zorder=0)
```

## 5. Как проверить

```
baseline: python polyart_lang.py scenes/amphora_night.plang
candidate: та же сцена + один texture_field
метрики:   PolyArtCVTest.analyze_image(...) обоих PNG
критерий:  Δrarity >= +5 при Δразмера(.polyart) <= 300 B
```

## 6. Риски

- Детерминированность между numpy-версиями (фиксировать RNG-протокол);
- `imshow` ломает «чистую векторность» SVG-экспорта → вариант C обязателен
  как print-путь;
- Маска `fills_below` требует порядка слоёв — документировать z-order.

## См. также

- [H02](H02_brush_height_normals.md) — фактура мазка тем же принципом
- `docs/lessons/06_dabs_and_fan.md` — щетина как векторная фактура
