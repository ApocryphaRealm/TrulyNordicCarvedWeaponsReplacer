# Truly Nordic Carved Weapons Replacer - the Blender half of the game build, one item per run.
# Imports our approved model's shapes (PyNifly), welds each shape (sharp edges kept from the split normals), decimates
# it to its triangle budget, turns every face outward where the item asks for it (orient_outward - the game culls a
# triangle's back), measures what the decimation changed (surface distance both ways, and how far each
# original vertex's texture coordinate moved, in pixels of the 2048 atlas), builds the edge-blood shapes for weapons
# whose vanilla model has them, and exports every shape as a single-shape NIF for assemble.py.
# The bow: its three shapes take vanilla's bone weights (nearest-face interpolated transfer from vanilla's BowMesh) and
# are exported together with vanilla's armature as one skinned NIF.
# Run: blender --background --factory-startup --python-exit-code 1 --python gb_blender.py -- <config.json> <item>
import bpy, bmesh, sys, os, json, addon_utils
import numpy as np
from mathutils.bvhtree import BVHTree
from mathutils.interpolate import poly_3d_calc

CFG, KEY = sys.argv[sys.argv.index("--") + 1:][:2]
C = json.load(open(CFG))[KEY]
OUT = C["out"]; os.makedirs(OUT, exist_ok=True)
addon_utils.enable("io_scene_nifly", default_set=True)
stats = {"item": KEY, "shapes": {}}

def clear():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
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
def bvh(o):
    me = o.data; M = o.matrix_world
    return BVHTree.FromPolygons([M @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])
def surf_dist(src, tree):
    d = []
    for v in src.data.vertices:
        hit = tree.find_nearest(src.matrix_world @ v.co)
        if hit[0] is not None: d.append(hit[3])
    d = np.array(d); return float(d.max()), float(np.percentile(d, 95))
def uv_shift(orig, dec, px=2048):
    """For every original corner: the dec surface point nearest its vertex, its UV interpolated there, the distance in
    pixels to the original UV. Corners on a UV seam are measured against the nearest dec face on the same side of the
    seam (the face whose UV lies closest), so a seam is not counted as a shift."""
    tree = bvh(dec); dme = dec.data; duv = dme.uv_layers[0].data; ome = orig.data; ouv = ome.uv_layers[0].data
    out = []; where = []
    for p in ome.polygons:
        for li in p.loop_indices:
            co = ome.vertices[ome.loops[li].vertex_index].co; target = ouv[li].uv
            best = None
            for loc, nrm, fi, dist in tree.find_nearest_range(co, 0.05) or [tree.find_nearest(co)]:
                if fi is None: continue
                q = dme.polygons[fi]; pts = [dme.vertices[i].co for i in q.vertices]
                w = poly_3d_calc(pts, loc); u = sum((duv[l].uv * wi for l, wi in zip(q.loop_indices, w)), start=target * 0)
                e = (u - target).length * px
                best = e if best is None else min(best, e)
            if best is not None: out.append(best); where.append(tuple(co))
    out = np.array(out); where = np.array(where); bad = out > 8
    stats.setdefault("uv_bad", {})[orig.name] = {"corners_over_8px": int(bad.sum()), "of": int(len(out)),
        "positions": np.round(where[bad][:12], 2).tolist()}
    return float(out.max()), float(np.percentile(out, 95)), float(np.percentile(out, 99.5))

