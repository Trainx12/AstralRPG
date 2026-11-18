"""Guia Astral en ventana de cofre con el diseno "Atlas Celestial" (18/11/2026).

Los dialogos vanilla no permiten cambiar fondo ni botones (son los de todo el juego), asi que el indice
se dibuja como las ventanas de Duelos/Party/Menu: un glifo de fondo (marco de Gemini, cinta con la
estrella, botones celestes con el texto ya pintado) y en cada boton el OBJETO REAL del pack a la izquierda.
Las secciones siguen siendo los dialogos del Atlas (texto largo, ilustraciones y recetas).

Uso: python guia_cofre.py  -> build/menus/DeluxeMenus/gui_menus/guia_astral*.yml + vista previa.
Los glifos y modelos los suma build_pack.py (assets()).
"""
import json
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw
from escape_menu import text
from services_ui import png, outlined

ROOT = Path(__file__).resolve().parent
GEMINI = ROOT / 'pack-source/guia_atlas'
SIZE, SPLIT = (224, 280), 56
X0, Y0 = 31, 57                       # primera casilla del cofre dentro del dibujo
NAVY, NAVY2, CYAN, CYAN2, GOLD, GOLD2 = '#121a3a', '#1b2652', '#39d4ff', '#1d6f8f', '#e8b24a', '#8a5a1c'
COMMAND = 'guiaastral'
MENU = 'guia_astral'
PER_PAGE = 10
# Rango libre de la fuente default (revisado contra el FINAL del 18/11).
START, END = '', ''
PAGE_CHARS = [(chr(0xf210 + 4 * n), chr(0xf211 + 4 * n), chr(0xf212 + 4 * n), chr(0xf213 + 4 * n)) for n in range(6)]

# Etiqueta corta (entra en el boton) y objeto real que se muestra, por destino del indice del Atlas.
SHORT = {
    'como': ('Inicio', 'nucleo_astral'), 'mercader': ('Goblin', 'peluche_zombie_horse'),
    'consumibles': ('XP/Suerte', 'frasco_xp_gigante'), 'proteccion': ('Terrenos', 'cuero_tratado'),
    'cocina': ('Cocina', 'manzana_esmeralda'), 'misiones': ('Misiones', 'gema_luminica'),
    'materiales': ('Materiales', 'cristal_arcano'), 'berserker': ('Berserker', 'espada_1'),
    'mago': ('Mago', 'baston_1'), 'arquero': ('Arquero', 'arco_1'), 'lanzas': ('Lanzas', 'lanza_1'),
    'talismanes': ('Talismanes', 'corazon_fin'), 'especiales': ('Especiales', 'gancho'),
    'taladros': ('Taladros', 'taladro_diamante'), 'motosierras': ('Sierras', 'motosierra_basica'),
    'carnivora': ('Carnivora', 'carnivora_espada'), 'asura': ('Asura', 'asura_espada'), 'agua': ('Agua', 'agua_espada'),
    'oficios': ('Oficios', 'lampara_minero'), 'mascotas_1': ('Mascotas', 'peluche_ocelot'),
    'bestiario/1': ('Bestiario', None), 'drops': ('Drops', None),
}
FALLBACK = {'carnivora': 'minecraft:spider_eye', 'asura': 'minecraft:blaze_powder', 'oficios': 'minecraft:iron_pickaxe',
            'mascotas_1': 'minecraft:bone', 'bestiario/1': 'minecraft:zombie_head', 'drops': 'minecraft:chest',
            'misiones': 'minecraft:writable_book'}


def entries(datapack):
    """Lee el indice del Atlas ya generado: si se agrega una seccion, aparece sola."""
    with zipfile.ZipFile(datapack) as z:
        index = json.loads(z.read('data/astral/dialog/atlas/indice.json'))
        out = []
        for button in index['actions']:
            label = button['label']
            caption = label[-1]['text'] if isinstance(label, list) else label['text']
            action = button.get('action', {})
            if action.get('type') == 'show_dialog':
                target = action['dialog']
                command = f'[console] dialog show %player_name% {target}'
                key = target.split('/', 2)[-1] if '/seccion/' in target else target.split(':', 1)[1].split('/', 1)[1]
            else:
                command = '[player] ' + action.get('command', '').lstrip('/')
                key = 'misiones'
            short, iid = SHORT.get(key, (caption[:10], None))
            icon = None
            if iid and f'data/astral/loot_table/item/{iid}.json' in z.namelist():
                entry = json.loads(z.read(f'data/astral/loot_table/item/{iid}.json'))['pools'][0]['entries'][0]
                comps = entry['functions'][0]['components']
                icon = (entry['name'], comps.get('minecraft:item_model'))
            out.append(dict(caption=caption, short=short, command=command,
                            icon=icon or (FALLBACK.get(key, 'minecraft:book'), None)))
    return out


def pages(items):
    return [items[i:i + PER_PAGE] for i in range(0, len(items), PER_PAGE)]


