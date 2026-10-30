# AstralRPG: todo el contexto en un solo archivo (para ChatGPT u otra IA)

> **Para la IA que lee esto:** sos el ayudante de un servidor de Minecraft RPG llamado AstralRPG.
> El dueño habla español rioplatense y **no es programador**: respondé en español, simple, paso a paso
> y sin jerga. Este archivo tiene todo lo que se hizo, cómo está armado y **por qué** se decidió cada cosa.
> La parte 1 es el resumen y la parte 2 es la copia completa de las guías del repo.
>
> Escrito el 30/10/2026. Si algo de acá no coincide con los archivos del repo, valen los archivos.

---

# PARTE 1 — Resumen y decisiones

## 1. Qué es

- Servidor de **Minecraft Java 26.1.2** con progresión RPG, **sin mods**: se entra desde Minecraft normal.
- Hosting: **Aternos** (gratis), dirección `AstralRPG2.aternos.me`. Software: **Paper 26.1.2** (Java 25).
- Modo no premium (entran cuentas originales y no originales) con login de **AuthMe**.
- Repositorio **público** en GitHub: https://github.com/Trainx12/AstralRPG
- Arrancó el 27/10/2026. En 2 días se armó todo lo de abajo.

## 2. Qué tiene el juego hoy

| Sistema | Resumen |
|---|---|
| **Clases** | Berserker (skill Forja), Mago (Hechicería), Arquero (Arquería). 5 tiers de armadura y armas por clase; cada tier se fabrica con el anterior. Las armaduras tienen skins propias. |
| **Forja Astral** | Mesa de herrería + guía (menú) con botón *Forjar*. Saca los materiales del inventario y avisa todo lo que falta junto. |
| **Niveles** | Plugin AuraSkills. Las armas y armaduras piden nivel de skill. |
| **Materiales** | Esencia de Élite → Alma Corrupta → Chispa Astral (de menos a más raro). Se usan para talismanes, lanzas, mejoras y el tier más alto. |
| **Élites** | Cualquier mob puede salir élite (tiers I a V). La probabilidad sube con tu equipo y con los días del mundo. Los élites de MythicMobs tienen afijos (Vampírico, Explosivo, Blindado, Veloz, Invocador, Maldito). |
| **Criaturas 3D** | MythicMobs + BetterModel (modelos 3D sin mods). Fauna: mapache y pingüino. Hostiles: espantapájaros, abejorro, araña y cara voladora. |
| **Jefes** | Momia (desierto), Yeti (picos nevados), Gólem de Forja (Nether), Cangrejo (playas) y Chamán (pantano, de noche). Cambian de fase al 60% y al 25% de vida. Tienen versión **Ancestral**: un evento raro que se anuncia a todo el server. |
| **Monturas** | Chocobo/Ave Corredora, Grillo, Escarabajo, Lagarto, Gran Ave y Pterodáctilo. Se ensillan y se manejan con WASD. |
| **Mascotas** | 6 mascotas 3D que dan efectos y suben hasta el nivel 30 (Lobo, Cuervo, Gólem, Zorro, Dragoncito y Fénix). Comando `/mascotas`. |
| **Herramientas** | Taladros (9 niveles, área de hasta 4x4) y motosierras (5 niveles, hasta tirar el árbol entero). |
| **Herrero** | Mejora armas y armaduras de +1 a +10. Desde +5 puede fallar. |
| **Bonus de set** | Llevar 2 o 4 piezas de la misma clase da un extra. |
| **Lobby** | Isla flotante en un mundo aparte, protegida. Tiene Tienda, Venta rápida, Bazar, Subastas, Herrero, Viajero (te lleva al mundo), la entrada a la mazmorra y 3 gachas. |
| **Gachas** | Cofres 3D con ruleta tipo CS:GO (plugin CrazyCrates): Armas 1000$, Monturas 2500$ y Cosméticos 500$. Tiradas x1/x10/x25/x50 y garantía de Épico a las 50/40/20 tiradas. |
| **Economía** | EssentialsX + Vault. Se empieza con 250$. Matar da 15$ (hostil), 150$ (élite) y 750$ (jefe). Hay tienda, venta rápida, subastas (`/ah`) y órdenes (`/orders`). |
| **Mazmorra** | "Minas Olvidadas": 4 salas con oleadas, 2 mini jefes, un jefe final y un cofre de premio (se cobra cada 30 minutos). |
| **Panel TAB** | Panel lateral con vida, oro, poder, nivel, skills y bajas. Rangos: Novato → Aventurero → Veterano → Héroe → Leyenda. |
| **Menús** | Menús de cofre (DeluxeMenus): `/menu`, `/mascotas`, gachas y bazar. |
| **Interfaz** | Ventanas de piedra y oro en el resource pack. El HUD propio quedó **apagado** (ver decisiones). |
| **Historia** | **Escrita pero no armada en el juego.** Está en la Parte 2 → `HISTORIA.md`. |

## 3. Cómo se trabaja (muy importante)

1. **Todo sale de scripts de Python** en `datapack-src/`. Nunca se editan a mano los archivos de `build/`.
   Se cambia el `.py`, se corre, y se generan los archivos en `build/`.
2. Después: commit y push a GitHub (desde la PC del dueño, con Git).
3. Después se sube a Aternos:
   - **Datapack** (`build/AstralRPG-Items.zip`): con el server **apagado**, en Files → `world/datapacks` → Upload.
   - **Configs de plugins** (MythicMobs, CrazyCrates, TAB, DeluxeMenus...): Files → abrir el archivo → pegar el
     contenido nuevo → Save → en la consola, el reload del plugin (`mm reload`, `crates reload`, `tab reload`,
     `dm reload`, `papi reload`, `essentials reload`, `bettermodel reload`).
   - **Resource pack** (`build/AstralRPG-Textures.zip`): se sirve desde GitHub. Hay que hacer push, esperar
     a que GitHub muestre el nuevo y poner el **sha1 nuevo** en `server.properties` → `resource-pack-sha1`.

Comandos para generar (desde la carpeta `datapack-src/`):
```
python build.py                    # datapack (ítems, recetas, Forja, guía, élites)
python gui_textures.py <gui>       # ventanas piedra/oro + HUD -> pack-source/gui
python build_pack.py pack-source   # resource pack
python mobs/build_models.py        # modelos 3D (.bbmodel)
python mobs/mythic.py              # MythicMobs: criaturas, monturas, jefes, vendedores
python mobs/mazmorra.py            # Mazmorra Minas Olvidadas
python mobs/mascotas.py            # Mascotas
python lobby.py                    # gachas, cobro, panel TAB, comandos del lobby
python menus.py                    # menús de cofre (DeluxeMenus)
```

**Si sos ChatGPT:** no podés ver el repo ni el server. Pedile al dueño que te pegue o suba el `.py`
que haya que cambiar. Devolvé el archivo entero o el cambio exacto, y decile qué comando correr y qué subir.

## 4. Reglas que no se rompen

- **El repo es público.** Nunca poner contraseñas en archivos que se suben (van en `docs/CREDENCIALES.local.md`,
  que Git ignora). Tampoco subir mapas de otras personas.
- **NUNCA usar Worlds → Upload sobre la fila `world` en Aternos**: reemplaza el mundo entero.
  Así se perdió el primer mundo el 28/10/2026 y no había backup.
- Aternos **no deja reemplazar el datapack con el server prendido**.
- Si cambia el resource pack, **siempre** hay que actualizar el sha1.
- Si cambia un ítem que los jugadores ya tienen, subir `ITEM_VERSION` en `build.py` (los ítems viejos se actualizan solos).
- Commit y push solo cuando el dueño lo pide.

## 5. Por qué se decidió cada cosa

| Decisión | Por qué |
|---|---|
| Sin mods (datapack + resource pack + plugins) | Para que cualquiera entre con Minecraft normal, sin instalar nada. |
| Todo generado con Python | Si se rompe el server, se rearma igual desde el repo. Cambiar un número en un lugar actualiza todo. |
| Aternos | Es gratis. Contra: se apaga solo cuando no hay nadie y tiene límites para subir archivos. |
| Modo no premium + AuthMe | Para que entren amigos sin cuenta original. AuthMe evita que otro entre con tu nombre. |
| Paper 26.1.2 fijo (no actualizar) | Los plugins están probados en esa versión. El aviso "4 releases behind" se ignora. |
| AuraSkills con preset `legacy.zip` | La 2.4 no trae Forja ni Hechicería sin ese preset, y los ítems los piden. |
| BetterModel para las criaturas | Modelos 3D sin mods. Los modelos se arman con código en `mobs/creatures.py`. |
| Gachas con **CrazyCrates** (y no ExcellentCrates) | La 7.x de ExcellentCrates solo se configura dentro del juego y la 6.x no anda con el NightCore que necesita ExcellentEnchants. Primero se probó cobrar y sortear con MythicMobs puro, y después se pasó a CrazyCrates por la ruleta animada. |
| El vendedor de gacha cobra y después `crates forceopen` | CrazyCrates no cobra con plata de Vault directo; así MythicMobs cobra y CrazyCrates solo muestra la ruleta. |
| Tiradas múltiples = 1 ruleta + el resto juntos | Para no tener que mirar 50 ruletas. |
| Garantía (pity) 50/40/20 | Para que nadie se frustre: siempre llega un Épico. |
| Anuncios con `tellraw` y no `/broadcast` | El prefijo de Essentials mostraba un color roto. |
| `minecraft:tp`, `minecraft:kill`, `minecraft:trigger` | Essentials pisa `/tp` y `/kill`. Su `/tp` mandaba al jugador al vacío del lobby. |
| Bazar con EconomyShopGUI, CrazyAuctions y DonutOrders | Primero hubo puestos de alquiler con cofres (QuickShop) y se sacaron por complicados. EzAuction y RoyalBazaar, que eran los elegidos, no están en el catálogo de Aternos. |
| `log_admin_commands false` y `broadcast-console-to-ops=false` | Los OP recibían spam de "Se ha cambiado la puntuación..." por los comandos automáticos. |
| Mascotas: resetear los contadores solo de quien mató algo | Lo mismo: resetear a todos cada rato llenaba el chat de spam. |
| HUD propio apagado (`HUD_RPG = False`) | En el juego la barra de ítems salía rosa y negra (textura rota). Quedaron solo las ventanas de piedra y oro. |
| Vida de los jefes con Resistencia y no más vida | Minecraft corta la vida máxima en 1024. |
| Stellarity 5.4.2 | La 6.x crashea en 26.1.2. |
| Mazmorra con un mapa de terceros que no está en el repo | El repo es público y no se pueden publicar mapas ajenos. El `.schem` se sube directo a Aternos. |
| Arcos que disparan solos | Para que el Arquero sea divertido y esté parejo con las otras clases (ver BALANCE). |
| Mago con menos daño | Los hechizos pegaban demasiado: el bastón V hacía ~37 de daño por segundo. |

