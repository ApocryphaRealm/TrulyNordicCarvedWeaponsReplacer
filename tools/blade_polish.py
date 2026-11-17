r"""The POLISHED BLADE (1.4.0, 2026-11-16; the owner 19:47: "I'd rather go with the 1 through 4 without the mirror").

The mirror-finish study (4. plans\nordic-carved-missing-weapons-20261115\mirror-finish-study-20261116\STUDY.md) and its
demo on the straight sword gave four changes for every Carved weapon's blade / edged steel; this module carries them
into the real build for every blade at once:
  1. the polished finish (tn_knot.maps_polish's recipe): no patina blotches (GRIME 0), one even steel field at FIELD sRGB
     (~0.76), roughness R_FIELD (~0.10) with brushing +/- R_BRUSH (0.015), polished bevels and strand tops at R_POL
     (0.055), the carving floors kept dark and rough (R_FLOOR 0.62)
  2. flat normals on the plain steel: the relief in the normal map is the carving's only (no hammer dents, no brushing)
  3. the blade's normals welded, not split: the 1.1.0 shading-fix pass (set2\shading_fix_split.py) split the blade's
     vertices along ~180-240 seams per face; gb_blender.py now welds a blade shape and marks only creases over
     BLADE_SHARP_DEG sharp ("weld_normals"), so the reflection rolls across each face without lines
  4. a blade-only atlas per weapon, sized to its blade at up to ~63 px per unit (the shared 2048 atlas gave the blades
     24-31 px/unit): the blade's triangles leave the shared steel shape for a shape of their own ("<shape>_blade", role
     "blade", its own texture set tn_<stem>_blade), their UVs moved block by block (scale k, no rotation or mirror) into
     a W x H atlas. The hilt keeps the shared atlas and its maps unchanged, byte for byte.

HOW THE BLADE MAPS ARE MADE (paint): from the item's own painted maps (the painter's PNGs - albedo, _n, _rmaos, _height),
never from a fresh design run, so the carving stays exactly the approved layout on every blade whatever painter made it:
  * each block of the old atlas is resampled (bilinear) into its place in the blade atlas: height, normal, roughness;
  * the carving's height field h = height - 1 (in carving-depth units) gives, at the NEW density, the floors, the AO, the
    convex ridges and the strand tops by maps_polish's own formulas; the polished bevel band is read from the painted
    roughness (maps_v3 painted the bevels and strand edges at 0.18, the field never below ~0.27);
  * the normal comes from the height field alone (item 2): its slope scale (depth x the painter's px/unit) is CALIBRATED
    per item from the painted normal map against the painted height, so the carving keeps its painted relief;
  * albedo, roughness, metalness and AO follow maps_polish exactly.
The blocks keep the old texel orientation, so the tangent frame of the normal map is unchanged.

Layout (layout(item)): the blade triangles are those of the source shape whose UV centroid lies in one of the item's
'rects' (old atlas pixels, rows down - the painter's blade column / head blocks). Each rect is shrunk to the tight box of
its triangles (+4 px) and packed into the smallest atlas of CANDIDATES that reaches 92 % of the target density (else the
densest); refuses when a selected UV island also has triangles outside the rects (a piece cut in two).
Run:  python -I blade_polish.py layout [item ...]     (prints and writes WORK\<item>\blade_layout.json)
      python -I blade_polish.py paint [item ...]      (WORK\<item>\blade\tn_<stem>_blade*.png; textures.py calls it)
"""
import os, sys, json, struct, math
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)

TARGET_PX = 63.0                                   # px per model unit (the study's 512x4096 straight-sword blade)
CANDIDATES = [(512, 2048), (1024, 2048), (512, 4096), (1024, 4096), (2048, 2048), (2048, 4096)]
PAD = 8
BLADE_SHARP_DEG = 30.0                             # gb_blender weld_normals: creases over this stay hard (the saber's
                                                   # 33.7 deg bevel line), the 1-25 deg shading-fix seams go
# maps_polish's recipe (the demo's tn_knot.POL), the owner's choice 19:47 (items 1-4)
POL = dict(FIELD=0.76, POLISH=0.80, R_FIELD=0.10, R_BRUSH=0.015, R_POL=0.055, R_FLOOR=0.62)
SEED = 11
DEBLUR_ITERS = 6


