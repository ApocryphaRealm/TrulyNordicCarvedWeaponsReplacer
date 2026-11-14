# Last step of the Standalone plugins: copy houseCARL's two files into the repo (plugin\standalone-nordic and
# plugin\standalone-ebony, both under ONE file name so a player can swap quality without losing items), set the light
# (ESL) header flag, and read the header back: masters, record count, flags.
# Run: python -I standalone_finish.py
import os, shutil, struct
MODS = r"D:\Modlists\Njordlinger\mods"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "TrulyNordicCarvedWeapons - Standalone.esp"
SRC = {"standalone-nordic": os.path.join(MODS, "houseCARL - TrulyNordicCarvedWeapons - Standalone", NAME),
       "standalone-ebony": os.path.join(MODS, "houseCARL - TrulyNordicCarvedWeapons - Standalone Ebony", "TrulyNordicCarvedWeapons - Standalone Ebony.esp")}
for sub, src in SRC.items():
    d = os.path.join(REPO, "plugin", sub); os.makedirs(d, exist_ok=True); p = os.path.join(d, NAME); shutil.copy2(src, p)
    b = bytearray(open(p, "rb").read()); assert b[:4] == b"TES4"
    struct.pack_into("<I", b, 8, struct.unpack_from("<I", b, 8)[0] | 0x200); open(p, "wb").write(b)
    size = struct.unpack_from("<I", b, 4)[0]; q = 24; mast = []; hedr = None
    while q < 24 + size:
        t = bytes(b[q:q + 4]); L = struct.unpack_from("<H", b, q + 4)[0]; dd = b[q + 6:q + 6 + L]
        if t == b"MAST": mast.append(dd[:-1].decode())
        if t == b"HEDR": hedr = struct.unpack_from("<fiI", dd, 0)
        q += 6 + L
    print(sub, "flags", hex(struct.unpack_from("<I", b, 8)[0]), "masters", mast, "records", hedr[1], "next id", hex(hedr[2]), len(b), "bytes")
# 1.3.0 (2026-11-13): the Ebony quality's models are the black-and-gold copies at meshes\TrulyNordic\ebony\ (tools\ebony.py)
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import ebony
ebony.plugin_paths(os.path.join(REPO, "plugin", "standalone-ebony", NAME))
