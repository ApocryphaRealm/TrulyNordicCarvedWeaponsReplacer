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
    Standalone - Ebony quality  the same items with the Ebony pieces' numbers, keyword and recipes (same plugin name),
                                and the Ebony LOOK (1.3.0): black ebony steel, gold knotwork and gold haft rings - every
                                model and texture at meshes\TrulyNordic\ebony\ / textures\pbr\TrulyNordic\ebony\
                                (tools\ebony.py), its installer pictures from fomod\images\ebony\
    Replacer - Ebony - No ESP / Replacer - Ebony - ESP (1.3.0, tools\ebony_replacer.py): the Carved Ebony look on the
                                VANILLA Ebony weapons, arrow and shield (SkyPatcher by record, or the light plugin
                                TrulyNordicCarvedWeapons - Ebony Replacer.esp); the first-person models, the shield and the
                                arrow in flight are loose files at the vanilla Ebony paths. Its last step, "Legacy of
                                Ysgramor", puts the same models on LoY's Wolf Ebony weapons and shield (loose files at
                                LoY's mesh paths + a SkyPatcher INI per LoY plugin, named after it); the sword, dagger and
                                shield it installs follow the installer's choice through FOMOD flags (conditional installs).
    Each option folder holds its model at the shared path (sword\sword.nif, mace\mace.nif, the shield), so only the
    chosen model is installed and the records find it whichever was chosen.

OPTIONAL FILE (additional_spec.NAME, working name "Additional Weapons"): the NEW weapons vanilla does not have (the spear;
the crossbow, its quiver and bolts next), beside any main file - its own light plugin in two quality variants (Quality
step), and a KID step per item that has one. Built from the table in additional_spec.py.

