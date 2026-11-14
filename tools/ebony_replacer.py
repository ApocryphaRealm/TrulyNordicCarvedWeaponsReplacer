#!/usr/bin/env python3
r"""The Ebony REPLACER (1.3.0, 2026-11-13): the black-and-gold Carved Ebony models on the VANILLA Ebony weapons, and on the
Wolf Ebony weapons of Legacy of Ysgramor.

The owner, 2026-11-13 20:41: "another couple FOMOD options for the installer to make the Ebony replacer also replace the
vanilla Ebony weapons ... And I also want an option to replace the Ebony Wolf equipment from legacy of YSGRAMOR";
20:46: "there's two different legacy of YSGRAMOR ... the original by Nordwar UA, and ... another version by Xtudo";
20:57: players who do not like the Ebony Wolf set (our other mod) "can have our truly Nordic set replace the ebony
weapons instead, or just have them as an additional set of Nordic styled ebony weapons".

WHAT IT REPLACES (Skyrim.esm; read 2026-11-13 from the masters, the counts are asserted)
    WEAP  8 base Ebony weapons (sword, war axe, mace, dagger, battleaxe, greatsword, warhammer, bow) + their 303
          enchanted copies = 311 - every WEAP whose model is one of the eight vanilla Ebony models, except Nettlebane
          (T03Nettlebane: a unique artifact on the Ebony dagger model, with its own first-person STAT - mods give it its
          own model; the No-ESP edition leaves it alone too, its STAT is not the Ebony dagger's); the Ebony Blade has
          its own model and is left alone
    AMMO  EbonyArrow (139BF) - the quiver/arrow model; the arrow in flight (PROJ ArrowEbonyProjectile) as a loose file
          at its vanilla path, as the Nordic Replacer does
    ARMO  ArmorEbonyShield (13964) + its 15 enchanted copies - NAMES only; the model is the loose file at the one vanilla
          path the ARMO and its ARMA (EbonyShieldAA) both use, weapons\ebony\ebonyshield.nif (SkyPatcher cannot set an
          armour addon's model, so the Nordic Replacer's shield is loose too)
    First-person: each vanilla Ebony weapon's 1st-person STAT points at weapons\ebony\1stpersonebony<x>.nif (the bow's at
    its 3rd-person ebonybowskinned.nif); our ebony copies of the Nordic Replacer's first-person files ship there.
    Checked against vanilla (cmp of the vanilla Ebony and Nordic NIFs, 2026-11-13): the same Prn per weapon type except
    the greatsword's 3rd person (vanilla Nordic 'WeaponSword', vanilla Ebony 'WeaponBack'; ours keeps the Nordic file's,
    as the shipped Nordic Replacer does); the bow has the same seven Bow_* bones (our bow is skinned to the Nordic bow's,
    which match); the arrow, flight and shield files have the vanilla node layout (Arrow / ArrowQuiver, the flight's
    TracerRoot / AddOnNode99 / Flow, Prn QUIVER / SHIELD).

NAMES - the Nordic Replacer's convention ("Carved " before the material): "Ebony Sword" -> "Carved Ebony Sword",
"Ebony Sword of Fire" -> "Carved Ebony Sword of Fire", "Ebony Arrow" -> "Carved Ebony Arrow". The ESP renames every
record it overrides (enchanted copies too, as the Nordic ESP does); the No-ESP edition renames the base items only
(enchantment overhauls rename the enchanted copies - see replacer_names.py).

TWO EDITIONS (build-packages.py, main files "Replacer - Ebony - ESP" / "Replacer - Ebony - No ESP")
    ESP     plugin\replacer-ebony\TrulyNordicCarvedWeapons - Ebony Replacer.esp: a light plugin, masters Skyrim.esm,
            Update.esm, Dawnguard.esm. Each record is the LAST Bethesda master's version (Update.esm for the war axe,
            dagger and mace, Dawnguard.esm for the arrow, Skyrim.esm for the rest) copied byte for byte - those masters'
            own master lists are prefixes of ours, so every FormID keeps its index - with only FULL / DESC (written as
            plain text: the masters are localized, ours is not), and for a WEAP / AMMO the model (MODL; MODT emptied as
            arrow_records.py does) changed.
    No ESP  SkyPatcher: the model by the vanilla first-person STAT (filterByFirstPersonModelOr, as the Nordic edition,
            so enchanted and added copies that show the vanilla Ebony first-person model change too), the arrow's model
            by FormID, the base names by FormID.

LEGACY OF YSGRAMOR - the Wolf Ebony WEAPONS and SHIELD (the Wolf Ebony helmet, armour (two), gauntlets and boots are
armour, which this mod has no models for, and stay as they are)
    Plugins read 2026-11-13: NordwarUA's NW_Companions_Replacer_Light.esp (Nexus 109963, full ESP, FormIDs 0x12C4-0x1870)
    and Xtudo's fixes (Nexus 111121): "Fixes" and "Fixes - Non Wuuthrad - Shield" ship the SAME filename ESL-flagged and
    COMPACTED (0x800-0x84A), "Fixes RMB version" and "Fixes - Default non ESL" keep the original FormIDs, and "Fixes -
    Standalone version" is a different plugin, NW_Wolf_Armor_Standalone.esp (0xD62-0xDCB). Every variant points the
    items at the same meshes, meshes\NordWar\Companions\Weapons\<X>Ebony.nif, used for BOTH views (each first-person
    STAT names the third-person file).
    So: the MODELS are loose files at those paths (our ebony first-person files, one per weapon; the shield), which
    serve every variant and every view; SkyPatcher sets the third-person model to our own file (so the third person
    matches the Nordic Replacer's exactly) and the name, per plugin, in an INI named after the plugin (it loads only
    when that plugin is active - no master). The weapon lines match by the first-person STAT, never by the weapon's
    FormID: the original and the compacted plugin share one filename, and a light plugin masks a FormID to its low 12
    bits, so the original's WEAP 0x1840 would land on the compacted plugin's recipe 0x840 - while neither plugin has a
    record at the other's STAT FormIDs (0x12D2-0x12D6 masks to 0x2D2-0x2D6, below a light plugin's range; 0x80E-0x812
    is below the original's) and the same holds for the two shield ARMOs (0x185A / 0x834). loyscan below proves it.
    Names: "Carved " before the whole name, "Wolf Ebony Sword" -> "Carved Wolf Ebony Sword" (the items keep their own
    identity beside the Carved Ebony ones).
    The Runic Ebony battleaxe / shield of the Standalone version are Wuuthrad / Ysgramor-shield models, not Wolf Ebony,
    and are left alone.

Run:  python -I ebony_replacer.py [--data <folder with Skyrim.esm, Update.esm>] [--dlc <folder with Dawnguard.esm>]
                                  [--strings <folder with skyrim_english.*strings>]      builds the ESP
      python -I ebony_replacer.py --stage      writes the replacer's ebony first-person / shield / flight copies
      python -I ebony_replacer.py --loyscan <plugin> ...   checks the LoY FormID layout this file relies on
"""
import os, sys, struct, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE); sys.path.insert(0, HERE)
import plugin_records as P
from items import ITEMS, MESH_REL

