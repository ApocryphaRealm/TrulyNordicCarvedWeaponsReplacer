# Texture half of the game build: the per-density normal fix for the four items painted before dagger v2, then BC7 DDS.
#
# The fix (past-mistakes library, "One px-per-unit value for a mixed-density atlas..."): those painters turned the
# height field into normals with ONE px-per-unit value (31, the blades' density), so parts laid out denser (guards,
# caps, pommels) got proportionally weaker normals. tn_knot.maps_v3's slope is linear in that value
# (g = dH/dpixel * PX, n = normalize(-gx, gy, 1)), so recomputing at a part's real density is exactly scaling the
# stored slope n.xy/n.z by k = density / 31 and renormalising - done here per UV island (each island's median texel
# density, measured from the model's own triangles), in float, from the painter's 8-bit normal PNG.
#
# Run: python -I textures.py [item ...]      (writes <WORK>\<item>\tex\*.png and <STAGE>\textures\...\*.dds)
import os, sys, json, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from items import ITEMS, WORK, TEX_REL
STAGE = os.path.join(WORK, "stage")
TEXCONV = r"D:\Modlists\Njordlinger\tools\Skyking Toolkit\runtime\texconv.exe"
FIX_PX = 31.0
FIX = {"sword": FIX_PX, "battleaxe": FIX_PX, "greatsword": FIX_PX, "warhammer": FIX_PX, "waraxe": FIX_PX}   # war axe v2 was painted at one px/unit too

def island_density(npz, W, H):
    """Per UV island: px per model unit along the atlas u and v axes (rows of the 3D->pixel Jacobian), area-weighted,
    and whether the island's mapping is orthogonal (rows within ~10 degrees of perpendicular), so the u and v slopes can
    be corrected separately. Returns two float images (ku, kv densities) and the per-island table."""
    d = np.load(npz); V, F, UV = d["V"].astype(np.float64), d["F"], d["UV"].astype(np.float64)
    par = np.arange(len(V))
    def find(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for a, b, c in F:
        for x, y in ((a, b), (a, c)):
            rx, ry = find(x), find(y)
            if rx != ry: par[rx] = ry
    isl = np.array([find(f[0]) for f in F])
    P = V[F]; px = UV * np.array([W, H])
    e1, e2 = P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]; u1, u2 = px[:, 1] - px[:, 0], px[:, 2] - px[:, 0]
    wa = 0.5 * np.linalg.norm(np.cross(e1, e2), axis=1)
    du = np.zeros(len(F)); dv = np.zeros(len(F)); cs = np.ones(len(F)); ok = wa > 1e-6
    for i in np.where(ok)[0]:
        J = np.stack([u1[i], u2[i]], 1) @ np.linalg.pinv(np.stack([e1[i], e2[i]], 1))
        a, b = np.linalg.norm(J[0]), np.linalg.norm(J[1])
        if a < 1e-3 or b < 1e-3: ok[i] = False; continue
        du[i], dv[i], cs[i] = a, b, abs(J[0] @ J[1]) / (a * b)
    tab = {}
    for i in np.unique(isl):
        m = (isl == i) & ok
        if m.sum(): tab[int(i)] = dict(du=float(np.average(du[m], weights=wa[m])), dv=float(np.average(dv[m], weights=wa[m])),
                                     ortho=bool(np.average(cs[m], weights=wa[m]) < 0.17), area=float(wa[m].sum()))
    # Only the documented defect is corrected: a carved part laid out DENSER than the 31 px/unit the painter assumed
    # (guards, caps: normals too weak). Corrected islands must be orthogonal, near-isotropic (u and v within 25%) and
    # over 31 * 1.1; strips, hafts and other parts laid out at a lower or uneven density stay as painted - and as the
    # owner saw them in the approved renders, which used these same maps on this same mesh.
    for t in tab.values():
        t["fix"] = t["ortho"] and max(t["du"], t["dv"]) / min(t["du"], t["dv"]) < 1.25 and min(t["du"], t["dv"]) > FIX_PX * 1.1
        t["ortho"] = t["fix"]
    imgs = []
    for key in ("du", "dv"):
        img = Image.new("F", (W, H), 0.0); dr = ImageDraw.Draw(img)
        for f in range(len(F)):
            t = tab.get(int(isl[f]))
            if t: dr.polygon([(float(u), float(H - v)) for u, v in px[f]], fill=t[key] if t["ortho"] else -1.0)
        imgs.append(np.asarray(img, np.float32))
    bbox = {}
    for f in range(len(F)):
        b = bbox.setdefault(int(isl[f]), [1e9, 1e9, -1e9, -1e9]); xs = px[f][:, 0]; ys = H - px[f][:, 1]
        b[0] = min(b[0], xs.min()); b[1] = min(b[1], ys.min()); b[2] = max(b[2], xs.max()); b[3] = max(b[3], ys.max())
    return imgs[0], imgs[1], tab, bbox

