# Gachas y lobby — 17/11/2026

Preparado localmente, SIN despliegue remoto. Principal documentado: Empower; Aternos es copia.
Paper 26.1.2, Java 25, CrazyCrates 26.1.2-560610d y AstralDecor **1.17.0**.
Conservar todos los pendientes anteriores y el pack FINAL; esta tarea no cambia el resource pack.
Las estatuas tanda3a ya estan instaladas segun el estado recibido (17/11 17:03 del servidor): no recrearlas.

## Archivos exactos

| Local | Destino | SHA-256 |
|---|---|---|
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` | `34f8223dd14d7170e45efc01799425e6a7cd3b940717710d2b3b9ab2efaf3bfe` |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` | `387ab506f7405c4f9fd9ee6ea5e2f7941d0c2fd5d2182c78186c3deed9714fff` |
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

El config completo es PRIVADO. Antes de instalar, descargar de nuevo el config vigente y aplicar
`python tools/configurar_crazycrates.py <config-vigente> --output .local/crazycrates-server/config-sin-menu.yml`.
El script modifica solo gui.toggle a false, conservando comentarios y todas las otras claves.
Si el config vigente difiere de la copia del ensayo, su SHA-256 sera distinto: regenerar esta lista.
No instalar la configuracion completa del servidor de prueba ni publicar el JAR de CrazyCrates.

## Instalacion conjunta

1. Esperar a que terminen las ruletas en curso, respaldar los archivos de destino y apagar.
2. Reemplazar JAR, datapack, Skript, los tres menus y las DOCE cajas. Las cajas llevan al final
   la confirmacion interna del premio; no mezclar menus/cajas nuevos con el JAR anterior.
   Conservar config/datos de AstralDecor, variables de Skript y todos los mundos.
3. Aplicar el parche al config vigente de CrazyCrates e instalar esa copia. No borrar examples/.
4. Iniciar: **reinicio completo obligatorio** por el JAR y el datapack. No PlugMan ni reload global.
5. Revisar consola: AstralDecor 1.17.0 y CrazyCrates habilitados, Skript sin errores.
   Ejecutar `crates reload` y `dm reload`. Si posteriormente cambia solo el script:
   `skript:skript reload astral_gameplay`. gui.toggle solo requiere `crates reload`, sin reinicio.
6. Con el lobby cargado, ejecutar TODAS las lineas sin comentarios de
   `build/lobby/carteles-17-11.txt`, en orden. No ejecutar comandos.txt entero.
   Elimina text_display astral_holo del lobby y los recrea; retira el rotulo viejo de Expediciones
   por astral.amb.expediciones y mueve solo el ranking de Minas (astral_rank_minas).
   No borra NPC, rankings de otros sitios ni bloques. Si otros chunks del lobby estan descargados,
   recorrer las posiciones antes de limpiar para evitar que sobreviva un display antiguo.
7. Probar x1/10/25/50, con y sin suerte: una ruleta y luego el resto, progreso premio por premio.
   Verificar rareza alta temprana, garantia al llegar al limite, saldo cobrado una vez y premios exactos.
   Llenar inventario antes de abrir: el lote comprado queda pendiente hasta que haya lugar.
   Comprobar desconexion/reconexion, reinicio, suerte que vence durante el lote y compras consecutivas.
8. Vitrina: sin brujula Menu; conservar flechas para recorrer todos los premios. /crates como jugador
   no debe abrir ejemplos. Carteles: Venta/Bazar/Tienda a Y103.5, nombres pequenos del modelo ocultos;
   Minas sobre el NPC en 174.636 102.6 225.735, ranking separado en 169.636 102.8 226.735;
   Expediciones en 178.699 109.727 225.649. Ajuste visual final pendiente con cliente.
9. Probar doble salto en cada mini juego/dropper/arena: no debe impulsar; en survival sigue disponible.

Nunca sustituir mundos ni usar Worlds > Upload en world. En Aternos usar solo sus vias permitidas;
si no acepta el JAR propio, dejar esa parte pendiente. Claude continua con navegador autorizado.

## Pity y equivalencia

El menu anterior sumaba t antes de elegir la primera caja: podia garantizar la primera tirada
de un lote que recien alcanzaba el limite al final, y despues del reset perdia el progreso.
Ahora AstralDecor conserva una cola en PDC por jugador y la suerte al comprar; suma UNO, decide
la caja, espera la entrega y el reset de CrazyCrates, confirma ese premio y continua.
Primera tirada: forceopen CSGO. Resto: API publica pickPrize/givePrize del mismo CrazyCrates,
que es tambien la seleccion usada por mass-open. No inventa ni recalcula pesos.
El ultimo argumento historico true/false ya no fuerza garantias: el contador decide cada premio.
El progreso en vuelo se guarda para reintentar una animacion interrumpida sin sumarla dos veces.
Las llaves de ranking/directas mantienen su comportamiento anterior, fuera de la compra del menu.

Caso controlado sin epicos naturales (la garantia entrega epico), contador inicial cero:

| Gacha / limite | Lote | Antes: posiciones garantizadas / contador final | Ahora |
|---|---:|---|---|
| Armas / 50 | 50 | 1 / 0 | 50 / 0 |
| Monturas / 40 | 50 | 1 / 0 | 40 / 10 |
| Cosmeticos / 20 | 50 | 1 / 0 | 20 y 40 / 10 |

Antes mostraba una sola garantia al evaluar el total; cualquier progreso restante se perdia
en el reset de la primera ruleta. Con contador n-1 y lote 10: antes final 0, ahora final 9.