## 6. Trampas conocidas (ya nos costaron tiempo)

- **MythicMobs:** un skill con `: ` adentro rompe el YAML (usar comillas simples). Al hacer clic (`~onInteract`), las
  condiciones del jugador van con `?~` (ej. `?~hascurrency{a=1000}`). Para que un NPC ejecute un comando como el
  jugador: `command{c="sudo <trigger.name> <comando>"}`. La vida en porcentaje es `?healthpercent{p=<0.6}`.
- **CrazyCrates:** `crates preview` solo funciona como jugador (con `sudo`). `crates forceopen <caja> <jugador>` abre gratis.
- **Lobby:** WorldGuard bloquea los mobs. Para spawnear vendedores, poner `mob-spawning allow` un momento
  (está en `build/lobby/comandos.txt`).
- **`cookie_request` al entrar** = el server está apagado. Prenderlo desde el panel.
- **Spam en el chat de los OP:** en skills que corren seguido, filtrar a quién se aplica (`@a[scores={x=1..}]`).
- **Huevos de mascotas y monturas no andan en el lobby.** Se usan en el mundo.
- **Aternos:** en las carpetas de plugins no hay botón Upload (se usa *New file* y se pega el contenido); en la
  raíz no se pueden crear carpetas. Si al guardar avisa "syntax errors", el YAML está roto.
- **Un comando nuevo sale en rojo en el chat pero anda:** el jugador tiene que volver a entrar.

## 7. Historial (qué se hizo y cuándo)

**27/10/2026**
- Datapack de ítems y resource pack.
- Élites con dificultad progresiva, talismanes y lanzas.
- Kit de admin, guía con menús y forja desde el menú.
- Skins de las armaduras de las 3 clases y texturas libres (CC0).
- Criaturas 3D (fauna, hostiles, monturas, élites, jefes), taladros y motosierras.
- Lobby con gachas y monedas al matar. Las gachas pasaron de ExcellentCrates a MythicMobs.

**28/10/2026**
- Gachas con ruleta de CrazyCrates.
- Panel TAB y rangos.
- Jefes con fases, afijos de élites, garantía de las gachas, jefes ancestrales, bonus de set y Herrero +1..+10.
- Cofres 3D de las gachas con carteles flotantes y tiradas x1 a x50.
- Mazmorra Minas Olvidadas.
- Bazar, subastas y órdenes.
- Mascotas 3D.
- Menús de cofre.
- Interfaz de piedra y oro (el HUD propio quedó apagado).
- Arreglos de spam en el chat de los OP.
- **Se perdió el primer mundo** por usar Worlds → Upload.

**30/10/2026**
- Se escribió la historia y las misiones (`docs/HISTORIA.md`).
- Se escribió este archivo.

## 8. Qué sigue (pendiente)

1. **Elegir cómo se arman las misiones.** Hay dos caminos:
   - Un plugin de misiones (hay que ver cuáles hay en el catálogo de plugins de Aternos).
   - Armarlas con MythicMobs y contadores (scoreboard), como se hizo con las mascotas y la mazmorra.
     Así queda todo en el repo, generado con Python (por ejemplo, un `datapack-src/misiones.py` nuevo).
2. Crear los ítems nuevos de la historia: 5 fragmentos (Marea, Pantano, Arena, Hielo, Fuego) y la Lámpara del Minero,
   en `items.py`, sin receta. Caen solo la primera vez que el jugador mata a cada jefe.
3. NPC nuevo **Cronista** (tablón de misiones diarias) en `mobs/mythic.py` (`NPCS`) y su posición en `lobby.py` (`NPC_POS`).
4. Título de chat "Portador de la Estrella" (como los de `TITLES` en `lobby.py`).
5. Otros pendientes:
   - Arreglar el HUD propio (barra rosa/negra).
   - Vincular Google Drive en Aternos → Backups.
   - Cambiar la contraseña de Aternos (se compartió por chat).

## 9. Dónde está cada cosa (mapa corto)

```
AstralRPG/
├── CLAUDE.md, README.md, BALANCE.md
├── docs/  GUIA.md (cómo agregar cosas), SERVIDOR.md (admin), HISTORIA.md (historia y misiones),
│          PARA_CHATGPT.md (este archivo), CREDENCIALES.local.md (solo en la PC, no se sube)
├── datapack-src/   items.py, tools.py, textures.py, build.py, build_pack.py, lobby.py, menus.py,
│                   gui_textures.py, hud_rpg.py, gen_textures.py, *_skins.py, pack-source/
│   └── mobs/       creatures.py (modelos), build_models.py, mythic.py (mobs, jefes, NPC, gachas),
│                   mazmorra.py, mascotas.py
└── build/          todo lo generado (no editar a mano): zips, models, mythicmobs, lobby, mazmorra, mascotas
```

---

# PARTE 2 — Copia completa de las guías del repo

Abajo está pegado, tal cual, el contenido de `README.md`, `BALANCE.md`, `docs/GUIA.md`, `docs/SERVIDOR.md`
y `docs/HISTORIA.md` (la copia es del 30/10/2026).



---

<!-- ==================== README.md ==================== -->

# [Archivo: README.md]

## AstralRPG

Servidor de Minecraft 26.1.2 (Paper) con progresión RPG, sin mods: se puede entrar desde vanilla.

**Administración del servidor (plugins, lobby, comandos, problemas conocidos): [docs/SERVIDOR.md](docs/SERVIDOR.md).**

**Dónde está cada cosa y cómo agregar cosas nuevas: [docs/GUIA.md](docs/GUIA.md).**

- `build/AstralRPG-Items.zip`: datapack (va en `world/datapacks`).
- `build/AstralRPG-Textures.zip`: resource pack que el servidor manda al entrar.
- `datapack-src/`: generadores. Para cambiar stats, recetas o drops se edita `items.py` (o `textures.py` para las texturas) y se corre:

```
python build.py
python build_pack.py pack-source
```

### Cómo se juega

- **Forja Astral**: poné una mesa de herrería, abrí la guía al lado (Esc → "Guía AstralRPG" o `/trigger astral.guia`) y apretá **Forjar**. Los materiales se sacan de tu inventario.
- La guía es un menú con todas las recetas, ítems y dónde conseguir cada material.
- Las armas y armaduras piden nivel de AuraSkills para usarse.
- **Lobby**: aparecés en la isla del lobby. Hay tienda, venta rápida, 3 gachas con ruleta y el Viajero que te lleva al mundo. `/spawn` vuelve al lobby, `/balance` muestra tu plata y `/sb` oculta o muestra el panel de stats.
- **Monturas** (Ave Corredora, Grillo, Escarabajo, Lagarto, Gran Ave, Pterodáctilo): clic derecho con una montura en la mano para ensillarla (se ve la silla puesta). Después, clic derecho para subirte: se maneja con WASD, espacio salta (o sube, en las voladoras) y shift para bajarte. Si muere, suelta la montura.


---

<!-- ==================== BALANCE.md ==================== -->

# [Archivo: BALANCE.md]

## Balance de AstralRPG

Valores de referencia (daño por segundo aproximado contra un mob sin armadura).

| Clase | Tier I | Tier III | Tier V |
|---|---|---|---|
| Berserker (espada + set) | ~10 | ~17 | ~27 (hasta ~38 con poca vida) |
| Mago (bastón + set) | ~4,4 a distancia | ~10 | ~20 a distancia |
| Arquero (arco + set) | ~8 | ~15 | ~30 (disparo automático cada 0,4 s) |
| Lanza (Combate) | ~9 | ~13 | ~19 + área + ejecución |

Cambios hechos al revisar:

- **Mago**: los hechizos pegaban demasiado (el bastón V hacía ~37 de daño por segundo). Ahora: daño 5/6/7/8,5/10 y recarga 1,25 s → 1 s.
- **Berserker V**: la armadura y la espada V multiplicaban la Furia entre sí (hasta x2,1). La armadura ahora tiene Furia I (+15% máx.) y la espada mantiene Furia II.
- **Arquero**: manteniendo click derecho el arco dispara solo, a máxima potencia, cada 0,9 / 0,75 / 0,6 / 0,5 / 0,4 s según el tier (vanilla: 1 s). El set de Arquero V lo baja un tick más. Multiplicadores: arco V x1,30, set V x1,25.

### Dificultad progresiva

