# -*- coding: utf-8 -*-
"""
Menus de cofre (DeluxeMenus) para que los jugadores no tengan que escribir comandos.

  /menu          menu principal (mascotas, mercado, subastas, guia, volver al lobby)
  /mascotas      tus mascotas: invocar o guardar (las que no tenes aparecen bloqueadas)
  gacha_*        lo abre el cofre de cada gacha: tirar x1 / x10 / x25 / x50 y ver premios
  bazar          lo abre el aldeano Bazar: mercado y venta rapida (EconomyShopGUI), subastas (CrazyAuctions), intercambio (AxTrade)

Los menus que abren los vendedores se abren desde la consola con 'dm open <menu> <jugador>'.
Salida: ../build/menus/DeluxeMenus/  (gui_menus/*.yml + config-gui_menus.yml con la lista para config.yml)
"""
import os
import textwrap

from lobby import GACHAS, PITY, HOLO_COLOR, HOLO_NAME, HOLO_DESC, pity_obj, TIRADAS, money, RARITY_WEIGHT
from mobs.mascotas import MASCOTAS, beneficios_actuales
from misiones import CHAPTERS, DAILIES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "build", "menus", "DeluxeMenus")
RULETA_TICKS = 140
# Puntaje del jugador (expansion 'ScoreboardObjectives' de PlaceholderAPI).
SCORE = "%objective_score_{{{}}}%"   # con llaves: los nombres llevan guion bajo

VIDRIO = {"gacha_rpg": "PURPLE_STAINED_GLASS_PANE", "gacha_monturas": "LIME_STAINED_GLASS_PANE",
          "gacha_cosmeticos": "PINK_STAINED_GLASS_PANE"}
ICONO = {"gacha_rpg": "AMETHYST_SHARD", "gacha_monturas": "SADDLE", "gacha_cosmeticos": "NAME_TAG"}
TIRADA_ICONO = {"gacha_rpg": "AMETHYST_SHARD", "gacha_monturas": "WHEAT", "gacha_cosmeticos": "PINK_DYE"}   # se apilan hasta 64
MASC_ICONO = {"lobo": "WOLF_SPAWN_EGG", "cuervo": "PARROT_SPAWN_EGG", "golem": "IRON_GOLEM_SPAWN_EGG",
              "zorro": "FOX_SPAWN_EGG", "dragon": "BLAZE_SPAWN_EGG", "fenix": "CHICKEN_SPAWN_EGG"}


def hexc(c):
    """#RRGGBB -> &#RRGGBB (formato de color de DeluxeMenus)."""
    return "&" + c


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


def item(key, material, slot, name, lore=(), amount=1, extra=None, glow=False):
    # Iconos de servicio propios, conservando las tarjetas ilustradas existentes.
    from menu_ui import button_model
    extra = dict(extra or {})
    icon_key = {'comprar':'tienda','guardar':'mascotas'}.get(key,key)
    model=button_model(icon_key)
    if model and 'item_model' not in extra:
        extra['item_model'] = q(model)
    L = [f"  {q(key)}:", f"    material: {material}", f"    slot: {slot}", f"    amount: {amount}",
         f"    display_name: {q(name)}"]
    flags = ["HIDE_ATTRIBUTES"] + (["HIDE_ENCHANTS"] if glow else [])
    if lore:
        L.append("    lore:")
        L += [f"    - {q(x)}" for x in lore]
    if glow:
        L += ["    enchantments:", "    - 'unbreaking;1'"]
    L += ["    item_flags:"] + [f"    - {f}" for f in flags]
    for k, v in (extra or {}).items():
        if isinstance(v, list):
            L.append(f"    {k}:")
            L += [f"    - {q(x)}" for x in v]
        elif isinstance(v, str) and v.startswith("\n"):
            L.append(f"    {k}:{v}")
        else:
            L.append(f"    {k}: {v}")
    return L


def relleno(material, size, ocupados):
    L = []
    for s in range(size):
        if s not in ocupados:
            L += item(f"vidrio_{s}", material, s, " ")
    return L


# Comandos que los jugadores escriben: se registran como comandos de verdad.
# Sin register_command, DeluxeMenus solo los atrapa al escribirlos y el chat los marca en rojo.
COMANDOS_JUGADOR = {"menu", "comandos", "mascotas", "misiones"}


def menu(title, command, size, items, update=False):
    L = [f"menu_title: {q(title)}", f"open_command: {command}", f"size: {size}"]
    if command in COMANDOS_JUGADOR:
        L.append("register_command: true")
    if update:
        L.append("update_interval: 1")
    return "\n".join(L + ["items:"] + items) + "\n"


def requisito_plata(costo):
    return ("\n      requirements:\n        plata:\n          type: has money\n          amount: " + str(costo) +
            "\n      deny_commands:\n      - " + q(f"[message] &cNo te alcanza: cuesta &e{money(costo)}&c. &7(/balance)") +
            "\n      - '[sound] ENTITY_VILLAGER_NO'")


