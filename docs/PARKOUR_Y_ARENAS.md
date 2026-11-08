# Mini juegos (parkour, droppers, Color Escape) y Arenas PvP

## Mini juegos (08/11/2026)

El selector de parkour se llama **Mini juegos** (`/minijuegos` o `/parkour`, aldeano y botones de
`/menu` y Portales). Mapas: Spiral, **Spiral 2**, **Paradise 3**, **Color Escape** y dos droppers
(**The Easiest Dropper** y **The Dropper (H4rs)**), cada uno con un submenú de 10 niveles.

- **Lo más vanilla posible:** al entrar se guardan el inventario completo (41 casillas) y la vida extra
  (modificador `astral:minijuego` que deja la vida en 20), y se borran los efectos. Todo se devuelve al
  salir a cualquier mundo que no sea mini juego. Variables persistentes `{astral.mj.inv::uuid::*}`:
  sobreviven a desconexiones y reinicios. Las arenas PvP no cambian.
- **Modo trabado:** en un mini juego todos quedan en aventura (se fuerza cada 10 ticks); solo un OP
  puede quedarse en creativo para revisar el mapa.
- **Nada crece solo:** `random_tick_speed 0` en mini juegos, arenas y mazmorras (chorus,
  enredaderas, cultivos, kelp... arruinarían los mapas). Las expediciones ya lo tenían.
- **Daño vanilla** (pedido del dueño, 08/11/2026): en parkour y Color Escape se recibe daño y se
  puede morir; al reaparecer se vuelve a la llegada del mapa elegido. Comida llena (la vida se
  regenera sola). La vida se revisa cada 10 ticks: si las skills la suben al reaparecer, se vuelve a 20.
- **Droppers:** daño por caída = te estrellaste, volvés al inicio del nivel. Caer al agua por debajo de
  `finish_y` = nivel completado y pasás al siguiente (el último te manda al lobby). Easiest: 60 bloques
  bajo la salida; H4rs: Y 20 (tiene agua decorativa a mitad de caída). Las salidas salen de los command
  blocks de cada mapa (ver `docs/IDEAS.md`). Easiest no tiene agua cerca de varias salidas: probar
  cada nivel y ajustar `finish_y` si hace falta.
- **Color Escape** necesita sus command blocks. `minijuegos_mapas.py` reescribe sus 372 comandos:
  `@a`/`@r` → `@p`; `execute as/at @a` y todo `@e` → a menos de 300 bloques. Así ningún comando
  toca otros mundos ni a otros jugadores (había `clear`, `gamemode` y `kill @e[type=wither]`).
  Conserva cofres y entidades. En 26.1 ya no existe `enable-command-block`: alcanza con
  `command_blocks_work true` solo en `colorescape`. Además `commands.yml` tiene
  `command-block-overrides: ['*']`: sin eso Essentials se queda con `xp`, `tp`, `clear`,
  `gamemode`... dentro de los command blocks (en la primera prueba tiró miles de errores de `xp`).
- **Instalado en Empower (08/11/2026):** mundos `parkour_spiral2`, `parkour_paradise3`,
  `colorescape`, `dropper_facil` y `dropper_h4rs` creados con Multiverse; sus `region/` (y
  `entities/` de Color Escape) copiados desde `mapas-subir/` con el servidor apagado. Se cargaron
  las 5 llegadas y el bloque de abajo coincide con el mapa. Falta probar jugando.
- **Droppers corregidos (prueba del dueño, 08/11/2026):** en el original cada nivel empezaba parado
  sobre una placa (vidrio, piedra, lana) que quitaban sus command blocks. Los niveles que fallaban
  salen 2 bloques debajo de la placa; se gana al caer al agua o al quedar parado bajo la Y de llegada
  (fondos de slime o alfombra). Del fácil se sacaron Small World, Anatomy y Rainbow (sin la lógica
  original no son droppers). Al entrar a cualquier mini juego se borran los efectos del anterior.
- **Color Escape de a uno y con reinicio:** si alguien está jugando, el siguiente no entra. Cuando el
  último sale, `astral_ce_clonar` copia encima la versión limpia guardada a 3000 bloques al este
  (zona `x -32..120, y -24..4, z -28..308`, en tandas de 7 de profundidad), borra objetos tirados y
  reinicia `colorEscape` y `advancement`. `/colorescape guardar` (una vez, con el mapa sin jugar) y
  `/colorescape reiniciar`.
