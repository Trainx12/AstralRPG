# Cosmeticos y SkinsRestorer: entrega sin desplegar

Generado por `python datapack-src/deploy_cosmeticos.py`. Servidor activo: Empower / Paper 26.1.2 / Java 25; Aternos es la copia antigua.
Requiere haber instalado la entrega `yeti-bastones-guia.md` (incluye Tienda). No reemplazarla por los derivados globales privados.

## Archivos exactos

| Local | Destino |
|---|---|
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` |
| `.local/cosmeticos-deps/SkinsRestorer.jar` | `plugins/SkinsRestorer.jar` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos.yml` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos_garantia.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos_garantia.yml` |
| `build/menus/DeluxeMenus/gui_menus/cosmeticos.yml` | `plugins/DeluxeMenus/gui_menus/cosmeticos.yml` |
| `build/menus/DeluxeMenus/gui_menus/cosmeticos_sombreros.yml` | `plugins/DeluxeMenus/gui_menus/cosmeticos_sombreros.yml` |
| `build/menus/DeluxeMenus/gui_menus/cosmeticos_alas.yml` | `plugins/DeluxeMenus/gui_menus/cosmeticos_alas.yml` |
| `build/menus/DeluxeMenus/gui_menus/gacha_cosmeticos.yml` | `plugins/DeluxeMenus/gui_menus/gacha_cosmeticos.yml` |
| `build/menus/DeluxeMenus/gui_menus/principal.yml` | `plugins/DeluxeMenus/gui_menus/principal.yml` |

Pack FINAL privado: `.local/terceros/AstralRPG-privado/build/entregas/cosmeticos-skins/AstralRPG-Textures.zip`; SHA-1 `7c86561ca5edae444bf3fae055eae78a3c31496f`.
Base Tienda/Yeti `18107d6003a7f9f190d604e67a9cdf6b6096e02f`; 73 entradas nuevas/cambiadas, ninguna eliminada, 5239 referencias auditadas. Los assets anteriores se conservan byte por byte.
Publicar durante el despliegue: `python tools/subir_pack_r2.py .local/terceros/AstralRPG-privado/build/entregas/cosmeticos-skins/AstralRPG-Textures.zip`. Verificar descarga publica y luego fijar `resource-pack-sha1=7c86561ca5edae444bf3fae055eae78a3c31496f`. No usar el ZIP publico.

## SkinsRestorer 15.12.6

[Descarga exacta del JAR](https://cdn.modrinth.com/data/TsLS8Py5/versions/ziIzW16f/SkinsRestorer.jar); SHA-1 `a995f863b5eb91338ddd56dc1c22c9f27b69b4ef`. El JAR de terceros queda solo en `.local/`, fuera del repo publico.
[Version oficial y compatibilidad Paper 26.1.2](https://modrinth.com/plugin/skinsrestorer/version/ziIzW16f).
Conservar toda la carpeta plugins/SkinsRestorer, skins guardadas y base de datos; respaldarla antes del primer arranque. No cambiar online-mode=false, AuthMe, /premium ni las configuraciones TAB/nonchat.
Integrar estas claves en plugins/SkinsRestorer/config.yml existente (no reemplazarlo completo):

```yaml
advanced:
  disableOnJoinSkins: true
  enablePaperJoinListener: false
  playerHeadChatObjects: false
server:
  resourcePackFix: false
  proxyMode:
    detection: DISABLED
login:
  noSkinIfLoginCanceled: true