def gacha_menu(gid, g):
    from market_ui import title, regions
    col, name, n, o = hexc(HOLO_COLOR[gid]), HOLO_NAME[gid], PITY[gid], pity_obj(gid)
    P = "%player_name%"
    items = item("info", ICONO[gid], 4, f"{col}&l✦ {name} ✦",
                 [f"&7{HOLO_DESC[gid]}", "", f"&7Precio: &e{money(g['cost'])} &7por tirada",
                  f"&7Epico garantizado cada &f{n} &7tiradas", f"&7Tu garantia: &e{SCORE.format(o)}&7/{n}"], glow=True,
                 extra={"update": "true"})
    for (_, slots), t in zip(regions(gid), TIRADAS):
        costo = g["cost"] * t
        cmds = ["[close]", f"[takemoney] {costo}", "[sound] BLOCK_AMETHYST_BLOCK_CHIME",
                f"[console] scoreboard players add {P} {o} {t}",
                f"[console] scoreboard players set {P} gachaflag 0",
                f"[console] execute if score {P} {o} matches {n}.. run scoreboard players set {P} gachaflag 1",
                f"[console] execute if score {P} gachaflag matches 1 run minecraft:tellraw {P} "
                "{text:'Tirada garantizada! (Epico o Legendario seguro)',color:'light_purple',bold:true}",
                f"[console] execute if score {P} gachaflag matches 1 run crates forceopen {gid}_garantia {P}",
                f"[console] execute unless score {P} gachaflag matches 1 run crates forceopen {gid} {P}"]
        if t > 1:
            cmds += [f"[message] &7Gira la ruleta... cuando termine te llegan los otros &e{t - 1}&7 premios.",
                     f"[console] crates give virtual {gid} {t - 1} {P} -s<delay={RULETA_TICKS}>",
                     f"[console] sudo {P} crates mass-open {gid} virtual {t - 1}<delay={RULETA_TICKS + 1}>",
                     f"[message] &aListo: &f{t} tiradas &aen la {name}.<delay={RULETA_TICKS + 2}>"]
        for index,slot in enumerate(slots):
            items += item(f"x{t}_{index}", 'PAPER', slot,
                      f"{col}&lTirar x{t}",
                      ["", f"&7Precio: &e{money(costo)}", "&7Suma " + (f"{t} tiradas" if t > 1 else "1 tirada") + " a tu garantia",
                       "" if t == 1 else "&8Gira 1 ruleta y despues llegan los demas premios", "", "&eClic para tirar"],
                      extra={"item_model":q(f'astral:servicios/{gid}_x{t}_{index}'),
                             "click_requirement": requisito_plata(costo), "click_commands": [c+'<delay=3>' if 'crates forceopen ' in c else c for c in cmds]})
    items += item("premios", "CHEST", 49, "&6&lVer premios", ["&7Todos los premios y su probabilidad"],
                  extra={"item_model":q(f'astral:menu/icon_{gid}'),"click_commands": ["[close]", f"[console] sudo {P} crates preview {gid}<delay=3>"]})
    items += item('saldo','GOLD_NUGGET',8,'&6Tu saldo',['&e%vault_eco_balance_formatted%$'],extra={'update':'true'})
    items += item('garantia','ENDER_EYE',47,'&dGarantia',[f'&7Tu progreso: &e{SCORE.format(o)}&7/{n}',
                  '&7Un Epico o Legendario reinicia el contador.'],extra={'update':'true'})
    items += item('probabilidades','BOOK',51,'&bProbabilidades',['&fComun: 60%','&aPoco comun: 25%',
                  '&bRaro: 11%','&dEpico: 3,5%','&6Legendario: 0,5%'])
    items += item('volver','ARROW',45,'&fVolver al Bazar',extra={'click_commands':['[openguimenu] bazar']})
    items += item('cerrar','BARRIER',53,'&cCerrar',extra={'click_commands':['[close]']})
    return menu(title(gid), f"astralmenu_{gid}", 54, items, update=True)


def subastas_menu():
    from market_ui import title, regions
    actions={
        'mercado':('&6Explorar el mercado',['&7Objetos publicados por otros jugadores.','&eClic para explorar.'],'ah'),
        'publicaciones':('&eMis publicaciones',['&7Consulta o cancela tus ventas activas.'],'ah listed'),
        'retirar':('&aRetirar objetos',['&7Recupera tus objetos cancelados o vencidos.'],'ah collect'),
        'publicar':('&bComo publicar',['&f1. Sostene el objeto que queres vender.','&f2. Escribi /ah sell <precio>.',
                    '&7El precio y la confirmacion los administra','&7el sistema de subastas.'],None),
    }
    lines=[]
    for key,slots in regions('subastas'):
        caption,lore,command=actions[key]
        for index,slot in enumerate(slots):
            cmds=['[sound] UI_BUTTON_CLICK']
            if command:cmds+=['[close]',f'[player] {command}<delay=3>']
            else:cmds+=['[message] &eCon el objeto en la mano, usa &f/ah sell <precio>&e.']
            lines+=item(f'{key}_{index}','PAPER',slot,caption,lore,extra={
                'item_model':q(f'astral:servicios/subastas_{key}_{index}'),'click_commands':cmds})
    lines+=item('saldo','GOLD_NUGGET',4,'&6Tu saldo',['&e%vault_eco_balance_formatted%$'],extra={'update':'true'})
    lines+=item('ayuda','BOOK',8,'&eCasa de Subastas',['&7Compra y vende entre jugadores.',
                '&7Revisa el objeto y su precio antes de comprar.'])
    lines+=item('volver','ARROW',45,'&fVolver al Bazar',extra={'click_commands':['[openguimenu] bazar']})
    lines+=item('cerrar','BARRIER',53,'&cCerrar',extra={'click_commands':['[close]']})
    return menu(title('subastas'),'astralmenu_subastas',54,lines,update=True)


def _pet_cards(pairs):
    P = "%player_name%"
    items = []
    for pid, slots in pairs:
        d = MASCOTAS[pid]
        col = hexc(d["color"])
        permission = f"astral.mascota.{pid}"
        requirement = f"\n      requirements:\n        tiene:\n          type: has permission\n          permission: {permission}"
        benefits = ["&6&lMejoras que te da", f"&aDesde nivel 1: &f{d['texto'][0]}",
                    f"&eDesde nivel 10: &f{d['texto'][1]}", f"&eDesde nivel 20: &f{d['texto'][2]}",
                    "&7Nivel 30: evolucion visual", "", "&8Los bonus solo se activan en mazmorras."]
        for index, slot in enumerate(slots):
            key = f"m_{pid}" if index == 0 else f"m_{pid}_hit_{index}"
            for priority, level in enumerate((20, 10, 1), 1):
                view = requirement
                if level > 1:
                    view += f"\n        nivel:\n          type: '>='\n          input: '{SCORE.format('plv_' + pid)}'\n          output: '{level}'"
                lore = ["", f"&7Nivel: &e{SCORE.format('plv_' + pid)}&7/30", "", "&a&lAl equiparla ahora:",
                        *['&f+ ' + bonus for bonus in beneficios_actuales(pid, level)], "", *benefits,
                        "", "&eClic izquierdo: equipar e invocar", "&bClic derecho: ver detalle"]
                items += item(key if level == 1 else key + f'_nv{level}', 'PAPER', slot, f"{col}&l{d['nombre']}", lore, extra={
                    'item_model': q(f'astral:mascotas/{pid}_{index}'), 'priority': priority, 'update': 'true',
                    'view_requirement': view,
                    'left_click_requirement': requirement + "\n      deny_commands:\n      - '[message] &cTodavia no tienes esta mascota.'\n      - '[sound] ENTITY_VILLAGER_NO'",
                    'left_click_commands': ['[close]', f"[console] scoreboard players set {P} mascota {d['n']}"],
                    'right_click_commands': [f'[openguimenu] mascota_{pid}']})
            items += item(key+'_no', 'PAPER', slot, f"&8&l{d['nombre']} &7(bloqueada)",
                          ['', *benefits, '', f"&7Se consigue en: &f{d['fuente']}", '',
                           '&7Desbloqueala para invocarla desde el santuario.'], extra={
                'item_model': q(f'astral:mascotas/{pid}_locked_{index}'), 'priority': 4,
                'left_click_commands': ['[message] &7Todavia no tienes esta mascota.', '[sound] ENTITY_VILLAGER_NO'],
                'right_click_commands': [f'[openguimenu] mascota_{pid}']})
    return items


