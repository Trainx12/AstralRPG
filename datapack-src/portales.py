"""Aldeano del lobby y menu de acceso al cruce de portales."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# End: portal_END.schem pegado con //paste -a parado en 146 82 78 (portal en 145 96 0),
# sin el terreno natural. Llegada elegida por el dueno frente a la torre.
# Nether: GuardianNPv3-92.schem ("guardianes"), separado en X -2248..-2138.
# Nether (15/11/2026): llegada nueva elegida por el dueno, frente al portal grande al Nether Hub.
ARRIVALS = {'end': (146.5, 84, 68.5, 180, 0),
            'nether': (-2137.59, 81, 159.48, 89.6, -2.1)}
END_PASTE = (146, 82, 78)
RESCUE_Y = 50  # la isla del End empieza en Y=64 y la base del Nether en Y=79
NPC_POSITION = (211.434, 105, 237.492, 90.0, 0)
# Copias del aldeano 2 bloques al este de cada llegada (mismo mob astral_npc_portales).
NPC_ARRIVALS = {'end': (148.5, 84, 68.5), 'nether': (-2137.59, 81, 161.5)}   # nether: 2 bloques al costado de la llegada

# Plugin AstralPortales (runtime/AstralPortales.java): Nether Hub <-> portal grande de portales_astrales.
# Hub: zona que marco el dueno con WorldEdit (-239,110,-11 a -315,169,54); portal del Hub en ~(-282,124,23).
PORTALES = {
    'hub': {'mundo': 'minecraft:the_nether', 'desde': [-315, 110, -11], 'hasta': [-239, 169, 54],
            'llegada': [-285.0, 124.0, 23.5, 90.0, 0.0]},
    'astral': {'mundo': 'minecraft:portales_astrales', 'desde': [-2250, 60, 100], 'hasta': [-2125, 220, 220],
               'llegada': list(ARRIVALS['nether'])},
}
PORTALES_YML = '''name: AstralPortales
version: 1.0.0
main: astral.AstralPortales
api-version: '26.1.2'
commands:
  astralportal:
    description: Guarda la llegada del Nether Hub o de portales_astrales donde estas parado
    usage: /astralportal hub|astral
    permission: astral.admin.portales
permissions:
  astral.admin.portales:
    default: op
  astral.admin.build:
    default: op
'''


def build_plugin(jdk, server):
    import os, subprocess, zipfile, yaml
    target = ROOT / '.local/portales-classes'
    target.mkdir(parents=True, exist_ok=True)
    jars = list((server / 'libraries').rglob('*.jar'))
    javac = [str(jdk / ('java.exe' if os.name == 'nt' else 'java')), '-m', 'jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*javac, '-encoding', 'UTF-8', '-source', '25', '-target', '25', '-classpath', os.pathsep.join(map(str, jars)),
                    '-d', str(target), str(ROOT / 'datapack-src/runtime/AstralPortales.java')], check=True)
    dest = ROOT / 'build/runtime/AstralPortales.jar'
    stamp = (2026, 11, 15, 0, 0, 0)
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((target / 'astral').glob('AstralPortales*.class')):
            z.writestr(zipfile.ZipInfo(p.relative_to(target).as_posix(), stamp), p.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml', stamp), PORTALES_YML)
        z.writestr(zipfile.ZipInfo('config.yml', stamp), yaml.safe_dump(PORTALES, sort_keys=False))
    return dest


def menu_data():
    from menu_ui import decorate
    from travel_ui import title, CARD_SLOTS
    items = {}
    for key, material, slot, name, lore, commands in (
        ('nether', 'OBSIDIAN', 10, '&c&lNether', ['&7Obsidiana, brasas y guardianes.', '&7Viajá a la plataforma del umbral.'], ['[close]', '[player] umbrales nether<delay=3>']),
        ('end', 'END_PORTAL_FRAME', 12, '&e&lEnd', ['&7Una isla al otro lado del vacío.', '&7Viajá a la plataforma del umbral.'], ['[close]', '[player] umbrales end<delay=3>']),
        ('parkour', 'FEATHER', 14, '&d&lMini juegos', ['&7Parkour, droppers y Color Escape.'], ['[openguimenu] parkour']),
        ('arenas', 'IRON_SWORD', 16, '&b&lArenas PvP', ['&7Elegí una arena para combatir.'], ['[openguimenu] arenas']),
        ('lobby', 'ENDER_PEARL', 22, '&aVolver al lobby', ['&7Volvé al punto de aparición.'], ['[close]', '[player] umbrales lobby<delay=3>']),
        ('cerrar', 'BARRIER', 26, '&cCerrar', ['&7Seguí explorando por tu cuenta.'], ['[close]']),
    ):
        items[key] = {'material': material, 'slot': slot, 'display_name': name,
                      'item_model': f'astral:viajes/{key}', 'lore': lore + ['', '&eClic para elegir.'],
                      'click_commands': commands}
    # Cada tarjeta comparte tooltip y accion en sus seis casillas.
    for key,item in list(items.items()):
        slots=CARD_SLOTS.get(key,[45,46,47] if key=='lobby' else [51,52,53])
        item['item_model']='astral:viajes/blank'
        item['slot']=slots[0]
        for slot in slots[1:]:items[f'{key}_{slot}']=dict(item,slot=slot)
    # Lobby: la primera casilla muestra la barrera vanilla.
    items['lobby']['material']='BARRIER';del items['lobby']['item_model']
    # Oceano Astral (oceano.py): casilla 49, abre la ventana de aviso.
    from oceano import portales_button
    items['oceano']=portales_button()
    return decorate({'menu_title': title('portales'), 'size': 54, 'items': items})



def script():
    lines = ['# Generado por portales.py. Destinos fijos, sin comandos del usuario.',
             'command /umbrales [<text>]:', '    executable by: players',
             '    description: Elige un Portal Astral.', '    trigger:',
             '        if arg-1 is not set:',
             '            execute console command "dm open portales %name of player%"',
             '            stop']
    for key, coordinates in ARRIVALS.items():
        coords = ' '.join(map(str, coordinates))
        lines.extend([f'        if arg-1 is "{key}":',
                      f'            execute console command "execute in minecraft:portales_astrales run minecraft:tp %name of player% {coords}"',
                      '            stop'])
    lines.extend(['        if arg-1 is "lobby":',
                  '            execute console command "spawn %name of player%"',
                  '            stop'])
    lines.append('        send "&eUsa /umbrales para elegir un portal." to player')
    # Caerse de la isla del End o de la base del Nether: directo al lobby (/spawn).
    lines.extend(['', f'# Rescate: debajo de Y={RESCUE_Y} en portales_astrales vuelve al lobby.',
                  'every 10 ticks:',
                  '    loop all players in world "portales_astrales":',
                  '        if gamemode of loop-player is survival or adventure:',
                  f'            if y-coordinate of loop-player is less than {RESCUE_Y}:',
                  '                set velocity of loop-player to vector(0, 0, 0)',
                  '                set fall distance of loop-player to 0',
                  '                execute console command "spawn %name of loop-player%"',
                  '                send action bar "&eTe caiste del portal: volviste al lobby." to loop-player'])
    return '\n'.join(lines) + '\n'


def npc(modelo=True):
    from mobs.tanda3c import npc_skills
    extra = ''.join(f'  - {s}\n' for s in npc_skills('astral_npc_portales')) if modelo else ''
    return '''# Generado por portales.py. Ubicacion en el lobby elegida por el dueno.
astral_npc_portales:
  Type: VILLAGER
  Display: '&b&lGuardian de los Portales'
  Health: 20
  Options:
    NoAI: true
    Silent: true
    Invincible: true
    Despawn: false
    Persistent: true
    Collidable: false
    PreventOtherDrops: true
    PreventRandomEquipment: true
    PreventSunburn: true
    Profession: CLERIC
    VillagerType: PLAINS
    AlwaysShowName: true
  Skills:
  - cancelevent @self ~onInteract
  - 'command{c="dm open portales <trigger.name>"} @self ~onInteract'
''' + extra


def generate():
    from menu_ui import decorate
    outputs = {
        'menus/DeluxeMenus/gui_menus/portales.yml': json.dumps(decorate(menu_data()), ensure_ascii=False, indent=2) + '\n',
        'mapas_exploracion/astral_portales.sk': script(),
        'mythicmobs/mobs/portales.yml': npc(),
    }
    for name, content in outputs.items():
        path = ROOT/'build'/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--jdk', type=Path, help='bin de JDK 25: compila tambien AstralPortales.jar')
    ap.add_argument('--server', type=Path, default=ROOT / '.local/testsrv')
    a = ap.parse_args()
    generate()
    if a.jdk:
        print(build_plugin(a.jdk.resolve(), a.server.resolve()))
