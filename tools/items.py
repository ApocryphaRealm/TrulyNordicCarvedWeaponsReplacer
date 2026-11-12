# The item table of the game build: where each approved model, its maps and its vanilla NIFs are, the triangle budget
# per shape, the vanilla blood shapes, and where the result goes. Every other build script reads it from here.
# Sources: D:\Claude output\4. plans\nordic-carved-redesign-20261110 (the design work; SET-BRIEF.md STATUS lists the
# approved version of each item).
import os, json
PLAN = r"D:\Claude output\4. plans\nordic-carved-redesign-20261110"
S2 = os.path.join(PLAN, "set2")
VAN = os.path.join(PLAN, r"set\work\vanilla\meshes\dlc02\weapons\nordic")
VAN_SHIELD = os.path.join(S2, r"work_sh1\vanilla\meshes\dlc02\armor\nordicshield\nordicshield.nif")
WORK = os.path.join(PLAN, r"package\work")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the shipped asset folders (1.1.0, 2026-11-12: the "ApocryphaTest" level dropped; every build script reads these two)
MESH_REL = r"meshes\TrulyNordic"
TEX_REL = r"textures\pbr\TrulyNordic"
METAL_T, WRAP_T = 11500, 3000

def W(*p): return os.path.join(S2, *p)
# ring pass (2026-11-12 after 1.1.1, the owner 08:35: "make the symbols all have the black filled ring"): repaint only, every
# NIF byte for byte its 1.1.1 source - sheaths dagger v6 / saber C2 / straight v3 / greatsword v3 (the locket's triquetra on
# the dark filled disc + polished ring), greatsword v5-sf (the pommel), bow v9 (both riser plates); set2 ring-pass-*.png
ITEMS = {
    # sword A5i (approved 2026-11-12 00:01: "looks good"): A5h's flat-sided pommel with the crack inside the hook closed;
    # A5f's blade and tip engraving; the wrap is A5d's, unchanged. Layout record in work_sword_a5i\engraving_check.json.
    # option: the curved saber and the straight sword (sword2) are the installer's "Sword" step; both install at sword\sword.nif
    # sheath: the shape named 'Scb' that the game leaves on the hip when the weapon is drawn (in the weapon's own frame)
    # 1.1.1 (2026-11-12): normals-only fix - carved faces' outline and creases given their own vertices
    # (set2\shading_fix_split.py --crease=35, real face dumps); geometry and maps identical
    "sword": dict(version="A5i-sf", sources=[W(r"work_sword_a5i_sf\A5I_metal.nif"), os.path.join(PLAN, r"A5\work\A5_wrap.nif")], orient=True, option=True,
                  sheath=dict(version="saber C2 (falchion fit, ringed symbol)", src=W(r"work_sheath_saber_fitC2\tn_sheath_saber_fitC2.nif"), tex=W(r"work_sheath_saber_fitC2\tex\tn_sheath_saber_fitC2")),
                  shapes={"metal": {"name": "NordicSwordA5", "tex": W(r"work_sword_a5i_sf\tex\nordicsworda5i")},
                          "wrap": {"name": "NordicWrapA5", "tex": None, "dds_from": r"D:\Modlists\Njordlinger\mods\Nordic Carved Redesign A (test)\textures\pbr\ApocryphaTest\NordicCarvedRedesignA5\nordicwrapa5"}},
                  third="nordicsword.nif", first="1stpersonnordicsword.nif", stem="sword", weap="DLC2NordicSword", fp_stat="03C353"),
    # the straight sword (installer option, 2026-11-11): greatsword v3's blade and upper hilt as a one-hander
    # 1.1.0 shading fix (2026-11-12): v1-sf = v1's NIF with the flat guard and pommel faces' outline vertices split from
    # their chamfers (set2\shading_fix_split.py, as bow v8) - geometry and maps identical; set2\shading-fix-1.1.0.png
    "sword2": dict(version="straight v1-sf", sources=[W(r"work_straightsword_sf\tn_straightsword.nif")], orient=True, option=True, path_stem="sword",
                   sheath=dict(version="v3 (ringed symbol)", src=W(r"work_sheath_straightsword_v3\tn_sheath_straightsword_v3.nif"), tex=W(r"work_sheath_straightsword_v3\tex\tn_sheath_straightsword_v3")),
                   shapes={"metal": {"name": "tn_straightsword", "tex": W(r"work_straightsword_sf\tex\tn_straightsword")}, "wrap": {"name": "TNStraightswordWrap", "tex": W(r"work_straightsword_sf\tex\tn_straightsword_wrap")}},
                   third="nordicsword.nif", first="1stpersonnordicsword.nif", stem="swordstraight", weap="DLC2NordicSword", fp_stat="03C353"),
    # v13 (approved 2026-11-11 23:57): v12's head (the owner's traced outline, 21:32; the same NIF, byte for byte) repainted
    # to the engraving layout rule - layout records in work_v13\engraving_check.json pass engraving-layout-gate
    # v14 (1.1.1): one flat carved cheek per side, the polished bevel takes the taper (battleaxe_build_v14.py), the flat
    # faces with their own vertices, the back spike's weave in the head's frame (battleaxe_paint_v14.py); set2\battleaxe-v14-*.png
    "battleaxe": dict(version="v14", sources=[W(r"work_v14\tn_battleaxe.nif")], orient=True,
                      shapes={"metal": {"name": "TNBattleaxe", "tex": W(r"work_v14\tex\tn_battleaxe")}, "wrap": {"name": "TNBattleaxeWrap", "tex": W(r"work_v14\tex\tn_battleaxe_wrap")}},
                      third="nordicbattleaxe.nif", first="1stpersonnordicbattleaxe.nif", stem="battleaxe", weap="DLC2NordicBattleaxe", fp_stat="03C34F"),
    # orient: the ricasso wrap (TNGreatswordWrap2) came out of tn_lib wound inward on most of its faces (1.0.0)
    # v4 (approved 2026-11-12 01:14: "Greatsword looks good"): v3 with the lower-guard medallion on a level boss;
    # v4-sf (1.1.0 shading fix, 2026-11-12): v4's NIF with the flat guard / boss / pommel faces' outline vertices split from
    # their chamfers (set2\shading_fix_split.py, as bow v8) - geometry and maps identical; set2\shading-fix-1.1.0.png
    # 1.1.1: the metal ships UNDECIMATED (target None): the game build's decimation stretched the blade's UVs 7-23x from
    # 15 to 85 % of its height (the ladder braid the owner saw); the work mesh's planar UVs are even (1.0x)
    "greatsword": dict(version="v5-sf", sources=[W(r"work_gs5_sf\tn_greatsword.nif")], orient=True,
                       sheath=dict(version="v3 (ringed symbol)", src=W(r"work_sheath_greatsword_v3\tn_sheath_greatsword_v3.nif"), tex=W(r"work_sheath_greatsword_v3\tex\tn_sheath_greatsword_v3")),
                       shapes={"metal": {"name": "tn_greatsword", "tex": W(r"work_gs5_sf\tex\tn_greatsword"), "target": None}, "wrap": {"name": "TNGreatswordWrap", "tex": W(r"work_gs5_sf\tex\tn_greatsword_wrap")},
                               "wrap2": {"name": "TNGreatswordWrap2", "tex": W(r"work_gs5_sf\tex\tn_greatsword_wrap2"), "target": 1500}},
                       third="nordicgreatsword.nif", first="1stpersonnordicgreatsword.nif", stem="greatsword", weap="DLC2NordicGreatsword", fp_stat="03C351"),
    # -sf (1.1.0 shading fix, round 2, 2026-11-12): the same NIF with its carved faces' outline AND creases (edge chamfers,
    # caps) given their own vertices (set2\shading_fix_split.py --crease=35); geometry and maps identical; set2\shading-fix-1.1.0.png
    "warhammer": dict(version="v2f-sf", sources=[W(r"work_wh2f_sf\tn_warhammer2.nif")], orient=True,   # v2f: v2e with the straight pommel (2026-11-11)
                      shapes={"metal": {"name": "tn_warhammer2", "tex": W(r"work_wh2f_sf\tex\tn_warhammer2")}, "wrap": {"name": "TNWarhammer2Wrap", "tex": W(r"work_wh2f_sf\tex\tn_warhammer2_wrap")}},
                      third="nordicwarhammer.nif", first="1stpersonnordicwarhammer.nif", stem="warhammer", weap="DLC2NordicWarhammer", fp_stat="03C355"),
    # added 2026-11-11 (the owner: "Did you add the Nordic War Axe?"); v3 = v2 with the straight pommel (00:28);
    # v4 (approved 2026-11-12 00:12): v3's mesh (the same NIF) repainted to the engraving layout rule
    # -sf (1.1.0 shading fix, round 2, 2026-11-12): the same NIF with its carved faces' outline AND creases (edge chamfers,
    # caps) given their own vertices (set2\shading_fix_split.py --crease=35); geometry and maps identical; set2\shading-fix-1.1.0.png
    "waraxe": dict(version="v4-sf", sources=[W(r"work_wa4_sf\tn_waraxe2.nif")], orient=True,
                   shapes={"metal": {"name": "tn_waraxe2", "tex": W(r"work_wa4_sf\tex\tn_waraxe2")}, "wrap": {"name": "TNWaraxe2Wrap", "tex": W(r"work_wa4_sf\tex\tn_waraxe2_wrap")}},
                   third="nordicwaraxe.nif", first="1stpersonnordiclwaraxe.nif", stem="waraxe", weap="DLC2NordicWarAxe", fp_stat="03C354"),
    # -sf (1.1.0 shading fix, round 2, 2026-11-12): the same NIF with its carved faces' outline AND creases (edge chamfers,
    # caps) given their own vertices (set2\shading_fix_split.py --crease=35); geometry and maps identical; set2\shading-fix-1.1.0.png
    "dagger": dict(version="v3-sf", sources=[W(r"work_dg3_sf\tn_dagger2.nif")], orient=True,
                   sheath=dict(version="v6 (ringed symbol)", src=W(r"work_sheath_dagger_v6\tn_sheath_dagger_v6.nif"), tex=W(r"work_sheath_dagger_v6\tex\tn_sheath_dagger_v6")),
                   shapes={"metal": {"name": "tn_dagger2", "tex": W(r"work_dg3_sf\tex\tn_dagger2")}, "wrap": {"name": "TNDagger2Wrap", "tex": W(r"work_dg3_sf\tex\tn_dagger2_wrap")}},
                   third="nordicdagger.nif", first="1stpersonnordicdagger.nif", stem="dagger", weap="DLC2NordicDagger", fp_stat="03C350"),
    # pointed maces (approved 2026-11-12 01:20: "mace looks good"): six-flanged v4 the default, classic v3 the option
    # -sf (1.1.0 shading fix, round 2, 2026-11-12): the same NIF with its carved faces' outline AND creases (edge chamfers,
    # caps) given their own vertices (set2\shading_fix_split.py --crease=35); geometry and maps identical; set2\shading-fix-1.1.0.png
    "mace": dict(version="six-flanged v4-sf", sources=[W(r"work_mc4_sf\tn_mace.nif")], orient=True,
                 shapes={"metal": {"name": "tn_mace", "tex": W(r"work_mc4_sf\tex\tn_mace")}, "wrap": {"name": "TNMaceWrap", "tex": W(r"work_mc4_sf\tex\tn_mace_wrap")}},
                 third="nordicmace.nif", first="1stpersonnordicmace.nif", stem="mace", weap="DLC2NordicMace", fp_stat="03C352"),
    # -sf (1.1.0 shading fix, round 2, 2026-11-12): the same NIF with its carved faces' outline AND creases (edge chamfers,
    # caps) given their own vertices (set2\shading_fix_split.py --crease=35); geometry and maps identical; set2\shading-fix-1.1.0.png
    "mace2": dict(version="classic v3-sf", sources=[W(r"work_mc2v3_sf\tn_mace.nif")], orient=True, path_stem="mace",
                  shapes={"metal": {"name": "tn_mace", "tex": W(r"work_mc2v3_sf\tex\tn_mace")}, "wrap": {"name": "TNMaceWrap", "tex": W(r"work_mc2v3_sf\tex\tn_mace_wrap")}},
                  third="nordicmace.nif", first="1stpersonnordicmace.nif", stem="macev2", weap="DLC2NordicMace", fp_stat="03C352", option=True),
    # v8 (2026-11-12): v2's limbs, grip and string; the riser plate redesigned (v3-v8) and its flat carved faces given
    # their own vertices (bow_v8_build.py: the surface gate passes, lean 0.3 deg p95 against v7's 24); skinned as before
    "bow": dict(version="v9", sources=[W(r"work_bow9\tn_bow2.nif")], skinned=True,
                shapes={"metal": {"name": "tn_bow2", "tex": W(r"work_bow9\tex\tn_bow2")}, "wrap": {"name": "TNBowWrap", "tex": W(r"work_bow9\tex\tn_bow2_wrap")},
                        "string": {"name": "TNBowString", "tex": W(r"work_bow9\tex\tn_bow2_string"), "target": None}},
                third="nordicbow.nif", first=None, stem="bow", weap="DLC2NordicBow", fp_stat="03CA7C"),
    # 1.1.1 (2026-11-12): normals-only fix - carved faces' outline and creases given their own vertices
    # (set2\shading_fix_split.py --crease=35, real face dumps); geometry and maps identical
    "shield": dict(version="v4-sf", sources=[W(r"work_sh4_sf\tn_shield4.nif")], orient=True,   # v4: vanilla's placement and profile, faces outward (2026-11-11)
                   shapes={"metal": {"name": "tn_shield4_steel", "tex": W(r"work_sh4_sf\tex\tn_shield4_steel"), "target": 18000}, "board": {"name": "tn_shield4_board", "tex": W(r"work_sh4_sf\tex\tn_shield4_board"), "target": 2000}},
                   third=None, first=None, stem="shield", armo="DLC2ArmorNordicShield"),
    # the clean shield (optional file, 2026-11-11 22:46): v4 with the crest as a plain carved disc - no spikes, points or straps
    "shield2": dict(version="v5 clean-sf", sources=[W(r"work_sh5_clean_sf\tn_shield5.nif")], orient=True, option=True,
                    shapes={"metal": {"name": "tn_shield5_steel", "tex": W(r"work_sh5_clean_sf\tex\tn_shield5_steel"), "target": 18000}, "board": {"name": "tn_shield5_board", "tex": W(r"work_sh5_clean_sf\tex\tn_shield5_board"), "target": 2000}},
                    third=None, first=None, stem="shieldclean", armo="DLC2ArmorNordicShield"),
    # quiver B4 + its arrows (2026-11-12 after 1.1.1; the owner: "Quiver B and the arrowheads from B, but I want the black
    # feathers for the fletching", then 08:35 the ring): B3's mesh byte for byte with the collar plate's triquetra on the
    # dark filled ring (set2\work_final_quiverB4, aqs_paint_ring.py; set2\ring-pass-quiver.png). Built by gb_quiver.py
    # (not gb_blender.py): the five arrow ends cut out of the quiver shapes, every arrow ONE shape on its own arrow atlas
    # (quiver_atlas.py copies the pixels), nothing decimated. third = the AMMO's model (the quiver on the back, the loose
    # and nocked arrow), flight = the PROJ's model. Replacer: the AMMO DLC2NordicArrow by record (SkyPatcher ammo / the
    # ESP); the projectile as a loose file at the vanilla path (SkyPatcher has no projectile model op, and the PROJ record
    # is contested - Shoot Straight overrides it in Njordlinger - so the ESP does not override it either).
    "quiver": dict(version="B4", sources=[W(r"work_final_quiverB4\tn_quiverB4.nif")], builder="gb_quiver",
                   shapes={"metal": {"name": "TNQuiver", "tex": W(r"work_final_quiverB4\tex\tn_quiverB4"), "target": None},
                           "leather": {"name": "TNQuiverLeather", "tex": W(r"work_final_quiverB4\tex\tn_quiverB4_soft"), "target": None},
                           "arrow": {"name": "arrow", "tex": os.path.join(WORK, r"quiver\tex\tn_quiver_arrow"), "target": None,
                                     # the atlas is the quiver design's own arrow pixels (quiver_atlas.py): its faces are
                                     # recorded in that design's engraving_check.json (engraving-layout gate)
                                     "design": W(r"work_final_quiverB4")}},
                   arrows_in_quiver=["arrowq1", "arrowq2", "arrowq3", "arrowq4", "arrowq5"],
                   third="nordicarrow.nif", flight="nordicarrowflight.nif", first=None, stem="quiver",
                   ammo="Dragonborn.esm|2623B", proj="Dragonborn.esm|2623A"),
    # the spear (2026-11-12 after 1.1.1; the owner 06:12: our own spear modelled from scratch, a NEW item - vanilla has no
    # spear, so it is in the Standalone packages only, never the Replacer). Approved design v4 = set2\work_final_spearD;
    # E = D's NIF byte for byte with the spearhead's triquetra on the dark filled ring (08:35; aqs_paint_ring.py,
    # set2\ring-pass-spear.png). Built on vanilla's two-handed AXE NIFs (the default moveset is TwoHandAxe): root, BSX,
    # BSInvMarker, Prn 'WeaponBack', blood shapes and collision come from nordicbattleaxe.nif / 1stpersonnordicbattleaxe.nif;
    # the blood is cut from the blade and wings (blood_region), not vanilla's axe-head box. Shipped UNDECIMATED (target
    # None, 14,088 triangles): no UV seam can stretch (the greatsword blade lesson). The leather binding uses the
    # greatsword's wrap maps, as in the approved renders (aqs_render.py), shipped as the spear's own copy.
    # new_item: its first-person model goes to meshes\TrulyNordic\spear\1stpersonspear.nif (never a vanilla path).
    "spear": dict(version="E", new_item=True, sources=[W(r"work_final_spearE\tn_spearE.nif")], orient=True,
                  shapes={"metal": {"name": "TNSpear", "tex": W(r"work_final_spearE\tex\tn_spearE"), "target": None},
                          "shaft": {"name": "TNSpearShaft_0", "tex": W(r"work_final_spearE\tex\tn_spearE_soft"), "target": None},
                          "wrap": {"name": "TNSpearWrap", "tex": W(r"work_gs5_sf\tex\tn_greatsword_wrap"), "target": None}},
                  blood_region=[[-4.8, 66.0, -2.5], [4.8, 104.5, 2.5]],
                  third="nordicbattleaxe.nif", first="1stpersonnordicbattleaxe.nif", stem="spear"),
}