def mascotas_menu():
    from mascotas_ui import title, regions, REST_SLOTS
    P = "%player_name%"
    items = item("info", "PAPER", 4, "&6&lSantuario de companeros",
                 ["&7Puedes llevar una mascota a la vez.", "&7Te sigue y sube de nivel con tus bajas.",
                  "&7Nivel 10 y 20: mejores bonus; nivel 30: evolucion.", "",
                  "&7Pasa el cursor por cada retrato para ver sus bonus.", "&8Bonus solo dentro de las mazmorras."],
                 extra={'item_model': q('astral:mascotas/nav_info')})
    items += _pet_cards(regions())
    for index, slot in enumerate(REST_SLOTS):
        items += item('guardar' if index == 0 else f'guardar_hit_{index}', 'PAPER', slot,
                      '&a&lDejar descansar a tu mascota', ['&7Guarda a tu companero actual.', '&7Conserva su nivel y sus mejoras.'],
                      extra={'item_model': q(f'astral:mascotas/rest_{index}'),
                             'click_commands': ['[close]', f'[console] scoreboard players set {P} mascota 98']})
    items += item('gacha', 'PAPER', 8, '&6&lConseguir mas companeros',
                  ['&7La Gacha de Monturas puede dar mascotas.', '&7Los otros retratos indican donde conseguirlas.'],
                  extra={'item_model': q('astral:mascotas/nav_gacha'), 'click_commands': ['[openguimenu] gacha_monturas']})
    items += item('volver', 'PAPER', 45, '&fVolver al atlas',
                  extra={'item_model': q('astral:mascotas/nav_back'), 'click_commands': ['[openguimenu] principal']})
    items += item('cerrar', 'PAPER', 53, '&cCerrar',
                  extra={'item_model': q('astral:mascotas/nav_close'), 'click_commands': ['[close]']})
    items += item('mas_companeros', 'PAPER', 46, '&eMas companeros &7(pagina 2)',
                  extra={'item_model': q('astral:mascotas/nav_next'), 'click_commands': ['[openguimenu] mascotas_2']})
    return menu(title(), 'mascotas', 54, items, update=True)


def mascotas_extra_menu(page):
    """Paginas 2-4: seis tarjetas grandes por pagina, mismo comportamiento que la pagina 1."""
    from mascotas_ui import page_title, page_regions, REST_SLOTS, LAST_PAGE
    P = "%player_name%"
    items = item("info", "PAPER", 4, "&6&lSantuario de companeros",
                 ["&7Clic izquierdo: equipar e invocar.", "&7Clic derecho: ver nivel, bonus y mejoras.",
                  "&8Bonus solo dentro de las mazmorras."], extra={'item_model': q('astral:mascotas/nav_info')})
    items += _pet_cards(page_regions(page))
    for index, slot in enumerate(REST_SLOTS):
        items += item('guardar' if index == 0 else f'guardar_hit_{index}', 'PAPER', slot,
                      '&a&lDejar descansar a tu mascota', ['&7Guarda a tu companero actual.', '&7Conserva su nivel y sus mejoras.'],
                      extra={'item_model': q(f'astral:mascotas/rest_{index}'),
                             'click_commands': ['[close]', f'[console] scoreboard players set {P} mascota 98']})
    items += item('gacha', 'PAPER', 8, '&6&lConseguir mas companeros',
                  ['&7La Gacha de Monturas puede dar mascotas.'],
                  extra={'item_model': q('astral:mascotas/nav_gacha'), 'click_commands': ['[openguimenu] gacha_monturas']})
    items += item('anterior', 'PAPER', 45, f'&eAnterior &7(pagina {page - 1})', extra={'item_model': q('astral:mascotas/nav_back'),
                  'click_commands': ['[openguimenu] ' + ('mascotas' if page == 2 else f'mascotas_{page - 1}')]})
    if page < LAST_PAGE:
        items += item('siguiente', 'PAPER', 53, f'&eSiguiente &7(pagina {page + 1})', extra={'item_model': q('astral:mascotas/nav_next'),
                      'click_commands': [f'[openguimenu] mascotas_{page + 1}']})
    else:
        items += item('cerrar', 'PAPER', 53, '&cCerrar', extra={'item_model': q('astral:mascotas/nav_close'), 'click_commands': ['[close]']})
    return menu(page_title(page), f'astralmascotas_{page}', 54, items, update=True)


def mascota_nueva_detalle(pid):
    d = MASCOTAS[pid]
    permission = f'astral.mascota.{pid}'
    requirement = '\n      requirements:\n        tiene:\n          type: has permission\n          permission: ' + permission
    lore = [f"&7Nivel: &e{SCORE.format('plv_' + pid)}&7/30",
            f"&7Experiencia: &e{SCORE.format('pmod_' + pid)}&7/25",
            *[f'&7Nv. {lv}: &f{bonus}' for lv, bonus in zip((1, 10, 20), d['texto'])],
            '&7Nivel 30: evolucion visual', '&8Bonus solo en mazmorras', '&7Se consigue en la Gacha de Monturas']
    lines = item('info', d['icono'], 13, hexc(d['color']) + d['nombre'], lore, extra={
        'update': 'true', 'item_model': q(f'astral:mascotas/catalogo_{pid}')})
    lines += item('invocar', 'LIME_DYE', 29, '&aInvocar', lore, extra={
        'click_requirement': requirement + "\n      deny_commands:\n      - '[message] &cTodavia no tienes esta mascota.'",
        'click_commands': ['[close]', f"[console] scoreboard players set %player_name% mascota {d['n']}"]})
    lines += item('estado', 'BARRIER', 31, '&cBloqueada', ['&7Ganala en la Gacha de Monturas'], extra={'priority': 2})
    lines += item('estado_si', 'EMERALD', 31, '&aDesbloqueada', extra={'priority': 1, 'view_requirement': requirement})
    lines += item('guardar', 'CHEST', 33, '&aGuardar mascota', extra={'click_commands': [
        '[close]', '[console] scoreboard players set %player_name% mascota 98']})
    lines += item('coleccion', 'ARROW', 45, '&eVolver a la coleccion', extra={'click_commands': [
        f"[openguimenu] mascotas_{2 + (d['n'] - 7) // 9}"]})
    return menu('&8' + d['nombre'], 'mascota_' + pid, 54, lines, update=True)