Cada mob hostil nuevo puede volverse élite. La amenaza cerca de un jugador es:

`amenaza = mejor tier Astral que tiene equipado (0-5) + 1 cada 7 días de mundo (máx. +3)`

- Probabilidad de élite: 6% + 5% por punto de amenaza (6% al empezar, 46% en endgame).
- Tier del élite: 1 + azar(0..amenaza)/2, máximo 5.

| Tier | Nombre | Vida | Daño | Extra | Drops |
|---|---|---|---|---|---|
| I | Veterano | +40% | +15% | | Esencia de Élite 50% |
| II | Élite | +90% | +30% | | Esencia x1-2 |
| III | Campeón | +160% | +50% | inmune al fuego | Esencia x2, Alma Corrupta 35% |
| IV | Pesadilla | +260% | +75% | + Resistencia I | Alma x1-2, Esencia x2 |
| V | Astral | +400% | +110% | + Regeneración | Chispa Astral 60%, Alma x2, Esencia x3 |

Se suma a LevelledMobs, que ya sube el nivel de los mobs según la distancia al spawn.

Los materiales nuevos sirven para los **Talismanes** (mano secundaria: vida, daño, velocidad y armadura, 3 niveles) y la línea de **Lanzas** (Combate, 5 niveles).


---

<!-- ==================== docs/GUIA.md ==================== -->

# [Archivo: docs/GUIA.md]

## Guía para agregar cosas a AstralRPG

Mapa de dónde está cada cosa, cómo se agrega algo nuevo y cómo se sube a Aternos.
La parte de administración (plugins, comandos, problemas conocidos) está en [SERVIDOR.md](SERVIDOR.md).

> Regla de oro: **nada se edita a mano en el servidor si sale de un generador.** Se cambia el `.py` en
> `datapack-src/`, se regenera, se hace commit y push, y recién ahí se sube a Aternos. Así el repo siempre
> tiene la versión buena y se puede rearmar todo.

---

### 1. Mapa del repositorio

```
AstralRPG/
├── CLAUDE.md                 Resumen para chats nuevos con Claude (reglas y dónde mirar)
├── README.md                 Qué es el proyecto y cómo se juega
├── BALANCE.md                Números de daño, élites y dificultad
├── docs/
│   ├── SERVIDOR.md           Administración: plugins, lobby, comandos, problemas conocidos
│   ├── GUIA.md               Este archivo
│   └── CREDENCIALES.local.md Usuario y clave de Aternos (solo en tu PC, Git lo ignora)
├── datapack-src/             TODO lo que se genera sale de acá
│   ├── items.py              Materiales, armas, armaduras, talismanes, lanzas, drops, élites
│   ├── tools.py              Taladros y motosierras
│   ├── textures.py           Qué textura usa cada ítem
│   ├── build.py              Arma el datapack: lógica, recetas, Forja, guía, hechizos, élites
│   ├── build_pack.py         Arma el resource pack
│   ├── gen_textures.py       Texturas generadas (armaduras, recolores)
│   ├── *_skins.py            Skins de armaduras de cada clase (Mago, Berserker, Arquero)
│   ├── cc0_textures.py       Texturas libres (créditos en pack-source/cc0/CREDITOS.txt)
│   ├── lobby.py              Lobby: gachas (CrazyCrates), cobro, panel TAB, spawn, comandos de consola
│   ├── menus.py              Menús de cofre (DeluxeMenus): /menu, /mascotas, gachas, bazar
│   ├── pack-source/          Texturas originales, referencias y modelos de BetterModel ya generados
│   └── mobs/
│       ├── creatures.py      Modelos 3D de las 17 criaturas y los 3 cofres de las gachas
│       ├── bbmodel.py        Motor que arma los .bbmodel (cubos, cajas redondeadas, elipsoides, texturas)
│       ├── build_models.py   Exporta los modelos y hace vistas previas 3D
│       ├── mythic.py         MythicMobs: vida, daño, drops, spawn, monturas, élites, jefes, vendedores (NPCS)
│       ├── mazmorra.py       Mazmorra Minas Olvidadas: salas, oleadas, mini jefes, Guardián, cofre final
│       ├── mascotas.py       Mascotas 3D: /mascotas, seguir al dueño, bonus por nivel, cómo se consiguen
│       └── bettermodel_config.yml  Config de BetterModel usada en el server
└── build/                    SALIDA (se sube al servidor; no se edita a mano)
    ├── AstralRPG-Items.zip         datapack → world/datapacks
    ├── AstralRPG-Textures.zip      resource pack (Aternos lo baja de GitHub)
    ├── models/*.bbmodel            → plugins/BetterModel/models/
    ├── mythicmobs/mobs/astral.yml  → plugins/MythicMobs/mobs/
    ├── mythicmobs/skills/astral.yml, gachas.yml → plugins/MythicMobs/skills/
    ├── mythicmobs/randomspawns/astral.yml → plugins/MythicMobs/randomspawns/
    └── lobby/
        ├── CrazyCrates/crates/*.yml  → plugins/CrazyCrates/crates/
        ├── TAB/                      → plugins/TAB/ (ver sección 5)
        ├── Essentials/spawn.yml      → plugins/Essentials/
        └── comandos.txt              comandos de consola para rearmar el lobby
```

---

### 2. Cómo agregar cada cosa

| Quiero agregar / cambiar... | Dónde | Después correr | Subir a |
|---|---|---|---|
| Un material, arma, armadura, talismán | `datapack-src/items.py` (y la textura en `textures.py`) | `python build.py` y `python build_pack.py pack-source` | datapack + resource pack |
| Una receta o lógica (hechizos, forja, guía) | `datapack-src/build.py` | `python build.py` | datapack |
| Un taladro o motosierra | `datapack-src/tools.py` | `python build.py` y `python build_pack.py pack-source` | datapack + resource pack |
| Una criatura nueva o cambiar su forma | `mobs/creatures.py` (agregarla a `ALL`) | `python mobs/build_models.py` | `build/models/*.bbmodel` + resource pack (ver 4) |
| Vida, daño, drops o dónde aparece una criatura | `mobs/mythic.py` (`MOBS`) | `python mobs/mythic.py` | `plugins/MythicMobs/...` + `mm reload` |
| Una montura nueva | `mobs/creatures.py` (con `saddle()` y en `MOUNTS`) + `mobs/mythic.py` (`kind="montura"`) | los dos de arriba | modelos + MythicMobs |
| Plata que da cada mob | `mobs/mythic.py` (`MONEY`, `ELITE_MONEY`) | `python mobs/mythic.py` | MythicMobs + `mm reload` |
| Un vendedor del lobby | `mobs/mythic.py` (`NPCS`) + posición en `lobby.py` (`NPC_POS`) | `python mobs/mythic.py` y `python lobby.py` | MythicMobs + spawnearlo (ver 5) |
| Premios, precio o probabilidades de una gacha | `lobby.py` (`rpg_rewards`, `mount_rewards`, `cosmetic_rewards`, `GACHAS`, `RARITY_WEIGHT`) | `python lobby.py` | `plugins/CrazyCrates/crates/` + `crates reload`; si cambia el precio también `gachas.yml` + `mm reload` |
| Garantía (pity) de una gacha | `lobby.py` (`PITY`) | `python lobby.py` | `gachas.yml` + `mm reload`, cajas + `crates reload`, y rehacer los carteles flotantes (final de `comandos.txt`) |
| Fases de un jefe | `mobs/mythic.py` (`FASES`) | `python mobs/mythic.py` | MythicMobs + `mm reload` |
| Afijos de élites | `mobs/mythic.py` (`AFIJOS`) | `python mobs/mythic.py` | MythicMobs + `mm reload` |
| Jefes ancestrales (eventos) | `mobs/mythic.py` (`ANCESTRALES`) | `python mobs/mythic.py` | MythicMobs + `mm reload` |
| Bonus de set por piezas | `items.py` (`SET_BONUS`) | `python build.py` | datapack (subir `ITEM_VERSION` si cambia la lore) |
| Costos de la mejora +1..+10 | `items.py` (`MEJORAS`, `MEJORA_DANO`, `MEJORA_VIDA`) | `python build.py` y `python mobs/mythic.py` | datapack + MythicMobs (el Herrero cobra la plata) |
| Cantidades de tiradas del menú (x1, x10...) | `lobby.py` (`TIRADAS`) y `mobs/mythic.py` (`_gacha`) | `python lobby.py` y `python mobs/mythic.py` | `gachas.yml` + `mobs/astral.yml` + `mm reload` |
| Mazmorra: salas, oleadas, mobs, premio | `mobs/mazmorra.py` (`SALAS`, `MOBS`, `PREMIO`) | `python mobs/mazmorra.py` | `plugins/MythicMobs/{mobs,skills}/mazmorra.yml` + `mm reload` (armado inicial: `build/mazmorra/comandos.txt`) |
| Mascotas: bonus, niveles, cómo se consiguen | `mobs/mascotas.py` (`MASCOTAS`); modelos en `mobs/creatures.py` | `python mobs/mascotas.py` (+ `build_models.py` y resource pack si cambia un modelo) | `plugins/MythicMobs/{mobs,skills}/mascotas.yml` + `mm reload` |
| Un menú de cofre (/menu, /mascotas, gachas, bazar) | `menus.py` (funciones `*_menu`) | `python menus.py` | `plugins/DeluxeMenus/gui_menus/` (y la lista en `config.yml`) + `dm reload` |
| Look de ventanas (piedra y oro) o del HUD (barra de ítems, corazones, comida, armadura, barras) | ventanas: `gui_textures.py` (recolorea las de Minecraft, necesita la carpeta `textures/gui` sacada del client.jar como argumento); HUD: `hud_rpg.py` (dibujado de cero, a 4x; **apagado** con `HUD_RPG = False` porque en el juego la barra de ítems salió rosa/negra) | `python gui_textures.py <carpeta gui>` → queda en `pack-source/gui/`, después `python build_pack.py pack-source` | resource pack |
| Un título nuevo para la gacha | `lobby.py` (`TITLES`) | `python lobby.py` | igual que arriba |
| Una línea del panel lateral o del tabulador | `lobby.py` (`TAB_SECTIONS`) | `python lobby.py` | `plugins/TAB/config.yml` (reemplazar esa sección) + `tab reload` |
| Rangos (Novato...Leyenda) | `lobby.py` (`RANKS`) | `python lobby.py` | igual que arriba |
| Precios de la tienda vanilla | En el server: `plugins/EconomyShopGUI/shops/*.yml` (no está en el repo) | — | `sreload` |
| Plata inicial, saldo mínimo | En el server: `plugins/Essentials/config.yml` (`starting-balance`, `min-money`) | — | `essentials reload` |

