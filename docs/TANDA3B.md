# Tanda 3b v4: esqueletos anteriores y Creeper Nuclear conservado

Entrega sin desplegar. Los cinco esqueletos vuelven exactamente a `315ab9d` (16 texeles/bloque).
El Creeper Nuclear conserva la version de `1008f75` (32 texeles/bloque).
Instalacion y archivos exactos: [manifiesto](../build/deploy/tanda3b.md).
Santuario, Forja, controladores, cantidades y pesos de oleadas no cambian.

## Restauracion e identidad

`creatures_tanda3b.py` restaura la geometria, pintura, proporciones, UV y animaciones de los
cinco esqueletos de `315ab9d`. `DungeonModel` mantiene la densidad anterior; `NuclearModel`
aisla la pintura y densidad de v3 para que el creeper no cambie. Se restaura la escala vanilla
y el step_height de cada esqueleto en MythicMobs; se retira la luz `pid=gem` que no existia
antes. El orbe del nigromante conserva su brillo original.

Se regeneraron los seis bbmodel desde el generador y se compararon byte a byte mediante
`git show`: cinco modelos y 122 assets BetterModel identicos a `315ab9d`; modelo nuclear
y 15 assets identicos a `1008f75`. Los assets son las conversiones ya versionadas, restauradas
sin una nueva conversion. Se retiraron los 42 assets de esqueletos agregados por v3, incluida
la gema y las piezas adicionales de torso y baston. Las definiciones completas de mobs y
skills de esqueletos coinciden con `315ab9d`; las nucleares coinciden con `1008f75`.
El Skript nuclear no cambia. No reaparecen el modelo ni los assets del creeper fantasma.

SHA-256 de los modelos (incluyen texturas embebidas y animaciones):

| Modelo | SHA-256 |
|---|---|
| `astral_creeper_nuclear` | `a941d593d3a803df66c174f20173290bd32da12193d51d21bc0d9afe8204439d` |
| `astral_esq_arquero` | `b7c59f4671b56331849698c5c0ea88a61502340da2b1dc3c7385ffb22a8502d9` |
| `astral_esq_escudero` | `0397cffc90bd3a1682fc1a921744606c404baab6080fdd6ea43874b13624764b` |
| `astral_esq_espadachin` | `ae5cbf811631a3e137260df7ad09fca6c8f75c13b50e8fd18ddf5e7f3ae8aa3b` |
| `astral_esq_guardian` | `cab9c7f20ff1200196169e5bf3dc0516638cfeb97940765f3304cbe27b73b182` |
| `astral_esq_nigromante` | `2b1c5e05b2a23dd550f174b6c9bf1807f53e93b065960078e4a47d71e767608e` |

## Vistas y pack

Se rehizo `build/previews/tanda3b.png` con los modelos propios a escala compartida con un
jugador de 1,8 bloques. Se regeneraron las seis comparaciones de frente, costado, 3/4,
angulo de referencia y espalda. Esas comparaciones incluyen referencias de terceros:
permanecen locales e ignoradas; no se publican. La lamina conjunta fue inspeccionada.

Pack: **17,716,907 bytes**. SHA-1: **`940383c3591d889686273c33edacfc4ca940620e`**.

## Creeper Nuclear (sin cambios respecto de 1008f75)

Modelo opaco con silueta vanilla, camuflaje oliva/marron original, rostro amarillo
sobre fondo rojo oscuro, cuatro patas con franjas de peligro y trebol nuclear posterior.
Paleta: `#2f4a1c`, `#4c6b25`, `#6f8a2f`, `#5a3d1a`, `#c9a227`; rostro
`#ffd21f`/`#ffe866` sobre `#7a1010`. Atlas 128x128.

ID `astral_creeper_nuclear`, nombre `&e&lCreeper Nuclear`.
`NUCLEAR_CHANCE=30`, `NUCLEAR_DAMAGE=2`, `NUCLEAR_POWER=2`, `NORMAL_POWER=3`.
Reemplaza el 30% de apariciones NATURAL solo en el mundo Bukkit `world`.
Potencia 6 y dano x2 antes del tier y la defensa, etiqueta `astral.nuclear`.
Cara 15/15 en reposo; cuerpo con luz ambiental, 15/15 al hincharse.
Particulas verdes y amarillas suaves; refuerzo al preparar la explosion.

Si se viene de v2, retirar solamente `plugins/BetterModel/models/astral_creeper_fantasma.bbmodel`
y aplicar la migracion de mobs, skills y Skript del manifiesto. El datapack no cambia.
Si v3 ya esta instalada, solo subir cinco modelos de esqueletos, skills `tanda3b.yml`, pack
y SHA-1; apagar para reemplazar y reiniciar. No recrear controladores ni sustituir mundos.

## Verificaciones y pendientes

Pasaron **164 pruebas** (53,349 s), `python verify.py` y `git diff --check`.
ZIP integro: 137 assets identicos a sus fuentes; todas las referencias de modelos
resueltas; todo el contenido ajeno a los esqueletos identico al pack de `1008f75`. La prueba de identidad
fija SHA-256 de los seis modelos; se conservan las pruebas nucleares, de probabilidades,
oleadas, limites de mundo, potencia 6, dano x2, animaciones y ausencia de assets fantasma.
Se verifica que cada asset del pack coincida con la fuente y sus referencias se resuelvan.

En v4 no se inicio un servidor de prueba ni un cliente. La conversion y prueba real con
Paper 26.1.2, BetterModel 3.6.0, MythicMobs 5.13.0 y Skript 2.17.1 fueron realizadas para
v3 segun el registro anterior; no son una nueva prueba de esta restauracion.

Pendientes: revision visual del dueno, cliente Minecraft (animaciones, aspecto nocturno y
combate), reemplazo natural real y protecciones de explosion en produccion, subida R2,
instalacion, reinicio y revision de consola. No desplegado en Empower ni Aternos.
