# Entrega 15/11/2026: efectos, nether hub, tren, PvP, reparar, durabilidad y arreglos

Pedido del dueno del 14-15/11. Pack FINAL nuevo: `ASTRAL_PRIVADO/build/entregas/efectos-15-11/AstralRPG-Textures.zip`
(armado sobre el FINAL desplegado `armas-mod` 3a710f8b: dibujos de efectos + particula de golpe visible otra vez).

## Archivos a subir

| Origen | Destino en el server |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` (ITEM_VERSION 21) |
| `build/runtime/AstralEfectos.jar` (nuevo) | `plugins/AstralEfectos.jar` |
| `build/runtime/AstralPortales.jar` (nuevo) | `plugins/AstralPortales.jar` |
| `build/runtime/AstralDecor.jar` (1.10.0) | `plugins/AstralDecor.jar` |
| `build/gameplay/astral_gameplay.sk` | `plugins/Skript/scripts/` |
| `build/services/astral_servicios.sk` | `plugins/Skript/scripts/` |
| `build/mazmorras/astral_mazmorras_copias.sk` | `plugins/Skript/scripts/` |
| `build/infinita/astral_infinita.sk` | `plugins/Skript/scripts/` |
| `build/rankings/astral_rankings.sk` | `plugins/Skript/scripts/` |
| `build/mapas_exploracion/astral_portales.sk` | `plugins/Skript/scripts/` |
| PRIVADO `build/mythicmobs/skills/astral.yml`, `skills/mascotas.yml`, `mobs/astral.yml` | `plugins/MythicMobs/skills|mobs/` |
| `build/mythicmobs/skills/mazmorra.yml`, `skills/trainx.yml` | `plugins/MythicMobs/skills/` |
| `build/menus/DeluxeMenus/gui_menus/principal.yml`, `configuraciones.yml` | `plugins/DeluxeMenus/gui_menus/` |
| `configuraciones: {file: configuraciones.yml}` | agregar en `plugins/DeluxeMenus/config.yml` (gui_menus) |
| `build/tren/AstralTrain/config.yml` (`viaje`) | `plugins/AstralTrain/config.yml`: solo la seccion `viaje` |
| ExcellentEnchants | YA HECHO en el server (15/11): `Enchanting_Table: true` y peso de 47 encantamientos bajado (10->2, 5/2->1) para que la mesa muestre vanilla y del plugin. Respaldo: `.local/ee/antes/`. Se aplica al reiniciar. |
| SleepMost | YA HECHO (15/11): `nightcycle-animation: true` en `world`, `sleepmost reload`. |
| Pack FINAL | R2 con `tools/subir_pack_r2.py` + `resource-pack-sha1` en `server.properties` |

## Reinicio y comandos (consola, sin `/`)

Reiniciar (datapack, plugins nuevos, pesos de ExcellentEnchants). Despues:

```text
astraltren fijar 96 99 192 SOUTH
astraltren recrear
execute in minecraft:lobby run minecraft:kill @e[type=text_display,tag=astral_rank_infinita,x=180.5,y=101.5,z=182.5,distance=..3]
execute in minecraft:lobby run minecraft:kill @e[type=text_display,tag=astral_rank_trainx,x=186.5,y=101.5,z=182.5,distance=..3]
execute in minecraft:portales_astrales run minecraft:kill @e[type=!player,x=-2189.1,y=81,z=179.3,distance=..2]
mm mobs spawn astral_npc_portales 1 portales_astrales,-2137.59,81,161.5
```

## Que cambia

- **Efectos** (`efectos.py`, plugin AstralEfectos): `/efectos` y boton Configuraciones en `/menu` (Bajo/Medio/Alto;
  arrancan en Medio). Bajo = como antes. Particulas de golpe: 3/6/12 por golpe (antes millones con dano T10 -> crash).
  Bastones: rayo del color y elemento del tier; Alto con explosion al impactar. Jefes: golpe al piso y disparos con
  elemento (hielo, fuego, veneno, agua, arena, naturaleza, piedra; Trainx vacio y luz). Alto: rastros de armas,
  auras de armaduras con set completo y mascotas nivel 30.
- **Nether Hub** (AstralPortales): portal de portales_astrales -> Hub (-285, 124, 23.5); portal del Hub -> llegada
  nueva de portales_astrales (-2137.59, 81, 159.48). Fuera del Hub, portales normales al survival. Hub y zona del
  portal sin romper/poner/mobs. Si la llegada no queda bien: parado en el lugar, `/astralportal hub` o `/astralportal astral`.
- **Mobs del nether**: piglins zombificados, piglins y slimes con tier, nombre y vida.
- **Tren**: vias nuevas x=96, z=176..207 (muros en 175 y 208).
- **Arenas PvP**: cada golpe saca % de la vida del rival segun arma, tier del arma y tier de su armadura (tope 25%).
- **Herrero**: boton Reparar (yunque, casilla 47): plata + 1 material por tier (150$ T1 ... 16.000$ T10).
- **Durabilidad**: equipo Astral gasta 1 punto por golpe (antes dano/4); T1-T2 con mas durabilidad.
- **Mazmorras**: se borra lo tirado (items, flechas, xp) al vaciarse una copia, al entrar el grupo y en la Infinita.
- **Rankings**: sin carteles de Infinita/Trainx en el lobby; `/ranking cartel` solo borra el de su mundo.
- **Sombrero**: sin casco ya no se pone un objeto en la cabeza (se ve solo para los demas).
- **Mesa de encantar**: vanilla y del plugin (antes casi siempre salian los del plugin por su peso).
- **Dormir**: la noche pasa con la animacion del cielo (SleepMost).

## Pendiente de probar en juego

Efectos en Medio/Alto, llegada exacta del Hub, tren con las vias nuevas, PvP en arena, Reparar.
