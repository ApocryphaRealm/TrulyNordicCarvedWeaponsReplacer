#!/usr/bin/env python3
r"""Writes the optional "Additional Weapons" light plugin (additional_spec.PLUGIN), one variant per quality, from the
table in additional_spec.py - no Creation Kit, no MO2 write.

  plugin\additional-nordic\<PLUGIN>   Nordic stats, recipes from the Nordic Standalone's templates
  plugin\additional-ebony\<PLUGIN>    Ebony stats, recipes from the Ebony Standalone's templates

Each run writes both files FROM SCRATCH (deterministic: the same table and templates give the same bytes). The plugin is
an ESL-flagged ESP; its masters are exactly the Bethesda masters its records reference (additional_spec.MASTER_ORDER),
never one of our plugins - so it works beside any main file. Every record is a copy of its template with each FormID
field remapped by its KNOWN position for that record type (FIDS below; an unknown subrecord on a template refuses):
a reference into a master is remapped by the master's NAME; a reference to the template plugin's own record must be one
of the same item's templates and is pointed at the matching new record (WEAP -> its STAT, recipe -> the WEAP).
Read-back: every record's subrecords are printed, and a WEAP's value / weight / damage / speed / reach / crit.
Run: python -I additional_records.py
"""
import os, sys, struct, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plugin_records as P
import additional_spec as S
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SA = "TrulyNordicCarvedWeapons - Standalone.esp"
DLC = r"D:\Modlists\Njordlinger\mods\Base Game DLC Content"      # the Bethesda DLC masters (read-only)
# a template source: "standalone" (that quality's Standalone plugin) or a Bethesda master by file name (2026-11-13, the
# bolts and the crossbow from Dawnguard.esm); a master template's references to its OWN other records stay references
# into that master (it becomes one of ours), except those to another template of the same item (-> the new record)
TEMPLATE_SOURCES = {"standalone": lambda q: os.path.join(REPO, "plugin", f"standalone-{q}", SA),
                    "Dawnguard.esm": lambda q: os.path.join(DLC, "Dawnguard.esm")}
def out_path(q): return os.path.join(REPO, "plugin", S.QUALITIES[q][0], S.PLUGIN)

# FormID fields by record type (byte offsets; None = an array of FormIDs). Layouts per the Skyrim SE record definitions
# (mutagen / xEdit): WEAP CRDT's effect SPEL at +16, STAT DNAM's material MATO at +4.
FIDS = {"STAT": {"DNAM": [4]},
        "WEAP": {"EITM": [0], "ETYP": [0], "BIDS": [0], "BAMT": [0], "KWDA": None, "INAM": [0], "WNAM": [0], "SNAM": [0],
                 "XNAM": [0], "NAM7": [0], "TNAM": [0], "UNAM": [0], "NAM9": [0], "NAM8": [0], "CNAM": [0], "YNAM": [0],
                 "ZNAM": [0], "CRDT": [16]},
        "COBJ": {"CNTO": [0], "CNAM": [0], "BNAM": [0]},
        # AMMO DATA: projectile at +0; PROJ DATA: light, muzzle flash light, explosion, sound, ... (plugin_records.FIDS)
        "AMMO": {"YNAM": [0], "ZNAM": [0], "KWDA": None, "DATA": [0]},
        "PROJ": {"DATA": [16, 20, 36, 40, 56, 60, 64, 84, 88]}}
PLAIN = {"STAT": {"EDID", "OBND", "MODL", "MODT"},
         "WEAP": {"EDID", "OBND", "FULL", "MODL", "MODT", "KSIZ", "DATA", "DNAM", "VNAM", "DESC", "EAMT"},
         "COBJ": {"EDID", "COCT", "NAM1"},
         "AMMO": {"EDID", "OBND", "FULL", "MODL", "MODT", "KSIZ"},
         "PROJ": {"EDID", "OBND", "FULL", "MODL", "MODT", "NAM1", "NAM2", "VNAM"}}
LSTRING = {"FULL", "DESC"}     # a localized master holds these as string ids: FULL is written from the table, DESC dropped
CTDA_P1_FORM = {74: True, 448: True, 659: False}   # GetGlobalValue, HasPerk (param 1 a FormID); EPTemperingItemIsEnchanted

