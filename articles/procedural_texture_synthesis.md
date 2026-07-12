# Procedural Texture Synthesis via Polynomial Fields

Procedural texture generation replaces hand-authored image assets with algorithmic rules that produce visual patterns on demand. This article develops a framework for texture synthesis grounded in polynomial scalar and vector fields, covering noise generation, reaction-diffusion dynamics, and cellular automata approximation. These techniques supply the texture layer for PolyArt compositions, where polynomial curves define geometry and procedural fields define surface appearance.

## Texture Models

A procedural texture is a function $T: \mathbb{R}^2 \to \mathbb{R}^k$ mapping spatial coordinates to color or scalar values. The function is composed from elementary building blocks—noise, gradients, and pattern primitives—combined via arithmetic operations and domain warping. The key advantage over bitmap textures is infinite resolution: $T$ can be evaluated at any scale without interpolation artifacts.

```python
import numpy as np

def evaluate_texture(texture_fn, resolution=(512, 512), bounds=((-1, 1), (-1, 1))):
    """Evaluate a procedural texture function over a pixel grid."""
    height, width = resolution
    x = np.linspace(bounds[0][0], bounds[0][1], width)
    y = np.linspace(bounds[1][0], bounds[1][1], height)
    xx, yy = np.meshgrid(x, y)
    return texture_fn(xx, yy)
```

## Polynomial Noise

Perlin-like noise can be generated from polynomial basis functions evaluated at lattice points, then interpolated. Instead of the standard permutation-table approach, we use a set of low-degree polynomials as kernel functions, producing smooth random fields with controllable spectral content.

```python
def polynomial_noise_field(seed=42, num_lattice=8, degree=3):
    """Generate a noise field using polynomial interpolation at lattice points."""
    rng = np.random.RandomState(seed)
    lattice_x = np.linspace(0, 1, num_lattice)
    lattice_y = np.linspace(0, 1, num_lattice)
    xx, yy = np.meshgrid(lattice_x, lattice_y)
    
    # Random lattice values
    lattice_values = rng.randn(num_lattice, num_lattice)
    
    def noise_fn(x, y):
        # Find lattice cell
        ix = np.clip((x * (num_lattice - 1)).astype(int), 0, num_lattice - 2)
        iy = np.clip((y * (num_lattice - 1)).astype(int), 0, num_lattice - 2)
        fx = x * (num_lattice - 1) - ix
        fy = y * (num_lattice - 1) - iy
        
        # Bilinear interpolation (degree-1 polynomial)
        c00 = lattice_values[iy, ix]
        c10 = lattice_values[iy, ix + 1]
        c01 = lattice_values[iy + 1, ix]
        c11 = lattice_values[iy + 1, ix + 1]
        
        return (c00 * (1 - fx) * (1 - fy) + c10 * fx * (1 - fy) +
                c01 * (1 - fx) * fy + c11 * fx * fy)
    
    return noise_fn

def fbm_noise(base_fn, octaves=6, lacunarity=2.0, persistence=0.5):
    """Fractal Brownian Motion from base polynomial noise."""
    def fbm(x, y):
        value = np.zeros_like(x)
        amplitude = 1.0
        frequency = 1.0
        for _ in range(octaves):
            value += amplitude * base_fn(x * frequency, y * frequency)
            amplitude *= persistence
            frequency *= lacunarity
        return value
    return fbm
```

## Reaction-Diffusion

Reaction-diffusion systems, modeled by partial differential equations of the form $\partial u/\partial t = D_u \nabla^2 u + f(u,v)$, produce Turing patterns—spots, stripes, and labyrinthine textures—found throughout biological systems. Discretizing the Laplacian on a grid and stepping forward with an Euler scheme provides an efficient polynomial-field approximation.