#### Tips por tema

**Ítems**
- Todos los ítems de AstralRPG se dan con `loot give <jugador> loot astral:item/<id>`. El `<id>` es la clave en `items.py`.
- Si cambiás un ítem que la gente ya tiene, subí `ITEM_VERSION` en `build.py`: los viejos se actualizan solos al entrar.
- Los ítems usan `item_model` `astral:<id>`; por eso en la ruleta de las gachas se ven con su textura (`Model: Namespace astral, Id <id>`).

**Criaturas y modelos**
- Medidas: 16 unidades = 1 bloque, el frente mira al norte (-Z), el piso es y=0.
- Para dar volumen: `m.rcube(...)` (caja con bordes redondeados), `m.blob(...)` (elipsoide), `taper(...)` en `creatures.py` (colas, cuellos y picos que se afinan).
- Vista previa 3D sin entrar al juego: `python mobs/build_models.py salida_3d.png` (el nombre tiene que terminar en `3d.png`). Para ver solo algunas: `ONLY=chocobo,yeti SC=6 python mobs/build_models.py prev_3d.png`.
- Los huesos que empiezan con `p_` son asientos (`p_seat`) y el hueso `silla` se oculta hasta ensillar. No renombrarlos.
- Si cambian los modelos hay que regenerar los assets de BetterModel (ver sección 4).

**MythicMobs (cosas que ya nos mordieron)**
- En YAML, un skill con `: ` adentro (por ejemplo en un `message`) rompe el archivo. Poné el skill entero entre comillas simples o evitá `: `.
- Condiciones al hacer clic (`~onInteract`): usar `?~condicion` (del jugador que hace clic), no `?condicion`. Ejemplo: `?~hascurrency{a=1000}`, `?~crouching`.
- Para que un vendedor ejecute un comando *como el jugador* (abrir `/shop`, `/sellgui`, la vitrina de CrazyCrates), usar `command{c="sudo <trigger.name> <comando>"} @self`. `asTarget=true` no funcionó.
- Cobrar: `currencytake{a=N} @trigger`. Ver si alcanza: `?~hascurrency{a=N}`.
- Vida en porcentaje: `?healthpercent{p=<0.6}` (escala 0 a 1). `percenthealth` no existe. En `~onDamaged` se mira la vida de *antes* del golpe.
- Vida máxima de un mob: Minecraft la corta en 1024. Para jefes más duros usar Resistencia, no más vida.
- Comandos de plugins con condición: `execute if score <jugador> obj matches 30.. run crates ...` funciona desde MythicMobs. Leer un puntaje en un mensaje: `<trigger.score.obj>`. Condición: `?~score{o=obj;v=>29}`.

**Gachas**
- El vendedor (MythicMobs) cobra y corre `crates forceopen <gacha> <jugador>` → CrazyCrates gira la ruleta y ejecuta los `Commands` del premio.
- Shift + clic → `sudo <jugador> crates preview <gacha>` (la vitrina solo se abre como jugador).
- Las probabilidades se calculan solas: rareza (`RARITY_WEIGHT`) × peso del premio dentro de su rareza. Las 3 cajas suman 100 %.
- Un premio puede ser cualquier comando de consola con `%player%`: `loot give`, `mm egg give`, `give`, `lp user ... meta setprefix`, `eco give`.

---

### 3. Cómo subir cambios a Aternos

#### Lo básico
1. Regenerar con Python, commit y push a `main` (Aternos y los pasos de abajo leen de GitHub).
2. Entrar al panel de Aternos (el dueño inicia sesión; la clave está en `docs/CREDENCIALES.local.md`).
3. Subir o editar los archivos (ver abajo).
4. Recargar el plugin o reiniciar, y mirar la consola por errores.

#### Qué se recarga sin reiniciar
| Cambio | Comando de consola |
|---|---|
| MythicMobs (mobs, skills, gachas.yml) | `mm reload` |
| BetterModel (.bbmodel) | `bettermodel reload` (y además actualizar el resource pack, ver 4) |
| CrazyCrates | `crates reload` |
| TAB | `tab reload` |
| PlaceholderAPI | `papi reload` |
| EssentialsX | `essentials reload` |
| EconomyShopGUI | `sreload` |
| Datapack (`AstralRPG-Items.zip`) | apagar, reemplazar, prender (Aternos no deja reemplazarlo prendido) |
| Plugins nuevos | instalar desde Plugins y reiniciar |

#### Cómo se editan archivos en Aternos (trucos)
- **Archivos que ya existen** (configs de plugins): Files → abrir el archivo → pegar el contenido nuevo → Save. Si Aternos avisa "This file contains syntax errors", el YAML está roto: no guardar.
- **Archivos nuevos dentro de `plugins/...`**: botón *New file* (el ícono al lado de *New folder*), ponerle el nombre y después abrirlo y pegar el contenido. En las carpetas de plugins **no hay botón Upload**.
- **En la raíz de Files no se pueden crear carpetas** ("Access denied").
- **`world/datapacks` sí tiene Upload**: Upload → Files.
- **Nunca usar Worlds → Upload en la fila `world`: reemplaza el mundo entero** (así se perdió el primer mundo). Para un mundo nuevo: crearlo con Multiverse y subir sus `region/*.mca` con el server apagado.
- En Paper 26.1 todos los mundos están en `world/dimensions/minecraft/<overworld|the_nether|the_end|lobby>/`.

#### Resource pack
Cada vez que cambia `build/AstralRPG-Textures.zip`:
1. Commit y push.
2. Esperar a que `https://raw.githubusercontent.com/Trainx12/AstralRPG/main/build/AstralRPG-Textures.zip` devuelva el archivo nuevo (puede tardar unos minutos).
3. Poner el sha1 nuevo en `server.properties` → `resource-pack-sha1` (en Aternos: Files → server.properties → Resource pack SHA-1).
4. Reiniciar.

---

### 4. Modelos de criaturas → resource pack

Los modelos `.bbmodel` los convierte BetterModel en el servidor. Para que el resource pack los tenga:
1. `python mobs/build_models.py` y `python mobs/mythic.py`.
2. Levantar un servidor de prueba local con BetterModel y los `.bbmodel` (o usar el de Aternos) para que genere `plugins/BetterModel/build/assets`.
3. Copiar esa carpeta `assets` a `datapack-src/pack-source/bettermodel/assets`.
4. `python build_pack.py pack-source` → nuevo `AstralRPG-Textures.zip` → seguir los pasos de "Resource pack".
5. Subir los `.bbmodel` a `plugins/BetterModel/models/` y `bettermodel reload`.

---

### 5. Lobby: qué vive solo en el servidor

Algunas cosas no son archivos del repo sino estado del servidor. Están todas en `build/lobby/comandos.txt` para volver a armarlas:
- Protección de WorldGuard del lobby (`rg flag -w lobby __global__ ...`).
- Config de Multiverse (`mvsetspawn`, `mv config first-spawn-override true`, etc.).
- Permisos de LuckPerms del grupo `default` (`essentials.spawn`, `balance`, `pay`...).
- Expansiones de PlaceholderAPI (`papi ecloud download ...`).
- Los 6 vendedores (`mm mobs spawn astral_npc_...`). WorldGuard no deja aparecer mobs en el lobby, así que primero `rg flag -w lobby __global__ mob-spawning allow`, después los spawns, después `... deny` (ya está así en el archivo).
- Essentials `config.yml`: `starting-balance: 250`, `min-money: 0`, `newbies.spawnpoint: none`, `newbies.kit: ''`.

Para mover o reemplazar un vendedor: `mm mobs kill astral_npc_<nombre>` y volver a spawnearlo con la línea de `comandos.txt`.

**TAB:** `lobby.py` genera `build/lobby/TAB/secciones-config.yml` con solo las secciones que cambiamos (`header-footer`, `playerlist-objective`, `belowname-objective`, `scoreboard`, `conditions`). En `plugins/TAB/config.yml` se reemplazan esas secciones y el resto queda como está. `groups.yml` se reemplaza entero. Las animaciones (`astral_titulo`, `astral_ip`) se agregan al final de `animations.yml`.

Placeholders útiles para el panel o el tabulador: `%vault_eco_balance_formatted%`, `%player_health_rounded%`, `%player_max_health_rounded%`, `%player_level%`, `%auraskills_power%`, `%auraskills_<skill>%`, `%luckperms_prefix%`, `%statistic_mob_kills%`, `%server_tps_1_colored%`, `%condition:rango%`. Para probar uno: `papi parse <jugador> %placeholder%`.

---

### 6. Servidor de prueba local

