"""Texturas del Set de Agua (arte del dueno, circuito PRIVADO): retoque al color del agua.

Lee los originales de ASTRAL_PRIVADO/originales/agua/ y deja los derivados en
ASTRAL_PRIVADO/build/entregas/agua-texturas/ con rutas del resource pack. Nunca escribe en el repo publico.

- Iconos 16x16 (casco, pechera, grebas, botas): tono llevado al celeste del agua y un poco mas de brillo.
- Espada 32x32: el acero gris pasa a agua turquesa (degradado por brillo); el mango a azul profundo.
- Armadura puesta: mitad de arriba de armor_tide_deepblue (capa 1) y de armor_tide_deepblue_legs (capa 2),
  del mod Ice and Fire que paso el dueno (TERCEROS: solo circuito privado).
- Casco: modelo 3D con las dos aletas de la cabeza (las de brazos y piernas no se pueden en vanilla).
- Hacha, pico, arco (con sus 3 tensados) y Perla Abisal: arte del dueno llevado al agua.
- Coral Astral y las dos menas: dibujo propio en tonos de agua (la mena de perla usa la gema del dueno).
"""
import colorsys
import json
import os
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PRIV = Path(os.environ.get('ASTRAL_PRIVADO', ROOT / '.local/terceros/AstralRPG-privado'))
SRC = PRIV / 'originales/agua'
OUT = PRIV / 'build/entregas/agua-texturas'
PIECES = ('helmet', 'chestplate', 'leggings', 'boots')


def tint(im, hue=0.565, sat_gain=1.05, val_gain=1.12, keep_dark=True):
    """Lleva cada pixel al celeste del agua conservando su brillo (y los oscuros casi negros)."""
    im = im.convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if keep_dark and v < 0.12:
                continue
            h2 = hue + (h - 0.62) * 0.6 if s > 0.15 else hue           # conserva la variacion original (azules y celestes)
            s2 = min(1.0, max(s, 0.35) * sat_gain)
            v2 = min(1.0, v * val_gain)
            r2, g2, b2 = colorsys.hsv_to_rgb(h2 % 1.0, s2, v2)
            px[x, y] = (round(r2 * 255), round(g2 * 255), round(b2 * 255), a)
    return im


def sword(im):
    """Hoja gris -> agua (turquesa claro a profundo segun el brillo); mango oscuro -> azul abisal."""
    im = im.convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if v < 0.35:      # mango y guarda oscura
                r2, g2, b2 = colorsys.hsv_to_rgb(0.62, 0.75, 0.18 + v * 0.9)
            else:             # hoja: de azul agua a espuma blanca en los brillos
                r2, g2, b2 = colorsys.hsv_to_rgb(0.545 - (v - 0.35) * 0.05, max(0.32, 0.9 - (v - 0.35) * 0.9), min(0.97, 0.42 + v * 0.55))
            px[x, y] = (round(r2 * 255), round(g2 * 255), round(b2 * 255), a)
    return im


def bow(im):
    """Madera -> agua (profunda en las sombras, clara en los brillos); cuerda gris -> espuma."""
    im = im.convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if s < 0.12:      # cuerda
                r2, g2, b2 = colorsys.hsv_to_rgb(0.52, 0.18, min(1.0, 0.55 + v * 0.45))
            else:
                r2, g2, b2 = colorsys.hsv_to_rgb(0.56 - v * 0.04, 0.85 - v * 0.45, min(0.98, 0.25 + v * 0.75))
            px[x, y] = (round(r2 * 255), round(g2 * 255), round(b2 * 255), a)
    return im


def _stone(seed):
    """Piedra del fondo marino: azul pizarra con vetas (base de las menas)."""
    import random
    rng = random.Random(seed); im = Image.new('RGBA', (16, 16)); px = im.load()
    for y in range(16):
        for x in range(16):
            v = rng.uniform(0.22, 0.34) + (0.05 if (x + 2 * y) % 7 == 0 else 0)
            r, g, b = colorsys.hsv_to_rgb(0.58, 0.38, v)
            px[x, y] = (round(r * 255), round(g * 255), round(b * 255), 255)
    return im


