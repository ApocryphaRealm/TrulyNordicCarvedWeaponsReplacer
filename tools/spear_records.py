#!/usr/bin/env python3
r"""The spear's records (2026-11-12), written into the two Standalone plugins with plugin_records.py - no Creation Kit, no
MO2 write. The spear is a NEW item (vanilla has no spear), so it is in the Standalone editions only, never the Replacer.

Each Standalone plugin (plugin\standalone-nordic and plugin\standalone-ebony, both "TrulyNordicCarvedWeapons - Standalone.esp")
gets four records, copied from that plugin's OWN battleaxe records (TNCW_Battleaxe and its STAT and recipes, which are
the vanilla Dragonborn / Skyrim battleaxe records houseCARL copied in 1.1.0 - same masters, so no FormID needs remapping;
only the fields named below change):
  TNCW_Spear_1st   STAT  model TrulyNordic\spear\1stpersonspear.nif (the first-person model, as the battleaxe's)
  TNCW_Spear       WEAP  "Carved Nordic Spear", model TrulyNordic\spear\spear.nif, first-person model TNCW_Spear_1st;
                         everything else the battleaxe's: AnimationType TwoHandAxe (6), keywords VendorItemWeapon +
                         WeapTypeBattleaxe + the quality's material keyword (DLC2WeaponMaterialNordic / WeapMaterialEbony),
                         equip slot, sounds, impact set, block bash; stats between that quality's battleaxe and greatsword
                         (STATS below), reach a little longer than the battleaxe
  TNCW_Spear_Recipe COBJ the battleaxe's forge recipe (same materials, perk, bench), creating the spear
  TNCW_Spear_Temper COBJ the battleaxe's temper recipe, tempering the spear
FormIDs 0x827-0x82A in both plugins (the same in both, so a player can swap quality and keep the item). The spear's
EditorID is what the FOMOD's KID option tags with the spear-animation keywords (TNCW_Spear).

Every pre-existing record is left byte for byte (the old file's records are a prefix-equal subset of the new file's, in
order); the read-back prints each new record's subrecords.  Idempotent: a plugin that already has TNCW_Spear is left alone.
Run: python -I spear_records.py
"""
import os, sys, struct, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plugin_records as P
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUG = {q: os.path.join(REPO, "plugin", f"standalone-{q}", "TrulyNordicCarvedWeapons - Standalone.esp") for q in ("nordic", "ebony")}
MODEL, FIRST = "TrulyNordic\\spear\\spear.nif", "TrulyNordic\\spear\\1stpersonspear.nif"
NAME = "Carved Nordic Spear"
OBND = (-4, -76, -1, 4, 104, 1)          # the game NIF's bounds (-3.80 .. 3.80, -75.5 .. 104.0, -1 .. 1), rounded
# value, weight, damage, critical damage, speed, reach - between the quality's battleaxe and greatsword (read from these
# plugins: Nordic battleaxe 650 / 23 / 21 / 11 / 0.7 / 1.3, greatsword 585 / 19 / 20 / 10 / 0.7 / 1.3; Ebony battleaxe
# 1585 / 26 / 23 / 11, greatsword 1440 / 22 / 22 / 11): value and weight the mean, damage and critical the lower
# (greatsword) value - a whole number cannot sit between two neighbours, and the spear's reach is its advantage -
# speed as both, reach 1.4 (battleaxe and greatsword 1.3)
STATS = {"nordic": (620, 21.0, 20, 10, 0.7, 1.4), "ebony": (1510, 24.0, 22, 11, 0.7, 1.4)}

def edid(d): return next((sd[:-1].decode() for s, sd in P.subrecords(d) if s == "EDID"), "")
def by_edid(pl, label, e):
    for h, d in pl.records(label):
        if struct.unpack_from("<I", h, 8)[0] & P.COMPRESSED: d = zlib.decompress(d[4:])
        if edid(d) == e: return bytearray(h), [list(x) for x in P.subrecords(d)]
    raise KeyError(f"{label} {e} not in {pl.path}")
def fid(h): return struct.unpack_from("<I", h, 12)[0]

