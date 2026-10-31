"""Interfaz exclusiva del Cronista: reloj azul, tarjetas y botones legibles.

No sustituye ninguna textura de inventario vanilla. Los menús referencian
glifos privados e item_model con namespace astral:cronista.
"""
import io
import json
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw
from escape_menu import text
from misiones import CHAPTERS, DAILIES

ROOT = Path(__file__).resolve().parent
ART = ROOT / 'pack-source/ref/cronista-clockwork.png'
TITLES = ['Historia', 'Diaria facil', 'Diaria media', 'Diaria dificil', 'Premio de historia']
STORY_REWARDS = [300, 500, 1000, 1500, 2000, 2500, 3000, 5000, 10000]


def png(im):
    buffer = io.BytesIO()
    im.save(buffer, 'PNG')
    return buffer.getvalue()


def panel(rewards=False):
    source = Image.open(ART).convert('RGBA')
    im = Image.new('RGBA', (208, 286))
    im.alpha_composite(source.resize(im.size, Image.Resampling.NEAREST))
    body = Image.new('RGBA', (176, 222), '#071a2d')
    d = ImageDraw.Draw(body)
    # Las posiciones son las del cofre de 54 slots y su inventario inferior.
    for row in range(6):
        for col in range(9):
            x, y = 7 + col * 18, 17 + row * 18
            d.rectangle((x, y, x + 17, y + 17), fill='#102e48', outline='#28516b')
            d.line((x + 1, y + 16, x + 16, y + 16), fill='#061525')
    d.rectangle((7, 128, 168, 137), fill='#8cb4c6')
    for row in range(3):
        for col in range(9):
            x, y = 7 + col * 18, 139 + row * 18
            d.rectangle((x, y, x + 17, y + 17), fill='#102b40', outline='#3c6177')
    for col in range(9):
        x = 7 + col * 18
        d.rectangle((x, 197, x + 17, 214), fill='#102b40', outline='#78919b')
    # Los titulos se dibujan sobre los items. Las ventanas transparentes
    # permiten ver modelos, cantidades y los objetos reales del jugador.
    for row in range(6):
        for col in range(9):
            x, y = 8 + col * 18, 18 + row * 18
            d.rectangle((x, y, x + 15, y + 15), fill=(0, 0, 0, 0))
    if not rewards:
        d.rectangle((7, 35, 168, 88), fill=(0, 0, 0, 0))
        d.rectangle((43, 89, 132, 106), fill=(0, 0, 0, 0))
    for row in range(3):
        for col in range(9):
            x, y = 8 + col * 18, 140 + row * 18
            d.rectangle((x, y, x + 15, y + 15), fill=(0, 0, 0, 0))
    for col in range(9):
        x = 8 + col * 18
        d.rectangle((x, 198, x + 15, 213), fill=(0, 0, 0, 0))
    im.paste(body, (16, 48))
    return im


@lru_cache(maxsize=1)
def glyph_widths():
    chars = json.loads((ROOT / 'pack-source/vanilla-base/font/ascii.json').read_text(encoding='utf-8'))['chars']
    font = Image.open(ROOT / 'pack-source/vanilla-base/font/ascii.png').convert('RGBA')
    widths = {}
    for row, line in enumerate(chars):
        for col, char in enumerate(line):
            box = font.crop((col * 8, row * 8, col * 8 + 8, row * 8 + 8)).getbbox()
            widths[char] = box[2] if box else 3
    return widths


def width(caption):
    return sum(glyph_widths().get(char, 5) + 1 for char in caption) - 1


def wrap(caption, limit=150):
    lines = []
    line = ''
    for word in caption.split():
        candidate = (line + ' ' + word).strip()
        if line and width(candidate) > limit:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def card(name, objective, amount, status):
    im = Image.new('RGBA', (162, 54), '#102a43')
    d = ImageDraw.Draw(im)
    colors = {'available': '#f5d881', 'active': '#75edec', 'done': '#a0acb6'}
    labels = {'available': 'SIN ACEPTAR', 'active': 'ACTIVA', 'done': 'COBRADA'}
    d.rectangle((0, 0, 161, 53), outline='#4b92ad')
    d.line((1, 10, 160, 10), fill='#315b76')
    text(im, name.upper(), (81, 2), color='#f6e4b8')
    lines = wrap(objective)
    if len(lines) > 4:
        raise ValueError(f'Objetivo demasiado largo para la tarjeta: {name}: {lines}')
    for index, line in enumerate(lines):
        text(im, line, (81, 13 + index * 8), color='#d8eff7')
    d.rectangle((1, 46, 160, 52), fill='#081c30')
    text(im, labels[status], (40, 46), color=colors[status])
    text(im, f'{amount}$', (135, 46), color='#ffe292')
    return im


def action_button(caption, color):
    im = Image.new('RGBA', (90, 18), '#061522')
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 89, 17), outline='#dbca83')
    d.rectangle((1, 1, 88, 16), fill=color, outline='#6bb6c3')
    d.line((2, 2, 87, 2), fill='#b9eef0')
    text(im, caption, (45, 5), color='#ffffff')
    return im


