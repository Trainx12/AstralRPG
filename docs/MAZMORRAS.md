# Mazmorras nuevas: preparacion y recorrido de revision

Arreglos del 08/11/2026 (commit 1a7e61a):
- Las criaturas de mazmorra usan `Despawn: false`. Con `true`, Minecraft las borraba al rato y el control
  veia la sala vacia y pasaba de oleada. RESET y LIMPIA las quitan.
- Pagan oro al morir: la condicion es `?~isplayer` (el que mata); con `?isplayer` no pagaba nunca.
- Se puede nadar (antes te devolvia al ultimo lugar seco; trababa Minas Olvidadas).
- `cumbre_hielo`, `forja_volcano` y `santuario_interstellar` estan en la lista de mazmorras: no se pierden
  cosas al morir, sin tumba, sin romper ni poner bloques.
- Expediciones en orden de dificultad (Bosque, Mina, Tumba, Cumbre, Forja, Santuario): la de una pide
  `astral.completada.<anterior>`, que se da al ganar la sala final. Los OP pasan siempre. Para darsela a
  alguien que ya la gano antes: `lp user <jugador> permission set astral.completada.<mazmorra> true`.
  Bosque y Mina comparten el mapa de exploracion `cavernas`.
- Forja en el server sigue con su version vieja de 3 salas (mundo `forja`); el repo la tiene como 1 sala en
  `forja_volcano` sin controlador colocado. Solo se le aplicaron los arreglos de oro, despawn y permiso.

Santuario, cambio del 04/11/2026: instalado el escenario de
`mapa_Santuari_Mazmorra.zip` (`interstellar.litematic`) en
`santuario_interstellar`. Llegada `34.5 180 40.5`, controlador
`46.5 180 48.5`, radio 18. Se conservan las cinco oleadas de Ancestrales.
Ambos puntos usan el piso original de bloques de hierro. La arena cuenta con
9x9 bloques libres en el centro y la llegada conecta con ese sector a pie.
El aldeano existente y `/mazmorras santuario` apuntan al mundo nuevo.
Se comprobaron pisos, altura libre y controlador en Aternos. Falta prueba de
combate con jugadores. La copia anterior sigue disponible en `santuario`.

Portales Astrales, instalados el 04/11/2026: mundo vacio `portales_astrales`,
plataforma central de terracota negra en `0.5 81 125.5`, End al este y Nether
al oeste mirando al norte. Se copio la torre del End con su primer plano y se
excluyo el fondo situado detras de la torre (Z original menor que 60).
El aldeano `astral_npc_portales` esta en `lobby 124.472 100 193.529` y abre
el menu DeluxeMenus `portales`. `/umbrales` permite abrir el mismo menu.
El NPC se creo en Portales Astrales y se traslado al lobby para respetar la
proteccion existente de aparicion de mobs. Se comprobaron en vivo su posicion,
los pisos de llegada y los bloques activos de ambos portales.

Portales separados (04/11/2026, mismo mundo `portales_astrales`):
- End: el dueno borro la torre vieja y se pego `portal_END.schem` (322x236x241,
  WorldEdit) con `//paste -a` parado en `146 82 78`. Portal activo en
  `145 96 0`. Despues se borro con `//replace` el terreno natural que traia
  (piedra, tierra, arena, agua, lava, arboles, minerales, plantas), con
  `//perf neighbors off` para que no cayera el polvo de concreto. Llegada
  `146.5 84 68.5` mirando al norte, frente a la torre. Los huecos que quedaron
  en el piso (4750 columnas rodeadas por la construccion) se taparon con
  concreto negro (`fill ... keep`, 2927 comandos calculados del schematic).
- Un aldeano `astral_npc_portales` a 2 bloques al este de cada llegada abre el mismo
  menu (otro portal o "Volver al Lobby" = `/umbrales lobby` -> `/spawn`). Rehacerlos:
  `mm mobs spawn astral_npc_portales 1 portales_astrales,148.5,84,68.5` y
  `mm mobs spawn astral_npc_portales 1 portales_astrales,-2190.5,81,90.5`, despues
  girarlos con `minecraft:tp` (no `tp`: lo agarra Essentials) a yaw 90.
