import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, r"C:\Users\e\Desktop\6756756756756756")
from cv_verify_all import load_img, edge_density, symmetry_score, fractal_dim, color_diversity, golden_ratio_score, texture_score, polynomial_smoothness, curvature_energy, compute_rarity, classify

img = load_img(r"C:\Users\e\Desktop\6756756756756756\emperor_mathematicus.png")
feat = {"edge_density":edge_density(img), "symmetry":symmetry_score(img), "fractal_dim":fractal_dim(img),
        "texture":texture_score(img), "color_diversity":color_diversity(img), "golden_ratio":golden_ratio_score(img),
        "polynomial_smoothness":polynomial_smoothness(img), "curvature_energy":curvature_energy(img)}
rarity = compute_rarity(feat)
cls = classify(feat)
print(f"Rarity: {rarity:.1f}/100  Class: {cls}")
for k,v in feat.items(): print(f"  {k}: {v:.3f}")
