# Truly Nordic Carved Weapons Replacer - the Blender half of the CROSSBOW game build (2026-11-13, design B4 - v4 after the owner's 07:41 test -
# set2\work_xbow_crossbowB4; was B3). The owner 07:16 (via Main Agent): "if the animated crossbow won't work, just ship it
# unanimated for now" - vanilla's trigger and string nut (TriggerCtrl, RollerNutTriggerCtrl) move only through the
# behaviour graph's Havok animations, which are not re-keyed here, so:
#   * the prod limbs take vanilla's LIMB weights (nearest face among vanilla's limb faces only) and the string vanilla's
#     string scheme as a function of x (v4, see vanilla_string_weights) - the draw and the reload bend and pull them
#     as vanilla's (vanilla's Havok clips crossbow_reload / _release move the limbs, StringR / StringL and
#     CockingMechanismCtrl; nothing of ours is on CockingMechanismCtrl);
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
need_m = {"TNCrossbow", "TNCrossbowLock", "TNCrossbowSoft", "TNCrossbowWrap"}; need_c = {"TNCrossbowLeverC", "TNCrossbowCatchC"}
assert need_m <= set(main) and need_c <= set(cocked), (sorted(main), sorted(cocked))
for k, o in list(main.items()) + list(cocked.items()):
    if k not in need_m | need_c: bpy.data.objects.remove(o)
SH = {k: main[k] for k in need_m}; SH.update({k: cocked[k] for k in need_c})
G = Matrix(((-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, -0.46), (0, 0, 0, 1)))       # design -> vanilla frame
for o in SH.values(): bake(o); o.data.transform(G)
stats["source_tris"] = {k: tris_of(v) for k, v in SH.items()}
roles = {"metal": join([SH["TNCrossbow"], SH["TNCrossbowLock"], SH["TNCrossbowLeverC"], SH["TNCrossbowCatchC"]], "metal"),
         "soft": SH["TNCrossbowSoft"], "wrap": SH["TNCrossbowWrap"]}
for k, o in roles.items(): o.name = o.data.name = k

# ------------------------------------------------------------------ vanilla armature + weights
new = imp(C["vanilla"])
arm = [o for o in new if o.type == "ARMATURE"][0]; vmesh = [o for o in new if o.type == "MESH" and o.vertex_groups][0]
stats["vanilla_groups"] = [g.name for g in vmesh.vertex_groups]
# bones only (SBP_32_BODY is a partition, not a bone); the mechanism bones are dropped: vanilla's Havok animations move
# CockingMechanismCtrl / TriggerCtrl / RollerNutTriggerCtrl, and nothing of ours may follow them (the still trigger)
VG = [g for g in stats["vanilla_groups"] if not g.startswith("SBP_")]
ROOT = [g for g in VG if g.lower() == "crossbowroot"]; assert ROOT, VG; ROOT = ROOT[0]
MECH = {"CockingMechanismCtrl", "TriggerCtrl", "RollerNutTriggerCtrl"}
STRINGB = {"StringR", "StringL"}
LIMBB = {"CrossBowBone_R01", "CrossBowBone_R02", "CrossBowBone_L01", "CrossBowBone_L02"}
# v4 (2026-11-13, after the owner's 07:41 test - "it tears the mesh and texture" going from unloaded to loaded, "stray
# artifacts floating where the string would be"): the B3 build took the PROD's weights by nearest face from the whole
# vanilla mesh; the limbs' rear halves lay nearest vanilla's string, got string weights, the string bones were stripped
# and 1,760 limb vertices fell to CrossbowRoot - in the Havok draw the front half bent and the rear half stayed (4.1
# units of stretch at crossbow_reload frame 57; set2\work_xbow_fix1113\lbs_check.py). Now:
#   * the prod takes its weights only from vanilla's LIMB faces (every vertex at least half on the four limb bones);
#   * the string takes vanilla's string scheme as an explicit function of x (vanilla_string_weights below).
vlimb = vmesh.copy(); vlimb.data = vmesh.data.copy(); vlimb.name = "vanilla_limbs"; bpy.context.collection.objects.link(vlimb)
def limb_share(o, v):
    return sum(g.weight for g in v.groups if o.vertex_groups[g.group].name in LIMBB)
