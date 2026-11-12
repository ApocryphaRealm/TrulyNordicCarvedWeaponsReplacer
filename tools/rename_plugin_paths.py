#!/usr/bin/env python3
r"""Rename an asset-path prefix inside a Skyrim SE plugin's records, changing nothing else (2026-11-12: the shipped asset
folders lost their 'ApocryphaTest' level - meshes\TrulyNordic\..., textures\pbr\TrulyNordic\...).

Walks the plugin (TES4 header, GRUPs, records; compressed records are refused - ours are written uncompressed), and in
every subrecord whose data contains OLD (case-insensitive) replaces it with NEW, then rewrites that subrecord's size, its
record's data size and every enclosing GRUP's size. Record headers (flags, FormID, version-control info), every other
subrecord and the record order are kept byte for byte.

Usage:  python tools/rename_plugin_paths.py <in.esp> <out.esp> [--old ApocryphaTest\TrulyNordic\ --new TrulyNordic\]
        python tools/rename_plugin_paths.py --diff <a.esp> <b.esp> [--old ... --new ...]
            record-level diff: every record of a must equal b's (same order, header, subrecords) once OLD -> NEW is
            applied to a; prints the count of records and of renamed subrecords, exit 1 on any other difference.
"""
import argparse, re, struct, sys

def records(b, o=0, end=None):
    """yields (kind, header bytes, payload bytes) depth first: kind 'GRUP-open' / 'GRUP-close' / 'REC'"""
    end = len(b) if end is None else end
    while o < end:
        typ = b[o:o + 4]; size = struct.unpack_from("<I", b, o + 4)[0]
        if typ == b"GRUP":
            yield ("GRUP-open", b[o:o + 24], None); yield from records(b, o + 24, o + size); yield ("GRUP-close", None, None); o += size
        else:
            yield ("REC", b[o:o + 24], b[o + 24:o + 24 + size]); o += 24 + size

def subrecords(data):
    q = 0; out = []
    while q < len(data):
        st = data[q:q + 4]; ln = struct.unpack_from("<H", data, q + 4)[0]
        if st == b"XXXX": raise SystemExit("XXXX (over-long subrecord) is not handled")
        out.append((st, data[q + 6:q + 6 + ln])); q += 6 + ln
    return out

def rename_payload(hdr, data, rx, new):
    flags = struct.unpack_from("<I", hdr, 8)[0]
    if flags & 0x00040000: raise SystemExit(f"compressed record {hdr[:4]!r} {struct.unpack_from('<I', hdr, 12)[0]:08X}: not handled")
    n = 0; out = b""
    for st, sd in subrecords(data):
        sd2, k = rx.subn(lambda m: new, sd); n += k
        if len(sd2) > 0xFFFF: raise SystemExit("subrecord too long")
        out += st + struct.pack("<H", len(sd2)) + sd2
    return out, n

def rewrite(b, old, new):
    rx = re.compile(re.escape(old.encode("latin-1")), re.I); nb = new.encode("latin-1")
    stack = [bytearray()]; hdrs = []; renamed = 0; recs = 0
    for kind, hdr, data in records(b):
        if kind == "GRUP-open": hdrs.append(bytearray(hdr)); stack.append(bytearray())
        elif kind == "GRUP-close":
            body = stack.pop(); h = hdrs.pop(); struct.pack_into("<I", h, 4, 24 + len(body)); stack[-1] += h + body
        else:
            d2, n = rename_payload(hdr, data, rx, nb); renamed += n; recs += 1
            h = bytearray(hdr); struct.pack_into("<I", h, 4, len(d2)); stack[-1] += h + d2
    return bytes(stack[0]), recs, renamed

def flat(b):
    return [(hdr, data) for kind, hdr, data in records(b) if kind == "REC"]

def main(argv):
    ap = argparse.ArgumentParser(); ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("--diff", action="store_true")
    ap.add_argument("--old", default="ApocryphaTest\\TrulyNordic\\"); ap.add_argument("--new", default="TrulyNordic\\")
    a = ap.parse_args(argv)
    A = open(a.a, "rb").read()
    if not a.diff:
        out, recs, n = rewrite(A, a.old, a.new); open(a.b, "wb").write(out)
        print(f"rename_plugin_paths: {a.a} -> {a.b}: {recs} records, {n} path strings renamed, {len(A)} -> {len(out)} bytes"); return 0
    B = open(a.b, "rb").read(); rx = re.compile(re.escape(a.old.encode("latin-1")), re.I); nb = a.new.encode("latin-1")
    ra, rb = flat(A), flat(B); bad = 0; nsub = 0
    if len(ra) != len(rb): print(f"DIFF record count {len(ra)} vs {len(rb)}"); return 1
    for (ha, da), (hb, db) in zip(ra, rb):
        if ha[:4] != hb[:4] or ha[8:] != hb[8:]: print("DIFF header", ha[:4], ha[12:16].hex()); bad += 1; continue
        sa, sb = subrecords(da), subrecords(db)
        if len(sa) != len(sb): print("DIFF subrecord count", ha[:4], ha[12:16].hex()); bad += 1; continue
        for (ta, xa), (tb, xb) in zip(sa, sb):
            ya = rx.sub(lambda m: nb, xa)
            if ya != xa: nsub += 1
            if ta != tb or ya != xb: print("DIFF", ha[:4], ha[12:16].hex(), ta, xa[:80], xb[:80]); bad += 1
    if B.count(b"ApocryphaTest") or B.lower().count(b"apocryphatest"): print("DIFF: the renamed plugin still names ApocryphaTest"); bad += 1
    print(f"rename_plugin_paths --diff: {len(ra)} records, {nsub} subrecords differ only by the prefix, {bad} other differences")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
