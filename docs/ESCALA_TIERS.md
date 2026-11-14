# Escala por tier (números grandes reales)

Santuario Azeroth preparado, sin desplegar: `santuario_azeroth` conserva tier fijo 5
con x1,5 de vida del mundo. Los atributos propios de los Ancestrales siguen intactos.
Skript reconoce tambien el nombre Bukkit `world_minecraft_santuario_azeroth`.
Interstellar conserva sus excepciones como copia. Ver [entrega](../build/deploy/santuario-azeroth.md).

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
- **Mazmorras:** tier fijo: bosque 1, mina 2, tumba 3, cumbre 4, forja 5, santuario 5 con ×1,5 de vida.
- **Élites:** misma probabilidad que antes (6% + 5% por amenaza); en mazmorras la mitad. Multiplican la
  vida ya escalada (Élite ×1,9 … Astral ×5).
- **Nombre con vida:** `[T3] Elite Zombi ❤ 11.500`, visible sobre la cabeza sin tener que pegarle. La vida
  se actualiza cada segundo en mobs a 32 bloques de un jugador (`mob/vida`).
- La vida del jugador es **normal**. El **daño de los mobs sube ×1,5 por tier** (T1 ×1,5, T2 ×2,25, T3 ×3,4,
  T4 ×5,1, T5 ×7,6 sobre su daño normal; `DANO_MOB`, modificador `attack_damage` en `mob/t#`). Pedido del dueño
  (08/11/2026): un mob T5 casi no lastimaba a un jugador T3.
- Tier fijo también en los mundos actuales de mazmorra: `cumbre_hielo` 4, `forja_volcano` 5, `santuario_interstellar` 5.
- Se sacó **LevelledMobs** (subía la vida por distancia) y **DamageIndicator** (lo reemplaza el indicador).

## Vida, defensa y daño de mobs (referencia Hypixel SkyBlock, 09/11/2026)

Todo sale de `escala.py` (`VIDA_*`, `DEFENSA_SET`, `DANO_GOLPE`).

| Tier | Vida con set completo | Defensa del set | Daño que frena | Golpe de un mob común de ese tier |
|---|---|---|---|---|
| T1 | 300 | 50 | 33% | 55 |
| T2 | 550 | 100 | 50% | 120 |
| T3 | 1.000 | 200 | 67% | 300 |
| T4 | 3.000 | 350 | 78% | 700 |
| T5 | 8.000 | 500 | 83% | 1.000 |

- **Vida:** 100 de base (`player/vida_base`, una vez por jugador) + `VIDA_PIEZA` por pieza. Los % de vida de cada
  clase siguen (Berserker más, Mago menos). El Herrero suma +0,5% … +5% de vida por pieza.
- **Defensa:** la armadura Astral ya no da armadura vanilla; da `astral.def` (reparto 15/40/30/15%, ± el % de
  defensa de la clase). El datapack la suma en `astraldef` (barra) y en etiquetas `astral.db0..db11` para Skript.
  Daño recibido de golpes, flechas, explosiones y PvP = daño × 100 / (defensa + 100).
- **Daño de mobs:** `astral_gameplay.sk` multiplica golpes, flechas y explosiones de un mob con tier por
  `DANO_MOB` (= `DANO_GOLPE` / 2,5, el golpe de un zombi en fácil). Mobs sin tier dentro de una mazmorra
  (jefes de MythicMobs) usan el tier de la mazmorra.
- **Caídas, lava, ahogo, mobs sin tier y PvP:** × (vida máxima / 20): pegan lo mismo en proporción que en
  Minecraft normal. La regeneración natural, las pociones y el robo de vida curan igual en proporción.
- Golpes para matar a un jugador del mismo tier: T1 8, T2 9, T3 10, T4 19, T5 48. Un T5 mata a un T3 en 3-4.

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

## Tanda 2: cajas medidas y vida de jefes

Vida: Bosque 12.500; Minas 72.000; Tumba 460.000; Cumbre 2.475.000; Forja 13.125.000. Se genera desde `EZ_JEFE × VIDA_REF` en `escala.py`.

Oleadas: 87% tier de la mazmorra, 3% uno mas y 10% uno menos (limites 1–5). Mundo abierto conserva 86/4/10. Jefes del mundo y Ancestrales fuera del Santuario: 25 EZ del tier calculado por `mob/tier_mundo` al aparecer; sin arma o sin jugador cercano, T1. No se vuelven a curar al cargar chunks. Santuario conserva sus atributos previos.

Medicion de todas las esquinas de los cubos existentes, con rotaciones, en pose de reposo. Se prioriza el alto: una sola escala no puede igualar proporciones distintas entre modelo y entidad. El ancho puede diferir. Las animaciones tampoco tienen una caja dinamica. Mascotas, monturas, NPC y estatuas quedan excluidos.