# ------------------------------------------------------------------ the source shape (BSTriShape vertex data, as the UV gate reads it)
def read_shape(path, want):
    d = open(path, "rb").read(); p = d.index(b"\n") + 1
    version, endian, user, nblocks, bsver = struct.unpack_from("<IBIII", d, p); p += 17
    for _ in range(3): p += 1 + d[p]
    ntypes, = struct.unpack_from("<H", d, p); p += 2; types = []
    for _ in range(ntypes):
        n, = struct.unpack_from("<I", d, p); p += 4; types.append(d[p:p + n].decode("latin-1")); p += n
    tidx = struct.unpack_from(f"<{nblocks}H", d, p); p += 2 * nblocks
    sizes = struct.unpack_from(f"<{nblocks}I", d, p); p += 4 * nblocks
    nstr, _ = struct.unpack_from("<II", d, p); p += 8; strings = []
    for _ in range(nstr):
        n, = struct.unpack_from("<I", d, p); p += 4; strings.append(d[p:p + n].decode("latin-1")); p += n
    ngroups, = struct.unpack_from("<I", d, p); p += 4 + 4 * ngroups
    for i, s in enumerate(sizes):
        blk = d[p:p + s]; p += s
        if types[tidx[i] & 0x7FFF] != "BSTriShape": continue
        ni = struct.unpack_from("<i", blk, 0)[0]; name = strings[ni] if 0 <= ni < len(strings) else ""
        if name != want: continue
        o = 4; nex = struct.unpack_from("<I", blk, o)[0]; o += 4 + 4 * nex + 4; o += 4 + 12 + 36 + 4 + 4; q = o + 28
        desc = struct.unpack_from("<Q", blk, q)[0]; ntri, nv = struct.unpack_from("<HH", blk, q + 8)
        stride = (desc & 0xF) * 4; ou = ((desc >> 8) & 0xF) * 4; vd = q + 16
        raw = np.frombuffer(blk, np.uint8, nv * stride, vd).reshape(nv, stride)
        uv = raw[:, ou:ou + 4].copy().view(np.float16).reshape(nv, 2).astype(np.float64)
        pos = raw[:, 0:12].copy().view(np.float32).reshape(nv, 3).astype(np.float64)
        F = np.frombuffer(blk, np.uint16, ntri * 3, vd + nv * stride).reshape(-1, 3).astype(np.int64)
        return pos, uv, F
    raise SystemExit(f"{path}: no shape {want!r}")


def source_of(item, role):
    from items import ITEMS
    it = ITEMS[item]; name = it["shapes"][role]["name"]
    for s in it["sources"]:
        try: return s, name, read_shape(s, name)
        except SystemExit: continue
    raise SystemExit(f"{item}: shape {name!r} is in none of its sources")


def selected(item):
    """(pos, uv, F, sel, source path, shape name, polish config)"""
    from items import ITEMS
    pc = ITEMS[item]["polish"]; src, name, (pos, uv, F) = source_of(item, pc["from"])
    c = uv[F].mean(1) * 2048; sel = np.zeros(len(F), bool); rid = np.full(len(F), -1)
    for r, (x0, y0, x1, y1) in enumerate(pc["rects"]):
        m = (c[:, 0] >= x0) & (c[:, 0] < x1) & (c[:, 1] >= y0) & (c[:, 1] < y1) & ~sel
        sel |= m; rid[m] = r
    return pos, uv, F, sel, rid, src, name, pc


