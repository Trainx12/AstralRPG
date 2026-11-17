# Pendiente conjunto — 17/11/2026

Generado por `datapack-src/deploy_destello_guia.py`. Preparado localmente; sin despliegue remoto.
Empower es el principal documentado; Aternos es copia. Paper 26.1.2 / Java 25.
Esta tabla reemplaza los hashes/listas del 17/11 en [bastones e interruptores](efectos-direccion-interruptores.md) y [tier T6, XP y suerte](tier6-suerte.md). Conservar sus instrucciones funcionales y pendientes.
Incluye direccion/interruptores, T6/XP/suerte, Destello/pausa y la tanda visual de varita/arcos/cascos. No sustituye otras entregas anteriores que todavia no se hayan instalado.

## Archivos actuales (SHA-256)

| Local desde la raiz | Destino | SHA-256 |
|---|---|---|
| `build/runtime/AstralEfectos.jar` | `plugins/AstralEfectos.jar` | `95a48419a73001a53b5468656f8eaf4d205dc2e345de6c1ccdc50816654b110c` |
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` | `34f8223dd14d7170e45efc01799425e6a7cd3b940717710d2b3b9ab2efaf3bfe` |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` | `40bc478d2cb1b35679e14496ae9569abf2887017db6b4419756de19458ab2fc4` |
| `.local/terceros/AstralRPG-privado/build/entregas/crop-kettle/CropAndKettle-Astral.zip` | `world/datapacks/CropAndKettle-Astral.zip` | `ebc22200ef9e0a5333716f8e9486fa3df1e5764d29e9a583f23a13aa55107e10` |
| `build/gameplay/astral_armas_especiales.sk` | `plugins/Skript/scripts/special_weapons.sk` | `45f2f6bb1292ad1cea5eb4bf655ea678630ffdfda08df6e1d183444f346c1807` |
| `build/services/astral_servicios.sk` | `plugins/Skript/scripts/astral_servicios.sk` | `2d930b05746e6fbde8b1dbe81aaeff95a774227d20c9cbf918abc30f2d74e88a` |
| `build/menus/DeluxeMenus/gui_menus/configuraciones.yml` | `plugins/DeluxeMenus/gui_menus/configuraciones.yml` | `e51c83103d02179fb624d479f15c91cd8cc38bec06d946f33a4d6e5c905d47a3` |

CNK permanece privado: no subir su ZIP al GitHub publico. La tanda visual posterior SI cambia el pack: usar el unico FINAL y el SHA-1 de [varita, arcos y cascos](varita-curacion-3d.md), subirlo a R2, verificar descarga y actualizar resource-pack-sha1 antes del mismo reinicio.

## Orden de instalacion y consola

1. Cotejar esta tabla con los archivos actuales. Respaldar solo los archivos que se reemplazan y apagar el servidor.
2. Reemplazar los siete archivos en los destinos indicados. Si CNK conserva el nombre original `CropAndKettle-v1.3.12-Data-Pack.zip`, reemplazar esa unica copia activa por la adaptada: no dejar ambos ZIP activos. Conservar los demas datapacks y configs.
3. Mantener una sola copia activa de AstralDecor y special_weapons.sk. Conservar desactivada la copia duplicada astral_armas_especiales.sk registrada el 16/11. Nunca reemplazar mundos ni usar Worlds > Upload en world.
4. Antes de iniciar, auditar las copias de TODOS los datapacks habilitados con `python tools/verificar_menu_pausa.py <Astral.zip> <CNK.zip> <otros-ZIP-o-carpetas-habilitados>`. La union en pausa y acciones rapidas debe ser solo astral:guia. Revisar tambien datapacks adicionales que no figuren en la documentacion.
5. Iniciar: reinicio completo obligatorio por JAR y datapacks. No usar PlugMan ni recarga global. El arranque carga Skript; si solo se cambia despues: `skript:skript reload special_weapons` (cero errores).
6. Ejecutar `dm reload`; si falta registrar Configuraciones, integrar `configuraciones: {file: configuraciones.yml}` en gui_menus sin pisar otras entradas. No hace falta mm reload ni crates reload: no cambian sus YAML.
7. Consola: `datapack list enabled`; AstralDecor 1.15.0 y AstralEfectos 1.2.0 activos, 216 recetas exactas, Skript sin errores. Mantener PacketEvents y el preset legacy de AuraSkills.
8. Con cliente: probar Destello en lobby y survival, sin cartel de carga ni giro de camara, mana 50 por uso, bloqueo/protecciones con devolucion, estela, sonidos y velocidad. Abrir pausa: debe decir Guia Astral; no debe haber acceso nuevo a CNK/Smithed. Comprobar cocina y los interruptores, XP, suerte y requisitos segun las dos guias anteriores.