## CrazyCrates real: conteos

Se instrumentan solo los comandos de entrega para contar un premio, conservando los doce YAML,
sus pesos, resets y confirmaciones. No es un ensayo de Vault, MythicMobs ni LuckPerms.
Cliente NMS simulado; tick rate acelerado solo en el servidor aislado. CSGO usa su animacion real.
Cada fila tiene 1000 premios, sin pity. Las muestras independientes no tienen que coincidir exactamente.

| Caja | Ruta | Basura | Comun | Poco comun | Raro | Epico | Legendario |
|---|---|---:|---:|---:|---:|---:|---:|
| gacha_rpg | force | 0 | 619 | 244 | 98 | 36 | 3 |
| gacha_rpg | mass | 0 | 598 | 254 | 110 | 28 | 10 |
| gacha_rpg_suerte | force | 0 | 547 | 219 | 174 | 55 | 5 |
| gacha_rpg_suerte | mass | 0 | 528 | 251 | 168 | 50 | 3 |
| gacha_monturas | force | 567 | 180 | 98 | 113 | 37 | 5 |
| gacha_monturas | mass | 546 | 214 | 103 | 107 | 26 | 4 |
| gacha_monturas_suerte | force | 514 | 175 | 98 | 155 | 53 | 5 |
| gacha_monturas_suerte | mass | 514 | 197 | 93 | 150 | 41 | 5 |
| gacha_cosmeticos | force | 0 | 601 | 235 | 127 | 34 | 3 |
| gacha_cosmeticos | mass | 0 | 610 | 238 | 108 | 38 | 6 |
| gacha_cosmeticos_suerte | force | 0 | 554 | 229 | 162 | 47 | 8 |
| gacha_cosmeticos_suerte | mass | 0 | 549 | 246 | 156 | 40 | 9 |

Sin desviaciones mayores a cinco desvios estandar por rareza respecto de la tabla. Los pesos YAML
se conservan sin cambios. Mass-open entrega la misma cantidad; el error corregido estaba en el pity del lote.
54 lotes reales: 10/25/50, contadores 0/n-1/n, las tres gachas, con/sin suerte.
El ensayo compara el score DESPUES DE CADA PREMIO con una secuencia de tiradas simples;
si corresponde garantia comprueba que el resultado sea epico/legendario.
Repeticion con el JAR final: verifica tambien la caja exacta en cada premio, suerte vencida
inmediatamente despues de comprar, vitrinas realmente abiertas y recuperacion simulada desde PDC
con una tirada en vuelo. No sustituye probar desconexion/reinicio con cliente y los plugins remotos.
365 pruebas unitarias aprobadas y auditoria de terceros sin arte privado en archivos versionados/ZIP.
Logs, Paper, cliente simulado, plugin de prueba y configuraciones instrumentadas quedan en .local.
No instalar GachaProbe.jar en remoto.

## Paradise 3: diagnostico remoto pendiente

La largada del datapack original es automatica en la caja X -35..-33, Y95..97, Z805..807;
no se agrega un boton ni se reemplazan bloques sin identificar el lugar real de la captura.
El generador agrega dos funciones propias de diagnostico/recuperacion; no altera largada, checkpoints ni meta.
Archivo privado actualizado: `.local/mapas/subir/parkour_paradise3-datapack.zip`.
Si se instalan estas funciones: apagar, respaldar y reemplazar SOLO el contenido de la carpeta activa
`world/datapacks/parkour_paradise3-datapack/` por el ZIP (data/ y pack.mcmeta en su raiz), sin otra copia
activa del mismo pack, e iniciar. No copiar regiones, entities, level.dat ni mundos.

Consola, con un jugador en Paradise (reemplazar JUGADOR):

```text
datapack list enabled
function pp3_main:astral/diagnostico
scoreboard players get #arranco pp3_astral
execute in minecraft:parkour_paradise3 run forceload query -34 766
execute in minecraft:parkour_paradise3 run data get entity @e[type=marker,name=console,limit=1,distance=0..] Pos
execute as JUGADOR run data get entity @s Pos
execute as JUGADOR run scoreboard players get @s pp3_level
```

Si el mundo existe pero las tareas no corren: `function pp3_main:astral/reiniciar_tareas`.
Esta funcion usa schedule replace del adaptador y no cambia bloques. Volver a comprobar la largada.
Para aislarla: `execute in minecraft:parkour_paradise3 as JUGADOR run function pp3_main:player/tp/to_start`;
teletransporta solo a ese jugador al comienzo original. No es una reparacion del mapa.
Registrar F3 del boton que falta, bloque actual y el correspondiente del original privado antes de repararlo.
Comprobar que #arranco vuelva a 1 tras reinicio, marcador console cargado, avanzar dos checkpoints,
morir/volver y terminar. En la meta real, OP: `/ranking meta parkour_paradise3`.
Sigue pendiente el diagnostico en vivo, la reparacion si falta un bloque y la prueba completa jugando.

## Reproducir

Desde la raiz (Python con Pillow, NumPy y PyYAML; JDK 25 local):

```text
python datapack-src/lobby.py
python datapack-src/menus.py
python datapack-src/rankings.py
python datapack-src/build.py
python datapack-src/minijuegos_datapack.py parkour_paradise3
python datapack-src/build_runtime.py --jdk <JDK25/bin> --server .local/testsrv
python tools/probar_gachas_paper.py --java <JDK25/bin/java.exe> --base .local/testsrv
python -m unittest discover -s datapack-src -p "test*.py"
python tools/verificar_terceros.py
python datapack-src/deploy_gachas_1711.py
```
