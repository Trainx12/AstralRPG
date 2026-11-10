# Minas Astrales

Todo sale de `datapack-src/minas.py` (números, precios, instalación, panel de TAB) y `datapack-src/minas.sk`
(lógica). Correr `python minas.py` y `python lobby.py` desde `datapack-src/`.

**Solo usa Skript + Vault (EssentialsX).** La primera versión necesitaba skript-reflect, que Aternos no tiene en su
catálogo (y no se pueden subir `.jar` a mano), así que se reescribió entera en Skript puro (03/11/2026).

## Las 20 minas

| # | Mina | Mezcla | Para abrirla: bloques en la anterior | Oro |
|---|---|---|---:|---:|
| 1 | I · Carbón | piedra + 22 % mena | — | — |
| 2-6 | I · Cobre, Hierro, Oro, Esmeralda, Diamante | piedra + 22 % mena | 400 → 1.300 | 80 → 1.300 |
| 7-12 | II · Carbón … Diamante | mena + 30 % bloque compacto | 1.700 → 4.500 | 2.500 → 60.000 |
| 13 | II · Restos ancestrales | netherrack + 8 % restos | 5.500 | 120.000 |
| 14-19 | III · Carbón … Diamante | solo bloques compactos | 7.000 → 20.000 | 250.000 → 700.000 |
| 20 | III · Netherita | solo bloques de netherita | 500.000 | 25.000.000 + 25 h de minería activa en Diamante III |

- Los bloques solo cuentan en **la mina más alta que abriste** (la que lleva a la siguiente). Se cuentan en memoria
  y se guardan cada 30 s y al salir (no se escribe el disco en cada bloque).
- "Minería activa" = estar en Diamante III habiendo picado en los últimos 10 segundos.
- Precios de venta en `PRICES` (piedra y roca 0,1; carbón 0,6; diamante 8; bloque de diamante 72; restos 600;
  bloque de netherita 4.000…). Ojo: Tier III Carbón paga menos por bloque que Restos ancestrales (los bloques de
  carbón valen poco); se compensa con que son 100 % bloques y con el costo bajo de las siguientes.

## Cómo funciona

- **Lobby:** aldeano *Minas Astrales* (`astral_npc_minas`, MythicMobs) 4 bloques al oeste de Expediciones. Abre
  el menú (`/minas` también, desde el lobby o las minas): verde = abierta (clic viaja), amarilla = la siguiente
  (muestra bloques, oro y ✔/✘; clic la desbloquea si cumple), barrera = bloqueada.
- **Cada mina:** aldeano *Venta rápida* (`astral_npc_mina_venta`) junto a la plataforma, con el botón
  **"Vender todos mis minerales"** (muestra cuánto te pagan). Vende minerales, piedra y roca del inventario; no
  toca nada con nombre o descripción (equipo y objetos Astral).
- **Viajes:** en cada mina, del otro lado de la plataforma, el aldeano *Viajes* (`astral_npc_mina_viaje`) abre el
  mismo menú: volver al lobby o ir a otra mina abierta.
- **Protección:** en el mundo `astral_minas` solo se pueden romper los bloques de la mezcla, dentro del pozo, y
  en una mina abierta. No se puede poner bloques, ni explotar, ni recibir daño. Si alguien entra por `/tp` a una
  mina que no abrió, vuelve al spawn. Si cae al vacío, vuelve a la plataforma.
- **Taladros:** el datapack no pica en este mundo (tag `astral.mines`); el script rompe el área del taladro
  (se reconoce por el nombre del ítem) solo dentro del pozo, y esos bloques también cuentan. Con Shift pica uno.
- **Auto-recolectado:** lo que se pica (a mano o con taladro) va directo al inventario, respetando Fortuna. Si el
  inventario está lleno, cae a los pies del jugador.
- **Regeneración:** cada mina tiene dos moldes ya rellenos debajo del pozo (y −20..−1 y −45..−26, tapados por la
  isla). Regenerar es un solo `/clone` del molde al pozo, alternando moldes. Solo se regenera una mina con gente
  adentro, cada 9 minutos (aviso 10 s antes; los que están en el pozo suben a la plataforma).
- **Panel lateral (TAB):** en el mundo de minas el panel es el mismo, pero en lugar de las misiones diarias muestra
  la mina actual, la siguiente, bloques picados / necesarios, el costo y (en Diamante III) los minutos.