```

AstralDecor aplica `sr applyskin <jugador>` una vez despues de que AuthMe confirme autenticacion y otra vez si termina de cargar el pack. Conserva la seleccion guardada de SkinsRestorer; sin seleccion usa la skin de la cuenta. No cambia prefijos ni formato del chat.
Si AstralDecor/config.yml existe: el JAR integra automaticamente cosmetics conservando npc-models/npc-skills/hidden-npcs. Mantener `skins-after-login: true` (valor por defecto).
Antes del primer arranque con jugadores, editar las claves anteriores con el servidor apagado. Para generar una config nueva, hacer un arranque de mantenimiento sin jugadores y volver a apagar.

Permisos de LuckPerms, consola sin / (no dar skinsrestorer.player ni comodines):

```text
lp group default permission set skinsrestorer.command true
lp group default permission set skinsrestorer.command.set true
lp group default permission set skinsrestorer.command.clear true
lp group default permission set skinsrestorer.command.set.other false
lp group default permission set skinsrestorer.command.clear.other false
lp group default permission set skinsrestorer.admin false
lp group default permission set skinsrestorer.admincommand false
```

Revisar permisos heredados con `lp user <jugador> permission check skinsrestorer.command.set.other`; debe ser false para un usuario normal. Probar /skin <nombre>, /skin set <nombre>, /skin clear; intentar cambiar otro jugador debe denegarse. No agregar skin/sr a allowedCommands de AuthMe antes del login.
[Comandos y permisos oficiales](https://skinsrestorer.net/docs/configuration/commands-permissions), [configuracion de login](https://skinsrestorer.net/docs/reference/server).

## Instalacion y consola

1. Medir memoria ANTES con `spark healthreport` y `spark heapsummary` en el servidor activo, tras calentamiento y con la misma cantidad de jugadores. Guardar heap usado, Metaspace y hora solo en el registro privado.
2. Esperar sala vacia, respaldar archivos/configs afectados y server.properties; apagar. Reemplazar los dos JAR y YAML de la tabla. No copiar plugins de prueba ni configs del Paper local.
3. Integrar cosmeticos_sombreros y cosmeticos_alas en gui_menus de plugins/DeluxeMenus/config.yml conservando las entradas existentes; referencia: build/menus/DeluxeMenus/config-gui_menus.yml.
4. Cambiar solo la descripcion del holograma de cosmeticos a Titulos, sombreros y alas (linea exacta abajo); no ejecutar todo build/lobby/comandos.txt. Publicar el pack FINAL en R2 y verificar SHA-1.
5. Encender y revisar Done, AstralDecor 1.3.0, SkinsRestorer 15.12.6 y ausencia de errores. Un reinicio es obligatorio por los JAR; no usar /reload. El arranque carga los YAML.
6. Para ajustes de YAML posteriores: `dm reload`, `crates reload`, `sr reload`. Repetir medicion spark tras el mismo calentamiento/jugadores; no inferir consumo comparando dos servidores distintos.
7. No sustituir mundos ni usar Worlds > Upload en world. Esta tarea no necesita datapack ni copiar mundos.

Comando de holograma:

```text
execute in minecraft:lobby positioned 208.5 102.55 197.5 run minecraft:kill @e[type=minecraft:text_display,tag=astral_holo,distance=..1]
execute in minecraft:lobby run summon minecraft:text_display 208.5 102.55 197.5 {Tags:["astral_holo"],billboard:"center",shadow:1b,background:1073741824,line_width:220,text:{"text": "", "extra": [{"text": "\u2726 Gacha de Cosmeticos \u2726", "color": "#FF7BD5", "bold": true}, {"text": "\nTitulos, sombreros y alas", "color": "gray"}, {"text": "\n500$ por tirada", "color": "gold"}, {"text": "\nEpico garantizado cada ", "color": "white"}, {"text": "20 tiradas", "color": "#FF7BD5", "bold": true}, {"text": "\nClic: tirar  -  Shift+clic: premios", "color": "dark_gray"}]}}
```

## Catalogo y comportamiento

| Tipo | Premio | Rareza |
|---|---|---|
| sombrero | Cabeza de Frankenstein | epic |
| sombrero | Sombrero de Bruja | epic |
| sombrero | Cuernos de Diablo | epic |
| sombrero | Gorro de Armero | common |
| sombrero | Gorro de Carnicero | common |
| sombrero | Gorro de Cartografo | common |
| sombrero | Gorro de Clerigo | rare |
| sombrero | Gorro de Desierto | common |
| sombrero | Gorro de Granjero | common |
| sombrero | Gorro de Pescador | common |
| sombrero | Gorro de Flechero | common |
| sombrero | Gorro de Bibliotecario | rare |
| sombrero | Gorro de Sabana | common |
| sombrero | Gorro de Pastor | common |
| sombrero | Gorro de Nieve | rare |
| sombrero | Gorro de Pantano | rare |
| sombrero | Gorro de Herrero | common |
| sombrero | Capucha de Ilusionista | epic |
| sombrero | Capucha de Vindicador | epic |
| sombrero | Sombrero de Carnivora | epic |
| alas | Alas de Carnivora | epic |
| alas | Alas de Asura | legendary |

19 sombreros de los dos ZIP nuevos y el sombrero de Carnivora existente. Asura aporta alas; no se encontraron otro sombrero, capa o aura para sumar. Armas, herramientas, armaduras y escudo de esos sets siguen fuera de esta gacha.
Permisos permanentes astral.cosmetico.<sombrero|alas>.<clave>; equipar/sacar desde /cosmeticos, sin ocupar inventario ni dar proteccion/estadisticas/vuelo. Sombreros visibles solo sin casco; el display se oculta a su propio portador para no tapar la primera persona. Ver ajuste visual desde otro jugador.
Seleccion en PDC del jugador: conserva reconexion/muerte. Los displays no son items ni drops y se eliminan al morir/salir. No se toca AxGraves. Alas seleccionadas dejan libres ambas manos; se conserva el soporte anterior de alas fisicas en segunda mano.
Los repetidos conservan el comportamiento de titulos: reotorgan el mismo permiso, sin compensacion. Totales de rareza sin cambiar; cada categoria comparte su peso entre mas premios, por lo que bajan probabilidades individuales. La gacha sigue dando titulos y conserva su garantia.
Los sombreros de aldeanos usan astral_cosmeticos:; no se reemplazan texturas vanilla de aldeanos, illagers ni NPC. El pack publico contiene reservas vanilla.

## Verificaciones y pendientes

Resultados reproducibles y limites se documentan en docs/SERVIDOR.md, seccion Cosmeticos y SkinsRestorer preparados. No se ejecutaron acciones en remoto ni se subio a R2.
Memoria spark ANTES/DESPUES en Empower: pendiente; no hay medicion remota ni cifra atribuible al plugin. Completar los pasos 1 y 6 al instalar.
Pendiente con cliente real: tirar gacha normal/garantia; desbloquear, equipar y quitar; ver cabeza e inventario y desde segundo jugador; reconectar; morir con AxGraves y verificar sin drops/duplicados; probar premium/no premium tras AuthMe y TAB/nonchat. La simulacion NMS no certifica el render del cliente ni integraciones remotas.
