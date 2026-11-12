#!/usr/bin/env python3
r"""The optional download of NEW weapons (2026-11-12) - one table, read by additional_records.py (the plugin) and
build-packages.py (the package and its FOMOD).

The owner (relayed by Main Agent): "im thinking we have the non vanilla weapons in a seperate optional file, for now its
just the one but later there will be more in the pack, the next item to add is a crossbow and its quiver and bolts".

The optional file works beside ANY main file (Replacer No-ESP / ESP, Standalone Nordic / Ebony): its own light plugin
(ESL-flagged ESP) that masters only the Bethesda files it needs - never one of our other plugins - and its own models and
textures at meshes\TrulyNordic\<item>\, textures\pbr\TrulyNordic\<item>\ (no path any main file ships).

TO ADD AN ITEM (the crossbow, its quiver, the bolts): one more entry in ADDITIONAL, with
  item      the key in items.py ITEMS (staged by items.py / gb_blender.py / textures.py / assemble.py like any item)
  records   the records it gets, each copied from a TEMPLATE record and then changed only in the fields named:
              sig, fid    record type and its FormID in our plugin - FIXED here, never reused or renumbered (saves and the
                          KID line point at it); light plugin, so 0x800-0xFFF. Same FormID in both quality variants.
              edid        the new EditorID
              template    (source, EditorID): "standalone" = that quality's Standalone plugin (plugin\standalone-<q>\);
                          more sources (a Bethesda master by FormID) are added in additional_records.TEMPLATE_SOURCES
              set         subrecords written as given: "FULL"/"MODL" text, "OBND" 6 shorts, "stats" per quality
                          (value, weight, damage, critical damage, speed, reach) for a WEAP
            Any reference inside a template to another template of the SAME item (WEAP -> its first-person STAT,
            recipe -> the weapon) is pointed at the matching new record automatically; any other reference to the
            template's own plugin refuses.
  kid       optional: the KID step of the FOMOD for this item (a default option that installs nothing, and an option that
            ships the keyword ini). Each item with a kid entry gets its own step and its own ini file name.
  image     the FOMOD picture (fomod\images\)
"""
NAME = "Additional Weapons"          # working name - the owner's final name of the optional file goes HERE, nowhere else
PLUGIN = f"TrulyNordicCarvedWeapons - {NAME}.esp"
QUALITIES = {  # quality: (plugin folder in the repo, FOMOD option, option folder, description)
    "nordic": ("additional-nordic", "Nordic quality (default)", "10 Quality - Nordic",
               "Forged and tempered like the Nordic pieces (Nordic smithing), with Nordic-tier stats."),
    "ebony": ("additional-ebony", "Ebony quality", "11 Quality - Ebony",
              "The ebony pieces' numbers, keyword and recipes (Ebony smithing, ebony ingots)."),
}
MASTER_ORDER = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]

ADDITIONAL = [
    # the spear (2026-11-12): moved here from the Standalone plugins (were 0x827-0x82A there). Stats as built: value and
    # weight the mean of the quality's battleaxe and greatsword, damage and critical the greatsword's, reach 1.4.
    dict(item="spear", image="spear.jpg",
         records=[
             dict(sig="STAT", fid=0x800, edid="TNCW_Spear_1st", template=("standalone", "TNCW_Battleaxe_1st"),
                  set={"MODL": r"TrulyNordic\spear\1stpersonspear.nif"}),
             dict(sig="WEAP", fid=0x801, edid="TNCW_Spear", template=("standalone", "TNCW_Battleaxe"),
                  set={"FULL": "Carved Nordic Spear", "MODL": r"TrulyNordic\spear\spear.nif", "OBND": (-4, -76, -1, 4, 104, 1),
                       "stats": {"nordic": (620, 21.0, 20, 10, 0.7, 1.4), "ebony": (1510, 24.0, 22, 11, 0.7, 1.4)}}),
             dict(sig="COBJ", fid=0x802, edid="TNCW_Spear_Recipe", template=("standalone", "TNCW_Battleaxe_Recipe")),
             dict(sig="COBJ", fid=0x803, edid="TNCW_Spear_Temper", template=("standalone", "TNCW_Battleaxe_Temper")),
         ],
         # the owner 08:02: "have a separate installer option in the FOMod for if they're using one of those other spear
         # mods. It'll have the keyword that they need, and otherwise it's registered as a battle axe".
         # WeapTypePike dropped 2026-11-12 (owner's decision via Main Agent).
         kid=dict(weap="TNCW_Spear", ini=PLUGIN[:-4] + "_KID.ini",
                  step="Spear animations", group="Carved Nordic Spear moveset", folder="40 Spear - Animation pack keywords",
                  default=("Battleaxe moveset (default)",
                           "The spear uses the battleaxe animations, the game's own two-handed axe moveset. Choose this if you have no spear animation mod."),
                  option=("Spear animation packs (keywords via KID)",
                          "For spear animation mods (Animated Armoury, Spear of Skyrim and the MCO spear packs built on it, Spear movement animation): "
                          "gives the spear the keywords those mods look for (WeapTypeHalberd, 000WeapTypeSoS, WeapTypeSpear). "
                          "Requires Keyword Item Distributor (KID) - install it first; without it this option does nothing."),
                  keywords=[("WeapTypeHalberd", "Animated Armoury (NewArmoury.esp) halberd"),
                            ("000WeapTypeSoS", "Spear of Skyrim"),
                            ("WeapTypeSpear", "Spear movement animation / Animated Armoury spear")])),
]

def check():
    seen = {}
    for it in ADDITIONAL:
        for r in it["records"]:
            assert 0x800 <= r["fid"] <= 0xFFF, f"{r['edid']}: {r['fid']:#x} outside the light plugin range"
            assert r["fid"] not in seen, f"{r['edid']}: FormID {r['fid']:#x} already used by {seen[r['fid']]}"
            seen[r["fid"]] = r["edid"]
    inis = [it["kid"]["ini"] for it in ADDITIONAL if it.get("kid")]
    assert len(inis) == len(set(inis)), "two items ship the same KID ini name"
    assert all("_KID" in i for i in inis)
check()
