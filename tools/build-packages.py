#!/usr/bin/env python3
r"""Build the release packages of Truly Nordic Carved Weapons Replacer from the staged build (assemble.py, textures.py).

The owner (2026-11-11 22:47): "instead of having all this in a single fomod we should have alternate files as the main
files to simplify the file layout and not as many options to click through". One version for all of them; the package
folder names carry no version and no "FOMOD".

MAIN FILES (plain folders, no installer; each with the default models - curved saber, six-flanged mace, carved shield)
    Replacer - No ESP           the vanilla Nordic carved weapons take our models through SkyPatcher; first-person
                                models and the shield are loose files at the vanilla paths
    Replacer - ESP              the same files and TrulyNordicCarvedWeapons.esp in place of the SkyPatcher ini
    Standalone - Nordic quality new items (TrulyNordicCarvedWeapons - Standalone.esp), crafted and tempered like the
                                Nordic pieces; the vanilla items are untouched (every file at our own paths)
    Standalone - Ebony quality  the same items with the Ebony pieces' numbers, keyword and recipes (same plugin name)
OPTIONAL FILES (each swaps ONE model and works over any main file - install it after the main file)
    Straight sword, Classic mace, Clean shield
    The alternate sits at the SAME path the default uses in every main file (meshes\ApocryphaTest\TrulyNordic\sword\
    sword.nif and so on), so the Standalone items and the Replacer records both pick it up. The Replacer main files also
    carry the first-person model (sword, mace) or the shield at the VANILLA path; that copy must not land over a Standalone
    install (it would change the vanilla item there), so each optional file carries a small FOMOD with no pages: the
    vanilla-path copy installs only when the Standalone plugin is not present.

WHAT IT REFUSES
    * a staged file missing for any item;
    * a texture path in a shipped NIF that the package (main file, or main file + the optional file) does not contain;
    * a model path in a Standalone plugin that the package does not contain.
NEVER DELETES A PACKAGE: a release folder this build replaces is moved to <project>\_work\superseded-packages\<date>\.

Usage:  python tools/build-packages.py [output folder]
"""
import os, re, sys, shutil, struct, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from items import ITEMS, WORK, MESH_REL, TEX_REL
sys.path.insert(0, r"D:\Claude output\4. plans\nordic-double-bit-axe"); import niflib
STAGE = os.path.join(WORK, "stage")
NAME = "Truly Nordic Carved Weapons Replacer"
INI_DIR = r"SKSE\Plugins\SkyPatcher\weapon\TrulyNordicCarvedWeaponsReplacer"
DEFAULT = ["sword", "battleaxe", "greatsword", "warhammer", "waraxe", "dagger", "mace", "bow", "shield"]
WEAPONS = [i for i in DEFAULT if i != "shield"]
SA_PLUGIN = "TrulyNordicCarvedWeapons - Standalone.esp"
VAN_SHIELD = r"meshes\dlc02\armor\nordicshield\nordicshield.nif"
OUR_SHIELD = MESH_REL + r"\shield\shield.nif"
FIRST_OWN = ("battleaxe", "greatsword")     # the Standalone's own first-person files (vanilla's 1st-person mesh is offset)
OPTIONALS = {"Optional - Straight sword": "sword2", "Optional - Classic mace": "mace2", "Optional - Clean shield": "shield2"}
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
            if p.lower().startswith("textures\\pbr\\apocryphatest"): out.add(p)
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

def main_replacer(dest, esp):
    for item in DEFAULT:
        s, d = third(item)
        if not item.startswith("shield"): put(s, os.path.join(dest, d))
        s, d = first_vanilla(item); put(s, os.path.join(dest, d))
        textures(item, dest)
    if esp: put(os.path.join(REPO, "plugin", "TrulyNordicCarvedWeapons.esp"), os.path.join(dest, "TrulyNordicCarvedWeapons.esp"))
    else:
        p = os.path.join(dest, INI_DIR); os.makedirs(p, exist_ok=True)
        body = [f"; {NAME}: the new models, by weapon record",
                "; Matched by the weapon's vanilla first-person model (the Dragonborn.esm STAT), so every enchanted",
                "; or added copy of the weapon that shows that model takes the new one. Generated by tools\\build-packages.py."] + [ini_line(i) for i in WEAPONS]
        open(os.path.join(p, "TrulyNordicCarvedWeapons.ini"), "w", newline="\r\n").write("\n".join(body) + "\n")
    docs(dest); check_textures([dest])

