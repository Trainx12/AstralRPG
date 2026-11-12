# AstralRPG: cómo está armado el servidor

Tren lobby → survival preparado, **sin desplegar**: [archivos, ubicacion pendiente,
comandos y reinicio](../build/deploy/tren-lobby.md). TrainCarts 2.0.0-1720,
BKCommonLib 2.0.0-2018 y AstralTrain 1.0.0; tres plazas, espera de 5 s, recorrido de
8 bloques y destino individual cama/punto valido en `world`, o spawn de `world`.
Requiere confirmar el hueco y el anden dentro de la montaña antes de activarlo.
El Viajero conserva su comando actual `mvtp <jugador> w:world` como respaldo.

Tanda 5a preparada, **sin desplegar**: [lista exacta de archivos, versiones y pruebas](../build/deploy/tanda5a.md).
Generadores: `datapack-src/tanda5a.py`, `escala.py`, `runtime/AstralProgression.java`.
GriefPrevention 16.18.7: solo survival, 36 bloques iniciales, minimo 6x6, sin ganancia por hora,
proteccion completa de fondo a techo. EconomyShopGUI suma paquetes de area mediante consola;
`/buyclaimblocks` y venta directa quedan desactivados. Respeta WorldGuard; Bolt conserva sus candados.
BlzdBackpacks 1.0.0-alpha.1: mochila virtual `/bp`, permisos `blzdbp.small/medium/large`
para 9/27/54 espacios, vendidos en Mochilas. No hay objeto mochila para anidar; shulkers y bundles bloqueados.
El contenido virtual permanece al morir, separado de AxGraves. Requiere prueba de muerte/tumba en remoto antes de habilitar compras.
Se instala con servidor apagado y reinicio; no usar recarga general para JAR nuevos.
Los cuatro packs de estructuras van solo a `world/datapacks`, generan en chunks nuevos;
AstralProgression restringe sus estructuras fuera del survival y agrega loot sin sustituir tablas vanilla.

## Cosmeticos y SkinsRestorer preparados (11/11/2026)

**Sin desplegar.** [Entrega exacta, descarga, SHA-1 y reinicio](../build/deploy/cosmeticos-skins.md).
AstralDecor 1.3.0 agrega 20 sombreros y 2 alas a la coleccion permanente de
`/cosmeticos`; la gacha conserva titulos, pesos por rareza y garantia. Los
sombreros solo se muestran sin casco, sin ocuparlo ni modificar sus estadisticas.
La seleccion persiste en datos del jugador; los displays no generan items al morir.
Carnivora aporta sombrero y alas; Asura aporta alas. El arte queda en el circuito privado.

SkinsRestorer **15.12.6**, compatible con Paper 26.1.2 segun su version oficial,
queda preparado para reinstalar conservando `plugins/SkinsRestorer` y sus datos.
Su JAR no se publica en el repo. Desactivar la aplicacion automatica al entrar
(`advanced.disableOnJoinSkins: true`, `advanced.enablePaperJoinListener: false`)
y `server.resourcePackFix`; AstralDecor ejecuta `sr applyskin <jugador>` despues
de que AuthMe confirme autenticacion y al terminar de cargar el pack. Conserva
la seleccion de skin; sin seleccion usa la cuenta. Mantener `online-mode=false`
y el `/premium` de AuthMe. Permisos limitados a cambiar/quitar la skin propia,
sin comandos para otros jugadores; claves y comandos exactos en la entrega.
No modifica los prefijos de LuckPerms ni el formato de TAB/nonchat.

Verificado: compilacion con Java 25; regeneracion lobby/menus/pack publico y
`build_privado.py --prepare`; suite Python completa de 221 pruebas y luego
5 pruebas focalizadas (incluye la nueva conservacion byte a byte de Tienda/Yeti).
Pack FINAL privado auditado: 5239 referencias, sin reemplazar texturas vanilla
de aldeanos/illagers. Paper 26.1.2 con SkinsRestorer y jugador NMS simulado:
13 comprobaciones correctas de permiso, display unico, manos/casco libres,
persistencia en playerdata, ocultacion con casco, quitar y muerte sin drops.
SkinsRestorer cargo y respondio a applyskin; sin errores en la ejecucion final.
Reproducir con `tools/probar_cosmeticos_paper.py --java <Java25> --base <Paper-local>`;
no subir CosmeticsProbe.jar. Evidencia local en `.local/cosmeticos-probe/paper.log`.

