# The item table of the game build: where each approved model, its maps and its vanilla NIFs are, the triangle budget
# per shape, the vanilla blood shapes, and where the result goes. Every other build script reads it from here.
# Sources: D:\Claude output\4. plans\nordic-carved-redesign-20261110 (the design work; SET-BRIEF.md STATUS lists the
# approved version of each item).
import os, json
PLAN = r"D:\Claude output\4. plans\nordic-carved-redesign-20261110"
S2 = os.path.join(PLAN, "set2")
VAN = os.path.join(PLAN, r"set\work\vanilla\meshes\dlc02\weapons\nordic")
VAN_XBOW = os.path.join(S2, r"refs\vanilla_xbow\meshes\dlc01\weapons\crossbow")   # Dawnguard crossbow, bolt quiver, bolt projectile
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
# hip (2026-11-13, the owner 05:15: "The saber clips into the armor, hiding it a little"): the THIRD-person NIF's every shape
# (and the collision hull) turned -4 deg about the weapon's x axis through the grip centre and moved 1.25 out along -z, so
# the sheathed weapon hangs out from the hip (WeaponSword: local -z is away from the thigh, +y down the blade); the
# grip stays in the fist (the pivot is the grip; the grip centre goes from z +0.67 to -0.58, inside vanilla's own 0.67
# off-centre). Scored against XPMSSE + steel / Nord plate / Nordic carved cuirasses (the owner's), slices of the
# weapon fully behind the armour from the side: Nordic carved 9 -> 6 (vanilla steel sheath 6), buried depth sum
# 21.5 -> 6.0 (vanilla 6.8). The first-person NIF is not moved (its sheath never shows; the blade stays straight in view).
    "sword": dict(hip=dict(rot_x_deg=-4.0, pivot=[-0.28, -2.98, 0.67], shift=[0.0, 0.0, -1.25]), version="A5i-sf", sources=[W(r"work_sword_a5i_sf\A5I_metal.nif"), os.path.join(PLAN, r"A5\work\A5_wrap.nif")], orient=True, option=True,
                  sheath=dict(version="saber C2 (falchion fit, ringed symbol)", src=W(r"work_sheath_saber_fitC2\tn_sheath_saber_fitC2.nif"), tex=W(r"work_sheath_saber_fitC2\tex\tn_sheath_saber_fitC2")),
                  shapes={"metal": {"name": "NordicSwordA5", "tex": W(r"work_sword_a5i_sf\tex\nordicsworda5i")},
                          "wrap": {"name": "NordicWrapA5", "tex": None, "dds_from": r"D:\Modlists\Njordlinger\mods\Nordic Carved Redesign A (test)\textures\pbr\ApocryphaTest\NordicCarvedRedesignA5\nordicwrapa5"}},
                  third="nordicsword.nif", first="1stpersonnordicsword.nif", stem="sword", weap="DLC2NordicSword", fp_stat="03C353"),
    # the straight sword (installer option, 2026-11-11): greatsword v3's blade and upper hilt as a one-hander
    # 1.1.0 shading fix (2026-11-12): v1-sf = v1's NIF with the flat guard and pommel faces' outline vertices split from
    # their chamfers (set2\shading_fix_split.py, as bow v8) - geometry and maps identical; set2\shading-fix-1.1.0.png
    # hip: as the saber's (same clip: Nordic carved 9 hidden slices / depth sum 19.0 -> 5 / 3.9), pivot its own grip centre
    "sword2": dict(hip=dict(rot_x_deg=-4.0, pivot=[0.0, -4.02, 0.67], shift=[0.0, 0.0, -1.25]), version="straight v1-sf", sources=[W(r"work_straightsword_sf\tn_straightsword.nif")], orient=True, option=True, path_stem="sword",
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
    # v2g-knurl (2026-11-12, the owner 20:05: "for the war axe and war hammer, I want the gnarling to be the entire face of the
    # hammerhead"): v2f-sf's NIF with ONLY the hammer's striking face (x -15.3; the other end is the pick) replaced, spliced at
    # the byte level (set2\knurl_full_geom.py + knurl_splice.py): 10 x 10 modelled pyramids edge to edge (0.58 x 0.54 pitch,
    # 0.28 high, tips level with the old face plane; the pocket walls 0.005 inside the outline behind a hair-line rim, as a
    # wall on the outline would be coplanar with the square head's sides), own vertices, UVs on the haft's plain steel; every other vertex record,
    # triangle and map pixel is v2f-sf's (work_wh2g_sf\splice_proof.json); set2\axes-knurl-v2.jpg
    "warhammer": dict(version="v2g-knurl", sources=[W(r"work_wh2g_sf\tn_warhammer2.nif")], orient=True,   # v2f: v2e with the straight pommel (2026-11-11)
                      shapes={"metal": {"name": "tn_warhammer2", "tex": W(r"work_wh2g_sf\tex\tn_warhammer2")}, "wrap": {"name": "TNWarhammer2Wrap", "tex": W(r"work_wh2g_sf\tex\tn_warhammer2_wrap")}},
                      third="nordicwarhammer.nif", first="1stpersonnordicwarhammer.nif", stem="warhammer", weap="DLC2NordicWarhammer", fp_stat="03C355"),
    # added 2026-11-11 (the owner: "Did you add the Nordic War Axe?"); v3 = v2 with the straight pommel (00:28);
    # v4 (approved 2026-11-12 00:12): v3's mesh (the same NIF) repainted to the engraving layout rule
    # -sf (1.1.0 shading fix, round 2, 2026-11-12): the same NIF with its carved faces' outline AND creases (edge chamfers,
    # caps) given their own vertices (set2\shading_fix_split.py --crease=35); geometry and maps identical; set2\shading-fix-1.1.0.png
    # v6-knurl (2026-11-12, the owner 20:05: "I want the gnarling to be the entire face of the hammerhead"; supersedes v5's
    # inset knurl): v4-sf's NIF with ONLY the poll's striking face replaced, spliced at the byte level (set2\knurl_full_geom.py
    # + knurl_splice.py): 10 x 6 modelled pyramids edge to edge (0.38 x 0.39 pitch, 0.19 high, tips level with v4's face
    # plane, the four corner ones clipped to the rounded outline), own vertices, UVs on the poll's plain steel; every other
    # vertex record, triangle and map pixel is v4-sf's (work_wa6_sf\splice_proof.json); set2\axes-knurl-v2.jpg
    # v7-knurl (2026-11-13, the owner 2026-11-12 20:48 / 2026-11-13 01:48: "the war axe doesn't have the symbol in the black
    # filled circle"): v6-knurl's NIF byte for byte; the blade's triquetra (both faces share the pixels) repainted onto the
    # set's standard medallion - dark filled disc R + 0.12, polished ring 0.12, the weave's rim and groove - R 3.458 -> 3.35
    # so the ring clears the braid; every map pixel outside the changed medallion zone + 25 px is v6's (set2\waraxe_paint_v7.py,
    # work_wa7_sf\engraving_check.json "_atlas"); set2\medallion-pass-20261113\
    "waraxe": dict(version="v7-knurl", sources=[W(r"work_wa7_sf\tn_waraxe2.nif")], orient=True,
                   shapes={"metal": {"name": "tn_waraxe2", "tex": W(r"work_wa7_sf\tex\tn_waraxe2")}, "wrap": {"name": "TNWaraxe2Wrap", "tex": W(r"work_wa7_sf\tex\tn_waraxe2_wrap")}},
                   third="nordicwaraxe.nif", first="1stpersonnordiclwaraxe.nif", stem="waraxe", weap="DLC2NordicWarAxe", fp_stat="03C354"),
    # -sf (1.1.0 shading fix, round 2, 2026-11-12): the same NIF with its carved faces' outline AND creases (edge chamfers,
    # caps) given their own vertices (set2\shading_fix_split.py --crease=35); geometry and maps identical; set2\shading-fix-1.1.0.png
    # v4B (2026-11-13, the owner 05:15: "instead of the dragon and animal bite art it uses the same art as the other weapons";
    # 06:11: "The new dagger design should be the default option from now on, and the current version should be an additional
    # option"; his pick 06:25: "Option b but shrink the symbol and outline so its within the engraving area and doesnt interrupt
    # the edges"): REPAINT ONLY of v3-sf - the NIF byte for byte; the blade flat's serpent replaced by outline + weave + the
    # triquetra (R 1.10) on the standard dark disc + polished ring with a 0.81 weave margin to the inset (set2\dagger_v4_paint.py
    # B); maps outside the blade island + 25 px = v3-sf's. The serpent v3-sf is the installer option "dagger2".
    # guard fix (2026-11-13, the owner 06:35: "Fix the guard"): both daggers' NIF is work_dg5_guard's - v3-sf with the
    # guard face evenly rounded along its length (set2\dagger_guardfix_build.py: half thickness 1.08 - 0.0223 x^2, was a
    # flat middle with smoothstep ends; ends 0.85 / 0.98, was 0.50) and the shading split re-run; the front outline, the
    # UVs and every other vertex unchanged, so both daggers' maps stay valid
    "dagger": dict(version="v4B (guard fix)", sources=[W(r"work_dg5_guard\tn_dagger2.nif")], orient=True,
                   sheath=dict(version="v6 (ringed symbol)", src=W(r"work_sheath_dagger_v6\tn_sheath_dagger_v6.nif"), tex=W(r"work_sheath_dagger_v6\tex\tn_sheath_dagger_v6")),
                   shapes={"metal": {"name": "tn_dagger2", "tex": W(r"work_dg4B\tex\tn_dagger2")}, "wrap": {"name": "TNDagger2Wrap", "tex": W(r"work_dg4B\tex\tn_dagger2_wrap")}},
                   third="nordicdagger.nif", first="1stpersonnordicdagger.nif", stem="dagger", weap="DLC2NordicDagger", fp_stat="03C350"),
    # the serpent dagger (v3-sf, the default until 2026-11-13) - the installer's alternate: its own texture folder (stem
    # daggerv2), installed at the shared dagger\dagger.nif like mace2; the same sheath
    "dagger2": dict(version="v3-sf (serpent, guard fix)", sources=[W(r"work_dg5_guard\tn_dagger2.nif")], orient=True, path_stem="dagger",
                    sheath=dict(version="v6 (ringed symbol)", src=W(r"work_sheath_dagger_v6\tn_sheath_dagger_v6.nif"), tex=W(r"work_sheath_dagger_v6\tex\tn_sheath_dagger_v6")),
                    shapes={"metal": {"name": "tn_dagger2", "tex": W(r"work_dg3_sf\tex\tn_dagger2")}, "wrap": {"name": "TNDagger2Wrap", "tex": W(r"work_dg3_sf\tex\tn_dagger2_wrap")}},
                    third="nordicdagger.nif", first="1stpersonnordicdagger.nif", stem="daggerv2", weap="DLC2NordicDagger", fp_stat="03C350", option=True),
    # pointed maces (approved 2026-11-12 01:20: "mace looks good"): six-flanged v4 the default, classic v3 the option
    # -sf (1.1.0 shading fix, round 2, 2026-11-12): the same NIF with its carved faces' outline AND creases (edge chamfers,
    # caps) given their own vertices (set2\shading_fix_split.py --crease=35); geometry and maps identical; set2\shading-fix-1.1.0.png
    # v5B (2026-11-13, the owner 05:39: "instead of an alternate version i want the main one replaced with the version that has
    # the no animal art and uses the symbol and braid or weave"; his pick 06:10: "Mace, option b"): REPAINT ONLY of v4-sf - the
    # NIF byte for byte; the flange face's beast's head replaced by outline + weave + the triquetra on the standard dark filled
    # disc + polished ring (set2\mace_v5_paint.py B; sheet set2\mace-v5-design-20261113); maps outside the face + 25 px = v4-sf's
    "mace": dict(version="six-flanged v5B", sources=[W(r"work_mc5B\tn_mace.nif")], orient=True,
                 shapes={"metal": {"name": "tn_mace", "tex": W(r"work_mc5B\tex\tn_mace")}, "wrap": {"name": "TNMaceWrap", "tex": W(r"work_mc5B\tex\tn_mace_wrap")}},
                 third="nordicmace.nif", first="1stpersonnordicmace.nif", stem="mace", weap="DLC2NordicMace", fp_stat="03C352"),
    # -sf (1.1.0 shading fix, round 2, 2026-11-12): the same NIF with its carved faces' outline AND creases (edge chamfers,
    # caps) given their own vertices (set2\shading_fix_split.py --crease=35); geometry and maps identical; set2\shading-fix-1.1.0.png
    "mace2": dict(version="classic v3-sf", sources=[W(r"work_mc2v3_sf\tn_mace.nif")], orient=True, path_stem="mace",
                  shapes={"metal": {"name": "tn_mace", "tex": W(r"work_mc2v3_sf\tex\tn_mace")}, "wrap": {"name": "TNMaceWrap", "tex": W(r"work_mc2v3_sf\tex\tn_mace_wrap")}},
                  third="nordicmace.nif", first="1stpersonnordicmace.nif", stem="macev2", weap="DLC2NordicMace", fp_stat="03C352", option=True),
    # v8 (2026-11-12): v2's limbs, grip and string; the riser plate redesigned (v3-v8) and its flat carved faces given
    # their own vertices (bow_v8_build.py: the surface gate passes, lean 0.3 deg p95 against v7's 24); skinned as before
    # v10A (2026-11-12/13, the owner 19:21: "the teardrop and other parts didn't have the same braiding going down it. But it
    # should", 20:05: "Do the braid on the bow", 00:17: "The braid is good on the bow"): v9's mesh with the riser's
    # string-side wall (the archer's side, collar to sleeve) on its own 55 px/unit island carrying the limb belly's straight
    # braid, its vertices split from the chamfers; every other point and UV, and every texture pixel outside the new
    # island, v9's (set2\bow_v10_build.py mode A, bow_v10_paint.py, work_bow10A\v10_proof.json; set2\bow-inner-face-options.jpg)
    "bow": dict(version="v10A", sources=[W(r"work_bow10A\tn_bow2.nif")], skinned=True,
                shapes={"metal": {"name": "tn_bow2", "tex": W(r"work_bow10A\tex\tn_bow2")}, "wrap": {"name": "TNBowWrap", "tex": W(r"work_bow10A\tex\tn_bow2_wrap")},
                        "string": {"name": "TNBowString", "tex": W(r"work_bow10A\tex\tn_bow2_string"), "target": None}},
                third="nordicbow.nif", first=None, stem="bow", weap="DLC2NordicBow", fp_stat="03CA7C"),
    # 1.1.1 (2026-11-12): normals-only fix - carved faces' outline and creases given their own vertices
    # (set2\shading_fix_split.py --crease=35, real face dumps); geometry and maps identical
    # v4-even (2026-11-12, the owner 19:18: "dark patches and light patches across the whole shield surface"): v4-sf's NIF
    # (byte for byte) with the maps repainted without the low-frequency tone patches - steel: tn_knot.GRIME = 0 (maps_v3's
    # 7x7-cell patina blotches, albedo x2 between dark and bright, held at their mean); board: the leather's 10x10-cell
    # worn patches off, plank tone +-5 % (was 15). Carving height and normal maps byte-identical (set2\shield_v4_even_paint.py,
    # set2\shields_shading\maps_diff_sh4.json); set2\shields-shading-fix.jpg
    "shield": dict(version="v4-even", sources=[W(r"work_sh4_sf2\tn_shield4.nif")], orient=True,   # v4: vanilla's placement and profile, faces outward (2026-11-11)
                   shapes={"metal": {"name": "tn_shield4_steel", "tex": W(r"work_sh4_sf2\tex\tn_shield4_steel"), "target": 18000}, "board": {"name": "tn_shield4_board", "tex": W(r"work_sh4_sf2\tex\tn_shield4_board"), "target": 2000}},
                   third=None, first=None, stem="shield", armo="DLC2ArmorNordicShield"),
    # the clean shield (optional file, 2026-11-11 22:46): v4 with the crest as a plain carved disc - no spikes, points or straps
    # v5 clean-even (2026-11-12): v5 clean-sf's NIF (byte for byte) with the same even repaint as shield v4-even
    # (set2\shield_v5_even_paint.py; the board maps are v4-even's)
    "shield2": dict(version="v5 clean-even", sources=[W(r"work_sh5_clean_sf2\tn_shield5.nif")], orient=True, option=True,
                    shapes={"metal": {"name": "tn_shield5_steel", "tex": W(r"work_sh5_clean_sf2\tex\tn_shield5_steel"), "target": 18000}, "board": {"name": "tn_shield5_board", "tex": W(r"work_sh5_clean_sf2\tex\tn_shield5_board"), "target": 2000}},
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
    # the halberd (2026-11-13; the owner 04:25 "option a for the halberd", 04:26 "match animated armory length"): design A2 =
    # option A (bearded blade: braid perimeter + weave + medallion; straight back spike and narrow leaf top blade, one
    # straight braid each) with the haft below the grip shortened so the whole is 163.0 long, Animated Armoury's halberd
    # length (set2\halberd_build.py A2; work_halberd_NOTES.md). A NEW item on vanilla's two-handed axe NIFs, built as the
    # spear: undecimated, its own first-person file, the grip wrap and the binding on the greatsword's wrap maps as in the
    # approved renders. Blood: the blade, the back spike and the top blade (blood_region).
    "halberd": dict(version="A2", new_item=True, sources=[W(r"work_halberdA2\tn_halberdA2.nif")], orient=True,
                    shapes={"metal": {"name": "TNHalberd", "tex": W(r"work_halberdA2\tex\tn_halberdA2"), "target": None, "design": W(r"work_halberdA2")},
                            "shaft": {"name": "TNHalberdShaft_0", "tex": W(r"work_halberdA2\tex\tn_halberdA2_soft"), "target": None},
                            "wrap": {"name": "TNHalberdWrap", "tex": W(r"work_gs5_sf\tex\tn_greatsword_wrap"), "target": None}},
                    blood_region=[[-18.8, 73.6, -2.0], [13.3, 135.0, 2.0]],
                    third="nordicbattleaxe.nif", first="1stpersonnordicbattleaxe.nif", stem="halberd"),
    # the bolt quiver B and its barbed bolts (2026-11-13; the owner 06:36 "make sure we have a crossbow and bolt models in
    # the upload"; design set2\work_xbow_boltquiverB, gated - work_xbow_NOTES.md). A NEW item for the Additional Weapons file
    # (AMMO "Carved Nordic Bolt"), built by gb_boltquiver.py like the arrow quiver: on vanilla Dawnguard steelbolt.nif's exact
    # structure (ArrowRoot > Arrow > ArrowQuiver; ArrowQuiver:1 the case, Arrow1-Arrow4 the bolts in it that vanish as the
    # count drops, Arrow:0 the loose / nocked bolt) and boltprojectile.nif's (SteelBoltFlight:0, the tracer kept). The
    # design's five bolt ends go to the four slots (two share the slot nearest the fifth). Nothing decimated.
    "boltquiver": dict(version="B", sources=[W(r"work_xbow_boltquiverB\tn_boltquiverB.nif"), W(r"work_xbow_boltquiverB\tn_boltBflight.nif")],
                       builder="gb_boltquiver", atlas_role="bolt",
                       shapes={"metal": {"name": "TNBoltQuiver", "tex": W(r"work_xbow_boltquiverB\tex\tn_boltquiverB"), "target": None, "design": W(r"work_xbow_boltquiverB")},
                               "leather": {"name": "TNBoltQuiverSoft", "tex": W(r"work_xbow_boltquiverB\tex\tn_boltquiverB_soft"), "target": None},
                               "bolt": {"name": "bolt", "tex": os.path.join(WORK, r"boltquiver\tex\tn_boltquiver_bolt"), "target": None, "design": W(r"work_xbow_boltquiverB")}},
                       third="steelbolt.nif", flight="boltprojectile.nif", first=None, stem="boltquiver", van_dir=VAN_XBOW),
    # the crossbow B3 (2026-11-13; the owner 06:38 "Do b for now", 07:16 "if the animated crossbow won't work, just ship it
    # unanimated for now"): set2\work_xbow_crossbowB3 (steel catch, B's boss on its own dark ring). A NEW item for the
    # Additional Weapons file, built by gb_crossbow.py on vanilla Dawnguard crossbow.nif: skinned to vanilla's bones - the
    # prod limbs and string take vanilla's weights (draw / reload as vanilla), the lever, catch and the rest are rigid on
    # CrossbowRoot (the trigger does not move: vanilla moves TriggerCtrl only through its Havok animations). One NIF for
    # third and first person (vanilla's 1stPersonCrossbow STAT names the same file).
    "crossbow": dict(version="B5 (still trigger; vanilla layout, one nut, prod on the front face, after the 08:40 review)", sources=[W(r"work_xbow_crossbowB5\tn_crossbowB5.nif"), W(r"work_xbow_crossbowB5\tn_crossbowB5_cocked.nif")],
                     builder="gb_crossbow",
                     shapes={"metal": {"name": "metal", "tex": W(r"work_xbow_crossbowB5\tex\tn_crossbowB5"), "target": None, "design": W(r"work_xbow_crossbowB5")},
                             "soft": {"name": "soft", "tex": W(r"work_xbow_crossbowB5\tex\tn_crossbowB5_soft"), "target": None},
                             "wrap": {"name": "wrap", "tex": W(r"work_gs5_sf\tex\tn_greatsword_wrap"), "target": None}},
                     third="crossbow.nif", first=None, stem="crossbow", van_dir=VAN_XBOW),
}

def vanilla_path(item, which):
    it = ITEMS[item]
    if item.startswith("shield"): return VAN_SHIELD if which == "third" else None
    f = it.get(which); return os.path.join(VAN, f) if f else None

def blender_config():
    probe = json.load(open(os.path.join(WORK, "vanilla_probe.json")))
    cfg = {}
    for k, it in ITEMS.items():
        if it.get("builder") == "gb_crossbow":   # gb_crossbow.py: the design NIFs, vanilla's skinned crossbow
            cfg[k] = {"out": os.path.join(WORK, k), "sources": it["sources"], "vanilla": os.path.join(it["van_dir"], it["third"])}; continue
        if it.get("builder") in ("gb_quiver", "gb_boltquiver"):   # gb_quiver.py / gb_boltquiver.py: sources and out only (no blood, no decimation)
            cfg[k] = {"out": os.path.join(WORK, k), "sources": it["sources"], "shapes": {r: {"name": sh["name"]} for r, sh in it["shapes"].items()}}
            if it.get("van_dir"): cfg[k]["vanilla"] = {w: os.path.join(it["van_dir"], it[w]) for w in ("third", "flight")}
            continue
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
