"""Parkour y arenas: agregar una entrada y ejecutar python menus.py.

Los mapas de terceros se preparan aparte con minijuegos_mapas.py, siempre en .local.
"""
import json
from pathlib import Path

from minijuegos_datapack import MAPS as DATAPACK_MAPS

ROOT = Path(__file__).resolve().parent.parent
PARKOURS = [dict(id='spiral', world='parkour_spiral', name='Spiral Parkour Challenge',
                 icon='FEATHER', description='Una espiral de saltos hasta la cima.',
                 difficulty='Progresiva', arrival=(0.5, -11, -1.5, 0, 0), rescue_y=-20),
            dict(id='spiral2', world='parkour_spiral2', name='Parkour Spiral 2',
                 icon='PHANTOM_MEMBRANE', description='La segunda espiral: mas alta y mas larga.',
                 difficulty='Dificil', arrival=(0.5, 54, -96.5, 0, 0), rescue_y=-70, logic=True),
            dict(id='paradise3', world='parkour_paradise3', name='Parkour Paradise 3',
                 icon='SUNFLOWER', description='Islas de saltos unidas por portales.',
                 difficulty='Media', arrival=(-33.5, 131, 766.5, 0, 0), rescue_y=-10, logic=True),
            dict(id='colorescape', world='colorescape', name='Color Escape', icon='LIME_DYE',
                 description='Escape de colores: resolve cada sala para salir.', difficulty='Puzzle',
                 arrival=(0.5, -14, 0.5, 0, 0), rescue_y=-70, logic=True, solo=True),
            # Magma Run (Filip00_, 26.2 bajado a 26.1): command blocks, para un jugador. Sus puntajes
            # y la barra estaban en los datos del mapa: se crean, y cada jugador arranca con los
            # valores que tenia el autor. Cambia velocidad y caida segura: se restauran al salir.
            dict(id='magmarun', world='magmarun', name='Magma Run', icon='MAGMA_BLOCK',
                 description='Corre antes de que suba el magma: 7 temas.', difficulty='Carrera',
                 arrival=(-28.5, 57, 74.5, 0, 0), rescue_y=-70, logic=True, solo=True,
                 init_scores=[('magma', 4), ('lvl', 0), ('magma_on_off_s', 0), ('author', 0),
                              ('difficulty', 0), ('RNG', 0), ('magma_speed', 1), ('rngsec', 0),
                              ('magma_stop', 0), ('level_progress', 0), ('outline_sec', 0),
                              ('outline_limit', 0), ('progress', 0), ('starting_game', 1),
                              ('outline', 0), ('choose_theme', 0)],
                 # Marcas que el autor tenia puestas a mano: sin "lobby" el boton Start no hace nada.
                 init_tags=['lobby', 'Player', 'magma_fast', 'magmasound'], exit_tags=['Start'],
                 bossbar=('minecraft:progress', 'Level Progress', 10, 'red')),
            # Datapacks adaptados con minijuegos_datapack.py (solo actuan en su mundo).
            dict(id='batallanaval', world='battleship', name='Batalla Naval', icon='OAK_BOAT',
                 description='Hunde la flota rival: 2 jugadores.', difficulty='2 jugadores',
                 arrival=(19.5, 5, 37.5, 0, 0), rescue_y=-70, logic=True)]
# Tower Defence se saco el 08/11/2026: su brujula "Game Menu" no abria el menu en el server
# (el clic no llegaba ni al mapa ni a Skript). El mundo sigue en el server, sin datapack.
# Droppers: cada nivel es un destino; se gana cayendo al agua y si te estrellas volves a empezar.
# Salidas leidas de los command blocks de cada mapa (docs/IDEAS.md).
# Cada nivel: (titulo, (x, y, z) de la salida original, Y de salida corregida, Y de llegada al fondo).
# Pedido del dueno (08/11/2026): aparecer parado justo encima de la placa de salida (ni arriba en el
# aire ni debajo), para elegir hacia donde tirarse. La Y de salida es la de la placa + 1. Se gana al caer al agua o al quedar parado bajo la Y de llegada (slime,
# alfombra del fondo...). None = como estaba (funcionaba). Se sacaron GLaDOS, Small World, Anatomy y
# Rainbow del facil: sin la logica original no son droppers (Rainbow ni tiene fondo).
DROPPERS = {
    'dropper_facil': dict(name='The Easiest Dropper', icon='WATER_BUCKET', rescue_y=-10, levels=[
        ('Epilepsy Warning', (1009, 253, 468), None, 6), ('Gaming Rig', (1036, 169, 761), None, 15),
        ('Metropolis', (347, 250, -163), None, None), ('Solar System', (150, 256, 983), None, None),
        ('The Nether', (310, 253, 143), None, 12), ('Pixel Art', (300, 252, -2), None, 6)]),
    # H4rs tiene agua decorativa a mitad de caida (Y 196-240); el agua final esta en Y 3-6.
    'dropper_h4rs': dict(name='The Dropper (H4rs)', icon='HEART_OF_THE_SEA', rescue_y=-70, finish_y=20, levels=[
        (None, (-75, 250, -271), 246, None), (None, (-68, 250, -246), 250, None),
        (None, (-75, 250, -219), 246, None), (None, (-75, 243, -191), None, None),
        (None, (-75, 252, -155), 251, None), (None, (-75, 250, -128), None, None),
        (None, (-73, 253, -111), 252, None), (None, (-75, 251, -75), None, None),
        (None, (-75, 249, -52), 248, None), (None, (-74, 251, -32), 250, None)]),
}
for _world, _d in DROPPERS.items():
    for _n, (_title, (_x, _y, _z), _start, _finish) in enumerate(_d['levels'], 1):
        PARKOURS.append(dict(id=f'{_world.split("_")[1]}{_n}', world=_world, group=_world,
                             name=f'Nivel {_n}' + (f' - {_title}' if _title else ''), icon='WATER_BUCKET',
                             description=_d['name'], difficulty='Dropper',
                             arrival=(_x + .5, _start if _start is not None else _y, _z + .5, 0, 0),
                             rescue_y=_d['rescue_y'],
                             finish_y=_finish if _finish is not None else _d.get('finish_y', _y - 60)))
