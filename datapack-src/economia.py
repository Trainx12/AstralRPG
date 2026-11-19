# -*- coding: utf-8 -*-
"""Economia de AstralRPG estilo Hypixel (plan E1, 18/11/2026).

TODAS las cifras de plata del server salen de aca. Los generadores importan `plata()` (x ESCALA)
o las tablas fijas de abajo; no escribir numeros de plata sueltos en otros archivos
(test_economia.py recorre build/ y lo controla).

Salida de este archivo (python economia.py):
  build/economia/Skript/scripts/astral_economia.sk   pagos de mobs, perdida al morir, Banco, rebase x100
  build/shop/EconomyShopGUI/shops/...                 tienda vanilla x100 (fuente: economia_tienda/)
  datapack-src/services_catalog.json                  vista previa de Venta rapida (precio POR UNIDAD)
"""
import json
import os
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'build' / 'economia'
TIENDA_SRC = HERE / 'economia_tienda' / 'shops'
TIENDA_OUT = ROOT / 'build' / 'shop' / 'EconomyShopGUI' / 'shops'

# ------------------------------------------------------------------ escala general
ESCALA = 100


def plata(n):
    """Cifra vieja -> cifra nueva (x ESCALA). Enteros cuando se puede."""
    v = round(n * ESCALA, 2)
    return int(v) if v == int(v) else v


def texto(n):
    """1.000.000$"""
    n = int(n) if n == int(n) else n
    return f'{n:,}'.replace(',', '.') + '$'


def corto(n):
    """30k / 1,2M / 2,5B (para texturas y carteles chicos)."""
    for div, suf in ((1_000_000_000, 'B'), (1_000_000, 'M'), (1_000, 'k')):
        if n >= div:
            v = n / div
            s = f'{v:.2f}'.rstrip('0').rstrip('.') if v < 100 else str(round(v))
            return s.replace('.', ',') + suf
    return str(int(n))


# ------------------------------------------------------------------ mobs
# Mobs Astral del survival (mythic.py): pagan segun el tier que les toco (mob/roll).
PLATA_MOB_TIER = {1: 1_500, 2: 3_000, 3: 6_000, 4: 12_000, 5: 25_000}
for _t in range(6, 11):
    PLATA_MOB_TIER[_t] = PLATA_MOB_TIER[_t - 1] * 2
# Multiplicador por categoria. 'jefe' = jefes del mundo (Momia, Yeti...): x50 como antes (15 -> 750).
MULT_MOB = {'hostil': 1, 'elite': 10, 'jefe': 50, 'ancestral': 100}

# Mazmorras (tier = escala.TIER_MAZMORRA del mundo). Cada mob de oleada al que lo mata;
# el jefe a cada participante vivo (no espectador) en la sala.
OLEADA_TIER = {1: 300, 2: 800, 3: 2_000, 4: 4_500, 5: 10_000}
JEFE_MAZMORRA_TIER = {1: 100_000, 2: 300_000, 3: 800_000, 4: 2_000_000, 5: 5_000_000}
ELITE_OLEADA = 10            # elite dentro de una mazmorra = 10 mobs de oleada
ECO_SANTUARIO = 3_000_000    # cada eco del Santuario, a cada participante
RADIO_PARTICIPANTES = 64

# ------------------------------------------------------------------ puntaje de mazmorras (plan E2, 18/11)
# Notas de peor a mejor; el numero es el que se guarda en el puntaje astral.nota (0 = sin nota).
NOTAS = ['F', 'D', 'C', 'B', 'A', 'S']
NOTA_MIN = {'S': 95, 'A': 85, 'B': 70, 'C': 55, 'D': 40, 'F': 0}
NOTA_COLOR = {'S': '&6', 'A': '&a', 'B': '&b', 'C': '&e', 'D': '&c', 'F': '&4'}
PUNTOS_MUERTE, PUNTOS_MUERTE_TOPE = 12, 60
PUNTOS_MINUTO, PUNTOS_MINUTO_TOPE = 4, 40
PUNTOS_SIN_MUERTES = 10
# Minutos objetivo desde que la party entra hasta que muere el jefe (estimados por cantidad de salas y oleadas).
# Para ajustar: mirar el tiempo que muestra el chat al ganar ("Tiempo: X min") y poner aca lo que tarda una
# party normal. Despues: python mazmorras_puntaje.py y subir astral_puntaje.sk (sk reload).
TIEMPO_OBJETIVO = {'bosque': 12, 'mina': 10, 'tumba': 14, 'cumbre': 12, 'forja': 10, 'santuario': 15, 'fosa': 10}


