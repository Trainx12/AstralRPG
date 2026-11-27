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
# Mobs vanilla del survival (24/11/2026, pedido del dueno): pagan segun su vida. Un zombi (20 de vida base)
# paga PLATA_VANILLA_TIER del tier que le toco; los demas en proporcion a su vida base (arana 16 = 0,8x,
# enderman 40 = 2x; los elites cuentan su vida extra). Un tercio de un mob Astral del mismo tier.
# No pagan los de spawner (granjas), los criados ni los de comandos/huevos (solo apariciones naturales).
PLATA_VANILLA_TIER = {t: PLATA_MOB_TIER[t] // 3 // 100 * 100 for t in PLATA_MOB_TIER}
VANILLA_VIDA_REF = 20      # vida base del zombi
VANILLA_TOPE = 10          # como mucho 10 zombis por mob (elites Astral, wither, etc.)
VANILLA_ORIGENES = ('natural', 'jockey', 'reinforce', 'patrol', 'raid', 'trial', 'split', 'drowned', 'chunk')
# Multiplicador por categoria. 'jefe' = jefes del mundo (Momia, Yeti...): x50 como antes (15 -> 750).
MULT_MOB = {'hostil': 1, 'elite': 10, 'jefe': 50, 'ancestral': 100}

# Mazmorras (tier = escala.TIER_MAZMORRA del mundo). Cada mob de oleada al que lo mata;
# el jefe a cada participante vivo (no espectador) en la sala.
OLEADA_TIER = {1: 300, 2: 800, 3: 2_000, 4: 4_500, 5: 10_000}
JEFE_MAZMORRA_TIER = {1: 100_000, 2: 300_000, 3: 800_000, 4: 2_000_000, 5: 5_000_000}
# 24/11 (dueno): cada mob de oleada paga lo mismo que un mob Astral del Survival de ese tier, y la
# Mazmorra Infinita paga como los mobs vanilla del Survival (segun su tier y vida). Primero solo para quien
# tenga MAZMORRA_PLATA_PERMISO (ByTrainx); abrirlo con `lp group default permission set astral.eco.mazmorras true`.
# 26/11 (dueno): los mobs de mazmorra pagan la MITAD que en el Survival (oleadas y Mazmorra Infinita).
MAZMORRA_PLATA_FACTOR = 0.5
OLEADA_TIER_NUEVO = {t: int(PLATA_MOB_TIER[t] * MAZMORRA_PLATA_FACTOR) for t in OLEADA_TIER}
MAZMORRA_PLATA_PERMISO = 'astral.eco.mazmorras'
ELITE_OLEADA = 10            # elite dentro de una mazmorra = 10 mobs de oleada
ECO_SANTUARIO = 3_000_000    # cada eco del Santuario, a cada participante
RADIO_PARTICIPANTES = 64

# ------------------------------------------------------------------ puntaje de mazmorras (plan E2, 18/11)
# Notas de peor a mejor; el numero es el que se guarda en el puntaje astral.nota (0 = sin nota).
NOTAS = ['F', 'D', 'C', 'B', 'A', 'S']
NOTA_MIN = {'S': 95, 'A': 85, 'B': 70, 'C': 55, 'D': 40, 'F': 0}
# S dorado ... F rojo (pedido del dueno 19/11).
NOTA_COLOR = {'S': '&6', 'A': '&d', 'B': '&a', 'C': '&b', 'D': '&9', 'F': '&c'}
PUNTOS_MUERTE, PUNTOS_MUERTE_TOPE = 12, 60
PUNTOS_MINUTO, PUNTOS_MINUTO_TOPE = 4, 40
PUNTOS_SIN_MUERTES = 10
# Minutos objetivo desde que la party entra hasta que muere el jefe (estimados por cantidad de salas y oleadas).
# Para ajustar: mirar el tiempo que muestra el chat al ganar ("Tiempo: X min") y poner aca lo que tarda una
# party normal. Despues: python mazmorras_puntaje.py y subir astral_puntaje.sk (sk reload).
TIEMPO_OBJETIVO = {'bosque': 12, 'mina': 10, 'tumba': 14, 'cumbre': 12, 'forja': 10, 'santuario': 15, 'fosa': 10, 'nave': 18}


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
# 25/11 (recorte de las Minas): antes {1: 1, 2: 3, 3: 8, 4: 18, 5: 40} y Santuario 60 (una S en tier 5 daba ~8M
# de promedio por partida, mas que una hora de Minas). Tier 1-2 igual.
RULETA_MULT_TIER = {1: 1, 2: 3, 3: 5, 4: 8, 5: 12}
RULETA_MULT_SANTUARIO = 18


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
# 26/11 (dueno: "mejora mucho las recompensas de los secretos"): antes la plata salia solo el 38% de las veces y era
# un 5-20% de lo que llevabas encima (10.000 a 5M; con el Banco casi siempre tocaba 10.000). Ahora la plata sale
# SIEMPRE y depende del tier del jugador (su mejor arma Astral): entre 1 y 2 veces SECRETO_PLATA_MOBS mobs Astral
# de su tier (~1 hora de farmeo: T1 450k-900k, T5 7,5M-15M, T10 240M-480M). SECRETO_DORADO_PROB de "secreto
# dorado" (x SECRETO_DORADO_MULT, con aviso a todos). Ademas sigue la ruleta: equipo +1 tier o premios del cofre.
SECRETO_PROB_EQUIPO = 0.03          # el resto son premios del pool de cofres del tier del jugador
SECRETO_PLATA_MOBS = 300
SECRETO_PLATA_TIER = {t: PLATA_MOB_TIER[t] * SECRETO_PLATA_MOBS for t in PLATA_MOB_TIER}   # minimo; maximo x2
SECRETO_DORADO_PROB = 0.10
SECRETO_DORADO_MULT = 3
SECRETO_TIRADAS = 2                 # tiradas de premios (con pesos de nota B)
SECRETO_NOTA_PESOS = 'B'


# ------------------------------------------------------------------ misiones del Cronista (24/11/2026)
# Cifras finales (ya en la escala nueva, sin plata()). Antes eran 30k..1M la historia y 30k/75k/150k las
# diarias: quedaron por debajo de lo que paga un jefe del mismo tier. Cada capitulo queda cerca del jefe
# de mazmorra de su tier (Minas T2 = 300k, Tumba T3 = 800k, Cumbre T4 = 2M, Forja T5 = 5M).
HISTORIA_PLATA = [50_000, 100_000, 200_000, 300_000, 500_000, 1_000_000, 2_500_000, 6_000_000, 10_000_000]
DIARIA_PLATA = [100_000, 250_000, 600_000]   # facil, media, dificil

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


# Cavernas de Cristal (plan E5 / 7e, 19/11/2026): venta de las menas propias (por unidad) y premios de comisiones.
# 25/11 (dueno, junto con el recorte de las Minas): antes 45.000 / 400.000 (~42M/h) y comisiones 2M/4M/8M.
# Objetivo nuevo: como Restos II - III Carbon de las Minas con taladro 2x2 (~8M/h). Cuenta en cavernas.py (plata_hora).
CAVERNAS_PRECIO = {'cristal_caverna': 8_500, 'geoda_estelar': 76_000}
CAVERNAS_COMISION = {'facil': 400_000, 'media': 750_000, 'dificil': 1_500_000}
# Vacio Estelar (7f): antes 110.000 el Fragmento y 3.000.000 el Nucleo (~72M/h). 25/11: un poco arriba de
# Netherita III de las Minas (~12M/h buscando vetas). Cuenta en vacio.py (plata_hora).
VACIO_PRECIO = {'fragmento_estelar': 18_000, 'nucleo_meteorito': 500_000}


def gema_costo(tier, calidad, extraer=False):
    """Plata para engarzar (o extraer) una gema de esa calidad en un equipo de ese tier."""
    return GEMA_PONER_TIER[tier] * GEMA_CALIDAD_MULT[calidad] * (GEMA_EXTRAER_MULT if extraer else 1)

# Minas: todo x100 salvo la Netherita III.
NETHERITA_BLOQUE = 15_000
# 25/11 (dueno): bajo de 2.500M a 250M junto con el recorte de abajo (pide igual 25 h de mineria en Diamante III).
NETHERITA_APERTURA = 250_000_000

# Minas Astrales, recorte del 25/11/2026 (pedido del dueno): con la plata de las minas altas se compraba toda la
# tienda y cientos de gachas. Ahora lo que paga cada bloque depende de la MINA MAS ALTA ABIERTA del jugador:
# la venta rapida multiplica por {-am.mult::rango} (minas.py, mult()). Referencia: las minas Tier I (1-6, con
# Esmeralda I) pagan igual que antes. De la 7 a la 20 sube poquito por mina hasta MINAS_SUBA veces lo de
# Diamante I en Netherita III. La cuenta se hace con Fortuna III (MINAS_FORTUNA = mineral promedio por mena), que
# es lo que usa cualquiera que mina en serio; sin Fortuna las minas II pagan un poco menos y las III igual.
# Antes Netherita III pagaba 15.000 por bloque y Restos II 4.818; ahora ~790 y ~560.
# El progreso fuerte de las minas altas lo dan los taladros (1x1 -> 4x4 = 16 veces mas bloques), no el precio.
# Los minerales de las minas no salen del mundo (AstralMinasLimite), asi que esto no toca la tienda.
MINAS_SUBA = 2.0
MINAS_FORTUNA = 2.2
MINAS_COSTO_FACTOR = 0.85      # abrir la mina N = 85 % de lo que se gana picando los bloques que pide en la N-1

# /pay de un jugador con mina mas alta a uno con mina mas baja (25/11, dueno): como mucho lo de una tirada del
# Gacha de Armas por hora, sumando lo que le pasen todos (asi no sirve usar varias cuentas).
PAGO_LIMITE = GACHA_TIRADA['gacha_rpg']
PAGO_HORAS = 1
PAGO_PERMISO_LIBRE = 'astral.eco.paylibre'

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
         f'    permmaz: {MAZMORRA_PLATA_PERMISO}',
         f'    interes: {BANCO_INTERES}',
         f'    interesmax: {BANCO_INTERES_MAX}',
         f'    horas: {BANCO_HORAS}',
         f'    escala: {ESCALA}',
         f'    titulo: {BANCO_TITULO}',
         f'    pagolim: {PAGO_LIMITE}',
         f'    pagoseg: {PAGO_HORAS * 3600}',
         f'    pagolibre: {PAGO_PERMISO_LIBRE}',
         '',
         'on load:',
         '    delete {-eco.tiermaz::*}', '    delete {-eco.mob::*}', '    delete {-eco.mult::*}',
         '    delete {-eco.oleada::*}', '    delete {-eco.jefe::*}', '    delete {-eco.perdida::*}',
         '    delete {-eco.banco.nombre::*}', '    delete {-eco.banco.lim::*}', '    delete {-eco.banco.costo::*}']
    L += [f'    set {{-eco.tiermaz::{w}}} to {t}' for w, t in mundos_mazmorra().items()]
    L += [f'    set {{-eco.mob::{t}}} to {v}' for t, v in PLATA_MOB_TIER.items()]
    L += [f'    set {{-eco.mult::{c}}} to {v}' for c, v in MULT_MOB.items()]
    L += [f'    set {{-eco.oleada::{t}}} to {v}' for t, v in OLEADA_TIER.items()]
    L += ['    delete {-eco.oleada2::*}'] + [f'    set {{-eco.oleada2::{t}}} to {v}' for t, v in OLEADA_TIER_NUEVO.items()]
    L += [f'    set {{-eco.jefe::{t}}} to {v}' for t, v in JEFE_MAZMORRA_TIER.items()]
    L += [f'    set {{-eco.santuario}} to {ECO_SANTUARIO}']
    from tanda5a import PARTY_SPLIT_WORLDS
    L += ['    delete {-eco.partymundo::*}'] + [f'    set {{-eco.partymundo::{w}}} to true' for w in PARTY_SPLIT_WORLDS]
    from escala import VIDA_MOB
    L += ['    delete {-eco.vanilla::*}', '    delete {-eco.vidamob::*}']
    L += [f'    set {{-eco.vanilla::{t}}} to {v}' for t, v in PLATA_VANILLA_TIER.items()]
    L += [f'    set {{-eco.vidamob::{t}}} to {VIDA_MOB[t]}' for t in PLATA_VANILLA_TIER]
    L += [f'    set {{-eco.perdida::{w}}} to true' for w in mundos_con_perdida()]
    for i, (nombre, lim, costo) in enumerate(BANCO_NIVELES, 1):
        L += [f'    set {{-eco.banco.nombre::{i}}} to "{nombre}"', f'    set {{-eco.banco.lim::{i}}} to {lim}',
              f'    set {{-eco.banco.costo::{i}}} to {costo}']
    import ventanas_19_11 as V
    L += ['    delete {-banco.titulo::*}'] + [f'    set {{-banco.titulo::{v}}} to "{V.titulo("banco_" + v)}"' for v in V.BANCO_VISTAS]
    L += [f'    set {{-banco.titulo::mejorar{n}}} to "{V.titulo(f"banco_mejorar{n}")}"' for n in (1, 2, 3, 4)]
    L += [f'    set {{-eco.banco.max}} to {len(BANCO_NIVELES)}',
          '    if {astral.banco.proximo} is not set:',
          '        set {astral.banco.proximo} to {@horas} hours after now', '']
    origenes = ', '.join(f'"{o}"' for o in VANILLA_ORIGENES[:-1]) + f' and "{VANILLA_ORIGENES[-1]}"'
    L += [SK_CUERPO.replace('__ORIGENES__', origenes).replace('__REF__', str(VANILLA_VIDA_REF))
          .replace('__TOPE__', str(VANILLA_TOPE)).replace('__MAZFACTOR__', str(MAZMORRA_PLATA_FACTOR))]
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

