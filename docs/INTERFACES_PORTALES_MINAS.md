# Interfaces de Portales, Minas, Arenas y Venta

## Implementacion v2: familia de servicios

ImageGen integrado funciono: genero cuatro marcos originales con exterior
transparente de 1122x1402 y dos atlas de tarjetas de 2048x683.
No se dibujaron marcos ni escenas con Pillow. Pillow recorta, reduce con NEAREST
y compone el panel, las letras, los botones y los iconos de estado.

`services_ui.ornament()` centraliza los nueve cortes del marco y es usado por
`services_ui.frame()` y el adaptador `travel_ui.py`. Este ultimo reutiliza tambien
`button`, `banner` y `card`, los colores crema y la fuente pixel del proyecto.
Las escenas antiguas dibujadas en `travel_ui.py` se retiraron. Los iconos chicos
y los 60 modelos de minerales por estado siguen siendo composiciones deterministas.
Los assets de servicios conservan exactamente los mismos bytes que en HEAD.
Las vistas previas de Herrero/Bazar/Gachas conservan sus hashes iniciales.

Originales entregables en `datapack-src/pack-source/ref/`:

- `portales-frame.png`, `minas-frame.png`, `arenas-frame.png`, `venta_minerales-frame.png`.
- `portales-cards.png`: Nether, End, Parkour y Arenas, de izquierda a derecha.
- `arenas-cards.png`: Coliseo, Ruinas, Vacio y Volcan, de izquierda a derecha.

El concepto del dueno se inspecciono y sus cuatro ventanas se recortaron como
referencia privada para ImageGen. Los recortes quedan en `.local/coordination/`;
no son archivos para publicar ni dependencias del pack. La lamina solicitada
incluye visualmente esos recortes junto a las nuevas ventanas y los servicios.

### Prompts usados en ImageGen

En todas las llamadas de marcos se adjunto el recorte correspondiente del concepto,
con `transparent_background=true`. Instruccion comun: unico marco frontal pixel art,
4:5, legible a 224x280, mismos materiales y adornos del concepto; cartel VACIO,
centro liso VACIO, borde estrecho; sin letras, numeros, botones, tarjetas, casillas,
inventario ni marcas; exterior realmente transparente. Centro aproximadamente
x13%-87%, y25%-92% (Portales y20%-92%).

- Portales: obsidiana y piedra violeta oscura; columnas con capiteles dorados,
  runas violetas luminosas, amatistas, portal espiral violeta central sobre el
  cartel, islitas con pasto en esquinas superiores y destellos de cuatro puntas;
  cartel con borde y flechas doradas, centro violeta muy oscuro. Misma familia
  ornamental del Arsenal Arcano.
- Minas: vigas de mina de madera con abrazaderas y remaches de hierro; faroles
  naranjas superiores, pico central sobre cartel vacio de piedra y madera;
  tunel pequeno solamente sobre el cartel; carbon, hierro, oro y diamante en
  esquinas inferiores, tramo de riel en la base; centro carbon. Familia Herrero.
- Arenas: columnas de piedra gris oscura de coliseo, almenas superiores,
  estandartes rojos con estrella dorada de cuatro puntas, espadas de plata
  cruzadas sobre laurel dorado, antorchas laterales; cartel de piedra vacio,
  centro carbon; misma familia de servicios de AstralRPG.
- Venta minerales: piedra oscura con bordes y abrazaderas de oro; minero de casco
  amarillo con lampara arriba a la izquierda; pico y carrito de minerales/monedas
  a la derecha; pepitas y gemas abajo, cartel dorado sin obstruir, centro marron
  oscuro; sin tira de conversion (se compone luego). Familia Herrero/Bazar.

Atlas Portales (referencia: recorte Portales; fondo opaco): exactamente cuatro
ilustraciones verticales iguales, en una sola fila sin espacios ni marcos,
proporcion total 3:1, sin texto. Nether: puerta de obsidiana, lava naranja y paisaje
rojo. End: isla palida, pilares negros y ojo verde flotante. Parkour: plataforma
flotante, botas y pluma cian brillante. PvP: espadas de plata con empunaduras de
oro sobre estandartes rojos y piedra de coliseo. Pixel art de siluetas claras para
reducir cada pintura a una tarjeta pequena.