def mascota_detalle_menu(pid):
    """Mi companero (companero_ui.py): cartel de nivel, barra de experiencia y mejoras con su estado real."""
    from companero_ui import title, LEVEL_SLOTS, XP_SLOTS, PERK_ROWS, PERK_LEVELS, INVOKE_SLOTS, REST_SLOTS
    P = "%player_name%"
    d = MASCOTAS[pid]
    col = hexc(d["color"])
    lv, mod = SCORE.format('plv_' + pid), SCORE.format('pmod_' + pid)
    perm = f"astral.mascota.{pid}"

    def cmp(name, kind, value, number):
        return f"\n        {name}:\n          type: '{kind}'\n          input: '{value}'\n          output: '{number}'"
    info = [f"&7Nivel: &e{lv}&7/30", f"&7Experiencia: &e{mod}&7/25 bajas",
            "&7Sube con los mobs que matas con ella afuera.", "&8Los bonus solo se activan en mazmorras."]
    items = []
    # Cartel "Nivel X / 30": una version por nivel; sin datos muestra el nivel 1.
    for i, slot in enumerate(LEVEL_SLOTS):
        for level in range(1, 31):
            items += item(f'nivel_{level}_{i}', 'PAPER', slot, f"{col}&l{d['nombre']}", info, extra={
                'item_model': q(f'astral:companero/nivel_{level}_{i}'), 'priority': level, 'update': 'true',
                'view_requirement': "\n      requirements:" + cmp('nivel', '==', lv, level)})
        items += item(f'nivel_base_{i}', 'PAPER', slot, f"{col}&l{d['nombre']}", info, extra={
            'item_model': q(f'astral:companero/nivel_1_{i}'), 'priority': 31})
    # Barra de 5 casillas: cada una cubre 5 de las 25 bajas del nivel; en nivel 30 queda llena.
    for j, slot in enumerate(XP_SLOTS):
        lore = [f"&7Experiencia: &e{mod}&7/25 bajas para el proximo nivel."]
        items += item(f'xp_{j}_full', 'PAPER', slot, '&bExperiencia', lore, extra={
            'item_model': q(f'astral:companero/xp_{j}_2'), 'priority': 1, 'update': 'true',
            'view_requirement': "\n      minimum_requirements: 1\n      requirements:" + cmp('maximo', '>=', lv, 30) + cmp('lleno', '>=', mod, 5 * (j + 1))})
        items += item(f'xp_{j}_half', 'PAPER', slot, '&bExperiencia', lore, extra={
            'item_model': q(f'astral:companero/xp_{j}_1'), 'priority': 2, 'update': 'true',
            'view_requirement': "\n      requirements:" + cmp('medio', '>=', mod, 5 * j + 3)})
        items += item(f'xp_{j}', 'PAPER', slot, '&bExperiencia', lore, extra={
            'item_model': q(f'astral:companero/xp_{j}_0'), 'priority': 3, 'update': 'true'})
    texts = list(d['texto']) + ['Evolucion visual de la mascota']
    for row, level, caption in zip(PERK_ROWS, PERK_LEVELS, texts):
        lore = [f"&7Desde nivel &e{level}&7: &f{caption}", "&8Los bonus solo se activan en mazmorras."]
        for c in range(8):
            items += item(f'mejora_{level}_{c}', 'PAPER', row * 9 + c, f"&6Nivel {level}", lore,
                          extra={'item_model': q('astral:viajes/blank')})
        items += item(f'estado_{level}', 'PAPER', row * 9 + 8, f"&aDesbloqueada (nivel {level})", lore, extra={
            'item_model': q('astral:companero/ok'), 'priority': 1, 'update': 'true',
            'view_requirement': "\n      requirements:" + cmp('nivel', '>=', lv, level)})
        items += item(f'estado_{level}_no', 'PAPER', row * 9 + 8, f"&7Bloqueada: llega a nivel {level}", lore, extra={
            'item_model': q('astral:companero/lock'), 'priority': 2})
    deny = ("\n      requirements:\n        tiene:\n          type: has permission\n          permission: " + perm +
            "\n      deny_commands:\n      - '[message] &cTodavia no tienes esta mascota.'\n      - '[sound] ENTITY_VILLAGER_NO'")
    for index, slot in enumerate(INVOKE_SLOTS):
        items += item('invocar' if index == 0 else f'invocar_{index}', 'PAPER', slot, f"&b&lInvocar a {d['nombre']}",
                      ['&7La equipa y la llama a tu lado.', '&7Solo una mascota a la vez.'], extra={
                          'item_model': q(f'astral:companero/invocar_{index}'), 'click_requirement': deny,
                          'click_commands': ['[close]', f"[console] scoreboard players set {P} mascota {d['n']}"]})
    for index, slot in enumerate(REST_SLOTS):
        items += item('descansar' if index == 0 else f'descansar_{index}', 'PAPER', slot, '&a&lDejar descansar a tu mascota',
                      ['&7Guarda a tu companero actual.', '&7Conserva su nivel y sus mejoras.'], extra={
                          'item_model': q(f'astral:companero/descansar_{index}'),
                          'click_commands': ['[close]', f'[console] scoreboard players set {P} mascota 98']})
    items += item('coleccion', 'PAPER', 45, '&fVolver a la coleccion', extra={
        'item_model': q('astral:companero/volver'), 'click_commands': ['[openguimenu] ' + ('mascotas' if d['n'] <= 6 else f"mascotas_{2 + (d['n'] - 7) // 9}")]})
    items += item('cerrar', 'PAPER', 53, '&cCerrar', extra={
        'item_model': q('astral:companero/cerrar'), 'click_commands': ['[close]']})
    return menu(title(pid), f'mascota_{pid}', 54, items, update=True)


def bazar_menu():
    from services_ui import title, bazar_regions
    actions = {
        'comprar': ('&a&lComprar en la Tienda', ['&7Selecciona un producto, revisa el precio', '&7y confirma con COMPRAR.'], 'economyshopgui:shop'),
        'vender': ('&6&lVenta rapida', ['&7Coloca el objeto, revisa su importe', '&7y confirma con VENDER.', '&7Cerrar devuelve el objeto.'], 'astralventa'),
        'subastas': ('&e&lSubastas', ['&7Comercio entre jugadores.', '&7Explora, consulta tus ventas y retira objetos.'], 'astralmenu_subastas'),
        'intercambio': ('&b&lIntercambio', ['&7Cambia objetos y oro cara a cara', '&7con otro jugador: &f/trade <jugador>'], None),
    }
    lines=[]
    for key,cols,rows in bazar_regions():
        name,lore,command=actions[key]
        for index,slot in enumerate(row*9+col for row in rows for col in cols):
            lines += item(f'{key}_{index}','PAPER',slot,name,lore,extra={
                'item_model':q(f'astral:servicios/bazar_{key}_{index}'),
                # DeluxeMenus programa la accion CLOSE al tick siguiente y
                # closeMenu programa closeInventory OTRO tick mas tarde.
                # Abrir antes del tercero cierra tambien el menu de destino.
                'click_commands':['[sound] UI_BUTTON_CLICK','[close]',f'[player] {command}<delay=3>'] if command else
                    ['[sound] UI_BUTTON_CLICK','[close]','[message] &bIntercambio: &fescribe &e/trade <jugador> &fcerca de el.',
                     '[message] &7Los dos ponen sus objetos u oro y confirman. Nadie pierde nada si se cancela.']})
    lines += item('saldo','GOLD_NUGGET',4,'&6Tu saldo',['&e%vault_eco_balance_formatted%$'],extra={'update':'true'})
    lines += item('ayuda','WRITABLE_BOOK',8,'&fBazar del Refugio',['&7Comprar y vender: precios del servidor.', '&7Subastas e intercambio: otros jugadores.'])
    lines += item('volver','ARROW',53,'&fVolver',extra={'click_commands':['[openguimenu] principal']})
    return menu(title('bazar'),'astralmenu_bazar',54,lines,update=True)


