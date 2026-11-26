# Taladros y Mochila de Ender — 26/11/2026

Preparado localmente. **SIN DESPLEGAR. No se subio a R2 ni al servidor.**

**CONFIG DE MOCHILAS Y ASTRALDECOR 1.24.8 VAN JUNTOS EN EL MISMO REINICIO.**
Si se activa inception sin este JAR, el plugin permite meter mochilas en cualquier mochila.
Usar la ventana diaria de las **05:00**: instalar la config con el servidor apagado en esa ventana,
con el JAR 1.24.8 ya listo en update, y arrancar. No activar `reiniciopendiente` ni reiniciar antes.

| Archivo local | Destino | SHA-1 |
|---|---|---|
| `build/mochilas-ender/AstralRPG-Items.zip` | `/world/datapacks/AstralRPG-Items.zip` | `3bedecaa3209d89d5f39f66445c8cdc94d706be7` |
| `build/mochilas-ender/AstralDecor.jar` | `/plugins/update/AstralDecor.jar` | `d2db96739b1695d3ec5db91a2ae95ea75dcc7859` |
| `build/mochilas-ender/ExpendableBackpacks/config.yml` | `/plugins/ExpendableBackpacks/config.yml` | `839ffd7333e01ffae6f5aae7a8f6a4eef37c2c6c` |
| `.local/terceros/AstralRPG-privado/build/entregas/mochila-ender-26-11/AstralRPG-Textures.zip` | `R2 (pendiente de Claude), luego resource-pack-sha1 de server.properties` | `34bfaa0bd7790ae68d4f84e1fc130e80fd19348a` |
| `build/menus/DeluxeMenus/gui_menus/g_mochilas.yml` | `/plugins/DeluxeMenus/gui_menus/g_mochilas.yml` | `bd322468677ad0250879d8c5ab2bcf3286b48d8b` |
| `build/menus/DeluxeMenus/gui_menus/g_mochila_netherite.yml` | `/plugins/DeluxeMenus/gui_menus/g_mochila_netherite.yml` | `4170015dab9e67a5b81a353057b96f5e58a93572` |
| `build/menus/DeluxeMenus/gui_menus/g_mochila_ender.yml` | `/plugins/DeluxeMenus/gui_menus/g_mochila_ender.yml` | `491e0b7042dfbefae4062fb855c4a33ff88a6600` |
| `build/menus/DeluxeMenus/config-guia.yml` | `Combinar SOLO g_mochila_ender en /plugins/DeluxeMenus/config.yml: gui_menus` | `5353102bfd06611474d7d10b3b5683ab12b7bfec` |

La configuracion publica es una plantilla: conservar otras preferencias del servidor y cambiar
`allow-backpack-inception: true`. Registrar `g_mochila_ender: {file: g_mochila_ender.yml}` bajo `gui_menus`.
El inicio carga todo. Si se modifican SOLO menus despues, `dm reload`; no usar recarga general de plugins.
Nunca sustituir mundos ni usar Worlds > Upload.

AstralDecor 1.24.8 **REEMPLAZA a la 1.24.7 en /plugins/update**, e incluye sus monturas.
Base local SHA-1 `0ea575f26a8740a946574ecd58c265b88f0de177`. Se reemplazan solo `AstralDecor*.class` y la version de plugin.yml;
se verifican bytes identicos del resto (incluidas AstralMounts*.class), ausencia de Gomera y version exacta.
Antes de reemplazar el JAR pendiente remoto, comparar con la entrega de monturas y descargar/revisar si difiere.
Se compila con Java 25; el fuente de compilacion temporal sustituye la inicializacion de Gomera por AstralSpell.
No se modifica AstralMesa: su precio de subasta todavia no suma la mejora del taladro.

El datapack y pack PUBLICO aislados estan en `build/mochilas-ender/`, base fija `2e292e9b739275106be39825c08bbfa86d8e2b25`.
El primero aplica solo 433 entradas de mejoras/migracion de taladros; el segundo solo tres archivos
provisorios propios. Los ZIP generales en build contienen otras regeneraciones: **NO usarlos para esta entrega**.
El pack publico aislado SHA-1 `49f268b0880189b46b161f1a08676908048cca71`
es de reserva, **NO reemplaza el FINAL privado** en el servidor.

