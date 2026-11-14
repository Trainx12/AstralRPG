# Entrega: Ropa de Minero y Talador (14/11/2026)

Pack FINAL privado: `<ASTRAL_PRIVADO>/build/entregas/oficios/AstralRPG-Textures.zip`
(pack en vivo d5a5c0a4 + 34 archivos de `oficios.own_textures()`). sha1 en `pack.sha1` de esa carpeta.

## Archivos
| Local | Servidor |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` |
| `build/minas/Skript/scripts/astral_minas.sk`, `build/bosque/astral_bosque.sk` | `plugins/Skript/scripts/` |
| `build/menus/DeluxeMenus/gui_menus/oficios.yml` | `plugins/DeluxeMenus/gui_menus/` |
| `build/shop/EconomyShopGUI/sections/Oficios.yml` | `plugins/EconomyShopGUI/sections/` |
| `build/shop/EconomyShopGUI/shops/Oficios.yml` | `plugins/EconomyShopGUI/shops/` |

`plugins/DeluxeMenus/config.yml`: sumar en `gui_menus:` la entrada `oficios: {file: oficios.yml}`.

## Pasos
1. Subir el pack FINAL con `python tools/subir_pack_r2.py <zip final>`, verificar la descarga y poner el sha1 en
   `resource-pack-sha1` de `server.properties` (comprobar que el archivo no quede vacio).
2. Subir los archivos de la tabla y editar el config de DeluxeMenus.
3. Reiniciar (datapack, pack y AstralDecor).
4. Probar: `/shop` -> Oficios abre el menu; `/function astral:admin/kit_oficios` da las 8 piezas; la guia muestra "Minero y Talador".