WHAT IT REFUSES
    * a staged file missing for any item;
    * a texture path in a shipped NIF that an install (Common + one option per step, every combination) does not contain;
    * a model path in a Standalone plugin that an install does not contain, or a vanilla path in a Standalone package;
    * (1.3.0) an Ebony quality install that ships a shared-look model or texture, or a NIF that names one; any other
      install that ships an ebony one.
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
ARMO_INI_DIR = r"SKSE\Plugins\SkyPatcher\armor\TrulyNordicCarvedWeaponsReplacer"
# the names (2026-11-13, the owner 06:48 "Yes they should rename them"): the No-ESP edition renames the same records the
# ESP overrides, by FormID (replacer_names.names_ini_lines reads them back from the ESP), one names ini per type folder
import replacer_names as RN
import ebony as EBL                # the Ebony look (1.3.0): its staged models and textures, and its folder names
import ebony_replacer as ER        # the Ebony Replacer (1.3.0): vanilla Ebony + Legacy of Ysgramor targets, lines, plugin
NAMES_INI = "TrulyNordicCarvedWeapons - Names.ini"
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
def textures(item, dest, ebony=False):
    rel = EBL.EB_TEX if ebony else TEX_REL
    put_tree(os.path.join(STAGE, rel, ITEMS[item]["stem"]), os.path.join(dest, rel, ITEMS[item]["stem"]))

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
    b = open(path, "rb").read(); out = set()
    for tag in (b"MODL", b"MOD2", b"MOD3", b"MOD4"):   # MOD2-4: the shield's ARMO / ARMA models (1.3.0)
        i = 0
        while True:
            i = b.find(tag, i)
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
    ("Sword", "Carved Nordic Sword model", [
        ("Curved saber (default)", "sword", "10 Sword - Curved saber", "sword-curved-saber.jpg",
         "A single-edged curved blade with a one-piece half guard sweeping up, a hooked pommel and a bold carved braid running to the point, in a falchion-shaped carved sheath.", True),
        ("Straight sword", "sword2", "11 Sword - Straight", "sword-straight.jpg",
         "The greatsword's double-edged blade and upper hilt at one-hand size, in a straight carved sheath of its own.", False)]),
    ("Mace", "Carved Nordic Mace model", [
        ("Six-flanged mace (default)", "mace", "20 Mace - Six-flanged", "mace-six-flanged.jpg",
         "A working six-flanged head with pointed striking edges, every flange face carved with the set's weave and a triquetra on a dark disc inside a polished ring.", True),
        ("Classic mace", "mace2", "21 Mace - Classic", "mace-classic.jpg",
         "The vanilla mace's four-flanged shape, rebuilt with pointed striking edges and carved with the same biting maw.", False)]),
    ("Shield", "Carved Nordic Shield model", [
        ("Carved shield (default)", "shield", "30 Shield - Carved", "shield-carved.jpg",
         "The carved crest filled out to the rim, with its spikes, its four points and the steel straps at the bottom.", True),
        ("Clean shield", "shield2", "31 Shield - Clean", "shield-clean.jpg",
         "The same round shield with the crest as a plain carved disc: the circle of braid and weave and the boss in the middle, nothing sticking out.", False)]),
    # 2026-11-13, the owner 06:11: "The new dagger design should be the default option from now on, and the current version
    # should be an additional option that they can use."
    ("Dagger", "Carved Nordic Dagger model", [
        ("Carved dagger (default)", "dagger", "40 Dagger - Carved", "dagger-carved.jpg",
         "The kukri-shaped dagger with its blade carved like the rest of the set: the weave filling the flat and a triquetra on a dark disc inside a polished ring.", True),
        ("Serpent dagger", "dagger2", "41 Dagger - Serpent", "dagger-serpent.jpg",
         "The same dagger with a Jormungandr world serpent coiling along the blade and biting toward the point.", False)]),
]
ALTERNATED = {o[1] for _, _, opts in STEPS for o in opts}
CORE = [i for i in DEFAULT if i not in ALTERNATED]
PACKAGES = {  # folder: (kind, plugin or ini, description for info.xml)
    "Replacer - No ESP": ("replacer", "ini", "Replaces the Dragonborn Nordic carved weapons' and shield's models. No plugin: SkyPatcher swaps the models by record."),
    "Replacer - ESP": ("replacer", "esp", "Replaces the Dragonborn Nordic carved weapons' and shield's models through one light plugin. No SkyPatcher needed."),
    "Replacer - Ebony - No ESP": ("replacer-ebony", "ini", "Replaces the vanilla Ebony weapons', arrow's and shield's models with the Carved Ebony set, black steel and gold knotwork. No plugin: SkyPatcher swaps the models by record. Optional: the same on Legacy of Ysgramor's Wolf Ebony weapons."),
    "Replacer - Ebony - ESP": ("replacer-ebony", "esp", "Replaces the vanilla Ebony weapons', arrow's and shield's models with the Carved Ebony set, black steel and gold knotwork, through one light plugin. Optional: the same on Legacy of Ysgramor's Wolf Ebony weapons (renamed through SkyPatcher)."),
    "Standalone - Nordic quality": ("standalone", "nordic", "Adds the carved set as new items, forged and tempered like the Nordic pieces. The vanilla Nordic items are untouched."),
    "Standalone - Ebony quality": ("standalone", "ebony", "Adds the carved set as new items with the ebony pieces' stats and recipes. The vanilla Nordic items are untouched."),
}

