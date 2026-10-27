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
BM = os.path.join(SRC, "bettermodel")
if os.path.isdir(BM):
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
