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

# Dano de la espada de cada tier antes de la escala (items.SWORDS: dmg * (1+bonus)).
ESPADA_REAL = {1: 6.6, 2: 7.08, 3: 8.75, 4: 9.45, 5: 12.0}
# Factor REAL para todas las armas Astral de ese tier (mantiene la diferencia entre clases).
FACTOR_ARMA = {0: 1.0, **{t: DANO[t] / ESPADA_REAL[t] for t in DANO}}
# Multiplicador REAL de vida de mobs (base vanilla 20): x25 / x120 / x575 / x2.750 / x13.125.
VIDA_MOB = {0: 1.0, **{t: VIDA_REF[t] / 20 for t in DANO}}
# Dano de los mobs al jugador: x1,5 por tier (T1 x1,5 ... T5 x7,6 del dano normal del mob).
DANO_MOB = {t: round(1.5 ** t, 2) for t in range(6)}
# Los numeros ya son reales: lo que se ve es lo real.
FACTOR_MOSTRADO = {t: 1.0 for t in range(6)}

# Armas especiales (rayo, ender, destello, sismo, estallido, guadana umbria, guantes): tier fijo.
TIER_ESPECIAL = 3

# Mazmorras: tier fijo. Santuario es el epilogo (V+): tier 5 con vida extra.
# Los mundos actuales de Cumbre, Forja y Santuario tienen otro nombre (cumbre_hielo...).
TIER_MAZMORRA = {"mina": 1, "bosque": 2, "tumba": 3, "cumbre": 4, "forja": 5, "santuario": 5,
                 "cumbre_hielo": 4, "forja_volcano": 5, "santuario_interstellar": 5}
EXTRA_VIDA_MAZMORRA = {"santuario": 1.5, "santuario_interstellar": 1.5}

# Probabilidades de tier en el mundo (en %).
PROB_TIER_MAS = 4
PROB_TIER_MENOS = 10

# Mana de los bastones (antes 20/40/70/110/180): sube, pero sin numeros locos.
MANA_BASTON = {1: 50, 2: 100, 3: 180, 4: 300, 5: 500}

# Colores del [T#] en el nombre de los mobs.
COLOR_TIER = {0: "gray", 1: "#9fe870", 2: "#4fb0ff", 3: "#c070ff", 4: "#ff8a3d", 5: "#ffd84d"}


def fmt(n):
    """12500 -> '12.500' (como se escribe en Argentina)."""
    return f"{int(round(n)):,}".replace(",", ".")
