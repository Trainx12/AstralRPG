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

# Bastones de Mago en 3D con brillo animado (varitas3d.py); reemplazan el modelo plano
from varitas3d import assets as wand_assets
files.update(wand_assets())

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
# Guadanas en 3D (guadanas3d.py); van despues de las texturas planas para reemplazarlas
from guadanas3d import assets as scythe_assets
files.update(scythe_assets())
# Espadas, hachas, Guantes de Puno Meteoro y arcos en 3D (armas3d.py)
from armas3d import assets as weapon3d_assets
files.update(weapon3d_assets())
from lanzas3d import assets as spear_assets
files.update(spear_assets())
from special_weapons3d import assets as special_weapon_assets
files.update(special_weapon_assets())
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

# Mantener vanilla las capas que se dibujan sobre los items del inventario.
# Version de prueba para aislar desapariciones al arrastrar o mostrar tooltips
# en 26.1.2. No cambia las ventanas, el HUD ni los modelos de herramientas.
VANILLA_GUI_OVERLAYS = {
    f"assets/minecraft/textures/gui/sprites/{sprite}.png"
    for sprite in (
        "container/slot_highlight_front", "container/slot_highlight_back",
        "container/bundle/slot_highlight_front", "container/bundle/slot_highlight_back",
        "tooltip/background", "tooltip/frame",
    )
}

# Modelos de criaturas (generados por BetterModel en el servidor de prueba, misma config que en Aternos)
# y la interfaz estilo RPG (ventanas de piedra y oro, barra de items, vida/comida en barras), de gui_textures.py
from hud_rpg import hud
allowed_hud = {"assets/minecraft/textures/gui/" + path for path in hud()}
for carpeta in ("bettermodel", "gui"):
    BM = os.path.join(SRC, carpeta)
    if not os.path.isdir(BM):
        continue
    for root, _, fs in os.walk(BM):
        for fname in fs:
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, BM).replace(os.sep, "/")
            if rel.removesuffix(".mcmeta") in VANILLA_GUI_OVERLAYS:
                continue
            # Heredar las barras vanilla aunque queden PNG de generaciones viejas.
            # Solo se personalizan los corazones, escudos, comida y aire elegidos.
            if carpeta == "gui":
                if "/sprites/hud/" in rel and rel not in allowed_hud:
                    continue
                if "/sprites/boss_bar/" in rel:
                    continue
            with open(full, "rb") as f:
                files[rel] = f.read()

# Iconos vanilla de la referencia. No sustituir los bloques ni los tiers RPG.
from reference_style import item_sprites
for name, sprite in item_sprites().items():
    files[f"assets/minecraft/textures/item/{name}.png"] = _png(sprite)
    if name.startswith('leather_'):
        # El modelo vanilla aplica tinte marron y otra capa encima. Sin este
        # modelo, el icono no se veria igual a la referencia aunque el PNG si.
        plain = f'astral:item/reference/{name}'
        dyed = f'astral:item/reference/{name}_dyed'
        put_json(f'assets/astral/models/item/reference/{name}.json', {
            'parent': 'minecraft:item/generated', 'textures': {'layer0': f'minecraft:item/{name}'}})
        neutral = sprite.convert('LA').convert('RGBA')
        files[f'assets/astral/textures/item/reference/{name}_dyed.png'] = _png(neutral)
        put_json(f'assets/astral/models/item/reference/{name}_dyed.json', {
            'parent': 'minecraft:item/generated', 'textures': {'layer0': f'astral:item/reference/{name}_dyed'}})
        put_json(f'assets/minecraft/items/{name}.json', {'model': {
            'type': 'minecraft:condition', 'property': 'minecraft:has_component', 'component': 'minecraft:dyed_color',
            'on_true': {'type': 'minecraft:model', 'model': dyed, 'tints': [{'type': 'minecraft:dye', 'default': -6265536}]},
            'on_false': {'type': 'minecraft:model', 'model': plain}}})
