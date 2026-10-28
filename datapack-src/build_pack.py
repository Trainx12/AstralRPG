# -*- coding: utf-8 -*-
"""
Arma el resource pack AstralRPG-Textures a partir de tu pack original.
Uso: python build_pack.py <carpeta donde esta descomprimido tu pack (la que tiene assets/)>
Salida: ../build/AstralRPG-Textures.zip
"""
import json
import os
import sys
import zipfile

from textures import MATERIAL_TEX, BLOCK_ITEMS, WEAPON_TEX, BOW_TEX, GEN_WEAPON, GEN_ITEM, ARMOR_SETS_TEX, ARMOR_ITEMS

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
OUT = os.path.join(HERE, "..", "build", "AstralRPG-Textures.zip")
RES_FORMAT = 84  # Minecraft 26.1.x

files = {}


def put_json(path, obj):
    files[path] = json.dumps(obj, indent=1).encode("utf-8")


def copy(src_rel, dst_rel=None):
    with open(os.path.join(SRC, src_rel), "rb") as f:
        files[dst_rel or src_rel] = f.read()


def model_ref(m):
    return {"type": "minecraft:model", "model": m}


# Materiales
for iid, tex in MATERIAL_TEX.items():
    copy(f"assets/astral/textures/item/{tex}.png")
    put_json(f"assets/astral/models/item/{iid}.json",
             {"parent": "minecraft:item/generated", "textures": {"layer0": f"astral:item/{tex}"}})
    put_json(f"assets/astral/items/{iid}.json", {"model": model_ref(f"astral:item/{iid}")})

# Madera estelar (modelo de bloque)
bm = os.path.join(SRC, "assets/astral/models/block")
for f in os.listdir(bm):
    copy(f"assets/astral/models/block/{f}")
bt = os.path.join(SRC, "assets/astral/textures/block")
for f in os.listdir(bt):
    copy(f"assets/astral/textures/block/{f}")
for iid, m in BLOCK_ITEMS.items():
    put_json(f"assets/astral/items/{iid}.json", {"model": model_ref(m)})

# Armas (en la mano como herramienta)
for iid, tex in WEAPON_TEX.items():
    copy(f"assets/armasrpg/textures/item/{tex}.png")
    put_json(f"assets/astral/models/item/{iid}.json",
             {"parent": "minecraft:item/handheld", "textures": {"layer0": f"armasrpg:item/{tex}"}})
    put_json(f"assets/astral/items/{iid}.json", {"model": model_ref(f"astral:item/{iid}")})

# Arcos con animacion
for iid, tex in BOW_TEX.items():
    for suf in ("", "_pulling_0", "_pulling_1", "_pulling_2"):
        copy(f"assets/armasrpg/textures/item/{tex}{suf}.png")
        put_json(f"assets/astral/models/item/{iid}{suf}.json",
                 {"parent": "minecraft:item/bow", "textures": {"layer0": f"armasrpg:item/{tex}{suf}"}})
    put_json(f"assets/astral/items/{iid}.json", {"model": {
        "type": "minecraft:condition", "property": "minecraft:using_item",
        "on_false": model_ref(f"astral:item/{iid}"),
        "on_true": {"type": "minecraft:range_dispatch", "property": "minecraft:use_duration", "scale": 0.05,
                    "entries": [{"threshold": 0.65, "model": model_ref(f"astral:item/{iid}_pulling_1")},
                                {"threshold": 0.9, "model": model_ref(f"astral:item/{iid}_pulling_2")}],
                    "fallback": model_ref(f"astral:item/{iid}_pulling_0")}}})

# Texturas generadas (gen_textures.py)
for iid in GEN_WEAPON + GEN_ITEM + ARMOR_ITEMS:
    copy(f"assets/astral/textures/item/gen/{iid}.png")
    parent = "minecraft:item/handheld" if iid in GEN_WEAPON else "minecraft:item/generated"
    put_json(f"assets/astral/models/item/{iid}.json", {"parent": parent, "textures": {"layer0": f"astral:item/gen/{iid}"}})
    put_json(f"assets/astral/items/{iid}.json", {"model": model_ref(f"astral:item/{iid}")})
# Taladros y motosierras (texturas de pack-source/drills, las animadas con .mcmeta)
import colorsys
import io as _io
from PIL import Image as _Img
from tools import DRILLS, CHAINSAWS


def _png(im):
    b = _io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