def _islands(F, nv):
    par = np.arange(nv)
    def find(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for a, b, c in F:
        ra = find(a); par[find(b)] = ra; par[find(c)] = ra
    return np.array([find(i) for i in range(nv)])[F[:, 0]]


def _pack(blocks, k, W, H):
    """first-fit columns, tallest first; returns {index: (dx, dy)} or None"""
    order = sorted(range(len(blocks)), key=lambda i: -(blocks[i][3] - blocks[i][1]))
    cols = []                       # [x, width, y_next]
    out = {}
    for i in order:
        w = (blocks[i][2] - blocks[i][0]) * k; h = (blocks[i][3] - blocks[i][1]) * k
        if h > H - 2 * PAD: return None
        for c in cols:
            if c[2] + h <= H - PAD and w <= max(c[1], 0) + 1e-6:
                out[i] = (c[0], c[2]); c[2] += h + PAD; break
        else:
            x = (cols[-1][0] + cols[-1][1] + PAD) if cols else PAD
            if x + w > W - PAD: return None
            cols.append([x, w, PAD + h + PAD]); out[i] = (x, PAD)
    return out


def layout(item, write=True):
    from items import WORK
    pos, uv, F, sel, rid, src, name, pc = selected(item)
    if not sel.any(): raise SystemExit(f"{item}: no triangle in the blade rects")
    isl = _islands(F, len(uv)); cut = sorted(set(isl[sel]) & set(isl[~sel]))
    if cut:
        bad = [(int(i), int((isl == i)[sel].sum()), int((isl == i)[~sel].sum())) for i in cut[:6]]
        raise SystemExit(f"{item}: {len(cut)} UV piece(s) cut by the blade rects (island, in, out): {bad}")
    P = pos[F]; A = 0.5 * np.linalg.norm(np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]), axis=1)
    U = uv[F] * 2048; e1, e2 = U[:, 1] - U[:, 0], U[:, 2] - U[:, 0]; UA = 0.5 * np.abs(e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0])
    # the blade's density: the 3D-area-weighted median of the triangles' own densities (the faces a player sees), not
    # the overall ratio, which small densely laid carved panels pull up (the saber's weave panels: 51 vs its faces' 24)
    dens = np.sqrt(UA[sel] / np.maximum(A[sel], 1e-12)); w = A[sel]; o_ = np.argsort(dens); cw = np.cumsum(w[o_])
    px_old = float(dens[o_][np.searchsorted(cw, 0.5 * cw[-1])])
    blocks = []
    for r in range(len(pc["rects"])):
        m = sel & (rid == r)
        if not m.any(): continue
        Q = U[m].reshape(-1, 2)
        blocks.append([max(0.0, math.floor(Q[:, 0].min()) - 4), max(0.0, math.floor(Q[:, 1].min()) - 4),
                       min(2048.0, math.ceil(Q[:, 0].max()) + 4), min(2048.0, math.ceil(Q[:, 1].max()) + 4)])
    kt = pc.get("px", TARGET_PX) / px_old
    best = None
    for W, H in CANDIDATES:
        lo, hi = 0.25, kt
        if _pack(blocks, hi, W, H) is not None: k = hi
        else:
            for _ in range(40):
                mid = 0.5 * (lo + hi)
                if _pack(blocks, mid, W, H) is not None: lo = mid
                else: hi = mid
            k = lo
        cand = (k, W, H)
        if k >= 0.92 * kt: best = cand; break
        if best is None or k > best[0] + 1e-6: best = cand
    k, W, H = best; k = math.floor(k * 1000) / 1000
    pl = _pack(blocks, k, W, H)
    out = dict(item=item, source=src, shape=name, W=W, H=H, k=k, px_old=round(px_old, 2), px_new=round(px_old * k, 2),
               target_px=pc.get("px", TARGET_PX), tris=int(sel.sum()), tris_left=int((~sel).sum()),
               y_range=[round(float(P[sel][:, :, 1].min()), 2), round(float(P[sel][:, :, 1].max()), 2)],
               blocks=[dict(src=b, dst=[round(pl[i][0], 3), round(pl[i][1], 3)]) for i, b in enumerate(blocks)],
               whole=bool(pc["from"] == "blade"), atlas_used=round(float(sum((b[2] - b[0]) * (b[3] - b[1]) for b in blocks) * k * k / (W * H)), 3))
    if write:
        os.makedirs(os.path.join(WORK, item), exist_ok=True)
        json.dump(out, open(os.path.join(WORK, item, "blade_layout.json"), "w"), indent=1)
    return out


# ------------------------------------------------------------------ the maps
def _box(a, r):
    k = 2 * r + 1; p = np.pad(a, r, mode="edge"); c = np.pad(np.cumsum(np.cumsum(p, 0), 1), ((1, 0), (1, 0)))
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)
def _blur(a, r, n=2):
    for _ in range(n): a = _box(a, r)
    return a
def _sm01(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)


def _load(base, suf, mode):
    return np.asarray(Image.open(base + suf + ".png").convert(mode), np.float32) / 255


def _sample(img, X, Y):
    """bilinear sample of img (H, W[, C]) at float pixel coords (centres at +0.5)"""
    Hh, Ww = img.shape[:2]; x = np.clip(X - 0.5, 0, Ww - 1); y = np.clip(Y - 0.5, 0, Hh - 1)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); x1 = np.minimum(x0 + 1, Ww - 1); y1 = np.minimum(y0 + 1, Hh - 1)
    fx = x - x0; fy = y - y0
    if img.ndim == 3: fx = fx[..., None]; fy = fy[..., None]
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x1] * fx * (1 - fy) + img[y1, x0] * (1 - fx) * fy + img[y1, x1] * fx * fy)


