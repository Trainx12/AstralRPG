"""Llegada segura al Survival (23/11/2026, pedido del dueno).

Al entrar al Survival (cambio de mundo, reaparecer en la cama o conectarse estando ahi) el jugador
queda 3 segundos sin recibir dano: habia mobs esperando en la cama que te mataban al aparecer.
Se cancela todo dano salvo el vacio. Script aparte para no mezclar con astral_gameplay.sk.
Al volver al Survival lleva al ultimo lugar donde estaba (salvo que haya muerto).
Tambien repone la vida base (escala.VIDA_JUGADOR_BASE) al reaparecer y al entrar: morir la vuelve a 20.
25/11: guarda la vida al salir y la devuelve al entrar (antes se recortaba a la base sin la armadura).
Solo ByTrainx hasta `/vidasalida publico`.

    python llegada_survival.py   ->  build/gameplay/astral_llegada.sk  (plugins/Skript/scripts/)
"""
from pathlib import Path

from escala import VIDA_JUGADOR_BASE
from portales import PORTALES

ROOT = Path(__file__).resolve().parent
SEGUNDOS = 3
PRUEBA = 'ByTrainx'   # vida al salir: solo el dueno hasta `/vidasalida publico`
ESPERA_VIDA = 10      # ticks al entrar antes de devolver la vida (que ya cuente la armadura)
MUNDOS = ('world', 'world_nether', 'world_the_end')   # Survival, su Nether y su End
# El Nether Hub (AstralPortales) esta en world_nether pero NO es Survival: llegar ahi no lleva al
# ultimo lugar ni se guarda como ultimo lugar (24/11: el portal mandaba a la casa en vez del Hub).
_HUB = PORTALES['hub']
HUB_MIN = [min(a, b) - 4 for a, b in zip(_HUB['desde'], _HUB['hasta'])]
HUB_MAX = [max(a, b) + 5 for a, b in zip(_HUB['desde'], _HUB['hasta'])]


