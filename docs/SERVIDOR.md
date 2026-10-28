# AstralRPG: cómo está armado el servidor

Documento de referencia para administrar el servidor. Actualizado el 28/10/2026.
Para saber dónde está cada cosa en el repo y cómo agregar cosas nuevas, ver [GUIA.md](GUIA.md).

> **Contraseñas:** este repositorio es público, así que acá no va ninguna contraseña.
> El usuario y la contraseña de Aternos están en `docs/CREDENCIALES.local.md`. Ese archivo existe solo
> en la PC del dueño y Git lo ignora, así que no se sube a GitHub.
> Como la contraseña de Aternos se compartió por chat, conviene cambiarla y actualizar ese archivo.

## Servidor

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

## Plugins

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
| CrazyAuctions (26.1.2) | Subastas entre jugadores (`/ah`), 5% de impuesto por venta |
| QuickShop-Hikari 6.3.0.3 | Cofres-tienda de los puestos del bazar (5% de impuesto por venta) |

## Lobby (mundo `lobby`)

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

## Bazar y subastas (lobby)

- **Bazar:** sala de piedra adentro del edificio grande del norte, detrás del vendedor de la tienda. 4 puestos contra la pared del fondo (x 171-185, z 149-150, pies en y 101), con 2 cofres cada uno y un cartel flotante (tag `astral_bazar`).
- **Alquiler:** con el aldeano *Administrador del Bazar* (`astral_npc_bazar`): clic → menú en el chat con el estado de cada puesto (libre / tuyo / ocupado) y botones (`/trigger bazar`). Cuesta 5.000$ por 7 días, se puede renovar y hay un puesto por jugador. Por dentro: grupo temporal de LuckPerms `puestoN` (miembro de la región `puestoN` de WorldGuard) y permiso temporal `astral.puesto.N` en el grupo `default` (marca que está ocupado). Todo vence solo.
- Cuando otro alquila un puesto vencido, se borran las tiendas del inquilino anterior (`qs removeall`) y se vacían los cofres.
- **Tiendas:** QuickShop. Con el ítem en la mano, clic izquierdo a un cofre del puesto y escribir el precio en el chat. 5% de impuesto por venta.
- **Subastas:** `/ah` (CrazyAuctions) o el aldeano *Subastas* (`astral_npc_subastas`). 5% de impuesto por venta.
- Valores en `datapack-src/lobby.py` (`PUESTOS`, `RENTA`, `RENTA_DIAS`); armado en `build/lobby/comandos.txt` (sección BAZAR Y SUBASTAS).

## Mazmorra: Minas Olvidadas (mundo `mina`)

Mundo vacío de Multiverse con el mapa `dungeon1-endlessxl.schem` (de terceros: **no está en el repo**, se sube directo a `plugins/WorldEdit/schematics/`) pegado con `//paste -o` (la esquina queda en -73 -55 -290). Dificultad difícil, sin mobs naturales, `keep_inventory` activado, protegido con WorldGuard.

- **4 salas** que se recorren con teletransporte: 1) Campamento Minero (mineros corruptos y esqueletos), 2) Lago Subterráneo (ahogados + mini jefe Capataz Ahogado), 3) Túneles de Soporte (arañas, esqueletos + mini jefe Gólem de Piedra Antiguo), 4) Salón del Guardián (jefe final con fases).
- Cada sala tiene un controlador invisible (`astral_mina_control_salaN`): al llegar un jugador larga las oleadas, cuando no quedan mobs pasa a la siguiente, y si la sala se queda vacía se reinicia sola. Con 2 o más jugadores aparecen mobs extra.
- **Cofre final:** materiales de élite, 2500$ y 25% de Chispa Astral. Se cobra una vez cada 30 minutos por jugador (permiso temporal `astral.mina.cd` de LuckPerms); se puede volver a entrar sin premio. Después de 15 segundos vuelven al lobby.
- **Entrada:** vendedor `astral_npc_mina` en el lobby. Salir: `/spawn`.
- Todo sale de `datapack-src/mobs/mazmorra.py`; el armado (crear el mundo, pegar el mapa, poner los controladores) está en `build/mazmorra/comandos.txt`.

