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
from items import ITEMS, WORK, MESH_REL, TEX_REL, vanilla_path
sys.path.insert(0, r"D:\Claude output\4. plans\nordic-double-bit-axe"); import niflib
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
def splice(n, b, tail, off=(0.0, 0.0, 0.0)):
    o = n.av_end(b, 0, [], []); head = bytearray(n.blocks[b][:o]); refs = struct.unpack_from("<3i", n.blocks[b], o + 16)
    t_off = n.transform(b)[0]
    struct.pack_into("<3f", head, t_off, *off); struct.pack_into("<9f", head, t_off + 12, 1, 0, 0, 0, 1, 0, 0, 0, 1)
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
pg = niflib.Nif(PGP)
_sc = [b for b in shapes_of(pg) if pg.name(b) == "Scb"][0]; _sh = shader_of(pg, _sc)
T_PLAIN = bytearray(pg.blocks[_sh]); struct.pack_into("<i", T_PLAIN, 12, -1)
_f1, _f2 = struct.unpack_from("<II", T_PLAIN, pg.net_end(_sh, 4, [], []))
assert struct.unpack_from("<I", T_PLAIN, 0)[0] == 0 and _f2 & 0x00800000, "template is not the plain TruePBR block"

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
def add_shape(n, main, tail, name, texset, off):
    o = n.av_end(main, 0, [], []); head = bytearray(n.blocks[main][:o]); struct.pack_into("<i", head, 0, new_string(n, name))
    ts = len(n.blocks); n.btypes.append("BSShaderTextureSet"); n.blocks.append(texset_block(texset))
    sh = len(n.blocks); n.btypes.append("BSLightingShaderProperty"); n.blocks.append(bytearray(T_PLAIN))
    set_shader(n, sh, ts, -1)
    sb = len(n.blocks); n.btypes.append("BSTriShape"); n.blocks.append(head + tail)
    struct.pack_into("<3i", n.blocks[sb], o + 16, -1, sh, -1); splice(n, sb, tail, off)
    struct.pack_into("<3i", n.blocks[sb], n.av_end(sb, 0, [], []) + 16, -1, sh, -1)
    append_child(n, parent_of(n, main), sb); return sb

def hull_points(item, off):
    P = []
    for role in ITEMS[item]["shapes"]:
        P.append(np.load(os.path.join(WORK, item, f"dec_{role}.npz"))["V"])
    P = np.concatenate(P).astype(np.float64) + np.array(off)
    h = ConvexHull(P); Q = P[h.vertices]
    if len(Q) > 40:   # farthest-point sampling of the hull's own vertices, then the hull of those
        sel = [int(np.argmax(Q[:, 1])), int(np.argmin(Q[:, 1]))]; d = np.minimum(np.linalg.norm(Q - Q[sel[0]], axis=1), np.linalg.norm(Q - Q[sel[1]], axis=1))
        while len(sel) < 40:
            i = int(np.argmax(d)); sel.append(i); d = np.minimum(d, np.linalg.norm(Q - Q[i], axis=1))
        Q = Q[sel]
    return Q, P
def rewrite_collision(n, item, off):
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
    Q, P = hull_points(item, off)
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
    n = niflib.Nif(vanilla_path(item, which)); D = os.path.join(WORK, item); rep = {"offset": off}
    shp = shapes_of(n); blood = [b for b in shp if "blood" in n.name(b).lower()]
    main = [b for b in shp if b not in blood and n.name(b) != "Scb"]; assert len(main) == 1, [n.name(b) for b in shp]; main = main[0]
    mn, mb = only_shape(os.path.join(D, "dec_metal.nif")); tail = geometry_tail(mn, mb)
    splice(n, main, tail, off); sh = shader_of(n, main); ts = texset_of(n, sh)
    n.blocks[ts] = texset_block(tex_paths(item, "metal")); set_shader(n, sh, ts, struct.unpack_from("<i", n.blocks[sh], 4)[0])
    for role in it["shapes"]:
        if role == "metal": continue
        rn, rb = only_shape(os.path.join(D, f"dec_{role}.nif"))
        add_shape(n, main, geometry_tail(rn, rb), f"TN_{it['stem']}_{role}", tex_paths(item, role), off)
    for i, b in enumerate(blood):
        bn, bb = only_shape(os.path.join(D, f"blood{min(i, 1)}.nif")); splice(n, b, geometry_tail(bn, bb), off)
    rep["blood_shapes"] = [n.name(b) for b in blood]
    rep["kept_vanilla_shapes"] = [n.name(b) for b in shp if n.name(b) == "Scb"]
    rep["collision"] = rewrite_collision(n, item, off)
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
        rep[role] = {"bones": names}
    rep["collision"] = rewrite_collision(n, item, (0.0, 0.0, 0.0))
    os.makedirs(os.path.dirname(out_path), exist_ok=True); n.save(out_path); niflib.Nif(out_path)
    rep["blocks"] = len(n.blocks); return rep

def build(item):
    it = ITEMS[item]; root = os.path.join(STAGE, item); rep = {}
    if item == "bow":
        rep["third"] = build_bow(os.path.join(root, MESH_REL, it["stem"], it["stem"] + ".nif"))
        # 1st-person: the STAT 1stPersonDLC2NordicBow points at the vanilla 3rd-person path, so the same file goes there
        import shutil; p = os.path.join(root, r"meshes\dlc02\weapons\nordic\nordicbow.nif"); os.makedirs(os.path.dirname(p), exist_ok=True)
        shutil.copy2(os.path.join(root, MESH_REL, it["stem"], it["stem"] + ".nif"), p); rep["first"] = "copy at meshes\\dlc02\\weapons\\nordic\\nordicbow.nif"
    elif item == "shield":
        rep["third"] = build_static(item, "third", os.path.join(root, r"meshes\dlc02\armor\nordicshield\nordicshield.nif"))
    else:
        rep["third"] = build_static(item, "third", os.path.join(root, MESH_REL, it["stem"], it["stem"] + ".nif"))
        rep["first"] = build_static(item, "first", os.path.join(root, r"meshes\dlc02\weapons\nordic", it["first"]))
    json.dump(rep, open(os.path.join(WORK, item, "assemble_report.json"), "w"), indent=1)
    print(item, json.dumps(rep)[:700])

if __name__ == "__main__":
    for k in (sys.argv[1:] or list(ITEMS)): build(k)
