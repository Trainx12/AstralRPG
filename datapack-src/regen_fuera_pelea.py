"""Curacion fuera de pelea (24/11/2026, pedido del dueno).

La comida cura poco (gameplay.REGEN_COMIDA: 2% de la vida maxima por vez) y llenar la vida costaba casi 4 barras
de comida. Ahora, tras SEGUNDOS sin pegar ni recibir dano, se cura POR_SEGUNDO de la vida maxima cada segundo
sin gastar comida, y la curacion por comida no se come la comida mientras tanto. En pelea queda como antes.

Tambien (24/11): si te pegaron hace menos de SPAWN_ESPERA segundos no podes usar /spawn.

Regla del dueno: arranca solo para ByTrainx. `/regenfuera publico` lo abre a todos, `/regenfuera privado` lo cierra.

    python regen_fuera_pelea.py   ->  build/gameplay/astral_regen.sk  (plugins/Skript/scripts/)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEGUNDOS = 20        # sin pelear antes de empezar a curar
POR_SEGUNDO = 0.04   # fraccion de la vida maxima por segundo (lleno en ~25 s)
PRUEBA = 'ByTrainx'
SPAWN_ESPERA = 5     # segundos desde el ultimo golpe recibido para poder usar /spawn (24/11)
SPAWN_COMANDOS = ('spawn', 'essentials:spawn', 'espawn', 'essentials:espawn',
                  'home', 'essentials:home', 'ehome', 'essentials:ehome')   # /home tambien (24/11)


def script():
    comandos = ', '.join(f'"{c}"' for c in SPAWN_COMANDOS[:-1]) + f' and "{SPAWN_COMANDOS[-1]}"'
    return f'''# Generado por datapack-src/regen_fuera_pelea.py: no editar a mano.
# Curacion fuera de pelea: {SEGUNDOS} s sin dano -> {round(POR_SEGUNDO * 100)}% de la vida maxima por segundo, sin comida.

function astral_regen_puede(p: player) :: boolean:
    if name of {{_p}} is "{PRUEBA}":
        return true
    if {{astral.regen.publico}} is true:
        return true
    return false

function astral_en_pelea(p: player) :: boolean:
    set {{_t}} to {{-astral.pelea::%uuid of {{_p}}%}}
    if {{_t}} is not set:
        return false
    if difference between {{_t}} and now is less than {SEGUNDOS} seconds:
        return true
    return false

on damage:
    if victim is a player:
        set {{-astral.pelea::%uuid of victim%}} to now
        set {{-astral.golpe::%uuid of victim%}} to now
    if attacker is a player:
        set {{-astral.pelea::%uuid of attacker%}} to now

on join:
    set {{-astral.pelea::%uuid of player%}} to now

every 1 second:
    loop all players:
        gamemode of loop-player is survival or adventure
        health of loop-player > 0
        health of loop-player < max health of loop-player
        astral_regen_puede(loop-player) is true
        astral_en_pelea(loop-player) is false
        heal loop-player by (max health of loop-player) * {POR_SEGUNDO}

# Fuera de pelea la comida no cura ni se gasta: se cancela su curacion y se devuelve lo que la comida pierda.
on heal of player with priority lowest:
    "%heal reason%" contains "satiat"
    astral_regen_puede(player) is true
    astral_en_pelea(player) is false
    cancel event
    set {{_f}} to food level of player
    set {{_s}} to saturation of player
    wait 2 ticks
    player is online
    if food level of player < {{_f}}:
        set food level of player to {{_f}}
    if saturation of player < {{_s}}:
        set saturation of player to {{_s}}

# Sin /spawn en pelea: si te pegaron hace menos de {SPAWN_ESPERA} s se cancela y avisa en el chat.
on command:
    sender is a player
    set {{_c}} to command
    loop {comandos}:
        if {{_c}} is loop-value:
            set {{_t}} to {{-astral.golpe::%uuid of player%}}
            {{_t}} is set
            difference between {{_t}} and now is less than {SPAWN_ESPERA} seconds
            cancel event
            if {{_c}} contains "home":
                send "&cNo se puede ir a tu casa mientras estás en pelea. Esperá {SPAWN_ESPERA} segundos sin que te peguen." to player
            else:
                send "&cNo se puede llevar al spawn mientras estás en pelea. Esperá {SPAWN_ESPERA} segundos sin que te peguen." to player
            stop

command /regenfuera <text>:
    permission: op
    trigger:
        if arg-1 is "publico":
            set {{astral.regen.publico}} to true
            send "&aCuracion fuera de pelea: abierta para todos." to sender
        else if arg-1 is "privado":
            delete {{astral.regen.publico}}
            send "&eCuracion fuera de pelea: solo {PRUEBA}." to sender
        else:
            send "&7/regenfuera publico | privado" to sender
'''


def main():
    out = ROOT.parent / 'build/gameplay/astral_regen.sk'
    out.write_text(script(), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
