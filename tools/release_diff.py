#!/usr/bin/env python3
r"""What changed between two releases of the package, per shipped file (2026-11-12, for the 1.1.1 posting decision).

Every file of NEW is matched to the same relative path in OLD and hashed (SHA-256). A NIF that differs is opened in
Blender (PyNifly) on both sides and classed per shape:
  geometry      the vertex positions or the triangle list (corner positions + UVs) changed;
  normals only  positions, triangles and UVs equal, the vertex normals (and so the vertex count, split at seams) differ;
  paths only    the texture-set strings differ and nothing else (niflib block compare);
A DDS / plugin / other file is identical or changed. Writes <out>.json and <out>.md.
Usage: python tools/release_diff.py <OLD release folder> <NEW release folder> --out <path without extension>
"""
import os, sys, json, hashlib, argparse, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
BL = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
BLENDER_PART = r'''
import bpy, sys, json, addon_utils
from collections import Counter
addon_utils.enable("io_scene_nifly", default_set=True)
def geo(p):
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    bpy.ops.import_scene.pynifly(filepath=p); out = {}
    for o in [o for o in bpy.data.objects if o.type == "MESH"]:
        me = o.data; M = o.matrix_world; uv = me.uv_layers[0].data if me.uv_layers else None
        P = [tuple(round(c, 4) for c in (M @ v.co)) for v in me.vertices]
        T = Counter(); N = Counter()
        cn = me.corner_normals
        for q in me.polygons:
            T[tuple(sorted((P[v], tuple(round(c, 4) for c in uv[l].uv) if uv else ()) for v, l in zip(q.vertices, q.loop_indices)))] += 1
            for v, l in zip(q.vertices, q.loop_indices): N[(P[v], tuple(round(c, 2) for c in cn[l].vector))] += 1
        out[o.name.split(".")[0]] = (set(P), T, N, len(me.vertices))
    return out
res = {}
for pair in json.load(open(sys.argv[sys.argv.index("--") + 1])):
    a, b, key = pair; A, B = geo(a), geo(b); r = {}
    for n in sorted(set(A) | set(B)):
        if n not in A or n not in B: r[n] = "shape added/removed"; continue
        if A[n][0] != B[n][0] or A[n][1] != B[n][1]: r[n] = "geometry"
        elif A[n][2] != B[n][2]: r[n] = "normals only"
        else: r[n] = "same"
    res[key] = r
json.dump(res, open(sys.argv[sys.argv.index("--") + 2], "w"), indent=1)
'''
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("old"); ap.add_argument("new"); ap.add_argument("--out", required=True); a = ap.parse_args()
    rows = {}; nif_pairs = []
    for dp, _, fs in os.walk(a.new):
        for f in fs:
            pn = os.path.join(dp, f); rel = os.path.relpath(pn, a.new); po = os.path.join(a.old, rel)
            if not os.path.isfile(po): rows[rel] = "added"; continue
            if sha(po) == sha(pn): rows[rel] = "identical"; continue
            if f.lower().endswith(".nif"): rows[rel] = "nif changed"; nif_pairs.append([po, pn, rel])
            else: rows[rel] = "changed"
    for dp, _, fs in os.walk(a.old):
        for f in fs:
            rel = os.path.relpath(os.path.join(dp, f), a.old)
            if not os.path.isfile(os.path.join(a.new, rel)): rows[rel] = "removed"
    # one Blender run per unique changed NIF (by hash pair)
    uniq = {}
    for po, pn, rel in nif_pairs: uniq.setdefault((sha(po), sha(pn)), [po, pn, rel])
    tmp = tempfile.mkdtemp(); jp = os.path.join(tmp, "pairs.json"); op = os.path.join(tmp, "out.json"); sp = os.path.join(tmp, "geo.py")
    json.dump(list(uniq.values()), open(jp, "w")); open(sp, "w").write(BLENDER_PART)
    if uniq: subprocess.run([BL, "--background", "--factory-startup", "--python-exit-code", "1", "--python", sp, "--", jp, op], capture_output=True, text=True, check=True)
    G = json.load(open(op)) if uniq else {}
    byhash = {k: G[v[2]] for k, v in uniq.items()}
    for po, pn, rel in nif_pairs:
        shapes = byhash[(sha(po), sha(pn))]; kinds = set(shapes.values()) - {"same"}
        rows[rel] = {"class": "geometry" if "geometry" in kinds or "shape added/removed" in kinds else ("normals only" if kinds else "texture paths / blocks only"), "shapes": shapes}
    json.dump(rows, open(a.out + ".json", "w"), indent=1)
    L = [f"# Release diff\n\nOLD `{a.old}`\n\nNEW `{a.new}`\n"]
    for cls in ("geometry", "normals only", "texture paths / blocks only"):
        L.append(f"\n## NIFs - {cls}\n")
        for rel, v in sorted(rows.items()):
            if isinstance(v, dict) and v["class"] == cls: L.append(f"- `{rel}`: " + ", ".join(f"{s} {k}" for s, k in v["shapes"].items() if k != "same"))
    L.append("\n## Other changed files\n")
    for rel, v in sorted(rows.items()):
        if v in ("changed", "added", "removed"): L.append(f"- `{rel}`: {v}")
    n_id = sum(1 for v in rows.values() if v == "identical"); L.append(f"\nIdentical files: {n_id} of {len(rows)}\n")
    open(a.out + ".md", "w", encoding="utf-8").write("\n".join(L)); print("\n".join(L))
if __name__ == "__main__":
    main()