Sirve para probar MythicMobs, BetterModel y el datapack sin tocar Aternos (sin economía ni gachas).
- Hubo uno en la carpeta temporal de Claude (`.../scratchpad/testsrv`, con su propio Java 25 en `jdk/`). Esas carpetas se pueden borrar; si no está, se rearma bajando Paper 26.1.2 y los mismos plugins.
- Arrancarlo, esperar a que cargue, y mirar el log buscando `Loaded N mobs`, `models are loaded` y errores.

---

### 7. Cosas importantes que no hay que olvidar

- **El repo es público.** Nunca commitear contraseñas; van en `docs/CREDENCIALES.local.md` (ignorado por Git). Tampoco subir mapas de terceros al repo.
- **No hay backups automáticos** salvo que se vincule Google Drive en Aternos → Backups. Bajar el mundo de vez en cuando.
- **Aternos apaga el server cuando no hay nadie.** Si al entrar sale `cookie_request`, es que está apagado: prenderlo desde el panel.
- **AuraSkills necesita el preset `legacy.zip`** para que existan Forja y Hechicería.
- **Versiones fijas:** Paper 26.1.2, Stellarity 5.4.2 (la 6.x crashea), ExcellentEnchants 5.4.3 con NightCore 2.16.7. No usar ExcellentCrates (la 7.x no se puede configurar por archivo y la 6.x no anda con este NightCore).
- **Chat de los OP lleno de "Se ha cambiado la puntuación...":** es la regla `log_admin_commands`; está apagada en los 5 mundos (ver `build/lobby/comandos.txt`). Si se crea un mundo nuevo, apagarla también ahí.
- **Un comando nuevo de DeluxeMenus sale en rojo en el chat pero funciona:** el juego del jugador no lo conoce hasta que vuelve a entrar.
- **Los huevos de monturas y mascotas no funcionan en el lobby** (no aparecen mobs ahí): se usan en el mundo.
- Después de cualquier cambio: revisar la consola. Los avisos `ExampleQuest...` de MythicMobs y los de GeoIP de AuthMe son normales.


---

<!-- ==================== docs/SERVIDOR.md ==================== -->

# [Archivo: docs/SERVIDOR.md]

## AstralRPG: cómo está armado el servidor

Documento de referencia para administrar el servidor. Actualizado el 28/10/2026.
Para saber dónde está cada cosa en el repo y cómo agregar cosas nuevas, ver [GUIA.md](GUIA.md).

> **Contraseñas:** este repositorio es público, así que acá no va ninguna contraseña.
> El usuario y la contraseña de Aternos están en `docs/CREDENCIALES.local.md`. Ese archivo existe solo
> en la PC del dueño y Git lo ignora, así que no se sube a GitHub.
> Como la contraseña de Aternos se compartió por chat, conviene cambiarla y actualizar ese archivo.

### Servidor

