# Tanda 2: instalacion pendiente

NO desplegado. El dueno debe ver `build/previews/tamanos-jefes.png` antes de subir.
Servidor actual: Empower (Aternos es copia). No se uso navegador, API ni red para desplegar.
No subir mundos, regiones, mapas, `.local`, logs ni carpetas enteras.

## Archivos locales → destino

| Local | Destino |
|---|---|
| build/AstralRPG-Items.zip | world/datapacks/AstralRPG-Items.zip |
| build/lobby/TAB/secciones-config.yml | plugins/TAB/config.yml: agregar type: AND a conditions.daily_count_0..7, conservando el resto |
| build/mythicmobs/mobs/astral.yml | plugins/MythicMobs/mobs/astral.yml |
| build/mythicmobs/skills/astral.yml | plugins/MythicMobs/skills/astral.yml |
| build/mythicmobs/mobs/mazmorra.yml | plugins/MythicMobs/mobs/mazmorra.yml |
| build/mythicmobs/skills/mazmorra.yml | plugins/MythicMobs/skills/mazmorra.yml |
| build/mythicmobs/mobs/bosque.yml | plugins/MythicMobs/mobs/bosque.yml |
| build/mythicmobs/skills/bosque.yml | plugins/MythicMobs/skills/bosque.yml |
| build/mythicmobs/mobs/tumba.yml | plugins/MythicMobs/mobs/tumba.yml |
| build/mythicmobs/skills/tumba.yml | plugins/MythicMobs/skills/tumba.yml |
| build/mythicmobs/mobs/cumbre.yml | plugins/MythicMobs/mobs/cumbre.yml |
| build/mythicmobs/skills/cumbre.yml | plugins/MythicMobs/skills/cumbre.yml |
| build/mythicmobs/mobs/forja.yml | plugins/MythicMobs/mobs/forja.yml |
| build/mythicmobs/skills/forja.yml | plugins/MythicMobs/skills/forja.yml |

Resource pack y modelos sin cambios; NO subirlos en esta tanda.
SHA-1 del pack conservado: `7a99922fb1734f4f80c64cee3f363a7b4d2404cb`. URL fija R2 documentada en SERVIDOR.md.

## Orden

1. Mostrar la vista previa al dueno. Resolver el limite de hitbox del Yeti antes de habilitar Cumbre al publico.
2. Mazmorras vacias: respaldar los archivos que se reemplazan y spigot.yml. Apagar el servidor.
3. Comprobar `settings.attribute.maxHealth.max`: minimo 13125000; conservar o poner 1000000000. La copia local fichas-paper tiene 1000000000, pero asw-native conserva 1024; el valor del servidor actual NO esta verificado. No subir esas configs locales enteras. Editar solo ese valor si hace falta.
4. Reemplazar los 13 archivos completos listados y editar las 8 condiciones de TAB. No tocar Santuario ni el mundo forja de expedicion.
5. Iniciar: el arranque carga datapack y YAML. Revisar consola por errores de funciones, atributos y MythicMobs. Si los YAML/TAB se editaron despues: `mm reload`, `tab reload`. No hace falta `bettermodel reload` ni R2.
6. Ejecutar los bloques siguientes con las mazmorras vacias (limpian controladores viejos, restos y crean los nuevos). Los objetivos ad.* se crean al cargar el datapack. Las cargas temporales se retiran al terminar.
7. Probar oleadas con 1, 2 y 5 jugadores: cola, 4 de llegada, limite 6/9, abandono/reset, jefe muerto, ayudantes, cofre y regreso. Comprobar magma sin division, piglins/hoglins sin zombificacion, Chaman sin vex, inmunidad al fuego y proyectiles del Yeti. Revisar consola y vida real con `attribute <UUID> minecraft:max_health get`. No afirmar despliegue hasta verificarlo.

## Resumen por mazmorra

