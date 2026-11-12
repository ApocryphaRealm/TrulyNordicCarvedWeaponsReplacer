#!/usr/bin/env python3
r"""Proof that a rebuilt release differs from the tested one ONLY by the asset-folder rename (2026-11-12, 1.1.0:
meshes\ApocryphaTest\TrulyNordic -> meshes\TrulyNordic, textures\pbr\ApocryphaTest\TrulyNordic -> textures\pbr\TrulyNordic).

For the tested release folder OLD and the renamed one NEW (each: the four package folders):
  * file list: every OLD file maps to exactly one NEW file once the prefix is renamed, and nothing else is added or lost;
  * DDS and images and docs other than the changelog/readme: byte-identical;
  * NIF: the same block types in the same order, every block byte-identical except BSShaderTextureSet blocks, whose
    paths must equal OLD's with the prefix renamed; the header strings (names) identical;
  * ESP: record-level equal apart from the prefix (tools/rename_plugin_paths.py --diff logic);
  * INI and XML: equal apart from the prefix;
  * every texture path in every NIF resolves inside its own install (Common + each FOMOD option), every model path in
    the Standalone plugins and the SkyPatcher ini resolves to a shipped NIF;
  * a byte search of every NEW file finds no 'ApocryphaTest'.
Writes a markdown summary to the path given with --md. Exit 1 on any difference.
Usage: python tools/rename_proof.py <OLD release folder> <NEW release folder> --md <out.md>
"""
import os, sys, re, struct, hashlib, argparse, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, r"D:\Claude output\4. plans\nordic-double-bit-axe"); import niflib
import rename_plugin_paths as RP
OLDP = [("meshes\\apocryphatest\\trulynordic", "meshes\\trulynordic"), ("textures\\pbr\\apocryphatest\\trulynordic", "textures\\pbr\\trulynordic")]
B_OLD, B_NEW = b"ApocryphaTest\\TrulyNordic\\", b"TrulyNordic\\"
def norm(rel):
    l = rel.lower()
    for a, b in OLDP: l = l.replace(a, b)
    return l
def sub(b): return re.sub(re.escape(B_OLD), lambda m: B_NEW, b, flags=re.I)
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def files(root):
    out = {}
    for dp, _, fs in os.walk(root):
        for f in fs: p = os.path.join(dp, f); out[os.path.relpath(p, root)] = p
    return out