def place(item, dest, kind, ebony=False):
    r"""One item's files: its third-person model at the shared path (the shield: ours for a Standalone, the vanilla path
    for a Replacer), its textures, and for a Replacer the vanilla-path first-person copy. ebony (1.3.0): the Ebony look's
    copies instead - every model ebony.mesh_map names, at meshes\TrulyNordic\ebony\, and the ebony textures."""
    if kind == "replacer-ebony":      # the vanilla Ebony items: our ebony third-person model by record, the rest loose
        if item.startswith("shield"):
            put(os.path.join(EBL.EB_STAGE, item, "replacer", "shield.nif"), os.path.join(dest, ER.SHIELD_FILE))
        elif item == "quiver":
            put(os.path.join(EBL.EB_STAGE, item, EBL.EB_MESH, "quiver", "quiver.nif"), os.path.join(dest, EBL.EB_MESH, "quiver", "quiver.nif"))
            put(os.path.join(EBL.EB_STAGE, item, "replacer", "flight.nif"), os.path.join(dest, ER.FLIGHT_FILE))
        else:
            _, rel = EBL.mesh_map(item)[0]; put(os.path.join(EBL.EB_STAGE, item, rel), os.path.join(dest, rel))
            put(os.path.join(EBL.EB_STAGE, item, "replacer", "first.nif"), os.path.join(dest, ER_FIRST[at(item)]))
        textures(item, dest, ebony=True); return
    if ebony:
        if kind == "replacer": fail(f"{item}: the Ebony look is for the Ebony quality files only")
        for _, rel in EBL.mesh_map(item): put(os.path.join(EBL.EB_STAGE, item, rel), os.path.join(dest, rel))
        textures(item, dest, ebony=True); return
    if item.startswith("shield"):
        s, _ = third(item); put(s, os.path.join(dest, VAN_SHIELD if kind == "replacer" else OUR_SHIELD))
    elif ITEMS[item].get("new_item"):     # the spear: the optional file only, its own first-person file at our path
        if kind != "additional": fail(f"{item} is a new item - the optional {AS.NAME} file only")
        s, d = third(item); put(s, os.path.join(dest, d))
        fp = os.path.join(MESH_REL, at(item), "1stperson" + at(item) + ".nif"); put(os.path.join(STAGE, item, fp), os.path.join(dest, fp))
    elif item == "crossbow":             # the crossbow (2026-11-13): one NIF for third and first person, our own path
        if kind != "additional": fail(f"{item} is a new item - the optional {AS.NAME} file only")
        rel = os.path.join(MESH_REL, "crossbow", "crossbow.nif"); put(os.path.join(STAGE, item, rel), os.path.join(dest, rel))
    elif item == "boltquiver":           # the bolt quiver / bolts (2026-11-13): the optional file only, our own paths
        if kind != "additional": fail(f"{item} is a new item - the optional {AS.NAME} file only")
        for f in ("boltquiver.nif", "boltflight.nif"):
            rel = os.path.join(MESH_REL, "boltquiver", f); put(os.path.join(STAGE, item, rel), os.path.join(dest, rel))
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

ER_FIRST = {v[0]: v[2] for v in ER.WEAPONS.values()}      # our item's path stem -> the vanilla Ebony first-person file
def place_loy(item, dest):
    r"""Legacy of Ysgramor: the item's ebony first-person file (the shield: our ebony shield) at LoY's mesh path, which
    both views of every LoY variant use; the textures come with the main option of the same item."""
    if item.startswith("shield"): src = os.path.join(EBL.EB_STAGE, item, "replacer", "shield.nif"); f = ER.LOY_FILES["shield"]
    else: src = os.path.join(EBL.EB_STAGE, item, "replacer", "first.nif"); f = ER.LOY_FILES[at(item)]
    put(src, os.path.join(dest, ER.LOY_DIR + f))