def ore_perla(gem):
    """Mena de Perla Abisal: piedra marina con tres gemitas (la gema del dueno achicada)."""
    im = _stone(7); small = gem.convert('RGBA').resize((6, 6), Image.LANCZOS)
    for x, y in ((1, 2), (9, 1), (5, 9)):
        im.alpha_composite(small, (x, y))
    return im


CORAL = [(0.47, 0.75, 0.45), (0.48, 0.65, 0.75), (0.50, 0.35, 0.97)]   # oscuro, medio, brillo (turquesa de arrecife)


def _coral_px(c):
    r, g, b = colorsys.hsv_to_rgb(*c); return (round(r * 255), round(g * 255), round(b * 255), 255)


def coral_item():
    """Coral Astral: rama de coral turquesa con puntas de espuma."""
    im = Image.new('RGBA', (16, 16)); px = im.load()
    dark, mid, hi = (_coral_px(c) for c in CORAL)
    trunk = [(7, 14), (7, 13), (8, 12), (8, 11), (8, 10), (7, 9), (7, 8), (8, 7)]
    left = [(6, 10), (5, 9), (4, 8), (4, 7), (3, 6), (3, 5), (4, 4)]
    right = [(9, 9), (10, 8), (11, 7), (11, 6), (12, 5), (12, 4), (11, 3)]
    top = [(8, 6), (8, 5), (9, 4), (8, 3), (8, 2)]
    for pts in (trunk, left, right, top):
        for x, y in pts:
            px[x, y] = mid; px[x + 1, y] = dark
    for x, y in ((4, 4), (11, 3), (8, 2), (3, 5), (12, 4)):
        px[x, y] = hi
    for x in range(5, 11):
        px[x, 15] = dark
    return im


def ore_coral():
    """Mena de Coral Astral: piedra marina con ramitas de coral."""
    im = _stone(11); px = im.load()
    dark, mid, hi = (_coral_px(c) for c in CORAL)
    for ox, oy in ((2, 3), (9, 2), (5, 9), (11, 10)):
        for dx, dy, c in ((1, 3, dark), (1, 2, mid), (1, 1, mid), (0, 0, hi), (2, 0, hi), (0, 1, mid), (2, 1, mid)):
            px[ox + dx, oy + dy] = c
    return im


def _box(x0, y0, z0, x1, y1, z1, u, v, w, h, d, inflate=0.0):
    """Caja con UV de piel (u,v = esquina de la plantilla; w,h,d en pixeles de textura 64x64 -> /4)."""
    q = lambda a, b, c, e: [a / 4, b / 4, c / 4, e / 4]
    return {'from': [x0 - inflate, y0 - inflate, z0 - inflate], 'to': [x1 + inflate, y1 + inflate, z1 + inflate], 'faces': {
        'north': {'uv': q(u + d, v + d, u + d + w, v + d + h), 'texture': '#t'},
        'east': {'uv': q(u, v + d, u + d, v + d + h), 'texture': '#t'},
        'south': {'uv': q(u + d + w + d, v + d, u + d + w + d + w, v + d + h), 'texture': '#t'},
        'west': {'uv': q(u + d + w, v + d, u + d + w + d, v + d + h), 'texture': '#t'},
        'up': {'uv': q(u + d, v, u + d + w, v + d), 'texture': '#t'},
        'down': {'uv': q(u + d + w, v + d, u + d + w + w, v), 'texture': '#t'}}}


