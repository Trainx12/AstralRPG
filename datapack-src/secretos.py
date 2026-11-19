# -*- coding: utf-8 -*-
"""Secretos de Astral (plan E3, 18/11/2026): carteles escondidos que dan un premio una vez por jugador.

- `/secreto crear [pista]` (OP): registra el cartel (o bloque) que estas mirando, le escribe el texto y
  muestra la linea para copiar a SECRETOS de este archivo. `/secreto borrar`, `/secreto lista`.
- Clic derecho en un secreto: lo reclama (una vez por jugador, guardado por UUID). `/secretos`: cuantos encontraste.
- Premio (ruleta invisible, cifras en economia.py): muy raro equipo de 1 tier mas que tu mejor arma Astral
  (puntaje astral.wt del datapack; sin equipo = tier I), plata (5-20% de lo que llevas, 10.000 a 5.000.000) o
  premios del pool de cofres de tu tier (usa pz_tirada de astral_puntaje.sk).

python secretos.py -> build/secretos/astral_secretos.sk
"""
from pathlib import Path

import economia as E

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/secretos/astral_secretos.sk'

# Secretos fijos (los que el dueno elige). (id, mundo Bukkit, x, y, z, pista). Vacio hasta que el dueno los coloque:
# /secreto crear en el juego y despues copiar aca la linea que imprime, para que queden en el repo.
SECRETOS = []

# Propuesta de 10 lugares (NO colocados): ver build/deploy/secretos.md.
PROPUESTAS = [
    ('lobby', 'Detras del Cronista, entre las columnas', (189, 102, 221)),
    ('lobby', 'Abajo del puente del tren, junto al agua', (112, 96, 192)),
    ('lobby', 'Arriba del edificio de Portales Astrales', (211, 112, 240)),
    ('world', 'Cueva cerca del spawn del survival', None),
    ('bosque', 'Bosque Sombrio: escondido en el Claro corrompido', (1504, 107, 1504)),
    ('tumba', 'Tumba: en el Pasaje de los sellos', (-175, 88, 203)),
    ('cumbre_hielo', 'Cumbre Helada: atras de la Plaza de la fuente', None),
    ('forja_volcano', 'Corazon de la Forja: junto al Nucleo', (82, 52, -55)),
    ('oceano', 'Oceano Astral: en el fondo, cerca de la entrada a la Fosa', None),
    ('astral_minas', 'Minas Astrales: en la sala de espera de la primera mina', None),
]


def datos():
    L = []
    for sid, w, sx, sy, sz, pista in SECRETOS:
        L += [f'    if {{secreto.lista::{sid}}} is not set:',
              f'        set {{secreto.lista::{sid}}} to "{w}|{sx}|{sy}|{sz}"',
              f'        set {{secreto.pista::{sid}}} to "{pista}"',
              f'        set {{secreto.idx::{w}|{sx}|{sy}|{sz}}} to "{sid}"']
    L += ['    delete {-sec.eq::*}']
    for t in range(1, 11):
        eq = E.equipo(min(t + 1, 10))
        L += [f'    set {{-sec.eqn::{t}}} to {len(eq)}']
        L += [f'    set {{-sec.eq::{t}::{j}}} to "{iid}"' for j, iid in enumerate(eq, 1)]
    return L