def _recolor(im, hue, sat=None, gain=1.0):
    im = im.copy()
    px = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = px[x, y]
            if not a:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if s > 0.15:
                h = hue
                s = sat if sat is not None else max(s, 0.6)
                v = min(1.0, v * gain)
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            px[x, y] = (int(r * 255), int(g * 255), int(b * 255), a)
    return im


def _tool_tex(tex):
    """Devuelve (imagen 16xN, cantidad de cuadros)."""
    if tex.startswith("gen:"):
        base = _Img.open(os.path.join(SRC, "drills", "industrial_chainsaw.png")).convert("RGBA")
        if tex == "gen:infernal":
            return _recolor(base, 0.05, 0.85), 1
        frames = [_recolor(base, 0.78, 0.55, g) for g in (0.9, 1.1, 1.3, 1.1)]
        strip = _Img.new("RGBA", (16, 16 * len(frames)))
        for i, f in enumerate(frames):
            strip.paste(f, (0, 16 * i))
        return strip, len(frames)
    im = _Img.open(os.path.join(SRC, "drills", tex)).convert("RGBA")
    if im.size[0] > 16:
        im = im.resize((16, 16 * im.size[1] // im.size[0]), _Img.BOX)
        _px = im.load()
        for _y in range(im.size[1]):
            for _x in range(16):
                _r, _g, _b, _a = _px[_x, _y]
                _px[_x, _y] = (_r, _g, _b, 255) if _a >= 110 else (0, 0, 0, 0)
    return im, im.size[1] // 16


for _t in DRILLS + CHAINSAWS:
    _iid = _t["id"]
    _im, _n = _tool_tex(_t["tex"])
    files[f"assets/astral/textures/item/tools/{_iid}.png"] = _png(_im)
    if _n > 1:
        put_json(f"assets/astral/textures/item/tools/{_iid}.png.mcmeta",
                 {"animation": {"frametime": 2 if _n > 4 else 3, "interpolate": False}})
    put_json(f"assets/astral/models/item/{_iid}.json",
             {"parent": "minecraft:item/handheld", "textures": {"layer0": f"astral:item/tools/{_iid}"}})
    put_json(f"assets/astral/items/{_iid}.json", {"model": model_ref(f"astral:item/{_iid}")})

# Como se ven puestas las armaduras
for s_id in ARMOR_SETS_TEX:
    for t in range(1, 6):
        name = f"{s_id}_{t}"
        for layer in ("humanoid", "humanoid_leggings"):
            copy(f"assets/astral/textures/entity/equipment/{layer}/{name}.png")
        put_json(f"assets/astral/equipment/{name}.json", {"layers": {
            "humanoid": [{"texture": f"astral:{name}"}],
            "humanoid_leggings": [{"texture": f"astral:{name}"}]}})

# Modelos de criaturas (generados por BetterModel en el servidor de prueba, misma config que en Aternos)
# y la interfaz estilo RPG (ventanas de piedra y oro, barra de items, vida/comida en barras), de gui_textures.py
for carpeta in ("bettermodel", "gui"):
    BM = os.path.join(SRC, carpeta)
    if not os.path.isdir(BM):
        continue
    for root, _, fs in os.walk(BM):
        for fname in fs:
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, BM).replace(os.sep, "/")
            with open(full, "rb") as f:
                files[rel] = f.read()

# pack.mcmeta y pack.png
files["pack.mcmeta"] = json.dumps({"pack": {
    "description": [{"text": "AstralRPG", "color": "light_purple"}, {"text": " - texturas del servidor", "color": "gray"}],
    "min_format": [RES_FORMAT, 0], "max_format": [999, 0]}}, indent=1).encode("utf-8")
try:
    from PIL import Image
    import io
    im = Image.open(os.path.join(SRC, "assets/astral/textures/item/nucleo_astral.png")).convert("RGBA")
    im = im.resize((128, 128), Image.NEAREST)
    buf = io.BytesIO()
    im.save(buf, "PNG")
    files["pack.png"] = buf.getvalue()
except Exception as e:
    print("sin pack.png:", e)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):
        z.writestr(p, files[p])
print(f"{len(files)} archivos -> {OUT}")


def models_for_datapack():
    """Devuelve {id_item: item_model} para el datapack."""
    m = {}
    for iid in list(MATERIAL_TEX) + list(BLOCK_ITEMS) + list(WEAPON_TEX) + list(BOW_TEX) + GEN_WEAPON + GEN_ITEM + ARMOR_ITEMS:
        m[iid] = f"astral:{iid}"
    return m
