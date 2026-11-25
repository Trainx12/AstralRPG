# AstralRPG — instrucciones para Claude

## Coordinacion con Codex

El dueno pidio que Claude defina la estructura y Codex programe, pruebe y publique en GitHub. Para pedidos de implementacion, leer `docs/CLAUDE_CODEX.md`, escribir el plan en `.local/coordination/plan.md` e invocar `tools/invoke-codex-plan.mjs` con `--publish`. Esperar el resultado y revisarlo; no editar los mismos archivos mientras corre Codex. Luego continuar el despliegue en el panel de Empower desde el navegador si hay herramientas disponibles y sesion iniciada. Si no las hay, informar el despliegue pendiente. No afirmar que GitHub o el servidor estan actualizados sin comprobarlo. Para consultas sin cambios, responder directamente.

Servidor de Minecraft RPG sin mods (Paper 26.1.2 en Empower Servers, nodo Argentina, `103.106.58.173:7004`; panel https://gp.empowerservers.com/server/44d1ad66). Se mudo desde Aternos el 07/11/2026; el server de Aternos queda como copia hasta confirmar que no falta nada. El dueño habla en español rioplatense; responder en español, simple y sin jerga.

**Antes de tocar algo, leer:**
- `docs/GUIA.md` — mapa del repo, dónde se agrega cada cosa, cómo subir al servidor y trucos que ya nos costaron.
- `docs/SERVIDOR.md` — plugins, lobby, comandos de admin y problemas conocidos.

## Reglas
- **REGLA DEL DUEÑO (23/11/2026): nada nuevo llega al público sin diseño terminado y sin que el dueño lo pruebe en su sala de admin (`/modo admin`, `/sala`).** Antes de eso se sube oculto (permiso solo para ByTrainx, solo en la sala o apagado). Abrirlo a todos es un paso aparte y solo con su OK. Orden: primero que funcione, después el diseño, después la prueba del dueño, recién ahí público.
- Todo sale de generadores en `datapack-src/` (Python). Se edita el `.py`, se regenera `build/`, commit + push, y después se sube al servidor. No editar a mano lo que está en `build/`.
- El repo es **público**: nunca commitear contraseñas (van en `docs/CREDENCIALES.local.md`, ignorado) ni mapas de terceros.
- El dueño inicia sesión en el panel en el navegador; Claude no escribe contraseñas.
- Empower: Startup → Docker Image tiene que ser **Java 25**; en Versions → Install dejar apagado **Wipe Server Files**; `management-server-enabled=false` (el panel le pone el puerto 7004 y choca con el juego). Ver docs/SERVIDOR.md.
- El datapack nuevo se toma al reiniciar. Las configs de plugins se editan con el editor de Files y se recargan (`mm reload`, `crates reload`, `tab reload`, `papi reload`, `essentials reload`, `bettermodel reload`).
- Si cambia `build/AstralRPG-Textures.zip`: subir a R2 con `python tools/subir_pack_r2.py` (mismo nombre y URL fija), verificar descarga publica y actualizar `resource-pack-sha1` en `server.properties`. Reiniciar. El push sigue publicando el codigo; no actualiza R2 solo.
- Commit y push solo cuando el dueño lo pide o lo aprueba para subir al server.

## Comandos de generación (desde `datapack-src/`)
```
python build.py                    # datapack (ítems, recetas, Forja, guía, élites)
python gui_textures.py <gui>       # ventanas piedra/oro + HUD RPG (hud_rpg.py) -> pack-source/gui
python build_pack.py pack-source   # resource pack
python mobs/build_models.py        # modelos 3D de criaturas (.bbmodel)
python mobs/mythic.py              # MythicMobs: criaturas, monturas, jefes, vendedores
python mobs/mazmorra.py           # Mazmorra Minas Olvidadas (salas, mobs, jefe, cofre)
python mobs/mascotas.py           # Mascotas 3D (/mascotas, bonus, niveles)
python lobby.py                    # gachas (CrazyCrates), cobro, TAB (tabulador + panel de minas), comandos del lobby
python betterhud.py                # BetterHud apagado por defecto y /sb para TAB; conservar pack-source/betterhud
python mazmorras_copias.py         # 6 copias por mazmorra: entrada (mazentrar), /party y 8 min tras el jefe
python infinita.py                 # Mazmorra Infinita: /infinita, 6 salas, tier y velocidad, sube cada 10 min
python panel_mundos.py             # panel lateral segun el mundo (TAB): infinita, mini juegos, arenas, survival
python duelos.py                   # Duelos dentro de /arenas: /desafiar (Skript) y arenas de Duels
python oceano_fosa.py              # Fosa del Crustaceo: jefe (MythicMobs) y comandos; la arena (terceros) vive en .local/acuatico
python oceano.py --java <java25>   # Oceano Astral: plugin AstralOceano (generador, sin aire, /oceano, regenera c/3 dias) + aviso
python menus.py                    # menus de cofre (DeluxeMenus): /menu, /mascotas, gachas, bazar, cofre del jefe y /fragmentos
python clases.py --jdk <java25>    # clases Segador/Invocador/Asesino: plugin AstralClases + invocacion MythicMobs (armaduras y libros salen con build.py); deploy_clases.py arma el FINAL
python mobs/trainx.py              # jefe final Trainx (modelo privado con la skin del dueno); la pelea sale con mobs/mazmorra.py
python renacimiento.py             # renacimiento, deseos (/deseo, /deseos) y deseo lite del Cronista
python rankings.py                 # rankings semanales (parkour, Infinita, Trainx, Minas, Bosque), carteles y /trofeos
python efectos.py --jdk <java25>   # efectos visuales: plugin AstralEfectos (/efectos Bajo/Medio/Alto, astralfx para jefes) + dibujos del pack
python portales.py --jdk <java25>  # menu/llegadas de portales + plugin AstralPortales (Nether Hub <-> portales_astrales, proteccion)
python armas_mod.py                # armas T6-T10, guante y ballestas con modelos de mods (solo circuito privado) + pack FINAL
python mochilas3d.py               # mochilas 3D (forma de Wet Backpacks, solo privado)
python armas_planas3d.py           # cuchillos T1-T10 y equipo de las Mareas en 3D (solo privado)
python deploy_modelos_efectos.py   # FINAL privado de mochilas, cuchillos, efectos y Fenix (build/deploy/modelos-3d-efectos.md)
python gemas.py --jdk <java25>     # Reforja de gemas: Skript, AstralGemas.jar, texturas; deploy_gemas.py arma la entrega
python cavernas.py --jdk <java25>  # Cavernas de Cristal: plugin AstralCavernas, MythicMobs, aviso; deploy_cavernas.py arma la entrega
python bazar.py --jdk <java25>     # Bazar privado: AstralBazar.jar, config/productos y entrega; docs/BAZAR_FASE1.md
python llegada_survival.py         # 3 s sin dano al llegar/reaparecer/conectarse en el Survival -> build/gameplay/astral_llegada.sk
python ancestral_evento.py         # jefe ancestral cada 3 h al lado de un jugador del Survival; se va si el elegido se aleja/cambia de mundo (solo ByTrainx hasta /ancestral publico) -> build/gameplay/astral_ancestral.sk (+ mobs/mythic.py)
python tpa_survival.py            # /tpa solo dentro del Survival (sin Nether Hub) -> build/gameplay/astral_tpa.sk + permisos en tpa_comandos.txt
python regen_fuera_pelea.py        # curacion fuera de pelea (20 s sin dano, 4%/s, sin comida; solo ByTrainx hasta /regenfuera publico) -> build/gameplay/astral_regen.sk
python mesa_encantamientos.py --jdk <java25>  # mesa de encantamientos AstralMesa (reemplaza LynExp): todos los encantamientos menos las mejoras del Herrero
python bosque_talar.py             # Bosque Astral 300x300: script (443 arboles de bosque_arboles.json); mapa con tools/bosque_mapa.py, bosque_armar.py, bosque_arboles.py
python minas_decor.py              # decoracion de cada Mina Astral con su mineral (comandos WorldEdit de consola, ver docs/MINAS.md)
python ee_descripciones.py <enchants del server>  # descripciones de ExcellentEnchants en espanol -> build/excellentenchants (subir y reiniciar)
python encantamientos_balance.py   # Temple nerfeado y proporcional (+10%/nivel x vida que falta) -> build/gameplay/astral_temple.sk; el de EE queda en 0 (AJUSTES en ee_descripciones.py); solo ByTrainx hasta /temple publico
python anticheat.py <plugins/GrimAC generado>  # GrimAC SOLO AVISA (sin castigos ni setbacks) -> build/anticheat (docs/SERVIDOR.md)
python traducciones.py --parchar  # plugins en espanol: mensajes traducidos -> build/traducciones + parches de idioma -> .local/traduccion/subir (docs/SERVIDOR.md)
```

## Trampas conocidas
- MythicMobs: skills con `: ` rompen el YAML (usar comillas simples). En `~onInteract`, condiciones del jugador con `?~` (ej. `?~hascurrency{a=1000}`). Comandos como jugador: `command{c="sudo <trigger.name> ..."}`.
- MythicMobs: `@NearestPlayer` no encuentra a jugadores en creativo. Para asignar un dueño usar el nombre (`@PlayerByName{name=<global.var>}`), como las mascotas.
- ClearLag: el limitador de apariciones cancela mobs de plugins salvo que `exempt-spawn-reasons` incluya `CUSTOM` (ver docs/SERVIDOR.md).
- CrazyCrates: `crates preview` solo funciona como jugador (usar `sudo`); `crates forceopen <caja> <jugador>` abre gratis.
- Lobby: WorldGuard bloquea mobs; para spawnear vendedores, `mob-spawning allow` un momento (ver `build/lobby/comandos.txt`).
- Spam en el chat de los OP ("Se ha cambiado la puntuación..."): en `server.properties` `broadcast-console-to-ops=false` y gamerule `log_admin_commands false`; en skills que corren seguido, filtrar a quién se aplica (`@a[scores={x=1..}]`).
- Memoria de codigo (Metaspace): en Aternos estaba limitada a 350 MB y el 02/11 se colgo con `OutOfMemoryError: Metaspace`. En Empower no hay tope (8 GB, `-Xmx6400M`). Igual cada `mm reload`/`skript reload` deja 2-3 MB pegados: tras muchas recargas, reiniciar. Medir con spark antes y despues de sumar plugins.
- Datapack: `@e[...]` sin `distance`/`x,y,z` recorre TODOS los mundos aunque vaya despues de `execute in <mundo>` (asi `tanda2/tick` hacia 84 recorridas/s y corria cada sala 6 veces; arreglado 24/11 sin cambiar el ritmo). Para limitar al mundo, `distance=0..`. No poner `@e` global en `tick`: usar una marca (ej. `#flechas astral.tmp`).
- Mobs del datapack: nunca `PersistenceRequired` en mobs que aparecen solos (los elites se acumulaban: 115 brujas). Variables de Skript que cambian cada tick: siempre `{-...}` (solo memoria).
- Plugins sacados por memoria en Aternos el 03/11/2026: QuickShop-Hikari, Duels, SkinsRestorer, DonutOrders y AxShulkers. En Empower se pueden reinstalar si el dueño lo pide (sus datos viejos siguen en `plugins/`). Duels volvió el 08/11/2026. El Bazar usa AxTrade (`/trade`) en lugar de Ordenes.
- BetterHud (apagado; el panel vuelve a TAB, `docs/BETTERHUD_Y_DUELS.md`): sus glifos van en nuestro pack y tienen que coincidir con la config del server: si cambia el arte o layout de `betterhud.py`, rearmar `pack-source/betterhud` (apagar el HUD y cambiar `/sb` no requiere rearmarlo). En sus textos `/` se escribe `//`. Ningún jefe puede usar barra `YELLOW` (BetterHud la vuelve invisible).
- Escala por tier (03/11/2026): dano de armas Astral y vida de mobs REALES y enormes (x5 por tier); vida del jugador, armadura y dano de mobs normales. Todo sale de `datapack-src/escala.py` (ver `docs/ESCALA_TIERS.md`). `spigot.yml` necesita los topes de atributos subidos; PvP de arena se divide en `astral_gameplay.sk`. DamageIndicator y LevelledMobs se sacaron.
- Minas Astrales (`docs/MINAS.md`): Skript puro, **sin skript-reflect** (se hizo asi por Aternos; en Empower ya se pueden subir `.jar`). Los schematics no van al repo (el de Hierro es de terceros).

Tanda 1 (10/11): panel general de TAB con `/sb` persistente; BetterHud `default-hud: []`. Conservar fuentes y shader combinado con Stellarity. Entrega sin desplegar: `build/deploy/tanda1.md`.

## Assets privados (tanda 4a)

Leer `docs/TERCEROS.md`. `ASTRAL_PRIVADO` (por defecto `.local/terceros/AstralRPG-privado`) guarda originales y derivados. `build/AstralRPG-Textures.zip` publico nunca contiene ese arte; el pack FINAL esta en el build privado. No copiar assets de BetterModel privados a `pack-source`. Subir a R2 pasando el ZIP FINAL a `tools/subir_pack_r2.py`; auditar con `tools/verificar_terceros.py` antes del commit publico. Entrega: `build/deploy/tanda4a.md`.
