r"""The Ebony quality LOOK of Truly Nordic (1.3.0, 2026-11-13): black ebony steel with gold knotwork and gold haft rings.

The owner, 2026-11-13 19:50 (the study): "turning the Ebony Nordic set black and make the weave and braid golden with dark
shading, but still shiny. And keep the regular shading around the knitting so that it has contrast"; 20:26, choosing:
"let's go with the full gold and not the alternating gold and black design and I want the pole arms rings on the pole
around the handle to also be gold". Study, method and sheets: 4. plans\nordic-carved-redesign-20261110\set2\
ebony-blackgold-20261113\ (variant A there = this file; the alternating variant B was not chosen and is not built).

MASKS come from the painter's own HEIGHT map (tn_knot.maps_v3 "_height" = clip(H / depth + 1, 0, 1)), never from colour:
    floor   height <= ~40/255   the carving's recess floors              -> kept exactly as painted (near black)
    strand  ~80..248            the rounded strand tops                   -> GOLD
    flush   >= 252              plain steel, margins, polished bevels     -> black ebony steel, glossy (bevels: dark-grey sheen)
    thin flush rims under ~7 px between carvings, and the medallion ring  -> GOLD
HAFT RINGS come from the MESH (WORK\<item>\orig_metal.npz, the shapes the atlas was painted for): every separate mesh part
that encircles the haft - short along the weapon's long axis (<= 2.0 units and <= 0.8 x its width), round (its two cross
widths within 1.4x), and open in the middle (no vertex nearer its centre than 0.35 x its outer radius: the haft passes
through it) - is rasterised from its UV triangles into a mask and painted gold (floors inside it, e.g. knurl grooves, stay
as painted). Rivets, pommels, sockets and caps fail one of the three tests. ring_parts() prints what it found.
Only metal pixels (RMAOS G >= 0.5) change; leather, wood, string and wraps are untouched (an atlas with no metal is copied).
Normal maps are the shared build's DDS, copied (the relief is the same).

OUTPUT (the build's stage, beside the shared files; build-packages.py ships it in the Ebony quality files only):
    <STAGE>\textures\pbr\TrulyNordic\ebony\<stem>\tn_<stem>[_role].dds
    <STAGE>\ebony\<item>\meshes\TrulyNordic\ebony\<at>\<file>.nif   (copies of the shared NIFs, texture paths -> ebony)
    <WORK>\ebony\<item>\tex\*.png                                  (the recoloured maps, with the height map beside them)
    <WORK>\ebony\masks\*.jpg, <WORK>\ebony\ebony_report.json, <WORK>\ebony\medallion_check.json (ebony-mode measure)
Run after textures.py and assemble.py:  python -I ebony.py [item ...]
                                        python -I ebony.py --plugins   (the Ebony plugins' model paths; also run by
                                        standalone_finish.py and additional_records.py)
                                        python -I ebony.py --rings     (print the haft rings found per item)
"""
import os, sys, json, shutil, struct
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from items import ITEMS, WORK, MESH_REL, TEX_REL, S2
import textures as TX
sys.path.insert(0, r"D:\Claude output\4. plans\nordic-double-bit-axe"); import niflib
sys.path.insert(0, S2)

STAGE = TX.STAGE
EB = "ebony"
EB_MESH = MESH_REL + "\\" + EB                 # meshes\TrulyNordic\ebony
EB_TEX = TEX_REL + "\\" + EB                   # textures\pbr\TrulyNordic\ebony
EB_WORK = os.path.join(WORK, EB)
EB_STAGE = os.path.join(STAGE, EB)
# every item an Ebony quality file ships: the main files' defaults and installer alternates, and the Additional Weapons
# file's spear and halberd, and (1.4.0, 2026-11-14) its crossbow and bolt quiver / bolts
MAIN = ["sword", "sword2", "battleaxe", "greatsword", "warhammer", "waraxe", "dagger", "dagger2", "mace", "mace2", "bow",
        "shield", "shield2", "quiver"]
