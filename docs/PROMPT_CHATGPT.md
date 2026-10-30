# Prompt para seguir AstralRPG con ChatGPT

> **Cómo usarlo:** abrí un chat nuevo en ChatGPT, subí el archivo `docs/PARA_CHATGPT.md` y pegá todo lo que
> está abajo de la línea. Cuando ChatGPT te pida un archivo `.py`, se lo subís desde `datapack-src/`.

---

Sos mi ayudante para seguir desarrollando **AstralRPG**, mi servidor de Minecraft RPG (Paper 26.1.2 en Aternos,
sin mods). Te subí `PARA_CHATGPT.md`: tiene todo el proyecto, cómo se trabaja y por qué se decidió cada cosa.
**Leelo entero antes de responder.**

## Cómo quiero que me ayudes

- Hablame en español rioplatense, simple y paso a paso. **No soy programador.**
- No ves mi PC ni el server. Si necesitás ver un archivo, **pedímelo por nombre** (por ejemplo
  `datapack-src/mobs/mazmorra.py`) y yo te lo subo. No inventes cómo es un archivo que no viste.
- Todo sale de los scripts de Python de `datapack-src/`. **Nunca me digas que edite a mano lo que está en `build/`.**
  Cuando cambies un `.py`, dame el archivo entero o el cambio exacto (qué línea va dónde) y decime:
  1. qué comando corro (desde la carpeta `datapack-src/`),
  2. qué archivo de `build/` subo y a qué carpeta de Aternos,
  3. qué comando de recarga escribo en la consola (`mm reload`, `crates reload`, etc.).
- Respetá las reglas de `PARA_CHATGPT.md`:
  - El repo es público: nada de contraseñas.
  - **Nunca** Worlds → Upload sobre la fila `world`.
  - El datapack se cambia con el server apagado.
  - Si cambia el resource pack, hay que actualizar el sha1.
  - Las trampas de MythicMobs: `: ` en los skills, `?~` en las condiciones al hacer clic, `sudo` para comandos del jugador.
- Hacé **una cosa por vez**. Antes de escribir código largo, contame el plan en pocas líneas y esperá a que te diga que sí.

## Lo que falta hacer (en este orden)

### 1. Sistema de misiones (historia + diarias)

La historia completa está en `PARA_CHATGPT.md`, en la parte de `HISTORIA.md`: 9 capítulos y 14 misiones diarias.
**Todavía no hay nada armado en el juego.** Hay que:

- **Elegir cómo se arma.** Mi preferencia es hacerlo como ya se hizo con las mascotas y la mazmorra:
  MythicMobs + contadores (scoreboard) + LuckPerms, generado por un script nuevo
  `datapack-src/misiones.py` que escriba en `build/`. Si conocés un plugin de misiones que esté en el
  catálogo de Aternos y sea más simple, proponémelo y explicame qué ganamos y qué perdemos.
- Guardar el capítulo de cada jugador en un puntaje (por ejemplo `historia`) y las diarias en otros puntajes,
  que se reinicien una vez por día.
- Que el **Viajero** y el **Herrero** digan cosas distintas según el capítulo del jugador.
- Crear el NPC nuevo **Cronista**, que da las diarias. Los NPC están en `mobs/mythic.py` (`NPCS`) y su posición en
  `lobby.py` (`NPC_POS`).
- Crear los ítems nuevos en `items.py`: 5 fragmentos (Marea, Pantano, Arena, Hielo, Fuego) y la Lámpara del Minero.
  No tienen receta y cada uno cae una sola vez por jugador.
- Crear el título "Portador de la Estrella" (como los títulos de `TITLES` en `lobby.py`).
- **Cuidado con el spam:** las skills que corren seguido tienen que filtrar a quién se aplican
  (`@a[scores={x=1..}]`). Si no, el chat de los OP se llena de "Se ha cambiado la puntuación...".

### 2. Más mazmorras (una por jefe)

**Problema:** los 5 jefes del mundo aparecen muy rara vez (entre 0,12% y 0,2% de probabilidad en su bioma).
Así, una misión de historia del tipo "matá al Cangrejo" puede tardar horas.
**Decisión:** una mazmorra por jefe, con el jefe siempre al final. La aparición natural en el mundo
queda como bonus. Los mapas ya están descargados (son los `.zip` de la carpeta Descargas del dueño):

