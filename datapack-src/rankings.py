"""Rankings semanales con carteles y premios (14/11/2026).

Uso (desde datapack-src):  python rankings.py
Salida: build/rankings/astral_rankings.sk (-> plugins/Skript/scripts/) y build/rankings/comandos.txt (carteles).

- Parkour (Spiral, Spiral 2, Paradise 3): menor tiempo de largada a meta. La largada es salir de la llegada
  (3 bloques); la meta la fija un OP parado en ella: /ranking meta <id>. Cartel atras de la llegada.
- Mazmorra Infinita: nivel mas alto aguantado al menos 2 minutos (tier x 100 + subidas extra).
- Santuario: menor tiempo de aparicion a muerte de Trainx (el grupo entero).
- Minas Astrales y Bosque: bloques y troncos sacados en la semana.
Cierre: lunes 00:00 hora Argentina. Premios al top 3 de cada ranking; titulos que solo salen de aca (/trofeos).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'build/rankings'

# ============================ PREMIOS (ajustables) ============================
from economia import plata as _x
# 25/11 (dueno: "es mucho"): antes 50M/25M/12,5M por ranking por semana (y son 7 rankings), con las Minas recortadas
# eran 15 horas de Esmeralda I. Ahora ~1 hora de mina media. Tiradas tambien bajan (antes 10+5 / 5+3 / 3+1).
PLATA = {1: 3_000_000, 2: 1_500_000, 3: 750_000}
TIRADAS = {1: (('gacha_cosmeticos', 5), ('gacha_rpg', 2)), 2: (('gacha_cosmeticos', 3), ('gacha_rpg', 1)),
           3: (('gacha_cosmeticos', 2),)}
ITEMS = {1: (('chispa_astral', 2),), 2: (('chispa_astral', 1),), 3: (('gema_luminica', 1),)}
# 25/11: frascos a la mitad (antes 6/4/2 pequenos, 3/2/1 grandes, 3/2/1 gigantes y barril al 1°).
ITEMS = {p: items + (('frasco_xp_pequeno',4-p),('frasco_xp_grande',2 if p==1 else 1)) + ((('frasco_xp_gigante',1),('manzana_esmeralda',1)) if p==1 else ()) for p,items in ITEMS.items()}
# 23/11: material raro extra, +XP de skills por 7 dias (AuraSkills: permiso auraskills.multiplier.<porcentaje>),
# titulo temporal 'Campeon de la Semana' (7 dias) al 1° y cartel de campeones (/ranking cartel campeones).
EXTRA_ITEMS = {1: (('gema_luminica_perfecta', 1),), 2: (('cristal_refinado', 2),), 3: (('cristal_refinado', 1),)}
ITEMS = {p: items + EXTRA_ITEMS[p] for p, items in ITEMS.items()}
XP_EXTRA = {1: 10, 2: 5, 3: 5}
DIAS_EXTRA = 7
TITULO_SEMANA = ('campeon_de_la_semana', 'Campeon de la Semana', '&e&l')
MASCOTA_PARKOUR = 'fenix'     # el 1° de cada parkour; si ya la tiene, 10 tiradas mas de Monturas
COLOR_PUESTO = {1: '&6&l', 2: '&f&l', 3: '&c'}
# ==============================================================================

PARKOURS = ('spiral', 'spiral2', 'paradise3')
# id, nombre, orden ('menor' = menos es mejor), titulos (oro, plata, bronce)
RANKINGS = [
    *[(f'parkour_{p}', n, 'menor', ('Rey del Parkour', 'Pies de Pluma', 'Saltarin'))
      for p, n in (('spiral', 'Parkour Spiral'), ('spiral2', 'Parkour Spiral 2'), ('paradise3', 'Parkour Paradise 3'))],
    ('infinita', 'Mazmorra Infinita', 'mayor', ('Domador del Infinito', 'Caminante Eterno', 'Explorador sin Fin')),
    # 21/11: el nombre del ranking (carteles) no dice 'Trainx' para no spoilear el jefe; titulos y jefe sin cambios.
    ('trainx', 'Vencer Santuario', 'menor', ('Verdugo de Trainx', 'Retador de Trainx', 'Testigo de la Estrella')),
    ('minas', 'Minas Astrales', 'mayor', ('Senor de las Minas', 'Pico de Oro', 'Picapiedra')),
    ('bosque', 'Bosque', 'mayor', ('Lenador Supremo', 'Hacha de Plata', 'Guardabosques')),
]
UNIDAD = {'infinita': 'nivel', 'trainx': 'tiempo', 'minas': 'bloques', 'bosque': 'troncos'}
TITULO_COLOR = {0: '&6', 1: '&7', 2: '&c'}


def titulos():
    """(clave, texto, color) de todos los titulos de ranking, sin repetir (los de parkour se comparten)."""
    out = {}
    for _, _, _, names in RANKINGS:
        for i, name in enumerate(names):
            out[name.lower().replace(' ', '_')] = (name, TITULO_COLOR[i])
    out[TITULO_SEMANA[0]] = (TITULO_SEMANA[1], TITULO_SEMANA[2])
    return out


def llegadas():
    from minijuegos import PARKOURS as P
    return {d['id']: d for d in P if d['id'] in PARKOURS}


def cartel_parkour(d):
    """Atras de la llegada: el jugador aparece mirando hacia adelante y al darse vuelta lo ve."""
    import math
    x, y, z, yaw, _ = d['arrival']
    a = math.radians(yaw)
    fx, fz = -math.sin(a), math.cos(a)      # adelante en Minecraft (yaw 0 = sur)
    return round(x - 3.5 * fx, 2), round(y + 2.2, 2), round(z - 3.5 * fz, 2)


def carteles():
    """(id, dimension, x, y, z) por defecto. Se pueden mover con /ranking cartel <id>."""
    out = []
    for pid, d in llegadas().items():
        out.append((f'parkour_{pid}', f'minecraft:{d["world"]}', *cartel_parkour(d)))
    # 15/11/2026: el dueno pidio borrar los de Infinita y Trainx del lobby; los vuelve a poner con /ranking cartel.
    # 20/11/2026: el de Minas va sobre el piso de minerales del lobby (antes quedaba atras del arbol del NPC).
    out += [('minas', 'minecraft:lobby', 146.5, 106.4, 237.5)]
    from santuario_azeroth import ARRIVAL, WORLD
    out.append(('trainx', f'minecraft:{WORLD}', ARRIVAL[0], ARRIVAL[1] + 2.5, ARRIVAL[2] + 3))
    from bosque_talar import SPAWN
    out.append(('bosque', 'minecraft:astral_bosque', SPAWN[0] - 3, SPAWN[1] + 2.4, SPAWN[2]))
    return out


def comandos():
    lines = ['# Carteles de ranking (text_display). Generado por datapack-src/rankings.py.',
             '# Se actualizan solos cada 30 s con el script. Para moverlos: parado donde va, /ranking cartel <id>.',
             'kill @e[type=text_display,tag=astral_rank]']
    for rid, dim, x, y, z in carteles():
        lines.append(f"execute in {dim} run summon text_display {x} {y} {z} {{Tags:['astral_rank','astral_rank_{rid}'],"
                     f"billboard:'center',alignment:'center',line_width:240,background:1711276032,"
                     f"text:{{text:'Ranking',color:'gold'}}}}")
    lines += ['# Metas de parkour: un OP parado en la meta de cada mapa:',
              *[f'#   /ranking meta parkour_{p}' for p in PARKOURS],
              '# Titulos de ranking: /trofeos (el jugador los equipa ahi).']
    return '\n'.join(lines) + '\n'


ITEM_NOMBRE = {'chispa_astral': 'Chispa Astral', 'chispa_astral_pl': 'Chispas Astrales', 'gema_luminica': 'Gema Luminica', 'barril_xp': 'Barril de XP',
               'manzana_esmeralda': 'Manzana Esmeralda'}


def premio_texto(pos):
    """Resumen corto del premio de un puesto (para el aviso al entrar a la zona)."""
    partes = [f'{PLATA[pos]:,}$'.replace(',', '.')]
    partes += [f'{n} {"tiradas" if n > 1 else "tirada"} {"Cosmeticos" if g == "gacha_cosmeticos" else "RPG"}' for g, n in TIRADAS[pos]]
    for item, n in ITEMS[pos]:
        if item in ITEM_NOMBRE:
            partes.append(f'{n} {ITEM_NOMBRE.get(item + "_pl", ITEM_NOMBRE[item])}' if n > 1 else ITEM_NOMBRE[item])
    partes.append('frascos de XP')
    partes.append('titulo exclusivo')
    if pos == 1:
        partes.append('Aura de Campeon')
    return ', '.join(partes)


def zonas():
    """Mundo -> ranking, para el aviso al entrar (23/11: pedido del dueno)."""
    from santuario_azeroth import WORLD as SANT
    z = {d['world']: f'parkour_{pid}' for pid, d in llegadas().items()}
    z['astral_minas'] = 'minas'
    z['astral_bosque'] = 'bosque'
    for base, rid in (('infinita', 'infinita'), (SANT, 'trainx')):
        z[base] = rid
        z.update({f'{base}_{i}': rid for i in range(2, 7)})
    return z


def aviso_zonas():
    mundos = '\n'.join(f'    if {{_w}} is "{w}":\n        set {{_r}} to "{r}"' for w, r in zonas().items())
    premios = '\n'.join(f'    send "{COLOR_PUESTO[p]}{p}° &7{premio_texto(p)}" to {{_p}}' for p in (1, 2, 3))
    return f'''function rk_aviso(p: player):
    set {{_w}} to name of world of {{_p}}
{mundos}
    {{_r}} is set
    # Solo al entrar a la zona (cada vez que entra), nunca repetido mientras esta adentro.
    send " " to {{_p}}
    send "&6&l✦ Ranking semanal: &e&l%rk_nombre({{_r}})%" to {{_p}}
    rk_resumen({{_p}}, {{_r}})
    send "&7Cierra cada lunes 00:00. Premios para los 3 primeros:" to {{_p}}
{premios}
    if {{_r}} starts with "parkour_":
        send "&6✦ &7El 1° de cada parkour gana ademas la mascota &f&lFenix&7." to {{_p}}
    send "&7Mira todos con &f/ranking &7y tus titulos con &f/trofeos&7." to {{_p}}
'''


def trofeos_lineas():
    color = {'&6': 'gold', '&7': 'gray', '&c': 'red', '&e&l': 'yellow'}
    out = []
    for k, (n, c) in titulos().items():
        js = (f"[{{text:'  «{n}» ',color:'{color[c]}'}},"
              f"{{text:'[Equipar]',color:'green',click_event:{{action:'run_command',command:'/trofeos {k}'}}}}]")
        out += [f'        if player has permission "astral.ranking.titulo.{k}":',
                '            add 1 to {_c}',
                f'            execute console command "tellraw %name of player% {js}"']
    return chr(10).join(out)


def skript():
    ids = [r[0] for r in RANKINGS]
    nombres = '\n'.join(f'    if {{_r}} is "{rid}":\n        return "{n}"' for rid, n, _, _ in RANKINGS)
    menor = '\n'.join(f'    if {{_r}} is "{rid}":\n        return true' for rid, _, o, _ in RANKINGS if o == 'menor')
    tit = '\n'.join(f'    if {{_r}} is "{rid}":\n' + '\n'.join(
        f'        if {{_pos}} is {i + 1}:\n            return "{names[i].lower().replace(" ", "_")}"' for i in range(3))
        for rid, _, _, names in RANKINGS)
    tit_txt = '\n'.join(f'    if {{_k}} is "{k}":\n        return "{c}«{n}»"' for k, (n, c) in titulos().items())
    lleg = llegadas()
    pk_entrar = '\n'.join(
        f'    if {{_w}} is "{d["world"]}":\n        set {{-rk.pk::%uuid of {{_p}}%}} to "parkour_{pid}"\n'
        f'        set {{-rk.ini::%uuid of {{_p}}%}} to location({d["arrival"][0]}, {d["arrival"][1]}, {d["arrival"][2]}, world of {{_p}})'
        for pid, d in lleg.items())
    premios = []
    for pos in (1, 2, 3):
        cmd = [f'        execute console command "eco give %{{_n}}% {PLATA[pos]}"']
        for gid, n in TIRADAS[pos]:
            cmd += [f'        execute console command "crates give virtual {gid} {n} %{{_n}}% -s"',
                    f'        wait 1 second',
                    f'        execute console command "sudo %{{_n}}% crates mass-open {gid} virtual {n}"',
                    '        wait 8 seconds']
        for item, n in ITEMS[pos]:
            cmd += [f'        execute console command "loot give %{{_n}}% loot astral:item/{item}"'] * n
        cmd += [f'        execute console command "lp user %{{_n}}% permission settemp auraskills.multiplier.{XP_EXTRA[pos]} true {DIAS_EXTRA}d replace"',
                f'        send "&b✦ +{XP_EXTRA[pos]}%% de experiencia de skills por {DIAS_EXTRA} dias." to {{_p}}']
        premios.append(f'    if {{_pos}} is {pos}:\n' + '\n'.join(cmd))
    premios = '\n'.join(premios)
    campeones = '\n'.join(
        f'    if {{astral.rk.campeon::{rid}}} is set:\n        add 1 to {{_i}}\n'
        f'        set {{_t}} to "%{{_t}}%,{{text:\'{n}: \',color:\'yellow\'}},{{text:\'%{{astral.rk.campeon::{rid}}}%\\n\',color:\'white\'}}"'
        for rid, n, _, _ in RANKINGS)
    plata_txt = ', '.join(f'{p}°: {PLATA[p]:,}$'.replace(',', '.') for p in (1, 2, 3))
    return f'''# Generado por datapack-src/rankings.py. No editar a mano (docs/DESEOS_Y_RANKINGS.md).
# Rankings semanales: parkour, Infinita, Santuario, Minas y Bosque. Cierre: lunes 00:00 (Argentina).

# ------------------------------------------------------------------ utilidades
function rk_nombre(r: text) :: text:
{nombres}
    return {{_r}}

function rk_menor(r: text) :: boolean:
{menor}
    return false

# Semana que empieza el lunes 00:00 en Argentina (UTC-3). El 05/01/1970 fue lunes.
function rk_semana() :: number:
    return floor(((unix timestamp of now) - 10800 - 345600) / 604800)

function rk_tiempo(s: number) :: text:
    set {{_m}} to floor({{_s}} / 60)
    set {{_r}} to {{_s}} - {{_m}} * 60
    set {{_d}} to floor({{_r}} * 10) / 10
    if {{_d}} < 10:
        return "%{{_m}}%:0%{{_d}}%"
    return "%{{_m}}%:%{{_d}}%"

function rk_valor(r: text, v: number) :: text:
    if rk_menor({{_r}}) is true:
        return rk_tiempo({{_v}})
    if {{_r}} is "infinita":
        set {{_t}} to floor({{_v}} / 100)
        set {{_x}} to {{_v}} - {{_t}} * 100
        if {{_t}} >= 11:
            if {{_x}} > 0:
                return "Tier X+ (+%{{_x}}%)"
            return "Tier X+"
        return "Tier %{{_t}}%"
    return "%{{_v}}%"

# Guarda el mejor valor de la semana y el record historico.
function rk_mejor(p: player, r: text, v: number):
    set {{_id}} to uuid of {{_p}}
    set {{astral.rk.nom::%{{_id}}%}} to name of {{_p}}
    set {{_old}} to {{astral.rk.sem::%{{_r}}%::%{{_id}}%}}
    if {{_old}} is set:
        if rk_menor({{_r}}) is true:
            if {{_v}} >= {{_old}}:
                stop
        else:
            if {{_v}} <= {{_old}}:
                stop
    set {{astral.rk.sem::%{{_r}}%::%{{_id}}%}} to {{_v}}
    rk_record({{_r}}, {{_v}}, name of {{_p}})

function rk_record(r: text, v: number, quien: text):
    set {{_old}} to {{astral.rk.rec::%{{_r}}%}}
    if {{_old}} is set:
        if rk_menor({{_r}}) is true:
            if {{_v}} >= {{_old}}:
                stop
        else:
            if {{_v}} <= {{_old}}:
                stop
    set {{astral.rk.rec::%{{_r}}%}} to {{_v}}
    set {{astral.rk.recnom::%{{_r}}%}} to {{_quien}}
    broadcast "&6✦ Nuevo record de &e%rk_nombre({{_r}})%&6: &f%{{_quien}}% &7(%rk_valor({{_r}}, {{_v}})%)"

# Suma (minas y bosque). Lo llaman astral_minas.sk y astral_bosque.sk.
function rk_sumar(p: player, r: text, n: number):
    set {{_id}} to uuid of {{_p}}
    set {{astral.rk.nom::%{{_id}}%}} to name of {{_p}}
    add {{_n}} to {{astral.rk.sem::%{{_r}}%::%{{_id}}%}}

# Lo llama astral_renacimiento.sk cuando muere Trainx: el grupo entero comparte el tiempo.
function rk_trainx(seg: number, ps: players):
    loop {{_ps::*}}:
        add name of loop-value to {{_n::*}}
    add 1 to {{astral.rk.grupos}}
    set {{_k}} to "g%{{astral.rk.grupos}}%"
    set {{astral.rk.sem::trainx::%{{_k}}%}} to {{_seg}}
    set {{astral.rk.nom::%{{_k}}%}} to join {{_n::*}} with ", "
    loop {{_ps::*}}:
        add "%uuid of loop-value%" to {{astral.rk.grupo::%{{_k}}%::*}}
    rk_record("trainx", {{_seg}}, join {{_n::*}} with ", ")
    loop {{_ps::*}}:
        send "&5✦ Tiempo contra Trainx: &f%rk_tiempo({{_seg}})%" to loop-value

# Top N de la semana: claves (uuid, o grupo para Trainx) ordenadas.
function rk_top(r: text, n: number) :: texts:
    loop {{astral.rk.sem::%{{_r}}%::*}}:
        set {{_v::%loop-index%}} to loop-value
    set {{_menor}} to rk_menor({{_r}})
    loop {{_n}} times:
        delete {{_bk}}
        delete {{_bv}}
        loop {{_v::*}}:
            set {{_x}} to loop-value-2
            set {{_xk}} to loop-index
            if {{_bk}} is not set:
                set {{_bk}} to {{_xk}}
                set {{_bv}} to {{_x}}
            else if {{_menor}} is true:
                if {{_x}} < {{_bv}}:
                    set {{_bk}} to {{_xk}}
                    set {{_bv}} to {{_x}}
            else if {{_x}} > {{_bv}}:
                set {{_bk}} to {{_xk}}
                set {{_bv}} to {{_x}}
        {{_bk}} is set
        add {{_bk}} to {{_out::*}}
        delete {{_v::%{{_bk}}%}}
    return {{_out::*}}

# ------------------------------------------------------------------ carteles
function rk_cartel_campeones():
    set {{_t}} to "['',{{text:'✦ Campeones de la semana ✦\\n',color:'gold',bold:true}},{{text:'Ganadores del ultimo cierre\\n',color:'gray'}}"
    set {{_i}} to 0
{campeones}
    if {{_i}} is 0:
        set {{_t}} to "%{{_t}}%,{{text:'Todavia no hubo cierre.\\n',color:'gray',italic:true}}"
    set {{_t}} to "%{{_t}}%]"
    execute console command "execute as @e[type=text_display,tag=astral_rank_campeones] run data merge entity @s {{text:%{{_t}}%}}"

function rk_cartel(r: text):
    if {{_r}} is "campeones":
        rk_cartel_campeones()
        stop
    set {{_t}} to "['',{{text:'✦ %rk_nombre({{_r}})% ✦\\n',color:'gold',bold:true}},{{text:'Top 10 de la semana\\n',color:'gray'}}"
    set {{_top::*}} to rk_top({{_r}}, 10)
    set {{_i}} to 0
    loop {{_top::*}}:
        add 1 to {{_i}}
        set {{_c}} to "white"
        if {{_i}} is 1:
            set {{_c}} to "gold"
        else if {{_i}} is 2:
            set {{_c}} to "#d8d8e8"
        else if {{_i}} is 3:
            set {{_c}} to "#e08a50"
        set {{_v}} to rk_valor({{_r}}, {{astral.rk.sem::%{{_r}}%::%loop-value%}})
        set {{_t}} to "%{{_t}}%,{{text:'%{{_i}}%. %{{astral.rk.nom::%loop-value%}}%  ',color:'%{{_c}}%'}},{{text:'%{{_v}}%\\n',color:'aqua'}}"
    if {{_i}} is 0:
        set {{_t}} to "%{{_t}}%,{{text:'Nadie todavia. ¡Se el primero!\\n',color:'gray',italic:true}}"
    if {{astral.rk.rec::%{{_r}}%}} is set:
        set {{_t}} to "%{{_t}}%,{{text:'Record: %{{astral.rk.recnom::%{{_r}}%}}% (%rk_valor({{_r}}, {{astral.rk.rec::%{{_r}}%}})%)\\n',color:'light_purple'}}"
    if {{_r}} starts with "parkour_":
        if {{astral.rk.meta::%{{_r}}%}} is not set:
            set {{_t}} to "%{{_t}}%,{{text:'Meta sin fijar\\n',color:'red'}}"
    set {{_falta}} to ((rk_semana() + 1) * 604800 + 345600 + 10800) - unix timestamp of now
    set {{_d}} to floor({{_falta}} / 86400)
    set {{_h}} to floor(({{_falta}} - {{_d}} * 86400) / 3600)
    set {{_t}} to "%{{_t}}%,{{text:'Premios: top 3 · cierra en %{{_d}}%d %{{_h}}%h',color:'yellow'}}]"
    execute console command "execute as @e[type=text_display,tag=astral_rank_%{{_r}}%] run data merge entity @s {{text:%{{_t}}%}}"

every 30 seconds:
{chr(10).join(f'    rk_cartel("{rid}")' for rid in ids)}
    rk_cartel_campeones()

# ------------------------------------------------------------------ parkour
function rk_pk_entrar(p: player):
    delete {{-rk.pk::%uuid of {{_p}}%}}
    delete {{-rk.t0::%uuid of {{_p}}%}}
    set {{_w}} to name of world of {{_p}}
{pk_entrar}

on world change:
    wait 5 ticks
    rk_pk_entrar(player)
    wait 2 seconds
    player is online
    rk_aviso(player)

on join:
    wait 2 seconds
    rk_pk_entrar(player)

{aviso_zonas()}

every 5 ticks:
    loop all players:
        set {{_id}} to uuid of loop-player
        set {{_r}} to {{-rk.pk::%{{_id}}%}}
        {{_r}} is set
        set {{_ini}} to {{-rk.ini::%{{_id}}%}}
        if world of loop-player is not world of {{_ini}}:
            rk_pk_entrar(loop-player)
        else if {{-rk.t0::%{{_id}}%}} is not set:
            # Esperando: arranca al alejarse 3 bloques de la llegada.
            if distance between loop-player and {{_ini}} > 3:
                if gamemode of loop-player is adventure or survival:
                    set {{-rk.t0::%{{_id}}%}} to unix timestamp of now
                    send action bar "&a⏱ ¡Largaste!" to loop-player
        else if {{-rk.t0::%{{_id}}%}} is not "fin":
            set {{_s}} to (unix timestamp of now) - {{-rk.t0::%{{_id}}%}}
            if gamemode of loop-player is creative or spectator:
                delete {{-rk.t0::%{{_id}}%}}
                send "&cTiempo anulado (modo de juego)." to loop-player
            else if loop-player is flying:
                delete {{-rk.t0::%{{_id}}%}}
                send "&cTiempo anulado (volando)." to loop-player
            else:
                send action bar "&e⏱ %rk_tiempo({{_s}})%" to loop-player
                set {{_meta}} to {{astral.rk.meta::%{{_r}}%}}
                if {{_meta}} is set:
                    if world of {{_meta}} is world of loop-player:
                        if distance between loop-player and {{_meta}} < 2.5:
                            delete {{-rk.t0::%{{_id}}%}}
                            send title "&6&l¡Meta!" with subtitle "&f%rk_tiempo({{_s}})%" to loop-player for 3 seconds
                            play sound "ui.toast.challenge_complete" to loop-player
                            set {{_old}} to {{astral.rk.sem::%{{_r}}%::%{{_id}}%}}
                            rk_mejor(loop-player, {{_r}}, {{_s}})
                            if {{_old}} is not set:
                                send "&6✦ Tu tiempo quedo en el ranking de la semana: &f%rk_tiempo({{_s}})%" to loop-player
                            else if {{_s}} < {{_old}}:
                                send "&6✦ ¡Mejoraste tu tiempo! &f%rk_tiempo({{_s}})% &7(antes %rk_tiempo({{_old}})%)" to loop-player
                            else:
                                send "&7Tu mejor tiempo de la semana sigue siendo &f%rk_tiempo({{_old}})%&7." to loop-player
                            send "&7Volve a la llegada para correr otra vez." to loop-player
                            set {{-rk.t0::%{{_id}}%}} to "fin"

# Despues de la meta: volver a la llegada habilita otra corrida.
every 1 second:
    loop all players:
        {{-rk.t0::%uuid of loop-player%}} is "fin"
        set {{_ini}} to {{-rk.ini::%uuid of loop-player%}}
        world of loop-player is world of {{_ini}}
        distance between loop-player and {{_ini}} < 2
        delete {{-rk.t0::%uuid of loop-player%}}

# ------------------------------------------------------------------ Mazmorra Infinita
every 5 seconds:
    loop all players:
        set {{_n}} to name of world of loop-player
        {{-inf.tier::%{{_n}}%}} is set
        gamemode of loop-player is survival or adventure
        set {{_sg}} to {{-inf.seg::%{{_n}}%}} ? 0
        {{_sg}} >= 120
        rk_mejor(loop-player, "infinita", {{-inf.tier::%{{_n}}%}} * 100 + ({{-inf.plus::%{{_n}}%}} ? 0))

# ------------------------------------------------------------------ comandos
command /ranking [<text>] [<text>]:
    trigger:
        if arg-1 is "meta":
            player has permission "astral.admin.ranking"
            set {{astral.rk.meta::%arg-2%}} to location of player
            send "&aMeta de &f%arg-2% &aguardada aca." to player
            stop
        if arg-1 is "cartel":
            player has permission "astral.admin.ranking"
            # Solo el cartel de ese id en el mundo donde esta el jugador (el de Trainx tambien esta en el Santuario).
            execute console command "execute as %uuid of player% at @s run minecraft:kill @e[type=text_display,tag=astral_rank_%arg-2%,distance=0..]"
            execute console command "execute as %uuid of player% at @s run summon text_display ~ ~2.2 ~ {{Tags:['astral_rank','astral_rank_%arg-2%'],billboard:'center',alignment:'center',line_width:240,background:1711276032,text:{{text:'Ranking',color:'gold'}}}}"
            rk_cartel(arg-2)
            send "&aCartel de &f%arg-2% &apuesto aca (se borro el anterior)." to player
            stop
        if arg-1 is "reiniciar":
            # Todo a 0 sin dar premios (tambien desde consola: ranking reiniciar).
            sender has permission "astral.admin.ranking"
            rk_borrar_puntajes()
            delete {{astral.rk.historial::*}}
            delete {{astral.rk.campeon::*}}
            delete {{astral.rk.premio::*}}
            set {{astral.rk.semana}} to rk_semana()
            send "&aRankings reiniciados: todo en 0." to sender
            stop
        if arg-1 is "cerrar":
            player has permission "astral.admin.ranking"
            rk_cerrar()
            stop
        send "&6&l--- Rankings de la semana ---" to player
{chr(10).join(f'        rk_resumen(player, "{rid}")' for rid in ids)}
        send "&7Premios cada lunes al top 3 ({plata_txt}, tiradas, Chispas y titulos exclusivos: &f/trofeos&7)." to player

function rk_resumen(p: player, r: text):
    set {{_top::*}} to rk_top({{_r}}, 3)
    set {{_l}} to "&e%rk_nombre({{_r}})%&7:"
    set {{_i}} to 0
    loop {{_top::*}}:
        add 1 to {{_i}}
        set {{_l}} to "%{{_l}}% &f%{{_i}}%. %{{astral.rk.nom::%loop-value%}}% &b(%rk_valor({{_r}}, {{astral.rk.sem::%{{_r}}%::%loop-value%}})%)"
    if {{_i}} is 0:
        set {{_l}} to "%{{_l}}% &8nadie todavia"
    send {{_l}} to {{_p}}

# ------------------------------------------------------------------ cierre semanal y premios
every 1 minute:
    {{astral.rk.semana}} is not rk_semana()
    if {{astral.rk.semana}} is not set:
        set {{astral.rk.semana}} to rk_semana()
        stop
    rk_cerrar()

function rk_titulo(r: text, pos: number) :: text:
{tit}
    return ""

function rk_cerrar():
    set {{astral.rk.semana}} to rk_semana()
    broadcast "&6&l✦ Cierre semanal de los rankings ✦"
{chr(10).join(f'    rk_cerrar_uno("{rid}")' for rid in ids)}
    rk_borrar_puntajes()

# 23/11: al cerrar todo vuelve a 0 (puntajes de la semana, grupos y record), no queda nada de la semana anterior.
function rk_borrar_puntajes():
    delete {{astral.rk.sem::*}}
    delete {{astral.rk.grupo::*}}
    delete {{astral.rk.rec::*}}
    delete {{astral.rk.recnom::*}}
    delete {{astral.rk.nom::*}}
    set {{astral.rk.grupos}} to 0

function rk_cerrar_uno(r: text):
    set {{_top::*}} to rk_top({{_r}}, 3)
    set {{_pos}} to 0
    loop {{_top::*}}:
        add 1 to {{_pos}}
        set {{_k}} to loop-value
        broadcast "&e%rk_nombre({{_r}})% &7%{{_pos}}%°: &f%{{astral.rk.nom::%{{_k}}%}}% &b(%rk_valor({{_r}}, {{astral.rk.sem::%{{_r}}%::%{{_k}}%}})%)"
        add "%rk_semana()%: %rk_nombre({{_r}})% %{{_pos}}%° %{{astral.rk.nom::%{{_k}}%}}%" to {{astral.rk.historial::*}}
        if {{_pos}} is 1:
            set {{astral.rk.campeon::%{{_r}}%}} to {{astral.rk.nom::%{{_k}}%}}
        if {{_r}} is "trainx":
            loop {{astral.rk.grupo::%{{_k}}%::*}}:
                rk_premio_pendiente(loop-value-2, {{_r}}, {{_pos}})
        else:
            rk_premio_pendiente({{_k}}, {{_r}}, {{_pos}})

function rk_premio_pendiente(u: text, r: text, pos: number):
    add "%{{_r}}%|%{{_pos}}%" to {{astral.rk.premio::%{{_u}}%::*}}
    loop all players:
        "%uuid of loop-player%" is {{_u}}
        rk_entregar(loop-player)

on join:
    wait 8 seconds
    player is online
    rk_entregar(player)

function rk_entregar(p: player):
    set {{_id}} to uuid of {{_p}}
    set {{_n}} to name of {{_p}}
    loop {{astral.rk.premio::%{{_id}}%::*}}:
        add loop-value to {{_lista::*}}
    delete {{astral.rk.premio::%{{_id}}%::*}}
    loop {{_lista::*}}:
        set {{_parts::*}} to loop-value split at "|"
        set {{_r}} to {{_parts::1}}
        set {{_pos}} to {{_parts::2}} parsed as integer
        send "&6&l✦ Premio de ranking: &e%rk_nombre({{_r}})% &6%{{_pos}}%° puesto" to {{_p}}
        play sound "ui.toast.challenge_complete" to {{_p}}
        set {{_t}} to rk_titulo({{_r}}, {{_pos}})
        execute console command "lp user %{{_n}}% permission set astral.ranking.titulo.%{{_t}}% true"
        send "&7Titulo exclusivo desbloqueado: %rk_titulo_texto({{_t}})% &7(equipalo con &f/trofeos&7)" to {{_p}}
        if {{_pos}} is 1:
            execute console command "lp user %{{_n}}% permission set astral.ranking.aura true"
            execute console command "lp user %{{_n}}% permission settemp astral.ranking.titulo.{TITULO_SEMANA[0]} true {DIAS_EXTRA}d replace"
            send "&7Titulo de {DIAS_EXTRA} dias: &e&l«{TITULO_SEMANA[1]}» &7(&f/trofeos&7)." to {{_p}}
            send "&7Cosmetico exclusivo: &d&lAura de Campeon &7(&f/trofeos aura&7)." to {{_p}}
            if {{_r}} starts with "parkour_":
                if {{_p}} has permission "astral.mascota.{MASCOTA_PARKOUR}":
                    execute console command "crates give virtual gacha_monturas 10 %{{_n}}% -s"
                    wait 1 second
                    execute console command "sudo %{{_n}}% crates mass-open gacha_monturas virtual 10"
                    wait 8 seconds
                else:
                    execute console command "lp user %{{_n}}% permission set astral.mascota.{MASCOTA_PARKOUR} true"
                    send "&6✦ Mascota rara: &f&lFenix&6. Llamala desde &f/mascotas&6." to {{_p}}
        rk_premio({{_p}}, {{_n}}, {{_pos}})

function rk_premio(p: player, n: text, pos: number):
{premios}

# ------------------------------------------------------------------ trofeos: titulos y aura
function rk_titulo_texto(k: text) :: text:
{tit_txt}
    return {{_k}}

command /trofeos [<text>]:
    executable by: players
    trigger:
        if arg-1 is "aura":
            if player does not have permission "astral.ranking.aura":
                send "&7El &d&lAura de Campeon &7se gana saliendo 1° en un ranking semanal." to player
                stop
            if {{astral.rk.aura::%uuid of player%}} is set:
                delete {{astral.rk.aura::%uuid of player%}}
                send "&7Aura apagada." to player
            else:
                set {{astral.rk.aura::%uuid of player%}} to true
                send "&dAura de Campeon encendida." to player
            stop
        if arg-1 is set:
            if player does not have permission "astral.ranking.titulo.%arg-1%":
                send "&cTodavia no ganaste ese titulo." to player
                stop
            execute console command "lp user %name of player% meta setprefix 100 ""%rk_titulo_texto(arg-1)%"""
            set {{astral.rk.equipado::%uuid of player%}} to arg-1
            send "&aTitulo equipado: %rk_titulo_texto(arg-1)%" to player
            stop
        send "&6&l--- Tus trofeos ---" to player
        set {{_c}} to 0
{trofeos_lineas()}
        if {{_c}} is 0:
            send "&7Todavia no tenes titulos de ranking. Se ganan cada lunes en el top 3 de &f/ranking&7." to player
        if player has permission "astral.ranking.aura":
            send "&d✦ Aura de Campeon: &f/trofeos aura &7(prender o apagar)" to player

