# Cocina (Crop & Kettle) — 16/11/2026

Preparado localmente. Sin subida a R2 ni despliegue en Empower/Aternos.
**Instalacion condicionada a resolver licencia de distribucion y economia antes de activar.**

## Version y conservacion

Crop & Kettle 1.3.12 por maybejake, para Paper 26.1.2 / Java 25. El original usa pack_format 107; se aplican sus overlays para 101.1 y se crea una copia privada fijada a 101.1. No se cambia la version del servidor.
Base FINAL: `.local\terceros\AstralRPG-privado\build\entregas\correcciones-goblin-golems\AstralRPG-Textures.zip`, SHA-1 `5c82d87d9371feb6f68a608729b617b75b77d2e4`. Conserva las entregas anteriores, incluida correcciones-goblin-golems.
FINAL preparado: `.local/terceros/AstralRPG-privado/build/entregas/crop-kettle/AstralRPG-Textures.zip`, SHA-1 **`0d7fbb96921f5915fa8f89f5f50a48bad8bdc3be`**.
Datapack adaptado: SHA-1 `8c7e6f3342dc8945c39efad9d436d3de0c216758`. Originales intactos:

- `.local/terceros/crop-kettle/CropAndKettle-v1.3.12-Data-Pack.zip`: SHA-1 `533b3b27afc27167d22060d767daf540c460bccc`.
- `.local/terceros/crop-kettle/CropAndKettle-v1.3.12-Resource-Pack.zip`: SHA-1 `6a058e64c7e1558b6b85461ab31f39762e690d71`.

Reproducir desde la raiz:

```text
python datapack-src/build.py
python datapack-src/tanda5a.py
python datapack-src/crop_kettle.py --base ".local\terceros\AstralRPG-privado\build\entregas\correcciones-goblin-golems\AstralRPG-Textures.zip"
python -m unittest discover -s datapack-src -p test_crop_kettle.py
```
El generador sin --base elige el FINAL privado mas reciente y excluye su propia salida. Antes de desplegar, cotejar esa base con el pack realmente instalado; si difiere, regenerar sobre el instalado. No instalar el ZIP publico de texturas.

## Compatibilidad y parches

- 75 recetas de registro CNK; 2 nativas Astral y 276 recetas de su runtime revisadas: 0 coincidencias nativas y 0 coincidencias de ingredientes por material con la mesa Astral.
- Mas de cien recetas de cocina propias van por funciones/olla, no por el registro de recetas de mesa. No hay reemplazos de `data/minecraft/recipe/*` ni de loot tables vanilla.
- Tags `minecraft:load`, `tick` y `pause_screen_additions`: aditivos, sin replace; conservan Guia Astral y el enlace opcional de Smithed. `mineable/axe`, no_impact y painting_variant/placeable tampoco reemplazan tags existentes.
- Los criterios de avances conservan sus condiciones previas y agregan el predicado de survival. Los selectores @a de las funciones tambien se filtran; los bucles de entidades programados corren en el overworld. El soporte queda limitado a survival, no cocina en Nether/End ni en mundos de plugins.
- CNK incorpora seis estructuras en chunks nuevos. AstralProgression debe estar activo y su lista `structure-namespaces` debe incluir `cnk` para cancelar generacion fuera del mundo survival configurado. Sin ese plugin/config NO activar. No se regeneran chunks ni se sustituyen regiones.
- Los aldeanos carniceros de survival pueden recibir ofertas CNK. Los NPC en otros mundos no entran en el escaneo programado. El original incluye tags de trades de 26.2; la entrega esta fijada a 26.1.2, no certificada para futuras versiones.
- No se pisan item models vanilla/Astral, fuentes ni sounds.json existentes. El atlas de bloques se combina conservando las fuentes de Astral; splashes.txt conserva Astral. El panorama del menu principal aportado por CNK se incorpora.
- 50 modelos CNK adaptan referencias de texturas de entidades al atlas de items, sin cambiar PNG ni geometria. Auditoria del FINAL: 7075 referencias verificadas.
- El generador y el parche no contienen arte ni codigo copiado de CNK. Los derivados y el informe detallado `audit.json` permanecen en ASTRAL_PRIVADO. Ningun ZIP CNK/FINAL va al GitHub publico.

## Economia: revisar antes de instalar

CNK agrega nuevas rutas de produccion de comida vanilla; por ejemplo, masa -> pan da BREAD vanilla, confirmado en Paper. Los alimentos nuevos usan sobre todo POISONOUS_POTATO con componentes propios. Vender por material sin comprobar componentes podria convertir estos objetos en dinero o venderlos accidentalmente.
La copia local de EconomyShopGUI del 31/10 (no acredita precios actuales) contiene: POISONOUS_POTATO venta $15; BREAD compra $252/venta $63,04; WHEAT $20/$5; MILK_BUCKET $18,45/$4,62; COOKIE $33,60/$8,48; PUMPKIN_PIE $42,48/$10,64. No se cambiaron precios ni se publico esa copia privada.
Antes de habilitar, revisar los shops actuales y probar /sellgui y venta rapida con un item CNK, un item Astral y su equivalente vanilla. Confirmar que los componentes impidan vender custom como vanilla; si no, agregar filtro de custom_data.cnk o deshabilitar las entradas afectadas con la configuracion actual del servidor. Revisar tambien arbitraje de compra de ingredientes y venta del pan producido. No se certifica economia remota.