| Mazmorra | Oleadas por sala previa | Puntos | Jefe / vida | s / scale |
|---|---|---|---|---|
| mina | 2, 2, 2 | sala1: 24, sala2: 1, sala3: 24, sala4: 24 | (36.5, 24, -248.5) / 72.000 | 2 / 2.24537 |
| bosque | 3 | sala1: 24, sala2: 24 | (1604.5, 101, 1382.5) / 12.500 | 2 / 2.628205 |
| tumba | 2, 3 | sala1: 10, sala2: 12, sala3: 12 | (0.568, 72, 0.512) / 460.000 | 2 / 2.102564 |
| cumbre | 4 | sala1: 24, sala2: 24 | (-101.8, 30, 56.9) / 2.475.000 | 16 / 16 |
| forja | 2, 2 | sala1: 24, sala2: 24, sala3: 24 | (-7.9, 47, -21.1) / 13.125.000 | 8 / 8.981481 |

Puntos exactos y selecciones: `build/deploy/tanda2-puntos.json`. Leidos de los mapas locales del servidor, sin modificarlos.

## Limites de tamano comprobados

- cumbre: caja vanilla 31.2 × 35.2 bloques; 396 bloques no aire intersectan su volumen en el punto pedido. Ejemplos y medidas en el JSON. Esta lectura estatica detecta interferencias; falta validar colisiones/IA en Paper.
- forja: caja vanilla 12.574 × 24.25 bloques; 0 bloques no aire intersectan su volumen en el punto pedido. Ejemplos y medidas en el JSON. Esta lectura estatica detecta interferencias; falta validar colisiones/IA en Paper.

Yeti: el modelo de 56 bloques excede el alto maximo de la caja (35,2). Se conserva el tamano pedido; Cumbre queda para prueba privada hasta que el dueno decida como resolver esa limitacion. El Golem conserva persecucion y step_height alto.

## Comandos de actualizacion (sin /)

### mina

```text
# Actualizacion Tanda 2. Mazmorra VACIA. No crear/importar/reemplazar mundos.
# Respaldar archivos del servidor; apagar para instalar el datapack y YAML, luego iniciar.
# El arranque carga MythicMobs; si se ajusto despues: mm reload.
# Cargar y retirar cada controlador anterior.
execute in minecraft:mina run forceload add 10 -125
mm mobs kill astral_mina_control_sala1
execute in minecraft:mina run forceload remove 10 -125
execute in minecraft:mina run forceload add 19 -159
mm mobs kill astral_mina_control_sala2
execute in minecraft:mina run forceload remove 19 -159
execute in minecraft:mina run forceload add 43 -202
mm mobs kill astral_mina_control_sala3
execute in minecraft:mina run forceload remove 43 -202
execute in minecraft:mina run forceload add 36 -249
mm mobs kill astral_mina_control_sala4
execute in minecraft:mina run forceload remove 36 -249
execute in minecraft:mina run forceload add 10 -125
mm mobs kill astral_mina_control_sala1
execute in minecraft:mina run function astral:tanda2/mina/sala1/cleanup
execute in minecraft:mina run forceload remove 10 -125
execute in minecraft:mina run forceload add 19 -159
mm mobs kill astral_mina_control_sala2
execute in minecraft:mina run function astral:tanda2/mina/sala2/cleanup
execute in minecraft:mina run forceload remove 19 -159
execute in minecraft:mina run forceload add 43 -202
mm mobs kill astral_mina_control_sala3
execute in minecraft:mina run function astral:tanda2/mina/sala3/cleanup
execute in minecraft:mina run forceload remove 43 -202
execute in minecraft:mina run forceload add 36 -249
mm mobs kill astral_mina_control_sala4
execute in minecraft:mina run function astral:tanda2/mina/sala4/cleanup
execute in minecraft:mina run forceload remove 36 -249
# Limpiar restos de la version anterior (solo IDs de ESTA mazmorra).
mm mobs kill astral_mina_minero
mm mobs kill astral_mina_esqueleto
mm mobs kill astral_mina_ahogado
mm mobs kill astral_mina_arana
mm mobs kill astral_mina_capataz
mm mobs kill astral_mina_golem
mm mobs kill astral_mina_guardian
# Crear exactamente un controlador en cada punto nuevo.
execute in minecraft:mina run forceload add 10 -125
mm mobs spawn astral_mina_control_sala1 1 mina,10.5,-45,-124.5
execute in minecraft:mina run forceload remove 10 -125
execute in minecraft:mina run forceload add 19 -159
mm mobs spawn astral_mina_control_sala2 1 mina,19.5,-39,-158.5
execute in minecraft:mina run forceload remove 19 -159
execute in minecraft:mina run forceload add 43 -202
mm mobs spawn astral_mina_control_sala3 1 mina,43.5,-24,-201.5
execute in minecraft:mina run forceload remove 43 -202
execute in minecraft:mina run forceload add 36 -249
mm mobs spawn astral_mina_control_sala4 1 mina,36.5,24,-248.5
execute in minecraft:mina run forceload remove 36 -249
# Conservar NPC, protecciones y permisos existentes. No ejecutar mv create ni pegar mapas.
rg flag -w mina __global__ enderdragon-block-damage deny
```

