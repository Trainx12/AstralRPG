# Nave del Vacio (evento del End), 22/11/2026: DESPLEGADA y CERRADA

**Estado (22/11 12:39):** instalada en Empower, cerrada hasta el evento. Abrir: `nave abrir` en consola (o `/nave abrir`
como OP): da `astral.nave.abierta` al grupo default (la tarjeta de Portales pag. 2 pasa a "Clic para entrar") y avisa
a todos. Cerrar: `nave cerrar`. Mientras esta cerrada, quien no es OP y entra a un mundo de la nave vuelve al lobby.
Pack `0a1a1ce6` (FINAL en entregas/nave-22-11, sobre 3e616f39) = base del proximo. Respaldo en `.local/deploy-nave/respaldo`.
Datapack: se parcho solo mob/roll y mob/extra_mazmorra sobre el del server (el build tiene otros cambios sin subir).
AstralParty: se agregaron los 3 mundos y la Palma al jar del server (sin recompilar).

Mazmorra tier 5 dentro de la nave con forma de mano. 3 copias (`nave`, `nave_2`, `nave_3`).
Fuente: `datapack-src/nave.py`, `datapack-src/mobs/capitan_vacio.py`, `datapack-src/runtime/AstralNave.java`,
salas calculadas con `tools/nave_salas.py` -> `datapack-src/nave_salas.json`. Prueba local: `tools/probar_nave_paper.py`.

## Como se juega
1. `mazentrar <jugador> nave` (party y copia libre, como todas). Al llegar, **vista desde afuera** (15 s): la camara
   da una vuelta alrededor de la mano y baja hasta la muñeca. Agacharse la saltea. Despues aparece en el Hangar.
2. Salas: Hangar -> Dedo Menor -> Dedo Anular -> Punta del Indice -> Puente de Mando (Timonel del Vacio) -> Palma.
   Al limpiar una sala se abre la **compuerta** en su centro: pisarla (o esperar 20 s) lleva a todo el grupo a la
   siguiente. No se puede volver. Si alguien cae al casco hueco, vuelve a la llegada de la sala.
3. Palma: **Capitan del Vacio** (19.687.500 de vida). Al 70% salen 3 Ojos Vigias: mientras viva alguno, el Capitan
   recibe solo el 20% del daño. Al 40%: falla de gravedad (pulsos que levantan, zonas de vacio en el piso) y se acelera.
4. Al morir: `mazfin` (8 minutos), cofre (`cofre_nave`, sin fragmento: no cambia el Renacimiento) y guia.

Golpes de espada T5 (62.500): Capitan 315 + Ojos Vigias ~10 cada uno (590.625) = ~345 golpes sin criticos ni
encantamientos. Con criticos (x1,5) ~230. En party de 4: ~85 golpes cada uno. Si no rompen los Ojos, el tramo
70%->40% cuesta 5 veces mas.

## Lag
La vista desde afuera mueve un soporte invisible por jugador durante 15 s y le manda a ese jugador 14 chunks de
distancia mientras dura (mundo vacio con una sola nave: chunks casi vacios). No corre nada cuando no hay nadie.

## Archivos a subir
| Local | Server |
|---|---|
| `build/nave/AstralNave.jar` | `plugins/AstralNave.jar` (nuevo) |
| `build/mythicmobs/mobs/nave.yml` | `plugins/MythicMobs/Mobs/nave.yml` |
| `build/mythicmobs/skills/nave.yml` | `plugins/MythicMobs/Skills/nave.yml` |
| `build/models/astral_capitan_vacio.bbmodel`, `astral_ojo_vigia.bbmodel` | `plugins/BetterModel/models/` |
| `build/mazmorras/astral_mazmorras_copias.sk` | `plugins/Skript/scripts/` |
| `build/mazmorras/astral_puntaje.sk` | `plugins/Skript/scripts/` |
| `build/economia/Skript/scripts/astral_economia.sk` | `plugins/Skript/scripts/` (comparar antes con el del server) |
| `build/gameplay/astral_gameplay.sk` | `plugins/Skript/scripts/` (comparar antes: solo suma los 3 mundos de la nave) |
| `build/menus/DeluxeMenus/gui_menus/cofre_nave.yml` | `plugins/DeluxeMenus/gui_menus/` + entrada `cofre_nave` en `config.yml` |
| `.local/nave/spaceship.schem` (privado) | `plugins/WorldEdit/schematics/spaceship.schem` |
| datapack `build/AstralRPG-Items.zip` | tier 5 y vida x1,5 en los mundos de la nave (`python build.py`; comparar con el del server, ver memoria manzanas) |
| AstralParty.jar (`python party.py ...`) | revive en la Palma (boss-rooms) |

Pack: los modelos los convirtio BetterModel en la prueba local (`.local/nave-probe/srv/plugins/BetterModel/build`).
Hay que armar el FINAL privado ENCIMA del ultimo (3e616f39) con esos assets, subir a R2 y cambiar el sha1.

## Comandos (consola), en orden
Ver `build/nave/comandos.txt`: crear los 3 mundos, pegar la nave en cada uno (esperar "loaded" antes de `//paste`),
reglas y WorldGuard. Despues: `mm reload`, `skript reload astral_mazmorras_copias`, `skript reload astral_puntaje`,
`bettermodel reload` y reinicio por el pack.

## Admin
`/nave estado`, `/nave saltar <mundo>`, `/nave sala <mundo> <n>`, `/nave intro <jugador>`, `/nave reiniciar <mundo>`.

## Pendiente
- La pagina de Portales sigue con "Proximamente" (se abre la segunda semana). Para probar: `mazentrar <jugador> nave`.
- Probar con cliente: que el modelo se vea del tamaño correcto (11,7 bloques; BetterModel multiplica la escala del
  modelo por la de la entidad, como el Cangrejo de la Fosa), la camara de la vista y los efectos.
- Bordes de sala de AstralParty (zonas_pelea) no se agregaron: las salas ya estan cerradas y el plugin devuelve a
  quien sale de los limites.
