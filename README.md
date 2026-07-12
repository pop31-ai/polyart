# PolyArt - Polynomial Art Format & API

A mathematical art library that creates images using polynomials, superformulas, and classical Greek/Roman artistic patterns.

## Features

- **PolyArt Format** (`.polyart`) - JSON-based format storing art as polynomial coefficients
- **Programmatic API** - Fluent/chainable API for creating art in Python
- **Visual Editor** - Tkinter-based editor with layer management, presets, undo/redo
- **Lightweight Viewer** - Fast viewer for `.polyart` files
- **Classical Patterns** - Greek meander, volute, lotus, palmette; Roman arch, column, dome
- **Golden Ratio** - Fibonacci spirals, golden rectangles, face/body proportion guides
- **Superformula** - Generalized superformula for organic shapes
- **Templates** - Pre-built artworks (Apollo, Greek vase, Parthenon, golden composition)

## Installation

```bash
pip install numpy matplotlib scipy
```

Or install all at once:

```bash
pip install -r requirements.txt
```

## Quick Start

### Programmatic API

```python
from polyart_api import Canvas, Templates

# Create from template
canvas = Templates.greek_vase()
canvas.render("greek_vase.png")

# Build your own
c = Canvas(name="My Art", width=10, height=10)
c.circle(0, 0, 2, fill=True, fill_color="#c8a040")
c.flower(1, 1, scale=0.5, n=6, fill=True, fill_color="#d4a030")
c.golden_spiral(-1, -1, a=0.1, turns=3, color="#8b6914")
c.save("my_art.polyart")
c.render("my_art.png")
```

### Visual Editor

```bash
python polyart_editor.py
```

Features: layer tree, property editing, Greek/Roman presets, undo/redo, color picker.

### Viewer

```bash
python polyart_viewer.py artwork.polyart
```

### File Format

```json
{
  "format": "polyart",
  "version": "1.0",
  "canvas": { "width": 10, "height": 10, "background": "#f5efe0" },
  "layers": [
    {
      "name": "Layer 1",
      "objects": [
        {
          "poly_x": [0.0, 1.0],
          "poly_y": [0.0, 0.5],
          "color": "#8b6914",
          "linewidth": 2.0,
          "fill": false
        }
      ]
    }
  ]
}
```

## API Reference

### Core Classes

| Class | Description |
|-------|-------------|
| `Canvas` | Main drawing surface. Chainable methods for adding shapes. |
| `PolyObj` | Single polynomial object (poly_x, poly_y coefficients). |
| `Layer` | Group of PolyObj with name. |
| `SuperFormula` | Generalized superformula shape generator. |

### Shape Helpers

| Class | Key Methods |
|-------|-------------|
| `GreekLines` | `meander()`, `volute()`, `lotus()`, `palmette()`, `acanthus_leaf()`, `greek_key_border()` |
| `RomanLines` | `arch()`, `column()`, `dome()`, `vault()`, `triumphal_arch()`, `column_flute()` |
| `GoldenRatio` | `golden_spiral()`, `golden_rectangle()`, `golden_triad()`, `fibonacci()`, `face_proportions()`, `body_proportions()` |
| `PolyCoeffs` | `line()`, `parabola()`, `cubic()`, `ellipse_poly()`, `circle_poly()`, `spiral_poly()`, `wave()`, `heart()`, `lissajous()`, `from_points()`, `closed_polygon()` |
| `SuperFormula` | `flower()`, `star()`, `circle()`, `square()`, `cross()`, `blob()`, `custom()` |

### Templates

```python
Templates.apollo_face()        # Classical Apollo face
Templates.rose(n=5, layers=3)  # Mathematical rose
Templates.greek_vase()         # Greek amphora
Templates.parthenon()          # Parthenon temple
Templates.roman_arch()         # Roman triumphal arch
Templates.golden_composition() # Golden ratio composition
Templates.geometric_tile()     # Geometric tile pattern
```

### Canvas Methods (chainable)

```python
c.circle(cx, cy, r, **kw)
c.ellipse(cx, cy, a, b, **kw)
c.line(x0, y0, x1, y1, **kw)
c.polyline(points, **kw)
c.polygon(vertices, **kw)
c.spiral(cx, cy, a, b, turns=3, **kw)
c.wave(x0, x1, amp, freq, y_off=0, **kw)
c.heart(cx, cy, scale, **kw)
c.lissajous(a, b, fx, fy, delta, **kw)
c.star(cx, cy, scale, n, **kw)
c.flower(cx, cy, scale, n, **kw)
c.blob(cx, cy, scale, m, **kw)
c.superformula(cx, cy, scale, **sf_kw)
c.meander(x0, y0, n, **kw)
c.arch(cx, cy, w, h, **kw)
c.golden_spiral(cx, cy, a, turns, **kw)
c.golden_rectangle(x0, y0, width, **kw)
c.volute(cx, cy, a, **kw)
```

Common kwargs: `color`, `linewidth`, `fill`, `fill_color`, `alpha`, `linestyle`.

## Dependencies

- Python 3.8+
- numpy
- matplotlib
- scipy (for spline-based portraits)

## License

MIT
