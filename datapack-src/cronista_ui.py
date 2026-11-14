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
ART = ROOT / 'pack-source/ref/cronista2-frame.png'   # marco de Gemini (noviembre 2026)
GEMINI = ROOT / 'pack-source/ref/gemini'
TITLES = ['Historia', 'Diaria facil', 'Diaria media', 'Diaria dificil', 'Premio de historia']
STORY_REWARDS = [300, 500, 1000, 1500, 2000, 2500, 3000, 5000, 10000]


def png(im):
    buffer = io.BytesIO()
    im.save(buffer, 'PNG')
    return buffer.getvalue()


# El marco va de GUI(-16, -37) a GUI(192, 240), siendo GUI(0, 0) la esquina del
# cofre de 54 slots. La abertura interior del dibujo queda justo alrededor de
# las casillas, asi el marco no tapa nada y nada tapa el marco.
OFFSET = (16, 37)
ART_INNER_TOP, ART_INNER_BOTTOM = 584, 2050   # bordes de la abertura en el dibujo
ART_INNER_LEFT, ART_INNER_RIGHT = 232, 1624
GUI_INNER_TOP, GUI_INNER_BOTTOM = 16, 218
# Un glifo no puede medir mas de 256 px ni tener ascent mayor a su alto,
# por eso el marco se parte en una franja de arriba y el resto.
SPLIT = 50


def frame(caption='EL CRONISTA'):
    source = Image.open(ART).convert('RGBA')
    top_h = GUI_INNER_TOP + OFFSET[1]
    scale = (GUI_INNER_BOTTOM - GUI_INNER_TOP) / (ART_INNER_BOTTOM - ART_INNER_TOP)
    rest_h = round((source.height - ART_INNER_TOP) * scale)
    im = Image.new('RGBA', (208, top_h + rest_h))
    # Nueve cortes: los costados del dibujo quedan fuera de las casillas (16 px por lado).
    sx = [0, ART_INNER_LEFT, ART_INNER_RIGHT, source.width]
    sy = [0, ART_INNER_TOP, source.height]
    dx = [0, OFFSET[0], OFFSET[0] + 176, 208]
    dy = [0, top_h, top_h + rest_h]
    for row in range(2):
        for col in range(3):
            piece = source.crop((sx[col], sy[row], sx[col + 1], sy[row + 1]))
            im.alpha_composite(piece.resize((dx[col + 1] - dx[col], dy[row + 1] - dy[row]), Image.Resampling.NEAREST), (dx[col], dy[row]))
    # Titulo dentro del cartel azul del marco.
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        text(im, caption, (104 + ox, 35 + oy), color='#0d1222')
    text(im, caption, (104, 35), color='#f6e4b8')
    return im


def gemini_icon(name, size=16):
    return Image.open(GEMINI / f'{name}.png').convert('RGBA').resize((size, size), Image.Resampling.LANCZOS)


def panel(rewards=False, caption='EL CRONISTA'):
    im = frame(caption)
    body = Image.new('RGBA', (176, 222))
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
    im.alpha_composite(body, OFFSET)
    # Los titulos se dibujan sobre los items. Las ventanas transparentes
    # permiten ver modelos, cantidades y los objetos reales del jugador.
    holes = ImageDraw.Draw(im)
    ox, oy = OFFSET

    def hole(x0, y0, x1, y1):
        holes.rectangle((x0 + ox, y0 + oy, x1 + ox, y1 + oy), fill=(0, 0, 0, 0))
    for row in range(6):
        for col in range(9):
            x, y = 8 + col * 18, 18 + row * 18
            hole(x, y, x + 15, y + 15)
    if not rewards:
        hole(7, 35, 168, 88)
        hole(43, 89, 132, 106)
    for row in range(3):
        for col in range(9):
            x, y = 8 + col * 18, 140 + row * 18
            hole(x, y, x + 15, y + 15)
    for col in range(9):
        x = 8 + col * 18
        hole(x, 198, x + 15, 213)
    return im