- **Datapack propio de Spiral 2 y Paradise 3** (de Hielke Maps): sin él no hay largada, checkpoints
  ni mecanismos. `python minijuegos_datapack.py` genera en `.local/mapas/subir/<mundo>-datapack.zip`
  una copia que solo actúa en su mundo: namespaces con prefijo (`pp3_main`, `sp2_time`...), puntajes
  con prefijo (`pp3_time`), todo `@a/@e/@p/@r/@n` con `predicate=<pp>_main:astral/en_mapa`, tick,
  load y `schedule` dentro de `execute in minecraft:<mundo>`, etiquetas de bloque mudadas a su
  namespace. Se quitan el filtro que bloqueaba recetas y logros de todo el server, `setdisplay` y
  `team`; los logros solo se cumplen en el mapa y no se anuncian. Se recrean los puntajes del
  `scoreboard.dat` del mapa, se activa el modo servidor del autor (`#is_server temp 1`) y queda
  cargado el chunk del marcador `console` (corre los temporizadores). Al salir de un mini juego,
  Skript llama `<pp>_main:astral/salir` (marcas, puntajes, efectos y objetos del mapa).
  Estos dos mundos conservan entidades y command blocks (traducidos igual que el datapack).
  **Instalado (08/11/2026)** como carpetas `world/datapacks/parkour_paradise3-datapack/` y
  `parkour_spiral2-datapack/` (en carpeta se puede corregir un archivo suelto sin volver a subir
  todo). Arranque sin funciones fallidas; `console` cargado y modo servidor activo en ambos.
  Falta probar jugando la largada, los checkpoints y los niveles con mecanismos.
- **Trampa (08/11/2026):** el `load` de los datapacks corre antes de que Multiverse cargue los mundos,
  y `execute in minecraft:<mundo>` falla en silencio: las tareas repetidas (largada, checkpoints,
  registro del jugador) nunca arrancaban. Ahora `astral/tick` llama a `astral/start` una sola vez,
  cuando el mundo ya existe (`#arranco <pp>_astral`). En Paradise la largada la da `player/tick_2`
  (caja `x -35..-33, y 95..97, z 805..807`), no el end gateway.
- **Color Escape:** su primer acertijo pide poner bloques de hierro en `3 -13 7` y `-3 -13 7` para
  abrir la puerta: el mundo permite `build`, `block-place` y `block-break` (en aventura solo se
  ponen los objetos que el mapa marca). `command_block_output false` en los mapas con command
  blocks (si no, a los OP les llena el chat). El mapa pasa a aventura a todo el que no tenga `dev`;
  los OP llevan la marca `astral.op` en los mini juegos y esos 4 command blocks la respetan.
- **Mapas 26.2** (Spiral 2 y Paradise 3): se revisaron todos sus bloques, block entities y entidades;
  ninguno es nuevo de 26.2. Se baja `DataVersion` a 4790 (26.1.2) en `level.dat` y en cada chunk.
- Los mundos preparados quedan en `.local/mapas/subir/` (no se publican).


`datapack-src/minijuegos.py` contiene las listas `PARKOURS` y `ARENAS`. Desde
`datapack-src`, ejecutar `python menus.py`: genera los selectores, el Skript,
los NPC y el archivo de despliegue, incluido `astral_gameplay.sk` actualizado.
No hace falta cambiar el datapack ni el resource pack para esta tarea.

El aldeano `astral_npc_arena` se reutiliza: abre el selector y se reubica a
`127.5 100 193.529`. El nuevo `astral_npc_parkour` va a `121.5 100 193.529`.
Quedan a los lados del Guardián de los Portales. Las posiciones están en
`NPC_POSITIONS`; no se agrega una segunda definición del aldeano Arena.
Los comandos de creación están en el archivo de despliegue, separado del
`build/lobby/comandos.txt` que tenía trabajo previo.

## Mundos privados y coordenadas

Los originales y las copias preparadas viven en `.local/mapas/`, ignorado por Git.
`python minijuegos_mapas.py` prepara:

| Origen privado | ZIP listo para subir | Mundo nuevo |
|---|---|---|
| `.local/mapas/parkour_spiral.zip` | `.local/mapas/subir/parkour_spiral.zip` | `parkour_spiral` |
| `.local/mapas/arenapvp_3.zip` | `.local/mapas/subir/arenas_tft.zip` | `arenas_tft` |

Cada ZIP tiene una única carpeta con ese nombre, `level.dat` y `region/*.mca`.
Se excluyen HTML, TXT, schematics, jugadores guardados, entidades, datapacks y
datos del minijuego original. Se limpian command blocks, spawners y su lógica,
y se vacían los inventarios originales. Se conserva la geometría del escenario.
Los originales no se modifican. Ninguno de estos archivos de terceros se publica.

