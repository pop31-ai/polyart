"""
PolyArt MetaDesk — перевод изображения в мета-текстовое описание (.plang).

Прямой мост «растр -> мета-язык»: картинка превращается в текстовый скрипт
мета-языка, где каждый контур описан как `polygon({x0, y0, x1, y1, ...})` —
«упоминание с координатами». Комментарии классифицируют фигуры
(окружность / многоугольник / кривая) для последующего анализа.

Экономия связи: текст (координаты контуров) компактнее растра и допускает
анализ, индексирование, передачу и восстановление через стандартный
конвейер (render -> PNG, save_polyart -> .polyart).

CLI:
    python polyart_metadesc.py <image.png> <stem> [--max-contours N] [--eps E]
        -> <stem>.plang   (мета-текстовое описание)
    затем: python polyart_lang.py <stem>.plang
        -> <stem>.png, <stem>.polyart
"""

import os
import sys
import json
import argparse
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BG = "#0d0a1a"


def load_rgb(path):
    img = plt.imread(path)
    if img.dtype == np.float64 or img.dtype == np.float32:
        if img.max() <= 1.0:
            img = (img * 255).astype(np.uint8)
    if img.ndim == 2:
        img = np.stack([img, img, img], axis=-1)
    if img.shape[2] == 4:
        rgb = img[:, :, :3].astype(np.float64)
        alpha = img[:, :, 3:4].astype(np.float64) / 255.0 if img[:, :, 3].max() > 1 else img[:, :, 3:4]
        bg = np.ones_like(rgb) * 255.0
        rgb = (rgb * alpha + bg * (1.0 - alpha)).astype(np.uint8)
        img = rgb
    return img[:, :, :3]


