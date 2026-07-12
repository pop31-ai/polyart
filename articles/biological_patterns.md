# From Turing to Polynomials: Modeling Biological Patterns

## Abstract

Alan Turing's 1952 theory of morphogenesis proposed that interacting chemical species, diffusing at different rates, could spontaneously generate spatial patterns—spots, stripes, and labyrinthine forms. Modern computational biology has validated this mechanism across species, from zebrafish pigmentation to seashell markings. Translating these reaction-diffusion systems into the polynomial framework of PolyArt opens a path to procedurally generating organic textures with biologically plausible structure. This article reviews the mathematical foundations of biological pattern formation and demonstrates how polynomial approximations capture the essential dynamics with dramatically reduced computational cost.

## 1. Introduction

Natural organisms display a remarkable diversity of surface patterns: the hexagonal rosettes on a giraffe, the alternating bands on a zebra, the fractal branching of a fern. These patterns arise from reaction-diffusion systems, lateral inhibition, and mechanical buckling during development. While full simulation of these processes requires solving coupled partial differential equations, the steady-state outputs can often be approximated by low-degree polynomial surfaces, making them directly expressible in PolyArt.

## 2. Turing Patterns

The classical Turing model consists of two species—an activator $u$ and an inhibitor $v$—governed by:

$$\frac{\partial u}{\partial t} = D_u \nabla^2 u + f(u, v)$$
$$\frac{\partial v}{\partial t} = D_v \nabla^2 v + g(u, v)$$

where $D_v \gg D_u$ (the inhibitor diffuses faster). In two dimensions, linear stability analysis around a homogeneous steady state yields dispersion relations predicting the characteristic wavelength $\lambda$ of the emerging pattern. When the system is solved on a bounded domain, the resulting steady state $u^*(x, y)$ is a spatially varying scalar field that encodes the pattern.

Key pattern classes include:

- **Spots**: localized peaks of activator concentration
- **Stripes**: periodic bands along one principal direction
- **Labyrinthine**: irregular winding bands with no preferred orientation
- **Mixed**: transitions between spots and stripes governed by parameter values

```python
import numpy as np

def turing_step(u, v, Du=0.00016, Dv=0.00008, dt=1.0, F=0.037, k=0.06):
    u_next = u.copy()
    v_next = v.copy()
    laplacian_u = (
        np.roll(u, 1, axis=0) + np.roll(u, -1, axis=0) +
        np.roll(u, 1, axis=1) + np.roll(u, -1, axis=1) - 4 * u
    )
    laplacian_v = (
        np.roll(v, 1, axis=0) + np.roll(v, -1, axis=0) +
        np.roll(v, 1, axis=1) + np.roll(v, -1, axis=1) - 4 * v
    )
    uvv = u * v * v
    u_next += dt * (Du * laplacian_u - uvv + F * (1 - u))
    v_next += dt * (Dv * laplacian_v + uvv - (F + k) * v)
    return u_next, v_next

def simulate_turing(grid_size=256, steps=10000):
    u = np.random.rand(grid_size, grid_size)
    v = np.random.rand(grid_size, grid_size)
    for _ in range(steps):
        u, v = turing_step(u, v)
    return u
```

## 3. Growth Models

Beyond steady-state patterns, biological organisms grow according to allometric laws. A growth curve $G(t)$ relating body mass to time is often sigmoidal and well-approximated by a logistic polynomial:

$$G(t) = \frac{L}{1 + e^{-k(t - t_0)}}$$

In PolyArt, animating a shape's evolution from a seed to a mature form involves interpolating polynomial coefficients along a growth trajectory, where the degree of the polynomial increases as structural complexity accumulates.

## 4. Polynomial Approximation

The critical insight is that reaction-diffusion steady states, while solutions of PDEs, are smooth functions on compact domains and therefore admit efficient polynomial approximation via Taylor expansion, Chebyshev projection, or radial basis function interpolation. For a pattern with characteristic wavelength $\lambda$ on a domain of size $L$, a polynomial of degree $d \approx 2L/\lambda$ suffices to capture the visible structure. This is typically degree 6–12 for common biological patterns, well within PolyArt's efficient evaluation range.

## 5. Variants and Extensions

The Gray-Scott model extends the basic Turing system with cubic kinetics, producing a richer taxonomy of patterns including "coral," "mitosis," and "spirals." The Gierer-Meinhardt model introduces nonlinear production terms. Each variant generates steady states with distinct topological features—genus, curvature distribution, and symmetry group—that map naturally onto polynomial shape descriptors in PolyArt.

## 6. Applications in Game Art

Procedural texture generation for games benefits enormously from polynomial-represented biological patterns. A single set of polynomial coefficients can encode a skin texture, a stone surface, or a foliage canopy at arbitrary resolution. Level-of-detail is controlled by truncating the polynomial to lower degree. During gameplay, pattern parameters (diffusion rates, reaction constants) can be interpolated in real time, allowing environments to visually evolve without precomputed texture atlases.

## References

1. Turing, A. M. "The Chemical Basis of Morphogenesis." *Philosophical Transactions of the Royal Society*, 1952.
2. Gray, P. and Scott, S. K. "Autocatalytic Reactions in the Isothermal, Continuous Stirred Tank Reactor." *Chemical Engineering Science*, 1983.
3. Gierer, A. and Meinhardt, H. "A Theory of Biological Pattern Formation." *Kybernetik*, 1972.
4. Murray, J. D. *Mathematical Biology*. Springer, 2002.
5. Cook, M. "An Explanation of Spiral Pattern Generation." Available online, 2024.
