"""Decodifica el titulo de la barra de jefe de BetterHud y calcula en que x cae cada texto/imagen.
Uso: decode_hud.py <paquete.bin> <carpeta build de BetterHud (con assets/)>"""
import json, struct, sys
from pathlib import Path
from PIL import Image

buf = Path(sys.argv[1]).read_bytes()
root = Path(sys.argv[2]) / "assets"


def mutf8(b):
    s = b.replace(b"\xc0\x80", b"\x00").decode("utf-8", "surrogatepass")
    return s.encode("utf-16", "surrogatepass").decode("utf-16")


class R:
    def __init__(s, b, i): s.b, s.i = b, i
    def take(s, n): v = s.b[s.i:s.i + n]; s.i += n; return v
    def u8(s): return s.take(1)[0]
    def i16(s): return struct.unpack(">h", s.take(2))[0]
    def u16(s): return struct.unpack(">H", s.take(2))[0]
    def i32(s): return struct.unpack(">i", s.take(4))[0]
    def str(s): return mutf8(s.take(s.u16()))
    def payload(s, t):
        if t == 1: return struct.unpack(">b", s.take(1))[0]
        if t == 2: return s.i16()
        if t == 3: return s.i32()
        if t == 4: return struct.unpack(">q", s.take(8))[0]
        if t == 5: return struct.unpack(">f", s.take(4))[0]
        if t == 6: return struct.unpack(">d", s.take(8))[0]
        if t == 7: return s.take(s.i32())
        if t == 8: return s.str()
        if t == 9:
            et, n = s.u8(), s.i32()
            return [] if n <= 0 else [s.payload(et) for _ in range(n)]
        if t == 10:
            d = {}
            while True:
                tt = s.u8()
                if tt == 0: return d
                key = s.str(); d[key] = s.payload(tt)
        if t == 11: return [s.i32() for _ in range(s.i32())]
        if t == 12: return [struct.unpack(">q", s.take(8))[0] for _ in range(s.i32())]
        raise ValueError(t)


r = R(buf, 1 + 16)
action = r.u8()
tag = r.u8()
title = r.payload(tag)

fonts = {}


def load_font(name):
    if name in fonts: return fonts[name]
    ns, path = name.split(":")
    data = json.loads((root / ns / "font" / f"{path}.json").read_text(encoding="utf-8"))
    adv = {}
    for p in data["providers"]:
        if p["type"] == "space":
            for c, a in p["advances"].items(): adv.setdefault(c, (a, None))
        elif p["type"] == "bitmap":
            fns, fpath = p["file"].split(":")
            img = Image.open(root / fns / "textures" / fpath).convert("RGBA")
            rows = p["chars"]; ch = img.height // len(rows); cw = img.width // len(rows[0])
            scale = p.get("height", 8) / ch
            for j, row in enumerate(rows):
                for i, c in enumerate(row):
                    if c in adv or c == "\x00": continue
                    cell = img.crop((i * cw, j * ch, i * cw + cw, j * ch + ch))
                    bbox = cell.split()[3].getbbox()
                    width = bbox[2] if bbox else 0
                    adv[c] = (int(0.5 + width * scale) + 1, (p.get("height"), p.get("ascent")))
    fonts[name] = adv
    return adv


x = 0
events = []


def walk(node, style):
    global x
    if isinstance(node, str):
        node = {"text": node}
    if isinstance(node, list):
        for n in node: walk(n, style)
        return
    st = dict(style)
    for k in ("font", "bold", "color"):
        if k in node: st[k] = node[k]
    text = node.get("text", node.get("", ""))
    if isinstance(text, str) and text:
        font = st.get("font", "minecraft:default")
        adv = load_font(font) if font.startswith("betterhud") else {}
        start, visible = x, ""
        for c in text:
            a, info = adv.get(c, (6, None))
            if info is not None:
                visible += c
            x += a + (1 if st.get("bold") and info is not None else 0)
        if visible:
            events.append((start, x, font.split(":")[1], st.get("color", ""), visible))
    for k in ("extra",):
        if k in node: walk(node[k], st)


walk(title, {})
img = [e for e in events if e[2].endswith("_image")]
base = img[0][0] if img else 0
for s, e, f, col, v in events:
    print(f"{s - base:5d} .. {e - base:5d}  {f:32s} {col:9s} {v[:30]}")