lv = [limb_share(vlimb, v) for v in vlimb.data.vertices]
import bmesh
bm = bmesh.new(); bm.from_mesh(vlimb.data); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not all(lv[v.index] >= 0.5 for v in f.verts)], context="FACES")
stats["vanilla_limb_faces"] = len(bm.faces); bm.to_mesh(vlimb.data); bm.free()
def vanilla_string_weights(x):
    """vanilla crossbow.nif's own string weights as a function of x (vanilla frame; StringR / R02 on -x): the middle
    50 / 50 StringR / StringL blending to 1.0 on its own side by |x| 1.8, 0.1 limb (R02 / L02) from |x| 23.9, 0.75 limb
    on the loop round the tip (|x| >= 25.6)"""
    ax = abs(x); own, oth, lb = ("StringR", "StringL", "CrossBowBone_R02") if x < 0 else ("StringL", "StringR", "CrossBowBone_L02")
    w_oth = 0.5 * (1.0 - min(1.0, ax / 1.8))
    w_lb = 0.0 if ax < 23.9 else (0.1 if ax < 24.9 else 0.1 + 0.65 * min(1.0, (ax - 24.9) / 0.7))
    w = {own: 1.0 - w_oth - w_lb}
    if w_oth > 1e-4: w[oth] = w_oth
    if w_lb > 0: w[lb] = w_lb
    return w
def transfer(o, src, idx=None):
    select_only(o); m = o.modifiers.new("dt", "DATA_TRANSFER"); m.object = src; m.use_vert_data = True
    m.data_types_verts = {"VGROUP_WEIGHTS"}; m.vert_mapping = "POLYINTERP_NEAREST"
    m.layers_vgroup_select_src = "ALL"; m.layers_vgroup_select_dst = "NAME"
    if idx is not None:
        vg = o.vertex_groups.new(name="_only"); vg.add(idx, 1.0, "REPLACE"); m.vertex_group = "_only"
    bpy.ops.object.modifier_apply(modifier=m.name)
    if idx is not None: o.vertex_groups.remove(o.vertex_groups["_only"])
def renorm(o, idx, allowed):
    gi = {g.name: g.index for g in o.vertex_groups}
    for i in idx:
        v = o.data.vertices[int(i)]; w = {o.vertex_groups[g.group].name: g.weight for g in v.groups if o.vertex_groups[g.group].name in VG}
        w = {k: x for k, x in w.items() if k in allowed and x > 1e-4}; s = sum(w.values())
        for g in VG: o.vertex_groups[g].remove([int(i)])
        if s <= 0: o.vertex_groups[ROOT].add([int(i)], 1.0, "REPLACE")
        else:
            for k, x in w.items(): o.vertex_groups[k].add([int(i)], x / s, "REPLACE")
for role, o in roles.items():
    for g in VG: o.vertex_groups.new(name=g)
    transfer(o, vmesh)
    # loose parts (by vertex connectivity): a part inside |x| < LIMB_X goes rigid on CrossbowRoot
    me = o.data; par = list(range(len(me.vertices)))
    def find(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for e in me.edges:
        a, b = find(e.vertices[0]), find(e.vertices[1])
        if a != b: par[a] = b
    P = np.array([list(v.co) for v in me.vertices]); comp = np.array([find(i) for i in range(len(P))])
    gi = {g.name: g.index for g in o.vertex_groups}; rigid = 0; limb = 0; dom = {}
    strings = 0; limb_idx = []
    for c in np.unique(comp):
        idx = np.where(comp == c)[0]
        if np.abs(P[idx, 0]).max() < LIMB_X:
            for g in VG:
                if g != ROOT: o.vertex_groups[g].remove(idx.tolist())
            o.vertex_groups[ROOT].add(idx.tolist(), 1.0, "REPLACE"); rigid += 1
        elif role == "soft":     # a soft part reaching the prod tips is the string: vanilla's string scheme by x
            for i in idx.tolist():
                for g in VG: o.vertex_groups[g].remove([i])
                for k, x in vanilla_string_weights(P[i, 0]).items(): o.vertex_groups[k].add([i], x, "REPLACE")
            strings += 1
        else:                    # the prod: vanilla's limb faces only, limb bones (and the root) only - one transfer below
            limb_idx += idx.tolist(); limb += 1
    if limb_idx:
        for g in VG: o.vertex_groups[g].remove(limb_idx)
        transfer(o, vlimb, limb_idx); renorm(o, limb_idx, LIMBB | {ROOT})
    stats.setdefault("string_parts", {})[role] = strings
    for g in list(o.vertex_groups):
        if g.name not in VG: o.vertex_groups.remove(g)
    for v in me.vertices:
        gs = [g for g in v.groups if g.weight > 0]
        if not gs: o.vertex_groups[ROOT].add([v.index], 1.0, "REPLACE"); dom["(none -> root)"] = dom.get("(none -> root)", 0) + 1; continue
        n = o.vertex_groups[max(gs, key=lambda g: g.weight).group].name; dom[n] = dom.get(n, 0) + 1
    stats["parts"][role] = {"rigid_on_root": rigid, "weights_from_vanilla": limb, "dominant_bone_counts": dom}
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
