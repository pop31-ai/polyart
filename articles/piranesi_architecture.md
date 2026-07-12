# Impossible Architecture Through Polynomial Curves

## Abstract

Giovanni Battista Piranesi's *Carceri d'Invenzione* (1745–1761) depicted vast, impossible prisons—interiors of paradoxical depth where staircases lead nowhere, arches support impossible masses, and perspective itself becomes unreliable. These images exploit the viewer's geometric intuition while systematically violating it. This article presents a mathematical framework for generating Piranesi-style impossible architecture using polynomial curves and implicit surfaces, demonstrating that the interplay between locally valid geometry and globally contradictory structure is naturally expressed through carefully constructed polynomial systems.

## 1. Piranesi's Legacy

Piranesi trained as an architect under Carlo Zucchi and studied Roman antiquities with obsessive precision. His technical mastery of one-point and two-point perspective is precisely what makes his impossible constructions so effective: each individual element obeys correct perspective rules, but the global assembly violates topological and metric consistency. The viewer's visual system accepts each局部 region as plausible, producing a cumulative sense of vertigo and spatial paradox.

Modern computational artists seek to generate similar effects procedurally. The challenge is to produce structures where local geometric validity coexists with global inconsistency, and where the transitions between valid and impossible regions appear seamless.

## 2. Mathematical Foundations

A polynomial surface $P(x, y, z) = 0$ defines a valid manifold in three-dimensional space. An impossible structure is created by embedding multiple locally valid polynomial surfaces that share boundary curves but have incompatible global topology. The key technique is to define a perspective transformation $\tau: \mathbb{R}^3 \to \mathbb{R}^2$ that varies spatially—effectively a non-homogeneous projection—so that depth at one location is inconsistent with depth at another, despite each region being locally consistent.

## 3. Nested Arches

The fundamental motif of Piranesi's architecture is the nested arch: a series of concentric archways receding into apparent depth, each rendered with correct local curvature. In polynomial form, an arch is a degree-4 implicit curve:

$$P(x, y) = \left(x^2 + y^2\right)^2 - a^2\left(x^2 + y^2\right) + b^2 y^2$$

By nesting multiple instances with increasing scale and decreasing spacing, the illusion of infinite recession is created. The critical step is to apply a depth-dependent affine transform to each successive arch such that the local perspective remains valid while the global depth accumulates beyond what any single consistent perspective could produce.

```python
import numpy as np

def arch_curve(x, y, a=0.5, b=0.3):
    r2 = x**2 + y**2
    return r2**2 - a**2 * r2 + b**2 * y**2

def nested_arches(n_arches=8, resolution=512):
    xs = np.linspace(-1, 1, resolution)
    ys = np.linspace(-1, 1, resolution)
    X, Y = np.meshgrid(xs, ys)
    canvas = np.zeros((resolution, resolution))
    
    for i in range(n_arches):
        scale = 1.0 / (i + 1)
        offset_y = -0.05 * i
        Xs = X * scale
        Ys = (Y - offset_y) * scale
        arch = arch_curve(Xs, Ys, a=0.4, b=0.25)
        mask = np.abs(arch) < 0.02
        intensity = 1.0 - 0.1 * i
        canvas[mask] = intensity
    
    return canvas
```

## 4. Perspective Distortion

Piranesi's spatial paradoxes exploit the fact that human depth perception integrates multiple monocular cues—linear perspective, texture gradient, occlusion, and relative size. By maintaining local consistency of linear perspective while violating its global consistency, impossible structures are produced. Formally, this is achieved by defining a projection field $\Pi(x,y)$ that maps each local region through a different projective transformation, with the transformations stitched along polynomial boundary curves to ensure C¹ continuity of the rendered image.

## 5. Implementation

A complete Piranesi scene in PolyArt consists of three polynomial layers: a structural layer defining the architectural geometry, a shading layer computing illumination (typically a polynomial approximation of Lambertian reflectance), and a depth layer encoding a non-consistent depth map. The depth layer is the locus of impossibility—it must be a smooth polynomial field that nonetheless cannot be the projection of any single 3D surface.

```python
def impossible_depth_field(resolution=512):
    xs = np.linspace(-1, 1, resolution)
    ys = np.linspace(-1, 1, resolution)
    X, Y = np.meshgrid(xs, ys)
    
    depth = np.zeros_like(X)
    depth += 0.5 * np.sin(3 * np.pi * X) * np.cos(2 * np.pi * Y)
    depth += 0.3 * (X**2 - Y**2)
    depth += 0.2 * np.sin(5 * np.pi * X + 3 * np.pi * Y)
    
    mask_left = X < 0
    depth[mask_left] *= -1
    
    return depth
```

## 6. Gallery

The approach generates a family of impossible architectural forms: Escher-like staircases where ascending and descending are identical, baroque colonnades that curve back into themselves, and vaulted chambers whose floors become ceilings. Each variant is produced by varying the polynomial coefficients while preserving the local-validity constraint.

## References

1. Piranesi, G. B. *Carceri d'Invenizione*. Rome, 1745–1761.
2. Ernst, B. *The Magic Mirror of M.C. Escher*. Random House, 1976.
3. Penrose, L. S. and Penrose, R. "Impossible Objects: A Special Type of Visual Illusion." *British Journal of Psychology*, 1958.
4. Koenderink, J. J. *Solid Shape*. MIT Press, 1992.
5. PolyArt Project. "Impossible Architecture Module." GitHub Repository, 2026.
