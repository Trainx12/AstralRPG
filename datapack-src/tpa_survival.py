"""/tpa solo dentro del Survival (24/11/2026, pedido del dueno).

Essentials da /tpa, /tpahere, /tpaccept, /tpdeny y /tpacancel a todos (permisos en el grupo default), pero
este script los corta si alguno de los dos jugadores no esta en el Survival (world, world_nether, world_the_end).
El Nether Hub (AstralPortales, dentro de world_nether) NO cuenta como Survival. Asi nadie se tepea al lobby,
a las minas, mazmorras, arenas ni otros mundos, ni sale de ahi hacia el Survival por /tpa.

Dos capas:
  1. Al escribir el comando: quien pide y el destinatario tienen que estar en el Survival.
  2. Al aceptar: el teletransporte que sale de /tpaccept se cancela si sale o llega fuera del Survival
     (por si alguien cambio de mundo entre el pedido y la aceptacion). Essentials tiene teleport-delay 0,
     asi que el viaje ocurre en el mismo momento del /tpaccept.

    python tpa_survival.py   ->  build/gameplay/astral_tpa.sk  (plugins/Skript/scripts/)
"""
from pathlib import Path

from llegada_survival import HUB_MAX, HUB_MIN, MUNDOS

ROOT = Path(__file__).resolve().parent

PEDIR = ('tpa', 'call', 'tpask', 'etpa', 'ecall', 'etpask', 'tpahere', 'etpahere')
ACEPTAR = ('tpaccept', 'tpyes', 'etpaccept', 'etpyes')
PERMISOS = ('essentials.tpa', 'essentials.tpahere', 'essentials.tpaccept', 'essentials.tpdeny',
            'essentials.tpacancel')
MSG = '&cEl /tpa solo funciona dentro del Survival.'


def _lista(cmds):
    todos = list(cmds) + [f'essentials:{c}' for c in cmds]
    return ', '.join(f'"{c}"' for c in todos[:-1]) + f' and "{todos[-1]}"'


def script():
    mundos = ' or '.join(f'"{m}"' for m in MUNDOS)
    return f'''# Generado por datapack-src/tpa_survival.py: no editar a mano.
# /tpa solo dentro del Survival (no al lobby, minas, mazmorras ni otros mundos). Nether Hub excluido.

function astral_tpa_ok(l: location) :: boolean:
    if name of world of {{_l}} is {mundos}:
        set {{_s}} to true
    if {{_s}} is not set:
        return false
    if name of world of {{_l}} is "world_nether":
        if x-coordinate of {{_l}} is between {HUB_MIN[0]} and {HUB_MAX[0]}:
            if y-coordinate of {{_l}} is between {HUB_MIN[1]} and {HUB_MAX[1]}:
                if z-coordinate of {{_l}} is between {HUB_MIN[2]} and {HUB_MAX[2]}:
                    return false
    return true

on command:
    sender is a player
    set {{_c}} to command
    set {{_pide}} to false
    loop {_lista(PEDIR)}:
        if {{_c}} is loop-value:
            set {{_pide}} to true
    set {{_acepta}} to false
    loop {_lista(ACEPTAR)}:
        if {{_c}} is loop-value:
            set {{_acepta}} to true
    if {{_pide}} is true:
        if astral_tpa_ok(location of player) is false:
            cancel event
            send "{MSG}" to player
            stop
        set {{_n::*}} to full command split at " "
        {{_n::2}} is set
        set {{_t}} to {{_n::2}} parsed as player
        {{_t}} is online
        if astral_tpa_ok(location of {{_t}}) is false:
            cancel event
            send "{MSG} &7(%{{_n::2}}% no esta en el Survival)" to player
    else if {{_acepta}} is true:
        if astral_tpa_ok(location of player) is false:
            cancel event
            send "{MSG}" to player
            stop
        set {{-astral.tpa.acepta::%uuid of player%}} to now

on teleport:
    set {{_ok}} to true
    if {{-astral.tpa.acepta::%uuid of player%}} is set:
        # tpahere: quien acepta viaja hacia quien pidio.
        if difference between {{-astral.tpa.acepta::%uuid of player%}} and now is less than 2 seconds:
            set {{_tpa}} to true
    if {{_tpa}} is not set:
        # tpa: quien pidio viaja hacia quien acepta.
        loop all players:
            {{-astral.tpa.acepta::%uuid of loop-player%}} is set
            difference between {{-astral.tpa.acepta::%uuid of loop-player%}} and now is less than 2 seconds
            loop-player is not player
            world of loop-player is world of event-location
            distance between loop-player and event-location is less than 2
            set {{_tpa}} to true
            stop loop
    {{_tpa}} is set
    if astral_tpa_ok(location of player) is false:
        set {{_ok}} to false
    if astral_tpa_ok(event-location) is false:
        set {{_ok}} to false
    {{_ok}} is false
    cancel event
    send "{MSG}" to player

on quit:
    delete {{-astral.tpa.acepta::%uuid of player%}}
'''


def comandos():
    return '\n'.join(['# Consola del panel, sin /. Dar el /tpa a todos (el script lo limita al Survival):']
                     + [f'lp group default permission set {p} true' for p in PERMISOS]) + '\n'


if __name__ == '__main__':
    out = ROOT.parent / 'build/gameplay/astral_tpa.sk'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(script(), encoding='utf-8', newline='\n')
    (ROOT.parent / 'build/gameplay/tpa_comandos.txt').write_text(comandos(), encoding='utf-8', newline='\n')
    print(out)