def xml_escape(t): return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
def module_config(title, steps=STEPS, conditional=None):
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">',
         f'\t<moduleName>{xml_escape(title)}</moduleName>', '\t<requiredInstallFiles>', '\t\t<folder source="Common" destination="" priority="0" />',
         '\t</requiredInstallFiles>', '\t<installSteps order="Explicit">']
    for step, group, opts in steps:
        L += [f'\t\t<installStep name="{step}">', '\t\t\t<optionalFileGroups order="Explicit">', f'\t\t\t\t<group name="{group}" type="SelectExactlyOne">', '\t\t\t\t\t<plugins order="Explicit">']
        for o in opts:
            name, _, folder, img, desc, default = o[:6]; flags = o[6] if len(o) > 6 else None
            L += [f'\t\t\t\t\t\t<plugin name="{xml_escape(name)}">', f'\t\t\t\t\t\t\t<description>{xml_escape(desc)}</description>',
                  f'\t\t\t\t\t\t\t<image path="fomod\\images\\{img}" />']
            if folder:   # an option that installs nothing (the spear's default moveset, optional file) carries no <files>
                L += ['\t\t\t\t\t\t\t<files>', f'\t\t\t\t\t\t\t\t<folder source="{folder}" destination="" priority="0" />', '\t\t\t\t\t\t\t</files>']
            if flags:    # (1.3.0) flags the conditional installs read (the Replacer - Ebony files' Legacy of Ysgramor step)
                L += ['\t\t\t\t\t\t\t<conditionFlags>'] + [f'\t\t\t\t\t\t\t\t<flag name="{k}">{v}</flag>' for k, v in flags.items()] + ['\t\t\t\t\t\t\t</conditionFlags>']
            L += [f'\t\t\t\t\t\t\t<typeDescriptor><type name="{"Recommended" if default else "Optional"}" /></typeDescriptor>', '\t\t\t\t\t\t</plugin>']
        L += ['\t\t\t\t\t</plugins>', '\t\t\t\t</group>', '\t\t\t</optionalFileGroups>', '\t\t</installStep>']
    L += ['\t</installSteps>']
    if conditional:   # [(required flags {name: value}, [folder, ...])] - every flag must match (operator And)
        L += ['\t<conditionalFileInstalls>', '\t\t<patterns>']
        for need, folders in conditional:
            L += ['\t\t\t<pattern>', '\t\t\t\t<dependencies operator="And">']
            L += [f'\t\t\t\t\t<flagDependency flag="{k}" value="{v}" />' for k, v in need.items()]
            L += ['\t\t\t\t</dependencies>', '\t\t\t\t<files>']
            L += [f'\t\t\t\t\t<folder source="{f}" destination="" priority="0" />' for f in folders]
            L += ['\t\t\t\t</files>', '\t\t\t</pattern>']
        L += ['\t\t</patterns>', '\t</conditionalFileInstalls>']
    L += ['</config>']
    return "\n".join(L) + "\n"
INFO = """<?xml version="1.0" encoding="UTF-8"?>
<fomod>
	<Name>{name}</Name>
	<Author>ApocryphaRealm</Author>
	<Version>{ver}</Version>
	<Description>{desc}</Description>
</fomod>
"""

def ebony_steps(steps):
    r"""the same installer with the Ebony look's pictures (fomod\images\ebony\<same name>)"""
    return [(st, g, [(o[0], o[1], o[2], "ebony\\" + o[3]) + tuple(o[4:]) for o in opts]) for st, g, opts in steps]

def fomod(dest, title, steps, ver, desc, conditional=None):
    r"""fomod\ModuleConfig.xml + info.xml + every option's picture, and the docs"""
    fm = os.path.join(dest, "fomod"); os.makedirs(os.path.join(fm, "images"))
    open(os.path.join(fm, "ModuleConfig.xml"), "w", encoding="utf-8").write(module_config(title, steps, conditional))
    open(os.path.join(fm, "info.xml"), "w", encoding="utf-8").write(INFO.format(name=xml_escape(title), ver=ver, desc=xml_escape(desc)))
    for _, _, opts in steps:
        for o in opts:
            if not os.path.isfile(os.path.join(fm, "images", o[3])): put(os.path.join(REPO, "fomod", "images", o[3]), os.path.join(fm, "images", o[3]))
    docs(dest)

