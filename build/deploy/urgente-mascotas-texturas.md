# Urgente: mascotas, texturas, Yeti, esqueletos y Cumbre

Despliegue PENDIENTE. Preparado para Empower (Paper 26.1.2 / Java 25, MythicMobs 5.13.0, BetterModel 3.6.0).
Aternos es copia; no se subio nada a ningun servidor ni a R2. No usar Worlds > Upload, mundos ni regiones.
PRIVADO = repositorio AstralRPG-privado, por defecto `.local/terceros/AstralRPG-privado`.

## Causa de las mascotas

`<global.pet_owner>` no es un placeholder valido en MythicMobs 5.13. El valido es `<global.var.pet_owner>`.
El anterior setowner no encontraba al jugador: la mascota quedaba sin UUID de dueno y ownerIsOnline la eliminaba.
Ahora sudoskill hace que el jugador invoque en su posicion y summonerIsOwner=true asigna su UUID, sin variable global.
Se conserva el control de permiso, seleccion, desconexion y guardado. Un pedido cambiado/guardado durante la demora se cancela.
Los bonus usan los nombres reales cumbre_hielo, forja_volcano y santuario_interstellar.

## Entrega unica: urgente y ajustes del menu/oleadas

Esta entrega reemplaza los packs y apoyos propuestos anteriormente. No ejecutar arreglos-apoyos.txt.
Los rangos de piso y comandos para recrear TODOS los controladores estan en arreglos-esqueleto-volcano.md y arreglos-puntos.json.
Si aun faltan los datapacks adaptados de parkour del arreglo anterior, usar las dos rutas privadas y destinos de esa guia; nunca subir mundos.
Menu: 14 accesos conservados + Fragmentos y Duelos; /trade en Comandos, Peluches dentro de la Tienda.
TAB: integrar scoreboard.scoreboards (minas, mazmorra, astral) y conditions de secciones-config.yml, conservando el resto del config remoto.
ScoreboardObjectives de PlaceholderAPI ya era requerido; conservar esa expansion. No necesita plugin nuevo.
Cada sala tiene bossbar PURPLE propia. Restantes suma vivos y pendientes; jugadores se asignan al controlador mas cercano para resolver radios solapados.
La barra se vacia al terminar/salir y no se muestra durante jefes. TAB reemplaza las diarias en los cinco mundos de mazmorra; Santuario sigue en espera.

## Archivos locales y destinos

