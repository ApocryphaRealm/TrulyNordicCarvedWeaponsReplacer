#!/usr/bin/env python3
r"""The quiver / arrow records (2026-11-12), written into the repo's three plugins with plugin_records.py:

  Replacer ESP (plugin\TrulyNordicCarvedWeapons.esp): an override of AMMO DLC2NordicArrow (Dragonborn.esm 02623B), copied
      from Dragonborn.esm with only its model changed to meshes\TrulyNordic\quiver\quiver.nif (the No-ESP edition does the
      same through SkyPatcher's ammo patcher, model=). The PROJ is NOT overridden: its model ships as a loose file at the
      vanilla path in both Replacer editions (SkyPatcher has no projectile model operation, and other mods edit that PROJ -
      Shoot Straight in Njordlinger - which an override from us would undo).
  Standalone - Nordic (plugin\standalone-nordic): new TNCW_NordicArrow (AMMO, the Nordic arrow's numbers), its own
      TNCW_NordicArrowProjectile (PROJ, the Nordic arrow projectile's numbers, our flight model) and
      TNCW_NordicArrow_Recipe (COBJ, Dragonborn's DLC2RecipeArrowNordic: same materials, perk, global and bench, 24 made).
  Standalone - Ebony (plugin\standalone-ebony, masters Skyrim + Update only): the same three with the Ebony arrow's
      numbers (Skyrim.esm EbonyArrow / ArrowEbonyProjectile); vanilla has no ebony arrow recipe, so the recipe follows the
      Nordic one's shape with the Ebony pieces' perk (Ebony Smithing) and an Ebony Ingot in place of the steel and
      quicksilver: 1 Firewood + 1 Ebony Ingot -> 24 at the forge (a choice made here - see NOTES-quiver.md).

Every pre-existing record is left byte for byte (checked: the old file's records are a prefix-equal subset of the new
file's, in order); the read-back prints each new record's subrecords. Masters are read-only.
Run: python -I arrow_records.py [--data <game Data dir>] [--dlc <folder holding Dragonborn.esm>]
"""
import os, sys, struct, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plugin_records as P
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser(); ap.add_argument("--data", default=r"D:\Modlists\Njordlinger\Stock Game\Data")
ap.add_argument("--dlc", default=r"D:\Modlists\Njordlinger\mods\Base Game DLC Content"); a = ap.parse_args()
SK = P.Plugin(os.path.join(a.data, "Skyrim.esm")); DB = P.Plugin(os.path.join(a.dlc, "Dragonborn.esm"))
QUIVER, FLIGHT = "TrulyNordic\\quiver\\quiver.nif", "TrulyNordic\\quiver\\arrowflight.nif"
MODT0 = bytes.fromhex("020000000000000000000000")          # a form-44 model-hash header with no hashes (as Dragonborn's own)
ESP = os.path.join(REPO, "plugin", "TrulyNordicCarvedWeapons.esp")
SAN = os.path.join(REPO, "plugin", "standalone-nordic", "TrulyNordicCarvedWeapons - Standalone.esp")
SAE = os.path.join(REPO, "plugin", "standalone-ebony", "TrulyNordicCarvedWeapons - Standalone.esp")
DB_AMMO, DB_PROJ, DB_COBJ = 0x0202623B, 0x0202623A, 0x0203CF53
SK_AMMO, SK_PROJ = 0x000139BF, 0x0003BE17
FIREWOOD, INGOT_EBONY, PERK_EBONY, FORGE = 0x0006F993, 0x0005AD9D, 0x000CB412, 0x00088105

def has(pl, label, edid):
    for h, d in pl.records(label):
        if any(s == "EDID" and sd[:-1].decode() == edid for s, sd in P.subrecords(d)): return True
    return False
def model(subs, path): P.set_sub(subs, "MODL", P.zs(path)); P.set_sub(subs, "MODT", MODT0, after="MODL"); return subs

def replacer():
    pl = P.Plugin(ESP)
    if any(struct.unpack_from("<I", h, 12)[0] == DB_AMMO for h, _ in pl.records("AMMO")): print("replacer: AMMO override already present"); return None
    h, subs = P.copy_record(DB, "AMMO", DB_AMMO, pl, strings={"FULL": "Carved Nordic Arrow"})
    model(subs, QUIVER); pl.add("AMMO", h, P.pack_subs(subs)); return pl