PLUGIN = "TrulyNordicCarvedWeapons - Ebony Replacer.esp"
ESP = os.path.join(REPO, "plugin", "replacer-ebony", PLUGIN)
MASTERS = ["Skyrim.esm", "Update.esm", "Dawnguard.esm"]
MODT0 = bytes.fromhex("020000000000000000000000")
VAN = "meshes\\weapons\\ebony\\"
# vanilla third-person model (lower case, as MODL holds it) -> (our item, its 1st-person STAT in Skyrim.esm, the 1st-person file)
WEAPONS = {
    "weapons\\ebony\\ebonysword.nif": ("sword", 0x036BDF, VAN + "1stpersonebonysword.nif"),
    "weapons\\ebony\\ebonywaraxe.nif": ("waraxe", 0x036BDA, VAN + "1stpersonebonywaraxe.nif"),
    "weapons\\ebony\\ebonymace.nif": ("mace", 0x036BDE, VAN + "1stpersonebonymace.nif"),
    "weapons\\ebony\\ebonydagger.nif": ("dagger", 0x036BDC, VAN + "1stpersonebonydagger.nif"),
    "weapons\\ebony\\ebonybattleaxe.nif": ("battleaxe", 0x036BDB, VAN + "1stpersonebonybattleaxe.nif"),
    "weapons\\ebony\\ebonygreatsword.nif": ("greatsword", 0x036BDD, VAN + "1stpersonebonygreatsword.nif"),
    "weapons\\ebony\\ebonywarhammer.nif": ("warhammer", 0x036BE0, VAN + "1stpersonebonywarhammer.nif"),
    "weapons\\ebony\\ebonybowskinned.nif": ("bow", 0x0596E4, VAN + "ebonybowskinned.nif"),
}
BASE_WEAP = {0x0139B1: "sword", 0x0139AB: "waraxe", 0x0139B0: "mace", 0x0139AE: "dagger", 0x0139AC: "battleaxe",
             0x0139AF: "greatsword", 0x0139B2: "warhammer", 0x0139AD: "bow"}