def look_check(roots, ebony, label):
    """1.3.0: an Ebony quality install ships only the Ebony look (models and textures at the ebony folders, every NIF
    naming only ebony textures); any other install ships none of it. Counts what it checked and fails on zero."""
    n = 0; mesh_eb, tex_eb = (EBL.EB_MESH + "\\").lower(), (EBL.EB_TEX + "\\").lower()
    for r in roots:
        for dp, _, fs in os.walk(r):
            for f in fs:
                rel = os.path.relpath(os.path.join(dp, f), r).lower()
                if rel.endswith(".nif") and not rel.startswith(MESH_REL.lower() + "\\"):   # a vanilla- or LoY-path model
                    for t in nif_textures(os.path.join(dp, f)):
                        if ebony != t.lower().startswith(tex_eb): fail(f"{label}: {rel} names {t} - the wrong look's texture")
                    continue
                if not rel.endswith((".nif", ".dds")) or not rel.startswith((MESH_REL.lower() + "\\", TEX_REL.lower() + "\\")): continue
                n += 1; is_eb = rel.startswith((mesh_eb, tex_eb))
                if ebony and not is_eb: fail(f"{label}: the Ebony quality install ships the shared-look {rel}")
                if not ebony and is_eb: fail(f"{label}: a Nordic-look install ships the Ebony-look {rel}")
                if rel.endswith(".nif"):
                    for t in nif_textures(os.path.join(dp, f)):
                        if ebony != t.lower().startswith(tex_eb): fail(f"{label}: {rel} names {t} - the wrong look's texture")
    if not n: fail(f"{label}: the look check found no model or texture of ours to check")
    return n

