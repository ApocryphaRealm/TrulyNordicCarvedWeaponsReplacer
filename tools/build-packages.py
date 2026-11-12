#!/usr/bin/env python3
r"""Build the release packages of Truly Nordic Carved Weapons Replacer from the staged build (assemble.py, textures.py).

The owner (2026-11-11 22:47, then 23:23): four main files, "each with their own FOMOD that has all of the models and
only installs the ones that you select", with pictures from the renders in the installer. One version for all of them;
the package folder names carry no version and no "FOMOD".

MAIN FILES (each a FOMOD: Common + the steps Sword, Mace, Shield - the default or its alternate, each with a picture)
    Replacer - No ESP           the vanilla Nordic carved weapons take our models through SkyPatcher; first-person
                                models and the shield are loose files at the vanilla paths
    Replacer - ESP              the same files and TrulyNordicCarvedWeapons.esp in place of the SkyPatcher ini
    Standalone - Nordic quality new items (TrulyNordicCarvedWeapons - Standalone.esp), crafted and tempered like the
                                Nordic pieces; the vanilla items are untouched (every file at our own paths)
    Standalone - Ebony quality  the same items with the Ebony pieces' numbers, keyword and recipes (same plugin name)
    Each option folder holds its model at the shared path (sword\sword.nif, mace\mace.nif, the shield), so only the
    chosen model is installed and the records find it whichever was chosen.

OPTIONAL FILE (additional_spec.NAME, working name "Additional Weapons"): the NEW weapons vanilla does not have (the spear;
the crossbow, its quiver and bolts next), beside any main file - its own light plugin in two quality variants (Quality
step), and a KID step per item that has one. Built from the table in additional_spec.py.

WHAT IT REFUSES
    * a staged file missing for any item;
    * a texture path in a shipped NIF that an install (Common + one option per step, every combination) does not contain;
    * a model path in a Standalone plugin that an install does not contain, or a vanilla path in a Standalone package.
NEVER DELETES A PACKAGE: a release folder this build replaces is moved to <project>\_work\superseded-packages\<date>\.

Usage:  python tools/build-packages.py [output folder]
"""
import os, re, sys, shutil, struct, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from items import ITEMS, WORK, MESH_REL, TEX_REL
import additional_spec as AS      # the optional file of NEW weapons (the spear; the crossbow, quiver and bolts next)
sys.path.insert(0, r"D:\Claude output\4. plans\nordic-double-bit-axe"); import niflib
STAGE = os.path.join(WORK, "stage")
NAME = "Truly Nordic Carved Weapons Replacer"
INI_DIR = r"SKSE\Plugins\SkyPatcher\weapon\TrulyNordicCarvedWeaponsReplacer"
DEFAULT = ["sword", "battleaxe", "greatsword", "warhammer", "waraxe", "dagger", "mace", "bow", "shield", "quiver"]
WEAPONS = [i for i in DEFAULT if i not in ("shield", "quiver")]
# the quiver / arrows (2026-11-12): the AMMO model (quiver.nif) by record - SkyPatcher's ammo patcher in the No-ESP
# edition, the ESP's AMMO override in the ESP edition; the PROJ model (arrowflight.nif) as a loose file at the vanilla
# path in both Replacer editions (no SkyPatcher projectile model op; the PROJ is left to whatever else edits it)
AMMO_INI_DIR = r"SKSE\Plugins\SkyPatcher\ammo\TrulyNordicCarvedWeaponsReplacer"
VAN_FLIGHT = r"meshes\dlc02\weapons\nordic\nordicarrowflight.nif"
SA_PLUGIN = "TrulyNordicCarvedWeapons - Standalone.esp"
VAN_SHIELD = r"meshes\dlc02\armor\nordicshield\nordicshield.nif"
OUR_SHIELD = MESH_REL + r"\shield\shield.nif"
FIRST_OWN = ("battleaxe", "greatsword")     # the Standalone's own first-person files (vanilla's 1st-person mesh is offset)
DOCS = ("README.md", "NOTICE.md", "CHANGELOG.md", "LICENSE")

