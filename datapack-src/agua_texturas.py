"""Texturas del Set de Agua (arte del dueno, circuito PRIVADO): retoque al color del agua.

Lee los originales de ASTRAL_PRIVADO/originales/agua/ y deja los derivados en
ASTRAL_PRIVADO/build/entregas/agua-texturas/ con rutas del resource pack. Nunca escribe en el repo publico.

- Iconos 16x16 (casco, pechera, grebas, botas): tono llevado al celeste del agua y un poco mas de brillo.
- Espada 32x32: el acero gris pasa a agua turquesa (degradado por brillo); el mango a azul profundo.
- Armadura puesta: mitad de arriba de armor_tide_deepblue (capa 1) y de armor_tide_deepblue_legs (capa 2),
  del mod Ice and Fire que paso el dueno (TERCEROS: solo circuito privado).
- Casco: modelo 3D con las dos aletas de la cabeza (las de brazos y piernas no se pueden en vanilla).
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
    sheet.save(path)


if __name__ == '__main__':
    print(generate())