| Local | Destino |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/mapas_exploracion/astral_viajes.sk` | `plugins/Skript/scripts/astral_viajes.sk` |
| `build/menus/DeluxeMenus/gui_menus/principal.yml` | `plugins/DeluxeMenus/gui_menus/principal.yml` |
| `build/menus/DeluxeMenus/gui_menus/comandos.yml` | `plugins/DeluxeMenus/gui_menus/comandos.yml` |
| `build/shop/EconomyShopGUI/sections/Peluches.yml` | `plugins/EconomyShopGUI/sections/Peluches.yml` |
| `build/shop/EconomyShopGUI/shops/Peluches.yml` | `plugins/EconomyShopGUI/shops/Peluches.yml` |
| `build/lobby/TAB/secciones-config.yml` | `plugins/TAB/config.yml: integrar scoreboard y conditions; conservar ajustes locales` |
| `build/models/astral_arana.bbmodel` | `plugins/BetterModel/models/astral_arana.bbmodel` |
| `build/models/astral_bosque_planta.bbmodel` | `plugins/BetterModel/models/astral_bosque_planta.bbmodel` |
| `build/models/astral_cangrejo.bbmodel` | `plugins/BetterModel/models/astral_cangrejo.bbmodel` |
| `build/models/astral_cara.bbmodel` | `plugins/BetterModel/models/astral_cara.bbmodel` |
| `build/models/astral_chaman.bbmodel` | `plugins/BetterModel/models/astral_chaman.bbmodel` |
| `build/models/astral_coloso_musgoso.bbmodel` | `plugins/BetterModel/models/astral_coloso_musgoso.bbmodel` |
| `build/models/astral_creeper_nuclear.bbmodel` | `plugins/BetterModel/models/astral_creeper_nuclear.bbmodel` |
| `build/models/astral_espantapajaros.bbmodel` | `plugins/BetterModel/models/astral_espantapajaros.bbmodel` |
| `build/models/astral_esq_arquero.bbmodel` | `plugins/BetterModel/models/astral_esq_arquero.bbmodel` |
| `build/models/astral_esq_escudero.bbmodel` | `plugins/BetterModel/models/astral_esq_escudero.bbmodel` |
| `build/models/astral_esq_guardian.bbmodel` | `plugins/BetterModel/models/astral_esq_guardian.bbmodel` |
| `build/models/astral_esq_nigromante.bbmodel` | `plugins/BetterModel/models/astral_esq_nigromante.bbmodel` |
| `build/models/astral_golem_forja.bbmodel` | `plugins/BetterModel/models/astral_golem_forja.bbmodel` |
| `build/models/astral_mapache.bbmodel` | `plugins/BetterModel/models/astral_mapache.bbmodel` |
| `build/models/astral_momia.bbmodel` | `plugins/BetterModel/models/astral_momia.bbmodel` |
| `build/models/astral_pinguino.bbmodel` | `plugins/BetterModel/models/astral_pinguino.bbmodel` |
| `build/models/astral_yeti.bbmodel` | `plugins/BetterModel/models/astral_yeti.bbmodel` |
| `build/mythicmobs/mobs/mascotas.yml` | `plugins/MythicMobs/mobs/mascotas.yml` |
| `build/mythicmobs/mobs/tanda3a.yml` | `plugins/MythicMobs/mobs/tanda3a.yml` |
| `build/mythicmobs/mobs/tanda3b.yml` | `plugins/MythicMobs/mobs/tanda3b.yml` |
| `build/mythicmobs/mobs/tanda4b.yml` | `plugins/MythicMobs/mobs/tanda4b.yml` |
| `build/mythicmobs/mobs/mazmorra.yml` | `plugins/MythicMobs/mobs/mazmorra.yml` |
| `build/mythicmobs/mobs/bosque.yml` | `plugins/MythicMobs/mobs/bosque.yml` |
| `build/mythicmobs/mobs/tumba.yml` | `plugins/MythicMobs/mobs/tumba.yml` |
| `build/mythicmobs/mobs/cumbre.yml` | `plugins/MythicMobs/mobs/cumbre.yml` |
| `build/mythicmobs/mobs/forja.yml` | `plugins/MythicMobs/mobs/forja.yml` |
| `build/mythicmobs/skills/tanda3b.yml` | `plugins/MythicMobs/skills/tanda3b.yml` |
| `build/mythicmobs/skills/mazmorra.yml` | `plugins/MythicMobs/skills/mazmorra.yml` |
| `build/mythicmobs/skills/bosque.yml` | `plugins/MythicMobs/skills/bosque.yml` |
| `build/mythicmobs/skills/tumba.yml` | `plugins/MythicMobs/skills/tumba.yml` |
| `build/mythicmobs/skills/cumbre.yml` | `plugins/MythicMobs/skills/cumbre.yml` |
| `build/mythicmobs/skills/forja.yml` | `plugins/MythicMobs/skills/forja.yml` |
| `PRIVADO/build/entregas/urgente-mascotas-texturas/models/astral_goblin.bbmodel` | `plugins/BetterModel/models/astral_goblin.bbmodel` |
| `PRIVADO/build/entregas/urgente-mascotas-texturas/models/astral_abejorro.bbmodel` | `plugins/BetterModel/models/astral_abejorro.bbmodel` |
| `PRIVADO/build/entregas/urgente-mascotas-texturas/mythicmobs/mobs/astral.yml` | `plugins/MythicMobs/mobs/astral.yml` |
| `PRIVADO/build/entregas/urgente-mascotas-texturas/mythicmobs/skills/astral.yml` | `plugins/MythicMobs/skills/astral.yml` |
| `PRIVADO/build/entregas/urgente-mascotas-texturas/mythicmobs/skills/mascotas.yml` | `plugins/MythicMobs/skills/mascotas.yml` |

No subir el ZIP publico de texturas: los 17 modelos privados de mascota y sus retratos ya instalados se conservan.
Los YAML privados astral.yml y skills/mascotas.yml tienen prioridad sobre las copias publicas.

## Pack FINAL

SHA-1: `9c181ed2a097ea27021f761346714ca04416e24f`. Tamano: 18733334 bytes. Auditoria: 5193 referencias de modelos.
`PRIVADO/build/entregas/urgente-mascotas-texturas/AstralRPG-Textures.zip` es la entrega aislada para publicar en el repo privado.
Todos los PNG usados por modelos estan en item/ o block/. Los sprites sinteticos de adornos son la excepcion: se generan con paletted_permutations declaradas en el atlas, no corresponden a PNG fuera del atlas.
Las capas Carnivora humanoid/humanoid_leggings conservan entity/equipment; las alas son item_display del runtime.
Los originales antiguos de Carnivora, Asura y peluches se retiraron del item-pack derivado; no se tocaron las fuentes.
La auditoria tambien normaliza PNG de modelos legacy de Stellarity y corrige su referencia ender_grass_block_side_snow.

## Instalacion (mazmorras vacias)

1. Respaldar los archivos que se reemplazan. Apagar el servidor: se cambia el datapack y el pack obligatorio.
2. Reemplazar solamente los archivos de la tabla. Conservar los otros modelos y configuraciones.
3. En plugins/WorldGuard/worlds/lobby/config.yml editar solo `mobs.block-plugin-spawning: false`.
   Conservar las regiones; `spawn_mobs=false` sigue evitando apariciones naturales. El arranque carga WG; si se edita encendido, `wg reload`.
4. Claude publica el FINAL con `python tools/subir_pack_r2.py <ruta-del-ZIP-FINAL>`; verificar la descarga publica y su SHA-1.
5. En server.properties conservar la URL R2 fija y poner `resource-pack-sha1=9c181ed2a097ea27021f761346714ca04416e24f`. Iniciar y revisar consola.
6. El arranque carga datapack, modelos, MythicMobs y Skript. Si se reemplazan YAML/script encendido: `mm reload`, `skript:skript reload astral_viajes`; para modelos: `bettermodel reload`.
   TAB: `tab reload`; menus: `dm reload`. Para esta entrega completa se recomienda un unico reinicio. No hacer varias recargas de prueba en produccion.
7. Recrear el controlador de mascotas (abajo) y TODOS los de mazmorra con salas vacias, usando arreglos-esqueleto-volcano.md.
8. Comprobar invocar/guardar/cambiar mascota y mundo, creativo/survival, bonus, arco en las tres animaciones, muerte y nuevas llegadas. Revisar consola.

## Comandos de actualizacion (sin /)

```text
execute in minecraft:lobby run forceload add 180 190
mm mobs kill astral_mascotas_control
mm mobs spawn astral_mascotas_control 1 lobby,180.5,92,190.5
```

Retirar espadachines existentes, con las mazmorras vacias (solo la etiqueta de esa variante):

```text
execute in minecraft:overworld run minecraft:kill @e[tag=ad.esq.espadachin]
execute in minecraft:the_nether run minecraft:kill @e[tag=ad.esq.espadachin]
execute in minecraft:the_end run minecraft:kill @e[tag=ad.esq.espadachin]
execute in minecraft:lobby run minecraft:kill @e[tag=ad.esq.espadachin]
execute in minecraft:arena run minecraft:kill @e[tag=ad.esq.espadachin]
execute in minecraft:mina run minecraft:kill @e[tag=ad.esq.espadachin]
execute in minecraft:bosque run minecraft:kill @e[tag=ad.esq.espadachin]
execute in minecraft:tumba run minecraft:kill @e[tag=ad.esq.espadachin]
execute in minecraft:cumbre_hielo run minecraft:kill @e[tag=ad.esq.espadachin]
execute in minecraft:forja_volcano run minecraft:kill @e[tag=ad.esq.espadachin]
execute in minecraft:santuario_interstellar run minecraft:kill @e[tag=ad.esq.espadachin]
```

No instalar el apoyo antiguo propuesto para Cumbre a Y32: el Yeti y el cofre vuelven al piso natural Y30.
Si aquel apoyo ya se instalo en el remoto, inspeccionarlo antes de habilitar Cumbre; no borrar construcciones por suposicion.

## Llegadas: tabla unica rutas_mazmorras.py

| Mazmorra | Mundo | Sala | X | Y | Z | yaw |
|---|---|---|---:|---:|---:|---:|
| mina | mina | sala1 | 10.5 | -45 | -124.5 | 0 |
| mina | mina | sala2 | 19.5 | -39 | -158.5 | 0 |
| mina | mina | sala3 | 43.5 | -24 | -201.5 | 0 |
| mina | mina | sala4 | 40.5 | 24 | -225.5 | 0 |
| bosque | bosque | sala1 | 1468.5 | 101 | 1570.5 | 0 |
| bosque | bosque | sala2 | 1603.7 | 100 | 1413.4 | -177.9 |
| tumba | tumba | sala1 | -148.426 | 62 | -97.473 | 0 |
| tumba | tumba | sala2 | -203.163 | 88 | 203.533 | 0 |
| tumba | tumba | sala3 | 0.368 | 73 | -44.104 | 0 |
| cumbre | cumbre_hielo | sala1 | -25.6 | 33 | -23.4 | 49.9 |
| cumbre | cumbre_hielo | sala2 | -54.9 | 30 | 6.5 | 45.7 |
| forja | forja_volcano | sala1 | 23.2 | 13 | -159.4 | 151.5 |
| forja | forja_volcano | sala2 | -125.5 | 13 | -125.7 | -13.4 |
| forja | forja_volcano | sala3 | 0.8 | 47 | 26 | -178.2 |
| santuario | santuario_interstellar | sala1 | 34.5 | 180 | 40.5 | 0 |

Entrada por NPC y /mazmorras usa la primera fila; transiciones usan la sala destino. Salidas: Essentials `spawn`, que toma el spawn vigente del lobby.
Cumbre: piso firme comprobado en -54.9 Y30 6.5 (white_concrete_powder); Y52.7 era la posicion desde donde el dueno miraba y no tiene piso ahi.
Jefe en -101.8 30 56.9, yaw -138.9. El generador anterior sobrescribia su llegada con la entrada de la oleada 1.

## Tamano y limites de la verificacion

Yeti Cumbre s=4, Ancestral s=2; alto 14 bloques, scale=6.363636, caja vanilla 12.409 x 14.
El ancho vanilla difiere del modelo (8 bloques). Sin intersecciones en el punto del jefe, llegada/puerta ni desplazamientos de 1 bloque en las cuatro direcciones del mapa local.
Detalles: urgente-yeti.json. Conserva la velocidad casi quieta elegida antes y los ataques del jefe. Falta recorrido de puerta y combate con cliente real.
No se obtuvo captura/video con cliente de la mascota siguiendo ni una comparacion con el esqueleto vanilla en Minecraft. Arco: detalle CPU frente/costado/3-4 en arco-arquero-animaciones.png.
Muerte: animacion death no repetida de 0.8 s, caida de 90 grados, articulaciones flojas. BetterModel usa su evento nativo de muerte; AST_MUERTE agrega tinte y poof.
Las vistas build/previews/muerte-*.png, yeti-tamano.png y esqueletos-brazos.png son renders CPU, no capturas de Minecraft.
GUI desde el FINAL: PRIVADO/build/entregas/urgente-mascotas-texturas/previews/urgente-gui-desde-pack.png (31 items).
El Paper local no cargo WorldGuard ni ClearLag; sus ajustes quedan para comprobar en el despliegue. La prueba NMS no reemplaza capturas/video con cliente ni la consola de produccion. No se instalaron plugins de prueba en remoto.
