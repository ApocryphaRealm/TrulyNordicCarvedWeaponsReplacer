# Second step of the Standalone plugins: the houseCARL copy assignments (which vanilla record each new record takes its
# fields from) and the follow-up edits, from standalone_spec.py's plan. FormIDs of the new records follow create.json's
# order from 0x800 (houseCARL allocates them that way; the read-back checks every one by EditorID).
# Run: python -I standalone_assign.py <spec dir> <plugin file name> <nordic|ebony>
import json, os, sys
SPEC, PLUGIN, Q = sys.argv[1], sys.argv[2], sys.argv[3]
recs = json.load(open(os.path.join(SPEC, "create.json"))); plan = json.load(open(os.path.join(SPEC, "plan.json")))
FID = {r["editorid"]: f"{0x800 + i:06X}:{PLUGIN}" for i, r in enumerate(recs)}
eb = Q == "ebony"
DB, SK = "Dragonborn.esm", "Skyrim.esm"
def a(target, src, source): return {"target": FID[target], "from": src, "from_source": source}
out = {
    "stat": [a(e, v, DB) for e, v in plan["stat"]],
    "weap": [a(e, v, DB) for e, v, _ in plan["weap"]],
    "cobj": [a(e, v, SK if v.endswith(SK) else DB) for e, v in (plan["cobj_ebony"] if eb else plan["cobj_nordic"])],
    "armo": [a(plan["shield"][0], plan["shield"][1], DB)],
    "arma": [a(plan["arma"][0], plan["arma"][1], DB)],
}
ops = []
sh = FID[plan["shield"][0]]; aa = FID[plan["arma"][0]]; mdl = plan["shield_model"]
ops += [{"formid": sh, "field_path": "Armature", "op": "ReplaceAll", "values": [aa]},
        {"formid": sh, "field_path": "WorldModel[0].Model.File", "value": mdl}, {"formid": sh, "field_path": "WorldModel[1].Model.File", "value": mdl},
        {"formid": aa, "field_path": "WorldModel[0].File", "value": mdl}, {"formid": aa, "field_path": "WorldModel[1].File", "value": mdl}]
if eb:
    # the matching Ebony item's numbers (Skyrim.esm, read 2026-11-11) and its material keyword in place of Nordic's
    EB = {"TNCW_Sword": (720, 15, 13, 6), "TNCW_Battleaxe": (1585, 26, 23, 11), "TNCW_Greatsword": (1440, 22, 22, 11),
          "TNCW_Warhammer": (1725, 30, 25, 12), "TNCW_WarAxe": (865, 17, 15, 7), "TNCW_Dagger": (290, 5, 10, 5),
          "TNCW_Mace": (1000, 19, 16, 8), "TNCW_Bow": (1440, 16, 17, 8)}
    wn, we = plan["materials"]["weap"]; an, ae = plan["materials"]["armo"]
    for e, (val, wt, dmg, crit) in EB.items():
        f = FID[e]
        ops += [{"formid": f, "field_path": "BasicStats.Value", "value": str(val)}, {"formid": f, "field_path": "BasicStats.Weight", "value": str(wt)},
                {"formid": f, "field_path": "BasicStats.Damage", "value": str(dmg)}, {"formid": f, "field_path": "Critical.Damage", "value": str(crit)},
                {"formid": f, "field_path": "Keywords", "op": "Remove", "value": wn}, {"formid": f, "field_path": "Keywords", "op": "Add", "value": we}]
    ops += [{"formid": sh, "field_path": "Value", "value": "750"}, {"formid": sh, "field_path": "Weight", "value": "14"},
            {"formid": sh, "field_path": "ArmorRating", "value": "32"},
            {"formid": sh, "field_path": "Keywords", "op": "Remove", "value": an}, {"formid": sh, "field_path": "Keywords", "op": "Add", "value": ae}]
for k, v in out.items(): json.dump(v, open(os.path.join(SPEC, f"assign_{Q}_{k}.json"), "w"), indent=1)
json.dump(ops, open(os.path.join(SPEC, f"ops_{Q}.json"), "w"), indent=1)
print({k: len(v) for k, v in out.items()}, "ops", len(ops))