Aternos: si se eligiera esa copia, instalar solo por sus vias permitidas y confirmar que acepta el JAR. Esta entrega no uso navegador ni APIs remotas; Claude continua la instalacion con acceso al panel.

## Implementacion y evidencia

- AstralDecor 1.15.0 agrega astraldecor:astralblink UUID dx dy dz, exclusivo de consola, con destino calculado desde el mundo actual y limites finitos/radio 13. Usa TeleportCause.PLUGIN y flags vigentes de velocidad/rotacion, RETAIN_PASSENGERS. Conserva la cancelacion de listeners. El listener de cosmeticos ignora viajes dentro del mismo mundo.
- Skript mantiene trayectoria, costo, devolucion, estela, sonidos, velocidad y caida. Danza del Ender ya usa la API mediante Skript, sin minecraft:tp; no se cambio su giro intencional hacia el enemigo. El unico minecraft:tp de armas cortas era Destello.
- CNK/Smithed se retiran de los tags de pausa y acciones rapidas despues de resolver overlays. No se agrega boton a Guia Astral ni replace:true. Cocina y archivos de dialogos originales siguen disponibles internamente.
- 38 pruebas unitarias aprobadas (armas, CNK, mesa, XP, requisitos, interruptores y loops). Auditoria final de Astral+CNK+Dungeons and Taverns 5.2.0: ambos tags contienen solo astral:guia.
- Paper 26.1.2 local, Skript 2.17.1: 28 comprobaciones aprobadas y BLINK RESULT failures=0. Jugador NMS simulado y captura directa en ServerGamePacketListenerImpl: en world y minecraft:lobby avanza 12 bloques, conserva mundo/rotacion/velocidad, emite posicion sin RESPAWN; cancelar devuelve mana una vez; rechaza NaN, desplazamiento excesivo y comando como jugador. Mana usa un doble de consola para contar debitos/devoluciones; no acredita el saldo real de AuraSkills. Arranque y scripts sin errores. No instalar BlinkProbe.jar en remoto.

## Limites y pendientes concretos

- El comando vanilla anterior TAMPOCO emitio RESPAWN en el ensayo local, en ninguno de los dos mundos. La causa del cartel remoto no esta reproducida ni confirmada. No se afirma solucion visual verificada.
- No se encontro el JAR de Multiverse en las dependencias locales. Lobby se creo por WorldCreator con clave minecraft:lobby, dimension separada. Falta ensayar el conjunto remoto de plugins (Multiverse, WorldGuard, BetterModel, mascotas y demas listeners) y cliente real.
- La API de Paper recibe destino absoluto; sus flags relativos conservan velocidad y rotacion. Los alias X/Y/Z/YAW/PITCH estan obsoletos y no garantizan coordenadas relativas del paquete. Confirmar ausencia de tiron de camara con cliente en survival y lobby antes de cerrar el incidente.
- No hay copias locales identificadas de DnT Stronghold Overhaul 2.4.0, Incendium 5.4.12 ni Stellarity 5.4.2. Falta auditar los ZIP realmente habilitados del servidor y su orden; no se certifica la union remota solo con las copias disponibles.
- Siguen pendientes los ensayos mass-open/pity y sus conteos del JAR exacto de CrazyCrates, detallados en tier6-suerte.md. No se alteraron probabilidades ni lotes en esta tarea.
- Despliegue, consola remota y validacion visual pendientes de Claude con navegador.

## Reproducir

Desde la raiz, con Python/dependencias locales:

