import sys
import json
import traceback

try:
    from polyart_cv_test import ImageFeatureExtractor, RarityScorer, PolyArtCVTest
except Exception as e:
    print("[ERROR] Cannot import polyart_cv_test: " + str(e))
    traceback.print_exc()
    sys.exit(1)

targets = [
    "curves_library_showcase.png",
    "flowers_showcase.png",
    "emotions_showcase.png",
    "states_showcase.png",
    "animals_showcase.png",
]

results = []
for name in targets:
    try:
        feat = ImageFeatureExtractor.load_image(name)
        all_feat = ImageFeatureExtractor.extract_all(feat)
        rarity = RarityScorer.compute_rarity(all_feat)
        cls = RarityScorer.classify(all_feat)
        results.append({
            "file": name,
            "rarity": rarity,
            "class": cls,
        })
        print("[CV] %s -> %s rarity=%.0f" % (name, cls.upper(), rarity))
    except Exception as e:
        print("[ERR] %s -> %s" % (name, str(e)))
        traceback.print_exc()
        results.append({"file": name, "error": str(e)})

with open("cv_verification_new.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n[OK] Saved cv_verification_new.json")
print("[DONE] CV verification complete.")