# La arena existente conserva los 25 puntos verificados, sin depender de datos locales ajenos.
ARENAS = [dict(id='clasica', world='arena', name='Arena Astral', icon='IRON_SWORD',
               description='La arena clasica de AstralRPG.', arrival=(-206.5, 73, -2371.5, 0, 0),
               spawn_points=[(x + .5, 73, z + .5, 0, 0) for x in range(-217, -195, 5)
                             for z in range(-2382, -2360, 5)], rescue_y=0)] + [
    dict(id=f'tft{i}', world='arenas_tft', name=f'TFT - Arena {i}', icon=icon,
         description='Arena del paquete TFT Arenas.', arrival=arrival, rescue_y=120)
    for i, icon, arrival in [(1, 'STONE_SWORD', (-286.5, 143, -550.5, 0, 0)),
                             (2, 'GOLDEN_SWORD', (-286.5, 139, -282.5, 0, 0)),
                             (3, 'DIAMOND_SWORD', (-286.5, 139, -14.5, 0, 0))]]
NPC_POSITIONS = {'parkour': (121.5, 100, 193.529), 'arena': (167.548, 102, 218.504, -89.6, 0)}
# Color Escape es un puzzle de una persona y lo que se abre queda abierto. Se juega de a uno y,
# cuando el ultimo sale, se copia encima la version limpia guardada lejos (08/11/2026).
# Zona del puzzle (sus command blocks, cofres y carteles: x -26..114, y -20..-1, z -22..305) con margen.
CE_BOX = dict(x1=-32, x2=120, y1=-24, y2=4, z1=-28, z2=308)
CE_BACKUP_DX = 3000      # copia limpia, 3000 bloques al este en el mismo mundo
CE_SLICE = 7             # 153 x 29 x 7 = 31.059 bloques por clone (< 32.768)


# Mundos de mini juego sin entrada propia en el menu (el End del Tower Defence).
EXTRA_WORLDS = ()


def parkour_worlds():
    return tuple(dict.fromkeys([d['world'] for d in PARKOURS] + list(EXTRA_WORLDS)))


def dropper_worlds():
    return tuple(DROPPERS)


def logic_worlds():
    """Mapas que conservan sus command blocks (selectores reescritos en minijuegos_mapas.py)."""
    return tuple(d['world'] for d in PARKOURS if d.get('logic'))


def arena_worlds():
    return tuple(dict.fromkeys(d['world'] for d in ARENAS))


def definitions():
    return [('parkour', d) for d in PARKOURS] + [('arena', d) for d in ARENAS]