CUERPO = r'''
function sec_clave(b: block) :: text:
    return "%name of world of {_b}%|%floor(x-coordinate of {_b})%|%floor(y-coordinate of {_b})%|%floor(z-coordinate of {_b})%"

function sec_tier(p: player) :: number:
    # astral.wt (datapack) = tier de la mejor arma Astral que lleva. Skript lo lee con etiquetas temporales.
    set {_t} to 1
    loop 10 times:
        execute console command "execute as %uuid of {_p}% if score @s astral.wt matches %loop-number% run tag @s add astral.secwt%loop-number%"
        if scoreboard tags of {_p} contain "astral.secwt%loop-number%":
            set {_t} to loop-number
            execute console command "tag %uuid of {_p}% remove astral.secwt%loop-number%"
    return {_t}

function sec_reclamar(p: player, id: text):
    set {_u} to uuid of {_p}
    if {secretos.tiene::%{_u}%::%{_id}%} is set:
        send "&7Ya encontraste este secreto. &8(/secretos)" to {_p}
        stop
    set {secretos.tiene::%{_u}%::%{_id}%} to now
    add 1 to {secretos.n::%{_u}%}
    send title "&d&l✦ Secreto de Astral ✦" with subtitle "&7Encontraste un secreto" to {_p} for 3 seconds
    play sound "ui.toast.challenge_complete" to {_p}
    execute console command "execute at %uuid of {_p}% run particle minecraft:end_rod ~ ~1 ~ 0.6 1 0.6 0.05 60"
    set {_r} to random number between 0 and 1
    set {_t} to sec_tier({_p})
    if {_r} < {@prob_equipo}:
        set {_n} to random integer between 1 and {-sec.eqn::%{_t}%}
        set {_id2} to {-sec.eq::%{_t}%::%{_n}%}
        execute console command "loot give %name of {_p}% loot astral:item/%{_id2}%"
        broadcast "&d&l✦ &e%name of {_p}% &dencontro un secreto de Astral y gano &f&lequipo de tier superior&d!"
    else if {_r} < {@prob_equipo} + {@prob_plata}:
        set {_v} to floor(balance of {_p} * (random number between {@pct_min} and {@pct_max}))
        if {_v} < {@plata_min}:
            set {_v} to {@plata_min}
        if {_v} > {@plata_max}:
            set {_v} to {@plata_max}
        add {_v} to balance of {_p}
        send "&dEl secreto guardaba &e+%{_v}%$" to {_p}
    else:
        send "&dEl secreto guardaba:" to {_p}
        loop {@tiradas} times:
            pz_tirada({_p}, min({_t}, 5), {@nota}, "un secreto")
    send "&7Secretos encontrados: &f%{secretos.n::%{_u}%}%&7/&f%size of {secreto.lista::*}%" to {_p}
    log "%now% %name of {_p}% %{_u}% secreto %{_id}%" to "astral-secretos"

on right click:
    event-block is set
    set {_id} to {secreto.idx::%sec_clave(event-block)%}
    {_id} is set
    cancel event
    set {_ahora} to unix timestamp of now
    if {_ahora} - ({-sec.ult::%uuid of player%} ? 0) < 1:
        stop
    set {-sec.ult::%uuid of player%} to {_ahora}
    sec_reclamar(player, {_id})

on break:
    {secreto.idx::%sec_clave(event-block)%} is set
    cancel event
    send "&cEso es un secreto de Astral. &7(OP: /secreto borrar mirandolo)" to player

command /secretos:
    executable by: players
    trigger:
        send "&d✦ Secretos de Astral: &f%{secretos.n::%uuid of player%} ? 0%&7 de &f%size of {secreto.lista::*}%&7 encontrados." to player
        send "&7Estan escondidos en el lobby, el survival, las mazmorras y el oceano." to player

command /secreto <text> [<text>]:
    permission: astral.admin.secretos
    executable by: players
    trigger:
        set {_b} to targeted block of player
        if arg-1 is "lista":
            send "&dSecretos (%size of {secreto.lista::*}%):" to player
            loop {secreto.lista::*}:
                send "&f%loop-index% &7%loop-value% &8%{secreto.pista::%loop-index%}%" to player
            stop
        if {_b} is not set:
            send "&cMira el cartel o bloque (a menos de 5 bloques)." to player
            stop
        set {_k} to sec_clave({_b})
        if arg-1 is "crear":
            if {secreto.idx::%{_k}%} is set:
                send "&cEse bloque ya es el secreto %{secreto.idx::%{_k}%}%." to player
                stop
            add 1 to {secreto.n}
            set {_id} to "c%{secreto.n}%"
            set {secreto.lista::%{_id}%} to {_k}
            set {_pista} to arg-2 ? "-"
            set {secreto.pista::%{_id}%} to {_pista}
            set {secreto.idx::%{_k}%} to {_id}
            if "%type of {_b}%" contains "sign":
                set line 1 of {_b} to "&5&l✦ Secreto ✦"
                set line 2 of {_b} to "&dde Astral"
                set line 3 of {_b} to "&7Clic derecho"
                set line 4 of {_b} to "&7para reclamar"
            send "&aSecreto %{_id}% creado. Linea para SECRETOS de secretos.py:" to player
            send "&f('%{_id}%', '%name of world of {_b}%', %floor(x-coordinate of {_b})%, %floor(y-coordinate of {_b})%, %floor(z-coordinate of {_b})%, '%{_pista}%')," to player
            log "%now% crear %{_id}% %{secreto.lista::%{_id}%}%" to "astral-secretos"
        else if arg-1 is "borrar":
            set {_id} to {secreto.idx::%{_k}%}
            if {_id} is not set:
                send "&cEse bloque no es un secreto." to player
                stop
            delete {secreto.idx::%{_k}%}
            delete {secreto.lista::%{_id}%}
            delete {secreto.pista::%{_id}%}
            send "&eSecreto %{_id}% borrado (los jugadores que lo encontraron lo conservan en su cuenta)." to player
        else:
            send "&7Uso: /secreto crear [pista] | borrar | lista" to player
'''


def script():
    L = ['# Generado por datapack-src/secretos.py (plan E3, 18/11/2026). No editar a mano.',
         '# Usa pz_tirada de astral_puntaje.sk (premios del cofre). Cifras: economia.py.', '',
         'options:',
         f'    prob_equipo: {E.SECRETO_PROB_EQUIPO}', f'    prob_plata: {E.SECRETO_PROB_PLATA}',
         f'    pct_min: {E.SECRETO_PLATA_PCT[0]}', f'    pct_max: {E.SECRETO_PLATA_PCT[1]}',
         f'    plata_min: {E.SECRETO_PLATA_MIN}', f'    plata_max: {E.SECRETO_PLATA_MAX}',
         f'    tiradas: {E.SECRETO_TIRADAS}', f'    nota: {E.NOTAS.index(E.SECRETO_NOTA_PESOS) + 1}', '',
         'on load:'] + datos()
    return '\n'.join(L) + '\n' + CUERPO


def generate():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(script(), encoding='utf-8')
    print(f'secretos: {len(SECRETOS)} fijos -> {OUT}')


if __name__ == '__main__':
    generate()