every 1 minute:
    loop all players:
        {{astral.rk.equipado::%uuid of loop-player%}} is "{TITULO_SEMANA[0]}"
        loop-player does not have permission "astral.ranking.titulo.{TITULO_SEMANA[0]}"
        delete {{astral.rk.equipado::%uuid of loop-player%}}
        execute console command "lp user %name of loop-player% meta removeprefix 100"
        send "&7Tu titulo &e&l«{TITULO_SEMANA[1]}» &7vencio." to loop-player

every 10 ticks:
    loop all players:
        {{astral.rk.aura::%uuid of loop-player%}} is set
        loop-player has permission "astral.ranking.aura"
        gamemode of loop-player is not spectator
        execute console command "execute at %name of loop-player% run particle minecraft:end_rod ~ ~0.2 ~ 0.4 0 0.4 0.01 3"
        execute console command "execute at %name of loop-player% run particle minecraft:dust{{color:[1.0,0.82,0.3],scale:0.8}} ~ ~1 ~ 0.35 0.6 0.35 0 2"
'''


def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'astral_rankings.sk').write_text(skript(), encoding='utf-8')
    (OUT / 'comandos.txt').write_text(comandos(), encoding='utf-8')
    print('rankings:', OUT / 'astral_rankings.sk')


if __name__ == '__main__':
    generate()