def slot_xy(slot):
    return X0 + slot % 9 * 18, Y0 + slot // 9 * 18


def button_slots(n):
    row, col = n // 2, n % 2
    first = row * 9 + (0 if col == 0 else 5)
    return list(range(first, first + 4))


def frame():
    """Ventana vacia de Gemini en nueve partes, sin deformar esquinas (cristales y luna)."""
    src = Image.open(GEMINI / 'reserva_atlas_ventana_vacia.png').convert('RGBA')
    s = src.width / 825
    sx = [0, round(100 * s), round(728 * s), src.width]
    sy = [0, round(128 * s), round(918 * s), src.height]
    k = 24 / sx[1]
    dx = [0, 24, SIZE[0] - 24, SIZE[0]]
    top = SIZE[1] - 18 - round((sy[2] - sy[1]) * 0) - 0
    dy = [16, 16 + round(sy[1] * k), SIZE[1] - round((src.height - sy[2]) * k), SIZE[1]]
    out = Image.new('RGBA', SIZE)
    for r in range(3):
        for c in range(3):
            piece = src.crop((sx[c], sy[r], sx[c + 1], sy[r + 1]))
            out.alpha_composite(piece.resize((dx[c + 1] - dx[c], dy[r + 1] - dy[r]), Image.Resampling.NEAREST), (dx[c], dy[r]))
    return out


