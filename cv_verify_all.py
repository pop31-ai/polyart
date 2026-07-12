import sys, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, r"C:\Users\e\Desktop\6756756756756756")

def load_img(path):
    img = plt.imread(path)
    if img.dtype in (np.float32, np.float64):
        img = (img * 255).clip(0, 255).astype(np.uint8)
    return img

def edge_density(img):
    gray = np.mean(img[:,:,:3], axis=2) if len(img.shape)==3 else img.astype(np.float64)
    gy, gx = np.gradient(gray)
    return float(np.mean(np.sqrt(gx**2+gy**2))/(np.sqrt(2)*255))

def symmetry_score(img):
    gray = np.mean(img[:,:,:3], axis=2) if len(img.shape)==3 else img.astype(np.float64)
    h, w = gray.shape; mid = w//2
    l, r = gray[:,:mid], np.fliplr(gray[:,w-mid:])
    mh, mw = min(l.shape[0],r.shape[0]), min(l.shape[1],r.shape[1])
    return float(max(0, min(1, 1 - np.mean(np.abs(l[:mh,:mw]-r[:mh,:mw]))/255)))

def fractal_dim(img):
    gray = np.mean(img[:,:,:3], axis=2) if len(img.shape)==3 else img.astype(np.float64)
    vals = gray/255.0
    sizes = [2,4,8,16,32]
    counts = []
    for s in sizes:
        h, w = vals.shape
        th, tw = h//s, w//s
        if th < 1 or tw < 1: continue
        block = vals[:th*s, :tw*s].reshape(th, s, tw, s)
        thresh = np.mean(block, axis=(1,3))
        counts.append(float(np.sum(thresh > 0.1)))
    if len(counts) < 2: return 1.5
    log_n = np.log([c for c in counts if c>0])
    log_s = np.log([sizes[i] for i in range(len(counts)) if counts[i]>0])
    if len(log_n) < 2: return 1.5
    return float(abs(np.polyfit(log_s, log_n, 1)[0]))

def color_diversity(img):
    if len(img.shape)<3: return 0.1
    pixels = img[:,:,:3].reshape(-1,3).astype(np.float64)
    step = max(1, len(pixels)//5000)
    sample = pixels[::step]
    unique_ratio = len(np.unique(sample, axis=0))/len(sample)
    return float(min(1, unique_ratio*5))

def golden_ratio_score(img):
    h, w = img.shape[:2]
    ratio = w/h
    phi = 1.618033988749895
    return float(max(0, 1 - abs(ratio - phi)/phi))

def texture_score(img):
    gray = np.mean(img[:,:,:3], axis=2) if len(img.shape)==3 else img.astype(np.float64)
    gy, gx = np.gradient(gray)
    angle = np.arctan2(gy, gx)
    hist, _ = np.histogram(angle.flatten(), bins=36, range=(-np.pi, np.pi))
    hist = hist.astype(float)/max(1, hist.sum())
    entropy = -np.sum(hist[hist>0]*np.log2(hist[hist>0]))
    return float(min(1, entropy/5.0))

def polynomial_smoothness(img):
    gray = np.mean(img[:,:,:3], axis=2) if len(img.shape)==3 else img.astype(np.float64)
    h, w = gray.shape
    row = gray[h//2, :]
    x = np.linspace(-1, 1, len(row))
    try:
        c = np.polyfit(x, row, 10)
        smooth = np.mean(np.abs(c[:5]))/max(1, np.mean(np.abs(c[5:])))
        return float(min(1, smooth/10))
    except: return 0.3

def curvature_energy(img):
    gray = np.mean(img[:,:,:3], axis=2) if len(img.shape)==3 else img.astype(np.float64)
    gy, gx = np.gradient(gray)
    gyy, _ = np.gradient(gy)
    _, gxx = np.gradient(gx)
    energy = np.mean(gxx**2 + gyy**2)
    return float(min(1, energy/10000))

def classify(features):
    sym = features.get("symmetry", 0.5)
    golden = features.get("golden_ratio", 0.5)
    poly = features.get("polynomial_smoothness", 0.5)
    curvature = features.get("curvature_energy", 0.5)
    fractal = features.get("fractal_dim", 1.5)
    texture = features.get("texture", 0.3)
    color_div = features.get("color_diversity", 0.3)
    art_score = sym*2.5 + golden*2.0 + poly*1.5 + curvature*1.5
    living_score = (fractal-1.0)*3.0 + texture*2.0 + color_div*1.5
    diff = art_score - living_score
    if diff > 0.3: return "ART"
    elif diff < -0.3: return "LIVING"
    return "BORDERLINE"

def compute_rarity(f):
    sym = f.get("symmetry",0.5); golden = f.get("golden_ratio",0.5)
    poly = f.get("polynomial_smoothness",0.5); edge = f.get("edge_density",0.3)
    texture = f.get("texture",0.3); color_div = f.get("color_diversity",0.3)
    curvature = f.get("curvature_energy",0.5); fractal = f.get("fractal_dim",1.5)
    W = {"edge_density":0.15,"symmetry":0.12,"fractal_dim":0.18,"texture":0.10,
         "color_diversity":0.12,"golden_ratio":0.08,"polynomial_smoothness":0.10,"curvature_energy":0.15}
    weighted = (W["edge_density"]*(1-edge) + W["symmetry"]*sym + W["fractal_dim"]*(fractal-1) +
                W["texture"]*texture + W["color_diversity"]*color_div + W["golden_ratio"]*golden +
                W["polynomial_smoothness"]*poly + W["curvature_energy"]*curvature)
    art_bonus = sym*0.3 + golden*0.3 + poly*0.2 + curvature*0.2
    return float(np.clip(weighted*60 + art_bonus*40, 0, 100))

PNG_DIR = r"C:\Users\e\Desktop\6756756756756756"
files = [f for f in sorted(os.listdir(PNG_DIR)) if f.endswith(".png")]

results = []
for f in files:
    path = os.path.join(PNG_DIR, f)
    try:
        img = load_img(path)
        feat = {"edge_density":edge_density(img), "symmetry":symmetry_score(img),
                "fractal_dim":fractal_dim(img), "texture":texture_score(img),
                "color_diversity":color_diversity(img), "golden_ratio":golden_ratio_score(img),
                "polynomial_smoothness":polynomial_smoothness(img), "curvature_energy":curvature_energy(img)}
        rarity = compute_rarity(feat)
        cls = classify(feat)
        results.append({"file":f, "rarity":rarity, "classification":cls, "features":{k:round(v,3) for k,v in feat.items()}})
        print(f"  [OK] {f:<40} {rarity:>4}/100  {cls}")
    except Exception as e:
        results.append({"file":f, "error":str(e)})
        print(f"  [ERR] {f:<40} {str(e)[:40]}")

art = sum(1 for r in results if r.get("classification")=="ART")
living = sum(1 for r in results if r.get("classification")=="LIVING")
border = sum(1 for r in results if r.get("classification")=="BORDERLINE")
errs = sum(1 for r in results if "error" in r)
valid = [r for r in results if "error" not in r]
avg = sum(r["rarity"] for r in valid)/max(1,len(valid))

print()
print("="*60)
print(f"  TOTAL: {len(results)} | ART: {art} | LIVING: {living} | BORDERLINE: {border} | ERR: {errs}")
print(f"  Average rarity: {avg:.1f}/100")
print("="*60)

with open(os.path.join(PNG_DIR, "cv_verification_report.json"), "w") as fp:
    json.dump(results, fp, indent=2, default=str)
print("Report saved: cv_verification_report.json")
