# Truly Nordic Carved Weapons Replacer - the Blender half of the quiver / arrow game build (2026-11-12, quiver B4).
# The approved design NIF (set2\work_final_quiverB4\tn_quiverB4.nif) holds four shapes: TNQuiver (steel atlas - the quiver's
# steel and the five arrow ends' nocks), TNQuiverLeather (soft atlas - leather, lining, straps, and the five arrow ends'
# shafts, cords and black vanes), TNArrow (steel - the loose arrow's nock, socket and barbed head) and TNArrowShaft (soft -
# its shaft, cords and vanes). Vanilla's nordicarrow.nif names ONE BSTriShape per arrow (Arrow1..Arrow5 in the quiver,
# 'Arrow:0' the loose / nocked arrow) and 'ArrowQuiver:0' for the quiver, each with one texture set, so:
#   * the five arrow ends are cut out of the two quiver shapes (loose parts, each assigned to the nearest of the five
#     arrow axes the design placed them on - aqs_build.py's `ends`), and each arrow (5 ends + the loose arrow) becomes ONE
#     shape: its steel and soft parts joined, their UVs moved into a new ARROW ATLAS that holds a pixel-exact copy of
#     every rectangle those parts use on the steel and soft atlases (same px per unit - nothing is resampled);
#   * the quiver keeps two shapes: its steel ('ArrowQuiver:0') and its leather (a second shape under the same
#     'ArrowQuiver' node, as the weapons' wraps are added).
# Nothing is decimated (6.5k + 1.4k triangles; the design's own normals are kept - no weld, no recomputed normals).
# Writes <out>\dec_<role>.nif / .npz (metal, leather, arrow, arrowq1..arrowq5), orig_<role>.npz (= dec, for silhouette.py),
# arrow_atlas_plan.json (the rectangles to copy, for quiver_atlas.py) and blender_stats.json.
# Run: blender --background --factory-startup --python-exit-code 1 --python gb_quiver.py -- <config.json> quiver
import bpy, bmesh, sys, os, json, math, addon_utils
import numpy as np

CFG, KEY = sys.argv[sys.argv.index("--") + 1:][:2]
C = json.load(open(CFG))[KEY]
OUT = C["out"]; os.makedirs(OUT, exist_ok=True)
addon_utils.enable("io_scene_nifly", default_set=True)
A = 2048                                   # the steel and soft atlases
stats = {"item": KEY, "source": C["sources"][0], "shapes": {}}

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

for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.pynifly(filepath=C["sources"][0])
for o in list(bpy.data.objects):
    if o.type != "MESH": bpy.data.objects.remove(o)
SH = {o.name: o for o in bpy.data.objects}
assert set(SH) >= {"TNQuiver", "TNQuiverLeather", "TNArrow", "TNArrowShaft"}, sorted(SH)
stats["source_tris"] = {k: tris_of(v) for k, v in SH.items()}

# ------------------------------------------------------------------ the five arrow ends' axes, in the NIF frame
# aqs_build.py quiver(): ends (x0, z0, ytop, tilt) in the design frame (mouth up); a point local (x, y, z) of an arrow end
# goes to (x0 + X ca - Y sa, ytop + X sa + Y ca, z0 + Z) with X, Y, Z = x, -y, -z; the NIF frame is (x, y, z) -> (-x, -y, z)
ENDS = [(-1.5, -0.8, 66.0, -3), (0.2, -1.0, 67.2, 2), (1.7, -0.6, 65.4, 5), (-0.7, 0.9, 64.6, -1), (1.0, 1.0, 66.6, 3)]
AX = []
for x0, z0, ytop, tilt in ENDS:
    ca, sa = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    p0 = np.array([-x0, -ytop, z0]); d = np.array([-sa, ca, 0.0])             # nock point, direction toward the tip (local +y)
    AX.append((p0, d / np.linalg.norm(d)))
def axis_dist(P, k):
    p0, d = AX[k]; Q = P - p0; t = Q @ d; return np.linalg.norm(Q - np.outer(t, d), axis=1), t