Atlas Arenas (referencia: recorte Arenas; fondo opaco): cuatro escenas verticales
iguales en fila sin espacios, marcos ni texto, proporcion 3:1. Coliseo soleado con
arena, arcos apilados y banderas rojo/oro; ruinas con arco de piedra, musgo,
enredaderas, pilares, pasto y cielo azul; Vacio con isla violeta, pilares oscuros y
portal de anillo purpura en cielo nocturno; Volcan con basalto, corrientes de lava
y montana en erupcion. Pixel art de siluetas grandes, sin personajes ni marcas.

## Casillas y funcionalidad conservadas (indices desde cero)

- Portales: 6 filas, menu `portales`. Nether 9,10,18,19,27,28; End
  11,12,20,21,29,30; Parkour 13,14,22,23,31,32; Arenas 15,16,24,25,33,34.
  Cada tarjeta tiene seis items transparentes con la misma accion. Lobby 45-47;
  cerrar 51-53. Nether/End/Lobby usan `[close]` y `umbrales <destino><delay=3>`;
  Parkour/Arenas usan `[openguimenu]`. Guardian y `/umbrales` conservados.
- Arenas: 6 filas, menu `arenas`. `clasica`, `tft1`, `tft2`, `tft3` usan las mismas
  cuatro regiones, ilustradas como Coliseo, Ruinas, Vacio y Volcan. Tooltip:
  nombre tematico y nombre real del destino. Cada casilla usa `[close]` seguido de
  `[player] arenas <id><delay=3>`. Lobby 45-47; cerrar 51-53. Parkour no cambia.
- Minas: 6 filas, 20 destinos reales en 6/7/7; `minas.slot()` y `-am.dest` intactos:
  10-15, 19-25, 28-34. Saldo 4 (transparente, importe real en tooltip sobre banner
  TU ORO), placas I/II/III 9/18/27, ayuda 45, lobby 49, cerrar 53. Tres modelos por
  mina: `mine_<id>_open` verde, `_next` dorado, `_locked` atenuado con candado.
  Tooltip con rango, bloques, costo y progreso reales. Sin cambios de precios,
  requisitos, tiempo, rangos ni teletransportes.
- Venta: 5 filas; vender 28-34, siete casillas con la misma accion; cerrar 35.
  Fondo con tira minerales > oro, RECIBIS, boton verde VENDER TODO y aviso de
  conservacion de objetos Astral. El importe real sigue en nombre/lore del boton;
  no se pinta una cifra ficticia. Se recalcula al vender. Calculo, exclusiones y
  pago conservados byte por byte respecto de HEAD.

Coordenadas de panel compartidas con servicios: 224x280 logicos, slot inicial
(31,57), separacion 18 px; franja Inventario gris, 4 filas reales del jugador.
Venta adelanta el inventario 18 px por tener cinco filas. Previews 672x840 NEAREST.
Fuente: dos columnas de mosaicos, maximo 224x256 px, avance horizontal neto cero;
U+E900-U+E93F reservados (56 usados), sin colisiones. No se sustituye HUD global.
Los iconos usan modelos pequenos; no hay modelos grandes nuevos sin declarar.

## Generacion y verificaciones

Desde `datapack-src/`, con Python, Pillow, NumPy y PyYAML:

```text
python portales.py
python minas.py
python minijuegos.py
python travel_ui.py --concept ../.local/coordination/concepto-interfaces.png
python build_pack.py pack-source
python -m unittest test_travel_ui test_portales_mapas test_minijuegos test_adventure_ui test_bazar test_market_ui test_gacha_ui test_cosmeticos_ui test_mascotas_ui
python verify.py
```

`--concept` es opcional y solo agrega la referencia privada a la comparacion;
el pack y las cuatro previews no dependen de ella. La comparacion tiene cuatro
filas: concepto | nueva | Herrero | Bazar | Gacha RPG.

En esta maquina: `.local/python/cpython-3.13-windows-x86_64-none/python.exe` y
`PYTHONPATH=.local/interfaces-deps` desde la raiz (ajustar `../` desde datapack-src).

Verificaciones: generadores, 48 pruebas de contratos/acciones/YAML/estados,
backend de venta intacto, 36 huecos del inventario de cada menu, dimensiones y
transparencia de originales, reconstruccion de mosaicos, avances y glifos del ZIP.
`verify.py` valido JSON, referencias, sprites, servicios, misiones y mazmorras;
solo avisos de deprecacion de Pillow, sin `--client-jar`. Assets de servicios
identicos a HEAD y 26 PNG de Servicios-preview identicos al estado inicial.

