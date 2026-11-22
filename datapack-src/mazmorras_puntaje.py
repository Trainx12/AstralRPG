# -*- coding: utf-8 -*-
"""Puntaje de mazmorras (S..F) y cofre con ruleta invisible (plan E2, 18/11/2026).

- `mazpuntaje inicio <mundo>`: lo llama mazmorras_copias.sk cuando una party entra a una copia libre.
- Cada muerte o caida (party -> espectador) en esa copia suma 1.
- `mazpuntaje fin <mundo>`: al ganar (mazfin; en la Fosa, la muerte del Cangrejo). Calcula la nota con el tiempo y
  las muertes, la muestra y deja UN cofre pendiente por jugador de la copia (puntaje astral.nota para la ventana).
- `astralcofre <jugador> <mazmorra>`: boton RECLAMAR del cofre (cofre_mazmorra.py). Fragmento la primera vez,
  ruleta de plata por nota, tiradas de items por nota y, con A o S, chance MUY baja de equipo del tier siguiente.
Todas las cifras: economia.py.  python mazmorras_puntaje.py -> build/mazmorras/astral_puntaje.sk
"""
from pathlib import Path

import economia as E

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/mazmorras/astral_puntaje.sk'
ROMANO = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
VANILLA = {'diamond': 'Diamante', 'emerald': 'Esmeralda', 'golden_apple': 'Manzana Dorada',
           'experience_bottle': 'Botella de Experiencia', 'netherite_scrap': 'Fragmento de Netherita',
           'totem_of_undying': 'Totem de la Inmortalidad', 'netherite_ingot': 'Lingote de Netherita',
           'enchanted_golden_apple': 'Manzana Dorada Encantada'}
FAMILIA = {'espada': 'Espada', 'hacha': 'Hacha', 'arco': 'Arco', 'baston': 'Baston', 'guadana': 'Guadana',
           'lanza': 'Lanza', 'cuchillo': 'Cuchillo', 'ballesta': 'Ballesta', 'berserker': 'Berserker', 'mago': 'Mago',
           'arquero': 'Arquero', 'helmet': 'Casco', 'chestplate': 'Pechera', 'leggings': 'Grebas', 'boots': 'Botas'}


def mazmorras():
    """[(key, nombre, tier, [mundos Bukkit])] de todas las mazmorras con cofre."""
    from mazmorras_copias import dungeons
    from instancias import bukkit
    from escala import TIER_MAZMORRA, TIER_FIJO
    out = []
    for d in dungeons():
        tier = TIER_MAZMORRA.get(d['dims'][0].split(':')[-1]) or TIER_FIJO.get(d['dims'][0].split(':')[-1])
        out.append((d['key'], d['name'], tier, [bukkit(x.split(':')[-1]) for x in d['dims']]))
    return out


def nombre_item(iid, astral):
    if not astral:
        return VANILLA[iid]
    from items import MATERIALS
    from tanda_xp import NOMBRES
    return MATERIALS[iid][0] if iid in MATERIALS else NOMBRES[iid]


def nombre_equipo(iid):
    partes = iid.split('_')
    tier = next(int(x) for x in partes if x.isdigit())
    palabras = [FAMILIA[x] for x in partes if not x.isdigit()]
    if len(palabras) == 2:           # armadura: Casco Berserker
        palabras.reverse()
    return ' '.join(palabras) + ' ' + ROMANO[tier]


def _nota_idx(n):
    return E.NOTAS.index(n) + 1


def _dar(iid, astral, cant, indent='    '):
    if astral:
        return [f'{indent}loop {cant} times:',
                f'{indent}    execute console command "loot give %name of {{_p}}% loot astral:item/{iid}"']
    return [f'{indent}execute console command "give %name of {{_p}}% minecraft:{iid} {cant}"']