def puntos(muertes, segundos, objetivo_min):
    """Misma cuenta que astral_puntaje.sk (para las pruebas)."""
    p = 100 - min(PUNTOS_MUERTE * muertes, PUNTOS_MUERTE_TOPE)
    sobre = max(0, int((segundos - objetivo_min * 60) // 60))
    p -= min(PUNTOS_MINUTO * sobre, PUNTOS_MINUTO_TOPE)
    return p + (PUNTOS_SIN_MUERTES if muertes == 0 else 0)


def nota(p):
    return next(n for n in reversed(NOTAS) if p >= NOTA_MIN[n])


# Ruleta invisible de plata del cofre: min + (max - min) * u^k (u al azar). Sesgada a lo bajo: siempre puede tocar poco.
RULETA_MIN = 2_000
RULETA_MAX = {'F': 5_000, 'D': 30_000, 'C': 80_000, 'B': 150_000, 'A': 250_000, 'S': 500_000}   # tier I
RULETA_K = {'F': 3.0, 'D': 2.5, 'C': 2.0, 'B': 1.8, 'A': 1.6, 'S': 1.4}
RULETA_MULT_TIER = {1: 1, 2: 3, 3: 8, 4: 18, 5: 40}
RULETA_MULT_SANTUARIO = 60


def ruleta_mult(key, tier):
    return RULETA_MULT_SANTUARIO if key == 'santuario' else RULETA_MULT_TIER[tier]


def ruleta_esperanza(n, mult=1):
    lo, hi = RULETA_MIN * mult, RULETA_MAX[n] * mult
    return lo + (hi - lo) / (RULETA_K[n] + 1)


# Items del cofre: tiradas por nota y peso extra a lo raro con mejor nota (peso x (1 + bonus x rareza)).
ITEM_TIRADAS = {'F': 1, 'D': 1, 'C': 2, 'B': 2, 'A': 3, 'S': 3}
RAREZA_BONUS = {'F': 0, 'D': 0, 'C': 0.3, 'B': 0.6, 'A': 1.0, 'S': 1.6}
# Equipo del tier SIGUIENTE (premio especial): probabilidad por tirada, solo A y S.
ESPECIAL_PROB = {'A': 0.005, 'S': 0.015}
EQUIPO_FAMILIAS = ['espada', 'hacha', 'arco', 'baston', 'guadana', 'lanza', 'cuchillo', 'ballesta'] + \
    [f'{c}_{p}' for c in ('berserker', 'mago', 'arquero') for p in ('helmet', 'chestplate', 'leggings', 'boots')]
EQUIPO_BALLESTA = (3, 4, 5)
# (id, astral?, cantidad, peso, rareza 0-2, tier minimo, tier maximo)
POOL_EXTRA = [
    ('frasco_xp_pequeno', True, 2, 10, 0, 1, 3), ('frasco_xp_grande', True, 1, 8, 1, 2, 5),
    ('frasco_xp_gigante', True, 1, 4, 2, 4, 5), ('manzana_esmeralda', True, 1, 3, 2, 4, 5),
    ('barril_xp', True, 1, 1, 2, 5, 5),
    ('diamond', False, 2, 8, 1, 1, 3), ('diamond', False, 4, 6, 1, 4, 5), ('emerald', False, 4, 8, 0, 1, 5),
    ('golden_apple', False, 2, 6, 0, 1, 5), ('experience_bottle', False, 8, 8, 0, 1, 5),
    ('netherite_scrap', False, 1, 3, 2, 3, 5), ('totem_of_undying', False, 1, 2, 2, 3, 5),
    ('netherite_ingot', False, 1, 2, 2, 5, 5), ('enchanted_golden_apple', False, 1, 1, 2, 5, 5),
]


def equipo(tier):
    return [f'{f}_{tier}' if '_' not in f else f.replace('_', f'_{tier}_', 1) for f in EQUIPO_FAMILIAS
            if f != 'ballesta' or tier in EQUIPO_BALLESTA]


def pool(tier):
    """[(id, astral?, cantidad, peso, rareza)] del cofre de una mazmorra de ese tier."""
    from tanda5a import MATERIAL_TIERS
    out = []
    for mid, mt in sorted(MATERIAL_TIERS.items()):
        if mt <= tier + 1:
            r = max(0, mt - tier + 1)
            out.append((mid, True, 2 if r == 0 else 1, 10 if r < 2 else 4, r))
    out += [(i, a, n, w, r) for i, a, n, w, r, lo, hi in POOL_EXTRA if lo <= tier <= hi]
    return out


def pesos(tier, n):
    return [round(w * (1 + RAREZA_BONUS[n] * r) * 10) for _, _, _, w, r in pool(tier)]


# ------------------------------------------------------------------ Secretos de Astral (plan E3, 18/11)
# Ruleta invisible al reclamar un secreto: equipo +1 tier (muy raro), plata o premios del cofre.
SECRETO_PROB_EQUIPO = 0.02
SECRETO_PROB_PLATA = 0.38           # el resto (60%) son premios del pool de cofres del tier del jugador
SECRETO_PLATA_PCT = (0.05, 0.20)    # de la plata que lleva encima
SECRETO_PLATA_MIN, SECRETO_PLATA_MAX = 10_000, 5_000_000
SECRETO_TIRADAS = 2                 # tiradas de premios (con pesos de nota B)
SECRETO_NOTA_PESOS = 'B'


# ------------------------------------------------------------------ servicios
# Mejora del Herrero +1..+10 (mas empinado que x100: late game caro).
MEJORAS_PLATA = [30_000, 75_000, 150_000, 300_000, 600_000, 1_200_000, 2_500_000, 5_000_000, 10_000_000, 25_000_000]
GACHA_TIRADA = {'gacha_rpg': 100_000, 'gacha_monturas': 250_000, 'gacha_cosmeticos': 50_000}

# Reforja de gemas (plan E4 / 7d, 19/11/2026): engarzar = base por tier del equipo x multiplicador de la calidad.
# Reemplazar cuesta lo mismo que engarzar (la gema vieja se destruye). Extraer sin romperla cuesta x GEMA_EXTRAER_MULT.
GEMA_PONER_TIER = {1: 10_000, 2: 25_000, 3: 50_000, 4: 100_000, 5: 200_000,
                   6: 400_000, 7: 700_000, 8: 1_200_000, 9: 2_000_000, 10: 3_500_000}
GEMA_CALIDAD_MULT = {1: 1, 2: 2, 3: 4, 4: 8, 5: 15}     # Cruda, Pulida, Impecable, Perfecta, Estelar
GEMA_EXTRAER_MULT = 3


def gema_costo(tier, calidad, extraer=False):
    """Plata para engarzar (o extraer) una gema de esa calidad en un equipo de ese tier."""
    return GEMA_PONER_TIER[tier] * GEMA_CALIDAD_MULT[calidad] * (GEMA_EXTRAER_MULT if extraer else 1)

# Minas: todo x100 salvo la Netherita III.
NETHERITA_BLOQUE = 15_000
NETHERITA_APERTURA = 2_500_000_000

# ------------------------------------------------------------------ muerte
PERDIDA_MUERTE = 0.5
PERDIDA_ESPERA_SEG = 10      # la caida con party y el respawn no cobran dos veces


def mundos_con_perdida():
    """Survival, minas, bosque, oceano, mazmorras e Infinita. Lobby, arenas, duelos, parkour y
    mini juegos quedan afuera (no estan en la lista)."""
    from escala import TIER_MAZMORRA, TIER_FIJO
    from infinita import WORLDS as INFINITA
    import minas, bosque_talar, oceano
    w = ['world', 'world_nether', 'world_the_end', minas.WORLD, bosque_talar.WORLD, oceano.WORLD]
    w += list(TIER_MAZMORRA) + list(TIER_FIJO) + list(INFINITA)
    from instancias import bukkit   # nombre real en Bukkit (el Santuario lleva prefijo)
    return sorted({bukkit(x) for x in w})


def mundos_mazmorra():
    """Mundo -> tier para los pagos de oleada/jefe. Incluye la Fosa (jefe propio)."""
    from escala import TIER_MAZMORRA, TIER_FIJO
    m = dict(TIER_MAZMORRA)
    m.update({w: t for w, t in TIER_FIJO.items() if w.startswith('fosa')})
    from instancias import bukkit   # nombre real en Bukkit (el Santuario lleva prefijo)
    return {bukkit(w): t for w, t in m.items()}


# ------------------------------------------------------------------ banco
BANCO_INTERES = 0.02
BANCO_INTERES_MAX = 2_000_000
BANCO_HORAS = 24
# (nombre, limite de saldo, costo para subir a este nivel)
BANCO_NIVELES = [('Inicial', 50_000_000, 0), ('Oro', 100_000_000, 5_000_000),
                 ('Diamante', 250_000_000, 20_000_000), ('Esmeralda', 500_000_000, 60_000_000),
                 ('Astral', 1_000_000_000, 200_000_000)]
BANCO_TITULO = '&8Banco Astral'

# ------------------------------------------------------------------ tienda (EconomyShopGUI)
# Secciones propias que generan otros archivos (no se copian de la tienda vanilla).
TIENDA_PROPIAS = {'Consumibles.yml', 'Mochilas.yml', 'Oficios.yml', 'Peluches.yml', 'Proteccion.yml'}
# Cadenas de crafteo en dos sentidos: (bloque, unidad, cantidad).
CADENAS = [('coal_block', 'coal', 9), ('iron_block', 'iron_ingot', 9), ('gold_block', 'gold_ingot', 9),
           ('diamond_block', 'diamond', 9), ('emerald_block', 'emerald', 9), ('lapis_block', 'lapis_lazuli', 9),
           ('redstone_block', 'redstone', 9), ('copper_block', 'copper_ingot', 9), ('netherite_block', 'netherite_ingot', 9),
           ('raw_iron_block', 'raw_iron', 9), ('raw_gold_block', 'raw_gold', 9), ('raw_copper_block', 'raw_copper', 9),
           ('iron_ingot', 'iron_nugget', 9), ('gold_ingot', 'gold_nugget', 9), ('slime_block', 'slime_ball', 9),
           ('hay_block', 'wheat', 9), ('bone_block', 'bone_meal', 9), ('dried_kelp_block', 'dried_kelp', 9)]
# Topes de venta: lo que sale de las Minas no puede venderse en la tienda mas caro que en la mina
# (si no, el recorte de la Netherita no sirve).
NETHERITA_LINGOTE = NETHERITA_BLOQUE / 9
NETHERITA_EQUIPO = {f'netherite_{p}': f'diamond_{p}' for p in
                    ('helmet', 'chestplate', 'leggings', 'boots', 'sword', 'pickaxe', 'axe', 'shovel', 'hoe', 'spear')}


def _items_tienda(data):
    for page in ((data or {}).get('pages') or {}).values():
        for key, it in ((page or {}).get('items') or {}).items():
            if isinstance(it, dict) and 'material' in it:
                yield key, it


def _x(v):
    if v is None or v == -1:
        return v
    return plata(v)


def tienda():
    """Lee economia_tienda/shops (copia del server del 18/11) y devuelve {ruta: yaml} x100 con topes."""
    out = {}
    for f in sorted(TIENDA_SRC.rglob('*.yml')):
        rel = f.relative_to(TIENDA_SRC).as_posix()
        if rel in TIENDA_PROPIAS:
            continue
        data = yaml.safe_load(f.read_text(encoding='utf-8')) or {}
        for _, it in _items_tienda(data):
            for k in ('buy', 'sell'):
                if k in it:
                    it[k] = _x(it[k])
        out[rel] = data
    # Topes de la cadena de la Netherita (precio por paquete = por unidad x stack-size).
    sells = {}
    for data in out.values():
        for _, it in _items_tienda(data):
            s = it.get('sell')
            if s not in (None, -1):
                sells.setdefault(str(it['material']).lower(), s / (it.get('stack-size') or 1))
    tope = {'netherite_block': NETHERITA_BLOQUE, 'netherite_ingot': NETHERITA_LINGOTE}
    plantilla = sells.get('netherite_upgrade_smithing_template', 0)
    for neth, dia in NETHERITA_EQUIPO.items():
        if dia in sells:
            tope[neth] = sells[dia] + NETHERITA_LINGOTE + plantilla
    for data in out.values():
        for _, it in _items_tienda(data):
            mat = str(it['material']).lower()
            if mat in tope and it.get('sell') not in (None, -1):
                n = it.get('stack-size') or 1
                it['sell'] = round(min(it['sell'], tope[mat] * n), 2)
    return out


def catalogo(shops=None):
    """Vista previa de Venta rapida: precio de venta POR UNIDAD (divide por stack-size)."""
    shops = shops if shops is not None else tienda()
    cat = {}
    for data in shops.values():
        for _, it in _items_tienda(data):
            s = it.get('sell')
            if s in (None, -1):
                continue
            u = round(s / (it.get('stack-size') or 1), 2)
            m = str(it['material']).upper()
            c = cat.setdefault(m, {'min': u, 'max': u})
            c['min'], c['max'] = min(c['min'], u), max(c['max'], u)
    return dict(sorted(cat.items()))


# ------------------------------------------------------------------ Skript
def skript():
    from escala import TIER_MAZMORRA  # noqa: F401 (documenta la fuente de mundos_mazmorra)
    L = ['# Generado por datapack-src/economia.py (plan E1 18/11/2026). No editar a mano.',
         '# Pagos de mobs, perdida de plata al morir, Banco Astral y rebase x100 de saldos.',
         '',
         'options:',
         f'    radio: {RADIO_PARTICIPANTES}',
         f'    perdida: {PERDIDA_MUERTE}',
         f'    espera: {PERDIDA_ESPERA_SEG}',
         f'    eliteola: {ELITE_OLEADA}',
         f'    interes: {BANCO_INTERES}',
         f'    interesmax: {BANCO_INTERES_MAX}',
         f'    horas: {BANCO_HORAS}',
         f'    escala: {ESCALA}',
         f'    titulo: {BANCO_TITULO}',
         '',
         'on load:',
         '    delete {-eco.tiermaz::*}', '    delete {-eco.mob::*}', '    delete {-eco.mult::*}',
         '    delete {-eco.oleada::*}', '    delete {-eco.jefe::*}', '    delete {-eco.perdida::*}',
         '    delete {-eco.banco.nombre::*}', '    delete {-eco.banco.lim::*}', '    delete {-eco.banco.costo::*}']
    L += [f'    set {{-eco.tiermaz::{w}}} to {t}' for w, t in mundos_mazmorra().items()]
    L += [f'    set {{-eco.mob::{t}}} to {v}' for t, v in PLATA_MOB_TIER.items()]
    L += [f'    set {{-eco.mult::{c}}} to {v}' for c, v in MULT_MOB.items()]
    L += [f'    set {{-eco.oleada::{t}}} to {v}' for t, v in OLEADA_TIER.items()]
    L += [f'    set {{-eco.jefe::{t}}} to {v}' for t, v in JEFE_MAZMORRA_TIER.items()]
    L += [f'    set {{-eco.santuario}} to {ECO_SANTUARIO}']
    L += [f'    set {{-eco.perdida::{w}}} to true' for w in mundos_con_perdida()]
    for i, (nombre, lim, costo) in enumerate(BANCO_NIVELES, 1):
        L += [f'    set {{-eco.banco.nombre::{i}}} to "{nombre}"', f'    set {{-eco.banco.lim::{i}}} to {lim}',
              f'    set {{-eco.banco.costo::{i}}} to {costo}']
    L += [f'    set {{-eco.banco.max}} to {len(BANCO_NIVELES)}',
          '    if {astral.banco.proximo} is not set:',
          '        set {astral.banco.proximo} to {@horas} hours after now', '']
    L += [SK_CUERPO]
    return '\n'.join(L) + '\n'


SK_CUERPO = r'''
# ================================================================== pagos
function astral_eco_mult(p: player) :: number:
    return 1 + ({-renac::%uuid of {_p}%} ? 0)

# Gemas de Topacio (gemas.py, 7d): el plugin AstralGemas deja el % extra en binario (etiquetas astral.gp0..gp5)
# al revisar el equipo cada segundo. Aca solo se leen: ningun comando por baja.
function astral_eco_gema(p: player) :: number:
    set {_g} to 0
    set {_b} to 1
    loop 6 times:
        set {_tag} to "astral.gp%loop-number - 1%"
        if {_p} has the scoreboard tag {_tag}:
            add {_b} to {_g}
        set {_b} to {_b} * 2
    return {_g}

function astral_eco_valor(p: player, n: number) :: number:
    return floor({_n} * astral_eco_mult({_p}) * (1 + astral_eco_gema({_p}) / 100))

function astral_eco_dar(p: player, n: number):
    set {_v} to astral_eco_valor({_p}, {_n})
    set {-eco.ultimo::%uuid of {_p}%} to {_v}
    {_v} > 0
    add {_v} to balance of {_p}
    send action bar "&6+%{_v}%$" to {_p}

function astral_eco_participantes(p: player, n: number):
    loop all players in radius {@radio} around {_p}:
        world of loop-player is world of {_p}
        gamemode of loop-player is survival or adventure
        astral_eco_dar(loop-player, {_n})
        send "&6Recompensa del jefe: &e+%{-eco.ultimo::%uuid of loop-player%}%$" to loop-player

# Lo llaman los mobs de MythicMobs (mythic.py, mazmorra.py): astralplatamob <jugador> <categoria> [tier]
# categoria: hostil, elite, jefe, ancestral (o un numero fijo, ya en la escala nueva).
command /astralplatamob <text> <text> [<text>]:
    executable by: console
    trigger:
        set {_p} to arg-1 parsed as player
        {_p} is set
        set {_n} to arg-2 parsed as number
        if {_n} is set:
            astral_eco_dar({_p}, {_n})
            stop
        set {_c} to arg-2
        set {_t} to (arg-3 parsed as integer) ? 1
        if {_t} < 1:
            set {_t} to 1
        set {_w} to name of world of {_p}
        set {_tm} to {-eco.tiermaz::%{_w}%}
        if {_tm} is set:
            if {_c} is "ancestral":
                if {_w} contains "santuario":
                    astral_eco_participantes({_p}, {-eco.santuario})
                    stop
                set {_c} to "jefe"
            if {_c} is "jefe":
                astral_eco_participantes({_p}, {-eco.jefe::%{_tm}%})
            else if {_c} is "elite":
                astral_eco_dar({_p}, {-eco.oleada::%{_tm}%} * {@eliteola})
            else:
                astral_eco_dar({_p}, {-eco.oleada::%{_tm}%})
            stop
        set {_b} to {-eco.mob::%{_t}%} ? {-eco.mob::1}
        astral_eco_dar({_p}, {_b} * ({-eco.mult::%{_c}%} ? 1))

# Mobs vanilla de las oleadas (tag ad.vanilla): antes pagaban 0.
on death:
    victim is not a player
    attacker is a player
    scoreboard tags of victim contain "ad.vanilla"
    set {_tm} to {-eco.tiermaz::%name of world of victim%}
    {_tm} is set
    if scoreboard tags of victim contain "astral.elite":
        astral_eco_dar(attacker, {-eco.oleada::%{_tm}%} * {@eliteola})
    else:
        astral_eco_dar(attacker, {-eco.oleada::%{_tm}%})

# ================================================================== perdida al morir
function astral_eco_perder(p: player):
    set {_u} to uuid of {_p}
    if {-eco.perdio::%{_u}%} is set:
        if difference between {-eco.perdio::%{_u}%} and now is less than {@espera} seconds:
            stop
    set {-eco.perdio::%{_u}%} to now
    set {_b} to balance of {_p}
    {_b} > 0
    set {_l} to floor({_b} * {@perdida})
    {_l} > 0
    remove {_l} from balance of {_p}
    send "&c☠ Perdiste &e%{_l}%$ &c(la mitad de la plata que llevabas)." to {_p}
    send "&7Lo que guardes en el &6Banco Astral &7del lobby no se pierde." to {_p}

on death of player:
    {-eco.perdida::%name of world of victim%} is set
    astral_eco_perder(victim)

# Caida con party (AstralParty pasa al jugador a espectador sin evento de muerte).
on gamemode change to spectator:
    scoreboard tags of player contain "astral.party.fallen"
    {-eco.perdida::%name of world of player%} is set
    astral_eco_perder(player)

# ================================================================== Banco Astral
function astral_banco_nivel(p: offline player) :: number:
    return {astral.banco.nivel::%uuid of {_p}%} ? 1

function astral_banco_lim(p: offline player) :: number:
    return {-eco.banco.lim::%astral_banco_nivel({_p})%}

function astral_banco_saldo(p: offline player) :: number:
    return {astral.banco.saldo::%uuid of {_p}%} ? 0

function astral_banco_menu(p: player):
    set {_s} to astral_banco_saldo({_p})
    set {_n} to astral_banco_nivel({_p})
    set {_lim} to astral_banco_lim({_p})
    set {_i} to floor(min({_s} * {@interes}, {@interesmax}, {_lim} - {_s}))
    set {_falta} to difference between now and {astral.banco.proximo}
    set {_inv} to chest inventory with 5 rows named "{@titulo}"
    set slot 4 of {_inv} to gold block named "&6&lSaldo del Banco: &e%{_s}%$" with lore "&7Cuenta: &f%{-eco.banco.nombre::%{_n}%}% &7(limite &e%{_lim}%$&7)" and "&7Proximo interes: &a+%{_i}%$ &7en &f%{_falta}%" and "&8Interes: 2%% cada 24 h, hasta 2.000.000$." and "&8No se pierde al morir."
    set slot 10 of {_inv} to lime dye named "&a&lDepositar todo" with lore "&7Tu plata encima: &e%balance of {_p}%$"
    set slot 11 of {_inv} to lime dye named "&aDepositar la mitad"
    set slot 12 of {_inv} to oak sign named "&aDepositar una cantidad" with lore "&7La escribis en el chat."
    set slot 14 of {_inv} to red dye named "&c&lRetirar todo"
    set slot 15 of {_inv} to red dye named "&cRetirar la mitad"
    set slot 16 of {_inv} to oak sign named "&cRetirar una cantidad" with lore "&7La escribis en el chat."
    if {_n} < {-eco.banco.max}:
        set {_sig} to {_n} + 1
        set slot 31 of {_inv} to emerald named "&b&lMejorar cuenta: %{-eco.banco.nombre::%{_sig}%}%" with lore "&7Limite: &e%{-eco.banco.lim::%{_sig}%}%$" and "&7Costo: &e%{-eco.banco.costo::%{_sig}%}%$ &7(de tu plata encima)" and "" and "&eClic para mejorar."
    else:
        set slot 31 of {_inv} to nether star named "&d&lCuenta Astral" with lore "&7Ya tenes la mejor cuenta."
    set slot 36 of {_inv} to arrow named "&fVolver" with lore "&7A Subastas y Banco."
    set slot 40 of {_inv} to barrier named "&cCerrar"
    open {_inv} to {_p}
    set {-banco.gui::%uuid of {_p}%} to true

function astral_banco_mover(p: player, modo: text, v: number):
    set {_u} to uuid of {_p}
    set {_s} to astral_banco_saldo({_p})
    if {_modo} is "depositar":
        set {_v} to floor(min({_v}, balance of {_p}, astral_banco_lim({_p}) - {_s}))
        if {_v} < 1:
            send "&cNo hay plata para depositar, o tu cuenta llego al limite." to {_p}
            stop
        remove {_v} from balance of {_p}
        set {astral.banco.saldo::%{_u}%} to {_s} + {_v}
        send "&aDepositaste &e%{_v}%$&a. Saldo del banco: &e%{_s} + {_v}%$" to {_p}
    else:
        set {_v} to floor(min({_v}, {_s}))
        if {_v} < 1:
            send "&cNo tenes plata en el banco." to {_p}
            stop
        set {astral.banco.saldo::%{_u}%} to {_s} - {_v}
        add {_v} to balance of {_p}
        send "&aRetiraste &e%{_v}%$&a. Saldo del banco: &e%{_s} - {_v}%$" to {_p}
    log "%now% %name of {_p}% %{_u}% %{_modo}% %{_v}% saldo_antes=%{_s}%" to "astral-banco"
    play sound "block.chain.place" to {_p}

function astral_banco_mejorar(p: player):
    set {_n} to astral_banco_nivel({_p})
    if {_n} >= {-eco.banco.max}:
        stop
    set {_c} to {-eco.banco.costo::%{_n} + 1%}
    if balance of {_p} < {_c}:
        send "&cNecesitas &e%{_c}%$ &cencima para mejorar la cuenta." to {_p}
        stop
    remove {_c} from balance of {_p}
    set {astral.banco.nivel::%uuid of {_p}%} to {_n} + 1
    send "&b&lCuenta mejorada: &f%{-eco.banco.nombre::%{_n} + 1%}%&b. Nuevo limite: &e%{-eco.banco.lim::%{_n} + 1%}%$" to {_p}
    log "%now% %name of {_p}% %uuid of {_p}% mejora nivel=%{_n} + 1% costo=%{_c}%" to "astral-banco"
    play sound "entity.player.levelup" to {_p}

command /banco:
    executable by: players
    trigger:
        astral_banco_menu(player)

command /astralbanco <text> [<text>]:
    trigger:
        if sender is a player:
            if arg-1 is "abrir":
                astral_banco_menu(player)
            stop
        if arg-1 is "abrir":
            set {_p} to arg-2 parsed as player
            {_p} is set
            astral_banco_menu({_p})
            stop
        if arg-1 is "info":
            set {_o} to arg-2 parsed as offline player
            send "[Banco] %arg-2%: saldo %astral_banco_saldo({_o})%$, cuenta %{-eco.banco.nombre::%astral_banco_nivel({_o})%}%, limite %astral_banco_lim({_o})%$. Proximo interes: %{astral.banco.proximo}%" to sender
            stop
        send "Uso: astralbanco info <jugador> | astralbanco abrir <jugador>" to sender

on inventory click:
    {-banco.gui::%uuid of player%} is set
    cancel event
    clicked inventory is not player's inventory
    set {_slot} to index of event-slot
    if {_slot} is 40:
        close inventory of player
    else if {_slot} is 36:
        close inventory of player
        execute console command "dm open subastas_inicio %name of player%"
    else if {_slot} is 10:
        astral_banco_mover(player, "depositar", balance of player)
        astral_banco_menu(player)
    else if {_slot} is 11:
        astral_banco_mover(player, "depositar", balance of player / 2)
        astral_banco_menu(player)
    else if {_slot} is 14:
        astral_banco_mover(player, "retirar", astral_banco_saldo(player))
        astral_banco_menu(player)
    else if {_slot} is 15:
        astral_banco_mover(player, "retirar", astral_banco_saldo(player) / 2)
        astral_banco_menu(player)
    else if {_slot} is 12 or 16:
        close inventory of player
        if {_slot} is 12:
            set {-banco.espera::%uuid of player%} to "depositar"
        else:
            set {-banco.espera::%uuid of player%} to "retirar"
        send "&6Escribi en el chat cuanto queres %{-banco.espera::%uuid of player%}% &7(solo el numero, o &fcancelar&7)." to player
    else if {_slot} is 31:
        astral_banco_mejorar(player)
        astral_banco_menu(player)

on inventory close:
    delete {-banco.gui::%uuid of player%}

on chat:
    set {_m} to {-banco.espera::%uuid of player%}
    {_m} is set
    cancel event
    delete {-banco.espera::%uuid of player%}
    set {_s} to message
    wait 1 tick
    if {_s} is "cancelar":
        astral_banco_menu(player)
        stop
    replace all "." and "," and "$" and " " with "" in {_s}
    set {_v} to {_s} parsed as number
    if {_v} is not set:
        send "&cEso no es un numero. Abri el banco de nuevo con &f/banco&c." to player
        stop
    astral_banco_mover(player, {_m}, {_v})
    astral_banco_menu(player)

on quit:
    delete {-banco.espera::%uuid of player%}
    delete {-banco.gui::%uuid of player%}

# Interes: cada 24 h reales de server (aunque el jugador no este conectado).
every 1 minute:
    {astral.banco.proximo} is set
    now > {astral.banco.proximo}
    set {astral.banco.proximo} to {@horas} hours after now
    loop {astral.banco.saldo::*}:
        set {_u} to loop-index
        set {_s} to loop-value
        set {_lim} to {-eco.banco.lim::%{astral.banco.nivel::%{_u}%} ? 1%}
        set {_i} to floor(min({_s} * {@interes}, {@interesmax}, {_lim} - {_s}))
        if {_i} > 0:
            set {astral.banco.saldo::%{_u}%} to {_s} + {_i}
            log "%now% %{_u}% interes %{_i}% saldo_antes=%{_s}%" to "astral-banco"
    loop all players:
        astral_banco_saldo(loop-player) > 0
        send "&6✦ El Banco Astral pago los intereses del dia. &7(/banco)" to loop-player

# ================================================================== rebase x100 (UNA sola vez)
# Correrlo desde la consola con el server recien iniciado y el dueno presente: astraleconomia rebase
# Multiplica x{@escala} la plata de TODOS los jugadores (Vault/Essentials) y el saldo del Banco.
command /astraleconomia <text>:
    executable by: console
    trigger:
        if arg-1 is not "rebase":
            send "Uso: astraleconomia rebase (una sola vez)" to console
            stop
        if {astral.eco.rebase} is set:
            send "[Economia] El rebase ya se hizo el %{astral.eco.rebase}%. No se repite." to console
            stop
        set {astral.eco.rebase} to now
        set {_n} to 0
        loop all offline players:
            set {_a} to balance of loop-offlineplayer
            if {_a} is set:
                if {_a} > 0:
                    set {_b} to {_a} * {@escala}
                    set balance of loop-offlineplayer to {_b}
                    log "%uuid of loop-offlineplayer% %name of loop-offlineplayer% saldo %{_a}% -> %{_b}%" to "astral-rebase"
                    add 1 to {_n}
        loop {astral.banco.saldo::*}:
            set {astral.banco.saldo::%loop-index%} to loop-value * {@escala}
            log "%loop-index% banco %loop-value% -> %loop-value * {@escala}%" to "astral-rebase"
        send "[Economia] Rebase x{@escala} listo: %{_n}% jugadores. Log: plugins/Skript/logs/astral-rebase.log" to console
'''


# ------------------------------------------------------------------ salida
def generate():
    (OUT / 'Skript' / 'scripts').mkdir(parents=True, exist_ok=True)
    (OUT / 'Skript' / 'scripts' / 'astral_economia.sk').write_text(skript(), encoding='utf-8')
    shops = tienda()
    for rel, data in shops.items():
        dest = TIENDA_OUT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')
    (HERE / 'services_catalog.json').write_text(json.dumps(catalogo(shops), indent=1), encoding='utf-8')
    print(f'economia: x{ESCALA}, {len(shops)} secciones de tienda, {len(mundos_con_perdida())} mundos con perdida -> {OUT}')


if __name__ == '__main__':
    generate()
