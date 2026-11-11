# Arreglos de esqueletos, Volcano, salas e interfaces

Base: c3d4af8. Entrega local, SIN despliegue remoto. Servidor vigente: Empower; Aternos es copia.
No usar APIs privadas ni Worlds > Upload. Nunca reemplazar world ni subir mapas/regiones.

## Revision previa necesaria

Los apoyos propuestos para Tumba y Cumbre NO estan instalados: revisar y aprobar antes de desplegar las oleadas. Se proponen porque el jefe estaba bajo la llegada del jugador y los puntos alternativos altos eran tejados. No cambiar las llegadas elegidas por el dueno. `arreglos-apoyos.txt` contiene cada comando exacto: solo fill keep de bloques de apoyo; no borra ni sustituye bloques existentes. Si un apoyo ocupa una decoracion no solida, no desplegar: corregir el punto en el generador.

Vista propia: `build/previews/esqueletos-brazos.png` (cinco variantes, idle/caminar/ataque, frente/costado).
Menu: `build/previews/menu-astral-arreglos.png`. Son renders CPU, no capturas de Minecraft.
Vistas PRIVADAS: `.local/terceros/AstralRPG-privado/build/previews/arreglos-cofres.png` y `arreglos-mascotas.png`. Tambien `arreglos-apoyos.png` en esa carpeta privada muestra las cuatro salas afectadas. No copiarlas al repo publico. Falta aprobacion visual del dueno antes de instalar.

## Archivos exactos