## Mapas

Las 20 minas usan el schematic de Hierro, `astral-mina-hierro.schem`. Cada copia conserva la mezcla de su rango, el vendedor y el aldeano de viajes.

El pozo ocupa X local 82–112, Y 73–92 y Z 78–108. En Hierro I equivale a X 1106–1136. El punto de pegado es X base + 7, Y 64 y Z 2 para alinear la plantilla con ese pozo.

Para migrar un mundo existente, seguir [reemplazar-mapas.txt](../build/minas/reemplazar-mapas.txt). El procedimiento limpia las construcciones anteriores antes de pegar, conserva las entidades y vuelve a preparar los moldes con los límites corregidos. Hacer una copia del mundo antes de ejecutar la limpieza.

## Instalación en Aternos

Seguir [instalacion.txt](../build/minas/instalacion.txt) en orden:

1. Crear el mundo `astral_minas` con Multiverse y sus reglas.
2. Pegar las 20 copias del mapa de Hierro en el juego (creativo, OP) con `//schem load` + `//paste -a`.
3. Invocar los 20 aldeanos de venta y el del lobby (`mm mobs spawn ...`). Antes subir el `astral.yml` nuevo de
   MythicMobs y `mm reload`.
4. Subir `build/minas/Skript/scripts/astral_minas.sk` a `plugins/Skript/scripts/` y la sección de TAB
   (`build/lobby/TAB/secciones-config.yml`: `scoreboard`, `conditions`, `placeholders` y
   `placeholder-output-replacements`). Combinar las claves de las dos últimas secciones
   con las que ya existan en TAB. Copiar el Skript generado antes de ejecutar
   `skript reload astral_minas` y `tab reload`. La barra de bloques muestra el avance y los
   bloques restantes; la de minutos solo aparece al preparar la última mina.
5. `/minasmoldes` (rellena los moldes, unos segundos por mina; se puede de a una: `/minasmoldes 5`) y `/minasactivar`.

El datapack ya tiene el cambio del taladro (no hace falta volver a subirlo).

La presentación de `/minas` y de venta rápida usa el marco propio del resource
pack. Generación, vistas previas y despliegue: [Interfaces de Portales y Minas](INTERFACES_PORTALES_MINAS.md).

Comandos de admin (`astral.minas.admin`): `/minasmoldes [n]`, `/minasactivar`, `/minasreset <n>`,
`/minasrango <jugador> <n>`. Con creativo + ese permiso se puede editar el mundo libremente.

## Probado

En el Paper local (Skript 2.17.1, sin skript-reflect): el script carga sin errores, los moldes salen con la mezcla
correcta, el `clone` regenera el pozo alternando moldes, los precios, la detección de mina/pozo y el área del
taladro. **No probado con un jugador real** (menú, cobro, venta y picar): probarlo en Aternos al instalar.

## Estado en Aternos (03/11/2026)

Instalado y activado: mundo `astral_minas`, los 20 mapas pegados (verificado el piso de cada pozo), 20 aldeanos de
venta, aldeano del lobby, script cargado sin errores, panel de TAB y moldes rellenos.
- `//schem load` necesita el nombre **con `.schem`** (sin la extensión WorldEdit dice "Invalid value for <schematic>").
- Los pegados se hicieron con `sudo <jugador> /paste -a` estando el jugador en la esquina de cada mina: WorldEdit
  desde la consola no puede elegir dónde pegar.

## Migración al mapa común en Aternos

Se copiaron los bloques de Hierro I al resto de las minas por chunks con `astral_minas_migracion.sk`. Se verificaron las esquinas de los pozos, se reconstruyeron los moldes y se reactivó la regeneración. La prueba en Hierro I clonó 19.220 bloques. La consola confirmó que las veinte minas conservan un aldeano en cada uno de los dos puntos previstos. El mundo se guardó al finalizar.

## Tanda 1: acceso al menu

`/minas` abre la interfaz desde cualquier mundo, incluidas mazmorras y expediciones. La restriccion anterior aparecio en `8771e8f` al quitar skript-reflect, sin motivo de combate documentado; se retiro sin agregar bloqueos de duelos. Regenerar con `python minas.py`; salida `build/minas/Skript/scripts/astral_minas.sk`.
