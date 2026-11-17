# Pack del 17/11: curacion, arcos, ballestas, cascos y Reparar

Preparado localmente; SIN subir a R2 ni desplegar. Base instalada verificada: `6421c6d38ec1303051a44b3f42b52a2b3f3dcb42`.
Un unico FINAL privado: `.local/terceros/AstralRPG-privado/build/entregas/pack-17-11/AstralRPG-Textures.zip`. SHA-1: `96286fbdc33d77b4ebcc11de8b15f7461631bac4`.
277 entradas cambiadas/agregadas, ninguna eliminada; 48 modelos con icono plano nuevo.
Arte propio de la varita en el pack publico; mods y vistas derivadas SOLO en privado.
Este FINAL reemplaza al de bcd2b3e (`e78c4e80...`, no desplegado); no instalar aquel.

## Instalacion conjunta con pendiente-17-11

1. Mantener todos los archivos y pasos de [pendiente-17-11](pendiente-17-11.md).
2. Con acceso autorizado a R2, desde la raiz: `python tools/subir_pack_r2.py .local/terceros/AstralRPG-privado/build/entregas/pack-17-11/AstralRPG-Textures.zip`.
   Descargar la URL publica despues de subir y verificar SHA-1 `96286fbdc33d77b4ebcc11de8b15f7461631bac4`.
   URL fija: https://pub-5e0d1c63a1554ba7b8e33b038e1a06fe.r2.dev/AstralRPG-Textures.zip
   No usar `build/AstralRPG-Textures.zip`: es el pack publico sin arte privado.
3. Respaldar archivos afectados y APAGAR. Instalar `build/AstralRPG-Items.zip`
   en `world/datapacks/AstralRPG-Items.zip`. Conservar todos los demas datapacks y mundos.
   Instalar `build/services/astral_servicios.sk` en `plugins/Skript/scripts/astral_servicios.sk`.
   Reparar usa las casillas 48-50 (todas clicables), bajo MEJORAR, sin tocar Equipo/Materiales.
4. En `server.properties`, conservar resource-pack con la URL fija y poner
   `resource-pack-sha1=96286fbdc33d77b4ebcc11de8b15f7461631bac4` SOLO despues de verificar la descarga.
5. INICIAR (reinicio completo obligatorio; no hace falta mm reload ni bettermodel reload).
   Para los menus previos: `dm reload`; si se reinstala su Skript: `skript:skript reload special_weapons`.
   Para Herrero: `skript:skript reload astral_servicios` (cero errores); el reinicio ya lo carga.
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
Vista propia del Herrero: `build/previews/herrero_reparar.png`, tres estados.
Reparar repite el sistema de MEJORAR: fondo propio y tres tiles con item_model,
gris sin equipo, verde con equipo/material/saldo, rojo si faltan recursos.
Nombre/lore conservan tier y costos; todas las casillas 48-50 responden al clic.
No cambia el costo ni el modificador `astral:reparar`. Volver permanece en 45.
Vistas privadas: `.local/terceros/AstralRPG-privado/build/entregas/pack-17-11/previews/`:
`ballestas_primera_persona.png`, `arcos_primera_persona.png`, `cascos_iconos.png`.
Resumenes nuevos: `ballestas_revision.png`, `arcos_revision.png` (vanilla/base instalada/despues).
Medidas privadas: `primera_persona_medidas.json`, 84 combinaciones de modelo/estado/mano.
Area 76,22%-109,09% de vanilla, centro a <=15 px (ancho 400); todas tocan el borde inferior.
Se normalizan los margenes transparentes del icono conservando su proporcion y orientacion
vanilla; rotacion/reflejo de mano izquierda y UV de fotogramas animados corregidos en el render.
Son renders CPU de los estados de reposo/tensado, sin animacion del brazo ni balanceo;
queda pendiente la validacion visual con cliente real y consola remota.

Verificaciones locales: 48 pruebas aprobadas (ventanas, bazar, oficios, loops,
modelos/efectos y 8 de esta tanda). La auditoria del FINAL y pack publico verifica
modelos/texturas; las regresiones comprueban todos los estados, cabeza intacta, fallbacks
planos, migracion puntual y preservacion de guante, mochilas, BetterModel, fuentes y shaders.
Paper 26.1.2 local / Java 25 / Skript 2.17.1 / Vault 1.7.3 / Essentials 2.22:
carga de 24 estructuras y recarga de `astral_servicios` sin errores. El ensayo usa
un umbral de aviso de watchdog de 60 s solo en su carpeta aislada; no instalar esa config.
No se simulo una compra ni clic con cliente: validar cobro, material y devolucion en remoto.

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
python tools/probar_herrero_1711.py --java <JDK25/bin/java.exe> --base .local/interfaces-v2-test
python tools/verificar_terceros.py
```
