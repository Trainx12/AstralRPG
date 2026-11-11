"""Menu Astral (Estrella del slot 9): marco de Gemini e iconos pintados, sobre la grilla vanilla."""
import json
from pathlib import Path
from PIL import Image, ImageDraw
from escape_menu import text
from services_ui import png, SIZE, SPLIT, outlined, illustration
from market_ui import band_color

ROOT = Path(__file__).resolve().parent
FRAME = ('menu2', (214, 640, 1582, 2147))
FILL, EDGE, ACCENT = '#1c1526', '#c9a14f', '#b48cf0'
TITLE_Y = 35
START, END = '', ''
GLYPHS = tuple(chr(0xea10 + i) for i in range(4))
# Mismo orden que menus.principal_menu: casillas 10-16 y 19-25.
KEYS = ('bazar', 'minas', 'mazmorras', 'expediciones', 'portales', 'parkour', 'arenas',
        'misiones', 'mascotas', 'cosmeticos', 'skills', 'guia', 'comandos', 'spawn',
        'fragmentos', 'duelos')
SLOTS = tuple(range(10, 17)) + tuple(range(19, 26)) + (30, 32)
ICON_ART = dict(bosque='expediciones', fragmentos='skills', tienda='bazar', peluches='mascotas',
                subastas='bazar', vender='bazar', intercambio='bazar', gacha_rpg='skills',
                gacha_monturas='mascotas', gacha_cosmeticos='cosmeticos', duelos='arenas')


def title():
    return '&f' + START + ''.join(GLYPHS) + END


def icon(key):
    """Icono de Gemini en 18x18 (el modelo lo dibuja a escala 1.125 sobre la casilla)."""
    im = illustration('menu_' + ICON_ART.get(key, key)).resize((18, 18), Image.Resampling.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 17, 17), outline=EDGE)
    return im


def panel():
    art, (l, t, r, b) = FRAME
    source = Image.open(ROOT / f'pack-source/ref/{art}-frame.png').convert('RGBA')
    sx, sy = [0, l, r, source.width], [0, t, b, source.height]
    dx, dy = [0, 24, 200, 224], [0, 56, 258, 280]
    im = Image.new('RGBA', SIZE)
    for row in range(3):
        for col in range(3):
            piece = source.crop((sx[col], sy[row], sx[col + 1], sy[row + 1]))
            im.alpha_composite(piece.resize((dx[col + 1] - dx[col], dy[row + 1] - dy[row]), Image.Resampling.NEAREST), (dx[col], dy[row]))
    outlined(im, 'MENU ASTRAL', (112, TITLE_Y))
    d = ImageDraw.Draw(im)
    d.rectangle((24, 56, 199, 258), fill=FILL)
    # Vitrina de dos filas de iconos, con un brillo de estrellas a los costados.
    d.rectangle((46, 73, 177, 148), fill='#140f1d', outline='#6c5a3a')
    for cx, cy in ((46, 73), (177, 73), (46, 148), (177, 148)):
        d.polygon(((cx, cy - 2), (cx + 2, cy), (cx, cy + 2), (cx - 2, cy)), fill=EDGE)
    for slot in (*SLOTS, 4, 49):
        x, y = 31 + slot % 9 * 18, 57 + slot // 9 * 18
        d.rectangle((x, y, x + 17, y + 17), outline=EDGE)
        d.rectangle((x + 1, y + 1, x + 16, y + 16), fill=(0, 0, 0, 0))
    d.rectangle((31, 168, 192, 177), fill=band_color(EDGE))
    d.line((31, 167, 192, 167), fill=EDGE); d.line((31, 178, 192, 178), fill=EDGE)
    for row in (*range(3), 4):
        for col in range(9):
            x, y = 31 + col * 18, 179 + row * 18 if row < 3 else 237
            d.rectangle((x, y, x + 17, y + 17), outline=EDGE)
            d.rectangle((x + 1, y + 1, x + 16, y + 16), fill=(0, 0, 0, 0))
    return im


def assets():
    files, providers = {}, []
    advances = {START: -32, END: 32}
    a, b, c, d = GLYPHS
    im = panel()
    for n, (part, ascent, char, rewind) in enumerate(((im.crop((0, 0, 224, SPLIT)), 53, a, b), (im.crop((0, SPLIT, 224, 280)), -3, c, d))):
        resource = f'font/menu/principal_{n}.png'
        files['assets/astral/textures/' + resource] = png(part)
        providers.append({'type': 'bitmap', 'file': 'astral:' + resource, 'height': part.height, 'ascent': ascent, 'chars': [char]})
        advances[rewind] = -(part.getbbox()[2] + 1)
    providers.append({'type': 'space', 'advances': advances})
    for key in KEYS:
        name = 'icon_' + key
        files[f'assets/astral/textures/item/menu/{name}.png'] = png(icon(key))
        files[f'assets/astral/models/menu/{name}.json'] = json.dumps({'parent': 'minecraft:item/generated', 'gui_light': 'front',
            'textures': {'layer0': f'astral:item/menu/{name}'}, 'display': {'gui': {'scale': [1.125, 1.125, 1]}}}).encode()
        files[f'assets/astral/items/menu/{name}.json'] = json.dumps({'oversized_in_gui': True,
            'model': {'type': 'minecraft:model', 'model': f'astral:menu/{name}'}}).encode()
    return files, providers


def preview(folder):
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    im = Image.new('RGBA', SIZE, '#22242a'); im.alpha_composite(panel())
    for key, slot in zip(KEYS, SLOTS):
        im.alpha_composite(icon(key), (31 + slot % 9 * 18, 57 + slot // 9 * 18))
    text(im, 'Inventario', (86, 169), color='#383c40')
    (folder / 'menu-astral.png').write_bytes(png(im.resize((672, 840), Image.Resampling.NEAREST)))


if __name__ == '__main__':
    preview(ROOT.parent / 'build/Servicios-preview')