def datos():
    """Tablas en memoria (on load): pool por tier, pesos por nota, equipo especial y datos de cada cofre."""
    from cofre_mazmorra import PREMIOS, NOMBRE, permiso
    L = ['    delete {-pz.pool::*}', '    delete {-pz.peso::*}', '    delete {-pz.total::*}', '    delete {-pz.eq::*}',
         '    delete {-pz.cofre::*}', '    delete {-pz.ruleta::*}']
    for n in E.NOTAS:
        i = _nota_idx(n)
        L += [f'    set {{-pz.ruleta::{i}::letra}} to "{n}"', f'    set {{-pz.ruleta::{i}::color}} to "{E.NOTA_COLOR[n]}"',
              f'    set {{-pz.ruleta::{i}::max}} to {E.RULETA_MAX[n]}', f'    set {{-pz.ruleta::{i}::k}} to {E.RULETA_K[n]}',
              f'    set {{-pz.ruleta::{i}::tiradas}} to {E.ITEM_TIRADAS[n]}',
              f'    set {{-pz.ruleta::{i}::especial}} to {E.ESPECIAL_PROB.get(n, 0)}']
    for t in sorted({t for _, _, t, _ in mazmorras()}):
        for j, (iid, astral, cant, _, _) in enumerate(E.pool(t), 1):
            L += [f'    set {{-pz.pool::{t}::{j}::id}} to "{iid}"', f'    set {{-pz.pool::{t}::{j}::astral}} to {str(astral).lower()}',
                  f'    set {{-pz.pool::{t}::{j}::cant}} to {cant}', f'    set {{-pz.pool::{t}::{j}::nombre}} to "{nombre_item(iid, astral)}"']
        L += [f'    set {{-pz.pooln::{t}}} to {len(E.pool(t))}']
        for n in E.NOTAS:
            w = E.pesos(t, n)
            L += [f'    set {{-pz.total::{t}::{_nota_idx(n)}}} to {sum(w)}']
            L += [f'    set {{-pz.peso::{t}::{_nota_idx(n)}::{j}}} to {x}' for j, x in enumerate(w, 1)]
        eq = E.equipo(t + 1)
        L += [f'    set {{-pz.eqn::{t}}} to {len(eq)}']
        for j, iid in enumerate(eq, 1):
            L += [f'    set {{-pz.eq::{t}::{j}::id}} to "{iid}"', f'    set {{-pz.eq::{t}::{j}::nombre}} to "{nombre_equipo(iid)}"']
    for key, nombre, tier, _ in mazmorras():
        frag = PREMIOS[key][0]
        L += [f'    set {{-pz.cofre::{key}::nombre}} to "{nombre}"', f'    set {{-pz.cofre::{key}::tier}} to {tier}',
              f'    set {{-pz.cofre::{key}::mult}} to {E.ruleta_mult(key, tier)}']
        if frag:   # la Nave del Vacio no da fragmento
            L += [f'    set {{-pz.cofre::{key}::perm}} to "{permiso(frag)}"', f'    set {{-pz.cofre::{key}::frag}} to "{NOMBRE[frag]}"']
    return L