# 24/11 (dueno): en mazmorras de party la plata de cada mob se reparte en partes iguales con los companeros
# del mismo mundo (como la XP de AstralProgression). Mismo permiso: astral.xp.partysplit.
function astral_eco_repartir(p: player, n: number):
    set {_l} to {-party.lider::%uuid of {_p}%}
    set {_solo} to true
    if {_l} is set:
        if {-eco.partymundo::%name of world of {_p}%} is set:
            if {_p} has permission "astral.xp.partysplit":
                set {_solo} to false
    if {_solo} is true:
        astral_eco_dar({_p}, {_n})
        stop
    # 25/11: lista por uuid, cada jugador cuenta una sola vez (Matute solo cobraba la mitad).
    set {_r::%uuid of {_p}%} to {_p}
    loop all players in world of {_p}:
        {-party.lider::%uuid of loop-player%} is {_l}
        gamemode of loop-player is survival or adventure
        set {_r::%uuid of loop-player%} to loop-player
    set {_c} to size of {_r::*}
    loop {_r::*}:
        astral_eco_dar(loop-value, {_n} / {_c})

function astral_eco_participantes(p: player, n: number):
    # 25/11: lista por uuid: un mismo jugador no puede contar dos veces (Matute, solo, cobro 50.000 de 100.000).
    loop all players in radius {@radio} around {_p}:
        world of loop-player is world of {_p}
        gamemode of loop-player is survival or adventure
        set {_r::%uuid of loop-player%} to loop-player
    # 24/11 (dueno): con el reparto prendido el premio del jefe se divide entre los que estan en la pelea.
    set {_c} to 1
    if {-eco.partymundo::%name of world of {_p}%} is set:
        if {_p} has permission "astral.xp.partysplit":
            # 25/11: antes max(size of {_r::*}, 1): Skript lo lee como el tamano de la lista "{_r::*}, 1"
            # (uno de mas): solo cobraba la mitad y 3 jugadores un cuarto cada uno.
            set {_c} to size of {_r::*}
            if {_c} < 1:
                set {_c} to 1
    log "jefe %{_n}% en %name of world of {_p}%: %{_c}% partes entre %{_r::*}%" to "astral_pagos_jefe"
    loop {_r::*}:
        astral_eco_dar(loop-value, {_n} / {_c})
        send "&6Recompensa del jefe: &e+%{-eco.ultimo::%uuid of loop-value%}%$" to loop-value

