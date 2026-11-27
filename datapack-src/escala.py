# -*- coding: utf-8 -*-
"""Escala de numeros por tier (sensacion de mejora grande).

El dano de las armas Astral y la vida de los mobs son REALES y enormes: cada tier
multiplica x5 el dano (100 / 500 / 2.500 / 12.500 / 62.500) y la vida de los mobs
sube un poco menos (5 golpes en T1 -> 4,2 en T5).

- Mobs del mundo: se adaptan al arma de mayor tier del jugador mas cercano
  (4% uno mas en T1-T5, 10% desde T6; 10% uno menos). Mazmorras: tier fijo.
- La vida del jugador y su armadura NO cambian. El dano de los mobs sube x1,5 por tier
  (pedido del dueno, 08/11/2026: un mob tier 5 casi no lastimaba a un jugador tier 3).
- La particula de corazones al pegar es transparente (si no, salen miles) y la vida del
  mob se ve con el indicador de dano de astral_gameplay.sk.
"""

# Tier maximo del juego (T6-T10 agregados el 14/11/2026).
CUCHILLO_DANO = 0.53  # 3.0 * .53 = 1.59 DPS frente a 1.60 de espada
CUCHILLO_VELOCIDAD = 3.0
TIER_MAX = 10
TIERS = range(1, TIER_MAX + 1)

# Dano de la espada de referencia por tier.
DANO = {1: 100, 2: 500, 3: 2500, 4: 12500, 5: 62500,
        6: 312500, 7: 1562500, 8: 7812500, 9: 39062500, 10: 195312500}  # T6-T10: 14/11/2026
# Golpes para matar a un mob de su mismo tier con 20 de vida base (un zombi).
GOLPES = {1: 5.0, 2: 4.8, 3: 4.6, 4: 4.4, 5: 4.2, 6: 4.0, 7: 3.8, 8: 3.6, 9: 3.4, 10: 3.2}
# Vida de ese mob: 500 / 2.400 / 11.500 / 55.000 / 262.500.
VIDA_REF = {t: round(DANO[t] * GOLPES[t]) for t in DANO}

# AuraSkills legacy: el nivel destino es el argumento de xp_requirements.yml.
# 25 -> 26: 100*(26-2)^2+100 = 57.700; 250 bajas/h = 230,8 XP/baja T5.
# 23/11 (pedido del dueno): curva creciente. T1 ~2 h, T2 3 h, T3 4 h (+1 h) y despues +2 h por tier hasta T10 ~18 h (250 bajas/h).
XP_MOB = {0: 0, 1: 84.5, 2: 110, 3: 148, 4: 170, 5: 193, 6: 217, 7: 241, 8: 265, 9: 289, 10: 313}
XP_ELITE = 1.5
XP_JEFE = 8
# 27/11 (dueno): XP del tier de la skill x4 con +1 tier y x10 con +2 o mas.
# Se conserva el tope +2 y el permiso astral.xp.tierbonus.
XP_TIER_ARRIBA = {1: 4, 2: 10}
XP_TIER_ARRIBA_TOPE = 2
# 26/11 (dueno): para todos, x0,15 a un tier abajo; x0,03 a dos o mas tiers abajo.
XP_TIER_ABAJO = {1: 0.15, 2: 0.03}


def xp_skill_mob(tier, elite=False, jefe=False):
    """Una sola recompensa por baja; jefe reemplaza el bonus de elite."""
    return round(XP_MOB[max(0, min(TIER_MAX, tier))] * (XP_JEFE if jefe else XP_ELITE if elite else 1), 2)


def xp_skill_level(destination):
    return 100 * (destination - 2) ** 2 + 100

