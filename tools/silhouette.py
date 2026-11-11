# Silhouette check of the decimation: each item's original and decimated shapes rasterised front (x,y) and side (z,y)
# at 10 px per unit; reports the pixels that differ as a share of the silhouette, and writes one overlay sheet
# (white = both, red = original only, cyan = decimated only).  Run: python -I silhouette.py
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from items import ITEMS, WORK
S = 10.0
def mask(item, kind, axes, lo, size):
    im = Image.new("L", size, 0); d = ImageDraw.Draw(im)
    for role in ITEMS[item]["shapes"]:
        z = np.load(os.path.join(WORK, item, f"{kind}_{role}.npz")); V, F = z["V"], z["F"]
        P = (V[:, axes] - lo) * S; P[:, 1] = size[1] - P[:, 1]
        for f in F: d.polygon([tuple(P[i]) for i in f], fill=255)
    return np.asarray(im) > 0
rep = {}; tiles = []
for item in ITEMS:
    allV = np.concatenate([np.load(os.path.join(WORK, item, f"orig_{r}.npz"))["V"] for r in ITEMS[item]["shapes"]])
    row = []
    for name, axes in (("front", [0, 1]), ("side", [2, 1])):
        lo = allV[:, axes].min(0) - 1; hi = allV[:, axes].max(0) + 1; size = tuple(int(x) for x in np.ceil((hi - lo) * S))
        a, b = mask(item, "orig", axes, lo, size), mask(item, "dec", axes, lo, size)
        diff = int((a ^ b).sum()); rep.setdefault(item, {})[name] = {"silhouette_px": int(a.sum()), "differing_px": diff, "share": round(diff / max(1, a.sum()), 5)}
        rgb = np.zeros(a.shape + (3,), np.uint8); rgb[a & b] = 255; rgb[a & ~b] = (255, 40, 40); rgb[~a & b] = (40, 230, 255)
        row.append(Image.fromarray(rgb))
    tiles.append((item, row))
H = 520; out = []
for item, row in tiles:
    sc = H / max(r.size[1] for r in row); ims = [r.resize((max(1, int(r.size[0] * sc)), H), Image.NEAREST) for r in row]
    t = Image.new("RGB", (sum(i.size[0] for i in ims) + 30, H + 24), (25, 25, 25)); x = 5
    for i in ims: t.paste(i, (x, 22)); x += i.size[0] + 10
    ImageDraw.Draw(t).text((5, 4), f"{item}: front / side  diff {rep[item]['front']['share']:.4%} / {rep[item]['side']['share']:.4%}", fill=(230, 230, 230)); out.append(t)
W = sum(t.size[0] for t in out) + 10 * len(out); sheet = Image.new("RGB", (W, H + 24), (10, 10, 10)); x = 0
for t in out: sheet.paste(t, (x, 0)); x += t.size[0] + 10
sheet.save(os.path.join(WORK, "silhouette_overlay.png")); json.dump(rep, open(os.path.join(WORK, "silhouette.json"), "w"), indent=1)
for k, v in rep.items(): print(k, v["front"]["share"], v["side"]["share"])
