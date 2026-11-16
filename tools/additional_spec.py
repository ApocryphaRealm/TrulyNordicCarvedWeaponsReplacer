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
              set         subrecords written as given: "FULL"/"MODL" text, "OBND" 6 shorts or "nif" (measured from the
                          staged model at MODL by nif_bounds.py, the Creation Kit's way), "stats" per quality
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
              "The ebony pieces' numbers, keyword and recipes (Ebony smithing, ebony ingots), in the black-and-gold Ebony look. "
              "Pick this beside Replacer - Ebony (the vanilla Ebony weapons replaced) or Standalone - Ebony quality: the spear and "
              "halberd have no vanilla record, so they always come in through this file's own light plugin."),
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
    # 2026-11-14: design B5 with vanilla's bent arms and a cocking lever on CockingMechanismCtrl; the lever's crossbar
    # reaches game z -3.43, so the bounds' top went from -3 to -4.
    dict(item="crossbow", image="halberd.jpg",
         records=[
             dict(sig="STAT", fid=0x80B, edid="TNCW_Crossbow_1st", template=("Dawnguard.esm", "1stPersonCrossbow"),
                  set={"MODL": r"TrulyNordic\crossbow\crossbow.nif"}),
             dict(sig="WEAP", fid=0x80C, edid="TNCW_Crossbow", template=("Dawnguard.esm", "DLC1CrossBow"),
                  set={"FULL": "Carved Nordic Crossbow", "MODL": r"TrulyNordic\crossbow\crossbow.nif", "OBND": (-27, -28, -4, 27, 29, 7),
                       "stats": {"nordic": (240, 17.0, 20, 10, 1.0, 1.0), "ebony": (900, 19.0, 25, 12, 1.0, 1.0)}}),
             dict(sig="COBJ", fid=0x80D, edid="TNCW_Crossbow_Recipe", template=("standalone", "TNCW_Bow_Recipe"), retarget={"CNAM": "TNCW_Crossbow"}),
             dict(sig="COBJ", fid=0x80E, edid="TNCW_Crossbow_Temper", template=("standalone", "TNCW_Bow_Temper"), retarget={"CNAM": "TNCW_Crossbow"}),
         ]),
    # the quarterstaff Q1 (2026-11-15; the owner 06:45 "start building the other weapon types that we haven't built yet"):
    # a blunt two-handed staff - the Standalone's warhammer records of that quality as templates (TwoHandAxe animation,
    # blunt keyword, warhammer sounds, Nordic or Ebony recipe and temper), our own NIFs. Stats (helper's pick): lighter,
    # cheaper and quicker than the warhammer, a little less damage, the halberd's length so a long reach.
    dict(item="quarterstaff", image="halberd.jpg",
         records=[
             dict(sig="STAT", fid=0x80F, edid="TNCW_Quarterstaff_1st", template=("standalone", "TNCW_Warhammer_1st"),
                  set={"MODL": r"TrulyNordic\quarterstaff\1stpersonquarterstaff.nif"}),
             dict(sig="WEAP", fid=0x810, edid="TNCW_Quarterstaff", template=("standalone", "TNCW_Warhammer"),
                  set={"FULL": "Carved Nordic Quarterstaff", "MODL": r"TrulyNordic\quarterstaff\quarterstaff.nif", "OBND": (-2, -81, -2, 2, 81, 2),
                       "stats": {"nordic": (520, 16.0, 18, 9, 0.85, 1.4), "ebony": (1300, 19.0, 21, 10, 0.85, 1.4)}}),
             dict(sig="COBJ", fid=0x811, edid="TNCW_Quarterstaff_Recipe", template=("standalone", "TNCW_Warhammer_Recipe")),
             dict(sig="COBJ", fid=0x812, edid="TNCW_Quarterstaff_Temper", template=("standalone", "TNCW_Warhammer_Temper")),
         ]),
    # the rapier AG (2026-11-15, the owner: "I also like option A for the rapier" - the swept hilt): a one-handed sword -
    # the Standalone's sword records of that quality as templates (OneHandSword animation, sword keyword and sounds, Nordic or
    # Ebony recipe and temper), our own NIFs (the third-person one carries the scabbard 'Scb'). Stats (helper's pick, against
    # the Standalone sword 290 / 12 / 11 / 6 / 1.0 / 1.0 Nordic, 720 / 15 / 13 / 6 / 1.0 / 1.0 Ebony): a lighter, quicker
    # thrusting blade - weight 3 less, speed 1.15, one point less damage, one more critical, reach 1.1 for its 74-unit
    # blade, value a little over the sword's for the work in the hilt.
    dict(item="rapier", image="halberd.jpg",
         records=[
             dict(sig="STAT", fid=0x813, edid="TNCW_Rapier_1st", template=("standalone", "TNCW_Sword_1st"),
                  set={"MODL": r"TrulyNordic\rapier\1stpersonrapier.nif"}),
             dict(sig="WEAP", fid=0x814, edid="TNCW_Rapier", template=("standalone", "TNCW_Sword"),
                  set={"FULL": "Carved Nordic Rapier", "MODL": r"TrulyNordic\rapier\rapier.nif", "OBND": (-7, -14, -4, 7, 75, 2),
                       "stats": {"nordic": (320, 9.0, 10, 7, 1.15, 1.1), "ebony": (780, 11.0, 12, 7, 1.15, 1.1)}}),
             dict(sig="COBJ", fid=0x815, edid="TNCW_Rapier_Recipe", template=("standalone", "TNCW_Sword_Recipe")),
             dict(sig="COBJ", fid=0x816, edid="TNCW_Rapier_Temper", template=("standalone", "TNCW_Sword_Temper")),
         ],
         # Keyword Compatibility Framework's rapier keyword (kcf.esm 0x805 WeapTypeRapier; Animated Armoury's rapier
         # animations and the packs built on KCF key on it). Named by EditorID, so no master: without kcf.esm KID makes an
         # empty keyword of that name and nothing changes. (KCF's own kcf_KID.ini also tags any weapon named "*Rapier".)
         kid=dict(weap="TNCW_Rapier", ini=PLUGIN[:-4] + " - Rapier_KID.ini",
                  step="Rapier animations", group="Carved Nordic Rapier moveset", folder="42 Rapier - Animation pack keywords",
                  default=("Sword moveset (default)",
                           "The rapier uses the one-handed sword animations, the game's own moveset. Choose this if you have no rapier animation mod."),
                  option=("Rapier animation packs (keyword via KID)",
                          "Gives the rapier the rapier keyword of Keyword Compatibility Framework (WeapTypeRapier), the one Animated Armoury's "
                          "rapier moveset and the packs built on it look for. Requires Keyword Item Distributor (KID); without the animation "
                          "mods the keyword changes nothing."),
                  keywords=[("WeapTypeRapier", "Keyword Compatibility Framework (kcf.esm 0x805) / Animated Armoury rapier")])),
    # THE BLADE FAMILIES (1.4.0, 2026-11-15, the owner 19:39: "use the European style single-handed sword as the base sword
    # design and have the saber be a weapon tagged as a katana ... scale the saber up to a long sword and great sword size and
    # add a European-styled longsword to have 3 blades each, all tagged for katana or sword animations"). The main files' sword
    # is now the straight sword; the greatsword stays. Added here (stats helper's pick, between their neighbours: the
    # Standalone sword 290 / 12 / 11 / 6 / 1.0 / 1.0 and greatsword 585 / 19 / 20 / 10 / 0.7 / 1.3 Nordic, 720 / 15 / 13 / 6 and
    # 1440 / 22 / 22 / 11 Ebony):
    #   the European LONGSWORD (option A, the owner 21:35) - a ONE-HANDED sword record (the Standalone sword's: OneHandSword,
    #     sword keyword, sounds, recipe and temper) with reach 1.1 for its 97-unit length: sword animations, as the owner asked
    #     for the European line; Keyword Compatibility Framework has no longsword keyword (kcf_KID.ini lists none), and a
    #     two-handed record would only be a shorter greatsword. Heavier and slower than the sword, two more damage.
    #   the SABER (saber B, until now the Replacer's sword) - one-handed, the sword's numbers a little lighter and quicker.
    #   the saber LONGSWORD (A5k L) - one-handed like the European longsword, a little lighter and quicker than it.
    #   the saber GREATSWORD (A5k G) - TWO-HANDED, the Standalone greatsword's records (TwoHandSword), a little lighter and
    #     quicker than the greatsword, one point less damage.
    dict(item="longsword", image="halberd.jpg",
         records=[
             dict(sig="STAT", fid=0x817, edid="TNCW_Longsword_1st", template=("standalone", "TNCW_Sword_1st"),
                  set={"MODL": r"TrulyNordic\longsword\1stpersonlongsword.nif"}),
             dict(sig="WEAP", fid=0x818, edid="TNCW_Longsword", template=("standalone", "TNCW_Sword"),
                  set={"FULL": "Carved Nordic Longsword", "MODL": r"TrulyNordic\longsword\longsword.nif", "OBND": "nif",
                       "stats": {"nordic": (410, 15.0, 13, 7, 0.9, 1.1), "ebony": (1020, 18.0, 15, 7, 0.9, 1.1)}}),
             dict(sig="COBJ", fid=0x819, edid="TNCW_Longsword_Recipe", template=("standalone", "TNCW_Sword_Recipe")),
             dict(sig="COBJ", fid=0x81A, edid="TNCW_Longsword_Temper", template=("standalone", "TNCW_Sword_Temper")),
         ]),
    dict(item="saber", image="sword-curved-saber.jpg",
         records=[
             dict(sig="STAT", fid=0x81B, edid="TNCW_Saber_1st", template=("standalone", "TNCW_Sword_1st"),
                  set={"MODL": r"TrulyNordic\saber\1stpersonsaber.nif"}),
             dict(sig="WEAP", fid=0x81C, edid="TNCW_Saber", template=("standalone", "TNCW_Sword"),
                  set={"FULL": "Carved Nordic Saber", "MODL": r"TrulyNordic\saber\saber.nif", "OBND": "nif",
                       "stats": {"nordic": (300, 11.0, 11, 6, 1.05, 1.0), "ebony": (740, 14.0, 13, 6, 1.05, 1.0)}}),
             dict(sig="COBJ", fid=0x81D, edid="TNCW_Saber_Recipe", template=("standalone", "TNCW_Sword_Recipe")),
             dict(sig="COBJ", fid=0x81E, edid="TNCW_Saber_Temper", template=("standalone", "TNCW_Sword_Temper")),
         ],
         # Keyword Compatibility Framework's katana keyword (kcf.esm 0x80A WeapTypeKatana) on the whole saber line - the saber, the
         # saber longsword and the saber greatsword - in ONE step and one ini (kid "weaps"): the katana movesets key on it
         # (e.g. the Elden Rim dual-wield katana moveset's OAR config, IsEquippedHasKeyword WeapTypeKatana), and KCF's own
         # kid list gives it to the vanilla Akaviri katanas and to two-handed nodachi / zanbato alike. Named by EditorID, no
         # master: without kcf.esm KID makes an empty keyword of that name and nothing changes.
         kid=dict(weaps=["TNCW_Saber", "TNCW_SaberLongsword", "TNCW_SaberGreatsword"], ini=PLUGIN[:-4] + " - Saber_KID.ini",
                  step="Saber animations", group="Carved Nordic Saber moveset", folder="43 Saber - Katana animation keywords",
                  default=("Sword movesets (default)",
                           "The saber and the saber longsword use the one-handed sword animations, the saber greatsword the greatsword "
                           "animations - the game's own movesets. Choose this if you have no katana animation mod."),
                  option=("Katana animation packs (keyword via KID)",
                          "Gives the saber, the saber longsword and the saber greatsword the katana keyword of Keyword Compatibility "
                          "Framework (WeapTypeKatana), the one the katana movesets (Animated Armoury's and the packs built on it) look "
                          "for. Requires Keyword Item Distributor (KID); without a katana animation mod the keyword changes nothing."),
                  keywords=[("WeapTypeKatana", "Keyword Compatibility Framework (kcf.esm 0x80A) / katana movesets")])),
    dict(item="saberlongsword", image="sword-curved-saber.jpg",
         records=[
             dict(sig="STAT", fid=0x81F, edid="TNCW_SaberLongsword_1st", template=("standalone", "TNCW_Sword_1st"),
                  set={"MODL": r"TrulyNordic\saberlongsword\1stpersonsaberlongsword.nif"}),
             dict(sig="WEAP", fid=0x820, edid="TNCW_SaberLongsword", template=("standalone", "TNCW_Sword"),
                  set={"FULL": "Carved Nordic Saber Longsword", "MODL": r"TrulyNordic\saberlongsword\saberlongsword.nif", "OBND": "nif",
                       "stats": {"nordic": (400, 14.0, 13, 7, 0.95, 1.1), "ebony": (1000, 17.0, 15, 7, 0.95, 1.1)}}),
             dict(sig="COBJ", fid=0x821, edid="TNCW_SaberLongsword_Recipe", template=("standalone", "TNCW_Sword_Recipe")),
             dict(sig="COBJ", fid=0x822, edid="TNCW_SaberLongsword_Temper", template=("standalone", "TNCW_Sword_Temper")),
         ]),
    dict(item="sabergreatsword", image="sword-curved-saber.jpg",
         records=[
             dict(sig="STAT", fid=0x823, edid="TNCW_SaberGreatsword_1st", template=("standalone", "TNCW_Greatsword_1st"),
                  set={"MODL": r"TrulyNordic\sabergreatsword\1stpersonsabergreatsword.nif"}),
             dict(sig="WEAP", fid=0x824, edid="TNCW_SaberGreatsword", template=("standalone", "TNCW_Greatsword"),
                  set={"FULL": "Carved Nordic Saber Greatsword", "MODL": r"TrulyNordic\sabergreatsword\sabergreatsword.nif", "OBND": "nif",
                       "stats": {"nordic": (570, 18.0, 19, 10, 0.75, 1.3), "ebony": (1400, 21.0, 21, 11, 0.75, 1.3)}}),
             dict(sig="COBJ", fid=0x825, edid="TNCW_SaberGreatsword_Recipe", template=("standalone", "TNCW_Greatsword_Recipe")),
             dict(sig="COBJ", fid=0x826, edid="TNCW_SaberGreatsword_Temper", template=("standalone", "TNCW_Greatsword_Temper")),
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

# Items built but held out of the release (the owner 2026-11-13 09:14: "post whatever we have for the Nordic equipment mod
# without the crossbow and bolts" - the crossbow is being reworked after his in-game test). Every consumer (plugin
# records, package, FOMOD steps) reads ADDITIONAL, so a held item ships nothing; remove it from HOLD to ship it again.
# TN_HOLD="" in the environment ships everything (for building and testing the held items).
# 2026-11-14 (the owner 05:02 "prep the Crossbow for testing next"): the crossbow (design B5, bent arms, cocking lever) and
# the bolt quiver come out of HOLD for the 1.4.0 test build. TN_HOLD="crossbow,boltquiver" holds them again.
# 2026-11-16 (the owner 14:58: "When we upload the carved set, I think we should leave out the middle size of the sword and
# saber"): the European LONGSWORD and the SABER LONGSWORD are switched off HERE, in SHIP_OFF - the one place. They stay
# built (items.py, their scabbards, the stage) and keep their FormIDs (0x817-0x81A, 0x81F-0x822 - never reused, nothing
# renumbered), but no package ships their models, records, recipes or KID line, and the saber step's texts name only the
# sizes that ship (kid_texts below). Ship them again: take them out of SHIP_OFF (or TN_HOLD="" for a test build).
SHIP_OFF = {"longsword", "saberlongsword"}
import os as _os
HOLD = set(SHIP_OFF) if _os.environ.get("TN_HOLD") is None else set(filter(None, _os.environ["TN_HOLD"].split(",")))
ADDITIONAL = [it for it in ADDITIONAL if it["item"] not in HOLD]


def kid_texts():
    """The saber line's KID step: tag only the saber sizes that ship, and say so in the installer's texts."""
    have = {r["edid"] for it in ADDITIONAL for r in it["records"]}
    for it in ADDITIONAL:
        k = it.get("kid")
        if not k or "weaps" not in k or it["item"] != "saber": continue
        k["weaps"] = [e for e in k["weaps"] if e in have]
        if "TNCW_SaberLongsword" in k["weaps"]: continue          # all three ship: the texts above stand
        k["default"] = (k["default"][0], "The saber uses the one-handed sword animations, the saber greatsword the greatsword animations - "
                                         "the game's own movesets. Choose this if you have no katana animation mod.")
        k["option"] = (k["option"][0], "Gives the saber and the saber greatsword the katana keyword of Keyword Compatibility Framework "
                                       "(WeapTypeKatana), the one the katana movesets (Animated Armoury's and the packs built on it) look for. "
                                       "Requires Keyword Item Distributor (KID); without a katana animation mod the keyword changes nothing.")
kid_texts()
