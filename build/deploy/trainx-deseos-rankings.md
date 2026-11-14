# Entrega: Trainx, Renacimiento, Deseos y Rankings (14/11/2026)

Pack FINAL privado: `<ASTRAL_PRIVADO>/build/entregas/trainx-deseos/AstralRPG-Textures.zip`
(base d00332e4 + ventanas nuevas + modelo de Trainx). sha1 en `pack.sha1` de esa carpeta.

## Archivos
| Local | Servidor |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `<privado>/build/models/astral_trainx.bbmodel` | `plugins/BetterModel/models/` |
| `build/mythicmobs/mobs/santuario.yml` | `plugins/MythicMobs/mobs/` |
| `build/mythicmobs/skills/santuario.yml`, `trainx.yml` | `plugins/MythicMobs/skills/` |
| `build/renacimiento/astral_renacimiento.sk`, `build/rankings/astral_rankings.sk` | `plugins/Skript/scripts/` |
| `build/minas/Skript/scripts/astral_minas.sk`, `build/bosque/astral_bosque.sk` | `plugins/Skript/scripts/` |
| `build/menus/DeluxeMenus/gui_menus/{fragmentos,renacer,deseo,deseo_lite}.yml` | `plugins/DeluxeMenus/gui_menus/` |
| `build/menus/DeluxeMenus/config-gui_menus.yml` | sumar sus entradas nuevas (renacer, deseo, deseo_lite) al `config.yml` de DeluxeMenus |

## Pasos
1. Subir el pack FINAL con `python tools/subir_pack_r2.py <zip final>`, verificar la descarga y poner el sha1 en
   `resource-pack-sha1` de `server.properties` (comprobar que el archivo no quede vacio).
2. Subir los archivos de la tabla.
3. Consola: `build/renacimiento/comandos.txt`.
4. Reiniciar (datapack nuevo y pack). Despues, consola: `build/rankings/comandos.txt` (carteles).
5. En el juego (OP): `/ranking meta parkour_spiral`, `parkour_spiral2`, `parkour_paradise3` parado en cada meta.