def split_ends(o, tmax):
    """loose parts of a quiver shape: those lying on an arrow end's axis (every vertex within 1.7 of it, along it from the
    nock to tmax: 1.5 for the steel - an end's only steel is its nock, local 0-1.0; 20 for the soft - shaft to 18, vanes,
    cords) go to that end; the rest stay the quiver's (a first pass with 20 for both took three of the mouth rim's top
    quads into an arrow). Returns (quiver part, {end index: [parts]})."""
    select_only(o); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="LOOSE"); bpy.ops.object.mode_set(mode="OBJECT")
    parts = [x for x in bpy.context.selected_objects]; keep, ends = [], {}
    for p in parts:
        V = np.array([list(p.matrix_world @ v.co) for v in p.data.vertices])
        best = None
        for k in range(5):
            dist, t = axis_dist(V, k)
            if dist.max() < 1.7 and t.min() > -0.5 and t.max() < tmax:
                s = float(dist.mean())
                if best is None or s < best[1]: best = (k, s)
        if best is None: keep.append(p)
        else: ends.setdefault(best[0], []).append(p)
    return join(keep, o.name), ends, len(parts)

q_steel, ends_steel, n1 = split_ends(SH["TNQuiver"], 1.5)
q_soft, ends_soft, n2 = split_ends(SH["TNQuiverLeather"], 20.0)
stats["split"] = {"TNQuiver loose parts": n1, "TNQuiverLeather loose parts": n2,
                  "end steel parts": {k: len(v) for k, v in sorted(ends_steel.items())}, "end soft parts": {k: len(v) for k, v in sorted(ends_soft.items())}}
assert sorted(ends_steel) == list(range(5)) and sorted(ends_soft) == list(range(5)), stats["split"]

# ------------------------------------------------------------------ the arrow atlas: rectangles copied pixel for pixel
arrows = {"arrow": ([SH["TNArrow"]], [SH["TNArrowShaft"]])}
for k in range(5): arrows[f"arrowq{k + 1}"] = (ends_steel[k], ends_soft[k])
PAD = 4
rects = []                                   # [src, x0, y0, x1, y1]
for name, (st, so) in arrows.items():
    for src, objs in (("steel", st), ("soft", so)):
        for o in objs:
            # each loose part's own islands (a part may use one rectangle only - checked below)
            x0, y0, x1, y1 = uv_px_box(o)
            rects.append([src, math.floor(x0) - PAD, math.floor(y0) - PAD, math.ceil(x1) + PAD, math.ceil(y1) + PAD])
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
# shelf packing, tallest first, into the smallest square atlas that holds them (1024 or 2048)
def pack(rs, D):
    order = sorted(range(len(rs)), key=lambda i: -(rs[i][4] - rs[i][2])); x = y = sh = 0; pos = {}
    for i in order:
        w, h = rs[i][3] - rs[i][1], rs[i][4] - rs[i][2]
        if x + w > D: x = 0; y += sh; sh = 0
        if y + h > D or w > D: return None
        pos[i] = (x, y); x += w; sh = max(sh, h)
    return pos
for D in (1024, 2048):
    POS = pack(M, D)
    if POS: break
assert POS, "the arrow rectangles do not fit a 2048 atlas"
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
for name, (st, so) in arrows.items():
    for o in st: move_uv(o, "steel")
    for o in so: move_uv(o, "soft")
    shapes[name] = join(list(st) + list(so), name)

# ------------------------------------------------------------------ export, dumps
for role, o in shapes.items():
    V, F, UV = arrays(o)
    for pre in ("dec", "orig"): np.savez(os.path.join(OUT, f"{pre}_{role}.npz"), V=V, F=F, UV=UV)
    stats["shapes"][role] = {"tris": tris_of(o), "verts": len(o.data.vertices), "lo": V.min(0).round(3).tolist(), "hi": V.max(0).round(3).tolist(),
                             "uv_lo": UV.reshape(-1, 2).min(0).round(4).tolist(), "uv_hi": UV.reshape(-1, 2).max(0).round(4).tolist()}
    export_single(o, os.path.join(OUT, f"dec_{role}.nif"))
json.dump(plan, open(os.path.join(OUT, "arrow_atlas_plan.json"), "w"), indent=1)
stats["arrow_atlas"] = {"size": D, "rectangles": len(M), "from_part_boxes": len(rects)}
json.dump(stats, open(os.path.join(OUT, "blender_stats.json"), "w"), indent=1)
print("STATS", json.dumps(stats)[:1500]); print("DONE", KEY)
