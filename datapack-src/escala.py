# -*- coding: utf-8 -*-
"""Escala de numeros por tier (sensacion de mejora grande).

El dano de las armas Astral y la vida de los mobs son REALES y enormes: cada tier
multiplica x5 el dano (100 / 500 / 2.500 / 12.500 / 62.500) y la vida de los mobs
sube un poco menos (5 golpes en T1 -> 4,2 en T5).

- Mobs del mundo: se adaptan al arma de mayor tier del jugador mas cercano
  (86% su tier, 4% uno mas, 10% uno menos). Mazmorras: tier fijo.
- La vida del jugador y su armadura NO cambian. El dano de los mobs sube x1,5 por tier
  (pedido del dueno, 08/11/2026: un mob tier 5 casi no lastimaba a un jugador tier 3).
- La particula de corazones al pegar es transparente (si no, salen miles) y la vida del
  mob se ve con el indicador de dano de astral_gameplay.sk.
"""

# Dano de la espada de referencia por tier.
DANO = {1: 100, 2: 500, 3: 2500, 4: 12500, 5: 62500}
# Golpes para matar a un mob de su mismo tier con 20 de vida base (un zombi).
GOLPES = {1: 5.0, 2: 4.8, 3: 4.6, 4: 4.4, 5: 4.2}
# Vida de ese mob: 500 / 2.400 / 11.500 / 55.000 / 262.500.
VIDA_REF = {t: round(DANO[t] * GOLPES[t]) for t in DANO}

# AuraSkills legacy: el nivel destino es el argumento de xp_requirements.yml.
# 25 -> 26: 100*(26-2)^2+100 = 57.700; 250 bajas/h = 230,8 XP/baja T5.
XP_MOB = {0: 0, 1: 20, 2: 40, 3: 80, 4: 140, 5: 230.8}
XP_ELITE = 1.5
XP_JEFE = 8


def xp_skill_mob(tier, elite=False, jefe=False):
    """Una sola recompensa por baja; jefe reemplaza el bonus de elite."""
    return round(XP_MOB[max(0, min(5, tier))] * (XP_JEFE if jefe else XP_ELITE if elite else 1), 2)


def xp_skill_level(destination):
    return 100 * (destination - 2) ** 2 + 100

# Dano de la espada de cada tier antes de la escala (items.SWORDS: dmg * (1+bonus)).
ESPADA_REAL = {1: 6.6, 2: 7.08, 3: 8.75, 4: 9.45, 5: 12.0}
# Factor REAL para todas las armas Astral de ese tier (mantiene la diferencia entre clases).
FACTOR_ARMA = {0: 1.0, **{t: DANO[t] / ESPADA_REAL[t] for t in DANO}}
# Multiplicador REAL de vida de mobs (base vanilla 20): x25 / x120 / x575 / x2.750 / x13.125.
VIDA_MOB = {0: 1.0, **{t: VIDA_REF[t] / 20 for t in DANO}}
# ---------------------------------------------------------------------------
# VIDA DEL JUGADOR Y DANO DE LOS MOBS (referencia Hypixel SkyBlock, 09/11/2026)
# ---------------------------------------------------------------------------
# Vida base del jugador (Hypixel: 100) y vida total con el set completo de cada tier.
VIDA_JUGADOR_BASE = 100
VIDA_SET = {1: 300, 2: 550, 3: 1000, 4: 3000, 5: 8000}
# Vida que da cada pieza de armadura (las 4 piezas suman VIDA_SET - base).
VIDA_PIEZA = {t: (VIDA_SET[t] - VIDA_JUGADOR_BASE) / 4 for t in VIDA_SET}
# Defensa como Hypixel: dano recibido = dano x 100 / (defensa + 100). La armadura Astral no da
# armadura vanilla: da DEFENSA (set completo por tier), repartida como la armadura vanilla.
DEFENSA_SET = {1: 50, 2: 100, 3: 200, 4: 350, 5: 500}
DEF_REPARTO = {"helmet": 0.15, "chestplate": 0.40, "leggings": 0.30, "boots": 0.15}


