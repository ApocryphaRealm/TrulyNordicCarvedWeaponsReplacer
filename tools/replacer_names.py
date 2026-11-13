#!/usr/bin/env python3
r"""The Replacer's item names (2026-11-13) - one convention, "Carved Nordic <Type>", across every file of the mod.

The owner (06:41): "If you're going to call one carved Nordic, you may as well call all of them carved Nordic. I just
want the naming convention to be consistent one way or the other across all the weapons." (06:48, on the Replacer
keeping the vanilla names): "Yes they should rename them".

Replacer ESP (plugin\TrulyNordicCarvedWeapons.esp), written in place, idempotent:
  - every WEAP and AMMO override it holds (the 8 Dragonborn Nordic weapons, their 303 enchanted copies, the Nordic
    arrow) gets "Carved " put before "Nordic" in its name, keeping the enchantment's pattern: "Virtuous Nordic Sword" ->
    "Virtuous Carved Nordic Sword", "Nordic Mace of Fear" -> "Carved Nordic Mace of Fear". Refuses a name without
    exactly one "Nordic ".
  - an override of ARMO DLC2ArmorNordicShield (Dragonborn.esm 026236) is added: Dragonborn's record byte for byte
    (Dragonborn masters Skyrim + Update, ours Skyrim + Update + Dragonborn, so every FormID keeps its index), with the
    two localized strings written as plain text - FULL "Carved Nordic Shield", DESC empty (Dragonborn's is string 0,
    the empty string). Masters, the light flag and every other record are left as they were.
Replacer No-ESP: names_ini_lines() gives build-packages.py the SkyPatcher lines, read back from the ESP (one
filterBy<Type>=Dragonborn.esm|<id>:fullName=~<name>~ line per record, by FormID - nothing else is matched): the 8 base
weapons, the arrow and the shield. NOT the enchanted copies (DLC2Ench*): SkyPatcher has only a fixed-text fullName= (no
prefix or replace, and no name filter for weapons), and enchantment overhauls re-enchant and rename those records - in
Njordlinger Thaumaturgy.esp wins 311 of them and 220 carry a different name ("Sanctified Nordic Warhammer", "... of
Exhaustion"), so a fixed vanilla-pattern name would label the item with an enchantment it does not have (read-back
2026-11-13, housecarl_records skypatcher overlay). Pass enchanted=True to get them anyway.
Run: python -I replacer_names.py [--dlc <folder holding Dragonborn.esm>]
"""
import os, sys, struct, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plugin_records as P
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESP = os.path.join(REPO, "plugin", "TrulyNordicCarvedWeapons.esp")
DB_SHIELD = 0x02026236
SHIELD_NAME = "Carved Nordic Shield"
FILTER = {"WEAP": "filterByWeapons", "AMMO": "filterByAmmos", "ARMO": "filterByArmors"}

def carved(name):
    if "Carved Nordic " in name: return name
    assert name.count("Nordic ") == 1, f"name {name!r}: not exactly one 'Nordic '"
    return name.replace("Nordic ", "Carved Nordic ")

def rename(pl):
    n = 0
    for g in pl.groups:
        if g[0] not in ("WEAP", "AMMO"): continue
        body = g[2]; o = 0; out = bytearray()
        while o < len(body):
            h = bytearray(body[o:o + 24]); ds = struct.unpack_from("<I", h, 4)[0]; d = bytes(body[o + 24:o + 24 + ds]); o += 24 + ds
            assert not struct.unpack_from("<I", h, 8)[0] & P.COMPRESSED, "compressed record"
            subs = P.subrecords(d)
            for s in subs:
                if s[0] == "FULL":
                    new = carved(s[1][:-1].decode("latin-1"))
                    if P.zs(new) != s[1]: s[1] = P.zs(new); n += 1
            d = P.pack_subs(subs); struct.pack_into("<I", h, 4, len(d)); out += h + d
        g[2] = out
    return n

def add_shield(pl, db):
    if any(struct.unpack_from("<I", h, 12)[0] == DB_SHIELD for h, _ in pl.records("ARMO")): return False
    assert db.masters == pl.masters[:len(db.masters)] and pl.masters[len(db.masters)] == db.name, "master layouts differ - FormIDs would need remapping"
    h, d = db.find("ARMO", DB_SHIELD); subs = []
    for s, sd in P.subrecords(d):
        if s == "FULL": sd = P.zs(SHIELD_NAME)
        elif s == "DESC":
            assert sd == b"\0\0\0\0", "the shield's DESC is not the empty string"; sd = b"\0"
        subs.append([s, sd])
    pl.add("ARMO", h, P.pack_subs(subs)); return True

def overrides(path=ESP):
    """(type, FormID within Dragonborn.esm, EditorID, name) for every override in the ESP"""
    pl = P.Plugin(path); out = []
    for lab in FILTER:
        for h, d in pl.records(lab):
            fid = struct.unpack_from("<I", h, 12)[0]; idx = fid >> 24
            assert idx < len(pl.masters) and pl.masters[idx] == "Dragonborn.esm", f"{lab} {fid:08X} is not a Dragonborn override"
            subs = P.subrecords(d)
            name = next(sd[:-1].decode("latin-1") for s, sd in subs if s == "FULL")
            edid = next(sd[:-1].decode("latin-1") for s, sd in subs if s == "EDID")
            out.append((lab, fid & 0xFFFFFF, edid, name))
    return out

def names_ini_lines(lab, enchanted=False):
    return [f"{FILTER[lab]}=Dragonborn.esm|{fid:X}:fullName=~{name}~" for t, fid, edid, name in overrides()
            if t == lab and (enchanted or not edid.startswith("DLC2Ench"))]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--dlc", default=r"D:\Modlists\Njordlinger\mods\Base Game DLC Content"); a = ap.parse_args()
    pl = P.Plugin(ESP); db = P.Plugin(os.path.join(a.dlc, "Dragonborn.esm"))
    n = rename(pl); s = add_shield(pl, db); pl.save(ESP)
    o = overrides(); print(f"renamed {n}; shield override {'added' if s else 'already present'}; {len(o)} overrides:",
                         {t: sum(1 for x in o if x[0] == t) for t in FILTER})
    bad = [x for x in o if not x[3].count("Carved Nordic ") == 1]
    assert not bad, bad
