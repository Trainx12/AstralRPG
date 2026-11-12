"""Minijuegos Astrales: marco de Gemini (12/11/2026) y ocho tarjetas ilustradas.

Cada tarjeta ocupa 2x2 casillas: columnas (0,1) (2,3) (5,6) (7,8), filas 0-1 y 2-3.
Fila 4: aviso del inventario. Fila 5: lobby (45) y cerrar (53).
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw
from services_ui import png, SIZE, SPLIT, header, tall, glyph_parts, illustration
from market_ui import band_color
from adventure_ui import label
from escape_menu import text

ROOT = Path(__file__).resolve().parent
FRAME = ('minijuegos', (247, 352, 2647, 1155))
FILL, EDGE = '#1c1426', '#c9a14f'
START, END = '', ''          # mismos saltos (-32/+32) que el santuario de mascotas
GLYPHS = tuple(chr(0xed44+i) for i in range(4))
GAMES = ('spiral', 'spiral2', 'paradise3', 'colorescape', 'magmarun', 'batallanaval', 'dropper_facil', 'dropper_h4rs')
LABELS = dict(spiral='SPIRAL', spiral2='SPIRAL2', paradise3='ISLAS', colorescape='COLOR',
              magmarun='MAGMA', batallanaval='NAVAL', dropper_facil='POZO', dropper_h4rs='VORTICE')
COLS = ((0, 1), (2, 3), (5, 6), (7, 8))
CARD_SLOTS = {g: [r*9+c for r in ((0, 1) if i < 4 else (2, 3)) for c in COLS[i % 4]] for i, g in enumerate(GAMES)}
LOBBY_SLOT, CLOSE_SLOT = 45, 53


def title():
    return '&f'+START+''.join(GLYPHS)+END


def slot_xy(slot):
    return 31+slot % 9*18, 57+slot//9*18


def card(game):
    art = illustration('minijuego_'+game)
    side = min(art.size)
    art = art.crop(((art.width-side)//2, (art.height-side)//2, (art.width+side)//2, (art.height+side)//2))
    im = art.resize((144, 144), Image.Resampling.BOX).resize((36, 36), Image.Resampling.LANCZOS)
    im.alpha_composite(Image.new('RGBA', (36, 11), (10, 6, 16, 190)), (0, 25))
    label(im, LABELS[game], (18, 26), 34, '#fff0cd')
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 35, 35), outline=EDGE); d.rectangle((1, 1, 34, 34), outline='#3b2a14')
    return im


def panel():
    art, (l, t, r, b) = FRAME
    src = Image.open(ROOT/f'pack-source/ref/{art}-frame.png').convert('RGBA')
    sx, sy = [0, l, r, src.width], [0, t, b, src.height]
    dx, dy = [0, 24, 200, 224], [0, 56, 258, SIZE[1]]
    im = Image.new('RGBA', SIZE)
    for row in range(3):
        for col in range(3):
            piece = src.crop((sx[col], sy[row], sx[col+1], sy[row+1]))
            im.alpha_composite(piece.resize((dx[col+1]-dx[col], dy[row+1]-dy[row]), Image.Resampling.LANCZOS), (dx[col], dy[row]))
    d = ImageDraw.Draw(im); d.rectangle((24, 56, 199, 258), fill=FILL)
    for slots in CARD_SLOTS.values():
        x, y = slot_xy(slots[0]); d.rectangle((x, y, x+35, y+35), fill=(0, 0, 0, 0))
    # Aviso en la fila 4 y botones de la fila 5 (los iconos son items reales).
    d.rectangle((31, 129, 192, 144), fill='#2a1f38', outline=EDGE)
    label(im, 'Tu inventario vuelve al salir', (112, 133), 156, '#e9dcff')
    for slot in (LOBBY_SLOT, CLOSE_SLOT):
        x, y = slot_xy(slot)
        d.rectangle((x, y, x+17, y+17), outline=EDGE); d.rectangle((x+1, y+1, x+16, y+16), fill=(0, 0, 0, 0))
    d.rectangle((31, 168, 192, 177), fill=band_color(EDGE))
    d.line((31, 167, 192, 167), fill=EDGE); d.line((31, 178, 192, 178), fill=EDGE)
    for row in (*range(3), 4):
        for col in range(9):
            x, y = 31+col*18, 179+row*18 if row < 3 else 237
            d.rectangle((x, y, x+17, y+17), outline='#5a4d6b')
            d.rectangle((x+1, y+1, x+16, y+16), fill=(0, 0, 0, 0))
    return im


def full_panel(image=None):
    head = header(FRAME[0], FRAME[1], 'MINIJUEGOS', 30, FILL)
    return tall(panel() if image is None else image, head), head.height


def assets():
    files, providers = {}, []; advances = {}
    a, b, c, d = GLYPHS; im, hh = full_panel()
    for n, ((part, ascent), char, rewind) in enumerate(zip(glyph_parts(im, hh), (a, c), (b, d))):
        path = f'font/minijuegos/menu_{n}.png'
        files['assets/astral/textures/'+path] = png(part)
        providers.append({'type': 'bitmap', 'file': 'astral:'+path, 'height': part.height, 'ascent': ascent, 'chars': [char]})
        advances[rewind] = -(part.getbbox()[2]+1)
    providers.append({'type': 'space', 'advances': advances})
    for game in GAMES:
        image = card(game)
        for i in range(4):
            col, row = i % 2, i//2
            name = f'{game}_{i}'
            files[f'assets/astral/textures/item/minijuegos/{name}.png'] = png(image.crop((col*18, row*18, col*18+18, row*18+18)))
            files[f'assets/astral/models/minijuegos/{name}.json'] = json.dumps({'parent': 'minecraft:item/generated', 'gui_light': 'front',
                'textures': {'layer0': f'astral:item/minijuegos/{name}'}, 'display': {'gui': {'scale': [1.125, 1.125, 1]}}}).encode()
            files[f'assets/astral/items/minijuegos/{name}.json'] = json.dumps({'oversized_in_gui': True,
                'model': {'type': 'minecraft:model', 'model': f'astral:minijuegos/{name}'}}).encode()
    return files, providers


def preview(path):
    im = Image.new('RGBA', SIZE, '#252a28'); im.alpha_composite(panel())
    for game, slots in CARD_SLOTS.items():
        im.alpha_composite(card(game), slot_xy(slots[0]))
    text(im, 'Inventario', (86, 169), color='#383c40')
    im, _ = full_panel(im)
    out = Image.new('RGBA', im.size, '#252a28'); out.alpha_composite(im)
    Path(path).write_bytes(png(out.resize((out.width*3, out.height*3), Image.Resampling.NEAREST)))


if __name__ == '__main__':
    preview(ROOT.parent/'build/Servicios-preview/minijuegos.png')