| Archivo local | Destino |
|---|---|
| `build/models/astral_esq_arquero.bbmodel` | `plugins/BetterModel/models/astral_esq_arquero.bbmodel` |
| `build/models/astral_esq_escudero.bbmodel` | `plugins/BetterModel/models/astral_esq_escudero.bbmodel` |
| `build/models/astral_esq_espadachin.bbmodel` | `plugins/BetterModel/models/astral_esq_espadachin.bbmodel` |
| `build/models/astral_esq_guardian.bbmodel` | `plugins/BetterModel/models/astral_esq_guardian.bbmodel` |
| `build/mythicmobs/mobs/mazmorra.yml` | `plugins/MythicMobs/mobs/mazmorra.yml` |
| `build/mythicmobs/mobs/bosque.yml` | `plugins/MythicMobs/mobs/bosque.yml` |
| `build/mythicmobs/mobs/tumba.yml` | `plugins/MythicMobs/mobs/tumba.yml` |
| `build/mythicmobs/mobs/cumbre.yml` | `plugins/MythicMobs/mobs/cumbre.yml` |
| `build/mythicmobs/mobs/forja.yml` | `plugins/MythicMobs/mobs/forja.yml` |
| `build/mythicmobs/mobs/tanda3a.yml` | `plugins/MythicMobs/mobs/tanda3a.yml` |
| `build/mythicmobs/mobs/tanda3b.yml` | `plugins/MythicMobs/mobs/tanda3b.yml` |
| `build/mythicmobs/skills/mazmorra.yml` | `plugins/MythicMobs/skills/mazmorra.yml` |
| `build/mythicmobs/skills/bosque.yml` | `plugins/MythicMobs/skills/bosque.yml` |
| `build/mythicmobs/skills/tumba.yml` | `plugins/MythicMobs/skills/tumba.yml` |
| `build/mythicmobs/skills/cumbre.yml` | `plugins/MythicMobs/skills/cumbre.yml` |
| `build/mythicmobs/skills/forja.yml` | `plugins/MythicMobs/skills/forja.yml` |
| `build/mythicmobs/skills/tanda3a.yml` | `plugins/MythicMobs/skills/tanda3a.yml` |
| `build/mythicmobs/skills/tanda3b.yml` | `plugins/MythicMobs/skills/tanda3b.yml` |
| `build/menus/DeluxeMenus/gui_menus/principal.yml` | `plugins/DeluxeMenus/gui_menus/principal.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascotas_2.yml` | `plugins/DeluxeMenus/gui_menus/mascotas_2.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascotas_3.yml` | `plugins/DeluxeMenus/gui_menus/mascotas_3.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_ghastito.yml` | `plugins/DeluxeMenus/gui_menus/mascota_ghastito.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_bombardero.yml` | `plugins/DeluxeMenus/gui_menus/mascota_bombardero.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_canonero.yml` | `plugins/DeluxeMenus/gui_menus/mascota_canonero.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_encapuchado.yml` | `plugins/DeluxeMenus/gui_menus/mascota_encapuchado.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_llamita.yml` | `plugins/DeluxeMenus/gui_menus/mascota_llamita.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_hondero.yml` | `plugins/DeluxeMenus/gui_menus/mascota_hondero.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_saqueador.yml` | `plugins/DeluxeMenus/gui_menus/mascota_saqueador.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_brujita.yml` | `plugins/DeluxeMenus/gui_menus/mascota_brujita.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_desierto.yml` | `plugins/DeluxeMenus/gui_menus/mascota_desierto.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_jungla.yml` | `plugins/DeluxeMenus/gui_menus/mascota_jungla.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_frondoso.yml` | `plugins/DeluxeMenus/gui_menus/mascota_frondoso.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_micelio.yml` | `plugins/DeluxeMenus/gui_menus/mascota_micelio.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_pradera.yml` | `plugins/DeluxeMenus/gui_menus/mascota_pradera.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_sabana.yml` | `plugins/DeluxeMenus/gui_menus/mascota_sabana.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_nieve.yml` | `plugins/DeluxeMenus/gui_menus/mascota_nieve.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_pantano.yml` | `plugins/DeluxeMenus/gui_menus/mascota_pantano.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_honguito.yml` | `plugins/DeluxeMenus/gui_menus/mascota_honguito.yml` |
| `build/lobby/CrazyCrates/crates/gacha_monturas.yml` | `plugins/CrazyCrates/crates/gacha_monturas.yml` |
| `build/lobby/CrazyCrates/crates/gacha_monturas_garantia.yml` | `plugins/CrazyCrates/crates/gacha_monturas_garantia.yml` |
| `build/mapas_exploracion/astral_viajes.sk` | `plugins/Skript/scripts/astral_viajes.sk` |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `.local/mapas/subir/parkour_paradise3-datapack.zip` (PRIVADO) | `world/datapacks/parkour_paradise3-datapack/` (descomprimir contenido, reemplazar la version instalada) |
| `.local/mapas/subir/parkour_spiral2-datapack.zip` (PRIVADO) | `world/datapacks/parkour_spiral2-datapack/` (descomprimir contenido, reemplazar la version instalada) |
| `.local/arreglos-pack/AstralRPG-Textures.zip` (FINAL PRIVADO) | R2, objeto `AstralRPG-Textures.zip`; verificar descarga publica y actualizar `resource-pack-sha1` |

No subir tambien una copia ZIP de los parkours si se conserva la carpeta: evitar dos versiones habilitadas. Reemplazar los datapacks adaptados COMPLETOS: funciones more_maps inertes y logros imposibles. El texto Volcano esta en more_maps:interact; sus llamadas tick y logros de Interaction explican el riesgo de reentrada. No se inspecciono el servidor remoto; si persiste, descargar SOLO las carpetas instaladas `world/datapacks/parkour_paradise3-datapack/`, `world/datapacks/parkour_spiral2-datapack/` y cualquier otro pack con namespace `more_maps`, a `.local/coordination/servidor-datapacks/` para comparar. No bajar ni subir mundos.

## Orden y recargas