def standalone(path, quality):
    pl = P.Plugin(path)
    if has(pl, "AMMO", "TNCW_NordicArrow"): print(f"{quality}: arrow records already present"); return None
    own = len(pl.masters) << 24; nid = pl.next_id(); F = {k: own | (nid + i) for i, k in enumerate(("ammo", "proj", "cobj"))}
    src = DB if quality == "nordic" else SK
    pa, pp = (DB_AMMO, DB_PROJ) if quality == "nordic" else (SK_AMMO, SK_PROJ)
    # PROJ
    h, subs = P.copy_record(src, "PROJ", pp, pl, new_fid=F["proj"], strings={"FULL": "Carved Nordic Arrow"})
    P.set_sub(subs, "EDID", P.zs("TNCW_NordicArrowProjectile")); model(subs, FLIGHT); pl.add("PROJ", h, P.pack_subs(subs))
    # AMMO -> our PROJ
    h, subs = P.copy_record(src, "AMMO", pa, pl, new_fid=F["ammo"], strings={"FULL": "Carved Nordic Arrow"})
    P.set_sub(subs, "EDID", P.zs("TNCW_NordicArrow")); model(subs, QUIVER)
    for s in subs:
        if s[0] == "DATA": s[1] = struct.pack("<I", F["proj"]) + s[1][4:]
    pl.add("AMMO", h, P.pack_subs(subs))
    # COBJ
    if quality == "nordic":
        h, subs = P.copy_record(DB, "COBJ", DB_COBJ, pl, new_fid=F["cobj"])
        P.set_sub(subs, "EDID", P.zs("TNCW_NordicArrow_Recipe")); P.set_sub(subs, "CNAM", struct.pack("<I", F["ammo"]))
    else:
        h = bytearray(DB.find("COBJ", DB_COBJ)[0]); struct.pack_into("<I", h, 12, F["cobj"])
        perk = bytearray.fromhex("000000000000803fc001540000000000000000000000000000000000ffffffff"); struct.pack_into("<I", perk, 12, PERK_EBONY)
        subs = [["EDID", P.zs("TNCW_NordicArrow_Recipe")], ["COCT", struct.pack("<I", 2)],
                ["CNTO", struct.pack("<Ii", FIREWOOD, 1)], ["CNTO", struct.pack("<Ii", INGOT_EBONY, 1)], ["CTDA", bytes(perk)],
                ["CNAM", struct.pack("<I", F["ammo"])], ["BNAM", struct.pack("<I", FORGE)], ["NAM1", struct.pack("<H", 24)]]
    pl.add("COBJ", h, P.pack_subs(subs)); pl.bump_next_id(nid + 3)
    return pl

def flat(path):
    b = open(path, "rb").read(); pl = P.Plugin(path); out = []
    for g in pl.groups:
        for h, d in pl.records(g[0]): out.append((g[0], h, d))
    return pl, out

def check_and_save(pl, path):
    old_pl, old = flat(path); tmp = path + ".new"; pl.save(tmp); new_pl, new = flat(tmp)
    # every old record still there, unchanged, in its order; the rest are the new ones
    it = iter(new); added = []
    for o in old:
        for n in it:
            if n == o: break
            added.append(n)
        else: raise SystemExit(f"{path}: an existing record changed or went missing ({o[0]} {struct.unpack_from('<I', o[1], 12)[0]:08X})")
    added += list(it)
    if [s for s in old_pl.tes4 if s[0] != "HEDR"] != [s for s in new_pl.tes4 if s[0] != "HEDR"]: raise SystemExit("TES4 changed beyond HEDR")
    os.replace(tmp, path)
    v0, n0, i0 = struct.unpack_from("<fiI", old_pl.hedr()[1]); v1, n1, i1 = struct.unpack_from("<fiI", new_pl.hedr()[1])
    print(f"== {os.path.relpath(path, REPO)}: {len(old)} records kept byte for byte, {len(added)} added; HEDR count {n0} -> {n1}, next id {i0:#x} -> {i1:#x}; flags {new_pl.flags:#x}; masters {new_pl.masters}")
    for lab, h, d in added:
        print(f"   + {lab} {struct.unpack_from('<I', h, 12)[0]:08X}")
        for s, sd in P.subrecords(d):
            txt = sd[:-1].decode("latin-1") if s in ("EDID", "FULL", "MODL") else sd.hex()
            print(f"       {s:4} {len(sd):3}  {txt[:120]}")

for path, fn in ((ESP, replacer), (SAN, lambda: standalone(SAN, "nordic")), (SAE, lambda: standalone(SAE, "ebony"))):
    pl = fn()
    if pl is not None: check_and_save(pl, path)