| Mob | s | Alto modelo (bloques) | scale | Alto caja vanilla |
|---|---:|---:|---:|---:|
| astral_mapache | 1 | 1.006 | 1.4375 | 1.006 |
| astral_pinguino | 1 | 1.556 | 2.22321 | 1.556 |
| astral_espantapajaros | 1 | 2.062 | 2.57812 | 2.062 |
| astral_espantapajaros_elite | 1.35 | 2.784 | 3.48047 | 2.784 |
| astral_abejorro | 1 | 1.038 | 1.29688 | 1.038 |
| astral_abejorro_elite | 1.35 | 1.401 | 1.75078 | 1.401 |
| astral_arana | 1 | 0.975 | 1.08333 | 0.975 |
| astral_arana_elite | 1.35 | 1.316 | 1.4625 | 1.316 |
| astral_cara | 1 | 1.675 | 3.35 | 1.675 |
| astral_cara_elite | 1.35 | 2.261 | 4.5225 | 2.261 |
| astral_momia | 2 | 4.100 | 2.10256 | 4.100 |
| astral_momia_ancestral | 2 | 4.100 | 2.10256 | 4.100 |
| astral_yeti | 2 | 7.000 | 3.18182 | 7.000 |
| astral_yeti_ancestral | 2 | 7.000 | 3.18182 | 7.000 |
| astral_golem_forja | 2 | 6.062 | 2.24537 | 6.062 |
| astral_golem_forja_ancestral | 2 | 6.062 | 2.24537 | 6.062 |
| astral_cangrejo | 2 | 2.825 | 3.13889 | 2.825 |
| astral_cangrejo_elite | 1.35 | 1.907 | 2.11875 | 1.907 |
| astral_cangrejo_ancestral | 2 | 2.825 | 3.13889 | 2.825 |
| astral_chaman | 2 | 5.125 | 2.6282 | 5.125 |
| astral_chaman_ancestral | 2 | 5.125 | 2.6282 | 5.125 |
| astral_yeti_cumbre | 8 | 28.000 | 12.7273 | 28.000 |
| astral_golem_forja_mazmorra | 8 | 24.250 | 8.98148 | 24.250 |
| astral_mina_guardian | 2 | 6.062 | 2.24537 | 6.062 |

Yeti de Cumbre: modelo de 16 x 28 x 8,8 bloques (`s=8`, cuatro veces el normal y el Ancestral). Caja RAVAGER de 24,818 x 28 con `scale=12,727273`, por debajo del tope 16; coincide el alto, no el ancho. Golem de Forja: modelo 12,9 x 24,25 x 12,9; `scale=8,981481`, priorizando el alto. Vista previa: `build/previews/tamanos-jefes.png`.

## Tiers 6 a 10 (14/11/2026)

Pedido del dueño: armaduras elegidas de mods (casco 3D + cuerpo plano, arte solo en el pack FINAL privado).
Todo sale de `escala.py` y `items_t6_10.py`. Entrega: `build/deploy/tiers6-10.md`.

| Tier | Daño espada | Vida mob (zombi) | Vida set completo | Defensa set | Golpe mob común |
|---|---|---|---|---|---|
| T6 | 312.500 | 1.250.000 | 15.000 | 650 | 2.800 |
| T7 | 1.562.500 | 5.937.500 | 25.000 | 800 | 5.600 |
| T8 | 7.812.500 | 28.125.000 | 40.000 | 1.000 | 11.000 |
| T9 | 39.062.500 | 132.812.500 | 65.000 | 1.250 | 22.000 |
| T10 | 195.312.500 | 625.000.000 | 100.000 | 1.500 | 40.000 |

- **Forja:** cada pieza/arma de tier N = la del tier N-1 + 4 del material del tier (desde T8 también 2 del anterior)
  + un material de clase. Materiales: Fragmento de Ocaso (T6), Esquirla de Eclipse (T7), Núcleo de Supernova (T8),
  Esencia del Vacío (T9), Corazón del Fin (T10). Nunca aparecen en cofres.
- **Drops:** un mob de tier t puede soltar el material de cada tier 6..t: común 1,2%, élite 12%, jefe de mundo seguro.
  Élites T5 4% y jefes de mundo T5 50% de Fragmento de Ocaso (primer paso desde T5).
- **Mundo:** el tier sigue a la mejor arma/armadura del inventario (hasta 10). La amenaza para élites queda topeada
  en 8 (la probabilidad de élite no sube más que con T5).
- **Mazmorra Infinita:** Tier I-V en la ventana ilustrada; la sexta tarjeta abre `infinita_tier_alto` (VI a X y X+,
  que sigue subiendo +25%).
- **Números que pasan el tope de los puntajes (2.147 millones):** el cartel de vida pasa a miles desde 2.000 millones,
  `fx/victim_pct` usa otra escala desde 20 millones de vida máxima y el hechizo de bastón calcula en miles desde el millón.
- **Armas T6-T10:** se ven como el arma T5 de su familia hasta que el dueño elija modelos (`ARMA_MODELO`).
- **Huecos sin modelo:** Berserker T6 y Arquero T8/T9 se ven como el T5 de su clase (`VISUAL` en `items_t6_10.py`).
- `spigot.yml` necesita `maxHealth.max` y `attackDamage.max` en `1.0E12`.