ADDITIONAL = ["spear", "halberd", "crossbow", "boltquiver"]
EBONY_ITEMS = MAIN + ADDITIONAL

GOLD = np.array([0.93, 0.74, 0.40], np.float32)      # satin gold (sRGB albedo) - the study's tone
EBONY = np.array([0.135, 0.135, 0.148], np.float32)  # ebony steel at the painted steel's mean tone
STEEL_L, POLISH_L = 0.40, 0.80
RING_ALONG, RING_ALONG_X, RING_ROUND, RING_HOLE, RING_MIN_TRIS = 2.0, 0.8, 1.4, 0.35, 50
# the items whose rings are gold: every weapon held by a haft or grip (the owner: "the pole arms rings on the pole
# around the handle"); the quiver's bands go round its tube, not a handle, and stay ebony black
# a weapon whose ring is not a mesh part of its own: the band of its metal between two positions along the long axis,
# within the given radius of the axis. The spear's socket ends in a polished foot above the binding (the spear sheet's
# "binding" view) - its last 1.2 units are its ring.
RING_BANDS = {"spear": [(57.0, 58.5, 1.25)]}
RING_ITEMS = {"sword", "sword2", "battleaxe", "greatsword", "warhammer", "waraxe", "dagger", "dagger2", "mace", "mace2", "bow", "spear", "halberd"}


def smooth01(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)


def tex_name(item, role): return f"tn_{ITEMS[item]['stem']}" + ("" if role == "metal" else f"_{role}")


def atlases(item):
    """(role, png base or None, dds name) for every texture set the item's NIFs name (the sheath included)."""
    it = ITEMS[item]; out = []
    for role, sh in it["shapes"].items():
        out.append((role, sh.get("tex"), tex_name(item, role)))
    if it.get("sheath"): out.append(("sheath", it["sheath"]["tex"], tex_name(item, "sheath")))
    return out


# ------------------------------------------------------------------ haft rings, from the mesh parts
def _raster(tri_px, W, H, which=None):
    im = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(im)
    for i in (range(len(tri_px)) if which is None else np.where(which)[0]): dr.polygon([tuple(map(float, q)) for q in tri_px[i]], fill=255)
    return np.asarray(im) > 0