# Aletas de la cabeza: medidas reales de ModelSeaSerpentArmor (Ice and Fire): caja 1x16x14 con UV en (0,32),
# pose (+-3.5, -8.8, 3.5), xRot 180 y yRot +-30 grados. En la cabeza 1 pixel = 1.6 unidades del modelo de item
# (16 unidades = casco de 10 pixeles) y el centro de la cabeza (0,-4,0) cae en (8,8,8). El giro va a 22.5
# (el maximo permitido por paso en modelos de item).
def _fin(side):
    px = 1.6
    cx, cy, cz = 8 + px * 3.5 * side, 8 + px * (8.8 - 0.4 - 4), 8 + px * (3.5 + 0.9)
    hx, hy, hz = px * 0.5, px * 8, px * 7
    side_uv = {'uv': [0, 46 / 4, 14 / 4, 62 / 4], 'rotation': 180, 'texture': '#t'}
    edge = {'uv': [14 / 4, 46 / 4, 15 / 4, 62 / 4], 'texture': '#t'}
    top = {'uv': [14 / 4, 32 / 4, 15 / 4, 46 / 4], 'texture': '#t'}
    return {'from': [round(cx - hx, 3), round(cy - hy, 3), round(cz - hz, 3)], 'to': [round(cx + hx, 3), round(cy + hy, 3), round(cz + hz, 3)],
            'rotation': {'angle': -22.5 * side, 'axis': 'y', 'origin': [round(cx, 3), round(cy, 3), round(cz, 3)]},
            'faces': {'east': side_uv, 'west': side_uv, 'north': edge, 'south': edge, 'up': top, 'down': top}}


def casco_3d():
    """Caja del casco (16 unidades = capa de armadura en la cabeza) + capa externa + las dos aletas del mod."""
    return {'textures': {'t': 'astral:item/agua_casco_3d', 'particle': 'astral:item/agua_casco_3d'},
            'elements': [_box(0, 0, 0, 16, 16, 16, 0, 0, 8, 8, 8),
                         _box(0, 0, 0, 16, 16, 16, 32, 0, 8, 8, 8, inflate=0.8),
                         _fin(-1), _fin(1)],
            'display': {'head': {'translation': [0, 0, 0], 'scale': [1, 1, 1]}}}


