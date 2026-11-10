# Panel TAB, BetterHud y Duels

## Tanda 1 preparada (10/11/2026), sin desplegar

El panel general vuelve a TAB en todos los mundos; Minas Astrales conserva su tablero. Filas: Vida, Defensa (armadura vanilla, equivalente a `[armor]`), Poder, Oro, lugar segun `sidebar.world_labels()`, Conectados, Rango, Diarias, Historia, Monstruos. `/sb` controla TAB y recuerda la preferencia. BetterHud queda instalado con `default-hud: []`; retirar `astral_panel` de sesiones existentes (el Skript lo retira al entrar).

Generadores: `lobby.py` (filas y condiciones TAB), `betterhud.py` (config apagada y `/sb`), `tanda1_entrega.py` (previas y despliegue). Vista: `build/previews/panel-tab.png`; lineas con colores: `build/deploy/panel-tab-lineas.txt`. Instrucciones vigentes: `build/deploy/tanda1.md`. Conservar pack BetterHud y shader combinado con Stellarity; su retirada requiere otra validacion. La seccion siguiente registra la instalacion anterior, no debe repetirse para esta tanda.

## Historial: panel dibujado del 08/11

## Panel de la derecha

El panel lateral de TAB se reemplazó por un panel **dibujado** con BetterHud 2.0.0
(toxicity188, el mismo autor de BetterModel), estilo "tarjeta de stats" con marco, gema
y los colores Astral (azul → violeta). Vista previa: `build/previews/panel-betterhud.png`.

| Sección | Filas | De dónde sale |
|---|---|---|
| Jugador | Vida, Defensa, Poder, Oro | `[health]/[max_health]`, `[armor]`, `%auraskills_power%`, `%vault_eco_balance_formatted%` |
| Mundo | Lugar, Conectados | nombre de `sidebar.world_labels()` según el mundo; `%server_online%/%server_max_players%` |
| Progreso | Rango, Diarias, Historia, Monstruos | rango por poder (mismos umbrales que TAB); `aq.done0..2`; `aq.state`; `%statistic_mob_kills%` |

- `/sb` lo apaga o lo prende y se acuerda (Skript `astral_panel.sk`, variable `{astral::panel_off::<uuid>}`).
  También apaga/prende el panel de TAB de las minas.
- En **Minas Astrales** (`astral_minas`) el panel de BetterHud se oculta y queda el panel de TAB de las minas
  (regeneración, siguiente mina, costo). En el resto de los mundos TAB ya no muestra panel lateral.
  El tabulador (encabezado, pie, vida, nombres) sigue igual.
- Usa PlaceholderAPI con las expansiones que ya estaban: Player, Server, Statistic, Vault y ScoreboardObjectives.

### Dónde se cambia

Todo sale de `datapack-src/betterhud.py`: dibujo (marco, gema, título, íconos 9x9), filas, colores,
tamaño (`W`, `ROW`...), condiciones y el `/sb`. `python betterhud.py` genera:

- `build/plugins/BetterHud/` → `plugins/BetterHud/` del server (`assets/astral_panel.png`, `images/`, `texts/`,
  `layouts/`, `huds/` con `astral.yml`; `config-cambios.yml` dice qué claves tocar en `config.yml`).
- `build/gameplay/astral_panel.sk` → `plugins/Skript/scripts/`.
- `build/previews/panel-betterhud.png` (usa la letra de Minecraft sacada del jar a `.local/betterhud-jar/ascii.png`).

**Cualquier cambio en esos archivos cambia los glifos del pack**: hay que rearmar `pack-source/betterhud`
(abajo), `python build_pack.py pack-source`, push y actualizar el sha1. Si el server y el pack no coinciden,
el panel sale con letras corridas o cuadrados.

### Trampas de BetterHud

- En los textos `/` escapa al carácter siguiente: una barra se escribe `//` (el generador lo hace solo).
- Un error de YAML en un archivo hace que no cargue **nada** de ese archivo (y el hud dice "this layout doesn't exist").
- La letra usa `merge-default-bitmap` + `use-unifont: true`. Sin unifont BetterHud pide la librería `freetype`
  y el Java de prueba no la tiene ("no freetype in system library path"). Por eso el pack suma ~5,5 MB.
- BetterHud dibuja con la **barra de jefe amarilla** y la vuelve invisible: ningún jefe puede usar `YELLOW`
  (la Momia/Faraón Ancestral pasó a `RED`).
- Su shader de texto (`rendertype_text.vsh`, ubica el panel en la pantalla) choca con el de Stellarity
  (nombres con colores animados). `build_pack.py` los junta en uno en `overlay_assets_26_1`. Si se actualiza
  BetterHud o Stellarity, revisar que siga armando ("cambio el shader de BetterHud" corta el armado).
- Las posiciones del hud usan solo 0/50/100 (`x: 100, y: 50` = borde derecho, al medio) para que no se corra
  con la escala de la GUI.
