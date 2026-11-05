"""Aldeano del lobby y menu de acceso al cruce de portales."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# End: portal_END.schem pegado con //paste -a parado en 146 82 78 (portal en 145 96 0),
# sin el terreno natural. Llegada elegida por el dueno frente a la torre.
# Nether: GuardianNPv3-92.schem ("guardianes"), separado en X -2248..-2138.
ARRIVALS = {'end': (146.5, 84, 68.5, 180, 0),
            'nether': (-2192.5, 81, 90.5, 180, 0)}
END_PASTE = (146, 82, 78)
RESCUE_Y = 50  # la isla del End empieza en Y=64 y la base del Nether en Y=79
NPC_POSITION = (124.472, 100, 193.529)
# Copias del aldeano 2 bloques al este de cada llegada (mismo mob astral_npc_portales).
NPC_ARRIVALS = {'end': (148.5, 84, 68.5), 'nether': (-2190.5, 81, 90.5)}


def menu_data():
    from travel_ui import title
    items = {}
    for key, material, slot, name, lore, commands in (
        ('nether', 'OBSIDIAN', 10, '&c&lNether', ['&7Obsidiana, brasas y guardianes.', '&7Viajá a la plataforma del umbral.'], ['[close]', '[player] umbrales nether<delay=3>']),
        ('end', 'END_PORTAL_FRAME', 12, '&e&lEnd', ['&7Una isla al otro lado del vacío.', '&7Viajá a la plataforma del umbral.'], ['[close]', '[player] umbrales end<delay=3>']),
        ('parkour', 'FEATHER', 14, '&d&lParkour', ['&7Elegí tu circuito y probá tus saltos.'], ['[openguimenu] parkour']),
        ('arenas', 'IRON_SWORD', 16, '&b&lArenas PvP', ['&7Elegí una arena para combatir.'], ['[openguimenu] arenas']),
        ('lobby', 'ENDER_PEARL', 22, '&aVolver al lobby', ['&7Volvé al punto de aparición.'], ['[close]', '[player] umbrales lobby<delay=3>']),
        ('cerrar', 'BARRIER', 26, '&cCerrar', ['&7Seguí explorando por tu cuenta.'], ['[close]']),
    ):
        items[key] = {'material': material, 'slot': slot, 'display_name': name,
                      'item_model': f'astral:viajes/{key}', 'lore': lore + ['', '&eClic para elegir.'],
                      'click_commands': commands}
    return {'menu_title': title('portales'), 'size': 27, 'items': items}



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


def npc():
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
'''


def generate():
    outputs = {
        'menus/DeluxeMenus/gui_menus/portales.yml': json.dumps(menu_data(), ensure_ascii=False, indent=2) + '\n',
        'mapas_exploracion/astral_portales.sk': script(),
        'mythicmobs/mobs/portales.yml': npc(),
    }
    for name, content in outputs.items():
        path = ROOT/'build'/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    generate()
