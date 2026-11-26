# Clases nuevas: Segador, Invocador y Asesino (22/11/2026)

**DESPLEGADO 22/11 16:26** (pack 76fc66d9, sobre nave-22-11 0a1a1ce6). Fuente unica `datapack-src/clases.py` (numeros, armaduras, libros, datos del plugin) y
`datapack-src/runtime/AstralClases.java` (habilidades). Modelo de la invocacion: `mobs/creatures_tanda3b.invocacion`.

## Que cambia en el juego

- **Guadanas I-X** pasan a ser del **Segador** (requisito Combate en vez de Hechiceria, mismo nivel). Pierden el
  "golpe en cono" del datapack: el area ahora es el barrido en semicirculo de AstralClases (60% del golpe a hasta
  8 mobs, radio 3,5). Cada baja con guadana da 1 alma (hasta 10) y cura 0,5% de la vida. Clic derecho con 10 almas
  (8 con el set completo): **Cosecha** = giro de 360 grados, radio 5, 250% del dano del arma a hasta 12 mobs, cura
  1% por alma gastada. La Guadana Umbria (especial) no cambia.
- **Cuchillos I-X** pasan a ser del **Asesino**: +50% por la espalda (en arenas +15%, lo suma `astral_pvp`),
  veneno 8% del golpe por segundo durante 3 s (solo mobs), agachado + clic derecho = invisible 2 s con recarga de
  20 s (los mobs comunes lo pierden de vista, los demas no ven la armadura). **Nunca en arenas/duelos.**
- **Libros del Invocador** T1/3/5/7/9/10 (nuevos): clic derecho invoca 1/2/2/3/3/4 esqueletos por 20 s.
  Cuestan 80/180/400/650/1100/1400 de mana, recarga 30 s (barra violeta arriba, como al picar vetas).
  Cada uno: 25% de la vida de un set completo del tier, la defensa del set del tier y 30% del golpe de la espada.
  Atraen a los mobs que te persiguen (50% por segundo). Jefes: les pegan x3 y reciben la mitad.
  Las bajas que hacen cuentan como tuyas (botin, XP, almas).
  Arriba de cada una: "Invocacion de <jugador> ❤ vida / maxima" (se actualiza en cada golpe y cada medio segundo).
- **Armaduras**: Segador T1/3/5/7/10, Invocador T1/3/5/7/9/10, Asesino T1-T10 (modelos elegidos por el dueno).
  Recetas en la Forja: la pieza anterior de la clase + los materiales del Berserker/Mago/Arquero de cada tier
  que se saltea. Guia del datapack: botones Segador, Invocador y Asesino.
- `ITEM_VERSION` 27: guadanas y cuchillos que ya tengan los jugadores se actualizan solos.

## Archivos a instalar

| Local | Destino |
|---|---|
| `build/AstralRPG-Items.zip` | datapack del mundo (**comparar antes con el del server**: memoria manzanas-21-11) |
| `build/clases/AstralClases.jar` | `plugins/AstralClases.jar` (nuevo) |
| `build/clases/MythicMobs/astral_clases.yml` | `plugins/MythicMobs/mobs/astral_clases.yml` |
| `build/models/astral_invocacion.bbmodel` | `plugins/BetterModel/models/astral_invocacion.bbmodel` |
| `build/gameplay/astral_gameplay.sk` | `plugins/Skript/scripts/astral_gameplay.sk` (etiqueta `astral.espalda` en PvP) |
| FINAL privado `entregas/clases-22-11/AstralRPG-Textures.zip` | R2 con `tools/subir_pack_r2.py` + `resource-pack-sha1` |

El FINAL se arma encima de `manzanas-21-11` (3e616f39) con `python datapack-src/deploy_clases.py`
(antes `python datapack-src/armaduras_t6_10.py <ids>` para hornear las armaduras).

Requiere reinicio (JAR nuevo y datapack). Despues: `bettermodel reload` si el modelo no aparece.

## Libros 3D

Los hace el dueno. Cada libro usa el modelo `astral:libro_invocador_<tier>`; hoy el FINAL apunta al libro vanilla.
Para cambiarlo basta reemplazar `assets/astral/items/libro_invocador_<tier>.json` en `deploy_clases.py`.

## Probado

- `tools/probar_clases_paper.py` (Paper local): datapack carga, items nuevos salen con nombre, AstralClases arranca,
  la invocacion aparece por MythicMobs y un mob tier 5 le pega con la escala (2,5 x 400 = ~1.000).
- Sin cliente real: falta probar barrido, almas, Cosecha, invisibilidad, invocar con libro, provocacion y PvP.

## Pendiente

- Guia Astral de cofre (menus g_*): agregar las tres clases.
- Libros 3D del dueno.

## Despliegue (22/11 16:26)

- Datapack: el del server + solo lo de clases y la version 27 (`.local/deploy-clases/AstralRPG-Items.zip`). Se dejaron
  como estaban en el server: quest/*, dialog/cronista/*, loot_table/guia.json, kit/historia, kit/consumibles,
  player/def y atlas/iconos.json (el repo trae trabajo de otras tandas sin desplegar: Cronista, premios de historia).
- El modelo de la invocacion necesita sus assets de BetterModel en el pack: se bajaron de
  `plugins/BetterModel/build/assets/bettermodel/*/astral_invocacion*` a `pack-source/bettermodel` y deploy_clases.py los suma.
- Consola: Done, AstralClases 1.0.0, 215 mobs, 25 scripts, sin errores.
