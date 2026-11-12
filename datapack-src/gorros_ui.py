"""Coleccion de sombreros: marco ilustrado propio (Gemini, 12/11/2026) y vitrina de 20 celdas grandes.

Los gorros van en columnas alternadas (1, 3, 5, 7) de las filas 0-4 para que cada uno tenga su celda
dorada grande; en el circuito privado se dibujan agrandados (`menu_sombrero_*`, oversized_in_gui).
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw
from cosmeticos_ui import FILL, EDGE
from services_ui import png, SPLIT, SIZE, outlined
from market_ui import band_color
from escape_menu import text
from adventure_ui import label

ROOT = Path(__file__).resolve().parent
START, END = '', ''
GLYPHS = tuple(chr(0xed10+i) for i in range(4))
FRAME = ('sombreros', (314, 352, 1533, 1998))
HAT_SLOTS = tuple(r*9+c for r in range(5) for c in (1, 3, 5, 7))
CLEAR_SLOTS = tuple(range(47, 52))
BACK_SLOT, GACHA_SLOT = 45, 53
CELL = '#132033'
# Escala extra de los gorros dentro del menu (solo modelos privados).
MENU_SCALE = 1.55


def title():
    return '&f'+START+''.join(GLYPHS)+END


def frame():
    art, (l, t, r, b) = FRAME
    src = Image.open(ROOT/f'pack-source/ref/{art}-frame.png').convert('RGBA')
    sx, sy = [0, l, r, src.width], [0, t, b, src.height]
    dx, dy = [0, 24, 200, 224], [0, 56, 258, SIZE[1]]
    im = Image.new('RGBA', SIZE)
    for row in range(3):
        for col in range(3):
            piece = src.crop((sx[col], sy[row], sx[col+1], sy[row+1]))
            im.alpha_composite(piece.resize((dx[col+1]-dx[col], dy[row+1]-dy[row]), Image.Resampling.LANCZOS), (dx[col], dy[row]))
    return im


def slot_xy(slot):
    return 31+slot % 9*18, 57+slot//9*18


def panel():
    im = frame(); d = ImageDraw.Draw(im)
    outlined(im, 'GORROS Y SOMBREROS', (116, 29))
    d.rectangle((24, 56, 199, 258), fill=FILL)
    # Celdas grandes de vitrina: 34 px, con el hueco real de la casilla en el centro.
    for slot in HAT_SLOTS:
        x, y = slot_xy(slot)
        d.rectangle((x-8, y+1, x+25, y+16), fill=CELL, outline=EDGE)
        d.rectangle((x-7, y+2, x+24, y+15), outline='#2f4258')
        for cx, cy in ((x-8, y+1), (x+25, y+1), (x-8, y+16), (x+25, y+16)):
            d.point((cx, cy), fill='#8bdce2')
        d.rectangle((x+1, y+1, x+16, y+16), fill=(0, 0, 0, 0))
    for slot in (BACK_SLOT, GACHA_SLOT):
        x, y = slot_xy(slot)
        d.rectangle((x, y, x+17, y+17), outline=EDGE)
        d.rectangle((x+1, y+1, x+16, y+16), fill=(0, 0, 0, 0))
    d.rectangle((67, 147, 156, 164), fill=(0, 0, 0, 0))
    d.rectangle((31, 168, 192, 177), fill=band_color(EDGE)); d.line((31, 167, 192, 167), fill=EDGE)
    d.line((31, 178, 192, 178), fill=EDGE); d.line((33, 169, 190, 169), fill='#ffffff60')
    for row in (*range(3), 4):
        for col in range(9):
            x, y = 31+col*18, 179+row*18 if row < 3 else 237
            d.rectangle((x, y, x+17, y+17), outline='#597477')
            d.rectangle((x+1, y+1, x+16, y+16), fill=(0, 0, 0, 0))
    return im


def clear_button():
    im = Image.new('RGBA', (90, 18), '#5a2230'); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 89, 17), outline=EDGE); d.rectangle((2, 2, 87, 15), outline='#a0545f')
    d.line((3, 1, 86, 1), fill='#ebdab1')
    label(im, 'QUITAR SOMBRERO', (45, 5), 84, '#f7e7c9')
    return im


def assets():
    im = panel(); files = {}; providers = []; advances = {START: -32, END: 32}
    for i, (box, ascent) in enumerate((((0, 0, 224, SPLIT), 53), ((0, SPLIT, 224, 280), -3))):
        part = im.crop(box); path = f'font/cosmeticos/gorros_{i}.png'
        files['assets/astral/textures/'+path] = png(part)
        providers.append(dict(type='bitmap', file='astral:'+path, height=part.height, ascent=ascent, chars=[GLYPHS[i*2]]))
        advances[GLYPHS[i*2+1]] = -(part.getbbox()[2]+1)
    providers.append(dict(type='space', advances=advances))
    button = clear_button()
    for i in range(5):
        name = f'quitar_sombrero_{i}'
        files[f'assets/astral/textures/item/cosmeticos/{name}.png'] = png(button.crop((i*18, 0, i*18+18, 18)))
        files[f'assets/astral/models/cosmeticos/{name}.json'] = json.dumps({'parent': 'minecraft:item/generated', 'gui_light': 'front',
            'textures': {'layer0': f'astral:item/cosmeticos/{name}'}, 'display': {'gui': {'scale': [1.125, 1.125, 1]}}}).encode()
        files[f'assets/astral/items/cosmeticos/{name}.json'] = json.dumps({'oversized_in_gui': True,
            'model': {'type': 'minecraft:model', 'model': f'astral:cosmeticos/{name}'}}).encode()
    # Reserva publica de los gorros agrandados: el privado los reemplaza por el modelo real.
    from cosmeticos_catalogo import HATS
    for key, *_ in HATS:
        files[f'assets/astral/items/cosmeticos/menu_sombrero_{key}.json'] = json.dumps(
            {'model': {'type': 'minecraft:model', 'model': 'minecraft:item/leather_helmet'}}).encode()
    return files, providers


def private_menu_models(files):
    """Circuito privado: copia de cada gorro con la vista de inventario agrandada."""
    from cosmeticos_catalogo import HATS
    out = {}
    for key, *_ in HATS:
        ref = json.loads(files[f'assets/astral/items/cosmeticos/sombrero_{key}.json'])['model']['model']
        ns, rel = ref.split(':', 1)
        base = json.loads(files[f'assets/{ns}/models/{rel}.json'])
        gui = dict(base.get('display', {}).get('gui', {'rotation': [30, 225, 0], 'scale': [0.625]*3}))
        gui['scale'] = [round(v*MENU_SCALE, 4) for v in gui.get('scale', [0.625]*3)]
        name = f'menu_sombrero_{key}'
        out[f'assets/astral/models/cosmeticos/{name}.json'] = json.dumps({'parent': ref, 'display': {'gui': gui}}).encode()
        out[f'assets/astral/items/cosmeticos/{name}.json'] = json.dumps({'oversized_in_gui': True,
            'model': {'type': 'minecraft:model', 'model': f'astral:cosmeticos/{name}'}}).encode()
    return out


def preview(path, hats=None):
    im = Image.new('RGBA', SIZE, '#1a2531'); im.alpha_composite(panel())
    im.alpha_composite(clear_button(), (67, 147))
    from cosmeticos_ui import nav_icon
    im.alpha_composite(nav_icon('back'), slot_xy(BACK_SLOT)); im.alpha_composite(nav_icon('gacha'), slot_xy(GACHA_SLOT))
    for slot, hat in zip(HAT_SLOTS, hats or []):
        x, y = slot_xy(slot)
        im.alpha_composite(hat, (x+9-hat.width//2, y+9-hat.height//2))
    text(im, 'Inventario', (86, 169), color='#383c40')
    Path(path).write_bytes(png(im.resize((672, 840), Image.Resampling.NEAREST)))