# every weapon item a Replacer - Ebony file can install (the alternates included): first-person copies are staged for each
REPLACER_WEAPONS = ["sword", "sword2", "battleaxe", "greatsword", "warhammer", "waraxe", "dagger", "dagger2", "mace", "mace2", "bow"]
AMMO_FID = 0x0139BF
FLIGHT_FILE = VAN + "ebonyarrowprojectile.nif"              # PROJ ArrowEbonyProjectile 03BE17
SHIELD_MODEL = "weapons\\ebony\\ebonyshield.nif"
SHIELD_FILE = "meshes\\" + SHIELD_MODEL
EXPECT = {"WEAP": 311, "AMMO": 1, "ARMO": 16}
SKIP = {0x01C492}           # T03Nettlebane: a unique artifact on the vanilla Ebony dagger model with its OWN first-person STAT
FILTER = {"WEAP": "filterByWeapons", "AMMO": "filterByAmmos", "ARMO": "filterByArmors"}

# Legacy of Ysgramor: plugin -> [(item, first-person STAT FormIDs in that plugin (every known layout), our name)];
# shield: plugin -> (ARMO FormIDs, name). loyscan() re-reads the plugins and refuses a layout this table gets wrong.
LOY_NAMES = {"sword": "Carved Wolf Ebony Sword", "greatsword": "Carved Wolf Ebony Greatsword", "dagger": "Carved Wolf Ebony Dagger",
             "battleaxe": "Carved Wolf Ebony Battleaxe", "waraxe": "Carved Wolf Ebony War Axe"}
LOY_SHIELD_NAME = "Carved Wolf Ebony Shield"
LOY_FILES = {"sword": "SwordEbony.nif", "greatsword": "GreatswordEbony.nif", "dagger": "DaggerEbony.nif",
             "battleaxe": "BattleAxeEbony.nif", "waraxe": "AxeEbony.nif", "shield": "ShieldEbony.nif"}
LOY_DIR = "meshes\\NordWar\\Companions\\Weapons\\"
LOY = {
    # NordwarUA original (and Xtudo's RMB / Default non ESL files): full ESP / Xtudo's Fixes + Non Wuuthrad: same name, light
    "NW_Companions_Replacer_Light.esp": dict(
        weapons={"sword": (0x12D5, 0x811), "greatsword": (0x12D4, 0x810), "dagger": (0x12D3, 0x80F),
                 "battleaxe": (0x12D2, 0x80E), "waraxe": (0x12D6, 0x812)},
        shield=(0x185A, 0x834)),
    # Xtudo's "Fixes - Standalone version"
    "NW_Wolf_Armor_Standalone.esp": dict(
        weapons={"sword": (0xD84,), "greatsword": (0xD87,), "dagger": (0xD88,), "battleaxe": (0xD82,), "waraxe": (0xD83,)},
        shield=(0xD7B,)),
}
LOY_WEAP_EDID = {"sword": "NW_Wolf_Ebony_Sword", "greatsword": "NW_Wolf_Ebony_Greatsword", "dagger": "NW_Wolf_Ebony_Dagger",
                 "battleaxe": "NW_Wolf_Ebony_Battleaxe", "waraxe": "NW_Wolf_Ebony_WarAxe"}
LOY_SHIELD_EDID = ("NW_Wolf_Shield_Ebony", "NW_Wolf_Ebony_Shield")


def at(item): return ITEMS[item].get("path_stem", ITEMS[item]["stem"])
def our_model(item): return f"TrulyNordic\\ebony\\{at(item)}\\{at(item)}.nif"     # MODL form (no 'meshes\')
def carved(name):
    if "Carved Ebony " in name: return name
    assert name.count("Ebony ") == 1, f"name {name!r}: not exactly one 'Ebony '"
    return name.replace("Ebony ", "Carved Ebony ")


