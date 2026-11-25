"""Evento de jefe ancestral cada X horas en el Survival (25/11/2026, pedido del dueno).

Las apariciones naturales de los ancestrales (mobs/mythic.py) son tan raras que nunca salio ninguno.
Ahora, cada HORAS horas el server elige a un jugador al aire libre en el Survival (`world`) y le hace
aparecer un jefe ancestral al azar a DISTANCIA bloques, con el aviso general de siempre (10 minutos).
Si el jugador elegido se va mas alla de LEJOS bloques, cambia de mundo o se desconecta, el jefe se va sin
premios (etiqueta astral.ancestral.fuera -> AST_ANCESTRAL_FUERA_* en mythic.py).

Regla del dueno: arranca solo para ByTrainx. `/ancestral publico` lo abre a todos, `/ancestral privado`
lo cierra, `/ancestral ya` lo fuerza al lado tuyo (para probar), `/ancestral cada <horas>` cambia el ritmo.

    python ancestral_evento.py   ->  build/gameplay/astral_ancestral.sk  (plugins/Skript/scripts/)
"""
from pathlib import Path

from mobs.mythic import ANCESTRALES

ROOT = Path(__file__).resolve().parent
HORAS = 3            # cada cuanto sale uno (se cambia en vivo con /ancestral cada <horas>)
DISTANCIA = 28       # bloques del jugador donde aparece
LEJOS = 100          # si el elegido se va mas lejos que esto, el jefe se va
REINTENTO = 5        # minutos hasta volver a probar si no habia nadie al aire libre
PRUEBA = 'ByTrainx'
MUNDO = 'world'