def ring_parts(item, verbose=True):
    """The metal mesh's parts that encircle the haft or grip. Returns ((faces mask, F, UV), list of part descriptions).
    A part qualifies when it is short along the long axis (<= RING_ALONG and <= RING_ALONG_X x its width) and round
    (cross widths within RING_ROUND), and EITHER open in the middle (no vertex nearer its centre than RING_HOLE x its
    outer radius - the haft passes through it) OR a closed plain band: no carving under it (under 2 % of its atlas
    pixels at carving-floor height) - the halberd's rings are capped bands; a pommel or cap end is carved."""
    if item not in RING_ITEMS: return None, []
    p = os.path.join(WORK, item, "orig_metal.npz")
    if not os.path.isfile(p): return None, []
    d = np.load(p); V, F, UV = d["V"].astype(np.float64), d["F"], d["UV"]
    key = np.round(V * 1000).astype(np.int64); _, inv = np.unique(key, axis=0, return_inverse=True); inv = inv.ravel()
    Fw = inv[F]; n = int(inv.max()) + 1
    r = np.concatenate([Fw[:, 0], Fw[:, 1]]); c = np.concatenate([Fw[:, 1], Fw[:, 2]])
    _, lab = connected_components(coo_matrix((np.ones(len(r)), (r, c)), shape=(n, n)), directed=False)
    flab = lab[Fw[:, 0]]
    ext = V.max(0) - V.min(0); ax = int(np.argmax(ext)); cr = [i for i in range(3) if i != ax]
    hp = ITEMS[item]["shapes"]["metal"]["tex"] + "_height.png"
    h = np.asarray(Image.open(hp).convert("L")) if os.path.isfile(hp) else None
    tri_px = None
    if h is not None:
        H_, W_ = h.shape; tri_px = (UV if UV.ndim == 3 else UV[F]) * np.array([W_, H_]); tri_px[..., 1] = H_ - tri_px[..., 1]
    sel = np.zeros(len(F), bool); found = []
    for k in np.unique(flab):
        m = flab == k
        if m.sum() < RING_MIN_TRIS: continue
        P = V[np.unique(F[m])]; lo, hi = P.min(0), P.max(0); e = hi - lo
        along, w1, w2 = e[ax], e[cr[0]], e[cr[1]]
        if along > RING_ALONG or along > RING_ALONG_X * min(w1, w2) or max(w1, w2) / max(min(w1, w2), 1e-6) > RING_ROUND: continue
        cen = (lo + hi) / 2; rad = np.hypot(P[:, cr[0]] - cen[cr[0]], P[:, cr[1]] - cen[cr[1]])
        kind = "open ring"
        if rad.min() < RING_HOLE * rad.max():
            if h is None: continue
            pix = _raster(tri_px, h.shape[1], h.shape[0], m)
            carved = float((h[pix] < 80).mean()) if pix.any() else 1.0
            if carved >= 0.02: continue
            kind = f"closed plain band (carved {carved:.3f})"
        sel |= m
        found.append(dict(kind=kind, at=[round(float(lo[ax]), 2), round(float(hi[ax]), 2)], width=[round(float(w1), 2), round(float(w2), 2)],
                          inner_r=round(float(rad.min()), 2), outer_r=round(float(rad.max()), 2), tris=int(m.sum())))
    for lo_, hi_, rmax in RING_BANDS.get(item, []):
        T = V[F]; ya = T[..., ax]; rr_ = np.hypot(T[..., cr[0]], T[..., cr[1]])
        m = (ya.min(1) >= lo_) & (ya.max(1) <= hi_) & (rr_.max(1) <= rmax)
        if m.any():
            sel |= m; found.append(dict(kind="band of the socket (RING_BANDS)", at=[lo_, hi_], inner_r=0.0, outer_r=round(float(rr_[m].max()), 2), tris=int(m.sum())))
    if verbose: print(f"  {item}: {len(found)} haft ring(s) " + "; ".join(f"along {f['at'][0]}..{f['at'][1]} r {f['inner_r']}-{f['outer_r']} ({f['kind']})" for f in found))
    return (sel, F, UV), found


def ring_mask(item, W, H):
    """Pixel mask of the haft rings on the metal atlas (W x H), grown 2 px into the gutter only (never onto a neighbour)."""
    got, found = ring_parts(item, verbose=False)
    if not got or not found: return None, found
    sel, F, UV = got
    px = (UV if UV.ndim == 3 else UV[F]) * np.array([W, H]); px[..., 1] = H - px[..., 1]
    ring = _raster(px, W, H, sel); cov = _raster(px, W, H)
    return ring | (ndi.binary_dilation(ring, iterations=2) & ~cov), found


# ------------------------------------------------------------------ the recolour (the study's variant A)
def medallions(base):
    """(cx, cy, step radius, ring width) of every measured medallion on this atlas (design records, medallion_check.json)."""
    from medallion_audit import MEDALLIONS
    work = os.path.dirname(os.path.dirname(base)); p = os.path.join(work, "medallion_check.json"); res = []
    if not os.path.isfile(p) or (os.path.basename(work), os.path.basename(base)) not in {(m[3], m[4]) for m in MEDALLIONS}: return res
    for f in json.load(open(p))["faces"].values():
        c = f.get("ring_centre_px") or f.get("symbol_centre_px"); rg = f.get("ring") or {}
        if c and f.get("step_r_px"): res.append((c[0], c[1], float(f["step_r_px"]), float(rg.get("width_px") or 2.5)))
    return list({tuple(r) for r in res})


