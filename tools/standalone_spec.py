# The Standalone plugins' record plan (Truly Nordic Carved Weapons Replacer 1.1.0, the owner 2026-11-11 22:43): new
# weapons and a new shield that leave the vanilla Dragonborn Nordic carved items alone, each crafted at the forge where
# the matching vanilla Nordic piece is (same perk, materials, bench) and tempered like it; an Ebony-quality build of the
# same records with the matching Ebony item's damage / armour, value, weight, material keyword and recipes.
# Writes three JSON files the houseCARL calls take (create spec, copy assignments per record type, Ebony overrides).
# Every vanilla FormID below was read from Skyrim.esm / Dragonborn.esm with housecarl_records (2026-11-11), not typed
# from memory; the read-back after the build prints each one's EditorID.
# Run: python -I standalone_spec.py <out dir>
import json, os, sys
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
M = "TrulyNordic"          # model paths are relative to meshes\
DB, SK = "Dragonborn.esm", "Skyrim.esm"
def D(x): return f"{x}:{DB}"
def S(x): return f"{x}:{SK}"
# key: (EditorID, name, vanilla WEAP, vanilla craft COBJ, vanilla temper COBJ, Ebony item, Ebony craft, Ebony temper, 1st-person model)
# The first-person model of a new weapon is a STAT: ours point at the third-person file (the vanilla bow does the same),
# except where vanilla's own first-person mesh sits at a different offset (battleaxe, greatsword), which ship their own.
WEAPONS = {
    "sword":      ("TNCW_Sword", "Carved Nordic Sword", D("01CDB1"), D("02B083"), D("03A9E0"), S("0139B1"), S("0DB8BC"), S("0F46BD"), f"{M}\\sword\\sword.nif"),
    "battleaxe":  ("TNCW_Battleaxe", "Carved Nordic Battleaxe", D("01CDAD"), D("02B07E"), D("03A9DB"), S("0139AC"), S("0DB8B8"), S("0F46B8"), f"{M}\\battleaxe\\1stpersonbattleaxe.nif"),
    "greatsword": ("TNCW_Greatsword", "Carved Nordic Greatsword", D("01CDAF"), D("02B081"), D("03A9DE"), S("0139AF"), S("0DB8BA"), S("0F46BA"), f"{M}\\greatsword\\1stpersongreatsword.nif"),
    "warhammer":  ("TNCW_Warhammer", "Carved Nordic Warhammer", D("01CDB3"), D("02B085"), D("03A9E2"), S("0139B2"), S("0DB8BE"), S("0F46C0"), f"{M}\\warhammer\\warhammer.nif"),
    "waraxe":     ("TNCW_WarAxe", "Carved Nordic War Axe", D("01CDB2"), D("02B084"), D("03A9E1"), S("0139AB"), S("0DB8BD"), S("0F46BE"), f"{M}\\waraxe\\waraxe.nif"),
    "dagger":     ("TNCW_Dagger", "Carved Nordic Dagger", D("01CDAE"), D("02B080"), D("03A9DD"), S("0139AE"), S("0DB8B9"), S("0F46B9"), f"{M}\\dagger\\dagger.nif"),
    "mace":       ("TNCW_Mace", "Carved Nordic Mace", D("01CDB0"), D("02B082"), D("03A9DF"), S("0139B0"), S("0DB8BB"), S("0F46BC"), f"{M}\\mace\\mace.nif"),
    "bow":        ("TNCW_Bow", "Carved Nordic Bow", D("026232"), D("02B07F"), D("03A9DC"), S("0139AD"), S("108CF9"), S("108D01"), f"{M}\\bow\\bow.nif"),
}
SHIELD = ("TNCW_Shield", "Carved Nordic Shield", D("026236"), D("02B065"), D("03A9DA"), S("013964"), S("0DD98C"), S("0EB4A7"), f"{M}\\shield\\shield.nif")
VAN_STAT = D("03C353"); VAN_ARMA = D("039E49")
NORDIC_MAT, EBONY_MAT = D("026230"), S("01E71E")             # DLC2WeaponMaterialNordic, WeapMaterialEbony
NORDIC_ARMAT, EBONY_ARMAT = D("024105"), S("06BBD8")         # DLC2ArmorMaterialNordicHeavy, ArmorMaterialEbony

recs, stat_pairs, weap_pairs, cobj_n, cobj_e = [], [], [], [], []
for k, (eid, name, wv, cr, tp, eb, ecr, etp, fp) in WEAPONS.items():
    recs.append({"record_type": "Static", "editorid": f"{eid}_1st", "ops": [{"field_path": "Model", "compose": {"type": "Model", "fields": {"File": fp}}}]})
    recs.append({"record_type": "Weapon", "editorid": eid, "ops": [
        {"field_path": "Name", "value": name},
        {"field_path": "Model", "compose": {"type": "Model", "fields": {"File": f"{M}\\{k}\\{k}.nif"}}},
        {"field_path": "FirstPersonModel", "value": f"@{eid}_1st"}]})
    for kind, van, evan in (("Recipe", cr, ecr), ("Temper", tp, etp)):
        recs.append({"record_type": "ConstructibleObject", "editorid": f"{eid}_{kind}", "ops": [
            {"field_path": "CreatedObject", "value": f"@{eid}"}, {"field_path": "CreatedObjectCount", "value": "1"}]})
        cobj_n.append((f"{eid}_{kind}", van)); cobj_e.append((f"{eid}_{kind}", evan))
    stat_pairs.append((f"{eid}_1st", VAN_STAT)); weap_pairs.append((eid, wv, eb))
eid, name, av, cr, tp, eb, ecr, etp, model = SHIELD
recs.append({"record_type": "ArmorAddon", "editorid": f"{eid}AA"})
recs.append({"record_type": "Armor", "editorid": eid, "ops": [{"field_path": "Name", "value": name}]})
for kind, van, evan in (("Recipe", cr, ecr), ("Temper", tp, etp)):
    recs.append({"record_type": "ConstructibleObject", "editorid": f"{eid}_{kind}", "ops": [
        {"field_path": "CreatedObject", "value": f"@{eid}"}, {"field_path": "CreatedObjectCount", "value": "1"}]})
    cobj_n.append((f"{eid}_{kind}", van)); cobj_e.append((f"{eid}_{kind}", evan))
json.dump(recs, open(os.path.join(OUT, "create.json"), "w"), indent=1)
json.dump(dict(stat=stat_pairs, weap=weap_pairs, cobj_nordic=cobj_n, cobj_ebony=cobj_e, shield=[eid, av, eb], arma=[f"{eid}AA", VAN_ARMA],
               shield_model=model, materials=dict(weap=[NORDIC_MAT, EBONY_MAT], armo=[NORDIC_ARMAT, EBONY_ARMAT])),
          open(os.path.join(OUT, "plan.json"), "w"), indent=1)
print(len(recs), "records ->", OUT)
