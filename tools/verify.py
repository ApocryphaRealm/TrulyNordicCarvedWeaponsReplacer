# Read-back of every built NIF (niflib, no Blender): each shape's shader block type, flags, TruePBR bit and texture set;
# every texture path of ours must resolve to a file in the staged data; a vanilla path is listed (it is the game's).
# Also checks every block reference points inside the file. Exit 1 on any failure.
# Run: python -I verify.py [stage dir]
import os, sys, struct
sys.path.insert(0, r"D:\Claude output\4. plans\nordic-double-bit-axe"); import niflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from items import WORK, TEX_REL
import winding
STAGE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, "stage")
bad = 0; n_nif = 0; WIND = []
data_roots = [os.path.join(STAGE, d) for d in os.listdir(STAGE) if os.path.isdir(os.path.join(STAGE, d))] + [STAGE]
def exists_any(rel): return any(os.path.isfile(os.path.join(r, rel)) for r in data_roots)
for dp, _, fs in os.walk(STAGE):
    for f in fs:
        if not f.lower().endswith(".nif"): continue
        p = os.path.join(dp, f); n = niflib.Nif(p); n_nif += 1; print("==", os.path.relpath(p, STAGE)); our_shapes = set()
        for b, t in enumerate(n.btypes):
            if t != "BSTriShape": continue
            o = n.av_end(b, 0, [], []); sk, sh, al = struct.unpack_from("<3i", n.blocks[b], o + 16)
            for r in (sk, sh, al):
                if r >= len(n.blocks): print("   BAD REF", r); bad += 1
            if n.btypes[sh] != "BSLightingShaderProperty": print(f"   {n.name(b)}: {n.btypes[sh]} (vanilla shader kept)"); continue
            blk = n.blocks[sh]; f1, f2 = struct.unpack_from("<II", blk, n.net_end(sh, 4, [], []))
            ts = n.i32(sh, n.ref_offsets(sh)[0][-1]); tb = n.blocks[ts]; k = struct.unpack_from("<I", tb, 0)[0]; q = 4; paths = []
            for _ in range(k):
                L = struct.unpack_from("<I", tb, q)[0]; paths.append(tb[q + 4:q + 4 + L].decode("latin-1")); q += 4 + L
            typ = struct.unpack_from("<I", blk, 0)[0]; pbr = bool(f2 & 0x00800000)
            # ours = under TEX_REL (1.1.0 renamed the folder; until 2026-11-12 this still matched the old
            # 'textures\pbr\apocryphatest' prefix, so no shape of ours had its shader and slots checked since then)
            ours = [x for x in paths if x.lower().startswith(TEX_REL.lower() + "\\")]
            miss = [x for x in ours if not exists_any(x)]
            line = f"   {n.name(b)}: type {typ} flags {f1:08x} {f2:08x} TruePBR {pbr} skin {n.btypes[sk] if sk >= 0 else '-'}"
            # a skinned shape whose shader lacks SLSF1 Skinned (0x2) and vice versa draws nothing (2026-11-11, the invisible bow)
            if (sk >= 0) != bool(f1 & 0x2): line += "  SKINNED FLAG MISMATCH"; bad += 1
            if ours:
                if typ != 0 or not pbr or [i for i, x in enumerate(paths) if x] != [0, 1, 5]: line += "  BAD SHADER/SLOTS"; bad += 1
                line += f"  slots 0/1/5 {'all present' if not miss else 'MISSING ' + ', '.join(miss)}"; bad += len(miss)
            else: line += "  vanilla textures: " + ", ".join(x for x in paths if x)[:120]
            if ours or "blood" in n.name(b).lower(): our_shapes.add(n.name(b))
            print(line)
        # face direction (winding.py): no edge wound against its neighbour, no surface facing in - our shapes only
        # (a shape kept from vanilla, e.g. the war axe's belt ring, is listed but not ours to fail)
        rows, faults = winding.check_nif(n, ours=lambda nm: nm in our_shapes or "blood" in nm.lower())
        for r in rows:
            print(f"   winding {r['shape']}: {r['faces']} faces, {r['surfaces']} surfaces, edges against a neighbour {r['edges_against_neighbour']}, "
                  f"surfaces facing in {r['surfaces_facing_in']} ({r['faces_facing_in']} faces){'' if r['ours'] else ' [vanilla shape]'}{'  WINDING FAULT' if r['fault'] else ''}")
            WIND.append(dict(nif=os.path.relpath(p, STAGE), **r))
        bad += faults