def recolour(base, rings=None):
    """Variant A on one atlas: returns (albedo float RGB, rmaos float RGBA, gold weight, stats)."""
    alb = np.asarray(Image.open(base + ".png").convert("RGB"), np.float32) / 255
    rm = np.asarray(Image.open(base + "_rmaos.png").convert("RGBA"), np.float32) / 255
    Hh, Ww = alb.shape[:2]
    hp = base + "_height.png"
    h = np.asarray(Image.open(hp).convert("L"), np.float32) if os.path.isfile(hp) else np.full((Hh, Ww), 255, np.float32)
    if h.shape != alb.shape[:2]: h = np.asarray(Image.fromarray(h.astype(np.uint8)).resize((Ww, Hh), Image.BILINEAR), np.float32)
    metal = smooth01((rm[..., 1] - 0.45) / 0.1)
    fw = 1 - smooth01((h - 40) / 40)                 # floor weight
    fl = smooth01((h - 247) / 5)                     # flush weight
    st = (1 - fw) * (1 - fl)                         # strand weight
    flushb = h >= 250; carved = (h < 248) & (metal > 0.5)
    near = ndi.distance_transform_edt(~carved) <= 6
    hull = ndi.binary_closing(carved, structure=np.ones((13, 13), bool), iterations=1)
    thin = flushb & ~ndi.binary_opening(flushb, structure=np.ones((7, 7), bool)) & near & hull
    yy, xx = np.mgrid[0:Hh, 0:Ww]
    disc = np.zeros((Hh, Ww), bool); ring = np.zeros((Hh, Ww), bool); meds = medallions(base)
    for cx, cy, r, w in meds:
        dd = np.hypot(xx - cx, yy - cy); disc |= dd < r; ring |= (dd >= r - 1) & (dd <= r + min(w, 6.0) + 2)   # a broad flange: its inner 8 px
    thin_w = ndi.gaussian_filter((thin | (ring & flushb)).astype(np.float32), 0.7)
    # strand crowns, one piece per strand run; a piece lying against plain flush steel along most of its outline is a
    # bevel / edge ramp, not a strand (bevels stay black with their sheen)
    sb = (h >= 80) & (h <= 248) & (metal > 0.5)
    seg, ns = ndi.label((h >= 160) & sb)
    idx = np.arange(1, ns + 1)
    ring1 = ndi.grey_dilation(seg, size=(3, 3)) * (seg == 0)
    touch = ndi.sum(np.ones_like(h), ring1, idx); tfloor = ndi.sum((h < 120).astype(np.float32), ring1, idx)
    notstrand = np.zeros(ns + 1, bool); notstrand[1:] = (tfloor / np.maximum(touch, 1)) < 0.20
    near_i = ndi.distance_transform_edt(seg == 0, return_distances=False, return_indices=True)
    segf = seg[near_i[0], near_i[1]] * sb
    near_floor = ndi.distance_transform_edt(h >= 80) <= 8
    strand_ok = sb & (~notstrand[segf] | near_floor)
    sok = ndi.gaussian_filter((strand_ok | disc | ~sb).astype(np.float32), 0.6)
    g = np.clip(st * sok + thin_w * fl, 0, 1)
    if rings is not None: g = np.maximum(g, ndi.gaussian_filter(rings.astype(np.float32), 0.6))
    lum = alb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    black = np.minimum(EBONY[None, None] * np.clip(lum / STEEL_L, 0.05, 2.2)[..., None] ** 0.4, 0.30)
    gold = GOLD[None, None] * np.clip(lum / POLISH_L, 0.08, 1.15)[..., None] ** 0.75
    c = black * (1 - g[..., None]) + gold * g[..., None]
    c = alb * fw[..., None] + c * (1 - fw[..., None])              # floors exactly as painted
    c = alb * (1 - metal[..., None]) + c * metal[..., None]        # non-metal untouched
    r0, m0 = rm[..., 0], rm[..., 1]
    rb = np.maximum(r0 * 0.85, 0.12); rg = np.clip(0.16 + 0.6 * (r0 - 0.18), 0.16, 0.38)
    rr = (rb * (1 - g) + rg * g) * (1 - fw) + r0 * fw; rr = r0 * (1 - metal) + rr * metal
    rmo = rm.copy(); rmo[..., 0] = rr; rmo[..., 1] = np.maximum(m0, (1 - fw) * metal)
    stats = dict(medallions=len(meds), strand_pieces=int(ns), bevel_pieces=int(notstrand.sum()), has_height=os.path.isfile(hp),
                 metal_share=round(float(metal.mean()), 4), gold_share=round(float((g * metal).sum() / max(metal.sum(), 1)), 4),
                 ring_px=int(rings.sum()) if rings is not None else 0)
    return c, rmo, g * metal, stats


