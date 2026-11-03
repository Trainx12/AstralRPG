# -*- coding: utf-8 -*-
"""Escala de numeros por tier (sensacion de mejora grande).

Idea: cada tier multiplica x5 el dano de las armas Astral. La vida de los mobs
sube un poco menos que el dano (5 golpes en T1 -> 4,2 en T5), asi cada tier se
siente mas fuerte aunque la mejora real sea moderada.

- Armas: el dano real se multiplica por FACTOR_ARMA[t] (espada de referencia = DANO[t]).
- Mobs del mundo: se adaptan al arma de mayor tier del jugador mas cercano
  (86% su tier, 4% uno mas, 10% uno menos). Vida x VIDA_MOB[t], dano x DANO_MOB[t].
- Mazmorras: tier fijo por mazmorra (TIER_MAZMORRA), elites con la mitad de chance.
- Jugador: la vida real NO cambia (pociones, comida y armadura siguen igual);
  el panel y las armaduras MUESTRAN la vida/defensa x VIDA_MOSTRADA[t].
"""

# Dano de la espada de referencia por tier (lo que ve el jugador en el golpe).
DANO = {1: 100, 2: 500, 3: 2500, 4: 12500, 5: 62500}
# Golpes para matar a un mob de su mismo tier con 20 de vida base (un zombi).
GOLPES = {1: 5.0, 2: 4.8, 3: 4.6, 4: 4.4, 5: 4.2}
# Vida de ese mob de referencia: 500 / 2.400 / 11.500 / 55.000 / 262.500.
VIDA_REF = {t: round(DANO[t] * GOLPES[t]) for t in DANO}
# Multiplicador de vida de mobs (base vanilla 20). Tier 0 = mob normal.
VIDA_MOB = {0: 1.0, **{t: VIDA_REF[t] / 20 for t in DANO}}
# Multiplicador del dano que los mobs le hacen al jugador: sube menos que la armadura.
DANO_MOB = {0: 1.0, 1: 1.0, 2: 1.15, 3: 1.3, 4: 1.45, 5: 1.6}
# Vida/defensa del jugador que se MUESTRA (la real no cambia).
VIDA_MOSTRADA = dict(VIDA_MOB)

# Dano total de la espada de cada tier antes de esta escala (items.SWORDS: dmg * (1+bonus)).
_ESPADA_VIEJA = {1: 6.6, 2: 7.08, 3: 8.75, 4: 9.45, 5: 12.0}
# Factor que se aplica a TODAS las armas Astral de ese tier (mantiene la diferencia entre clases).
FACTOR_ARMA = {0: 1.0, **{t: DANO[t] / _ESPADA_VIEJA[t] for t in DANO}}

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
