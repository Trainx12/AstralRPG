"""Guia Astral entera en ventanas de cofre con el diseno "Atlas Celestial" (18-19/11/2026).

Los dialogos vanilla no permiten cambiar fondo ni botones (son los de todo el juego). Por eso TODA la guia
se muestra como las ventanas de Duelos/Party/Menu: un glifo de fondo (marco de Gemini, cinta dorada con el
titulo) y en las casillas los OBJETOS REALES del pack (con sus stats al pasar el mouse).

Como funciona:
- build.py sigue armando la guia como dialogos (es la fuente de datos: textos, items, recetas). Al final,
  `capture(files, ...)` (llamado desde guia_atlas.generate) guarda esa fuente en build/runtime/guia_fuente.json
  y SACA del datapack la guia vieja (dialogos guia/*, receta/*, atlas/*) y los botones de ESC.
- `menus()` convierte cada dialogo en un menu de DeluxeMenus (g_<ruta>), con tres fondos: indice (botones
  pintados), general y receta. El titulo de cada ventana va como texto en la cinta (centrado con espacios).

Uso: python guia_cofre.py  -> build/menus/DeluxeMenus/gui_menus/guia_astral*.yml y g_*.yml + vistas previas.
Los glifos y modelos los suma build_pack.py (assets()).
"""
import json
import re
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw
from escape_menu import text
from services_ui import png

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'build/runtime/guia_fuente.json'
GEMINI = ROOT / 'pack-source/guia_atlas'
SIZE, SPLIT = (224, 280), 56
X0, Y0 = 31, 57                       # primera casilla del cofre dentro del dibujo
NAVY, NAVY2, CYAN, CYAN2, GOLD, GOLD2 = '#121a3a', '#1b2652', '#39d4ff', '#1d6f8f', '#e8b24a', '#8a5a1c'
COMMAND = 'guiaastral'
MENU = 'guia_astral'
PER_PAGE = 10
TITLE_COLOR = '&#ffe9a8'
# Rango libre de la fuente default (revisado contra el FINAL del 18/11).
START, END = '', ''
PAGE_CHARS = [(chr(0xf210 + 4 * n), chr(0xf211 + 4 * n), chr(0xf212 + 4 * n), chr(0xf213 + 4 * n)) for n in range(6)]
BG_CHARS = {'general': tuple(chr(0xf230 + i) for i in range(4)), 'receta': tuple(chr(0xf234 + i) for i in range(4))}
SHIFT = {1 << k: chr(0xf240 + k) for k in range(8)}          # espacios +1..+128 para centrar el titulo

# Etiqueta corta (entra en el boton del indice) y objeto real que se muestra, por destino.
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
FALLBACK = {'bestiario/1': 'minecraft:zombie_head', 'drops': 'minecraft:chest', 'misiones': 'minecraft:writable_book'}
NAV_MODELS = {'back': 'astral:mascotas/nav_back', 'next': 'astral:mascotas/nav_next',
              'close': 'astral:mascotas/nav_close', 'info': 'astral:mascotas/nav_info'}
INFO_MODEL = 'astral:menu/icon_guia'


# ---------------------------------------------------------------- captura (corre dentro de build.py)

