#!/usr/bin/env python3
r"""Small, explicit Skyrim SE plugin writer for the arrow records (2026-11-12) - no Creation Kit, no MO2 write.

The repo's plugins were first written by houseCARL into MO2 patch folders; adding the quiver's arrow records there is not
allowed from a build helper (no writes into the MO2 instance), so these records are written straight into the repo's
plugin files: a vanilla record is read from the game's own master (read-only), its subrecords re-laid with every FormID
field remapped by its KNOWN position for that record type (AMMO, PROJ, COBJ - nothing is guessed: an unknown subrecord
signature on a copied record refuses), localized strings (the masters are localized, ours are not) written as plain
strings, and the record appended to its top group (created if missing, in vanilla's group order) with every enclosing
size and the TES4 HEDR record count / next object id updated. Records are written uncompressed.
"""
import struct, zlib

LOCALIZED = 0x80; COMPRESSED = 0x00040000
GROUP_ORDER = ["GMST", "KYWD", "LCRT", "AACT", "TXST", "GLOB", "CLAS", "FACT", "HDPT", "HAIR", "EYES", "RACE", "SOUN", "ASPC",
               "MGEF", "SCPT", "LTEX", "ENCH", "SPEL", "SCRL", "ACTI", "TACT", "ARMO", "BOOK", "CONT", "DOOR", "INGR", "LIGH",
               "MISC", "APPA", "STAT", "SCOL", "MSTT", "PWAT", "GRAS", "TREE", "CLDC", "FLOR", "FURN", "WEAP", "AMMO", "NPC_",
               "LVLN", "KEYM", "ALCH", "IDLM", "COBJ", "PROJ", "HAZD", "SLGM", "LVLI", "WTHR", "CLMT", "SPGD", "RFCT", "REGN",
               "NAVI", "CELL", "WRLD", "DIAL", "QUST", "IDLE", "PACK", "CSTY", "LSCR", "LVSP", "ANIO", "WATR", "EFSH", "EXPL",
               "DEBR", "IMGS", "IMAD", "FLST", "PERK", "BPTD", "ADDN", "AVIF", "CAMS", "CPTH", "VTYP", "MATT", "IPCT", "IPDS",
               "ARMA", "ECZN", "LCTN", "MESG", "RGDL", "DOBJ", "LGTM", "MUSC", "FSTP", "FSTS", "SMBN", "SMQN", "SMEN", "DLBR",
               "MUST", "DLVW", "WOOP", "SHOU", "EQUP", "RELA", "SCEN", "ASTP", "OTFT", "ARTO", "MATO", "MOVT", "SNDR", "DUAL",
               "SNCT", "SOPM", "COLL", "CLFM", "REVB", "LENS", "VOLI"]
# FormID fields by record type: subrecord -> list of byte offsets (None = every 4 bytes, an array of FormIDs).
# String fields that a localized master holds as a string-table id.
FIDS = {
    "AMMO": {"YNAM": [0], "ZNAM": [0], "KWDA": None, "DATA": [0]},
    "PROJ": {"DATA": [16, 20, 36, 40, 56, 60, 64, 84, 88]},
    "COBJ": {"CNTO": [0], "CNAM": [0], "BNAM": [0]},
}
PLAIN = {"AMMO": {"EDID", "OBND", "MODL", "MODT", "KSIZ"}, "PROJ": {"EDID", "OBND", "MODL", "MODT", "NAM1", "NAM2", "VNAM"},
         "COBJ": {"EDID", "COCT", "NAM1"}}
LSTRING = {"FULL", "DESC", "ONAM"}

def subrecords(data):
    q = 0; out = []
    while q < len(data):
        st = data[q:q + 4].decode(); ln = struct.unpack_from("<H", data, q + 4)[0]
        if st == "XXXX": raise SystemExit("XXXX not handled")
        out.append([st, bytes(data[q + 6:q + 6 + ln])]); q += 6 + ln
    return out
def pack_subs(subs):
    return b"".join(s.encode() + struct.pack("<H", len(d)) + d for s, d in subs)

