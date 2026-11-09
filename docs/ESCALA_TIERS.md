# Escala por tier (números grandes reales)

Pedido del dueño (03/11/2026): que cada tier se sienta como un salto enorme. Todo sale de
`datapack-src/escala.py`; para cambiar un número se edita ahí y se regenera (`python build.py`,
`python gameplay.py`).

El **daño de las armas Astral y la vida de los mobs son reales y enormes**. La vida del jugador, su
armadura y el daño de los mobs **no cambian** (se probó mostrarlos grandes y al dueño no le gustó).

## Números

| Tier | Daño espada | Vida de un mob de su tier (zombi) | Golpes |
|---|---|---|---|
| 0 (sin arma Astral) | vanilla | vanilla | — |
| 1 | 100 | 500 (×25) | 5 |
| 2 | 500 | 2.400 (×120) | 4,8 |
| 3 | 2.500 | 11.500 (×575) | 4,6 |
| 4 | 12.500 | 55.000 (×2.750) | 4,4 |
| 5 | 62.500 | 262.500 (×13.125) | 4,2 |

- **Armas:** todas las armas Astral de un tier se multiplican por `FACTOR_ARMA` (daño de la tabla /
  daño viejo de la espada); cada clase conserva su diferencia. Espadas, hachas y guadañas: atributo de
  daño y "Daño: 2.500" en la descripción. Bastones: daño del hechizo. Arcos: Puntería multiplica la
  flecha. Lanzas: encantamiento **Poder Astral**. Armas especiales, Guadaña Umbría y Guantes Meteoro:
  **tier 3** (sus habilidades también, opción `escala` de `special_weapons.sk`).
- **Efectos** (sangrado, remate, hendidura, cono) escalan con el tier del arma del atacante; contra
  jugadores quedan como antes. Ejecución mata seguro.
- **Arena PvP:** el daño entre jugadores se divide por el factor del arma del atacante.
- **Indicador de daño** (reemplaza DamageIndicator, `astral_gameplay.sk`): cada golpe de un jugador a
  un mob muestra `-2.500` y `❤ 9.000 / 11.500` arriba del mob por un segundo. Colores: blanco golpe,
  cian rayo, dorado explosión, amarillo flecha.
- **Corazones al pegar:** Minecraft tira uno por cada 2 de daño (miles por golpe). La partícula `damage`
  del resource pack es transparente para que no se vean.
- **Maná de bastones:** 50 / 100 / 180 / 300 / 500 (antes 20 / 40 / 70 / 110 / 180).

## Mobs

- Cada mob hostil nuevo (más golems y vex de MythicMobs; nunca los invulnerables) recibe un tier al
  aparecer (`mob/roll` del datapack, cada segundo) y la etiqueta `astral.mt#`.
- **Mundo:** tier = mejor arma Astral del inventario del jugador más cercano (128 bloques, score
  `astral.wt`): 86% ese tier, 4% uno más, 10% uno menos. Sin arma Astral: mob vanilla.
- **Mazmorras:** tier fijo: mina 1, bosque 2, tumba 3, cumbre 4, forja 5, santuario 5 con ×1,5 de vida.
- **Élites:** misma probabilidad que antes (6% + 5% por amenaza); en mazmorras la mitad. Multiplican la
  vida ya escalada (Élite ×1,9 … Astral ×5).
- **Nombre con vida:** `[T3] Elite Zombi ❤ 11.500`, visible sobre la cabeza sin tener que pegarle. La vida
  se actualiza cada segundo en mobs a 32 bloques de un jugador (`mob/vida`).
- La vida del jugador es **normal**. El **daño de los mobs sube ×1,5 por tier** (T1 ×1,5, T2 ×2,25, T3 ×3,4,
  T4 ×5,1, T5 ×7,6 sobre su daño normal; `DANO_MOB`, modificador `attack_damage` en `mob/t#`). Pedido del dueño
  (08/11/2026): un mob T5 casi no lastimaba a un jugador T3.
- Tier fijo también en los mundos actuales de mazmorra: `cumbre_hielo` 4, `forja_volcano` 5, `santuario_interstellar` 5.
- Se sacó **LevelledMobs** (subía la vida por distancia) y **DamageIndicator** (lo reemplaza el indicador).

## Maná y bastones (referencia Hypixel SkyBlock, 09/11/2026)

Todo sale de `escala.py` (`MANA_*`, `HECHIZO`, `REGEN_*`).

- **Base:** 100 de maná para todos y 2 por segundo de recuperación (en Hypixel: 100 + Inteligencia, 2% del
  máximo por segundo). Se configura en `plugins/AuraSkills/stats.yml` (`traits.max_mana.base` y
  `traits.mana_regen.base`, ver `build/gameplay/AuraSkills/stats-mana.txt`) y `skills reload`.
- Cada objeto que da maná también da el **2% de ese maná por segundo** de recuperación (×(1 + mregen%) en las
  piezas de Mago), así la recuperación queda en ~2% del máximo como en Hypixel.
- **Set de Mago completo** T1→T5: 100 / 200 / 350 / 600 / 1.150 (T3 ≈ Wise Dragon, T5 ≈ Storm).
- **Bastones** T1→T5: +100 / 180 / 250 / 300 / 350 de maná (Spirit Sceptre 300, Hyperion 350).
- **Hechizo del bastón:** cuesta 30 / 50 / 90 / 150 / 200 de maná (lo cobra `special_weapons.sk` antes de
  llamar a `astral:spell/cast`). Daño base = espada del mismo tier ×1,2 (120 / 600 / 3.000 / 15.000 / 75.000),
  más el % de daño mágico del bastón y la armadura de Mago. Antes el hechizo no usaba la escala de tiers
  (pegaba 5-14 a mobs de miles de vida).
- **Armas especiales:** Transmisión Instantánea 50 (Aspect of the End), Danza del Ender sin maná y 15 s de
  recarga (Shadow Fury), Onda Sísmica 100, Estallido 30.
- `ITEM_VERSION = 12`: los objetos se actualizan solos.

## Servidor (Aternos)

- `spigot.yml`: topes de `maxHealth` (1.000.000.000) y `attackDamage` (10.000.000) subidos: hacen falta
  para la vida real enorme. `log-named-deaths: false` porque ahora casi todos los mobs tienen nombre.
- Datapack con `ITEM_VERSION = 8`: los objetos se actualizan solos conservando mejoras.
- Resource pack nuevo (partícula transparente): actualizar URL y SHA-1 en `server.properties`.