**Pendientes:** medicion spark ANTES/DESPUES en Empower (sin cifras remotas
disponibles), cliente real y segundo jugador, gacha en CrazyCrates, reconexion
real, muerte con AxGraves y cuentas premium/no premium con AuthMe/TAB/nonchat.
La prueba local no carga esos plugins ni certifica el render del cliente.
Instalar exige apagar y reiniciar por los JAR. No hubo subida a R2 ni cambios
en Empower/Aternos; nunca reemplazar mundos.

Entrega Tienda y decoracion del 11/11 preparada, **sin desplegar**:
[archivos, SHA-1, reinicio y comprobaciones](../build/deploy/tienda-modelo.md).
AstralDecor 1.1 recupera los modelos de NPC al terminar de cargar BetterModel y
activa su indicador propio de nombre siempre visible. Guardianes escondidos sin nombre.
Alas en segunda mano con cualquier pechera; peluches con mensajes y bypass oficial de WorldGuard.
La entrega privada esta aislada para conservar los derivados previos sin publicar.

Documento de referencia para administrar el servidor. Actualizado el 07/11/2026 (mudanza a Empower Servers).
Para saber dónde está cada cosa en el repo y cómo agregar cosas nuevas, ver [GUIA.md](GUIA.md).

## Fichas de armas y barra de Defensa (08/11/2026)