# Dano de la espada de cada tier antes de la escala (items.SWORDS: dmg * (1+bonus)).
ESPADA_REAL = {1: 6.6, 2: 7.08, 3: 8.75, 4: 9.45, 5: 12.0, 6: 12.8, 7: 13.6, 8: 14.4, 9: 15.2, 10: 16.0}
# Factor REAL para todas las armas Astral de ese tier (mantiene la diferencia entre clases).
FACTOR_ARMA = {0: 1.0, **{t: DANO[t] / ESPADA_REAL[t] for t in DANO}}
# Multiplicador REAL de vida de mobs (base vanilla 20): x25 / x120 / x575 / x2.750 / x13.125.
VIDA_MOB = {0: 1.0, **{t: VIDA_REF[t] / 20 for t in DANO}}
# ---------------------------------------------------------------------------
# VIDA DEL JUGADOR Y DANO DE LOS MOBS (referencia Hypixel SkyBlock, 09/11/2026)
# ---------------------------------------------------------------------------
# Vida base del jugador (Hypixel: 100) y vida total con el set completo de cada tier.
VIDA_JUGADOR_BASE = 100
VIDA_SET = {1: 300, 2: 550, 3: 1000, 4: 3000, 5: 8000, 6: 15000, 7: 25000, 8: 40000, 9: 65000, 10: 100000}
# Vida que da cada pieza de armadura (las 4 piezas suman VIDA_SET - base).
VIDA_PIEZA = {t: (VIDA_SET[t] - VIDA_JUGADOR_BASE) / 4 for t in VIDA_SET}
# Defensa como Hypixel: dano recibido = dano x 100 / (defensa + 100). La armadura Astral no da
# armadura vanilla: da DEFENSA (set completo por tier), repartida como la armadura vanilla.
DEFENSA_SET = {1: 50, 2: 100, 3: 200, 4: 350, 5: 500, 6: 650, 7: 800, 8: 1000, 9: 1250, 10: 1500}
DEF_REPARTO = {"helmet": 0.15, "chestplate": 0.40, "leggings": 0.30, "boots": 0.15}
# Proteccion como Defensa (25/11/2026): cada nivel suma este % de la Defensa de ESA pieza (crece con el tier).
# Proteccion +8%/nivel; Fuego, Explosiones y Proyectiles +4%/nivel contra todo. Quien tiene la etiqueta
# astral.protdef pierde el 4%/8% fijo de Minecraft (no se cuenta dos veces). Solo ByTrainx hasta abrirlo.
# Filo en porcentaje (26/11/2026, dueno): +3% de dano por nivel (Filo V = +15%) en vez de +0,5..+3 fijo de Minecraft,
# que no se notaba con el dano por tier. Interruptor #pub astral.filo (como protdef): 0 = solo ByTrainx, 1 = todos,
# -1 = Filo de Minecraft. AstralMesa lo suma en la linea "Dano:" (filo-porcentaje en su config).
FILO_PCT = 3
PROT_DEF_PCT = {"protection": 8, "fire_protection": 4, "blast_protection": 4, "projectile_protection": 4}
# Armadura vanilla como Defensa (25/11/2026, dueno: "la defensa de las vanilla es mejor que la de las clases").
# Antes la armadura de Minecraft usaba su propia reduccion (hasta 40-44% contra mobs sin tier) y la barra la
# mostraba x5 (diamante = 100). Ahora cada punto vale 1,5 de Defensa Astral (+1 por pieza de netherita) y la
# reduccion de Minecraft se anula: set de netherita 35, diamante 31, hierro 23 < set de clase T1 (45-55).
# Interruptor #pub astral.vandef (como protdef): 0 = solo ByTrainx, 1 = todos, -1 = apagado.
_VAN_PUNTOS = {
    "leather": (1, 3, 2, 1), "chainmail": (2, 5, 4, 1), "golden": (2, 5, 3, 1), "copper": (2, 4, 3, 1),
    "iron": (2, 6, 5, 2), "diamond": (3, 8, 6, 3), "netherite": (3, 8, 6, 3)}
DEF_VANILLA_PUNTO = 1.5
DEF_VANILLA_EXTRA = {"netherite": 1}
VANILLA_PIEZAS = {}  # slot -> [(item, puntos de armadura, Defensa)]
for _mat, _pts in _VAN_PUNTOS.items():
    for _slot, _piece, _p in zip(("head", "chest", "legs", "feet"), ("helmet", "chestplate", "leggings", "boots"), _pts):
        VANILLA_PIEZAS.setdefault(_slot, []).append(
            (f"minecraft:{_mat}_{_piece}", _p, int(_p * DEF_VANILLA_PUNTO + 0.5) + DEF_VANILLA_EXTRA.get(_mat, 0)))
VANILLA_PIEZAS["head"].append(("minecraft:turtle_helmet", 2, 3))


def defensa_pieza(tier, piece, def_pct=0, extra=0):
    """Defensa de una pieza: su parte del set, +/- el % de defensa de su clase, +5 por punto de armadura extra."""
    return round(DEFENSA_SET[tier] * DEF_REPARTO[piece] * (1 + def_pct / 100) + extra * 5)