| Dato | Valor |
|---|---|
| Dirección | `AstralRPG2.aternos.me` |
| Hosting | Aternos (panel en https://aternos.org/server/) |
| Software | Paper 26.1.2, build 74 (Java 25) |
| Modo | No premium (`online-mode=false`): entran cuentas cracked y originales |
| Login | AuthMe: cada jugador hace `/register <clave> <clave>` la primera vez y `/login <clave>` después |
| Mods | Ninguno. Se entra desde Minecraft vanilla 26.1.2 |
| Repositorio | https://github.com/Trainx12/AstralRPG (público) |

Aternos apaga el servidor cuando no hay nadie. Para prenderlo hay que entrar al panel, apretar **Start** y dejar terminar el anuncio. Si se cierra el anuncio antes de tiempo, a veces el arranque se cancela y hay que apretar Start de nuevo.

**Reglas al cambiar archivos:**
- Aternos no deja reemplazar archivos con el servidor prendido: hay que apagarlo antes de subir el datapack o configs nuevas.
- Cada vez que cambia `AstralRPG-Textures.zip`, hay que actualizar `resource-pack-sha1` en `server.properties` con el sha1 nuevo. Si no se actualiza, los jugadores no bajan la versión nueva o el pack falla al cargar.
- **Nunca usar el botón Upload de la fila del mundo `world` en la página Worlds: reemplaza el mundo entero.** Así se perdió el mundo original el 28/10/2026 (no había backups porque Aternos solo los hace con Google Drive vinculado). Conviene vincular Google Drive en Backups y bajar el mundo de vez en cuando.
- En Paper 26.1 todos los mundos viven dentro de `world/`: `world/dimensions/minecraft/<overworld|the_nether|the_end|lobby>/region`.

### Plugins

| Plugin | Para qué está |
|---|---|
| AuraSkills 2.4.0 | Skills y niveles (Forja, Hechicería, Arquería, Combate, Minería, Tala...). **Tiene cargado el preset `legacy.zip`** (sin él no existen Forging ni Sorcery) |
| LevelledMobs | Sube el nivel de los mobs según la distancia al spawn |
| MythicMobs 5.13.0 | Criaturas custom: fauna, hostiles, monturas, élites y jefes |
| BetterModel 3.6.0 | Modelos 3D de esas criaturas (sin mods) |
| ExcellentEnchants 5.4.3 + NightCore + PacketEvents | Encantamientos extra (el Taladro Infernal usa Tunnel) |
| Bolt | Protege cofres, shulkers y puertas |
| WorldGuard + WorldEdit | Zonas protegidas y edición |
| AuthMe | Login con contraseña (necesario en modo no premium) |
| SkinsRestorer | Skins para cuentas no premium |
| AxGraves | Tumba con tus cosas al morir |
| ClearLag++ | Limpia ítems tirados para que no haya lag |
| TAB | Tabulador y panel lateral de stats (ver Lobby) |
| nonchat | Filtro y formato de chat |
| RHLeafDecay | Las hojas se caen rápido al talar |
| LuckPerms | Permisos |
| PlaceholderAPI | Variables para otros plugins (con la expansión LuckPerms para los títulos en el chat) |
| Multiverse-Core 5.8.2 | Mundo aparte `lobby` (la isla de spawn) |
| EssentialsX 2.22.0 + EssentialsX Spawn + Vault | Monedas (`/balance`, `/pay`), `/spawn` al lobby |
| EconomyShopGUI 7.3.3 | Tienda (`/shop`) y venta rápida (`/sellgui`) de ítems vanilla |
| CrazyCrates (26.1.2) | Ruleta animada tipo CS:GO de las gachas del lobby |
| DeluxeMenus 1.14.1 | Menús de cofre: `/menu`, `/mascotas`, gachas y bazar (los genera `datapack-src/menus.py`) |
| CrazyAuctions (26.1.2) | Subastas entre jugadores (`/ah`), 5% de impuesto por venta |
| DonutOrders 2.0.0 | Órdenes de compra entre jugadores (`/orders`) |
| QuickShop-Hikari 6.3.0.3 | Instalado pero sin permisos para jugadores (se usó en los puestos que se sacaron) |

### Lobby (mundo `lobby`)

Isla de "Parrot Spawn" (solo la isla grande, sin la torre del loro). Es un mundo vacío aparte, en modo aventura, sin mobs, sin PvP ni daño, y protegido con WorldGuard (`__global__`).

- **Spawn:** centro de la plaza (180.5, 98, 190.5). Los jugadores nuevos aparecen ahí la primera vez; después entran donde salieron. `/spawn` vuelve al lobby, y si morís sin cama reaparecés en el lobby.
- **Vendedores** (de MythicMobs, quietos e invulnerables). Tienda, Venta y Viajero son aldeanos; las 3 gachas son cofres 3D (BetterModel, modelos `astral_cofre_*`) que abren la tapa cuando cobran la tirada. Arriba de cada cofre hay un cartel flotante (text_display con tag `astral_holo`) con el nombre, el precio y cada cuántas tiradas sale un Épico seguro; se rehacen con las líneas del final de `comandos.txt` (primero el `kill`):

| Edificio | Vendedor | Qué hace |
|---|---|---|
| Norte (grande) | Tienda | Abre `/shop` |
| Noroeste | Venta rápida | Abre `/sellgui` |
| Cofre violeta (sobre el cristal del medio, lado este) | Gacha de Armas (1000$) | Materiales, armas, talismanes |
| Cofre verde (cristal del norte, lado este) | Gacha de Monturas (2500$) | Monturas con silla y mascotas |
| Cofre rosa (cristal del sur, lado este) | Gacha de Cosméticos (500$) | Títulos para el chat y moldes de adorno |
| Junto al banco del sur | Viajero | Te lleva al mundo normal |

  En las gachas: clic para tirar (el vendedor cobra y abre la ruleta de CrazyCrates con `crates forceopen`), shift + clic para ver la vitrina de premios (común 60%, poco común 25%, raro 11%, épico 3,5%, legendario 0,5%).
- **Tiradas x1 / x10 / x25 / x50:** clic al cofre muestra en el chat un botón por cantidad (con el precio). El botón hace `/trigger gachatirar set <código>` (gacha × 100 + tiradas: 1xx Armas, 2xx Monturas, 3xx Cosméticos) y el cofre, cada 1/4 de segundo, cobra a los jugadores cercanos que lo apretaron. Con más de una tirada gira la ruleta **una vez** (con animación; si toca la garantía, es esa) y unos 7 segundos después llegan los demás premios juntos: CrazyCrates les da llaves virtuales y las abre con `crates mass-open` (necesita `crazycrates.massopen` en el grupo `default` y `Max-Mass-Open: 50` en las cajas). En tiradas múltiples, si sale un Épico el contador de garantía vuelve a 0.
- **Garantía (pity):** cada tirada suma 1 a un contador por jugador y por gacha (scoreboard `pity_rpg`, `pity_monturas`, `pity_cosmeticos`). Al llegar a 50 (Armas) / 40 (Monturas) / 20 (Cosméticos) tiradas sin Épico, esa tirada sale de la caja `<gacha>_garantia` (solo Épico o Legendario). Sacar Épico o Legendario vuelve el contador a 0. El vendedor le dice al jugador cuánto lleva (también con shift + clic). Los objetivos se crean con las líneas `scoreboard objectives add pity_...` de `comandos.txt` (una sola vez). Para ver o tocar el contador de alguien: `scoreboard players get <jugador> pity_rpg` / `... set <jugador> pity_rpg 0`.
- **Jefes con fases:** los 5 jefes cambian al 60% y al 25% de vida (avisan en el chat): invocan ayudantes, hacen ondas en el piso con 1 segundo de aviso para alejarse, se cubren con escudo un rato o se curan. Está en `FASES` de `mobs/mythic.py`.
- **Afijos de élites:** cada élite de MythicMobs sale con uno al azar, que se ve en el nombre: Vampírico (se cura al pegar), Explosivo (pega en área al morir), Blindado (Resistencia), Veloz, Invocador (llama a la versión normal) y Maldito (Debilidad cerca). Está en `AFIJOS`. Los élites del datapack (mobs vanilla) no tienen afijos.
- **Eventos mundiales (jefes ancestrales):** cada jefe tiene una versión *Ancestral* (más grande, otro color, 1000 de vida con Resistencia, fases y un afijo). Aparece muy rara vez en los mismos biomas, se anuncia a todo el servidor con las coordenadas y si nadie la mata en 10 minutos se va. Da 3000$, Chispas y Almas. Para lanzar un evento a mano: `mm mobs spawn astral_yeti_ancestral` (o `momia`, `golem_forja`, `cangrejo`, `chaman`). Está en `ANCESTRALES` de `mobs/mythic.py`.
- **Herrero (mejora +1 a +10):** aldeano del lobby. Con un arma o pieza de armadura de AstralRPG en la mano: clic = te dice cuánto cuesta la siguiente mejora; shift + clic = mejorar. Armas: +3% a +40% de daño. Armaduras: +0,25 a +3 de vida por pieza. Cuesta plata y materiales de élite y jefe (`MEJORAS` en `items.py`); de +5 en adelante puede fallar: se pierden los materiales, pero no la plata ni el ítem. Los bastones de Mago no se mejoran. La mejora es un encantamiento (`astral:mejora_arma` / `astral:mejora_armadura`) y se conserva cuando se actualizan los ítems. Para ponerlo: parate donde lo quieras y `/mm mobs spawn astral_npc_herrero` (con `mob-spawning allow`, ver `comandos.txt`).
- **Bonus de set por piezas:** además de los stats del set, llevar 2 o 4 piezas de la misma clase (de cualquier tier) da un extra: Berserker +5% daño / Fuerza al matar; Mago +2 armadura / Regeneración y Velocidad al matar; Arquero +5% velocidad / Velocidad II y Salto al matar. Está en `SET_BONUS` de `items.py` (es del datapack: hay que apagar para subirlo).
- **Monedas:** se empieza con 250$. Se gana vendiendo en la tienda y matando: 15$ por hostil de AstralRPG, 150$ por élite y 750$ por jefe.
- **Archivos:** `datapack-src/lobby.py` genera `build/lobby/CrazyCrates/crates/*.yml` (premios y probabilidades), `build/mythicmobs/skills/gachas.yml` (cobro), `build/lobby/Essentials/spawn.yml` y `build/lobby/comandos.txt` (todos los comandos de consola para armarlo de nuevo). Los vendedores están en `datapack-src/mobs/mythic.py` (`NPCS`).
- Si falta un vendedor: correr las líneas `mm mobs spawn astral_npc_...` de `comandos.txt` (con el `mob-spawning allow`/`deny` de alrededor). Para borrar uno: `mm mobs kill astral_npc_<nombre>`.
- **Panel y tabulador (TAB):** a la derecha, panel con nombre, rango, título, vida, oro, poder, nivel, Forja/Hechicería/Arquería, bajas y mundo (`/sb` lo oculta o muestra). En el tabulador: encabezado animado, corazones de vida, título de la gacha y poder de cada jugador. Rango según el poder de AuraSkills: Novato, Aventurero (150), Veterano (400), Héroe (800), Leyenda (1500). Lo genera `datapack-src/lobby.py` en `build/lobby/TAB/` (las secciones de `config.yml` se reemplazan una por una; `groups.yml` entero; las animaciones se agregan a `animations.yml`). Después: `tab reload`. Usa las expansiones de PlaceholderAPI LuckPerms, Vault, Player, Server y Statistic.
- Los huevos de mascotas y monturas no funcionan en el lobby (ahí no aparecen mobs): hay que usarlos en el mundo.
- Si cambian los premios: subir los `.yml` a `plugins/CrazyCrates/crates/` y correr `crates reload`.
- Las gachas no usan ExcellentCrates: la 7.x guarda todo en base de datos (solo se edita dentro del juego) y la 6.x no anda con el NightCore que necesita ExcellentEnchants.

### Mascotas

6 mascotas 3D que siguen al jugador (también entre mundos) y le dan efectos mientras están afuera. Una a la vez. En el lobby no salen.

| Mascota | Nivel 1 | Nivel 10 | Nivel 20 | Cómo se consigue |
|---|---|---|---|---|
| Lobo del Bosque | Fuerza I | + Velocidad I | + Resistencia I | 3% al matar Espantapájaros o Abejorros |
| Cuervo Arcano | Visión nocturna, marca a los mobs cerca | + Suerte | + Velocidad I | Gacha de Monturas (raro) |
| Gólem de Piedra | Resistencia I | + Regeneración I | + Absorción | Mazmorra: 15% el Gólem Antiguo, 5% el cofre |
| Zorro Espectral | Velocidad I | + Salto I | Velocidad II | 20% el Yeti, 2% las Caras Voladoras |
| Dragoncito de Fuego | Resistencia al fuego | + Fuerza I | + Prisa I | Gacha de Monturas (épico) |
| Fénix | Te salva con poca vida cada 10 min | cada 7 min | cada 5 min | Gacha de Monturas (legendario) |

- **Uso:** `/mascotas` (alias en `commands.yml` → `/trigger mascota set 99`) abre un menú con botones *Invocar* y *Guardar*.
- **Niveles:** 1 nivel cada 25 mobs que mata el dueño con la mascota afuera, hasta 30. Nivel 30: más grande y con partículas.
- **Por dentro:** tener la mascota = permiso `astral.mascota.<lobo|cuervo|golem|zorro|dragon|fenix>`; la elegida está en el puntaje `petsel`; los niveles en `plv_<id>`. Un controlador invisible (`astral_mascotas_control`) en un chunk del lobby siempre cargado atiende los pedidos de todos.
- Dar una mascota a mano: `lp user <jugador> permission set astral.mascota.<id> true`. Armado: `build/mascotas/comandos.txt`.

### Menús, bazar y subastas

- **Menús de cofre (DeluxeMenus):** `/menu` (principal), `/mascotas`, y los que abren los vendedores: cada cofre de gacha (`dm open gacha_<x> <jugador>`: tirar x1/x10/x25/x50 y ver premios) y el aldeano *Bazar* (`dm open bazar <jugador>`: mercado, venta rápida, subastas y órdenes). Shift + clic al cofre de gacha sigue mostrando la vitrina. La garantía se ve en el menú con `%objective_score_{pity_rpg}%` (expansión ScoreboardObjectives de PlaceholderAPI).
- **Mercado y venta rápida:** EconomyShopGUI (`/shop`, `/sellgui`), con precios fijos.
- **Subastas (CrazyAuctions, `/ah`):** ítems únicos entre jugadores; publicar con `/ah sell <precio>` y el ítem en la mano. Aldeano *Subastas* (`astral_npc_subastas`).
- **Órdenes de compra (DonutOrders, `/orders`):** pedís algo y pagás por adelantado; quien te lo entrega cobra al toque.
- EzAuction y RoyalBazaar (los que se habían elegido) no están en el catálogo de plugins de Aternos.
- Los 4 puestos con cofres y alquiler que hubo antes se sacaron (regiones `puesto1-4`, grupos y cofres borrados).

### Mazmorra: Minas Olvidadas (mundo `mina`)

Mundo vacío de Multiverse con el mapa `dungeon1-endlessxl.schem` (de terceros: **no está en el repo**, se sube directo a `plugins/WorldEdit/schematics/`) pegado con `//paste -o` (la esquina queda en -73 -55 -290). Dificultad difícil, sin mobs naturales, `keep_inventory` activado, protegido con WorldGuard.

- **4 salas** que se recorren con teletransporte: 1) Campamento Minero (mineros corruptos y esqueletos), 2) Lago Subterráneo (ahogados + mini jefe Capataz Ahogado), 3) Túneles de Soporte (arañas, esqueletos + mini jefe Gólem de Piedra Antiguo), 4) Salón del Guardián (jefe final con fases).
- Cada sala tiene un controlador invisible (`astral_mina_control_salaN`): al llegar un jugador larga las oleadas, cuando no quedan mobs pasa a la siguiente, y si la sala se queda vacía se reinicia sola. Con 2 o más jugadores aparecen mobs extra.
- **Cofre final:** materiales de élite, 2500$ y 25% de Chispa Astral. Se cobra una vez cada 30 minutos por jugador (permiso temporal `astral.mina.cd` de LuckPerms); se puede volver a entrar sin premio. Después de 15 segundos vuelven al lobby.
- **Entrada:** vendedor `astral_npc_mina` en el lobby. Salir: `/spawn`.
- Todo sale de `datapack-src/mobs/mazmorra.py`; el armado (crear el mundo, pegar el mapa, poner los controladores) está en `build/mazmorra/comandos.txt`.

