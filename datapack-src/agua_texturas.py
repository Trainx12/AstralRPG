"""Texturas del Set de Agua (arte del dueno, circuito PRIVADO): retoque al color del agua.

Lee los originales de ASTRAL_PRIVADO/originales/agua/ y deja los derivados en
ASTRAL_PRIVADO/build/entregas/agua-texturas/ con rutas del resource pack. Nunca escribe en el repo publico.

- Iconos 16x16 (casco, pechera, grebas, botas): tono llevado al celeste del agua y un poco mas de brillo.
- Espada 32x32: el acero gris pasa a agua turquesa (degradado por brillo); el mango a azul profundo.
- Armadura puesta: mitad de arriba de armor_tide_deepblue (capa 1) y de armor_tide_deepblue_legs (capa 2),
  del mod Ice and Fire que paso el dueno (TERCEROS: solo circuito privado).
- Casco: casco cerrado azul oscuro y aletas reconstruidas desde el icono; resto del set intacto.
- Hacha, pico y arco (con sus 3 tensados): arte del dueno llevado al agua. Perla Abisal: su gema sin retocar.
- Perla Abisal, Coral Astral y sus menas (version piedra): arte del dueno sin retocar.
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


def casco_3d():
    """Casco cerrado azul oscuro y aletas verticales tomadas del icono (sin cabeza/orejas)."""
    im=tint(Image.open(SRC/'agua_helmet.png')).convert('RGBA')
    # El cuerpo cerrado tapa la piel. El frente y las aletas son voxeles del icono.
    elements=[{'from':[2,0,0],'to':[14,16,16],'faces':{face:{'uv':[0,0,16,16],'texture':'#solid'} for face in ('north','south','east','west','up','down')}}]
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=im.getpixel((x,y))
            if not a:continue
            uv=[x*16/im.width,y*16/im.height,(x+1)*16/im.width,(y+1)*16/im.height]
            # Aletas extendidas por los costados, con profundidad; no son las orejas del mod.
            front=x<4 or x>=im.width-4
            elements.append({'from':[x,15-y,-.12],'to':[x+1,16-y,9 if front else .12],
                             'faces':{f:{'uv':uv,'texture':'#icon'} for f in ('north','south','east','west','up','down')}})
    return {'textures':{'icon':'astral:item/agua_helmet','solid':'astral:item/agua_casco_solido','particle':'astral:item/agua_helmet'},
            'elements':elements,'display':{'head':{'translation':[0,0,0],'scale':[1,1,1]}}}


def generate():
    files = {}
    for p in PIECES:
        files[f'assets/astral/textures/item/agua_{p}.png'] = tint(Image.open(SRC / f'agua_{p}.png'))
    files['assets/astral/textures/item/agua_espada.png'] = sword(Image.open(SRC / 'agua_espada.png'))
    files['assets/astral/textures/item/agua_hacha.png'] = sword(Image.open(SRC / 'agua_hacha.png'))
    files['assets/astral/textures/item/agua_pico.png'] = sword(Image.open(SRC / 'agua_pico.png'))
    for suf in ('', '_pulling_0', '_pulling_1', '_pulling_2'):
        files[f'assets/astral/textures/item/agua_arco{suf}.png'] = bow(Image.open(SRC / f'agua_arco{suf}.png'))
    gem = Image.open(SRC / 'perla_abisal.png').convert('RGBA')   # el dueno la quiere tal cual
    files['assets/astral/textures/item/perla_abisal.png'] = gem
    # Mena de perla: la del dueno (version piedra). La de pizarra profunda queda guardada en originales.
    files['assets/astral/textures/block/perla_abisal_ore.png'] = Image.open(SRC / 'perla_abisal_ore.png').convert('RGBA')
    files['assets/astral/textures/item/coral_astral.png'] = Image.open(SRC / 'coral_astral.png').convert('RGBA')
    files['assets/astral/textures/block/coral_astral_ore.png'] = Image.open(SRC / 'coral_astral_ore.png').convert('RGBA')
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
    # Casco cerrado con aletas del icono: en la cabeza el modelo; inventario conserva su icono.
    full = tint(Image.open(SRC / 'armadura_puesta_64x64.png'), val_gain=1.05)
    files['assets/astral/textures/item/agua_casco_3d.png'] = full
    files['assets/astral/textures/item/agua_casco_solido.png'] = Image.new('RGBA',(16,16),(7,29,48,255))
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
