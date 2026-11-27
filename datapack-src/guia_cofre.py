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
SHIFT = {1 << k: chr(0xf240 + k) for k in range(8)}          # espacios +1..+128 para centrar el titulo

# Etiqueta corta (entra en el boton del indice) y objeto real que se muestra, por destino.
SHORT = {
    'como': ('Inicio', 'nucleo_astral'), 'mercader': ('Goblin', 'peluche_zombie_horse'),
    'consumibles': ('XP/Suerte', 'frasco_xp_gigante'), 'proteccion': ('Terrenos', 'cuero_tratado'),
    'cocina': ('Comida', 'manzana_esmeralda'), 'misiones': ('Misiones', 'gema_luminica'),
    'crafteos': ('Crafteos', None), 'stellarity': ('Stellarity', None),
    'materiales': ('Materiales', 'cristal_arcano'), 'berserker': ('Berserker', 'espada_1'),
    'mago': ('Mago', 'baston_1'), 'arquero': ('Arquero', 'arco_1'), 'lanzas': ('Lanzas', 'lanza_1'),
    # 23/11 pedido del dueno: las clases nuevas muestran su arma (antes salia un libro vanilla).
    'segador': ('Segador', 'guadana_1'), 'invocador': ('Invocador', 'libro_invocador_1'),
    'asesino': ('Asesino', 'cuchillo_1'),
    'talismanes': ('Talismanes', 'corazon_fin'), 'especiales': ('Especiales', 'gancho'),
    'taladros': ('Taladros', 'taladro_diamante'), 'motosierras': ('Sierras', 'motosierra_basica'),
    'carnivora': ('Carnivora', 'carnivora_espada'), 'asura': ('Asura', 'asura_espada'), 'agua': ('Agua', 'agua_espada'),
    'oficios': ('Oficios', 'lampara_minero'), 'mascotas_1': ('Mascotas', 'peluche_ocelot'),
    'bestiario/1': ('Bestiario', None), 'drops': ('Drops', None),
}
FALLBACK = {'bestiario/1': 'minecraft:zombie_head', 'drops': 'minecraft:chest', 'misiones': 'minecraft:writable_book'}
FALLBACK.update(crafteos='minecraft:crafting_table', stellarity='minecraft:end_stone')
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
    from guia_ampliacion import extend_source
    return extend_source(json.loads(SOURCE.read_text(encoding='utf-8')))


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
        # En la guia no va la lista "Material para: ..." (hace el cartel larguisimo).
        if plain(line).strip().lower().startswith(('material para', 'se usa en', 'sirve para')):
            continue
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


HI = 4                                   # el fondo se dibuja a 4x: el arte de Gemini se ve fino, no pixelado
TILE = 256                               # Minecraft no carga glifos de mas de 256 px: el fondo va en cuadros
ORIGINAL = GEMINI / 'original'


def clean(im, tolerance=40):
    """Quita el fondo liso de la hoja de Gemini (relleno desde los bordes)."""
    from PIL import ImageDraw as _D
    rgb = im.convert('RGB')
    w, h = rgb.size
    marker = (1, 254, 3)
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)] + [(x, 0) for x in range(0, w, 37)] + \
                [(x, h - 1) for x in range(0, w, 37)] + [(0, y) for y in range(0, h, 37)] + [(w - 1, y) for y in range(0, h, 37)]:
        if rgb.getpixel((x, y)) != marker:
            _D.floodfill(rgb, (x, y), marker, thresh=tolerance)
    out = im.convert('RGBA')
    px, src = out.load(), rgb.load()
    for y in range(h):
        for x in range(w):
            if src[x, y] == marker:
                px[x, y] = (0, 0, 0, 0)
    return out


_ART = {}


def art(name):
    if name not in _ART:
        _ART[name] = clean(Image.open(ORIGINAL / f'{name}.png'))
    return _ART[name]


def frame_hi():
    """Ventana vacia de Gemini (original) en nueve partes, a 4x."""
    src = art('atlas_ventana_vacia')
    sx, sy = [0, 100, 728, src.width], [0, 128, 918, src.height]
    k = 24 * HI / sx[1]
    W, H = SIZE[0] * HI, SIZE[1] * HI
    dx = [0, 24 * HI, W - 24 * HI, W]
    dy = [16 * HI, 16 * HI + round(sy[1] * k), H - round((src.height - sy[2]) * k), H]
    out = Image.new('RGBA', (W, H))
    for r in range(3):
        for c in range(3):
            piece = src.crop((sx[c], sy[r], sx[c + 1], sy[r + 1]))
            out.alpha_composite(piece.resize((dx[c + 1] - dx[c], dy[r + 1] - dy[r]), Image.Resampling.LANCZOS), (dx[c], dy[r]))
    return out