class Plugin:
    def __init__(self, path):
        self.path = path; self.name = __import__("os").path.basename(path); b = open(path, "rb").read(); self.b = b
        hs = struct.unpack_from("<I", b, 4)[0]; self.tes4_hdr = bytearray(b[:24]); self.tes4 = subrecords(b[24:24 + hs])
        self.flags = struct.unpack_from("<I", b, 8)[0]
        self.masters = [d[:-1].decode() for s, d in self.tes4 if s == "MAST"]
        self.groups = []                                    # [(label, group header bytes, body bytes)]
        o = 24 + hs
        while o < len(b):
            assert b[o:o + 4] == b"GRUP"; gs = struct.unpack_from("<I", b, o + 4)[0]
            self.groups.append([b[o + 8:o + 12].decode(), bytearray(b[o:o + 24]), bytearray(b[o + 24:o + gs])]); o += gs
    @property
    def localized(self): return bool(self.flags & LOCALIZED)
    def records(self, label):
        """top-level records of one group (no nested groups expected in the types we touch)"""
        for g in self.groups:
            if g[0] != label: continue
            body = g[2]; o = 0
            while o < len(body):
                assert body[o:o + 4] != b"GRUP", "nested group"
                ds = struct.unpack_from("<I", body, o + 4)[0]; yield bytes(body[o:o + 24]), bytes(body[o + 24:o + 24 + ds]); o += 24 + ds
    def find(self, label, fid):
        for h, d in self.records(label):
            if struct.unpack_from("<I", h, 12)[0] == fid:
                if struct.unpack_from("<I", h, 8)[0] & COMPRESSED: d = zlib.decompress(d[4:])
                return h, d
        raise KeyError(f"{label} {fid:08X} not in {self.path}")
    def hedr(self):
        for s in self.tes4:
            if s[0] == "HEDR": return s
    def next_id(self): return struct.unpack_from("<I", self.hedr()[1], 8)[0]
    def add(self, label, hdr, data):
        """append a record (header with its FormID set, uncompressed payload) to its top group"""
        h = bytearray(hdr); struct.pack_into("<I", h, 8, struct.unpack_from("<I", h, 8)[0] & ~COMPRESSED); struct.pack_into("<I", h, 4, len(data))
        g = [x for x in self.groups if x[0] == label]; added_group = 0
        if not g:
            gh = bytearray(b"GRUP" + struct.pack("<I", 24) + label.encode() + struct.pack("<iHHI", 0, 0, 0, 0))
            new = [label, gh, bytearray()]; idx = GROUP_ORDER.index(label)
            pos = next((i for i, x in enumerate(self.groups) if GROUP_ORDER.index(x[0]) > idx), len(self.groups))
            self.groups.insert(pos, new); g = [new]; added_group = 1
        g[0][2] += h + data
        hd = self.hedr(); v, n, nid = struct.unpack_from("<fiI", hd[1], 0); hd[1] = struct.pack("<fiI", v, n + 1 + added_group, nid) + hd[1][12:]
    def bump_next_id(self, nid):
        hd = self.hedr(); v, n, old = struct.unpack_from("<fiI", hd[1], 0); hd[1] = struct.pack("<fiI", v, n, max(old, nid)) + hd[1][12:]
    def save(self, path):
        t4 = pack_subs(self.tes4); h = bytearray(self.tes4_hdr); struct.pack_into("<I", h, 4, len(t4))
        out = bytes(h) + t4
        for label, gh, body in self.groups:
            gh = bytearray(gh); struct.pack_into("<I", gh, 4, 24 + len(body)); out += bytes(gh) + bytes(body)
        open(path, "wb").write(out)

def remap_fid(v, src, dst, own_new=None):
    """a FormID of plugin src as seen from plugin dst: by master NAME (src's own index = src's own file name)"""
    if v == 0: return 0
    i = v >> 24; names = src.masters + [src.name]
    if i >= len(names): raise SystemExit(f"{v:08X}: index past {src.name}'s masters")
    nm = names[i]
    if own_new is not None and nm == own_new[0]: return own_new[1](v)
    if nm not in dst.masters: raise SystemExit(f"{v:08X} points into {nm}, which {dst.path} does not master")
    return (dst.masters.index(nm) << 24) | (v & 0xFFFFFF)

def copy_record(src, label, fid, dst, new_fid=None, strings=None, drop=(), own_new=None):
    """the vanilla record (label, fid) of master src, re-laid for dst: FormIDs remapped by name, localized strings replaced
    from `strings` (subrecord -> text; a localized string not given is dropped), subrecords in `drop` left out"""
    h, d = src.find(label, fid); out = []
    for s, sd in subrecords(d):
        if s in drop: continue
        if s in LSTRING:
            if src.localized:
                if strings and s in strings: out.append([s, strings[s].encode("latin-1") + b"\0"])
                continue
            out.append([s, (strings[s].encode("latin-1") + b"\0") if strings and s in strings else sd]); continue
        if s in FIDS[label]:
            offs = FIDS[label][s]; sd = bytearray(sd)
            for o in (range(0, len(sd), 4) if offs is None else offs):
                if o + 4 <= len(sd): struct.pack_into("<I", sd, o, remap_fid(struct.unpack_from("<I", sd, o)[0], src, dst, own_new))
            out.append([s, bytes(sd)]); continue
        if s == "CTDA":                                         # condition: Parameter 1 and the reference are FormIDs here
            sd = bytearray(sd); func = struct.unpack_from("<H", sd, 8)[0]
            assert func in (74, 448), f"condition function {func} - only GetGlobalValue (74) and HasPerk (448) are known here"
            struct.pack_into("<I", sd, 12, remap_fid(struct.unpack_from("<I", sd, 12)[0], src, dst))
            struct.pack_into("<I", sd, 24, remap_fid(struct.unpack_from("<I", sd, 24)[0], src, dst)); out.append(["CTDA", bytes(sd)]); continue
        if s not in PLAIN[label]: raise SystemExit(f"{label} {fid:08X}: subrecord {s} has no known layout here - refusing to copy it blind")
        out.append([s, sd])
    hh = bytearray(h)
    struct.pack_into("<I", hh, 12, new_fid if new_fid is not None else remap_fid(fid, src, dst))
    return hh, out

def set_sub(subs, sig, data, after=None):
    for s in subs:
        if s[0] == sig: s[1] = data; return subs
    i = next((k + 1 for k, s in enumerate(subs) if s[0] == after), len(subs)) if after else len(subs)
    subs.insert(i, [sig, data]); return subs
def zs(t): return t.encode("latin-1") + b"\0"