# Lo que paga un mob de oleada: el valor nuevo (24/11) solo con el permiso, hasta que el dueno lo abra.
function astral_eco_oleada(p: player, t: number) :: number:
    if {_p} has permission "{@permmaz}":
        return {-eco.oleada2::%{_t}%} ? {-eco.oleada::%{_t}%}
    return {-eco.oleada::%{_t}%}

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
                astral_eco_repartir({_p}, astral_eco_oleada({_p}, {_tm}) * {@eliteola})
            else:
                astral_eco_repartir({_p}, astral_eco_oleada({_p}, {_tm}))
            stop
        set {_b} to {-eco.mob::%{_t}%} ? {-eco.mob::1}
        astral_eco_repartir({_p}, {_b} * ({-eco.mult::%{_c}%} ? 1))

# Mobs vanilla de las oleadas (tag ad.vanilla): antes pagaban 0.
on death:
    victim is not a player
    attacker is a player
    victim has scoreboard tag "ad.vanilla"
    set {_tm} to {-eco.tiermaz::%name of world of victim%}
    {_tm} is set
    if victim has scoreboard tag "astral.split":
        astral_eco_repartir(attacker, astral_eco_oleada(attacker, {_tm}))
    else if victim has scoreboard tag "astral.elite":
        astral_eco_repartir(attacker, astral_eco_oleada(attacker, {_tm}) * {@eliteola})
    else:
        astral_eco_repartir(attacker, astral_eco_oleada(attacker, {_tm}))

