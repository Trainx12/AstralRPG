# Tanda 3c: maquinas de Mini juegos, NPC en 3D y mejoras de jefes

Generado por `datapack-src/mobs/entrega_tanda3c.py`. Nada de esto se instala solo.

## Archivos

- Pack FINAL (privado) a R2: `python tools/subir_pack_r2.py .local/terceros/AstralRPG-privado/build/AstralRPG-Textures.zip`
- `resource-pack-sha1=a18b694f5002cef979fe72ad6caf24134550db03` en `server.properties` (comprobar antes la descarga publica).
- `plugins/BetterModel/models/`: `astral_maquina_arcade.bbmodel`, `astral_maquina_capsulas.bbmodel`, `astral_npc_mago.bbmodel`, `astral_npc_herrero.bbmodel`, `astral_npc_subastas.bbmodel`, `astral_npc_bazar.bbmodel`, `astral_npc_cronista.bbmodel`, `astral_npc_minero.bbmodel`, `astral_npc_caballero.bbmodel`, `astral_npc_hechicero.bbmodel`, `astral_npc_bruja.bbmodel`, `astral_coloso_musgoso.bbmodel`, `astral_bosque_planta.bbmodel`, `astral_momia.bbmodel`, `astral_yeti.bbmodel`, `astral_golem_forja.bbmodel`, `astral_cangrejo.bbmodel`, `astral_chaman.bbmodel`, `astral_chocobo.bbmodel`, `astral_ave.bbmodel`, `astral_pterodactilo.bbmodel` desde `build/models/`, y `astral_vendedor.bbmodel` desde el build privado (ahora con el hueso del nombre).
- `plugins/MythicMobs/mobs/`: `tanda3c.yml`, `arena.yml`, `portales.yml`, `mazmorra.yml`, `bosque.yml`, `tumba.yml`, `cumbre.yml`, `forja.yml` desde `build/mythicmobs/mobs/`; `astral.yml` desde el build PRIVADO (conserva los vendedores).
- `plugins/MythicMobs/skills/`: `tanda3c.yml` publico y `astral.yml` del build PRIVADO.
- `plugins/Skript/scripts/astral_minijuegos.sk` (usa `minecraft:kill`).
- Santuario no se toca. La Tienda sigue como aldeano.

## Orden

1. `list` (sin jugadores), respaldo en `.local/deploy-backups/tanda3c-<fecha>/`, apagar.
2. Subir pack a R2, verificar SHA-1 publico, actualizar `server.properties`, subir archivos y comparar tamanos.
3. Encender, esperar `Done (` y revisar el log (modelos cargados, sin errores de MythicMobs).

## NPC

Cada NPC conserva su aldeano, nombre y clics; el modelo se pone solo al cargar (`~onLoad`). Si alguno sigue viendose como aldeano,
rehacerlo en su lugar con estas lineas (primero `forceload add` alrededor en `astral_minas` y `astral_bosque`):

```
rg flag -w lobby __global__ mob-spawning allow
rg flag -w astral_bosque __global__ mob-spawning allow
mm mobs kill astral_npc_bazar
mm mobs spawn astral_npc_bazar 1 lobby,178.637,101,152.678,-1.7,0
mm mobs kill astral_npc_subastas
mm mobs spawn astral_npc_subastas 1 lobby,205.466,100,175.476,2.7,0
mm mobs kill astral_npc_herrero
mm mobs spawn astral_npc_herrero 1 lobby,198.657,100,181.429,92.1,0
mm mobs kill astral_npc_expediciones
mm mobs spawn astral_npc_expediciones 1 lobby,178.636,100,225.735,180,0
mm mobs kill astral_npc_viajero
mm mobs spawn astral_npc_viajero 1 lobby,178.0,98,190.0,180,0
mm mobs kill astral_npc_cronista
mm mobs spawn astral_npc_cronista 1 lobby,181.636,100,225.735,180,0
mm mobs kill astral_npc_minas
mm mobs spawn astral_npc_minas 1 lobby,174.636,100,225.735,180,0
mm mobs kill astral_npc_mina_viaje
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,84.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,596.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,1108.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,1620.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,2132.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,2644.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,3156.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,3668.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,4180.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,4692.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,5204.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,5716.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,6228.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,6740.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,7252.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,7764.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,8276.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,8788.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,9300.5,93,70.5,0,0
mm mobs spawn astral_npc_mina_viaje 1 astral_minas,9812.5,93,70.5,0,0
mm mobs kill astral_npc_bosque_viaje
mm mobs spawn astral_npc_bosque_viaje 1 astral_bosque,-7.5,65,56.5,-90,0
mm mobs kill astral_npc_arena
mm mobs spawn astral_npc_arena 1 lobby,127.5,100,193.529
rg flag -w lobby __global__ mob-spawning deny
rg flag -w astral_bosque __global__ mob-spawning deny
```

Guardianes escondidos de mazmorra (`astral_npc_mina`, `astral_npc_bosque`, `astral_npc_tumba`, `astral_npc_cumbre`, `astral_npc_forja`): usan la bruja y siguen con el nombre oculto; los recoloca el dueno solo si hiciera falta.

## Maquinas de Mini juegos

Las dos abren el mismo panel (`dm open parkour`). El dueno elige el lugar; el ultimo numero es hacia donde miran (0 sur, 90 oeste, 180 norte, -90 este):

```
rg flag -w lobby __global__ mob-spawning allow
mm mobs spawn astral_maquina_arcade 1 lobby,<x>,<y>,<z>,<giro>,0
mm mobs spawn astral_maquina_capsulas 1 lobby,<x>,<y>,<z>,<giro>,0
mm mobs kill astral_npc_parkour
rg flag -w lobby __global__ mob-spawning deny
```

## Probar con un jugador

- Nombre visible arriba de cada NPC, maquina y vendedor (hueso `mtag_nombre` de BetterModel).
- Clic en cada NPC abre su menu de siempre y hace el saludo; clic en los bordes de las maquinas tambien abre el panel.
- Pantalla, marquesina y luces de las maquinas a brillo maximo; cupula transparente con las capsulas a la vista.
- Jefes: yeti, golem de la forja, momia, chaman y cangrejo con su tamano y ataques de siempre.