def decimate(o, target):
    select_only(o); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0005, use_sharp_edge_from_normals=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    n0 = tris_of(o)
    if target and n0 > target:
        # UV seams are protected: every vertex on an edge whose two faces disagree on a UV is put in group 'seam',
        # and the collapse (inverted group, factor 1000) all but never moves it, so no face is stretched across a seam
        me = o.data; bm = bmesh.new(); bm.from_mesh(me); uvl = bm.loops.layers.uv.active; seam = set()
        for e in bm.edges:
            if len(e.link_loops) != 2: seam.update(v.index for v in e.verts); continue
            a, b = e.link_loops
            # loop a runs v0->v1 on its face, loop b runs v1->v0: compare the UVs at the same vertex
            if (a[uvl].uv - b.link_loop_next[uvl].uv).length > 1e-5 or (a.link_loop_next[uvl].uv - b[uvl].uv).length > 1e-5:
                seam.update(v.index for v in e.verts)
        bm.free()
        g = o.vertex_groups.new(name="seam"); g.add(sorted(seam), 1.0, "REPLACE")
        stats.setdefault("seam_verts", {})[o.name] = len(seam)
        m = o.modifiers.new("dec", "DECIMATE"); m.decimate_type = "COLLAPSE"; m.ratio = target / n0; m.use_collapse_triangulate = True
        m.vertex_group = "seam"; m.invert_vertex_group = True; m.vertex_group_factor = 1000.0
        bpy.ops.object.modifier_apply(modifier=m.name)
        o.vertex_groups.remove(o.vertex_groups["seam"])
    me = o.data
    try: bpy.ops.mesh.customdata_custom_splitnormals_clear()
    except Exception: pass
    for p in me.polygons: p.use_smooth = True
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3]); bm.to_mesh(me); bm.free()
    # sharp by angle as well (blade bevels, flange corners): edges over 50 degrees stay hard
    sharp = me.attributes.get("sharp_edge") or me.attributes.new("sharp_edge", "BOOLEAN", "EDGE")
    bm = bmesh.new(); bm.from_mesh(me); bm.edges.ensure_lookup_table()
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle(0) > 0.87: sharp.data[e.index].value = True
    bm.free(); me.update()
    return n0

def export_single(o, path):
    select_only(o)
    r = bpy.ops.export_scene.pynifly(filepath=path, target_game="SKYRIMSE", export_colors=False, blender_xf=False, intuit_defaults=False)
    print("EXPORT", path, r, tris_of(o))

def make_blood(dec, region, uvbox, name, offset=0.012):
    """Edge blood: the dec metal's faces inside region (axis-aligned box in model units), pushed out 0.012 along the
    normal, planar UV over vanilla's own blood UV range (u along the long axis y, v across x)."""
    b = dec.copy(); b.data = dec.data.copy(); b.name = name; bpy.context.collection.objects.link(b)
    me = b.data; lo, hi = np.array(region[0]), np.array(region[1])
    bm = bmesh.new(); bm.from_mesh(me)
    kill = [f for f in bm.faces if not all(np.all((np.array(v.co) >= lo) & (np.array(v.co) <= hi)) for v in f.verts)]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bm.to_mesh(me); bm.free()
    n = tris_of(b)
    if n > 900:
        select_only(b); m = b.modifiers.new("dec", "DECIMATE"); m.decimate_type = "COLLAPSE"; m.ratio = 900 / n
        bpy.ops.object.modifier_apply(modifier=m.name)
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3]); bm.normal_update()
    for v in bm.verts: v.co += v.normal * offset
    uvl = bm.loops.layers.uv.active
    (u0, v0), (u1, v1) = uvbox
    for f in bm.faces:
        for l in f.loops:
            x, y = l.vert.co.x, l.vert.co.y
            l[uvl].uv = (u0 + (u1 - u0) * (y - lo[1]) / (hi[1] - lo[1]), v0 + (v1 - v0) * (x - lo[0]) / (hi[0] - lo[0]))
    bm.to_mesh(me); bm.free()
    return b

