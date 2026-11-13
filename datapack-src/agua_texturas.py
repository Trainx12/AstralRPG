"""Texturas del Set de Agua (arte del dueno, circuito PRIVADO): retoque al color del agua.

Lee los originales de ASTRAL_PRIVADO/originales/agua/ y deja los derivados en
ASTRAL_PRIVADO/build/entregas/agua-texturas/ con rutas del resource pack. Nunca escribe en el repo publico.

- Iconos 16x16 (casco, pechera, grebas, botas): tono llevado al celeste del agua y un poco mas de brillo.
- Espada 32x32: el acero gris pasa a agua turquesa (degradado por brillo); el mango a azul profundo.
- Armadura puesta: la mitad de arriba del 64x64 es la capa estandar 64x32 (casco, pecho, brazos, botas);
  se usa tambien para las grebas (capa 2) hasta que el dueno pase una propia.
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


def generate():
    files = {}
    for p in PIECES:
        files[f'assets/astral/textures/item/agua_{p}.png'] = tint(Image.open(SRC / f'agua_{p}.png'))
    files['assets/astral/textures/item/agua_espada.png'] = sword(Image.open(SRC / 'agua_espada.png'))
    layer = tint(Image.open(SRC / 'armadura_puesta_64x64.png').crop((0, 0, 64, 32)), val_gain=1.05)
    files['assets/astral/textures/entity/equipment/humanoid/agua.png'] = layer
    files['assets/astral/textures/entity/equipment/humanoid_leggings/agua.png'] = layer
    jsons = {}
    for p in PIECES:
        jsons[f'assets/astral/models/item/agua_{p}.json'] = {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'astral:item/agua_{p}'}}
        jsons[f'assets/astral/items/agua_{p}.json'] = {'model': {'type': 'minecraft:model', 'model': f'astral:item/agua_{p}'}}
    jsons['assets/astral/models/item/agua_espada.json'] = {'parent': 'minecraft:item/handheld', 'textures': {'layer0': 'astral:item/agua_espada'}}
    jsons['assets/astral/items/agua_espada.json'] = {'model': {'type': 'minecraft:model', 'model': 'astral:item/agua_espada'}}
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
