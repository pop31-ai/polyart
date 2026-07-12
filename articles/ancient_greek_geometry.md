# Ancient Greek Geometry in Modern Generative Art

The geometric principles formalized by Euclid, Apollonius, and the Pythagorean school constitute the oldest surviving framework for algorithmic shape construction. This article demonstrates how classical Greek geometry—Euclidean compass-and-straightedge constructions, conic sections, the golden ratio, and architectural orders—translates directly into modern generative art algorithms within the PolyArt system.

## Historical Context

Greek mathematics, from roughly 600 BCE to 300 CE, prioritized constructive methods over algebraic computation. A proposition was considered proved only when a finite sequence of construction steps produced the desired figure. This constraint—finite, deterministic, geometrically grounded—is precisely the constraint under which PolyArt generates artwork: every curve must be constructible from polynomial operations.

## Euclid's Elements

The first four books of the Elements define constructions using only an unmarked straightedge and compass. Bisecting an angle, constructing a perpendicular, and inscribing regular polygons are all polynomial operations in disguise. The regular pentagon, for instance, requires constructing the golden ratio $\varphi = (1+\sqrt{5})/2$.

```python
import numpy as np

def euclidean_circle(center, radius, num_points=200):
    """Generate a circle using the classical center-radius construction."""
    t = np.linspace(0, 2 * np.pi, num_points)
    return np.column_stack([center[0] + radius * np.cos(t),
                            center[1] + radius * np.sin(t)])

def euclidean_bisect(angle_start, angle_end, center):
    """Bisect an angle using Euclidean construction (arithmetic mean)."""
    return (angle_start + angle_end) / 2.0

def regular_polygon(n, center, radius, rotation=0):
    """Construct a regular n-gon inscribed in a circle."""
    angles = np.linspace(rotation, rotation + 2 * np.pi, n, endpoint=False)
    return np.column_stack([center[0] + radius * np.cos(angles),
                            center[1] + radius * np.sin(angles)])

def golden_ratio_construction(unit_length=1.0):
    """Construct the golden ratio using Euclid's method (Elements VI.30)."""
    phi = (1 + np.sqrt(5)) / 2
    return phi * unit_length
```

## Conic Sections

Apollonius of Perga (c. 200 BCE) systematized the study of conic sections: ellipse, parabola, and hyperbola, all obtainable by slicing a cone with a plane. These curves are polynomial or rational-polynomial in nature and form natural building blocks for PolyArt compositions. An ellipse with semi-axes $a$ and $b$ is parameterized as $\mathbf{r}(t) = (a\cos t,\; b\sin t)$.

```python
def conic_ellipse(a, b, num_points=200):
    """Generate an ellipse as a conic section."""
    t = np.linspace(0, 2 * np.pi, num_points)
    return np.column_stack([a * np.cos(t), b * np.sin(t)])

def conic_parabola(a, domain=(-3, 3), num_points=200):
    """Generate a parabola y = a*x^2."""
    x = np.linspace(domain[0], domain[1], num_points)
    return np.column_stack([x, a * x**2])

def conic_hyperbola(a, b, domain=(-3, 3), num_points=200):
    """Generate a hyperbola x^2/a^2 - y^2/b^2 = 1."""
    t = np.linspace(0.1, 2.0, num_points // 2)
    x_upper = a * np.cosh(t)
    y_upper = b * np.sinh(t)
    t2 = np.linspace(0.1, 2.0, num_points - num_points // 2)
    x_lower = a * np.cosh(t2)
    y_lower = -b * np.sinh(t2)
    return np.vstack([np.column_stack([x_upper, y_upper]),
                      np.column_stack([x_lower, y_lower])])
```

## Architectural Orders

Greek temple architecture codified three proportional systems—the Doric, Ionic, and Corinthian orders—each defined by precise geometric ratios. The Doric column has a height-to-diameter ratio of approximately 6:1, the Ionic 8:1, and the Corinthian 10:1. Entablature proportions follow similar integer ratios, creating harmonic visual rhythms.

```python
def greek_column(order="ionic", base_height=1.0, num_points=100):
    """Generate a Greek column profile based on architectural order."""
    ratios = {"doric": 6, "ionic": 8, "corinthian": 10}
    height = ratios.get(order, 8) * base_height
    
    t = np.linspace(0, height, num_points)
    # Slight entasis (convex taper) per Vitruvian specification
    entasis = 0.02 * base_height * np.cos(np.pi * t / (2 * height))
    radius = base_height * (0.5 - 0.05 * t / height + entasis)
    
    profile_x = radius * np.cos(np.linspace(0, 2 * np.pi, num_points))
    profile_y = t
    return np.column_stack([profile_x, profile_y])

def greek_key_pattern(width=10, height=2, segments=8):
    """Generate a Greek key (meander) pattern."""
    points = []
    seg_w = width / segments
    current_x = 0
    direction = 1
    for i in range(segments):
        level = height * 0.5 * (i % 2)
        points.append([current_x, level])
        points.append([current_x, height])
        points.append([current_x + direction * seg_w * 0.5, height])
        points.append([current_x + direction * seg_w * 0.5, level + height * 0.3])
        points.append([current_x + direction * seg_w, level + height * 0.3])
        current_x += direction * seg_w
    return np.array(points)
```

## Implementation

PolyArt integrates Greek geometry through a `GreekBuilder` class that maps classical constructions to polynomial curve segments. The golden spiral—constructed from quarter-circle arcs scaled by $\varphi$—is approximated as a piecewise polynomial, while architectural motifs generate tileable border patterns.

```python
def golden_spiral(num_turns=3, points_per_arc=50):
    """Construct a golden spiral from quarter-circle arcs scaled by phi."""
    phi = (1 + np.sqrt(5)) / 2
    all_points = []
    for turn in range(num_turns):
        radius = phi ** (turn * 0.25)
        t = np.linspace(0, np.pi / 2, points_per_arc)
        offset_angle = turn * np.pi / 2
        x = radius * np.cos(t + offset_angle)
        y = radius * np.sin(t + offset_angle)
        all_points.append(np.column_stack([x, y]))
    return np.vstack(all_points)
```

## Examples

A complete PolyArt composition might combine a Doric column frame, a golden spiral centerpiece, and a Greek key border—each element generated as polynomial curves and rendered with golden-ratio color palettes. The mathematical coherence between Greek construction principles and polynomial representation ensures that every element shares a common analytical language.

## References

1. Euclid. (c. 300 BCE). *Elements*. Translated by T. L. Heath (1956), Dover.
2. Apollonius of Perga. (c. 200 BCE). *Conics*. Translated by R. Catesby Taliaferro (1952).
3. Vitruvius. (c. 30 BCE). *De Architectura*. Translated by M. H. Morgan (1914), Harvard UP.
4. Kappraff, J. (2002). *Connections: The Geometric Bridge Between Art and Science*. World Scientific.
5. March, R. J. (1998). *Geometry of Architecture*. McGraw-Hill.