# the quiver / arrow NIFs (2026-11-12): vanilla's structure kept exactly - every node and shape name in the same parent
# tree, the extra data (BSX, BSInvMarker, Prn), the alpha properties and the tracer's effect shaders / controller
# blocks byte for byte; only our geometry, shaders and texture sets differ; each arrow ONE shape on the arrow atlas
from items import ITEMS, VAN
def tree(n):
    out = []
    def walk(b, path):
        t = n.btypes[b]; nm = n.name(b) if niflib.has_net(t) else None; here = f"{path}/{t}:{nm}"; out.append(here)
        if t in niflib.NODES:
            kids, _ = n.children(b)
            for k in kids:
                if k >= 0: walk(k, here)
    walk(n.roots[0], ""); return out
KEEP = {"BSXFlags", "BSInvMarker", "NiStringExtraData", "NiAlphaProperty", "BSEffectShaderProperty", "NiTransformController",
        "NiTransformInterpolator", "NiTransformData", "bhkCollisionObject"}
if "quiver" in ITEMS and os.path.isdir(os.path.join(STAGE, "quiver")):
    qd = os.path.join(STAGE, "quiver", r"meshes\TrulyNordic\quiver")
    for ours_f, van_f, extra in (("quiver.nif", ITEMS["quiver"]["third"], {"/BSFadeNode:Arrow/NiNode:ArrowQuiver/BSTriShape:TN_quiver_leather"}),
                                 ("arrowflight.nif", ITEMS["quiver"]["flight"], set())):
        a, v = niflib.Nif(os.path.join(qd, ours_f)), niflib.Nif(os.path.join(VAN, van_f)); ta, tv = tree(a), tree(v)
        miss = [x for x in tv if x not in ta]; more = [x for x in ta if x not in tv and x not in extra]
        kv = [(t, bytes(v.blocks[i])) for i, t in enumerate(v.btypes) if t in KEEP and t != "bhkCollisionObject"]
        ka = [(t, bytes(a.blocks[i])) for i, t in enumerate(a.btypes) if t in KEEP and t != "bhkCollisionObject"]
        same = sorted(kv) == sorted(ka)
        line = f"== structure {ours_f} vs vanilla {van_f}: {len(tv)} vanilla nodes/shapes, missing {miss or 0}, added {more or 0} (allowed: {sorted(extra) or 'none'}); kept blocks {len(kv)} {'byte for byte' if same else 'DIFFER'}"
        if miss or more or not same: line += "  STRUCTURE FAULT"; bad += 1
        print(line)
    n = niflib.Nif(os.path.join(qd, "quiver.nif"))
    for b, t in enumerate(n.btypes):
        if t == "BSTriShape" and n.name(b).startswith("Arrow") and n.name(b) != "ArrowQuiver:0":
            sh = struct.unpack_from("<i", n.blocks[b], n.av_end(b, 0, [], []) + 20)[0]; ts = n.i32(sh, n.ref_offsets(sh)[0][-1]); tb = bytes(n.blocks[ts])
            ok = b"tn_quiver_arrow.dds" in tb
            print(f"   {n.name(b)}: one shape, texture set {'tn_quiver_arrow' if ok else 'NOT THE ARROW ATLAS'}"); bad += 0 if ok else 1
import json; json.dump(WIND, open(os.path.join(STAGE, "..", "winding_report.json") if os.path.basename(STAGE) == "stage" else os.path.join(os.environ.get("TEMP", "."), "tncw_winding_report.json"), "w"), indent=1)
print(f"RESULT {n_nif} NIFs:", "PASS" if bad == 0 else f"FAIL {bad}")
sys.exit(1 if bad else 0)