def save_png(path, a, mode):
    Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8), mode).save(path)


def mask_preview(path, alb, g, rings):
    """The gold mask over the dimmed atlas: gold = knotwork / rims / medallion ring, red outline = the haft rings."""
    a = np.asarray(Image.open(alb).convert("RGB"), np.float32) / 255 * 0.35
    o = a * (1 - g[..., None]) + np.array([1.0, 0.8, 0.25]) * g[..., None]
    if rings is not None:
        edge = rings & ~ndi.binary_erosion(rings, iterations=2); o[edge] = [1.0, 0.1, 0.1]
    im = Image.fromarray(np.clip(o * 255, 0, 255).astype(np.uint8)); im.thumbnail((1024, 1024)); im.save(path, quality=90)


# ------------------------------------------------------------------ the arrows' atlas (copied rectangles, as quiver_atlas.py)
def arrow_atlas(out_base, steel, soft):
    plan = json.load(open(os.path.join(WORK, "quiver", "arrow_atlas_plan.json"))); N = plan["size"]
    src = {"steel": steel, "soft": soft}
    for suf, fill in {"": (0, 0, 0), "_rmaos": (230, 0, 255, 128)}.items():
        ims = {k: Image.open(v + suf + ".png") for k, v in src.items()}
        mode = ims["steel"].mode; fill = tuple(fill[:len(mode)]) + (255,) * max(0, len(mode) - len(fill))
        o = Image.new(mode, (N, N), fill)
        for r in plan["rects"]: o.paste(ims[r["src"]].convert(mode).crop(tuple(r["src_box"])), tuple(r["dst"]))
        o.save(out_base + suf + ".png")


# ------------------------------------------------------------------ NIF copies with the texture paths at the ebony folder
def ebony_path(p):
    r"""textures\pbr\TrulyNordic\<x>  ->  textures\pbr\TrulyNordic\ebony\<x> (refuses anything else of ours)"""
    pre = TEX_REL.lower() + "\\"
    if not p.lower().startswith(pre): return p
    rest = p[len(pre):]
    if rest.lower().startswith(EB + "\\"): return p
    return p[:len(pre)] + EB + "\\" + rest


def ebony_nif(src, dst):
    """Copy a NIF with every BSShaderTextureSet path of ours moved to the ebony folder; nothing else changes. Returns the
    number of paths moved (0 refuses - a model with none of our textures is not an ebony model)."""
    n = niflib.Nif(src); moved = 0
    for b, t in enumerate(n.btypes):
        if t != "BSShaderTextureSet": continue
        blk = n.blocks[b]; k = struct.unpack_from("<I", blk, 0)[0]; q = 4; paths = []
        for _ in range(k):
            L = struct.unpack_from("<I", blk, q)[0]; paths.append(blk[q + 4:q + 4 + L].decode("latin-1")); q += 4 + L
        assert q == len(blk), (src, b)
        new = [ebony_path(p) for p in paths]; moved += sum(a != c for a, c in zip(paths, new))
        out = struct.pack("<I", k)
        for p in new: e = p.encode("latin-1"); out += struct.pack("<I", len(e)) + e
        n.blocks[b] = bytearray(out)
    if not moved: raise SystemExit(f"ebony_nif: {src} names none of our textures")
    os.makedirs(os.path.dirname(dst), exist_ok=True); n.save(dst); niflib.Nif(dst)
    return moved