- Caerse por debajo de Y=50 en `portales_astrales` (supervivencia/aventura) lleva
  al lobby con `/spawn` (en `astral_portales.sk`, generado por `portales.py`).
- Nether: `GuardianNPv3-92.schem` ("guardianes"), separado en X -2248..-2138;
  llegada `-2192.5 81 90.5` mirando al norte (elegida por el dueno).
- El menu del aldeano lleva a cada uno (`/umbrales end|nether`, en `portales.py`).
  Ambos viajes se probaron en vivo.

La construccion de `Entrada_Del_nether.zip` se exporto como
`plugins/WorldEdit/schematics/entrada-del-nether.schem` para la colocacion
manual del dueno. Mide 367x256x119 bloques. En un mundo con techo Y=319,
una base Y=64 permite colocar su altura completa. Los ZIP originales y los
resultados privados estan en `.local/portales/`. Las cargas de revision se
retiraron de `chunk_tickets.dat` con el servidor apagado, conservando las
65 cargas que ya tenia el lobby. Respaldos en `.local/portales/cargas/`.

Forja, cambio del 04/11/2026: `volcano.zip` esta instalado en
`forja_volcano`, con llegada de revision `82.5 52 -55.5`. El volcan sur
anterior (`forja`, procedente de `volcan gigante.zip`) pasa a expedicion,
con llegada `1536.5 222 1900.5` y aldeano en `1536.5 222 1901.5`.
Las dos llegadas y el punto del aldeano se comprobaron en Aternos con piso
y dos bloques de aire. Skript y MythicMobs recargaron las rutas.
La nueva Forja queda disponible para revisar el escenario. Falta seleccionar
el espacio de combate y colocar su controlador. El mapa es muy irregular y
la llegada comprobada no garantiza espacio para un golem.

El dueno confirmo eliminar `reino` completo con sus aldeanos. Se retiro
su entrada de Multiverse y se elimino `world/dimensions/minecraft/reino`
desde Aternos con el servidor apagado.

Intercambio de Cumbre preparado para Aternos. La expedicion usa `exp_nieve`
con las regiones extraidas de `nieve.zip`; las plataformas del servidor no
forman parte de esos archivos. La mazmorra usa `cumbre_hielo` con el escenario
de `ice-lobby.zip`. Las regiones privadas estan en
`.local/mapas/intercambio-nieve/<mundo>/region/`. Crear o comprobar ambos mundos
en Multiverse y subir sus regiones con el servidor apagado. Las dimensiones
anteriores quedan disponibles para volver atras.

Tras el arranque, comprobar el piso y el espacio de llegada de ambos mundos.
Aplicar `build/mapas_exploracion/astral_viajes.sk` y los dos YAML de Cumbre en
`build/mythicmobs/`, y recargar Skript y MythicMobs. En `exp_nieve`, fijar el
spawn en `16.5,83,10.5,0,0` y colocar `astral_npc_cumbre` en
`16.5,83,12.5`. En `cumbre_hielo`, fijar el spawn en `8.5,65,8.5,180,0`
y crear los tres controladores con los comandos de `build/mazmorras/cumbre/`.
Revisar las tres salas con un jugador antes de dar por probado el combate.

Actualizacion de Forja (03/11/2026): los cuatro archivos de region existentes en
Aternos contenian solo aire. Se respaldaron en `.local/mapas/respaldo-forja-aternos/`
y se instalaron las cuatro regiones del recorte del volcan sur con el servidor
apagado, exclusivamente en `world/dimensions/minecraft/forja/region/`.
La entrada existente de `/mazmorras forja` usa `1536.5 224 1900.5`; en el
recorte instalado hay piedra en Y=221 y aire entre Y=222 y Y=226 en esa columna.

Estado local: generadores y recortes preparados. **Ningun mundo se modifico en Aternos.** Las entradas nuevas
estan deshabilitadas hasta revisar piso, llegada, altura libre y espacio de combate dentro de Minecraft.
El usuario pidio preparar ubicaciones sugeridas para hacer esa revision.