def texsets(n):
    out = []
    for b, t in enumerate(n.btypes):
        if t != "BSShaderTextureSet": continue
        tb = n.blocks[b]; k = struct.unpack_from("<I", tb, 0)[0]; q = 4; ps = []
        for _ in range(k):
            L = struct.unpack_from("<I", tb, q)[0]; ps.append(tb[q + 4:q + 4 + L].decode("latin-1")); q += 4 + L
        out.append((b, ps))
    return out
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("old"); ap.add_argument("new"); ap.add_argument("--md"); a = ap.parse_args()
    O, N = files(a.old), files(a.new); bad = []; stats = dict(files=0, dds_same=0, nif_same_but_paths=0, texpaths=0, esp=0, ini=0, xml=0, other_same=0)
    On = {norm(r): r for r in O}; Nn = {r.lower(): r for r in N}
    if set(On) != set(Nn):
        bad.append(f"file list differs: only old {sorted(set(On) - set(Nn))[:8]}, only new {sorted(set(Nn) - set(On))[:8]}")
    for k in sorted(set(On) & set(Nn)):
        po, pn = O[On[k]], N[Nn[k]]; ext = k.rsplit(".", 1)[-1]; stats["files"] += 1
        if ext == "dds" or ext in ("jpg", "png"):
            if sha(po) != sha(pn): bad.append(f"{k}: not byte-identical")
            else: stats["dds_same" if ext == "dds" else "other_same"] += 1
        elif ext == "nif":
            no, nn = niflib.Nif(po), niflib.Nif(pn)
            if no.btypes != nn.btypes: bad.append(f"{k}: block list differs"); continue
            if no.strings != nn.strings: bad.append(f"{k}: header strings differ")
            ts = {b for b, _ in texsets(no)}
            for b in range(len(no.blocks)):
                if b in ts: continue
                if bytes(no.blocks[b]) != bytes(nn.blocks[b]): bad.append(f"{k}: block {b} {no.btypes[b]} differs")
            for (b, ps), (b2, ps2) in zip(texsets(no), texsets(nn)):
                want = [sub(p.encode("latin-1")).decode("latin-1") for p in ps]
                if want != ps2: bad.append(f"{k}: texture set {b} {ps2} != {want}")
                stats["texpaths"] += sum(1 for p in ps2 if p)
            stats["nif_same_but_paths"] += 1
        elif ext in ("esp", "esm", "esl"):
            A, B = open(po, "rb").read(), open(pn, "rb").read(); ra, rb = RP.flat(A), RP.flat(B)
            ok = len(ra) == len(rb)
            for (ha, da), (hb, db) in zip(ra, rb):
                if ha[:4] != hb[:4] or ha[8:] != hb[8:]: ok = False; break
                sa, sb = RP.subrecords(da), RP.subrecords(db)
                if len(sa) != len(sb) or any(ta != tb or sub(xa) != xb for (ta, xa), (tb, xb) in zip(sa, sb)): ok = False; break
            if not ok: bad.append(f"{k}: plugin differs beyond the prefix")
            else: stats["esp"] += 1
        elif ext in ("ini", "xml", "txt"):
            if sub(open(po, "rb").read()) != open(pn, "rb").read(): bad.append(f"{k}: text differs beyond the prefix")
            else: stats["ini" if ext == "ini" else "xml"] += 1
        elif ext == "md":
            pass   # README / CHANGELOG carry the rename note
        else:
            if sha(po) != sha(pn): bad.append(f"{k}: not byte-identical")
            else: stats["other_same"] += 1
    # no 'ApocryphaTest' anywhere in the new files
    hits = [r for r, p in N.items() if b"apocryphatest" in open(p, "rb").read().lower() or "apocryphatest" in r.lower()]
    for h in hits: bad.append(f"{h}: still names ApocryphaTest")
    # every reference resolves inside its own install
    res = 0
    for pkg in sorted(os.listdir(a.new)):
        root = os.path.join(a.new, pkg)
        if not os.path.isdir(root): continue
        opts = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)) and d not in ("Common", "fomod")]
        groups = {}
        for d in opts: groups.setdefault(d[0], []).append(d)
        for combo in itertools.product(*groups.values()):
            roots = [os.path.join(root, "Common")] + [os.path.join(root, d) for d in combo]
            def has(rel): return any(os.path.isfile(os.path.join(r, rel)) for r in roots)
            for r in roots:
                for dp, _, fs in os.walk(r):
                    for f in fs:
                        p = os.path.join(dp, f)
                        if f.lower().endswith(".nif"):
                            for _, ps in texsets(niflib.Nif(p)):
                                for t in ps:
                                    if t.lower().startswith("textures\\pbr\\trulynordic"):
                                        res += 1
                                        if not has(t): bad.append(f"{pkg} {combo}: {os.path.relpath(p, root)} names {t}, not shipped")
                        elif f.lower().endswith(".esp"):
                            for m in RP.flat(open(p, "rb").read()):
                                for st, sd in RP.subrecords(m[1]):
                                    s = sd.rstrip(b"\0").decode("latin-1", "replace")
                                    if st in (b"MODL", b"MOD2", b"MOD3", b"MOD4", b"MOD5") and s.lower().startswith("trulynordic\\"):
                                        res += 1
                                        if not has("meshes\\" + s): bad.append(f"{pkg} {combo}: {f} {m[0][:4].decode()} {st.decode()} {s} not shipped")
                        elif f.lower().endswith(".ini"):
                            for line in open(p, encoding="utf-8", errors="replace"):
                                mm = re.search(r"model=(\S+)", line)
                                if mm:
                                    res += 1
                                    if not has("meshes\\" + mm.group(1)): bad.append(f"{pkg} {combo}: ini model {mm.group(1)} not shipped")
    lines = [f"- files compared: {stats['files']} (each tested-build file maps to exactly one renamed-build file)",
             f"- DDS byte-identical: {stats['dds_same']}; other binaries / images byte-identical: {stats['other_same']}",
             f"- NIFs equal block for block except the texture-set path strings: {stats['nif_same_but_paths']} ({stats['texpaths']} texture paths, each = the tested path with the prefix renamed)",
             f"- plugins equal record for record except the prefix: {stats['esp']}; INI equal except the prefix: {stats['ini']}; XML/TXT: {stats['xml']}",
             f"- references resolved inside their own install (every package x every FOMOD option combination): {res}",
             f"- files in the renamed build still naming ApocryphaTest: {len(hits)}",
             f"- differences beyond the prefix: {len(bad)}"]
    for b in bad[:40]: lines.append("  - " + b)
    print("\n".join(lines))
    if a.md: open(a.md, "a", encoding="utf-8").write("\n".join(lines) + "\n")
    return 1 if bad else 0
if __name__ == "__main__":
    sys.exit(main())
