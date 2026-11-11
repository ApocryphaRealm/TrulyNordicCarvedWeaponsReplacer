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
MESH_REL = r"meshes\ApocryphaTest\TrulyNordic"
TEX_REL = r"textures\pbr\ApocryphaTest\TrulyNordic"
METAL_T, WRAP_T = 11500, 3000

def W(*p): return os.path.join(S2, *p)
ITEMS = {
    "sword": dict(version="A5d", sources=[os.path.join(PLAN, r"A5\work\A5_metal.nif"), os.path.join(PLAN, r"A5\work\A5_wrap.nif")],
                  shapes={"metal": {"name": "NordicSwordA5", "tex": W(r"work_sword_ns\tex\nordicsworda5c_nsb")},
                          "wrap": {"name": "NordicWrapA5", "tex": None, "dds_from": r"D:\Modlists\Njordlinger\mods\Nordic Carved Redesign A (test)\textures\pbr\ApocryphaTest\NordicCarvedRedesignA5\nordicwrapa5"}},
                  third="nordicsword.nif", first="1stpersonnordicsword.nif", stem="sword", weap="DLC2NordicSword", fp_stat="03C353"),
    "battleaxe": dict(version="v8", sources=[W(r"work_v8\tn_battleaxe.nif")],
                      shapes={"metal": {"name": "TNBattleaxe", "tex": W(r"work_v8\tex\tn_battleaxe")}, "wrap": {"name": "TNBattleaxeWrap", "tex": W(r"work_v8\tex\tn_battleaxe_wrap")}},
                      third="nordicbattleaxe.nif", first="1stpersonnordicbattleaxe.nif", stem="battleaxe", weap="DLC2NordicBattleaxe", fp_stat="03C34F"),
    "greatsword": dict(version="v3", sources=[W(r"work_gs3\tn_greatsword.nif")],
                       shapes={"metal": {"name": "tn_greatsword", "tex": W(r"work_gs3\tex\tn_greatsword")}, "wrap": {"name": "TNGreatswordWrap", "tex": W(r"work_gs3\tex\tn_greatsword_wrap")},
                               "wrap2": {"name": "TNGreatswordWrap2", "tex": W(r"work_gs3\tex\tn_greatsword_wrap2"), "target": 1500}},
                       third="nordicgreatsword.nif", first="1stpersonnordicgreatsword.nif", stem="greatsword", weap="DLC2NordicGreatsword", fp_stat="03C351"),
    "warhammer": dict(version="v2e", sources=[W(r"work_wh2e\tn_warhammer2.nif")],
                      shapes={"metal": {"name": "tn_warhammer2", "tex": W(r"work_wh2e\tex\tn_warhammer2")}, "wrap": {"name": "TNWarhammer2Wrap", "tex": W(r"work_wh2e\tex\tn_warhammer2_wrap")}},
                      third="nordicwarhammer.nif", first="1stpersonnordicwarhammer.nif", stem="warhammer", weap="DLC2NordicWarhammer", fp_stat="03C355"),
    "dagger": dict(version="v3", sources=[W(r"work_dg3\tn_dagger2.nif")],
                   shapes={"metal": {"name": "tn_dagger2", "tex": W(r"work_dg3\tex\tn_dagger2")}, "wrap": {"name": "TNDagger2Wrap", "tex": W(r"work_dg3\tex\tn_dagger2_wrap")}},
                   third="nordicdagger.nif", first="1stpersonnordicdagger.nif", stem="dagger", weap="DLC2NordicDagger", fp_stat="03C350"),
    "mace": dict(version="v3", sources=[W(r"work_mc3\tn_mace.nif")],
                 shapes={"metal": {"name": "tn_mace", "tex": W(r"work_mc3\tex\tn_mace")}, "wrap": {"name": "TNMaceWrap", "tex": W(r"work_mc3\tex\tn_mace_wrap")}},
                 third="nordicmace.nif", first="1stpersonnordicmace.nif", stem="mace", weap="DLC2NordicMace", fp_stat="03C352"),
    "mace2": dict(version="v2", sources=[W(r"work_mc2\tn_mace.nif")],
                  shapes={"metal": {"name": "tn_mace", "tex": W(r"work_mc2\tex\tn_mace")}, "wrap": {"name": "TNMaceWrap", "tex": W(r"work_mc2\tex\tn_mace_wrap")}},
                  third="nordicmace.nif", first="1stpersonnordicmace.nif", stem="macev2", weap="DLC2NordicMace", fp_stat="03C352", option=True),
    "bow": dict(version="v2", sources=[W(r"work_bow2\tn_bow2.nif")], skinned=True,
                shapes={"metal": {"name": "tn_bow2", "tex": W(r"work_bow2\tex\tn_bow2")}, "wrap": {"name": "TNBowWrap", "tex": W(r"work_bow2\tex\tn_bow2_wrap")},
                        "string": {"name": "TNBowString", "tex": W(r"work_bow2\tex\tn_bow2_string"), "target": None}},
                third="nordicbow.nif", first=None, stem="bow", weap="DLC2NordicBow", fp_stat="03CA7C"),
    "shield": dict(version="v3", sources=[W(r"work_sh3\tn_shield3.nif")],
                   shapes={"metal": {"name": "tn_shield3_steel", "tex": W(r"work_sh3\tex\tn_shield3_steel"), "target": 18000}, "board": {"name": "tn_shield3_board", "tex": W(r"work_sh3\tex\tn_shield3_board"), "target": 2000}},
                   third=None, first=None, stem="shield", armo="DLC2ArmorNordicShield"),
}

def vanilla_path(item, which):
    it = ITEMS[item]
    if item == "shield": return VAN_SHIELD if which == "third" else None
    f = it.get(which); return os.path.join(VAN, f) if f else None

def blender_config():
    probe = json.load(open(os.path.join(WORK, "vanilla_probe.json")))
    cfg = {}
    for k, it in ITEMS.items():
        c = {"out": os.path.join(WORK, k), "sources": it["sources"], "shapes": {}, "skinned": it.get("skinned", False)}
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
                c["blood"].append({"vanilla_name": name, "region": [lo, hi], "uvbox": [d["uvlo"], d["uvhi"]]})
        if it.get("skinned"): c["vanilla_skin"] = vp
        cfg[k] = c
    return cfg

if __name__ == "__main__":
    p = os.path.join(WORK, "blender_config.json"); json.dump(blender_config(), open(p, "w"), indent=1); print(p)
