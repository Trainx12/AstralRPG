# -*- coding: utf-8 -*-
"""Escala de numeros por tier (sensacion de mejora grande).

Los numeros REALES quedan chicos (como Minecraft): las armas pegan como antes y los mobs
tienen un poco mas de vida por tier. Lo que el jugador VE se multiplica por el factor del
tier del mob (FACTOR_MOSTRADO): cada golpe muestra "-2.500" y "vida 9.000 / 11.500".
Asi no salen miles de corazones al pegar ni barras de vida imposibles.

- Mobs del mundo: se adaptan al arma de mayor tier del jugador mas cercano
  (86% su tier, 4% uno mas, 10% uno menos). Mazmorras: tier fijo.
- La vida del jugador y el dano de los mobs NO cambian.
"""

# Dano MOSTRADO de la espada de referencia por tier.
DANO = {1: 100, 2: 500, 3: 2500, 4: 12500, 5: 62500}
# Golpes para matar a un mob de su mismo tier con 20 de vida base (un zombi).
GOLPES = {1: 5.0, 2: 4.8, 3: 4.6, 4: 4.4, 5: 4.2}
# Vida MOSTRADA de ese mob: 500 / 2.400 / 11.500 / 55.000 / 262.500.
VIDA_REF = {t: round(DANO[t] * GOLPES[t]) for t in DANO}

# Dano real de la espada de cada tier (items.SWORDS: dmg * (1+bonus)). No se cambia.
ESPADA_REAL = {1: 6.6, 2: 7.08, 3: 8.75, 4: 9.45, 5: 12.0}
# Lo que se ve = lo real x este factor (segun el tier del mob golpeado).
FACTOR_MOSTRADO = {0: 1.0, **{t: DANO[t] / ESPADA_REAL[t] for t in DANO}}

# Multiplicador REAL de vida de mobs (base 20): mantiene los golpes de GOLPES con el
# dano real. 1,65 / 1,7 / 2,0 / 2,08 / 2,52. Tier 0 = mob normal.
VIDA_MOB = {0: 1.0, **{t: VIDA_REF[t] / FACTOR_MOSTRADO[t] / 20 for t in DANO}}
# Dano de los mobs al jugador: normal.
DANO_MOB = {t: 1.0 for t in range(6)}

# Las armas reales no se escalan (se dejan los nombres para el codigo que los usa).
FACTOR_ARMA = {t: 1.0 for t in range(6)}

# Armas especiales (rayo, ender, destello, sismo, estallido, guadana umbria, guantes): tier fijo.
TIER_ESPECIAL = 3

# Mazmorras: tier fijo. Santuario es el epilogo (V+): tier 5 con vida extra.
TIER_MAZMORRA = {"mina": 1, "bosque": 2, "tumba": 3, "cumbre": 4, "forja": 5, "santuario": 5}
EXTRA_VIDA_MAZMORRA = {"santuario": 1.5}

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