def fix_normal(item, base, out_dir):
    W, H = Image.open(base + "_n.png").size
    du, dv, tab, bbox = island_density(os.path.join(WORK, item, "orig_metal.npz"), W, H)
    # pixels outside every island (gutters) and islands whose mapping is not orthogonal keep k = 1 (left as painted)
    from scipy import ndimage
    has = du != 0; idx = ndimage.distance_transform_edt(~has, return_distances=False, return_indices=True)
    du = np.where(has, du, du[idx[0], idx[1]]); dv = np.where(has, dv, dv[idx[0], idx[1]])
    ku = np.where(du > 0, du / FIX[item], 1.0); kv = np.where(dv > 0, dv / FIX[item], 1.0)
    k = np.stack([ku, kv], -1)
    n = np.asarray(Image.open(base + "_n.png").convert("RGB"), np.float32) / 255 * 2 - 1     # DX (green down)
    s = n[..., :2] / np.maximum(n[..., 2:3], 1e-3) * k
    m = np.concatenate([s, np.ones_like(s[..., :1])], -1); m /= np.linalg.norm(m, axis=-1, keepdims=True)
    new = Image.fromarray(np.clip((m * 0.5 + 0.5) * 255 + 0.5, 0, 255).astype(np.uint8), "RGB")
    new.save(os.path.join(out_dir, os.path.basename(base) + "_n.png"))
    gl = m * np.array([1, -1, 1], np.float32)
    Image.fromarray(np.clip((gl * 0.5 + 0.5) * 255 + 0.5, 0, 255).astype(np.uint8), "RGB").save(os.path.join(out_dir, os.path.basename(base) + "_n_gl.png"))
    # report: island densities, and a before/after crop of the island scaled the most
    rows = sorted(((max(t["du"], t["dv"]) / FIX[item], i) for i, t in tab.items() if t["ortho"]), reverse=True) or [(1.0, next(iter(tab)))]
    kmax, imax = rows[0]; b = bbox[imax]; pad = 12
    box = (max(0, int(b[0]) - pad), max(0, int(b[1]) - pad), min(W, int(b[2]) + pad), min(H, int(b[3]) + pad))
    if box[2] - box[0] > 700: box = (box[0], box[1], box[0] + 700, box[3])
    if box[3] - box[1] > 700: box = (box[0], box[1], box[2], box[1] + 700)
    a = Image.open(base + "_n.png").convert("RGB").crop(box); c = new.crop(box)
    sc = max(1, int(380 / max(a.size)))
    a = a.resize((a.size[0] * sc, a.size[1] * sc), Image.NEAREST); c = c.resize(a.size, Image.NEAREST)
    sheet = Image.new("RGB", (a.size[0] * 2 + 30, a.size[1] + 40), (30, 30, 30)); sheet.paste(a, (10, 30)); sheet.paste(c, (a.size[0] + 20, 30))
    d = ImageDraw.Draw(sheet); d.text((10, 8), f"{item}: before (one px/unit = 31)", fill=(230, 230, 230)); d.text((a.size[0] + 20, 8), f"after (part density up to {kmax * 31:.0f} px/unit, x{kmax:.2f})", fill=(230, 230, 230))
    sheet.save(os.path.join(WORK, f"normalfix_{item}.png"))
    sc_u = {i: round(t["du"] / FIX[item], 2) for i, t in tab.items() if t["ortho"]}
    sc_v = {i: round(t["dv"] / FIX[item], 2) for i, t in tab.items() if t["ortho"]}
    changed = [i for i in sc_u if abs(sc_u[i] - 1) > 0.1 or abs(sc_v[i] - 1) > 0.1]
    tot = sum(t["area"] for t in tab.values())
    return {"islands": len(tab), "non_orthogonal_left_as_painted": sum(1 for t in tab.values() if not t["ortho"]),
            "area_share_changed_over_10pct": round(sum(tab[i]["area"] for i in changed) / tot, 3),
            "changed": sorted({(sc_u[i], sc_v[i]) for i in changed}, reverse=True)[:12], "crop_island_k": round(kmax, 2)}

def texconv(src_png, out_dir, name, fmt, srgb=False):
    tmp = os.path.join(out_dir, name + ".png"); shutil.copy2(src_png, tmp)
    args = [TEXCONV, "-nologo", "-y", "-f", fmt, "-m", "0", "-o", out_dir] + (["-srgb"] if srgb else []) + [tmp]
    r = subprocess.run(args, capture_output=True, text=True)
    os.remove(tmp)
    if r.returncode or not os.path.isfile(os.path.join(out_dir, name + ".dds")): raise SystemExit(f"texconv failed for {src_png}: {r.stdout} {r.stderr}")

def build(item):
    it = ITEMS[item]; rep = {}
    tex_dir = os.path.join(STAGE, TEX_REL, it["stem"]); os.makedirs(tex_dir, exist_ok=True)
    fixed = os.path.join(WORK, item, "tex"); os.makedirs(fixed, exist_ok=True)
    for role, sh in it["shapes"].items():
        name = f"tn_{it['stem']}" + ("" if role == "metal" else f"_{role}")
        if sh.get("dds_from"):
            for suf in ("", "_n", "_rmaos"): shutil.copy2(sh["dds_from"] + suf + ".dds", os.path.join(tex_dir, name + suf + ".dds"))
            rep[role] = "DDS copied from the installed A5 test mod (unchanged)"; continue
        base = sh["tex"]
        for suf in ("", "_n", "_rmaos"):
            w, h = Image.open(base + suf + ".png").size
            if max(w, h) > 2048: raise SystemExit(f"{base}{suf}.png is {w}x{h}, over 2048")
        nsrc = base + "_n.png"
        if role == "metal" and item in FIX:
            rep["normal_fix"] = fix_normal(item, base, fixed); nsrc = os.path.join(fixed, os.path.basename(base) + "_n.png")
        texconv(base + ".png", tex_dir, name, "BC7_UNORM_SRGB", srgb=True)
        texconv(nsrc, tex_dir, name + "_n", "BC7_UNORM")
        texconv(base + "_rmaos.png", tex_dir, name + "_rmaos", "BC7_UNORM")
        rep[role] = name
    json.dump(rep, open(os.path.join(WORK, item, "textures_report.json"), "w"), indent=1)
    print(item, json.dumps(rep)[:600])

if __name__ == "__main__":
    for k in (sys.argv[1:] or list(ITEMS)): build(k)