La barra sobre la hotbar es de **AuraSkills**, no de `hud_rpg.py` (apagado).
Se edita el bloque `action_bar` de `plugins/AuraSkills/messages/global.yml` y se
recarga con `skills reload`. El bloque completo sale de `gameplay.py` en
`build/gameplay/AuraSkills/global-action_bar.yml`; reemplazar solo ese bloque.
Conservar `action_bar.placeholder_api: true` en `plugins/AuraSkills/config.yml`
y la expansión ScoreboardObjectives de PlaceholderAPI. El datapack actualiza
`astraldef` con el atributo real `minecraft:armor` cada 10 ticks. Defensa aparece
en reposo; XP, habilidades y boss bars conservan sus formatos para evitar saturar la barra.
Se inserta el placeholder directamente, sin depender de una clave nueva de mensajes.
Referencia: [configuración oficial de AuraSkills](https://wiki.aurelium.dev/auraskills/main-config/).

Las fichas salen de `ficha.py`; `ITEM_VERSION = 11` migra armas viejas conservando
mejora, encantamientos añadidos y desgaste. El Herrero aplica nombre/lore de +0 a +10.
Se dejan visibles los encantamientos nativos, además de listar los propios en azul:
así siguen apareciendo los añadidos por yunque/mesa sin depender de addons de Skript.
El daño mostrado es el atributo base con el multiplicador del Herrero; efectos
condicionales, armadura y otros bonus pueden modificar el golpe. Arcos y lanzas
sin atributo propio no anuncian un daño fijo inventado. Los bastones muestran el
daño base efectivo de `spell/cast`, sin bonus de armadura; la ficha anterior mostraba
una escala que esa función no aplicaba. No se cambió su balance.

Instalación exacta y comprobaciones: `build/gameplay/fichas-despliegue.txt`.
Apagar, reemplazar el ZIP dentro de `world/datapacks` y volver a iniciar.
El script se instala como `plugins/Skript/scripts/special_weapons.sk` (una sola copia).
Para recargarlo: `skript:skript reload special_weapons`. Resource pack sin cambios.

> **Contraseñas:** este repositorio es público, así que acá no va ninguna contraseña.
> Las claves van en `docs/CREDENCIALES.local.md`. Ese archivo existe solo
> en la PC del dueño y Git lo ignora, así que no se sube a GitHub.
> La contraseña de Aternos se compartió con el soporte de Empower para la migración: cambiarla.

## Servidor

| Dato | Valor |
|---|---|
| Dirección | `103.106.58.173:7004` |
| Hosting | Empower Servers, nodo AR01 (Argentina). Panel: https://gp.empowerservers.com/server/44d1ad66 · Facturación: https://billing.empowerservers.com |
| Plan | 8 GB de RAM, 200 GB de disco, respaldos diarios (complemento). Trimestral, se renueva solo |
| Software | Paper 26.1.2, build 74 (Java 25) |
| Modo | No premium (`online-mode=false`): entran cuentas cracked y originales |
| Login | AuthMe: los no premium hacen `/register <clave> <clave>` la primera vez y `/login <clave>` después. Los premium escriben `/premium` una vez (estando logueados) y desde ahí entran sin contraseña. Es el modo premium propio de AuthMe (`settings.enablePremium: true` en `plugins/AuthMe/config.yml`), que usa PacketEvents para confirmar la cuenta con Mojang. `/freemium` lo desactiva |
| Mods | Ninguno. Se entra desde Minecraft vanilla 26.1.2 |
| Repositorio | https://github.com/Trainx12/AstralRPG (público) |

El servidor queda prendido las 24 horas. Tarda unos 3 minutos en arrancar (`Done (177s)`) y usa ~2 GB al prender.

### Empower: lo que hay que saber (07/11/2026)
- **Java 25 elegido a mano:** Startup → Docker Image → **Java 25**. La imagen "Java Universal" detecta Java 17 y Paper 26.1 no arranca ("requires Java 25").
- **El panel reescribe `server.properties` al arrancar:** pone `server-port`, `query.port` y `management-server-port` en 7004. Por eso `management-server-enabled=false` (si no, choca con el puerto del juego: "FAILED TO BIND TO PORT"). Dejar `resource-pack-prompt=` vacío: con comillas el panel rompe la línea siguiente (`resource-pack-sha1`).
- **Versions → Install:** el interruptor **Wipe Server Files** borra todo el servidor. Tiene que quedar apagado.
- **Archivos:** Files permite subir cualquier cosa, también `.jar`, y hay SFTP (misma clave que el panel). Sin tope de Metaspace (Aternos tenía 350 MB): Java arranca con `-Xmx6400M`.
- **Soporte:** el chat de la esquina del panel (el formulario de tickets no tiene departamentos).
- **Migración (07/11/2026):** el soporte pasó los 24 mundos, los datapacks y las configs de la raíz. La carpeta `plugins/` (configs y datos, sin los `.jar`) y `config/` (Paper) se bajaron de Aternos y se subieron a mano. Los 29 `.jar` se bajaron de Modrinth, Spigot (SleepMost) y GitHub (Vault) con las mismas versiones. El servidor de Aternos queda como copia hasta confirmar jugando que no falta nada.

**Reglas al cambiar archivos:**
- **ClearLag y mascotas:** el limitador de apariciones (`optimizations.mob-spawn-limiter`) cancela todo mob nuevo cuando
  hay 20 pasivos cada 4 chunks, y eso incluye las mascotas que invoca MythicMobs (desaparecian al invocarlas en el spawn y
  en el lobby). En `plugins/ClearLag/config.yml`, `exempt-spawn-reasons` tiene que incluir `CUSTOM` ademas de `CURED`.
  Las mascotas llevan la etiqueta `clearlag_exclude` para que las otras limpiezas no las toquen.
- El datapack nuevo se toma al reiniciar: reemplazarlo en `world/datapacks` y reiniciar (o apagar, reemplazar, prender).
- Cada vez que cambia `AstralRPG-Textures.zip`, hay que actualizar `resource-pack-sha1` en `server.properties` con el sha1 nuevo. Si no se actualiza, los jugadores no bajan la versión nueva o el pack falla al cargar.
- **Nunca usar Upload en la fila world de Worlds: reemplaza el mundo entero.** Asi se perdio el mundo original en Aternos el 28/10/2026.
- **Respaldos:** El dueno contrato el servicio pago **Respaldos Diarios** de Empower: cada 4 horas, fuera del servidor y administrado por Empower. En el panel hay un respaldo manual bueno del 10/11 (558 MB). Los backups del panel fallan con carpetas que cambian; `.pteroignore` en la raiz excluye `logs`, `cache`, `.cache`, `libraries`, `versions`, `crash-reports`. La tarea programada del panel "Backup diario" fallo en la prueba (0 MB); no contar con ella como respaldo valido.
- En Paper 26.1 todos los mundos viven dentro de `world/`: `world/dimensions/minecraft/<overworld|the_nether|the_end|lobby>/region`.

## Memoria y lag (revision 02/11/2026, en Aternos)

> Desde el 07/11/2026 el server está en Empower, sin tope de Metaspace y con 8 GB. Lo de abajo explica por qué
> se sacaron plugins en Aternos. Ahora se pueden volver a poner, pero conviene medir con spark antes y después.

- **Cuelgue del 02/11 18:25:** `java.lang.OutOfMemoryError: Metaspace`. Metaspace es la memoria donde Java guarda
  el codigo de los plugins. Aternos arranca Java con `-XX:MaxMetaspaceSize=350M -Xmx2300M` (visto en el informe
  de spark, pestana JVM Flags) y no deja cambiarlo. Con ~35 plugins se usan ~300-325 MB de esos 350 a los pocos
  minutos de prender (el "Non-heap" de spark suma ademas la cache de codigo, por eso marca ~430 MB). El server arranca en ~420 MB
  ("Non-heap" en `spark health --memory`) y crece cuando se usan cosas nuevas (entrar a mundos, mobs nuevos) y con
  cada recarga: medido +2-3 MB por `skript reload all` o `mm reload`, que no se liberan hasta reiniciar.
- **Lag:** los elites del datapack eran persistentes y se acumulaban (se mataron 115 brujas cerca del spawn); el
  rescate de caidas escribia variables de Skript a disco cada tick. Las dos cosas se corrigieron.
- **Plugins sacados por memoria (03/11/2026):** QuickShop-Hikari, Duels (volvió en Empower el 08/11/2026), SkinsRestorer, DonutOrders y AxShulkers
  (y despues LevelledMobs y DamageIndicator por la escala por tier). No reinstalarlos sin medir. En Aternos, borrar un jar hay que confirmarlo con un clic real en "Yes" y revisar
  la lista despues: si no, el jar sigue ahi y vuelve a cargar. Resultado: Non-heap al prender 421 -> 395 MB.
- **Reglas:** despues de una sesion con muchas recargas, reiniciar. Antes de sumar un plugin, medir Non-heap antes y
  despues. Estado sano sin jugadores: 20 TPS, ~420 MB Non-heap, ~1 GB de 2,2 GB de memoria normal.

## Plugins

| Plugin | Para qué está |
|---|---|
| AuraSkills 2.4.0 | Skills y niveles (Forja, Hechicería, Arquería, Combate, Minería, Tala...). **Tiene cargado el preset `legacy.zip`** (sin él no existen Forging ni Sorcery) |
| LevelledMobs | Sube el nivel de los mobs según la distancia al spawn |
| MythicMobs 5.13.0 | Criaturas custom: fauna, hostiles, monturas, élites y jefes |
| BetterModel 3.6.0 | Modelos 3D de esas criaturas (sin mods) |
| BetterHud 2.0.0 | Panel dibujado de la derecha (`/sb`). Ver [BETTERHUD_Y_DUELS.md](BETTERHUD_Y_DUELS.md) |
| Duels Optimised | Duelos 1 contra 1 en la arena `Astral` (`/duel <jugador>`), sin perder ítems |
| ExcellentEnchants 5.4.3 + NightCore + PacketEvents | Encantamientos extra (el Taladro Infernal fue retirado; los taladros usan el area del datapack) |
| Bolt | Protege cofres, shulkers y puertas |
| WorldGuard + WorldEdit | Zonas protegidas y edición |
| AuthMe | Login con contraseña (necesario en modo no premium). Modo premium activado: los premium con `/premium` entran sin contraseña. **No instalar FastLogin**: choca con el `/premium` de AuthMe 6 |
| AxGraves | Tumba con tus cosas al morir |
| ClearLag++ | Limpia ítems tirados para que no haya lag |
| TAB | Tabulador y panel lateral de las Minas Astrales (ver Lobby) |
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
| Junto al banco del sur | Viajero (respaldo conservado) | Te lleva al mundo normal; retiro pendiente de decidir tras validar el tren |
| Dentro de la montaña, acceso por el hueco (XYZ pendientes) | Tren al survival (preparado, sin instalar) | Tres plazas, cama/punto valido del survival o spawn de world; ver entrega |

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
- **Panel anterior (BetterHud, 08/11/2026; reemplazado en la tanda 1 preparada por TAB):** panel dibujado con vida, defensa, poder, oro, lugar, conectados, rango, diarias, historia y monstruos (`/sb` lo oculta o muestra). Sale de `datapack-src/betterhud.py`; ver [BETTERHUD_Y_DUELS.md](BETTERHUD_Y_DUELS.md). En las Minas Astrales se ve el panel de TAB de las minas.
- **Tabulador (TAB):** en el tabulador: encabezado animado, corazones de vida, título de la gacha y poder de cada jugador. Rango según el poder de AuraSkills: Novato, Aventurero (150), Veterano (400), Héroe (800), Leyenda (1500). Lo genera `datapack-src/lobby.py` en `build/lobby/TAB/` (las secciones de `config.yml` se reemplazan una por una; `groups.yml` entero; las animaciones se agregan a `animations.yml`). Después: `tab reload`. Usa las expansiones de PlaceholderAPI LuckPerms, Vault, Player, Server y Statistic.
- Los huevos de mascotas y monturas no funcionan en el lobby (ahí no aparecen mobs): hay que usarlos en el mundo.
- Si cambian los premios: subir los `.yml` a `plugins/CrazyCrates/crates/` y correr `crates reload`.
- Las gachas no usan ExcellentCrates: la 7.x guarda todo en base de datos (solo se edita dentro del juego) y la 6.x no anda con el NightCore que necesita ExcellentEnchants.

## Mascotas

23 mascotas 3D que siguen al jugador, tambien entre mundos y en el lobby o la arena. Una a la vez.
Sus efectos solo se activan en mina, bosque, tumba, cumbre, forja y santuario. Al salir, los efectos
ya aplicados caducan naturalmente: hasta 3,5 segundos, o 20 segundos para la absorcion del Fenix.
En lobby y arena se permiten invocaciones con WorldGuard; `spawn_mobs=false` impide apariciones naturales.

| Mascota | Nivel 1 | + Nivel 10 | + Nivel 20 | Como se consigue |
|---|---|---|---|---|
| Lobo del Bosque | Fuerza I | + Velocidad I | + Resistencia I | Espantapajaros y Armored Grubs (raro) |
| Cuervo Arcano | Vision nocturna y marca a los mobs cercanos | + Suerte | + Velocidad I | Gacha de Monturas |
| Golem de Piedra | Resistencia I | + Regeneracion I | + 2 corazones de absorcion | Mazmorra Minas Olvidadas (raro) |
| Zorro Espectral | Velocidad I | + Salto I | Velocidad II | Yeti de las Cumbres y Caras Voladoras (raro) |
| Dragoncito de Fuego | Resistencia al fuego | + Fuerza I | + Prisa I | Gacha de Monturas (epico) |
| Fenix | Te salva con poca vida (cada 10 min) | cada 7 min | cada 5 min | Gacha de Monturas (legendario) |
| Ghastito de Nube | Caida lenta | + Regeneracion I | + Suerte | Gacha de Monturas |
| Bombardero Musgoso | Resistencia I | + Fuerza I | + Prisa I | Gacha de Monturas |
| Canonero de Bolsillo | Fuerza I | + Prisa I | + Suerte | Gacha de Monturas |
| Zorro Encapuchado | Velocidad I | + Vision nocturna | + Fuerza I | Gacha de Monturas |
| Llamita Viajera | Salto I | + Suerte | + Resistencia I | Gacha de Monturas |
| Pequeno Hondero | Prisa I | + Velocidad I | + Suerte | Gacha de Monturas |
| Saqueador Elegante | Suerte | + Fuerza I | + Resistencia I | Gacha de Monturas |
| Brujita Estelar | Regeneracion I | + Resistencia al fuego | + Suerte | Gacha de Monturas |
| Cubito del Desierto | Resistencia al fuego | + Prisa I | + Resistencia I | Gacha de Monturas |
| Cubito de la Jungla | Salto I | + Velocidad I | + Fuerza I | Gacha de Monturas |
| Cubito Frondoso | Regeneracion I | + Prisa I | + Resistencia I | Gacha de Monturas |
| Cubito de Micelio | Regeneracion I | + Suerte | + 2 corazones de absorcion | Gacha de Monturas |
| Cubito de Pradera | Velocidad I | + Suerte | + Regeneracion I | Gacha de Monturas |
| Cubito de Sabana | Prisa I | + Resistencia al fuego | + Velocidad I | Gacha de Monturas |
| Cubito de Nieve | Velocidad I | + Resistencia I | + Suerte | Gacha de Monturas |
| Cubito de Pantano | Respiracion acuatica | + Regeneracion I | + Resistencia I | Gacha de Monturas |
| Honguito Errante | Regeneracion I | + Resistencia I | + Prisa I | Gacha de Monturas |

- **Uso:** `/mascotas` (alias en `commands.yml` → `/trigger mascota set 99`) abre un menú con botones *Invocar* y *Guardar*.
- **Niveles:** 1 nivel cada 25 mobs que mata el dueño con la mascota afuera, hasta 30. Nivel 30: más grande y con partículas.
- **Por dentro:** tener la mascota = permiso `astral.mascota.<id>` (23 IDs en `datapack-src/mobs/mascotas.py`); la elegida está en el puntaje `petsel`; los niveles en `plv_<id>`. Un controlador invisible (`astral_mascotas_control`) en un chunk del lobby siempre cargado atiende los pedidos de todos.
- Dar una mascota a mano: `lp user <jugador> permission set astral.mascota.<id> true`. Armado: `build/mascotas/comandos.txt`.

## Menús, bazar y subastas

- **Menú de comandos:** `/comandos` (o el libro abajo a la izquierda de `/menu`) lista los comandos para jugadores por tema, con para qué sirve y cómo se usa; los que no piden datos se usan con un clic. Se edita en `COMANDOS` de `datapack-src/menus.py`.
- **Menús de cofre (DeluxeMenus):** `/menu` (principal), `/mascotas`, y los que abren los vendedores: cada cofre de gacha (`dm open gacha_<x> <jugador>`: tirar x1/x10/x25/x50 y ver premios) y el aldeano *Bazar* (`dm open bazar <jugador>`: mercado, venta rápida, subastas e intercambio). Shift + clic al cofre de gacha sigue mostrando la vitrina. La garantía se ve en el menú con `%objective_score_{pity_rpg}%` (expansión ScoreboardObjectives de PlaceholderAPI).
- **Mercado y venta rápida:** EconomyShopGUI (`/shop`, `/sellgui`), con precios fijos.
- **Subastas (CrazyAuctions, `/ah`):** ítems únicos entre jugadores; publicar con `/ah sell <precio>` y el ítem en la mano. Aldeano *Subastas* (`astral_npc_subastas`).
- **Intercambio (AxTrade, `/trade <jugador>`):** cambio de objetos y oro cara a cara. Es la cuarta tarjeta del Bazar (antes era Órdenes de DonutOrders).
- EzAuction y RoyalBazaar (los que se habían elegido) no están en el catálogo de plugins de Aternos.
- Los 4 puestos con cofres y alquiler que hubo antes se sacaron (regiones `puesto1-4`, grupos y cofres borrados).

## Mazmorra: Minas Olvidadas (mundo `mina`)

Mundo vacío de Multiverse con el mapa `dungeon1-endlessxl.schem` (de terceros: **no está en el repo**, se sube directo a `plugins/WorldEdit/schematics/`) pegado con `//paste -o` (la esquina queda en -73 -55 -290). Dificultad difícil, sin mobs naturales, `keep_inventory` activado, protegido con WorldGuard.

- **4 salas** que se recorren con teletransporte: 1) Campamento Minero (mineros corruptos y esqueletos), 2) Lago Subterráneo (ahogados + mini jefe Capataz Ahogado), 3) Túneles de Soporte (arañas, esqueletos + mini jefe Gólem de Piedra Antiguo), 4) Salón del Guardián (jefe final con fases).
- Cada sala tiene un controlador invisible (`astral_mina_control_salaN`): al llegar un jugador larga las oleadas, cuando no quedan mobs pasa a la siguiente, y si la sala se queda vacía se reinicia sola. Con 2 o más jugadores aparecen mobs extra.
- **Cofre final:** materiales de élite, 2500$ y 25% de Chispa Astral. Se cobra una vez cada 30 minutos por jugador (permiso temporal `astral.mina.cd` de LuckPerms; el grupo default lo tiene en false para que funcione con OP, ver docs/MAZMORRAS.md); se puede volver a entrar sin premio. Después de 15 segundos vuelven al lobby.
- **Entrada:** vendedor `astral_npc_mina` en el lobby. Salir: `/spawn`.
- Todo sale de `datapack-src/mobs/mazmorra.py`; el armado (crear el mundo, pegar el mapa, poner los controladores) está en `build/mazmorra/comandos.txt`.