# Golpe de un mob comun (un zombi) de cada tier, antes de la defensa. Golpes para matar a un jugador
# del mismo tier con el set completo: T1 8, T2 9 y ~10 desde T3 (23/11, dueno: en la Cumbre T4 hacian
# falta 19 golpes y en el End un enderman T5 casi no lastimaba; antes T4 19, T5 48, T6-T10 ~40).
# T4+: ~12 golpes de zombi (VIDA_SET x (DEFENSA_SET + 100) / 100 / 12); los mobs de MythicMobs (Damage 3-8) en 3-6.
DANO_GOLPE = {1: 55, 2: 120, 3: 300, 4: 1100, 5: 4000, 6: 9400, 7: 18750, 8: 36700, 9: 73000, 10: 133000}
# Jefes de mazmorra (MythicMobs sin tier): conservan la escala anterior; su Damage ya esta pensado para ella
# (Capitan 30, Golem del Santuario 41). Con DANO_GOLPE mataban de un golpe a un jugador T5.
DANO_GOLPE_JEFE = {1: 55, 2: 120, 3: 300, 4: 700, 5: 1000, 6: 2800, 7: 5600, 8: 11000, 9: 22000, 10: 40000}
# Golpe de un zombi en dificultad facil (la del server); el resto de los mobs escala igual.
GOLPE_VANILLA = 2.5
# Multiplicador del dano de los mobs con tier (lo aplica astral_gameplay.sk a golpes, flechas y explosiones).
DANO_MOB = {0: 1.0, **{t: round(DANO_GOLPE[t] / GOLPE_VANILLA, 3) for t in DANO_GOLPE}}
DANO_JEFE = {0: 1.0, **{t: round(DANO_GOLPE_JEFE[t] / GOLPE_VANILLA, 3) for t in DANO_GOLPE_JEFE}}
# Jefes del Survival (normales y ancestrales, etiqueta astral.jmN de mob/jefe_mundo), 26/11 dueno: el dano
# depende del tier. Un jefe de Damage JEFE_MUNDO_REF mata a un jugador de su tier con el set completo en
# JEFE_MUNDO_GOLPES golpes (el Coloso Ancestral, Damage 25,6, en ~5). Antes pegaban un % fijo de tu vida.
JEFE_MUNDO_REF = 16
JEFE_MUNDO_GOLPES = 8
DANO_JEFE_MUNDO = {t: round(VIDA_SET[t] * (DEFENSA_SET[t] + 100) / 100 / JEFE_MUNDO_GOLPES / JEFE_MUNDO_REF, 3)
                   for t in VIDA_SET}
# Caidas, lava, ahogo, mobs sin tier y PvP: se multiplican por (vida maxima / 20), asi pegan lo mismo
# en proporcion que en Minecraft normal. La regeneracion natural y las pociones tambien.
# Los numeros ya son reales: lo que se ve es lo real.
FACTOR_MOSTRADO = {t: 1.0 for t in range(TIER_MAX + 1)}

# Armas especiales (rayo, ender, destello, sismo, estallido, guadana umbria, guantes): tier fijo.
TIER_ESPECIAL = 3

# Mazmorras: tier fijo. Santuario es el epilogo (V+): tier 5 con vida extra.
# Los mundos actuales de Cumbre, Forja y Santuario tienen otro nombre (cumbre_hielo...).
# expand_map suma las 6 copias de cada mazmorra (instancias.py) con el mismo valor.
from instancias import expand_map as _copias
TIER_MAZMORRA = _copias({"bosque": 1, "mina": 2, "tumba": 3, "cumbre": 4, "forja": 5, "santuario": 5,
                 "cumbre_hielo": 4, "forja_volcano": 5, "santuario_interstellar": 5, "santuario_azeroth": 5})
# Mundos con tier fijo que no son mazmorras (sin vida extra ni elites de mazmorra).
TIER_FIJO = {"oceano": 2, "fosa": 3, "fosa_2": 3, "fosa_3": 3,  # oceano abierto y Fosa del Crustaceo
             "cavernas_cristal": 4, "vacio_estelar": 6}  # Cavernas de Cristal (cavernas.py); el Corazon es tier 5 (build.py mob/roll)
