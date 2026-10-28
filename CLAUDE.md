# AstralRPG — instrucciones para Claude

Servidor de Minecraft RPG sin mods (Paper 26.1.2 en Aternos, `AstralRPG2.aternos.me`). El dueño habla en español rioplatense; responder en español, simple y sin jerga.

**Antes de tocar algo, leer:**
- `docs/GUIA.md` — mapa del repo, dónde se agrega cada cosa, cómo subir a Aternos y trucos que ya nos costaron.
- `docs/SERVIDOR.md` — plugins, lobby, comandos de admin y problemas conocidos.

## Reglas
- Todo sale de generadores en `datapack-src/` (Python). Se edita el `.py`, se regenera `build/`, commit + push, y después se sube a Aternos. No editar a mano lo que está en `build/`.
- El repo es **público**: nunca commitear contraseñas (van en `docs/CREDENCIALES.local.md`, ignorado) ni mapas de terceros.
- El dueño inicia sesión en Aternos en el navegador; Claude no escribe la contraseña.
- **Nunca** indicar Worlds → Upload sobre la fila `world` en Aternos: reemplaza el mundo entero.
- Aternos no deja reemplazar el datapack con el server prendido. Las configs de plugins se editan con el editor de Files y se recargan (`mm reload`, `crates reload`, `tab reload`, `papi reload`, `essentials reload`, `bettermodel reload`).
- Si cambia `build/AstralRPG-Textures.zip`: push, esperar a que GitHub raw sirva el nuevo, y actualizar `resource-pack-sha1` en `server.properties`.
- Commit y push solo cuando el dueño lo pide o lo aprueba para subir al server.

## Comandos de generación (desde `datapack-src/`)
```
python build.py                    # datapack (ítems, recetas, Forja, guía, élites)
python build_pack.py pack-source   # resource pack
python mobs/build_models.py        # modelos 3D de criaturas (.bbmodel)
python mobs/mythic.py              # MythicMobs: criaturas, monturas, jefes, vendedores
python mobs/mazmorra.py           # Mazmorra Minas Olvidadas (salas, mobs, jefe, cofre)
python mobs/mascotas.py           # Mascotas 3D (/mascotas, bonus, niveles)
python lobby.py                    # gachas (CrazyCrates), cobro, panel TAB, comandos del lobby
python menus.py                    # menus de cofre (DeluxeMenus): /menu, /mascotas, gachas, bazar
```

## Trampas conocidas
- MythicMobs: skills con `: ` rompen el YAML (usar comillas simples). En `~onInteract`, condiciones del jugador con `?~` (ej. `?~hascurrency{a=1000}`). Comandos como jugador: `command{c="sudo <trigger.name> ..."}`.
- CrazyCrates: `crates preview` solo funciona como jugador (usar `sudo`); `crates forceopen <caja> <jugador>` abre gratis.
- Lobby: WorldGuard bloquea mobs; para spawnear vendedores, `mob-spawning allow` un momento (ver `build/lobby/comandos.txt`).
- `cookie_request` al entrar = el server está apagado.