def defensa_pieza(tier, piece, def_pct=0, extra=0):
    """Defensa de una pieza: su parte del set, +/- el % de defensa de su clase, +5 por punto de armadura extra."""
    return round(DEFENSA_SET[tier] * DEF_REPARTO[piece] * (1 + def_pct / 100) + extra * 5)


# Golpe de un mob comun (un zombi) de cada tier, antes de la defensa. Golpes para matar a un jugador
# del mismo tier con el set completo: T1 8, T2 9, T3 10, T4 19, T5 48. Un T5 mata a un T3 en 3 golpes.
DANO_GOLPE = {1: 55, 2: 120, 3: 300, 4: 700, 5: 1000}
# Golpe de un zombi en dificultad facil (la del server); el resto de los mobs escala igual.
GOLPE_VANILLA = 2.5
# Multiplicador del dano de los mobs con tier (lo aplica astral_gameplay.sk a golpes, flechas y explosiones).
DANO_MOB = {0: 1.0, **{t: round(DANO_GOLPE[t] / GOLPE_VANILLA, 3) for t in DANO_GOLPE}}
# Caidas, lava, ahogo, mobs sin tier y PvP: se multiplican por (vida maxima / 20), asi pegan lo mismo
# en proporcion que en Minecraft normal. La regeneracion natural y las pociones tambien.
# Los numeros ya son reales: lo que se ve es lo real.
FACTOR_MOSTRADO = {t: 1.0 for t in range(6)}

# Armas especiales (rayo, ender, destello, sismo, estallido, guadana umbria, guantes): tier fijo.
TIER_ESPECIAL = 3

# Mazmorras: tier fijo. Santuario es el epilogo (V+): tier 5 con vida extra.
# Los mundos actuales de Cumbre, Forja y Santuario tienen otro nombre (cumbre_hielo...).
TIER_MAZMORRA = {"bosque": 1, "mina": 2, "tumba": 3, "cumbre": 4, "forja": 5, "santuario": 5,
                 "cumbre_hielo": 4, "forja_volcano": 5, "santuario_interstellar": 5, "santuario_azeroth": 5}
EXTRA_VIDA_MAZMORRA = {"santuario": 1.5, "santuario_interstellar": 1.5, "santuario_azeroth": 1.5}

# Probabilidades de tier en el mundo (en %).
PROB_TIER_MAS = 4
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
MANA_BASTON = {1: 100, 2: 180, 3: 250, 4: 300, 5: 350}
# Mana del set completo de Mago (cada pieza da 1/4): T3 ~ Wise Dragon 350, T5 ~ Storm 1.150.
MANA_SET_MAGO = {1: 100, 2: 200, 3: 350, 4: 600, 5: 1150}
# Costo del hechizo de cada bastón (Frozen Scythe 50, Bonzo 90, Spirit Sceptre 200).
MANA_HECHIZO = {1: 30, 2: 50, 3: 90, 4: 150, 5: 200}
# Daño base del hechizo = espada del mismo tier x 1,2 (sin bonus de dano magico).
# Cuesta mana, asi que pega un poco mas que un espadazo, como las habilidades de Mago.
FACTOR_HECHIZO = 1.2
HECHIZO = {t: round(DANO[t] * FACTOR_HECHIZO) for t in DANO}
# Armas especiales: (mana, recarga en segundos). Destello = Aspect of the End (50, sin recarga);
# Danza = Shadow Fury (sin mana, 15 s).
MANA_ESPECIAL = {"destello": 50, "danza": 0, "sismo": 100, "estallido": 30, "curacion": 60}
# Varita de Curacion (Wand of Healing): % de la vida maxima por segundo, segundos y radio.
CURACION = {"pct": 5, "segundos": 5, "radio": 7}
CD_DANZA = 15

# Colores del [T#] en el nombre de los mobs.
COLOR_TIER = {0: "gray", 1: "#9fe870", 2: "#4fb0ff", 3: "#c070ff", 4: "#ff8a3d", 5: "#ffd84d"}


def fmt(n):
    """12500 -> '12.500' (como se escribe en Argentina)."""
    return f"{int(round(n)):,}".replace(",", ".")