def fail(msg): print("FAILED: " + msg); sys.exit(1)
def version():
    t = open(os.path.join(REPO, "fomod", "info.xml"), encoding="utf-8").read()
    m = re.search(r"<Version>(\d+\.\d+\.\d+)</Version>", t)
    if not m: fail("no <Version>x.y.z</Version> in fomod/info.xml (version-gate writes it)")
    return m.group(1)
def supersede(folder):
    p = os.path.dirname(os.path.abspath(folder)); root = None
    while not root:
        if os.path.isdir(os.path.join(p, "_work")): root = os.path.join(p, "_work", "superseded-packages")
        elif os.path.dirname(p) == p: root = os.path.join(os.path.dirname(os.path.abspath(folder)), "_superseded")
        else: p = os.path.dirname(p)
    day = os.path.join(root, time.strftime("%Y-%m-%d")); os.makedirs(day, exist_ok=True)
    to = os.path.join(day, "%s (replaced %s)" % (os.path.basename(os.path.normpath(folder)), time.strftime("%H%M%S")))
    shutil.move(folder, to); print("  previous package moved to", to)
def put(src, dst):
    if not os.path.isfile(src): fail(f"missing staged file {src}")
    os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy2(src, dst)
def put_tree(src, dst):
    if not os.path.isdir(src) or not os.listdir(src): fail(f"missing staged folder {src}")
    for dp, _, fs in os.walk(src):
        for f in fs: put(os.path.join(dp, f), os.path.join(dst, os.path.relpath(os.path.join(dp, f), src)))

def at(item): return ITEMS[item].get("path_stem", ITEMS[item]["stem"])
def third(item):            # staged third-person file of an item -> its shared path
    it = ITEMS[item]
    if item.startswith("shield"): return os.path.join(STAGE, item, VAN_SHIELD), OUR_SHIELD
    return os.path.join(STAGE, item, MESH_REL, it["stem"], it["stem"] + ".nif"), os.path.join(MESH_REL, at(item), at(item) + ".nif")
def first_vanilla(item):    # staged first-person file at the vanilla path (Replacer only)
    it = ITEMS[item]
    if item.startswith("shield"): return os.path.join(STAGE, item, VAN_SHIELD), VAN_SHIELD
    rel = r"meshes\dlc02\weapons\nordic" + "\\" + (it["first"] or it["third"])
    return os.path.join(STAGE, item, rel), rel
def textures(item, dest): put_tree(os.path.join(STAGE, TEX_REL, ITEMS[item]["stem"]), os.path.join(dest, TEX_REL, ITEMS[item]["stem"]))

def ini_line(item):
    it = ITEMS[item]
    return f"filterByFirstPersonModelOr=Dragonborn.esm|{it['fp_stat'].lstrip('0')}:model={MESH_REL[len('meshes') + 1:]}\\{at(item)}\\{at(item)}.nif"

def nif_textures(path):
    n = niflib.Nif(path); out = set()
    for b, t in enumerate(n.btypes):
        if t != "BSShaderTextureSet": continue
        tb = n.blocks[b]; k = struct.unpack_from("<I", tb, 0)[0]; q = 4
        for _ in range(k):
            L = struct.unpack_from("<I", tb, q)[0]; p = tb[q + 4:q + 4 + L].decode("latin-1"); q += 4 + L
            if p.lower().startswith(TEX_REL.lower() + "\\"): out.add(p)   # was the pre-1.1.0 'apocryphatest' prefix (matched nothing)
    return out
def plugin_models(path):
    """Every MODL path in a plugin (uncompressed records, as houseCARL writes them)."""
    b = open(path, "rb").read(); out = set(); i = 0
    while True:
        i = b.find(b"MODL", i)
        if i < 0: break
        L = struct.unpack_from("<H", b, i + 4)[0]; s = b[i + 6:i + 6 + L].rstrip(b"\0")
        if s.lower().endswith(b".nif"): out.add("meshes\\" + s.decode("latin-1"))
        i += 6
    return out
def check_textures(folders):
    for folder in folders:
        for dp, _, fs in os.walk(folder):
            for f in fs:
                if f.lower().endswith(".nif"):
                    for t in nif_textures(os.path.join(dp, f)):
                        if not any(os.path.isfile(os.path.join(r, t)) for r in folders): fail(f"{os.path.join(dp, f)} names {t}, which this install does not ship")