# ------------------------------------------------------------------ localized strings (the masters' string tables)
def read_strings(folder, plugin="skyrim"):
    out = {}
    for ext in ("strings", "dlstrings", "ilstrings"):
        b = open(os.path.join(folder, f"{plugin}_english.{ext}"), "rb").read(); n, size = struct.unpack_from("<II", b, 0)
        base = 8 + n * 8
        for i in range(n):
            sid, off = struct.unpack_from("<II", b, 8 + i * 8); p = base + off
            if ext != "strings": p += 4
            raw = b[p:b.index(b"\0", p)]
            try: out[sid] = raw.decode("utf-8")
            except UnicodeDecodeError: out[sid] = raw.decode("latin-1")
    return out


def find_any(pl, label, fid):
    try: return pl.find(label, fid)
    except KeyError: return None


def targets(sk):
    """(label, FormID) of every record the ESP overrides, read from Skyrim.esm"""
    out = []
    for h, d in sk.records("WEAP"):
        if struct.unpack_from("<I", h, 8)[0] & P.COMPRESSED: continue          # none of the Ebony weapons is compressed
        subs = dict((s, v) for s, v in P.subrecords(d))
        m = subs.get("MODL", b"")[:-1].decode("latin-1").lower()
        fid = struct.unpack_from("<I", h, 12)[0]
        if m in WEAPONS and fid not in SKIP: out.append(("WEAP", fid))
    out.append(("AMMO", AMMO_FID))
    for h, d in sk.records("ARMO"):
        if struct.unpack_from("<I", h, 8)[0] & P.COMPRESSED: continue
        subs = dict((s, v) for s, v in P.subrecords(d))
        if subs.get("MOD2", b"")[:-1].decode("latin-1").lower() == SHIELD_MODEL: out.append(("ARMO", struct.unpack_from("<I", h, 12)[0]))
    return out


def build_esp(data, dlc, strings):
    sk = P.Plugin(os.path.join(data, "Skyrim.esm")); up = P.Plugin(os.path.join(data, "Update.esm"))
    dg = P.Plugin(os.path.join(dlc, "Dawnguard.esm")); ST = read_strings(strings)
    for m in (sk, up, dg): assert m.masters == MASTERS[:len(m.masters)] and MASTERS[len(m.masters)] == m.name, f"{m.name}: master layout differs"
    tg = targets(sk); counts = {k: sum(1 for t in tg if t[0] == k) for k in EXPECT}
    assert counts == EXPECT, f"target counts {counts}, expected {EXPECT}"
    pl = P.Plugin(os.path.join(REPO, "plugin", "TrulyNordicCarvedWeapons.esp"))      # its TES4 record header (light flag) only
    pl.tes4 = [["HEDR", struct.pack("<fiI", 1.71, 0, 0x800)], ["CNAM", P.zs("ApocryphaRealm")],
               ["SNAM", P.zs("Truly Nordic Carved Weapons Replacer - Ebony Replacer ESP: the Carved Ebony models and names on "
                             "the vanilla Ebony weapons, arrow and shield.")]]
    for m in MASTERS: pl.tes4 += [["MAST", P.zs(m)], ["DATA", b"\0" * 8]]
    pl.groups = []; src_count = {}
    for label, fid in tg:
        src = next(m for m in (dg, up, sk) if find_any(m, label, fid))
        src_count[src.name] = src_count.get(src.name, 0) + 1
        h, d = src.find(label, fid); _, skd = sk.find(label, fid)
        sksub = dict((s, v) for s, v in P.subrecords(skd))
        def text(sig):
            sid = struct.unpack_from("<I", sksub[sig])[0]
            return "" if sid == 0 else ST[sid]
        subs = []
        for s, v in P.subrecords(d):
            if s in ("FULL", "DESC", "ONAM"):
                t = text(s) if s in sksub else ""
                v = P.zs(carved(t) if s == "FULL" else t)
            elif s == "MODL" and label == "WEAP":
                v = P.zs(our_model(WEAPONS[v[:-1].decode("latin-1").lower()][0]))
            elif s == "MODL" and label == "AMMO":
                v = P.zs(our_model("quiver"))
            elif s == "MODT" and label in ("WEAP", "AMMO"):
                v = MODT0
            subs.append([s, v])
        pl.add(label, h, P.pack_subs(subs))
    os.makedirs(os.path.dirname(ESP), exist_ok=True); pl.save(ESP)
    print(f"wrote {ESP}: {counts} overrides; record sources {src_count}")
    return counts


