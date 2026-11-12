"""Mi companero: una pantalla por mascota, en formato ancho como la referencia del dueno.

El retrato grande va a la izquierda, FUERA de la grilla del cofre (el marco se extiende E px a la
izquierda); las 9 columnas quedan para nivel, experiencia y mejoras. Arte de Gemini (noviembre 2026):
marco companero2, retratos retrato_<mascota> e iconos mejora_<efecto> en pack-source/ref/gemini.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from escape_menu import text
from services_ui import png, SPLIT, outlined, header, tall, glyph_parts, illustration
from market_ui import band_color
from adventure_ui import label
from mobs.mascotas import MASCOTAS as ALL_PETS
MASCOTAS = ALL_PETS
# El render de terceros se inyecta solo al construir la entrega privada.
PORTRAITS = {}

ROOT = Path(__file__).resolve().parent
E = 88                          # ancho extra a la izquierda para el retrato
W = 224 + E                     # ancho del marco
BOTTOM = 34                     # alto del borde de abajo
SIZE = (W, 56 + 202 + BOTTOM)
FILL, EDGE, GOLD = '#182c2d', '#c9a14f', '#e2b85a'
FRAME = ('companero2', (215, 430, 1813, 1699))
TITLE, TITLE_Y, SUB_FRAC = 'MI COMPANERO', 22, .80   # cartel grande y cinta del nombre (fraccion del encabezado)
START, END = '', ''
# Minecraft no dibuja glifos de mas de 256 px de ancho: cada parte va en dos mitades (izquierda y derecha).
HALF = W // 2
GLYPHS = {pid: tuple(chr(0xeb10 + i * 8 + j) for j in range(8)) for i, pid in enumerate(MASCOTAS)}

LEVEL_SLOTS = (0, 1, 2, 3)      # cartel "Nivel X / 30"
XP_SLOTS = (4, 5, 6, 7, 8)      # "Experiencia" y la barra
PERK_ROWS = (1, 2, 3, 4)        # una fila por mejora; el estado va en la columna 8
PERK_LEVELS = (1, 10, 20, 30)
INVOKE_SLOTS = (46, 47, 48)
REST_SLOTS = (49, 50, 51)
# (icono, texto corto, segunda linea opcional) por mejora; la de nivel 30 es comun a todas.
PERKS = {
    'lobo': (('fuerza', 'Fuerza I', ''), ('velocidad', 'Velocidad I', ''), ('resistencia', 'Resistencia I', '')),
    'cuervo': (('vision', 'Vision nocturna', 'Marca enemigos cercanos'), ('suerte', 'Suerte I', ''), ('velocidad', 'Velocidad I', '')),
    'golem': (('resistencia', 'Resistencia I', ''), ('regeneracion', 'Regeneracion I', ''), ('absorcion', 'Absorcion', '2 corazones extra')),
    'zorro': (('velocidad', 'Velocidad I', ''), ('salto', 'Salto I', ''), ('velocidad2', 'Velocidad II', '')),
    'dragon': (('anti_fuego', 'Resistencia al fuego', ''), ('fuerza', 'Fuerza I', ''), ('prisa', 'Prisa I', '')),
    'fenix': (('rescate', 'Rescate cada 10 min', 'Te salva con poca vida'), ('rescate', 'Rescate cada 7 min', ''), ('rescate', 'Rescate cada 5 min', '')),
}
EVOLUTION = ('evolucion', 'Evolucion visual', '')
from terceros import PETS
_EFFECT_ICONS = dict(slow_falling='salto', regeneration='regeneracion', luck='suerte',
    resistance='resistencia', strength='fuerza', haste='prisa', speed='velocidad',
    night_vision='vision', jump_boost='salto', fire_resistance='anti_fuego',
    absorption='absorcion', water_breathing='vision')
for _pid, *_, _effects in PETS:
    _lines = {'fire_resistance':('Resistencia','al fuego'),
              'water_breathing':('Respiracion','acuatica'),
              'absorption':('Absorcion','2 corazones extra')}
    PERKS[_pid] = tuple((_EFFECT_ICONS[e], *_lines.get(e,(caption.lstrip('+ '),'')))
                       for e, caption in zip(_effects, MASCOTAS[_pid]['texto']))


def slot_xy(slot):
    return 31 + E + slot % 9 * 18, 57 + slot // 9 * 18


def title(pid):
    # Por parte: mitad izquierda, salto a la mitad derecha, mitad derecha, vuelta al origen.
    return '&f' + START + ''.join(GLYPHS[pid]) + END


def icon(name, size=16):
    return illustration('mejora_' + name).resize((size, size), Image.Resampling.LANCZOS)


def frame():
    """Marco sin encabezado: columnas laterales angostas y el borde de abajo con su canto real."""
    art, (l, t, r, b) = FRAME
    src = Image.open(ROOT / f'pack-source/ref/{art}-frame.png').convert('RGBA')
    scale = (W - 48) / (r - l)
    keep = round(BOTTOM / scale)        # del pie se usa la franja de abajo (no se aplasta)
    sx = [0, l, r, src.width]
    rows = [((t, b), (56, 258)), ((src.height - keep, src.height), (258, SIZE[1]))]
    im = Image.new('RGBA', SIZE)
    for (y0, y1), (d0, d1) in rows:
        for (x0, x1), (e0, e1) in zip(((sx[0], sx[1]), (sx[1], sx[2]), (sx[2], sx[3])), ((0, 24), (24, W - 24), (W - 24, W))):
            im.alpha_composite(src.crop((x0, y0, x1, y1)).resize((e1 - e0, d1 - d0), Image.Resampling.NEAREST), (e0, d0))
    return im


def panel(pid):
    d_ = MASCOTAS[pid]
    im = frame(); d = ImageDraw.Draw(im)
    d.rectangle((24, 56, W - 25, 257), fill=FILL)
    # Retrato grande a la izquierda (fuera de la grilla), con marco dorado.
    x0, y0, x1, y1 = 29, 57, 24 + E - 3, 165
    if pid in PORTRAITS:
        art = Image.new('RGBA', (160, 220), '#10221f')
        portrait = ImageOps.contain(PORTRAITS[pid], (150, 210), Image.Resampling.LANCZOS)
        art.alpha_composite(portrait, ((160-portrait.width)//2, (220-portrait.height)//2))
    elif MASCOTAS[pid]['n'] <= 6:
        art = illustration('retrato_' + pid)
    else:
        # Reserva propia, sin pixeles licenciados ni retrato de otra mascota.
        art = Image.new('RGBA', (80, 110), '#10221f')
        art.alpha_composite(paw(MASCOTAS[pid]['color']).resize((56,56), Image.Resampling.NEAREST), (12,27))
    w, h = x1 - x0 - 3, y1 - y0 - 3
    ch = min(art.height, round(art.width * h / w)); cw = round(ch * w / h)
    left = (art.width - cw) // 2; top = (art.height - ch) // 2
    im.alpha_composite(art.crop((left, top, left + cw, top + ch)).resize((w, h), Image.Resampling.LANCZOS), (x0 + 2, y0 + 2))
    d.rectangle((x0, y0, x1, y1), outline=GOLD); d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), outline='#3d2c12')
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        d.polygon(((cx, cy - 2), (cx + 2, cy), (cx, cy + 2), (cx - 2, cy)), fill='#7fe0d8')
    # Debajo del retrato, al costado del inventario.
    cx = (x0 + x1) // 2
    for i, line in enumerate(('Bonus solo', 'en mazmorras')):
        label(im, line, (cx, 196 + i * 10), x1 - x0, '#9fc7b8')
    d.polygon(((cx, 186), (cx + 3, 189), (cx, 192), (cx - 3, 189)), fill=GOLD)
    # Filas de mejoras: icono, "Nv. X - mejora" (y una segunda linea si hace falta), casilla de estado.
    for row, level, (ic, caption, sub) in zip(PERK_ROWS, PERK_LEVELS, list(PERKS[pid]) + [EVOLUTION]):
        bx, by = slot_xy(row * 9)
        evo = level == 30
        d.rectangle((bx, by, bx + 161, by + 17), fill='#2a2416' if evo else '#10221f', outline=GOLD if evo else '#4f6550')
        im.alpha_composite(icon(ic), (bx + 1, by + 1))
        caption = f'Nv. {level} - {caption}'
        color = '#ffe08a' if evo else '#f3e4b8'
        if sub:
            label(im, caption, (bx + 81, by + 1), 122, color)
            label(im, sub, (bx + 81, by + 9), 122, '#9fc7b8')
        else:
            label(im, caption, (bx + 81, by + 5), 122, color)
    # Inventario del jugador (corrido E px a la derecha, como el cofre).
    d.rectangle((31 + E, 168, 192 + E, 177), fill=band_color(EDGE))
    d.line((31 + E, 167, 192 + E, 167), fill=EDGE); d.line((31 + E, 178, 192 + E, 178), fill=EDGE)
    for row in (*range(3), 4):
        for col in range(9):
            x, y = 31 + E + col * 18, 179 + row * 18 if row < 3 else 237
            d.rectangle((x, y, x + 17, y + 17), outline='#546a57')
            d.rectangle((x + 1, y + 1, x + 16, y + 16), fill=(0, 0, 0, 0))
    return im


def full(pid, image=None):
    head = header(FRAME[0], FRAME[1], TITLE, TITLE_Y, FILL, width=W)
    sub_y = round(SUB_FRAC * head.height) - 4
    outlined(head, MASCOTAS[pid]['nombre'], (W // 2, sub_y), color='#f3e4b8', outline='#0b1a19')
    return tall(panel(pid) if image is None else image, head), head.height


def level_plaque(level):
    im = Image.new('RGBA', (72, 18), FILL); d = ImageDraw.Draw(im)
    d.rectangle((2, 1, 69, 16), fill='#1d2a1e', outline=GOLD); d.rectangle((3, 2, 68, 15), outline='#3d2c12')
    for x, s in ((1, 1), (70, -1)):          # laureles
        for k in range(3):
            d.point((x + s * (1 + k), 6 + k * 3), fill='#9bbf4a'); d.point((x + s * (2 + k), 5 + k * 3), fill='#9bbf4a')
    label(im, f'Nivel {level} / 30', (36, 5), 62, '#ffe08a')
    return im


def xp_strip(states):
    """Barra de 5 casillas con la etiqueta 'Experiencia'; states: 0 vacio, 1 medio, 2 lleno por casilla."""
    im = Image.new('RGBA', (90, 18), FILL); d = ImageDraw.Draw(im)
    text(im, 'Experiencia', (31, 0), color='#f3e4b8')
    d.rectangle((1, 10, 88, 16), fill='#0b1715', outline=GOLD)
    for j, state in enumerate(states):
        if state:
            x0 = 2 + j * 17; x1 = x0 + (16 if state == 2 else 8)
            d.rectangle((x0, 11, min(x1, 87), 15), fill='#3fd6e0'); d.line((x0, 12, min(x1, 87), 12), fill='#bff6f6')
    return im


def xp_tile(index, state):
    states = [0] * 5; states[index] = state
    return xp_strip(states).crop((index * 18, 0, index * 18 + 18, 18))


def perk_state(ok):
    im = Image.new('RGBA', (18, 18), '#10221f'); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 17, 17), outline='#4f6550')
    if ok:
        d.rectangle((2, 2, 15, 15), fill='#1f3a1c', outline='#7fe07a')
        d.line((5, 9, 8, 12), fill='#9ff58f', width=2); d.line((8, 12, 13, 5), fill='#9ff58f', width=2)
    else:
        d.rectangle((5, 8, 12, 14), fill=GOLD, outline='#5a4320'); d.arc((6, 3, 11, 10), 180, 360, fill='#f0dca0'); d.point((8, 11), fill='#3a2a10')
    return im


def button(caption, fill, outline, art=None):
    im = Image.new('RGBA', (54, 18), fill); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 53, 17), outline=outline); d.rectangle((1, 1, 52, 16), outline='#0b1715')
    d.line((2, 2, 51, 2), fill='#ffffff50')
    if art:
        im.alpha_composite(art, (3, 2))
        label(im, caption, (33, 5), 32, '#ffffff')
    else:
        label(im, caption, (27, 5), 48, '#ffffff')
    return im


def paw(color):
    im = Image.new('RGBA', (14, 14)); d = ImageDraw.Draw(im)
    d.ellipse((4, 6, 10, 12), fill=color)
    for x, y in ((2, 4), (5, 1), (9, 1), (12, 4)):
        d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=color)
    return im


def bed(color):
    im = Image.new('RGBA', (14, 14)); d = ImageDraw.Draw(im)
    d.rectangle((1, 7, 12, 10), fill=color); d.rectangle((1, 4, 2, 12), fill=color); d.rectangle((11, 9, 12, 12), fill=color)
    d.rectangle((3, 5, 6, 7), fill='#ffffff')
    return im


def nav(kind):
    im = Image.new('RGBA', (18, 18), '#10221f'); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 17, 17), outline=GOLD)
    if kind == 'back':
        d.polygon(((3, 9), (8, 4), (8, 7), (14, 7), (14, 11), (8, 11), (8, 14)), fill=GOLD)
    else:
        d.rectangle((1, 1, 16, 16), fill='#6b1f1f', outline='#c96b5a')
        d.line((5, 5, 12, 12), fill='#ffffff', width=2); d.line((12, 5, 5, 12), fill='#ffffff', width=2)
    return im


def assets():
    files, providers = {}, []
    advances = {START: -(32 + E), END: 32 + E}
    for pid in MASCOTAS:
        im, head_height = full(pid)
        chars = GLYPHS[pid]
        for n, (part, ascent) in enumerate(glyph_parts(im, head_height)):
            left_char, jump, right_char, back = chars[n * 4:n * 4 + 4]
            for side, char, box in (('a', left_char, (0, 0, HALF, part.height)), ('b', right_char, (HALF, 0, W, part.height))):
                piece = part.crop(box)
                path = f'font/companero/{pid}_{n}{side}.png'
                files['assets/astral/textures/' + path] = png(piece)
                providers.append({'type': 'bitmap', 'file': 'astral:' + path, 'height': piece.height, 'ascent': ascent, 'chars': [char]})
                width = piece.getbbox()[2] + 1
                if side == 'a':
                    advances[jump] = HALF - width        # deja el cursor en la mitad del marco
                else:
                    advances[back] = -(HALF + width)     # vuelve al borde izquierdo
    providers.append({'type': 'space', 'advances': advances})

    def model(name, image):
        files[f'assets/astral/textures/item/companero/{name}.png'] = png(image)
        files[f'assets/astral/models/companero/{name}.json'] = json.dumps({'parent': 'minecraft:item/generated', 'gui_light': 'front',
            'textures': {'layer0': f'astral:item/companero/{name}'}, 'display': {'gui': {'scale': [1.125, 1.125, 1]}}}).encode()
        files[f'assets/astral/items/companero/{name}.json'] = json.dumps({'oversized_in_gui': True,
            'model': {'type': 'minecraft:model', 'model': f'astral:companero/{name}'}}).encode()

    def tiles(name, image):
        for i in range(image.width // 18):
            model(f'{name}_{i}', image.crop((i * 18, 0, i * 18 + 18, 18)))
    for level in range(1, 31):
        tiles(f'nivel_{level}', level_plaque(level))
    for j in range(5):
        for state in range(3):
            model(f'xp_{j}_{state}', xp_tile(j, state))
    model('ok', perk_state(True)); model('lock', perk_state(False))
    tiles('invocar', button('INVOCAR', '#1f6b6a', '#7fe0d8'))
    tiles('descansar', button('DESCANSAR', '#6b5a24', GOLD))
    model('volver', nav('back')); model('cerrar', nav('close'))
    return files, providers


def preview(folder, pid, level, progress):
    im = Image.new('RGBA', SIZE, '#202c29'); im.alpha_composite(panel(pid))
    im.alpha_composite(level_plaque(level), slot_xy(LEVEL_SLOTS[0]))
    states = [2 if level >= 30 or progress >= 5 * (j + 1) else (1 if progress >= 5 * j + 3 else 0) for j in range(5)]
    im.alpha_composite(xp_strip(states), slot_xy(XP_SLOTS[0]))
    for row, need in zip(PERK_ROWS, PERK_LEVELS):
        im.alpha_composite(perk_state(level >= need), slot_xy(row * 9 + 8))
    im.alpha_composite(button('INVOCAR', '#1f6b6a', '#7fe0d8'), slot_xy(INVOKE_SLOTS[0]))
    im.alpha_composite(button('DESCANSAR', '#6b5a24', GOLD), slot_xy(REST_SLOTS[0]))
    im.alpha_composite(nav('back'), slot_xy(45)); im.alpha_composite(nav('close'), slot_xy(53))
    text(im, 'Inventario', (86 + E, 169), color='#383c40')
    im, _ = full(pid, im)
    out = Image.new('RGBA', im.size, '#202c29'); out.alpha_composite(im)
    (Path(folder) / f'mascota-{pid}.png').write_bytes(png(out.resize((out.width * 3, out.height * 3), Image.Resampling.NEAREST)))


if __name__ == '__main__':
    folder = ROOT.parent / 'build/Servicios-preview'
    for pid, level, progress in (('lobo', 12, 13), ('cuervo', 12, 13), ('golem', 12, 13), ('zorro', 12, 13), ('dragon', 12, 13), ('fenix', 30, 0)):
        preview(folder, pid, level, progress)