1. Aprobar vistas y apoyos; salas vacias, respaldo de archivos de la tabla. Apagar el servidor.
2. Subir los archivos indicados. Subir el pack FINAL privado con `python tools/subir_pack_r2.py .local/arreglos-pack/AstralRPG-Textures.zip`, verificar descarga publica y SHA-1; entonces actualizar server.properties. No usar el ZIP publico como pack final.
3. Iniciar y revisar consola. El reinicio carga datapack, modelos y configs. Para ajustes posteriores: `bettermodel reload`, `mm reload`, `dm reload`, `crates reload`, `skript:skript reload astral_viajes`. `minecraft:reload` solo recarga datapacks; no sustituye reinicio de propiedades/pack.
4. ANTES de admitir jugadores a las salas, ejecutar los comandos aprobados de `arreglos-apoyos.txt`. Comprobar suelo y aire en TODOS los puntos de `arreglos-puntos.json`. Es requisito de esta version, no una migracion automatica.
5. Recrear los controladores SOLO con salas vacias; mismas coordenadas e IDs (abajo). No matar un jefe con una partida activa. Probar oleadas, ayudantes, cofre, guia y vuelta al lobby.
6. Reconectar con pack y comprobar brazos/arco y contorno. Probar ataques e Interaction en world sin Volcano, y ambos parkours sin publicidad repetida. Revisar 25 accesos del menu, las 23 mascotas y vitrina normal/garantizada.

## Cofres

| Mazmorra | Plataforma | Cofre X Y Z |
|---|---|---|
| Minas Olvidadas | No: spawn del jefe | (36.5, 24, -248.5) |
| Bosque Sombrio | Si: altar de troncos | (1604.5, 101, 1382.5) |
| Tumba del Rey de Arena | Si: altar de oro, elevar apoyo propuesto | (0.5, 73, 0.5) |
| Cumbre Helada | No: spawn del jefe | (-101.8, 33, 56.9) |
| Corazon de la Forja | No: spawn del jefe | (-7.9, 47, -21.1) |

Forja: aire Y47 sobre suelo invisible barrier Y46 y lava Y45. No se coloca el cofre dentro de ninguno. La sala no tiene una tarima visible diferenciada junto al jefe. Minas: suelo de ladrillo continuo. Cumbre: plaza de nieve; el apoyo propuesto resuelve la altura, sin inventar un altar de recompensa.

## Controladores (solo sin jugadores)

```text
mm mobs kill astral_mina_control_sala1
execute in minecraft:mina run function astral:tanda2/mina/sala1/reset
mm mobs spawn astral_mina_control_sala1 1 mina,10.5,-45,-124.5
mm mobs kill astral_mina_control_sala2
execute in minecraft:mina run function astral:tanda2/mina/sala2/reset
mm mobs spawn astral_mina_control_sala2 1 mina,19.5,-39,-158.5
mm mobs kill astral_mina_control_sala3
execute in minecraft:mina run function astral:tanda2/mina/sala3/reset
mm mobs spawn astral_mina_control_sala3 1 mina,43.5,-24,-201.5
mm mobs kill astral_mina_control_sala4
execute in minecraft:mina run function astral:tanda2/mina/sala4/reset
mm mobs spawn astral_mina_control_sala4 1 mina,36.5,24,-248.5
mm mobs kill astral_bosque_control_sala1
execute in minecraft:bosque run function astral:tanda2/bosque/sala1/reset
mm mobs spawn astral_bosque_control_sala1 1 bosque,1468.5,101,1570.5
mm mobs kill astral_bosque_control_sala2
execute in minecraft:bosque run function astral:tanda2/bosque/sala2/reset
mm mobs spawn astral_bosque_control_sala2 1 bosque,1604.5,101,1382.5
mm mobs kill astral_tumba_control_sala1
execute in minecraft:tumba run function astral:tanda2/tumba/sala1/reset
mm mobs spawn astral_tumba_control_sala1 1 tumba,-148.5,60,-98.5
mm mobs kill astral_tumba_control_sala2
execute in minecraft:tumba run function astral:tanda2/tumba/sala2/reset
mm mobs spawn astral_tumba_control_sala2 1 tumba,-175.5,88,203.5
mm mobs kill astral_tumba_control_sala3
execute in minecraft:tumba run function astral:tanda2/tumba/sala3/reset
mm mobs spawn astral_tumba_control_sala3 1 tumba,0.568,72,0.512
mm mobs kill astral_cumbre_control_sala1
execute in minecraft:cumbre_hielo run function astral:tanda2/cumbre/sala1/reset
mm mobs spawn astral_cumbre_control_sala1 1 cumbre_hielo,-25.6,33,-23.4
mm mobs kill astral_cumbre_control_sala2
execute in minecraft:cumbre_hielo run function astral:tanda2/cumbre/sala2/reset
mm mobs spawn astral_cumbre_control_sala2 1 cumbre_hielo,-101.8,30,56.9
mm mobs kill astral_forja_control_sala1
execute in minecraft:forja_volcano run function astral:tanda2/forja/sala1/reset
mm mobs spawn astral_forja_control_sala1 1 forja_volcano,23.2,13,-159.4
mm mobs kill astral_forja_control_sala2
execute in minecraft:forja_volcano run function astral:tanda2/forja/sala2/reset
mm mobs spawn astral_forja_control_sala2 1 forja_volcano,-125.5,13,-125.7
mm mobs kill astral_forja_control_sala3
execute in minecraft:forja_volcano run function astral:tanda2/forja/sala3/reset
mm mobs spawn astral_forja_control_sala3 1 forja_volcano,-7.9,47,-21.1
```

