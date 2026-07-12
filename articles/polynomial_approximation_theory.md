# Polynomial Approximation of Complex Curves: Theory and Practice

Polynomial approximation provides a foundational mathematical framework for representing complex curves in generative art systems. By leveraging classical approximation theory—including Chebyshev polynomials, least-squares fitting, and error bounds—we can faithfully reconstruct arbitrary shapes with compact, analytically tractable representations. This article surveys the key theoretical results and practical considerations relevant to the PolyArt system, where every rendered curve is ultimately expressed as a polynomial mapping from parameter space to pixel coordinates.

## Polynomial Basis

The choice of polynomial basis critically influences both approximation quality and numerical behavior. The monomial basis $\{1, x, x^2, \dots, x^n\}$ is intuitive but suffers from ill-conditioning at high degrees. Chebyshev polynomials $T_n(x) = \cos(n \arccos x)$ form an orthogonal basis on $[-1, 1]$ and are the preferred choice for minimax approximation. Their extrema are evenly distributed, which minimizes the maximum interpolation error.

```python
import numpy as np

def chebyshev_polynomial(n, x):
    """Evaluate the nth Chebyshev polynomial of the first kind."""
    if n == 0:
        return np.ones_like(x)
    if n == 1:
        return x.copy()
    t_prev2 = np.ones_like(x)
    t_prev1 = x.copy()
    for _ in range(2, n + 1):
        t_curr = 2 * x * t_prev1 - t_prev2
        t_prev2 = t_prev1
        t_prev1 = t_curr
    return t_curr

def chebyshev_coefficients(f, n, num_samples=1024):
    """Compute Chebyshev expansion coefficients via discrete orthogonality."""
    k = np.arange(n + 1)
    theta = (2 * k + 1) * np.pi / (2 * (n + 1))
    x_k = np.cos(theta)
    f_k = f(x_k)
    coeffs = np.zeros(n + 1)
    for j in range(n + 1):
        coeffs[j] = (2.0 / (n + 1)) * np.sum(f_k * np.cos(j * theta))
    coeffs[0] /= 2.0
    return coeffs
```

## Approximation Methods

Two primary paradigms exist for constructing polynomial approximations: interpolation and least-squares fitting. Interpolation forces the polynomial through $n+1$ data points exactly, while least-squares minimizes $\sum_i |f(x_i) - p(x_i)|^2$ over a potentially larger dataset. For noisy or overdetermined curve data, least-squares is preferred. When the target function is smooth and known analytically, Chebyshev interpolation provides near-minimax accuracy.

```python
def least_squares_fit(x, y, degree):
    """Fit a polynomial of given degree using least squares."""
    vandermonde = np.vander(x, degree + 1, increasing=True)
    coeffs, residuals, rank, sv = np.linalg.lstsq(vandermonde, y, rcond=None)
    return coeffs

def evaluate_polynomial(coeffs, x):
    """Evaluate polynomial with given coefficients at points x."""
    return sum(c * x**i for i, c in enumerate(coeffs))
```

## Error Analysis

Runge's phenomenon demonstrates that high-degree polynomial interpolation on equally spaced nodes can diverge catastrophically near interval endpoints. For $f(x) = 1/(1 + 25x^2)$, the interpolation error grows exponentially with degree. Chebyshev nodes eliminate this issue by clustering points toward the boundaries, ensuring uniform convergence for continuous functions on $[-1, 1]$.

The Lebesgue constant $\Lambda_n$ quantifies interpolation stability: the error of the best polynomial approximation is bounded by $(1 + \Lambda_n)$ times the minimax error. For Chebyshev nodes, $\Lambda_n = O(\log n)$, compared to $O(2^n/\sqrt{n})$ for equispaced nodes.

## PolyArt Implementation

Within PolyArt, curve segments are approximated by independent polynomial patches. Each patch is fitted using Chebyshev nodes sampled along the parametric domain. The system automatically selects degree via an information criterion: fitting proceeds from degree 1 upward, halting when the residual reduction falls below a threshold relative to the added complexity.

```python
def auto_fit_curve(parametric_fn, t_range, max_degree=20, tol=1e-8):
    """Automatically fit a polynomial curve with adaptive degree selection."""
    for deg in range(1, max_degree + 1):
        coeffs_x = chebyshev_coefficients(
            lambda t: parametric_fn(t)[0], deg
        )
        coeffs_y = chebyshev_coefficients(
            lambda t: parametric_fn(t)[1], deg
        )
        residual = compute_residual(coeffs_x, coeffs_y, parametric_fn, t_range)
        if residual < tol:
            return deg, coeffs_x, coeffs_y
    return max_degree, coeffs_x, coeffs_y
```

## Numerical Stability

Evaluating high-degree polynomials in the monomial basis accumulates rounding errors. Three strategies mitigate this: (1) use Horner's method, reducing evaluation to $O(n)$ multiplications with controlled error growth; (2) evaluate in the Chebyshev basis via the three-term recurrence; (3) partition long curves into low-degree pieces, keeping each segment well-conditioned. PolyArt defaults to piecewise degree-8 patches, which remain numerically robust in IEEE 754 double precision.

```python
def horner_eval(coeffs, x):
    """Evaluate polynomial using Horner's method for numerical stability."""
    result = coeffs[-1]
    for c in reversed(coeffs[:-1]):
        result = result * x + c
    return result
```

## References

1. Trefethen, L. N. (2019). *Approximation Theory and Approximation Practice*. SIAM.
2. Runge, C. (1901). "Ueber die empirische Darstellung von Functionen." *Mathematische Annalen*, 54, 453–468.
3. Powell, M. J. D. (1981). *Approximation Theory and Methods*. Cambridge University Press.
4. Cheney, E. W. (2000). *Introduction to Approximation Theory*. AMS Chelsea Publishing.
5. Davis, P. J. (1975). *Interpolation and Approximation*. Dover Publications.