def compass_hi():
    src = art('atlas_cabecera_botones_finos')
    return src.crop((375, 0, 560, 185)).resize((34 * HI, 34 * HI), Image.Resampling.LANCZOS)


def ribbon_hi(width=168):
    src = art('atlas_cabecera_botones_finos')
    piece = src.crop((48, 0, 885, 300))
    return piece.resize((width * HI, round(piece.height * width * HI / piece.width)), Image.Resampling.LANCZOS)


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


def overlay(band=True):
    """Capa de 1x (casillas, textos, botones): se agranda sin suavizar para que quede nitida."""
    ov = Image.new('RGBA', SIZE)
    d = ImageDraw.Draw(ov)
    d.rectangle((24, 50, SIZE[0] - 25, SIZE[1] - 24), fill=NAVY)
    if band:
        # Cinta del titulo: el texto de la ventana cae en y 45-52 (cofre: x 8, y 6).
        d.rectangle((26, 42, SIZE[0] - 27, 55), fill='#0d1430', outline=GOLD)
        d.line((27, 43, SIZE[0] - 28, 43), fill='#f6d27a')
        d.line((27, 54, SIZE[0] - 28, 54), fill=GOLD2)
    return ov


def compose(ov, top=None, compass=False):   # la ventana de Gemini ya trae su brujula
    hi = frame_hi()
    hi.alpha_composite(ov.resize((SIZE[0] * HI, SIZE[1] * HI), Image.Resampling.NEAREST))
    if top is not None:
        art_im, (x, y) = top
        hi.alpha_composite(art_im, (x, y))
    if compass:
        c = compass_hi()
        hi.alpha_composite(c, ((SIZE[0] * HI - c.width) // 2, 9 * HI))
    return hi


def general_panel():
    ov = overlay()
    d = ImageDraw.Draw(ov)
    for slot in range(45):
        x, y = slot_xy(slot)
        d.rectangle((x, y, x + 17, y + 17), fill='#141d42', outline='#22305f')
    d.rectangle((X0 - 1, Y0 + 5 * 18 - 1, X0 + 162, Y0 + 6 * 18), fill='#0d1430')
    for slot in (45, 47, 49, 51, 53):
        x, y = slot_xy(slot)
        d.rectangle((x, y, x + 17, y + 17), fill='#1b2652', outline=GOLD2)
    inventory(ov)
    return compose(ov)


INGREDIENTS = [14, 15, 16, 23, 24, 25, 32, 33, 34]
OUTPUT, FORGE = 20, (39, 40, 41)


def receta_panel(method='FORJAR'):
    ov = overlay()
    d = ImageDraw.Draw(ov)
    x0, y0 = slot_xy(10)
    d.rectangle((x0 - 1, y0 - 1, x0 + 54, y0 + 54), fill='#0d1430', outline=GOLD)
    d.rectangle((x0, y0, x0 + 53, y0 + 53), outline=GOLD2)
    x, y = slot_xy(OUTPUT)
    d.rectangle((x, y, x + 17, y + 17), fill='#24316a', outline='#f6d27a')
    text(ov, 'RESULTADO', (x0 + 27, Y0 - 1 + 4), color='#f6d27a')
    ax, ay = slot_xy(22)
    d.polygon(((ax + 15, ay + 4), (ax + 15, ay + 14), (ax + 3, ay + 9)), fill=GOLD, outline='#5a3610')
    d.rectangle((ax + 14, ay + 7, ax + 17, ay + 11), fill=GOLD)
    sx, sy = slot_xy(INGREDIENTS[0])
    text(ov, 'NECESITAS', (sx + 27, Y0 - 1 + 4), color='#9fdcf0')
    for slot in INGREDIENTS:
        x, y = slot_xy(slot)
        d.rectangle((x, y, x + 17, y + 17), fill='#141d42', outline=CYAN2)
    fx, fy = slot_xy(FORGE[0])
    ov.alpha_composite(gold_button(method, 54), (fx, fy))
    d.rectangle((X0 - 1, Y0 + 5 * 18 - 1, X0 + 162, Y0 + 6 * 18), fill='#0d1430')
    for slot in (45, 53):
        x, y = slot_xy(slot)
        d.rectangle((x, y, x + 17, y + 17), fill='#1b2652', outline=GOLD2)
    inventory(ov)
    return compose(ov)


def index_panel(page_entries, page, total):
    ov = overlay(band=False)
    rib = ribbon_hi()
    rh = rib.height // HI
    # El texto va en la cinta azul del dibujo (62 % de su alto).
    fit_text(ov, 'GUIA ASTRAL', (SIZE[0] // 2, round(rh * 0.62) - 4), 160, '#ffe9a8')
    for n, entry in enumerate(page_entries):
        x, y = slot_xy(button_slots(n)[0])
        ov.alpha_composite(cyan_button(entry['short']), (x, y))
    if page > 0:
        ov.alpha_composite(gold_button('<', 18), slot_xy(45))
    if page < total - 1:
        ov.alpha_composite(gold_button('>', 18), slot_xy(53))
    ov.alpha_composite(gold_button('CERRAR', 54), slot_xy(48))
    text(ov, f'{page + 1}/{total}', (slot_xy(46)[0] + 18, slot_xy(46)[1] + 5), color='#9fdcf0')
    inventory(ov)
    hi = frame_hi()
    hi.alpha_composite(rib, ((SIZE[0] * HI - rib.width) // 2, 0))
    hi.alpha_composite(ov.resize((SIZE[0] * HI, SIZE[1] * HI), Image.Resampling.NEAREST))
    return hi


# Fondo = 4 x 5 cuadros. Cada fondo tiene 20 caracteres; NEG pega los cuadros (los glifos dejan 1 px) y
# ROW vuelve al principio de la fila.
COLS, ROWS = -(-SIZE[0] * HI // TILE), -(-SIZE[1] * HI // TILE)
NEG, ROW = '', ''
BACKGROUNDS = ['pagina0', 'pagina1', 'pagina2', 'pagina3', 'pagina4', 'general', 'receta']


def bg_chars(n):
    # 23/11: antes 0xF300+, que choca con ventanas_19_11 (0xF300/F301 y 0xF310+: Cavernas tapaba la pagina 1).
    return tuple(chr(0xE200 + n * 32 + i) for i in range(COLS * ROWS))


PAGE_CHARS = [bg_chars(n) for n in range(5)]
BG_CHARS = {'general': bg_chars(5), 'receta': bg_chars(6)}
BG_CHARS['receta_stellarity'] = bg_chars(7)


def tiles(hi, chars, name, files, providers):
    for r in range(ROWS):
        for c in range(COLS):
            box = (c * TILE, r * TILE, min((c + 1) * TILE, hi.width), min((r + 1) * TILE, hi.height))
            part = hi.crop(box)
            # Punto casi invisible arriba a la derecha: el juego mide el ancho hasta el ultimo pixel no transparente.
            if part.getpixel((part.width - 1, 0))[3] == 0:
                part.putpixel((part.width - 1, 0), (0, 0, 0, 1))
            resource = f'font/guia_astral/{name}_{r}_{c}.png'
            files['assets/astral/textures/' + resource] = png(part)
            # La fila r empieza en y = 64r (en pixeles de pantalla del juego); la parte de arriba del
            # dibujo queda 53 px sobre la linea del titulo, igual que las demas ventanas.
            providers.append({'type': 'bitmap', 'file': 'astral:' + resource, 'height': part.height // HI,
                              'ascent': 53 - r * TILE // HI, 'chars': [chars[r * COLS + c]]})


def big_model(files, name, texture, scale, down=0):
    """Item que se dibuja grande en la casilla (ilustraciones y retratos); down baja el dibujo en px."""
    files[f'assets/astral/models/atlas_ui/{name}.json'] = json.dumps({
        'parent': 'minecraft:item/generated', 'gui_light': 'front', 'textures': {'layer0': texture},
        'display': {'gui': {'scale': [scale, scale, 1], 'translation': [0, -down, 0]}}}).encode()
    files[f'assets/astral/items/atlas_ui/{name}.json'] = json.dumps({
        'oversized_in_gui': scale > 1, 'model': {'type': 'minecraft:model', 'model': f'astral:atlas_ui/{name}'}}).encode()


def assets(source=None):
    data = load() if source is None else source
    files, providers = {}, []
    advances = {START: -32, END: 32, NEG: -1, ROW: -SIZE[0]}
    advances.update({ch: n for n, ch in SHIFT.items()})
    groups = pages(entries(data))
    if len(groups) > len(PAGE_CHARS):
        raise ValueError('Mas paginas de indice que fondos reservados')
    for page, chunk in enumerate(groups):
        tiles(index_panel(chunk, page, len(groups)), PAGE_CHARS[page], f'pagina{page}', files, providers)
    tiles(general_panel(), BG_CHARS['general'], 'general', files, providers)
    tiles(receta_panel(), BG_CHARS['receta'], 'receta', files, providers)
    tiles(receta_panel('METODO'), BG_CHARS['receta_stellarity'], 'receta_stellarity', files, providers)
    providers.append({'type': 'space', 'advances': advances})
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


def background(chars):
    out = ''
    for r in range(ROWS):
        out += ''.join(ch + NEG for ch in chars[r * COLS:(r + 1) * COLS]) + ROW
    return out


def title(chars, caption=''):
    out = '&f' + START + background(chars) + END
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


PAGINA_DE = {}


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
            dest = entry['command'].split('[openguimenu] ', 1)[-1].strip()
            if page > 0 and entry['command'].startswith('[openguimenu] '):
                PAGINA_DE[dest] = menu_id(page)   # 23/11: Volver de una seccion vuelve a SU pagina del indice
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


# Secciones que solo tenian texto: se muestran con objetos reales (modelos del pack FINAL).
SHOWCASE = {
    'atlas/seccion/cocina': ('&6&lCocina - Crop & Kettle', [
        ('cnk:cooking_pot_item', 'Olla', 'Se fabrica con un caldero y una fogata. Ahi se cocinan las recetas.'),
        ('cnk.book:cookbook', 'Recetario', 'Muestra las recetas que vas descubriendo.'),
        ('cnk:cutting_board_item', 'Tabla de cortar', 'Para picar ingredientes.'),
        ('cnk:knife', 'Cuchillo', 'Se usa con la tabla de cortar.'),
        ('cnk:mixing_bowl_item', 'Bol', 'Para mezclar masas y salsas.'),
        ('cnk:grape_seeds', 'Semillas nuevas', 'Cultivos nuevos que crecen en survival.'),
        ('cnk:beef_cutlets', 'Comidas', 'Mas de cien recetas para cocinar.'),
        ('cnk:coffee', 'Bebidas', 'Cafe, vinos y mas.'),
        ('cnk:chef_hat', 'Gorro de chef', 'Se consigue cocinando.'),
    ]),
}
ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
CATALOG = {'armadura': 'Armaduras', 'espada': 'Espadas', 'hacha': 'Hachas', 'cuchillo': 'Cuchillos'}


def pretty_title(caption):
    """'Atlas Celestial · armadura 1 · 1/1' -> 'Armaduras I'; 'espada · 1/2' -> 'Espadas 1/2'."""
    caption = caption.replace('Atlas Celestial · ', '').replace('_', ' ')
    caption = re.sub(r' · 1/1$', '', caption)
    caption = re.sub(r' · (\d+/\d+)$', lambda m: ' ' + m.group(1), caption)
    m = re.match(r'(armadura|espada|hacha|cuchillo)(?: (\d+)(?!/))?(.*)$', caption)
    if m:
        tier = ' ' + ROMAN[int(m.group(2))] if m.group(2) and int(m.group(2)) < len(ROMAN) else ''
        caption = CATALOG[m.group(1)] + tier + m.group(3)
    return caption[:1].upper() + caption[1:]


def dialog_menus(data):
    out = {}
    for key, d in data['dialogs'].items():
        name = menu_name(key)
        caption = pretty_title(plain(d.get('title', '')))
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
        if key in SHOWCASE:
            # Seccion de puro texto: una sola tarjeta con la explicacion y los objetos reales de muestra.
            lore = wrap([l for c in cards for l in c['lore'] or [c['name']]])
            cards = [dict(material='KNOWLEDGE_BOOK', model=INFO_MODEL, name=SHOWCASE[key][0], lore=lore)]
            items += [(dict(material='PAPER', model=m, name='&f' + n, lore=['&7' + x for x in wrap([t], 36)]), [])
                      for m, n, t in SHOWCASE[key][1]]
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
                if mid.startswith('vanilla_'):
                    # 23/11: los mobs vanilla no tienen retrato en el pack (se veian violeta y negro): huevo de spawn.
                    it.pop('model', None)
                    it.update(material=mid[len('vanilla_'):].upper() + '_SPAWN_EGG')
                else:
                    it.update(material='PAPER', model=f'astral:atlas_ui/mobchico_{mid}')
            buttons.append((it, click(act)))
        if rid and rid in data['recetas']:
            out[name] = recipe_menu(name, caption, data['recetas'][rid], nav, cards)
            continue
        # Si un objeto ya es un boton (abre su receta), no se muestra repetido como imagen suelta.
        clickable = {it.get('model') for it, _ in buttons if it.get('model')}
        items = [(it, cmds) for it, cmds in items if not it.get('model') or it['model'] not in clickable]
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
        lines += nav_items(nav, name)
        out[name] = '\n'.join(lines) + '\n'
    return out


def volver_pagina(name, back):
    if name in PAGINA_DE:
        return [PAGINA_DE[name] and f'[openguimenu] {PAGINA_DE[name]}' if x.strip() == f'[openguimenu] {MENU}' else x for x in back]
    return back


def nav_items(nav, name=None):
    lines = []
    back = volver_pagina(name, nav.get('back', [f'[openguimenu] {MENU}']))
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
                       ['[sound] UI_BUTTON_CLICK'] + volver_pagina(name, nav.get('back', [f'[openguimenu] {MENU}'])))
    lines += yaml_item('cerrar', 53, dict(name='&cCerrar', model=NAV_MODELS['close']), ['[close]'])
    return '\n'.join(lines) + '\n'


# 23/11 pedido del dueno: mochilas (ExpendableBackpacks 1.2.0) en la Guia, con su receta real.
# Recetas sacadas del plugin (BackpackRecipes): cuero = LSL/LCL/LLL; cada mejora = 8 del material
# alrededor de la mochila anterior; Netherite en la Mesa de Herreria. Se entra desde "Terrenos y mochilas".
ENDER_PUBLICO = True
MOCHILAS_MENU = 'g_mochilas'
MOCHILAS = [('leather', 'Cuero', 9, '&6'), ('copper', 'Cobre', 18, '&#e0804a'), ('iron', 'Hierro', 27, '&f'),
            ('gold', 'Oro', 36, '&e'), ('diamond', 'Diamante', 45, '&b'), ('netherite', 'Netherite', 54, '&8'), ('ender', 'Ender', 27, '&3')]
MEJORA = {'copper': ('COPPER_INGOT', 'Lingote de cobre'), 'iron': ('IRON_INGOT', 'Lingote de hierro'),
          'gold': ('GOLD_INGOT', 'Lingote de oro'), 'diamond': ('DIAMOND', 'Diamante')}
GRILLA = [10, 11, 12, 19, 20, 21, 28, 29, 30]      # mesa 3x3 dibujada sobre el fondo general
FLECHA, RESULTADO, NOTA = 23, 25, 40


def mochila_item(n, lore=None):
    mat, nombre, espacios, color = MOCHILAS[n]
    return dict(material='PLAYER_HEAD', model=f'astral:mochila_{mat}', name=f'{color}Mochila de {nombre}',
                lore=lore if lore is not None else [f'&7{espacios} espacios'])


def mochila_menus():
    out = {}
    pagina = lambda n: f'g_mochila_{MOCHILAS[n][0]}'
    # Seccion: explicacion + las 6 mochilas (clic = su receta)
    lines = [f"menu_title: {q(title(BG_CHARS['general'], 'Mochilas'))}", 'size: 54', 'items:']
    lines += yaml_item('info', 13, dict(material='KNOWLEDGE_BOOK', model=INFO_MODEL, name='&6&lMochilas', lore=wrap([
        '&7Una mochila es un objeto: tenela en la mano y hace clic derecho para abrirla.',
        '&7Se fabrica la de Cuero en la Mesa de Crafteo y se mejora nivel por nivel. Tambien se compran en /shop -> Mochilas.',
        '&7Si moris, cae a tu tumba con todo lo que tiene adentro. ' + ('Solo la Mochila de Ender puede guardar otras mochilas.' if ENDER_PUBLICO else 'No se puede meter una mochila dentro de otra.')])))
    for n, slot in enumerate((21, 22, 23, 30, 31, 32, 40)):
        it = mochila_item(n, [f'&7{MOCHILAS[n][2]} espacios', '', '&e» Clic: ver como se fabrica'])
        lines += yaml_item(f'm{n}', slot, it, ['[sound] UI_BUTTON_CLICK', f'[openguimenu] {pagina(n)}'])
    lines += nav_items({'back': ['[openguimenu] g_atlas_seccion_proteccion']}, MOCHILAS_MENU)
    out[MOCHILAS_MENU] = '\n'.join(lines) + '\n'
    # Una ventana por mochila con la receta en su lugar real de la mesa 3x3
    for n, (mat, nombre, espacios, color) in enumerate(MOCHILAS):
        if mat == 'leather':
            L, S, C = (dict(material='LEATHER', name='&fCuero'), dict(material='STRING', name='&fHilo'),
                       dict(material='CHEST', name='&fCofre'))
            grilla, donde = [L, S, L, L, C, L, L, L, L], 'Mesa de Crafteo'
            como = ['&77 cuero, 1 hilo y 1 cofre en la Mesa de Crafteo.', '&7El hilo arriba al medio y el cofre en el centro.']
        elif mat == 'ender':
            E = dict(material='ENDER_EYE', name='&fOjo de ender')
            P = dict(material='ENDER_PEARL', name='&fPerla de ender')
            grilla = [E, P, E, P, dict(material='CHEST', name='&fCofre'), P,
                      E, dict(material='IRON_BLOCK', name='&fBloque de hierro'), E]
            donde = 'Mesa de Crafteo'
            como = wrap(['&7Todas las copias de la misma Mochila de Ender comparten lo que tiene adentro.',
                         '&7Copia sin forma: Mochila de Ender + perla de ender.'] +
                        (['&7Puede guardar mochilas normales, nunca otra de Ender.'] if ENDER_PUBLICO else []))
        elif mat == 'netherite':
            grilla = [None] * 9
            grilla[3:6] = [dict(material='NETHERITE_UPGRADE_SMITHING_TEMPLATE', name='&fPlantilla de mejora de netherite'),
                           mochila_item(n - 1), dict(material='NETHERITE_INGOT', name='&fLingote de netherite')]
            donde = 'Mesa de Herreria'
            como = ['&7En la Mesa de Herreria: plantilla de netherite,', '&7la Mochila de Diamante y 1 lingote de netherite.']
        else:
            material, ing = MEJORA[mat]
            M = dict(material=material, name='&f' + ing)
            grilla, donde = [M, M, M, M, mochila_item(n - 1), M, M, M, M], 'Mesa de Crafteo'
            como = [f'&7Pone la Mochila de {MOCHILAS[n - 1][1]} en el centro', f'&7y rodeala con 8 de {ing.lower()}.',
                    '&7Lo que tenia adentro se conserva.']
        lines = [f"menu_title: {q(title(BG_CHARS['general'], f'Mochila de {nombre}'))}", 'size: 54', 'items:']
        for k, (slot, it) in enumerate(zip(GRILLA, grilla)):
            if it:
                lines += yaml_item(f'g{k}', slot, it)
        lines += yaml_item('flecha', FLECHA, dict(name=f'&7{donde}', model=NAV_MODELS['next']))
        lines += yaml_item('resultado', RESULTADO, mochila_item(n, [f'&7{espacios} espacios', '&7Clic derecho para abrirla']))
        lines += yaml_item('como', NOTA, dict(material='KNOWLEDGE_BOOK', model=INFO_MODEL, name=f'&6&l{donde}', lore=como))
        nav = {'back': [f'[openguimenu] {MOCHILAS_MENU}']}
        if n > 0:
            nav['prev'] = [f'[openguimenu] {pagina(n - 1)}']
        if n < len(MOCHILAS) - 1:
            nav['next'] = [f'[openguimenu] {pagina(n + 1)}']
        lines += nav_items(nav, pagina(n))
        out[pagina(n)] = '\n'.join(lines) + '\n'
    return out


def menus(data=None):
    data = load() if data is None else data
    from guia_ampliacion import extend_source, menus as extension_menus
    data = extend_source(data)
    out = index_menus(data)
    out.update(dialog_menus(data))
    # Boton "Mochilas" dentro de Terrenos y mochilas (sin tocar el indice: su fondo trae los nombres dibujados).
    sec = menu_name('atlas/seccion/proteccion')
    boton = mochila_item(0, ['&7Como se fabrican y mejoran', '', '&e» Clic para abrir'])
    boton['name'] = '&bMochilas: recetas'
    out[sec] += '\n'.join(yaml_item('mochilas', 31, boton, ['[sound] UI_BUTTON_CLICK', f'[openguimenu] {MOCHILAS_MENU}'])) + '\n'
    out.update(mochila_menus())
    out.update(extension_menus(data))
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
