# Parkour y Arenas PvP

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
| Arena / `tft1` | `-286.5 143 -550.5 0 0` | Provisorio: requiere punto OP |
| Arena / `tft2` | `-286.5 139 -282.5 0 0` | Provisorio: requiere punto OP |
| Arena / `tft3` | `-286.5 139 -14.5 0 0` | Provisorio: requiere punto OP |

TFT es un mundo 1.12.2 cuyo spawn NBT es `0 64 0` (el TXT propone `0 100 0`).
El schematic mide 263 × 256 × 801 y contiene tres grupos separados en Z:
`0..253`, `274..527`, `547..800`; `WEOrigin=(-418,0,-683)`.
Las propuestas trasladan tres columnas del schematic a ese origen. No está
verificada la correspondencia con el mundo guardado ni la seguridad de esas
llegadas. **Los tres botones TFT rechazan el viaje hasta fijar cada punto**;
no mandan jugadores a coordenadas provisorias. No se implementó cronómetro/final.

## Instalación en Aternos

La lista completa de archivos locales, destinos y comandos está en
[`build/minijuegos/despliegue.txt`](../build/minijuegos/despliegue.txt).
Debe continuarla quien tenga navegador y sesión del dueño. No hay APIs privadas.

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
   orientación y nombres de dimensión. En TFT visitar primero las coordenadas
   provisorias como OP, buscar un lugar seguro dentro de cada arena y fijarlo:

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
  (`clasica`) o Y=60 (TFT), siempre al mapa elegido. Cambiar `rescue_y` si la
  recorrida revela que el escenario requiere otro límite.
- La estrella del slot 9 abre el menú y permite volver al lobby. Se recupera el
  modo anterior al salir, también tras reconectar/reiniciar dentro del mapa.
- TFT rechaza viajes antes de fijar el punto y luego acepta; un no OP no puede
  guardar puntos. Un ID desconocido no ejecuta ningún comando de consola.
- Con dos jugadores: daño PvP ajustado por tier en ambas arenas, inventario y
  experiencia conservados al morir, regreso a la arena elegida si el respawn
  permanece en ese mundo. Si otro plugin manda al lobby, se respeta esa salida.
- Revisar consola después de carga, viajes, muerte y rescate. Estas pruebas
  con jugadores y los puntos de TFT siguen pendientes hasta el despliegue real.

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
