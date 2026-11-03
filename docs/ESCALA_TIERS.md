# Escala por tier (números grandes, mostrados)

Pedido del dueño (03/11/2026): que cada tier se sienta como un salto enorme. Todo sale de
`datapack-src/escala.py`; para cambiar un número se edita ahí y se regenera (`python build.py`,
`python gameplay.py`, `python build_pack.py pack-source`).

**Los números reales quedan chicos** (como Minecraft) y lo que se **ve** es grande. Primero se
probó con daño y vida reales gigantes, pero Minecraft tira un corazón oscuro por cada 2 de daño
(miles por golpe, lag) y no puede mostrar la vida de mobs con cientos de miles de corazones.

## Números

| Tier | Daño mostrado (espada) | Vida mostrada de un mob de su tier (zombi) | Golpes | Vida real del mob |
|---|---|---|---|---|
| 0 (sin arma Astral) | vanilla | vanilla | — | ×1 |
| 1 | 100 | 500 | 5 | ×1,65 |
| 2 | 500 | 2.400 | 4,8 | ×1,7 |
| 3 | 2.500 | 11.500 | 4,6 | ×2,01 |
| 4 | 12.500 | 55.000 | 4,4 | ×2,08 |
| 5 | 62.500 | 262.500 | 4,2 | ×2,52 |

- **Lo mostrado** = lo real × `FACTOR_MOSTRADO` del tier del mob golpeado (×15 en T1 … ×5.208 en T5).
- **Armas:** el daño real no cambia. Las cuerpo a cuerpo muestran "Daño: 2.500" en la descripción (se
  oculta el "8,75 de daño" vanilla); bastones y arcos muestran su daño en números del tier.
- **Indicador de daño** (reemplaza DamageIndicator, `astral_gameplay.sk`): cada golpe de un jugador a
  un mob muestra `-2.500` y `❤ 9.000 / 11.500` arriba del mob por un segundo. Colores: blanco golpe,
  cian rayo, dorado explosión, amarillo flecha.
- **Corazones al pegar:** la partícula `damage` del resource pack es transparente.
- **Maná de bastones:** 50 / 100 / 180 / 300 / 500 (antes 20 / 40 / 70 / 110 / 180). Es real.

## Mobs

- Cada mob hostil nuevo (más golems y vex de MythicMobs; nunca los invulnerables) recibe un tier al
  aparecer (`mob/roll` del datapack, cada segundo) y la etiqueta `astral.mt#`.
- **Mundo:** tier = mejor arma Astral del inventario del jugador más cercano (128 bloques, score
  `astral.wt`): 86% ese tier, 4% uno más, 10% uno menos. Sin arma Astral: mob vanilla.
- **Mazmorras:** tier fijo: mina 1, bosque 2, tumba 3, cumbre 4, forja 5, santuario 5 con ×1,5 de vida.
- **Élites:** misma probabilidad que antes (6% + 5% por amenaza); en mazmorras la mitad. Multiplican la
  vida ya escalada (Élite ×1,9 … Astral ×5).
- **Nombre:** `[T3] Elite Zombi` / `[T2] Minero Corrupto`.
- El daño de los mobs al jugador y la vida del jugador son **normales**.
- Se sacó **LevelledMobs** (subía la vida por distancia) y **DamageIndicator** (lo reemplaza el indicador).

## Servidor (Aternos)

- `spigot.yml`: topes de `maxHealth` y `attackDamage` subidos (no hacen falta con la vida real chica,
  pero no molestan). `log-named-deaths: false` porque ahora casi todos los mobs tienen nombre.
- Datapack con `ITEM_VERSION = 7`: los objetos se actualizan solos conservando mejoras.
- Resource pack nuevo (partícula transparente): actualizar URL y SHA-1 en `server.properties`.