def principal_menu():
    buttons = [
        ('bazar', 'EMERALD', '&6&lBazar del Refugio', ['&7Compra, vende o intercambia.'], ['[openguimenu] bazar']),
        ('minas', 'IRON_PICKAXE', '&b&lMinas Astrales', ['&7Entra a las minas desde el lobby.'], ['[close]', '[player] minas<delay=3>']),
        ('mazmorras', 'SPAWNER', '&d&lMazmorras', ['&7Viaja a las mazmorras descubiertas.'], ['[openguimenu] mazmorras']),
        ('expediciones', 'FILLED_MAP', '&a&lExpediciones Astrales', ['&7Explora y encontra a sus guardianes.'], ['[openguimenu] expediciones']),
        ('portales', 'ENDER_EYE', '&b&lPortales Astrales', ['&7Elegi tu proximo destino.'], ['[openguimenu] portales']),
        ('parkour', 'FEATHER', '&a&lMini juegos', ['&7Parkour, droppers y Color Escape.'], ['[openguimenu] parkour']),
        ('arenas', 'IRON_SWORD', '&c&lArenas PvP', ['&7Pelea sin perder tu equipo.'], ['[openguimenu] arenas']),
        ('misiones', 'WRITABLE_BOOK', '&e&lEl Cronista', ['&7Misiones, historia y recompensas.'], ['[console] execute as %player_name% at @s run function astral:quest/gui/page/0', '[openguimenu] misiones']),
        ('mascotas', 'BONE', '&6&lMascotas', ['&7Coleccion de 23 companeros en 3 paginas.', '&7Invoca, entrena o guarda a tu mascota.'], ['[openguimenu] mascotas']),
        ('cosmeticos', 'NAME_TAG', '&d&lCosmeticos y titulos', ['&7Elegi tus titulos y gorros.'], ['[openguimenu] cosmeticos']),
        ('skills', 'EXPERIENCE_BOTTLE', '&a&lHabilidades', ['&7Consulta tus niveles y habilidades.'], ['[close]', '[player] skills<delay=3>']),
        ('guia', 'BOOK', '&b&lGuia', ['&7Clases, equipo, recetas y Forja.'], ['[close]', '[player] trigger astral.guia set 1<delay=3>']),
        ('comandos', 'OAK_SIGN', '&e&lComandos', ['&7Consulta como usar cada comando.'], ['[openguimenu] comandos']),
        ('spawn', 'RED_BED', '&f&lVolver al lobby', ['&7Volve a la plaza del Refugio.'], ['[close]', '[player] spawn<delay=3>']),
        ('fragmentos', 'AMETHYST_SHARD', '&d&lFragmentos Astrales', ['&7Coleccion y recompensas de los jefes.'], ['[openguimenu] fragmentos']),
        ('duelos', 'DIAMOND_SWORD', '&c&lDuelos', ['&7Desafia a otro jugador.', '&eEscribi /duel <jugador>.'], ['[close]', '[message] &eUsa /duel <jugador> para enviar un desafio.']),
    ]
    from menu_ui import SLOTS, KEYS, title as menu_title
    assert [b[0] for b in buttons] == list(KEYS)
    items = []
    for slot, (key, material, name, lore, commands) in zip(SLOTS, buttons):
        # Icono de Gemini (menu_ui.py); el material queda por si falta el pack.
        items += item(key, material, slot, name, lore,
                      extra={'item_model': f'astral:menu/icon_{key}', 'click_commands': ['[sound] UI_BUTTON_CLICK'] + commands})
    items += item('info', 'NETHER_STAR', 4, '&b&l%player_name%',
                  ['&7Saldo: &e%vault_eco_balance_formatted%$', '&7Abri este menu con la Estrella del slot 9.'],
                  extra={'update': 'true'})
    items += item('cerrar', 'BARRIER', 49, '&cCerrar',
                  extra={'click_commands': ['[sound] UI_BUTTON_CLICK', '[close]']})
    return menu(menu_title(), 'menu', 54, items, update=True)