## Orden y ubicaciones propuestas

Son centros de salas, no coordenadas ya probadas con un jugador. Puede ser necesario moverlos o construir
un piso/puente. Primero recorrer en creativo; despues probar el combate en supervivencia.

| Mundo | Salas sugeridas (X, Y, Z) | Final |
|---|---|---|
| `bosque` | (1440.5,104,1568.5) → (1504.5,107,1504.5) → (1600.5,97,1440.5) | Chaman |
| `tumba` | llegada (-148.426,62,-97.473) → llegada (-203.163,88,203.533) → llegada (0.368,73,-44.104), jefe (0.568,72,0.512) | Momia |
| `mina` | Se conservan sus cuatro salas e identificadores actuales | Guardian |
| `cumbre` | (-128.5,79,0.5) → (0.5,115,0.5) → (96.5,97,0.5) | Yeti |
| `forja` | (1536.5,224,1900.5) → (1456.5,210,2032.5) → (1536.5,200,2304.5) | Golem de Forja |
| `santuario` | (-329.5,51,65.5), una arena con cinco oleadas de un jefe cada una | Cangrejo → Chaman → Momia → Yeti → Golem, todos Ancestrales |
| `arena` | 25 llegadas aleatorias entre X=-218..-194, Y=73, Z=-2383..-2357 | Solo PvP, sin premios ni progreso |

En la Forja hay lava y magma. Preparar plataformas y revisar especialmente la segunda y tercera sala.
Se usa **un solo volcan: el del sur** de `volcan gigante.zip`. El recorte preparado excluye el volcan
del norte; las tres salas pertenecen al mismo recorrido de la Forja. No importar el mapa completo.
Decision confirmada por el usuario para evitar que los jugadores se pierdan.
En el bosque hay arboles altos y desniveles; el Yeti necesita una superficie mas amplia que la del jugador.
En el Santuario se conserva la isla inicial y la construccion del reloj para ambientacion; la arena sugerida
esta en la isla inicial y necesita comprobar que los jefes grandes no caigan al vacio.

El spawn original de la arena (-32,70,48) cae en el vacio. La propuesta usa la zona de estadio donde estaba
el jugador guardado, y se comprobo que hay piedra a Y=-46. En el desierto el spawn original (35531,60,35496)
es una plataforma de servicio; las salas se proponen en el escenario principal, cerca del origen.

Actualizacion de Arena (01/11/2026): el dueno selecciono `(-194,73,-2357)` y
`(-218,73,-2383)` (675 bloques). La entrada del NPC ahora elige al azar entre
25 puntos interiores a Y=73, comprobados contra el recorte privado: piso solido
y tres bloques de aire. Cada entrada se sortea de forma independiente; dos jugadores
pueden recibir el mismo punto. Reemplaza la llegada anterior a Y=-44.
Para instalar: reemplazar `plugins/MythicMobs/mobs/arena.yml`, agregar
`plugins/MythicMobs/skills/arena.yml` y ejecutar `mm reload`. No hace falta mover el
NPC del lobby ni cambiar el mapa. El ajuste afecta la entrada por el NPC, no el
respawn de muerte ni otros teletransportes.

Instalado en Aternos el 01/11/2026 desde `4f72c7b`: reemplazado `mobs/arena.yml`,
creado `skills/arena.yml` y ejecutado `mm reload`. El registro confirma 115 mobs
y 384 skills (26 nuevas), sin errores nuevos; siguen los tres avisos conocidos de
dialogos de ejemplo. No fue necesario mover el NPC. Pendiente probar la entrada con
jugador. Comprobante privado: `.local/deploy-ui/arena-instalada.jpg`.

El Cangrejo sigue en las playas del mundo normal. `volcan.zip` sigue de reserva.
El Santuario se abre despues del titulo Portador de la Estrella; no bloquea el epilogo inicial.

## Ajuste de la sala final de Tumba (01/11/2026)

