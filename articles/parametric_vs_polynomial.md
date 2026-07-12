# Parametric vs Polynomial: A Comparative Study in Art Generation

Curve representation is a central design decision in generative art systems. Parametric forms—Bezier curves, NURBS, and B-splines—dominate computer-aided design, while global polynomial representations offer analytical elegance and compact storage. This article compares both paradigms along axes of expressiveness, computational cost, and suitability for the PolyArt system, where curves must be rendered, analyzed, and classified.

## Parametric Curves

A Bezier curve of degree $n$ is defined as $\mathbf{C}(t) = \sum_{i=0}^{n} \binom{n}{i} (1-t)^{n-i} t^i \mathbf{P}_i$, where $\mathbf{P}_i$ are control points. B-splines generalize this by introducing a knot vector that provides local control: moving one control point affects only a finite neighborhood of the curve. NURBS add rational weighting, enabling exact conic section representation.

```python
import numpy as np
from math import comb

def bezier_curve(control_points, num_samples=100):
    """Evaluate a Bezier curve at uniformly spaced parameter values."""
    n = len(control_points) - 1
    t = np.linspace(0, 1, num_samples)
    points = np.zeros((num_samples, 2))
    for k in range(n + 1):
        basis = comb(n, k) * ((1 - t) ** (n - k)) * (t ** k)
        points[:, 0] += basis * control_points[k][0]
        points[:, 1] += basis * control_points[k][1]
    return points

def b_spline_basis(knots, i, degree, t):
    """Evaluate the ith B-spline basis function of given degree."""
    if degree == 0:
        return 1.0 if knots[i] <= t < knots[i + 1] else 0.0
    left = 0.0
    denom_l = knots[i + degree] - knots[i]
    if denom_l != 0:
        left = ((t - knots[i]) / denom_l) * b_spline_basis(knots, i, degree - 1, t)
    right = 0.0
    denom_r = knots[i + degree + 1] - knots[i + 1]
    if denom_r != 0:
        right = ((knots[i + degree + 1] - t) / denom_r) * b_spline_basis(knots, i + 1, degree - 1, t)
    return left + right
```

## Polynomial Curves

A polynomial curve in parametric form is $\mathbf{C}(t) = (x(t), y(t))$ where $x$ and $y$ are polynomials in $t$. Unlike B-splines, the polynomial representation is global: every coefficient influences the entire curve. This globality is advantageous for analytical operations—integration, differentiation, and root-finding follow directly from polynomial algebra—but limits local editing flexibility.

```python
def polynomial_curve(coeffs_x, coeffs_y, num_samples=100):
    """Evaluate a polynomial parametric curve."""
    t = np.linspace(0, 1, num_samples)
    x = sum(c * t**i for i, c in enumerate(coeffs_x))
    y = sum(c * t**i for i, c in enumerate(coeffs_y))
    return np.column_stack([x, y])

def polynomial_derivative(coeffs):
    """Compute derivative coefficients of a polynomial."""
    return [i * c for i, c in enumerate(coeffs) if i > 0]
```

## Representation Power

B-splines of degree $n$ can exactly reproduce any polynomial curve of degree $\leq n$ by appropriate knot placement (clamped knots with full multiplicity at endpoints). Conversely, a single polynomial of degree $n$ can approximate any smooth B-spline segment to arbitrary accuracy by increasing $n$. The critical difference is storage: a degree-$n$ B-spline segment requires $n+1$ control points and $n+1$ knots, while a polynomial requires only $n+1$ coefficients.

For art generation, B-splines excel when the designer needs intuitive local control. Polynomials excel when curves are generated algorithmically and must support downstream mathematical analysis—such as PolyArt's curvature-based rarity scoring.

## Conversion Methods

Converting B-splines to polynomials is straightforward: each B-spline segment, between consecutive knots, is a polynomial that can be extracted by de Boor's algorithm and then converted to the monomial basis. The reverse direction—fitting a polynomial to a B-spline—is a standard least-squares problem.

```python
def de_boor_point(control_points, knots, degree, t):
    """Evaluate a point on a B-spline curve using de Boor's algorithm."""
    n = len(control_points) - 1
    k = degree
    for i in range(len(knots) - 1):
        if knots[i] <= t < knots[i + 1]:
            k = i
            break
    d = [np.array(control_points[j]) for j in range(k - degree, k + 1)]
    for r in range(1, degree + 1):
        for j in range(degree, r - 1, -1):
            left = degree - r + 1
            denom = knots[j + degree - r + 1] - knots[j]
            if denom == 0:
                alpha = 0.0
            else:
                alpha = (t - knots[j]) / denom
            d[j - (k - degree)] = (1 - alpha) * d[j - 1 - (k - degree)] + alpha * d[j - (k - degree)]
    return d[degree]

def bspline_to_polynomial(control_points, knots, degree, segment_index):
    """Extract a polynomial representation of one B-spline segment."""
    samples = []
    t_start = knots[degree]
    t_end = knots[-(degree + 1)]
    for t in np.linspace(t_start, t_end, degree + 1):
        pt = de_boor_point(control_points, knots, degree, t)
        samples.append(pt)
    t_eval = np.linspace(t_start, t_end, degree + 1)
    vander_x = np.vander(t_eval, degree + 1, increasing=True)
    coeffs_x = np.linalg.solve(vander_x, [p[0] for p in samples])
    coeffs_y = np.linalg.solve(vander_x, [p[1] for p in samples])
    return coeffs_x, coeffs_y
```

## Performance

Evaluation complexity differs: de Boor evaluation is $O(n^2)$ for a B-spline of degree $n$, while Horner evaluation of a polynomial is $O(n)$. For rendering at thousands of sample points per frame, the $O(n)$ advantage accumulates. However, B-splines enable level-of-detail by subdividing only visible segments, which PolyArt does not currently exploit.

## When to Use Each

Use B-splines or Bezier curves when interactive design demands intuitive handle manipulation. Use polynomial representations when curves are procedurally generated, require mathematical analysis (curvature, arc length, intersection testing), or must be serialized compactly. PolyArt chooses polynomials as its internal representation, converting from B-spline inputs at import time.

## References

1. Farin, G. (2002). *Curves and Surfaces for CAGD*. Morgan Kaufmann.
2. Piegl, L. & Tiller, W. (1997). *The NURBS Book*. Springer.
3. de Boor, C. (1978). *A Practical Guide to Splines*. Springer.
4. Goldman, R. (2003). "An Overview of Classical CAGD." *Handbook of Computer Aided Geometric Design*.
5. Sederberg, T. W. (2012). *Computer Aided Geometric Design*. Lecture notes, BYU.
