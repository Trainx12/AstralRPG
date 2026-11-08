# Reino y Cavernas

El dueno eligio Medieval Fantasy Kingdom Spawn como escenario general y CoalCave
para los interiores. Son dos mundos nuevos, `reino` y `cavernas`. No sustituyen
`lobby`, `mina`, ni las otras mazmorras. Los aldeanos de cada mazmorra y los
combates quedan pendientes de los lugares que elija el dueno al explorar.

## Preparacion del 01/11/2026

Generador: `datapack-src/mapas_exploracion.py`. Copia los registros comprimidos
originales y comprueba que todos los exportados sean identicos, incluidos POI.
No usa `sanitize` de `mapas.py`: no reemplaza bloques ni vacia cofres. No crea
plataformas, no pega construcciones y no elimina decoracion. Los archivos de
terceros permanecen en `.local/mapas/astral-nuevos/`, ignorados por Git.

| Mundo | Llegada (X Y Z) | Orientacion | Limites del recorte X/Z |
|---|---|---|---|
| reino | 5.5 67 0.5 | Norte, yaw 180 | -192 -176 .. 175 175 |
| cavernas | 172.5 102 89.5 | Sur, yaw 0 | 32 16 .. 271 255 |

Se conservaron todos los chunks con bloques del escenario y un chunk de margen;
se excluyeron regiones vacias alejadas. El reino tiene 336 chunks de escenario
y 506 exportados; las cavernas, 121 de escenario y 225 exportados. Los bloques
de luz invisibles sin escenario no extienden el rectangulo util.

Las llegadas usan caminos de tierra existentes. Se comprobo un piso de 3x3 y
tres bloques libres encima, mas un recorrido conectado de 322 posiciones en
el reino y 396 en las cavernas. La primera propuesta de las cavernas se desplazo
dos bloques para evitar una losa del camino. El spawn original del reino
estaba dentro del suelo. Falta revision visual con jugador en Minecraft.

Los originales no contienen command blocks, spawners, structure blocks ni jigsaw.
Tampoco contienen entidades de decoracion en sus regiones de entidades. No se
importan datos de jugadores, datapacks, scoreboard ni configuraciones originales.

## Repetir e instalar

Descargas originales:

