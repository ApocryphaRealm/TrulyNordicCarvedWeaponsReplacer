#!/usr/bin/env python3
r"""The Ebony quality items' names: "Carved Nordic Ebony <Item>" (the owner, 2026-11-15 06:14: "The carved Nordic ebony
equipment should be called the carved Nordic ebony crossbow, sword, etc. if it's being currently set up in this game as
the standalone, which adds it to the ebony crafting tier that doesn't replace ebony").

Applies to the two Ebony quality plugins that ADD items at the ebony crafting tier - plugin\standalone-ebony\ (Standalone
- Ebony quality) and plugin\additional-ebony\ (Additional Weapons, Ebony quality). The Replacer - Ebony files rename the
vanilla Ebony items (Carved Ebony ...) and the Nordic quality files keep "Carved Nordic ..."; neither is touched here.

Every record whose FULL starts "Carved Nordic " (and does not already read "Carved Nordic Ebony ") gets the FULL
"Carved Nordic Ebony <rest>": WEAP, ARMO, AMMO and the projectiles' PROJ alike (a projectile's name is never shown, it
is kept in step with its ammo). Nothing else changes: FormIDs, EditorIDs, record order and every other subrecord stay
byte for byte; subrecord, record and GRUP sizes are rewritten. The plugins are not localized (FULL is plain text) and
the mod carries no string tables, so there is no other language file to change. Idempotent.

Run by additional_records.py (after it writes the Ebony variant) and standalone_finish.py, so a rebuilt plugin never
comes out with the Nordic names; on its own:  python -I ebony_names.py   (renames both, prints old -> new)
"""
import os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import plugin_records as P
REPO = os.path.dirname(HERE)
PLUGINS = [os.path.join(REPO, "plugin", "standalone-ebony", "TrulyNordicCarvedWeapons - Standalone.esp"),
           os.path.join(REPO, "plugin", "additional-ebony", "TrulyNordicCarvedWeapons - Additional Weapons.esp")]
OLD, NEW = "Carved Nordic ", "Carved Nordic Ebony "


def new_name(full):
    if full.startswith(NEW) or not full.startswith(OLD): return None
    return NEW + full[len(OLD):]


def rename(path, verbose=True):
    pl = P.Plugin(path)
    if pl.localized: raise SystemExit(f"{path}: localized plugin - FULL is a string id, not handled here")
    changed = []
    for g in pl.groups:
        body = g[2]; o = 0; out = bytearray()
        while o < len(body):
            if body[o:o + 4] == b"GRUP": raise SystemExit(f"{path}: nested group in {g[0]} - not handled")
            hdr = bytearray(body[o:o + 24]); ds = struct.unpack_from("<I", hdr, 4)[0]; data = bytes(body[o + 24:o + 24 + ds]); o += 24 + ds
            subs = P.subrecords(data); hit = False
            for s in subs:
                if s[0] == "FULL":
                    nm = new_name(s[1][:-1].decode("latin-1"))
                    if nm:
                        if struct.unpack_from("<I", hdr, 8)[0] & P.COMPRESSED: raise SystemExit(f"{path}: compressed record - not handled")
                        edid = next((x[1][:-1].decode() for x in subs if x[0] == "EDID"), "")
                        changed.append((g[0], struct.unpack_from("<I", hdr, 12)[0], edid, s[1][:-1].decode("latin-1"), nm))
                        s[1] = P.zs(nm); hit = True
            if hit: data = P.pack_subs(subs); struct.pack_into("<I", hdr, 4, len(data))
            out += hdr + data
        g[2] = out
    if changed: pl.save(path)
    if verbose:
        print(f"ebony_names: {os.path.basename(os.path.dirname(path))}\\{os.path.basename(path)}: {len(changed)} renamed")
        for sig, fid, edid, a, b in changed: print(f"   {sig} {fid:08X} {edid}: {a} -> {b}")
    # read-back: no FULL in this plugin still reads "Carved Nordic " without "Ebony"
    left = [(g[0], s[1][:-1].decode("latin-1")) for g in P.Plugin(path).groups for h, d in P.Plugin(path).records(g[0])
            for s in P.subrecords(d) if s[0] == "FULL" and new_name(s[1][:-1].decode("latin-1"))]
    if left: raise SystemExit(f"{path}: still Nordic names: {left}")
    return changed


if __name__ == "__main__":
    for p in PLUGINS: rename(p)