def overrides(path=ESP):
    """(type, FormID within Skyrim.esm, EditorID, name, model) for every override in the ESP"""
    pl = P.Plugin(path); out = []
    assert pl.masters == MASTERS, pl.masters
    for lab in FILTER:
        for h, d in pl.records(lab):
            fid = struct.unpack_from("<I", h, 12)[0]; assert fid >> 24 == 0, f"{lab} {fid:08X} is not a Skyrim.esm record"
            sub = dict((s, v) for s, v in P.subrecords(d))
            out.append((lab, fid, sub["EDID"][:-1].decode("latin-1"), sub["FULL"][:-1].decode("latin-1"),
                        sub.get("MODL", b"\0")[:-1].decode("latin-1")))
    return out


# ------------------------------------------------------------------ the No-ESP edition's SkyPatcher lines
def model_lines():
    return [f"filterByFirstPersonModelOr=Skyrim.esm|{stat:X}:model={our_model(item)}" for item, stat, _ in WEAPONS.values()]
def ammo_lines(): return [f"filterByAmmos=Skyrim.esm|{AMMO_FID:X}:model={our_model('quiver')}"]
def names_lines(lab):
    """base items only (EditorIDs not starting with 'Ench'), read back from the ESP"""
    return [f"{FILTER[lab]}=Skyrim.esm|{fid:X}:fullName=~{name}~" for t, fid, edid, name, _ in overrides()
            if t == lab and not edid.startswith("Ench") ]

def loy_lines(plugin, kind, models):
    r"""kind 'weapon': model (our third-person file) + name per Wolf Ebony weapon, by its first-person STAT; 'armor': the
    shield's name. models: the item each LoY weapon takes (the installer's sword / dagger choice decides the FILE at our
    shared path, so 'sword' covers both sword options)."""
    t = LOY[plugin]
    if kind == "armor":
        return [f"filterByArmors={','.join(f'{plugin}|{x:X}' for x in t['shield'])}:fullName=~{LOY_SHIELD_NAME}~"]
    return [f"filterByFirstPersonModelOr={','.join(f'{plugin}|{x:X}' for x in stats)}:model={our_model(models[item])}:fullName=~{LOY_NAMES[item]}~"
            for item, stats in t["weapons"].items()]


# ------------------------------------------------------------------ the staged ebony copies the replacer ships
def stage():
    r"""<EB_STAGE>\<item>\replacer\first.nif: the ebony copy of the item's Nordic Replacer first-person file (the bow: of
    its one skinned file); <EB_STAGE>\shield*\replacer\shield.nif and <EB_STAGE>\quiver\replacer\flight.nif: copies of
    the Ebony look's shield and flight. build-packages.py puts them at the vanilla Ebony / LoY paths."""
    import shutil
    import ebony as EBL
    STAGE_FIRST = {i: "meshes\\dlc02\\weapons\\nordic\\" + ITEMS[i]["first"] for i in REPLACER_WEAPONS if i != "bow"}
    STAGE_FIRST["bow"] = None
    n = 0
    for item, rel in STAGE_FIRST.items():
        dst = os.path.join(EBL.EB_STAGE, item, "replacer", "first.nif")
        if item == "bow": src = os.path.join(EBL.EB_STAGE, "bow", EBL.EB_MESH, "bow", "bow.nif"); os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy2(src, dst)
        else: EBL.ebony_nif(os.path.join(EBL.STAGE, item, rel), dst)
        n += 1
    for item in ("shield", "shield2"):
        dst = os.path.join(EBL.EB_STAGE, item, "replacer", "shield.nif"); os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(EBL.EB_STAGE, item, EBL.EB_MESH, "shield", "shield.nif"), dst); n += 1
    dst = os.path.join(EBL.EB_STAGE, "quiver", "replacer", "flight.nif"); os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(os.path.join(EBL.EB_STAGE, "quiver", EBL.EB_MESH, "quiver", "arrowflight.nif"), dst); n += 1
    print(f"stage: {n} replacer files under {EBL.EB_STAGE}\\<item>\\replacer\\")
    return n