def extract_regions(path, k=12, min_area=120, downscale=0.35):
    """Постеризация изображения (k-средние в LAB): k цветовых кластеров ->
    замкнутые контуры областей. Возвращает список {pts, color, area}."""
    img = load_rgb(path)
    h, w = img.shape[:2]
    small = cv2.resize(img, (int(w * downscale), int(h * downscale)),
                       interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(small, cv2.COLOR_RGB2LAB)
    data = lab.reshape(-1, 3).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(data, k, None, crit, 5, cv2.KMEANS_PP_CENTERS)
    centers = cv2.cvtColor(centers.reshape(-1, 1, 3).astype(np.uint8),
                           cv2.COLOR_LAB2RGB).reshape(-1, 3)
    labels = labels.reshape(small.shape[:2])
    regions = []
    for lab_ in range(k):
        mask = (labels == lab_).astype(np.uint8) * 255
        cnts, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            area = cv2.contourArea(c)
            if area < min_area:
                continue
            pts = c.reshape(-1, 2).astype(np.float64)
            pts *= 1.0 / downscale
            regions.append({
                "pts": pts,
                "color": centers[lab_],
                "area": area / (downscale * downscale),
            })
    regions.sort(key=lambda r: -r["area"])
    return regions


def douglas_peucker(pts, eps):
    """Упрощение полилинии (Ramer–Douglas–Peucker)."""
    pts = np.asarray(pts, dtype=np.float64)
    if len(pts) <= 2:
        return pts

    def perp_dist(p, a, b):
        if np.allclose(a, b):
            return np.hypot(p[0] - a[0], p[1] - a[1])
        t = np.dot(p - a, b - a) / np.dot(b - a, b - a)
        t = max(0.0, min(1.0, t))
        proj = a + t * (b - a)
        return np.hypot(p[0] - proj[0], p[1] - proj[1])

    def recurse(i, j):
        a, b = pts[i], pts[j]
        if j - i <= 1:
            return [pts[i], pts[j]]
        d = np.array([perp_dist(p, a, b) for p in pts[i + 1:j]])
        if len(d) == 0:
            return [pts[i], pts[j]]
        k = int(np.argmax(d))
        if d[k] > eps:
            left = recurse(i, i + 1 + k)
            right = recurse(i + 1 + k, j)
            return left[:-1] + right
        return [pts[i], pts[j]]

    out = recurse(0, len(pts) - 1)
    return np.array(out)


def fit_circle(pts):
    x, y = pts[:, 0], pts[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones(len(pts))]
    b = x ** 2 + y ** 2
    try:
        sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    except np.linalg.LinAlgError:
        return None
    cx, cy, cc = sol
    r2 = cx ** 2 + cy ** 2 + cc
    if r2 <= 0:
        return None
    r = np.sqrt(r2)
    err = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    return (cx, cy, r), float(np.mean(err) / r)


def classify_shape(pts):
    """Классификация контура: circle / polygon / curve (для комментария)."""
    circ = fit_circle(pts)
    if circ and circ[1] < 0.12:
        cx, cy, r = circ[0]
        return f"circle(cx={cx:.2f}, cy={cy:.2f}, r={r:.2f})"
    simp = douglas_peucker(pts, 4.0)
    if 3 <= len(simp) <= 10:
        return f"polygon(vertices={len(simp)})"
    return f"curve(points={len(pts)})"


def to_hex(c):
    r, g, b = [int(v) for v in c]
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def contours_to_plang(regions, out_plang, stem, canvas_size=10.0, eps=1.5):
    if not regions:
        raise ValueError("no regions found")
    img_h, img_w = _region_size(regions)
    sx = canvas_size / img_w
    half = canvas_size / 2.0
    ylim = half * img_h / img_w

    def px(x):
        return (x - img_w / 2.0) * sx

    def py(y):
        return (img_h / 2.0 - y) * sx

    lines = []
    lines.append(f"# PolyArt MetaDesk: мета-текстовое описание {os.path.basename(stem)}")
    lines.append(f"# источник: {os.path.basename(stem)}.png | областей: {len(regions)}")
    lines.append(f'canvas({canvas_size}, {canvas_size}, "{BG}");')
    lines.append(f"xlim({-half}, {half});")
    lines.append(f"ylim({-ylim:.4f}, {ylim:.4f});")
    lines.append("")

    for i, r in enumerate(regions):
        pts = r["pts"]
        simp = douglas_peucker(pts, eps)
        if len(simp) < 3:
            continue
        closed = np.vstack([simp, simp[0]])
        col = to_hex(r["color"])
        cls = classify_shape(closed)
        lines.append(f"# shape #{i}: {cls}, color={col}")
        flat = []
        for x, y in closed:
            flat.append(f"{px(x):.2f}")
            flat.append(f"{py(y):.2f}")
        chunk = ", ".join(flat)
        lines.append(f"polygon({{{chunk}}}, \"{col}\", \"{col}\");")
        lines.append("")

    lines.append(f'render("{stem}.png", 150);')
    lines.append(f'save_polyart("{stem}.polyart");')
    lines.append('print("metadesc done");')

    with open(out_plang, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[OK] Plang: {out_plang} (regions={len(regions)}, text size={os.path.getsize(out_plang)} B)")
    return out_plang


def _region_size(regions):
    xmax = max(float(r["pts"][:, 0].max()) for r in regions)
    ymax = max(float(r["pts"][:, 1].max()) for r in regions)
    return int(round(ymax)) + 1, int(round(xmax)) + 1


def main():
    ap = argparse.ArgumentParser(description="Image -> polyart meta-text description (.plang)")
    ap.add_argument("image")
    ap.add_argument("stem")
    ap.add_argument("--max-regions", type=int, default=50)
    ap.add_argument("--k", type=int, default=8, help="цветовых кластеров")
    ap.add_argument("--eps", type=float, default=1.5)
    args = ap.parse_args()

    regions = extract_regions(args.image, k=args.k)[:args.max_regions]
    contours_to_plang(regions, args.stem + ".plang", args.stem, eps=args.eps)
    print(f"[DONE] {len(regions)} regions -> {args.stem}.plang")
    print(f"       Run: python polyart_lang.py {args.stem}.plang")


if __name__ == "__main__":
    main()