# Mobs vanilla del survival (24/11): pagan segun su vida (economia.PLATA_VANILLA_TIER). Solo los que aparecen
# solos: la marca astral.vpaga se pone al aparecer (sin spawners, crias, comandos ni MythicMobs).
on spawn of living entity:
    event-entity is not a player
    set {_r} to "%spawn reason%"
    loop __ORIGENES__:
        if {_r} contains loop-value:
            add "astral.vpaga" to scoreboard tags of event-entity
            stop

on death:
    victim is not a player
    attacker is a player
    victim has scoreboard tag "astral.vpaga"
    victim does not have scoreboard tag "ad.vanilla"
    victim does not have scoreboard tag "inf.mob"
    {-eco.tiermaz::%name of world of victim%} is not set
    astral_eco_dar(attacker, astral_eco_vanilla(victim))

# Mazmorra Infinita (24/11): sus mobs salen por comando (tag inf.mob) y pagan la mitad que los vanilla del Survival (26/11)
# segun el tier elegido; el +25% de vida de cada subida en X+ tambien suma (con el mismo tope). Con party
# se reparte como en las demas mazmorras.
on death:
    victim is not a player
    attacker is a player
    victim has scoreboard tag "inf.mob"
    attacker has permission "{@permmaz}"
    astral_eco_repartir(attacker, astral_eco_vanilla(victim) * __MAZFACTOR__)