```text
python datapack-src/special_weapons.py
python datapack-src/crop_kettle.py --datapack-only
python datapack-src/build_runtime.py --jdk <JDK25/bin> --server .local/testsrv
python tools/probar_destello_paper.py --java <JDK25/bin/java.exe> --base .local/testsrv
python datapack-src/deploy_destello_guia.py
python tools/verificar_terceros.py
```

`--datapack-only` no selecciona ni reescribe el FINAL privado: usa los originales CNK conservados. Logs y plugins de ensayo permanecen exclusivamente en .local/.

## Pack FINAL unico de la tanda visual

Reemplaza el FINAL de bcd2b3e (e78c4e80): NO instalar aquel ZIP. Incluye Reparar y primera persona corregida.

Local: `.local/terceros/AstralRPG-privado/build/entregas/pack-17-11/AstralRPG-Textures.zip`. Destino R2: `AstralRPG-Textures.zip` (URL fija existente).
SHA-1 FINAL: `96286fbdc33d77b4ebcc11de8b15f7461631bac4`. Base instalada: `6421c6d38ec1303051a44b3f42b52a2b3f3dcb42`.

1. Subir con `python tools/subir_pack_r2.py .local/terceros/AstralRPG-privado/build/entregas/pack-17-11/AstralRPG-Textures.zip`. Descargar la URL publica y verificar ese SHA-1.
2. Con el servidor apagado, actualizar `server.properties`: `resource-pack-sha1=96286fbdc33d77b4ebcc11de8b15f7461631bac4`. Conservar resource-pack con su URL fija.
3. Instalar el datapack de la tabla actualizada de arriba y los demas pendientes en el mismo apagado; iniciar y revisar consola. Reinicio completo obligatorio.
4. Aceptar el pack con cliente real y comprobar varita, arcos/ballestas en ambas manos y estados, cascos en cabeza y planos en mano/GUI/suelo/marco.

5. Herrero: abrir la ventana, verificar Reparar en 48-50 (gris sin equipo, verde listo, rojo sin recursos), pasar el cursor para costo y material, probar clic en las tres casillas y comprobar cobro/reparacion una sola vez. El arranque carga el Skript; para una correccion posterior: `skript:skript reload astral_servicios`, cero errores. Revisar consola y devolucion del equipo al cerrar. Vista: `build/previews/herrero_reparar.png`.

Detalle, migracion automatica de varitas existentes y vistas privadas: [varita-curacion-3d](varita-curacion-3d.md).
R2, panel remoto y comprobacion con cliente siguen pendientes de Claude; esta entrega no afirma despliegue.

## Monturas, criaturas y Basura (17/11)

Entrega adicional: [monturas-17-11.md](monturas-17-11.md), con ocho archivos exactos y hashes.
Instalar AstralDecor **1.16.0** (sustituye el 1.15.0 indicado arriba) en el mismo apagado/reinicio.
Incluye las copias privadas de mobs/astral.yml y skills/astral.yml, las tres cajas de Monturas
y su menu. Mantener todos los otros pendientes. No cambia el pack FINAL ni su SHA-1.
Tras arrancar: consola limpia; para ajustes posteriores `mm reload`, `crates reload`, `dm reload`.
Despliegue y validacion con cliente siguen pendientes; no se reemplazan mundos.

### Estatuas del Santuario (instalable por separado, sin reinicio)

Subir `build/mythicmobs/mobs/tanda3a.yml` a `plugins/MythicMobs/mobs/tanda3a.yml`.
Conservar skills/tanda3a.yml: no cambia. Ejecutar en consola:
```
mm reload
mm mobs kill astral_estatua_cangrejo
```
Las cinco estatuas ahora usan IRON_GOLEM; el modelo sigue a escala 2.0.
Conservar la Forja existente. El dueno, parado en cada pedestal correspondiente:
```
/mm mobs spawn astral_estatua_coloso_musgoso
/mm mobs spawn astral_estatua_chaman
/mm mobs spawn astral_estatua_momia
/mm mobs spawn astral_estatua_yeti
```
Si falta tambien la Forja: `/mm mobs spawn astral_estatua_golem_forja`.
Comprobar `mm mobs listactive`, persistencia tras cargar chunks y consola sin errores.
No recrear una estatua que ya exista: verificar primero para evitar duplicados.
La escala visual relativa necesita validacion con cliente en los pedestales.