def main_standalone(dest, quality):
    for item in DEFAULT:
        s, d = third(item); put(s, os.path.join(dest, d)); textures(item, dest)
        if item in FIRST_OWN:
            s, _ = first_vanilla(item); put(s, os.path.join(dest, MESH_REL, item, "1stperson" + item + ".nif"))
    p = os.path.join(REPO, "plugin", "standalone-" + quality, SA_PLUGIN); put(p, os.path.join(dest, SA_PLUGIN))
    for m in plugin_models(os.path.join(dest, SA_PLUGIN)):
        if not os.path.isfile(os.path.join(dest, m)): fail(f"{SA_PLUGIN} ({quality}) points at {m}, which the package does not ship")
    for dp, _, fs in os.walk(os.path.join(dest, "meshes")):
        if "dlc02" in dp.lower(): fail(f"a Standalone package must not ship a vanilla path: {dp}")
    docs(dest); check_textures([dest])

FOMOD = """<?xml version="1.0" encoding="UTF-8"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">
	<moduleName>{name}</moduleName>
	<requiredInstallFiles>
		<folder source="Common" destination="" priority="0" />
	</requiredInstallFiles>
	<conditionalFileInstalls>
		<patterns>
			<pattern>
				<dependencies operator="And">
					<fileDependency file="{plugin}" state="Missing" />
				</dependencies>
				<files>
					<folder source="Replacer" destination="" priority="0" />
				</files>
			</pattern>
		</patterns>
	</conditionalFileInstalls>
</config>
"""
INFO = """<?xml version="1.0" encoding="UTF-8"?>
<fomod>
	<Name>{name}</Name>
	<Author>ApocryphaRealm</Author>
	<Version>{ver}</Version>
	<Description>{desc}</Description>
</fomod>
"""
def optional(dest, item, title, ver):
    common = os.path.join(dest, "Common"); rep = os.path.join(dest, "Replacer")
    s, d = third(item); put(s, os.path.join(common, d)); textures(item, common)
    s, d = first_vanilla(item); put(s, os.path.join(rep, d))
    f = os.path.join(dest, "fomod"); os.makedirs(f)
    nm = f"{NAME} - {title}"
    open(os.path.join(f, "ModuleConfig.xml"), "w", encoding="utf-8").write(FOMOD.format(name=nm, plugin=SA_PLUGIN))
    open(os.path.join(f, "info.xml"), "w", encoding="utf-8").write(INFO.format(name=nm, ver=ver, desc=f"{title} for {NAME}: install after any main file. No choices to make - it detects the Standalone plugin."))
    docs(dest); check_textures([common])

def main(out_root=None):
    ver = version()
    if out_root is None:
        out_root = os.path.normpath(os.path.join(REPO, "..", "..", "7. current test builds", "Skyrim - " + NAME, f"{NAME} {ver}"))
    if os.path.isdir(out_root): supersede(out_root)
    os.makedirs(out_root)
    main_replacer(os.path.join(out_root, "Replacer - No ESP"), esp=False)
    main_replacer(os.path.join(out_root, "Replacer - ESP"), esp=True)
    main_standalone(os.path.join(out_root, "Standalone - Nordic quality"), "nordic")
    main_standalone(os.path.join(out_root, "Standalone - Ebony quality"), "ebony")
    for folder, item in OPTIONALS.items(): optional(os.path.join(out_root, folder), item, folder.split(" - ", 1)[1], ver)
    for d in sorted(os.listdir(out_root)):
        n = sum(len(fs) for _, _, fs in os.walk(os.path.join(out_root, d)))
        sz = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(os.path.join(out_root, d)) for f in fs)
        print(f"  {d:30} {n:4} files  {sz / 1e6:7.1f} MB")
    print(f"built {out_root}\n  version {ver}")
    return out_root

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