function astral_eco_vanilla(e: entity) :: number:
    set {_t} to 1
    loop 10 times:
        set {_tag} to "astral.mt%loop-number%"
        if {_e} has scoreboard tag {_tag}:
            set {_t} to loop-number
    # max health de Skript va en corazones: x2 = vida real; / multiplicador del tier = vida base vanilla.
    set {_x} to (max health of {_e}) * 2 / ({-eco.vidamob::%{_t}%} ? 1) / __REF__
    set {_x} to min({_x}, __TOPE__)
    # Hijos de slime: vida heredada, premio de como maximo un mob normal del tier.
    if {_e} has scoreboard tag "astral.split":
        set {_x} to min({_x}, 1)
    return {-eco.vanilla::%{_t}%} * {_x}

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

# Ventanas con el diseno del dueno (19/11, ventanas_19_11.py): banco, depositar, retirar, mejorar, movimiento y cuenta.
# Los importes van en vivo en las piezas (pasar el mouse); los botones ocupan varias casillas (modelo _0.._n).
function astral_banco_pieza(model: text, label: text, lore: texts) :: item:
    set {_i} to paper named colored {_label}
    set item model of {_i} to "astral:ventanas1911/%{_model}%"
    set lore of {_i} to {_lore::*}
    return {_i}

function astral_banco_tiles(inv: inventory, inicio: number, cols: number, filas: number, model: text, label: text, lore: texts):
    set {_r} to 0
    while {_r} < {_filas}:
        set {_c} to 0
        while {_c} < {_cols}:
            set {_k} to {_r} * {_cols} + {_c}
            set slot ({_inicio} + {_r} * 9 + {_c}) of {_inv} to astral_banco_pieza("%{_model}%_%{_k}%", {_label}, ({_lore::*}))
            add 1 to {_c}
        add 1 to {_r}

