# Truly Nordic Carved Weapons Replacer - the Blender half of the BOLT quiver / bolt game build (2026-11-13, quiver B and
# its barbed bolts, set2\work_xbow_boltquiverB). As gb_quiver.py (the arrow quiver), on vanilla Dawnguard's structure:
#   * tn_boltquiverB.nif: TNBoltQuiver (steel atlas - the case's steel and the five bolt ends' nocks) and TNBoltQuiverSoft
#     (soft atlas - leather, lining, straps, and the five ends' shafts, cords and vanes). The five ends are cut out (loose
#     parts on an end's axis, xbow_build.py boltquiver()'s `ends`); vanilla's steelbolt.nif has FOUR in-case slots
#     (Arrow1-Arrow4), so each slot takes the nearest end and the fifth end joins the slot nearest to it (all five show at
#     a full stack, and they vanish slot by slot as the count drops, as vanilla's).
#   * tn_boltBflight.nif: TNBolt (steel: nock, socket, barbed head) and TNBoltSoft (soft: shaft, cords, vanes) -> ONE
#     shape 'bolt', used as the flight bolt (SteelBoltFlight:0) and the loose / nocked bolt (Arrow:0).
#   * every bolt shape's UVs move onto one BOLT ATLAS that holds a pixel-exact copy of the rectangles it uses on the steel
#     and soft atlases (quiver_atlas.py boltquiver copies the pixels; nothing resampled).
#   * each shape is moved from the design frame into the LOCAL frame of the vanilla shape it replaces
#     (boltquiver_frames.py -> frames.json; vanilla's node and shape transforms are kept as they are).
# Nothing is decimated; the design's own normals are kept (no weld, no recomputed normals).
# Writes <out>\dec_<role>.nif / .npz (metal, leather, bolt, flight, Arrow1..Arrow4), arrow_atlas_plan.json, blender_stats.json.
# Run: blender --background --factory-startup --python-exit-code 1 --python gb_boltquiver.py -- <config.json> boltquiver
import bpy, sys, os, json, math, addon_utils
import numpy as np
from mathutils import Matrix

CFG, KEY = sys.argv[sys.argv.index("--") + 1:][:2]
C = json.load(open(CFG))[KEY]
OUT = C["out"]; os.makedirs(OUT, exist_ok=True)
FR = json.load(open(os.path.join(OUT, "frames.json")))
addon_utils.enable("io_scene_nifly", default_set=True)
A = 2048
stats = {"item": KEY, "sources": C["sources"], "shapes": {}}

def select_only(o):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
def tris_of(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
def arrays(o):
    me = o.data; M = o.matrix_world
    V = np.array([list(M @ v.co) for v in me.vertices], np.float32)
    F = np.array([list(p.vertices) for p in me.polygons if len(p.vertices) == 3], np.int32)
    uv = me.uv_layers[0].data
    UV = np.array([[list(uv[l].uv) for l in p.loop_indices] for p in me.polygons if len(p.vertices) == 3], np.float32)
    return V, F, UV
def export_single(o, path):
    select_only(o)
    r = bpy.ops.export_scene.pynifly(filepath=path, target_game="SKYRIMSE", export_colors=False, blender_xf=False, intuit_defaults=False)
    print("EXPORT", path, r, tris_of(o))
def dup(o, name):
    c = o.copy(); c.data = o.data.copy(); c.name = name; bpy.context.collection.objects.link(c); return c
def join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); o = bpy.context.view_layer.objects.active
    o.name = name; o.data.name = name; return o
def uv_px_box(o):
    U = np.array([list(l.uv) for l in o.data.uv_layers[0].data], np.float64)
    return (U[:, 0].min() * A, (1 - U[:, 1].max()) * A, U[:, 0].max() * A, (1 - U[:, 1].min()) * A)
def bake(o):     # object transform into the mesh: everything below works on world = mesh coordinates
    o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4)

for o in list(bpy.data.objects): bpy.data.objects.remove(o)
for src in C["sources"]: bpy.ops.import_scene.pynifly(filepath=src)
for o in list(bpy.data.objects):
    if o.type != "MESH": bpy.data.objects.remove(o)