def script():
    mundos = ' or '.join(f'"{m}"' for m in MUNDOS)
    return f'''# Generado por datapack-src/llegada_survival.py: no editar a mano.
# {SEGUNDOS} segundos sin dano al llegar al Survival (mobs esperando en la cama).

function astral_llegada(p: player):
    wait 1 tick
    name of world of {{_p}} is {mundos}
    set {{-astral.llegada::%uuid of {{_p}}%}} to now
    send action bar "&a{SEGUNDOS} segundos de proteccion al llegar" to {{_p}}

# Vida base {VIDA_JUGADOR_BASE} (escala.py): al morir Minecraft la vuelve a 20 y la marca del datapack
# (astral.vida{VIDA_JUGADOR_BASE}) queda puesta, asi que no se reponia. Se repone al reaparecer y al entrar.
function astral_vida_base(p: player, curar: boolean):
    wait 1 tick
    {{_p}} is online
    execute console command "minecraft:attribute %name of {{_p}}% minecraft:max_health base set {VIDA_JUGADOR_BASE}"
    {{_curar}} is true
    set health of {{_p}} to max health of {{_p}}

# Volver al ultimo lugar (23/11, pedido del dueno): al salir del Survival se guarda donde estaba y al volver
# (tren, Viajero, portal, comando) se lo lleva ahi. Si muere, se borra y vale lo normal (cama o spawn).
# {{astral.ultimo::...}} es persistente: sobrevive reinicios.
function astral_es_survival(w: world) :: boolean:
    name of {{_w}} is {mundos}
    return true

function astral_en_hub(l: location) :: boolean:
    # Siempre devuelve true/false (un valor vacio no pasaria la condicion "is false").
    if name of world of {{_l}} is "world_nether":
        if x-coordinate of {{_l}} is between {HUB_MIN[0]} and {HUB_MAX[0]}:
            if y-coordinate of {{_l}} is between {HUB_MIN[1]} and {HUB_MAX[1]}:
                if z-coordinate of {{_l}} is between {HUB_MIN[2]} and {HUB_MAX[2]}:
                    return true
    return false

on teleport:
    astral_es_survival(world of player) is true
    astral_en_hub(location of player) is false
    set {{-astral.salida::%uuid of player%}} to location of player

on command:
    sender is a player
    set {{_c}} to command
    loop "home", "essentials:home", "ehome" and "essentials:ehome":
        if {{_c}} is loop-value:
            set {{-astral.home::%uuid of player%}} to now
            stop

on world change:
    astral_llegada(player)
    set {{_u}} to uuid of player
    if astral_en_hub(location of player) is true:
        delete {{-astral.salida::%{{_u}}%}}
    else if astral_es_survival(world of player) is true:
        # 24/11: /home lleva a la casa, no al ultimo lugar.
        if {{-astral.home::%{{_u}}%}} is set:
            if difference between {{-astral.home::%{{_u}}%}} and now is less than 5 seconds:
                delete {{astral.ultimo::%{{_u}}%}}
                delete {{-astral.salida::%{{_u}}%}}
        {{astral.ultimo::%{{_u}}%}} is set
        set {{_l}} to {{astral.ultimo::%{{_u}}%}}
        delete {{astral.ultimo::%{{_u}}%}}
        delete {{-astral.salida::%{{_u}}%}}
        wait 2 ticks
        player is online
        astral_es_survival(world of player) is true
        astral_en_hub(location of player) is false
        teleport player to {{_l}}
        send "&7Volviste al ultimo lugar donde estabas en el Survival." to player
    else:
        {{-astral.salida::%{{_u}}%}} is set
        astral_es_survival(world of {{-astral.salida::%{{_u}}%}}) is true
        set {{astral.ultimo::%{{_u}}%}} to {{-astral.salida::%{{_u}}%}}
        delete {{-astral.salida::%{{_u}}%}}

on death of player:
    delete {{astral.ultimo::%uuid of victim%}}
    delete {{-astral.salida::%uuid of victim%}}

on respawn:
    astral_llegada(player)
    astral_vida_base(player, true)

on join:
    astral_llegada(player)
    astral_vida_base(player, false)
    astral_vida_salida(player)

# Vida al salir (25/11, pedido del dueno): Minecraft carga la vida antes de sumar la vida de la armadura y la
# recorta a la vida base ({VIDA_JUGADOR_BASE}). Se guarda al salir y se devuelve al entrar, ya con la armadura puesta.
# Regla del dueno: arranca solo para {PRUEBA}; `/vidasalida publico` la abre a todos.
function astral_vidasalida_puede(p: player) :: boolean:
    if name of {{_p}} is "{PRUEBA}":
        return true
    if {{astral.vidasalida.publico}} is true:
        return true
    return false

function astral_vida_salida(p: player):
    set {{_u}} to uuid of {{_p}}
    {{astral.vidasalida::%{{_u}}%}} is set
    set {{_h}} to {{astral.vidasalida::%{{_u}}%}}
    delete {{astral.vidasalida::%{{_u}}%}}
    astral_vidasalida_puede({{_p}}) is true
    wait {ESPERA_VIDA} ticks
    {{_p}} is online
    health of {{_p}} > 0
    if {{_h}} > max health of {{_p}}:
        set {{_h}} to max health of {{_p}}
    set health of {{_p}} to {{_h}}

command /vidasalida <text>:
    permission: op
    trigger:
        if arg-1 is "publico":
            set {{astral.vidasalida.publico}} to true
            send "&aVida al salir: abierta para todos." to sender
        else if arg-1 is "privado":
            delete {{astral.vidasalida.publico}}
            send "&eVida al salir: solo {PRUEBA}." to sender
        else:
            send "&7/vidasalida publico | privado" to sender

on damage of player:
    {{-astral.llegada::%uuid of victim%}} is set
    if difference between {{-astral.llegada::%uuid of victim%}} and now is less than {SEGUNDOS} seconds:
        damage cause is not void
        cancel event
    else:
        delete {{-astral.llegada::%uuid of victim%}}

on quit:
    delete {{-astral.llegada::%uuid of player%}}
    # Muerto (pantalla de muerte) no se guarda: reaparece normal.
    health of player > 0
    set {{astral.vidasalida::%uuid of player%}} to health of player
'''


if __name__ == '__main__':
    out = ROOT.parent / 'build/gameplay/astral_llegada.sk'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(script(), encoding='utf-8', newline='\n')
    print(out)