### bosque

```text
# Actualizacion Tanda 2. Mazmorra VACIA. No crear/importar/reemplazar mundos.
# Respaldar archivos del servidor; apagar para instalar el datapack y YAML, luego iniciar.
# El arranque carga MythicMobs; si se ajusto despues: mm reload.
# Cargar y retirar cada controlador anterior.
execute in minecraft:bosque run forceload add 1440 1568
mm mobs kill astral_bosque_control_sala1
execute in minecraft:bosque run forceload remove 1440 1568
execute in minecraft:bosque run forceload add 1504 1504
mm mobs kill astral_bosque_control_sala2
execute in minecraft:bosque run forceload remove 1504 1504
execute in minecraft:bosque run forceload add 1600 1440
mm mobs kill astral_bosque_control_sala3
execute in minecraft:bosque run forceload remove 1600 1440
execute in minecraft:bosque run forceload add 1468 1570
mm mobs kill astral_bosque_control_sala1
execute in minecraft:bosque run function astral:tanda2/bosque/sala1/cleanup
execute in minecraft:bosque run forceload remove 1468 1570
execute in minecraft:bosque run forceload add 1604 1382
mm mobs kill astral_bosque_control_sala2
execute in minecraft:bosque run function astral:tanda2/bosque/sala2/cleanup
execute in minecraft:bosque run forceload remove 1604 1382
# Limpiar restos de la version anterior (solo IDs de ESTA mazmorra).
mm mobs kill astral_bosque_espantapajaros
mm mobs kill astral_bosque_abejorro
mm mobs kill astral_bosque_cara
mm mobs kill astral_bosque_chaman
# Crear exactamente un controlador en cada punto nuevo.
execute in minecraft:bosque run forceload add 1468 1570
mm mobs spawn astral_bosque_control_sala1 1 bosque,1468.5,101,1570.5
execute in minecraft:bosque run forceload remove 1468 1570
execute in minecraft:bosque run forceload add 1604 1382
mm mobs spawn astral_bosque_control_sala2 1 bosque,1604.5,101,1382.5
execute in minecraft:bosque run forceload remove 1604 1382
# Conservar NPC, protecciones y permisos existentes. No ejecutar mv create ni pegar mapas.
rg flag -w bosque __global__ enderdragon-block-damage deny
```

### tumba

