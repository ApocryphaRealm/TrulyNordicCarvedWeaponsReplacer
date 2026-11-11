# Probe: import NIFs with PyNifly and write each mesh object's counts, world bounds and UV bounds to a JSON file.
# Run: blender --background --factory-startup --python-exit-code 1 --python probe_blender.py -- <out.json> <nif> [<nif>...]
import bpy, sys, json, addon_utils
import numpy as np
args = sys.argv[sys.argv.index("--") + 1:]
addon_utils.enable("io_scene_nifly", default_set=True)
res = {}
for p in args[1:]:
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    bpy.ops.import_scene.pynifly(filepath=p)
    r = res[p] = {}
    for o in bpy.data.objects:
        if o.type != "MESH": continue
        me = o.data; M = o.matrix_world
        V = np.array([list(M @ v.co) for v in me.vertices])
        d = {"verts": len(V), "tris": sum(len(q.vertices) - 2 for q in me.polygons), "lo": V.min(0).tolist(), "hi": V.max(0).tolist()}
        if me.uv_layers:
            U = np.array([list(l.uv) for l in me.uv_layers[0].data]); d["uvlo"] = U.min(0).tolist(); d["uvhi"] = U.max(0).tolist()
        r[o.name] = d
json.dump(res, open(args[0], "w"), indent=1)
for p, r in res.items():
    print("==", p)
    for k, d in r.items(): print("  ", k, d["tris"], [round(x, 2) for x in d["lo"]], [round(x, 2) for x in d["hi"]], [round(x, 3) for x in d.get("uvlo", [])], [round(x, 3) for x in d.get("uvhi", [])])