# (comando, material, nombre, para que sirve, como se usa, acciones al hacer clic o None si hay que escribirlo)
COMANDOS = [
    ('Aventura', 'LIME_STAINED_GLASS_PANE', [
        ('parkour', 'FEATHER', '/minijuegos', ['Parkour, droppers y Color Escape.', 'Entras sin tu inventario: se devuelve al salir.'], '/minijuegos [id]', ['[openguimenu] parkour']),
        ('arenas', 'IRON_SWORD', '/arenas', ['Arenas PvP con tu equipo.', 'Conservas todo al morir.'], '/arenas [id]', ['[openguimenu] arenas']),
        ('menu', 'COMPASS', '/menu', ['Menu principal: expediciones, mazmorras,', 'misiones, bazar, mascotas y guia.', 'Tambien con la Estrella del slot 9.'], '/menu', ['[openguimenu] principal']),
        ('mazmorras', 'NETHER_STAR', '/mazmorras', ['Viaja a las mazmorras que ya descubriste', 'hablando con su guardian.'], '/mazmorras', ['[close]', '[player] mazmorras<delay=3>']),
        ('expediciones', 'FILLED_MAP', '/expediciones', ['Destinos de exploracion: Reino,', 'Cavernas y las zonas de busqueda.'], '/expediciones', ['[close]', '[player] expediciones<delay=3>']),
        ('spawn', 'RED_BED', '/spawn', ['Vuelve a la plaza del lobby.', 'Sirve si te perdes o te trabas.'], '/spawn', ['[close]', '[player] spawn']),
        ('guia', 'BOOK', 'Guia', ['Clases, equipo, recetas y la Forja.', 'Tambien desde /menu.'], 'Boton Guia en /menu', ['[close]', '[player] trigger astral.guia set 1']),
    ]),
    ('Personaje', 'LIGHT_BLUE_STAINED_GLASS_PANE', [
        ('skills', 'EXPERIENCE_BOTTLE', '/skills', ['Tus habilidades (Forja, Hechiceria,', 'Arqueria, Combate...) y sus niveles.'], '/skills', ['[close]', '[player] skills<delay=3>']),
        ('mascotas', 'BONE', '/mascotas', ['Invoca o guarda a tu mascota.', 'Sube de nivel matando mobs con ella.'], '/mascotas', ['[openguimenu] mascotas']),
        ('cosmeticos', 'NAME_TAG', '/cosmeticos', ['Elegi tu titulo para el chat entre', 'los que desbloqueaste. Tambien /titulos.'], '/cosmeticos', ['[openguimenu] cosmeticos']),
        ('titulo', 'PAPER', '/titulo quitar', ['Saca el titulo que tenes puesto.', 'No pierde los que desbloqueaste.'], '/titulo quitar', ['[close]', '[player] titulo quitar']),
        ('sb', 'ITEM_FRAME', '/sb', ['Muestra u oculta el panel de la', 'derecha (vida, oro, poder, nivel).'], '/sb', ['[close]', '[player] sb']),
        ('mochilas', 'CHEST', '/bp', ['Abre tu mochila virtual.', 'El permiso se compra en /shop.'], '/bp', ['[close]', '[player] bp<delay=3>']),
        ('proteccion', 'GOLDEN_SHOVEL', 'Proteccion de terreno', ['Compra area en /shop y marca', 'dos esquinas con una pala de oro.'], '/shop', ['[close]', '[player] economyshopgui:shop<delay=3>']),
        ('recetas', 'BOOK', 'Recetas y Forja', ['Consulta materiales y recetas', 'en la Guia Astral.'], 'Guia Astral', ['[close]', '[player] trigger astral.guia set 1']),
    ]),
    ('Economia', 'YELLOW_STAINED_GLASS_PANE', [
        ('balance', 'GOLD_INGOT', '/balance', ['Cuanto oro tenes.'], '/balance', ['[close]', '[player] balance']),
        ('baltop', 'GOLD_BLOCK', '/baltop', ['Los jugadores con mas oro.'], '/baltop', ['[close]', '[player] baltop']),
        ('pay', 'GOLD_NUGGET', '/pay', ['Pasale oro a otro jugador.'], '/pay <jugador> <cantidad>', None),
        ('shop', 'EMERALD', '/shop', ['Tienda del servidor: compra', 'materiales y objetos vanilla.'], '/shop', ['[close]', '[player] economyshopgui:shop<delay=3>']),
        ('sellgui', 'CHEST', 'Venta rapida', ['Pone objetos y cobralos', 'al precio del servidor.'], 'Clic para abrir', ['[close]', '[player] astralventa<delay=3>']),
        ('worth', 'OAK_SIGN', '/worth', ['Cuanto vale el objeto que', 'tenes en la mano.'], '/worth', ['[close]', '[player] worth']),
        ('ah', 'BELL', '/ah', ['Subastas entre jugadores.', 'Vender: objeto en la mano y /ah sell <precio>.'], '/ah', ['[close]', '[player] ah<delay=3>']),
        ('trade', 'VILLAGER_SPAWN_EGG', '/trade', ['Intercambio cara a cara con otro', 'jugador: objetos y oro, los dos confirman.'], '/trade <jugador>', None),
    ]),
    ('Cuenta', 'RED_STAINED_GLASS_PANE', [
        ('login', 'TRIPWIRE_HOOK', '/login', ['Entrar con tu clave al conectarte.', 'La primera vez: /register <clave> <clave>.'], '/login <clave>', None),
        ('changepassword', 'IRON_DOOR', '/changepassword', ['Cambiar tu clave.'], '/changepassword <vieja> <nueva>', None),
        ('premium', 'DIAMOND', '/premium', ['Solo cuentas originales: despues', 'entras sin escribir la clave.'], '/premium', None),
    ]),
]


def comandos_menu():
    """Lista de comandos para jugadores, agrupada por tema (una fila por tema)."""
    items = []
    used = set()
    for row, (tema, vidrio, cmds) in enumerate(COMANDOS, start=1):
        base = row * 9
        items += item(f'tema_{row}', vidrio, base, f'&f&l{tema}')
        used.add(base)
        for col, (key, material, name, que, uso, clic) in enumerate(cmds, start=1):
            lore = ['&7' + x for x in que] + ['', '&fUso: &e' + uso]
            if clic:
                lore.append('&aClic para usarlo.')
                extra = {'click_commands': ['[sound] UI_BUTTON_CLICK'] + clic}
            else:
                lore.append('&7Escribilo en el chat.')
                extra = {'click_commands': ['[close]', f'[message] &eEscribi: &f{uso}']}
            items += item(f'cmd_{key}', material, base + col, '&e&l' + name, lore, extra=extra)
            used.add(base + col)
    items += item('info', 'WRITABLE_BOOK', 4, '&e&lComandos de AstralRPG',
                  ['&7Pasa el cursor por cada uno para ver', '&7para que sirve. Los que no piden datos', '&7se usan con un clic.'])
    items += item('volver', 'ARROW', 49, '&fVolver al menu', extra={'click_commands': ['[openguimenu] principal']})
    used |= {4, 49}
    items += relleno('GRAY_STAINED_GLASS_PANE', 54, used)
    return menu('&8Comandos de AstralRPG', 'comandos', 54, items)