## Interfaces auditadas

Principal: 14 accesos conservados y 11 agregados: Bosque, Fragmentos, tienda, peluches, subastas, venta, intercambio, tres gachas y duelos. Forja y recetas siguen en Guia; titulos en Cosmeticos; todas las paginas de aventura siguen accesibles. Trade y Duel requieren nombre, por eso el boton explica el comando.
Mascotas: paginas 1/2/3 y 23 detalles; iconos de nuevas mascotas en el circuito privado. CrazyCrates: 20 mascotas obtenibles en gacha (17 nuevas + cuervo/dragon/fenix); Lobo/Golem/Zorro conservan drops. Pesos y garantia sin cambio. Guia: catalogo completo en tres paginas. Misiones/cronista: contador pet generico cubre las 23; no habia lista fija de seis en sus textos. TAB no muestra mascota activa; no necesita lista nueva. El panel artistico de pagina 1 y los seis detalles originales conservan arte; nuevas paginas usan sus modelos privados.

## Reproduccion del pack aislado

La base privada aprobada es a6d26e9 / SHA-1 a18b694f5002cef979fe72ad6caf24134550db03. Tras convertir los modelos con BetterModel local: `python tools/copiar_assets_arreglos.py .local/tanda4a-paper/plugins/BetterModel/build/assets`; `python datapack-src/build_pack.py datapack-src/pack-source`; `python tools/armar_pack_arreglos.py`. Los 17 iconos se preparan con build_privado.py --prepare, pero el ensamblador aislado toma SOLO sus 51 archivos catalogo_<id>, sin mezclar los demas derivados privados. Procedencia y hash en `.local/arreglos-pack/procedencia.json`. La copia exclusiva para Git privado esta en `build/entregas/arreglos-esqueleto-volcano/` de ese repositorio. Se detecto una edicion concurrente ajena en tanda4b_privado.py: no se incluye en el commit ni en este pack aislado.

## Limites

No se desplego ni se subio a R2. No hubo cliente Minecraft conectado: falta captura en juego del contorno y aprobacion visual. Las pruebas del tracker y regresiones se informan en el resultado; un render CPU no certifica el cliente. Los apoyos son una propuesta explicita, no una modificacion del mapa instalada. Mundo normal: conservados puntos de elites y aparicion natural; solo se corrige el rig compartido. Santuario sin cambios.
Pack publico (reserva): SHA-1 `041c895fe6b0081fa2daffd0a2657958be869253`.
Pack FINAL privado aislado: SHA-1 `faf97322ae9f701e748cd7d585d4fd7fccfdf364`.