```text
# Actualizacion Tanda 2. Mazmorra VACIA. No crear/importar/reemplazar mundos.
# Respaldar archivos del servidor; apagar para instalar el datapack y YAML, luego iniciar.
# El arranque carga MythicMobs; si se ajusto despues: mm reload.
# Cargar y retirar cada controlador anterior.
execute in minecraft:tumba run forceload add -149 -99
mm mobs kill astral_tumba_control_sala1
execute in minecraft:tumba run forceload remove -149 -99
execute in minecraft:tumba run forceload add -176 203
mm mobs kill astral_tumba_control_sala2
execute in minecraft:tumba run forceload remove -176 203
execute in minecraft:tumba run forceload add 0 0
mm mobs kill astral_tumba_control_sala3
execute in minecraft:tumba run forceload remove 0 0
execute in minecraft:tumba run forceload add -149 -99
mm mobs kill astral_tumba_control_sala1
execute in minecraft:tumba run function astral:tanda2/tumba/sala1/cleanup
execute in minecraft:tumba run forceload remove -149 -99
execute in minecraft:tumba run forceload add -176 203
mm mobs kill astral_tumba_control_sala2
execute in minecraft:tumba run function astral:tanda2/tumba/sala2/cleanup
execute in minecraft:tumba run forceload remove -176 203
execute in minecraft:tumba run forceload add 0 0
mm mobs kill astral_tumba_control_sala3
execute in minecraft:tumba run function astral:tanda2/tumba/sala3/cleanup
execute in minecraft:tumba run forceload remove 0 0
# Limpiar restos de la version anterior (solo IDs de ESTA mazmorra).
mm mobs kill astral_tumba_espantapajaros
mm mobs kill astral_tumba_arana
mm mobs kill astral_tumba_cara
mm mobs kill astral_tumba_momia
mm mobs kill astral_tumba_s1_arana
mm mobs kill astral_tumba_s1_momia
mm mobs kill astral_tumba_s1_esqueleto
mm mobs kill astral_tumba_s1_cara
mm mobs kill astral_tumba_s1_espantapajaros
mm mobs kill astral_tumba_s1_golem
mm mobs kill astral_tumba_s2_arana
mm mobs kill astral_tumba_s2_momia
mm mobs kill astral_tumba_s2_esqueleto
mm mobs kill astral_tumba_s2_cara
mm mobs kill astral_tumba_s2_espantapajaros
mm mobs kill astral_tumba_s2_golem
# Crear exactamente un controlador en cada punto nuevo.
execute in minecraft:tumba run forceload add -149 -99
mm mobs spawn astral_tumba_control_sala1 1 tumba,-148.5,60,-98.5
execute in minecraft:tumba run forceload remove -149 -99
execute in minecraft:tumba run forceload add -176 203
mm mobs spawn astral_tumba_control_sala2 1 tumba,-175.5,88,203.5
execute in minecraft:tumba run forceload remove -176 203
execute in minecraft:tumba run forceload add 0 0
mm mobs spawn astral_tumba_control_sala3 1 tumba,0.568,72,0.512
execute in minecraft:tumba run forceload remove 0 0
# Conservar NPC, protecciones y permisos existentes. No ejecutar mv create ni pegar mapas.
rg flag -w tumba __global__ enderdragon-block-damage deny
```

### cumbre

