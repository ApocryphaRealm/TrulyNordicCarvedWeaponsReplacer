# Assembles every game NIF of Truly Nordic Carved Weapons Replacer from the vanilla NIF's own structure (root, BSXFlags,
# BSInvMarker, the Prn extra data, the 1st-person mace's 'Scb', the blood-decal shapes' shaders and alpha) and our
# decimated shapes from gb_blender.py:
#   * the main shape takes our metal geometry, every further role (wrap, second wrap, string, shield board) is added as
#     a shape under the same parent, the blood shapes take our blood geometry (gb_blender.make_blood);
#   * every shape of ours gets PGPatcher's PLAIN TruePBR shader block (type 0, SLSF2 bit 23; read from PGPatcher's
#     1st-person Nordic sword 'Scb', exactly as A5c/A5d) and a texture set: 0 albedo, 1 normal, 5 RMAOS;
#   * the convex collision hull is rebuilt from our shapes (in the rigid body's own frame, Havok scale 1/69.99124),
#     at most 40 hull points; the dagger keeps vanilla's two-box list shape (its kukri sits inside the same boxes);
#   * a 1st-person NIF holds the same model moved by the offset between vanilla's 1st- and 3rd-person meshes
#     (battleaxe and greatsword; zero for the others);
#   * the bow: vanilla's skinned BowMesh is replaced by our three skinned shapes (weights from vanilla, BSDismember
#     SBP_32_BODY), each shape's skin bones re-pointed at vanilla's own bone nodes by name.
# Run: python -I assemble.py [item ...]     -> <WORK>\stage\<item>\meshes\...
import os, sys, json, struct, math
import numpy as np
from scipy.spatial import ConvexHull
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from items import ITEMS, WORK, MESH_REL, TEX_REL, VAN, vanilla_path
sys.path.insert(0, r"D:\Claude output\4. plans\nordic-double-bit-axe"); import niflib
# the plain TruePBR shader template. It was read from PGPatcher's output of the vanilla first-person Nordic sword (its "Scb"
# shape) in the Test profile's PGPatcher Output; a PGPatcher re-run with our Replacer installed (2026-11-14) no longer writes
# that file, so the block is kept in the repo: data\truepbr_plain_shader.bin = that template exactly as every staged shape
# of 1.3.0 carries it (name and texture-set refs -1, SLSF1 Skinned clear; identical on the sword, spear and crossbow shapes).
# PGP stays as the fallback source when the file is missing.
TEMPLATE_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "truepbr_plain_shader.bin")
PGP = r"D:\Modlists\Njordlinger\mods\PGPatcher Output - Njordlinger Test\meshes\dlc02\weapons\nordic\1stpersonnordicsword.nif"
HK = 69.99124
STAGE = os.path.join(WORK, "stage")
probe = json.load(open(os.path.join(WORK, "vanilla_probe.json")))
report = {}

def shapes_of(n): return [b for b, t in enumerate(n.btypes) if t == "BSTriShape"]
def only_shape(path):
    n = niflib.Nif(path); s = shapes_of(n); assert len(s) == 1, (path, s); return n, s[0]
def geometry_tail(n, b):
    o = n.av_end(b, 0, [], []); tail = bytearray(n.blocks[b][o:]); struct.pack_into("<3i", tail, 16, -1, -1, -1); return tail
def splice(n, b, tail, off=(0.0, 0.0, 0.0), rot=None):
    """off: the shape's translation; rot: its rotation (3x3, applied as R @ p + off, stored row-major), identity if None"""
    o = n.av_end(b, 0, [], []); head = bytearray(n.blocks[b][:o]); refs = struct.unpack_from("<3i", n.blocks[b], o + 16)
    t_off = n.transform(b)[0]
    R = (1, 0, 0, 0, 1, 0, 0, 0, 1) if rot is None else tuple(float(x) for x in np.asarray(rot).reshape(9))
    struct.pack_into("<3f", head, t_off, *off); struct.pack_into("<9f", head, t_off + 12, *R)
    struct.pack_into("<f", head, t_off + 48, 1.0)
    new = head + tail; struct.pack_into("<3i", new, o + 16, *refs); n.blocks[b] = new
def texset_block(paths):
    blk = struct.pack("<I", len(paths))
    for p in paths: e = p.encode("latin-1"); blk += struct.pack("<I", len(e)) + e
    return bytearray(blk)
def shader_of(n, b): return struct.unpack_from("<i", n.blocks[b], n.av_end(b, 0, [], []) + 20)[0]
def texset_of(n, sh): return n.i32(sh, n.ref_offsets(sh)[0][-1])
def parent_of(n, b):
    for p, t in enumerate(n.btypes):
        if t in niflib.NODES and b in n.children(p)[0]: return p
