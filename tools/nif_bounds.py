#!/usr/bin/env python3
r"""Object bounds (a record's OBND) from a built NIF, the Creation Kit's way (2026-11-16, the blade families restructure):
the extents of every vertex of every BSTriShape in the model's ROOT frame (each shape's transform and its parents' up to the
root applied), rounded outward to whole units (int16). The scabbard and blood shapes count - the CK reads the whole model.

Reference: NordicSkyforgedArmorAndWeapons tools\build-esp.py ground_model_bounds (shield_size.world_points), written after
the Skyforge Steel Shield shipped with 0,0,0 / 0,0,0 bounds (gate row item-object-bounds-not-all-zero). Vertices come from
winding._tris_from_shape, which reads a skinned shape's vertices from its skin partition.

  python -I nif_bounds.py <a.nif> [...]        prints each NIF's bounds
"""
import os, sys, math
import numpy as np
sys.path.insert(0, r"D:\Claude output\4. plans\nordic-double-bit-axe"); import niflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winding


def _xf(n, b):
    _, t, r, s = n.transform(b)
    return np.array(t, np.float64), np.array(r, np.float64).reshape(3, 3), s


def world_points(path):
    n = niflib.Nif(path)
    parent = {}
    for p, ty in enumerate(n.btypes):
        if ty in niflib.NODES:
            for c in n.children(p)[0]:
                if c >= 0: parent.setdefault(c, p)
    out = []
    for b, ty in enumerate(n.btypes):
        if ty != "BSTriShape": continue
        V, _ = winding._tris_from_shape(n, b)
        if not len(V): continue
        cur, R, t = b, np.eye(3), np.zeros(3)
        while cur is not None:
            tl, Rl, sl = _xf(n, cur); R, t = Rl @ R * sl, Rl @ t * sl + tl
            cur = parent.get(cur)
        out.append(V @ R.T + t)
    if not out: raise SystemExit(f"{path}: no shape vertices - cannot compute bounds")
    return np.concatenate(out)


def bounds(path):
    P = world_points(path)
    ob = tuple([int(math.floor(x)) for x in P.min(0)] + [int(math.ceil(x)) for x in P.max(0)])
    if not all(-32768 <= x <= 32767 for x in ob) or not any(ob):
        raise SystemExit(f"{path}: bounds out of range or all zero: {ob}")
    return ob


if __name__ == "__main__":
    for p in sys.argv[1:]: print(bounds(p), p)
