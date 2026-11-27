# Nucleo de Venta Automatica: interruptor e icono (27/11/2026)

Preparado localmente. Despliegue remoto y prueba visual pendientes de Claude.
Sigue oculto: solo ByTrainx, salvo apertura explicita con `autoventa publico`.
La receta sigue desactivada y no aparece en la Guia.

## Archivos exactos

| Local | Destino |
| --- | --- |
| `build/autoventa/astral_minas.sk` | `plugins/Skript/scripts/astral_minas.sk` |
| `build/autoventa/AstralRPG-Autoventa.zip` | `world/datapacks/AstralRPG-Autoventa.zip` |
| `.local/terceros/AstralRPG-privado/build/entregas/corazon-astral-27-11/AstralRPG-Textures.zip` | Resource pack FINAL en R2 (Claude); conservar URL fija |

ZIP aditivo SHA-256: `5683ea6a4903d9d52928d8ca359b12fb9752c58157bc541177ae2b7c3cfff8e8`.
FINAL esperado SHA-1: `575c6dc776f4ca270dc7e006a9d54dac799d600b`.
Su base fue `bazar-tarjeta-27-11` (SHA-1 `799e337a060e63317de40b9d03252e5e6e24ff5b`):
solo agrega/reemplaza las tres entradas `assets/astral/{items/autoventa.json,models/item/autoventa.json,textures/item/autoventa.png}`.
Si hay un FINAL posterior, regenerar sobre esa base antes de instalar.
No publicar el FINAL privado en GitHub. No subir `receta-desactivada.json`.

## Instalacion por Claude

El plan indica que el datapack anterior aun no cargo. Apagar para reemplazar el ZIP,
el FINAL y `resource-pack-sha1` de `server.properties`; iniciar con el reinicio diario
de las 05:00 o el autorizado por el dueno. No reiniciar por cuenta propia.
Con el datapack nuevo ya cargado, un cambio exclusivo de Skript basta con
`skript reload astral_minas` (alternativa sin alias: `skript:skript reload astral_minas`).
No usar reload global. No sustituir mundos ni Worlds > Upload.

La copia de servidor faltaba en build: se reconstruyo desde el respaldo pre-autoventa
y el bloque de HEAD; coincide exactamente con SHA-256
`317a43a8bfa2e75eb7be8e814536bf1ec37952177992abadd4d77e2d72f51240` del plan.
Se probo el reemplazo de ese bloque conservando el resto. Antes de subir, descargar
la copia remota vigente y comparar; si cambio, regenerar:
`python datapack-src/deploy_autoventa.py --server-script COPIA_REMOTA.sk`.
Tambien acepta la version sin autoventa y la ya actualizada (idempotente).
No subir el acumulado `build/minas` ni `build/AstralRPG-Items.zip` del workspace:
contienen cambios previos ajenos. Conservar las variables de Skript.

Revisar consola sin errores, `datapack list enabled`, prioridad aditiva al final.
Si hace falta: `datapack enable "file/AstralRPG-Autoventa.zip" last`.
Dar un Nucleo actualizado: `minecraft:loot give ByTrainx loot astral:item/autoventa`.
Los ya entregados conservan lore/icono anterior hasta reemplazarlos; el toggle
los reconoce por custom_data igualmente. No se migra todo el inventario.
Comprobar `papi parse ByTrainx %auraskills_mining%` numerico.

## Comportamiento y verificacion

Shift + clic derecho con el Nucleo en principal o secundaria alterna en cualquier mundo.
Sin Shift no cambia. Estado por UUID en `{am.autoventa.off::UUID}`, persistente;
ausencia = ENCENDIDO. APAGADO no vende y conserva el aviso habitual de inventario lleno.
Barra de accion ENCENDIDO/APAGADO y clic con tonos distintos. Brillo fijo: no se usa
como indicador por jugador. Identificacion real por custom_data, sin aceptar renombrados.

Pruebas: `python -m unittest test_autoventa` desde datapack-src;
`python tools/probar_autoventa_paper.py --java JAVA25 --base PAPER_LOCAL --work DIRECTORIO_NUEVO`;
`python tools/verificar_terceros.py`. El ensayo incluye segundo arranque para persistencia.
Usa un doble local DeluxeMenus/PAPI: la expansion real y la vista del icono quedan
pendientes de probar en servidor con cliente. No Discord mientras siga oculto.

Verificado el 27/11: cuatro pruebas Python y 48 comprobaciones Paper 26.1.2 con
Skript 2.17.1 aprobadas, incluyendo reinicio real y persistencia. Auditoria de
terceros del repo y del contenido aislado a publicar sin arte privado.