# Deseo lite del Cronista (renacimiento.py): misma ventana azul, con las 5 opciones y las reglas marcadas.
DESEO_SLOTS = (20, 21, 22, 23, 24)
DESEO_REGLAS = 40


def deseo_panel():
    im = panel(True, 'UN DESEO')
    d = ImageDraw.Draw(im)
    ox, oy = OFFSET

    def box(slot, color):
        x, y = ox + 7 + slot % 9 * 18, oy + 17 + slot // 9 * 18
        d.rectangle((x - 1, y - 1, x + 18, y + 18), outline=color)
    for slot in DESEO_SLOTS:
        box(slot, '#f0cd75')
    box(DESEO_REGLAS, '#67e8cd')
    return im


def glyph_parts(im):
    """Parte el marco en dos glifos validos: (imagen, ascent)."""
    top, rest = im.crop((0, 0, 208, SPLIT)), im.crop((0, SPLIT, 208, im.height))
    # La parte de arriba de un glifo queda en y = 13 - ascent dentro del cofre.
    return [(top, 13 + OFFSET[1]), (rest, 13 + OFFSET[1] - SPLIT)]


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


def card(name, objective, amount, status, scene=False):
    im = Image.new('RGBA', (162, 54), '#102a43')
    if scene:
        art = Image.open(GEMINI / 'cronista_escena.png').convert('RGBA')
        top = (art.height - art.width // 3) // 2
        pic = art.crop((0, top, art.width, top + art.width // 3)).resize((162, 54), Image.Resampling.LANCZOS)
        im = Image.blend(im, pic, .35)
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


def tab_icon(art, color, marker=0):
    im = gemini_icon(art)
    d = ImageDraw.Draw(im)
    if marker:
        d.rectangle((10, 10, 15, 15), fill='#071a2d')
        for x in range(marker):
            d.line((11 + x * 2, 11, 11 + x * 2, 14), fill=color)
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
        # El atlas de items de 26.1 solo incorpora el directorio textures/item.
        tex = f'astral:item/cronista/{name}'
        files[f'assets/astral/textures/item/cronista/{name}.png'] = png(image)
        definition = {'parent': 'minecraft:item/generated', 'gui_light': 'front', 'textures': {'layer0': tex},
                      'display': {'gui': {'scale': [image.width / 16, image.height / 16, 1]}}}
        files[f'assets/astral/models/cronista/{name}.json'] = json.dumps(definition).encode('utf-8')
        files[f'assets/astral/items/cronista/{name}.json'] = json.dumps({
            'oversized_in_gui': image.width > 16 or image.height > 16,
            'model': {'type': 'minecraft:model', 'model': f'astral:cronista/{name}'}}).encode('utf-8')

    def tiles(name, image):
        # Cada slot dibuja su fragmento a escala 1.125. Evita el limite de
        # escala de los modelos y conserva todos los puntos de clic.
        columns = image.width // 18
        for row in range(image.height // 18):
            for col in range(columns):
                model(f'{name}_{row * columns + col}', image.crop((col*18, row*18, col*18+18, row*18+18)))

    for name, chars, image in [('background', ('\ue431', '\ue435'), panel(False)), ('rewards', ('\ue433', '\ue436'), panel(True)),
                               ('deseo', ('\ue437', '\ue438'), deseo_panel())]:
        for part, ((im, ascent), char) in enumerate(zip(glyph_parts(image), chars)):
            # Minecraft mide el avance de un glifo hasta su ultima columna con
            # pixeles visibles. Un punto casi invisible en la ultima columna
            # fija el avance en 209 para las dos partes y no se corren.
            im.putpixel((im.width - 1, 0), (0, 0, 0, 1))
            files[f'assets/astral/textures/font/cronista/{name}_{part}.png'] = png(im)
            providers.append({'type': 'bitmap', 'file': f'astral:font/cronista/{name}_{part}.png',
                              'height': im.height, 'ascent': ascent, 'chars': [char]})
    # \ue430 lleva al borde del marco, \ue434 vuelve 209 para dibujar la
    # segunda parte en el mismo lugar y \ue432 deja el cursor donde estaba.
    providers.append({'type': 'space', 'advances': {'\ue430': -24, '\ue434': -209, '\ue432': -185}})
    for name, caption, color in [('accept', 'ACEPTAR MISION', '#166456'), ('claim', 'COMPROBAR', '#18577b'),
                                  ('done', 'YA COBRADA', '#344658'), ('waiting', 'SIN DATOS', '#344658')]:
        tiles(name, action_button(caption, color))
    for name, art, color, marker in [('history', 'cronista_historia', '#f0cd75', 0), ('easy', 'cronista_diarias', '#67e8cd', 1),
                                      ('medium', 'cronista_diarias', '#60bcf2', 2), ('hard', 'cronista_diarias', '#ac9dff', 3),
                                      ('reward', 'cronista_encargos', '#ffdb79', 0)]:
        model(name, tab_icon(art, color, marker))
    for name, color, marker in [('active', '#5fe4e6', 0), ('pause', '#d97c7c', 0), ('refresh', '#89cadd', 0), ('back', '#b4c9d5', 0)]:
        model(name, clock(color, marker))
    for did, tier, name, counter, goal, desc in DAILIES:
        for status in ('available', 'active', 'done'):
            tiles(f'daily_{did}_{status}', card(name, desc, [300, 750, 1500][tier], status))
    for state in range(10):
        chapter = max(1, state)
        for status in ('available', 'active'):
            tiles(f'story_{state}_{status}', card(f'Capitulo {chapter} / 9', CHAPTERS[chapter - 1].split(': ', 1)[-1], STORY_REWARDS[chapter - 1], status, True))
    tiles('story_complete', card('Historia completada', 'La Estrella vuelve a brillar. El Santuario Celestial te espera.', 0, 'done', True))
    return files, providers


def title(page):
    top, rest = {4: ('\ue433', '\ue436'), 'deseo': ('\ue437', '\ue438')}.get(page, ('\ue431', '\ue435'))
    # El nombre CRONISTA ya viene dibujado en el marco.
    return '&f\ue430' + top + '\ue434' + rest + '\ue432'


def preview(path):
    frame_im = panel()
    im = Image.new('RGBA', frame_im.size, '#2d2922')
    # Lo que se ve por las ventanas: el fondo oscuro vanilla del cofre.
    ImageDraw.Draw(im).rectangle((OFFSET[0], OFFSET[1], OFFSET[0] + 175, OFFSET[1] + 221), fill='#1b1b1b')
    im.alpha_composite(frame_im)
    body = Image.new('RGBA', (176, 222))
    arts = ['cronista_historia', 'cronista_diarias', 'cronista_diarias', 'cronista_diarias']
    colors = ['#f0cd75', '#67e8cd', '#60bcf2', '#ac9dff']
    for slot, (art, color) in enumerate(zip(arts, colors)):
        body.alpha_composite(tab_icon(art, color, min(slot, 3)), (8 + slot * 18, 18))
    body.alpha_composite(card('Capitulo 1 / 9', CHAPTERS[0].split(': ', 1)[-1], STORY_REWARDS[0], 'available', True), (7, 35))
    body.alpha_composite(action_button('ACEPTAR MISION', '#166456'), (43, 89))
    body.alpha_composite(clock('#d97c7c'), (8, 108))
    body.alpha_composite(clock('#89cadd'), (134, 108))
    body.alpha_composite(clock('#b4c9d5'), (152, 108))
    text(body, 'Inventario', (37, 129), '#30343b')
    im.alpha_composite(body, OFFSET)
    target = Path(path)
    temp = target.with_suffix('.png.tmp')
    temp.write_bytes(png(im.resize((im.width * 3, im.height * 3), Image.Resampling.NEAREST)))
    temp.replace(target)
