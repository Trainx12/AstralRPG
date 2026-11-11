# Arreglos: integrados en entrega unica

Despliegue pendiente. Seguir urgente-mascotas-texturas.md, que contiene el pack FINAL vigente y todos los destinos.
Esta revision reemplaza la propuesta de apoyos: NO agregar bloques. No usar arreglos-apoyos.txt ni el pack aislado anterior.
Principal: los 14 accesos anteriores mas Fragmentos y Duelos. Trade sigue explicado en Comandos; Peluches dentro de la Tienda.

| Mazmorra | Sala | Piso minimo | Piso maximo | Puntos |
|---|---|---:|---:|---:|
| mina | sala1 | -45 | -45 | 24 |
| mina | sala2 | -39 | -36 | 1 |
| mina | sala3 | -24 | -24 | 24 |
| mina | sala4 | 24 | 24 | 24 |
| bosque | sala1 | 97 | 102 | 24 |
| bosque | sala2 | 100 | 101 | 24 |
| tumba | sala1 | 58 | 60 | 10 |
| tumba | sala2 | 88 | 88 | 12 |
| tumba | sala3 | 72 | 72 | 12 |
| cumbre | sala1 | 30 | 30 | 21 |
| cumbre | sala2 | 30 | 30 | 22 |
| forja | sala1 | 13 | 13 | 24 |
| forja | sala2 | 13 | 13 | 24 |
| forja | sala3 | 47 | 47 | 24 |

Vistas CPU propias: build/previews/menu-astral-arreglos.png y menu-comandos.png.
Vistas de mapas solo en el build privado: previews/arreglos-apoyos.png y arreglos-cofres.png. Sin puntos dorados de apoyo.

## Controladores: salas vacias, despues de instalar y reiniciar

```text
execute in minecraft:mina run forceload add 10 -125
mm mobs kill astral_mina_control_sala1
execute in minecraft:mina run function astral:tanda2/mina/sala1/reset
mm mobs spawn astral_mina_control_sala1 1 mina,10.5,-45,-124.5
execute in minecraft:mina run forceload add 19 -159
mm mobs kill astral_mina_control_sala2
execute in minecraft:mina run function astral:tanda2/mina/sala2/reset
mm mobs spawn astral_mina_control_sala2 1 mina,19.5,-39,-158.5
execute in minecraft:mina run forceload add 43 -202
mm mobs kill astral_mina_control_sala3
execute in minecraft:mina run function astral:tanda2/mina/sala3/reset
mm mobs spawn astral_mina_control_sala3 1 mina,43.5,-24,-201.5
execute in minecraft:mina run forceload add 36 -249
mm mobs kill astral_mina_control_sala4
execute in minecraft:mina run function astral:tanda2/mina/sala4/reset
mm mobs spawn astral_mina_control_sala4 1 mina,36.5,24,-248.5
execute in minecraft:bosque run forceload add 1468 1570
mm mobs kill astral_bosque_control_sala1
execute in minecraft:bosque run function astral:tanda2/bosque/sala1/reset
mm mobs spawn astral_bosque_control_sala1 1 bosque,1468.5,101,1570.5
execute in minecraft:bosque run forceload add 1604 1382
mm mobs kill astral_bosque_control_sala2
execute in minecraft:bosque run function astral:tanda2/bosque/sala2/reset
mm mobs spawn astral_bosque_control_sala2 1 bosque,1604.5,101,1382.5
execute in minecraft:tumba run forceload add -149 -99
mm mobs kill astral_tumba_control_sala1
execute in minecraft:tumba run function astral:tanda2/tumba/sala1/reset
mm mobs spawn astral_tumba_control_sala1 1 tumba,-148.5,60,-98.5
execute in minecraft:tumba run forceload add -176 203
mm mobs kill astral_tumba_control_sala2
execute in minecraft:tumba run function astral:tanda2/tumba/sala2/reset
mm mobs spawn astral_tumba_control_sala2 1 tumba,-175.5,88,203.5
execute in minecraft:tumba run forceload add 0 0
mm mobs kill astral_tumba_control_sala3
execute in minecraft:tumba run function astral:tanda2/tumba/sala3/reset
mm mobs spawn astral_tumba_control_sala3 1 tumba,0.568,72,0.512
execute in minecraft:cumbre_hielo run forceload add -26 -24
mm mobs kill astral_cumbre_control_sala1
execute in minecraft:cumbre_hielo run function astral:tanda2/cumbre/sala1/reset
mm mobs spawn astral_cumbre_control_sala1 1 cumbre_hielo,-25.6,33,-23.4
execute in minecraft:cumbre_hielo run forceload add -102 56
mm mobs kill astral_cumbre_control_sala2
execute in minecraft:cumbre_hielo run function astral:tanda2/cumbre/sala2/reset
mm mobs spawn astral_cumbre_control_sala2 1 cumbre_hielo,-101.8,30,56.9
execute in minecraft:forja_volcano run forceload add 23 -160
mm mobs kill astral_forja_control_sala1
execute in minecraft:forja_volcano run function astral:tanda2/forja/sala1/reset
mm mobs spawn astral_forja_control_sala1 1 forja_volcano,23.2,13,-159.4
execute in minecraft:forja_volcano run forceload add -126 -126
mm mobs kill astral_forja_control_sala2
execute in minecraft:forja_volcano run function astral:tanda2/forja/sala2/reset
mm mobs spawn astral_forja_control_sala2 1 forja_volcano,-125.5,13,-125.7
execute in minecraft:forja_volcano run forceload add -8 -22
mm mobs kill astral_forja_control_sala3
execute in minecraft:forja_volcano run function astral:tanda2/forja/sala3/reset
mm mobs spawn astral_forja_control_sala3 1 forja_volcano,-7.9,47,-21.1
```

Los packs de parkour adaptados del arreglo anterior se conservan: si falta instalarlos, reemplazar solamente sus datapacks, nunca mundos.
Fuentes privadas: .local/mapas/subir/parkour_paradise3-datapack.zip y parkour_spiral2-datapack.zip.
Destinos: world/datapacks/parkour_paradise3-datapack/ y world/datapacks/parkour_spiral2-datapack/ (contenido descomprimido, sin copia ZIP duplicada).