def build(q):
    pl = P.Plugin(PLUG[q])
    if any(edid(d) == "TNCW_Spear" for _, d in pl.records("WEAP")): print(f"{q}: spear records already present"); return None
    own = len(pl.masters) << 24; nid = pl.next_id(); F = {k: own | (nid + i) for i, k in enumerate(("stat", "weap", "recipe", "temper"))}
    # STAT
    h, s = by_edid(pl, "STAT", "TNCW_Battleaxe_1st"); struct.pack_into("<I", h, 12, F["stat"])
    P.set_sub(s, "EDID", P.zs("TNCW_Spear_1st")); P.set_sub(s, "MODL", P.zs(FIRST)); pl.add("STAT", h, P.pack_subs(s))
    # WEAP
    h, s = by_edid(pl, "WEAP", "TNCW_Battleaxe"); ba = fid(h); struct.pack_into("<I", h, 12, F["weap"])
    val, wt, dmg, crit, spd, reach = STATS[q]
    P.set_sub(s, "EDID", P.zs("TNCW_Spear")); P.set_sub(s, "OBND", struct.pack("<6h", *OBND)); P.set_sub(s, "FULL", P.zs(NAME))
    P.set_sub(s, "MODL", P.zs(MODEL)); P.set_sub(s, "WNAM", struct.pack("<I", F["stat"]))
    P.set_sub(s, "DATA", struct.pack("<IfH", val, wt, dmg))
    for x in s:
        if x[0] == "DNAM":
            dn = bytearray(x[1]); assert dn[0] == 6, ("battleaxe AnimationType is not TwoHandAxe", dn[0])
            struct.pack_into("<ff", dn, 4, spd, reach); x[1] = bytes(dn)
        if x[0] == "CRDT": cr = bytearray(x[1]); struct.pack_into("<H", cr, 0, crit); x[1] = bytes(cr)
    pl.add("WEAP", h, P.pack_subs(s))
    # COBJ x2
    for kind in ("Recipe", "Temper"):
        h, s = by_edid(pl, "COBJ", f"TNCW_Battleaxe_{kind}"); struct.pack_into("<I", h, 12, F[kind.lower()])
        cn = [x for x in s if x[0] == "CNAM"]; assert len(cn) == 1 and struct.unpack("<I", cn[0][1])[0] == ba, f"{kind}: CNAM is not the battleaxe"
        P.set_sub(s, "EDID", P.zs(f"TNCW_Spear_{kind}")); P.set_sub(s, "CNAM", struct.pack("<I", F["weap"])); pl.add("COBJ", h, P.pack_subs(s))
    pl.bump_next_id(nid + 4)
    return pl

def flat(path):
    pl = P.Plugin(path); out = []
    for g in pl.groups:
        for h, d in pl.records(g[0]): out.append((g[0], h, d))
    return pl, out

def check_and_save(pl, path):
    """as arrow_records.check_and_save: every old record still there, unchanged, in its order; the rest are the new ones"""
    old_pl, old = flat(path); tmp = path + ".new"; pl.save(tmp); new_pl, new = flat(tmp)
    it = iter(new); added = []
    for o in old:
        for n in it:
            if n == o: break
            added.append(n)
        else: raise SystemExit(f"{path}: an existing record changed or went missing ({o[0]} {fid(o[1]):08X})")
    added += list(it)
    if [s for s in old_pl.tes4 if s[0] != "HEDR"] != [s for s in new_pl.tes4 if s[0] != "HEDR"]: raise SystemExit("TES4 changed beyond HEDR")
    os.replace(tmp, path)
    v0, n0, i0 = struct.unpack_from("<fiI", old_pl.hedr()[1]); v1, n1, i1 = struct.unpack_from("<fiI", new_pl.hedr()[1])
    print(f"== {os.path.relpath(path, REPO)}: {len(old)} records kept byte for byte, {len(added)} added; HEDR count {n0} -> {n1}, next id {i0:#x} -> {i1:#x}; flags {new_pl.flags:#x}; masters {new_pl.masters}")
    for lab, h, d in added:
        print(f"   + {lab} {fid(h):08X}")
        for s, sd in P.subrecords(d):
            txt = sd[:-1].decode("latin-1") if s in ("EDID", "FULL", "MODL") else sd.hex()
            ex = ""
            if lab == "WEAP" and s == "DATA": ex = "value %d weight %.1f damage %d" % struct.unpack_from("<IfH", sd, 0)
            if lab == "WEAP" and s == "DNAM": ex = "anim %d speed %.3f reach %.3f" % (sd[0], *struct.unpack_from("<ff", sd, 4))
            if lab == "WEAP" and s == "CRDT": ex = "crit damage %d" % struct.unpack_from("<H", sd, 0)
            print(f"       {s:4} {len(sd):3}  {txt[:110]}  {ex}")

if __name__ == "__main__":
    for q in ("nordic", "ebony"):
        pl = build(q)
        if pl is not None: check_and_save(pl, PLUG[q])
