"""Ventanas ilustradas de Duelos y Party (18/11/2026), con arte de Gemini.

El dueno paso la referencia (.local/gemini/duelos-party/referencia2.png) y Gemini genero, sobre fondo magenta,
los marcos vacios y los botones. `gemini_recortes.py` les quita el magenta y los guarda en
pack-source/ref/gemini/dp_*.png. Aca solo se acomodan: el marco va estirado en 9 partes como fondo (glifo de
la fuente) y cada boton es un item partido en casillas de 18 px (mismo molde que infinita_ui).

Los marcos tienen costados anchos (armas, mochila): la ventana mide 256 px (cofre de 176 + 40 por lado).
Ventanas por tema (duelos, party): menu (tarjetas fijas), lista (36 casillas libres) y dialogo (dos botones).
Cada ventana tiene su propio texto en la franja de abajo. Los plugins leen `titulos-ui.properties`.
Uso: python duelos_party_ui.py  -> vistas previas build/previews/ui_*.png y build/runtime/titulos-ui.properties
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance
from services_ui import png, glyph_parts, SPLIT
from adventure_ui import label
from escape_menu import text

ROOT = Path(__file__).resolve().parent
ART = ROOT / 'pack-source/ref/gemini'
SIDE = 40
SIZE = (176 + 2 * SIDE, 280)
X0 = SIDE + 7                     # x de la primera casilla
HEAD_MAX = 80                     # alto maximo del encabezado (pantallas chicas con escala 4)
# Interior liso de cada marco de Gemini (medido sobre dp_<tema>_marco.png).
FRAMES = {'duelos': (167, 335, 748, 1062), 'party': (150, 284, 733, 1067)}
THEMES = {   # relleno, borde, texto de la franja y color de los huecos de lista
    'duelos': dict(fill='#1f1c23', band='#2a2426', edge='#a33a32', text='#efe2d0', slot='#4a3f44'),
    'party': dict(fill='#28201a', band='#3a2a1a', edge='#a0783c', text='#f3e3c0', slot='#5b4630'),
}
WINDOWS = {
    'duelos': {'menu': ['Sin perdida de items'],
               'lista': ['Elegi a tu rival', 'Elegi la arena', 'Pedidos recibidos', 'Ranking total', 'Ranking semanal'],
               'dialogo': ['Confirmar desafio', 'Responder desafio', 'Mis estadisticas', 'Resultado', 'Rendirse']},
    'party': {'menu': ['Hasta 6 jugadores por party'],
              'lista': ['Invitar jugadores', 'Mirar companeros'],
              'dialogo': ['Administrar companero', 'Confirmar expulsion']},
}


def _cols(c0, c1, r0, r1):
    return [r * 9 + c for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)]


MENU_CARDS = {
    'duelos': {'desafiar': _cols(0, 2, 0, 3), 'pedidos': _cols(3, 5, 0, 1), 'estadisticas': _cols(6, 8, 0, 1),
               'ranking': _cols(3, 5, 2, 3), 'salir_cola': _cols(6, 8, 2, 3)},
    'party': {'izquierda': _cols(0, 3, 2, 3), 'derecha': _cols(5, 8, 2, 3)},
}
DIALOG = {'duelos': {'izquierda': _cols(1, 3, 2, 3), 'derecha': _cols(5, 7, 2, 3)},
          'party': {'izquierda': _cols(0, 3, 2, 3), 'derecha': _cols(5, 8, 2, 3)}}
CENTER = 13
MEMBER_SLOTS = [10, 11, 12, 14, 15, 16]          # el primero siempre es el lider
NAV = {'volver': 45, 'anterior': 47, 'info': 49, 'siguiente': 51, 'cerrar': 53}
# Botones de Gemini: nombre -> archivo dp_<archivo>.png. "_off" = version apagada (gris).
BUTTONS = {
    'duelos': ['desafiar', 'pedidos', 'estadisticas', 'ranking', 'salir_cola', 'aceptar', 'rechazar', 'enviar',
               'cancelar', 'revancha', 'rendirse', 'arenas', 'seguir'],
    'party': ['p_invitar', 'p_salir', 'p_disolver', 'p_crear', 'p_aceptar', 'p_rechazar', 'p_echar', 'p_lider',
              'p_mirar', 'p_invitar_off', 'p_aceptar_off'],
}
FIRST_CHAR = 0xEF00


def frame(theme):
    return Image.open(ART / f'dp_{theme}_marco.png').convert('RGBA'), FRAMES[theme]


def head_image(theme):
    """Encabezado del marco en su proporcion (con tope de alto), estirado en 3 partes a lo ancho."""
    art, (l, t, r, b) = frame(theme)
    inner = SIZE[0] - 2 * SIDE
    height = min(HEAD_MAX, round(t * inner / (r - l)))
    head = Image.new('RGBA', (SIZE[0], height))
    for (x0, x1), (d0, d1) in zip(((0, l), (l, r), (r, art.width)), ((0, SIDE), (SIDE, SIZE[0] - SIDE), (SIZE[0] - SIDE, SIZE[0]))):
        head.alpha_composite(art.crop((x0, 0, x1, t)).resize((d1 - d0, height), Image.Resampling.LANCZOS), (d0, 0))
    return head


def slot_xy(slot):
    return X0 + slot % 9 * 18, 57 + slot // 9 * 18


def button(name, size):
    """Boton de Gemini al tamano de su lugar; los *_off se apagan a gris."""
    off = name.endswith('_off')
    art = Image.open(ART / f"dp_{name.removesuffix('_off')}.png").convert('RGBA')
    im = art.resize(size, Image.Resampling.LANCZOS)
    if off:
        alpha = im.getchannel('A')
        im = ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(0.1)).enhance(0.55); im.putalpha(alpha)
    # Opaco: lo transparente (hojas, esquinas) toma el color del interior; si no, se veria el gris del cofre.
    back = Image.new('RGBA', size, THEMES['party' if name.startswith('p_') else 'duelos']['fill'])
    back.alpha_composite(im)
    return back


def card_size(slots):
    cols = {s % 9 for s in slots}; rows = {s // 9 for s in slots}
    return 18 * len(cols), 18 * len(rows)


def places(theme, kind):
    if kind == 'menu':
        return MENU_CARDS[theme]
    if kind == 'dialogo':
        return DIALOG[theme]
    return {}


def holes(theme, kind):
    if kind == 'lista':
        return list(range(36)) + list(NAV.values())
    out = [s for slots in places(theme, kind).values() for s in slots] + [NAV['volver'], NAV['cerrar']]
    if theme == 'party' and kind == 'menu':
        out += MEMBER_SLOTS
    if kind == 'dialogo':
        out.append(CENTER)
    return out


def panel(theme, kind, caption):
    c = THEMES[theme]
    art, (l, t, r, b) = frame(theme)
    sx, sy = [0, l, r, art.width], [0, t, b, art.height]
    dx, dy = [0, SIDE, SIZE[0] - SIDE, SIZE[0]], [0, SPLIT, 258, SIZE[1]]
    im = Image.new('RGBA', SIZE)
    for row in range(3):
        for col in range(3):
            piece = art.crop((sx[col], sy[row], sx[col + 1], sy[row + 1]))
            im.alpha_composite(piece.resize((dx[col + 1] - dx[col], dy[row + 1] - dy[row]), Image.Resampling.LANCZOS), (dx[col], dy[row]))
    d = ImageDraw.Draw(im)
    d.rectangle((SIDE, SPLIT, SIZE[0] - SIDE - 1, 257), fill=c['fill'])
    if theme == 'party' and kind == 'menu':
        x0, y0 = slot_xy(1); x1, y1 = slot_xy(16)
        d.rectangle((x0 - 3, y0 - 1, x1 + 20, y1 + 20), fill=c['band'], outline=c['edge'])
        label(im, 'Lider', (slot_xy(1)[0] + 9, y0 + 5), 30, '#ffe08a')
        label(im, 'Companeros', (slot_xy(6)[0] + 9, y0 + 5), 52, c['text'])
        for s in MEMBER_SLOTS:
            x, y = slot_xy(s); d.rectangle((x - 1, y - 1, x + 18, y + 18), outline='#ffe08a' if s == 10 else c['edge'])
    if kind == 'dialogo':
        x, y = slot_xy(CENTER); d.rectangle((x - 2, y - 2, x + 19, y + 19), fill=c['band'], outline=c['edge'])
    for s in holes(theme, kind):
        x, y = slot_xy(s)
        if kind == 'lista' and s < 36:
            d.rectangle((x, y, x + 17, y + 17), outline=c['slot'])
        d.rectangle((x + 1, y + 1, x + 16, y + 16), fill=(0, 0, 0, 0))
    for slots in places(theme, kind).values():
        (x0, y0), (w, h) = slot_xy(slots[0]), card_size(slots)
        d.rectangle((x0, y0, x0 + w - 1, y0 + h - 1), fill=(0, 0, 0, 0))
    # Franja con el texto de la ventana (fila 4), botones de abajo y base del inventario.
    d.rectangle((X0, 129, X0 + 161, 144), fill=c['band'], outline=c['edge'])
    label(im, caption, (X0 + 81, 133), 156, c['text'])
    for s in (NAV['volver'], NAV['cerrar']) if kind != 'lista' else NAV.values():
        x, y = slot_xy(s)
        d.rectangle((x, y, x + 17, y + 17), outline=c['edge']); d.rectangle((x + 1, y + 1, x + 16, y + 16), fill=(0, 0, 0, 0))
    from market_ui import band_color
    d.rectangle((X0, 168, X0 + 161, 177), fill=band_color(c['edge']))
    d.line((X0, 167, X0 + 161, 167), fill=c['edge']); d.line((X0, 178, X0 + 161, 178), fill=c['edge'])
    for row in (*range(3), 4):
        for col in range(9):
            x, y = X0 + col * 18, 179 + row * 18 if row < 3 else 237
            d.rectangle((x, y, x + 17, y + 17), outline=c['slot'])
            d.rectangle((x + 1, y + 1, x + 16, y + 16), fill=(0, 0, 0, 0))
    return im


def tall(panel_image, head):
    out = Image.new('RGBA', (panel_image.width, head.height + panel_image.height - SPLIT))
    out.alpha_composite(panel_image.crop((0, SPLIT, panel_image.width, panel_image.height)), (0, head.height))
    out.alpha_composite(head, (0, 0))
    return out


def windows():
    return [(th, k, cap) for th in ('duelos', 'party') for k in ('menu', 'lista', 'dialogo') for cap in WINDOWS[th][k]]


def glyphs():
    """Por ventana: encabezado, retroceso, cuerpo, retroceso. Mas los saltos de inicio/fin del tema ancho."""
    n = FIRST_CHAR + 2; out = {}
    for w in windows():
        out[w] = tuple(chr(n + i) for i in range(4)); n += 4
    return chr(FIRST_CHAR), chr(FIRST_CHAR + 1), out


def title(theme, kind, caption):
    start, end, g = glyphs()
    return start + ''.join(g[(theme, kind, caption)]) + end


def key(theme, kind, caption):
    return f"{theme}.{kind}.{caption.lower().replace(' ', '_')}"


def titles_properties():
    lines = ['# Generado por datapack-src/duelos_party_ui.py: titulos (glifos) de las ventanas ilustradas.']
    for th, k, cap in windows():
        esc = ''.join(ch if ord(ch) < 128 else f'\\u{ord(ch):04x}' for ch in '§f' + title(th, k, cap))
        lines.append(f'{key(th, k, cap)}={esc}')
    return '\n'.join(lines) + '\n'


def full(theme, kind, caption, image=None):
    head = head_image(theme)
    return tall(panel(theme, kind, caption) if image is None else image, head), head.height


def card_names():
    names = []
    for th in BUTTONS:
        names += BUTTONS[th]
    return names


def card_sizes(name):
    """Tamanos en que se usa cada boton (un boton puede ir en menu y en dialogo)."""
    if name == 'desafiar':
        return [(54, 72)]
    if name.startswith('p_'):
        return [(72, 36)]
    return [(54, 36)]


def assets():
    files, providers = {}, []
    start, end, g = glyphs()
    advances = {start: -(SIDE + 8), end: SIDE + 8}
    for (th, k, cap), (h, hr, b, br) in g.items():
        image, hh = full(th, k, cap)
        for (part, ascent), char, rewind, tag in zip(glyph_parts(image, hh), (h, b), (hr, br), ('head', 'body')):
            path = f'font/duelparty/{th}_{k}_{WINDOWS[th][k].index(cap)}_{tag}.png'
            files['assets/astral/textures/' + path] = png(part)
            providers.append({'type': 'bitmap', 'file': 'astral:' + path, 'height': part.height, 'ascent': ascent, 'chars': [char]})
            advances[rewind] = -(part.width + 1)
    providers.append({'type': 'space', 'advances': advances})
    for name in card_names():
        for size in card_sizes(name):
            im = button(name, size)
            cols, rows = size[0] // 18, size[1] // 18
            for i in range(cols * rows):
                col, row = i % cols, i // cols
                piece = f'{name}_{i}'
                files[f'assets/astral/textures/item/duelparty/{piece}.png'] = png(im.crop((col * 18, row * 18, col * 18 + 18, row * 18 + 18)))
                files[f'assets/astral/models/duelparty/{piece}.json'] = json.dumps({'parent': 'minecraft:item/generated', 'gui_light': 'front',
                    'textures': {'layer0': f'astral:item/duelparty/{piece}'}, 'display': {'gui': {'scale': [1.125, 1.125, 1]}}}).encode()
                files[f'assets/astral/items/duelparty/{piece}.json'] = json.dumps({'oversized_in_gui': True,
                    'model': {'type': 'minecraft:model', 'model': f'astral:duelparty/{piece}'}}).encode()
    return files, providers


def preview(theme, kind, caption, path, fill=None):
    im = Image.new('RGBA', SIZE, '#252a28'); im.alpha_composite(panel(theme, kind, caption))
    pl = places(theme, kind)
    for place, what in (fill or {}).items():
        if isinstance(place, int):
            im.alpha_composite(what, slot_xy(place))
        else:
            im.alpha_composite(button(what, card_size(pl[place])), slot_xy(pl[place][0]))
    from menu_ui import icon as menu_icon
    im.alpha_composite(menu_icon('back'), slot_xy(NAV['volver']))
    im.alpha_composite(menu_icon('close'), slot_xy(NAV['cerrar']))
    text(im, 'Inventario', (X0 + 55, 169), color='#383c40')
    out_im, _ = full(theme, kind, caption, im)
    out = Image.new('RGBA', out_im.size, '#252a28'); out.alpha_composite(out_im)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(png(out.resize((out.width * 3, out.height * 3), Image.Resampling.NEAREST)))


def previews():
    folder = ROOT.parent / 'build/previews'
    head = Image.new('RGBA', (18, 18), '#c8a07a')
    preview('duelos', 'menu', WINDOWS['duelos']['menu'][0], folder / 'ui_duelos_menu.png', {k: k for k in MENU_CARDS['duelos']})
    preview('duelos', 'dialogo', 'Responder desafio', folder / 'ui_duelos_responder.png',
            {CENTER: head, 'izquierda': 'aceptar', 'derecha': 'rechazar'})
    preview('duelos', 'lista', 'Elegi a tu rival', folder / 'ui_duelos_lista.png', {0: head, 1: head, 2: head})
    if (ART / 'dp_p_invitar.png').exists():
        preview('party', 'menu', WINDOWS['party']['menu'][0], folder / 'ui_party_menu.png',
                {10: head, 11: head, 12: head, 'izquierda': 'p_invitar', 'derecha': 'p_salir'})
        preview('party', 'menu', WINDOWS['party']['menu'][0], folder / 'ui_party_invitado.png',
                {'izquierda': 'p_aceptar', 'derecha': 'p_rechazar'})
        preview('party', 'dialogo', 'Administrar companero', folder / 'ui_party_companero.png',
                {CENTER: head, 'izquierda': 'p_echar', 'derecha': 'p_lider'})


def write_titles():
    out = ROOT.parent / 'build/runtime/titulos-ui.properties'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(titles_properties(), encoding='ascii')
    return out


if __name__ == '__main__':
    previews()
    print(write_titles())