**Instalado en Aternos el 01/11/2026**, desde el commit `ef0ec9c`:
reemplazados `mobs/tumba.yml` y `skills/tumba.yml`, creado `ad.party` y recargado
MythicMobs (115 mobs y 358 skills; sin errores nuevos, solo los tres avisos de
dialogos de ejemplo). Se retiro un controlador viejo por sala y se creo uno nuevo
en cada ubicacion; posiciones comprobadas por consola. Se retiraron las seis cargas
temporales de chunks. WorldGuard confirma `build: DENY` en Tumba. No se modifico
el mapa ni el modo de juego del jugador. Pendiente prueba de combate con dos tier III.
Comprobante privado: `.local/deploy-ui/tumba-instalada.jpg`.

Sala1: llegada `-148.426 62 -97.473`, controlador `-148.5 60 -98.5`, radio 28.
Seleccion WorldEdit `(-128,63,-112)..(-168,58,-86)` (6642 bloques).
Los puntos de aparicion usan piso y tres bloques libres del recorte local, dentro de
la seleccion y a diferentes alturas segun el terreno.
Base para dos jugadores tier III, dificil, con las mismas estadisticas de sala2:

| Oleada | Base | Refuerzos por encima de 2 jugadores |
|---|---|---|
| 1 | 3 aranas venenosas, 3 momias, 2 esqueletos, 1 cara | 3 momias por jugador extra |
| 2 | 4 aranas venenosas, 3 momias, 3 esqueletos | 4 esqueletos por jugador extra |

Las variantes de sala1 tienen IDs propios `astral_tumba_s1_*`, para que no se
mezclen los contadores ni la limpieza entre salas. Para mover su controlador:
cargar el chunk viejo con `execute in minecraft:tumba run forceload add -192 128`,
ejecutar `mm mobs kill astral_tumba_control_sala1`, retirar esa carga y crear el nuevo
con las tres lineas de sala1 del archivo de comandos generado. Hacerlo sin un
combate activo. Las ocho pruebas de `test_mazmorras` cubren ambas salas.

La segunda sala usa llegada `-203.163 88 203.533` y controlador nuevo en
`-175.5 88 203.5`, radio 36 (limpieza y transicion 44). La seleccion del dueno es
`(-191,88,195)..(-160,93,211)`. Las apariciones se reparten en puntos dentro del
rectangulo, con piso solido y tres bloques de aire comprobados en el recorte privado.
Se evitan el agua y las columnas del interior; los golems usan dos puntos con espacio
de 3x3. Si el escenario fue modificado en Aternos, volver a revisar esos puntos.

Base de dos jugadores tier III, dificil; con un jugador se mantiene la misma base:

| Oleada | Base | Refuerzos por encima de 2 jugadores |
|---|---|---|
| 1 | 5 aranas venenosas, 5 momias comunes, 4 esqueletos, 2 caras, 1 espantapajaros | 3 momias por jugador extra |
| 2 | 7 aranas venenosas, 6 momias comunes, 5 esqueletos | 4 esqueletos por jugador extra |
| 3 | 2 golems agresivos | 1 golem por cada 2 jugadores extra completos |

Se cuenta al inicio de cada oleada dentro del radio del controlador, excluyendo
espectadores. Ejemplo con 4 jugadores: 11 momias en ola1, 13 esqueletos en ola2,
3 golems en ola3. No se mezclan estos refuerzos con el antiguo extra fijo de grupo.

Balance inicial (vida/dano): arana 32/6, momia 60/9, esqueleto 40/7, cara 36/7,
espantapajaros 70/10, golem 380/16. La arana usa CAVE_SPIDER para el veneno y
el golem tiene IA agresiva contra jugadores. Las momias comunes no tienen fases
ni habilidades del jefe. Falta validar dificultad efectiva con dos jugadores en Minecraft.

