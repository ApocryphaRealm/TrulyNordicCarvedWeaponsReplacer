# render_review.py - large, textured review renders of one shipped weapon mesh for the owner to mark up
# (2026-11-11: "show me the battle axe for truly nordic, i want to alter it"). Front, side and three-quarter views,
# EEVEE with a neutral key/fill and a plain backdrop, each 1600 px tall.
# Run: blender --background --factory-startup --python render_review.py -- <mesh.nif> <out folder> <name>
import bpy, sys, os, addon_utils
from mathutils import Vector
nif, out, name = sys.argv[sys.argv.index("--") + 1:][:3]
os.makedirs(out, exist_ok=True)
addon_utils.enable("io_scene_nifly", default_set=True)
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.pynifly(filepath=nif, blender_xf=False, import_collisions=False)
ms = [o for o in bpy.data.objects if o.type == 'MESH']
pts = [o.matrix_world @ Vector(c) for o in ms for c in o.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
mid = (lo + hi) / 2; size = hi - lo
sc = bpy.context.scene
for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
    try: sc.render.engine = eng; break
    except TypeError: pass
if sc.world is None: sc.world = bpy.data.worlds.new("W")
sc.world.use_nodes = True
bg = sc.world.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (0.42, 0.42, 0.44, 1); bg.inputs["Strength"].default_value = 0.9
for nm, en, rot, col in (("Key", 4.0, (0.9, 0.2, 0.6), (1, 0.97, 0.92)), ("Fill", 1.5, (1.1, -0.3, -2.2), (0.85, 0.9, 1))):
    L = bpy.data.objects.new(nm, bpy.data.lights.new(nm, 'SUN')); sc.collection.objects.link(L)
    L.data.energy = en; L.data.color = col; L.rotation_euler = rot
cd = bpy.data.cameras.new("C"); cd.type = 'ORTHO'
cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
long_axis = max(range(3), key=lambda i: size[i])
cd.ortho_scale = size[long_axis] * 1.08
sc.render.resolution_y = 1600; sc.render.resolution_x = 1000; sc.render.image_settings.file_format = 'PNG'
up = Vector((0, 0, 0)); up[long_axis] = 1
# "front" looks at the flat of the head (along the thinnest axis); "side" looks along the remaining axis
side_axes = sorted([i for i in range(3) if i != long_axis], key=lambda i: size[i])
cd.ortho_scale = max(size[long_axis], size[side_axes[1]] * 1600 / 1000) * 1.12
d = max(size) * 4
views = {}
a, b = side_axes
for label, vec in (("front", (a, 1)), ("side", (b, 1))):
    v = Vector((0, 0, 0)); v[vec[0]] = vec[1]; views[label] = v
v = Vector((0, 0, 0)); v[a] = 0.7071; v[b] = 0.7071; views["threequarter"] = v
for label, v in views.items():
    cam.location = mid + v * d
    cam.rotation_euler = (mid - cam.location).to_track_quat('-Z', 'Y' if long_axis == 1 else 'Z' if long_axis == 2 else 'X').to_euler()
    sc.render.filepath = os.path.join(out, f"{name}_{label}.png"); bpy.ops.render.render(write_still=True)
print("REVIEW", name, "bounds", tuple(round(x, 1) for x in size), "->", out)
