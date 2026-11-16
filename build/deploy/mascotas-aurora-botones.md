# Mascotas, Aurora y botones - 16/11/2026

Implementado y preparado; sin despliegue remoto. GitHub publica codigo y salidas propias, no instala el servidor.

## Resultado

- Retiradas lobo, zorro espectral, golem de piedra, cuervo y dragon. Se mantienen Fenix y las 17 cubee: tres paginas de seis, sin huecos. IDs 6-23, permisos, XP y niveles conservados. Los .bbmodel originales quedan archivados.
- Se eliminaron sus invocaciones, drops de mobs/cofres, detalles, paginas obsoletas, guia y premios normales/con suerte/con garantia. Rarezas totales y garantia cada 40 tiradas conservadas.
- Al entrar, cada permiso retirado da una llave virtual normal de Monturas y un mensaje. Marcador persistente por UUID y mascota en Skript; no borrar variables ni repetir pagos manualmente. Se limpia la seleccion 1-5 y se eliminan solo entidades con tags de mascotas retiradas en el mundo del jugador. Las llaves se usan con `/crates mass-open gacha_monturas virtual 1` (permiso existente `crazycrates.massopen`); no son una compra y no usan Suerte.
- AstralOceano 1.4.0 elimina la tarea Java que invocaba Aurora y su definicion MythicMobs. Era decorativa: no tenia dialogo ni tienda que migrar; el aviso conserva las advertencias del Oceano.
- Seis marcos Gemini finales: configuraciones (3 filas), renacer (6), deseo (6), deseo_lite (6), oficios (4), oceano_aviso (3). Botones de hojas 36 conservan item_model; nivel activo con borde dorado, deseos espaciados, texto oscuro sobre pergamino, precio real de sets en nombre/lore, ayuda de Oficios sin choque, Entrar preparado y Volver.
- Navegacion de mascotas y cosmeticos: PNG 18x18 con trama y marca P, provisoria. Se revisaron tambien Minas, venta, portales, viajes, Infinita, servicios y Duelos; Herrero/Venta y Duelos reciben modelos para volver/cerrar. Las cabezas de jugadores y objetos depositados son su icono real. Botones anchos dibujados en el fondo mantienen sus zonas de clic.

## Arte y vistas

Vistas CPU por ventana: `build/Servicios-preview/ventanas-16-11/`. La galeria publica muestra reservas propias donde hay arte licenciado; no es una captura de Minecraft ni una prueba de interaccion humana.
Tabla completa ventana -> boton -> slot -> PNG/modelo -> estado: [botones.md](../Servicios-preview/ventanas-16-11/botones.md). Los modelos compuestos y los botones dibujados en un fondo se identifican por su recurso del pack; las reservas reemplazables tienen ruta fuente explicita.
Arte final propio: `datapack-src/pack-source/ref/ventanas-1611/*.png` y los `boton_*.png` de hojas 36 en `pack-source/provisorias/` (nombre historico de carpeta). No se rehizo arte final. Reservas pendientes del dueno: `pack-source/provisorias/navegacion/{cosmeticos,mascotas}_nav_{gacha,back,close,info,next}.png` y `mascotas_rest_0.png` a `mascotas_rest_4.png`. Cada tile mide 18x18; el boton Descansar se compone de cinco tiles.

## Archivos y destinos