# Las armaduras puestas heredan todas las texturas y la geometria vanilla.
# Los iconos de inventario de la referencia se conservan por separado.
from escape_menu import assets as escape_assets
files.update(escape_assets())
from cronista_ui import assets as cronista_assets
cronista_files, cronista_providers = cronista_assets()
files.update(cronista_files)
default_font = json.loads(files['assets/minecraft/font/default.json'])
default_font['providers'] = cronista_providers + default_font['providers']
from services_ui import assets as services_assets
service_files, service_providers = services_assets()
files.update(service_files)
default_font['providers'] = service_providers + default_font['providers']
from market_ui import assets as market_assets
market_files, market_providers = market_assets()
files.update(market_files)
default_font['providers'] = market_providers + default_font['providers']
from adventure_ui import assets as adventure_assets
adventure_files, adventure_providers = adventure_assets()
files.update(adventure_files)
default_font['providers'] = adventure_providers + default_font['providers']
from cosmeticos_ui import assets as cosmetic_assets
cosmetic_files, cosmetic_providers = cosmetic_assets()
files.update(cosmetic_files)
default_font['providers'] = cosmetic_providers + default_font['providers']
from mascotas_ui import assets as pet_ui_assets
pet_ui_files, pet_ui_providers = pet_ui_assets()
files.update(pet_ui_files)
default_font['providers'] = pet_ui_providers + default_font['providers']
from gacha_ui import assets as gacha_assets
gacha_files, gacha_providers = gacha_assets()
files.update(gacha_files)
default_font['providers'] = gacha_providers + default_font['providers']
from travel_ui import assets as travel_assets
travel_files, travel_providers = travel_assets()
files.update(travel_files)
default_font['providers'] = travel_providers + default_font['providers']
put_json('assets/minecraft/font/default.json', default_font)

# Arte nuevo de inventario: prevalece sobre las texturas antiguas.
from item_redesign import assets as redesigned_item_assets, IDS as REDESIGN_IDS
files.update(redesigned_item_assets())

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

# Sin corazones oscuros al pegar (particula damage_indicator): textura transparente.
# El dano se ve con el indicador propio de astral_gameplay.sk (escala.py).
try:
    from PIL import Image as _Img
    _buf = _io.BytesIO()
    _Img.new("RGBA", (8, 8), (0, 0, 0, 0)).save(_buf, "PNG")
    files["assets/minecraft/textures/particle/damage.png"] = _buf.getvalue()
except Exception as e:
    print("sin particula transparente:", e)

# Stellarity (resource pack oficial, con permiso del autor): ver pack-source/terceros/CREDITOS.txt.
# Lo nuestro gana en los choques; la fuente default se junta; sus overlays van al pack.mcmeta.
STELLARITY_RENOMBRES = {  # nombre en el datapack 5.4.2 -> nombre en el pack 6.0.1
    "endermans_hand": "enderman_hand",
    "shepherds_pie": "shepherd_pie",
    "void_locket": "void_pendant",
    "_technical/empress_wing": "empress_wings",
}


def stellarity():
    zpath = os.path.join(SRC, "terceros", "Stellarity-6.0.1-RP.zip")
    if not os.path.exists(zpath):
        print("sin Stellarity:", zpath)
        return
    with zipfile.ZipFile(zpath) as st:
        meta = json.loads(st.read("pack.mcmeta").decode("utf-8"))
        added = 0
        for name in st.namelist():
            if name.endswith("/") or name in ("pack.mcmeta", "pack.png", "README.md") or "/optifine/" in name:
                continue
            data = st.read(name)
            if name == "assets/minecraft/font/default.json" and name in files:
                ours = json.loads(files[name])
                theirs = json.loads(data.decode("utf-8"))
                ours["providers"] = ours.get("providers", []) + theirs.get("providers", [])
                files[name] = json.dumps(ours, ensure_ascii=False).encode("utf-8")
                continue
            if name in files:
                continue
            files[name] = data
            added += 1
    # El server usa el datapack 5.4.2 y el pack es 6.0.1: algunos items cambiaron de nombre.
    # Se agrega el nombre viejo apuntando al modelo nuevo (si no, salen violeta y negro).
    for old, new in STELLARITY_RENOMBRES.items():
        src, dst = f"assets/stellarity/items/{new}.json", f"assets/stellarity/items/{old}.json"
        if src in files and dst not in files:
            files[dst] = files[src]
            added += 1
    pack = json.loads(files["pack.mcmeta"])
    pack["overlays"] = meta.get("overlays", {"entries": []})
    files["pack.mcmeta"] = json.dumps(pack, indent=1).encode("utf-8")
    print(f"Stellarity: {added} archivos agregados")


stellarity()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
archive = _io.BytesIO()
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):
        z.writestr(p, files[p])
from pathlib import Path
target = Path(OUT).resolve()
temporary = target.with_suffix('.zip.tmp')
temporary.write_bytes(archive.getvalue())
temporary.replace(target)
print(f"{len(files)} archivos -> {OUT}")


def models_for_datapack():
    """Devuelve {id_item: item_model} para el datapack."""
    m = {}
    for iid in list(MATERIAL_TEX) + list(BLOCK_ITEMS) + list(WEAPON_TEX) + list(BOW_TEX) + GEN_WEAPON + GEN_ITEM + ARMOR_ITEMS + REDESIGN_IDS:
        m[iid] = f"astral:{iid}"
    return m