def _links(obj):
    if isinstance(obj, dict):
        if obj.get('type') == 'show_dialog':
            yield obj['dialog'].split(':', 1)[1]
        for v in obj.values():
            yield from _links(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _links(v)


def is_guide(key):
    return key in ('guia', 'guia_esc') or key.startswith(('guia/', 'receta/', 'atlas/'))


def capture(files, recetas, retratos, ilustraciones, index):
    """Guarda la guia (dialogos) como fuente de los menus y la saca del datapack."""
    prefix = 'data/astral/dialog/'
    dialogs = {n[len(prefix):-5]: json.loads(files[n]) for n in list(files)
               if n.startswith(prefix) and n.endswith('.json')}
    seen, stack = set(), ['atlas/indice']
    while stack:
        k = stack.pop()
        if k in seen or k not in dialogs:
            continue
        seen.add(k)
        stack += list(_links(dialogs[k]))
    data = dict(index=index, dialogs={k: dialogs[k] for k in sorted(seen) if k != 'atlas/indice'},
                recetas=recetas, retratos=retratos, ilustraciones=ilustraciones)
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    SOURCE.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    for k in dialogs:
        if is_guide(k):
            del files[prefix + k + '.json']
    # Otros dialogos que apuntaban a la guia vieja: ahora abren la ventana de cofre.
    def fix(obj):
        if isinstance(obj, dict):
            if obj.get('type') == 'show_dialog' and is_guide(obj['dialog'].split(':', 1)[1]):
                obj.clear()
                obj.update(type='run_command', command=COMMAND)
            for v in obj.values():
                fix(v)
        elif isinstance(obj, list):
            for v in obj:
                fix(v)
    for k in dialogs:
        if not is_guide(k):
            d = dialogs[k]
            fix(d)
            files[prefix + k + '.json'] = json.dumps(d, ensure_ascii=False, indent=1)
    # Sin botones en ESC ni en acciones rapidas: la guia se abre desde el Menu Astral.
    for tag in ('pause_screen_additions', 'quick_actions'):
        files[f'data/minecraft/tags/dialog/{tag}.json'] = json.dumps({'values': []})
    link = json.dumps([{'text': 'Guia Astral: ', 'color': 'light_purple', 'italic': False},
                       {'text': '[Abrir]', 'color': 'aqua', 'underlined': True,
                        'click_event': {'action': 'run_command', 'command': '/' + COMMAND}},
                       {'text': ' o desde /menu.', 'color': 'gray'}], ensure_ascii=False)
    files['data/astral/function/guide/give.mcfunction'] = f'scoreboard players reset @s astral.guia\ntellraw @s {link}\n'
    files['data/astral/function/atlas/open.mcfunction'] = f'scoreboard players reset @s astral.guia2\ntellraw @s {link}\n'
    join = files.get('data/astral/function/guide/join.mcfunction', '')
    files['data/astral/function/guide/join.mcfunction'] = '\n'.join(
        f'tellraw @s {link}' if l.startswith('dialog show') else l.replace('Esc -> Guia AstralRPG', '/menu -> Guia')
        for l in join.splitlines()) + '\n'
    return data


def load():
    return json.loads(SOURCE.read_text(encoding='utf-8'))


# ---------------------------------------------------------------- texto y items para DeluxeMenus

COLORS = dict(black='0', dark_blue='1', dark_green='2', dark_aqua='3', dark_red='4', dark_purple='5', gold='6',
              gray='7', dark_gray='8', blue='9', green='a', aqua='b', red='c', light_purple='d', yellow='e', white='f')
PRIVATE = re.compile('[-]')


def code(color):
    if not color:
        return ''
    return '&' + color if color.startswith('#') else '&' + COLORS.get(color, 'f')


def legacy(comp, color='white', bold=False):
    """Componente JSON -> lineas con codigos & (DeluxeMenus acepta &#RRGGBB)."""
    out = ['']
    def walk(c, color, bold):
        if isinstance(c, str):
            c = {'text': c}
        if isinstance(c, list):
            if not c:
                return
            head = c[0] if isinstance(c[0], dict) else {'text': c[0]}
            color = head.get('color', color); bold = head.get('bold', bold)
            walk(head, color, bold)
            for x in c[1:]:
                walk(x, color, bold)
            return
        color = c.get('color', color); bold = c.get('bold', bold)
        if c.get('font') or PRIVATE.search(c.get('text', '')):
            body = ''
        else:
            body = c.get('text', '')
        parts = body.split('\n')
        for i, part in enumerate(parts):
            if i:
                out.append('')
            if part:
                out[-1] += code(color) + ('&l' if bold else '') + part
        for x in c.get('extra', []):
            walk(x, color, bold)
    walk(comp, color, bold)
    return out


def plain(comp):
    return re.sub(r'&(#[0-9a-fA-F]{6}|[0-9a-fk-or])', '', ''.join(legacy(comp)))


def wrap(lines, width=42):
    out = []
    for line in lines:
        m = re.match(r'((?:&(?:#[0-9a-fA-F]{6}|[0-9a-fk-or]))*)(.*)', line)
        prefix, body = m.group(1), m.group(2)
        if len(re.sub(r'&(#[0-9a-fA-F]{6}|[0-9a-fk-or])', '', body)) <= width:
            out.append(line)
            continue
        clean = re.sub(r'&(#[0-9a-fA-F]{6}|[0-9a-fk-or])', '', body)
        out += [prefix + piece for piece in textwrap.wrap(clean, width)]
    return out


def stack_item(stack):
    """Stack de item (id/count/components) -> datos de item para DeluxeMenus."""
    comps = stack.get('components', {})
    name = comps.get('minecraft:custom_name') or comps.get('minecraft:item_name')
    name = ''.join(legacy(name)) if name else '&f' + stack['id'].split(':')[-1].replace('_', ' ').capitalize()
    lore = []
    for line in comps.get('minecraft:lore', []):
        lore += legacy(line, 'dark_purple')
    count = stack.get('count', 1)
    it = dict(material=stack['id'].split(':')[-1].upper(), name=name, lore=lore, amount=max(1, min(64, count)))
    if count > 64:
        it['lore'] = [f'&7Cantidad: &f{count}'] + it['lore']
    if comps.get('minecraft:item_model'):
        it['model'] = comps['minecraft:item_model']
    if comps.get('minecraft:enchantment_glint_override'):
        it['glow'] = True
    dyed = comps.get('minecraft:dyed_color')
    if dyed is not None:
        rgb = dyed['rgb'] if isinstance(dyed, dict) else dyed
        it['rgb'] = f'{rgb >> 16 & 255}, {rgb >> 8 & 255}, {rgb & 255}'
    return it


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


def yaml_item(key, slot, it, commands=()):
    lines = [f'  {q(key)}:', f"    material: {it.get('material', 'PAPER')}", f'    slot: {slot}',
             f"    amount: {it.get('amount', 1)}", f"    display_name: {q(it.get('name', ' '))}"]
    if it.get('model'):
        lines.append(f"    item_model: {q(it['model'])}")
    if it.get('lore'):
        lines += ['    lore:'] + [f'    - {q(x)}' for x in it['lore']]
    if it.get('rgb'):
        lines.append(f"    rgb: {q(it['rgb'])}")
    if it.get('glow'):
        lines += ['    enchantments:', "    - 'unbreaking;1'"]
    lines += ['    item_flags:', '    - HIDE_ATTRIBUTES', '    - HIDE_ENCHANTS', '    - HIDE_DYE']
    if commands:
        lines += ['    click_commands:'] + [f'    - {q(x)}' for x in commands]
    return lines


# ---------------------------------------------------------------- dibujo

_GLYPHS = {}


def glyphs():
    if not _GLYPHS:
        font = Image.open(ROOT / 'pack-source/vanilla-base/font/ascii.png').convert('RGBA')
        chars = json.loads((ROOT / 'pack-source/vanilla-base/font/ascii.json').read_text(encoding='utf-8'))['chars']
        for row, line in enumerate(chars):
            for col, char in enumerate(line):
                g = font.crop((col * 8, row * 8, col * 8 + 8, row * 8 + 8))
                box = g.getbbox()
                _GLYPHS[char] = (g, box[2] if box else 3)
    return _GLYPHS


def text_width(caption, bold=False):
    g = glyphs()
    return sum(g.get(c, g['?'])[1] + 1 + (1 if bold else 0) for c in caption) - 1


def fit_text(im, caption, center, room, color):
    """Texto vanilla de 8 px con sombra; si no entra, error (se acorta la etiqueta en SHORT)."""
    g = glyphs()
    width = text_width(caption)
    if width > room:
        raise ValueError(f'Etiqueta muy larga para el boton: {caption!r} ({width} > {room} px)')
    x, y = round(center[0] - width / 2), center[1]
    for c in caption:
        glyph, advance = g.get(c, g['?'])
        alpha = glyph.getchannel('A')
        for offset, col in (((1, 1), '#051020'), ((0, 0), color)):
            layer = Image.new('RGBA', (8, 8), col)
            layer.putalpha(alpha)
            im.alpha_composite(layer, (x + offset[0], y + offset[1]))
        x += advance + 1


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
    dy = [16, 16 + round(sy[1] * k), SIZE[1] - round((src.height - sy[2]) * k), SIZE[1]]
    out = Image.new('RGBA', SIZE)
    for r in range(3):
        for c in range(3):
            piece = src.crop((sx[c], sy[r], sx[c + 1], sy[r + 1]))
            out.alpha_composite(piece.resize((dx[c + 1] - dx[c], dy[r + 1] - dy[r]), Image.Resampling.NEAREST), (dx[c], dy[r]))
    return out


def compass():
    src = Image.open(GEMINI / 'reserva_atlas_cabecera_botones_finos.png').convert('RGBA')
    s = src.width / 928
    art = src.crop((round(375 * s), 0, round(560 * s), round(185 * s)))
    return art.resize((34, 34), Image.Resampling.NEAREST)


def ribbon(caption):
    src = Image.open(GEMINI / 'reserva_atlas_cabecera_botones_finos.png').convert('RGBA')
    s = src.width / 928
    art = src.crop((round(48 * s), 0, round(885 * s), round(300 * s)))
    w = 168
    art = art.resize((w, round(art.height * w / art.width)), Image.Resampling.NEAREST)
    im = Image.new('RGBA', (w, art.height))
    im.alpha_composite(art)
    fit_text(im, caption, (w // 2, round(art.height * 0.62) - 4), w, '#ffe9a8')
    return im


def gold_button(caption, width):
    im = Image.new('RGBA', (width, 18))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, width - 1, 17), fill='#c98d2c', outline='#5a3610')
    d.rectangle((1, 1, width - 2, 16), outline=GOLD)
    d.line((2, 2, width - 3, 2), fill='#ffd88a')
    text(im, caption, (width // 2, 5), color='#fff6dc')
    return im


def cyan_button(caption, width=72):
    im = Image.new('RGBA', (width, 18))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, width - 1, 17), fill=NAVY, outline=CYAN)
    d.rectangle((1, 1, width - 2, 16), outline=CYAN2)
    d.line((2, 2, width - 3, 2), fill='#2a3a72')
    d.rectangle((1, 1, 16, 16), fill=NAVY2, outline=GOLD2)       # hueco del objeto real
    fit_text(im, caption, (18 + (width - 19) // 2, 5), width - 19, '#e8f8ff')
    return im


def inventory(im):
    d = ImageDraw.Draw(im)
    d.line((X0, 168, X0 + 161, 168), fill=GOLD2)
    text(im, 'Inventario', (X0 + 30, 169), color='#7f8fb8')
    for row in range(4):
        for col in range(9):
            x, y = X0 + col * 18, (179 + row * 18) if row < 3 else 237
            d.rectangle((x, y, x + 17, y + 17), fill='#0c1230', outline='#3a4a7a')


def base(band=True):
    im = frame()
    d = ImageDraw.Draw(im)
    d.rectangle((24, 50, SIZE[0] - 25, SIZE[1] - 24), fill=NAVY)
    if band:
        # Cinta del titulo: el texto de la ventana cae en y 45-52 (cofre: x 8, y 6).
        d.rectangle((26, 42, SIZE[0] - 27, 55), fill='#0d1430', outline=GOLD)
        d.line((27, 43, SIZE[0] - 28, 43), fill='#f6d27a')
        d.line((27, 54, SIZE[0] - 28, 54), fill=GOLD2)
        c = compass()
        im.alpha_composite(c, ((SIZE[0] - c.width) // 2, 9))
    return im


def general_panel():
    im = base()
    d = ImageDraw.Draw(im)
    for slot in range(45):
        x, y = slot_xy(slot)
        d.rectangle((x, y, x + 17, y + 17), fill='#141d42', outline='#22305f')
    d.rectangle((X0 - 1, Y0 + 5 * 18 - 1, X0 + 162, Y0 + 6 * 18), fill='#0d1430')
    for slot in (45, 47, 49, 51, 53):
        x, y = slot_xy(slot)
        d.rectangle((x, y, x + 17, y + 17), fill='#1b2652', outline=GOLD2)
    inventory(im)
    return im


INGREDIENTS = [14, 15, 16, 23, 24, 25, 32, 33, 34]
OUTPUT, FORGE = 20, (39, 40, 41)


def receta_panel():
    im = base()
    d = ImageDraw.Draw(im)
    # Marco dorado del resultado (3x3 casillas, el item va en el centro).
    x0, y0 = slot_xy(10)
    d.rectangle((x0 - 1, y0 - 1, x0 + 54, y0 + 54), fill='#0d1430', outline=GOLD)
    d.rectangle((x0, y0, x0 + 53, y0 + 53), outline=GOLD2)
    x, y = slot_xy(OUTPUT)
    d.rectangle((x, y, x + 17, y + 17), fill='#24316a', outline='#f6d27a')
    text(im, 'RESULTADO', (x0 + 27, Y0 - 1 + 4), color='#f6d27a')
    # Flecha hacia el resultado.
    ax, ay = slot_xy(22)
    d.polygon(((ax + 15, ay + 4), (ax + 15, ay + 14), (ax + 3, ay + 9)), fill=GOLD, outline='#5a3610')
    d.rectangle((ax + 14, ay + 7, ax + 17, ay + 11), fill=GOLD)
    sx, sy = slot_xy(INGREDIENTS[0])
    text(im, 'NECESITAS', (sx + 27, Y0 - 1 + 4), color='#9fdcf0')
    for slot in INGREDIENTS:
        x, y = slot_xy(slot)
        d.rectangle((x, y, x + 17, y + 17), fill='#141d42', outline=CYAN2)
    fx, fy = slot_xy(FORGE[0])
    im.alpha_composite(gold_button('FORJAR', 54), (fx, fy))
    d.rectangle((X0 - 1, Y0 + 5 * 18 - 1, X0 + 162, Y0 + 6 * 18), fill='#0d1430')
    for slot in (45, 53):
        x, y = slot_xy(slot)
        d.rectangle((x, y, x + 17, y + 17), fill='#1b2652', outline=GOLD2)
    inventory(im)
    return im


def index_panel(page_entries, page, total):
    im = base(band=False)
    rib = ribbon('GUIA ASTRAL')
    im.alpha_composite(rib, ((SIZE[0] - rib.width) // 2, 0))
    for n, entry in enumerate(page_entries):
        x, y = slot_xy(button_slots(n)[0])
        im.alpha_composite(cyan_button(entry['short']), (x, y))
    if page > 0:
        im.alpha_composite(gold_button('<', 18), slot_xy(45))
    if page < total - 1:
        im.alpha_composite(gold_button('>', 18), slot_xy(53))
    im.alpha_composite(gold_button('CERRAR', 54), slot_xy(48))
    text(im, f'{page + 1}/{total}', (slot_xy(46)[0] + 18, slot_xy(46)[1] + 5), color='#9fdcf0')
    inventory(im)
    return im


def glyph_pair(im, chars, name, files, providers, advances):
    a, b, c, e = chars
    for n, (part, ascent, char, rewind) in enumerate(((im.crop((0, 0, 224, SPLIT)), 53, a, b),
                                                      (im.crop((0, SPLIT, 224, SIZE[1])), -3, c, e))):
        resource = f'font/guia_astral/{name}_{n}.png'
        files['assets/astral/textures/' + resource] = png(part)
        providers.append({'type': 'bitmap', 'file': 'astral:' + resource, 'height': part.height,
                          'ascent': ascent, 'chars': [char]})
        advances[rewind] = -(part.getbbox()[2] + 1)


def big_model(files, name, texture, scale, down=0):
    """Item que se dibuja grande en la casilla (ilustraciones y retratos); down baja el dibujo en px."""
    files[f'assets/astral/models/atlas_ui/{name}.json'] = json.dumps({
        'parent': 'minecraft:item/generated', 'gui_light': 'front', 'textures': {'layer0': texture},
        'display': {'gui': {'scale': [scale, scale, 1], 'translation': [0, -down, 0]}}}).encode()
    files[f'assets/astral/items/atlas_ui/{name}.json'] = json.dumps({
        'oversized_in_gui': scale > 1, 'model': {'type': 'minecraft:model', 'model': f'astral:atlas_ui/{name}'}}).encode()


def assets(source=None):
    data = load() if source is None else source
    files, providers, advances = {}, [], {START: -32, END: 32}
    advances.update({ch: n for n, ch in SHIFT.items()})
    groups = pages(entries(data))
    for page, chunk in enumerate(groups):
        glyph_pair(index_panel(chunk, page, len(groups)), PAGE_CHARS[page], f'pagina{page}', files, providers, advances)
    glyph_pair(general_panel(), BG_CHARS['general'], 'general', files, providers, advances)
    glyph_pair(receta_panel(), BG_CHARS['receta'], 'receta', files, providers, advances)
    providers.append({'type': 'space', 'advances': advances})
    # Ilustraciones de seccion (arte propio de Gemini): textura de item + modelo grande.
    for name in sorted(set(data['ilustraciones'].values())):
        path = GEMINI / (name + '.png')
        if path.exists():
            files[f'assets/astral/textures/item/atlas_ui/ilus_{name}.png'] = path.read_bytes()
            big_model(files, 'ilus_' + name, f'astral:item/atlas_ui/ilus_{name}', 2, down=8)
    return files, providers


def portrait_assets(pack_files, source=None):
    """Retratos del Bestiario (solo en el FINAL privado: algunos modelos son de terceros)."""
    data = load() if source is None else source
    files = {}
    for mid in sorted(set(data['retratos'].values())):
        src = pack_files.get(f'assets/astral/textures/gui/atlas/mobs/{mid}.png')
        if src is None:
            continue
        files[f'assets/astral/textures/item/atlas_ui/mob_{mid}.png'] = src
        big_model(files, 'mob_' + mid, f'astral:item/atlas_ui/mob_{mid}', 3, down=16)
        big_model(files, 'mobchico_' + mid, f'astral:item/atlas_ui/mob_{mid}', 1)
    return files


def title(chars, caption=''):
    a, b, c, e = chars
    out = '&f' + START + a + b + c + e + END
    if caption:
        caption = caption.replace('Atlas Celestial · ', '')
        caption = ''.join(ch if ch in glyphs() else {'–': '-', '·': '-', '→': '>', '←': '<'}.get(ch, '') for ch in
                          __import__('unicodedata').normalize('NFKD', caption))
        while text_width(caption) > 160:
            caption = caption[:-2].rstrip() + '.'
        shift = 80 - text_width(caption) // 2
        for n in sorted(SHIFT, reverse=True):
            while shift >= n:
                out += SHIFT[n]
                shift -= n
        out += TITLE_COLOR + caption
    return out


# ---------------------------------------------------------------- menus

def menu_name(key):
    return 'g_' + re.sub(r'[^a-z0-9_]', '_', key.lower())


def entries(data):
    out = []
    for e in data['index']:
        target, command = e.get('dialog'), e.get('command')
        key = (target.split('/', 2)[-1] if '/seccion/' in target else target.split('/', 1)[1]) if target else 'misiones'
        short, iid = SHORT.get(key, (e['caption'][:10], None))
        icon = e.get('icons', {}).get(iid) if iid else None
        out.append(dict(caption=e['caption'], short=short,
                        command=f'[openguimenu] {menu_name(target)}' if target else '[player] ' + command.lstrip('/'),
                        icon=icon or {'id': FALLBACK.get(key, 'minecraft:book')}))
    return out


def pages(items):
    return [items[i:i + PER_PAGE] for i in range(0, len(items), PER_PAGE)]


def index_menus(data):
    groups = pages(entries(data))
    out = {}
    menu_id = lambda p: MENU if p == 0 else f'{MENU}_{p + 1}'
    for page, chunk in enumerate(groups):
        lines = [f'menu_title: {q(title(PAGE_CHARS[page]))}', 'size: 54']
        if page == 0:
            lines += [f'open_command: {COMMAND}', 'register_command: true']
        lines.append('items:')
        for n, entry in enumerate(chunk):
            cmds = ['[sound] UI_BUTTON_CLICK', entry['command']]
            icon = stack_item(entry['icon'])
            icon.update(name='&b' + entry['caption'], lore=['&7Clic para abrir'])
            for k, slot in enumerate(button_slots(n)):
                it = icon if k == 0 else dict(name=icon['name'], lore=icon['lore'], model='astral:viajes/blank')
                lines += yaml_item(f'b{n}_{k}', slot, it, cmds)
        if page > 0:
            lines += yaml_item('anterior', 45, dict(name='&ePagina anterior', model='astral:viajes/blank'),
                               ['[sound] UI_BUTTON_CLICK', f'[openguimenu] {menu_id(page - 1)}'])
        if page < len(groups) - 1:
            lines += yaml_item('siguiente', 53, dict(name='&eSiguiente pagina', model='astral:viajes/blank'),
                               ['[sound] UI_BUTTON_CLICK', f'[openguimenu] {menu_id(page + 1)}'])
        for k, slot in enumerate((48, 49, 50)):
            lines += yaml_item(f'cerrar_{k}', slot, dict(name='&cCerrar', model='astral:viajes/blank'), ['[close]'])
        out[menu_id(page)] = '\n'.join(lines) + '\n'
    return out


NAV_WORDS = {'volver': 'back', 'siguiente': 'next', 'anterior': 'prev', 'cerrar': 'close', '←': 'prev'}


def nav_kind(label):
    low = label.strip().lower()
    for word, kind in NAV_WORDS.items():
        if low.startswith(word):
            return kind
    if low.endswith('→'):
        return 'next'
    return None


def click(action):
    if not action:
        return ['[close]']
    if action.get('type') == 'show_dialog':
        key = action['dialog'].split(':', 1)[1]
        if key == 'atlas/indice' or key == 'guia':
            return [f'[openguimenu] {MENU}']
        return [f'[openguimenu] {menu_name(key)}']
    if action.get('type') == 'run_command':
        cmd = action['command'].lstrip('/')
        if cmd == COMMAND:
            return [f'[openguimenu] {MENU}']
        return ['[player] ' + cmd]
    return ['[close]']


def representative(data, key, depth=0):
    """Item que representa a una ventana (para su boton): el primero que tenga adentro."""
    d = data['dialogs'].get(key)
    if not d or depth > 3:
        return None
    rid = recipe_id(d)
    if rid and rid in data['recetas']:
        return data['recetas'][rid]['out']
    for b in d.get('body', []):
        if b['type'] == 'minecraft:item':
            return b['item']
    for a in d.get('actions', []):
        act = a.get('action', {})
        if act.get('type') == 'show_dialog' and not nav_kind(plain(a['label'])):
            found = representative(data, act['dialog'].split(':', 1)[1], depth + 1)
            if found:
                return found
    return None


def recipe_id(d):
    for a in d.get('actions', []):
        m = re.search(r'trigger astral\.forja set (\d+)', a.get('action', {}).get('command', ''))
        if m:
            return m.group(1)
    return None


def cards_from_text(messages):
    """Parrafos -> tarjetas: un TITULO EN MAYUSCULAS se junta con el texto que le sigue."""
    cards, current = [], None
    for comp in messages:
        lines = [l for l in legacy(comp, 'gray') if plain(l).strip()]
        if not lines:
            continue
        txt = plain(comp).strip()
        if txt.isupper() and len(txt) <= 40:
            current = dict(name='&6&l' + txt.title(), lore=[])
            cards.append(current)
            continue
        if current is not None and not current['lore']:
            current['lore'] = wrap(lines)
            current = None
            continue
        current = None
        head, sep, rest = txt.partition(': ')
        if sep and len(head) <= 26:
            cards.append(dict(name='&6' + head, lore=wrap(['&7' + rest])))
        elif len(txt) <= 32:
            cards.append(dict(name=lines[0], lore=[]))
        else:
            cards.append(dict(name='&6Informacion', lore=wrap(lines)))
    for c in cards:
        c.update(material='KNOWLEDGE_BOOK', model=INFO_MODEL)
    return cards


def content_slots(count, top_reserved):
    """Casillas de contenido en filas centradas (filas 0-4; con ilustracion arriba, desde la fila 2)."""
    rows = list(range(2, 5)) if top_reserved else list(range(5))
    per_row = 7 if count <= 7 * len(rows) else 9
    slots, left = [], count
    for r in rows:
        n = min(per_row, left)
        if n <= 0:
            break
        start = (9 - n) // 2 if per_row == 7 or n < 9 else 0
        slots += [r * 9 + start + i for i in range(n)]
        left -= n
    if left > 0 and top_reserved:            # sobra: usar los costados de arriba
        extra = [s for r in (0, 1) for s in (r * 9 + c for c in (0, 1, 2, 6, 7, 8))]
        slots += extra[:left]
    return slots


def dialog_menus(data):
    out = {}
    for key, d in data['dialogs'].items():
        name = menu_name(key)
        caption = plain(d.get('title', ''))
        rid = recipe_id(d)
        nav, cards, items, buttons, ilus, portrait = {}, [], [], [], None, None
        texts = []
        for b in d.get('body', []):
            if b['type'] == 'minecraft:item':
                it = stack_item(b['item'])
                desc = b.get('description')
                if desc:
                    extra = [l for l in legacy(desc.get('contents', desc) if isinstance(desc, dict) and 'contents' in desc else desc, 'gray') if plain(l).strip()]
                    if extra and plain(extra[0]).strip() == plain(it['name']).strip():
                        extra = extra[1:]
                    it['lore'] = it['lore'] + ([''] if it['lore'] and extra else []) + wrap(extra)
                items.append((it, []))
                continue
            raw = json.dumps(b.get('contents', ''), ensure_ascii=False)
            chars = re.findall('[--]', json.loads(raw) if False else ''.join(
                x.get('text', '') if isinstance(x, dict) else x for x in (b['contents'] if isinstance(b['contents'], list) else [b['contents']])))
            for ch in chars:
                if ch in data['ilustraciones']:
                    ilus = data['ilustraciones'][ch]
                if ch in data['retratos']:
                    portrait = data['retratos'][ch]
            texts.append(b['contents'])
        cards = cards_from_text(texts)
        actions = list(d.get('actions', []))
        for field in ('action', 'exit_action'):
            if field in d:
                actions.append(d[field])
        for a in actions:
            label = plain(a.get('label', ''))
            kind = nav_kind(label)
            act = a.get('action')
            if kind:
                nav[kind] = click(act)
                continue
            if act and act.get('type') == 'run_command' and 'astral.forja' in act.get('command', ''):
                nav['forge'] = click(act)
                continue
            target = act.get('dialog', '').split(':', 1)[1] if act and act.get('type') == 'show_dialog' else None
            rep = representative(data, target) if target else None
            if target and target in data['dialogs'] and recipe_id(data['dialogs'][target]):
                it = stack_item(rep) if rep else dict(material='BOOK')
                it['lore'] = it.get('lore', []) + ['', '&e» Clic: ver la receta']
            else:
                it = stack_item(rep) if rep else dict(material='BOOK', model=INFO_MODEL)
                it['name'] = '&b' + PRIVATE.sub('', label).strip()
                it['lore'] = ['&7Clic para abrir']
                it['amount'] = 1
            if target and target.startswith('atlas/criatura/'):
                mid = target.split('/')[-1]
                it.update(material='PAPER', model=f'astral:atlas_ui/mobchico_{mid}')
            buttons.append((it, click(act)))
        if rid and rid in data['recetas']:
            out[name] = recipe_menu(name, caption, data['recetas'][rid], nav, cards)
            continue
        content = [(c, []) for c in cards] + items + buttons
        reserved = bool(ilus or portrait)
        lines = [f"menu_title: {q(title(BG_CHARS['general'], caption))}", 'size: 54', 'items:']
        if portrait:
            lines += yaml_item('retrato', 4, dict(material='PAPER', name='&f' + caption.split('· ')[-1],
                                                  model=f'astral:atlas_ui/mob_{portrait}'))
        elif ilus:
            lines += yaml_item('ilustracion', 4, dict(material='PAPER', name='&f' + caption,
                                                      model=f'astral:atlas_ui/ilus_{ilus}'))
        slots = content_slots(len(content), reserved)
        if len(slots) < len(content):
            raise ValueError(f'{key}: {len(content)} cosas no entran en una ventana')
        for n, ((it, cmds), slot) in enumerate(zip(content, slots)):
            lines += yaml_item(f'c{n}', slot, it, (['[sound] UI_BUTTON_CLICK'] + cmds) if cmds else ())
        lines += nav_items(nav)
        out[name] = '\n'.join(lines) + '\n'
    return out


def nav_items(nav):
    lines = []
    back = nav.get('back', [f'[openguimenu] {MENU}'])
    lines += yaml_item('volver', 45, dict(name='&eVolver', model=NAV_MODELS['back']), ['[sound] UI_BUTTON_CLICK'] + back)
    if 'prev' in nav:
        lines += yaml_item('anterior', 47, dict(name='&eAnterior', model=NAV_MODELS['back']), ['[sound] UI_BUTTON_CLICK'] + nav['prev'])
    if 'next' in nav:
        lines += yaml_item('siguiente', 51, dict(name='&eSiguiente', model=NAV_MODELS['next']), ['[sound] UI_BUTTON_CLICK'] + nav['next'])
    lines += yaml_item('indice', 49, dict(name='&bIndice de la Guia', model=NAV_MODELS['info']), ['[sound] UI_BUTTON_CLICK', f'[openguimenu] {MENU}'])
    lines += yaml_item('cerrar', 53, dict(name='&cCerrar', model=NAV_MODELS['close']), ['[close]'])
    return lines


def recipe_menu(name, caption, recipe, nav, cards):
    lines = [f"menu_title: {q(title(BG_CHARS['receta'], caption))}", 'size: 54', 'items:']
    out = stack_item(recipe['out'])
    lines += yaml_item('resultado', OUTPUT, out)
    for n, ing in enumerate(recipe['ings']):
        if 'stack' in ing:
            it = stack_item(ing['stack'])
        else:
            ident = ing['id']
            material = 'POTION' if ident == 'water_bottle' else ident.split(':')[-1].upper()
            it = dict(material=material, name='&f' + ing['name'].capitalize(), amount=max(1, min(64, ing['count'])))
            if ing['count'] > 64:
                it['lore'] = [f"&7Cantidad: &f{ing['count']}"]
        it['name'] = f"&f{ing['count']}x " + re.sub(r'^(&(#[0-9a-fA-F]{6}|[0-9a-fk-or]))+', '', it['name'])
        slot = INGREDIENTS[n] if n < len(INGREDIENTS) else 42 + n - len(INGREDIENTS)
        lines += yaml_item(f'material{n}', slot, it)
    tip = ['&7Sacas los materiales de tu inventario.', '&7Tenes que estar al lado de una', '&7Mesa de Herreria.']
    for k, slot in enumerate(FORGE):
        lines += yaml_item(f'forjar{k}', slot, dict(name='&6&lForjar', lore=tip, model='astral:viajes/blank'),
                           ['[sound] UI_BUTTON_CLICK', '[close]'] + nav.get('forge', []))
    nav = {k: v for k, v in nav.items() if k != 'forge'}
    lines += yaml_item('volver', 45, dict(name='&eVolver', model=NAV_MODELS['back']),
                       ['[sound] UI_BUTTON_CLICK'] + nav.get('back', [f'[openguimenu] {MENU}']))
    lines += yaml_item('cerrar', 53, dict(name='&cCerrar', model=NAV_MODELS['close']), ['[close]'])
    return '\n'.join(lines) + '\n'


def menus(data=None):
    data = load() if data is None else data
    out = index_menus(data)
    out.update(dialog_menus(data))
    return out


def write(out_dir, data=None):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in list(out_dir.glob('g_*.yml')):
        old.unlink()
    result = menus(data)
    for name, body in result.items():
        (out_dir / f'{name}.yml').write_text(body, encoding='utf-8')
    # Lista para pegar en plugins/DeluxeMenus/config.yml (gui_menus:), aparte de la de menus.py.
    (out_dir.parent / 'config-guia.yml').write_text(
        '# Guia Astral (guia_cofre.py): pegar en config.yml, dentro de gui_menus:\n' +
        ''.join(f'  {n}:\n    file: {n}.yml\n' for n in result), encoding='utf-8')
    return list(result)


def preview(target, data=None):
    data = load() if data is None else data
    groups = pages(entries(data))
    panels = [index_panel(c, p, len(groups)) for p, c in enumerate(groups)] + [general_panel(), receta_panel()]
    sheet = Image.new('RGBA', (SIZE[0] * len(panels), SIZE[1]), '#0b0b12')
    for n, im in enumerate(panels):
        sheet.alpha_composite(im, (n * SIZE[0], 0))
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.Resampling.NEAREST).save(target)


if __name__ == '__main__':
    names = write(ROOT.parent / 'build/menus/DeluxeMenus/gui_menus')
    preview(ROOT.parent / 'build/previews/guia_astral_cofre.png')
    print('menus:', len(names))