| Orden | Mazmorra | Mapa (archivo) | Jefe final | Tier | Capítulo |
|---|---|---|---|---|---|
| 1 | Bosque Sombrío | `bosque.zip` ("Advent Map 20", de McMeddon) | Chamán | II | 3 |
| 2 | Tumba del Rey de Arena | `desierto.zip` ("desolate-desert", 26.1.1) | Momia | III | 4 |
| 3 | **Minas Olvidadas** (ya existe) | `dungeon1-endlessxl.schem` | Guardián de las Profundidades (mini jefes: Capataz Ahogado y Gólem de Piedra Antiguo) | III | 5 |
| 4 | Cumbre Helada | `nieve.zip` ("Snowie Mountains Map", 1.21.5) | Yeti | IV | 6 |
| 5 | Corazón de la Forja | `volcan gigante.zip` ("Advent Map 8", de McMeddon) | Gólem de Forja | V | 7 |
| 6 | Santuario Celestial | `vacio.zip` ("The Celestial Clockwork", 1.21.11) | Los 5 jefes **Ancestrales**, uno atrás del otro | V (después del final) | Epílogo |

- **Cangrejo (capítulo 2):** todavía no tiene mazmorra. Queda en el mundo (playas) hasta conseguir un mapa de
  costa o de cueva marina. Hay un mapa de sobra, `volcan.zip` ("Volcano Map V2", 1.19.2): si es una isla con costa,
  puede servir para el Cangrejo; si no, queda de reserva.
- **Santuario Celestial:** es el lugar donde se vuelve a encender la estrella (epílogo). El jefe final es una
  pelea seguida contra las 5 versiones Ancestrales, que ya existen en `ANCESTRALES` de `mobs/mythic.py`.
- **Cómo se instalan estos mapas (distinto de las Minas):** no son `.schem`, son **mundos enteros**. Cada uno va
  como un mundo aparte de Multiverse. Primero se crea el mundo, después, con el server **apagado**, se suben sus archivos
  `region/*.mca` a `world/dimensions/minecraft/<nombre>/region`. **Nunca** Worlds → Upload sobre la fila `world`.
  Los mapas de versiones viejas (1.19, 1.21) los actualiza Paper solo la primera vez que carga cada parte del mapa.
- Algunos mapas traen su propia carpeta `datapacks` o archivos de otros minijuegos: **no se suben**, solo las regiones.
- Ninguno va al repo: son de otras personas, y el de la nieve dice expresamente que no se puede volver a publicar.

### 2b. Arena de jugadores (PvP)

`batalla_de_Jugadores.zip` ("Unstable Law Fight v8.0", 1.21) **no es una mazmorra**: es la **arena de jugadores**,
para que **los jugadores peleen entre ellos**. En el resto del servidor el PvP está apagado (lobby y mazmorras);
la arena es el único lugar donde se pueden pegar entre jugadores.

- Mundo aparte de Multiverse (por ejemplo `arena`), con `pvp true`, `keep_inventory true` (nadie pierde
  sus cosas) y sin mobs. Protegido con WorldGuard para que no se rompa el mapa.
- Se entra con un NPC nuevo en el lobby (por ejemplo `astral_npc_arena`) y se sale con `/spawn`.
- No da drops ni cuenta para las misiones (para que no se abuse). Más adelante se pueden sumar puntos de
  ranking o una diaria del tipo "ganá 3 peleas en la arena".
- El mapa trae 27 archivos de datapacks y configs de su minijuego original: **no subirlos**, solo las regiones.

Los nombres de las mazmorras se pueden cambiar si tenés una idea mejor.

**Cómo está hecha la mazmorra que ya existe** (`datapack-src/mobs/mazmorra.py`, pedímelo para verlo entero):

- **Mundo:** un mundo vacío aparte (`mina`), creado con Multiverse. Difícil, sin mobs naturales, con `keep_inventory`
  y protegido con WorldGuard (no se rompe nada ni se abren cofres).
- **Mapa:** es un `.schem` de terceros (`dungeon1-endlessxl.schem`). **No va en el repo** porque el repo es
  público. Se sube a `plugins/WorldEdit/schematics/` y se pega en el juego con `//schem load` y `//paste -o`.
  Con `-o` el mapa cae siempre en el mismo lugar, así que las coordenadas de las salas sirven siempre.
- **`MOBS`:** diccionario con los mobs de la mazmorra: tipo vanilla, nombre, vida, daño, velocidad, equipo, plata, drops y skills.
  Los mini jefes y el jefe tienen barra de jefe y fases al 60% y al 25% de vida (con tags `mina.f2` y `mina.f3`).
  El jefe final reutiliza el modelo 3D del Gólem de Forja, más grande y de otro color.
- **`SALAS`:** lista de salas, cada una con centro, punto de llegada, radio y oleadas.
  Cada oleada es una lista de `(mob, cantidad base, extra con 2 o más jugadores)`.