```text
# Actualizacion Tanda 2. Mazmorra VACIA. No crear/importar/reemplazar mundos.
# Respaldar archivos del servidor; apagar para instalar el datapack y YAML, luego iniciar.
# El arranque carga MythicMobs; si se ajusto despues: mm reload.
# Cargar y retirar cada controlador anterior.
execute in minecraft:cumbre_hielo run forceload add 16 18
mm mobs kill astral_cumbre_control_sala1
execute in minecraft:cumbre_hielo run forceload remove 16 18
execute in minecraft:cumbre_hielo run forceload add 24 -2
mm mobs kill astral_cumbre_control_sala2
execute in minecraft:cumbre_hielo run forceload remove 24 -2
execute in minecraft:cumbre_hielo run forceload add 6 32
mm mobs kill astral_cumbre_control_sala3
execute in minecraft:cumbre_hielo run forceload remove 6 32
execute in minecraft:cumbre_hielo run forceload add -26 -24
mm mobs kill astral_cumbre_control_sala1
execute in minecraft:cumbre_hielo run function astral:tanda2/cumbre/sala1/cleanup
execute in minecraft:cumbre_hielo run forceload remove -26 -24
execute in minecraft:cumbre_hielo run forceload add -102 56
mm mobs kill astral_cumbre_control_sala2
execute in minecraft:cumbre_hielo run function astral:tanda2/cumbre/sala2/cleanup
execute in minecraft:cumbre_hielo run forceload remove -102 56
# Limpiar restos de la version anterior (solo IDs de ESTA mazmorra).
mm mobs kill astral_cumbre_arana
mm mobs kill astral_cumbre_cara
mm mobs kill astral_cumbre_espantapajaros
mm mobs kill astral_cumbre_yeti
# Crear exactamente un controlador en cada punto nuevo.
execute in minecraft:cumbre_hielo run forceload add -26 -24
mm mobs spawn astral_cumbre_control_sala1 1 cumbre_hielo,-25.6,33,-23.4
execute in minecraft:cumbre_hielo run forceload remove -26 -24
execute in minecraft:cumbre_hielo run forceload add -102 56
mm mobs spawn astral_cumbre_control_sala2 1 cumbre_hielo,-101.8,30,56.9
execute in minecraft:cumbre_hielo run forceload remove -102 56
# Conservar NPC, protecciones y permisos existentes. No ejecutar mv create ni pegar mapas.
rg flag -w cumbre_hielo __global__ enderdragon-block-damage deny
```

### forja

```text
# Actualizacion Tanda 2. Mazmorra VACIA. No crear/importar/reemplazar mundos.
# Respaldar archivos del servidor; apagar para instalar el datapack y YAML, luego iniciar.
# El arranque carga MythicMobs; si se ajusto despues: mm reload.
# Cargar y retirar cada controlador anterior.
execute in minecraft:forja_volcano run forceload add 82 -56
mm mobs kill astral_forja_control_sala1
execute in minecraft:forja_volcano run forceload remove 82 -56
execute in minecraft:forja_volcano run forceload add 23 -160
mm mobs kill astral_forja_control_sala1
execute in minecraft:forja_volcano run function astral:tanda2/forja/sala1/cleanup
execute in minecraft:forja_volcano run forceload remove 23 -160
execute in minecraft:forja_volcano run forceload add -126 -126
mm mobs kill astral_forja_control_sala2
execute in minecraft:forja_volcano run function astral:tanda2/forja/sala2/cleanup
execute in minecraft:forja_volcano run forceload remove -126 -126
execute in minecraft:forja_volcano run forceload add -8 -22
mm mobs kill astral_forja_control_sala3
execute in minecraft:forja_volcano run function astral:tanda2/forja/sala3/cleanup
execute in minecraft:forja_volcano run forceload remove -8 -22
# Limpiar restos de la version anterior (solo IDs de ESTA mazmorra).
mm mobs kill astral_forja_espantapajaros
mm mobs kill astral_forja_arana
mm mobs kill astral_forja_cara
mm mobs kill astral_forja_golem_forja
# Crear exactamente un controlador en cada punto nuevo.
execute in minecraft:forja_volcano run forceload add 23 -160
mm mobs spawn astral_forja_control_sala1 1 forja_volcano,23.2,13,-159.4
execute in minecraft:forja_volcano run forceload remove 23 -160
execute in minecraft:forja_volcano run forceload add -126 -126
mm mobs spawn astral_forja_control_sala2 1 forja_volcano,-125.5,13,-125.7
execute in minecraft:forja_volcano run forceload remove -126 -126
execute in minecraft:forja_volcano run forceload add -8 -22
mm mobs spawn astral_forja_control_sala3 1 forja_volcano,-7.9,47,-21.1
execute in minecraft:forja_volcano run forceload remove -8 -22
# Conservar NPC, protecciones y permisos existentes. No ejecutar mv create ni pegar mapas.
rg flag -w forja_volcano __global__ enderdragon-block-damage deny
```
