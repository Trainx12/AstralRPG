# Guía para agregar cosas a AstralRPG

Tanda 5a (preparada, sin desplegar): [entrega](../build/deploy/tanda5a.md).
Para proteger terreno en survival: pala de oro y clic derecho en dos esquinas. Minimo 6x6;
protege todo de fondo a techo. Se empieza con 36 bloques de area, sin ganar por tiempo.
`/shop` → Proteccion agrega area: 36 + 25 = 61, **no** un cuadrado 11x11.
Puede repartirse entre varias zonas, cada una de al menos 36 bloques.
`/trust jugador` comparte, `/untrust jugador` quita acceso y `/abandonclaim` libera la zona.
`/shop` → Mochilas compra un permiso permanente para 9, 27 o 54 espacios; `/bp` abre.
La mochila es virtual, persiste al morir y su contenido no pasa a AxGraves. No admite shulkers ni bundles.
Balance: `escala.py`; precios/probabilidades/configuraciones: `tanda5a.py`;
versiones verificadas: `tanda5a-versions.json`. Regenerar datapack con `build.py`
y luego `tanda5a.py --java <java25> --server <Paper-local>` para compilar el runtime propio.

NPC Tienda y decoracion: `deploy_tienda.py` prepara la entrega aislada sobre el pack
instalado, `preview_decor.py` renderiza las alas con pechera solo en privado y
`tools/probar_decor_paper.py` prueba AstralDecor con WorldGuard y reinicio local.
Ver [tienda-modelo.md](../build/deploy/tienda-modelo.md); no instalar el plugin de prueba en remoto.

Entrega conjunta posterior (sin desplegar): [yeti-bastones-guia.md](../build/deploy/yeti-bastones-guia.md).
`deploy_yeti.py` conserva el FINAL de Tienda y prepara YAML privados aislados;
`preview_plush.py` deja las vistas de peluches solo en privado. Usar la lista conjunta
para instalar ambas tareas en un reinicio. Lobby no admite colocar peluches, tampoco OP.

Mapa de dónde está cada cosa, cómo se agrega algo nuevo y cómo se sube al servidor (Empower Servers).
La parte de administración (plugins, comandos, problemas conocidos) está en [SERVIDOR.md](SERVIDOR.md).

> Regla de oro: **nada se edita a mano en el servidor si sale de un generador.** Se cambia el `.py` en
> `datapack-src/`, se regenera, se hace commit y push, y recién ahí se sube al servidor. Así el repo siempre
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
│   ├── IDEAS.md              Ideas pendientes del dueño, ordenadas por trabajo
│   ├── BOSQUE.md             Bosque Astral: tala con árboles que vuelven a crecer
│   └── CREDENCIALES.local.md Claves del servidor (solo en tu PC, Git lo ignora)
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
    ├── AstralRPG-Textures.zip      resource pack (el servidor lo baja de R2)
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
| Daño por tier, vida de mobs, maná de bastones, vida mostrada | `datapack-src/escala.py` (ver `docs/ESCALA_TIERS.md`) | `python build.py`, `python gameplay.py`, `python lobby.py` | datapack + scripts + TAB |
| Una receta o lógica (hechizos, forja, guía) | `datapack-src/build.py` | `python build.py` | datapack |
| Armas especiales independientes (rayo, saltos, sismo, estallido) | `special_weapons.py`, `special_weapons.sk`, `special_weapons3d.py`; ver `docs/ARMAS_ESPECIALES.md` | `python build.py` y `python build_pack.py pack-source` | datapack + resource pack + script (`special_weapons.sk` en el servidor) |
| Forma 3D o colores de un arma (bastones, guadanas, espadas, hachas, arcos, Guantes Meteoro) | `datapack-src/varitas3d.py` (bastones y motor), `guadanas3d.py` o `armas3d.py` (una funcion por arma; los arcos tienen 4 modelos: quieto y 3 de tensado) | `python varitas3d.py`, `python guadanas3d.py` o `python armas3d.py` (vista previa en `build/previews/`) y `python build_pack.py pack-source` | resource pack |
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
| Panel de la derecha y `/sb` | `lobby.py` (TAB); `betterhud.py` (apagado y toggle) | `python lobby.py`, `python betterhud.py` | TAB y `astral_panel.sk`; ver `build/deploy/tanda1.md` |
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