## Datapacks (`world/datapacks`)

Tienen que estar antes de generar un mundo nuevo, si no, no aparecen sus estructuras. Se suben con Files → `world/datapacks` → Upload → Files.

- **AstralRPG-Items.zip**: el nuestro. Tiene ítems, recetas, Forja Astral, guía, élites, taladros y motosierras.
- Dungeons and Taverns 5.2.0 y DnT Stronghold Overhaul 2.4.0: estructuras.
- Incendium 5.4.12: Nether.
- Stellarity 5.4.2: End. La 6.0.1 crasheaba en 26.1.2, por eso quedó la 5.4.2.

## Resource pack

- Se sirve desde `https://raw.githubusercontent.com/Trainx12/AstralRPG/main/build/AstralRPG-Textures.zip`.
- Es obligatorio (`require-resource-pack=true`).
- Incluye las texturas originales del dueño (`assets/astral`, `assets/armasrpg`), las armaduras de Mago, Berserker y Arquero, las texturas CC0 (créditos en `datapack-src/pack-source/cc0/CREDITOS.txt`), los taladros y motosierras, y los modelos de BetterModel.
- Después de cambiarlo: commit y push, esperar a que GitHub sirva el archivo nuevo (puede tardar unos minutos) y recién ahí poner el sha1 nuevo en `server.properties`.

## Cómo cambiar cosas

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

## Comandos útiles (como OP o desde la consola, sin `/`)

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
| `bettermodel reload` | Recargar modelos (tienen que ser 20: 17 criaturas + 3 cofres) |
| `bolt edit add <amigo>` y clic en la caja | Compartir un cofre o shulker protegido |
| `bolt trust` | Confiar todas tus protecciones a un amigo |
| `bolt info` y clic | Ver de quién es una protección |

## Sistemas del juego (resumen)

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

## Problemas conocidos y soluciones

- Avisos de MythicMobs sobre `ExampleQuest...`: son de los ejemplos que trae el plugin, no afectan nada.
- Aviso de Paper "4 releases behind": se queda en 26.1.2 a propósito, porque los plugins están probados ahí.
- Errores de GeoIP de AuthMe: no afectan.
- Error al entrar `Failed to decode packet 'clientbound/minecraft:cookie_request'`: el servidor está apagado y responde la sala de espera de Aternos, que no es compatible con el cliente 26.1. Prender el servidor desde el panel y entrar cuando diga Online.
- Si alguien no ve texturas: que acepte el resource pack al entrar. Si sigue igual, revisar que el sha1 coincida.
- Si aparece "Unknown skill": cargar el preset legacy de AuraSkills (ver comandos).
- El área de los taladros puede romper bloques dentro de una zona de WorldGuard si picás justo en el borde.

## Servidor de prueba local

Para probar sin tocar Aternos hubo una copia del servidor (mismos plugins, sin economía) en la carpeta temporal de Claude. Esas carpetas se pueden borrar; se rearma bajando Paper 26.1.2 y los mismos plugins. El mundo de prueba es plano. Detalles en [GUIA.md](GUIA.md#6-servidor-de-prueba-local).

## Comandos de admin del lobby y la economía

| Comando | Qué hace |
|---|---|
| `eco give <jugador> <monto>` | Dar plata (`eco take` / `eco set` para sacar o fijar) |
| `lp user <jugador> meta setprefix 100 &b&l«ASTRAL»` | Dar un título (`meta removeprefix 100` lo saca) |
| `loot give <jugador> loot astral:item/<id>` | Dar cualquier ítem de AstralRPG |
| `mm egg give <jugador> astral_<montura> 1` | Huevo de montura o mascota (usar en el mundo, no en el lobby) |
| `crates forceopen <gacha_rpg\|gacha_monturas\|gacha_cosmeticos> <jugador>` | Tirada gratis |
| `mvtp <jugador> w:world` / `spawn` | Ir al mundo / al lobby |
| `mm mobs kill astral_npc_<nombre>` | Borrar un vendedor (se vuelve a poner con `build/lobby/comandos.txt`) |
