# Interfaces de Portales y Minas Astrales

`datapack-src/travel_ui.py` dibuja el arte original con Pillow, sin imágenes
generadas por IA ni referencias de terceros: obsidiana violeta, estrellas y
umbrales rojo/marfil para Portales; vigas, remaches, rieles y faroles para Minas.
Los botones ocupan una sola casilla (16 px). Los marcos usan títulos de fuente
con avance horizontal neto cero, glifos exclusivos U+E900–U+E911 y bitmaps de
224 × 56 y 224 × 170/224 px. No reemplazan el inventario ni el HUD global.

Portales conserva el identificador `portales`, el Guardián y `/umbrales`.
Casillas: 10 Nether, 12 End, 14 Parkour, 16 Arenas, 22 lobby, 26 cerrar.
Parkour/Arenas usan la acción nativa `openguimenu` de DeluxeMenus; los viajes
cierran y esperan tres ticks para evitar el cierre pendiente de DeluxeMenus.

Minas mantiene sus 20 destinos, filas por tier y todas las condiciones de
compra y venta. Las cabeceras 9/18/27 muestran I/II/III; 4 muestra oro,
45 rango y ayuda, 49 vuelve al lobby y 53 cierra. Las casillas de las minas
siguen saliendo de `minas.slot()`, con el mismo mapa `-am.dest` del manejador.
Venta conserva 13 para vender y 22 para cerrar. Oro, requisitos, precios,
teletransportes y exclusión de objetos personalizados no cambiaron.

Se incluyen, con autorización del dueño, los cambios locales previos de
`minas.py`, `minas.sk`, su salida y `docs/MINAS.md`: temporizador de regeneración,
barra de bloques y cantidad restante. La salida TAB generada coincide con la
ya publicada: no se agregaron cambios ajenos a esa configuración.

## Regeneración y verificaciones

Desde `datapack-src/`:

```text
python portales.py
python minas.py
python travel_ui.py
python build_pack.py pack-source
python -m unittest test_travel_ui test_portales_mapas test_minijuegos test_adventure_ui test_bazar test_market_ui test_gacha_ui test_cosmeticos_ui test_mascotas_ui
python verify.py
```

Vistas previas: `build/Interfaces-preview/portales.png`, `minas.png` y
`minas-venta.png`. Son composiciones del marco y los iconos; las vetas de la
maqueta son representaciones originales, mientras el juego usa los minerales
vanilla y barreras según el rango. Los importes y requisitos aparecen en el lore
real, al pasar el cursor. La maqueta muestra todas las minas para comparar tiers.

Validado: 42 pruebas, YAML, acciones, destinos sin superposición, salidas
regeneradas, bitmaps, avances de fuente y ausencia de colisiones de glifos en el
pack final. `verify.py` valida JSON y referencias de datapack/arte existentes.
Paper 26.1.2 + Skript 2.17.1 cargó y recargó `astral_minas.sk` sin errores,
sin skript-reflect. Los avisos de objetivos scoreboard ya existentes al recargar
son esperables. Falta la prueba visual e interacción con jugador en Minecraft.

## Despliegue pendiente en Aternos

No se modificó Aternos. Actualizar desde el commit de esta tarea, manteniendo
los archivos del servidor ajenos a ella.

| Archivo local | Destino / uso |
|---|---|
| `build/menus/DeluxeMenus/gui_menus/portales.yml` | Editor Files: `plugins/DeluxeMenus/gui_menus/portales.yml` |
| `build/minas/Skript/scripts/astral_minas.sk` | Editor Files: `plugins/Skript/scripts/astral_minas.sk` |
| `build/AstralRPG-Textures.zip` | Descarga de resource pack por URL raw fija al commit; no subir como mundo ni datapack |
| `build/lobby/TAB/secciones-config.yml` | Comprobar `plugins/TAB/config.yml`: combinar `scoreboard`, `conditions`, `placeholders` y `placeholder-output-replacements` si faltan los cambios previos del panel de minas. No reemplazar otras claves |

SHA-1 del pack: `e5e539e749de9833869f128cb76a37a77b74c9b5`.

1. Obtener el SHA completo del commit publicado de esta tarea. La URL será
   `https://raw.githubusercontent.com/Trainx12/AstralRPG/<SHA-completo>/build/AstralRPG-Textures.zip`.
   Descargar esa URL y verificar el SHA-1 anterior antes de usarla.
2. Apagar el servidor para esta instalación conjunta. Conservar las configs
   actuales y editar únicamente los destinos de la tabla. No se requiere
   cambiar DeluxeMenus/config.yml: el menú `portales` ya está registrado.
3. Guardar la URL fija en `server.properties` → `resource-pack`, y el SHA-1
   anterior en `resource-pack-sha1`. Este cambio requiere arranque/reinicio;
   `dm reload` no recarga server.properties.
4. Iniciar el servidor y comprobar consola: carga de DeluxeMenus, Skript y TAB.
   El arranque ya carga los archivos. Si las configs se editaron con el servidor
   encendido, los comandos de consola son `dm reload`,
   `skript reload astral_minas` y `tab reload` (solo si cambió TAB).
5. Reconectar un jugador y aceptar el pack nuevo. Revisar `/umbrales` y sus seis
   acciones, `/minas`, una mina abierta, la siguiente con requisitos cumplidos
   e incumplidos y una posterior bloqueada. Revisar venta con inventario vacío,
   minerales y equipo personalizado; comprobar oro antes/después y cierre.
   Comprobar temporizador/barra de TAB en una mina ocupada.

No hace falta regenerar pozos, ejecutar `/minasmoldes`, sustituir mundos ni
actualizar mapas, MythicMobs o el datapack. Nunca usar Worlds → Upload en `world`.