def script():
    nombres = [f'"{m}_ancestral"' for m in ANCESTRALES]
    mobs = ', '.join(nombres[:-1]) + ' and ' + nombres[-1]
    return f'''# Generado por datapack-src/ancestral_evento.py: no editar a mano.
# Jefe ancestral cada X horas al lado de un jugador del Survival; se va si el elegido se aleja.

options:
    mundo: {MUNDO}
    lejos: {LEJOS}

function astral_anc_puede(p: player) :: boolean:
    if name of {{_p}} is "{PRUEBA}":
        return true
    if {{astral.ancestral.publico}} is true:
        return true
    return false

# Al aire libre (o bajo arboles/techo cerca): nada solido mas de 12 bloques por encima.
function astral_anc_afuera(p: player) :: boolean:
    set {{_h}} to highest solid block at location of {{_p}}
    if y-coordinate of {{_h}} - y-coordinate of {{_p}} > 12:
        return false
    return true

# Lugar al aire libre a {DISTANCIA} bloques del jugador (sin agua ni lava, a una altura parecida).
function astral_anc_sitio(p: player) :: location:
    set {{_c}} to location of {{_p}}
    loop 12 times:
        set {{_a}} to random number between 0 and 360
        set {{_t}} to {{_c}} offset by vector(cos({{_a}}) * {DISTANCIA}, 0, sin({{_a}}) * {DISTANCIA})
        set {{_b}} to highest solid block at {{_t}}
        set {{_arriba}} to block above {{_b}}
        set {{_tipo}} to "%type of {{_arriba}}% %type of {{_b}}%"
        if {{_tipo}} does not contain "water":
            if {{_tipo}} does not contain "lava":
                if {{_tipo}} does not contain "agua":
                    set {{_dy}} to y-coordinate of {{_b}} - y-coordinate of {{_c}}
                    if {{_dy}} < 15:
                        if {{_dy}} > -15:
                            return location of {{_arriba}}

# Jugador elegido al azar entre los que estan al aire libre en el Survival.
function astral_anc_elegido() :: player:
    loop all players:
        name of world of loop-player is "{{@mundo}}"
        gamemode of loop-player is survival
        astral_anc_puede(loop-player) is true
        astral_anc_afuera(loop-player) is true
        add loop-player to {{_c::*}}
    size of {{_c::*}} > 0
    return random element out of {{_c::*}}

function astral_anc_lanzar(p: player, s: location):
    set {{_mobs::*}} to {mobs}
    set {{_mob}} to random element out of {{_mobs::*}}
    set {{_w}} to name of world of {{_s}}
    set {{-astral.anc.lanzando}} to true
    execute console command "mm mobs spawn %{{_mob}}% 1 %{{_w}}%,%x-coordinate of {{_s}} + 0.5%,%y-coordinate of {{_s}}%,%z-coordinate of {{_s}} + 0.5%"
    wait 3 ticks
    delete {{-astral.anc.lanzando}}
    loop entities in radius 6 of {{_s}}:
        loop-entity is not a player
        "%name of loop-entity%" contains "Ancestral"
        add "astral.ancestral.ev" to scoreboard tags of loop-entity
        set {{-astral.anc.ent}} to loop-entity
        set {{-astral.anc.jug}} to {{_p}}
        send title "&6&lJefe Ancestral" with subtitle "&eAlgo despertó cerca tuyo..." to {{_p}} for 3 seconds
        send "&6&l(!) &eUn jefe ancestral apareció cerca tuyo. Si te alejás más de {LEJOS} bloques o cambiás de mundo, se va." to {{_p}}
        stop

every 1 minute:
    {{-astral.anc.ent}} is not set
    {{-astral.anc.lanzando}} is not set
    set {{_cada}} to {{astral.ancestral.cada}} ? {HORAS} hours
    if {{astral.ancestral.ultimo}} is set:
        difference between {{astral.ancestral.ultimo}} and now is less than {{_cada}}
        stop
    if {{-astral.anc.reintento}} is set:
        difference between {{-astral.anc.reintento}} and now is less than {REINTENTO} minutes
        stop
    set {{-astral.anc.reintento}} to now
    set {{_p}} to astral_anc_elegido()
    {{_p}} is set
    set {{_s}} to astral_anc_sitio({{_p}})
    {{_s}} is set
    set {{astral.ancestral.ultimo}} to now
    astral_anc_lanzar({{_p}}, {{_s}})

# El elegido se aleja, cambia de mundo o se va: el jefe se va sin premios.
every 2 seconds:
    {{-astral.anc.ent}} is set
    set {{_e}} to {{-astral.anc.ent}}
    set {{_p}} to {{-astral.anc.jug}}
    if {{_e}} is dead:
        delete {{-astral.anc.ent}}
        delete {{-astral.anc.jug}}
        stop
    set {{_fuera}} to false
    if {{_p}} is not online:
        set {{_fuera}} to true
    else if world of {{_p}} is not world of {{_e}}:
        set {{_fuera}} to true
    else if distance between {{_p}} and {{_e}} > {{@lejos}}:
        set {{_fuera}} to true
    {{_fuera}} is true
    add "astral.ancestral.fuera" to scoreboard tags of {{_e}}
    if {{_p}} is online:
        send "&7El jefe ancestral se desvaneció porque te alejaste." to {{_p}}
    delete {{-astral.anc.ent}}
    delete {{-astral.anc.jug}}

command /ancestral [<text>] [<number>]:
    permission: op
    trigger:
        if arg-1 is "publico":
            set {{astral.ancestral.publico}} to true
            send "&aEvento ancestral: abierto para todos." to sender
        else if arg-1 is "privado":
            delete {{astral.ancestral.publico}}
            send "&eEvento ancestral: solo {PRUEBA}." to sender
        else if arg-1 is "cada":
            arg-2 is set
            arg-2 > 0
            set {{astral.ancestral.cada}} to "%arg-2% hours" parsed as timespan
            send "&aEvento ancestral: cada %arg-2% horas." to sender
        else if arg-1 is "ya":
            sender is a player
            if {{-astral.anc.ent}} is set:
                send "&cYa hay un jefe ancestral del evento vivo." to sender
                stop
            set {{_s}} to astral_anc_sitio(player)
            if {{_s}} is not set:
                send "&cNo encontré lugar al aire libre cerca tuyo." to sender
                stop
            astral_anc_lanzar(player, {{_s}})
            send "&aJefe ancestral lanzado (no cambia el reloj del evento)." to sender
        else:
            set {{_h}} to {{astral.ancestral.cada}} ? {HORAS} hours
            if {{astral.ancestral.publico}} is true:
                send "&7Evento ancestral: &apublico&7, cada %{{_h}}%." to sender
            else:
                send "&7Evento ancestral: &esolo {PRUEBA}&7, cada %{{_h}}%." to sender
            if {{astral.ancestral.ultimo}} is set:
                send "&7Ultimo: hace %difference between {{astral.ancestral.ultimo}} and now%." to sender
            send "&7/ancestral publico | privado | cada <horas> | ya" to sender
'''


def main():
    out = ROOT.parent / 'build/gameplay/astral_ancestral.sk'
    out.write_text(script(), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