def docs(dest):
    for f in DOCS: shutil.copy2(os.path.join(REPO, f), dest)

# ------------------------------------------------------------------ the four main files, each with its own installer
# The owner (2026-11-11 23:23): "There shouldn't be any optional files. There should be four main files, each with their
# own FOMOD that has all of the models and only installs the ones that you select ... And you can include pictures from
# these renders in the FOMOD". Common = every item without an alternate; one step per alternated item, each option a
# folder holding that model at the shared path (and, for a Replacer, its vanilla-path first-person model or shield), so
# only the chosen model is ever installed. Every option shows its picture (gate row fomod-every-option-has-a-picture).
STEPS = [  # (step, group, [(option, item, folder, image, description, default)])
    ("Sword", "Nordic Sword model", [
        ("Curved saber (default)", "sword", "10 Sword - Curved saber", "sword-curved-saber.jpg",
         "A single-edged curved blade with a one-piece half guard sweeping up, a hooked pommel and a bold carved braid running to the point, in a falchion-shaped carved sheath.", True),
        ("Straight sword", "sword2", "11 Sword - Straight", "sword-straight.jpg",
         "The greatsword's double-edged blade and upper hilt at one-hand size, in a straight carved sheath of its own.", False)]),
    ("Mace", "Nordic Mace model", [
        ("Six-flanged mace (default)", "mace", "20 Mace - Six-flanged", "mace-six-flanged.jpg",
         "A working six-flanged head with pointed striking edges, a beast's biting maw carved on every flange face.", True),
        ("Classic mace", "mace2", "21 Mace - Classic", "mace-classic.jpg",
         "The vanilla mace's four-flanged shape, rebuilt with pointed striking edges and carved with the same biting maw.", False)]),
    ("Shield", "Nordic Shield model", [
        ("Carved shield (default)", "shield", "30 Shield - Carved", "shield-carved.jpg",
         "The carved crest filled out to the rim, with its spikes, its four points and the steel straps at the bottom.", True),
        ("Clean shield", "shield2", "31 Shield - Clean", "shield-clean.jpg",
         "The same round shield with the crest as a plain carved disc: the circle of braid and weave and the boss in the middle, nothing sticking out.", False)]),
]
ALTERNATED = {o[1] for _, _, opts in STEPS for o in opts}
CORE = [i for i in DEFAULT if i not in ALTERNATED]
PACKAGES = {  # folder: (kind, plugin or ini, description for info.xml)
    "Replacer - No ESP": ("replacer", "ini", "Replaces the Dragonborn Nordic carved weapons' and shield's models. No plugin: SkyPatcher swaps the models by record."),
    "Replacer - ESP": ("replacer", "esp", "Replaces the Dragonborn Nordic carved weapons' and shield's models through one light plugin. No SkyPatcher needed."),
    "Standalone - Nordic quality": ("standalone", "nordic", "Adds the carved set as new items, forged and tempered like the Nordic pieces. The vanilla Nordic items are untouched."),
    "Standalone - Ebony quality": ("standalone", "ebony", "Adds the carved set as new items with the ebony pieces' stats and recipes. The vanilla Nordic items are untouched."),
}

def place(item, dest, kind):
    """One item's files: its third-person model at the shared path (the shield: ours for a Standalone, the vanilla path
    for a Replacer), its textures, and for a Replacer the vanilla-path first-person copy."""
    if item.startswith("shield"):
        s, _ = third(item); put(s, os.path.join(dest, VAN_SHIELD if kind == "replacer" else OUR_SHIELD))
    elif ITEMS[item].get("new_item"):     # the spear: the optional file only, its own first-person file at our path
        if kind != "additional": fail(f"{item} is a new item - the optional {AS.NAME} file only")
        s, d = third(item); put(s, os.path.join(dest, d))
        fp = os.path.join(MESH_REL, at(item), "1stperson" + at(item) + ".nif"); put(os.path.join(STAGE, item, fp), os.path.join(dest, fp))
    elif item == "quiver":
        s, d = third(item); put(s, os.path.join(dest, d))
        fl = os.path.join(STAGE, item, MESH_REL, "quiver", "arrowflight.nif"); put(fl, os.path.join(dest, MESH_REL, "quiver", "arrowflight.nif"))
        if kind == "replacer": put(fl, os.path.join(dest, VAN_FLIGHT))
    else:
        s, d = third(item); put(s, os.path.join(dest, d))
        s, d = first_vanilla(item)
        if kind == "replacer": put(s, os.path.join(dest, d))
        elif item in FIRST_OWN: put(s, os.path.join(dest, MESH_REL, item, "1stperson" + item + ".nif"))
    textures(item, dest)