SH = {o.name: o for o in bpy.data.objects}
assert set(SH) >= {"TNBoltQuiver", "TNBoltQuiverSoft", "TNBolt", "TNBoltSoft"}, sorted(SH)
for o in SH.values(): bake(o)
stats["source_tris"] = {k: tris_of(v) for k, v in SH.items()}
# the design frame check: the quiver mouth up (bolt ends to y ~22.6), the flight bolt from nock y -21 to tip y 0
qb = arrays(SH["TNBoltQuiver"])[0]; bb = arrays(SH["TNBolt"])[0]
stats["import_bounds"] = {"TNBoltQuiver": [qb.min(0).round(2).tolist(), qb.max(0).round(2).tolist()], "TNBolt": [bb.min(0).round(2).tolist(), bb.max(0).round(2).tolist()]}
assert qb[:, 1].max() > 22 and qb[:, 1].min() > -0.1 and bb[:, 1].min() < -20.5 and bb[:, 1].max() < 0.1, stats["import_bounds"]

# ------------------------------------------------------------------ the five bolt ends' axes (design frame)
# xbow_build.py: a point local (x, y, z) of an end goes to (x0 + X ca - Y sa, ytop + X sa + Y ca, z0 + Z), X, Y, Z = x, -y, -z
ENDS = [(-1.3, -0.7, 22.0, -3), (0.2, -0.9, 22.6, 2), (1.4, -0.5, 21.7, 4), (-0.6, 0.8, 21.4, -1), (0.9, 0.9, 22.3, 3)]
AX = []
for x0, z0, ytop, tilt in ENDS:
    ca, sa = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    AX.append((np.array([x0, ytop, z0]), np.array([sa, -ca, 0.0])))          # nock point, toward the (absent) tip
def axis_dist(P, k):
    p0, d = AX[k]; Q = P - p0; t = Q @ d; return np.linalg.norm(Q - np.outer(t, d), axis=1), t
def split_ends(o, tmax):
    """loose parts lying on an end's axis (every vertex within 1.7 of it, from the nock to tmax along it: 1.5 for the steel
    - an end's only steel is its nock, local 0-0.8; 10 for the soft - shaft 0.75-9.0, vanes 1.5-6.2, cords) go to that end"""
    select_only(o); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="LOOSE"); bpy.ops.object.mode_set(mode="OBJECT")
    parts = [x for x in bpy.context.selected_objects]; keep, ends = [], {}
    for p in parts:
        V = np.array([list(p.matrix_world @ v.co) for v in p.data.vertices]); best = None
        for k in range(5):
            dist, t = axis_dist(V, k)
            if dist.max() < 1.7 and t.min() > -0.5 and t.max() < tmax:
                s = float(dist.mean())
                if best is None or s < best[1]: best = (k, s)
        if best is None: keep.append(p)
        else: ends.setdefault(best[0], []).append(p)
    return join(keep, o.name), ends, len(parts)
q_steel, ends_steel, n1 = split_ends(SH["TNBoltQuiver"], 1.5)
q_soft, ends_soft, n2 = split_ends(SH["TNBoltQuiverSoft"], 10.0)
stats["split"] = {"TNBoltQuiver loose parts": n1, "TNBoltQuiverSoft loose parts": n2,
                  "end steel parts": {k: len(v) for k, v in sorted(ends_steel.items())}, "end soft parts": {k: len(v) for k, v in sorted(ends_soft.items())}}
assert sorted(ends_steel) == list(range(5)) and sorted(ends_soft) == list(range(5)), stats["split"]

# ------------------------------------------------------------------ five ends -> four vanilla slots
slots = {k: np.array(v) for k, v in FR["slots_design_xz"].items()}
endc = {k: np.array([ENDS[k][0], ENDS[k][1]]) for k in range(5)}
pairs, fs, fe = {}, set(slots), set(endc)
while fs:
    d, a, b = min((float(np.linalg.norm(slots[a] - endc[b])), a, b) for a in fs for b in fe)
    pairs[a] = [b]; fs.discard(a); fe.discard(b)
for b in fe:   # the fifth end joins the slot nearest to it
    a = min(slots, key=lambda s: float(np.linalg.norm(slots[s] - endc[b]))); pairs[a].append(b)
stats["slots"] = {a: [f"end{b + 1} (x {ENDS[b][0]}, z {ENDS[b][1]})" for b in v] for a, v in sorted(pairs.items())}

# ------------------------------------------------------------------ the bolt atlas: rectangles copied pixel for pixel
def loose(o):     # a whole shape (the flight bolt) as its loose parts: one UV box per part
    select_only(o); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="LOOSE"); bpy.ops.object.mode_set(mode="OBJECT"); return list(bpy.context.selected_objects)
