# PolyArt: Polynomial Mathematical Art System

> Mathematics is the queen of the sciences, and art is its most beautiful expression.

A complete ecosystem for creating mathematical art using polynomials, golden ratio, biological laws, and classical art traditions. From Ancient Greek geometry to impossible Piranesi architecture, from Turing biological patterns to 3D wireframe rendering.

## Project Structure

```
polyart/
  polyart_api.py          # Core API: Canvas, PolyObj, GreekLines, RomanLines, GoldenRatio
  polyart_format.py       # .polyart file format: save/load/render
  polyart_editor.py       # Visual editor (tkinter): layers, presets, undo/redo
  polyart_viewer.py       # Lightweight .polyart viewer
  polyart_sculpture.py    # Sculpture: LatheBody, MuscleRelief, PiranesiArch, RomanSymbols, GameAssets
  polyart_biology.py      # Biology: GrowthCurves, Phyllotaxis, Biomechanics, TuringPatterns, Variants
  polyart_3d.py           # 3D: Wireframe3D, Surface3D, Scene3D, Rotations
  polyart_cv_test.py      # Computer Vision: art vs nature classification, rarity scoring
  polyart_emotions.py     # Emotion Templates: 10 emotions + 4 physical states
  polyart_animals.py      # Animal Templates: 9 animals in polynomial style
  polyart_lang.py         # Meta-Language DSL: tokenizer, parser, interpreter (50+ commands)
  polyart_curves.py       # Curves Library: body systems - skeletal, muscle, skin, veins, nerves, limbs, head, figure
  polyart_flowers.py      # Botanical Art: flowers (rose, lily, daisy, tulip, sunflower, orchid, lotus), plants, compositions
  polyart_spqr.py         # SPQR Roman Architecture: columns, arches, Piranesi impossible geometry, Roman forum, Colosseum
  examples/               # 13 showcase demos + 3 .polyart scripts
  articles/               # 32 technical articles
  CONTRIBUTORS.md         # 30+ team members
  CHANGELOG.md            # Version history
```

## Modules

| Module | Purpose | Key Classes |
|--------|---------|-------------|
| `polyart_api` | Core polynomial art engine | Canvas, PolyObj, GreekLines, RomanLines, GoldenRatio, SuperFormula, Templates |
| `polyart_format` | .polyart file format | save, load, render |
| `polyart_sculpture` | Classical sculpture & architecture | LatheBody, MuscleRelief, PiranesiArch, RomanSymbols, GameAssets |
| `polyart_biology` | Mathematical biology | GrowthCurves, Phyllotaxis, Biomechanics, TuringPatterns, VariantGenerator |
| `polyart_3d` | 3D wireframe & surfaces | Wireframe3D, Surface3D, Scene3D, Rotations |
| `polyart_cv_test` | Computer vision classification | ImageFeatureExtractor, RarityScorer, PolyArtCVTest |
| `polyart_emotions` | Emotion & state rendering | EmotionTemplates (10 emotions), StateTemplates (4 states) |
| `polyart_animals` | Animal polynomial art | AnimalTemplates (lion, eagle, wolf, horse, snake, bear, dolphin, owl, dragon) |
| `polyart_lang` | Meta-language DSL | Tokenizer, Parser, Interpreter - 50+ built-in commands |
| `polyart_curves` | Body system curves | SkeletalCurves, MuscleCurves, SkinCurves, VeinCurves, NerveCurves, LimbCurves, HeadCurves, FigureCurves |
| `polyart_flowers` | Botanical art | FlowerCurves, PlantCurves, CompositionCurves |
| `polyart_spqr` | SPQR Roman architecture & Piranesi | RomanOrders, RomanArch, PiranesiArchitecture, SPQRForum, SPQRComposition |

## Quick Start

```python
from polyart_api import Canvas, Templates

# Render a template
c = Templates.greek_vase()
c.render("greek_vase.png")

# Build your own
c = Canvas(name="My Art", width=10, height=10, background="#0d0a1a")
c.golden_spiral(0, 0, a=0.1, turns=4, color="#c8a040", linewidth=2)
c.flower(1, 1, scale=0.5, n=6, fill=True, fill_color="#d94a6e")
c.circle(-1, -1, 0.8, fill=True, fill_color="#4a90d9", fill_alpha=0.3)
c.save("my_art.polyart")
c.render("my_art.png")
```

### 3D Rendering

