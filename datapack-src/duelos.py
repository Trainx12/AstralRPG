"""Duelos (Duels Optimised 8.3) dentro de Arenas PvP.

Desde /arenas -> "Desafiar a un jugador" (o /desafiar): ventana con las cabezas de los jugadores
conectados; al elegir uno se ejecuta `/duel <jugador>` y Duels abre su ventana de pedido, donde el
retador ELIGE LA ARENA. El desafiado acepta con `/duel accept <retador>`. Sin apuestas ni perdida de
inventario (config de plugin-presets/Duels--config.yml).

python duelos.py  ->  build/duelos/astral_duelos.sk y Duels/arenas.json (preset + build).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/duelos'

# Dos puntos enfrentados por arena (mundo Bukkit, x, y, z, yaw). "Astral" conserva su nombre
# para no perder estadisticas. TFT: piso comprobado en Paper local (ArenaScan, 12/11/2026),
# 12 bloques a cada lado de la llegada del menu /arenas.
DUEL_ARENAS = [
    ('Astral', 'arena', (-216.5, 73, -2381.5, -45), (-196.5, 73, -2361.5, 135)),
    ('TFT1', 'arenas_tft', (-274.5, 143, -550.5, 90), (-298.5, 143, -550.5, -90)),
    ('TFT2', 'arenas_tft', (-274.5, 139, -282.5, 90), (-298.5, 139, -282.5, -90)),
    ('TFT3', 'arenas_tft', (-274.5, 139, -14.5, 90), (-298.5, 139, -14.5, -90)),
]
TITLE = '&8Desafiar a un jugador'
# Boton en la ventana ilustrada de /arenas (fila de abajo, entre Lobby 45-47 y Cerrar 51-53).
ARENAS_BUTTON_SLOT = 49


def arenas_json():
    def pos(world, p):
        x, y, z, yaw = p
        return {'world': world, 'x': x, 'y': y, 'z': z, 'pitch': 0, 'yaw': yaw}
    return [{'name': name, 'disabled': False, 'kits': [], 'positions': {'1': pos(world, a), '2': pos(world, b)}}
            for name, world, a, b in DUEL_ARENAS]


def arenas_button():
    return dict(material='DIAMOND_SWORD', slot=ARENAS_BUTTON_SLOT, item_model='astral:menu/icon_duelos',
                display_name='&c&lDesafiar a un jugador',
                lore=['&7Elegi a quien desafiar y despues la arena.', '&7Nadie pierde items en un duelo.',
                      '&7El otro acepta con &e/duel accept <tu nombre>&7.'],
                click_commands=['[close]', '[player] desafiar<delay=3>'])


def script():
    return f'''# Generado por duelos.py. Skript 2.17, sin addons. Ventana para elegir rival de Duels.
function astral_desafiar(p: player):
    close {{_p}}'s inventory
    set {{_id}} to uuid of {{_p}}
    delete {{-duelo.obj::%{{_id}}%::*}}
    set {{_inv}} to a new chest inventory with 6 rows named colored "{TITLE}"
    set {{_n}} to 0
    loop all players:
        loop-player is not {{_p}}
        {{_n}} < 45
        set slot {{_n}} of {{_inv}} to skull of loop-player named "&e%name of loop-player%"
        set lore of slot {{_n}} of {{_inv}} to "&7Clic: elegi la arena y envia el desafio." and "&7Nadie pierde items en un duelo."
        set {{-duelo.obj::%{{_id}}%::%{{_n}}%}} to name of loop-player
        add 1 to {{_n}}
    if {{_n}} is 0:
        set slot 22 of {{_inv}} to barrier named "&cNo hay otros jugadores conectados"
    set slot 49 of {{_inv}} to book named "&eComo funciona"
    set lore of slot 49 of {{_inv}} to "&71. Elegi a quien desafiar." and "&72. Elegi la arena y envia el pedido." and "&73. El otro acepta con /duel accept <tu nombre>."
    set slot 45 of {{_inv}} to arrow named "&fVolver a Arenas"
    set slot 53 of {{_inv}} to barrier named "&cCerrar"
    set {{-duelo.gui::%{{_id}}%}} to {{_inv}}
    open {{_inv}} to {{_p}}

command /desafiar:
    trigger:
        if sender is a player:
            astral_desafiar(player)

on inventory click:
    set {{_id}} to uuid of player
    set {{_inv}} to {{-duelo.gui::%{{_id}}%}}
    if {{_inv}} is not set:
        stop
    if player's current inventory is not {{_inv}}:
        delete {{-duelo.gui::%{{_id}}%}}
        stop
    cancel event
    if clicked inventory is not {{_inv}}:
        stop
    set {{_slot}} to index of event-slot
    if {{_slot}} is 53:
        close player's inventory
        stop
    if {{_slot}} is 45:
        close player's inventory
        execute console command "dm open arenas %name of player%"
        stop
    set {{_t}} to {{-duelo.obj::%{{_id}}%::%{{_slot}}%}}
    if {{_t}} is not set:
        stop
    close player's inventory
    if {{_t}} parsed as player is not set:
        send "&cEse jugador ya no esta conectado." to player
        stop
    make player execute command "duel %{{_t}}%"

on inventory close:
    delete {{-duelo.gui::%uuid of player%}}

on quit:
    delete {{-duelo.gui::%uuid of player%}}
    delete {{-duelo.obj::%uuid of player%::*}}
'''


def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'astral_duelos.sk').write_text(script(), encoding='utf8')
    data = json.dumps(arenas_json(), indent=2) + '\n'
    for path in (ROOT/'datapack-src/plugin-presets/Duels--arenas.json', ROOT/'build/plugins-basicos/Duels/arenas.json'):
        path.write_text(data, encoding='utf8')


if __name__ == '__main__':
    generate()
    print(OUT/'astral_duelos.sk')