function astral_banco_menu(p: player, vista: text = "banco"):
    set {_s} to astral_banco_saldo({_p})
    set {_n} to astral_banco_nivel({_p})
    set {_lim} to astral_banco_lim({_p})
    set {_i} to floor(min({_s} * {@interes}, {@interesmax}, {_lim} - {_s}))
    set {_falta} to difference between now and {astral.banco.proximo}
    if {_vista} is "mejorar":
        if {_n} >= {-eco.banco.max}:
            set {_vista} to "cuenta"
    set {_tit} to {-banco.titulo::%{_vista}%}
    if {_vista} is "mejorar":
        set {_tit} to {-banco.titulo::mejorar%{_n}%} ? {_tit}
    set {_inv} to chest inventory with 6 rows named {_tit}
    set {_cuenta} to "&7Cuenta: &f%{-eco.banco.nombre::%{_n}%}% &7(limite &e%{_lim}%$&7)"
    set {_int} to "&7Proximo interes: &a+%{_i}%$ &7en &f%{_falta}%"
    if {_vista} is "banco":
        set slot 5 of {_inv} to astral_banco_pieza("i_saldo", "&6&lSaldo del Banco: &e%{_s}%$", ({_cuenta}, {_int} and "&8No se pierde al morir."))
        set slot 14 of {_inv} to astral_banco_pieza("i_encima", "&aPlata encima: &e%balance of {_p}%$", ("&8Se pierde la mitad al morir."))
        set slot 23 of {_inv} to astral_banco_pieza("i_cuenta", "&fCuenta %{-eco.banco.nombre::%{_n}%}%", ("&7Limite: &e%{_lim}%$"))
        astral_banco_tiles({_inv}, 27, 3, 2, "b_depositar", "&a&lDepositar", ("&7Guarda plata en el banco." and "&7Tu plata encima: &e%balance of {_p}%$"))
        astral_banco_tiles({_inv}, 30, 3, 2, "b_retirar", "&6&lRetirar", ("&7Saca plata del banco." and "&7Saldo: &e%{_s}%$"))
        astral_banco_tiles({_inv}, 33, 3, 2, "b_mejorar_cuenta", "&b&lMejorar cuenta", ("&7Mas limite para guardar."))
    else if {_vista} is "depositar" or "retirar":
        if {_vista} is "depositar":
            set slot 5 of {_inv} to astral_banco_pieza("i_encima", "&aPlata encima: &e%balance of {_p}%$", ("&7Es lo que podes depositar."))
            set slot 14 of {_inv} to astral_banco_pieza("i_limite", "&6Capacidad: &e%{_lim} - {_s}%$", ({_cuenta}))
        else:
            set slot 5 of {_inv} to astral_banco_pieza("i_saldo", "&6Saldo del Banco: &e%{_s}%$", ({_int}))
            set slot 14 of {_inv} to astral_banco_pieza("i_encima", "&aPlata encima: &e%balance of {_p}%$", ("&8Se pierde la mitad al morir."))
        set {_sel} to {-banco.sel::%uuid of {_p}%} ? "todo"
        astral_banco_tiles({_inv}, 27, 3, 1, "b_todo", "&eTodo", ("&7Elegir todo." and "&8(despues CONFIRMAR)"))
        astral_banco_tiles({_inv}, 30, 3, 1, "b_mitad", "&eMitad", ("&7Elegir la mitad." and "&8(despues CONFIRMAR)"))
        astral_banco_tiles({_inv}, 33, 3, 1, "b_otra", "&eOtra cantidad", ("&7La escribis en el chat."))
        set {_m} to "b_confirmar_dep"
        if {_vista} is "retirar":
            set {_m} to "b_confirmar_ret"
        astral_banco_tiles({_inv}, 38, 5, 1, {_m}, "&a&lConfirmar: %{_sel}%", ("&7%{_vista}% %{_sel}% de tu plata." and "&7Elegido: &f%{_sel}%"))
    else if {_vista} is "mejorar":
        set {_sig} to {_n} + 1
        set slot 5 of {_inv} to astral_banco_pieza("i_limite", "&bNuevo limite: &e%{-eco.banco.lim::%{_sig}%}%$", ("&7Cuenta %{-eco.banco.nombre::%{_sig}%}%"))
        set slot 14 of {_inv} to astral_banco_pieza("i_saldo", "&6Costo: &e%{-eco.banco.costo::%{_sig}%}%$", ("&7Se paga con tu plata encima."))
        set slot 23 of {_inv} to astral_banco_pieza("i_cuenta", "&fCuenta actual: %{-eco.banco.nombre::%{_n}%}%", ("&7Limite: &e%{_lim}%$"))
        astral_banco_tiles({_inv}, 40, 5, 1, "b_mejorar", "&b&lMejorar a %{-eco.banco.nombre::%{_sig}%}%", ("&7Costo: &e%{-eco.banco.costo::%{_sig}%}%$"))
    else if {_vista} is "cuenta":
        set slot 5 of {_inv} to astral_banco_pieza("i_limite", "&dLimite: &e%{_lim}%$", ("&7Nivel maximo."))
        set slot 14 of {_inv} to astral_banco_pieza("i_saldo", "&6Interes: &e2%% cada 24 h", ({_int}))
        set slot 23 of {_inv} to astral_banco_pieza("i_encima", "&aTope de interes: &e{@interesmax}$", ("&8Ahorros protegidos en la Banca Astral."))
    else if {_vista} is "movimiento":
        set {_u} to {-banco.ultimo::%uuid of {_p}%} ? "Sin movimientos"
        set {_k} to 0
        while {_k} < 15:
            set slot (floor({_k} / 5) * 9 + 2 + mod({_k}, 5)) of {_inv} to astral_banco_pieza("blank", "&a&l%{_u}%", ("&7Nuevo saldo: &e%{_s}%$"))
            add 1 to {_k}
        astral_banco_tiles({_inv}, 38, 5, 1, "b_volver_banco", "&eVolver al banco", ("&7Saldo: &e%{_s}%$"))
    if {_vista} is not "movimiento":
        set slot 45 of {_inv} to astral_banco_pieza("b_atras_0", "&fVolver", ("&7Atras."))
    set slot 53 of {_inv} to astral_banco_pieza("b_cerrar_0", "&cCerrar", (""))
    open {_inv} to {_p}
    set {-banco.gui::%uuid of {_p}%} to {_vista}

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
        set {-banco.ultimo::%{_u}%} to "Depositaste %{_v}%$"
    else:
        set {_v} to floor(min({_v}, {_s}))
        if {_v} < 1:
            send "&cNo tenes plata en el banco." to {_p}
            stop
        set {astral.banco.saldo::%{_u}%} to {_s} - {_v}
        add {_v} to balance of {_p}
        send "&aRetiraste &e%{_v}%$&a. Saldo del banco: &e%{_s} - {_v}%$" to {_p}
        set {-banco.ultimo::%{_u}%} to "Retiraste %{_v}%$"
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
    set {_v} to {-banco.gui::%uuid of player%}
    set {_id} to uuid of player
    if {_slot} is 53:
        close inventory of player
        stop
    if {_slot} is 45:
        if {_v} is "banco":
            close inventory of player
            execute console command "dm open subastas_inicio %name of player%"
        else:
            astral_banco_menu(player, "banco")
        stop
    if {_v} is "banco":
        set {_c} to mod({_slot}, 9)
        if {_slot} >= 27:
            if {_slot} <= 44:
                delete {-banco.sel::%{_id}%}
                if {_c} <= 2:
                    astral_banco_menu(player, "depositar")
                else if {_c} <= 5:
                    astral_banco_menu(player, "retirar")
                else:
                    astral_banco_menu(player, "mejorar")
        stop
    if {_v} is "depositar" or "retirar":
        if {_slot} is between 27 and 29:
            set {-banco.sel::%{_id}%} to "todo"
            astral_banco_menu(player, {_v})
        else if {_slot} is between 30 and 32:
            set {-banco.sel::%{_id}%} to "mitad"
            astral_banco_menu(player, {_v})
        else if {_slot} is between 33 and 35:
            close inventory of player
            set {-banco.espera::%{_id}%} to {_v}
            send "&6Escribi en el chat cuanto queres %{_v}% &7(solo el numero, o &fcancelar&7)." to player
        else if {_slot} is between 38 and 42:
            set {_base} to balance of player
            if {_v} is "retirar":
                set {_base} to astral_banco_saldo(player)
            set {_m} to {_base}
            if {-banco.sel::%{_id}%} is "mitad":
                set {_m} to {_base} / 2
            delete {-banco.sel::%{_id}%}
            astral_banco_mover(player, {_v}, {_m})
            astral_banco_menu(player, "movimiento")
        stop
    if {_v} is "mejorar":
        if {_slot} is between 40 and 44:
            astral_banco_mejorar(player)
            astral_banco_menu(player, "mejorar")
        stop
    if {_v} is "movimiento":
        if {_slot} is between 38 and 42:
            astral_banco_menu(player, "banco")

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
    astral_banco_menu(player, "movimiento")

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
# ------------------------------------------------------------------ /pay con limite (25/11/2026, dueno)
# Si el que paga tiene una mina astral mas alta abierta ({am.rank}) que el que recibe, al que recibe le pueden
# pasar como mucho {@pagolim}$ (una tirada del Gacha de Armas) cada hora, sumando todos los que le pasen.
# Misma mina o hacia arriba: libre. {eco.pago.modo}: "publico" = todos; "privado" (al empezar) = solo cuando paga
# ByTrainx (lo prueba el dueno); "apagado". Los que tienen {@pagolibre} no tienen limite en modo publico.
function astral_pago_aplica(p: player) :: boolean:
    set {_m} to {eco.pago.modo} ? "privado"
    if {_m} is "publico":
        if {_p} has permission "{@pagolibre}":
            return false
        return true
    if {_m} is "privado":
        if name of {_p} is "ByTrainx":
            return true
    return false