def menu_data(kind):
    from menu_ui import decorate
    if kind == 'arena':
        from travel_ui import title, ARENA_SLOTS
        if len(ARENAS)!=len(ARENA_SLOTS) or {d['id'] for d in ARENAS}!=set(ARENA_SLOTS):
            raise ValueError('Actualizar las tarjetas de arte al cambiar el catalogo de arenas')
        items={}
        themes=('Coliseo','Ruinas','Vacio','Volcan')
        for d,theme in zip(ARENAS,themes):
            for n,slot in enumerate(ARENA_SLOTS[d['id']]):
                key=d['id'] if n==0 else f'{d["id"]}_{slot}'
                items[key]=dict(material='PAPER',slot=slot,item_model='astral:viajes/blank',
                    display_name='&f'+theme,lore=['&7'+d['name'],'&7'+d['description'],'&7No perdes nada al morir.'],
                    click_commands=['[close]',f'[player] arenas {d["id"]}<delay=3>'])
        for key,slots,commands in [('lobby',[45,46,47],['[close]','[player] spawn<delay=3>']),('cerrar',[51,52,53],['[close]'])]:
            for n,slot in enumerate(slots):
                items[key if n==0 else f'{key}_{slot}']=dict(material='PAPER',slot=slot,item_model='astral:viajes/blank',display_name='&f'+key.title(),click_commands=commands)
        # Lobby: la primera casilla muestra la barrera vanilla.
        items['lobby']=dict(items['lobby'],material='BARRIER',display_name='&fVolver al lobby');del items['lobby']['item_model']
        return decorate(dict(menu_title=title('arenas'),size=54,items=items))
    if kind == 'parkour':
        maps = [d for d in PARKOURS if not d.get('group')]
        maps += [dict(id=g, name=d['name'], icon=d['icon'], description=f'{len(d["levels"])} niveles de caida libre.',
                      difficulty='Dropper', open_menu=g) for g, d in DROPPERS.items()]
    elif kind in DROPPERS:
        maps = [d for d in PARKOURS if d.get('group') == kind]
    else:
        maps = ARENAS
    command = 'arenas' if kind == 'arena' else 'parkour'
    slots = [10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25]
    if len(maps) > len(slots):
        raise ValueError('Ampliar el selector antes de agregar mas de 14 mapas')
    items = {}
    for slot, d in zip(slots, maps):
        lore = ['&7' + d['description']]
        if kind != 'arena':
            lore += ['&7Tipo: &f' + d['difficulty'], '&7Sin tu inventario ni vida extra:', '&7se te devuelven al salir.']
        else:
            lore += ['&7Se pelea con tu equipo;', '&7no perdes nada al morir.']
        if d.get('needs_point'):
            lore += ['&eRequiere una llegada revisada por un OP.']
        click = ['[openguimenu] ' + d['open_menu']] if d.get('open_menu') else ['[close]', f'[player] {command} {d["id"]}<delay=3>']
        items[d['id']] = dict(material=d['icon'], slot=slot, display_name='&a&l' + d['name'], lore=lore, click_commands=click)
    for slot in slots[len(maps):]:
        items[f'proximo_{slot}'] = dict(material='GRAY_DYE', slot=slot, display_name='&7Proximamente')
    if kind in DROPPERS:
        items['volver'] = dict(material='ARROW', slot=30, display_name='&fVolver a Mini juegos', click_commands=['[openguimenu] parkour'])
    else:
        items['lobby'] = dict(material='RED_BED', slot=30, display_name='&fVolver al lobby',
                              click_commands=['[close]', '[player] spawn<delay=3>'])
    items['cerrar'] = dict(material='BARRIER', slot=32, display_name='&cCerrar', click_commands=['[close]'])
    titles = {'parkour': '&8Mini juegos', 'arena': '&8Arenas PvP', **{g: '&8' + d['name'] for g, d in DROPPERS.items()}}
    return decorate(dict(menu_title=titles[kind], size=36, items=items))


