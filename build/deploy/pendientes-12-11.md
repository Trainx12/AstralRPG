# Pendientes 12/11/2026: tren, Cronista, mochilas y Santuario

Un solo reinicio. Antes: `list` sin jugadores, respaldo en `.local/backups/`, aviso `say` 30 s, `stop`.

## Tren del lobby (ya desplegado sin reiniciar, commit f3970eb)

El pack original del tren tiene los nombres cruzados: `basic_coaster_cart` es la locomotora (alta, con chimenea)
y `basic_coaster_head` el vagon con asiento. Ahora: locomotora adelante (norte) + 3 vagones.
Se subieron `build/tren/AstralTrain/train.yml` -> `plugins/AstralTrain/train.yml` y
`build/tren/Train_Carts/savedTrainModules/astral_lobby.yml` -> `plugins/Train_Carts/savedTrainModules/`,
y se corrio `astraltren recrear`. El pack de texturas no cambio.

## Archivos (servidor apagado)

| Local | Destino |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/menus/DeluxeMenus/gui_menus/misiones.yml` | `plugins/DeluxeMenus/gui_menus/misiones.yml` |
| `build/menus/DeluxeMenus/gui_menus/comandos.yml` | `plugins/DeluxeMenus/gui_menus/comandos.yml` |
| `build/runtime/AstralProgression.jar` | `plugins/AstralProgression.jar` |
| `build/tanda5a/AstralProgression/config.yml` | `plugins/AstralProgression/config.yml` |
| `build/tanda5a/EconomyShopGUI/sections/Mochilas.yml` | `plugins/EconomyShopGUI/sections/Mochilas.yml` |
| `build/tanda5a/EconomyShopGUI/shops/Mochilas.yml` | `plugins/EconomyShopGUI/shops/Mochilas.yml` |
| `build/gameplay/astral_gameplay.sk` | `plugins/Skript/scripts/astral_gameplay.sk` |
| `build/mapas_exploracion/astral_viajes.sk` | `plugins/Skript/scripts/astral_viajes.sk` |
| `build/mythicmobs/mobs/santuario.yml` | `plugins/MythicMobs/mobs/santuario.yml` |
| `build/mythicmobs/skills/santuario.yml` | `plugins/MythicMobs/skills/santuario.yml` |
| `.local/santuario-spirit/entrega/region/r.0.0.mca` (privado) | `world/dimensions/minecraft/santuario_azeroth/region/r.0.0.mca` |

Santuario: borrar ANTES en `world/dimensions/minecraft/santuario_azeroth/` todos los `.mca` de `region/`,
`entities/` y `poi/` (mapa viejo bugeado y su controlador). Se sube solo `r.0.0.mca`.

## Despues de arrancar (consola)

Comandos de `build/mazmorras/santuario/comandos.txt` desde `mm mobs kill astral_santuario_control_sala1`
hasta el `mm mobs spawn` (controlador nuevo, forceload nuevo). No hace falta `rg flag` ni gamerules otra vez.

## Que cambia para el jugador

- **Cronista**: al tocar ACEPTAR MISION en la historia se cierra el menu y el Cronista cuenta el capitulo en
  una ventana (dialogo vanilla, estilo pergamino de la Guia) con boton "Entendido". Textos en
  `datapack-src/misiones.py` (`STORY_TEXT`). LuxDialogues no sirve: es pago y llega hasta 1.21.11.
- **Mochilas**: unico plugin ExpendableBackpacks. `/shop` -> Mochilas (slot 42): Cuero 9 ($5.000), Cobre 18
  ($20.000), Hierro 27 ($50.000), Oro 36 ($100.000), Diamante 45 ($175.000). La mochila es un item, clic derecho
  la abre; pide un lugar libre antes de cobrar. Guia -> "Terrenos y mochilas" explica recetas y muerte.
- **Santuario**: mapa nuevo `spiritarena.schem` en la misma dimension (cielo del End). Entrada, jefes, cofre y
  guia PROVISORIOS arriba del centro (256.5 180 254.5) hasta que el dueno pase coordenadas: se cambian en el
  bloque "COORDENADAS DEL SANTUARIO" de `datapack-src/santuario_azeroth.py`.

## Pruebas locales

- `python -m unittest discover -s datapack-src -p "test_*.py"`: 239 OK (con numpy instalado).
- `tools/probar_tren_paper.py`: TRAIN RESULT failures=0 (locomotora al norte, vagones bajos).
- `tools/probar_tanda5a_paper.py`: T5A failures=0 en las dos fases (mochila por `backpack give`, abre 9,
  guarda y reabre sin duplicar, conserva 7 esmeraldas tras reiniciar).
- Datapack en Paper limpio: carga y corre `quest/gui/story_dialog` sin errores.
- `tools/pegar_santuario_spirit.py`: PASTE OK (191,61,187)-(321,191,321); piso y aire comprobados en los puntos.

Sin cliente real: no se vio el dialogo en pantalla, ni la compra con dinero de verdad (Vault), ni el Santuario
recorrido. Duelos queda pendiente: falta el `.jar` de Duels Optimised (BuiltByBit, lo baja el dueno).