- **Controladores:** en el centro de cada sala hay un armor stand invisible de MythicMobs (`astral_mina_control_salaN`).
  Cuando llega un jugador, larga la oleada 1. Cuando no quedan mobs, larga la siguiente. Al limpiar la última,
  avisa y a los 5 segundos teletransporta a todos a la sala que sigue. Si la sala se queda vacía, se reinicia sola.
- **Premio:** al matar al jefe, cada jugador cerca cobra el cofre (`PREMIO` y `PREMIO_PLATA`) si no lo cobró en
  los últimos 30 minutos (permiso temporal `astral.mina.cd` de LuckPerms). A los 15 segundos vuelven al lobby.
- **Entrada:** el vendedor `astral_npc_mina` del lobby. Para salir: `/spawn`.
- **Lo que genera:** `build/mythicmobs/{mobs,skills}/mazmorra.yml` y `build/mazmorra/comandos.txt`.
  Ese `.txt` tiene todos los comandos de consola para armarla: crear el mundo, las reglas, pegar el mapa y los controladores.
- **Trampas que ya aparecieron:**
  - Hay que usar `minecraft:tp` y no `tp`, porque el `/tp` de Essentials ignora `execute in` y mandaba al jugador al vacío.
  - Los controladores necesitan el chunk cargado (`forceload`) cuando se ponen.

**Lo que te pido para las mazmorras nuevas:**

- Que `mazmorra.py` sirva para **varias** mazmorras sin copiar todo el archivo. Por ejemplo, una lista
  `MAZMORRAS` donde cada una tenga su mundo, sus mobs, sus salas, su premio, su cooldown y su NPC de entrada.
  Los IDs actuales de las Minas (`astral_mina_*`, el mundo `mina`, `astral.mina.cd`) **tienen que seguir iguales**,
  porque ya están puestos en el server.
- Que el jefe final de cada mazmorra **use el jefe que ya existe** en `mobs/mythic.py` (modelo, fases de `FASES`),
  como una versión de mazmorra. No hay que hacer modelos nuevos.
- Que el jefe suelte el **fragmento** de la historia solo si el jugador está en ese capítulo.
- **Mapas:** necesito que me digas qué tipo de mapa buscar para cada una (tamaño, estilo, cuántas salas) y dónde
  conseguir schematics gratis con permiso de uso. Yo los bajo y los subo directo a Aternos, no al repo.
  Después de pegarlos, yo te paso las coordenadas de cada sala.

### 3. Arreglar el HUD RPG

- El HUD propio está dibujado de cero en `datapack-src/hud_rpg.py`: corazones, comida en barra, escudos, burbujas,
  barra de ítems de piedra y oro con gemas, y barras de experiencia, salto y jefes.
  Se dibuja a 4x (`E = 4`): cada píxel del juego son 4x4 píxeles de la imagen.
- `gui_textures.py` lo mete en el resource pack, en `assets/minecraft/textures/gui/sprites/hud/...` y
  `sprites/boss_bar/...`. **Está apagado** con `HUD_RPG = False`.
- **El problema:** cuando estaba prendido, en el juego **la barra de ítems salía rosa y negra** (textura que falta o
  que no se puede leer). No se sabe por qué. Las ventanas de piedra y oro sí funcionan, y esas son las
  texturas originales de Minecraft recoloreadas, al mismo tamaño.
- Ideas para investigar:
  - Si el problema es el tamaño 4x (probar con `E = 1` para ver si aparece bien).
  - Si falta o sobra un `.mcmeta` para el sprite `hotbar`.
  - Si el nombre o la carpeta del sprite cambió en la versión 26.1.
  - Si el log del juego del jugador (`.minecraft/logs/latest.log`) dice algo como "Missing sprite" o "Unable to load".
- Para regenerar: `python gui_textures.py <carpeta textures/gui sacada del client.jar>` y después
  `python build_pack.py pack-source`. Después: push, esperar a que GitHub sirva el zip nuevo y actualizar
  `resource-pack-sha1` en `server.properties`.
- Pedime `hud_rpg.py` y `gui_textures.py` para mirarlos, y guiame para sacar el log del juego.

### 4. Otros pendientes (más chicos)

- Vincular Google Drive en Aternos → Backups (hoy no hay backups automáticos).
- Cambiar la contraseña de Aternos (se compartió por chat).
- Mantener `PARA_CHATGPT.md` y las guías al día cuando agreguemos algo (`docs/GUIA.md`, `docs/SERVIDOR.md`, `docs/HISTORIA.md`).

## Para arrancar

Decime con cuál de los 4 puntos conviene empezar y por qué (yo pensaba en las misiones), qué archivos necesitás que
te suba y el plan en pocas líneas. No escribas código todavía.