def misiones_menu(current_page=0):
    """Tarjetas grandes: tocar la mision o ACEPTAR inicia el mismo flujo."""
    from cronista_ui import title as cronista_title
    P = "%player_name%"
    priorities = {}
    card_slots = list(range(9, 36))
    primary_slots = [38, 39, 40, 41, 42]

    def req(**scores):
        return "\n      requirements:" + "".join(
            f"\n        r{i}:\n          type: string equals\n          input: {q(SCORE.format('aq.' + key))}\n          output: {q(value)}"
            for i, (key, value) in enumerate(scores.items()))

    def action(function):
        page = int(function.rsplit('/', 1)[1]) if function.startswith('gui/page/') else current_page
        # Abrir desde consola reconstruye las condiciones con los scores ya
        # actualizados. No cerrar para mandar al jugador a leer el chat.
        return [f"[console] execute as {P} at @s run function astral:quest/{function}",
                f"[console] dm open {mission_menu_id(page)} {P}<delay=2>"]

    def button(key, material, slot, name, lore, page, function=None, model=None, shift=False, **scores):
        if page != current_page:
            return []
        priorities[slot] = priorities.get(slot, 0) + 1
        extra = {'priority': priorities[slot], 'update': 'true'}
        if scores:
            extra['view_requirement'] = req(**scores)
        if model:
            extra['item_model'] = q(model if ':' in model else 'astral:cronista/' + model)
        if function:
            if shift:
                extra['left_click_commands'] = ['[message] &7Para pausar, usa &eShift + clic&7. Tus avances se conservan.']
                extra['shift_left_click_commands'] = action(function)
            else:
                extra['click_commands'] = action(function)
        return item(key, material, slot, name, lore, extra=extra)

    def card_button(key, name, lore, page, model, function=None, **scores):
        lines = []
        for index, slot in enumerate(card_slots):
            lines += button(key if slot == 22 else f'{key}_hit_{slot}', 'PAPER', slot, name, lore, page,
                            function, model=f'{model}_{index}', **scores)
        return lines

    def primary(key, caption, lore, page, function=None, model='accept', **scores):
        lines = []
        for index, slot in enumerate(primary_slots):
            lines += button(key if slot == 40 else f'{key}_hit_{slot}', 'PAPER', slot, caption, lore, page,
                            function, model=f'{model}_{index}', **scores)
        return lines

    L = []
    for page, label, icon, model in [(0, 'Historia', 'BOOK', 'history'), (1, 'Diaria facil - 300$', 'CLOCK', 'easy'),
                                     (2, 'Diaria media - 750$', 'CLOCK', 'medium'), (3, 'Diaria dificil - 1500$', 'CLOCK', 'hard')]:
        L += item(f'tab_{page}', icon, page, f'&b&l{label}', ['&7Abre la tarjeta de esa mision.',
                  '&7Cambiar de pestana no acepta nada.'], extra={'item_model': q('astral:cronista/' + model),
                  'click_commands': action(f'gui/page/{page}')})
    L += item('ayuda', 'CLOCK', 8, '&b&lComo aceptar', ['&f1. Lee el objetivo y el premio en la tarjeta.',
              '&f2. Clic en la tarjeta o en &aACEPTAR MISION&f.', '&f3. Vas a ver &bACTIVA &fy una confirmacion.',
              '&f4. Completa el objetivo y usa &eCOMPROBAR&f.', '&7Las diarias cambian a las 00:00 (Argentina).'],
              extra={'item_model': q('astral:cronista/active')})

    rewards = [300, 500, 1000, 1500, 2000, 2500, 3000, 5000, 10000]
    progress = {
        1: ['&7Herrero: &f' + SCORE.format('aq.herrero') + '/1', '&7Forja tier I: &f' + SCORE.format('aq.forge1') + '/1'],
        2: ['&7Espantapajaros: &f' + SCORE.format('aq.scare') + '/10', '&7Armored Grubs: &f' + SCORE.format('aq.bee') + '/10', '&7Elites: &f' + SCORE.format('aq.helite') + '/1'],
        3: ['&7Cangrejo: &f' + SCORE.format('aq.f1') + '/1'],
        4: ['&7Caras: &f' + SCORE.format('aq.face') + '/15', '&7Chaman: &f' + SCORE.format('aq.f2') + '/1'],
        5: ['&7Momia: &f' + SCORE.format('aq.f3') + '/1'], 6: ['&7Minas: &f' + SCORE.format('aq.f4') + '/1'],
        7: ['&7Yeti: &f' + SCORE.format('aq.f5') + '/1'],
        8: ['&7Forja tier V: &f' + SCORE.format('aq.forge5') + '/1', '&7Golem: &f' + SCORE.format('aq.f6') + '/1'],
    }
    for state in range(10):
        chapter = max(1, state)
        base = ['&f' + line for line in textwrap.wrap(CHAPTERS[chapter - 1], 43)]
        base += ['', f'&6Recompensa: {rewards[chapter - 1]}$']
        if chapter == 2: base += ['&6+ una pieza de armadura tier I a eleccion']
        if chapter in (5, 7): base += ['&6+ material astral']
        if chapter == 9: base += ['&6+ titulo Portador de la Estrella']
        base += [''] + progress.get(chapter, [])
        for active in ((0,) if state == 0 else (0, 1)):
            scores = {'state': state, **({'accepted': active} if state else {})}
            status = 'active' if active else 'available'
            lore = base + ['', '&b&lACTIVA - ya la aceptaste.' if active else '&e&lSIN ACEPTAR',
                           '&7Completa y usa COMPROBAR.' if active else '&aClic en esta tarjeta para aceptarla.']
            L += card_button(f'historia_{state}_{status}', f'&b&lCapitulo {chapter}/9', lore, 0,
                             f'story_{state}_{status}', None if active else 'gui/accept', **scores)
            if active:
                L += primary(f'cobrar_{state}', '&b&lCOMPROBAR OBJETIVOS', ['&bEsta mision YA esta aceptada.',
                             '&7Comprueba avances y cobra si terminaste.', '&7Si falta algo no consume ni paga.'], 0, 'viajero', model='claim', **scores)
                L += button(f'pausar_{state}', 'CLOCK', 45, '&cPausar mision', ['&7Conserva tus avances.',
                             '&eShift + clic para pausar.'], 0, 'gui/reject', model='pause', shift=True, **scores)
            else:
                L += primary(f'aceptar_{state}', '&a&lACEPTAR MISION', ['&fUn clic la deja ACTIVA.',
                             '&7No tenes que escribir comandos.'], 0, 'gui/accept', **scores)
                L += button(f'rechazar_{state}', 'CLOCK', 45, '&7Dejar para mas tarde', ['&7No acepta ni entrega premios.'],
                             0, 'gui/reject', model='pause', **scores)
    L += card_button('historia_fin', '&6&lHistoria completada', ['&7El Santuario Celestial te espera.'],
                     0, 'story_complete', state=10)
    L += primary('historia_terminada', '&6&lHISTORIA COMPLETADA', ['&7Completaste los nueve capitulos.'],
                 0, model='done', state=10)
    L += button('premio_pendiente', 'CHEST', 7, '&6Premio de armadura', ['&7Se desbloquea al cobrar el capitulo 2.'],
                 0, 'gui/page/4', model='reward')

    extras = {11: '&6+ Alma Corrupta', 12: '&6+ Alma Corrupta', 13: '&6+ 25% de Chispa Astral', 14: '&6+ 2 Esencias de Elite'}
    for did, tier, name, counter, goal, desc in DAILIES:
        page = tier + 1
        base = ['&f' + line for line in textwrap.wrap(desc, 43)] + ['', f'&6Recompensa: {[300, 750, 1500][tier]}$']
        if did in extras: base += [extras[did]]
        if counter:
            base += ['', f'&7Progreso: &f{SCORE.format("aq." + counter)}/{goal}' + (' cm (1000 bloques)' if counter == 'ride' else '')]
        else:
            base += ['', '&7Entrega junto al NPC indicado en el objetivo.', '&7Acepta primero; despues usa COMPROBAR.']
        for active, done, status in [(0, 0, 'available'), (1, 0, 'active'), (0, 1, 'done'), (1, 1, 'done')]:
            scores = {f'd{tier}': did, f'active{tier}': active, f'done{tier}': done}
            suffix = f'{did}_{active}_{done}'
            lore = base + ['', '&7Ya cobraste esta diaria.' if done else '&b&lACTIVA - ya la aceptaste.' if active else '&e&lSIN ACEPTAR',
                           '&7Volve manana.' if done else '&7Completa y usa COMPROBAR.' if active else '&aClic en esta tarjeta para aceptarla.']
            accept = f'gui/daily/accept/{tier}/{did}'
            L += card_button(f'diaria_{suffix}', '&b&l' + name, lore, page, f'daily_{did}_{status}',
                             accept if not active and not done else None, **scores)
            if done:
                L += primary(f'diaria_fin_{suffix}', '&7&lYA COBRADA', ['&7No se puede cobrar otra vez hoy.'], page, model='done', **scores)
            elif active:
                L += primary(f'diaria_cobrar_{suffix}', '&b&lCOMPROBAR OBJETIVOS', ['&bEsta diaria YA esta aceptada.',
                             '&7Comprueba avances y cobra si terminaste.'], page, f'gui/daily/claim/{tier}', model='claim', **scores)
                L += button(f'diaria_pausar_{suffix}', 'CLOCK', 45, '&cPausar diaria', ['&7Conserva avances hasta medianoche.',
                             '&eShift + clic para pausar.'], page, f'gui/daily/reject/{tier}', model='pause', shift=True, **scores)
            else:
                L += primary(f'diaria_aceptar_{suffix}', '&a&lACEPTAR MISION', ['&fUn clic la deja ACTIVA.',
                             '&7Desde ese momento cuenta el progreso.'], page, accept, **scores)
                L += button(f'diaria_rechazar_{suffix}', 'CLOCK', 45, '&7Dejar para mas tarde', ['&7No acepta ni entrega premios.'],
                             page, f'gui/daily/reject/{tier}', model='pause', **scores)

    for n, (cls, piece, material) in enumerate(((c, p, m) for c in ('Berserker', 'Mago', 'Arquero')
            for p, m in (('Casco', 'IRON_HELMET'), ('Pechera', 'IRON_CHESTPLATE'), ('Grebas', 'IRON_LEGGINGS'), ('Botas', 'IRON_BOOTS'))), 1):
        slot = [10, 11, 12, 13, 19, 20, 21, 22, 28, 29, 30, 31][n - 1]
        L += button(f'premio_{n}', material, slot, f'&6{cls} - {piece}', ['&7Una sola pieza del capitulo 2.',
                     '&eClic para elegir y recibirla.'], 4, f'gui/choice/{n}')
    if current_page != 4:
        L += item('sin_datos', 'BARRIER', 22, '&eMisiones sin cargar', ['&7Actualiza o avisa al administrador.'], extra={'priority': 9999})
        for slot in primary_slots:
            L += item('sin_accion' if slot == 40 else f'sin_accion_hit_{slot}', 'CLOCK', slot, '&7Esperando datos',
                      ['&7No se puede aceptar sin una mision asignada.'], extra={'priority': 9999,
                      'item_model': q(f'astral:cronista/waiting_{primary_slots.index(slot)}')})
    L += item('actualizar', 'CLOCK', 52, '&bActualizar', ['&7Vuelve a leer tus objetivos y estado.'],
              extra={'item_model': q('astral:cronista/refresh'), 'click_commands': action(f'gui/page/{current_page}')})
    L += item('volver', 'ARROW', 53, '&fVolver al menu', extra={'item_model': q('astral:cronista/back'),
              'click_commands': ['[openguimenu] principal']})
    result = menu(cronista_title(current_page), mission_menu_id(current_page), 54, L, update=True)
    return result.replace('items:\n', f"open_commands:\n- '[console] execute as {P} at @s run function astral:quest/sync'\n- '[refresh]<delay=2>'\nitems:\n", 1)