def xml_escape(t): return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
def module_config(title, steps=STEPS):
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">',
         f'\t<moduleName>{xml_escape(title)}</moduleName>', '\t<requiredInstallFiles>', '\t\t<folder source="Common" destination="" priority="0" />',
         '\t</requiredInstallFiles>', '\t<installSteps order="Explicit">']
    for step, group, opts in steps:
        L += [f'\t\t<installStep name="{step}">', '\t\t\t<optionalFileGroups order="Explicit">', f'\t\t\t\t<group name="{group}" type="SelectExactlyOne">', '\t\t\t\t\t<plugins order="Explicit">']
        for name, _, folder, img, desc, default in opts:
            L += [f'\t\t\t\t\t\t<plugin name="{xml_escape(name)}">', f'\t\t\t\t\t\t\t<description>{xml_escape(desc)}</description>',
                  f'\t\t\t\t\t\t\t<image path="fomod\\images\\{img}" />']
            if folder:   # an option that installs nothing (the spear's default moveset, optional file) carries no <files>
                L += ['\t\t\t\t\t\t\t<files>', f'\t\t\t\t\t\t\t\t<folder source="{folder}" destination="" priority="0" />', '\t\t\t\t\t\t\t</files>']
            L += [f'\t\t\t\t\t\t\t<typeDescriptor><type name="{"Recommended" if default else "Optional"}" /></typeDescriptor>', '\t\t\t\t\t\t</plugin>']
        L += ['\t\t\t\t\t</plugins>', '\t\t\t\t</group>', '\t\t\t</optionalFileGroups>', '\t\t</installStep>']
    L += ['\t</installSteps>', '</config>']
    return "\n".join(L) + "\n"
INFO = """<?xml version="1.0" encoding="UTF-8"?>
<fomod>
	<Name>{name}</Name>
	<Author>ApocryphaRealm</Author>
	<Version>{ver}</Version>
	<Description>{desc}</Description>
</fomod>
"""

def fomod(dest, title, steps, ver, desc):
    r"""fomod\ModuleConfig.xml + info.xml + every option's picture, and the docs"""
    fm = os.path.join(dest, "fomod"); os.makedirs(os.path.join(fm, "images"))
    open(os.path.join(fm, "ModuleConfig.xml"), "w", encoding="utf-8").write(module_config(title, steps))
    open(os.path.join(fm, "info.xml"), "w", encoding="utf-8").write(INFO.format(name=xml_escape(title), ver=ver, desc=xml_escape(desc)))
    for _, _, opts in steps:
        for o in opts:
            if not os.path.isfile(os.path.join(fm, "images", o[3])): put(os.path.join(REPO, "fomod", "images", o[3]), os.path.join(fm, "images", o[3]))
    docs(dest)