Ademas de reemplazar los dos YAML de Tumba y ejecutar `mm reload`, crear una vez
`scoreboard objectives add ad.party dummy` (si ya existe, conservarlo). Con la
mazmorra vacia, cargar el chunk viejo de sala2 con
`execute in minecraft:tumba run forceload add -128 -64`, ejecutar
`mm mobs kill astral_tumba_control_sala2`, retirar la carga con
`execute in minecraft:tumba run forceload remove -128 -64` y crear el controlador
nuevo con las tres lineas de sala2 del archivo de comandos generado.

Validacion local: `python -m unittest test_mazmorras` con PyYAML. Se interpretan las
llamadas del YAML generado y se verifican cantidades para grupos de 1 a 20,
limites de aparicion, controladores, IA y referencias de modelos. No sustituye una
prueba con Paper/MythicMobs y jugadores. Sintaxis de referencia:
[Summon](https://wiki.mythiccraft.io/mythicmobs/skills/mechanics/summon) y
[Location](https://wiki.mythiccraft.io/mythicmobs/Skills/Targeters/Location).

Preparado localmente segun las dos capturas del dueno: la Momia aparece exactamente en
`0.568 72 0.512` (sin dispersion aleatoria) y el grupo llega a `0.368 73 -44.104`.
El controlador va en el punto del jefe; radio de activacion 56 y de limpieza/premios 64,
para incluir la llegada a unos 45 bloques. Falta probar el combate en Minecraft.

Para aplicar en una Tumba ya instalada: reemplazar `plugins/MythicMobs/mobs/tumba.yml`
y `plugins/MythicMobs/skills/tumba.yml` por los generados en `build/mythicmobs/` y
ejecutar `mm reload`. Con la mazmorra vacia, cargar el chunk del controlador viejo
(`execute in minecraft:tumba run forceload add 96 -192`), eliminarlo con
`mm mobs kill astral_tumba_control_sala3` y retirar esa carga
(`execute in minecraft:tumba run forceload remove 96 -192`). Crear el controlador nuevo
con las tres lineas de sala3 de `build/mazmorras/tumba/comandos.txt`.
No volver a crear el mundo ni los otros controladores.

La proteccion generada es `rg flag -w tumba __global__ build deny`: impide construir
y romper a jugadores sin bypass de WorldGuard. Comprobarla con una cuenta sin OP.
El dueno cerrara las entradas en el mapa. `/spawn` sigue disponible para salir de la
mazmorra; este ajuste no bloquea comandos de escape.

## Recortes privados preparados

Estan en `.local/mapas/preparados/`, ignorados por Git. **No publicar ni agregar al repo.**

| Archivo | Uso | Tamaño aproximado |
|---|---|---|
| `bosque-regiones.zip` | Bosque Sombrio | 1.6 MB |
| `desierto-regiones.zip` | Tumba del Rey de Arena | 2.0 MB |
| `nieve-regiones.zip` | Cumbre Helada | 1.5 MB |
| `forja-regiones.zip` | Corazon de la Forja | 5.9 MB |
| `santuario-regiones.zip` | Santuario Celestial | 0.8 MB |
| `arena-regiones.zip` | Arena PvP | 3.7 MB |

Cada ZIP contiene solo `region/*.mca` recortados por chunks; no incluye `level.dat`, jugadores, entidades,
datapacks ni configuraciones originales. La limpieza reemplaza command blocks, structure blocks, jigsaw
y spawners por ladrillos de piedra, quita su logica y vacia inventarios/loot de los cofres originales.
Los bloques y la decoracion restantes se conservan. Los archivos descargados no se modificaron.

`datapack-src/mapas.py` permite repetir la inspeccion y los recortes sin dependencias aparte de Pillow,
que el proyecto ya usa. Las vistas topograficas estan en `.local/mapas/` y tampoco se publican.

Ejemplo (desde `datapack-src`):

```text
python mapas.py <carpeta-Downloads> --map bosque
python mapas.py <carpeta-Downloads> --map bosque --prepare 1360 1360 1695 1647 --out ../.local/mapas/preparados
```

Limites usados: desierto `-272 -272 191 223`, nieve `-208 -96 191 95`, forja `1360 1792 1647 2399`,
santuario `-432 -144 143 271`, arena `-560 -2624 15 -2129`.

## Instalar y revisar una a la vez

1. Crear un mundo nuevo con el nombre del cuadro, usando los comandos generados en
   `build/mazmorras/<nombre>/comandos.txt`. Para PvP: `build/arena/comandos.txt`.
2. Apagar el servidor. Confirmar en el panel cual es la carpeta de ese mundo nuevo; en la disposicion
   26.1 del servidor sera `world/dimensions/minecraft/<nombre>/region`. Subir ahi los `.mca` del recorte.
   **Nunca Worlds → Upload sobre `world`, ni reemplazar `mina`, ni subir el ZIP original entero.**
3. Encender. Aplicar reglas del mundo y recorrer las coordenadas propuestas con OP en creativo.
   Los comandos de teletransporte del recorrido estan comentados en el `.txt`; cambiar `<jugador>`.
4. Ajustar centros, llegadas y radios en `datapack-src/mobs/mazmorras_data.py`.
   Para habilitar una mazmorra revisada, agregar `enabled=True` a su definicion en `DEFINITIONS`.
   En la arena, cambiar `ARENA['enabled']` a `True` y confirmar `arrival`.
5. Regenerar con `python mobs/mazmorra.py`, subir los YAML de esa mazmorra en `mobs/` y `skills/`,
   y hacer `mm reload`. Crear sus controladores y NPC una sola vez con los comandos del `.txt`.
6. Probar todas las oleadas, abandonar una sala para probar su reinicio, terminarla con dos jugadores,
   volver durante el cooldown y comprobar el credito de historia. Recien entonces abrir el acceso.

Las nuevas mazmorras son compartidas, como las Minas; no hay instancias separadas por grupo.
Su dificultad aumenta la cantidad de enemigos cuando hay dos o mas jugadores. Los jefes reutilizan
sus modelos, fases, stats y drops existentes. Los recuerdos de historia se acreditan a los jugadores
cercanos al limpiar la sala final, aunque el cofre este en cooldown.

El Santuario usa una sola sala con cinco oleadas: evita que se activen cinco controladores a la vez.
Sus Ancestrales conservan el combate y los afijos; no anuncian un evento global ni desaparecen por tiempo.

La arena tiene `keep_inventory`, PvP solo en ese mundo y sin mobs naturales; se guardan las mascotas
al entrar. Las misiones excluyen ese mundo. Los comandos para apagar PvP en los demas mundos estan
en su `.txt`, pero solo se ejecutan para los mundos que existan.

## Correccion de finalizacion prematura de Tumba (01/11/2026)

El registro de Aternos mostro llegada al trono a las 22:00:39, credito de
victoria a las 22:00:40 y /spawn a las 22:00:57, sin muerte del jefe. Al
cargar la sala se encontro la Momia Ancestral aun viva. La primera comprobacion
de ausencia de mobs podia adelantarse al registro del summon.

La sala3 ahora mantiene tumba.espera durante los primeros 10 ticks de la
invocacion. Ademas, su temporizador y la skill de victoria exigen la marca
tumba.jefe.derrotado: solo la Momia de esta mazmorra la entrega a su propio
controlador mediante @Parent en ~onDeath. Inicio y reset borran la marca;
una ausencia, desaparicion o fallo de aparicion no concede victoria. Se
conserva la espera de que no queden ayudantes antes de dar el premio.
Las demas salas, recompensas y posiciones no cambian. Nueve pruebas de
mazmorras pasaron, incluida la regresion de esta condicion de victoria.

Aplicado en Aternos: MythicMobs recargo a las 22:11:28 sin errores nuevos.
Se reinicio la sala vacia y se comprobo la retirada de la Momia anterior.
Regresion real: con sala vacia y tumba.ola1 establecido a las 22:14:06,
la consulta de las 22:14:25 conservo ola1 sin tumba.fin ni credito/premios.
Se retiro la marca de prueba y la carga temporal del chunk. Las 52 pruebas
locales completas pasaron. Falta repetir el combate normal con jugador para
comprobar el ciclo de muerte del jefe, ayudantes, premio y regreso.

## Cofre final que no se abria (08/11/2026)

El cofre de la Tumba aparecia pero el clic no hacia nada. Las mazmorras tenian `build deny` sin
`interact allow`: WorldGuard cancela el clic sobre entidades y MythicMobs no recibe `~onInteract`
(el lobby ya tenia `interact allow`). Ahora las mazmorras y los mapas de expedicion llevan
`interact allow` (cofres y aldeanos) y `use deny` (puertas, botones y palancas siguen bloqueados).
Los OP no lo notan porque saltean WorldGuard: probar con un jugador sin OP.

## Cofre que decia "ya cobraste" a los OP (09/11/2026)

La espera de 30 minutos del cofre es el permiso temporal `astral.<mazmorra>.cd`. Un OP tiene todo permiso
que nadie definio, asi que el cofre le decia "ya cobraste" la primera vez y no daba nada. Arreglo: ponerlo
en `false` para el grupo `default` (le gana al OP; el permiso temporal del jugador le gana al false).
Ya esta en los `comandos.txt` de cada mazmorra. Una vez, en la consola:

```text
lp group default permission set astral.mina.cd false
lp group default permission set astral.bosque.cd false
lp group default permission set astral.tumba.cd false
lp group default permission set astral.cumbre.cd false
lp group default permission set astral.forja.cd false
lp group default permission set astral.santuario.cd false
```

Si un rango tiene `*`, sus jugadores siguen viendo "ya cobraste".

## Cofre del jefe y Fragmentos Astrales (09/11/2026)

Generador: `datapack-src/cofre_mazmorra.py` (lo llaman `menus.py` y `build_pack.py`).
- Todas las mazmorras terminan con el cofre (antes solo la Tumba). Aparece donde se llega a la sala final
  (Tumba: base de oro, con el guia). Ya no se manda al lobby solo: el menu tiene "Volver al lobby".
- Al tocarlo abre `cofre_<mazmorra>` (DeluxeMenus, marco de Mazmorras): fragmento del jefe, plata,
  item Astral y materiales de elite. El boton RECLAMAR cobra todo cada 30 minutos (`astral.<mazmorra>.cd`).
- El fragmento se da solo la primera vez: despues se ve apagado y dice "Solo se puede reclamar la primera vez".
  No es un item: queda en `/fragmentos` (permiso `astral.fragmento.<id>`), asi no se pierde.
  Seran la llave del renacimiento.

| Mazmorra | Primera vez | Item Astral (cada cobro) | Plata |
|---|---|---|---|
| Minas Olvidadas | Lampara del Minero | 1 Cristal Arcano Refinado | 2500$ |
| Bosque Sombrio | Fragmento del Pantano | 1 Cristal Arcano Refinado | 1500$ |
| Tumba del Rey de Arena | Fragmento de la Arena | 1 Gema Luminica | 2000$ |
| Cumbre Helada | Fragmento de Hielo | 2 Gemas Luminicas | 2500$ |
| Corazon de la Forja | Fragmento de Fuego | 1 Chispa Astral | 3000$ |
| Santuario Celestial | Corazon Astral | 2 Chispas Astrales | 5000$ |

El Fragmento de la Marea sale del Cangrejo (no tiene mazmorra) la primera vez que se lo mata.
La historia ya no entrega fragmentos como item. Los nodos `astral.fragmento.*` van en false para el grupo
default (`build/mazmorra/comandos.txt`), igual que la espera del cofre, para que funcione con OP.
La tapa de los cofres (tambien los de las gachas) abria hacia abajo: era el signo de la animacion.

## Tanda 1: orden y nombres de entrada

Quien termino Mina antes y no Bosque se destraba con `lp user <jugador> permission set astral.completada.bosque true`.
Los NPC de entrada tienen `AlwaysShowName: false` para esconderlos en salas secretas. Tras `mm reload`, guardar sus posiciones, quitar los existentes y volver a colocarlos; no duplicarlos. Cofre y guia finales conservan su nombre visible. Santuario queda sin desplegar.
