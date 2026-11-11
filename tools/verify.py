# Read-back of every built NIF (niflib, no Blender): each shape's shader block type, flags, TruePBR bit and texture set;
# every texture path of ours must resolve to a file in the staged data; a vanilla path is listed (it is the game's).
# Also checks every block reference points inside the file. Exit 1 on any failure.
# Run: python -I verify.py [stage dir]
import os, sys, struct
sys.path.insert(0, r"D:\Claude output\4. plans\nordic-double-bit-axe"); import niflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from items import WORK
STAGE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, "stage")
bad = 0; n_nif = 0
data_roots = [os.path.join(STAGE, d) for d in os.listdir(STAGE) if os.path.isdir(os.path.join(STAGE, d))] + [STAGE]
def exists_any(rel): return any(os.path.isfile(os.path.join(r, rel)) for r in data_roots)
for dp, _, fs in os.walk(STAGE):
    for f in fs:
        if not f.lower().endswith(".nif"): continue
        p = os.path.join(dp, f); n = niflib.Nif(p); n_nif += 1; print("==", os.path.relpath(p, STAGE))
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
            ours = [x for x in paths if x.lower().startswith("textures\\pbr\\apocryphatest")]
            miss = [x for x in ours if not exists_any(x)]
            line = f"   {n.name(b)}: type {typ} flags {f1:08x} {f2:08x} TruePBR {pbr} skin {n.btypes[sk] if sk >= 0 else '-'}"
            # a skinned shape whose shader lacks SLSF1 Skinned (0x2) and vice versa draws nothing (2026-11-11, the invisible bow)
            if (sk >= 0) != bool(f1 & 0x2): line += "  SKINNED FLAG MISMATCH"; bad += 1
            if ours:
                if typ != 0 or not pbr or [i for i, x in enumerate(paths) if x] != [0, 1, 5]: line += "  BAD SHADER/SLOTS"; bad += 1
                line += f"  slots 0/1/5 {'all present' if not miss else 'MISSING ' + ', '.join(miss)}"; bad += len(miss)
            else: line += "  vanilla textures: " + ", ".join(x for x in paths if x)[:120]
            print(line)
print(f"RESULT {n_nif} NIFs:", "PASS" if bad == 0 else f"FAIL {bad}")
sys.exit(1 if bad else 0)