def clock(color='#36c4e6', marker=0):
    im = Image.new('RGBA', (16, 16))
    d = ImageDraw.Draw(im)
    d.ellipse((1, 1, 14, 14), fill='#bd944e', outline='#392c1a')
    d.ellipse((3, 3, 12, 12), fill='#10283e', outline=color)
    for x, y in [(7, 3), (12, 7), (7, 12), (3, 7)]:
        d.point((x, y), fill='#ecdfb7')
    d.line((7, 4, 7, 8, 10, 8), fill=color, width=1)
    if marker:
        d.rectangle((11, 10, 15, 15), fill='#071a2d')
        for x in range(marker):
            d.line((11 + x * 2, 11, 11 + x * 2, 14), fill=color)
    return im


def assets():
    files, providers = {}, []

    def model(name, image):
        tex = f'astral:cronista/{name}'
        files[f'assets/astral/textures/cronista/{name}.png'] = png(image)
        definition = {'parent': 'minecraft:item/generated', 'gui_light': 'front', 'textures': {'layer0': tex},
                      'display': {'gui': {'scale': [image.width / 16, image.height / 16, 1]}}}
        files[f'assets/astral/models/cronista/{name}.json'] = json.dumps(definition).encode('utf-8')
        files[f'assets/astral/items/cronista/{name}.json'] = json.dumps({'model': {
            'type': 'minecraft:model', 'model': f'astral:cronista/{name}'}}).encode('utf-8')

    def tiles(name, image):
        # Cada slot dibuja su fragmento a escala 1.125. Evita el limite de
        # escala de los modelos y conserva todos los puntos de clic.
        columns = image.width // 18
        for row in range(image.height // 18):
            for col in range(columns):
                model(f'{name}_{row * columns + col}', image.crop((col*18, row*18, col*18+18, row*18+18)))

    for name, char, reward in [('background', '\ue431', False), ('rewards', '\ue433', True)]:
        im = panel(reward)
        files[f'assets/astral/textures/font/cronista/{name}.png'] = png(im)
        providers.append({'type': 'bitmap', 'file': f'astral:font/cronista/{name}.png',
                          'height': 286, 'ascent': 61, 'chars': [char]})
    providers.append({'type': 'space', 'advances': {'\ue430': -24, '\ue432': -185}})
    for name, caption, color in [('accept', 'ACEPTAR MISION', '#166456'), ('claim', 'COMPROBAR', '#18577b'),
                                  ('done', 'YA COBRADA', '#344658'), ('waiting', 'SIN DATOS', '#344658')]:
        tiles(name, action_button(caption, color))
    for name, color, marker in [('history', '#f0cd75', 0), ('easy', '#67e8cd', 1), ('medium', '#60bcf2', 2),
                                 ('hard', '#ac9dff', 3), ('reward', '#ffdb79', 0), ('active', '#5fe4e6', 0),
                                 ('pause', '#d97c7c', 0), ('refresh', '#89cadd', 0), ('back', '#b4c9d5', 0)]:
        model(name, clock(color, marker))
    for did, tier, name, counter, goal, desc in DAILIES:
        for status in ('available', 'active', 'done'):
            tiles(f'daily_{did}_{status}', card(name, desc, [300, 750, 1500][tier], status))
    for state in range(10):
        chapter = max(1, state)
        for status in ('available', 'active'):
            tiles(f'story_{state}_{status}', card(f'Capitulo {chapter} / 9', CHAPTERS[chapter - 1].split(': ', 1)[-1], STORY_REWARDS[chapter - 1], status))
    tiles('story_complete', card('Historia completada', 'La Estrella vuelve a brillar. El Santuario Celestial te espera.', 0, 'done'))
    return files, providers


def title(page):
    glyph = '\ue433' if page == 4 else '\ue431'
    return '&f\ue430' + glyph + '\ue432&b&lCRONISTA'


def preview(path):
    im = Image.new('RGBA', (208, 286), '#2d2922')
    im.alpha_composite(panel())
    body = Image.new('RGBA', (176, 222))
    icons = ['history', 'easy', 'medium', 'hard']
    colors = ['#f0cd75', '#67e8cd', '#60bcf2', '#ac9dff']
    for slot, color in enumerate(colors):
        body.alpha_composite(clock(color, min(slot, 3)), (8 + slot * 18, 18))
    _, tier, name, counter, goal, desc = DAILIES[0]
    body.alpha_composite(card(name, desc, 300, 'available'), (7, 35))
    body.alpha_composite(action_button('ACEPTAR MISION', '#166456'), (43, 89))
    body.alpha_composite(clock('#d97c7c'), (8, 108))
    body.alpha_composite(clock('#89cadd'), (134, 108))
    body.alpha_composite(clock('#b4c9d5'), (152, 108))
    text(body, 'CRONISTA', (43, 5), '#b9eaf5')
    text(body, 'Inventario', (37, 129), '#30343b')
    im.alpha_composite(body, (16, 48))
    target = Path(path)
    temp = target.with_suffix('.png.tmp')
    temp.write_bytes(png(im.resize((624, 858), Image.Resampling.NEAREST)))
    temp.replace(target)