def orient_outward(objs, apply=True, rays=12, samples=300, seed=7):
    """Every face's winding made to face OUT (the game draws a triangle from its front only - single-sided shader).
    Per shape: bmesh recalc (each island - faces joined over 2-face edges - gets one consistent winding, and a guess at
    outward); then each island is put to a vote by rays: from sampled faces, rays in a 60-degree cone round the normal
    and round its opposite are cast against ALL the item's shapes; the side whose rays escape more is outside, and an
    island whose back side wins is reversed. This fixes open surfaces too (a board's back face, a crest's back), which
    the recalc alone orients by guess (shield 1.0.0: its plank back and the crest's back faced the front - invisible
    from behind). Returns a report per shape."""
    import random
    from mathutils import Vector
    rnd = random.Random(seed)
    V, P, off = [], [], 0
    for o in objs:
        M = o.matrix_world; V += [M @ v.co for v in o.data.vertices]; P += [[off + i for i in p.vertices] for p in o.data.polygons]; off += len(o.data.vertices)
    tree = BVHTree.FromPolygons(V, P)
    def cone(n):
        while True:
            d = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1))).normalized()
            if d.dot(n) > 0.5: return d
    rep = {}
    for o in objs:
        me = o.data; before = [tuple(p.normal) for p in me.polygons]
        bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.normal_update()
        seen, islands = set(), []
        for f in bm.faces:
            if f.index in seen: continue
            isl, stack = [], [f]; seen.add(f.index)
            while stack:
                g = stack.pop(); isl.append(g)
                for e in g.edges:
                    if len(e.link_faces) != 2: continue
                    for h in e.link_faces:
                        if h.index not in seen: seen.add(h.index); stack.append(h)
            islands.append(isl)
        flipped, votes = 0, []
        for isl in islands:
            pick = isl if len(isl) <= samples else rnd.sample(isl, samples)
            sc = [0.0, 0.0]
            for f in pick:
                c = f.calc_center_median(); n = f.normal; a = f.calc_area()
                if n.length < 0.5 or a <= 0: continue
                for k, s in enumerate((1.0, -1.0)):
                    esc = 0
                    for _ in range(rays):
                        d = cone(n * s); hit = tree.ray_cast(c + n * s * 1e-3, d, 1000.0)
                        if hit[0] is None: esc += 1
                    sc[k] += a * esc / rays
            flip = sc[1] > sc[0]
            if flip:
                flipped += len(isl)
                bmesh.ops.reverse_faces(bm, faces=isl)   # on the bmesh only; written back when apply
            votes.append((len(isl), round(sc[0], 2), round(sc[1], 2), flip))
        bm.normal_update(); bm.faces.ensure_lookup_table(); after = [tuple(f.normal) for f in bm.faces]
        if apply: bm.to_mesh(me); me.update()
        changed = sum(1 for a, b in zip(before, after) if a[0] * b[0] + a[1] * b[1] + a[2] * b[2] < 0)
        bm.free()
        rep[o.name] = {"islands": len(islands), "faces": len(before), "faces_reversed_vs_input": changed,
                       "islands_flipped_by_ray_vote": sum(1 for v in votes if v[3]), "faces_in_flipped_islands": flipped,
                       "largest_islands (faces, out-score front, out-score back, flipped)": sorted(votes, key=lambda v: -v[0])[:8]}
        print("ORIENT", o.name, json.dumps(rep[o.name])[:400])
    return rep

# ------------------------------------------------------------------ import our shapes
clear()
for src in C["sources"]:
    before = set(bpy.data.objects); bpy.ops.import_scene.pynifly(filepath=src)
    for o in set(bpy.data.objects) - before:
        if o.type != "MESH": bpy.data.objects.remove(o)
shapes = {}
for role, sh in C["shapes"].items():
    o = bpy.data.objects[sh["name"]]; o.name = "dec_" + role
    orig = o.copy(); orig.data = o.data.copy(); orig.name = "orig_" + role; bpy.context.collection.objects.link(orig)
    n0 = decimate(o, sh.get("target"))
    V, F, UV = arrays(orig); np.savez(os.path.join(OUT, f"orig_{role}.npz"), V=V, F=F, UV=UV)
    V, F, UV = arrays(o); np.savez(os.path.join(OUT, f"dec_{role}.npz"), V=V, F=F, UV=UV)
    tree_o, tree_d = bvh(orig), bvh(o)
    s = {"tris_before": n0, "tris_after": tris_of(o)}
    s["dist_orig_to_dec_max"], s["dist_orig_to_dec_p95"] = surf_dist(orig, tree_d)
    s["dist_dec_to_orig_max"], s["dist_dec_to_orig_p95"] = surf_dist(o, tree_o)
    s["uv_shift_px_max"], s["uv_shift_px_p95"], s["uv_shift_px_p995"] = uv_shift(orig, o, sh.get("atlas_px", 2048))
    stats["shapes"][role] = s; shapes[role] = o
    print("STATS", role, json.dumps(s))

# ------------------------------------------------------------------ face orientation (outward, both shapes together)
if C.get("orient"):
    stats["orient"] = orient_outward(list(shapes.values()), apply=C["orient"] != "check")
    for role, o in shapes.items():   # the npz dumps carry the oriented winding
        V, F, UV = arrays(o); np.savez(os.path.join(OUT, f"dec_{role}.npz"), V=V, F=F, UV=UV)