def vanilla_path(item, which):
    it = ITEMS[item]
    if item.startswith("shield"): return VAN_SHIELD if which == "third" else None
    f = it.get(which); return os.path.join(VAN, f) if f else None

def blender_config():
    probe = json.load(open(os.path.join(WORK, "vanilla_probe.json")))
    cfg = {}
    for k, it in ITEMS.items():
        if it.get("builder") == "gb_quiver":   # gb_quiver.py: sources and out only (no blood, no decimation)
            cfg[k] = {"out": os.path.join(WORK, k), "sources": it["sources"], "shapes": {r: {"name": sh["name"]} for r, sh in it["shapes"].items()}}; continue
        c = {"out": os.path.join(WORK, k), "sources": it["sources"], "shapes": {}, "skinned": it.get("skinned", False), "orient": it.get("orient", False)}
        if it.get("sheath"): c["sheath"] = it["sheath"]["src"]   # welded and oriented on its own, never decimated
        for role, sh in it["shapes"].items():
            t = sh.get("target", METAL_T if role == "metal" else WRAP_T)
            c["shapes"][role] = {"name": sh["name"], "target": t, "atlas_px": 2048 if role in ("metal", "board") else 512}
        vp = vanilla_path(k, "third")
        if vp and k != "bow":
            pr = probe[vp.replace("\\", "/")] if vp.replace("\\", "/") in probe else probe[vp]
            c["blood"] = []
            for name, d in pr.items():
                if "blood" not in name.lower(): continue
                lo = [d["lo"][0] - 1.0, d["lo"][1] - 0.5, d["lo"][2] - 1.5]; hi = [d["hi"][0] + 1.0, d["hi"][1] + 0.5, d["hi"][2] + 1.5]
                if it.get("blood_region"): lo, hi = it["blood_region"]   # a new item on a vanilla base: its own blade, not the base's head box
                c["blood"].append({"vanilla_name": name, "region": [lo, hi], "uvbox": [d["uvlo"], d["uvhi"]]})
        if it.get("skinned"): c["vanilla_skin"] = vp
        cfg[k] = c
    return cfg

if __name__ == "__main__":
    p = os.path.join(WORK, "blender_config.json"); json.dump(blender_config(), open(p, "w"), indent=1); print(p)
