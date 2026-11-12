"""Entrada a las 6 copias de cada mazmorra, parties y limite de 8 minutos despues del jefe.

- `mazentrar <jugador> <mazmorra>` (consola; lo usan los NPC y /mazmorras): si un companero de party ya
  esta en una copia de esa mazmorra, va ahi; si no, toma la primera copia libre y lleva a los companeros
  de party que esten en el lobby. Sin copias libres: "Mazmorra ocupada".
- `mazfin <mundo>` (consola; lo usa el controlador al ganar): 8 minutos despues, los que sigan en esa
  copia vuelven al spawn y la copia queda libre.
- `/party`: invitar, aceptar, rechazar, salir, echar. Solo en memoria (se borra al reiniciar).

python mazmorras_copias.py -> build/mazmorras/astral_mazmorras_copias.sk
"""
from pathlib import Path

from instancias import COPIES, DUNGEON_WORLDS, copias, bukkit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/mazmorras/astral_mazmorras_copias.sk'
MINUTOS_FIN = 8
PARTY_MAX = 6
LIBRE_TRAS = 15        # segundos que una copia vacia espera antes de recibir otro grupo (reinicio de salas)


def dungeons():
    from viajes_mazmorras import destinations
    out = []
    for d in destinations():
        if not d.get('enabled', False):
            continue
        room = d['rooms'][0]
        x, y, z = room['llegada']
        out.append(dict(key=d['key'], name=d['name'], dims=copias(DUNGEON_WORLDS[d['key']]),
                        arrival=(x, y, z, room.get('yaw', 0))))
    return out


def all_worlds():
    return [bukkit(dim) for d in dungeons() for dim in d['dims']]


