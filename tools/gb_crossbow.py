# Truly Nordic Carved Weapons Replacer - the Blender half of the CROSSBOW game build (2026-11-13, design B5 - the owner's 08:40 review,
# set2\work_xbow_crossbowB5; B4 and B3 before it - the B5 weights and the limb-break cause are in the block above prod_weights).
# Earlier notes (B3/B4): the owner 07:16 (via Main Agent): "if the animated crossbow won't work, just ship it
# unanimated for now" - vanilla's trigger and string nut (TriggerCtrl, RollerNutTriggerCtrl) move only through the
# behaviour graph's Havok animations, which are not re-keyed here, so:
#   * the prod limbs take vanilla's LIMB weights (nearest face among vanilla's limb faces only) and the string vanilla's
#     string scheme as a function of x (v4, see vanilla_string_weights) - the draw and the reload bend and pull them
#     as vanilla's (vanilla's Havok clips crossbow_reload / _release move the limbs, StringR / StringL and
#     CockingMechanismCtrl; since 2026-11-14 our cocking lever rides CockingMechanismCtrl);
#   * the lever, the catch and every other part (stock, lock box and plates, prod block, stirrup, wrap) are weighted
#     100 % to CrossbowRoot - they stay still. A part keeps the transferred weights only if it reaches past |x| 8
#     (the limbs start at vanilla's R01/L01 heads, |x| 2.97; the prod block's plates stay within |x| 6).
#   * the lever and catch are the COCKED state's (lever at rest, the catch up with its hooks where the drawn string
#     lands, vanilla's nut y 2.85); the string is the main NIF's straight string (vanilla's bind pose is the rest string).
# Frame: the design's top is +z, vanilla's is -z: (x, y, z) -> (-x, y, -z - 0.46) (work_xbow_NOTES.md, a 180-degree turn
# about y; the nut, sear and trigger pivots then sit on vanilla's bones). Nothing decimated; the design's normals kept.
# Writes <out>\skinned.nif (three skinned shapes: dec_metal, dec_soft, dec_wrap + vanilla's armature), dec_<role>.npz
# (vanilla frame, for the collision hull) and blender_stats.json.
# Run: blender --background --factory-startup --python-exit-code 1 --python gb_crossbow.py -- <config.json> crossbow
import bpy, sys, os, json, addon_utils
import numpy as np
from mathutils import Matrix

CFG, KEY = sys.argv[sys.argv.index("--") + 1:][:2]
C = json.load(open(CFG))[KEY]
OUT = C["out"]; os.makedirs(OUT, exist_ok=True)
addon_utils.enable("io_scene_nifly", default_set=True)
stats = {"item": KEY, "sources": C["sources"], "shapes": {}, "parts": {}}
LIMB_X = 8.0
def select_only(o):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
def tris_of(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
def join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); o = bpy.context.view_layer.objects.active
    o.name = name; o.data.name = name; return o
def bake(o):     # (shape keys dropped first: the exporter writes the Basis key, which mesh.transform left behind)
    if o.data.shape_keys: o.shape_key_clear()
    o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4)
def imp(path):
    before = set(bpy.data.objects); bpy.ops.import_scene.pynifly(filepath=path, import_collisions=False); return [o for o in bpy.data.objects if o not in before]

for o in list(bpy.data.objects): bpy.data.objects.remove(o)
main = {o.name: o for o in imp(C["sources"][0]) if o.type == "MESH"}
cocked = {o.name: o for o in imp(C["sources"][1]) if o.type == "MESH"}
for o in list(bpy.data.objects):
    if o.type != "MESH": bpy.data.objects.remove(o)
need_m = {"TNCrossbow", "TNCrossbowProd", "TNCrossbowLock", "TNCrossbowSoft", "TNCrossbowWrap", "TNCrossbowCock"}; need_c = {"TNCrossbowLeverC", "TNCrossbowCatchC"}
assert need_m <= set(main) and need_c <= set(cocked), (sorted(main), sorted(cocked))
for k, o in list(main.items()) + list(cocked.items()):
    if k not in need_m | need_c: bpy.data.objects.remove(o)
SH = {k: main[k] for k in need_m}; SH.update({k: cocked[k] for k in need_c})
G = Matrix(((-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, -0.46), (0, 0, 0, 1)))       # design -> vanilla frame
for o in SH.values(): bake(o); o.data.transform(G)
stats["source_tris"] = {k: tris_of(v) for k, v in SH.items()}

