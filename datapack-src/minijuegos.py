"""Parkour y arenas: agregar una entrada y ejecutar python menus.py.

Los mapas de terceros se preparan aparte con minijuegos_mapas.py, siempre en .local.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARKOURS = [dict(id='spiral', world='parkour_spiral', name='Spiral Parkour Challenge',
                 icon='FEATHER', description='Una espiral de saltos hasta la cima.',
                 difficulty='Progresiva', arrival=(0.5, -11, -1.5, 0, 0), rescue_y=-20)]
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
NPC_POSITIONS = {'parkour': (121.5, 100, 193.529), 'arena': (127.5, 100, 193.529)}


def parkour_worlds():
    return tuple(dict.fromkeys(d['world'] for d in PARKOURS))


def arena_worlds():
    return tuple(dict.fromkeys(d['world'] for d in ARENAS))


def definitions():
    return [('parkour', d) for d in PARKOURS] + [('arena', d) for d in ARENAS]


def menu_data(kind):
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
        return dict(menu_title=title('arenas'),size=54,items=items)
    maps = PARKOURS if kind == 'parkour' else ARENAS
    command = 'parkour' if kind == 'parkour' else 'arenas'
    slots = [10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25]
    if len(maps) > len(slots):
        raise ValueError('Ampliar el selector antes de agregar mas de 14 mapas')
    items = {}
    for slot, d in zip(slots, maps):
        lore = ['&7' + d['description']]
        if kind == 'parkour':
            lore += ['&7Dificultad: &f' + d['difficulty'], '&7Sin gancho ni dano de caida.']
        else:
            lore += ['&7Se pelea con tu equipo;', '&7no perdes nada al morir.']
        if d.get('needs_point'):
            lore += ['&eRequiere una llegada revisada por un OP.']
        items[d['id']] = dict(material=d['icon'], slot=slot, display_name='&a&l' + d['name'],
                              lore=lore, click_commands=['[close]', f'[player] {command} {d["id"]}<delay=3>'])
    for slot in slots[len(maps):]:
        items[f'proximo_{slot}'] = dict(material='GRAY_DYE', slot=slot, display_name='&7Proximamente')
    items['lobby'] = dict(material='RED_BED', slot=30, display_name='&fVolver al lobby',
                          click_commands=['[close]', '[player] spawn<delay=3>'])
    items['cerrar'] = dict(material='BARRIER', slot=32, display_name='&cCerrar', click_commands=['[close]'])
    return dict(menu_title='&8Mapas de Parkour' if kind == 'parkour' else '&8Arenas PvP', size=36, items=items)


def script():
    lines = ['# Generado por minijuegos.py. Mundos y destinos limitados a la lista Python.',
             '# Persistentes: puntos OP, mapa elegido y modo anterior (reconexiones/reinicios).']
    for kind, worlds in [('parkour', parkour_worlds()), ('arena', arena_worlds())]:
        names = ' or '.join(f'"{w}"' for w in worlds)
        lines += [f'function astral_{kind}_world(w: world) :: boolean:',
                  f'    if name of {{_w}} is {names}:', '        return true', '    return false', '']
    lines += ['function astral_parkour_mode(p: player):',
              '    set {_u} to uuid of {_p}',
              '    if astral_parkour_world(world of {_p}) is true:',
              '        if {_p} is op:',
              '            if gamemode of {_p} is creative:', '                stop',
              '        if {astral.minijuegos.mode::%{_u}%} is not set:',
              '            set {astral.minijuegos.mode::%{_u}%} to gamemode of {_p}',
              '        set gamemode of {_p} to adventure',
              '        set food level of {_p} to 10',
              '        set saturation of {_p} to 10',
              '    else:',
              '        if {astral.minijuegos.mode::%{_u}%} is set:',
              '            if {_p} is not op:',
              '                set gamemode of {_p} to {astral.minijuegos.mode::%{_u}%}',
              '            else if gamemode of {_p} is not creative:',
              '                set gamemode of {_p} to {astral.minijuegos.mode::%{_u}%}',
              '            delete {astral.minijuegos.mode::%{_u}%}', '',
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
        if kind == 'parkour':
            lines += ['        if {astral.minijuegos.mode::%uuid of {_p}%} is not set:',
                      '            set {astral.minijuegos.mode::%uuid of {_p}%} to gamemode of {_p}']
        lines += [f'        set {{astral.minijuegos.selected::%uuid of {{_p}}%}} to "{key}"',
                  '        set {_x} to x-coordinate of {_l}', '        set {_y} to y-coordinate of {_l}',
                  '        set {_z} to z-coordinate of {_l}', '        set {_yaw} to yaw of {_l}',
                  '        set {_pitch} to pitch of {_l}', '        set {_name} to name of {_p}',
                  '        set velocity of {_p} to vector(0, 0, 0)', '        set fall distance of {_p} to 0',
                  f'        execute console command "execute in minecraft:{d["world"]} run minecraft:tp %{{_name}}% %{{_x}}% %{{_y}}% %{{_z}}% %{{_yaw}}% %{{_pitch}}%"',
                  '        astral_parkour_mode({_p})', '        stop']
    for command, kind in [('parkour', 'parkour'), ('arenas', 'arena')]:
        lines += ['', f'command /{command} [<text>]:', '    executable by: players', '    trigger:',
                  '        if arg-1 is not set:', f'            execute console command "dm open {command} %name of player%"', '            stop']
        for k, d in definitions():
            if k == kind:
                lines += [f'        if arg-1 is "{d["id"]}":',
                          f'            astral_minijuego_ir(player, "{kind}.{d["id"]}")', '            stop']
        lines += [f'        send "&eUsa /{command} para elegir un destino." to player']
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
              'on respawn:', '    wait 2 ticks']
    for world in arena_worlds():
        maps = [d for d in ARENAS if d['world'] == world]
        keys = ' or '.join(f'"arena.{d["id"]}"' for d in maps)
        lines += [f'    if name of world of player is "{world}":',
                  '        set {_id} to {astral.minijuegos.selected::%uuid of player%}',
                  f'        if {{_id}} is not {keys}:', f'            set {{_id}} to "arena.{maps[0]["id"]}"',
                  '        astral_minijuego_ir(player, {_id})']
    lines += ['', 'on damage of player:', '    if astral_parkour_world(world of victim) is true:',
              '        cancel event', '',
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
            lines += [f'            if {{_id}} is "{kind}.{d["id"]}":',
                      f'                if y-coordinate of loop-player is less than {d["rescue_y"]}:',
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
    name = '&a&lParkour' if kind == 'parkour' else '&c&lArena PvP'
    menu = 'parkour' if kind == 'parkour' else 'arenas'
    return portal_npc().replace('portales.py', 'minijuegos.py').replace('astral_npc_portales', 'astral_npc_' + kind).replace('&b&lGuardian de los Portales', name).replace('dm open portales', 'dm open ' + menu)


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
            lines += [f'mv gamerule set minecraft:fall_damage false {world}',
                      f'lp group default permission set mv.bypass.gamemode.{world} true',
                      f'rg flag -w {world} __global__ fall-damage deny']
    lines += ['# Reiniciar una vez para cargar todo junto y evitar acumular Metaspace con recargas.',
              '# Si solo se actualizan configs con los mundos ya instalados:']
    lines += ['dm reload', 'mm reload', 'skript:skript reload astral_gameplay', 'skript:skript reload astral_minijuegos',
              '# Revisar consola: sin errores Skript/MythicMobs/DeluxeMenus. Si hay errores, mantener acceso cerrado.',
              '# NPC: ejecutar SOLO luego de cargar los menus/scripts y revisar las llegadas.',
              'rg flag -w lobby __global__ mob-spawning allow']
    for kind, position in NPC_POSITIONS.items():
        lines += [f'mm mobs kill astral_npc_{kind}',
                  f'mm mobs spawn astral_npc_{kind} 1 lobby,{position[0]},{position[1]},{position[2]}']
    lines += ['rg flag -w lobby __global__ mob-spawning deny',
              '# TFT: llegadas verificadas por defecto, rescate bajo Y=120. No requieren fijar punto OP.',
              '# Opcional: /astralpunto arena tft1 (o tft2/tft3) sobrescribe la llegada. /astralpunto lista muestra puntos guardados.',
              '# Verificacion: estrella slot 9, salida lobby, modo restaurado, gancho bloqueado, rescate y PvP con dos jugadores.']
    return '\n'.join(lines) + '\n'


def generate():
    from gameplay import script as gameplay_script
    from mobs.mythic import npc_block
    outputs = {'minijuegos/astral_minijuegos.sk': script(),
               'minijuegos/despliegue.txt': deployment(),
               'gameplay/astral_gameplay.sk': gameplay_script(),
               'mythicmobs/mobs/minijuegos.yml': npc('parkour'),
               'mythicmobs/mobs/arena.yml': '# Generado por mobs/arena.py\n' + npc_block(
                   'astral_npc_arena', '&c&lArena de jugadores &7- PvP', 'ARMORER',
                   ['command{c="dm open arenas <trigger.name>"} @self ~onInteract'])}
    for kind, filename in [('parkour', 'parkour'), ('arena', 'arenas')]:
        outputs[f'menus/DeluxeMenus/gui_menus/{filename}.yml'] = json.dumps(menu_data(kind), ensure_ascii=False, indent=2) + '\n'
    for filename, content in outputs.items():
        path = ROOT / 'build' / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    generate()