## Datapacks (`world/datapacks`)

Tienen que estar antes de generar un mundo nuevo, si no, no aparecen sus estructuras. Se suben con Files → `world/datapacks` → Upload → Files.

- **AstralRPG-Items.zip**: el nuestro. Tiene ítems, recetas, Forja Astral, guía, élites, taladros y motosierras.
- Dungeons and Taverns 5.2.0 y DnT Stronghold Overhaul 2.4.0: estructuras.
- Incendium 5.4.12: Nether.
- Stellarity 5.4.2: End. La 6.0.1 crasheaba en 26.1.2, por eso quedó la 5.4.2.

## Resource pack

- Hosting nuevo preparado: URL fija R2 `https://pub-5e0d1c63a1554ba7b8e33b038e1a06fe.r2.dev/AstralRPG-Textures.zip`. El servidor seguia usando GitHub raw segun la comprobacion de Claude, SHA-1 `19dddebabccf78aaa1518084f166b66139277003`; no se cambio en esta tanda.
- Es obligatorio (`require-resource-pack=true`).
- Incluye las texturas originales del dueño (`assets/astral`, `assets/armasrpg`), las armaduras de Mago, Berserker y Arquero, las texturas CC0 (créditos en `datapack-src/pack-source/cc0/CREDITOS.txt`), los taladros y motosierras, y los modelos de BetterModel.
- Despues de cambiarlo: commit y push, `python tools/subir_pack_r2.py` (boto3 y credenciales locales), verificar descarga publica, guardar URL fija R2 y SHA-1 devuelto en `server.properties` y reiniciar. `--dry-run` calcula el hash sin subir.

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
| `bettermodel reload` | Recargar modelos (catalogo propio mas modelos privados; ver docs/TERCEROS.md) |
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
  - Hostiles: espantapájaros, Armored Grub, araña y cara voladora.
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
- "Excediste la cantidad de registros" (AuthMe): limite de cuentas por IP. Subido de 1 a 3 el 08/11/2026 (`restrictions.maxRegPerIp: 3` en `plugins/AuthMe/config.yml`, luego `authme reload`) para amigos en la misma red.
- Error al entrar `Failed to decode packet 'clientbound/minecraft:cookie_request'`: era la sala de espera de Aternos con el server apagado. En Empower no pasa; si no conecta, revisar en el panel que diga Running y la consola.
- Si alguien no ve texturas: que acepte el resource pack al entrar. Si sigue igual, revisar que el sha1 coincida.
- Si aparece "Unknown skill": cargar el preset legacy de AuraSkills (ver comandos).
- El área de los taladros puede romper bloques dentro de una zona de WorldGuard si picás justo en el borde.
- WorldEdit: su "varita de navegacion" es la brujula (clic derecho teletransporta a los OP). Se probo cambiarla para el Tower Defence y no alcanzo; se dejo como estaba (`navigation-wand.item: minecraft:compass`).
- Consola y `execute console command` de Skript: `clear` es el de nonchat (borra el chat de todos) y `tp` el de Essentials. Usar `minecraft:clear` y `minecraft:tp`. Las funciones de datapacks si usan los de Minecraft.