## Gachas, carteles y doble salto — tanda del 17/11

Entrega adicional vigente: [gachas-carteles-17-11.md](gachas-carteles-17-11.md).
AstralDecor **1.17.0** sustituye el 1.16.0 anterior; instalar los siguientes archivos en el mismo apagado.
Conservar todos los otros pendientes y el pack FINAL. Las estatuas tanda3a ya estan instaladas segun el estado recibido.

| Local | Destino | SHA-256 |
|---|---|---|
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` | `34f8223dd14d7170e45efc01799425e6a7cd3b940717710d2b3b9ab2efaf3bfe` |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` | `40bc478d2cb1b35679e14496ae9569abf2887017db6b4419756de19458ab2fc4` |
| `build/gameplay/astral_gameplay.sk` | `plugins/Skript/scripts/astral_gameplay.sk` | `d2e3ded9f527d93d91e976e98d3f89ad4e526e661ef1dc89b44cbf43fc97fd87` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos.yml` | `7d4335154fef0ae36435a1dee8f510b8aaf3fc7285e6eedc461ac9099e1e36d7` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos_garantia.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos_garantia.yml` | `8a6c324c9b550e682b8fa1f6bc32d6ea00adc3797992774406f2c93ab8beca5b` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos_garantia_suerte.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos_garantia_suerte.yml` | `8a6c324c9b550e682b8fa1f6bc32d6ea00adc3797992774406f2c93ab8beca5b` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos_suerte.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos_suerte.yml` | `c58181a7259f43a84b6688a941cd5d11855febeb22688e3481c255a29138a96d` |
| `build/lobby/CrazyCrates/crates/gacha_monturas.yml` | `plugins/CrazyCrates/crates/gacha_monturas.yml` | `82c8e0f628cbed89928f1755f5d2f96a859d77799a06ebd1cff6791517da5344` |
| `build/lobby/CrazyCrates/crates/gacha_monturas_garantia.yml` | `plugins/CrazyCrates/crates/gacha_monturas_garantia.yml` | `c373cfa12e6e2a0cea67026f6b066890dc96a193b246e7bfc2c88b4c39cd08ff` |
| `build/lobby/CrazyCrates/crates/gacha_monturas_garantia_suerte.yml` | `plugins/CrazyCrates/crates/gacha_monturas_garantia_suerte.yml` | `c373cfa12e6e2a0cea67026f6b066890dc96a193b246e7bfc2c88b4c39cd08ff` |
| `build/lobby/CrazyCrates/crates/gacha_monturas_suerte.yml` | `plugins/CrazyCrates/crates/gacha_monturas_suerte.yml` | `a27fa0a46b45b5db650a34bb63f18bc7ad9e296ebed1b0869e7317326473129c` |
| `build/lobby/CrazyCrates/crates/gacha_rpg.yml` | `plugins/CrazyCrates/crates/gacha_rpg.yml` | `56dca58ab3d64a2c08dc96b0eacba5003452ad4169b0ce0e5c4a5fdc255ec1fa` |
| `build/lobby/CrazyCrates/crates/gacha_rpg_garantia.yml` | `plugins/CrazyCrates/crates/gacha_rpg_garantia.yml` | `56c4ad346850dd1f294a341bd101875f0e1f975f8a4295f810562a4e1a2107a6` |
| `build/lobby/CrazyCrates/crates/gacha_rpg_garantia_suerte.yml` | `plugins/CrazyCrates/crates/gacha_rpg_garantia_suerte.yml` | `56c4ad346850dd1f294a341bd101875f0e1f975f8a4295f810562a4e1a2107a6` |
| `build/lobby/CrazyCrates/crates/gacha_rpg_suerte.yml` | `plugins/CrazyCrates/crates/gacha_rpg_suerte.yml` | `80d3c3840d0fc32343aad055a06968a6f5938cba4646f0d54fb9ac4a968206e9` |
| `build/menus/DeluxeMenus/gui_menus/gacha_rpg.yml` | `plugins/DeluxeMenus/gui_menus/gacha_rpg.yml` | `d9e7e788f2b3194a3deee2759593bf40f1da333730937873a59a94d4b7bbda74` |
| `build/menus/DeluxeMenus/gui_menus/gacha_monturas.yml` | `plugins/DeluxeMenus/gui_menus/gacha_monturas.yml` | `c001372a6ea23310ec36acf0b33effd6ae995e192a8bf67412233165f61047b0` |
| `build/menus/DeluxeMenus/gui_menus/gacha_cosmeticos.yml` | `plugins/DeluxeMenus/gui_menus/gacha_cosmeticos.yml` | `f86e6d7e90ee86528ce43bcc88c35ebf384d4ede4cd23083e18ac8fb68a955eb` |
| `.local/crazycrates-server/config-sin-menu.yml` | `plugins/CrazyCrates/config.yml` | `1e786a263d22ddd3bdf06ad7bec7c2900f88c8a57c076580a2981fb81910c255` |