def generate():
    files = {}
    for p in PIECES:
        files[f'assets/astral/textures/item/agua_{p}.png'] = tint(Image.open(SRC / f'agua_{p}.png'))
    files['assets/astral/textures/item/agua_espada.png'] = sword(Image.open(SRC / 'agua_espada.png'))
    files['assets/astral/textures/item/agua_hacha.png'] = sword(Image.open(SRC / 'agua_hacha.png'))
    files['assets/astral/textures/item/agua_pico.png'] = sword(Image.open(SRC / 'agua_pico.png'))
    for suf in ('', '_pulling_0', '_pulling_1', '_pulling_2'):
        files[f'assets/astral/textures/item/agua_arco{suf}.png'] = bow(Image.open(SRC / f'agua_arco{suf}.png'))
    gem = tint(Image.open(SRC / 'perla_abisal.png'), hue=0.53, sat_gain=1.0, val_gain=1.05)
    files['assets/astral/textures/item/perla_abisal.png'] = gem
    files['assets/astral/textures/block/perla_abisal_ore.png'] = ore_perla(gem)
    files['assets/astral/textures/item/coral_astral.png'] = coral_item()
    files['assets/astral/textures/block/coral_astral_ore.png'] = ore_coral()
    layer = tint(Image.open(SRC / 'armadura_puesta_64x64.png').crop((0, 0, 64, 32)), val_gain=1.05)
    files['assets/astral/textures/entity/equipment/humanoid/agua.png'] = layer
    # Capa 2 (grebas): la del mod (armor_tide_deepblue_legs), mitad de arriba en formato 64x32.
    legs = tint(Image.open(SRC / 'armadura_grebas_64x64.png').crop((0, 0, 64, 32)), val_gain=1.05)
    files['assets/astral/textures/entity/equipment/humanoid_leggings/agua.png'] = legs
    jsons = {}
    for p in PIECES:
        jsons[f'assets/astral/models/item/agua_{p}.json'] = {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'astral:item/agua_{p}'}}
        jsons[f'assets/astral/items/agua_{p}.json'] = {'model': {'type': 'minecraft:model', 'model': f'astral:item/agua_{p}'}}
    jsons['assets/astral/models/item/agua_espada.json'] = {'parent': 'minecraft:item/handheld', 'textures': {'layer0': 'astral:item/agua_espada'}}
    jsons['assets/astral/items/agua_espada.json'] = {'model': {'type': 'minecraft:model', 'model': 'astral:item/agua_espada'}}
    for iid in ('agua_hacha', 'agua_pico'):
        jsons[f'assets/astral/models/item/{iid}.json'] = {'parent': 'minecraft:item/handheld', 'textures': {'layer0': f'astral:item/{iid}'}}
        jsons[f'assets/astral/items/{iid}.json'] = {'model': {'type': 'minecraft:model', 'model': f'astral:item/{iid}'}}
    for suf in ('', '_pulling_0', '_pulling_1', '_pulling_2'):
        jsons[f'assets/astral/models/item/agua_arco{suf}.json'] = {'parent': 'minecraft:item/bow', 'textures': {'layer0': f'astral:item/agua_arco{suf}'}}
    m = lambda suf: {'type': 'minecraft:model', 'model': f'astral:item/agua_arco{suf}'}
    jsons['assets/astral/items/agua_arco.json'] = {'model': {   # igual que el arco vanilla: 3 tensados segun el tiempo de uso
        'type': 'minecraft:condition', 'property': 'minecraft:using_item', 'on_false': m(''),
        'on_true': {'type': 'minecraft:range_dispatch', 'property': 'minecraft:use_duration', 'scale': 0.05, 'fallback': m('_pulling_0'),
                    'entries': [{'threshold': 0.65, 'model': m('_pulling_1')}, {'threshold': 0.9, 'model': m('_pulling_2')}]}}}
    # Casco 3D con las orejas (pedido del dueno): en la cabeza se dibuja este modelo; en el inventario, el icono.
    full = tint(Image.open(SRC / 'armadura_puesta_64x64.png'), val_gain=1.05)
    files['assets/astral/textures/item/agua_casco_3d.png'] = full
    jsons['assets/astral/models/item/agua_casco_3d.json'] = casco_3d()
    jsons['assets/astral/items/agua_helmet.json'] = {'model': {
        'type': 'minecraft:select', 'property': 'minecraft:display_context',
        'cases': [{'when': 'head', 'model': {'type': 'minecraft:model', 'model': 'astral:item/agua_casco_3d'}}],
        'fallback': {'type': 'minecraft:model', 'model': 'astral:item/agua_helmet'}}}
    jsons['assets/astral/equipment/agua.json'] = {'layers': {'humanoid': [{'texture': 'astral:agua'}], 'humanoid_leggings': [{'texture': 'astral:agua'}]}}
    for rel, im in files.items():
        d = OUT / rel; d.parent.mkdir(parents=True, exist_ok=True); im.save(d)
    for rel, obj in jsons.items():
        d = OUT / rel; d.parent.mkdir(parents=True, exist_ok=True); d.write_text(json.dumps(obj), encoding='utf-8')
    return OUT


def preview(path):
    base = OUT / 'assets/astral/textures'
    sheet = Image.new('RGBA', (16 * 4 * 8 + 32 * 8 + 64 * 6 + 40, 32 * 6 + 20), (40, 44, 52, 255))
    x = 0
    for p in PIECES:
        sheet.alpha_composite(Image.open(base / f'item/agua_{p}.png').resize((128, 128), Image.NEAREST), (x, 0)); x += 132
    sheet.alpha_composite(Image.open(base / 'item/agua_espada.png').resize((192, 192), Image.NEAREST), (x, 0)); x += 196
    sheet.alpha_composite(Image.open(base / 'entity/equipment/humanoid/agua.png').resize((384, 192), Image.NEAREST), (x, 0))
    x = 0
    for n in ('item/agua_hacha', 'item/agua_pico', 'item/agua_arco', 'item/agua_arco_pulling_2', 'item/perla_abisal', 'item/coral_astral',
              'block/perla_abisal_ore', 'block/coral_astral_ore'):
        im = Image.open(base / f'{n}.png').convert('RGBA')
        sheet.alpha_composite(im.resize((96, 96), Image.NEAREST), (x, 200 - 4)); x += 100
    sheet.save(path)


if __name__ == '__main__':
    print(generate())
