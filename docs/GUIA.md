# Guía para agregar cosas a AstralRPG

Mapa de dónde está cada cosa, cómo se agrega algo nuevo y cómo se sube a Aternos.
La parte de administración (plugins, comandos, problemas conocidos) está en [SERVIDOR.md](SERVIDOR.md).

> Regla de oro: **nada se edita a mano en el servidor si sale de un generador.** Se cambia el `.py` en
> `datapack-src/`, se regenera, se hace commit y push, y recién ahí se sube a Aternos. Así el repo siempre
> tiene la versión buena y se puede rearmar todo.

---

## 1. Mapa del repositorio

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

## 2. Cómo agregar cada cosa

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
| Un título nuevo para la gacha | `lobby.py` (`TITLES`) | `python lobby.py` | igual que arriba |
| Una línea del panel lateral o del tabulador | `lobby.py` (`TAB_SECTIONS`) | `python lobby.py` | `plugins/TAB/config.yml` (reemplazar esa sección) + `tab reload` |
| Rangos (Novato...Leyenda) | `lobby.py` (`RANKS`) | `python lobby.py` | igual que arriba |
| Precios de la tienda vanilla | En el server: `plugins/EconomyShopGUI/shops/*.yml` (no está en el repo) | — | `sreload` |
| Plata inicial, saldo mínimo | En el server: `plugins/Essentials/config.yml` (`starting-balance`, `min-money`) | — | `essentials reload` |

### Tips por tema

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

## 3. Cómo subir cambios a Aternos

### Lo básico
1. Regenerar con Python, commit y push a `main` (Aternos y los pasos de abajo leen de GitHub).
2. Entrar al panel de Aternos (el dueño inicia sesión; la clave está en `docs/CREDENCIALES.local.md`).
3. Subir o editar los archivos (ver abajo).
4. Recargar el plugin o reiniciar, y mirar la consola por errores.

### Qué se recarga sin reiniciar
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

### Cómo se editan archivos en Aternos (trucos)
- **Archivos que ya existen** (configs de plugins): Files → abrir el archivo → pegar el contenido nuevo → Save. Si Aternos avisa "This file contains syntax errors", el YAML está roto: no guardar.
- **Archivos nuevos dentro de `plugins/...`**: botón *New file* (el ícono al lado de *New folder*), ponerle el nombre y después abrirlo y pegar el contenido. En las carpetas de plugins **no hay botón Upload**.
- **En la raíz de Files no se pueden crear carpetas** ("Access denied").
- **`world/datapacks` sí tiene Upload**: Upload → Files.
- **Nunca usar Worlds → Upload en la fila `world`: reemplaza el mundo entero** (así se perdió el primer mundo). Para un mundo nuevo: crearlo con Multiverse y subir sus `region/*.mca` con el server apagado.
- En Paper 26.1 todos los mundos están en `world/dimensions/minecraft/<overworld|the_nether|the_end|lobby>/`.

### Resource pack
Cada vez que cambia `build/AstralRPG-Textures.zip`:
1. Commit y push.
2. Esperar a que `https://raw.githubusercontent.com/Trainx12/AstralRPG/main/build/AstralRPG-Textures.zip` devuelva el archivo nuevo (puede tardar unos minutos).
3. Poner el sha1 nuevo en `server.properties` → `resource-pack-sha1` (en Aternos: Files → server.properties → Resource pack SHA-1).
4. Reiniciar.

---

## 4. Modelos de criaturas → resource pack

Los modelos `.bbmodel` los convierte BetterModel en el servidor. Para que el resource pack los tenga:
1. `python mobs/build_models.py` y `python mobs/mythic.py`.
2. Levantar un servidor de prueba local con BetterModel y los `.bbmodel` (o usar el de Aternos) para que genere `plugins/BetterModel/build/assets`.
3. Copiar esa carpeta `assets` a `datapack-src/pack-source/bettermodel/assets`.
4. `python build_pack.py pack-source` → nuevo `AstralRPG-Textures.zip` → seguir los pasos de "Resource pack".
5. Subir los `.bbmodel` a `plugins/BetterModel/models/` y `bettermodel reload`.

---

## 5. Lobby: qué vive solo en el servidor

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

## 6. Servidor de prueba local

Sirve para probar MythicMobs, BetterModel y el datapack sin tocar Aternos (sin economía ni gachas).
- Hubo uno en la carpeta temporal de Claude (`.../scratchpad/testsrv`, con su propio Java 25 en `jdk/`). Esas carpetas se pueden borrar; si no está, se rearma bajando Paper 26.1.2 y los mismos plugins.
- Arrancarlo, esperar a que cargue, y mirar el log buscando `Loaded N mobs`, `models are loaded` y errores.

---

## 7. Cosas importantes que no hay que olvidar

- **El repo es público.** Nunca commitear contraseñas; van en `docs/CREDENCIALES.local.md` (ignorado por Git). Tampoco subir mapas de terceros al repo.
- **No hay backups automáticos** salvo que se vincule Google Drive en Aternos → Backups. Bajar el mundo de vez en cuando.
- **Aternos apaga el server cuando no hay nadie.** Si al entrar sale `cookie_request`, es que está apagado: prenderlo desde el panel.
- **AuraSkills necesita el preset `legacy.zip`** para que existan Forja y Hechicería.
- **Versiones fijas:** Paper 26.1.2, Stellarity 5.4.2 (la 6.x crashea), ExcellentEnchants 5.4.3 con NightCore 2.16.7. No usar ExcellentCrates (la 7.x no se puede configurar por archivo y la 6.x no anda con este NightCore).
- **Chat de los OP lleno de "Se ha cambiado la puntuación...":** es la regla `log_admin_commands`; está apagada en los 5 mundos (ver `build/lobby/comandos.txt`). Si se crea un mundo nuevo, apagarla también ahí.
- **Un comando nuevo de DeluxeMenus sale en rojo en el chat pero funciona:** el juego del jugador no lo conoce hasta que vuelve a entrar.
- **Los huevos de monturas y mascotas no funcionan en el lobby** (no aparecen mobs ahí): se usan en el mundo.
- Después de cualquier cambio: revisar la consola. Los avisos `ExampleQuest...` de MythicMobs y los de GeoIP de AuthMe son normales.