def build_package(dest, folder, ver):
    kind, what, desc = PACKAGES[folder]; common = os.path.join(dest, "Common")
    for item in CORE: place(item, common, kind)
    if kind == "replacer":
        if what == "esp": put(os.path.join(REPO, "plugin", "TrulyNordicCarvedWeapons.esp"), os.path.join(common, "TrulyNordicCarvedWeapons.esp"))
        else:
            p = os.path.join(common, INI_DIR); os.makedirs(p, exist_ok=True)
            body = [f"; {NAME}: the new models, by weapon record",
                    "; Matched by the weapon's vanilla first-person model (the Dragonborn.esm STAT), so every enchanted",
                    "; or added copy of the weapon that shows that model takes the new one. Generated by tools\\build-packages.py."] + [ini_line(i) for i in WEAPONS]
            open(os.path.join(p, "TrulyNordicCarvedWeapons.ini"), "w", newline="\r\n").write("\n".join(body) + "\n")
            p = os.path.join(common, AMMO_INI_DIR); os.makedirs(p, exist_ok=True); q = ITEMS["quiver"]
            body = [f"; {NAME}: the Nordic arrow's model (the quiver on the back, the loose and nocked arrow).",
                    "; The flying arrow (its projectile) ships as a loose file at the vanilla path. Generated by tools\\build-packages.py.",
                    f"filterByAmmos={q['ammo']}:model={MESH_REL[len('meshes') + 1:]}\\quiver\\quiver.nif"]
            open(os.path.join(p, "TrulyNordicCarvedWeapons.ini"), "w", newline="\r\n").write("\n".join(body) + "\n")
    else:
        put(os.path.join(REPO, "plugin", "standalone-" + what, SA_PLUGIN), os.path.join(common, SA_PLUGIN))
    for _, _, opts in STEPS:
        for _, item, f, _, _, _ in opts: place(item, os.path.join(dest, f), kind)
    fomod(dest, f"{NAME} - {folder}", STEPS, ver, desc)
    # every install the installer can make: Common + one option per step -> every texture resolves, no vanilla path in
    # a Standalone, every model path its plugin names is shipped
    import itertools
    for combo in itertools.product(*[opts for _, _, opts in STEPS]):
        roots = [common] + [os.path.join(dest, o[2]) for o in combo]; check_textures(roots)
        if kind == "standalone":
            for m in plugin_models(os.path.join(common, SA_PLUGIN)):
                if not any(os.path.isfile(os.path.join(r, m)) for r in roots): fail(f"{folder}: {SA_PLUGIN} points at {m}, which the install {[o[0] for o in combo]} does not ship")
    if kind == "standalone":
        for dp, _, fs in os.walk(dest):
            if "\\meshes\\dlc02" in dp.lower(): fail(f"a Standalone package must not ship a vanilla path: {dp}")

# ------------------------------------------------------------------ the optional file of NEW weapons (additional_spec.py)
# The owner (2026-11-12, via Main Agent): the non-vanilla weapons go in a separate optional file - the spear now, the
# crossbow with its quiver and bolts next. It installs beside ANY main file: its own light plugin (two variants, the same
# name, chosen by the Quality step), every model and texture at meshes\TrulyNordic\<item>\ / textures\pbr\TrulyNordic\
# <item>\ (main() refuses a path any main file also ships), and one KID step per item that has one. Everything comes
# from additional_spec.ADDITIONAL, so a new item is a new table entry, not new code here.
def kid_ini(it):
    k = it["kid"]; weap = next(r for r in it["records"] if r["edid"] == k["weap"])
    fid = f"0x{weap['fid']:X}~{AS.PLUGIN}"
    L = [f"; {NAME} - {AS.NAME}: keywords for the {k['weap']} weapon's animation packs. Generated by tools\\build-packages.py.",
         "; Needs Keyword Item Distributor (KID). Each keyword is named by its EditorID, so this file adds no plugin masters;",
         "; a keyword whose plugin is not loaded is created by KID as a new empty keyword - it changes nothing, as the packs'",
         "; own conditions point at their own plugin's keyword. Without a pack the weapon keeps the moveset its record gives it.",
         f"; The weapon is matched by its FormID in {AS.PLUGIN} and by its EditorID as a second, equivalent term."]
    for kw, why in k["keywords"]:
        L += [f"; {why}", f"Keyword = {kw}|Weapon|{fid},{k['weap']}"]
    return "\n".join(L) + "\n"
def additional_steps():
    img = AS.ADDITIONAL[0]["image"]
    steps = [("Quality", f"{AS.NAME} quality", [(opt, None, fold, img, d, q == next(iter(AS.QUALITIES)))
                                               for q, (_, opt, fold, d) in AS.QUALITIES.items()])]
    for it in AS.ADDITIONAL:
        k = it.get("kid")
        if k: steps.append((k["step"], k["group"], [(k["default"][0], None, None, it["image"], k["default"][1], True),
                                                    (k["option"][0], None, k["folder"], it["image"], k["option"][1], False)]))
    return steps
ADD_DESC = "New carved weapons that are not in the vanilla game, as their own light plugin. Installs beside any main file (Replacer or Standalone, either quality)."

