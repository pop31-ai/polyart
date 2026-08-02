"""
PolyArt Relief — лазерное сканирование картины маслом как ландшафт.

Идея: картина маслом — не плоское изображение, а рельеф пасты (импасто).
"Лазерное сканирование" восстанавливает высотную карту H(x, y) по яркости и
энергии мазков, после чего сцена описывается в терминах рельефа:

    горы    — локальные максимумы H (толстые мазки)  → контурные кольца
    озёра   — локальные минимумы H (тёмные лессировки) → залитые эллипсы
    равнины — зоны малого рельефа                      → полиномиальные пятна

Результат генерируется как скрипт мета-языка (.plang) — "упоминание с
координатами" — и через save_polyart() превращается в канонический
.polyart JSON, рендерящийся стандартным конвейером.

CLI:
    python polyart_relief.py <painting.png> <stem>
        -> <stem>.plang, <stem>_topomap.png (эталонная карта рельефа)
    затем: python polyart_lang.py <stem>.plang
        -> <stem>.png, <stem>.polyart
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter, maximum_filter, minimum_filter, label

MOUNTAIN_COLORS = ["#6a5a2a", "#8a7a3a", "#a8904c", "#c8b060", "#e8dc80"]
LAKE_COLOR = "#2a5a8a"
LAKE_SHORE = "#8ab8d8"
PLAIN_COLOR = "#3a3a2a"
BG = "#0d0a1a"


def load_gray(path):
    img = plt.imread(path)
    if img.ndim == 3:
        gray = np.mean(img[:, :, :3], axis=2)
    else:
        gray = img
    g = gray.astype(np.float64)
    return g / g.max() if g.max() > 1 else g


def simulate_scan(path):
    """Симуляция лазерного сканирования картины маслом.

    Возвращает карту рельефа пасты (энергия мазков = толщина импасто) и
    исходную яркость. Горы — высокоэнергетичные мазки; озёра — гладкие
    тёмные зоны (лессировки); равнины — гладкие светлые участки.
    """
    gray = load_gray(path)
    gy, gx = np.gradient(gray)
    energy = np.hypot(gx, gy)
    energy = energy / (energy.max() + 1e-9)
    energy = gaussian_filter(energy, 2)
    return energy, gray


def _detect_extrema(H, n, min_dist, use_max, border_frac=0.03):
    h, w = H.shape
    filt = maximum_filter if use_max else minimum_filter
    m = filt(H, size=2 * min_dist + 1)
    mask = (H == m) & (H > 0.02)
    yb, xb = int(h * border_frac), int(w * border_frac)
    mask[:yb, :] = False
    mask[-yb:, :] = False
    mask[:, :xb] = False
    mask[:, -xb:] = False
    cand = np.argwhere(mask)
    if len(cand) == 0:
        return []
    vals = H[cand[:, 0], cand[:, 1]]
    ring = max(min_dist // 2, 4)
    prom = np.zeros(len(cand))
    for i, (y, x) in enumerate(cand):
        y0, y1 = max(0, y - ring), min(h, y + ring + 1)
        x0, x1 = max(0, x - ring), min(w, x + ring + 1)
        prom[i] = vals[i] - float(np.median(H[y0:y1, x0:x1]))
    order = np.argsort(-prom)
    picked = []
    for i in order:
        y, x = cand[i]
        if all((y - y0) ** 2 + (x - x0) ** 2 >= min_dist ** 2 for (y0, x0) in picked):
            picked.append((int(y), int(x)))
            if len(picked) >= n:
                break
    return picked


def _support_radius(H, y, x, frac=0.4, max_r=120):
    h0 = H[y, x]
    hmax, wmax = H.shape
    for r in range(2, max_r):
        y0, y1 = max(0, y - r), min(hmax, y + r + 1)
        x0, x1 = max(0, x - r), min(wmax, x + r + 1)
        if np.mean(H[y0:y1, x0:x1]) < h0 * frac:
            return r
    return max_r


def analyze_terrain(relief, gray, n_mountains=6, n_lakes=4, min_dist=24):
    h, w = gray.shape
    energy = relief

    peaks = _detect_extrema(energy, n_mountains, min_dist, use_max=True)
    mountains = []
    for (y, x) in peaks:
        r = _support_radius(energy, y, x) * 1.5
        mountains.append({"x": float(x), "y": float(y),
                          "h": float(energy[y, x]), "r": max(r, 14.0)})

    lakes = []
    base = float(np.percentile(gray, 60))
    smooth_thr = float(np.percentile(energy, 65))
    lake_mask = (gray < base - 0.015) & (energy < smooth_thr)
    lbl, ncomp = label(lake_mask)
    comps = []
    for i in range(1, ncomp + 1):
        ys, xs = np.where(lbl == i)
        if len(ys) < 40:
            continue
        if len(ys) > 0.12 * h * w:
            continue
        bw, bh = xs.max() - xs.min(), ys.max() - ys.min()
        if bw > 0.6 * w or bh > 0.6 * h:
            continue
        comps.append({"cx": float(xs.mean()), "cy": float(ys.mean()),
                      "rx": bw / 2 + 1, "ry": bh / 2 + 1, "area": len(ys)})
    comps.sort(key=lambda c: -c["area"])
    lakes = comps[:n_lakes]

    return {
        "mountains": mountains,
        "lakes": lakes,
        "size": (h, w),
        "mean": float(energy.mean()),
    }


def features_to_plang(feat, out_plang, stem, canvas_size=10.0):
    h, w = feat["size"]
    sx = canvas_size / w
    half = canvas_size / 2.0
    ylim = half * h / w

    def px(x):  # пиксель -> юниты холста
        return (x - w / 2.0) * sx

    def py(y):  # пиксель -> юниты холста (y инвертирован)
        return (h / 2.0 - y) * sx

    def rp(r):
        return r * sx

    lines = []
    lines.append(f"# PolyArt Relief: ландшафт по лазерному сканированию {os.path.basename(stem)}")
    lines.append(f'canvas({canvas_size}, {canvas_size}, "{BG}");')
    lines.append(f"xlim({-half}, {half});")
    lines.append(f"ylim({-ylim:.4f}, {ylim:.4f});")
    lines.append("")

    lines.append("# равнины (зоны малого рельефа)")
    lines.append(f'oval(0, 0, {half:.3f}, {ylim:.3f}, true, "{PLAIN_COLOR}", 0.45, "{PLAIN_COLOR}", 0.1);')
    lines.append("")

    lines.append("# озёра (лессировки и тёмные гладкие зоны)")
    for lk in feat["lakes"]:
        lines.append(f'oval({px(lk["cx"]):.3f}, {py(lk["cy"]):.3f}, '
                     f'{rp(lk["rx"]):.3f}, {rp(lk["ry"]):.3f}, '
                     f'true, "{LAKE_COLOR}", 0.75, "{LAKE_SHORE}", 0.3);')
        lines.append(f'circle({px(lk["cx"]):.3f}, {py(lk["cy"]):.3f}, '
                     f'{rp(max(lk["rx"], lk["ry"])) * 1.35:.3f}, '
                     f'false, "{LAKE_SHORE}", 0.4, "{LAKE_SHORE}", 0.25);')
    lines.append("")

    lines.append("# горы (толстые мазки пасты — контурные кольца)")
    n_col = len(MOUNTAIN_COLORS)
    for m in sorted(feat["mountains"], key=lambda m: -m["h"]):
        cx = px(m["x"])
        cy = py(m["y"])
        for k in range(n_col):
            rr = rp(m["r"]) * 2.5 * (1.0 - k / (n_col + 1.0))
            if rr < 0.05:
                continue
            col = MOUNTAIN_COLORS[k]
            alpha = 0.4 + 0.12 * k
            lines.append(f'circle({cx:.3f}, {cy:.3f}, {rr:.3f}, false, "{col}", {alpha:.2f}, "{col}", 0.5);')
    lines.append("")

    lines.append(f'render("{stem}.png", 150);')
    lines.append(f'save_polyart("{stem}.polyart");')
    lines.append('print("terrain done");')

    with open(out_plang, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[OK] Plang: {out_plang}")


def render_topomap(feat, relief, out_png):
    h, w = feat["size"]
    fig, ax = plt.subplots(1, 1, figsize=(8, 8 * h / w), facecolor=BG)
    ax.set_facecolor(BG)
    levels = np.linspace(0.0, 1.0, 20)
    cs = ax.contourf(relief, levels=levels, cmap="terrain")
    ax.contour(relief, levels=levels[::2], colors="#1a1a0a", linewidths=0.3, alpha=0.6)
    for m in feat["mountains"]:
        ax.plot(m["x"], m["y"], "o", color="white", markersize=4)
    for lk in feat["lakes"]:
        ax.plot(lk["cx"], lk["cy"], "o", color="#8ab8d8", markersize=4)
    ax.set_title("Laser-scan relief (terrain)", color="#e8dc80", fontsize=10)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_png, dpi=150, facecolor=BG)
    plt.close(fig)
    print(f"[OK] Topomap: {out_png}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python polyart_relief.py <painting.png> <stem>")
        return
    painting, stem = sys.argv[1], sys.argv[2]
    relief, gray = simulate_scan(painting)
    feat = analyze_terrain(relief, gray)
    features_to_plang(feat, stem + ".plang", stem)
    render_topomap(feat, relief, stem + "_topomap.png")
    print(f"[DONE] Mountains={len(feat['mountains'])}, Lakes={len(feat['lakes'])}")
    print(f"       Run: python polyart_lang.py {stem}.plang")


if __name__ == "__main__":
    main()