## Licencia

[Custom License de maybejake](https://www.curseforge.com/minecraft/data-packs/crop-and-kettle/license), edicion 25/10/2025: permite jugar en cualquier servidor y editar para uso personal; exige credito y prohibe redistribuir CNK/assets o usarlos en proyectos propios. La guia acredita al autor. Los ZIP no traen LICENSE; se verifico la pagina del autor.
La combinacion se prepara solo para este uso local privado. **No subir este FINAL a un bucket R2 publico** sin permiso expreso del autor para distribuir el pack combinado a los jugadores. La licencia permite jugar en server, pero no concede de forma expresa esa redistribucion publica. Obtener ese permiso o acordar un circuito autorizado de instalacion de recursos desde la descarga oficial antes del despliegue. No se publico el FINAL ni se altero R2.

## Archivos y destinos (solo despues de resolver condiciones)

La documentacion vigente identifica Empower como principal desde el 07/11; Aternos es copia. Confirmar panel y pack instalado con Claude. Apagar desde el panel y respaldar solamente los archivos a reemplazar.

| Archivo local | Destino |
|---|---|
| `.local/terceros/AstralRPG-privado/build/entregas/crop-kettle/CropAndKettle-Astral.zip` | `world/datapacks/CropAndKettle-Astral.zip` |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` (actualiza la guia) |
| `build/tanda5a/AstralProgression/config.yml` | Integrar `cnk` en `plugins/AstralProgression/config.yml` → `structure-namespaces`, conservando el resto de la config remota |
| `.local/terceros/AstralRPG-privado/build/entregas/crop-kettle/AstralRPG-Textures.zip` | Pack de recursos FINAL privado; distribucion pendiente de permiso del autor |

Instalar CNK una sola vez en `world/datapacks/`, junto a Astral: Paper comparte datapacks entre dimensiones. No copiar en lobby/minas/mazmorras ni crear carpetas datapacks dentro de cada dimension. Eliminar solo una instalacion CNK duplicada si existe, previa copia; nunca tocar mapas.
El config regenerado tambien refleja golems/items de fuentes ya publicadas; para esta instalacion integrar solamente `cnk` en la lista remota, sin reemplazar otros ajustes.
Cuando exista permiso para el circuito de recursos, actualizar `resource-pack-sha1` con el SHA-1 de la descarga verificada y mantener su URL correspondiente. No pegar un hash local sin verificar el archivo distribuido.

## Inicio, consola y comprobacion

Reinicio completo obligatorio: datapack/worldgen, configuracion y resource pack. No usar recarga general en caliente. No se necesita mm reload ni skript reload si las configs ya cargaron al iniciar. Si se ajustan solo precios despues: `sreload`.
Consola: `datapack list enabled`; verificar Astral y CropAndKettle-Astral, ausencia de errores de functions/advancements/recipes y AstralProgression activo con survival correcto. Comprobar carga de Skript y MythicMobs. Revisar ambos accesos del menu de pausa y el recetario CNK con cliente.
En survival, fabricar olla (caldero+fogata), cocinar una receta del recetario y plantar un cultivo nuevo; comprobar crecimiento, cosecha y protecciones de claims/WorldGuard con un jugador sin permisos de admin. Repetir intento en lobby/minas/mazmorras: no debe activar CNK ni generar estructuras. Medir `spark` antes/despues con carga representativa; la prueba local no certifica TPS remoto.
Nunca usar Worlds > Upload en la fila world, ni sustituir mundos/regiones. No se utilizaron navegador, APIs privadas ni credenciales para este trabajo.

## Pruebas locales

Ensayo `.local/crop-kettle-probe5`: APROBADO. Paper 26.1.2, Java 25, Astral completo, Skript, MythicMobs y BetterModel. Jugador NMS sin cliente: olla real consume masa y produce pan; maiz crece con random ticks acelerados; predicado de survival positivo y Nether excluido.
Costo ponderado de entradas CNK: 0.147233 ms/tick.
Microbenchmark local: 200 llamadas por entrada, ponderadas por sus periodos; un jugador, una olla y un cultivo. Incluye dispatch de comandos; no equivale a perfil de produccion. Logs privados incluyen baseline y CNK; no se publican.

Reproducir: `python tools/probar_crop_kettle_paper.py --java <java25> --base .local/correcciones-probe/paper --work .local/crop-kettle-ensayo-nuevo`. No instalar CropKettleProbe.jar en remoto. Pruebas propias: seis controles unitarios de conservacion, overlays, atlas, animacion y aislamiento; mas conservacion byte a byte del FINAL anterior cuando esta disponible.
Pendientes: cliente visual, interacciones/protecciones con jugadores reales, estructuras en mundos de plugins, economia actual, permiso de distribucion, R2 y despliegue remoto.