## 3. Cómo subir cambios al servidor (Empower)

Desde el 07/11/2026 el servidor está en Empower Servers (`103.106.58.173:7004`). Datos y trampas del panel en [SERVIDOR.md](SERVIDOR.md#empower-lo-que-hay-que-saber-07112026).

### Lo básico
1. Regenerar con Python, commit y push a `main` (el resource pack se publica aparte en R2).
2. Entrar al panel https://gp.empowerservers.com/server/44d1ad66 (el dueño inicia sesión).
3. Subir o editar los archivos en Files (ver abajo).
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
| Datapack (`AstralRPG-Items.zip`) | reemplazar en `world/datapacks` y reiniciar |
| Plugins nuevos | subir el `.jar` a `plugins/` y reiniciar |

### Cómo se editan archivos en Empower
- **Files** deja editar, crear, subir (también `.jar`) y descomprimir `.zip` en cualquier carpeta. Para muchos archivos: subir un `.zip` y usar *Unarchive*. También hay SFTP (misma clave que el panel).
- **Plugins:** bajar el `.jar` de Modrinth, Hangar o Spigot y subirlo a `plugins/`. La pestaña Plugins del panel solo tiene versiones viejas. *Pull* desde URL existe, pero corta después de ~5 descargas seguidas.
- **Versions → Install:** dejar apagado **Wipe Server Files** (borra todo el servidor).
- **No tocar Startup → Docker Image:** tiene que quedar en Java 25.
- Para un mundo nuevo: crearlo con Multiverse, o subir su carpeta a `world/dimensions/minecraft/` con el server apagado.
- En Paper 26.1 todos los mundos están en `world/dimensions/minecraft/<overworld|the_nether|the_end|lobby>/`.

### Resource pack
Cada vez que cambia `build/AstralRPG-Textures.zip`:
1. Commit y push.
2. Ejecutar `python tools/subir_pack_r2.py build/AstralRPG-Textures.zip` (boto3). Sube a R2 y compara el SHA-1 de la descarga publica; imprime solo URL + SHA-1. `--dry-run` no usa red ni claves.
3. Guardar la URL fija `https://pub-5e0d1c63a1554ba7b8e33b038e1a06fe.r2.dev/AstralRPG-Textures.zip` en `resource-pack` y el hash verificado en `resource-pack-sha1` de `server.properties`. Mantener el servidor apagado durante la actualizacion del pack y las propiedades.
4. Reiniciar.

---

## 4. Modelos de criaturas → resource pack

Los modelos `.bbmodel` los convierte BetterModel en el servidor. Para que el resource pack los tenga:
1. `python mobs/build_models.py` y `python mobs/mythic.py`.
2. Levantar un servidor de prueba local con BetterModel y los `.bbmodel` (o usar el servidor) para que genere `plugins/BetterModel/build/assets`.
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

**TAB:** `lobby.py` genera `build/lobby/TAB/secciones-config.yml`. En `plugins/TAB/config.yml` se reemplazan las secciones del archivo y se combinan las claves de `placeholders` y `placeholder-output-replacements` con las que ya existan. El panel usa las expansiones Statistic (tiempo jugado) y ScoreboardObjectives (misiones y minas). Para el panel de minas hay que copiar también el nuevo `astral_minas.sk` y recargarlo antes de ejecutar `tab reload`. `groups.yml` se reemplaza entero. Las animaciones (`astral_titulo`, `astral_ip`) se agregan al final de `animations.yml`.

Placeholders útiles para el panel o el tabulador: `%vault_eco_balance_formatted%`, `%player_health_rounded%`, `%player_max_health_rounded%`, `%player_level%`, `%auraskills_power%`, `%auraskills_<skill>%`, `%luckperms_prefix%`, `%statistic_mob_kills%`, `%server_tps_1_colored%`, `%condition:rango%`. Para probar uno: `papi parse <jugador> %placeholder%`.

---

## 6. Servidor de prueba local

Sirve para probar MythicMobs, BetterModel y el datapack sin tocar el servidor (sin economía ni gachas).
- Hubo uno en la carpeta temporal de Claude (`.../scratchpad/testsrv`, con su propio Java 25 en `jdk/`). Esas carpetas se pueden borrar; si no está, se rearma bajando Paper 26.1.2 y los mismos plugins.
- Arrancarlo, esperar a que cargue, y mirar el log buscando `Loaded N mobs`, `models are loaded` y errores.

---

## 7. Cosas importantes que no hay que olvidar

- **El repo es público.** Nunca commitear contraseñas; van en `docs/CREDENCIALES.local.md` (ignorado por Git). Tampoco subir mapas de terceros al repo.
- **Respaldos:** El dueno contrato el servicio pago **Respaldos Diarios** de Empower: cada 4 horas, fuera del servidor y administrado por Empower. En el panel hay un respaldo manual bueno del 10/11 (558 MB). Los backups del panel fallan con carpetas que cambian; `.pteroignore` en la raiz excluye `logs`, `cache`, `.cache`, `libraries`, `versions`, `crash-reports`. La tarea programada del panel "Backup diario" fallo en la prueba (0 MB); no contar con ella como respaldo valido.
- **El servidor está prendido 24/7** en Empower. Si no conecta, mirar en el panel que diga Running y revisar la consola.
- **AuraSkills necesita el preset `legacy.zip`** para que existan Forja y Hechicería.
- **Versiones fijas:** Paper 26.1.2, Stellarity 5.4.2 (la 6.x crashea), ExcellentEnchants 5.4.3 con NightCore 2.16.7. No usar ExcellentCrates (la 7.x no se puede configurar por archivo y la 6.x no anda con este NightCore).
- **Chat de los OP lleno de "Se ha cambiado la puntuación...":** es la regla `log_admin_commands`; está apagada en los 5 mundos (ver `build/lobby/comandos.txt`). Si se crea un mundo nuevo, apagarla también ahí.
- **Un comando nuevo de DeluxeMenus sale en rojo en el chat pero funciona:** el juego del jugador no lo conoce hasta que vuelve a entrar.
- **Los huevos de monturas y mascotas no funcionan en el lobby** (no aparecen mobs ahí): se usan en el mundo.
- Después de cualquier cambio: revisar la consola. Los avisos `ExampleQuest...` de MythicMobs y los de GeoIP de AuthMe son normales.

## Estrella del Menu (slot 9)

Cada jugador recibe una Estrella del Nether **Menu Astral** en el slot 9 de la barra,
tambien en creativo y en arena. Clic derecho o izquierdo abre `/menu`, un cofre con
iconos vanilla, saldo y accesos a servicios. Ese slot queda reservado: si tenia un
objeto, se mueve a un slot libre del inventario; si el inventario esta lleno,
se suelta a los pies con todos sus componentes y cantidad. No se borra. La estrella se repone al entrar,
reaparecer, cambiar de mundo y cada 5 segundos. No requiere otro resource pack.

Generadores: `datapack-src/estrella_menu.py` y `menus.py`; `build.py` incorpora las
funciones `astral:menu_star/*` al datapack. Desde `datapack-src/`: `python estrella_menu.py`,
`python menus.py`, `python build.py`.

Subir `build/gameplay/astral_estrella.sk` a `plugins/Skript/scripts/astral_estrella.sk`,
`build/AstralRPG-Items.zip` a `world/datapacks/AstralRPG-Items.zip`, y los menus
`principal.yml` y `comandos.yml` de `build/menus/DeluxeMenus/gui_menus/` a la misma
carpeta dentro de `plugins/DeluxeMenus/gui_menus/`. Registrar `portales: {file: portales.yml}`
en `gui_menus` de `plugins/DeluxeMenus/config.yml` conservando las otras entradas.

**Apagar para reemplazar el datapack y volver a iniciar.** Luego `dm reload` y
`skript:skript reload astral_estrella` (usar el nombre completo evita el alias `sk`
de AuraSkills). El arranque ya carga el datapack; `minecraft:reload` solo si hace
falta recargarlo despues. Admin OP: `/estrella [jugador]`. La lista exacta y las
pruebas en juego estan en `build/gameplay/estrella-despliegue.txt`.

La proteccion cubre movimientos, drops, mano secundaria y ventas por inventario.
Las ventas directas `/sell`, `/sellall`, `/sellhand` y `/sellinventory` se redirigen
con un aviso a `/sellgui`, porque algunas variantes incluyen todos los slots.
`/ah sell` con la estrella seleccionada se cancela. La muerte quita la estrella de
los drops y del inventario antes de las tumbas; se entrega otra al reaparecer.
Revisar consola y comprobar estas interacciones en el servidor con AxTrade,
EconomyShopGUI, CrazyAuctions y AxGraves: las pruebas locales no sustituyen esa revision.


## Parkour y Arenas PvP

Los selectores `/parkour` y `/arenas`, sus aldeanos, llegadas OP y reglas salen de
`datapack-src/minijuegos.py` (listas `PARKOURS` y `ARENAS`). Regenerar con
`python menus.py`; incluye el Skript de gameplay actualizado, sin cambiar el resource pack.
Instalación, ZIP privados, coordenadas por revisar y pruebas en
[Parkour y Arenas](PARKOUR_Y_ARENAS.md). Lista exacta para el servidor:
`build/minijuegos/despliegue.txt`. Los mundos se instalan como destinos nuevos;
jamás se reemplaza `world`. Las arenas TFT requieren fijar su punto con OP antes de viajar.

Panel lateral actual: TAB (`lobby.py`), BetterHud apagado por defecto; `/sb` en `betterhud.py` controla TAB. Ver `build/deploy/tanda1.md`.

## Circuito de assets privados y dos packs

La tanda 4a incorpora un circuito separado: [pasos completos y tabla de mascotas](TERCEROS.md). El pack publico se regenera como siempre, sin arte privado. Preparar modelos con `python datapack-src/build_privado.py --prepare`, convertir TODOS los modelos en BetterModel local y combinar con `--assets <build/assets>`. El pack FINAL sale en `<ASTRAL_PRIVADO>/build/AstralRPG-Textures.zip`; ese es el que se pasa a `tools/subir_pack_r2.py` para el servidor. El publico sigue siendo reproducible sin el clon privado. Auditar los archivos versionados con `python tools/verificar_terceros.py` antes de publicar codigo. No copiar estos assets a pack-source ni commitearlos en el repo publico.

Correccion urgente del 11/11: `pack_audit.py` comprueba referencias de todos los modelos,
PNG del atlas y capas de armadura; `build_pack.py` y `build_privado.py --assets` la
ejecutan antes de reemplazar el ZIP. Los PNG reales fuera de item/block se normalizan;
los sprites sinteticos de adornos se validan contra las paletas declaradas del atlas.
`preview_pack_gui.py` renderiza los 31 items afectados desde el ZIP FINAL; su imagen
queda solo en el repositorio privado. `deploy_urgente.py` prepara la entrega aislada
y [la lista de instalacion](../build/deploy/urgente-mascotas-texturas.md).
Las llegadas de mazmorras se mantienen en `mobs/rutas_mazmorras.py`: cambiar esa tabla,
regenerar `mobs/mazmorra.py`, `viajes_mazmorras.py` y `build.py`, y correr `test_urgente`.