```python
from polyart_3d import Wireframe3D, Scene3D
from polyart_api import Canvas

scene = Scene3D(background="#0a0a15")
scene.add_wireframe(Wireframe3D.sphere(0, 0, 2), color="#c8a040")
scene.add_wireframe(Wireframe3D.torus(3, 0, 1.5, 0.5), color="#4a90d9")
canvas = Canvas(xlim=(-5, 5), ylim=(-5, 5))
scene.render_to_canvas(canvas)
scene.render("scene_3d.png")
```

### Biology & Growth

```python
from polyart_biology import Phyllotaxis, GrowthCurves, TuringPatterns
from polyart_api import Canvas

c = Canvas(name="Bio")
xs, ys = Phyllotaxis.golden_points(n=200, scale=2.0)
for x, y in zip(xs, ys):
    c.circle(x, y, 0.05, fill=True, fill_color="#c8a040")
c.render("phyllotaxis.png")
```

### CV Classification

```python
from polyart_cv_test import PolyArtCVTest

# Analyze an image: is it rare art or nature?
result = PolyArtCVTest.analyze_image("my_artwork.png")
print(f"Rarity: {result['rarity']}/100")
print(f"Classification: {result['classification']}")
```

### Emotions & States

```python
from polyart_emotions import EmotionTemplates, StateTemplates

# Render emotions
EmotionTemplates.joy("joy.png")
EmotionTemplates.anger("anger.png")

# Render physical states
StateTemplates.sleeping("sleeping.png")
StateTemplates.dancing("dancing.png")
```

### Animal Art

```python
from polyart_animals import AnimalTemplates

AnimalTemplates.lion("lion.png", s=3.0)
AnimalTemplates.dragon("dragon.png", s=4.0)
```

### Botanical / Floral Art

```python
from polyart_flowers import FlowerCurves, PlantCurves, CompositionCurves

# Single flower
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
FlowerCurves.sunflower(ax, 0, 0, s=2.0)
FlowerCurves.rose(ax, -3, 0, s=1.5, petals=8)
FlowerCurves.lotus(ax, 3, 0, s=1.5)
plt.savefig("flowers.png")

# Full composition
CompositionCurves.garden_scene(ax, 0, 0, s=5.0)
CompositionCurves.wreath(ax, 0, 0, s=3.0, n_flowers=12)
```

### Meta-Language DSL

```
# demo.polyart
canvas 10 10 "#0d0a1a"
color "#c8a040"
repeat 6 {
    rotate $i * 60 {
        spiral 0 0 0.05 4 2.0
    }
}
flower 2 2 0.5 6 "#d94a6e"
save "output.png"
```

## Showcase Examples

| # | Name | Objects | Description |
|---|------|---------|-------------|
| 01 | Golden Mandala | 799 | Fibonacci spirals + golden ratio concentric circles |
| 02 | Piranesi Carcere | 303 | Impossible prison architecture |
| 03 | Roman Legion | 165 | SPQR formation: eagle, shields, gladii |
| 04 | Anatomy da Vinci | 93 | Vitruvian biomechanical study |
| 05 | Procedural Forest | 790 | Fractal branching trees + terrain |
| 06 | Turing Savanna | 219 | Leopard spots + zebra stripes |
| 07 | RPG Game Mockup | 628 | Tilemap + characters + UI |
| 08 | Greek Amphora Gallery | 121 | 5 lathe-rendered vessels |
| 09 | Flower Variants | 78 | 8 parametric flower forms |
| 10 | Biomechanical Atlas | 57 | Bones, joints, tendons, Wolff's law |

### Generated Showcases

| Image | CV Classification | Rarity |
|-------|------------------|--------|
| `emotions_showcase.png` | ART | 56/100 |
| `states_showcase.png` | ART | 55/100 |
| `animals_showcase.png` | ART | 63/100 |
| `curves_library_showcase.png` | ART | 59/100 |
| `flowers_showcase.png` | ART | 63/100 |

## Articles

1. PolyArt Format Specification
2. Golden Ratio as Generative Principle
3. From Turing to Polynomials: Biological Patterns
4. Impossible Architecture Through Polynomial Curves
5. Procedural Game Asset Generation
6. Polynomial Approximation Theory
7. Mathematical Color Theory
8. Parametric vs Polynomial Curves
9. Neural-Symbolic Hybrid Classification
10. Ancient Greek Geometry in Modern Art
11. Procedural Texture Synthesis
12. Computer Vision for Art Classification

## Dependencies

- Python 3.8+
- numpy
- matplotlib
- scipy (for spline portraits)

## License

MIT
