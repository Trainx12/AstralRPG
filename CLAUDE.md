# AstralRPG — instrucciones para Claude

## Coordinacion con Codex

El dueno pidio que Claude defina la estructura y Codex programe, pruebe y publique en GitHub. Para pedidos de implementacion, leer `docs/CLAUDE_CODEX.md`, escribir el plan en `.local/coordination/plan.md` e invocar `tools/invoke-codex-plan.mjs` con `--publish`. Esperar el resultado y revisarlo; no editar los mismos archivos mientras corre Codex. Luego continuar el despliegue en el panel de Empower desde el navegador si hay herramientas disponibles y sesion iniciada. Si no las hay, informar el despliegue pendiente. No afirmar que GitHub o el servidor estan actualizados sin comprobarlo. Para consultas sin cambios, responder directamente.

Servidor de Minecraft RPG sin mods (Paper 26.1.2 en Empower Servers, nodo Argentina, `103.106.58.173:7004`; panel https://gp.empowerservers.com/server/44d1ad66). Se mudo desde Aternos el 07/11/2026; el server de Aternos queda como copia hasta confirmar que no falta nada. El dueño habla en español rioplatense; responder en español, simple y sin jerga.

**Antes de tocar algo, leer:**
- `docs/GUIA.md` — mapa del repo, dónde se agrega cada cosa, cómo subir al servidor y trucos que ya nos costaron.
- `docs/SERVIDOR.md` — plugins, lobby, comandos de admin y problemas conocidos.

## Reglas
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
python menus.py                    # menus de cofre (DeluxeMenus): /menu, /mascotas, gachas, bazar, cofre del jefe y /fragmentos
```

## Trampas conocidas
- MythicMobs: skills con `: ` rompen el YAML (usar comillas simples). En `~onInteract`, condiciones del jugador con `?~` (ej. `?~hascurrency{a=1000}`). Comandos como jugador: `command{c="sudo <trigger.name> ..."}`.
- MythicMobs: `@NearestPlayer` no encuentra a jugadores en creativo. Para asignar un dueño usar el nombre (`@PlayerByName{name=<global.var>}`), como las mascotas.
- ClearLag: el limitador de apariciones cancela mobs de plugins salvo que `exempt-spawn-reasons` incluya `CUSTOM` (ver docs/SERVIDOR.md).
- CrazyCrates: `crates preview` solo funciona como jugador (usar `sudo`); `crates forceopen <caja> <jugador>` abre gratis.
- Lobby: WorldGuard bloquea mobs; para spawnear vendedores, `mob-spawning allow` un momento (ver `build/lobby/comandos.txt`).
- Spam en el chat de los OP ("Se ha cambiado la puntuación..."): en `server.properties` `broadcast-console-to-ops=false` y gamerule `log_admin_commands false`; en skills que corren seguido, filtrar a quién se aplica (`@a[scores={x=1..}]`).
- Memoria de codigo (Metaspace): en Aternos estaba limitada a 350 MB y el 02/11 se colgo con `OutOfMemoryError: Metaspace`. En Empower no hay tope (8 GB, `-Xmx6400M`). Igual cada `mm reload`/`skript reload` deja 2-3 MB pegados: tras muchas recargas, reiniciar. Medir con spark antes y despues de sumar plugins.
- Mobs del datapack: nunca `PersistenceRequired` en mobs que aparecen solos (los elites se acumulaban: 115 brujas). Variables de Skript que cambian cada tick: siempre `{-...}` (solo memoria).
- Plugins sacados por memoria en Aternos el 03/11/2026: QuickShop-Hikari, Duels, SkinsRestorer, DonutOrders y AxShulkers. En Empower se pueden reinstalar si el dueño lo pide (sus datos viejos siguen en `plugins/`). Duels volvió el 08/11/2026. El Bazar usa AxTrade (`/trade`) en lugar de Ordenes.
- BetterHud (apagado; el panel vuelve a TAB, `docs/BETTERHUD_Y_DUELS.md`): sus glifos van en nuestro pack y tienen que coincidir con la config del server: si cambia el arte o layout de `betterhud.py`, rearmar `pack-source/betterhud` (apagar el HUD y cambiar `/sb` no requiere rearmarlo). En sus textos `/` se escribe `//`. Ningún jefe puede usar barra `YELLOW` (BetterHud la vuelve invisible).
- Escala por tier (03/11/2026): dano de armas Astral y vida de mobs REALES y enormes (x5 por tier); vida del jugador, armadura y dano de mobs normales. Todo sale de `datapack-src/escala.py` (ver `docs/ESCALA_TIERS.md`). `spigot.yml` necesita los topes de atributos subidos; PvP de arena se divide en `astral_gameplay.sk`. DamageIndicator y LevelledMobs se sacaron.
- Minas Astrales (`docs/MINAS.md`): Skript puro, **sin skript-reflect** (se hizo asi por Aternos; en Empower ya se pueden subir `.jar`). Los schematics no van al repo (el de Hierro es de terceros).

Tanda 1 (10/11): panel general de TAB con `/sb` persistente; BetterHud `default-hud: []`. Conservar fuentes y shader combinado con Stellarity. Entrega sin desplegar: `build/deploy/tanda1.md`.