Reinicio completo por JAR/datapack. Luego `crates reload`, `dm reload` y consola sin errores.
Ejecutar las lineas de `build/lobby/carteles-17-11.txt` para limpiar/recrear carteles (solo lobby).
El config privado se prepara sobre una copia NUEVA del vigente con `tools/configurar_crazycrates.py`:
solo `gui.toggle: false`; ese cambio aislado requiere `crates reload` y no requiere reinicio.
Actualizacion opcional del datapack privado de Paradise y comandos de diagnostico en la entrega enlazada.
Paradise sigue pendiente de diagnostico en vivo; no se certifica largada/checkpoints/meta ni boton reparado.
Despliegue, consola remota, cliente visual y reconexion/reinicio con lotes en curso siguen pendientes de Claude.
Nunca sustituir mundos ni usar Worlds > Upload en world.

## Mascotas, oceano y panorama (entrega anterior)

Lista y hashes vigentes: [mascotas-oceano-panorama-17-11](mascotas-oceano-panorama-17-11.md).
Esta tanda reemplaza los mismos JAR/datapack/script de las tablas anteriores y agrega AstralProgression, AstralOceano y el YAML privado de mascotas. Conservar el resto de 054db88 pendiente.
FINAL anterior, sustituido por la ultima entrega de cascos: `.local/terceros/AstralRPG-privado/build/entregas/mascotas-oceano-panorama-17-11/AstralRPG-Textures.zip`; SHA-1 `d9ec25c013ccffd028bd384a189e9b3524fdda37`, encima de `96286fbdc33d77b4ebcc11de8b15f7461631bac4`.
Apagar y reiniciar. R2 e instalacion remota pendientes de Claude con navegador. Nunca reemplazar mundos. Instrucciones del dueno: [decoraciones](../../docs/OCEANO_DECORACIONES.md).

## Cascos, silencio y mercader (ultima entrega)

Lista exacta y hashes: [cascos-silencio-mercader-17-11](cascos-silencio-mercader-17-11.md). Sustituye AstralDecor por 1.18.0, YAML de mobs y FINAL de 98156c2; conservar sus demas archivos y 054db88.
Unico FINAL `.local/terceros/AstralRPG-privado/build/entregas/cascos-silencio-mercader-17-11/AstralRPG-Textures.zip`; SHA-1 `9d83b49323139271250519fbfd7df7f65857d730`. Requiere apagar/reiniciar por JAR y pack. Solo YAML: `mm reload`. R2, servidor y cliente pendientes de Claude; sin despliegue verificado.

## Bastones perforantes y golemcitos (ultima entrega)

Lista exacta y hashes: [bastones-golems-17-11](bastones-golems-17-11.md). AstralDecor 1.20.0, AstralEfectos 1.4.0, datapack v26 y script PvP. FINAL privado `.local/terceros/AstralRPG-privado/build/entregas/bastones-golems-17-11/AstralRPG-Textures.zip`; SHA-1 `5448b7ff24d6da012cc08de16a0d74b11b23a2e0`, encima de `9d83b49323139271250519fbfd7df7f65857d730`. Apagar y reiniciar. R2, servidor y cliente pendientes de Claude; no hay despliegue verificado. Ver la distincion tarea/acumulado antes de combinar con Chaman/hitboxes. No sustituir mundos.