if os.path.isfile(TEMPLATE_BIN):
    T_PLAIN = bytearray(open(TEMPLATE_BIN, "rb").read())
    # the flags sit after the NiObjectNET head (name -1, no extra data, controller -1: 12 bytes) and the shader type (4)
    _f1, _f2 = struct.unpack_from("<II", T_PLAIN, 16)
else:
    pg = niflib.Nif(PGP)
    _sc = [b for b in shapes_of(pg) if pg.name(b) == "Scb"][0]; _sh = shader_of(pg, _sc)
    T_PLAIN = bytearray(pg.blocks[_sh]); struct.pack_into("<i", T_PLAIN, 12, -1)
    _f1, _f2 = struct.unpack_from("<II", T_PLAIN, pg.net_end(_sh, 4, [], []))
assert struct.unpack_from("<I", T_PLAIN, 0)[0] == 0 and _f2 & 0x00800000 and not _f1 & 0x2, "template is not the plain TruePBR block"

def tex_paths(item, role):
    stem = ITEMS[item]["stem"]; name = f"tn_{stem}" + ("" if role == "metal" else f"_{role}")
    b = f"{TEX_REL}\\{stem}\\{name}"
    return [b + ".dds", b + "_n.dds", "", "", "", b + "_rmaos.dds", "", "", ""]
def set_shader(n, sh, ts, name_idx):
    blk = bytearray(T_PLAIN); struct.pack_into("<i", blk, 4, name_idx); n.blocks[sh] = blk
    struct.pack_into("<i", n.blocks[sh], n.ref_offsets(sh)[0][-1], ts)
def new_string(n, s):
    n.strings.append(s); return len(n.strings) - 1
def append_child(n, parent, child):
    kids, off = n.children(parent); blk = n.blocks[parent]
    n.blocks[parent] = blk[:off] + struct.pack("<I", len(kids) + 1) + blk[off + 4:off + 4 + 4 * len(kids)] + struct.pack("<i", child) + blk[off + 4 + 4 * len(kids):]
def add_shape(n, main, tail, name, texset, off, rot=None):
    o = n.av_end(main, 0, [], []); head = bytearray(n.blocks[main][:o]); struct.pack_into("<i", head, 0, new_string(n, name))
    ts = len(n.blocks); n.btypes.append("BSShaderTextureSet"); n.blocks.append(texset_block(texset))
    sh = len(n.blocks); n.btypes.append("BSLightingShaderProperty"); n.blocks.append(bytearray(T_PLAIN))
    set_shader(n, sh, ts, -1)
    sb = len(n.blocks); n.btypes.append("BSTriShape"); n.blocks.append(head + tail)
    struct.pack_into("<3i", n.blocks[sb], o + 16, -1, sh, -1); splice(n, sb, tail, off, rot)
    struct.pack_into("<3i", n.blocks[sb], n.av_end(sb, 0, [], []) + 16, -1, sh, -1)
    append_child(n, parent_of(n, main), sb); return sb

def hip_xf(item, which):
    """The sheathed placement of a third-person NIF (items.py 'hip'): rotation R and translation t with p' = R p + t,
    a turn of rot_x_deg about the weapon's x axis through the pivot, then the shift. Identity for any other case."""
    h = ITEMS[item].get("hip")
    if which != "third" or not h: return None, np.zeros(3)
    a = math.radians(h["rot_x_deg"]); c, s = math.cos(a), math.sin(a)
    R = np.array([[1, 0, 0], [0, c, -s], [0, s, c]]); piv = np.array(h["pivot"], np.float64)
    return R, piv - R @ piv + np.array(h["shift"], np.float64)
def hull_points(item, off, rot=None):
    P = []
    for role in ITEMS[item]["shapes"]:
        P.append(np.load(os.path.join(WORK, item, f"dec_{role}.npz"))["V"])
    P = np.concatenate(P).astype(np.float64)
    P = (P if rot is None else P @ np.asarray(rot).T) + np.array(off)
    h = ConvexHull(P); Q = P[h.vertices]
    if len(Q) > 40:   # farthest-point sampling of the hull's own vertices, then the hull of those
        sel = [int(np.argmax(Q[:, 1])), int(np.argmin(Q[:, 1]))]; d = np.minimum(np.linalg.norm(Q - Q[sel[0]], axis=1), np.linalg.norm(Q - Q[sel[1]], axis=1))
        while len(sel) < 40:
            i = int(np.argmax(d)); sel.append(i); d = np.minimum(d, np.linalg.norm(Q - Q[i], axis=1))
        Q = Q[sel]
    return Q, P
