"""Cofre final de las mazmorras y la coleccion de Fragmentos Astrales.

Al tocar el cofre se abre una ventana con el marco de Mazmorras que muestra el botin:
fragmento del jefe (solo la primera vez), plata, un item Astral y materiales de elite.
Los fragmentos no se entregan como item: quedan guardados en /fragmentos (permiso
astral.fragmento.<id> de LuckPerms), asi nadie los pierde. Seran la llave del renacimiento.

Lo usan menus.py (ventanas de DeluxeMenus), build_pack.py (dibujos) y mobs/mazmorra.py.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from services_ui import png, SIZE, SPLIT, ornament, outlined, glyph_parts
from adventure_ui import START, END, label, star

ROOT = Path(__file__).resolve().parent.parent

# id, nombre, modelo encendido, de donde sale. En el orden de la historia.
FRAGMENTOS = [
    ("marea", "Fragmento de la Marea", "astral:fragmento_marea", "el Cangrejo de las playas"),
    ("pantano", "Fragmento del Pantano", "astral:fragmento_pantano", "el cofre del Bosque Sombrio"),
    ("arena", "Fragmento de la Arena", "astral:fragmento_arena", "el cofre de la Tumba del Rey de Arena"),
    ("lampara", "Lampara del Minero", "astral:cofre/lampara", "el cofre de las Minas Olvidadas"),
    ("hielo", "Fragmento de Hielo", "astral:fragmento_hielo", "el cofre de la Cumbre Helada"),
    ("fuego", "Fragmento de Fuego", "astral:fragmento_fuego", "el cofre del Corazon de la Forja"),
    ("corazon", "Corazon Astral", "astral:cofre/corazon", "el cofre del Santuario Celestial"),
]
NOMBRE = {f: n for f, n, _, _ in FRAGMENTOS}
MODELO = {f: m for f, _, m, _ in FRAGMENTOS}
# mazmorra -> (fragmento de la primera vez, item Astral de cada cobro)
PREMIOS = {
    "mina": ("lampara", ("cristal_refinado", 1)),
    "bosque": ("pantano", ("cristal_refinado", 1)),
    "tumba": ("arena", ("gema_luminica", 1)),
    "cumbre": ("hielo", ("gema_luminica", 2)),
    "forja": ("fuego", ("chispa_astral", 1)),
    "santuario": ("corazon", ("chispa_astral", 2)),
}
ITEM_NOMBRE = {"cristal_refinado": "Cristal Arcano Refinado", "gema_luminica": "Gema Luminica",
               "chispa_astral": "Chispa Astral", "esencia_elite": "Esencia de Elite",
               "alma_corrupta": "Alma Corrupta", "cristal_arcano": "Cristal Arcano"}
COOLDOWN = "30m"

# Marco y colores de la ventana de Mazmorras (adventure_ui).
FILL, EDGE, ACCENT = '#1f1329', '#b28fd0', '#c88bdb'
GLYPHS = {'cofre': tuple(chr(0xe620 + j) for j in range(4)),
          'fragmentos': tuple(chr(0xe624 + j) for j in range(4))}
CAPTIONS = {'cofre': 'BOTIN DEL JEFE', 'fragmentos': 'FRAGMENTOS ASTRALES'}
SLOTS_PREMIO = (19, 21, 23, 25)            # fragmento, plata, item Astral, materiales
SLOTS_BOTON = tuple(range(38, 43))         # boton RECLAMAR dibujado
SLOTS_FRAG = tuple(range(19, 26))          # los 7 fragmentos
SLOTS_PIE = {'cofre': (45, 49, 53), 'fragmentos': (45, 49, 53)}


def permiso(frag):
    return f"astral.fragmento.{frag}"


def espera(key):
    return f"astral.{key}.cd"


def lp_defaults():
    """Nodos en false para el grupo default: sin esto un OP tiene todo permiso no definido."""
    return [f"lp group default permission set {permiso(f)} false" for f, *_ in FRAGMENTOS]


def title(kind):
    return '&f' + START + ''.join(GLYPHS[kind]) + END


# ---------------------------------------------------------------- dibujos
def _xy(slot):
    return 31 + slot % 9 * 18, 57 + slot // 9 * 18


def _hueco(d, slot, marco=EDGE):
    x, y = _xy(slot)
    d.rectangle((x, y, x + 17, y + 17), outline=marco)
    d.rectangle((x + 1, y + 1, x + 16, y + 16), fill=(0, 0, 0, 0))


def _pedestal(d, slot, oro=True):
    x, y = _xy(slot)
    d.rectangle((x - 3, y - 3, x + 20, y + 20), fill='#2b1d38', outline='#d8b25a' if oro else '#7f7a84')
    d.rectangle((x - 2, y - 2, x + 19, y + 19), outline='#120b18')
    for px, py in ((x - 3, y - 3), (x + 20, y - 3), (x - 3, y + 20), (x + 20, y + 20)):
        d.point((px, py), fill='#f3dcab')


def panel(kind):
    im = ornament('mazmorras2', (278, 888, 1502, 2026))
    outlined(im, CAPTIONS[kind], (112, 39))
    d = ImageDraw.Draw(im)
    d.rectangle((24, 56, 199, 258), fill=FILL)       # tapa la ventana vanilla
    if kind == 'cofre':
        label(im, 'PRIMERA VEZ: FRAGMENTO', (112, 64), 150, '#f4e4be')
        for slot in SLOTS_PREMIO:
            _pedestal(d, slot)
            _hueco(d, slot, '#d8b25a')
        for x in (52, 172):
            star(d, x, 66, ACCENT, 2)
        # Boton RECLAMAR de 5 casillas: los clics los atrapan items invisibles encima.
        x0, y0 = _xy(SLOTS_BOTON[0]); x1, y1 = _xy(SLOTS_BOTON[-1])
        d.rectangle((x0, y0, x1 + 17, y1 + 17), fill='#2f6b3a', outline='#0d2412')
        d.line((x0 + 1, y0 + 1, x1 + 16, y0 + 1), fill='#7fd48a')
        d.line((x0 + 1, y1 + 16, x1 + 16, y1 + 16), fill='#173d1f')
        d.rectangle((x0 - 1, y0 - 1, x1 + 18, y1 + 18), outline='#d8b25a')
        label(im, 'RECLAMAR', ((x0 + x1 + 17) // 2, y0 + 5), 86, '#f2ffe9')
    else:
        label(im, 'TU COLECCION', (112, 64), 150, '#f4e4be')
        xa, ya = _xy(SLOTS_FRAG[0]); xb, _ = _xy(SLOTS_FRAG[-1])
        d.rectangle((xa - 4, ya - 4, xb + 21, ya + 21), fill='#2b1d38', outline='#d8b25a')
        d.rectangle((xa - 3, ya - 3, xb + 20, ya + 20), outline='#120b18')
        for slot in SLOTS_FRAG:
            _hueco(d, slot, '#5d4a6e')
        label(im, 'NO SE PUEDEN PERDER', (112, 120), 150, '#cbb8e0')
        label(im, 'LLAVE DEL RENACIMIENTO', (112, 132), 160, '#8f7aa6')
    for slot in SLOTS_PIE[kind]:
        _hueco(d, slot)
    # Inventario del jugador, igual que las demas ventanas de Mazmorras.
    from market_ui import band_color
    d.rectangle((31, 168, 192, 177), fill=band_color(EDGE))
    d.line((31, 167, 192, 167), fill=EDGE); d.line((31, 178, 192, 178), fill=EDGE)
    for row in (*range(3), 4):
        for col in range(9):
            x, y = 31 + col * 18, 179 + row * 18 if row < 3 else 237
            d.rectangle((x, y, x + 17, y + 17), outline=EDGE)
            d.rectangle((x + 1, y + 1, x + 16, y + 16), fill=(0, 0, 0, 0))
    return im


def sprite_lampara():
    im = Image.new('RGBA', (32, 32)); d = ImageDraw.Draw(im)
    d.rectangle((14, 2, 17, 5), fill='#3b3b44')                     # gancho
    d.rectangle((9, 6, 22, 9), fill='#4a4a55', outline='#24242b')   # tapa
    d.rectangle((10, 10, 21, 25), fill='#ffcf5a', outline='#2c2c34')
    d.rectangle((13, 12, 18, 23), fill='#fff3b0')                   # llama
    d.line((15, 14, 15, 21), fill='#ffffff')
    d.line((10, 17, 21, 17), fill='#2c2c34')
    d.rectangle((9, 26, 22, 29), fill='#4a4a55', outline='#24242b')
    return im


def sprite_corazon():
    im = Image.new('RGBA', (32, 32)); d = ImageDraw.Draw(im)
    d.ellipse((2, 2, 29, 29), fill=(79, 209, 255, 60))              # halo
    d.polygon([(16, 28), (4, 15), (4, 9), (9, 5), (16, 9), (23, 5), (28, 9), (28, 15)],
              fill='#4fd1ff', outline='#123a5c')
    d.polygon([(16, 24), (8, 14), (8, 10), (11, 8), (16, 12)], fill='#9fe8ff')
    d.line((16, 7, 16, 23), fill='#fff2a0'); d.line((10, 15, 22, 15), fill='#fff2a0')
    d.point((16, 15), fill='#ffffff')
    return im


def _fuente(frag):
    if frag == 'lampara':
        return sprite_lampara()
    if frag == 'corazon':
        return sprite_corazon()
    from item_redesign import sprite
    return sprite(f'fragmento_{frag}')


def apagado(im):
    """Version gris y oscura con un candado: fragmento ya cobrado o sin conseguir."""
    alpha = im.getchannel('A')
    gris = ImageOps.grayscale(im).convert('RGBA'); gris.putalpha(alpha)
    gris = Image.blend(gris, Image.new('RGBA', im.size, (40, 36, 48, 0)), .25); gris.putalpha(alpha)
    s = im.width // 32 or 1
    d = ImageDraw.Draw(gris)
    d.rectangle((20 * s, 20 * s, 29 * s, 29 * s), fill='#342f3c', outline='#d4c9a8')
    d.arc((21 * s, 14 * s, 28 * s, 24 * s), 180, 360, fill='#d4c9a8', width=s)
    d.point((24 * s, 24 * s), fill='#d4c9a8')
    return gris


def _modelo(files, name, image):
    files[f'assets/astral/textures/item/cofre/{name}.png'] = png(image)
    files[f'assets/astral/models/cofre/{name}.json'] = json.dumps({
        'parent': 'minecraft:item/generated', 'textures': {'layer0': f'astral:item/cofre/{name}'}}).encode()
    files[f'assets/astral/items/cofre/{name}.json'] = json.dumps({
        'model': {'type': 'minecraft:model', 'model': f'astral:cofre/{name}'}}).encode()


def assets():
    files, providers, advances = {}, [], {}
    for kind, (a, b, c, d) in GLYPHS.items():
        im = panel(kind)
        for n, ((part, ascent), char, rewind) in enumerate(zip(glyph_parts(im, SPLIT), (a, c), (b, d))):
            resource = f'font/cofre/{kind}_{n}.png'
            files[f'assets/astral/textures/{resource}'] = png(part)
            providers.append({'type': 'bitmap', 'file': 'astral:' + resource, 'height': part.height,
                              'ascent': ascent, 'chars': [char]})
            advances[rewind] = -(part.getbbox()[2] + 1)
    providers.append({'type': 'space', 'advances': advances})
    _modelo(files, 'lampara', sprite_lampara())
    _modelo(files, 'corazon', sprite_corazon())
    for frag, *_ in FRAGMENTOS:
        _modelo(files, f'{frag}_apagado', apagado(_fuente(frag)))
    return files, providers


# ---------------------------------------------------------------- ventanas
def _req(tipo, perm):
    return {'requirements': {'r': {'type': tipo, 'permission': perm}}}


def _invisible(slot, entry):
    return dict(entry, material='PAPER', slot=slot, item_model='astral:viajes/blank', item_flags=['HIDE_ATTRIBUTES'])


def _pie(items):
    items['lobby'] = {'material': 'NETHER_STAR', 'slot': 45, 'display_name': '&a&lVolver al lobby',
                      'lore': ['&7Sales de la mazmorra.'], 'click_commands': ['[close]', '[player] spawn']}
    items['cerrar'] = {'material': 'BARRIER', 'slot': 53, 'display_name': '&cCerrar', 'click_commands': ['[close]']}


def cofre_menu(dungeon):
    key, nombre, plata = dungeon['key'], dungeon['name'], dungeon['money']
    frag, (astral, n_astral) = PREMIOS[key]
    materiales = list(dungeon['reward'])
    items = {}
    items['fragmento'] = {
        'material': 'PAPER', 'item_model': MODELO[frag], 'slot': SLOTS_PREMIO[0], 'priority': 1,
        'display_name': f'&b&l{NOMBRE[frag]}',
        'lore': ['&aSe consigue la primera vez.', '&7Se guarda en tus &bFragmentos Astrales&7:',
                 '&7no ocupa lugar y no se puede perder.'],
        'view_requirement': _req('!has permission', permiso(frag)), 'enchantments': ['unbreaking;1'],
        'item_flags': ['HIDE_ATTRIBUTES', 'HIDE_ENCHANTS']}
    items['fragmento_apagado'] = {
        'material': 'PAPER', 'item_model': f'astral:cofre/{frag}_apagado', 'slot': SLOTS_PREMIO[0], 'priority': 2,
        'display_name': f'&8&l{NOMBRE[frag]}',
        'lore': ['&cYa reclamado.', '&7Solo se puede reclamar la primera vez.', '&7Lo tienes en &f/fragmentos&7.'],
        'item_flags': ['HIDE_ATTRIBUTES']}
    items['plata'] = {'material': 'GOLD_INGOT', 'slot': SLOTS_PREMIO[1], 'display_name': f'&e&l{plata}$',
                      'lore': ['&7Cada vez que cobras el cofre.']}
    items['astral'] = {'material': 'PAPER', 'item_model': f'astral:{astral}', 'slot': SLOTS_PREMIO[2], 'amount': n_astral,
                       'display_name': f'&d&l{n_astral}x {ITEM_NOMBRE[astral]}',
                       'lore': ['&7Item Astral de esta mazmorra.', '&7Cada vez que cobras el cofre.'],
                       'item_flags': ['HIDE_ATTRIBUTES']}
    items['materiales'] = {'material': 'PAPER', 'item_model': 'astral:alma_corrupta', 'slot': SLOTS_PREMIO[3],
                           'display_name': '&a&lMateriales de elite',
                           'lore': [f'&f{n}x {ITEM_NOMBRE.get(i, i)}' for i, n in materiales]
                                   + ['&e25% &fChispa Astral', '&7Cada vez que cobras el cofre.'],
                           'item_flags': ['HIDE_ATTRIBUTES']}
    cobro = ['[close]', f'[console] eco give %player_name% {plata}']
    for i, n in materiales + [(astral, n_astral)]:
        cobro += [f'[console] loot give %player_name% loot astral:item/{i}'] * n
    cobro += ['[console] loot give %player_name% loot astral:item/chispa_astral <chance=25>',
              f'[console] lp user %player_name% permission settemp {espera(key)} true {COOLDOWN}',
              f'[message] &6Cofre de {nombre}: &e{plata}$&f, {n_astral}x {ITEM_NOMBRE[astral]} y materiales de elite.',
              '[sound] ENTITY_PLAYER_LEVELUP']
    primera = [f'[console] lp user %player_name% permission set {permiso(frag)} true',
               f'[message] &b&lNuevo fragmento: &f{NOMBRE[frag]}&7. Quedo guardado en &f/fragmentos&7.',
               '[sound] UI_TOAST_CHALLENGE_COMPLETE']
    espera_txt = ['[message] &7Ya cobraste este cofre hace poco. &8(se puede cobrar cada 30 minutos)',
                  '[sound] ENTITY_VILLAGER_NO']
    libre = {'type': '!has permission', 'permission': espera(key)}
    for n, slot in enumerate(SLOTS_BOTON):
        base = {'display_name': '&a&lRECLAMAR', 'update': True}
        # Primera vez: tambien guarda el fragmento. Prioridad menor = se muestra primero.
        items[f'reclamar_{n}'] = _invisible(slot, dict(
            base, priority=1, lore=['&7Cobra plata, item Astral y materiales.', f'&bY guarda el {NOMBRE[frag]}.'],
            view_requirement=_req('!has permission', permiso(frag)),
            click_requirement={'requirements': {'libre': libre}, 'deny_commands': espera_txt},
            click_commands=cobro[:1] + primera + cobro[1:]))
        items[f'reclamar_ya_{n}'] = _invisible(slot, dict(
            base, priority=2, lore=['&7Cobra plata, item Astral y materiales.', '&8Se puede cobrar cada 30 minutos.'],
            click_requirement={'requirements': {'libre': libre}, 'deny_commands': espera_txt},
            click_commands=cobro))
    items['coleccion'] = {'material': 'PAPER', 'item_model': 'astral:cofre/corazon', 'slot': 49,
                          'display_name': '&b&lFragmentos Astrales', 'lore': ['&7Mira los fragmentos que ya guardaste.'],
                          'click_commands': ['[openguimenu] fragmentos']}
    _pie(items)
    return {'menu_title': title('cofre'), 'size': 54, 'update_interval': 1, 'items': items}


def fragmentos_menu():
    items = {}
    for (frag, nombre, modelo, origen), slot in zip(FRAGMENTOS, SLOTS_FRAG):
        items[frag] = {'material': 'PAPER', 'item_model': modelo, 'slot': slot, 'priority': 1,
                       'display_name': f'&b&l{nombre}', 'lore': ['&aGuardado.', '&7No se puede perder.'],
                       'view_requirement': _req('has permission', permiso(frag)),
                       'enchantments': ['unbreaking;1'], 'item_flags': ['HIDE_ATTRIBUTES', 'HIDE_ENCHANTS']}
        items[frag + '_falta'] = {'material': 'PAPER', 'item_model': f'astral:cofre/{frag}_apagado', 'slot': slot,
                                  'priority': 2, 'display_name': f'&8&l{nombre}',
                                  'lore': ['&cTodavia no lo tienes.', f'&7Se consigue en {origen}.'],
                                  'item_flags': ['HIDE_ATTRIBUTES']}
    items['info'] = {'material': 'NETHER_STAR', 'slot': 49, 'display_name': '&b&lFragmentos Astrales',
                     'lore': ['&7Cada jefe da su fragmento la primera vez.', '&7Quedan guardados aca para siempre.',
                              '&7Con todos se podra renacer.']}
    items['volver'] = {'material': 'ARROW', 'slot': 45, 'display_name': '&fVolver al menu',
                       'click_commands': ['[openguimenu] principal']}
    items['cerrar'] = {'material': 'BARRIER', 'slot': 53, 'display_name': '&cCerrar', 'click_commands': ['[close]']}
    return {'menu_title': title('fragmentos'), 'open_command': 'fragmentos', 'register_command': True,
            'size': 54, 'update_interval': 1, 'items': items}


def generate():
    """Escribe las ventanas en build/menus/DeluxeMenus/gui_menus y devuelve sus nombres."""
    from mobs.mazmorra import MINA
    from mobs.mazmorras_data import catalog
    out = ROOT / 'build/menus/DeluxeMenus/gui_menus'
    out.mkdir(parents=True, exist_ok=True)
    nombres = []
    for dungeon in [MINA] + catalog():
        name = f"cofre_{dungeon['key']}"
        (out / f'{name}.yml').write_text(json.dumps(cofre_menu(dungeon), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        nombres.append(name)
    (out / 'fragmentos.yml').write_text(json.dumps(fragmentos_menu(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return nombres + ['fragmentos']


def previews(folder=ROOT / 'build/Servicios-preview'):
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    from escape_menu import text
    for kind in GLYPHS:
        im = Image.new('RGBA', SIZE, '#22242a'); im.alpha_composite(panel(kind))
        if kind == 'cofre':
            from item_redesign import sprite
            for slot, pic in zip(SLOTS_PREMIO, (_fuente('arena'), sprite('chispa_astral'), sprite('chispa_astral'), sprite('alma_corrupta'))):
                im.alpha_composite(pic.resize((16, 16)), (_xy(slot)[0] + 1, _xy(slot)[1] + 1))
        else:
            for n, (frag, *_ ) in enumerate(FRAGMENTOS):
                pic = _fuente(frag) if n < 3 else apagado(_fuente(frag))
                im.alpha_composite(pic.resize((16, 16)), (_xy(SLOTS_FRAG[n])[0] + 1, _xy(SLOTS_FRAG[n])[1] + 1))
        text(im, 'Inventario', (86, 169), color='#383c40')
        (folder / f'cofre-{kind}.png').write_bytes(png(im.resize((im.width * 3, im.height * 3), Image.Resampling.NEAREST)))


if __name__ == '__main__':
    previews()