### Datapacks (`world/datapacks`)

Tienen que estar antes de generar un mundo nuevo, si no, no aparecen sus estructuras. Se suben con Files → `world/datapacks` → Upload → Files.

- **AstralRPG-Items.zip**: el nuestro. Tiene ítems, recetas, Forja Astral, guía, élites, taladros y motosierras.
- Dungeons and Taverns 5.2.0 y DnT Stronghold Overhaul 2.4.0: estructuras.
- Incendium 5.4.12: Nether.
- Stellarity 5.4.2: End. La 6.0.1 crasheaba en 26.1.2, por eso quedó la 5.4.2.

### Resource pack

- Se sirve desde `https://raw.githubusercontent.com/Trainx12/AstralRPG/main/build/AstralRPG-Textures.zip`.
- Es obligatorio (`require-resource-pack=true`).
- Incluye las texturas originales del dueño (`assets/astral`, `assets/armasrpg`), las armaduras de Mago, Berserker y Arquero, las texturas CC0 (créditos en `datapack-src/pack-source/cc0/CREDITOS.txt`), los taladros y motosierras, y los modelos de BetterModel.
- Después de cambiarlo: commit y push, esperar a que GitHub sirva el archivo nuevo (puede tardar unos minutos) y recién ahí poner el sha1 nuevo en `server.properties`.

### Cómo cambiar cosas

Todo se genera con Python desde `datapack-src/`:

```
cd datapack-src
python gen_textures.py
python build.py
python build_pack.py pack-source
```

`gen_textures.py` solo hace falta si cambiaron texturas generadas (armaduras, recolores, CC0).

| Qué querés cambiar | Archivo |
|---|---|
| Materiales, drops de mobs, armaduras, armas, talismanes, lanzas, élites | `items.py` |
| Taladros y motosierras (niveles, velocidad, área, recetas) | `tools.py` |
| Qué textura usa cada ítem | `textures.py` |
| Lógica: hechizos, arcos, forja, guía, élites, área de taladros | `build.py` |
| Criaturas: modelos | `mobs/creatures.py` → `python mobs/build_models.py` |
| Criaturas: vida, drops, spawn | `mobs/mythic.py` |

Salida:
- `build/AstralRPG-Items.zip` (datapack).
- `build/AstralRPG-Textures.zip` (resource pack).
- `build/models/*.bbmodel` va a `plugins/BetterModel/models/`.
- `build/mythicmobs/{mobs,skills,randomspawns}/astral.yml` va a `plugins/MythicMobs/...`.

**Para subir cambios al servidor:**
1. Apagá el servidor.
2. Reemplazá los archivos.
3. Actualizá el sha1 si cambió el resource pack.
4. Prendé el servidor y mirá la consola por errores.

Si cambia un ítem que los jugadores ya tienen, subí `ITEM_VERSION` en `build.py`: los ítems viejos se actualizan solos al entrar.

### Comandos útiles (como OP o desde la consola, sin `/`)

| Comando | Qué hace |
|---|---|
| `op <jugador>` | Dar OP |
| `skills skill setlevel <jugador> <skill> <nivel>` | Poner nivel de AuraSkills (`mining`, `foraging`, `forging`, `sorcery`, `archery`, `fighting`) |
| `skills preset load legacy.zip` y `skills reload` | Volver a cargar Forging/Sorcery si se resetea AuraSkills |
| `function astral:admin/todo` | Te da todas las cajas de shulker con todos los ítems |
| `function astral:admin/kit_<nombre>` | Una caja: `materiales`, `berserker`, `mago`, `arquero`, `armas`, `especiales`, `herramientas` |
| `function astral:admin/materiales` | Dos de cada material |
| `trigger astral.guia` | Abre la guía (también Esc → Guía AstralRPG) |
| `mm mobs spawn astral_<id>` | Spawnear una criatura (ej. `astral_chocobo`, `astral_yeti`) |
| `mm mobs list` | Lista de criaturas cargadas (tienen que ser 34: 27 criaturas + 7 vendedores) |
| `bettermodel reload` | Recargar modelos (tienen que ser 26: 17 criaturas, 3 cofres y 6 mascotas) |
| `bolt edit add <amigo>` y clic en la caja | Compartir un cofre o shulker protegido |
| `bolt trust` | Confiar todas tus protecciones a un amigo |
| `bolt info` y clic | Ver de quién es una protección |

### Sistemas del juego (resumen)

- **Forja Astral:** abrí la guía al lado de una mesa de herrería (a 3 bloques o menos) y apretá Forjar. Saca los materiales del inventario y, si falta algo, avisa todo lo que falta junto.
- **Clases:** Berserker (Forja), Mago (Hechicería) y Arquero (Arquería). Cada una tiene 5 tiers de armadura y armas, y cada tier se hace con el anterior. Las armaduras tienen skins propias.
- **Arcos:** manteniendo clic derecho disparan solos.
- **Élites:** la dificultad sube con tu equipo y con los días (ver `BALANCE.md`).
- **Criaturas (MythicMobs):**
  - Fauna: mapache y pingüino.
  - Hostiles: espantapájaros, abejorro, araña y cara voladora.
  - Monturas, que nacen sin silla y se ensillan: chocobo, grillo, escarabajo, lagarto, ave y pterodáctilo.
  - Jefes: momia, yeti, gólem de forja, cangrejo y chamán.
  - Hay élites de 5 hostiles, con 2,5 veces la vida.
- **Taladros (Minería 5 → 40):** 9 niveles. Rompen 1x1, 2x1, 2x2, 3x3 y 4x4. Del nivel 3 en adelante son indestructibles.
- **Motosierras (Tala 5 → 32):** 5 niveles. Cortan 1, 2, 3 y 6 troncos, o el árbol entero.
- El área del taladro y la tala solo afectan bloques naturales. Esos bloques extra no dan experiencia de AuraSkills.

### Problemas conocidos y soluciones

- Avisos de MythicMobs sobre `ExampleQuest...`: son de los ejemplos que trae el plugin, no afectan nada.
- Aviso de Paper "4 releases behind": se queda en 26.1.2 a propósito, porque los plugins están probados ahí.
- Errores de GeoIP de AuthMe: no afectan.
- Error al entrar `Failed to decode packet 'clientbound/minecraft:cookie_request'`: el servidor está apagado y responde la sala de espera de Aternos, que no es compatible con el cliente 26.1. Prender el servidor desde el panel y entrar cuando diga Online.
- Si alguien no ve texturas: que acepte el resource pack al entrar. Si sigue igual, revisar que el sha1 coincida.
- Si aparece "Unknown skill": cargar el preset legacy de AuraSkills (ver comandos).
- El área de los taladros puede romper bloques dentro de una zona de WorldGuard si picás justo en el borde.

### Servidor de prueba local