def mesh_map(item):
    """(staged shared NIF, ebony game path) for every model an Ebony quality file ships of this item: the third-person
    model at the item's shared path (the shield at ours), the item's own first-person file where it has one, the arrows."""
    it = ITEMS[item]; at = it.get("path_stem", it["stem"]); st = os.path.join(STAGE, item); out = []
    if item.startswith("shield"):
        return [(os.path.join(st, r"meshes\dlc02\armor\nordicshield\nordicshield.nif"), os.path.join(EB_MESH, "shield", "shield.nif"))]
    out.append((os.path.join(st, MESH_REL, it["stem"], it["stem"] + ".nif"), os.path.join(EB_MESH, at, at + ".nif")))
    if item == "quiver":
        out.append((os.path.join(st, MESH_REL, "quiver", "arrowflight.nif"), os.path.join(EB_MESH, "quiver", "arrowflight.nif")))
    elif item == "boltquiver":     # the bolt in flight (the PROJ's model), beside the quiver / bolts
        out.append((os.path.join(st, MESH_REL, "boltquiver", "boltflight.nif"), os.path.join(EB_MESH, "boltquiver", "boltflight.nif")))
    elif it.get("new_item"):
        out.append((os.path.join(st, MESH_REL, at, "1stperson" + at + ".nif"), os.path.join(EB_MESH, at, "1stperson" + at + ".nif")))
    elif item in ("battleaxe", "greatsword"):   # the Standalone's own first-person files (build-packages.FIRST_OWN)
        out.append((os.path.join(st, r"meshes\dlc02\weapons\nordic", it["first"]), os.path.join(EB_MESH, item, "1stperson" + item + ".nif")))
    return out


# ------------------------------------------------------------------ the medallion measure on the ebony maps
def measure_medallions(done):
    r"""Every MEDALLIONS row (set2\medallion_audit.py) whose atlas this build recoloured, measured on the EBONY maps. The
    engraving-layout gate judges these in its ebony mode (the steel around the disc is black, so the disc is judged by
    its own darkness and by the gold ring's contrast, not by disc / steel)."""
    import medallion_measure as MM
    from medallion_audit import MEDALLIONS
    faces = {}
    for key, piece, face, work, stem, cx, cy, rg, lay in MEDALLIONS:
        eb = done.get((work, stem))
        if not eb or key not in EBONY_ITEMS: continue
        m = MM.measure(eb, cx, cy, rg, name=f"{piece} / {face} (ebony)")
        m.update(item=key, piece=piece, face=face, work=work, look="ebony")
        faces[f"{key}: {piece} / {face}"] = {k: v for k, v in m.items() if k != "stem"}
    return faces


# ------------------------------------------------------------------ the Ebony quality plugins' model paths
EBONY_AT = sorted({ITEMS[k].get("path_stem", ITEMS[k]["stem"]) for k in EBONY_ITEMS if not k.startswith("shield")} | {"shield"})
EBONY_PLUGINS = [os.path.join(os.path.dirname(HERE), "plugin", "standalone-ebony", "TrulyNordicCarvedWeapons - Standalone.esp"),
                 os.path.join(os.path.dirname(HERE), "plugin", "additional-ebony", "TrulyNordicCarvedWeapons - Additional Weapons.esp")]