| Selector / ID | Llegada por defecto X Y Z yaw pitch | Estado |
|---|---|---|
| Parkour / `spiral` | `0.5 -11 -1.5 0 0` | Spawn NBT: `Data.spawn.pos=[0,-11,-2]`, yaw/pitch 0; centrado en el bloque |
| Arena / `clasica` | 25 puntos interiores, Y=73 | Conserva exactamente la lista de la arena existente |
| Arena / `tft1` | `-286.5 143 -550.5 0 0` | Verificada: centro del piso en Y=142 y dos bloques de aire |
| Arena / `tft2` | `-286.5 139 -282.5 0 0` | Verificada: centro del piso en Y=138 y dos bloques de aire |
| Arena / `tft3` | `-286.5 139 -14.5 0 0` | Verificada: centro del piso en Y=138 y dos bloques de aire |

TFT es un mundo 1.12.2 cuyo spawn NBT es `0 64 0` (el TXT propone `0 100 0`).
El schematic mide 263 × 256 × 801 y contiene tres grupos separados en Z:
`0..253`, `274..527`, `547..800`; `WEOrigin=(-418,0,-683)`.
Claude verificó las regiones 1.12 de `.local/mapas/subir/arenas_tft.zip`: cada
arena tiene un piso plano de 61 × 61 bloques y las llegadas de la tabla quedan
en el centro, con dos bloques de aire arriba. Los tres botones TFT permiten
viajar con estas llegadas por defecto. `/astralpunto` es una sobrescritura
opcional y los puntos ya guardados conservan prioridad. No se implementó cronómetro/final.

## Instalación en Aternos

La lista completa de archivos locales, destinos y comandos está en
[`build/minijuegos/despliegue.txt`](../build/minijuegos/despliegue.txt).
Debe continuarla quien tenga navegador y sesión del dueño. No hay APIs privadas.

### Actualización TFT con los mundos ya instalados

Copiar únicamente estos archivos con el editor Files:

| Archivo local | Destino |
|---|---|
| `build/minijuegos/astral_minijuegos.sk` | `plugins/Skript/scripts/astral_minijuegos.sk` |
| `build/menus/DeluxeMenus/gui_menus/arenas.yml` | `plugins/DeluxeMenus/gui_menus/arenas.yml` |

Ejecutar `skript:skript reload astral_minijuegos` y `dm reload`. No requiere
apagar ni reiniciar; si ya hubo muchas recargas, preferir un reinicio por Metaspace.
Revisar consola y probar `/arenas tft1`, `/arenas tft2`, `/arenas tft3` y rescate
bajo Y=120. No reinstalar ni sustituir mundos para esta actualización.

### Instalación inicial completa

1. Comprobar que se usa Paper 26.1.2, Skript 2.17+, DeluxeMenus, MythicMobs,
   Multiverse, WorldGuard y LuckPerms, y que los dos nombres nuevos están libres.
   Descargar respaldo desde el panel antes de instalar mundos.
2. Con el servidor encendido, crear **únicamente los mundos nuevos** con los
   comandos `mv create minecraft:parkour_spiral ...` y `minecraft:arenas_tft ...`
   del archivo de despliegue. Si ya existen con contenido, no sobrescribirlos:
   revisar esa situación antes de continuar.
3. Apagar. En Worlds, comprobar las filas nuevas `parkour_spiral` y `arenas_tft`.
   Usar Upload únicamente en cada fila nueva con su ZIP correspondiente.
   **Nunca Worlds > Upload en `world`, ni sustituir un mundo existente del proyecto.**
   Si el panel no permite seleccionar inequívocamente esos destinos, dejar esa
   parte pendiente. No subir el paquete TFT original ni el schematic.
4. Copiar mediante Files los YAML y Skript indicados. Combinar las entradas
   `parkour` y `arenas` de `config-gui_menus.yml` con `gui_menus` del servidor,
   conservando las demás. Reemplazar `mobs/arena.yml`; no duplicar ese NPC en otro archivo.
5. Encender y revisar consola, incluida la conversión del mundo TFT antiguo.
   Si hace falta registrar mundos ya presentes, usar
   `mv import minecraft:parkour_spiral normal` y
   `mv import minecraft:arenas_tft normal`; no repetir si ya están registrados.
   Comprobar `/mv list` y autocompletar `/minecraft:execute in`: los destinos
   generados exigen `minecraft:parkour_spiral` y `minecraft:arenas_tft`.
