"""Mazmorra Infinita: dos ventanas ilustradas (Gemini, 12/11/2026) para elegir tier y velocidad.

Mismo molde que minijuegos_ui: marco de Gemini estirado en 9 partes y tarjetas de 2x2 casillas.
- Tier: Tier I-IV arriba (filas 0-1) y Tier V / V+ abajo, centradas (filas 2-3).
- Velocidad: cuatro tarjetas en las filas 1-2.
Fila 4: franja con el aviso. Fila 5: volver (45, solo en velocidad) y cerrar (53).
Arte: pack-source/ref/infinita-frame.png, ref/gemini/infinita_tier_<n>.png y infinita_vel_<n>.png.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw
from services_ui import png, SIZE, header, tall, glyph_parts, illustration
from market_ui import band_color
from adventure_ui import label
from escape_menu import text

ROOT = Path(__file__).resolve().parent
# Corte del centro vacio del marco (se mide sobre el original de Gemini, ver medir_marco()).
FRAME = ('infinita', (100, 225, 828, 1060))
FILL, EDGE = '#1c1426', '#c9a14f'
START, END = '', ''          # saltos -32/+32 compartidos con minijuegos y mascotas
KINDS = ('tier', 'vel')
GLYPHS = {'tier': tuple(chr(0xed50 + i) for i in range(4)), 'vel': tuple(chr(0xed54 + i) for i in range(4))}
CAPTIONS = {'tier': 'ELEGI TU TIER', 'vel': 'VELOCIDAD'}
HINTS = {'tier': 'Despues de 20 min sube cada 10', 'vel': 'Mas jugadores, mas monstruos'}
TIER_LABELS = ('I', 'II', 'III', 'IV', 'V', 'V+')   # 'TIER III' no entra en 36 px; el nombre completo va en el item
VEL_LABELS = ('FACIL', 'NORMAL', 'DIFICIL', 'PESADILLA')
COLS = ((0, 1), (2, 3), (5, 6), (7, 8))


def _slots(col_pair, rows):
    return [r * 9 + c for r in rows for c in col_pair]


CARD_SLOTS = {
    'tier': [_slots(COLS[i], (0, 1)) for i in range(4)] + [_slots(COLS[1], (2, 3)), _slots(COLS[2], (2, 3))],
    # Cartas anchas (3x2) para que entre PESADILLA: columnas 1-3 y 5-7, filas 0-1 y 2-3.
    'vel': [_slots(c, r) for r in ((0, 1), (2, 3)) for c in ((1, 2, 3), (5, 6, 7))],
}
BACK_SLOT, CLOSE_SLOT = 45, 53


def title(kind):
    return '&f' + START + ''.join(GLYPHS[kind]) + END


def slot_xy(slot):
    return 31 + slot % 9 * 18, 57 + slot // 9 * 18


def card_size(kind, index=0):
    slots = CARD_SLOTS[kind][index]
    return 18 * len({x % 9 for x in slots}), 18 * len({x // 9 for x in slots})


def card(kind, index):
    """Tarjeta: pintura, placa con el nombre y, en velocidad, los segundos arriba a la derecha."""
    w, h = card_size(kind, index)
    art = illustration(f'infinita_{kind}_{index + 1}')
    # Recorte con la proporcion de la tarjeta; en vertical se queda con la parte de arriba (los monstruos).
    if art.width / art.height > w / h:
        cw = round(art.height * w / h); art = art.crop(((art.width - cw) // 2, 0, (art.width + cw) // 2, art.height))
    else:
        ch = round(art.width * h / w); top = round((art.height - ch) * 0.3)
        art = art.crop((0, top, art.width, top + ch))
    im = art.resize((w * 4, h * 4), Image.Resampling.BOX).resize((w, h), Image.Resampling.LANCZOS)
    labels = TIER_LABELS if kind == 'tier' else VEL_LABELS
    plate_y = h - 11
    im.alpha_composite(Image.new('RGBA', (w, h - plate_y), (10, 6, 16, 205)), (0, plate_y))
    d = ImageDraw.Draw(im)
    d.line((1, plate_y, w - 2, plate_y), fill=EDGE)
    d.rectangle((0, 0, w - 1, h - 1), outline=EDGE); d.rectangle((1, 1, w - 2, h - 2), outline='#3b2a14')
    # El nombre va despues del borde para que PESADILLA no pierda la ultima letra.
    label(im, labels[index], (w // 2, plate_y + 1), w - 2, '#fff0cd')
    if kind == 'vel':  # cartelito con los segundos arriba a la derecha (le gusto al dueno, 12/11)
        from infinita import SPEEDS
        d.rectangle((w - 19, 2, w - 3, 12), fill=(10, 6, 16, 215), outline=EDGE)
        label(im, f'{SPEEDS[index][3]}s', (w - 11, 3), 15, '#e8c55b')
    return im


def panel(kind):
    art, (l, t, r, b) = FRAME
    src = Image.open(ROOT / f'pack-source/ref/{art}-frame.png').convert('RGBA')
    sx, sy = [0, l, r, src.width], [0, t, b, src.height]
    dx, dy = [0, 24, 200, 224], [0, 56, 258, SIZE[1]]
    im = Image.new('RGBA', SIZE)
    for row in range(3):
        for col in range(3):
            piece = src.crop((sx[col], sy[row], sx[col + 1], sy[row + 1]))
            im.alpha_composite(piece.resize((dx[col + 1] - dx[col], dy[row + 1] - dy[row]), Image.Resampling.LANCZOS), (dx[col], dy[row]))
    d = ImageDraw.Draw(im); d.rectangle((24, 56, 199, 258), fill=FILL)
    for index, slots in enumerate(CARD_SLOTS[kind]):
        (x, y), (w, h) = slot_xy(slots[0]), card_size(kind, index)
        d.rectangle((x, y, x + w - 1, y + h - 1), fill=(0, 0, 0, 0))
    if kind == 'tier':
        # Hueco del medio de abajo: simbolo de infinito dorado entre Tier V y Tier V+.
        cx, cy = 31 + 4 * 18 + 9, 57 + 2 * 18 + 18
        for ox in (-4, 4):
            d.ellipse((cx + ox - 4, cy - 3, cx + ox + 4, cy + 3), outline='#e8c55b', width=2)
    # Franja con el aviso (fila 4) y casillas de la fila 5 (los iconos son items reales).
    d.rectangle((31, 129, 192, 144), fill='#2a1f38', outline=EDGE)
    label(im, HINTS[kind], (112, 133), 156, '#e9dcff')
    for slot in ((BACK_SLOT, CLOSE_SLOT) if kind == 'vel' else (CLOSE_SLOT,)):
        x, y = slot_xy(slot)
        d.rectangle((x, y, x + 17, y + 17), outline=EDGE); d.rectangle((x + 1, y + 1, x + 16, y + 16), fill=(0, 0, 0, 0))
    d.rectangle((31, 168, 192, 177), fill=band_color(EDGE))
    d.line((31, 167, 192, 167), fill=EDGE); d.line((31, 178, 192, 178), fill=EDGE)
    for row in (*range(3), 4):
        for col in range(9):
            x, y = 31 + col * 18, 179 + row * 18 if row < 3 else 237
            d.rectangle((x, y, x + 17, y + 17), outline='#5a4d6b')
            d.rectangle((x + 1, y + 1, x + 16, y + 16), fill=(0, 0, 0, 0))
    return im


def full_panel(kind, image=None):
    head = header(FRAME[0], FRAME[1], CAPTIONS[kind], 40, FILL)   # 40: sobre la placa de Gemini
    return tall(panel(kind) if image is None else image, head), head.height


def assets():
    files, providers = {}, []
    for kind in KINDS:
        advances = {}
        a, b, c, d = GLYPHS[kind]; im, hh = full_panel(kind)
        for n, ((part, ascent), char, rewind) in enumerate(zip(glyph_parts(im, hh), (a, c), (b, d))):
            path = f'font/infinita/{kind}_{n}.png'
            files['assets/astral/textures/' + path] = png(part)
            providers.append({'type': 'bitmap', 'file': 'astral:' + path, 'height': part.height, 'ascent': ascent, 'chars': [char]})
            advances[rewind] = -(part.getbbox()[2] + 1)
        providers.append({'type': 'space', 'advances': advances})
        for index in range(len(CARD_SLOTS[kind])):
            image = card(kind, index)
            ncols = card_size(kind, index)[0] // 18
            for i in range(len(CARD_SLOTS[kind][index])):
                col, row = i % ncols, i // ncols
                name = f'{kind}{index + 1}_{i}'
                files[f'assets/astral/textures/item/infinita/{name}.png'] = png(image.crop((col * 18, row * 18, col * 18 + 18, row * 18 + 18)))
                files[f'assets/astral/models/infinita/{name}.json'] = json.dumps({'parent': 'minecraft:item/generated', 'gui_light': 'front',
                    'textures': {'layer0': f'astral:item/infinita/{name}'}, 'display': {'gui': {'scale': [1.125, 1.125, 1]}}}).encode()
                files[f'assets/astral/items/infinita/{name}.json'] = json.dumps({'oversized_in_gui': True,
                    'model': {'type': 'minecraft:model', 'model': f'astral:infinita/{name}'}}).encode()
    return files, providers


def preview(kind, path):
    im = Image.new('RGBA', SIZE, '#252a28'); im.alpha_composite(panel(kind))
    for index, slots in enumerate(CARD_SLOTS[kind]):
        im.alpha_composite(card(kind, index), slot_xy(slots[0]))
    from menu_ui import icon
    if kind == 'vel':
        im.alpha_composite(icon('back'), slot_xy(BACK_SLOT))
    im.alpha_composite(icon('close'), slot_xy(CLOSE_SLOT))
    text(im, 'Inventario', (86, 169), color='#383c40')
    im, _ = full_panel(kind, im)
    out = Image.new('RGBA', im.size, '#252a28'); out.alpha_composite(im)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(png(out.resize((out.width * 3, out.height * 3), Image.Resampling.NEAREST)))


def menus():
    """Ventanas de DeluxeMenus. Al elegir, la consola ejecuta infelegir (astral_infinita.sk)."""
    from infinita import TIERS, SPEEDS
    from menu_ui import decorate
    out = {}
    P = '%player_name%'
    items = {}
    for index, ((t, name, _), slots) in enumerate(zip(TIERS, CARD_SLOTS['tier'])):
        lore = [f'&7Pelea contra mobs de {name}.', '&720 min en este tier; despues sube cada 10 min.', '', '&eClic para elegir']
        for n, slot in enumerate(slots):
            items[f'tier{t}' if n == 0 else f'tier{t}_hit_{n}'] = dict(material='PAPER', slot=slot, item_model=f'astral:infinita/tier{index + 1}_{n}',
                item_flags=['HIDE_ATTRIBUTES'], display_name=f'&5&l{name}', lore=lore,
                click_commands=[f'[console] infelegir {P} tier {t}', '[openguimenu] infinita_vel'])
    items['cerrar'] = dict(material='BARRIER', slot=CLOSE_SLOT, display_name='&cCerrar', click_commands=['[close]'])
    out['infinita_tier'] = decorate(dict(menu_title=title('tier'), size=54, items=items))
    items = {}
    for index, ((v, name, _, s), slots) in enumerate(zip(SPEEDS, CARD_SLOTS['vel'])):
        lore = [f'&7Aparece un grupo de mobs cada {s} s.', '&7Mas jugadores, mas mobs.', '', '&eClic para entrar']
        for n, slot in enumerate(slots):
            items[f'vel{v}' if n == 0 else f'vel{v}_hit_{n}'] = dict(material='PAPER', slot=slot, item_model=f'astral:infinita/vel{index + 1}_{n}',
                item_flags=['HIDE_ATTRIBUTES'], display_name=f'&5&l{name}', lore=lore,
                click_commands=['[close]', f'[console] infelegir {P} vel {v}<delay=2>'])
    items['volver'] = dict(material='ARROW', slot=BACK_SLOT, display_name='&fVolver al tier', click_commands=['[openguimenu] infinita_tier'])
    items['cerrar'] = dict(material='BARRIER', slot=CLOSE_SLOT, display_name='&cCerrar', click_commands=['[close]'])
    out['infinita_vel'] = decorate(dict(menu_title=title('vel'), size=54, items=items))
    return out


def write_menus():
    folder = ROOT.parent / 'build/menus/DeluxeMenus/gui_menus'
    folder.mkdir(parents=True, exist_ok=True)
    for name, data in menus().items():
        (folder / f'{name}.yml').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return list(menus())


if __name__ == '__main__':
    for kind in KINDS:
        preview(kind, ROOT.parent / f'build/Servicios-preview/infinita_{kind}.png')
    print(write_menus())