# ------------------------------------------------------------------ vanilla armature + weights
new = imp(C["vanilla"])
arm = [o for o in new if o.type == "ARMATURE"][0]; vmesh = [o for o in new if o.type == "MESH" and o.vertex_groups][0]
stats["vanilla_groups"] = [g.name for g in vmesh.vertex_groups]
# bones only (SBP_32_BODY is a partition, not a bone); of the mechanism bones only CockingMechanismCtrl carries ours (the cocking lever); vanilla's Havok animations
# move CockingMechanismCtrl, and the trigger and nut stay still (the owner's decision - the still trigger)
VG = [g for g in stats["vanilla_groups"] if not g.startswith("SBP_")]
ROOT = [g for g in VG if g.lower() == "crossbowroot"]; assert ROOT, VG; ROOT = ROOT[0]
# B5 (2026-11-13, the owner 08:40: "I still see a break in the bow arms when cocked back and the string is moved from its
# attachment point"). The B4 break, measured on the staged NIF: prod vertices at |x| 4-7 were 100 % CrossbowRoot and at
# |x| 8 already 0.87 L01 - the design's slabs are many LOOSE pieces (a face has its own vertices, the walls and chamfer
# their own quads) and the rule "a loose piece inside |x| < 8 goes rigid" sent every root-end piece of each arm to the
# root, so in the draw the root third stayed and the rest bent. The edge-stretch check could not see it (loose pieces
# share no edges). Now:
#   * the PROD is its own design shape (TNCrossbowProd: the centre piece against the face, both arms, the tip bosses) and
#     every vertex of it takes its weights from ONE smooth function of |x| (prod_weights) - pieces that touch get the same
#     weights wherever they touch, so the arm, its faces, walls and tip bend as one piece;
#   * the string's end (from |x| 24.9 out) blends to the SAME limb bone as the tip it hangs on, 1.0 from |x| 26.1 - the end
#     rides with the tip boss instead of drifting with the string bone (vanilla's own end was 0.25 string / 0.75 limb);
#   * everything else (stock, deck, nut, lever, plates, bridle, stirrup, wrap) is rigid on CrossbowRoot;
#   * (2026-11-14, the owner: "give the crossbow ... a cocking lever, just like you would get a vanilla crossbow") the
#     cocking lever (TNCrossbowCock, its hub on vanilla's pivot) is 100 % CockingMechanismCtrl - the reload swings it.
def sm(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def prod_weights(x):
    """vanilla frame (R bones on -x): rigid inside the bridle, onto the first limb bone across vanilla's R01/L01 head
    (|x| 2.97), then L01 -> L02 along the arm as vanilla's limb faces (0.25 L02 at |x| ~11, 0.75 at ~15, 1.0 from 18)"""
    ax = abs(x); b1, b2 = ("CrossBowBone_R01", "CrossBowBone_R02") if x < 0 else ("CrossBowBone_L01", "CrossBowBone_L02")
    t1 = sm((ax - 2.6) / 0.8); t2 = sm((ax - 8.0) / 10.0)
    w = {ROOT: 1.0 - t1, b1: t1 * (1.0 - t2), b2: t1 * t2}
    return {k: v for k, v in w.items() if v > 1e-4}
def string_weights(x):
    """vanilla crossbow.nif's string scheme as a function of x (StringR / R02 on -x): the middle 50 / 50 StringR / StringL
    blending to 1.0 on its own side by |x| 1.8, 0.1 limb from |x| 23.9; B5: from |x| 24.9 the limb share rises to 1.0 at
    26.1, so the end on the tip boss follows the tip exactly"""
    ax = abs(x); own, oth, lb = ("StringR", "StringL", "CrossBowBone_R02") if x < 0 else ("StringL", "StringR", "CrossBowBone_L02")
    w_oth = 0.5 * (1.0 - min(1.0, ax / 1.8))
    w_lb = 0.0 if ax < 23.9 else (0.1 if ax < 24.9 else 0.1 + 0.9 * sm((ax - 24.9) / 1.2))
    w = {own: max(0.0, 1.0 - w_oth - w_lb)}
    if w_oth > 1e-4: w[oth] = w_oth
    if w_lb > 0: w[lb] = w_lb
    return {k: v for k, v in w.items() if v > 1e-4}
def set_w(o, i, w):
    for k, x in w.items(): o.vertex_groups[k].add([i], x, "REPLACE")
def components(o):
    """loose parts by POSITION (vertices within 1e-4 merged first: a UV seam is not a break)"""
    me = o.data; P = np.array([list(v.co) for v in me.vertices]); key = {}
    par = list(range(len(P)))
    def find(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for i, p in enumerate(np.round(P / 1e-4).astype(np.int64)):
        k = tuple(p)
        if k in key: par[find(i)] = find(key[k])
        else: key[k] = i
    for e in me.edges:
        a, b = find(e.vertices[0]), find(e.vertices[1])
        if a != b: par[a] = b
    return P, np.array([find(i) for i in range(len(P))])
pw = {}
for k, o in SH.items():
    for g in VG: o.vertex_groups.new(name=g)
    P = np.array([list(v.co) for v in o.data.vertices])
    if k == "TNCrossbowProd":
        for i in range(len(P)): set_w(o, i, prod_weights(P[i, 0]))
        for x0 in range(0, 28, 2):
            if ((np.abs(P[:, 0]) >= x0) & (np.abs(P[:, 0]) < x0 + 2)).any():
                pw[f"|x| {x0}-{x0 + 2}"] = {b: round(v, 2) for b, v in prod_weights(-(x0 + 1.0)).items()}
        stats["prod_weights_by_x"] = pw
    elif k == "TNCrossbowCock":     # the cocking lever (2026-11-14): rigid on vanilla's cocking bone - the reload swings it
        COCK = [g for g in VG if g == "CockingMechanismCtrl"]; assert COCK, VG
        o.vertex_groups[COCK[0]].add(list(range(len(P))), 1.0, "REPLACE")
    elif k == "TNCrossbowSoft":
        P, comp = components(o); n_str = 0
        for c in np.unique(comp):
            idx = np.where(comp == c)[0]
            if np.abs(P[idx, 0]).max() > 8.0:
                n_str += 1
                for i in idx.tolist(): set_w(o, i, string_weights(P[i, 0]))
            else:
                o.vertex_groups[ROOT].add(idx.tolist(), 1.0, "REPLACE")
        stats["string_parts"] = n_str
    else:
        o.vertex_groups[ROOT].add(list(range(len(P))), 1.0, "REPLACE")
roles = {"metal": join([SH["TNCrossbow"], SH["TNCrossbowProd"], SH["TNCrossbowLock"], SH["TNCrossbowLeverC"], SH["TNCrossbowCatchC"], SH["TNCrossbowCock"]], "metal"),
         "soft": SH["TNCrossbowSoft"], "wrap": SH["TNCrossbowWrap"]}
for k, o in roles.items(): o.name = o.data.name = k
for role, o in roles.items():
    me = o.data; dom = {}
    for g in list(o.vertex_groups):
        if g.name not in VG: o.vertex_groups.remove(g)
    for v in me.vertices:
        gs = [g for g in v.groups if g.weight > 0]
        if not gs: o.vertex_groups[ROOT].add([v.index], 1.0, "REPLACE"); dom["(none -> root)"] = dom.get("(none -> root)", 0) + 1; continue
        n = o.vertex_groups[max(gs, key=lambda g: g.weight).group].name; dom[n] = dom.get(n, 0) + 1
    stats["parts"][role] = {"dominant_bone_counts": dom}
    V = np.array([list(v.co) for v in me.vertices], np.float32)
    np.savez(os.path.join(OUT, f"dec_{role}.npz"), V=V)
    stats["shapes"][role] = {"tris": tris_of(o), "verts": len(me.vertices), "lo": V.min(0).round(3).tolist(), "hi": V.max(0).round(3).tolist()}
    o.parent = arm; am = o.modifiers.new("arm", "ARMATURE"); am.object = arm
keep = set(roles.values()) | {arm}
for o in list(bpy.data.objects):
    if o not in keep and o.type == "MESH": bpy.data.objects.remove(o)
bpy.ops.object.select_all(action="DESELECT")
for o in roles.values(): o.select_set(True)
arm.select_set(True); bpy.context.view_layer.objects.active = roles["metal"]
r = bpy.ops.export_scene.pynifly(filepath=os.path.join(OUT, "skinned.nif"), target_game="SKYRIMSE", export_colors=False, blender_xf=False, intuit_defaults=False)
print("EXPORT skinned", r)
# PyNifly names the file after the source the joined objects came from (the cocked NIF's lever and catch: _cocked)
for alt in ("skinned_cocked.nif",):
    a = os.path.join(OUT, alt)
    if os.path.isfile(a): os.replace(a, os.path.join(OUT, "skinned.nif"))
assert os.path.isfile(os.path.join(OUT, "skinned.nif")), os.listdir(OUT)
json.dump(stats, open(os.path.join(OUT, "blender_stats.json"), "w"), indent=1); print("STATS", json.dumps(stats)[:3000]); print("DONE", KEY)
