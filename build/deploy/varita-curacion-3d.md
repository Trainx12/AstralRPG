# Pack del 17/11: curacion, arcos, ballestas y cascos

Preparado localmente; SIN subir a R2 ni desplegar. Base instalada verificada: `6421c6d38ec1303051a44b3f42b52a2b3f3dcb42`.
Un unico FINAL privado: `.local/terceros/AstralRPG-privado/build/entregas/pack-17-11/AstralRPG-Textures.zip`. SHA-1: `e78c4e802679116eda7033807de4b8868086edd0`.
249 entradas cambiadas/agregadas, ninguna eliminada; 48 modelos con icono plano nuevo.
Arte propio de la varita en el pack publico; mods y vistas derivadas SOLO en privado.

## Instalacion conjunta con pendiente-17-11

1. Mantener todos los archivos y pasos de [pendiente-17-11](pendiente-17-11.md).
2. Con acceso autorizado a R2, desde la raiz: `python tools/subir_pack_r2.py .local/terceros/AstralRPG-privado/build/entregas/pack-17-11/AstralRPG-Textures.zip`.
   Descargar la URL publica despues de subir y verificar SHA-1 `e78c4e802679116eda7033807de4b8868086edd0`.
   URL fija: https://pub-5e0d1c63a1554ba7b8e33b038e1a06fe.r2.dev/AstralRPG-Textures.zip
   No usar `build/AstralRPG-Textures.zip`: es el pack publico sin arte privado.
3. Respaldar archivos afectados y APAGAR. Instalar `build/AstralRPG-Items.zip`
   en `world/datapacks/AstralRPG-Items.zip`. Conservar todos los demas datapacks y mundos.
   No cambia Skript en esta tanda; la lista acumulada conserva su actualizacion anterior.
4. En `server.properties`, conservar resource-pack con la URL fija y poner
   `resource-pack-sha1=e78c4e802679116eda7033807de4b8868086edd0` SOLO despues de verificar la descarga.
5. INICIAR (reinicio completo obligatorio; no hace falta mm reload ni bettermodel reload).
   Para los menus previos: `dm reload`; si se reinstala su Skript: `skript:skript reload special_weapons`.
6. Revisar consola, `datapack list enabled`, descarga del pack con cliente y texturas sin errores.
   Probar arcos T1-T10, Mareas y ballestas 3/4/5 en ambas manos, todos sus estados,
   sin tapar mira ni recortar bordes. Verificar cascos en cabeza/mano/GUI/suelo/marco.

Empower es el principal documentado; Aternos queda como copia. Claude debe confirmar
el destino con navegador y usar solo las funciones permitidas por el panel. Nunca
Worlds > Upload en world ni sustitucion de mundos. Esta tarea no usa APIs remotas.

## Items existentes y vistas

Las varitas ya creadas tienen item_model minecraft:stick y NO cambian solo con el pack.
El datapack agrega `astral:upgrade/varita_curacion_modelo` al chequeo automatico de inventario:
aplica solo item_model y glint, preservando nombre, lore, encantamientos, datos y cantidad.
Los cofres se actualizan al sacar la varita al inventario. Sin subir version global de items.
Como OP se puede ejecutar `execute as <jugador> run function astral:upgrade/varita_curacion_modelo`.
Los cascos y armas con item_model astral existente reciben el aspecto nuevo al aceptar el pack.

Vista propia: `build/previews/varita_curacion_3d.png` (tambien GIF).
Vistas privadas: `.local/terceros/AstralRPG-privado/build/entregas/pack-17-11/previews/`:
`ballestas_primera_persona.png`, `arcos_primera_persona.png`, `cascos_iconos.png`.
Son renders CPU; queda pendiente la validacion visual con cliente real y consola remota.

Verificaciones locales: 37 pruebas aprobadas (11 modelos/efectos, 20 fichas/oficios/cascos/
requisitos/interruptores y 6 de esta tanda). La auditoria del FINAL y pack publico verifica
modelos/texturas; las regresiones comprueban todos los estados, cabeza intacta, fallbacks
planos, migracion puntual y preservacion de guante, mochilas, BetterModel, fuentes y shaders.

## Reproducir

```text
python datapack-src/special_weapons.py
python datapack-src/build.py
cd datapack-src
python build_pack.py pack-source
cd ..
python datapack-src/deploy_pack_1711.py
python datapack-src/preview_pack_1711.py --client .local/pack-1711-client.jar
python datapack-src/deploy_destello_guia.py
python -m unittest discover -s datapack-src -p test_pack_1711.py
python tools/verificar_terceros.py
```