def ribbon(caption):
    src = Image.open(GEMINI / 'reserva_atlas_cabecera_botones_finos.png').convert('RGBA')
    s = src.width / 928
    art = src.crop((round(48 * s), 0, round(885 * s), round(300 * s)))
    w = 168
    art = art.resize((w, round(art.height * w / art.width)), Image.Resampling.NEAREST)
    im = Image.new('RGBA', (w, art.height))
    im.alpha_composite(art)
    outlined(im, caption, (w // 2, round(art.height * 0.62) - 4), color='#ffe9a8', outline='#20160a')
    return im


_GLYPHS = {}


def fit_text(im, caption, center, room, color):
    """Texto vanilla de 8 px; si no entra en el boton, junta las letras (sin espacio entre ellas)."""
    if not _GLYPHS:
        font = Image.open(ROOT / 'pack-source/vanilla-base/font/ascii.png').convert('RGBA')
        chars = json.loads((ROOT / 'pack-source/vanilla-base/font/ascii.json').read_text(encoding='utf-8'))['chars']
        for row, line in enumerate(chars):
            for col, char in enumerate(line):
                g = font.crop((col * 8, row * 8, col * 8 + 8, row * 8 + 8))
                box = g.getbbox()
                _GLYPHS[char] = (g, box[2] if box else 3)
    glyphs = [_GLYPHS.get(c, _GLYPHS['?']) for c in caption]
    gap = 1  # sin achicar: si no entra, se acorta la etiqueta en SHORT
    width = sum(a + gap for _, a in glyphs) - gap
    if width > room:
        raise ValueError(f'Etiqueta muy larga para el boton: {caption!r} ({width} > {room} px)')
    x, y = round(center[0] - width / 2), center[1]
    for g, advance in glyphs:
        alpha = g.getchannel('A')
        for offset, col in (((1, 1), '#051020'), ((0, 0), color)):
            layer = Image.new('RGBA', (8, 8), col)
            layer.putalpha(alpha)
            im.alpha_composite(layer, (x + offset[0], y + offset[1]))
        x += advance + gap


def cyan_button(caption, width=72):
    im = Image.new('RGBA', (width, 18))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, width - 1, 17), fill=NAVY, outline=CYAN)
    d.rectangle((1, 1, width - 2, 16), outline=CYAN2)
    d.line((2, 2, width - 3, 2), fill='#2a3a72')
    d.rectangle((1, 1, 16, 16), fill=NAVY2, outline=GOLD2)       # hueco del objeto real
    fit_text(im, caption, (18 + (width - 19) // 2, 5), width - 19, '#e8f8ff')
    return im


def gold_button(caption, width):
    im = Image.new('RGBA', (width, 18))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, width - 1, 17), fill='#c98d2c', outline='#5a3610')
    d.rectangle((1, 1, width - 2, 16), outline=GOLD)
    d.line((2, 2, width - 3, 2), fill='#ffd88a')
    text(im, caption, (width // 2, 5), color='#fff6dc')
    return im


def panel(page_entries, page, total):
    im = frame()
    d = ImageDraw.Draw(im)
    d.rectangle((24, 50, SIZE[0] - 25, SIZE[1] - 24), fill=NAVY)
    rib = ribbon('GUIA ASTRAL')
    im.alpha_composite(rib, ((SIZE[0] - rib.width) // 2, 0))
    for n, entry in enumerate(page_entries):
        x, y = slot_xy(button_slots(n)[0])
        im.alpha_composite(cyan_button(entry['short']), (x, y))
    # Fila de abajo: anterior / pagina / cerrar / siguiente.
    if page > 0:
        im.alpha_composite(gold_button('<', 18), slot_xy(45))
    if page < total - 1:
        im.alpha_composite(gold_button('>', 18), slot_xy(53))
    im.alpha_composite(gold_button('CERRAR', 54), slot_xy(48))
    text(im, f'{page + 1}/{total}', (slot_xy(46)[0] + 18, slot_xy(46)[1] + 5), color='#9fdcf0')
    # Inventario del jugador: casillas oscuras con borde dorado.
    d.line((X0, 168, X0 + 161, 168), fill=GOLD2)
    text(im, 'Inventario', (X0 + 30, 169), color='#7f8fb8')
    for row in range(4):
        for col in range(9):
            x, y = X0 + col * 18, (179 + row * 18) if row < 3 else 237
            d.rectangle((x, y, x + 17, y + 17), fill='#0c1230', outline='#3a4a7a')
    return im


def title(page):
    a, b, c, e = PAGE_CHARS[page]
    return '&f' + START + a + b + c + e + END


def assets(datapack):
    files, providers, advances = {}, [], {START: -32, END: 32}
    groups = pages(entries(datapack))
    for page, chunk in enumerate(groups):
        im = panel(chunk, page, len(groups))
        a, b, c, e = PAGE_CHARS[page]
        for n, (part, ascent, char, rewind) in enumerate(((im.crop((0, 0, 224, SPLIT)), 53, a, b),
                                                          (im.crop((0, SPLIT, 224, SIZE[1])), -3, c, e))):
            resource = f'font/guia_astral/pagina{page}_{n}.png'
            files['assets/astral/textures/' + resource] = png(part)
            providers.append({'type': 'bitmap', 'file': 'astral:' + resource, 'height': part.height,
                              'ascent': ascent, 'chars': [char]})
            advances[rewind] = -(part.getbbox()[2] + 1)
    providers.append({'type': 'space', 'advances': advances})
    return files, providers


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


def item(key, slot, name, material='PAPER', model='astral:viajes/blank', lore=(), commands=()):
    lines = [f'  {q(key)}:', f'    material: {material}', f'    slot: {slot}', f'    display_name: {q(name)}']
    if model:
        lines.append(f'    item_model: {q(model)}')
    if lore:
        lines += ['    lore:'] + [f'    - {q(x)}' for x in lore]
    lines += ['    item_flags:', '    - HIDE_ATTRIBUTES']
    if commands:
        lines += ['    click_commands:'] + [f'    - {q(x)}' for x in commands]
    return lines


def menu_id(page):
    return MENU if page == 0 else f'{MENU}_{page + 1}'


def menus(datapack):
    groups = pages(entries(datapack))
    out = {}
    for page, chunk in enumerate(groups):
        lines = [f'menu_title: {q(title(page))}', f'size: 54']
        if page == 0:
            lines += [f'open_command: {COMMAND}', 'register_command: true']
        lines.append('items:')
        for n, entry in enumerate(chunk):
            cmds = ['[sound] UI_BUTTON_CLICK', '[close]', entry['command'] + '<delay=2>']
            lore = ['&7Clic para abrir']
            material, model = entry['icon']
            for k, slot in enumerate(button_slots(n)):
                if k == 0:
                    lines += item(f'b{n}_icono', slot, '&b' + entry['caption'], material.split(':')[-1].upper(),
                                  model, lore, cmds)
                else:
                    lines += item(f'b{n}_{k}', slot, '&b' + entry['caption'], lore=lore, commands=cmds)
        if page > 0:
            lines += item('anterior', 45, '&ePagina anterior', commands=['[sound] UI_BUTTON_CLICK', f'[openguimenu] {menu_id(page - 1)}'])
        if page < len(groups) - 1:
            lines += item('siguiente', 53, '&eSiguiente pagina', commands=['[sound] UI_BUTTON_CLICK', f'[openguimenu] {menu_id(page + 1)}'])
        for k, slot in enumerate((48, 49, 50)):
            lines += item(f'cerrar_{k}', slot, '&cCerrar', commands=['[close]'])
        out[menu_id(page)] = '\n'.join(lines) + '\n'
    return out


def write(datapack, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    result = menus(datapack)
    for name, body in result.items():
        (out_dir / f'{name}.yml').write_text(body, encoding='utf-8')
    return list(result)


def preview(datapack, target):
    groups = pages(entries(datapack))
    sheet = Image.new('RGBA', (SIZE[0] * len(groups), SIZE[1]), '#0b0b12')
    for page, chunk in enumerate(groups):
        im = panel(chunk, page, len(groups))
        sheet.alpha_composite(im, (page * SIZE[0], 0))
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.Resampling.NEAREST).save(target)


if __name__ == '__main__':
    dp = ROOT.parent / 'build/AstralRPG-Items.zip'
    names = write(dp, ROOT.parent / 'build/menus/DeluxeMenus/gui_menus')
    preview(dp, ROOT.parent / 'build/previews/guia_astral_cofre.png')
    print('menus:', names)