COBRO = r'''
function pz_especial(p: player, t: number, maz: text):
    set {_j} to random integer between 1 and {-pz.eqn::%{_t}%}
    execute console command "loot give %name of {_p}% loot astral:item/%{-pz.eq::%{_t}%::%{_j}%::id}%"
    broadcast "&6&l✦ &e%name of {_p}% &6saco &f&l%{-pz.eq::%{_t}%::%{_j}%::nombre}% &6del cofre de &f%{_maz}%&6!"
    play sound "ui.toast.challenge_complete" to {_p}

function pz_tirada(p: player, t: number, n: number, maz: text):
    if random number between 0 and 1 < {-pz.ruleta::%{_n}%::especial}:
        pz_especial({_p}, {_t}, {_maz})
        stop
    set {_r} to random integer between 1 and {-pz.total::%{_t}%::%{_n}%}
    set {_acc} to 0
    loop {-pz.pooln::%{_t}%} times:
        set {_j} to loop-number
        add {-pz.peso::%{_t}%::%{_n}%::%{_j}%} to {_acc}
        if {_r} <= {_acc}:
            set {_id} to {-pz.pool::%{_t}%::%{_j}%::id}
            set {_c} to {-pz.pool::%{_t}%::%{_j}%::cant}
            if {-pz.pool::%{_t}%::%{_j}%::astral} is true:
                loop {_c} times:
                    execute console command "loot give %name of {_p}% loot astral:item/%{_id}%"
            else:
                execute console command "give %name of {_p}% minecraft:%{_id}% %{_c}%"
            send "&7  + &f%{_c}%x %{-pz.pool::%{_t}%::%{_j}%::nombre}%" to {_p}
            stop

function pz_cofre(p: player, key: text, n: number):
    set {_maz} to {-pz.cofre::%{_key}%::nombre}
    set {_t} to {-pz.cofre::%{_key}%::tier}
    set {_perm} to {-pz.cofre::%{_key}%::perm}
    if {_perm} is set:
        if {_p} does not have permission {_perm}:
            execute console command "lp user %name of {_p}% permission set %{_perm}% true"
            send "&b&lNuevo fragmento: &f%{-pz.cofre::%{_key}%::frag}%&7. Quedo guardado en &f/fragmentos&7." to {_p}
            play sound "ui.toast.challenge_complete" to {_p}
    set {_mult} to {-pz.cofre::%{_key}%::mult}
    set {_lo} to {@min} * {_mult}
    set {_hi} to {-pz.ruleta::%{_n}%::max} * {_mult}
    set {_v} to floor({_lo} + ({_hi} - {_lo}) * ((random number between 0 and 1) ^ {-pz.ruleta::%{_n}%::k}))
    add {_v} to balance of {_p}
    set {_letra} to {-pz.ruleta::%{_n}%::letra}
    send "&6Cofre de %{_maz}% &7(nota &l%{_letra}%&7): &e+%{_v}%$" to {_p}
    send title "&e+%{_v}%$" with subtitle "&7Ruleta del cofre (nota %{_letra}%)" to {_p} for 3 seconds
    loop {-pz.ruleta::%{_n}%::tiradas} times:
        pz_tirada({_p}, {_t}, {_n}, {_maz})
    # Gemas (gemas.py): chance segun la nota (F nada ... S 45%); con A/S mejor calidad.
    execute console command "astralgema cofre %name of {_p}% %{_t}% %{_n}%"
    execute console command "execute as %name of {_p}% run function astral:xp/cofre"
    execute console command "lp user %name of {_p}% permission settemp astral.%{_key}%.cd true {@cooldown}"
    play sound "entity.player.levelup" to {_p}
'''


