# PolyArt Format: A Polynomial-Based Vector Art Specification

## Abstract

PolyArt is a novel vector art format that represents visual compositions entirely through polynomial functions. Unlike raster formats (PNG, JPEG) that store discrete pixel values, and unlike SVG which relies on path-based primitives, PolyArt encodes every visual element—shapes, colors, gradients, and transformations—as coefficients of polynomial expressions. This yields infinitely scalable artwork that can be rendered at any resolution with mathematical precision, while remaining compact, composable, and amenable to procedural manipulation. This document formally specifies the PolyArt format, its JSON schema, its mathematical foundations, and its rendering pipeline.

## 1. Introduction

Digital vector art has long been dominated by the Scalable Vector Graphics (SVG) format, which describes imagery through XML-based path data, geometric primitives, and filter effects. While SVG achieves resolution independence, its reliance on cubic Bézier curves and discrete path commands introduces complexity that limits programmatic generation and mathematical analysis. PolyArt reimagines vector art from first principles: every visual construct is a polynomial, enabling algebraic composition, seamless interpolation, and rigorous mathematical reasoning about artistic properties.

## 2. Format Design

A PolyArt document is a JSON file containing four top-level sections: `metadata`, `canvas`, `layers`, and `animations`. The `metadata` block declares version, author, and license. The `canvas` defines the coordinate space (typically centered at the origin, spanning \[-1, 1\] on both axes). The `layers` array contains ordered visual elements, each described by polynomial expressions. The optional `animations` section maps time variables to parameter updates, enabling motion without frame-by-frame data.

```json
{
  "version": "1.0.0",
  "canvas": {
    "width": 1920,
    "height": 1080,
    "coordinate_system": "cartesian",
    "bounds": [-1, -1, 1, 1]
  },
  "layers": [
    {
      "type": "shape",
      "polynomial": {
        "fill": [0.8, 0.2, 0.1],
        "path": "P(x,y) = x^2 + y^2 - 0.25"
      }
    }
  ]
}
```

## 3. Polynomial Representation

The core innovation of PolyArt is the polynomial shape descriptor. A 2D implicit curve is defined by a bivariate polynomial $P(x, y)$, and a point $(x, y)$ lies on the shape boundary when $P(x, y) = 0$. Fills are determined by sign: points where $P(x, y) < 0$ are interior, and points where $P(x, y) > 0$ are exterior.

Color is itself polynomial. The RGB channels are expressed as three polynomials of the spatial coordinates:

$$C_r(x,y) = \sum_{i=0}^{d} \sum_{j=0}^{d-i} a_{ij}^{(r)} x^i y^j$$

This allows smooth, analytically defined gradients that generalize linear and radial gradients. A simple linear gradient across the x-axis is the degree-1 polynomial $C(x,y) = a_0 + a_1 x$.

```python
import numpy as np

class PolyArtShape:
    def __init__(self, coefficients, degree):
        self.coeffs = np.array(coefficients)
        self.degree = degree

    def evaluate(self, x, y):
        value = 0.0
        idx = 0
        for i in range(self.degree + 1):
            for j in range(self.degree + 1 - i):
                value += self.coeffs[idx] * (x ** i) * (y ** j)
                idx += 1
        return value

    def rasterize(self, resolution=512):
        xs = np.linspace(-1, 1, resolution)
        ys = np.linspace(-1, 1, resolution)
        X, Y = np.meshgrid(xs, ys)
        return self.evaluate(X, Y)
```

## 4. Layer System

Layers in PolyArt are stacked and composited using standard alpha blending, but each layer's visual content is fully polynomial. Layer types include `shape` (implicit polynomial curves), `field` (color fields without explicit boundaries), and `compound` (boolean combinations of shapes using polynomial arithmetic). Union is achieved by multiplication: $P_{union}(x,y) = P_1(x,y) \cdot P_2(x,y)$, and intersection by addition of signed distance fields.

## 5. Rendering Pipeline

Rendering a PolyArt file proceeds in four stages. First, the document is parsed and all polynomial expressions are compiled into evaluation kernels. Second, a signed distance field is computed on a grid covering the canvas. Third, the field is evaluated per-pixel (or per-sample for anti-aliasing) to determine fill membership and color. Finally, alpha compositing merges layers into the output image. GPU fragment shaders can evaluate low-degree polynomials in real time, enabling interactive rendering at 60 fps.

## 6. Advantages over SVG

PolyArt offers several advantages. Infinite scalability is inherent—polynomials are defined everywhere, not segmented into finite path commands. Algebraic composition is natural: merging shapes is multiplication or addition of polynomials, not union of path data. Interpolation between artworks is a convex combination of coefficient vectors, enabling smooth morphing. File sizes are often smaller for mathematically regular content, since a degree-5 polynomial in two variables requires only 21 coefficients per channel.

## 7. Future Work

Planned extensions include support for rational polynomial curves (enabling exact conic sections), hierarchical polynomial LOD for progressive refinement, and a real-time collaboration protocol where incremental coefficient updates stream between clients.

## References

1.-svg/spec. W3C Scalable Vector Graphics (SVG) Specification, Version 2. W3C, 2023.
2. Praun, E., et al. "Real-Time Hatching." Proceedings of SIGGRAPH, 2001.
3. Sederberg, T. W. *Computer-Aided Geometric Design*. Utah State University, 2023.
4. PolyArt Project. "Polynomial Vector Art Format Specification." GitHub Repository, 2026.
5. Bloomenthal, J. "An Implicit Surface Polygonizer." *Graphics Gems IV*, Academic Press, 1994.