Paper 26.1.2-74, Java 25, Skript 2.17.1, Vault 1.7.3 y Essentials 2.22.0:
carga sin errores de `astral_minas.sk` (50 estructuras) y recarga
`skript:skript reload astral_minas` confirmada por consola. Servidor aislado nuevo
en `.local/interfaces-v2-test`, solo 127.0.0.1:25579, sin copiar mundos previos ni
skript-reflect; apagado con `stop`, codigo 0 y guardado confirmado. El primer
intento en sandbox no pudo abrir el JAR cache por permisos de Java; la prueba
autorizada fuera del sandbox si completo carga y recarga. Los codigos ANSI de
consola se quitaron para validar la confirmacion. Logs y prueba quedan privados.

La validacion con jugador en Minecraft sigue pendiente: visual, clics, hover,
ventas con equipo personalizado y coexistencia con los plugins reales. Una
preview o carga del parser no sustituye esa prueba.

## Archivos de la tarea

Fuentes: `services_ui.py`, `travel_ui.py`, `minijuegos.py`, `minas.sk`,
`test_travel_ui.py`, los seis PNG de referencia anteriores y este documento.
`portales.py` conserva la implementacion previa y se regenera con el adaptador.

Salidas: `build/AstralRPG-Textures.zip`,
`build/menus/DeluxeMenus/gui_menus/{portales,arenas}.yml`,
`build/minas/Skript/scripts/astral_minas.sk`,
`build/Interfaces-preview/{portales,minas,arenas,minas-venta,comparacion}.png`.
No se edita `build/` a mano. Se conserva el trabajo previo ajeno a esta tarea.

## Despliegue pendiente en Aternos

Sin commit, push ni acceso al servidor en esta corrida. No hay URL nueva publicada.
Claude debe revisar y publicar antes de fijar el resource pack al SHA completo del
commit correspondiente. No usar `main` como URL mutable.

| Archivo local exacto | Destino exacto / uso |
|---|---|
| `build/menus/DeluxeMenus/gui_menus/portales.yml` | `plugins/DeluxeMenus/gui_menus/portales.yml` |
| `build/menus/DeluxeMenus/gui_menus/arenas.yml` | `plugins/DeluxeMenus/gui_menus/arenas.yml` |
| `build/minas/Skript/scripts/astral_minas.sk` | `plugins/Skript/scripts/astral_minas.sk` |
| `build/AstralRPG-Textures.zip` | URL raw fija al commit, configurada en `server.properties` |

SHA-1 del ZIP final: `705d17921151ce0aff3c6cf2a1ba366f809d328c`.

1. Publicar y comprobar descarga/SHA-1 de
   `https://raw.githubusercontent.com/Trainx12/AstralRPG/<SHA-completo>/build/AstralRPG-Textures.zip`.
2. Apagar Aternos para instalar la actualizacion conjunta. Reemplazar solo los
   tres archivos de plugins de la tabla, conservando las configs ajenas. Portales
   y Arenas ya estan registrados: no reemplazar `plugins/DeluxeMenus/config.yml`.
3. En `server.properties`, actualizar `resource-pack` con la URL fija y
   `resource-pack-sha1` con el hash anterior; conservar `require-resource-pack=true`.
4. Iniciar y revisar consola: Skript y DeluxeMenus deben cargar sin errores.
   El pack/server.properties requiere reinicio. Configs solas admiten `dm reload`
   y `skript:skript reload astral_minas`; no repetir si el arranque ya las cargo.
5. Reconectar al jugador, aceptar el pack, comprobar `/umbrales`, `/arenas`,
   `/minas` y Venta Rapida del minero. Probar todas las tarjetas, Lobby/Cerrar,
   abierta/siguiente/bloqueada, requisitos cumplidos e incumplidos, venta vacia,
   minerales y objetos Astral, saldo antes/despues, Esc, shift-clic, numeros y arrastre.

No actualizar datapack, TAB, MythicMobs ni mapas por esta tarea. No regenerar
pozos ni usar `/minasmoldes`. Nunca sustituir mundos ni Worlds > Upload en `world`.
