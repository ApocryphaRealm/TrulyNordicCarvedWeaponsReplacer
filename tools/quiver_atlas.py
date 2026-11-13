# The quiver's ARROW ATLAS (2026-11-12): gb_quiver.py moves every arrow's steel and soft parts onto one atlas so each
# arrow is one shape with one texture set (vanilla names one BSTriShape per arrow); this copies the pixels - every
# rectangle in <WORK>\quiver\arrow_atlas_plan.json from the steel or soft map to its place, byte for byte, for the
# albedo, both normal conventions and RMAOS. Unused space is black albedo / flat normal / rough non-metal.
# Proof: each copied rectangle is compared back with its source (0 px may differ); written to arrow_atlas_proof.json.
# Run: python -I quiver_atlas.py [quiver|boltquiver]
import os, sys, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from items import ITEMS, WORK
K = sys.argv[1] if len(sys.argv) > 1 else "quiver"   # 2026-11-13: also "boltquiver" (the bolt atlas, role "bolt")
it = ITEMS[K]; D_ = os.path.join(WORK, K); plan = json.load(open(os.path.join(D_, "arrow_atlas_plan.json")))
SRC = {"steel": it["shapes"]["metal"]["tex"], "soft": it["shapes"]["leather"]["tex"]}
dst = it["shapes"][it.get("atlas_role", "arrow")]["tex"]; os.makedirs(os.path.dirname(dst), exist_ok=True); N = plan["size"]
FILL = {"": (0, 0, 0), "_n": (128, 128, 255), "_n_gl": (128, 128, 255), "_rmaos": (230, 0, 255, 128)}
proof = {"size": N, "rectangles": len(plan["rects"]), "maps": {}}
for suf, fill in FILL.items():
    srcs = {k: Image.open(v + suf + ".png") for k, v in SRC.items()}
    mode = srcs["steel"].mode; assert all(s.mode == mode for s in srcs.values()), {k: s.mode for k, s in srcs.items()}
    if len(fill) != len(mode): fill = tuple(fill[:len(mode)]) if len(mode) < len(fill) else tuple(fill) + (255,) * (len(mode) - len(fill))
    out = Image.new(mode, (N, N), fill)
    for r in plan["rects"]:
        x0, y0, x1, y1 = r["src_box"]; out.paste(srcs[r["src"]].crop((x0, y0, x1, y1)), tuple(r["dst"]))
    out.save(dst + suf + ".png")
    back = np.asarray(Image.open(dst + suf + ".png")); bad = 0
    for r in plan["rects"]:
        x0, y0, x1, y1 = r["src_box"]; dx, dy = r["dst"]
        a = np.asarray(srcs[r["src"]])[y0:y1, x0:x1]; b = back[dy:dy + (y1 - y0), dx:dx + (x1 - x0)]; bad += int(np.any(a != b, axis=-1).sum() if a.ndim == 3 else (a != b).sum())
    proof["maps"][os.path.basename(dst) + suf] = {"mode": mode, "px_differ_from_source": bad}
json.dump(proof, open(os.path.join(D_, "arrow_atlas_proof.json"), "w"), indent=1)
print(json.dumps(proof))
sys.exit(1 if any(v["px_differ_from_source"] for v in proof["maps"].values()) else 0)