```python
def reaction_diffusion_step(U, V, Du, Dv, f, k, dt=1.0):
    """Advance a Gray-Scott reaction-diffusion system by one time step."""
    # 5-point Laplacian stencil
    laplacian_U = (
        np.roll(U, 1, axis=0) + np.roll(U, -1, axis=0) +
        np.roll(U, 1, axis=1) + np.roll(U, -1, axis=1) - 4 * U
    )
    laplacian_V = (
        np.roll(V, 1, axis=0) + np.roll(V, -1, axis=0) +
        np.roll(V, 1, axis=1) + np.roll(V, -1, axis=1) - 4 * V
    )
    
    U_new = U + dt * (Du * laplacian_U - U * V**2 + f * (1 - U))
    V_new = V + dt * (Dv * laplacian_V + U * V**2 - (f + k) * V)
    
    return U_new, V_new

def generate_turing_pattern(width=200, height=200, steps=10000, f=0.04, k=0.06):
    """Generate a Turing pattern via reaction-diffusion."""
    rng = np.random.RandomState(0)
    U = np.ones((height, width))
    V = np.zeros((height, width))
    
    # Seed with random concentrations in center region
    cx, cy = width // 2, height // 2
    r = width // 10
    U[cy-r:cy+r, cx-r:cx+r] = 0.50 + 0.01 * rng.randn(2 * r, 2 * r)
    V[cy-r:cy+r, cx-r:cx+r] = 0.25 + 0.01 * rng.randn(2 * r, 2 * r)
    
    for _ in range(steps):
        U, V = reaction_diffusion_step(U, V, Du=0.16, Dv=0.08, f=f, k=k)
    
    return V
```

## Cellular Patterns

Cellular automata produce discrete textures with sharp boundaries. A polynomial approximation maps the binary cell state to smooth values suitable for rendering. By applying a degree-3 smoothing kernel to the CA state, we obtain continuous fields that blend naturally with polynomial curve overlays.

```python
def cellular_automaton_1d(width=512, rule=110, steps=256):
    """Generate a 1D cellular automaton pattern."""
    cells = np.zeros(width, dtype=int)
    cells[width // 2] = 1
    pattern = np.zeros((steps, width), dtype=int)
    pattern[0] = cells
    
    for step in range(1, steps):
        new_cells = np.zeros(width, dtype=int)
        for i in range(1, width - 1):
            neighborhood = (cells[i-1] << 2) | (cells[i] << 1) | cells[i+1]
            new_cells[i] = (rule >> neighborhood) & 1
        cells = new_cells
        pattern[step] = cells
    
    return pattern

def smooth_cellular(pattern, sigma=2.0):
    """Apply polynomial smoothing to a cellular automaton pattern."""
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(pattern.astype(float), sigma=sigma)
```

## Tileable Textures

For game and web applications, textures must tile seamlessly. Polynomial fields achieve this through periodic boundary conditions in the lattice and phase-preserving noise functions. The modular structure of polynomial evaluation ensures that $T(0, y) = T(1, y)$ when the basis functions are periodic.

```python
def tileable_noise(seed=42, num_lattice=8):
    """Generate a noise field that tiles seamlessly."""
    rng = np.random.RandomState(seed)
    lattice_values = rng.randn(num_lattice, num_lattice)
    # Force wrap-around continuity
    lattice_values[:, 0] = lattice_values[:, -1]
    lattice_values[0, :] = lattice_values[-1, :]
    
    def noise_fn(x, y):
        # Use periodic coordinates
        x_mod = x % 1.0
        y_mod = y % 1.0
        ix = (x_mod * num_lattice).astype(int) % num_lattice
        iy = (y_mod * num_lattice).astype(int) % num_lattice
        fx = x_mod * num_lattice - ix
        fy = y_mod * num_lattice - iy
        ix_next = (ix + 1) % num_lattice
        iy_next = (iy + 1) % num_lattice
        
        return (lattice_values[iy, ix] * (1 - fx) * (1 - fy) +
                lattice_values[iy, ix_next] * fx * (1 - fy) +
                lattice_values[iy_next, ix] * (1 - fx) * fy +
                lattice_values[iy_next, ix_next] * fx * fy)
    
    return noise_fn
```

## Game Applications

PolyArt exports polynomial-curve artwork as tileable textures for game engines. Each curve segment is rasterized with procedural shading, and the tile boundaries are ensured continuous via the periodic polynomial fields. This pipeline generates unique, mathematically coherent texture atlases without manual artist intervention.

## References

1. Perlin, K. (2002). "Improving Noise." *ACM SIGGRAPH*, 26(2), 681–682.
2. Gray, J. A. & Scott, S. K. (1990). "Autocatalytic reactions in the isotropic and anisotropic regimes." *Physica D*, 34, 383–398.
3. Wolfram, S. (1984). "Cellular Automata as Models of Complexity." *Nature*, 311, 419–424.
4. Ebert, D. S. et al. (2003). *Texturing and Modeling: A Procedural Approach*. Morgan Kaufmann.
5. Gustavson, S. (2005). "Simplex noise demystified." *Web article*.