La documentacion identifica Empower como principal y Aternos como copia. Claude debe verificar el panel y la base realmente instalada. Instalar despues de las tandas XP, balance/agua y Crop & Kettle; no mezclar sus versiones. Manifest exacto con SHA-256: [archivos.json](mascotas-aurora-botones-archivos.json).
| Archivo local | Destino |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/duelos/astral_duelos.sk` | `plugins/Skript/scripts/astral_duelos.sk` |
| `build/lobby/CrazyCrates/crates/gacha_monturas.yml` | `plugins/CrazyCrates/crates/gacha_monturas.yml` |
| `build/lobby/CrazyCrates/crates/gacha_monturas_garantia.yml` | `plugins/CrazyCrates/crates/gacha_monturas_garantia.yml` |
| `build/lobby/CrazyCrates/crates/gacha_monturas_garantia_suerte.yml` | `plugins/CrazyCrates/crates/gacha_monturas_garantia_suerte.yml` |
| `build/lobby/CrazyCrates/crates/gacha_monturas_suerte.yml` | `plugins/CrazyCrates/crates/gacha_monturas_suerte.yml` |
| `build/mascotas/astral_mascotas_retiro.sk` | `plugins/Skript/scripts/astral_mascotas_retiro.sk` |
| `build/menus/DeluxeMenus/gui_menus/configuraciones.yml` | `plugins/DeluxeMenus/gui_menus/configuraciones.yml` |
| `build/menus/DeluxeMenus/gui_menus/deseo.yml` | `plugins/DeluxeMenus/gui_menus/deseo.yml` |
| `build/menus/DeluxeMenus/gui_menus/deseo_lite.yml` | `plugins/DeluxeMenus/gui_menus/deseo_lite.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_bombardero.yml` | `plugins/DeluxeMenus/gui_menus/mascota_bombardero.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_brujita.yml` | `plugins/DeluxeMenus/gui_menus/mascota_brujita.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_canonero.yml` | `plugins/DeluxeMenus/gui_menus/mascota_canonero.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_desierto.yml` | `plugins/DeluxeMenus/gui_menus/mascota_desierto.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_encapuchado.yml` | `plugins/DeluxeMenus/gui_menus/mascota_encapuchado.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_fenix.yml` | `plugins/DeluxeMenus/gui_menus/mascota_fenix.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_frondoso.yml` | `plugins/DeluxeMenus/gui_menus/mascota_frondoso.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_ghastito.yml` | `plugins/DeluxeMenus/gui_menus/mascota_ghastito.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_hondero.yml` | `plugins/DeluxeMenus/gui_menus/mascota_hondero.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_honguito.yml` | `plugins/DeluxeMenus/gui_menus/mascota_honguito.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_jungla.yml` | `plugins/DeluxeMenus/gui_menus/mascota_jungla.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_llamita.yml` | `plugins/DeluxeMenus/gui_menus/mascota_llamita.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_micelio.yml` | `plugins/DeluxeMenus/gui_menus/mascota_micelio.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_nieve.yml` | `plugins/DeluxeMenus/gui_menus/mascota_nieve.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_pantano.yml` | `plugins/DeluxeMenus/gui_menus/mascota_pantano.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_pradera.yml` | `plugins/DeluxeMenus/gui_menus/mascota_pradera.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_sabana.yml` | `plugins/DeluxeMenus/gui_menus/mascota_sabana.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascota_saqueador.yml` | `plugins/DeluxeMenus/gui_menus/mascota_saqueador.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascotas.yml` | `plugins/DeluxeMenus/gui_menus/mascotas.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascotas_2.yml` | `plugins/DeluxeMenus/gui_menus/mascotas_2.yml` |
| `build/menus/DeluxeMenus/gui_menus/mascotas_3.yml` | `plugins/DeluxeMenus/gui_menus/mascotas_3.yml` |
| `build/menus/DeluxeMenus/gui_menus/oceano_aviso.yml` | `plugins/DeluxeMenus/gui_menus/oceano_aviso.yml` |
| `build/menus/DeluxeMenus/gui_menus/oficios.yml` | `plugins/DeluxeMenus/gui_menus/oficios.yml` |
| `build/menus/DeluxeMenus/gui_menus/renacer.yml` | `plugins/DeluxeMenus/gui_menus/renacer.yml` |
| `build/mythicmobs/mobs/astral.yml` | `plugins/MythicMobs/mobs/astral.yml` |
| `build/mythicmobs/mobs/cumbre.yml` | `plugins/MythicMobs/mobs/cumbre.yml` |
| `build/mythicmobs/mobs/fosa.yml` | `plugins/MythicMobs/mobs/fosa.yml` |
| `build/mythicmobs/mobs/mascotas.yml` | `plugins/MythicMobs/mobs/mascotas.yml` |
| `build/mythicmobs/mobs/santuario.yml` | `plugins/MythicMobs/mobs/santuario.yml` |
| `build/mythicmobs/skills/mascotas.yml` | `plugins/MythicMobs/skills/mascotas.yml` |
| `build/mythicmobs/skills/mazmorra.yml` | `plugins/MythicMobs/skills/mazmorra.yml` |
| `build/oceano/AstralOceano.jar` | `plugins/AstralOceano.jar` |
| `build/services/astral_servicios.sk` | `plugins/Skript/scripts/astral_servicios.sk` |

En `plugins/DeluxeMenus/config.yml`, actualizar solo la seccion gui_menus con `build/menus/DeluxeMenus/config-gui_menus.yml`, conservando otras opciones/menus del servidor. Retirar los registros y archivos `mascota_lobo.yml`, `mascota_zorro.yml`, `mascota_golem.yml`, `mascota_cuervo.yml`, `mascota_dragon.yml` y `mascotas_4.yml`. No borrar otros archivos de mascotas.

## FINAL privado y condiciones de despliegue

FINAL: `.local/terceros/AstralRPG-privado/build/entregas/mascotas-aurora-botones/AstralRPG-Textures.zip`. SHA-1 **`f9f48c8ab3c71ca002adc4e1ca830ade3734f968`**.
Base conservada: `.local/terceros/AstralRPG-privado/build/entregas/crop-kettle/AstralRPG-Textures.zip`; SHA-1 `0d7fbb96921f5915fa8f89f5f50a48bad8bdc3be`; 16786 entradas de base intactas fuera del delta. No instalar `build/AstralRPG-Textures.zip`, que es publico y carece del arte privado.
Este FINAL conserva Crop & Kettle. Su permiso de distribucion publica sigue pendiente segun [crop-kettle.md](crop-kettle.md): no publicar en R2 hasta resolver esa condicion. Si el pack instalado difiere de esta base, recombinar sobre la base correcta antes de instalar; no perder sus entradas.
Una vez resuelto: apagar desde el panel, respaldar solo archivos a reemplazar, instalar JAR/datapack/configs/menus/Skript. Conservar `plugins/AstralOceano/config.yml` (fecha de regeneracion y ajustes) y las variables de Skript. No reemplazar mundos, regiones ni usar Worlds > Upload en world.
Para el pack, solo despues de resolver distribucion: `python tools/subir_pack_r2.py ".local/terceros/AstralRPG-privado/build/entregas/mascotas-aurora-botones/AstralRPG-Textures.zip"`. Verificar descarga publica, actualizar resource-pack-sha1 en server.properties y conservar la URL fija. Reinicio completo con Java 25 obligatorio.

## Limpieza limitada y consola

Con la entrada de la Fosa cargada, borrar la Aurora existente solo en el Oceano (comando de consola, sin /):
```text
execute in minecraft:oceano run minecraft:kill @e[tag=oceano.aurora,distance=0..]
```
El selector distance=0.. limita la seleccion a esa dimension. Si la entidad estaba en un chunk descargado, visitar la entrada y repetir. No usar mm mobs killall. El modelo BetterModel privado puede permanecer archivado; el nuevo runtime nunca lo invoca.
El reinicio carga todo. Para recargas posteriores de solo configuracion: `crates reload`, `mm reload`, `dm reload`, `skript:skript reload astral_mascotas_retiro`, `skript:skript reload astral_servicios`, `skript:skript reload astral_duelos`. No usar /reload de Bukkit. El JAR requiere reinicio.
Revisar consola: AstralOceano 1.4.0 habilitado, sin errores de Skript/MythicMobs/DeluxeMenus, sin PET_GANAR de retiradas, sin nuevas Aurora. Entrar con jugador elegible, comprobar llave/mensaje una vez, Fenix y bonus; abrir las seis ventanas con el pack nuevo.

## Verificaciones

Suite completa: 323 pruebas OK; incluye modelos de botones de tanda XP. Tras la revision visual, 25 pruebas focalizadas de ventanas, navegacion y modelos OK. Auditoria publica de terceros verificada antes del commit.
Ensayo Paper 26.1.2 / Java 25: dos arranques, RET RESULT failures=0 en ambos. Skript real: dos llaves iniciales, cinco totales, sin duplicado al reingresar ni tras reinicio, seleccion retirada limpiada, entidad retirada eliminada, XP/permiso Fenix intactos. CrazyCrates se representa con un doble que verifica el comando exacto; falta probar la animacion real con cliente.
Compilacion AstralOceano 1.4.0 OK. Auditoria de referencias de pack y conservacion byte por byte del FINAL anterior. Logs y FINAL quedan privados.

## Reproduccion

Desde datapack-src: `python build.py`, `python mobs/mascotas.py`, `python mobs/mythic.py`, `python mobs/mazmorra.py`, `python lobby.py`, `python duelos.py`, `python menus.py`, `python oceano_fosa.py`, `python oceano.py --java <java25> --base ../.local/testsrv`, `python build_pack.py pack-source`. Luego `python deploy_mascotas_aurora_botones.py`. La importacion de originales Gemini (`ventanas_1611.py --import-art`) es explicita y solo se necesita para actualizar el arte fuente; compilar usa los PNG versionados.
Pruebas: `python -m unittest discover -s datapack-src -p test*.py`; `python tools/probar_retiro_1611_paper.py --java <java25> --base .local/testsrv --work .local/retiro-1611-ensayo-nuevo`. No instalar RetiroProbe.jar en remoto.

## Pendientes

Despliegue remoto, permiso de distribucion heredado de Crop & Kettle, R2, comprobacion de base instalada y revision con cliente real. Navegacion marcada P pendiente de arte final del dueno. No se afirmo instalacion en Aternos ni Empower.