on command:
    sender is a player
    command is "pay" or "epay" or "essentials:pay" or "essentials:epay"
    astral_pago_aplica(player) is true
    set {_args} to "%arguments%"
    set {_a::*} to {_args} split at " "
    if {_a::1} is "*" or "**":
        cancel event
        send "&cNo se puede pagar a todos a la vez." to player
        stop
    set {_o} to {_a::1} parsed as offline player
    {_o} is set
    set {_rd} to {am.rank::%uuid of player%} ? 1
    set {_rr} to {am.rank::%uuid of {_o}%} ? 1
    {_rd} > {_rr}
    set {_t} to {_a::2} ? ""
    replace all "," with "" in {_t}
    replace all "$" with "" in {_t}
    set {_n} to {_t} parsed as number
    if {_n} is not set:
        cancel event
        send "&cEscribi la cantidad solo con numeros (sin k ni M). Ej: &f/pay %{_a::1}% 50000" to player
        stop
    {_n} > 0
    set {_id} to uuid of {_o}
    set {_ahora} to unix timestamp of now
    if ({eco.pago.desde::%{_id}%} ? 0) + {@pagoseg} <= {_ahora}:
        set {eco.pago.desde::%{_id}%} to {_ahora}
        set {eco.pago.monto::%{_id}%} to 0
    set {_queda} to {@pagolim} - ({eco.pago.monto::%{_id}%} ? 0)
    if {_n} > {_queda}:
        cancel event
        set {_min} to ceil(({eco.pago.desde::%{_id}%} + {@pagoseg} - {_ahora}) / 60)
        send "&cTenes una mina astral mas alta que &f%{_a::1}%&c: le podes pasar hasta &e{@pagolim}$ &cpor hora entre todos." to player
        if {_queda} > 0:
            send "&7En esta hora todavia puede recibir &e%{_queda}%$&7." to player
        else:
            send "&7Ya recibio el maximo. Proba de nuevo en &f%{_min}% min&7." to player
        stop
    balance of player >= {_n}
    add {_n} to {eco.pago.monto::%{_id}%}
    log "%now% %name of player% (mina %{_rd}%) -> %{_a::1}% (mina %{_rr}%) %{_n}%$" to "astral-pagos"

command /astralpago [<text>] [<text>]:
    permission: astral.eco.admin
    trigger:
        if arg-1 is "publico" or "privado" or "apagado":
            set {eco.pago.modo} to arg-1
        if arg-1 is "ver":
            set {_o} to arg-2 parsed as offline player
            if {_o} is set:
                send "[Pagos] %arg-2%: recibio %{eco.pago.monto::%uuid of {_o}%} ? 0%$ desde %{eco.pago.desde::%uuid of {_o}%} ? 0% (unix)" to sender
            stop
        set {_m} to {eco.pago.modo} ? "privado"
        send "&eLimite de /pay hacia minas mas bajas: &f%{_m}% &7(/astralpago publico|privado|apagado, /astralpago ver <jugador>)" to sender
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
