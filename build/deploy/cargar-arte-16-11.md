# Arte final y Manzana de la Suerte - 16/11/2026

Implementado y preparado; despliegue remoto y R2 pendientes. Continuar despues de mascotas-aurora-botones y antes de mochilas-3d.

## Archivos exactos

| Local | Destino |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos.yml` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos_suerte.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos_suerte.yml` |
| `build/menus/DeluxeMenus/gui_menus/consumibles.yml` | `plugins/DeluxeMenus/gui_menus/consumibles.yml` |
| `build/menus/DeluxeMenus/gui_menus/goblin_mercader.yml` | `plugins/DeluxeMenus/gui_menus/goblin_mercader.yml` |

FINAL privado: `.local/terceros/AstralRPG-privado/build/entregas/cargar-arte-16-11/AstralRPG-Textures.zip`.
SHA-1 FINAL: `90c90b745bce97490550d8d22a8a1cc4011be8e1`. SHA-1 publico: `9cba70db656e8e0a0f7c6672eba19a1bdb12d0ff`.
Base: `.local/terceros/AstralRPG-privado/build/entregas/mascotas-aurora-botones/AstralRPG-Textures.zip`; SHA-1 `f9f48c8ab3c71ca002adc4e1ca830ade3734f968`; 17275 entradas intactas fuera del delta.
El FINAL conserva Crop & Kettle, modelos, retratos y fuentes privados. El dueno autorizo incluir Crop & Kettle en el FINAL de R2 (16/11); no hay bloqueo de permiso pendiente para esta entrega.
El ZIP publico carece del arte privado: no instalarlo en lugar del FINAL.

## Instalacion por Claude

Verificar primero la version instalada y las entregas anteriores. La documentacion identifica Empower como principal y Aternos como copia. No se uso navegador ni se verifico consola remota.
Apagar, respaldar solo los archivos a reemplazar, instalar la tabla anterior y reiniciar completamente con Java 25. No sustituir mundos ni regiones ni usar Worlds > Upload en world. BetterHud sigue apagado: el layout regenerado se conserva en GitHub, no necesita instalarse para esta tarea.
Publicar el FINAL: `python tools/subir_pack_r2.py ".local/terceros/AstralRPG-privado/build/entregas/cargar-arte-16-11/AstralRPG-Textures.zip"`. Verificar la descarga publica y actualizar `resource-pack-sha1` en `server.properties` al SHA-1 FINAL antes del arranque, conservando la URL fija.
El reinicio carga datapack y configuraciones. Para posteriores recargas de solo configuracion: `dm reload`, `crates reload`, `mm reload`. No usar /reload de Bukkit.
Revisar consola y entrar con el nuevo pack: probar Saltador y Gancho por separado, barril en GUI/mano, botella vanilla, materiales VI-X, navegacion de mascotas/cosmeticos y compra/consumo de Manzana de la Suerte. ITEM_VERSION 25 actualiza items existentes conservando sus IDs.

## Arte y verificaciones

Arte propio final, sin redibujar ni recolorear. Items y botella copiados byte por byte; botones recortados al cuadro central sin magenta y escalados. Navegacion 18x18. Barril privado conserva el modelo 3D fuera de GUI. Tiers altos de Infinita y sus numeros romanos intactos.
Vista CPU publica: `build/Servicios-preview/arte-16-11.png`. No sustituye una prueba con cliente.
Siguen provisorios `boton_sin_datos` y `mascotas_rest_0` a `mascotas_rest_4`. `cosmeticos_nav_next` no se usa en los menus actuales y conserva su reserva.
Reproduccion desde datapack-src: `python arte_1611.py --import-art` solo para importar originales; `python build.py`, `python lobby.py`, `python menus.py`, `python mobs/mythic.py`, `python betterhud.py`, `python build_pack.py pack-source`, `python deploy_arte_1611.py`. Compilar usa las fuentes PNG versionadas.
Verificado: suite completa de 327 pruebas OK; 4 contratos de arte OK, referencias de ambos packs, conservacion del FINAL, 76 etiquetas de mundos BetterHud, vista CPU y auditoria publica sin arte privado. Sin prueba con cliente ni consola remota.
Pruebas reproducibles: `python -m unittest discover -s datapack-src -p "test*.py"`; `python tools/verificar_terceros.py` antes del commit.