bolts = {"bolt": (loose(SH["TNBolt"]), loose(SH["TNBoltSoft"]))}
for a, ends in pairs.items(): bolts[a] = ([p for e in ends for p in ends_steel[e]], [p for e in ends for p in ends_soft[e]])
PAD = 4; rects = []
for name, (st, so) in bolts.items():
    for src, objs in (("steel", st), ("soft", so)):
        for o in objs:
            x0, y0, x1, y1 = uv_px_box(o); rects.append([src, math.floor(x0) - PAD, math.floor(y0) - PAD, math.ceil(x1) + PAD, math.ceil(y1) + PAD])
def merge(rs):
    rs = [list(r) for r in rs]; changed = True
    while changed:
        changed = False
        for i in range(len(rs)):
            for j in range(i + 1, len(rs)):
                a, b = rs[i], rs[j]
                if a[0] == b[0] and a[1] <= b[3] and b[1] <= a[3] and a[2] <= b[4] and b[2] <= a[4]:
                    rs[i] = [a[0], min(a[1], b[1]), min(a[2], b[2]), max(a[3], b[3]), max(a[4], b[4])]; rs.pop(j); changed = True; break
            if changed: break
    return [[r[0], max(r[1], 0), max(r[2], 0), min(r[3], A), min(r[4], A)] for r in rs]
M = merge(rects)
def pack(rs, D):
    order = sorted(range(len(rs)), key=lambda i: -(rs[i][4] - rs[i][2])); x = y = sh = 0; pos = {}
    for i in order:
        w, h = rs[i][3] - rs[i][1], rs[i][4] - rs[i][2]
        if x + w > D: x = 0; y += sh; sh = 0
        if y + h > D or w > D: return None
        pos[i] = (x, y); x += w; sh = max(sh, h)
    return pos
for D in (512, 1024, 2048):
    POS = pack(M, D)
    if POS: break
assert POS, "the bolt rectangles do not fit a 2048 atlas"
plan = {"size": D, "rects": [dict(src=M[i][0], src_box=M[i][1:], dst=list(POS[i])) for i in range(len(M))]}
def find_rect(src, box):
    for i, r in enumerate(M):
        if r[0] == src and r[1] <= box[0] + 1e-6 and r[2] <= box[1] + 1e-6 and r[3] >= box[2] - 1e-6 and r[4] >= box[3] - 1e-6: return i
    raise SystemExit(f"no rectangle holds {src} {box}")
def move_uv(o, src):
    i = find_rect(src, uv_px_box(o)); dx, dy = POS[i][0] - M[i][1], POS[i][1] - M[i][2]
    for l in o.data.uv_layers[0].data:
        px, py = l.uv[0] * A + dx, (1 - l.uv[1]) * A + dy
        l.uv = (px / D, 1 - py / D)
shapes = {"metal": q_steel, "leather": q_soft}
for name, (st, so) in bolts.items():
    for o in st: move_uv(o, "steel")
    for o in so: move_uv(o, "soft")
    shapes[name] = join(list(st) + list(so), name)
shapes["flight"] = dup(shapes["bolt"], "flight")

# ------------------------------------------------------------------ into each vanilla shape's local frame; export
for role, o in shapes.items():
    Vd = arrays(o)[0]; stats["shapes"][role] = {"design_lo": Vd.min(0).round(3).tolist(), "design_hi": Vd.max(0).round(3).tolist()}
    o.data.transform(Matrix(FR["design_to_local"][role]))
    V, F, UV = arrays(o)
    for pre in ("dec", "orig"): np.savez(os.path.join(OUT, f"{pre}_{role}.npz"), V=V, F=F, UV=UV)
    stats["shapes"][role].update({"tris": tris_of(o), "verts": len(o.data.vertices), "local_lo": V.min(0).round(3).tolist(), "local_hi": V.max(0).round(3).tolist(),
                                  "uv_lo": UV.reshape(-1, 2).min(0).round(4).tolist(), "uv_hi": UV.reshape(-1, 2).max(0).round(4).tolist()})
    export_single(o, os.path.join(OUT, f"dec_{role}.nif"))
json.dump(plan, open(os.path.join(OUT, "arrow_atlas_plan.json"), "w"), indent=1)
stats["bolt_atlas"] = {"size": D, "rectangles": len(M), "from_part_boxes": len(rects)}
json.dump(stats, open(os.path.join(OUT, "blender_stats.json"), "w"), indent=1)
print("STATS", json.dumps(stats)[:2500]); print("DONE", KEY)