# ------------------------------------------------------------------ Replacer - Ebony (1.3.0, tools\ebony_replacer.py)
def write_ini(path, head, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = [f"; {NAME}: {head[0]}"] + [f"; {h}" for h in head[1:]] + lines
    open(path, "w", newline="\r\n").write("\n".join(body) + "\n")

LOY_FOLDER = "50 Legacy of Ysgramor - Wolf Ebony weapons"
LOY_CORE = ["battleaxe", "greatsword", "waraxe"]          # LoY's Wolf Ebony items that have no installer alternate
LOY_ALT = {"sword": "sword", "sword2": "sword", "dagger": "dagger", "dagger2": "dagger", "shield": "shield", "shield2": "shield"}
def loy_alt_folder(item): return f"5{list(LOY_ALT).index(item) + 1} Legacy of Ysgramor - {item}"
def ebony_replacer_steps():
    r"""the Replacer installer in the Ebony look - every Sword / Dagger / Shield option flags its choice - and the Legacy
    of Ysgramor step; plus the conditional installs that give LoY's items the chosen sword, dagger and shield"""
    steps = []
    for st, g, opts in ebony_steps(STEPS):
        out = [tuple(o[:6]) + (({LOY_ALT[o[1]]: o[1]},) if o[1] in LOY_ALT else ()) for o in opts]
        steps.append((st, g.replace("Carved Nordic", "Carved Ebony"), out))
    steps.append(("Legacy of Ysgramor", "Legacy of Ysgramor - Wolf Ebony weapons", [
        ("Leave them as they are (default)", None, None, "ebony\\carved-ebony-set.jpg",
         "Legacy of Ysgramor's Wolf Ebony weapons keep their own look. Choose this if you do not use Legacy of Ysgramor.", True, {"loy": "Off"}),
        ("Carved Wolf Ebony weapons", None, LOY_FOLDER, "ebony\\carved-ebony-set.jpg",
         "For Legacy of Ysgramor (NordwarUA's original or Xtudo's fixes, any version): the Wolf Ebony sword, greatsword, dagger, "
         "battleaxe, war axe and shield take the Carved Ebony models chosen above and are renamed Carved Wolf Ebony (the names and "
         "the third-person models through SkyPatcher). The Wolf Ebony armour keeps its look. Put this mod below Legacy of "
         "Ysgramor and its patches in Mod Organizer's left pane.", False, {"loy": "On"})]))
    cond = [({"loy": "On", LOY_ALT[o[1]]: o[1]}, [loy_alt_folder(o[1])]) for _, _, opts in STEPS for o in opts if o[1] in LOY_ALT]
    return steps, cond

def build_ebony_replacer(dest, folder, ver):
    kind, what, desc = PACKAGES[folder]; common = os.path.join(dest, "Common")
    for item in CORE: place(item, common, kind)
    gen = "Generated by tools\\build-packages.py from tools\\ebony_replacer.py."
    if what == "esp":
        put(ER.ESP, os.path.join(common, ER.PLUGIN))
    else:
        write_ini(os.path.join(common, INI_DIR, "TrulyNordicCarvedWeapons - Ebony.ini"), [
            "the vanilla Ebony weapons' new models (Carved Ebony), by weapon record.",
            "Matched by the weapon's vanilla first-person model (the Skyrim.esm STAT), so every enchanted or added copy", "that shows that model takes the new one. " + gen], ER.model_lines())
        write_ini(os.path.join(common, AMMO_INI_DIR, "TrulyNordicCarvedWeapons - Ebony.ini"), [
            "the Ebony arrow's model (the quiver on the back, the loose and nocked arrow).",
            "The arrow in flight (its projectile) ships as a loose file at the vanilla path. " + gen], ER.ammo_lines())
        for d, lab in ((INI_DIR, "WEAP"), (AMMO_INI_DIR, "AMMO"), (ARMO_INI_DIR, "ARMO")):
            lines = ER.names_lines(lab)
            if not lines: fail(f"no {lab} names in the Ebony Replacer ESP")
            write_ini(os.path.join(common, d, "TrulyNordicCarvedWeapons - Ebony Names.ini"), [
                f"the item names, Carved Ebony ... - {len(lines)} {lab} record(s), each by FormID (nothing else is matched).",
                "The enchanted copies keep their names here: enchantment mods rename them (see tools\\replacer_names.py).", gen], lines)
    steps, cond = ebony_replacer_steps()
    for _, _, opts in steps:
        for o in opts:
            if o[1]: place(o[1], os.path.join(dest, o[2]), kind)
    # Legacy of Ysgramor: the items without an alternate, and one INI per LoY plugin named after it (loads only beside it)
    loy = os.path.join(dest, LOY_FOLDER)
    for item in LOY_CORE: place_loy(item, loy)
    models = {i: i for i in ER.LOY_NAMES}
    for plug in ER.LOY:
        write_ini(os.path.join(loy, INI_DIR, plug + ".ini"), [
            f"Legacy of Ysgramor's Wolf Ebony weapons ({plug}): the Carved Ebony third-person model and the name.",
            "Matched by each weapon's first-person STAT, never by its own FormID: NordwarUA's original and Xtudo's light",
            "version share this filename with different FormIDs, and each STAT FormID below exists in one layout only.",
            "This file loads only when that plugin is active. " + gen], ER.loy_lines(plug, "weapon", models))
        write_ini(os.path.join(loy, ARMO_INI_DIR, plug + ".ini"), [
            f"Legacy of Ysgramor's Wolf Ebony shield ({plug}): the name (the model is the loose file at LoY's own path).",
            "This file loads only when that plugin is active. " + gen], ER.loy_lines(plug, "armor", models))
    for item in LOY_ALT: place_loy(item, os.path.join(dest, loy_alt_folder(item)))
    fomod(dest, f"{NAME} - {folder}", steps, ver, desc, cond)
    # every install the installer can make: Common + one option per step + the conditional folders whose flags match
    import itertools
    n = 0
    for combo in itertools.product(*[opts for _, _, opts in steps]):
        flags = {}
        for o in combo:
            if len(o) > 6: flags.update(o[6])
        roots = [common] + [os.path.join(dest, o[2]) for o in combo if o[2]]
        roots += [os.path.join(dest, f) for need, fs in cond if all(flags.get(k) == v for k, v in need.items()) for f in fs]
        label = f"{folder} {[o[0] for o in combo]}"; check_textures(roots); look_check(roots, True, label)
        def shipped(m): return any(os.path.isfile(os.path.join(r, m)) for r in roots)
        if what == "esp":
            for m in plugin_models(os.path.join(common, ER.PLUGIN)):
                if not shipped(m): fail(f"{label}: {ER.PLUGIN} points at {m}, which the install does not ship")
        for r in roots:
            for dp, _, fs in os.walk(r):
                for f in fs:
                    if f.lower().endswith(".ini"):
                        for m in re.findall(r"model=([^:\r\n]+\.nif)", open(os.path.join(dp, f)).read()):
                            if not shipped("meshes\\" + m): fail(f"{label}: {f} sets model {m}, which the install does not ship")
        for m in list(ER_FIRST.values()) + [ER.SHIELD_FILE, ER.FLIGHT_FILE]:
            if not shipped(m): fail(f"{label}: the vanilla Ebony file {m} is not installed")
        loy_on = flags.get("loy") == "On"
        for f in ER.LOY_FILES.values():
            if shipped(ER.LOY_DIR + f) != loy_on: fail(f"{label}: Legacy of Ysgramor file {f} {'missing' if loy_on else 'installed without the option'}")
        n += 1
    for dp, _, fs in os.walk(dest):
        if "\\meshes\\dlc02" in dp.lower(): fail(f"a Replacer - Ebony package must not ship a Nordic vanilla path: {dp}")
    print(f"  {folder}: {n} installer combinations checked")

def build_package(dest, folder, ver):
    kind, what, desc = PACKAGES[folder]; common = os.path.join(dest, "Common"); eb = kind == "standalone" and what == "ebony"
    if kind == "replacer-ebony": return build_ebony_replacer(dest, folder, ver)
    for item in CORE: place(item, common, kind, ebony=eb)
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
            for d, lab in ((INI_DIR, "WEAP"), (AMMO_INI_DIR, "AMMO"), (ARMO_INI_DIR, "ARMO")):
                p = os.path.join(common, d); os.makedirs(p, exist_ok=True); lines = RN.names_ini_lines(lab)
                if not lines: fail(f"no {lab} names in the Replacer ESP")
                body = [f"; {NAME}: the item names, Carved Nordic ... - {len(lines)} {lab} record(s), each by FormID (nothing else is matched).",
                        "; The enchanted copies keep their names here: enchantment mods rename them (see tools\\replacer_names.py).",
                        "; Generated by tools\\build-packages.py from tools\\replacer_names.py."] + lines
                open(os.path.join(p, NAMES_INI), "w", newline="\r\n").write("\n".join(body) + "\n")
    else:
        put(os.path.join(REPO, "plugin", "standalone-" + what, SA_PLUGIN), os.path.join(common, SA_PLUGIN))
    for _, _, opts in STEPS:
        for _, item, f, _, _, _ in opts: place(item, os.path.join(dest, f), kind, ebony=eb)
    fomod(dest, f"{NAME} - {folder}", ebony_steps(STEPS) if eb else STEPS, ver, desc)
    # every install the installer can make: Common + one option per step -> every texture resolves, no vanilla path in
    # a Standalone, every model path its plugin names is shipped
    import itertools
    for combo in itertools.product(*[opts for _, _, opts in STEPS]):
        roots = [common] + [os.path.join(dest, o[2]) for o in combo]; check_textures(roots)
        look_check(roots, eb, f"{folder} {[o[0] for o in combo]}")
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
    steps = [("Quality", f"{AS.NAME} quality", [(opt, None, fold, ("ebony\\" + img) if q == "ebony" else img, d, q == next(iter(AS.QUALITIES)))
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
        if q == "ebony":   # 1.3.0: the Ebony quality's items in the Ebony look (1.4.0: the crossbow and bolts too)
            for it in AS.ADDITIONAL:
                if it["item"] in EBL.EBONY_ITEMS: place(it["item"], os.path.join(dest, fold), "additional", ebony=True)
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
        eb_fold = os.path.join(dest, AS.QUALITIES["ebony"][2])
        look_check([common], False, f"{AS.NAME} Common"); look_check([eb_fold], True, f"{AS.NAME} {AS.QUALITIES['ebony'][1]}")
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