def script(minutos=MINUTOS_FIN):
    MINUTOS_FIN = minutos  # la prueba local usa 1 minuto
    L = [f'# Generado por mazmorras_copias.py: {COPIES} copias por mazmorra, parties y {MINUTOS_FIN} minutos tras el jefe.',
         '# Variables {-...}: solo memoria. Se borran al reiniciar (nadie queda adentro tras un reinicio).',
         '',
         'function party_miembros(p: player) :: players:',
         '    set {_l} to {-party.lider::%uuid of {_p}%}',
         '    if {_l} is not set:',
         '        return {_p}',
         '    return {-party.miembros::%{_l}%::*}',
         '',
         'function party_avisar(l: text, m: text):',
         '    loop {-party.miembros::%{_l}%::*}:',
         '        send "&d[Party] &f%{_m}%" to loop-value',
         '',
         'function party_sacar(p: player):',
         '    set {_l} to {-party.lider::%uuid of {_p}%}',
         '    if {_l} is not set:',
         '        stop',
         '    if {_l} is "%uuid of {_p}%":',
         '        party_avisar({_l}, "%name of {_p}% disolvio la party.")',
         '        loop {-party.miembros::%{_l}%::*}:',
         '            delete {-party.lider::%uuid of loop-value%}',
         '        delete {-party.miembros::%{_l}%::*}',
         '        stop',
         '    delete {-party.miembros::%{_l}%::%uuid of {_p}%}',
         '    delete {-party.lider::%uuid of {_p}%}',
         '    party_avisar({_l}, "%name of {_p}% salio de la party.")',
         '    send "&dSaliste de la party." to {_p}',
         '',
         'command /party [<text>] [<text>]:',
         '    aliases: grupo',
         '    executable by: players',
         '    description: Grupo para entrar juntos a las mazmorras.',
         '    trigger:',
         '        set {_l} to {-party.lider::%uuid of player%}',
         '        if arg-1 is not set:',
         '            if {_l} is not set:',
         f'                send "&dParty: &fno estas en ninguna. &7/party invitar <jugador> (hasta {PARTY_MAX})." to player',
         '                stop',
         '            loop {-party.miembros::%{_l}%::*}:',
         '                add name of loop-value to {_n::*}',
         '            send "&dParty (%size of {_n::*}%): &f%{_n::*}%" to player',
         '            send "&7Entran juntos a la misma mazmorra. /party salir para dejarla." to player',
         '            stop',
         '        if arg-1 is "invitar":',
         '            set {_t} to arg-2 parsed as player',
         '            if {_t} is not set:',
         '                send "&cEse jugador no esta conectado. Uso: /party invitar <jugador>" to player',
         '                stop',
         '            if {_t} is player:',
         '                send "&cNo podes invitarte a vos mismo." to player',
         '                stop',
         '            if {-party.lider::%uuid of {_t}%} is set:',
         '                send "&c%name of {_t}% ya esta en una party." to player',
         '                stop',
         '            if {_l} is not set:',
         '                set {_l} to "%uuid of player%"',
         '                set {-party.lider::%uuid of player%} to {_l}',
         '                set {-party.miembros::%{_l}%::%uuid of player%} to player',
         '            if {_l} is not "%uuid of player%":',
         '                send "&cSolo el lider de la party puede invitar." to player',
         '                stop',
         f'            if size of {{-party.miembros::%{{_l}}%::*}} >= {PARTY_MAX}:',
         f'                send "&cLa party esta llena (maximo {PARTY_MAX})." to player',
         '                stop',
         '            set {-party.inv::%uuid of {_t}%} to {_l}',
         '            set {-party.invt::%uuid of {_t}%} to now',
         '            send "&dInvitaste a &f%name of {_t}%&d. Tiene 60 segundos para aceptar." to player',
         '            send "&d%name of player% te invito a su party. &fEscribi &a/party aceptar &fo &c/party rechazar&f." to {_t}',
         '            stop',
         '        if arg-1 is "aceptar":',
         '            set {_i} to {-party.inv::%uuid of player%}',
         '            if {_i} is not set:',
         '                send "&cNo tenes invitaciones." to player',
         '                stop',
         '            delete {-party.inv::%uuid of player%}',
         '            if difference between {-party.invt::%uuid of player%} and now > 60 seconds:',
         '                send "&cLa invitacion vencio. Pedi otra." to player',
         '                stop',
         '            if {-party.lider::%{_i}%} is not set:',
         '                send "&cEsa party ya no existe." to player',
         '                stop',
         '            if {_l} is set:',
         '                party_sacar(player)',
         f'            if size of {{-party.miembros::%{{_i}}%::*}} >= {PARTY_MAX}:',
         '                send "&cLa party se lleno." to player',
         '                stop',
         '            set {-party.lider::%uuid of player%} to {_i}',
         '            set {-party.miembros::%{_i}%::%uuid of player%} to player',
         '            party_avisar({_i}, "%name of player% se unio a la party.")',
         '            stop',
         '        if arg-1 is "rechazar":',
         '            delete {-party.inv::%uuid of player%}',
         '            send "&7Invitacion rechazada." to player',
         '            stop',
         '        if arg-1 is "salir":',
         '            if {_l} is not set:',
         '                send "&cNo estas en una party." to player',
         '                stop',
         '            party_sacar(player)',
         '            stop',
         '        if arg-1 is "echar":',
         '            if {_l} is not "%uuid of player%":',
         '                send "&cSolo el lider puede echar." to player',
         '                stop',
         '            set {_t} to arg-2 parsed as player',
         '            if {_t} is not set:',
         '                send "&cUso: /party echar <jugador>" to player',
         '                stop',
         '            if {-party.lider::%uuid of {_t}%} is not {_l}:',
         '                send "&cEse jugador no esta en tu party." to player',
         '                stop',
         '            if {_t} is player:',
         '                stop',
         '            party_sacar({_t})',
         '            send "&cTe echaron de la party." to {_t}',
         '            stop',
         '        send "&dParty: &f/party invitar <jugador>, aceptar, rechazar, salir, echar <jugador>" to player',
         '',
         'on quit:',
         '    party_sacar(player)',
         '    delete {-party.inv::%uuid of player%}',
         '',
         'function maz_jugadores(w: world) :: number:',
         '    set {_c} to 0',
         '    loop all players:',
         '        world of loop-player is {_w}',
         '        add 1 to {_c}',
         '    return {_c}',
         '',
         'function maz_entrar(p: player, key: text):']
    for d in dungeons():
        x, y, z, yaw = d['arrival']
        L += [f'    if {{_key}} is "{d["key"]}":',
              f'        set {{_nombre}} to "{d["name"]}"',
              f'        set {{_tp}} to "{x} {y} {z} {yaw} 0"']
        for n, dim in enumerate(d['dims'], 1):
            L += [f'        set {{_dim::{n}}} to "{dim}"', f'        set {{_mundo::{n}}} to "{bukkit(dim)}"']
    L += ['    if {_nombre} is not set:',
          '        stop',
          '    # 1) Si un companero de party ya esta adentro, va a su copia.',
          '    set {_m::*} to party_miembros({_p})',
          '    set {_elegida} to 0',
          f'    loop {COPIES} times:',
          '        set {_w} to world({_mundo::%loop-number%})',
          '        if {_w} is set:',
          '            loop {_m::*}:',
          '                loop-value-2 is not {_p}',
          '                world of loop-value-2 is {_w}',
          '                set {_elegida} to loop-number',
          '        if {_elegida} > 0:',
          '            exit loop',
          '    if {_elegida} > 0:',
          '        set {_grupo::*} to {_p}',
          '    else:',
          '        # 2) Primera copia vacia (y vacia hace un rato, para que se reinicien las salas).',
          f'        loop {COPIES} times:',
          '            set {_w} to world({_mundo::%loop-number%})',
          '            if {_w} is set:',
          '                if maz_jugadores({_w}) is 0:',
          '                    if {-maz.vacia::%{_mundo::%loop-number%}%} is set:',
          f'                        if difference between {{-maz.vacia::%{{_mundo::%loop-number%}}%}} and now >= {LIBRE_TRAS} seconds:',
          '                            set {_elegida} to loop-number',
          '                            exit loop',
          '        if {_elegida} is 0:',
          '            send "&cMazmorra ocupada: &flas %size of {_dim::*}% copias de %{_nombre}% estan en uso. &7Proba en unos minutos." to {_p}',
          '            stop',
          '        # La party entra junta: los companeros que esten en el lobby.',
          '        loop {_m::*}:',
          '            if loop-value is {_p}:',
          '                add loop-value to {_grupo::*}',
          '            else if name of world of loop-value is "lobby":',
          '                add loop-value to {_grupo::*}',
          '    set {_d} to {_dim::%{_elegida}%}',
          '    delete {-maz.vacia::%{_mundo::%{_elegida}%}%}',
          '    loop {_grupo::*}:',
          '        send "&8[&7%{_nombre}%&8] &7Entrando a la copia &f%{_elegida}%&7... &8(Para salir: /spawn)" to loop-value',
          '        execute console command "execute in minecraft:%{_d}% run minecraft:tp %uuid of loop-value% %{_tp}%"',
          '',
          'command /mazentrar <player> <text>:',
          '    executable by: console',
          '    trigger:',
          '        maz_entrar(arg-1, arg-2)',
          '',
          'command /mazfin <text>:',
          '    executable by: console',
          '    trigger:',
          '        if {-maz.fin::%arg-1%} is set:',
          '            stop',
          '        set {-maz.fin::%arg-1%} to now',
          '        set {_w} to world(arg-1)',
          '        if {_w} is set:',
          '            loop all players:',
          '                world of loop-player is {_w}',
          f'                send "&6Ganaron! &fTienen {MINUTOS_FIN} minutos para abrir el cofre. Despues vuelven al spawn." to loop-player',
          '',
          'every 5 seconds:']
    for name in all_worlds():
        L += [f'    set {{_w}} to world("{name}")',
              '    if {_w} is set:',
              '        if maz_jugadores({_w}) is 0:',
              f'            if {{-maz.vacia::{name}}} is not set:',
              f'                set {{-maz.vacia::{name}}} to now',
              f'            delete {{-maz.fin::{name}}}',
              f'            delete {{-maz.aviso::{name}}}',
              '        else:',
              f'            delete {{-maz.vacia::{name}}}',
              f'            if {{-maz.fin::{name}}} is set:',
              f'                set {{_t}} to difference between {{-maz.fin::{name}}} and now',
              f'                if {{_t}} >= {MINUTOS_FIN} minutes:',
              '                    loop all players:',
              '                        world of loop-player is {_w}',
              '                        send "&eSe termino el tiempo en la mazmorra: volviste al spawn." to loop-player',
              '                        execute console command "spawn %name of loop-player%"',
              f'                    delete {{-maz.fin::{name}}}',
              f'                    delete {{-maz.aviso::{name}}}',
              f'                else if {{_t}} >= {MINUTOS_FIN - 1} minutes:',
              f'                    if {{-maz.aviso::{name}}} is not set:',
              f'                        set {{-maz.aviso::{name}}} to true',
              '                        loop all players:',
              '                            world of loop-player is {_w}',
              '                            send "&eQueda 1 minuto: despues volves al spawn." to loop-player']
    return '\n'.join(L) + '\n'


def generate():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(script(), encoding='utf8')
    return OUT


if __name__ == '__main__':
    print(generate())