- [Medieval Fantasy Kingdom Spawn](https://www.planetminecraft.com/project/medieval-fantasy-kingdom-spawn-volcano-castle-amp-underground-arena/), archivo `medivalspawn.zip`.
- [CoalCave](https://www.planetminecraft.com/project/coalcave-amp-underground-dungeon-system-mining-zone-amp-boss-arenas/), archivo `coalcave.zip`.

Guardar ambos ZIP en `.local/mapas/astral-nuevos/originales/` y ejecutar:

```text
python datapack-src/mapas_exploracion.py
```

Produce las regiones privadas, los ZIP de traslado y los informes de integridad;
los comandos de instalacion van a `build/mapas_exploracion/<mundo>/comandos.txt`.
Crear primero los mundos vacios con Multiverse y aplicar las reglas de
proteccion y conservacion ANTES de cargar los mapas. Apagar el servidor y subir
exclusivamente las regiones a `world/dimensions/minecraft/<mundo>/region/`,
y sus POI a la carpeta `poi/` del mismo mundo. Nunca Worlds -> Upload sobre
`world`. Despues encender y fijar el spawn con `mv setspawn`.

Las reglas previstas son aventura, sin PvP, sin apariciones naturales, sin
actualizaciones aleatorias ni propagacion del fuego, y proteccion de WorldGuard.
No se cambia el spawn global de Essentials. No teletransportar jugadores
automaticamente durante la instalacion.

Referencia de comandos: [Multiverse](https://mvplugins.org/core/fundamentals/commands-usage/).

## Instalado en Aternos el 01/11/2026

Se crearon `reino` y `cavernas`, se aplicaron las reglas con los mundos vacios,
se apago el servidor y se cargaron las cuatro regiones y tres POI del reino,
y la region y el POI de las cavernas. Se reemplazaron exclusivamente las regiones
vacias de esos mundos nuevos. Los otros mundos, NPCs y el lobby no se modificaron.

El servidor arranco correctamente y quedo Online, con el dueno conectado.
Las dos llegadas se fijaron con `mv setspawn`; se comprobo el piso esperado y
tres bloques de aire mediante condiciones `execute if block` en Aternos, que
solo ejecutaron `mv info <mundo>` al cumplir las cuatro condiciones.
Reino paso a las 12:27:33 y Cavernas a las 12:28:01, hora argentina.
Las dos cargas temporales de chunks se retiraron despues de verificar.

`random_tick_speed` y `fire_spread_radius_around_player` siguen en 0 en ambos
mundos despues del reinicio. No se crearon plataformas, NPCs, controladores ni
combates. No se hizo commit ni push y los mapas no se publicaron en GitHub.
La revision estetica completa con jugador queda para el dueno.

Para entrar: `/mvtp reino` y `/mvtp cavernas`; para volver: `/spawn`.
Llegadas exactas y orientaciones en la tabla de arriba.

En Multiverse 5.8.2 se comprobo que `mv setspawn` recibe X,Y,Z,yaw,pitch,
aunque la documentacion consultada indica pitch,yaw. El generador conserva el
orden comprobado en el servidor. Se retiro `spawn_radius`: no es una gamerule
valida en esta version y no es necesaria para el teletransporte de Multiverse.

Comprobantes privados: `.local/mapas/astral-nuevos/instalacion-aternos.txt` y
`.local/mapas/astral-nuevos/aternos-online.png`. No volver a crear los mundos
para ajustar una llegada; cambiar la definicion y aplicar solo `mv setspawn`.

## Aldeanos de enlace instalados el 01/11/2026

Expediciones Astrales del lobby ahora lleva directamente a Cavernas (el mapa 3,
CoalCave, elegido para interiores). Las entradas nuevas de las mazmorras siguen
pendientes; este cambio solo permite recorrer y preparar ambos escenarios.

| Aldeano | Posicion | Destino al hacer clic |
|---|---|---|
| Expediciones Astrales | lobby 178.636 100 225.735, yaw 180 | cavernas 172.5 102 89.5 |
| Guia al Reino | cavernas 172.5 102 91.5, yaw 180 | reino 5.5 67 0.5 |
| Guia a las Cavernas | reino 7.5 67 0.5, yaw 90 | cavernas 172.5 102 89.5 |

Ambos guias estan a dos bloques de sus llegadas, sobre el camino original.
Son aldeanos de MythicMobs quietos, invulnerables y sin colision. Se comprobo
su piso y espacio libre antes de crearlos. WorldGuard permite mob-spawning
en los dos mapas para los NPCs; las apariciones naturales siguen desactivadas.

Fuente de las interacciones: `datapack-src/mobs/mythic.py`, entradas
`astral_npc_expediciones`, `astral_npc_guia_reino` y `astral_npc_guia_cavernas`.
Regenerar con `python datapack-src/mobs/mythic.py`. Los comandos de colocacion
salen de `python datapack-src/mapas_exploracion.py --enlaces`, en
`build/mapas_exploracion/enlaces.txt`.

Se respaldo el YAML remoto antes de editar. Solo se cambio la interaccion de
Expediciones y se agregaron los dos guias, conservando las demas definiciones
remotas; se compararon los YAML antes y despues. Despues de guardar y volver
a leer el archivo se verifico que coincidiera con la configuracion preparada.
MythicMobs recargo 118 mobs y 384 skills, sin errores nuevos; siguen los tres
avisos conocidos de dialogos de ejemplo.

Se recreo unicamente Expediciones en su posicion anterior para renovar su
interaccion. Las posiciones de los tres aldeanos se verificaron por consola
a las 12:35:16 (Argentina). Se retiraron las dos cargas temporales de chunks.
No se modificaron bloques ni se colocaron NPCs de entrada a mazmorras.
Pendiente: comprobar los tres clics con el jugador. No se lo teletransporto
automaticamente ni se cambio su modo de juego.

## Descubrimiento y viajes (01/11/2026)

`/mazmorras` abre los destinos personales. Cada NPC de entrada concede
`astral.descubierto.<clave>` en LuckPerms al interactuar; el menu y el comando
directo vuelven a comprobarlo. El grupo default tiene `astral.descubierto.* false`
para evitar desbloqueos implicitos de OP. Los permisos exactos personales true
prevalecen. No se exige completar la historia, tampoco en SANTUARIO_ENTRAR.
Las interacciones anteriores a la instalacion no se pueden reconstruir: hablar
con el aldeano nuevamente. Fuente: viajes_mazmorras.py y mobs/mazmorra.py.
Skript se recarga con `skript reload astral_viajes`; `sk reload` pertenece a
AuraSkills en este servidor. Primera carga sin errores y 16 menus registrados.

Se instalaron nueve text_display en Cavernas, generados por
hologramas_mazmorras.py: inicio, profundidad1/2, cerca1/2/3 y tramo1/2/3.
Los tres ultimos dicen «Estás en el último tramo» en #B86AFF.
No se modificaron bloques y se retiraron las cargas temporales de chunks.

## Ampliacion a seis expediciones

Interfaz publica `/expediciones`, tambien alias `/expedicion`, y clic normal
en Expediciones Astrales. Ofrece seis busquedas, volver al lobby y abrir
las mazmorras descubiertas; buscar nunca concede el permiso de descubrimiento.

| Orden | Mazmorra | Mapa de busqueda | Llegada prevista |
|---|---|---|---|
| 1 | Bosque Sombrio | cavernas | 172.5 102 89.5 |
| 2 | Tumba | exp_desierto (mapa_desierto.zip) | 180.233 102 134.266 |
| 3 | Minas Olvidadas | cavernas | 172.5 102 89.5 |
| 4 | Cumbre | exp_nieve (nieve.zip) | 16.5 83 10.5 |
| 5 | Corazon de la Forja | forja (volcan sur anterior) | 1536.5 222 1900.5 |
| 6 | Santuario | exp_santuario (mapa_santuario.rar) | 26.5 103 -31.5 |

Los tres mapas nuevos son mundos separados. Se exporta el escenario completo
con un chunk de margen; en Santuario se excluye una isla tecnica desconectada
en 1000,1000. Sus nueve bloques de comandos permanecen, con Command vacio para
que no ejecuten el minijuego original. No se modifican bloques, paletas ni
construcciones. Originales y recortes quedan en .local, sin publicarse.
Los informes privados contienen hashes y comprobacion de piso 3x3, tres bloques
de aire y recorrido conectado. La revision visual final en Minecraft sigue
siendo necesaria, especialmente para mapas antiguos.

Los tres mundos nuevos se cargaron en Aternos y arrancaron correctamente. Se
fijaron sus spawns y se crearon los tres guias solo cuando coincidieron piso
y aire originales. Se verificaron sus posiciones por consola y se retiraron
las cargas temporales. No se movieron los aldeanos de entrada que coloco el
dueno. La exploracion visual y ubicacion de los guardianes restantes quedan
a criterio del dueno.

### Llegada del Desierto ajustada a la captura del dueno

Llegada: 180.233 102 134.266, yaw -124.8, pitch 0. Guia junto al camino:
179.5 102 135.5. Se actualizan tanto Multiverse como la ruta de /expediciones.
El NPC de prueba astral_npc_tumba en 185.27445 95 144.03117 se retira solo
en exp_desierto; la otra instancia de Tumba no se toca. No se modifican bloques.
Comandos generados: build/mapas_exploracion/ajuste-desierto.txt.

Revision final del 01/11: las cinco llegadas (Bosque y Minas comparten una)
pasaron en Aternos el piso 3x3 y tres bloques de aire por columna, con el guia
en su posicion. La inspeccion del Santuario ahora interpreta correctamente
la metadata de tablones 1.12 (abedul); sus bloques exportados no cambiaron.
Se confirmo la retirada efectiva del NPC de prueba de Desierto por consulta
de entidad vacia y una sola instancia restante de astral_npc_tumba. Por su
invulnerabilidad se retiro fijando Health=0 en la instancia de coordenadas
exactas, no eliminando globalmente el tipo. Se liberaron las seis cargas
temporales utilizadas durante esta revision.