EXTRA_VIDA_MAZMORRA = _copias({"santuario": 1.5, "santuario_interstellar": 1.5, "santuario_azeroth": 1.5})
# Nave del Vacio (nave.py, evento del End): 3 copias, tier 5 con vida x1,5 como el Santuario.
from nave import WORLDS as _NAVE, TIER as _NAVE_TIER, EXTRA_VIDA as _NAVE_VIDA
TIER_MAZMORRA.update({w: _NAVE_TIER for w in _NAVE})
EXTRA_VIDA_MAZMORRA.update({w: _NAVE_VIDA for w in _NAVE})

# Probabilidades de tier en el mundo (en %).
PROB_TIER_MAS = 4
PROB_TIER_MAS_ALTO = 10  # Desde T6 aumenta solo la posibilidad de uno mas.
TIER_PROB_ALTA = 6
PROB_TIER_MENOS = 10
PROB_MAZ_MAS = 3
PROB_MAZ_MENOS = 10
EZ_JEFE = {"bosque": 25, "mina": 30, "tumba": 40, "cumbre": 45, "forja": 50}
VIDA_JEFE = {k: ez * VIDA_REF[TIER_MAZMORRA[k]] for k, ez in EZ_JEFE.items()}
OLEADA_TOPE = 6
OLEADA_TOPE_FORJA = 9
OLEADA_TANDA = 2
OLEADA_INTERVALO = 100  # ticks: cinco segundos
LLEGADA_MOBS = 4
EXTRA_JUGADOR_PCT = 40

# ---------------------------------------------------------------------------
# MANA (referencia: Hypixel SkyBlock, 09/11/2026). Ver docs/ESCALA_TIERS.md.
# Hypixel: 100 de base, cada Inteligencia suma 1 y se recupera el 2% del maximo por segundo.
# ---------------------------------------------------------------------------
# AuraSkills (plugins/AuraSkills/stats.yml): traits.max_mana.base y traits.mana_regen.base.
# mana_regen de AuraSkills es una cantidad fija por segundo: 2 = 2% de los 100 de base, y cada
# item que da mana suma tambien el 2% de ese mana como regeneracion (REGEN_POR_MANA).
MANA_BASE = 100
REGEN_BASE = 2
REGEN_POR_MANA = 0.02
# Mana que da el bastón en la mano (Bonzo 250-300, Spirit Sceptre 300, Hyperion 350).
MANA_BASTON = {1: 100, 2: 180, 3: 250, 4: 300, 5: 350, 6: 400, 7: 450, 8: 500, 9: 550, 10: 600}
# Mana del set completo de Mago (cada pieza da 1/4): T3 ~ Wise Dragon 350, T5 ~ Storm 1.150.
MANA_SET_MAGO = {1: 100, 2: 200, 3: 350, 4: 600, 5: 1150, 6: 1600, 7: 2200, 8: 3000, 9: 4000, 10: 5200}
# Costo del hechizo de cada bastón (Frozen Scythe 50, Bonzo 90, Spirit Sceptre 200).
MANA_HECHIZO = {1: 30, 2: 50, 3: 90, 4: 150, 5: 200, 6: 250, 7: 300, 8: 360, 9: 430, 10: 500}
# Daño base del hechizo = espada del mismo tier x 1,2 (sin bonus de dano magico).
# Cuesta mana, asi que pega un poco mas que un espadazo, como las habilidades de Mago.
HECHIZO_PERFORA = (1.0, 0.7, 0.7)  # Objetivos distintos en orden del disparo
FACTOR_HECHIZO = 1.2
HECHIZO = {t: round(DANO[t] * FACTOR_HECHIZO) for t in DANO}
# Armas especiales: (mana, recarga en segundos). Destello = Aspect of the End (50, sin recarga);
# Danza = Shadow Fury (sin mana, 15 s).
MANA_ESPECIAL = {"destello": 50, "danza": 0, "sismo": 100, "estallido": 30, "curacion": 60}
# Varita de Curacion (Wand of Healing): % de la vida maxima por segundo, segundos y radio.
CURACION = {"pct": 5, "segundos": 5, "radio": 7}
CD_DANZA = 15

# Colores del [T#] en el nombre de los mobs.
COLOR_TIER = {0: "gray", 1: "#9fe870", 2: "#4fb0ff", 3: "#c070ff", 4: "#ff8a3d", 5: "#ffd84d",
              6: "#ff5fd2", 7: "#5ff0ff", 8: "#ff3b3b", 9: "#ffffff", 10: "#b388ff"}


def fmt(n):
    """12500 -> '12.500' (como se escribe en Argentina)."""
    return f"{int(round(n)):,}".replace(",", ".")