Para probar sin tocar Aternos hubo una copia del servidor (mismos plugins, sin economía) en la carpeta temporal de Claude. Esas carpetas se pueden borrar; se rearma bajando Paper 26.1.2 y los mismos plugins. El mundo de prueba es plano. Detalles en [GUIA.md](GUIA.md#6-servidor-de-prueba-local).

### Comandos de admin del lobby y la economía

| Comando | Qué hace |
|---|---|
| `eco give <jugador> <monto>` | Dar plata (`eco take` / `eco set` para sacar o fijar) |
| `lp user <jugador> meta setprefix 100 &b&l«ASTRAL»` | Dar un título (`meta removeprefix 100` lo saca) |
| `loot give <jugador> loot astral:item/<id>` | Dar cualquier ítem de AstralRPG |
| `mm egg give <jugador> astral_<montura> 1` | Huevo de montura o mascota (usar en el mundo, no en el lobby) |
| `crates forceopen <gacha_rpg\|gacha_monturas\|gacha_cosmeticos> <jugador>` | Tirada gratis |
| `mvtp <jugador> w:world` / `spawn` | Ir al mundo / al lobby |
| `mm mobs kill astral_npc_<nombre>` | Borrar un vendedor (se vuelve a poner con `build/lobby/comandos.txt`) |


---

<!-- ==================== docs/HISTORIA.md ==================== -->

# [Archivo: docs/HISTORIA.md]

## La historia de AstralRPG

Borrador de la historia y de las misiones (diarias y de historia). Todavía **no está en el juego**:
esto es el guion para después armarlo. Usa solo cosas que ya existen en el server (jefes, mazmorra,
materiales, NPC del lobby), salvo donde dice *(nuevo)*.

---

### 1. La idea en pocas líneas

Hace mucho, sobre este mundo brillaba la **Estrella Astral**, que mantenía en calma a las criaturas.
Una noche se partió. Sus pedazos cayeron por todo el mundo:

- El **polvo** de la estrella se metió en los mobs comunes. Por eso algunos se vuelven **élites**
  (de ahí sale la *Esencia de Élite*).
- Los pedazos medianos se pudrieron por dentro y se volvieron **Almas Corruptas**.
- Los **5 fragmentos grandes** cayeron en 5 lugares distintos y transformaron a la criatura más fuerte
  de cada zona en un **jefe**.
- Las **Chispas Astrales** son lo único que quedó limpio de la estrella. Con ellas se forja el mejor equipo.

Lo que se salvó del cielo es una isla que quedó flotando: **el Refugio** (el lobby). Ahí viven los
últimos que recuerdan la estrella. El **Viajero** es el último de los Guardianes Astrales y es quien
cuenta la historia: es el que lleva a los jugadores al mundo.

**Objetivo del jugador:** juntar los 5 fragmentos, derrotar a los jefes y volver a encender la estrella.

---

### 2. Personajes

| Personaje | Quién es en la historia | Ya existe |
|---|---|---|
| **Viajero** | El último Guardián Astral. Viejo, cansado y con mucha fe en los nuevos. Da la historia principal. | Sí |
| **Herrero** | Sabe trabajar el metal de la estrella. Él inventó la Forja Astral. Gruñón pero justo. | Sí |
| **Tienda** | Comerciante del Refugio. Siempre necesita provisiones. Da diarias de recolección. | Sí |
| **Bazar** | Coleccionista de rarezas. Paga bien por materiales de élite. | Sí |
| **Cronista** *(nuevo)* | Escribe todo lo que pasa en el Refugio. Tiene el tablón de misiones diarias. | No |

Las 3 clases tienen una razón dentro de la historia:
- **Berserker:** los que pelean con la fuerza que da el metal astral (Forja).
- **Mago:** los que escuchan el eco de la estrella y lo usan como hechizo (Hechicería).
- **Arquero:** los centinelas que vigilaban el cielo desde las torres (Arquería).

---

### 3. Misiones de historia

Cada capítulo pide más o menos un tier de equipo. Los premios usan la economía actual
(hostil 15$, élite 150$, jefe 750$).

#### Prólogo — La isla que flota
**Lo da:** Viajero · **Tier recomendado:** ninguno

> *"Otro más que cayó del cielo... Bienvenido al Refugio. Lo que ves acá es todo lo que quedó de la
> Estrella Astral. Antes de bajar al mundo, andá a ver al Herrero. Sin metal no vas a durar una noche."*

1. Hablar con el Viajero.
2. Hablar con el Herrero.
3. Abrir la Guía AstralRPG y forjar cualquier pieza de **Tier I**.
4. Volver con el Viajero.

**Premio:** 300$ y que el Viajero te lleve al mundo por primera vez.

#### Capítulo 1 — Los campos que no duermen
**Lo da:** Viajero · **Tier:** I

> *"De noche, en las llanuras, los espantapájaros se levantan solos. Eso es polvo de la estrella.
> Si queda polvo, los fragmentos no pueden estar lejos."*

1. Matar 10 **Espantapájaros** y 10 **Abejorros**.
2. Matar 1 **élite** de cualquier tipo.
3. Traerle 3 **Esencias de Élite** al Herrero.

**Premio:** 500$ y una pieza de Tier I a elección. *(Acá el Herrero explica las mejoras +1.)*

#### Capítulo 2 — La marea de pinzas
**Lo da:** Viajero · **Tier:** I–II · **Jefe:** Cangrejo (playas)

> *"Los pescadores ya no se acercan a la orilla. Dicen que algo enorme sale del agua y que tiene un
> brillo azul adentro. Ese es el primer fragmento."*

1. Encontrar y derrotar al **Cangrejo**.
2. Llevarle el **Fragmento de la Marea** *(ítem nuevo, lo suelta el jefe la primera vez)* al Viajero.

**Premio:** 1000$.

#### Capítulo 3 — El pantano que canta
**Lo da:** Viajero · **Tier:** II · **Jefe:** Chamán (pantano, de noche)

> *"Hubo un chamán que quiso usar el fragmento para curar el pantano. Ahora el fragmento lo usa a él.
> No le tengas lástima: ya no es quien era."*

1. Matar 15 **Caras Voladoras** (están en el pantano de noche).
2. Derrotar al **Chamán**.
3. Entregar el **Fragmento del Pantano**.

**Premio:** 1500$.

#### Capítulo 4 — Arena con memoria
**Lo da:** Viajero · **Tier:** III · **Jefe:** Momia (desierto)

> *"En el desierto hay un rey que tendría que estar muerto hace mil años. El fragmento lo despertó.
> Llevá agua y no te quedes quieto cuando el piso tiemble."*

1. Derrotar a la **Momia**.
2. Entregar el **Fragmento de la Arena**.

**Premio:** 2000$ y 1 Alma Corrupta.

#### Capítulo 5 — Las Minas Olvidadas
**Lo da:** Viajero, después NPC de la Mina · **Tier:** III

> *"Los mineros cavaron justo donde cayó un pedazo de la estrella. Se volvieron locos. El que los
> mandaba se ahogó en el lago de abajo, y en el fondo hay un Guardián que nadie vio y salió vivo."*

1. Terminar la mazmorra **Minas Olvidadas** (las 4 salas).
2. En el cofre final aparece la **Lámpara del Minero** *(ítem nuevo, solo la primera vez)*. Hay que
   llevársela al Viajero.

**Premio:** 2500$ (además del cofre). El Viajero cuenta que la lámpara muestra el camino al fragmento helado.

#### Capítulo 6 — El silencio blanco
**Lo da:** Viajero · **Tier:** IV · **Jefe:** Yeti (picos nevados)

> *"Más arriba de las nubes no se escucha nada. Ni el viento. El Yeti custodia el fragmento como si
> fuera su cría. Va a pelear hasta el final."*

1. Derrotar al **Yeti**.
2. Entregar el **Fragmento de Hielo**.

**Premio:** 3000$ y 1 Chispa Astral.

#### Capítulo 7 — El corazón de la forja
**Lo da:** Herrero · **Tier:** V · **Jefe:** Gólem de Forja (Nether)

> *"El último fragmento cayó tan fuerte que atravesó el mundo y terminó en el Nether. Allá se fundió
> con un gólem que yo mismo había hecho hace mucho. Es mi culpa. Terminalo vos."*

1. Forjar una pieza de **Tier V**.
2. Derrotar al **Gólem de Forja**.
3. Entregar el **Fragmento de Fuego**.

**Premio:** 5000$.

#### Epílogo — Encender la estrella
**Lo da:** Viajero

> *"Cinco fragmentos. Hace siglos que no los veía juntos... Ponelos acá. Vas a ver."*

1. Entregar los 5 fragmentos.
2. Se ve una animación en el cielo del Refugio *(partículas y fuegos artificiales)*.

**Premio:** título de chat **"Portador de la Estrella"** y 10000$.

> *"La estrella vuelve a brillar, pero algo no está bien. Sus ecos más viejos siguen allá abajo..."*

Eso abre el contenido de después del final: los **jefes Ancestrales** se explican como "ecos" de la
estrella, que aparecen de vez en cuando para probar a los que la volvieron a encender.

---

### 4. Misiones diarias

Las da el **Cronista** *(nuevo)* desde un tablón en el Refugio. Cada día salen **3 al azar**: una fácil,
una media y una difícil. Se reinician a la medianoche.

#### Fáciles (300$)
| Misión | Qué hay que hacer | Texto |
|---|---|---|
| Ronda nocturna | Matar 15 hostiles de AstralRPG | *"Anoche se escucharon ruidos cerca del camino. Limpiá la zona."* |
| Provisiones | Entregar 32 de pan o carne cocida a la Tienda | *"La Tienda se quedó sin comida otra vez."* |
| Madera para el Refugio | Entregar 64 troncos | *"Hay que arreglar el muelle. Traé madera."* |
| Piedra y hierro | Entregar 64 de piedra y 16 de hierro al Herrero | *"El Herrero no puede trabajar con las manos vacías."* |
| Plaga de arañas | Matar 10 Arañas | *"Las arañas tapan las cuevas con tela. Despejá alguna."* |

#### Medias (750$)
| Misión | Qué hay que hacer | Texto |
|---|---|---|
| Caza de élites | Matar 3 élites | *"El polvo de la estrella se está juntando. Buscá a los que brillan."* |
| Encargo del Bazar | Entregar 5 Esencias de Élite al Bazar | *"El Bazar paga bien por esencias frescas."* |
| Explorador | Recorrer 3 biomas distintos (desierto, nieve, pantano...) | *"Necesito saber cómo están las tierras lejanas."* |
| Mascota entrenada | Matar 25 mobs con una mascota afuera | *"Las mascotas también tienen que pelear."* |
| Jinete | Andar 1000 bloques en una montura | *"Probá que tu montura aguanta el viaje."* |

#### Difíciles (1500$ + material)
| Misión | Qué hay que hacer | Premio extra |
|---|---|---|
| Expedición a las Minas | Terminar las Minas Olvidadas | 1 Alma Corrupta |
| Cazador de jefes | Derrotar a cualquier jefe | 1 Alma Corrupta |
| Pesadilla | Matar un élite de tier IV o V | 1 Chispa Astral (25%) |
| Mejora arriesgada | Hacer una mejora +5 o más en el Herrero | 2 Esencias de Élite |

**Racha:** terminar las 3 diarias 7 días seguidos da un premio extra (por ejemplo, una tirada gratis
en la Gacha de Armas).

---

### 5. Cosas nuevas que haría falta crear

- **Ítems:** los 5 fragmentos (Marea, Pantano, Arena, Hielo, Fuego) y la Lámpara del Minero. Van en
  `items.py`, sin receta, y solo caen la primera vez que el jugador mata a cada jefe.
- **NPC:** el Cronista con su tablón de misiones.
- **Diálogos:** el Viajero y el Herrero tendrían que decir cosas distintas según el capítulo en el que vaya el jugador.
- **Título de chat:** "Portador de la Estrella".
- **Sistema de misiones:** un plugin (ver cuáles tiene Aternos) o algo armado con MythicMobs y
  contadores (scoreboard), como se hizo con las mascotas y la mazmorra.
