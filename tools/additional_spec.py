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
    # the halberd (2026-11-13; the owner 04:25 "option a for the halberd", 04:26 "match animated armory length" - design A2,
    # 163 long). A two-handed axe like the battleaxe it is built on. Stats (helper's pick, beside the battleaxe and the
    # spear): heavier and dearer than the battleaxe, the battleaxe's damage and critical, a little slower (0.65), the
    # longest reach of the set (1.5) for its length.
    dict(item="halberd", image="halberd.jpg",
         records=[
             dict(sig="STAT", fid=0x804, edid="TNCW_Halberd_1st", template=("standalone", "TNCW_Battleaxe_1st"),
                  set={"MODL": r"TrulyNordic\halberd\1stpersonhalberd.nif"}),
             dict(sig="WEAP", fid=0x805, edid="TNCW_Halberd", template=("standalone", "TNCW_Battleaxe"),
                  set={"FULL": "Carved Nordic Halberd", "MODL": r"TrulyNordic\halberd\halberd.nif", "OBND": (-19, -29, -2, 13, 135, 2),
                       "stats": {"nordic": (680, 24.0, 21, 11, 0.65, 1.5), "ebony": (1650, 27.0, 23, 11, 0.65, 1.5)}}),
             dict(sig="COBJ", fid=0x806, edid="TNCW_Halberd_Recipe", template=("standalone", "TNCW_Battleaxe_Recipe")),
             dict(sig="COBJ", fid=0x807, edid="TNCW_Halberd_Temper", template=("standalone", "TNCW_Battleaxe_Temper")),
         ],
         # Animated Armoury's halberd keyword (NewArmoury.esp 0xE4580): its halberd moveset, and Simple Dodge's
         # "Halberd (Animated Armoury)" OAR set, which keys on the same keyword (IsEquippedHasKeyword NewArmoury.esp E4580)
         kid=dict(weap="TNCW_Halberd", ini=PLUGIN[:-4] + " - Halberd_KID.ini",
                  step="Halberd animations", group="Carved Nordic Halberd moveset", folder="41 Halberd - Animation pack keywords",
                  default=("Battleaxe moveset (default)",
                           "The halberd uses the battleaxe animations, the game's own two-handed axe moveset. Choose this if you do not use Animated Armoury."),
                  option=("Animated Armoury halberd moveset (keyword via KID)",
                          "Gives the halberd Animated Armoury's halberd keyword (WeapTypeHalberd), so Animated Armoury's halberd moveset plays - "
                          "and Simple Dodge's halberd dodge set, which looks for the same keyword. Requires Animated Armoury (NewArmoury.esp) "
                          "and Keyword Item Distributor (KID); without them this option does nothing."),
                  keywords=[("WeapTypeHalberd", "Animated Armoury (NewArmoury.esp) halberd")])),
    # the bolts (2026-11-13; the owner 06:36 "make sure we have a crossbow and bolt models in the upload"): bolt quiver B
    # and its barbed bolts (items.py "boltquiver"). The AMMO and its PROJ are copies of Dawnguard's steel bolt
    # (DLC1BoltSteel / DLC1BoltSteelProjectile: the bolt flag - the "non-bolt" bit clear - its speed, gravity, sounds and
    # impact data), so the plugin masters Dawnguard.esm. Damage between the steel bolt (10) and the dwarven bolt (14) at
    # Nordic quality, higher at Ebony; the weight of both (0.1). The recipe is the Standalone's Carved Nordic Arrow recipe
    # of that quality (its materials, perk and forge) making 10 bolts, as Dawnguard's bolt recipes do.
    dict(item="boltquiver", image="halberd.jpg",
         records=[
             dict(sig="PROJ", fid=0x808, edid="TNCW_BoltProjectile", template=("Dawnguard.esm", "DLC1BoltSteelProjectile"),
                  set={"FULL": "Carved Nordic Bolt", "MODL": r"TrulyNordic\boltquiver\boltflight.nif"}),
             dict(sig="AMMO", fid=0x809, edid="TNCW_Bolt", template=("Dawnguard.esm", "DLC1BoltSteel"),
                  set={"FULL": "Carved Nordic Bolt", "MODL": r"TrulyNordic\boltquiver\boltquiver.nif",
                       "ammo": {"nordic": (12.0, 2, 0.1), "ebony": (16.0, 6, 0.1)}}),
             dict(sig="COBJ", fid=0x80A, edid="TNCW_Bolt_Recipe", template=("standalone", "TNCW_NordicArrow_Recipe"),
                  retarget={"CNAM": "TNCW_Bolt"}, set={"NAM1": 10}),
         ]),
    # the crossbow B3 (2026-11-13; the owner 06:38 "Do b for now", 07:16 "just ship it unanimated for now" - the trigger
    # stays still, the limbs and string draw as vanilla's): a copy of Dawnguard's DLC1CrossBow (animation type crossbow,
    # its sounds, impact set, keywords) and its first-person STAT 1stPersonCrossbow, both pointed at our one NIF (vanilla's
    # STAT names the same file as the WEAP). Stats between the crossbow (value 120, weight 14, damage 19, crit 9) and the
    # dwarven crossbow (350, 20, 22, 11) at Nordic quality, above both at Ebony. Recipes: the Standalone's bow recipe and
    # temper of that quality (its materials, perk and benches), pointed at the crossbow.
    dict(item="crossbow", image="halberd.jpg",
         records=[
             dict(sig="STAT", fid=0x80B, edid="TNCW_Crossbow_1st", template=("Dawnguard.esm", "1stPersonCrossbow"),
                  set={"MODL": r"TrulyNordic\crossbow\crossbow.nif"}),
             dict(sig="WEAP", fid=0x80C, edid="TNCW_Crossbow", template=("Dawnguard.esm", "DLC1CrossBow"),
                  set={"FULL": "Carved Nordic Crossbow", "MODL": r"TrulyNordic\crossbow\crossbow.nif", "OBND": (-27, -28, -3, 27, 29, 7),
                       "stats": {"nordic": (240, 17.0, 20, 10, 1.0, 1.0), "ebony": (900, 19.0, 25, 12, 1.0, 1.0)}}),
             dict(sig="COBJ", fid=0x80D, edid="TNCW_Crossbow_Recipe", template=("standalone", "TNCW_Bow_Recipe"), retarget={"CNAM": "TNCW_Crossbow"}),
             dict(sig="COBJ", fid=0x80E, edid="TNCW_Crossbow_Temper", template=("standalone", "TNCW_Bow_Temper"), retarget={"CNAM": "TNCW_Crossbow"}),
         ]),
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