FINAL privado: base preferida del Bazar 26/11 `0312be092e42a975d016e114281e5ee4ceab196c`;
delta de solo `assets/astral/models/item/mochila_ender.json`, `assets/astral/items/mochila_ender.json`
y `assets/astral/textures/item/mochilas/mochila_ender.png`. Los otros archivos se comparan byte por byte.
Si no existe la base pendiente del Bazar, el generador usa la base en vivo del 25/11 con prefijo
`0fc13619`; tambien acepta `--base <FINAL.zip>` explicito. Revisar que corresponda a la version a instalar.
El SHA-1 resultante cambia segun la base. Imprime ambos hashes. No se sube a R2 automaticamente.
Vista privada revisada: `.local/terceros/AstralRPG-privado/build/entregas/mochila-ender-26-11/previews/mochilas-3d.png` (7 columnas).

Oculto por defecto: `#pub astral.mejtal = 0` y `#pub astral.mochender = 0`.
Solo ByTrainx mejora taladros y guarda mochilas normales en Ender. En normales se bloquea cualquier mochila;
Ender dentro de Ender se bloquea siempre, tambien clones y otras UUID. No altera UUID ni contenido.
Los interruptores se conservan en reinicios/recargas. Solo cuando el dueno lo pruebe y autorice:

```
scoreboard players set #pub astral.mejtal 1
scoreboard players set #pub astral.mochender 1
```

Para abrir el texto de la Guia: cambiar `ENDER_PUBLICO = True` en guia_cofre.py, regenerar y subir las
tres paginas afectadas; `dm reload`. Con False conserva el aviso general de bloqueo.
Para cerrar de nuevo, poner ambos scores en 0 (no borra mochilas ya guardadas y permite sacarlas).

Reproducir desde datapack-src con Python + Pillow/numpy/PyYAML y Java 25 del plan:

```
python build.py
python guia_cofre.py
python build_pack.py pack-source
python deploy_mochila_ender.py --public-only
python deploy_mochila_ender.py --java <java25>
python -m unittest test_ficha test_forge_story test_guia_cofre test_taladros_ender -q
python ../tools/probar_taladros_ender_paper.py --java <java25> --base ../.local/testsrv
python deploy_mochila_ender.py --delivery-only
```

Verificaciones: 16 pruebas Python focalizadas; comprobaciones de delta, version y aislamiento del JAR;
Guia con receta real, navegacion y slots sin solapamientos; vista 3D privada revisada.
El ensayo Paper termino con **373 comprobaciones correctas, cero fallos**, en dos arranques
(371 + 2), incluyendo atributo nativo 1,600000024 con +10 y persistencia real del plugin.
Usa eventos Bukkit reales. El JAR local ExpendableBackpacks-1.2.0.jar declara 1.0.0 en plugin.yml;
es el mismo binario de la prueba, no se redistribuye en esta entrega.
El movimiento aprobado por evento se aplica en el ensayo: no simula paquetes completos de un cliente.
Reconexion mediante eventos; reconexion de cliente y revision visual en sala del dueno siguen pendientes.
Logs privados en `.local/ender-probe/`; no publicar.

`verify.py` valida JSON y referencias del datapack y se detiene en un fallo previo:
`motosierra_basica` usa `minecraft:select`, pero el verificador espera un modelo simple (`KeyError: model`).
Se comprobo la misma definicion en HEAD. `test_gameplay` tiene dos fallos previos corroborados en HEAD:
requisito de armadura antiguo (Defensa en lugar de Combate) y click_requirement de Cazador de Bugs.
No se modifican esas funciones ni se afirma que la suite general este completamente verde.

Pendientes remotos de Claude: subir archivos correspondientes y FINAL a R2, verificar descarga y SHA-1,
actualizar propiedades, esperar el reinicio autorizado, comprobar consola/version y prueba real del dueno.
Probar taladros I-IX, conservar +N al forjar, normal dentro de Ender con contenido, salir/entrar y reiniciar,
normal vs Ender, shift/1-9/F/arrastre, otro jugador con privado/publico y clon Ender siempre bloqueado.
No anunciar nada mientras siga oculto.

Discord para cuando el dueno lo abra (guardar, NO publicar ahora):
> El Herrero ahora mejora taladros hasta +10 para picar mas rapido.
> La Mochila de Ender tiene un nuevo aspecto y su receta esta en la Guia Astral.
> Solo la Mochila de Ender puede guardar mochilas normales; otra de Ender no entra.