def script():
    lines = ['# Generado por minijuegos.py. Mundos y destinos limitados a la lista Python.',
             '# Persistentes: puntos OP, mapa elegido y modo anterior (reconexiones/reinicios).']
    for kind, worlds in [('parkour', parkour_worlds()), ('arena', arena_worlds())]:
        names = ' or '.join(f'"{w}"' for w in worlds)
        lines += [f'function astral_{kind}_world(w: world) :: boolean:',
                  f'    if name of {{_w}} is {names}:', '        return true', '    return false', '']
    dw = ' or '.join(f'"{w}"' for w in dropper_worlds())
    lines += ['function astral_dropper_world(w: world) :: boolean:', f'    if name of {{_w}} is {dw}:',
              '        return true', '    return false', '',
              '# Mini juegos lo mas vanilla posible (pedido del dueno, 08/11/2026): el inventario y la vida',
              '# extra se guardan al entrar y se devuelven al salir. Variables persistentes: sobreviven a',
              '# desconexiones y reinicios. Arenas PvP no entran aca: se pelea con tu equipo.',
              'function astral_mj_guardar(p: player):',
              '    set {_u} to uuid of {_p}',
              '    if {astral.mj.saved::%{_u}%} is set:', '        stop',
              '    loop 41 times:',
              '        set {_i} to loop-value - 1',
              '        set {_it} to slot {_i} of inventory of {_p}',
              '        if {_it} is not air:',
              '            set {astral.mj.inv::%{_u}%::%{_i}%} to {_it}',
              '    set {astral.mj.saved::%{_u}%} to now',
              '    clear inventory of {_p}',
              '    remove all potion effects from {_p}',
              '    send "&7Tu inventario y tu vida extra quedan guardados: &fse devuelven al salir." to {_p}',
              '',
              '# Vida vanilla (20). Se revisa seguido: al reaparecer, las skills pueden volver a sumar vida.',
              'function astral_mj_vida(p: player):',
              '    if max health of {_p} is 10:', '        stop',
              '    set {_u} to uuid of {_p}',
              '    if {-astral.mj.vida::%{_u}%} is set:', '        stop',
              '    set {-astral.mj.vida::%{_u}%} to true',
              '    set {_n} to name of {_p}',
              '    execute console command "attribute %{_n}% minecraft:max_health modifier remove astral:minijuego"',
              '    wait 1 tick',
              '    set {_h} to max health of {_p} * 2',
              '    if {_h} is not 20:',
              '        set {_d} to 20 - {_h}',
              '        execute console command "attribute %{_n}% minecraft:max_health modifier add astral:minijuego %{_d}% add_value"',
              '    wait 1 tick',
              '    if health of {_p} > max health of {_p}:',
              '        set health of {_p} to max health of {_p}',
              '    delete {-astral.mj.vida::%{_u}%}',
              '',
              '# Borra todo lo que deja un mini juego: al salir al lobby y al pasar a otro mini juego',
              '# (pedido del dueno, 08/11/2026: Magma Run dejaba sin salto y con su barra en Tower Defence).',
              'function astral_mj_limpiar(p: player):',
              '    if {astral.mj.saved::%uuid of {_p}%} is set:',
              '        clear inventory of {_p}',
              '    remove all potion effects from {_p}',
              '    # Magma Run cambia atributos base del jugador: vuelven a los de siempre.',
              '    execute console command "attribute %name of {_p}% minecraft:movement_speed base reset"',
              '    execute console command "attribute %name of {_p}% minecraft:safe_fall_distance base reset"',
              '    execute console command "attribute %name of {_p}% minecraft:jump_strength base reset"',
          ] + [f'    execute console command "bossbar set {d["bossbar"][0]} players"' for d in PARKOURS if d.get('bossbar')] + [
              f'    remove "{t}" from scoreboard tags of {{_p}}' for d in PARKOURS
               for t in d.get('init_tags', []) + d.get('exit_tags', [])] + [
              '    # Datapacks adaptados (minijuegos_datapack.py): marcas, puntajes y efectos del mapa.',
          ] + [f'    execute console command "execute as %name of {{_p}}% run function {d["prefix"]}_main:astral/salir"'
               for d in DATAPACK_MAPS.values()] + [
              '',
              'function astral_mj_devolver(p: player):',
              '    set {_u} to uuid of {_p}',
              '    if {astral.mj.saved::%{_u}%} is not set:', '        stop',
              '    astral_mj_limpiar({_p})',
              '    loop indices of {astral.mj.inv::%{_u}%::*}:',
              '        set {_i} to loop-value parsed as integer',
              '        set slot {_i} of inventory of {_p} to {astral.mj.inv::%{_u}%::%loop-value%}',
              '    delete {astral.mj.inv::%{_u}%::*}',
              '    delete {astral.mj.saved::%{_u}%}',
              '    execute console command "attribute %name of {_p}% minecraft:max_health modifier remove astral:minijuego"',
              '',
              'function astral_parkour_mode(p: player):',
              '    set {_u} to uuid of {_p}',
              '    if astral_parkour_world(world of {_p}) is true:',
              '        if {astral.minijuegos.mode::%{_u}%} is not set:',
              '            set {astral.minijuegos.mode::%{_u}%} to gamemode of {_p}',
              '        if {_p} is op:',
              '            add "astral.op" to scoreboard tags of {_p}',
              '        # Todos en aventura; solo un OP puede quedarse en creativo (para revisar el mapa).',
              '        if gamemode of {_p} is not adventure:',
              '            if {_p} is not op:',
              '                set gamemode of {_p} to adventure',
              '            else if gamemode of {_p} is not creative:',
              '                set gamemode of {_p} to adventure',
              '        astral_mj_guardar({_p})',
              '        astral_mj_vida({_p})',
              '        # Vision nocturna: solo si le falta (un mapa o la muerte la pueden sacar).',
              "        execute console command \"execute as %name of {_p}% unless entity @s[nbt={active_effects:[{id:'minecraft:night_vision'}]}] run effect give @s minecraft:night_vision infinite 0 true\"",
              '        set food level of {_p} to 20',
              '        set saturation of {_p} to 5',
              '    else:',
              '        remove "astral.op" from scoreboard tags of {_p}',
              '        astral_mj_devolver({_p})',
              '        if {astral.minijuegos.mode::%{_u}%} is set:',
              '            set gamemode of {_p} to {astral.minijuegos.mode::%{_u}%}',
              '            delete {astral.minijuegos.mode::%{_u}%}', '',
              '# Dropper: al caer al agua bien abajo se pasa al siguiente nivel.',
              'function astral_dropper_ganar(p: player, next: text):',
              '    set {_u} to uuid of {_p}',
              '    if {-astral.dropper.win::%{_u}%} is set:', '        stop',
              '    set {-astral.dropper.win::%{_u}%} to true',
              '    send title "&a&lNivel completado" to {_p} for 2 seconds',
              '    play sound "entity.player.levelup" to {_p}',
              '    wait 2 seconds',
              '    delete {-astral.dropper.win::%{_u}%}',
              '    if {_p} is not online:', '        stop',
              '    if astral_dropper_world(world of {_p}) is false:', '        stop',
              '    if {_next} is "":',
              '        send "&6&lTerminaste todos los niveles de este dropper." to {_p}',
              '        execute console command "spawn %name of {_p}%"',
              '        stop',
              '    astral_minijuego_ir({_p}, {_next})', '',
              'function astral_minijuego_ir(p: player, id: text):']
    for kind, d in definitions():
        key = kind + '.' + d['id']
        lines += [f'    if {{_id}} is "{key}":', f'        if world "{d["world"]}" is not set:',
                  '            send "&eEse mundo todavia no esta disponible." to {_p}', '            stop',
                  f'        set {{_l}} to {{astral.punto::{key}}}']
        if d.get('needs_point'):
            lines += ['        if {_l} is not set:',
                      '            send "&eEsta arena necesita que un OP revise y fije su llegada." to {_p}', '            stop']
        else:
            points = d.get('spawn_points', [d['arrival']])
            lines += ['        if {_l} is not set:']
            if len(points) > 1:
                lines += [f'            set {{_n}} to random integer between 1 and {len(points)}']
            for i, (x, y, z, yaw, pitch) in enumerate(points, 1):
                indent = '            '
                if len(points) > 1:
                    lines += [f'            if {{_n}} is {i}:']; indent += '    '
                lines += [f'{indent}set {{_l}} to location({x}, {y}, {z}, world "{d["world"]}", {yaw}, {pitch})']
        if d.get('solo'):
            lines += [f'        if name of world of {{_p}} is not "{d["world"]}":',
                      f'            loop all players in world "{d["world"]}":',
                      '                if loop-player is not {_p}:',
                      f'                    send "&e{d["name"]} esta ocupado: se juega de a uno. &7Proba en un rato." to {{_p}}',
                      '                    stop']
        lines += [f'        if name of world of {{_p}} is not "{d["world"]}":',
                  '            if astral_parkour_world(world of {_p}) is true:',
                  '                astral_mj_limpiar({_p})']
        if d['id'] == 'colorescape':
            lines += ['        set {astral.ce.sucio} to true']
        for objective, value in d.get('init_scores', []):
            lines += [f'        execute console command "scoreboard players set %name of {{_p}}% {objective} {value}"']
        for tag in d.get('init_tags', []):
            lines += [f'        add "{tag}" to scoreboard tags of {{_p}}']
        if d.get('bossbar'):
            lines += [f'        execute console command "bossbar set {d["bossbar"][0]} players %name of {{_p}}%"']
        if kind == 'parkour':
            lines += ['        if {astral.minijuegos.mode::%uuid of {_p}%} is not set:',
                      '            set {astral.minijuegos.mode::%uuid of {_p}%} to gamemode of {_p}']
        lines += [f'        set {{astral.minijuegos.selected::%uuid of {{_p}}%}} to "{key}"',
                  '        set {_x} to x-coordinate of {_l}', '        set {_y} to y-coordinate of {_l}',
                  '        set {_z} to z-coordinate of {_l}', '        set {_yaw} to yaw of {_l}',
                  '        set {_pitch} to pitch of {_l}', '        set {_name} to name of {_p}',
                  '        set velocity of {_p} to vector(0, 0, 0)', '        set fall distance of {_p} to 0',
                  '        # Efectos de otro mini juego (vision nocturna, saturacion...) no pasan a este.',
                  '        remove all potion effects from {_p}',
                  f'        execute console command "execute in minecraft:{d["world"]} run minecraft:tp %{{_name}}% %{{_x}}% %{{_y}}% %{{_z}}% %{{_yaw}}% %{{_pitch}}%"',
                  '        astral_parkour_mode({_p})', '        stop']
    for command, kind in [('parkour', 'parkour'), ('minijuegos', 'parkour'), ('arenas', 'arena')]:
        lines += ['', f'command /{command} [<text>]:', '    executable by: players', '    trigger:',
                  '        if arg-1 is not set:', f'            execute console command "dm open {'arenas' if kind == 'arena' else 'parkour'} %name of player%"', '            stop']
        for k, d in definitions():
            if k == kind:
                lines += [f'        if arg-1 is "{d["id"]}":',
                          f'            astral_minijuego_ir(player, "{kind}.{d["id"]}")', '            stop']
        lines += [f'        send "&eUsa /{command} para elegir un destino." to player']
    b = CE_BOX
    span = f'{b["x1"]} {b["z1"]} {b["x2"]} {b["z2"]}'
    back = f'{b["x1"] + CE_BACKUP_DX} {b["z1"]} {b["x2"] + CE_BACKUP_DX} {b["z2"]}'
    lines += ['', '# Color Escape: guardar = puzzle -> copia limpia; restaurar = copia limpia -> puzzle.',
              'function astral_ce_clonar(dir: text):',
              '    # Puntajes propios del mapa (no venian: el mapa se preparo sin sus datos).',
              '    execute console command "scoreboard objectives add colorEscape dummy"',
              '    execute console command "scoreboard objectives add advancement dummy"',
              f'    execute console command "execute in minecraft:colorescape run forceload add {span}"',
              f'    execute console command "execute in minecraft:colorescape run forceload add {back}"',
              '    wait 3 seconds',
              f'    set {{_z}} to {b["z1"]}',
              f'    while {{_z}} <= {b["z2"]}:',
              f'        set {{_z2}} to min({{_z}} + {CE_SLICE - 1}, {b["z2"]})',
              '        if {_dir} is "guardar":',
              f'            execute console command "execute in minecraft:colorescape run clone {b["x1"]} {b["y1"]} %{{_z}}% {b["x2"]} {b["y2"]} %{{_z2}}% {b["x1"] + CE_BACKUP_DX} {b["y1"]} %{{_z}}% replace"',
              '        else:',
              f'            execute console command "execute in minecraft:colorescape run clone {b["x1"] + CE_BACKUP_DX} {b["y1"]} %{{_z}}% {b["x2"] + CE_BACKUP_DX} {b["y2"]} %{{_z2}}% {b["x1"]} {b["y1"]} %{{_z}}% replace"',
              '        wait 2 ticks',
              f'        add {CE_SLICE} to {{_z}}',
              '    if {_dir} is not "guardar":',
              '        execute console command "execute in minecraft:colorescape run minecraft:kill @e[type=item,distance=0..]"',
              '        execute console command "scoreboard players reset * colorEscape"',
              '        execute console command "scoreboard players reset * advancement"',
              f'    execute console command "execute in minecraft:colorescape run forceload remove {span}"',
              f'    execute console command "execute in minecraft:colorescape run forceload remove {back}"',
              '',
              'command /colorescape <text>:',
              '    permission: astral.minas.admin',
              '    trigger:',
              '        if arg-1 is "guardar":',
              '            send "&eGuardando la copia limpia de Color Escape (el mapa tiene que estar sin jugar)..." to command sender',
              '            astral_ce_clonar("guardar")',
              '            set {astral.ce.copia} to true',
              '        else if arg-1 is "reiniciar":',
              '            send "&eReiniciando Color Escape..." to command sender',
              '            astral_ce_clonar("restaurar")',
              '            delete {astral.ce.sucio}',
              '        else:',
              '            send "&eUsa /colorescape guardar o /colorescape reiniciar." to command sender',
              '',
              '# Cuando no queda nadie adentro, vuelve a como estaba.',
              'every 5 seconds:',
              '    if {astral.ce.sucio} is set:',
              '        if {astral.ce.copia} is set:',
              '            if world "colorescape" is set:',
              '                loop all players in world "colorescape":',
              '                    stop',
              '                delete {astral.ce.sucio}',
              '                astral_ce_clonar("restaurar")',
              '']
    lines += ['', 'command /astralpunto <text> [<text>]:', '    executable by: players', '    trigger:',
              '        if player is not op:', '            send "&cSolo OP." to player', '            stop',
              '        if arg-1 is "lista":']
    for kind, d in definitions():
        key = kind + '.' + d['id']
        lines += [f'            send "&e{kind} {d["id"]} &7({d["world"]}): %{{astral.punto::{key}}}%" to player']
    lines += ['            stop']
    for kind, d in definitions():
        lines += [f'        if arg-1 is "{kind}":', f'            if arg-2 is "{d["id"]}":',
                  f'                if name of world of player is not "{d["world"]}":',
                  f'                    send "&cPrimero entra al mundo {d["world"]}." to player', '                    stop',
                  f'                if y-coordinate of player is less than {d["rescue_y"]}:',
                  '                    send "&cLa llegada debe quedar por encima del limite de rescate." to player',
                  '                    stop',
                  f'                set {{astral.punto::{kind}.{d["id"]}}} to location of player',
                  '                send "&aLlegada guardada con orientacion." to player', '                stop']
    lines += ['        send "&eUsa /astralpunto <parkour|arena> <id> o /astralpunto lista." to player', '',
              'on world change:', '    wait 2 ticks', '    astral_parkour_mode(player)', '',
              'on join:', '    wait 2 ticks', '    astral_parkour_mode(player)', '',
              'on respawn:', '    wait 2 ticks',
              '    if astral_parkour_world(world of player) is true:',
              '        set {_id} to {astral.minijuegos.selected::%uuid of player%}',
              '        if {_id} is set:',
              '            astral_minijuego_ir(player, {_id})',
              '        stop']
    for world in arena_worlds():
        maps = [d for d in ARENAS if d['world'] == world]
        keys = ' or '.join(f'"arena.{d["id"]}"' for d in maps)
        lines += [f'    if name of world of player is "{world}":',
                  '        set {_id} to {astral.minijuegos.selected::%uuid of player%}',
                  f'        if {{_id}} is not {keys}:', f'            set {{_id}} to "arena.{maps[0]["id"]}"',
                  '        astral_minijuego_ir(player, {_id})']
    # Parkour y Color Escape: danio y muerte como en vanilla (pedido del dueno, 08/11/2026).
    # Al morir se conserva todo y se reaparece en la llegada del mapa (on respawn).
    lines += ['', 'on damage of player:', '    if astral_dropper_world(world of victim) is true:',
              '        cancel event',
              '        if damage cause is fall:',
              '            if {-astral.dropper.win::%uuid of victim%} is not set:',
              '                send "&cTe estrellaste. &7Volves al principio del nivel." to victim',
              '                astral_minijuego_ir(victim, {astral.minijuegos.selected::%uuid of victim%})', '',
              'on food level change:', '    if astral_parkour_world(world of player) is true:', '        cancel event', '',
              'every 10 ticks:', '    loop all players:', '        astral_parkour_mode(loop-player)',
              '        set {_w} to name of world of loop-player',
              '        set {_id} to {astral.minijuegos.selected::%uuid of loop-player%}']
    # Seleccion alternativa para quien entra por mvtp; TFT tiene llegadas verificadas.
    for world in dict.fromkeys(d['world'] for _, d in definitions()):
        entries = [(k, d) for k, d in definitions() if d['world'] == world]
        keys = ' or '.join(f'"{k}.{d["id"]}"' for k, d in entries)
        kind, first = entries[0]
        lines += [f'        if {{_w}} is "{world}":', f'            if {{_id}} is not {keys}:',
                  f'                set {{_id}} to "{kind}.{first["id"]}"',
                  '                set {astral.minijuegos.selected::%uuid of loop-player%} to {_id}']
        for kind, d in entries:
            lines += [f'            if {{_id}} is "{kind}.{d["id"]}":']
            if d.get('finish_y') is not None:
                group = [x for x in PARKOURS if x.get('group') == d['group']]
                pos = group.index(d)
                nxt = f'parkour.{group[pos + 1]["id"]}' if pos + 1 < len(group) else ''
                lines += [f'                if y-coordinate of loop-player is less than {d["finish_y"]}:',
                          '                    if block at loop-player is water:',
                          f'                        astral_dropper_ganar(loop-player, "{nxt}")',
                          '                    # Fondo sin agua (slime, alfombra): parado y vivo tambien gana.',
                          '                    else if loop-player is on ground:',
                          f'                        astral_dropper_ganar(loop-player, "{nxt}")']
            lines += [f'                if y-coordinate of loop-player is less than {d["rescue_y"]}:',
                      '                    if gamemode of loop-player is survival or adventure:']
            if d.get('needs_point'):
                lines += [f'                        if {{astral.punto::{kind}.{d["id"]}}} is not set:',
                          '                            execute console command "spawn %name of loop-player%"',
                          '                        else:', '                            astral_minijuego_ir(loop-player, {_id})']
            else:
                lines += ['                        astral_minijuego_ir(loop-player, {_id})']
    return '\n'.join(lines) + '\n'