# ------------------------------------------------------------------ the LoY layout check
def loyscan(paths):
    """Every LoY plugin given: its Wolf Ebony weapons' first-person STATs and shield ARMO are where LOY says, and no
    FormID of another layout lands on a record of this plugin (a light plugin masks to 12 bits). Refuses otherwise."""
    import zlib
    def subs(d):
        q = 0; out = []
        while q < len(d):
            s = d[q:q + 4].decode("latin-1"); L = struct.unpack_from("<H", d, q + 4)[0]; out.append((s, d[q + 6:q + 6 + L])); q += 6 + L
        return out
    def walk(b, o, end, out):
        while o < end:
            if b[o:o + 4] == b"GRUP": gs = struct.unpack_from("<I", b, o + 4)[0]; walk(b, o + 24, o + gs, out); o += gs; continue
            ds, fl, fid = struct.unpack_from("<III", b, o + 4); d = b[o + 24:o + 24 + ds]
            if fl & 0x40000: d = zlib.decompress(d[4:])
            out.append((b[o:o + 4].decode(), fid, d)); o += 24 + ds
    for p in paths:
        name = os.path.basename(p); t = LOY[name]; b = open(p, "rb").read(); hs = struct.unpack_from("<I", b, 4)[0]
        light = bool(struct.unpack_from("<I", b, 8)[0] & 0x200); nm = sum(1 for s, _ in subs(b[24:24 + hs]) if s == "MAST")
        recs = []; walk(b, 24 + hs, len(b), recs); own = {}
        for sig, fid, d in recs:
            if fid >> 24 == nm: own[fid & 0xFFFFFF] = (sig, dict(subs(d)))
        def at_id(x):
            k = (x & 0xFFF) if light else x
            if light and k < 0x800: return None
            return own.get(k)
        for item, stats in t["weapons"].items():
            hits = [(x, at_id(x)) for x in stats]; real = [(x, r) for x, r in hits if r]
            assert len(real) == 1 and real[0][1][0] == "STAT", f"{name} {item}: STAT candidates {[(hex(x), r and r[0]) for x, r in hits]}"
            stat = real[0][0] & 0xFFFFFF
            weap = [r for r in own.values() if r[0] == "WEAP" and "WNAM" in r[1] and struct.unpack_from("<I", r[1]["WNAM"])[0] & 0xFFF == stat & 0xFFF
                    and struct.unpack_from("<I", r[1]["WNAM"])[0] >> 24 == nm]
            assert len(weap) == 1 and weap[0][1]["EDID"][:-1].decode() == LOY_WEAP_EDID[item], f"{name} {item}: weapons on STAT {stat:X}: {[w[1]['EDID'] for w in weap]}"
            mdl = real[0][1][1]["MODL"][:-1].decode("latin-1").lower()
            assert mdl == ("NordWar\\Companions\\Weapons\\" + LOY_FILES[item]).lower(), f"{name} {item}: STAT model {mdl}"
        hits = [(x, at_id(x)) for x in t["shield"]]; real = [(x, r) for x, r in hits if r]
        assert len(real) == 1 and real[0][1][0] == "ARMO" and real[0][1][1]["EDID"][:-1].decode() in LOY_SHIELD_EDID, f"{name} shield: {hits}"
        print(f"loyscan OK: {p} ({'light' if light else 'full'}, {len(own)} own records): 5 weapons by STAT and the shield resolve to exactly one record each")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=r"D:\Modlists\Njordlinger\Stock Game\Data")
    ap.add_argument("--dlc", default=r"D:\Modlists\Njordlinger\mods\Base Game DLC Content")
    ap.add_argument("--strings", default=None, help="folder holding skyrim_english.strings / .dlstrings / .ilstrings (from Skyrim - Interface.bsa)")
    ap.add_argument("--stage", action="store_true"); ap.add_argument("--loyscan", nargs="+")
    a = ap.parse_args()
    if a.stage: stage()
    elif a.loyscan: loyscan(a.loyscan)
    else:
        if not a.strings: sys.exit("--strings <folder> needed (extract strings\\skyrim_english.* from Skyrim - Interface.bsa)")
        build_esp(a.data, a.dlc, a.strings)
        o = overrides(); bad = [x for x in o if x[3].count("Carved Ebony ") != 1]
        assert not bad, bad[:5]
        print("base names:", [(x[2], x[3]) for x in o if not x[2].startswith("Ench")])
