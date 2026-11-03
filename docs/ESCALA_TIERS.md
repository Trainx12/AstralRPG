# Escala por tier (números grandes)

Pedido del dueño (03/11/2026): que cada tier se sienta como un salto enorme. Todo sale de
`datapack-src/escala.py`; para cambiar un número se edita ahí y se regenera (`python build.py`,
`python gameplay.py`, `python lobby.py`).

## Números

| Tier | Daño espada | Vida de un mob de su tier (base zombi 20) | Golpes | Vida/defensa mostrada del jugador |
|---|---|---|---|---|
| 0 (sin arma Astral) | vanilla | vanilla (×1) | — | ×1 |
| 1 | 100 | 500 (×25) | 5 | ×25 |
| 2 | 500 | 2.400 (×120) | 4,8 | ×120 |
| 3 | 2.500 | 11.500 (×575) | 4,6 | ×575 |
| 4 | 12.500 | 55.000 (×2.750) | 4,4 | ×2.750 |
| 5 | 62.500 | 262.500 (×13.125) | 4,2 | ×13.125 |

- **Armas:** todas las armas Astral de un tier se multiplican por el mismo factor
  (`FACTOR_ARMA` = daño de la tabla / daño viejo de la espada), así cada clase conserva su diferencia.
  Espadas, hachas y guadañas: atributo de daño (el tooltip muestra el número real). Bastones: daño del
  hechizo. Arcos: el encantamiento Puntería multiplica la flecha. Lanzas: encantamiento **Poder Astral**.
  Armas especiales, Guadaña Umbría y Guantes Meteoro: **tier 3** fijo (sus habilidades también escalan,
  opción `escala` de `special_weapons.sk`).
- **Efectos** (sangrado, remate, hendidura, cono): escalan con el tier del arma del atacante.
  Ejecución mata seguro. Contra jugadores el sangrado y el remate quedan como antes.
- **Maná de bastones:** 50 / 100 / 180 / 300 / 500 (antes 20 / 40 / 70 / 110 / 180).

## Mobs

- Cada mob hostil nuevo (más golems y vex de MythicMobs; nunca los invulnerables) recibe un tier al
  aparecer (`mob/roll` del datapack, cada segundo).
- **Mundo:** tier = mejor arma Astral del inventario del jugador más cercano (128 bloques, score
  `astral.wt`): 86% ese tier, 4% uno más, 10% uno menos. Sin arma Astral: mob vanilla.
- **Mazmorras:** tier fijo: mina 1, bosque 2, tumba 3, cumbre 4, forja 5, santuario 5 con ×1,5 de vida.
- Vida × `VIDA_MOB`, daño × `DANO_MOB` (1 / 1,15 / 1,3 / 1,45 / 1,6): pegan un poco más por tier,
  siempre menos de lo que sube la armadura.
- **Élites:** misma probabilidad que antes (6% + 5% por amenaza); en mazmorras la mitad. Ahora
  multiplican la vida ya escalada (Élite ×1,9 … Astral ×5).
- **Nombre:** `[T3] Elite Zombi` / `[T2] Minero Corrupto`. Un mob común de tier 0 queda sin cartel.
- Se sacó **LevelledMobs** (subía la vida por distancia y chocaba con esto).

## Jugador

- La vida y la armadura **reales no cambian**: pociones, comida, regeneración, armadura y
  durabilidad funcionan igual que antes.
- Se **muestran** grandes: el panel TAB usa `astral.vida`/`astral.vidamax` = vida real × factor del
  tier de la mejor armadura puesta (`astral.at`). Las armaduras muestran "Defensa: N" y esconden el
  "+8 Armadura" vanilla.
- **Arena PvP:** el daño entre jugadores se divide por el factor del arma del atacante
  (`astral_gameplay.sk`, etiquetas `astral.ht0..5`): el PvP queda como antes.

## Servidor (Aternos)

- `spigot.yml`: `settings.attribute.maxHealth.max` y `attackDamage.max` subidos (los valores vanilla
  2048 cortan la vida de los mobs desde tier 2).
- Datapack con `ITEM_VERSION = 6`: los objetos se actualizan solos en el inventario conservando
  mejoras, adornos y desgaste.
- Scripts: `astral_gameplay.sk` (PvP) y `special_weapons.sk` (habilidades).
- TAB: `%player_health_rounded%` → `%objective_score_{astral.vida}%` (y `astral.vidamax`).