## Servidor de prueba local

Para probar sin tocar el servidor hubo una copia del servidor (mismos plugins, sin economía) en la carpeta temporal de Claude. Esas carpetas se pueden borrar; se rearma bajando Paper 26.1.2 y los mismos plugins. El mundo de prueba es plano. Detalles en [GUIA.md](GUIA.md#6-servidor-de-prueba-local).

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

## Tanda 1 instalada (10/11/2026)

Tanda 1 instalada por el responsable del despliegue, commit `0c4bb1b` (estado comunicado en el plan de Claude). Panel general en TAB, BetterHud apagado (`default-hud: []`); `/sb` persistente. Copias locales: `.local/deploy-backups/tanda1-20261110-1422/`. Lista: `build/deploy/tanda1.md`.

El resource pack se sirve desde R2: `https://pub-5e0d1c63a1554ba7b8e33b038e1a06fe.r2.dev/AstralRPG-Textures.zip`. SHA-1 instalado: `7a99922fb1734f4f80c64cee3f363a7b4d2404cb`.

La Galeria de Expediciones de la terraza fue borrada a pedido del dueno (3 aldeanos y 8 rotulos). `ambiente.py` ya no la recrea; se conservan los modulos de Expediciones, Bazar, Subastas y Herrero.

Tanda 2 preparada localmente, sin desplegar: `build/deploy/tanda2.md`. Requiere apagar para cambiar el datapack y comprobar el tope `settings.attribute.maxHealth.max` de `spigot.yml` (recomendado 1.000.000.000, minimo 13.125.000). No usar configs de servidores de prueba completas. Yeti de Cumbre corregido a 28 bloques de alto (`s=8`, `scale=12,727273`); chequeo de terreno en `build/deploy/tanda2.md`.

El dueno contrato el servicio pago **Respaldos Diarios** de Empower: cada 4 horas, fuera del servidor y administrado por Empower. En el panel hay un respaldo manual bueno del 10/11 (558 MB). Los backups del panel fallan con carpetas que cambian; `.pteroignore` en la raiz excluye `logs`, `cache`, `.cache`, `libraries`, `versions`, `crash-reports`. La tarea programada del panel "Backup diario" fallo en la prueba (0 MB); no contar con ella como respaldo valido.

Tanda 4a preparada, sin desplegar: [circuito privado y catalogo de las 17 mascotas nuevas](TERCEROS.md). Lista exacta de archivos, reinicio y reposicion de vendedores en `build/deploy/tanda4a.md`. El pack FINAL se toma del repositorio privado; no reemplazarlo por el ZIP publico al subir a R2.

## Correccion urgente del 11/11 (preparada, despliegue pendiente)

Mascotas: `<global.pet_owner>` no se resuelve en MythicMobs 5.13; dejaba la mascota
sin dueno y `ownerIsOnline` la retiraba. La invocacion ahora corre como el jugador
con `sudoskill` y `summonerIsOwner=true`, asignando su UUID sin un nombre global.
Los bonus usan los mundos reales `cumbre_hielo`, `forja_volcano` y `santuario_interstellar`.

En `plugins/WorldGuard/worlds/lobby/config.yml`, dentro de `mobs`, conservar
`block-plugin-spawning: false`. Claude ya aplico ese ajuste en el servidor segun
el diagnostico del pedido; comprobarlo al desplegar. Permite invocaciones de plugins
con la region protegida. `spawn_mobs=false` sigue evitando mobs naturales.
Una edicion con el servidor encendido requiere `wg reload`; el reinicio tambien la carga.
ClearLag debe conservar `CUSTOM` en `exempt-spawn-reasons` y la exclusion `clearlag_exclude`.

La Cumbre llega a `-25.6 33 -23.4` (yaw 49.9); el jefe recibe al grupo en
`-54.9 30 6.5` (yaw 45.7). Y30 tiene piso firme en el mapa local; Y52.7 era la
posicion de observacion del dueno. Yeti y cofre: `-101.8 30 56.9`.
El Yeti usa `s=4`, el doble del Ancestral, con `minecraft:scale=6.363636` y 14 bloques
de alto. Esto reemplaza el tamano de 28 bloques indicado en la nota historica de Tanda 2.
No instalar el apoyo antiguo propuesto a Y32 sobre esa ubicacion.

Entrega posterior preparada, sin desplegar: [yeti-bastones-guia.md](../build/deploy/yeti-bastones-guia.md),
con Tienda incluida en un solo reinicio. Sustituye el tamano anterior por 10 bloques
(`s=20/7`), frente a 7 del Ancestral. La caja conservadora de Cumbre usa
`minecraft:scale=6.199573`, cubre brazos y alto y deja altura sobrante por el
escalado uniforme vanilla. Bastones intersectan cajas completas. Los cinco guias
finales aparecen a 2 bloques del cofre; los seis peluches se corrigen al cargar.
Lobby sigue sin permitir colocarlos, incluso con OP/bypass.

El espadachin ya no forma parte de las apariciones; se conserva el modelo.
La muerte de criaturas usa `death` de BetterModel 3.6.0 (0.8 s, sin repeticion),
mas tinte y humo. NPC, mascotas, cofres y monturas conservan sus animaciones.
Archivos exactos, SHA-1 FINAL, tabla de todas las llegadas y reinicio:
[urgente-mascotas-texturas.md](../build/deploy/urgente-mascotas-texturas.md).
Las vistas CPU y el jugador NMS simulado no sustituyen la revision visual con cliente
ni la consola del servidor remoto.


Ajuste posterior del mismo 11/11: se anula la propuesta de apoyos en Tumba/Cumbre.
Los mobs y cofres usan piso natural, con rangos por sala en `mobs/salas_seguras.py`.
`arreglos-apoyos.txt` se elimina; no agregar bloques. Menu Astral conserva 14 accesos
mas Fragmentos y Duelos. Intercambio esta en Comandos y Peluches dentro de la Tienda.
El panel TAB reemplaza diarias por sala/oleada/restantes en las cinco mazmorras;
se elimina Rango del panel general. La bossbar PURPLE es independiente por sala,
cuenta vivos y pendientes, y se oculta durante el jefe o al salir. Los scores `ad.*`
se crean al cargar el datapack. Integrar las secciones de TAB conservando el resto.
Entrega unica vigente: `build/deploy/urgente-mascotas-texturas.md`; requiere un reinicio.