def edid(d): return next((sd[:-1].decode() for s, sd in P.subrecords(d) if s == "EDID"), "")
def by_edid(pl, label, e):
    for h, d in pl.records(label):
        if struct.unpack_from("<I", h, 8)[0] & P.COMPRESSED: d = zlib.decompress(d[4:])
        if edid(d) == e: return bytearray(h), [list(x) for x in P.subrecords(d)]
    raise KeyError(f"{label} {e} not in {pl.path}")

def relay(src, sig, subs, remap, rec=None):
    """every FormID field of one template record through remap(v); refuses an unknown subrecord. A subrecord the table
    retargets (rec["retarget"]) is passed through untouched here and rewritten by apply_set."""
    out = []
    for s, sd in subs:
        sd = bytearray(sd)
        if rec and s in rec.get("retarget", {}): out.append([s, bytes(sd)]); continue
        if s in LSTRING and src.localized:
            if s == "FULL": out.append([s, bytes(sd)])      # replaced by the table's FULL (apply_set refuses a record without one)
            continue
        if s in FIDS[sig]:
            offs = FIDS[sig][s]
            for o in (range(0, len(sd), 4) if offs is None else offs):
                if o + 4 <= len(sd): struct.pack_into("<I", sd, o, remap(struct.unpack_from("<I", sd, o)[0]))
        elif s == "CTDA" and sig == "COBJ":
            func = struct.unpack_from("<H", sd, 8)[0]
            assert func in CTDA_P1_FORM, f"condition function {func} - layout not known here"
            assert not sd[0] & 0x04, "condition compares against a global - not handled"
            if CTDA_P1_FORM[func]: struct.pack_into("<I", sd, 12, remap(struct.unpack_from("<I", sd, 12)[0]))
            struct.pack_into("<I", sd, 24, remap(struct.unpack_from("<I", sd, 24)[0]))
        elif s not in PLAIN[sig]: raise SystemExit(f"{src.name} {sig}: subrecord {s} has no known layout here - refusing to copy it blind")
        out.append([s, bytes(sd)])
    return out

def apply_set(q, rec, subs, new_fid=None, src=None):
    if src is not None and src.localized and any(x[0] == "FULL" for x in subs) and "FULL" not in rec.get("set", {}):
        raise SystemExit(f"{rec['edid']}: its template's FULL is a string id of {src.name} - the table must give a FULL")
    for k, e in rec.get("retarget", {}).items():   # a FormID field pointed at another record of ours, by its EditorID
        P.set_sub(subs, k, struct.pack("<I", new_fid(e)))
    for k, v in rec.get("set", {}).items():
        if k in ("FULL", "MODL"): P.set_sub(subs, k, P.zs(v))
        elif k == "OBND": P.set_sub(subs, k, struct.pack("<6h", *v))
        elif k == "stats":
            val, wt, dmg, crit, spd, reach = v[q]
            P.set_sub(subs, "DATA", struct.pack("<IfH", val, wt, dmg))
            for x in subs:
                if x[0] == "DNAM": dn = bytearray(x[1]); struct.pack_into("<ff", dn, 4, spd, reach); x[1] = bytes(dn)
                if x[0] == "CRDT": cr = bytearray(x[1]); struct.pack_into("<H", cr, 0, crit); x[1] = bytes(cr)
        elif k == "ammo":     # AMMO DATA: projectile, flags (0 = a bolt: the "non-bolt" bit 0x4 clear), damage, value, weight
            dmg, val, wt = v[q]; dd = bytearray(next(x[1] for x in subs if x[0] == "DATA"))
            struct.pack_into("<fIf", dd, 8, dmg, val, wt); P.set_sub(subs, "DATA", bytes(dd))
        elif k == "NAM1": P.set_sub(subs, "NAM1", struct.pack("<H", v))
        else: raise SystemExit(f"{rec['edid']}: unknown set key {k}")
    P.set_sub(subs, "EDID", P.zs(rec["edid"]))

