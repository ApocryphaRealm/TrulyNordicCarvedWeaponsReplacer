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
VK = r"D:\Claude output\4. plans\nordic-carved-sword-redesign-20261121"   # 1.5.0: the Viking-age sword + greatsword design
def VKW(*p): return os.path.join(VK, "work", *p)
# ring pass (2026-11-12 after 1.1.1, the owner 08:35: "make the symbols all have the black filled ring"): repaint only, every
# NIF byte for byte its 1.1.1 source - sheaths dagger v6 / saber C2 / straight v3 / greatsword v3 (the locket's triquetra on
# the dark filled disc + polished ring), greatsword v5-sf (the pommel), bow v9 (both riser plates); set2 ring-pass-*.png
ITEMS = {
    # sword A5i (approved 2026-11-12 00:01: "looks good"): A5h's flat-sided pommel with the crack inside the hook closed;
    # A5f's blade and tip engraving; the wrap is A5d's, unchanged. Layout record in work_sword_a5i\engraving_check.json.
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
    # saber B (1.4.0, 2026-11-15; the owner 18:58 "Build the ebony version with saber b for now"): the BLADE is A5j v4b
    # (set2\sword_a5j_build.py key M, `bash set2\run_aa.sh sword_a5j M`: blank first, one constant edge bevel, the narrow
    # braid with pointed ends, the weave cut at the 18:14 line, the triquetra medallion in the weave), built on A5i's exact
    # outline in A5i's own frame; the hilt (guard, ferrule, pommel, wrap) stays A5i-sf's. The A5i metal NIF keeps only its
    # welded pieces reaching no higher than y 20 ("drop_islands_y_over", as the approved renders' render_game_pbr.py did):
    # its old blade leaves. The v4b blade is a shape of its own (TN_sword_blade) on its own 2048 atlas, undecimated; the
    # edge blood is cut from it. Sheath C2 unchanged: no v4b blade vertex above the guard leaves it (A5i's blade the
    # control; 4. plans\nordic-carved-missing-weapons-20261115\work\saber_b_build\sheath_fit_*.json).
    # THE SABER LINE (1.4.0, 2026-11-15, the owner 19:39: "use the European style single-handed sword as the base sword design
    # and have the saber be a weapon tagged as a katana ... scale the saber up to a long sword and great sword size"): saber B
    # is no longer the Replacer's sword - it is a NEW item of the Additional Weapons ("Carved Nordic Saber", WeapTypeKatana
    # through the KID step), built exactly as before (the same sources, maps, sheath C2, hip and blood) on vanilla's Nordic
    # sword NIFs, with its own first-person file and its own paths (stem "saber": meshes\TrulyNordic\saber\).
    "saber": dict(hip=dict(rot_x_deg=-4.0, pivot=[-0.28, -2.98, 0.67], shift=[0.0, 0.0, -1.25]), version="A5i-sf hilt + A5j v4b blade (saber B)",
                  sources=[W(r"work_sword_a5i_sf\A5I_metal.nif"), os.path.join(PLAN, r"A5\work\A5_wrap.nif"), W(r"work_sword_a5jM\tn_sword_a5jM.nif")], orient=True, new_item=True,
                  sheath=dict(version="saber C2 (falchion fit, ringed symbol)", src=W(r"work_sheath_saber_fitC2\tn_sheath_saber_fitC2.nif"), tex=W(r"work_sheath_saber_fitC2\tex\tn_sheath_saber_fitC2")),
                  shapes={"metal": {"name": "NordicSwordA5", "tex": W(r"work_sword_a5i_sf\tex\nordicsworda5i"), "drop_islands_y_over": 20.0},
                          "wrap": {"name": "NordicWrapA5", "tex": None, "dds_from": r"D:\Modlists\Njordlinger\mods\Nordic Carved Redesign A (test)\textures\pbr\ApocryphaTest\NordicCarvedRedesignA5\nordicwrapa5"},
                          "blade": {"name": "TNSaberA5j", "tex": W(r"work_sword_a5jM\tex\tn_sword_a5jM"), "target": None}},
                  blood_from="blade",
                  third="nordicsword.nif", first="1stpersonnordicsword.nif", stem="saber"),
    # the saber LONGSWORD (sword_a5k L) and saber GREATSWORD (sword_a5k G) (the owner 20:13: "The larger sabers look fine"):
    # set2\sword_a5k_build.py L / G (the blade, its own 2048 atlas, undecimated) + set2\sword_a5k_hilt.py L / G (the shipped
    # saber's guard, ferrule and hooked pommel scaled x1.08 / x1.18 on A5i's atlas - the "metal" role, so the normal fix and the
    # Ebony gold / damascus work on it as on the saber's - and the wrap rebuilt at the longer grip on its own maps). NEW items:
    # the longsword one-handed on vanilla's Nordic SWORD NIFs (OneHandSword, Prn WeaponSword; reach 1.1), the greatsword
    # two-handed on vanilla's Nordic GREATSWORD NIFs (TwoHandSword, Prn WeaponBack). Their scabbards: set2\run_sheath_blades.sh
    # saberL / saberG - sheath C2's construction (fit C, ringed triquetra on a weave locket, weave chape) fitted by the probe /
    # design steps to each blade and hilt, fittings scaled with the blade (x1.10 / x1.25). Blood from the blade. hip (longsword
    # only, the greatsword hangs on the back as the greatsword does): the saber's tilt about its own grip centre (the grip is
    # 4.288 longer at the bottom, so the pivot is 2.144 lower).
    "saberlongsword": dict(hip=dict(rot_x_deg=-4.0, pivot=[-0.28, -5.124, 0.67], shift=[0.0, 0.0, -1.25]), version="A5k L (saber B scaled to a longsword)",
                           sources=[W(r"work_sword_a5kL\tn_sword_a5kL.nif"), W(r"work_sword_a5kL_hilt\tn_sword_a5kL_hilt.nif")], orient=True, new_item=True,
                           sheath=dict(version="saberL r2 (sheath C2 construction, fitted with the blade mesh, x1.10)", src=W(r"work_sheath_saberL_sf\tn_sheath_saberL.nif"), tex=W(r"work_sheath_saberL_sf\tex\tn_sheath_saberL")),
                           shapes={"metal": {"name": "hilt", "tex": W(r"work_sword_a5i_sf\tex\nordicsworda5i"), "target": None},
                                   "wrap": {"name": "wrap", "tex": W(r"work_sword_a5kL_hilt\tex\tn_sword_a5kL_wrap"), "target": None, "design": W(r"work_sword_a5kL")},
                                   "blade": {"name": "TNSaberA5k", "tex": W(r"work_sword_a5kL\tex\tn_sword_a5kL"), "target": None}},
                           blood_from="blade", blood_region=[[-9.0, 3.0, -3.0], [9.0, 78.5, 4.0]],
                           third="nordicsword.nif", first="1stpersonnordicsword.nif", stem="saberlongsword"),
    "sabergreatsword": dict(version="A5k G (saber B scaled to a greatsword)",
                            sources=[W(r"work_sword_a5kG\tn_sword_a5kG.nif"), W(r"work_sword_a5kG_hilt\tn_sword_a5kG_hilt.nif")], orient=True, new_item=True,
                            sheath=dict(version="saberG r2 (sheath C2 construction, fitted with the blade mesh, x1.25)", src=W(r"work_sheath_saberG_sf\tn_sheath_saberG.nif"), tex=W(r"work_sheath_saberG_sf\tex\tn_sheath_saberG")),
                            shapes={"metal": {"name": "hilt", "tex": W(r"work_sword_a5i_sf\tex\nordicsworda5i"), "target": None},
                                    "wrap": {"name": "wrap", "tex": W(r"work_sword_a5kG_hilt\tex\tn_sword_a5kG_wrap"), "target": None, "design": W(r"work_sword_a5kG")},
                                    "blade": {"name": "TNSaberA5k", "tex": W(r"work_sword_a5kG\tex\tn_sword_a5kG"), "target": None}},
                            blood_from="blade", blood_region=[[-10.0, 3.0, -3.0], [10.0, 91.5, 4.0]],
                            third="nordicgreatsword.nif", first="1stpersonnordicgreatsword.nif", stem="sabergreatsword"),
    # the European LONGSWORD A (the owner 21:35: "Longsword, we'll go with the first option that has the curved guard with the
    # symbol on the guard and the pommel"): set2\longsword_build.py A (the blade: the family's straight double-edged blade,
    # one bevel per edge, one straight 3-strand braid; its own 2048 atlas, undecimated) + set2\longsword_hilt.py A (the
    # greatsword's lower guard with its medallion x0.72 and its ferrule, collar and disc pommel x0.90 on the GREATSWORD's atlas -
    # the "metal" role; the wrap rebuilt at the hand-and-a-half grip, 14.9 long, its maps copied into work_longswordA_hilt\tex).
    # A NEW one-handed item on vanilla's Nordic SWORD NIFs (OneHandSword, Prn WeaponSword; reach 1.1 for its 97.3 length):
    # Keyword Compatibility Framework has no longsword keyword, and the owner asked for sword animations on the European line.
    # Its scabbard: set2\run_sheath_blades.sh longswordA - the greatsword sheath v3's construction (the same guard family's
    # throat) fitted to this blade and hilt. hip: the straight sword's tilt about its own grip centre (14.45 visible grip).
    "longsword": dict(hip=dict(rot_x_deg=-4.0, pivot=[0.0, -5.9, 0.67], shift=[0.0, 0.0, -1.25]), version="A (greatsword scheme scaled down)",
                      sources=[W(r"work_longswordA\tn_longswordA.nif"), W(r"work_longswordA_hilt\tn_longswordA_hilt.nif")], orient=True, new_item=True,
                      sheath=dict(version="longswordA r2 (greatsword sheath v3 construction, fitted with the blade mesh)", src=W(r"work_sheath_longswordA_sf\tn_sheath_longswordA.nif"), tex=W(r"work_sheath_longswordA_sf\tex\tn_sheath_longswordA")),
                      shapes={"metal": {"name": "LSHiltGS", "tex": W(r"work_gs5_sf\tex\tn_greatsword"), "target": None},
                              "wrap": {"name": "LSWrap", "tex": W(r"work_longswordA_hilt\tex\tn_longsword_wrap"), "target": None, "design": W(r"work_longswordA")},
                              "blade": {"name": "TNLongsword", "tex": W(r"work_longswordA\tex\tn_longswordA"), "target": None}},
                      blood_from="blade", blood_region=[[-4.0, 3.0, -2.0], [4.0, 78.5, 3.5]],
                      third="nordicsword.nif", first="1stpersonnordicsword.nif", stem="longsword"),
    # THE SWORD (1.4.0, 2026-11-15, the restructure): the straight sword - until now the installer's "Straight sword" option
    # (item "sword2") - is the main files' ONE sword (the Sword step is gone; the saber line is in the Additional Weapons).
    # The same NIF, maps, sheath and hip as the option had, so its files (sword\sword.nif, textures\...\swordstraight\) are
    # byte for byte the 1.4.0 option's.
    # the straight sword (2026-11-11): greatsword v3's blade and upper hilt as a one-hander
    # 1.1.0 shading fix (2026-11-12): v1-sf = v1's NIF with the flat guard and pommel faces' outline vertices split from
    # their chamfers (set2\shading_fix_split.py, as bow v8) - geometry and maps identical; set2\shading-fix-1.1.0.png
    # hip: as the saber's (same clip: Nordic carved 9 hidden slices / depth sum 19.0 -> 5 / 3.9), pivot its own grip centre
    # 1.5.0 (2026-11-21, the owner 06:33: "This the new default option for 1.5 and have the current 1.4 longsword and regular
    # sword versions as optional replacers"): the VIKING-AGE sword (4. plans\nordic-carved-sword-redesign-20261121, approved
    # try 11 06:21 + try 12's seamless pommel band) - NordwarUA-shaped blade (81.9 long), fuller with the 1.4.0 three-strand
    # braid + dots, the wide base's two-strand cable, the triquetra guard, oval grip, braided band over five knuckles. Its maps
    # are the approved design's finished maps (make_maps12.py: tex_nordic, tex_ebony - dots, rims, wires, satin knuckles and
    # the Ebony damascus already in them; ebony.py ships tex_ebony as it is: "ebony_maps"). Its own texture folder
    # (swordviking) so the 1.4.0 straight sword (the installer's European option, frozen from the posted 1.4.0 files in
    # build-packages.py) keeps its own. design_offset: the design is centred on z 0; the 1.4.0 sword (and vanilla) hold the
    # grip at z +0.67, so every shape is moved there (assemble.py) and the hand holds it where it held 1.4.0's. Hip: the
    # 1.4.0 turn and shift, pivoted on this grip's centre (y -4.75).
    "sword": dict(hip=dict(rot_x_deg=-4.0, pivot=[0.0, -4.75, 0.0], shift=[0.0, 0.0, -1.25]), design_offset=[0.0, 0.0, 0.67], version="Viking-age try 12", sources=[VKW("t12S", "tn_nordsword12S.nif")], orient=True, path_stem="sword",
                   sheath=dict(version="Viking-age t12S (straight sword sheath v3 construction, refitted)", src=VKW("sheath_t12S_sf", "tn_sheath_t12S.nif"), tex=VKW("sheath_t12S_sf", "tex", "tn_sheath_t12S")),
                   shapes={"metal": {"name": "TNNordsword12", "tex": VKW("t12S", "tex_nordic", "tn_nordsword12S"), "target": None},
                           "wrap": {"name": "TNNordsword12Wrap", "tex": os.path.join(VK, "game", "wrap", "tn_nordsword12S_wrap"), "target": None, "design": VKW("t12S")}},
                   ebony_maps={"metal": VKW("t12S", "tex_ebony", "tn_nordsword12S")},
                   third="nordicsword.nif", first="1stpersonnordicsword.nif", stem="swordviking", weap="DLC2NordicSword", fp_stat="03C353"),
    # v13 (approved 2026-11-11 23:57): v12's head (the owner's traced outline, 21:32; the same NIF, byte for byte) repainted
    # to the engraving layout rule - layout records in work_v13\engraving_check.json pass engraving-layout-gate
    # v14 (1.1.1): one flat carved cheek per side, the polished bevel takes the taper (battleaxe_build_v14.py), the flat
    # faces with their own vertices, the back spike's weave in the head's frame (battleaxe_paint_v14.py); set2\battleaxe-v14-*.png
    # v15 (1.4.0, 2026-11-16, the UV-overlap gate): v14 with its two lower haft rings' UV pieces moved off the head socket's
    # texels (set2\battleaxe_v15_ringfix.py; the Ebony ring pass had painted the socket's lower rows gold); nothing else changed
    "battleaxe": dict(version="v15 (ring fix)", sources=[W(r"work_v15\tn_battleaxe.nif")], orient=True,
                      shapes={"metal": {"name": "TNBattleaxe", "tex": W(r"work_v15\tex\tn_battleaxe")}, "wrap": {"name": "TNBattleaxeWrap", "tex": W(r"work_v15\tex\tn_battleaxe_wrap")}},
                      third="nordicbattleaxe.nif", first="1stpersonnordicbattleaxe.nif", stem="battleaxe", weap="DLC2NordicBattleaxe", fp_stat="03C34F"),
    # orient: the ricasso wrap (TNGreatswordWrap2) came out of tn_lib wound inward on most of its faces (1.0.0)
    # v4 (approved 2026-11-12 01:14: "Greatsword looks good"): v3 with the lower-guard medallion on a level boss;
    # v4-sf (1.1.0 shading fix, 2026-11-12): v4's NIF with the flat guard / boss / pommel faces' outline vertices split from
    # their chamfers (set2\shading_fix_split.py, as bow v8) - geometry and maps identical; set2\shading-fix-1.1.0.png
    # 1.1.1: the metal ships UNDECIMATED (target None): the game build's decimation stretched the blade's UVs 7-23x from
    # 15 to 85 % of its height (the ladder braid the owner saw); the work mesh's planar UVs are even (1.0x)
    # v6-sf (1.4.0, 2026-11-16, the bevel "notch"): v5-sf with the lower-guard boss WALL strip moved off the blade's
    # planar island in the atlas - greatsword_v4_build.py's fixed WALL_UV (8, 900) sat on the left bevel's texels (rows
    # 901-913, cols 9-99), so the wall's dark plain metal was painted across the bevel mid-blade (shipped 1.1.0-1.3.0).
    # set2\greatsword_v6_wallfix.py: wall UVs +(2, 1123) px to free space, the blade under the old spot from v3 (same
    # blade painting, no boss); positions, normals, triangles and every other UV identical (work_gs6_sf\wallfix.json).
    # 1.5.0 (2026-11-21): the VIKING-AGE greatsword (116.9 long; as the sword above, plus the carved black-and-gold rope
    # ring at the oval grip's exact middle). The 1.4.0 European greatsword (v6-sf) is the installer's European option, frozen
    # from the posted 1.4.0 files. Its own texture folder (greatswordviking), the mesh paths unchanged (path_stem). The
    # 1.4.0 greatsword (and vanilla) hold the grip at x -0.30, z +0.60: design_offset moves the design (centred on 0) there.
    "greatsword": dict(design_offset=[-0.30, 0.0, 0.60], version="Viking-age try 12", sources=[VKW("t12G", "tn_nordsword12G.nif")], orient=True, path_stem="greatsword",
                       sheath=dict(version="Viking-age t12G (greatsword sheath v3 construction, refitted)", src=VKW("sheath_t12G_sf", "tn_sheath_t12G.nif"), tex=VKW("sheath_t12G_sf", "tex", "tn_sheath_t12G")),
                       shapes={"metal": {"name": "TNNordsword12", "tex": VKW("t12G", "tex_nordic", "tn_nordsword12G"), "target": None},
                               "wrap": {"name": "TNNordsword12Wrap", "tex": os.path.join(VK, "game", "wrap", "tn_nordsword12G_wrap"), "target": None, "design": VKW("t12G")}},
                       ebony_maps={"metal": VKW("t12G", "tex_ebony", "tn_nordsword12G")},
                       third="nordicgreatsword.nif", first="1stpersonnordicgreatsword.nif", stem="greatswordviking", weap="DLC2NordicGreatsword", fp_stat="03C351"),
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
    # A3 (2026-11-15, the owner's mark on the A2 head-front render): the blade's lower edge is one smooth concave crescent
    # from the beard's point to the socket instead of A2's straight diagonal; the engraving re-laid on the new face and the
    # medallion re-centred in it; everything else as A2 (set2\halberd-A3-crescent, halberd_build.py A3).
    "halberd": dict(version="A3", new_item=True, sources=[W(r"work_halberdA3\tn_halberdA3.nif")], orient=True,
                    shapes={"metal": {"name": "TNHalberd", "tex": W(r"work_halberdA3\tex\tn_halberdA3"), "target": None, "design": W(r"work_halberdA3")},
                            "shaft": {"name": "TNHalberdShaft_0", "tex": W(r"work_halberdA3\tex\tn_halberdA3_soft"), "target": None},
                            "wrap": {"name": "TNHalberdWrap", "tex": W(r"work_gs5_sf\tex\tn_greatsword_wrap"), "target": None}},
                    blood_region=[[-18.8, 73.6, -2.0], [13.3, 135.0, 2.0]],
                    third="nordicbattleaxe.nif", first="1stpersonnordicbattleaxe.nif", stem="halberd"),
    # the quarterstaff Q1 (2026-11-15, the owner 06:45 "start building the other weapon types that we haven't built yet. Just
    # do them one at a time" - the Animated Armoury list's quarterstaff): set2\quarterstaff_build.py Q1 - a 160-long dark-ash
    # staff, the set's grip wrap, a forged square steel shoe at each end (four raised plates, one straight braid each, square
    # bands, a square neck over a ring and a leather binding, a blunt four-sided cap). A NEW item built as the halberd: on
    # vanilla's two-handed axe NIFs (TwoHandAxe moveset), undecimated, its own first-person file; blood on the top shoe.
    "quarterstaff": dict(version="Q1", new_item=True, sources=[W(r"work_quarterstaffQ1\tn_quarterstaffQ1.nif")], orient=True,
                    shapes={"metal": {"name": "TNQuarterstaff", "tex": W(r"work_quarterstaffQ1\tex\tn_quarterstaffQ1"), "target": None, "design": W(r"work_quarterstaffQ1")},
                            "shaft": {"name": "TNQuarterstaffShaft_0", "tex": W(r"work_quarterstaffQ1\tex\tn_quarterstaffQ1_soft"), "target": None},
                            "wrap": {"name": "TNQuarterstaffWrap", "tex": W(r"work_gs5_sf\tex\tn_greatsword_wrap"), "target": None}},
                    blood_region=[[-2.2, 60.0, -2.2], [2.2, 80.5, 2.2]],
                    third="nordicbattleaxe.nif", first="1stpersonnordicbattleaxe.nif", stem="quarterstaff"),
    # the rapier AG (2026-11-15, the owner: "I also like option A for the rapier" - the swept hilt): set2\rapier_build.py AG
    # (run set2\run_aa.sh rapier AG) = option A exactly, with the side ring and the two swept bars on -z: on the hip the
    # WeaponSword node's +z points into the thigh, so on +z the ring would sit in the armour. A long narrow diamond-section
    # blade from a carved ricasso (one two-strand braid), quillons with turned tips and knobs, two arms to the ricasso, the
    # knuckle bow into a wheel pommel (outline + weave). A NEW one-handed item on vanilla's Nordic SWORD NIFs (OneHandSword
    # moveset; Prn WeaponSword), undecimated, its own first-person file; the grip wrap on the greatsword's wrap maps as in the
    # approved renders. Its scabbard r1 (set2\run_sheath_rapier.sh): the straight sword sheath v3's construction fitted to
    # this blade - black leather over wood, a forged locket over the ricasso's top and a chape, both framed weave panels (a
    # 2.2-wide locket face has no room for a bold symbol) - as 'Scb'. hip: the saber's tilt; the shift only 0.58 out (this
    # model's grip is on z 0, the set's swords' on +0.67), so the grip centre lands on -0.58 like theirs.
    "rapier": dict(version="AG", new_item=True, hip=dict(rot_x_deg=-4.0, pivot=[0.0, -4.68, 0.0], shift=[0.0, 0.0, -0.58]),
                   sources=[W(r"work_rapierAG\tn_rapierAG.nif")], orient=True,
                   sheath=dict(version="r1 (straight sheath v3 construction, weave locket and chape)", src=W(r"work_sheath_rapier_sf\tn_sheath_rapier.nif"), tex=W(r"work_sheath_rapier_sf\tex\tn_sheath_rapier")),
                   shapes={"metal": {"name": "TNRapier", "tex": W(r"work_rapierAG\tex\tn_rapierAG"), "target": None, "design": W(r"work_rapierAG")},
                           "wrap": {"name": "TNRapierWrap", "tex": W(r"work_gs5_sf\tex\tn_greatsword_wrap"), "target": None}},
                   blood_region=[[-1.0, 8.5, -0.45], [1.0, 74.1, 0.45]],
                   third="nordicsword.nif", first="1stpersonnordicsword.nif", stem="rapier"),
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

# THE POLISHED BLADE (1.4.0, 2026-11-16; the owner 19:47: "I'd rather go with the 1 through 4 without the mirror" - the
# mirror-finish study's items 1-4 on every Carved weapon's blade / edged steel; tools\blade_polish.py has the method).
# Per item: the shape the blade is in ("from": metal, or the saber line's own "blade" shape) and the blade's blocks in
# the painter's 2048 atlas (pixels, rows down: x0, y0, x1, y1) - the blade column of the swords, dagger and rapier, the
# heads of the axes, halberd and spear (bit, cheeks, spikes and their walls; never the socket, the poll or the haft).
# Each blade becomes the shape "<shape>_blade" (role "blade", texture set tn_<stem>_blade) on its own atlas, welded
# (weld_normals), never decimated; the edge blood is cut from it. The hilt keeps its shape's atlas and maps unchanged.
# Not polished: the warhammer and maces (no edge), the quarterstaff, and the longsword / saber longsword (not shipped).
POLISH = {
    # 1.5.0 the Viking-age pair: the blade's 16 UV islands in the design atlas (4. plans\nordic-carved-sword-redesign-20261121\
    # game\blade_rects.py: every blade island, no other triangle's centroid inside), repainted on the blade's own atlas at
    # 1.4.0's density (Main Agent's order 3: the braid as 3D and lustrous as 1.4.0's) from "maps" = game\polish_src.py's
    # source (the approved carving's height and normals with the dots, the painter's roughness); "design": the painter's folder
    "sword": dict(maps=os.path.join(VK, "game", "polish_src", "tn_nordsword12S"), design=VKW("t12S"), rects=[(10, 10, 97, 1992), (108, 58, 131, 1476), (109, 11, 144, 45), (109, 1488, 144, 1523), (142, 58, 165, 1476),
                                            (176, 10, 199, 1428), (176, 1441, 414, 2015), (210, 10, 233, 1428), (244, 10, 248, 1430), (259, 10, 262, 1430),
                                            (273, 10, 356, 68), (273, 79, 356, 138), (273, 149, 319, 1257), (330, 149, 376, 1257), (387, 10, 433, 1118), (444, 10, 490, 1118)]),
    "greatsword": dict(maps=os.path.join(VK, "game", "polish_src", "tn_nordsword12G"), design=VKW("t12G"), rects=[(10, 10, 83, 1998), (94, 58, 120, 1980), (95, 11, 130, 45), (95, 1992, 130, 2027), (131, 58, 156, 1980),
                                                 (167, 10, 193, 1932), (167, 1945, 266, 2007), (204, 10, 230, 1932), (241, 10, 244, 1934), (255, 10, 259, 1934),
                                                 (270, 10, 561, 718), (277, 1943, 375, 2005), (572, 10, 628, 1558), (639, 10, 695, 1558), (706, 10, 762, 1558), (773, 10, 829, 1558)]),
    "saber": {"from": "blade", "rects": [(0, 0, 420, 2048)]},
    "sabergreatsword": {"from": "blade", "rects": [(0, 0, 420, 2048)]},
    "dagger": dict(rects=[(0, 0, 490, 1828)]),
    "dagger2": dict(rects=[(0, 0, 490, 1828)]),
    "rapier": dict(rects=[(150, 0, 275, 1592)]),
    "spear": dict(rects=[(730, 0, 1020, 1420)]),
    "halberd": dict(px=52.0, rects=[(0, 0, 844, 1498), (844, 0, 1026, 1300), (0, 1545, 650, 1765)]),
    "battleaxe": dict(rects=[(0, 320, 470, 1245), (590, 340, 900, 655), (1000, 210, 1032, 480), (1000, 885, 1032, 1190)]),
    "waraxe": dict(rects=[(5, 5, 465, 810), (475, 0, 512, 260)]),
}
for _k, _pc in POLISH.items():
    _it = ITEMS[_k]; _src = _pc.get("from", "metal"); _sh = _it["shapes"][_src]
    _it["polish"] = {"from": _src, "rects": [list(r) for r in _pc["rects"]], "maps": _pc.get("maps", _sh["tex"]), "px": _pc.get("px", 63.0)}
    _tex = os.path.join(WORK, _k, "blade", f"tn_{_it['stem']}_blade")
    if _src == "blade":
        _sh.update(tex=_tex, target=None, split=True, weld_normals=True, design=os.path.dirname(os.path.dirname(_it["polish"]["maps"])))
    else:
        _it["shapes"]["blade"] = {"name": _sh["name"] + "_blade", "tex": _tex, "target": None, "split": True, "weld_normals": True,
                                  "design": _pc.get("design") or os.path.dirname(os.path.dirname(_it["polish"]["maps"]))}   # its faces: the painter's engraving_check.json
    _it["blood_from"] = "blade"

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
            c["shapes"][role] = {"name": sh["name"], "target": t, "atlas_px": 2048 if role in ("metal", "board", "blade") else 512}
            if sh.get("drop_islands_y_over") is not None: c["shapes"][role]["drop_islands_y_over"] = sh["drop_islands_y_over"]
            if sh.get("split"):   # the polished blade (1.4.0): its triangles and UV blocks (tools\blade_polish.py)
                import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import blade_polish   # python -I drops the script's folder
                L = blade_polish.layout(k)
                c["shapes"][role].update(split={"from": it["polish"]["from"], "layout": L}, weld_normals=True, atlas_px=L["H"])
        if it.get("blood_from"): c["blood_from"] = it["blood_from"]   # the shape the edge blood is cut from (default metal)
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
