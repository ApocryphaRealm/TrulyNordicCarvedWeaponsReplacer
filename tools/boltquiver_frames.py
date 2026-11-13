# The bolt quiver's frames (2026-11-13), read from vanilla Dawnguard's steelbolt.nif / boltprojectile.nif with niflib, for
# gb_boltquiver.py: for every vanilla shape our geometry goes into, the 4x4 matrix that takes a point of the DESIGN frame
# to that shape's own local frame (the shape keeps vanilla's transform and every parent node's - nothing in vanilla's
# tree moves). Written to <WORK>\boltquiver\frames.json.
#
# Design frames (set2\work_xbow_NOTES.md): the quiver mouth up (foot y 0, mouth y 16.2, the bolt ends to y 22.6), front +z;
# the bolt as vanilla's flight bolt (tip at the origin, nock at y -21).
# Vanilla (world = the root's frame, the root's own 180-degree turn included): the case lies along x, mouth toward -x
# (x -4.18..12.57), width along y (+-2.95), thickness along z (-5.14..-0.86, centre -3.0). The skeleton's QUIVER /
# BOLTDefault node (XPMSSE) points its +z out of the back, so +z is the side that shows - the design's front (+z) goes to
# +z. Case centre on vanilla's: x = 12.3 - y. A proper rotation (no mirror): (x, y, z) -> (12.3 - y, x, z - 3.0).
# The loose / nocked bolt Arrow:0 is vanilla's flight mesh under the Arrow node (tip at world x 12, centre y 0, z -2.5):
# (x, y, z) -> (y + 12, -x, z - 2.5) - the same local geometry as the flight shape.
# Run: python -I boltquiver_frames.py
import os, sys, json
import numpy as np
sys.path.insert(0, r"D:\Claude output\4. plans\nordic-double-bit-axe"); import niflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from items import ITEMS, WORK
import winding
it = ITEMS["boltquiver"]; OUT = os.path.join(WORK, "boltquiver"); os.makedirs(OUT, exist_ok=True)

def M4(R, t): m = np.eye(4); m[:3, :3] = R; m[:3, 3] = t; return m
D_QUIVER = M4(np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]], float), [12.3, 0.0, -3.0])
D_BOLT = M4(np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]], float), [12.0, 0.0, -2.5])
D_FLIGHT = np.eye(4)

def chains(n):
    """world matrix of every node and shape (a shape's own scale taken as 1: the build writes 1.0)"""
    out = {}
    def walk(b, W):
        t = n.btypes[b]
        if t in niflib.NODES or t == "BSTriShape":
            _, tl, rl, sl = n.transform(b); L = M4(np.array(rl, float).reshape(3, 3) * (sl if t != "BSTriShape" else 1.0), tl)
            Wb = W @ L; out[n.name(b)] = (b, Wb)
            if t in niflib.NODES:
                for k in n.children(b)[0]:
                    if k >= 0: walk(k, Wb)
    walk(n.roots[0], np.eye(4)); return out

q = niflib.Nif(it["van_dir"] + "\\" + it["third"]); f = niflib.Nif(it["van_dir"] + "\\" + it["flight"])
cq, cf = chains(q), chains(f)
roles = {"metal": ("ArrowQuiver:1", D_QUIVER), "leather": ("ArrowQuiver:1", D_QUIVER), "bolt": ("Arrow:0", D_BOLT)}
for k in range(1, 5): roles[f"Arrow{k}"] = (f"Arrow{k}", D_QUIVER)
fr = {"design_to_local": {}, "slots_design_xz": {}, "check": {}}
for role, (shape, D) in roles.items():
    b, W = cq[shape]; fr["design_to_local"][role] = (np.linalg.inv(W) @ D).tolist()
for role, (shape, D) in {"flight": ("SteelBoltFlight:0", D_FLIGHT)}.items():
    b, W = cf[shape]; fr["design_to_local"][role] = (np.linalg.inv(W) @ D).tolist()
# vanilla's in-case bolts: their centre across the case, in the design frame (x, z), for the pairing
Dinv = np.linalg.inv(D_QUIVER)
for k in range(1, 5):
    b, W = cq[f"Arrow{k}"]; V, _ = winding._tris_from_shape(q, b); Wv = (W[:3, :3] @ V.T).T + W[:3, 3]
    c = (Wv.min(0) + Wv.max(0)) / 2; d = Dinv[:3, :3] @ c + Dinv[:3, 3]; fr["slots_design_xz"][f"Arrow{k}"] = [float(d[0]), float(d[2])]
# check: vanilla's Arrow:0 local mesh is the flight mesh (so the loose bolt's mapping is vanilla's own)
b0 = cq["Arrow:0"][0]; bf = cf["SteelBoltFlight:0"][0]
V0, _ = winding._tris_from_shape(q, b0); Vf, _ = winding._tris_from_shape(f, bf)
fr["check"]["arrow0_local_equals_flight_local_maxdiff"] = float(np.abs(np.sort(V0, 0) - np.sort(Vf, 0)).max()) if V0.shape == Vf.shape else "shape differs"
for nm in ("Arrow:0", "ArrowQuiver:1", "SteelBoltFlight:0"):
    pass
for role in fr["design_to_local"]: assert abs(np.linalg.det(np.array(fr["design_to_local"][role])[:3, :3]) - 1) < 1e-3, role
json.dump(fr, open(os.path.join(OUT, "frames.json"), "w"), indent=1); print(json.dumps(fr["slots_design_xz"]), fr["check"])