def build_additional(dest, ver):
    common = os.path.join(dest, "Common")
    for it in AS.ADDITIONAL: place(it["item"], common, "additional")
    for q, (pdir, _, fold, _) in AS.QUALITIES.items():
        put(os.path.join(REPO, "plugin", pdir, AS.PLUGIN), os.path.join(dest, fold, AS.PLUGIN))
    for it in AS.ADDITIONAL:
        if it.get("kid"):
            ko = os.path.join(dest, it["kid"]["folder"]); os.makedirs(ko)
            open(os.path.join(ko, it["kid"]["ini"]), "w", newline="\r\n").write(kid_ini(it))
    steps = additional_steps()
    fomod(dest, f"{NAME} - {AS.NAME}", steps, ver, ADD_DESC)
    # every install the installer can make: the plugin's masters are Bethesda's only, it is light, every texture and model
    # path it names is shipped, and nothing lands outside our own folders
    import itertools
    for combo in itertools.product(*[opts for _, _, opts in steps]):
        roots = [common] + [os.path.join(dest, o[2]) for o in combo if o[2]]; check_textures(roots)
        plug = [os.path.join(r, AS.PLUGIN) for r in roots if os.path.isfile(os.path.join(r, AS.PLUGIN))]
        if len(plug) != 1: fail(f"{AS.NAME}: the install {[o[0] for o in combo]} ships {len(plug)} copies of {AS.PLUGIN}")
        b = open(plug[0], "rb").read(); flags = struct.unpack_from("<I", b, 8)[0]
        if not flags & 0x200: fail(f"{AS.PLUGIN} is not ESL-flagged")
        hs = struct.unpack_from("<I", b, 4)[0]; ms = re.findall(rb"MAST..([^\0]*)\0", b[24:24 + hs], re.S)
        if any(m.decode() not in AS.MASTER_ORDER for m in ms): fail(f"{AS.PLUGIN} masters {ms} - Bethesda masters only")
        for m in plugin_models(plug[0]):
            if not any(os.path.isfile(os.path.join(r, m)) for r in roots): fail(f"{AS.PLUGIN} points at {m}, which the install {[o[0] for o in combo]} does not ship")
    for r in [common] + [os.path.join(dest, o[2]) for _, _, opts in steps for o in opts if o[2]]:
        for dp, _, fs in os.walk(r):
            for f in fs:
                rel = os.path.relpath(os.path.join(dp, f), r).lower()
                if "\\" in rel and not rel.startswith((MESH_REL.lower() + "\\", TEX_REL.lower() + "\\")):
                    fail(f"{AS.NAME}: {rel} is outside meshes\\TrulyNordic / textures\\pbr\\TrulyNordic")

def installed(dest):
    """every game-relative file path any option of a package can install (Common and every option folder)"""
    out = set()
    for d in os.listdir(dest):
        if d == "fomod" or not os.path.isdir(os.path.join(dest, d)): continue
        for dp, _, fs in os.walk(os.path.join(dest, d)):
            out |= {os.path.relpath(os.path.join(dp, f), os.path.join(dest, d)).lower() for f in fs}
    return out

def main(out_root=None):
    ver = version()
    if out_root is None:
        out_root = os.path.normpath(os.path.join(REPO, "..", "..", "7. current test builds", "Skyrim - " + NAME, f"{NAME} {ver}"))
    if os.path.isdir(out_root): supersede(out_root)
    os.makedirs(out_root)
    for folder in PACKAGES: build_package(os.path.join(out_root, folder), folder, ver)
    build_additional(os.path.join(out_root, AS.NAME), ver)
    add = installed(os.path.join(out_root, AS.NAME))   # the optional file works beside any main file: no shared path
    for folder in PACKAGES:
        clash = add & installed(os.path.join(out_root, folder))
        if clash: fail(f"{AS.NAME} and {folder} both ship {sorted(clash)[:5]}")
    for d in sorted(os.listdir(out_root)):
        n = sum(len(fs) for _, _, fs in os.walk(os.path.join(out_root, d)))
        sz = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(os.path.join(out_root, d)) for f in fs)
        print(f"  {d:30} {n:4} files  {sz / 1e6:7.1f} MB")
    print(f"built {out_root}\n  version {ver}")
    return out_root

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