def mission_menu_id(page):
    return "misiones" if page == 0 else f"misiones_{page}"


def main():
    from minijuegos import generate as generate_minigames
    generate_minigames()
    from cosmeticos import generate as generate_cosmetics
    generate_cosmetics()
    from viajes_mazmorras import generate as generate_dungeon_travel
    generate_dungeon_travel()
    os.makedirs(os.path.join(OUT, "gui_menus"), exist_ok=True)
    menus = {f"{gid}": gacha_menu(gid, g) for gid, g in GACHAS.items()}
    menus.update({"mascotas": mascotas_menu(), "bazar": bazar_menu(), "subastas": subastas_menu(), "principal": principal_menu(), "misiones": misiones_menu(), "comandos": comandos_menu()})
    menus.update({mission_menu_id(page): misiones_menu(page) for page in range(1, 5)})
    menus.update({f"mascota_{pid}": mascota_detalle_menu(pid) for pid in MASCOTAS})
    menus.update({f"mascotas_{page}": mascotas_extra_menu(page) for page in (2, 3, 4)})
    for k, txt in menus.items():
        open(os.path.join(OUT, "gui_menus", f"{k}.yml"), "w", encoding="utf-8").write(txt)
    lista = ["# Pegar dentro de plugins/DeluxeMenus/config.yml, en 'gui_menus:' (generado por datapack-src/menus.py)", "gui_menus:"]
    lista += [f"  {k}:\n    file: {k}.yml" for k in menus]
    lista += ['  mazmorras:\n    file: mazmorras.yml']
    from cofre_mazmorra import generate as generate_cofres
    lista += [f'  {k}:\n    file: {k}.yml' for k in generate_cofres()]
    lista += ['  expediciones:\n    file: expediciones.yml']
    lista += ['  portales:\n    file: portales.yml']
    from minijuegos import DROPPERS
    lista += ['  parkour:\n    file: parkour.yml', '  arenas:\n    file: arenas.yml']
    lista += [f'  {g}:\n    file: {g}.yml' for g in DROPPERS]
    lista += [f'  {n}:\n    file: {n}.yml' for n in ('cosmeticos','cosmeticos_titulos','cosmeticos_sombreros')]
    open(os.path.join(OUT, "config-gui_menus.yml"), "w", encoding="utf-8").write("\n".join(lista) + "\n")
    print(f"menus: {len(menus)} -> {os.path.abspath(OUT)}")


if __name__ == "__main__":
    main()
