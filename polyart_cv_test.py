"""
PolyArt CV Test - Computer Vision image classification using pure math features.
Classifies images as "rare art" or "living/biological" via feature analysis.
No external ML libraries - only numpy, matplotlib, os, json, math.
"""

import sys
import io
import os
import json
import math
import tempfile

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

if sys.stdout.encoding is None or sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class ImageFeatureExtractor:
    """Extract mathematical features from images using numpy."""

    @staticmethod
    def load_image(path):
        """Load image as numpy array using matplotlib."""
        img = plt.imread(path)
        if img.dtype == np.float32 or img.dtype == np.float64:
            img = (img * 255).clip(0, 255).astype(np.uint8)
        return img

    @staticmethod
    def color_histogram(img, n_bins=32):
        """Compute color histogram features."""
        channels = []
        if len(img.shape) == 3:
            for c in range(min(img.shape[2], 3)):
                hist, _ = np.histogram(img[:, :, c].flatten(), bins=n_bins, range=(0, 256))
                channels.append(hist.astype(np.float64))
        else:
            hist, _ = np.histogram(img.flatten(), bins=n_bins, range=(0, 256))
            channels.append(hist.astype(np.float64))
        combined = np.concatenate(channels)
        total = combined.sum()
        if total > 0:
            combined /= total
        return combined

    @staticmethod
    def edge_density(img):
        """Compute edge density using Sobel-like gradient."""
        if len(img.shape) == 3:
            gray = np.mean(img[:, :, :3], axis=2)
        else:
            gray = img.astype(np.float64)
        gy = np.gradient(gray, axis=0)
        gx = np.gradient(gray, axis=1)
        mag = np.sqrt(gx ** 2 + gy ** 2)
        max_possible = np.sqrt(2) * 255
        return float(np.mean(mag) / max_possible) if max_possible > 0 else 0.0

    @staticmethod
    def symmetry_score(img):
        """Compute bilateral symmetry score."""
        if len(img.shape) == 3:
            gray = np.mean(img[:, :, :3], axis=2)
        else:
            gray = img.astype(np.float64)
        h, w = gray.shape
        mid = w // 2
        left = gray[:, :mid]
        right = np.fliplr(gray[:, w - mid:])
        min_h = min(left.shape[0], right.shape[0])
        min_w = min(left.shape[1], right.shape[1])
        diff = np.abs(left[:min_h, :min_w] - right[:min_h, :min_w])
        max_val = 255.0
        score = 1.0 - np.mean(diff) / max_val
        return float(max(0.0, min(1.0, score)))

    @staticmethod
    def fractal_dimension(img, threshold=128):
        """Estimate fractal dimension using box-counting."""
        if len(img.shape) == 3:
            gray = np.mean(img[:, :, :3], axis=2)
        else:
            gray = img.astype(np.float64)
        binary = (gray > threshold).astype(np.uint8)
        h, w = binary.shape
        max_dim = max(h, w)
        powers = [2 ** i for i in range(1, int(np.log2(max_dim)) + 1) if 2 ** i <= max_dim]
        if len(powers) < 2:
            return 1.5
        counts = []
        for box_size in powers:
            count = 0
            for y in range(0, h, box_size):
                for x in range(0, w, box_size):
                    block = binary[y:y + box_size, x:x + box_size]
                    if block.any():
                        count += 1
            if count > 0:
                counts.append((box_size, count))
        if len(counts) < 2:
            return 1.5
        log_sizes = np.log([c[0] for c in counts])
        log_counts = np.log([c[1] for c in counts])
        coeffs = np.polyfit(log_sizes, log_counts, 1)
        fd = -coeffs[0]
        return float(np.clip(fd, 1.0, 2.0))

    @staticmethod
    def texture_complexity(img):
        """Compute texture complexity via local variance."""
        if len(img.shape) == 3:
            gray = np.mean(img[:, :, :3], axis=2)
        else:
            gray = img.astype(np.float64)
        block = 8
        h, w = gray.shape
        variances = []
        for y in range(0, h - block + 1, block):
            for x in range(0, w - block + 1, block):
                patch = gray[y:y + block, x:x + block]
                variances.append(np.var(patch))
        if not variances:
            return 0.0
        mean_var = np.mean(variances)
        normalized = mean_var / (128.0 ** 2 + 1e-8)
        return float(min(1.0, normalized))

    @staticmethod
    def color_diversity(img):
        """Compute color diversity (unique hue count)."""
        if len(img.shape) < 3 or img.shape[2] < 3:
            return 0.1
        r = img[:, :, 0].astype(np.float64)
        g = img[:, :, 1].astype(np.float64)
        b = img[:, :, 2].astype(np.float64)
        max_c = np.maximum(np.maximum(r, g), b)
        min_c = np.minimum(np.minimum(r, g), b)
        diff = max_c - min_c
        saturation = np.where(max_c > 0, diff / (max_c + 1e-8), 0)
        hue = np.zeros_like(r)
        mask = diff > 0
        r_mask = (max_c == r) & mask
        g_mask = (max_c == g) & mask
        b_mask = (max_c == b) & mask
        hue[r_mask] = (60 * ((g[r_mask] - b[r_mask]) / (diff[r_mask] + 1e-8)) + 360) % 360
        hue[g_mask] = (60 * ((b[g_mask] - r[g_mask]) / (diff[g_mask] + 1e-8)) + 120) % 360
        hue[b_mask] = (60 * ((r[b_mask] - g[b_mask]) / (diff[b_mask] + 1e-8)) + 240) % 360
        sat_mask = saturation > 0.2
        if sat_mask.sum() == 0:
            return 0.0
        hue_vals = hue[sat_mask]
        hue_bins = np.round(hue_vals / 15).astype(int) % 24
        unique_hues = len(np.unique(hue_bins))
        return float(min(1.0, unique_hues / 24.0))

    @staticmethod
    def golden_ratio_score(img):
        """Score how well the composition follows golden ratio."""
        if len(img.shape) == 3:
            gray = np.mean(img[:, :, :3], axis=2)
        else:
            gray = img.astype(np.float64)
        h, w = gray.shape
        phi = (1 + math.sqrt(5)) / 2
        ratios = [w / h if h > 0 else 1.0, h / w if w > 0 else 1.0]
        ratio_scores = [1.0 - min(abs(r - phi) / phi, 1.0) for r in ratios]
        gy, gx = np.gradient(gray)
        energy = gx ** 2 + gy ** 2
        total_energy = energy.sum()
        if total_energy < 1e-8:
            return 0.5
        thirds = [
            energy[:h // 3, :].sum(),
            energy[h // 3:2 * h // 3, :].sum(),
            energy[2 * h // 3:, :].sum(),
        ]
        total_t = sum(thirds)
        if total_t > 0:
            thirds = [t / total_t for t in thirds]
        third_uniformity = 1.0 - np.std(thirds)
        golden_y = int(h / phi)
        golden_x = int(w / phi)
        region_sizes = []
        for ry in [golden_y, h - golden_y]:
            for rx in [golden_x, w - golden_x]:
                if ry > 0 and rx > 0:
                    region_sizes.append(energy[:ry, :rx].sum())
        if sum(region_sizes) > 0:
            region_dist = np.std(region_sizes) / (np.mean(region_sizes) + 1e-8)
        else:
            region_dist = 0.0
        score = (np.mean(ratio_scores) * 0.4 +
                 float(third_uniformity) * 0.3 +
                 max(0.0, 1.0 - region_dist) * 0.3)
        return float(np.clip(score, 0.0, 1.0))

    @staticmethod
    def polynomial_smoothness(img):
        """Fit polynomial to brightness profile, measure residuals."""
        if len(img.shape) == 3:
            gray = np.mean(img[:, :, :3], axis=2)
        else:
            gray = img.astype(np.float64)
        h, w = gray.shape
        row_profile = np.mean(gray, axis=1)
        col_profile = np.mean(gray, axis=0)
        x_row = np.linspace(-1, 1, len(row_profile))
        x_col = np.linspace(-1, 1, len(col_profile))
        scores = []
        for profile, x_vals in [(row_profile, x_row), (col_profile, x_col)]:
            coeffs = np.polyfit(x_vals, profile, min(5, len(profile) - 1))
            predicted = np.polyval(coeffs, x_vals)
            residual = np.sqrt(np.mean((profile - predicted) ** 2))
            norm = np.std(profile) + 1e-8
            scores.append(1.0 - min(residual / norm, 1.0))
        return float(np.clip(np.mean(scores), 0.0, 1.0))

    @staticmethod
    def curvature_energy(img):
        """Compute curvature energy of edge contours."""
        if len(img.shape) == 3:
            gray = np.mean(img[:, :, :3], axis=2)
        else:
            gray = img.astype(np.float64)
        gy = np.gradient(gray, axis=0)
        gx = np.gradient(gray, axis=1)
        mag = np.sqrt(gx ** 2 + gy ** 2)
        gyy = np.gradient(gy, axis=0)
        gxx = np.gradient(gx, axis=1)
        gxy = np.gradient(gx, axis=0)
        denom = (mag ** 2 + 1e-8) ** 1.5
        curvature = np.abs(gxx * gy ** 2 - 2 * gxy * gx * gy + gyy * gx ** 2) / denom
        edge_mask = mag > np.percentile(mag, 70)
        if edge_mask.sum() == 0:
            return 0.5
        edge_curvatures = curvature[edge_mask]
        mean_curv = np.mean(edge_curvatures)
        normalized = mean_curv / 1.0
        return float(np.clip(normalized, 0.0, 1.0))

    @staticmethod
    def extract_all(img):
        """Extract all features into a feature vector dict."""
        return {
            "edge_density": ImageFeatureExtractor.edge_density(img),
            "symmetry": ImageFeatureExtractor.symmetry_score(img),
            "fractal_dim": ImageFeatureExtractor.fractal_dimension(img),
            "texture": ImageFeatureExtractor.texture_complexity(img),
            "color_diversity": ImageFeatureExtractor.color_diversity(img),
            "golden_ratio": ImageFeatureExtractor.golden_ratio_score(img),
            "polynomial_smoothness": ImageFeatureExtractor.polynomial_smoothness(img),
            "curvature_energy": ImageFeatureExtractor.curvature_energy(img),
        }


class RarityScorer:
    """Score artwork rarity based on extracted features."""

    WEIGHTS = {
        "edge_density": 0.15,
        "symmetry": 0.12,
        "fractal_dim": 0.18,
        "texture": 0.10,
        "color_diversity": 0.12,
        "golden_ratio": 0.08,
        "polynomial_smoothness": 0.10,
        "curvature_energy": 0.15,
    }

    @staticmethod
    def compute_rarity(features):
        """Compute rarity score 0-100 from features."""
        fractal_norm = (features.get("fractal_dim", 1.5) - 1.0)
        sym = features.get("symmetry", 0.5)
        golden = features.get("golden_ratio", 0.5)
        poly = features.get("polynomial_smoothness", 0.5)
        edge = features.get("edge_density", 0.3)
        texture = features.get("texture", 0.3)
        color_div = features.get("color_diversity", 0.3)
        curvature = features.get("curvature_energy", 0.5)
        weighted = (
            RarityScorer.WEIGHTS["edge_density"] * (1.0 - edge) +
            RarityScorer.WEIGHTS["symmetry"] * sym +
            RarityScorer.WEIGHTS["fractal_dim"] * fractal_norm +
            RarityScorer.WEIGHTS["texture"] * texture +
            RarityScorer.WEIGHTS["color_diversity"] * color_div +
            RarityScorer.WEIGHTS["golden_ratio"] * golden +
            RarityScorer.WEIGHTS["polynomial_smoothness"] * poly +
            RarityScorer.WEIGHTS["curvature_energy"] * curvature
        )
        art_bonus = (sym * 0.3 + golden * 0.3 + poly * 0.2 + curvature * 0.2)
        raw_score = weighted * 60 + art_bonus * 40
        return float(np.clip(raw_score, 0, 100))

    @staticmethod
    def classify(features):
        """Classify as 'art' or 'living' based on feature profile."""
        sym = features.get("symmetry", 0.5)
        golden = features.get("golden_ratio", 0.5)
        poly = features.get("polynomial_smoothness", 0.5)
        curvature = features.get("curvature_energy", 0.5)
        fractal = features.get("fractal_dim", 1.5)
        texture = features.get("texture", 0.3)
        color_div = features.get("color_diversity", 0.3)
        art_score = sym * 2.5 + golden * 2.0 + poly * 1.5 + curvature * 1.5
        living_score = (fractal - 1.0) * 3.0 + texture * 2.0 + color_div * 1.5
        diff = art_score - living_score
        if diff > 0.3:
            return "art"
        elif diff < -0.3:
            return "living"
        else:
            return "borderline"

    @staticmethod
    def generate_report(features, rarity, classification):
        """Generate a text report of the analysis."""
        lines = []
        rarity_label = "rare" if rarity >= 70 else "common" if rarity < 40 else "moderate"
        label_text = {
            "art": "ART ({0})".format(rarity_label),
            "living": "LIVING/BIological ({0})".format(rarity_label),
            "borderline": "BORDERLINE ({0})".format(rarity_label),
        }
        lines.append("  Rarity Score: {0}/100".format(int(round(rarity))))
        lines.append("  Classification: {0}".format(label_text.get(classification, classification)))
        lines.append("  Features:")
        lines.append("    Edge Density: {0:.2f}".format(features.get("edge_density", 0)))
        lines.append("    Symmetry: {0:.2f}".format(features.get("symmetry", 0)))
        lines.append("    Fractal Dim: {0:.2f}".format(features.get("fractal_dim", 0)))
        lines.append("    Texture: {0:.2f}".format(features.get("texture", 0)))
        lines.append("    Golden Ratio: {0:.2f}".format(features.get("golden_ratio", 0)))
        lines.append("    Polynomial Smooth: {0:.2f}".format(features.get("polynomial_smoothness", 0)))
        lines.append("    Curvature Energy: {0:.2f}".format(features.get("curvature_energy", 0)))
        lines.append("    Color Diversity: {0:.2f}".format(features.get("color_diversity", 0)))
        return "\n".join(lines)


class PolyArtCVTest:
    """Main CV test runner."""

    @staticmethod
    def analyze_image(path):
        """Full analysis pipeline for a single image."""
        img = ImageFeatureExtractor.load_image(path)
        features = ImageFeatureExtractor.extract_all(img)
        rarity = RarityScorer.compute_rarity(features)
        classification = RarityScorer.classify(features)
        return {
            "path": path,
            "filename": os.path.basename(path),
            "features": features,
            "rarity": rarity,
            "classification": classification,
            "report": RarityScorer.generate_report(features, rarity, classification),
        }

    @staticmethod
    def batch_analyze(directory, extensions=(".png", ".jpg", ".jpeg")):
        """Analyze all images in a directory."""
        results = []
        for fname in sorted(os.listdir(directory)):
            if any(fname.lower().endswith(ext) for ext in extensions):
                path = os.path.join(directory, fname)
                try:
                    result = PolyArtCVTest.analyze_image(path)
                    results.append(result)
                except Exception as e:
                    results.append({"path": path, "filename": fname, "error": str(e)})
        return results

    @staticmethod
    def generate_synthetic_test():
        """Generate synthetic test images and classify them."""
        tmpdir = tempfile.mkdtemp(prefix="polyart_test_")
        paths = []

        # 1. Golden spiral (art)
        fig, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=100)
        theta = np.linspace(0, 4 * np.pi, 2000)
        a = 0.1
        b = 0.2
        r = a * np.exp(b * theta)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        ax.plot(x, y, color="#1a1a2e", linewidth=1.5)
        ax.set_facecolor("#f0e6d3")
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_aspect("equal")
        ax.axis("off")
        p1 = os.path.join(tmpdir, "golden_spiral.png")
        fig.savefig(p1, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        paths.append(p1)

        # 2. Random noise (living/nature)
        fig, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=100)
        noise = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        ax.imshow(noise)
        ax.axis("off")
        p2 = os.path.join(tmpdir, "random_noise.png")
        fig.savefig(p2, bbox_inches="tight")
        plt.close(fig)
        paths.append(p2)

        # 3. Symmetric mandala (art, high rarity)
        fig, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=100, subplot_kw={"projection": "polar"})
        n_rings = 8
        n_petals = 12
        for ring in range(n_rings):
            r_vals = np.linspace(0.1 + ring * 0.1, 0.2 + ring * 0.1, 200)
            theta_vals = np.linspace(0, 2 * np.pi, 200)
            for petal in range(n_petals):
                offset = petal * 2 * np.pi / n_petals
                th = theta_vals + offset
                r_mod = r_vals * (1 + 0.3 * np.sin(n_petals * th))
                color_val = plt.cm.plasma(ring / n_rings)
                ax.plot(th, r_mod, color=color_val, linewidth=1.0, alpha=0.7)
        ax.set_facecolor("#0d1117")
        ax.axis("off")
        p3 = os.path.join(tmpdir, "symmetric_mandala.png")
        fig.savefig(p3, bbox_inches="tight", facecolor=fig.get_facecolor(), pad_inches=0.1)
        plt.close(fig)
        paths.append(p3)

        # 4. Perlin-like noise (living)
        fig, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=100)
        shape = (128, 128)
        result = np.zeros(shape)
        for scale in [2, 4, 8, 16, 32]:
            small = np.random.randn(scale, scale)
            x_up = np.linspace(0, scale - 1, shape[1])
            y_up = np.linspace(0, scale - 1, shape[0])
            from numpy import interp
            upsampled = np.zeros(shape)
            for i in range(shape[0]):
                for j in range(shape[1]):
                    yi = min(scale - 2, max(0, int(y_up[i])))
                    xi = min(scale - 2, max(0, int(x_up[j])))
                    fy = y_up[i] - yi
                    fx = x_up[j] - xi
                    val = (small[yi, xi] * (1 - fy) * (1 - fx) +
                           small[yi + 1, xi] * fy * (1 - fx) +
                           small[yi, xi + 1] * (1 - fy) * fx +
                           small[yi + 1, xi + 1] * fy * fx)
                    upsampled[i, j] = val
            result += upsampled / scale
        result = ((result - result.min()) / (result.max() - result.min() + 1e-8) * 255).astype(np.uint8)
        colored = np.stack([result, (result * 0.8).clip(0, 255).astype(np.uint8),
                           (result * 0.5).clip(0, 255).astype(np.uint8)], axis=2)
        ax.imshow(colored)
        ax.axis("off")
        p4 = os.path.join(tmpdir, "perlin_noise.png")
        fig.savefig(p4, bbox_inches="tight")
        plt.close(fig)
        paths.append(p4)

        # 5. Grid pattern (art)
        fig, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=100)
        ax.set_facecolor("#ffffff")
        for i in range(21):
            x = i / 20.0
            lw = 2.0 if i % 5 == 0 else 0.5
            color = "#1a1a2e" if i % 5 == 0 else "#cccccc"
            ax.axvline(x, color=color, linewidth=lw)
            ax.axhline(x, color=color, linewidth=lw)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")
        p5 = os.path.join(tmpdir, "grid_pattern.png")
        fig.savefig(p5, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        paths.append(p5)

        # 6. Fractal-like triangle pattern (borderline)
        fig, ax = plt.subplots(1, 1, figsize=(4, 4), dpi=100)
        ax.set_facecolor("#f5f5f5")

        def draw_tri(ax, x, y, size, depth, max_depth):
            if depth >= max_depth or size < 0.005:
                return
            tri_x = [x, x - size / 2, x + size / 2, x]
            tri_y = [y, y + size * 0.866, y + size * 0.866, y]
            intensity = int(255 * (1 - depth / max_depth))
            color_rgb = (intensity / 255.0, (intensity * 0.3) / 255.0, (intensity * 0.6) / 255.0)
            ax.fill(tri_x, tri_y, color=color_rgb, edgecolor="#333333", linewidth=0.3)
            draw_tri(ax, x, y + size * 0.866, size / 2, depth + 1, max_depth)
            draw_tri(ax, x - size / 2, y, size / 2, depth + 1, max_depth)
            draw_tri(ax, x + size / 2, y, size / 2, depth + 1, max_depth)

        draw_tri(ax, 0.5, 0.05, 0.8, 0, 5)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")
        p6 = os.path.join(tmpdir, "fractal_triangles.png")
        fig.savefig(p6, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        paths.append(p6)

        return paths, tmpdir

    @staticmethod
    def run_demo():
        """Run full demo: generate test images, classify, print report."""
        print("=" * 55)
        print("  PolyArt CV Test - Feature-Based Image Classification")
        print("=" * 55)
        print()
        print("Generating synthetic test images...")
        paths, tmpdir = PolyArtCVTest.generate_synthetic_test()
        print("Generated {0} test images in: {1}".format(len(paths), tmpdir))
        print()
        print("Analyzing images...")
        print()
        print("=" * 55)
        print("  PolyArt CV Classification Report")
        print("=" * 55)
        print()

        art_count = 0
        living_count = 0
        borderline_count = 0

        for path in paths:
            result = PolyArtCVTest.analyze_image(path)
            print("Image: {0}".format(result["filename"]))
            print(result["report"])
            print()

            c = result["classification"]
            if c == "art":
                art_count += 1
            elif c == "living":
                living_count += 1
            else:
                borderline_count += 1

        print("=" * 55)
        print("  Summary")
        print("=" * 55)
        print("  Total images analyzed: {0}".format(len(paths)))
        print("  Classified as ART:     {0}".format(art_count))
        print("  Classified as LIVING:  {0}".format(living_count))
        print("  Classified as BORDER:  {0}".format(borderline_count))
        print("=" * 55)
        print()

        json_results = []
        for path in paths:
            result = PolyArtCVTest.analyze_image(path)
            json_results.append({
                "filename": result["filename"],
                "classification": result["classification"],
                "rarity": result["rarity"],
                "features": {k: round(v, 4) for k, v in result["features"].items()},
            })

        report_path = os.path.join(tmpdir, "polyart_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(json_results, f, indent=2)
        print("JSON report saved to: {0}".format(report_path))
        print()

        print("Feature weights used:")
        for feat, w in sorted(RarityScorer.WEIGHTS.items()):
            print("  {0}: {1:.2f}".format(feat, w))
        print()
        print("Classification logic:")
        print("  ART: higher symmetry, golden ratio, smoothness, curvature")
        print("  LIVING: higher fractal dimension, texture, color variation")
        print()
        print("Demo complete.")


if __name__ == "__main__":
    PolyArtCVTest.run_demo()