def npc(kind):
    from portales import npc as portal_npc
    name = '&a&lMini juegos' if kind == 'parkour' else '&c&lArena PvP'
    menu = 'parkour' if kind == 'parkour' else 'arenas'
    return portal_npc(modelo=False).replace('portales.py', 'minijuegos.py').replace('astral_npc_portales', 'astral_npc_' + kind).replace('&b&lGuardian de los Portales', name).replace('dm open portales', 'dm open ' + menu)


def deployment():
    lines = ['# Generado por minijuegos.py. Ver docs/PARKOUR_Y_ARENAS.md antes de instalar.',
             '# Actualizacion TFT con mundos ya instalados: copiar SOLO estos dos archivos por Files:',
             '# build/minijuegos/astral_minijuegos.sk -> plugins/Skript/scripts/astral_minijuegos.sk',
             '# build/menus/DeluxeMenus/gui_menus/arenas.yml -> plugins/DeluxeMenus/gui_menus/arenas.yml',
             '# Recargar: skript:skript reload astral_minijuegos; dm reload. Revisar consola y probar /arenas tft1, tft2, tft3.',
             '# No requiere apagar ni reiniciar; si hubo muchas recargas, preferir un reinicio por Metaspace.',
             '# No reinstalar mundos para esta actualizacion. Lo siguiente es la instalacion inicial completa.',
             '# Apagar para instalar mundos NUEVOS. Nunca reemplazar world ni Worlds > Upload en world.',
             '# ZIP privados: .local/mapas/subir/parkour_spiral.zip y arenas_tft.zip.',
             '# Importacion depende del soporte del panel para mundos adicionales; si no existe, detener esa parte.',
             '# Si NO existen: con servidor encendido crear SOLO mundos nuevos, sin jugadores dentro:',
             'mv create minecraft:parkour_spiral normal --world-type FLAT --no-structures --generator-settings {"layers":[{"block":"minecraft:air","height":1}],"biome":"minecraft:the_void"}',
             'mv create minecraft:arenas_tft normal --world-type FLAT --no-structures --generator-settings {"layers":[{"block":"minecraft:air","height":1}],"biome":"minecraft:the_void"}',
             *[f'mv create minecraft:{w} normal --world-type FLAT --no-structures --generator-settings {{"layers":[{{"block":"minecraft:air","height":1}}],"biome":"minecraft:the_void"}}'
               for w in parkour_worlds() if w != 'parkour_spiral'],
             '# Apagar. Worlds > Upload SOLO en las filas nuevas parkour_spiral y arenas_tft, con su ZIP respectivo.',
             '# Archivos locales -> destino (editor Files; conservar las otras entradas de config.yml):']
    for name in ('principal', 'comandos', 'parkour', 'arenas'):
        lines += [f'build/menus/DeluxeMenus/gui_menus/{name}.yml -> plugins/DeluxeMenus/gui_menus/{name}.yml']
    lines += ['build/menus/DeluxeMenus/config-gui_menus.yml -> fusionar gui_menus en plugins/DeluxeMenus/config.yml',
              'build/minijuegos/astral_minijuegos.sk -> plugins/Skript/scripts/astral_minijuegos.sk',
              'build/gameplay/astral_gameplay.sk -> plugins/Skript/scripts/astral_gameplay.sk',
              'build/mythicmobs/mobs/minijuegos.yml -> plugins/MythicMobs/mobs/minijuegos.yml',
              'build/mythicmobs/mobs/arena.yml -> plugins/MythicMobs/mobs/arena.yml',
              '# No instalar dos definiciones astral_npc_arena. Se reutiliza y reubica el NPC existente.',
              '# Encender tras instalar los mundos; importar solo si aparecen como carpetas NUEVAS:',
              'mv import minecraft:parkour_spiral normal', 'mv import minecraft:arenas_tft normal',
              '# Paper 26.1: comprobar /mv list y /minecraft:execute in (autocompletado OP).',
              '# Claves esperadas: minecraft:parkour_spiral y minecraft:arenas_tft. Si difieren, NO abrir acceso.']
    for world in parkour_worlds() + arena_worlds():
        parkour = world in parkour_worlds()
        lines += [f'mv modify {world} set pvp {str(not parkour).lower()}',
                  f'mv modify {world} set gamemode survival',
                  f'mv gamerule set minecraft:keep_inventory true {world}',
                  f'mv gamerule set minecraft:spawn_mobs false {world}',
                  f'mv gamerule set minecraft:random_tick_speed 0 {world}',
                  f'mv gamerule set minecraft:command_blocks_work false {world}',
                  f'mv gamerule set minecraft:pvp {str(not parkour).lower()} {world}',
                  f'mv modify {world} set respawn-world {world}',
                  f'rg flag -w {world} __global__ build deny',
                  f'rg flag -w {world} __global__ block-break deny',
                  f'rg flag -w {world} __global__ block-place deny',
                  f'rg flag -w {world} __global__ chest-access deny',
                  f'rg flag -w {world} __global__ mob-spawning {"deny" if parkour else "allow"}',
                  f'rg flag -w {world} __global__ pvp {"deny" if parkour else "allow"}']
        if parkour:
            lines += [f'lp group default permission set mv.bypass.gamemode.{world} true']
            # Danio vanilla (en droppers el evento de caida marca que se estrello).
            lines += [f'mv gamerule set minecraft:fall_damage true {world}',
                      f'rg flag -w {world} __global__ fall-damage']
            if world in logic_worlds() or world in EXTRA_WORLDS:
                # Color Escape: sus command blocks (selectores ya limitados) y sus cofres y botones.
                lines += [f'mv gamerule set minecraft:command_block_output false {world}',
                          f'mv gamerule set minecraft:command_blocks_work true {world}',
                          f'rg flag -w {world} __global__ chest-access allow',
                          f'rg flag -w {world} __global__ interact allow',
                          f'rg flag -w {world} __global__ use allow']
                for d in PARKOURS:
                    if d['world'] == world:
                        lines += [f'scoreboard objectives add {o} dummy' for o, _ in d.get('init_scores', [])]
                        if d.get('bossbar'):
                            bid, name, top, color = d['bossbar']
                            lines += [f'bossbar add {bid} "{name}"', f'bossbar set {bid} max {top}',
                                      f'bossbar set {bid} color {color}']
                if world == 'colorescape':
                    # Sus acertijos piden poner y romper bloques (aventura: solo los que el mapa permite).
                    lines += [f'rg flag -w {world} __global__ build allow',
                              f'rg flag -w {world} __global__ block-place allow',
                              f'rg flag -w {world} __global__ block-break allow']
                if world in DATAPACK_MAPS or world in EXTRA_WORLDS:
                    # Su datapack crea caballos, viboras y marcadores.
                    lines += [f'rg flag -w {world} __global__ mob-spawning allow']
    lines += ['# Reiniciar una vez para cargar todo junto y evitar acumular Metaspace con recargas.',
              '# Si solo se actualizan configs con los mundos ya instalados:']
    lines += ['dm reload', 'mm reload', 'skript:skript reload astral_gameplay', 'skript:skript reload astral_minijuegos',
              '# Revisar consola: sin errores Skript/MythicMobs/DeluxeMenus. Si hay errores, mantener acceso cerrado.',
              '# NPC: ejecutar SOLO luego de cargar los menus/scripts y revisar las llegadas.',
              'rg flag -w lobby __global__ mob-spawning allow']
    for kind, position in NPC_POSITIONS.items():
        lines += [f'mm mobs kill astral_npc_{kind}',
                  f'mm mobs spawn astral_npc_{kind} 1 lobby,' + ','.join(map(str,position))]
    lines += ['rg flag -w lobby __global__ mob-spawning deny',
              '# TFT: llegadas verificadas por defecto, rescate bajo Y=120. No requieren fijar punto OP.',
              '# Opcional: /astralpunto arena tft1 (o tft2/tft3) sobrescribe la llegada. /astralpunto lista muestra puntos guardados.',
              '# Verificacion: estrella slot 9, salida lobby, modo restaurado, gancho bloqueado, rescate y PvP con dos jugadores.']
    return '\n'.join(lines) + '\n'


def generate():
    from menu_ui import decorate
    from gameplay import script as gameplay_script
    from mobs.mythic import npc_block
    outputs = {'minijuegos/astral_minijuegos.sk': script(),
               'minijuegos/despliegue.txt': deployment(),
               'gameplay/astral_gameplay.sk': gameplay_script(),
               'mythicmobs/mobs/minijuegos.yml': npc('parkour'),
               'mythicmobs/mobs/arena.yml': '# Generado por mobs/arena.py\n' + npc_block(
                   'astral_npc_arena', '&c&lArena de jugadores &7- PvP', 'ARMORER',
                   ['command{c="dm open arenas <trigger.name>"} @self ~onInteract'])}
    for kind, filename in [('parkour', 'parkour'), ('arena', 'arenas')] + [(g, g) for g in DROPPERS]:
        outputs[f'menus/DeluxeMenus/gui_menus/{filename}.yml'] = json.dumps(decorate(menu_data(kind)), ensure_ascii=False, indent=2) + '\n'
    for filename, content in outputs.items():
        path = ROOT / 'build' / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    generate()