def plugin_paths(path):
    r"""Point an Ebony quality plugin's model paths (MODL / MOD2 / MOD3 / MOD4, every record type) of the Ebony items at
    meshes\TrulyNordic\ebony\<item>\ - TrulyNordic\<at>\ -> TrulyNordic\ebony\<at>\ for each item folder in EBONY_AT,
    nothing else changed (rename_plugin_paths.rewrite: subrecord, record and GRUP sizes rewritten). Idempotent: an
    ebony path no longer matches. Items outside EBONY_ITEMS keep the shared paths."""
    import rename_plugin_paths as RP
    b = open(path, "rb").read(); total = 0
    for at in EBONY_AT:
        b, _, n = RP.rewrite(b, "TrulyNordic\\" + at + "\\", "TrulyNordic\\" + EB + "\\" + at + "\\"); total += n
    open(path, "wb").write(b)
    left = sorted({m.decode("latin-1") for m in __import__("re").findall(rb"TrulyNordic\\([A-Za-z0-9_]+)\\", b)} - {EB})
    print(f"plugin_paths: {os.path.basename(os.path.dirname(path))}\\{os.path.basename(path)}: {total} path(s) moved to the ebony folder;"
          f" folders still shared: {left or 'none'}")
    return total


def build(items):
    os.makedirs(os.path.join(EB_WORK, "masks"), exist_ok=True)
    rp = os.path.join(EB_WORK, "ebony_report.json")
    report = json.load(open(rp)) if os.path.isfile(rp) and set(items) != set(EBONY_ITEMS) else {}
    done = {}
    for item in items:
        it = ITEMS[item]; stem = it["stem"]; rep = {"atlases": {}, "meshes": {}}
        tex_out = os.path.join(STAGE, EB_TEX, stem); os.makedirs(tex_out, exist_ok=True)
        shared = os.path.join(STAGE, TEX_REL, stem)
        png_out = os.path.join(EB_WORK, item, "tex"); os.makedirs(png_out, exist_ok=True)
        print(item)
        for role, base, name in atlases(item):
            if role == "arrow": continue        # built from the recoloured steel / soft below
            if base is None or not os.path.isfile(base + "_rmaos.png") or \
                    np.asarray(Image.open(base + "_rmaos.png").convert("RGBA"))[..., 1].max() < 115:   # no metal (G < 0.45)
                for suf in ("", "_n", "_rmaos"): shutil.copy2(os.path.join(shared, name + suf + ".dds"), os.path.join(tex_out, name + suf + ".dds"))
                if base:   # PNG copies for the arrows' atlas and the renders
                    for suf in ("", "_rmaos", "_n_gl"):
                        if os.path.isfile(base + suf + ".png"): shutil.copy2(base + suf + ".png", os.path.join(png_out, os.path.basename(base) + suf + ".png"))
                rep["atlases"][name] = "no metal - the shared maps, copied"; continue
            W_, H_ = Image.open(base + ".png").size
            rings, found = ring_mask(item, W_, H_) if role == "metal" else (None, [])
            c, rmo, g, stt = recolour(base, rings)
            ob = os.path.join(png_out, os.path.basename(base))
            save_png(ob + ".png", c, "RGB"); save_png(ob + "_rmaos.png", rmo, "RGBA")
            for suf in ("_height", "_n_gl"):
                src = base + suf + ".png"
                if suf == "_n_gl":
                    fx = os.path.join(WORK, item, "tex", os.path.basename(base) + "_n_gl.png"); src = fx if os.path.isfile(fx) else src
                if os.path.isfile(src): shutil.copy2(src, ob + suf + ".png")
            TX.texconv(ob + ".png", tex_out, name, "BC7_UNORM_SRGB", srgb=True)
            TX.texconv(ob + "_rmaos.png", tex_out, name + "_rmaos", "BC7_UNORM")
            shutil.copy2(os.path.join(shared, name + "_n.dds"), os.path.join(tex_out, name + "_n.dds"))
            mask_preview(os.path.join(EB_WORK, "masks", name + "_gold.jpg"), base + ".png", g, rings)
            stt["haft_rings"] = found; rep["atlases"][name] = stt
            done[(os.path.basename(os.path.dirname(os.path.dirname(base))), os.path.basename(base))] = ob
            print(f"  {name}: gold {stt['gold_share']:.3f} of the metal, {len(found)} ring part(s), medallions {stt['medallions']}")
        if item == "quiver":
            q = ITEMS["quiver"]["shapes"]; name = tex_name("quiver", "arrow")
            ob = os.path.join(png_out, os.path.basename(q["arrow"]["tex"]))
            arrow_atlas(ob, os.path.join(png_out, os.path.basename(q["metal"]["tex"])), os.path.join(png_out, os.path.basename(q["leather"]["tex"])))
            shutil.copy2(q["arrow"]["tex"] + "_n_gl.png", ob + "_n_gl.png")
            TX.texconv(ob + ".png", tex_out, name, "BC7_UNORM_SRGB", srgb=True)
            TX.texconv(ob + "_rmaos.png", tex_out, name + "_rmaos", "BC7_UNORM")
            shutil.copy2(os.path.join(shared, name + "_n.dds"), os.path.join(tex_out, name + "_n.dds"))
            rep["atlases"][name] = "the arrows' atlas, its rectangles copied from the recoloured steel and soft maps"
        for src, rel in mesh_map(item):
            dst = os.path.join(EB_STAGE, item, rel); rep["meshes"][rel] = ebony_nif(src, dst)
        # every texture an ebony NIF names is in the ebony folder and was written
        for rel in rep["meshes"]:
            n = niflib.Nif(os.path.join(EB_STAGE, item, rel))
            for b, t in enumerate(n.btypes):
                if t != "BSShaderTextureSet": continue
                blk = n.blocks[b]; k = struct.unpack_from("<I", blk, 0)[0]; q = 4
                for _ in range(k):
                    L = struct.unpack_from("<I", blk, q)[0]; p = blk[q + 4:q + 4 + L].decode("latin-1"); q += 4 + L
                    if not p: continue
                    if p.lower().startswith(TEX_REL.lower() + "\\") and not p.lower().startswith(EB_TEX.lower() + "\\"):
                        raise SystemExit(f"{rel} still names the shared {p}")
                    if p.lower().startswith(EB_TEX.lower() + "\\") and not os.path.isfile(os.path.join(STAGE, p)):
                        raise SystemExit(f"{rel} names {p}, which this build did not write")
        report[item] = rep
    meds = measure_medallions(done)
    mp = os.path.join(EB_WORK, "medallion_check.json")
    old = json.load(open(mp)).get("faces", {}) if os.path.isfile(mp) and set(items) != set(EBONY_ITEMS) else {}
    old.update(meds)
    json.dump({"tool": "tools\\ebony.py (set2\\medallion_measure.py on the ebony maps)", "mode": "ebony", "faces": old}, open(mp, "w"), indent=1)
    json.dump(report, open(rp, "w"), indent=1)
    for k, m in meds.items(): print(f"  medallion {k}: floor L {m.get('L_floor')} ring x{(m.get('ring') or {}).get('L_ring_vs_floor')} w {(m.get('ring') or {}).get('width_px')}px")
    print("ebony:", len(items), "item(s) ->", os.path.join(STAGE, EB_TEX), "and", EB_STAGE)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--plugins":
        for pth in EBONY_PLUGINS: plugin_paths(pth)
        sys.exit(0)
    if a and a[0] == "--rings":
        for k in a[1:] or EBONY_ITEMS: ring_parts(k)
        sys.exit(0)
    bad = [k for k in a if k not in EBONY_ITEMS]
    if bad: raise SystemExit(f"not an Ebony item: {bad} (EBONY_ITEMS: {EBONY_ITEMS})")
    build(a or EBONY_ITEMS)