def script():
    from cofre_mazmorra import COOLDOWN
    maz = mazmorras()
    L = ['# Generado por datapack-src/mazmorras_puntaje.py (plan E2, 18/11/2026). No editar a mano.',
         '# Puntaje S..F por copia de mazmorra y cofre con ruleta invisible. Cifras: economia.py.', '',
         'options:', f'    min: {E.RULETA_MIN}', f'    cooldown: {COOLDOWN}', '',
         'on load:',
         '    execute console command "scoreboard objectives add astral.nota dummy"',
         '    delete {-pz.key::*}', '    delete {-pz.obj::*}']
    for key, _, tier, mundos in maz:
        for w in mundos:
            L += [f'    set {{-pz.key::{w}}} to "{key}"', f'    set {{-pz.obj::{w}}} to {E.TIEMPO_OBJETIVO[key]}']
    L += datos()
    L += ['',
          'command /mazpuntaje <text> <text>:',
          '    executable by: console',
          '    trigger:',
          '        if arg-1 is "inicio":',
          '            pz_inicio(arg-2)',
          '        else if arg-1 is "fin":',
          '            pz_fin(arg-2)',
          '',
          'function pz_inicio(w: text):',
          '    set {-pz.ini::%{_w}%} to unix timestamp of now',
          '    set {-pz.muertes::%{_w}%} to 0',
          '    delete {-pz.hecho::%{_w}%}',
          '',
          'function pz_muerte(p: player):',
          '    set {_w} to name of world of {_p}',
          '    {-pz.ini::%{_w}%} is set',
          '    {-pz.hecho::%{_w}%} is not set',
          '    set {_u} to uuid of {_p}',
          '    set {_ahora} to unix timestamp of now',
          '    if {_ahora} - ({-pz.ult::%{_u}%} ? 0) < 10:',
          '        stop',
          '    set {-pz.ult::%{_u}%} to {_ahora}',
          '    add 1 to {-pz.muertes::%{_w}%}',
          '',
          'on death of player:',
          '    pz_muerte(victim)',
          '',
          '# Caida con party: AstralParty pasa al jugador a espectador sin evento de muerte.',
          'on gamemode change to spectator:',
          '    scoreboard tags of player contain "astral.party.fallen"',
          '    pz_muerte(player)',
          '',
          'function pz_fin(w: text):',
          '    set {_key} to {-pz.key::%{_w}%}',
          '    {_key} is set',
          '    {-pz.hecho::%{_w}%} is not set',
          '    set {-pz.hecho::%{_w}%} to true',
          '    set {_m} to {-pz.muertes::%{_w}%} ? 0',
          '    set {_obj} to {-pz.obj::%{_w}%}',
          '    set {_seg} to {_obj} * 60',
          '    if {-pz.ini::%{_w}%} is set:',
          '        set {_seg} to (unix timestamp of now) - {-pz.ini::%{_w}%}',
          f'    set {{_pts}} to 100 - min({{_m}} * {E.PUNTOS_MUERTE}, {E.PUNTOS_MUERTE_TOPE})',
          '    set {_sobre} to floor(({_seg} - {_obj} * 60) / 60)',
          '    if {_sobre} > 0:',
          f'        remove min({{_sobre}} * {E.PUNTOS_MINUTO}, {E.PUNTOS_MINUTO_TOPE}) from {{_pts}}',
          '    if {_m} is 0:',
          f'        add {E.PUNTOS_SIN_MUERTES} to {{_pts}}',
          '    set {_n} to 1']
    for n in E.NOTAS[1:]:
        L += [f'    if {{_pts}} >= {E.NOTA_MIN[n]}:', f'        set {{_n}} to {_nota_idx(n)}']
    L += ['    set {_nombre} to {-pz.cofre::%{_key}%::nombre}',
          '    set {_tmin} to floor({_seg} / 60)',
          '    set {_tseg} to mod({_seg}, 60)',
          '    loop all players:',
          '        name of world of loop-player is {_w}',
          '        set {_u} to uuid of loop-player',
          '        set {pz.pend.key::%{_u}%} to {_key}',
          '        set {pz.pend.nota::%{_u}%} to {_n}',
          '        execute console command "scoreboard players set %name of loop-player% astral.nota %{_n}%"',
          '        if ({pz.mejor::%{_u}%::%{_key}%} ? 0) < {_n}:',
          '            set {pz.mejor::%{_u}%::%{_key}%} to {_n}']
    for n in E.NOTAS:
        c = E.NOTA_COLOR[n]
        L += [f'        if {{_n}} is {_nota_idx(n)}:',
              # Mismo cartel grande que mazfin ("X conquistada") con el puntaje abajo (dueno 19/11).
              f'            send title "&b%{{_nombre}}% conquistada" with subtitle "{c}&lPuntaje {n}" to loop-player for 6 seconds',
              f'            send "&6Nota de la mazmorra: {c}&l{n} &7(%{{_pts}}% puntos)" to loop-player']
    L += ['        send "&7Tiempo: &f%{_tmin}% min %{_tseg}% s &8(objetivo %{_obj}% min) &7| Muertes de la party: &f%{_m}%" to loop-player',
          '        send "&7Abri el cofre: la plata y los premios dependen de la nota." to loop-player',
          '',
          '# Boton RECLAMAR del cofre (DeluxeMenus cofre_<mazmorra>): una ruleta por jugador por victoria.',
          'command /astralcofre <player> <text>:',
          '    executable by: console',
          '    trigger:',
          '        set {_p} to arg-1',
          '        set {_u} to uuid of {_p}',
          '        if {pz.pend.key::%{_u}%} is not arg-2:',
          '            send "&cEste cofre se cobra al ganar la mazmorra. &7(Cada victoria trae un cofre nuevo.)" to {_p}',
          '            play sound "entity.villager.no" to {_p}',
          '            stop',
          '        set {_n} to {pz.pend.nota::%{_u}%}',
          '        delete {pz.pend.key::%{_u}%}',
          '        delete {pz.pend.nota::%{_u}%}',
          '        execute console command "scoreboard players set %name of {_p}% astral.nota 0"',
          '        log "%now% %name of {_p}% %{_u}% %arg-2% nota=%{_n}%" to "astral-cofres"']
    L += ['        pz_cofre({_p}, arg-2, {_n})']
    return '\n'.join(L) + '\n' + COBRO


def generate():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(script(), encoding='utf-8')
    print(f'puntaje: {len(mazmorras())} mazmorras -> {OUT}')


if __name__ == '__main__':
    generate()