def rewrite_collision(n, item, off, rot=None):
    cv = [b for b, t in enumerate(n.btypes) if t == "bhkConvexVerticesShape"]
    if not cv: return "kept vanilla (" + ",".join(sorted({t for t in n.btypes if t.startswith("bhk")})) + ")"
    b = cv[0]; blk = n.blocks[b]
    rb = [i for i, t in enumerate(n.btypes) if t.startswith("bhkRigidBody")][0]
    if n.btypes[rb] == "bhkRigidBodyT":   # only the T body places its shape by its translation and rotation
        t = np.array(struct.unpack_from("<3f", n.blocks[rb], 52), np.float64) * HK
        qx, qy, qz, qw = struct.unpack_from("<4f", n.blocks[rb], 68)
    else:
        # a plain body's translation/rotation fields are not a reliable frame (vanilla's greatsword holds 120 units of
        # x the game cannot be applying; the bow holds a 90-degree turn): zero them, so the hull is in the mesh frame
        # whichever way a reader treats them
        struct.pack_into("<3f", n.blocks[rb], 52, 0.0, 0.0, 0.0); struct.pack_into("<4f", n.blocks[rb], 68, 0.0, 0.0, 0.0, 1.0)
        t = np.zeros(3); qx, qy, qz, qw = 0.0, 0.0, 0.0, 1.0
    # the node the collision object hangs on places it (the bow's hangs on Bow_MidBone, turned 90 degrees): its world
    # transform, composed up the parent chain, is folded into t and R below
    co = [i for i, tt in enumerate(n.btypes) if tt == "bhkCollisionObject"][0]; node = struct.unpack_from("<i", n.blocks[co], 0)[0]
    NT, NR = np.zeros(3), np.eye(3); cur = node
    while cur is not None:
        _, tl, rl, sl = n.transform(cur); Rl = np.array(rl, np.float64).reshape(3, 3)
        NT, NR = Rl @ NT * sl + np.array(tl), Rl @ NR
        cur = parent_of(n, cur)
    R = np.array([[1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
                  [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
                  [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)]])
    Rr = R; R = NR @ Rr; t = NR @ t + NT          # body frame inside the node frame inside the world
    Q, P = hull_points(item, off, rot)
    L = ((Q - t) @ R) / HK                       # world -> the rigid body's frame, Havok units
    h = ConvexHull(L); eq = {}
    for e in h.equations: eq[tuple(np.round(e, 4))] = e
    E = np.array(list(eq.values()), np.float32); Lv = L[h.vertices].astype(np.float32)
    head = bytearray(blk[:32]); nv = len(Lv)
    body = struct.pack("<I", nv) + np.concatenate([Lv, np.zeros((nv, 1), np.float32)], 1).tobytes() + struct.pack("<I", len(E)) + E.tobytes()
    n.blocks[b] = head + body
    world_back = (Lv.astype(np.float64) * HK) @ R.T + t
    inside = float(((E[:, :3].astype(np.float64) @ (((P - t) @ R) / HK).T) + E[:, 3:4]).max())
    return {"hull_points": nv, "planes": len(E), "lo": np.round(world_back.min(0), 2).tolist(), "hi": np.round(world_back.max(0), 2).tolist(),
            "max_plane_eval_over_mesh": round(inside, 5), "rigid_body": n.btypes[rb], "collision_frame": "rotated" if not np.allclose(R, np.eye(3), atol=1e-4) else "identity", "node": n.name(node) if n.btypes[node] in niflib.NODES else n.btypes[node]}

def offset_1st(item):
    it = ITEMS[item]
    def main_box(path):
        d = probe[path.replace("\\", "/")]
        k = [k for k in d if "blood" not in k.lower() and not k.startswith("bhk") and k != "Scb"][0]; return np.array(d[k]["lo"]), np.array(d[k]["hi"])
    l3, h3 = main_box(vanilla_path(item, "third")); l1, h1 = main_box(vanilla_path(item, "first"))
    assert np.allclose(h3 - l3, h1 - l1, atol=0.08), (item, h3 - l3, h1 - l1)
    return tuple(float(x) for x in np.round((l1 + h1) / 2 - (l3 + h3) / 2, 4))

def build_static(item, which, out_path):
    it = ITEMS[item]; off = (0.0, 0.0, 0.0) if which == "third" else offset_1st(item)
    rot, t_hip = hip_xf(item, which)
    if rot is not None: off = tuple(float(x) for x in np.array(off) + t_hip)
    n = niflib.Nif(vanilla_path(item, which)); D = os.path.join(WORK, item); rep = {"offset": off}
    if rot is not None: rep["hip"] = dict(it["hip"], shape_rotation=np.round(rot, 6).tolist(), shape_translation=np.round(off, 4).tolist())
    shp = shapes_of(n); blood = [b for b in shp if "blood" in n.name(b).lower()]
    main = [b for b in shp if b not in blood and n.name(b) != "Scb"]; assert len(main) == 1, [n.name(b) for b in shp]; main = main[0]
    mn, mb = only_shape(os.path.join(D, "dec_metal.nif")); tail = geometry_tail(mn, mb)
    splice(n, main, tail, off, rot); sh = shader_of(n, main); ts = texset_of(n, sh)
    n.blocks[ts] = texset_block(tex_paths(item, "metal")); set_shader(n, sh, ts, struct.unpack_from("<i", n.blocks[sh], 4)[0])
    for role in it["shapes"]:
        if role == "metal": continue
        rn, rb = only_shape(os.path.join(D, f"dec_{role}.nif"))
        add_shape(n, main, geometry_tail(rn, rb), f"TN_{it['stem']}_{role}", tex_paths(item, role), off, rot)
    if it.get("sheath"):
        # our sheath as the shape the game knows by name: 'Scb' is left on the sheath node when the weapon is drawn
        assert not [b for b in shp if n.name(b) == "Scb"], f"{item}: vanilla already carries an Scb"
        sn, sb = only_shape(os.path.join(D, "dec_sheath.nif"))
        add_shape(n, main, geometry_tail(sn, sb), "Scb", tex_paths(item, "sheath"), off, rot)
        rep["sheath"] = it["sheath"]["version"]
    for i, b in enumerate(blood):
        bn, bb = only_shape(os.path.join(D, f"blood{min(i, 1)}.nif")); splice(n, b, geometry_tail(bn, bb), off, rot)
    rep["blood_shapes"] = [n.name(b) for b in blood]
    rep["kept_vanilla_shapes"] = [n.name(b) for b in shp if n.name(b) == "Scb"]
    rep["collision"] = rewrite_collision(n, item, off, rot)
    os.makedirs(os.path.dirname(out_path), exist_ok=True); n.save(out_path); niflib.Nif(out_path)
    rep["blocks"] = len(n.blocks); return rep

def build_bow(out_path):
    item = "bow"; n = niflib.Nif(vanilla_path(item, "third")); s = niflib.Nif(os.path.join(WORK, item, "skinned.nif"))
    bones_v = {n.name(b): b for b, t in enumerate(n.btypes) if t == "NiNode"}
    main = [b for b in shapes_of(n) if n.name(b) == "BowMesh:0"][0]
    roles = {"metal": "dec_metal", "wrap": "dec_wrap", "string": "dec_string"}
    src_sh = {n2: b for b in shapes_of(s) for n2 in [s.name(b)]}
    vskin = n.i32(main, n.av_end(main, 0, [], []) + 16)
    vdata, vpart = struct.unpack_from("<ii", n.blocks[vskin], 0)
    rep = {}
    for role, sname in roles.items():
        sb = src_sh[sname]; so = s.av_end(sb, 0, [], [])
        sk = s.i32(sb, so + 16); sd, sp = struct.unpack_from("<ii", s.blocks[sk], 0)
        assert s.btypes[sk] == "BSDismemberSkinInstance", s.btypes[sk]
        if role == "metal":
            idx_shape, idx_skin, idx_data, idx_part = main, vskin, vdata, vpart
            sh = shader_of(n, main); ts = texset_of(n, sh); nm = struct.unpack_from("<i", n.blocks[main], 0)[0]
        else:
            idx_shape, idx_skin, idx_data, idx_part = (len(n.blocks) + i for i in range(4))
            for t in ("BSTriShape", "BSDismemberSkinInstance", "NiSkinData", "NiSkinPartition"): n.btypes.append(t); n.blocks.append(bytearray())
            ts = len(n.blocks); n.btypes.append("BSShaderTextureSet"); n.blocks.append(bytearray())
            sh = len(n.blocks); n.btypes.append("BSLightingShaderProperty"); n.blocks.append(bytearray(T_PLAIN))
            nm = new_string(n, f"TN_bow_{role}")
            append_child(n, parent_of(n, main), idx_shape)
        # shape: our block with its name, skin/shader/alpha refs re-pointed
        blk = bytearray(s.blocks[sb]); struct.pack_into("<i", blk, 0, nm); struct.pack_into("<3i", blk, so + 16, idx_skin, sh, -1)
        # its NiAVObject flags/transform as vanilla's BowMesh (identity in both), extra data list and controller: none
        n.btypes[idx_shape] = "BSTriShape"; n.blocks[idx_shape] = blk
        k = bytearray(s.blocks[sk]); struct.pack_into("<iii", k, 0, idx_data, idx_part, 0)
        nb = struct.unpack_from("<I", k, 12)[0]; names = []
        for j in range(nb):
            bi = struct.unpack_from("<i", k, 16 + 4 * j)[0]; nmj = s.name(bi); names.append(nmj)
            struct.pack_into("<i", k, 16 + 4 * j, bones_v[nmj])
        n.btypes[idx_skin] = "BSDismemberSkinInstance"; n.blocks[idx_skin] = k
        n.btypes[idx_data] = "NiSkinData"; n.blocks[idx_data] = bytearray(s.blocks[sd])
        n.btypes[idx_part] = "NiSkinPartition"; n.blocks[idx_part] = bytearray(s.blocks[sp])
        n.blocks[ts] = texset_block(tex_paths(item, role)); set_shader(n, sh, ts, struct.unpack_from("<i", n.blocks[sh], 4)[0] if role == "metal" else -1)
        # a skinned shape needs SLSF1 Skinned (0x2) - the plain template is from a rigid weapon, and without the flag the engine
        # draws nothing and the bow's 3D never finishes attaching (2026-11-11: invisible bow, equip motion stalls halfway)
        fo = n.net_end(sh, 4, [], []); f1 = struct.unpack_from("<I", n.blocks[sh], fo)[0]; struct.pack_into("<I", n.blocks[sh], fo, f1 | 0x2)
        # NiAVObject flags as vanilla's BowMesh (0xE); pynifly writes 0
        ne = struct.unpack_from("<I", n.blocks[idx_shape], 4)[0]; struct.pack_into("<I", n.blocks[idx_shape], 8 + 4 * ne + 4, 0xE)
        rep[role] = {"bones": names}
    rep["collision"] = rewrite_collision(n, item, (0.0, 0.0, 0.0))
    os.makedirs(os.path.dirname(out_path), exist_ok=True); n.save(out_path); niflib.Nif(out_path)
    rep["blocks"] = len(n.blocks); return rep

def set_box(n, body, P):
    """A vanilla bhkBoxShape + bhkRigidBodyT fitted to points P (in the frame of the node the collision hangs on): the
    T body places its box by its translation (Havok units) and rotation; vanilla's arrow and quiver bodies turn the box
    180 degrees about z (a box is symmetric under it), so only the centre and the half extents change. Refuses any other
    rotation rather than guessing an orientation."""
    qx, qy, qz, qw = struct.unpack_from("<4f", n.blocks[body], 68)
    assert abs(abs(qz) - 1) < 1e-4 or abs(abs(qw) - 1) < 1e-4, ("box body rotation is not 0 / 180 about z", qx, qy, qz, qw)
    box = struct.unpack_from("<i", n.blocks[body], 0)[0]; assert n.btypes[box] == "bhkBoxShape", n.btypes[box]
    lo, hi = P.min(0), P.max(0); c, h = (lo + hi) / 2, (hi - lo) / 2
    before = dict(centre=np.round(np.array(struct.unpack_from("<3f", n.blocks[body], 52)) * HK, 3).tolist(), half=np.round(np.array(struct.unpack_from("<3f", n.blocks[box], 16)) * HK, 3).tolist())
    struct.pack_into("<3f", n.blocks[body], 52, *(c / HK)); struct.pack_into("<3f", n.blocks[box], 16, *(h / HK))
    return dict(before=before, after=dict(centre=np.round(c, 3).tolist(), half=np.round(h, 3).tolist()))

def build_quiver(root):
    """nordicarrow.nif (the AMMO's model) and nordicarrowflight.nif (the PROJ's) on vanilla's own structure: every shape
    name, node, extra data, alpha property, tracer node and controller kept; our geometry spliced into vanilla's shapes
    (identity shape transforms - gb_quiver's geometry is in the NIF root frame, as vanilla's shapes end up after theirs),
    each with the plain TruePBR shader and its own texture set; the quiver's leather added as a second shape under
    'ArrowQuiver'; the five arrows in the quiver go to Arrow1..Arrow5 by nearest position; collision boxes refitted."""
    it = ITEMS["quiver"]; D = os.path.join(WORK, "quiver"); rep = {}
    import winding
    def shape(n, name): return [b for b in shapes_of(n) if n.name(b) == name][0]
    def put(n, b, role, ts_reuse=None):
        sn, sb = only_shape(os.path.join(D, f"dec_{role}.nif")); splice(n, b, geometry_tail(sn, sb))
        sh = shader_of(n, b); tex = tex_paths("quiver", "arrow" if role.startswith("arrow") else role)
        if ts_reuse is None: ts = len(n.blocks); n.btypes.append("BSShaderTextureSet"); n.blocks.append(texset_block(tex))
        else: ts = ts_reuse; n.blocks[ts] = texset_block(tex)
        set_shader(n, sh, ts, struct.unpack_from("<i", n.blocks[sh], 4)[0]); return ts
    def centre_world(n, b):
        V, _ = winding._tris_from_shape(n, b); _, t, r, s = n.transform(b)
        W = (np.array(r, np.float64).reshape(3, 3) @ V.T).T * s + np.array(t); return (W.min(0) + W.max(0)) / 2
    # ---- nordicarrow.nif
    n = niflib.Nif(os.path.join(VAN, it["third"]))
    van = {nm: centre_world(n, shape(n, nm)) for nm in ("Arrow1", "Arrow2", "Arrow3", "Arrow4", "Arrow5")}
    ours = {r: (lambda V: (V.min(0) + V.max(0)) / 2)(np.load(os.path.join(D, f"dec_{r}.npz"))["V"].astype(np.float64)) for r in it["arrows_in_quiver"]}
    # nearest pairs by the position across the quiver (x, z), greedily from the closest pair: the game's own order of
    # which arrow goes first as the count drops stays where vanilla had it
    pairs, free_v, free_o = {}, set(van), set(ours)
    while free_v:
        d, a, b = min((float(np.hypot(*(van[a][[0, 2]] - ours[b][[0, 2]]))), a, b) for a in free_v for b in free_o)
        pairs[a] = b; free_v.discard(a); free_o.discard(b)
    ts0 = texset_of(n, shader_of(n, shape(n, "ArrowQuiver:0")))      # vanilla's one shared set, reused for the quiver steel
    put(n, shape(n, "ArrowQuiver:0"), "metal", ts_reuse=ts0)
    put(n, shape(n, "Arrow:0"), "arrow")
    for a, r in sorted(pairs.items()): put(n, shape(n, a), r)
    ln, lb = only_shape(os.path.join(D, "dec_leather.nif"))
    add_shape(n, shape(n, "ArrowQuiver:0"), geometry_tail(ln, lb), "TN_quiver_leather", tex_paths("quiver", "leather"), (0.0, 0.0, 0.0))
    # collision: the root's body (the loose arrow) and ArrowQuiver's body (the quiver)
    bodies = {}
    for co in [i for i, t in enumerate(n.btypes) if t == "bhkCollisionObject"]:
        node, _, body = struct.unpack_from("<iHi", n.blocks[co], 0); bodies[n.name(node)] = body
    L = lambda *rs: np.concatenate([np.load(os.path.join(D, f"dec_{r}.npz"))["V"] for r in rs]).astype(np.float64)
    coll = {"Arrow (root) - loose arrow": set_box(n, bodies["Arrow"], L("arrow")), "ArrowQuiver - quiver": set_box(n, bodies["ArrowQuiver"], L("metal", "leather"))}
    out = os.path.join(root, MESH_REL, "quiver", "quiver.nif"); os.makedirs(os.path.dirname(out), exist_ok=True); n.save(out); niflib.Nif(out)
    rep["third"] = dict(path=os.path.relpath(out, root), arrows=pairs, collision=coll, blocks=len(n.blocks))
    # ---- nordicarrowflight.nif
    f = niflib.Nif(os.path.join(VAN, it["flight"]))
    b = shape(f, "SteelArrowFlight:0"); put(f, b, "arrow", ts_reuse=texset_of(f, shader_of(f, b)))
    co = [i for i, t in enumerate(f.btypes) if t == "bhkCollisionObject"][0]; body = struct.unpack_from("<iHi", f.blocks[co], 0)[2]
    fc = set_box(f, body, L("arrow"))
    out2 = os.path.join(root, MESH_REL, "quiver", "arrowflight.nif"); f.save(out2); niflib.Nif(out2)
    import shutil; p = os.path.join(root, r"meshes\dlc02\weapons\nordic", it["flight"]); os.makedirs(os.path.dirname(p), exist_ok=True); shutil.copy2(out2, p)
    rep["flight"] = dict(path=os.path.relpath(out2, root), vanilla_path_copy=os.path.relpath(p, root), collision=fc, blocks=len(f.blocks),
                         kept=[f.name(i) for i in range(len(f.blocks)) if f.btypes[i] in niflib.NODES or f.btypes[i] == "BSTriShape"])
    return rep

def build_boltquiver(root):
    """boltquiver.nif (the bolt AMMO's model) and boltflight.nif (its PROJ's) on vanilla Dawnguard steelbolt.nif /
    boltprojectile.nif's own structure: every node, shape name, transform, extra data, alpha property, the tracer's effect
    shaders, controller and the collision kept byte for byte (vanilla's boxes fit ours: case 16.2 long vs 16.8, bolt 21.0
    vs 21.1); our geometry spliced into vanilla's shapes WITH vanilla's own shape transforms (gb_boltquiver.py moved it
    into each shape's local frame); each shape the plain TruePBR shader; the case's leather a second shape under
    ArrowQuiver in ArrowQuiver:1's frame. Paths: meshes\\TrulyNordic\\boltquiver\\ (a new item - nothing at a vanilla path)."""
    D = os.path.join(WORK, "boltquiver"); it = ITEMS["boltquiver"]; rep = {}
    def shape(n, name): return [b for b in shapes_of(n) if n.name(b) == name][0]
    def put(n, b, role, ts):
        sn, sb = only_shape(os.path.join(D, f"dec_{role}.nif")); _, t, r, _s = n.transform(b)
        splice(n, b, geometry_tail(sn, sb), tuple(t), np.array(r, np.float64).reshape(3, 3))
        sh = shader_of(n, b); set_shader(n, sh, ts, struct.unpack_from("<i", n.blocks[sh], 4)[0])
    def new_ts(n, role):
        ts = len(n.blocks); n.btypes.append("BSShaderTextureSet"); n.blocks.append(texset_block(tex_paths("boltquiver", role))); return ts
    n = niflib.Nif(os.path.join(it["van_dir"], it["third"]))
    ts_q = texset_of(n, shader_of(n, shape(n, "ArrowQuiver:1"))); n.blocks[ts_q] = texset_block(tex_paths("boltquiver", "metal"))   # vanilla's one shared set -> the case steel
    ts_b = new_ts(n, "bolt")                                                                                                   # one set for every bolt
    put(n, shape(n, "ArrowQuiver:1"), "metal", ts_q); put(n, shape(n, "Arrow:0"), "bolt", ts_b)
    for k in range(1, 5): put(n, shape(n, f"Arrow{k}"), f"Arrow{k}", ts_b)
    qb = shape(n, "ArrowQuiver:1"); _, t, r, _s = n.transform(qb); ln, lb = only_shape(os.path.join(D, "dec_leather.nif"))
    add_shape(n, qb, geometry_tail(ln, lb), "TN_boltquiver_leather", tex_paths("boltquiver", "leather"), tuple(t), np.array(r, np.float64).reshape(3, 3))
    out = os.path.join(root, MESH_REL, "boltquiver", "boltquiver.nif"); os.makedirs(os.path.dirname(out), exist_ok=True); n.save(out); niflib.Nif(out)
    rep["third"] = dict(path=os.path.relpath(out, root), blocks=len(n.blocks), slots=json.load(open(os.path.join(D, "blender_stats.json")))["slots"], collision="kept vanilla (two bhkBoxShape)")
    f = niflib.Nif(os.path.join(it["van_dir"], it["flight"])); b = shape(f, "SteelBoltFlight:0")
    ts = texset_of(f, shader_of(f, b)); f.blocks[ts] = texset_block(tex_paths("boltquiver", "bolt")); put(f, b, "flight", ts)
    out2 = os.path.join(root, MESH_REL, "boltquiver", "boltflight.nif"); f.save(out2); niflib.Nif(out2)
    rep["flight"] = dict(path=os.path.relpath(out2, root), blocks=len(f.blocks), collision="kept vanilla (bhkBoxShape)",
                         kept=[f.name(i) for i in range(len(f.blocks)) if f.btypes[i] in niflib.NODES or f.btypes[i] == "BSTriShape"])
    return rep

def build_crossbow(out_path):
    """crossbow.nif on vanilla Dawnguard crossbow.nif's own structure: the root, BSBehaviorGraphExtraData, BSInvMarker,
    BSXFlags, Prn 'WeaponBow', every bone node and its transform, the 7 NiTransformControllers / interpolators / data
    kept byte for byte; vanilla's one skinned shape Crossbow:0 replaced by our three (metal, soft, wrap - gb_crossbow.py's
    skinned.nif), each with its NiSkinInstance (vanilla's type), NiSkinData and NiSkinPartition, the skin bones
    re-pointed at vanilla's own bone nodes by name; the plain TruePBR shader with SLSF1 Skinned; the convex hull rebuilt."""
    item = "crossbow"; it = ITEMS[item]; n = niflib.Nif(os.path.join(it["van_dir"], it["third"]))
    s = niflib.Nif(os.path.join(WORK, item, "skinned.nif"))
    bones_v = {n.name(b): b for b, t in enumerate(n.btypes) if t == "NiNode"}
    main = [b for b in shapes_of(n) if n.name(b) == "Crossbow:0"][0]
    ne0 = struct.unpack_from("<I", n.blocks[main], 4)[0]; vflags = struct.unpack_from("<I", n.blocks[main], 8 + 4 * ne0 + 4)[0]
    vskin = n.i32(main, n.av_end(main, 0, [], []) + 16); vdata, vpart = struct.unpack_from("<ii", n.blocks[vskin], 0)
    src_sh = {s.name(b): b for b in shapes_of(s)}; rep = {}
    for role in ("metal", "soft", "wrap"):
        sb = src_sh[role]; so = s.av_end(sb, 0, [], []); sk = s.i32(sb, so + 16); sd, sp = struct.unpack_from("<ii", s.blocks[sk], 0)
        assert s.btypes[sk] in ("NiSkinInstance", "BSDismemberSkinInstance"), s.btypes[sk]
        if role == "metal":
            idx_shape, idx_skin, idx_data, idx_part = main, vskin, vdata, vpart
            sh = shader_of(n, main); ts = texset_of(n, sh); nm = struct.unpack_from("<i", n.blocks[main], 0)[0]
        else:
            idx_shape, idx_skin, idx_data, idx_part = (len(n.blocks) + i for i in range(4))
            for t in ("BSTriShape", "NiSkinInstance", "NiSkinData", "NiSkinPartition"): n.btypes.append(t); n.blocks.append(bytearray())
            ts = len(n.blocks); n.btypes.append("BSShaderTextureSet"); n.blocks.append(bytearray())
            sh = len(n.blocks); n.btypes.append("BSLightingShaderProperty"); n.blocks.append(bytearray(T_PLAIN))
            nm = new_string(n, f"TN_crossbow_{role}"); append_child(n, parent_of(n, main), idx_shape)
        blk = bytearray(s.blocks[sb]); struct.pack_into("<i", blk, 0, nm); struct.pack_into("<3i", blk, so + 16, idx_skin, sh, -1)
        n.btypes[idx_shape] = "BSTriShape"; n.blocks[idx_shape] = blk
        k = bytearray(s.blocks[sk]); nb = struct.unpack_from("<I", k, 12)[0]; k = k[:16 + 4 * nb]     # NiSkinInstance (vanilla's type)
        struct.pack_into("<iii", k, 0, idx_data, idx_part, 0); names = []
        for j in range(nb):
            nmj = s.name(struct.unpack_from("<i", k, 16 + 4 * j)[0]); names.append(nmj); struct.pack_into("<i", k, 16 + 4 * j, bones_v[nmj])
        n.btypes[idx_skin] = "NiSkinInstance"; n.blocks[idx_skin] = k
        n.btypes[idx_data] = "NiSkinData"; n.blocks[idx_data] = bytearray(s.blocks[sd])
        n.btypes[idx_part] = "NiSkinPartition"; n.blocks[idx_part] = bytearray(s.blocks[sp])
        n.blocks[ts] = texset_block(tex_paths(item, role)); set_shader(n, sh, ts, struct.unpack_from("<i", n.blocks[sh], 4)[0] if role == "metal" else -1)
        fo = n.net_end(sh, 4, [], []); f1 = struct.unpack_from("<I", n.blocks[sh], fo)[0]; struct.pack_into("<I", n.blocks[sh], fo, f1 | 0x2)   # SLSF1 Skinned
        ne = struct.unpack_from("<I", n.blocks[idx_shape], 4)[0]; struct.pack_into("<I", n.blocks[idx_shape], 8 + 4 * ne + 4, vflags)       # vanilla's NiAVObject flags
        rep[role] = {"bones": names}
    rep["collision"] = rewrite_collision(n, item, (0.0, 0.0, 0.0))
    os.makedirs(os.path.dirname(out_path), exist_ok=True); n.save(out_path); niflib.Nif(out_path)
    rep["blocks"] = len(n.blocks); rep["path"] = out_path; return rep

def build(item):
    it = ITEMS[item]; root = os.path.join(STAGE, item); rep = {}
    if item == "crossbow":
        rep = build_crossbow(os.path.join(root, MESH_REL, "crossbow", "crossbow.nif")); json.dump(rep, open(os.path.join(WORK, item, "assemble_report.json"), "w"), indent=1)
        print(item, json.dumps(rep)[:900]); return
    if item == "boltquiver":
        rep = build_boltquiver(root); json.dump(rep, open(os.path.join(WORK, item, "assemble_report.json"), "w"), indent=1)
        print(item, json.dumps(rep)[:900]); return
    if item == "quiver":
        rep = build_quiver(root); json.dump(rep, open(os.path.join(WORK, item, "assemble_report.json"), "w"), indent=1)
        print(item, json.dumps(rep)[:900]); return
    if item == "bow":
        rep["third"] = build_bow(os.path.join(root, MESH_REL, it["stem"], it["stem"] + ".nif"))
        # 1st-person: the STAT 1stPersonDLC2NordicBow points at the vanilla 3rd-person path, so the same file goes there
        import shutil; p = os.path.join(root, r"meshes\dlc02\weapons\nordic\nordicbow.nif"); os.makedirs(os.path.dirname(p), exist_ok=True)
        shutil.copy2(os.path.join(root, MESH_REL, it["stem"], it["stem"] + ".nif"), p); rep["first"] = "copy at meshes\\dlc02\\weapons\\nordic\\nordicbow.nif"
    elif item.startswith("shield"):
        rep["third"] = build_static(item, "third", os.path.join(root, r"meshes\dlc02\armor\nordicshield\nordicshield.nif"))
    else:
        rep["third"] = build_static(item, "third", os.path.join(root, MESH_REL, it["stem"], it["stem"] + ".nif"))
        if it.get("new_item"):   # a new item (the spear): its own first-person file at our path, read by its STAT; no vanilla path
            rep["first"] = build_static(item, "first", os.path.join(root, MESH_REL, it["stem"], "1stperson" + it["stem"] + ".nif"))
        else:
            rep["first"] = build_static(item, "first", os.path.join(root, r"meshes\dlc02\weapons\nordic", it["first"]))
    json.dump(rep, open(os.path.join(WORK, item, "assemble_report.json"), "w"), indent=1)
    print(item, json.dumps(rep)[:700])

if __name__ == "__main__":
    for k in (sys.argv[1:] or list(ITEMS)): build(k)
