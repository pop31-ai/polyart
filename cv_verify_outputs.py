"""
PolyArt CV Verification for generated outputs.

Uses the canonical feature extractor from polyart_cv_test.py to analyze
generated images (oil-brush demos, painter templates, meta-language demo,
showcases) and produce:
  - cv_output_report.json  (metrics per image)
  - cv_output_gallery.html (browser gallery with metrics)

Usage: python cv_verify_outputs.py
"""

import os
import json
import html
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from polyart_cv_test import ImageFeatureExtractor, RarityScorer
except Exception as e:
    print("[ERROR] Cannot import polyart_cv_test: %s" % e)
    sys.exit(1)

TARGETS = [
    "oil_brush_twin_demo.png",
    "paint_demo_sunset.png",
    "paint_demo_forest.png",
    "paint_demo_winter.png",
    "curves_library_showcase.png",
    "flowers_showcase.png",
    "emotions_showcase.png",
    "states_showcase.png",
    "animals_showcase.png",
    os.path.join("examples", "01_golden_mandala.png"),
    os.path.join("examples", "05_procedural_forest.png"),
    os.path.join("examples", "07_game_rpg.png"),
    os.path.join("examples", "12_polyart_lang.png"),
]

GROUP_LABELS = {
    "oil_brush_twin_demo.png": "Oil brush twin (core demo)",
    "paint_demo_sunset.png": "PainterCanvas template",
    "paint_demo_forest.png": "PainterCanvas template",
    "paint_demo_winter.png": "PainterCanvas template",
    "12_polyart_lang.png": "Meta-language demo",
}


def analyze(path):
    img = ImageFeatureExtractor.load_image(path)
    features = ImageFeatureExtractor.extract_all(img)
    rarity = RarityScorer.compute_rarity(features)
    cls = RarityScorer.classify(features)
    return {
        "file": path,
        "filename": os.path.basename(path),
        "rarity": rarity,
        "class": cls,
        "features": {k: round(v, 4) for k, v in features.items()},
    }


def build_gallery(results):
    cards = []
    for r in results:
        if "error" in r:
            cards.append('<div class="card"><h3>{0}</h3><p class="err">{1}</p></div>'
                         .format(html.escape(r["filename"]), html.escape(r["error"])))
            continue
        label = GROUP_LABELS.get(r["filename"], "PolyArt output")
        feats = "".join(
            "<tr><td>{0}</td><td>{1:.3f}</td></tr>".format(k, v)
            for k, v in r["features"].items()
        )
        cls_class = {"art": "art", "living": "living", "borderline": "border"}[r["class"]]
        cards.append(
            '<div class="card">'
            '<img src="{0}" alt="{1}">'
            '<h3>{1} <span class="tag">{2}</span></h3>'
            '<p class="sub">{3}</p>'
            '<div class="score">Rarity <b>{4:.0f}</b>/100</div>'
            '<table>{5}</table>'
            "</div>".format(
                html.escape(r["file"]),
                html.escape(r["filename"]),
                r["class"].upper(),
                html.escape(label),
                r["rarity"],
                feats,
            )
        )
    page = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>PolyArt CV verification</title>
<style>
  body {{ font-family: sans-serif; margin: 24px; background: #101018; color: #ddd; }}
  h1 {{ color: #e8c86a; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 18px; }}
  .card {{ background: #1b1b28; border: 1px solid #333; border-radius: 10px; padding: 12px; }}
  .card img {{ width: 100%; border-radius: 6px; background: #000; }}
  h3 {{ margin: 8px 0 2px; font-size: 15px; }}
  .tag {{ font-size: 11px; padding: 2px 8px; border-radius: 20px; vertical-align: 2px; }}
  .art {{ background: #2a6a3a; }} .living {{ background: #6a3a2a; }} .border {{ background: #6a6a2a; }}
  .sub {{ color: #999; font-size: 12px; margin: 0 0 6px; }}
  .score {{ color: #e8c86a; margin-bottom: 6px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  td {{ padding: 2px 4px; border-bottom: 1px solid #26263a; }}
  td:nth-child(2) {{ text-align: right; color: #9bd4ff; }}
</style>
</head>
<body>
<h1>PolyArt — CV verification gallery</h1>
<p>{0} images · {1} ART · {2} LIVING · {3} BORDERLINE · avg rarity {4:.0f}/100</p>
<div class="grid">{5}</div>
</body>
</html>""".format(
        len(results),
        sum(1 for r in results if r.get("class") == "art"),
        sum(1 for r in results if r.get("class") == "living"),
        sum(1 for r in results if r.get("class") == "borderline"),
        sum(r.get("rarity", 0) for r in results if "error" not in r)
        / max(1, sum(1 for r in results if "error" not in r)),
        "".join(cards),
    )
    with open("cv_output_gallery.html", "w", encoding="utf-8") as f:
        f.write(page)


def main():
    print("=" * 60)
    print("  PolyArt CV Verification of generated outputs")
    print("=" * 60)
    results = []
    for path in TARGETS:
        if not os.path.exists(path):
            print("[SKIP] %s (missing)" % path)
            results.append({"file": path, "filename": os.path.basename(path),
                            "error": "missing"})
            continue
        try:
            r = analyze(path)
            results.append(r)
            print("[CV] %-34s -> %-9s rarity=%5.1f"
                  % (r["filename"], r["class"].upper(), r["rarity"]))
        except Exception as e:
            print("[ERR] %s -> %s" % (path, str(e)))
            results.append({"file": path, "filename": os.path.basename(path),
                            "error": str(e)})

    valid = [r for r in results if "error" not in r]
    art = sum(1 for r in valid if r["class"] == "art")
    living = sum(1 for r in valid if r["class"] == "living")
    border = sum(1 for r in valid if r["class"] == "borderline")
    avg = sum(r["rarity"] for r in valid) / max(1, len(valid))
    print("-" * 60)
    print("  TOTAL %d | ART %d | LIVING %d | BORDER %d | avg rarity %.1f"
          % (len(valid), art, living, border, avg))
    print("=" * 60)

    with open("cv_output_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    build_gallery(results)
    print("[OK] cv_output_report.json saved")
    print("[OK] cv_output_gallery.html saved")


if __name__ == "__main__":
    main()