- **Primera versión (08/11) salió rota en el juego:** letras al doble de tamaño y fondo corrido medio ancho a la
  izquierda. Causas: la letra de BetterHud mide 16 px (los textos llevan `scale: 0.5`) y las imágenes se
  **centran** en su `x` (el fondo va en `x: W/2`). Además recorta las filas vacías de arriba de una imagen
  (la punta de la gema toca la fila 0 para que no corra todo 1 px).
- **Medir sin entrar al juego:** `tools/betterhud_paquete.cjs <salida.bin>` (bot con minecraft-protocol, variable
  `MC_PROTOCOL` con la ruta del paquete) guarda el título que manda BetterHud y
  `python tools/betterhud_medir.py <salida.bin> plugins/BetterHud/build` dice en qué x empieza y termina cada
  texto respecto del fondo. Con el arreglo: etiquetas en 21, valores terminan en 144, igual que el diseño.
  La altura de cada fila sale del `ascent` de `build/assets/betterhud/font/hud_*.json` (`((-ascent) & 8191) - 4105`).

### Rearmar el pack de BetterHud

1. Paper 26.1.2 local en `.local/betterhud-test/` con `BetterHud-bukkit-2.0.0.jar`, PlaceholderAPI y Skript
   (Java 25 de prueba; ver GUIA sección 6).
2. Borrar los ejemplos de BetterHud (`huds/ layouts/ images/ popups/ texts/ compasses/`), copiar
   `build/plugins/BetterHud/*` y aplicar `config-cambios.yml` (`pack-type: folder`, `default-hud: astral_panel`).
3. Arrancar y apagar. Copiar `plugins/BetterHud/build/assets` y `build/betterhud_26_1` a
   `datapack-src/pack-source/betterhud/`.
4. `python build_pack.py pack-source`. Pruebas: `python -m unittest test_betterhud`.

Prueba con jugador: un bot (`.local/betterhud-test/bot.cjs`, minecraft-protocol) entra y muestra los textos
que manda BetterHud. Se comprobó: nombre del lugar (Supervivencia → El Nether al pasar), vida en vivo,
rango, barras `/`, y que `hud hud remove/add` lo saca y lo vuelve a poner. **No se pudo ver con un cliente
real** (posición, tamaño y que no tape nada): eso queda para el primer ingreso al server.

## Duels

Vuelve Duels Optimised (Realizedd, BuiltByBit, gratis; la versión tiene que decir 26.1). Se sacó en Aternos
por memoria; en Empower no hay ese límite. La config ya estaba lista en `datapack-src/plugin-presets/`
(`Duels--config.yml` config-version 18: sin apuestas ni pérdida de inventario, duelos de hasta 10 minutos;
`Duels--arenas.json` arena `Astral` en el mundo `arena`; `Duels--lobby.json` vuelve al lobby),
exportada con `node plugins_basicos.mjs` a `build/plugins-basicos/Duels/`.

- Jugadores: `/duel <jugador>` (desafía), `/duel accept <jugador>`, `/duel deny <jugador>`.
- Admin: `/duels` (ayuda), `/duels arena list`, `/duels reload`.
- El jar se baja de BuiltByBit con cuenta (lo baja el dueño). En el server quedaron los datos viejos en
  `plugins/Duels/`; si `arenas.json` está vacío, subir los de `build/plugins-basicos/Duels/`.

## Despliegue historico del 08/11 (reemplazado por tanda1.md)

1. Subir `BetterHud-bukkit-2.0.0.jar` (Hangar, sha256 `4ff7892b…3307b`) y el jar de Duels a `plugins/`.
   Reiniciar una vez para que BetterHud cree su carpeta.
2. `plugins/BetterHud/`: borrar los `.yml` de ejemplo de `huds/ layouts/ images/ popups/ texts/ compasses/`
   (incluido `huds/-All file prefixed...yml`), subir `assets/astral_panel.png` y los cuatro `astral.yml`,
   y en `config.yml` cambiar las claves de `config-cambios.yml`.
3. `plugins/Skript/scripts/astral_panel.sk`.
4. TAB: reemplazar la sección `scoreboard:` de `plugins/TAB/config.yml` por la de
   `build/lobby/TAB/secciones-config.yml` (solo queda el panel de minas; el comando pasa a `/sbtab`).
5. MythicMobs: `build/mythicmobs/mobs/astral.yml`, `tumba.yml`, `santuario.yml` (barra roja).
6. `server.properties`: `resource-pack` por commit y `resource-pack-sha1` nuevo.
7. Reiniciar. Comprobar en consola que BetterHud no muestre `[!]` y que su
   `plugins/BetterHud/build/assets/betterhud/font/` tenga los mismos archivos que `pack-source/betterhud`.
8. Entrar y mirar el panel; `/sb` dos veces; ir a las minas; `/duel` entre dos cuentas.

Para volver atrás: `default-hud: []` en BetterHud (`hud reload`) y restaurar la sección `scoreboard:` anterior
de TAB (está en el historial de `build/lobby/TAB/secciones-config.yml`), `tab reload`.