def build(q):
    srcs = {}; plan = []        # (rec, src plugin, header, subs, own map)
    for it in S.ADDITIONAL:
        tpl = []
        for rec in it["records"]:
            kind, e = rec["template"]
            if kind not in srcs: srcs[kind] = P.Plugin(TEMPLATE_SOURCES[kind](q))
            h, subs = by_edid(srcs[kind], rec["sig"], e); tpl.append((rec, srcs[kind], h, subs))
        for rec, src, h, subs in tpl:   # the template's own FormIDs of THIS item -> the new records
            own = {struct.unpack_from("<I", h2, 12)[0] & 0xFFFFFF: r2["fid"] for r2, s2, h2, _ in tpl if s2 is src}
            plan.append((rec, src, h, subs, own))
    # pass 1: which masters are referenced
    used = {"Skyrim.esm"}
    def collect(src, own):
        def f(v):
            if v == 0: return 0
            i = v >> 24; names = src.masters + [src.name]
            if i >= len(names): raise SystemExit(f"{v:08X}: index past {src.name}'s masters")
            if names[i] == src.name:
                if (v & 0xFFFFFF) in own: return v
                if src.name in S.MASTER_ORDER: used.add(src.name); return v
                raise SystemExit(f"{v:08X} points at a record of {src.name} that is not one of this item's templates")
            else: used.add(names[i])
            return v
        return f
    for rec, src, h, subs, own in plan:
        relay(src, rec["sig"], subs, collect(src, own), rec)
        if src.name in S.MASTER_ORDER: used.add(src.name)     # a master template's record keeps its master's FormID space
    extra = sorted(used - set(S.MASTER_ORDER))
    if extra: raise SystemExit(f"references into {extra} - not a Bethesda master in MASTER_ORDER (never master our own plugins)")
    masters = [m for m in S.MASTER_ORDER if m in used]
    # the new plugin: the template plugin's TES4 header (ESL flag, form version), HEDR 1.71, our masters
    t4src = next(iter(srcs.values()))
    hdr = bytearray(t4src.tes4_hdr); struct.pack_into("<I", hdr, 8, 0x200); struct.pack_into("<I", hdr, 12, 0)
    tes4 = [["HEDR", struct.pack("<fiI", 1.71, 0, 0x800)]]
    for m in masters: tes4 += [["MAST", P.zs(m)], ["DATA", bytes(8)]]
    tmp = out_path(q) + ".new"; os.makedirs(os.path.dirname(tmp), exist_ok=True)
    t4 = P.pack_subs(tes4); struct.pack_into("<I", hdr, 4, len(t4)); open(tmp, "wb").write(bytes(hdr) + t4)
    pl = P.Plugin(tmp); own_idx = len(masters) << 24
    def remap(src, own):
        def f(v):
            if v == 0: return 0
            nm = (src.masters + [src.name])[v >> 24]
            if nm == src.name and (v & 0xFFFFFF) in own: return own_idx | own[v & 0xFFFFFF]
            return (masters.index(nm) << 24) | (v & 0xFFFFFF)
        return f
    top = 0x7FF
    by_edid_new = {r["edid"]: r["fid"] for it in S.ADDITIONAL for r in it["records"]}
    for rec, src, h, subs, own in plan:
        out = relay(src, rec["sig"], subs, remap(src, own), rec); apply_set(q, rec, out, lambda e: own_idx | by_edid_new[e], src)
        h = bytearray(h); struct.pack_into("<I", h, 12, own_idx | rec["fid"]); pl.add(rec["sig"], h, P.pack_subs(out))
        top = max(top, rec["fid"])
    pl.bump_next_id(top + 1); pl.save(tmp); os.replace(tmp, out_path(q))
    return out_path(q)

def readback(path):
    pl = P.Plugin(path); hd = struct.unpack_from("<fiI", pl.hedr()[1])
    print(f"== {os.path.relpath(path, REPO)}: flags {pl.flags:#x} (ESL {bool(pl.flags & 0x200)}), masters {pl.masters}, "
          f"HEDR {hd[0]:.2f} records {hd[1]} next id {hd[2]:#x}")
    for g in pl.groups:
        for h, d in pl.records(g[0]):
            print(f"   {g[0]} {struct.unpack_from('<I', h, 12)[0]:08X}")
            for s, sd in P.subrecords(d):
                txt = sd[:-1].decode("latin-1") if s in ("EDID", "FULL", "MODL") else sd.hex()
                ex = ""
                if g[0] == "WEAP" and s == "DATA": ex = "value %d weight %.1f damage %d" % struct.unpack_from("<IfH", sd, 0)
                if g[0] == "WEAP" and s == "DNAM": ex = "anim %d speed %.3f reach %.3f" % (sd[0], *struct.unpack_from("<ff", sd, 4))
                if g[0] == "WEAP" and s == "CRDT": ex = "crit damage %d" % struct.unpack_from("<H", sd, 0)
                print(f"       {s:4} {len(sd):3}  {txt[:100]}  {ex}")

if __name__ == "__main__":
    for q in S.QUALITIES: readback(build(q))