def calibrate(h, n):
    """slope scale c = depth x painter px/unit: the painted normal's slope |n.xy / n.z| against the painted height's
    gradient per pixel, median over carving pixels with a clear gradient"""
    gx = np.zeros_like(h); gy = np.zeros_like(h); gx[:, 1:-1] = (h[:, 2:] - h[:, :-2]) / 2; gy[1:-1] = (h[2:] - h[:-2]) / 2
    g = np.hypot(gx, gy); nn = n * 2 - 1; s = np.hypot(nn[..., 0], nn[..., 1]) / np.maximum(nn[..., 2], 0.05)
    m = (g > 0.02) & (h > -0.95) & (h < -0.02) & (s > 0.05)
    if m.sum() < 200: return None, int(m.sum())
    return float(np.median(s[m] / g[m])), int(m.sum())


def paint(item, out_dir=None):
    from items import ITEMS, WORK
    it = ITEMS[item]; pc = it["polish"]
    L = layout(item)
    W, H, k = L["W"], L["H"], L["k"]
    base = pc["maps"]                                  # the painter's PNG base of the source shape's atlas
    out_dir = out_dir or os.path.join(WORK, item, "blade"); os.makedirs(out_dir, exist_ok=True)
    h_o = _load(base, "_height", "L") - 1.0
    n_o = _load(base, "_n", "RGB"); n_o[..., 1] = 1 - n_o[..., 1]          # DX -> GL (green up), as maps_v3's _n_gl
    r_o = _load(base, "_rmaos", "RGBA")[..., 0]
    # per new pixel: the old atlas position (block by block); outside every block: the nearest block's edge
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) + 0.5
    OX = np.full((H, W), np.nan, np.float32); OY = np.full((H, W), np.nan, np.float32)
    cal = []
    for b in L["blocks"]:
        x0, y0, x1, y1 = b["src"]; dx, dy = b["dst"]
        bx0, by0 = int(math.floor(dx)), int(math.floor(dy)); bx1 = int(math.ceil(dx + (x1 - x0) * k)); by1 = int(math.ceil(dy + (y1 - y0) * k))
        sl = (slice(max(by0, 0), min(by1, H)), slice(max(bx0, 0), min(bx1, W)))
        OX[sl] = x0 + (xx[sl] - dx) / k; OY[sl] = y0 + (yy[sl] - dy) / k
        c, nm = calibrate(h_o[int(y0):int(y1), int(x0):int(x1)], n_o[int(y0):int(y1), int(x0):int(x1)])
        if c: cal.append((c, nm))
    if cal:
        cw = sum(n for _, n in cal); C = sum(c * n for c, n in cal) / cw
    else:
        C = 0.095 * L["px_old"]; cw = 0
    have = np.isfinite(OX)
    from scipy import ndimage
    idx = ndimage.distance_transform_edt(~have, return_distances=False, return_indices=True)
    OX = OX[idx[0], idx[1]]; OY = OY[idx[0], idx[1]]
    # the painted height was smoothed by maps_v3 (blur(H, 1, 2): two 3x3 boxes at the OLD density); that known blur is
    # undone (Van Cittert, DEBLUR_ITERS steps, kept within the carving's range) before the bicubic upsampling, and
    # maps_polish's own blur(H, 1, 2) is applied at the NEW density - so the carving's walls are as sharp as a painter
    # run at the new density would make them, within what the 8-bit height holds
    h_d = h_o.copy()
    for _ in range(DEBLUR_ITERS): h_d = np.clip(h_d + (h_o - _blur(h_d, 1, 2)), -1.0, 0.0)
    from scipy.ndimage import map_coordinates
    h = map_coordinates(h_d, [OY - 0.5, OX - 0.5], order=3, mode="nearest").astype(np.float32); h = np.clip(h, -1.0, 0.0)
    r_old = _sample(r_o, OX, OY)
    # the maps_polish recipe at the new density (h in carving-depth units: 0 plain, -1 floor)
    Hs = _blur(h, 1, 2).astype(np.float32)
    floor = _sm01(-Hs * 1.3 - 0.15)
    ao = 1.0 - 0.75 * np.clip(_blur(Hs, 6, 2) - Hs, 0, 1)
    ridge = _sm01((Hs - _blur(Hs, 3, 2)) / 0.18)
    top = _sm01((Hs + 0.45) * 3.0) * (_blur(floor, 4, 1) > 0.02)
    bevel = np.clip((0.29 - r_old) / 0.09, 0, 1) * (1 - floor)                # the painted polished bevel band (maps_v3: 0.18 at BEVEL 1, ~0.24 at the aa painter's 0.6)
    edge = np.clip(np.maximum(bevel, np.maximum(ridge * 0.85, top * 0.45)), 0, 1)
    def noise(ny, nx, sd):
        g = (np.random.default_rng(sd).random((max(2, ny), max(2, nx))) * 255).astype(np.uint8)
        return np.asarray(Image.fromarray(g).resize((W, H), Image.BICUBIC), np.float32) / 255 - 0.5
    brush = noise(H // 40, W, SEED + 1) * 0.7 + noise(H // 10, W // 2, SEED + 3) * 0.3
    f = POL["FIELD"]; fieldc = np.array([f, f + 0.006, f + 0.016], np.float32)
    basec = fieldc[None, None] * (1 + 0.012 * brush)[..., None]
    p = POL["POLISH"]; polish = np.array([p, p + 0.005, p + 0.015], np.float32); floorc = np.array([0.040, 0.040, 0.044], np.float32)
    fine = noise(H // 2, W // 2, SEED + 2)
    alb = basec * (1 - edge[..., None]) + polish[None, None] * edge[..., None]
    alb = alb * (1 - floor[..., None]) + floorc[None, None] * (1 + 0.2 * fine[..., None]) * floor[..., None]
    alb = alb * (0.40 + 0.60 * ao[..., None])
    bn = np.clip(brush * 1.6 + 0.5, 0, 1)
    rough = POL["R_FIELD"] + POL["R_BRUSH"] * (2 * bn - 1)
    rough = rough * (1 - edge) + POL["R_POL"] * edge; rough = rough * (1 - floor) + (POL["R_FLOOR"] + 0.04 * fine) * floor
    metal = 1.0 - 0.30 * floor
    s = C * k                                           # slope per (h per new pixel)
    gx = np.zeros_like(Hs); gy = np.zeros_like(Hs); gx[:, 1:-1] = (Hs[:, 2:] - Hs[:, :-2]) / 2 * s; gy[1:-1] = (Hs[2:] - Hs[:-2]) / 2 * s
    n_gl = np.stack([-gx, gy, np.ones_like(gx)], -1); n_gl /= np.linalg.norm(n_gl, axis=-1, keepdims=True); n_dx = n_gl * np.array([1, -1, 1], np.float32)
    stem = f"tn_{it['stem']}_blade"; ob = os.path.join(out_dir, stem)
    def save(a, suf, mode): Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8), mode).save(ob + suf + ".png")
    save(alb, "", "RGB"); save(n_dx * 0.5 + 0.5, "_n", "RGB"); save(n_gl * 0.5 + 0.5, "_n_gl", "RGB")
    save(np.stack([rough, metal, ao, np.ones_like(ao)], -1), "_rmaos", "RGBA"); save(np.clip(Hs + 1, 0, 1), "_height", "L")
    # the plain field's measured finish (the check against the recipe)
    plain = (h > -0.004) & (edge < 0.05) & have
    lum = alb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    rep = dict(L, slope_scale=round(float(C), 4), slope_scale_from_px=int(cw), recipe=POL,
               field_albedo_p50=round(float(np.median(lum[plain])), 3) if plain.any() else None,
               field_rough_p5_p50_p95=[round(float(np.percentile(rough[plain], q)), 4) for q in (5, 50, 95)] if plain.any() else None,
               polished_rough_p50=round(float(np.median(rough[(edge > 0.9) & have & (floor < 0.05)])), 4) if ((edge > 0.9) & have).any() else None,
               floor_rough_p50=round(float(np.median(rough[(floor > 0.9) & have])), 4) if ((floor > 0.9) & have).any() else None,
               plain_normal_tilt_deg_p99=round(float(np.percentile(np.degrees(np.arccos(np.clip(n_gl[plain][:, 2], -1, 1))), 99)) if plain.any() else 0.0, 4),
               out=ob)
    json.dump(rep, open(os.path.join(out_dir, "blade_polish.json"), "w"), indent=1, default=str)
    print(item, json.dumps({k_: rep[k_] for k_ in ("W", "H", "k", "px_old", "px_new", "tris", "slope_scale", "field_albedo_p50", "field_rough_p5_p50_p95", "polished_rough_p50", "floor_rough_p50", "plain_normal_tilt_deg_p99")}))
    return rep


def polished_items():
    from items import ITEMS
    return [k for k, it in ITEMS.items() if it.get("polish")]


if __name__ == "__main__":
    a = sys.argv[1:]; cmd = a[0] if a else "layout"; items = a[1:] or polished_items()
    for i in items:
        if cmd == "layout": print(json.dumps(layout(i)))
        elif cmd == "paint": paint(i)
        else: raise SystemExit("layout | paint")