6. Ejecutar las reglas Multiverse, gamerules, LuckPerms y WorldGuard del archivo.
   Configuran PvP solo en las arenas, inventario conservado, protección de bloques
   y cofres, sin mobs naturales ni command blocks del mapa original. Las arenas
   mantienen la posibilidad de mascotas, sin sus bonus de mazmorra.
   Parkour usa aventura, hambre fija y sin daño. El permiso por mundo
   `mv.bypass.gamemode.parkour_spiral` deja a Skript conservar el modo anterior;
   OP en creativo conserva creativo. No se cambia la configuración global de modos.
7. Recorrer cada mapa como OP en creativo, comprobar piso y dos bloques de aire,
   orientación y nombres de dimensión tras la conversión del mundo. Las llegadas
   TFT ya están verificadas en el mapa; si se quiere cambiarlas, guardar otro punto
   es opcional, igual que para parkour y la arena clásica:

   ```text
   /astralpunto parkour spiral
   /astralpunto arena clasica
   /astralpunto arena tft1
   /astralpunto arena tft2
   /astralpunto arena tft3
   /astralpunto lista
   ```

   Ejecutar cada comando parado en el mundo correcto; exige OP y estar por encima
   del límite de rescate. Guarda posición y orientación en variables persistentes
   de Skript, que tienen prioridad sobre Python. No borrar `variables.csv` al instalar.
   Fijar `clasica` es opcional: sustituye el reparto de 25 puntos por un único punto.
8. Crear/reubicar los dos NPC con las líneas de `despliegue.txt`, que permiten mobs
   temporalmente en el lobby y vuelven a bloquearlos. No ejecutar de nuevo para
   añadir copias. El comando `mm mobs kill astral_npc_arena` elimina la copia anterior.

Se requiere apagar/encender para instalar los mundos. Para actualizaciones posteriores
de scripts/menús, con mundos ya instalados, bastan `dm reload`, `mm reload`,
`skript:skript reload astral_gameplay` y `skript:skript reload astral_minijuegos`.
Es preferible un reinicio conjunto si ya hubo varias recargas por el límite de Metaspace.

En Paper 26.1 los mundos adicionales usan `world/dimensions/<namespace>/<key>/`:
ver [Multiverse: creación y almacenamiento de mundos](https://mvplugins.org/core/how-to/customise-world-creation/).
El control de modos y el permiso por mundo se documentan en
[Multiverse: configuración](https://mvplugins.org/core/reference/configuration-file/).

## Pruebas de aceptación en el servidor

- `/parkour`, `/arenas`, ambos aldeanos, `/menu` y `/comandos` muestran los selectores.
- Un jugador normal entra en Spiral en aventura, no rompe/coloca bloques, no usa
  ganchos ni doble salto, no pierde hambre ni recibe daño; OP creativo conserva su modo.
- Debajo de Y=-20 vuelve a la llegada de Spiral. Las arenas rescatan bajo Y=0
  (`clasica`) o Y=120 (TFT), siempre al mapa elegido. Cambiar `rescue_y` si la
  recorrida revela que el escenario requiere otro límite.
- La estrella del slot 9 abre el menú y permite volver al lobby. Se recupera el
  modo anterior al salir, también tras reconectar/reiniciar dentro del mapa.
- TFT permite viajar sin punto OP guardado a las coordenadas de la tabla; si hay
  un punto guardado, tiene prioridad. Un no OP no puede guardar puntos.
  Un ID desconocido no ejecuta ningún comando de consola.
- Con dos jugadores: daño PvP ajustado por tier en ambas arenas, inventario y
  experiencia conservados al morir, regreso a la arena elegida si el respawn
  permanece en ese mundo. Si otro plugin manda al lobby, se respeta esa salida.
- Revisar consola después de carga, viajes, muerte y rescate. Estas pruebas
  con jugadores siguen pendientes hasta el despliegue real.

## Agregar un mapa

Agregar una entrada con `id`, `world`, `name`, `icon`, `description`, `arrival`
(`x,y,z,yaw,pitch`) y `rescue_y`; parkour también lleva `difficulty`. Usar
`needs_point=True` mientras no se haya revisado la llegada. Preparar/importar el
mundo nuevo y ejecutar `python menus.py`: menús, rescate, protección, ganchos y
división PvP salen de las listas. Añadir al despliegue los permisos de acceso
de Multiverse si el servidor tiene `enforce-access` activado.

El selector admite hasta 14 entradas por tipo; falla explícitamente al superar
esa cantidad. Pruebas: `python -m unittest discover -s datapack-src -p 'test*.py'`
desde la raíz, con Pillow, PyYAML y NumPy disponibles.