# ------------------------------------------------------------------ the sheath ('Scb'): its own approved NIF, in the weapon's frame
# Welded and given sharp edges like the weapon's shapes, never decimated (the sheaths are ~2-4k triangles), oriented on
# its own (the blade inside it would block every ray of the weapon's vote, and the sheath's rays the weapon's).
if C.get("sheath"):
    before = set(bpy.data.objects); bpy.ops.import_scene.pynifly(filepath=C["sheath"])
    new = [o for o in set(bpy.data.objects) - before]
    sh_o = [o for o in new if o.type == "MESH"]
    for o in new:
        if o.type != "MESH": bpy.data.objects.remove(o)
    assert len(sh_o) == 1, [o.name for o in sh_o]
    sh_o = sh_o[0]; sh_o.name = "dec_sheath"
    n0 = decimate(sh_o, None)
    stats["sheath"] = {"source": C["sheath"], "tris_before": n0, "tris_after": tris_of(sh_o), "orient": orient_outward([sh_o])}
    V, F, UV = arrays(sh_o); np.savez(os.path.join(OUT, "dec_sheath.npz"), V=V, F=F, UV=UV)
    export_single(sh_o, os.path.join(OUT, "dec_sheath.nif"))
    bpy.data.objects.remove(sh_o)

# ------------------------------------------------------------------ blood shapes (from the decimated metal)
for i, bl in enumerate(C.get("blood", [])):
    b = make_blood(shapes[C.get("blood_from", "metal")], bl["region"], bl["uvbox"], f"blood{i}")
    stats.setdefault("blood", []).append({"name": bl["vanilla_name"], "tris": tris_of(b)})
    export_single(b, os.path.join(OUT, f"blood{i}.nif"))

# ------------------------------------------------------------------ export
if C.get("skinned"):
    # the bow: vanilla armature + weights
    before = set(bpy.data.objects); bpy.ops.import_scene.pynifly(filepath=C["vanilla_skin"], import_collisions=False)
    new = set(bpy.data.objects) - before
    arm = [o for o in new if o.type == "ARMATURE"][0]; vmesh = [o for o in new if o.type == "MESH" and o.vertex_groups][0]
    for role, o in shapes.items():
        for g in vmesh.vertex_groups: o.vertex_groups.new(name=g.name)
        select_only(o); m = o.modifiers.new("dt", "DATA_TRANSFER"); m.object = vmesh; m.use_vert_data = True
        m.data_types_verts = {"VGROUP_WEIGHTS"}; m.vert_mapping = "POLYINTERP_NEAREST"
        m.layers_vgroup_select_src = "ALL"; m.layers_vgroup_select_dst = "NAME"
        bpy.ops.object.modifier_apply(modifier=m.name)
        dom = {}
        for v in o.data.vertices:
            gs = [g for g in v.groups if o.vertex_groups[g.group].name.startswith("Bow_")]
            if gs:
                g = max(gs, key=lambda g: g.weight); dom[o.vertex_groups[g.group].name] = dom.get(o.vertex_groups[g.group].name, 0) + 1
        stats["shapes"][role]["dominant_bone_counts"] = dom
        if role == "string":   # where along the string each bone dominates (y ranges), to check against vanilla
            yr = {}
            for v in o.data.vertices:
                gs = [g for g in v.groups if o.vertex_groups[g.group].name.startswith("Bow_")]
                if gs:
                    n = o.vertex_groups[max(gs, key=lambda g: g.weight).group].name; y = (o.matrix_world @ v.co).y
                    r = yr.setdefault(n, [1e9, -1e9]); r[0] = min(r[0], y); r[1] = max(r[1], y)
            stats["shapes"][role]["string_bone_y"] = yr
        o.parent = arm; am = o.modifiers.new("arm", "ARMATURE"); am.object = arm
    keep = set(shapes.values()) | {arm}
    for o in list(bpy.data.objects):
        if o not in keep and o.type == "MESH": bpy.data.objects.remove(o)
    bpy.ops.object.select_all(action="DESELECT")
    for o in shapes.values(): o.select_set(True)
    arm.select_set(True); bpy.context.view_layer.objects.active = shapes["metal"]
    r = bpy.ops.export_scene.pynifly(filepath=os.path.join(OUT, "skinned.nif"), target_game="SKYRIMSE", export_colors=False, blender_xf=False, intuit_defaults=False)
    print("EXPORT skinned", r)
else:
    for role, o in shapes.items(): export_single(o, os.path.join(OUT, f"dec_{role}.nif"))
json.dump(stats, open(os.path.join(OUT, "blender_stats.json"), "w"), indent=1)
print("DONE", KEY)
