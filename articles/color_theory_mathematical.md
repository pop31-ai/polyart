# Mathematical Color Theory for Generative Art

Color selection in generative art systems demands a rigorous mathematical framework that bridges device-independent color spaces with human perceptual response. This article develops the core mathematical models—HSV, HSL, CIELAB—and shows how algebraic constructions such as the golden ratio yield aesthetically balanced palettes. The PolyArt system uses these foundations to generate deterministic, reproducible color schemes for polynomial-curve renderings.

## Color Models

The RGB model maps directly to display hardware but is perceptually non-uniform: equal step sizes in RGB coordinates do not correspond to equal perceived color differences. The HSV (Hue, Saturation, Value) and HSL (Hue, Saturation, Lightness) models decouple chrominance from luminance, enabling intuitive palette control. The conversion from RGB to HSV is given by:

$$H = \begin{cases} 0^\circ & \text{if } C = 0 \\ 60^\circ \cdot \left(\frac{G - B}{C} \bmod 6\right) & \text{if } V = R \\ 60^\circ \cdot \left(\frac{B - R}{C} + 2\right) & \text{if } V = G \\ 60^\circ \cdot \left(\frac{R - G}{C} + 4\right) & \text{if } V = B \end{cases}$$

where $C = \max(R,G,B) - \min(R,G,B)$.

```python
import colorsys

def hsv_to_rgb_array(h, s, v):
    """Convert HSV values (h in degrees 0-360, s,v in 0-1) to RGB."""
    r, g, b = colorsys.hsv_to_rgb(h / 360.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def rgb_to_hsv_array(r, g, b):
    """Convert RGB (0-255) to HSV (h: 0-360, s: 0-1, v: 0-1)."""
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return (h * 360.0, s, v)
```

## Perceptual Spaces

For high-fidelity color manipulation, CIELAB (L\*a\*b\*) provides perceptual uniformity: a Euclidean distance of 1 unit in L\*a\*b\* space corresponds roughly to a just-noticeable difference. The CIELUV space offers similar advantages and is preferred for self-luminous displays. Transforming palette coordinates into perceptual space before interpolation ensures smooth, artifact-free gradients.

```python
import numpy as np

def linear_interpolation_rgb(c1, c2, t):
    """Linearly interpolate between two RGB colors."""
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def perceptual_gradient(c1, c2, steps=50):
    """Generate a gradient with perceptual weighting applied to HSV interpolation."""
    h1, s1, v1 = rgb_to_hsv_array(*c1)
    h2, s2, v2 = rgb_to_hsv_array(*c2)
    gradient = []
    for i in range(steps):
        t = i / (steps - 1)
        # Apply gamma correction for perceptual uniformity
        t_perceptual = t ** 1.5
        h = h1 + (h2 - h1) * t_perceptual
        s = s1 + (s2 - s1) * t_perceptual
        v = v1 + (v2 - v1) * t_perceptual
        gradient.append(hsv_to_rgb_array(h % 360, s, v))
    return gradient
```

## φ-based Palettes

The golden ratio $\varphi = (1 + \sqrt{5})/2 \approx 1.618$ provides a natural mechanism for generating hue sequences that avoid repetition and clustering. By setting successive hues as $\theta_n = (n \cdot 137.508^\circ) \bmod 360°$—derived from $360°/\varphi^2$—the resulting palette achieves maximum visual separation with no two adjacent hues forming a simple rational fraction of the circle.

```python
def golden_ratio_palette(base_hue=0, saturation=0.7, value=0.85, count=12):
    """Generate a color palette using golden-ratio-based hue spacing."""
    golden_angle = 360.0 / (1.618033988749895 ** 2)  # ~137.508 degrees
    palette = []
    for i in range(count):
        hue = (base_hue + i * golden_angle) % 360
        palette.append(hsv_to_rgb_array(hue, saturation, value))
    return palette
```

## Gradient Algorithms

Smooth gradient generation along a parametric curve requires mapping the parameter $t \in [0,1]$ to a color trajectory. Catmull-Rom splines in HSV space produce $C^1$-continuous color transitions. For PolyArt's polynomial curves, the gradient is computed by composing the curve's polynomial parameterization with a color-transfer function.

```python
def catmull_rom_gradient(control_colors, t):
    """Interpolate along a Catmull-Rom spline in HSV space at parameter t."""
    n = len(control_colors) - 1
    segment = min(int(t * n), n - 1)
    local_t = (t * n) - segment
    
    hsv_points = [rgb_to_hsv_array(*c) for c in control_colors]
    p0 = hsv_points[max(segment - 1, 0)]
    p1 = hsv_points[segment]
    p2 = hsv_points[min(segment + 1, n)]
    p3 = hsv_points[min(segment + 2, n)]
    
    result = []
    for channel in range(3):
        v = catmull_rom_value(p0[channel], p1[channel], p2[channel], p3[channel], local_t)
        result.append(v)
    
    return hsv_to_rgb_array(result[0] % 360, max(0, min(1, result[1])), max(0, min(1, result[2])))

def catmull_rom_value(p0, p1, p2, p3, t):
    t2 = t * t
    t3 = t2 * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
```

## Alpha Blending

Compositing semi-transparent polynomial curves requires alpha blending in linear light space. The standard over operator is $C_{\text{out}} = \alpha_a C_a + (1 - \alpha_a) C_b$, applied per-channel after gamma-linearization.

```python
def linearize(c):
    """Convert sRGB to linear RGB."""
    return [(x / 255.0) ** 2.2 for x in c]

def delinearize(c):
    """Convert linear RGB back to sRGB."""
    return tuple(int((max(0, min(1, x)) ** (1 / 2.2)) * 255) for x in c)

def alpha_blend(fg, bg, alpha):
    """Alpha-composite fg over bg in linear light space."""
    fg_lin = linearize(fg)
    bg_lin = linearize(bg)
    blended = [alpha * f + (1 - alpha) * b for f, b in zip(fg_lin, bg_lin)]
    return delinearize(blended)
```

## References

1. Fairchild, M. D. (2013). *Color Appearance Models*. Wiley.
2. Wyszecki, G. & Stiles, W. S. (1982). *Color Science*. Wiley.
3. Glassner, A. (1995). *Principles of Digital Image Synthesis*. Morgan Kaufmann.
4. Smith, A. R. (1978). "Color Gamut Transform Pairs." *ACM SIGGRAPH*, 12(3), 12–19.
5. GREENE, S. (1990). "Hue luma color model for computer graphics." *IEEE CG&A*.
