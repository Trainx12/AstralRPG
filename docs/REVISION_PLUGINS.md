# Revision de plugins anteriores — 02/11/2026

Comparacion de las tres capturas del dueno contra `plugins` ejecutado en la consola
de Aternos (30 plugins activos) y los archivos de `plugins/`. Una carpeta sola no
demuestra que el plugin este instalado: ProtocolLib tiene carpeta, pero no JAR ni
aparece activo. AxAPI y bStats son carpetas de bibliotecas/configuracion.

## Cambio autorizado y realizado

Sleep-most 5.7.0 instalado desde el catalogo de Aternos. Verificado
`plugins/SleepMost-5.7.0.jar` (955.13 kB). Pendiente cargarlo en el proximo reinicio,
revisar errores de compatibilidad y configurar/probar el porcentaje de durmientes.
No se reinicio: habia dos jugadores conectados. No se modificaron horarios ni mundos.
Comprobante privado: `.local/deploy-ui/sleepmost-instalado.png`.

## Ya activos de las capturas

WorldGuard, WorldEdit, TAB, RHLeafDecay, PlaceholderAPI, nonchat, nightcore,
LuckPerms, LevelledMobs, ExcellentEnchants, DeluxeMenus, ClearLag, AxGraves y
AuraSkills. SkinsRestorer tambien esta activo; el dueno no quiere dedicar trabajo
a ese plugin, no solicito desinstalarlo. spark viene integrado en Paper moderno.

## Ausentes y equivalencias

| Plugin | Funcion / situacion |
|---|---|
| RestrictionMaster | Reglas para restringir crafteo, uso y encantamientos; protecciones propias cubren parte del uso actual. |
| ProtocolLib | Biblioteca para manipular paquetes; carpeta residual, sin JAR ni plugin activo. PacketEvents no es un reemplazo compatible de su API. |
| nLogin | Registro/login; cubierto por AuthMe. |
| nCore | No identificado con certeza solo por el nombre de carpeta; no instalar sin identificar el JAR original. |
| nAntiBot | Filtra conexiones de bots; funcion distinta del login. |
| MiniMOTD | Presentacion del servidor en la lista multijugador. |
| Magic | Varitas y hechizos; magia propia en el datapack. |
| ItemEdit | Edicion administrativa de nombres, lore y propiedades de objetos. |
| GrapplingHook | Gancho; excluido por el dueno, ya existe el propio. |
| ExpendableBackpacks | Mochilas portatiles mejorables. |
| ExecutableItems | Objetos que ejecutan habilidades/acciones; objetos propios via datapack/Skript. |
| SCore | Biblioteca del ecosistema Ssomar, usada por ExecutableItems. |
| Duels | Duelos organizados; arena propia no equivale a un gestor de duelos. |
| DamageIndicator | Muestra dano de los golpes; el nombre no identifica autor/version exactos. |
| CustomDrop | Cambia drops de bloques/mobs; loot propio via datapack/MythicMobs. Autor/version por confirmar. |
| Craftorithm | Administracion de recetas; Forja/recetas propias ya implementadas. |
| Chunky | Genera terreno anticipadamente para reducir tirones de exploracion. |
| Chessure | Regenera contenido de cofres; no es un plugin de ajedrez. |
| BossLand | Jefes, invocaciones y botin; ya tenemos jefes y mazmorras propios. |
| BlockProt | Protege cofres/puertas; cubierto por Bolt. |
| AxTrade | Intercambio directo de objetos/monedas entre jugadores. |
| AxShulkers | Abrir shulkers sin colocarlas. |
| AuroraQuests | Misiones y pools periodicos; historia y diarias propias. |
| Aurora | Base del ecosistema Aurora; sin beneficio por si sola. |

`update`, `.paper-remapped` y `bStats` no son plugins jugables para restaurar.
En la revision inicial solo Sleep-most estaba autorizado. La ampliacion posterior
del dueno autorizo AxTrade, AxShulkers, ExpendableBackpacks, Chessure,
DamageIndicator y Duels, con configuracion basica y conservando lo ya usado.

## Instalacion y revision posterior

Contrastados los ajustes actuales con `AVANCE_CODEX.md` y `ARMAS_ESPECIALES.md`:
Claude conservo Duels migrado a config-version 18 y preparo los colores de dano
para las armas especiales. Se conservaron esos ajustes. No se reinstalo la config
vieja de Duels version 12 ni la de otro DamageIndicator.

- AxTrade 1.28.2: activo; objetos y oro mediante Vault, sin EXP ni monedas de
  ejemplo. Distancia 10 bloques, doble confirmacion de 5 segundos, cancelacion al
  moverse/interactuar/usar comandos. Menu en castellano. Sin intercambios en arena
  ni las seis mazmorras. Permisos de uso propios del plugin, sin permisos admin nuevos.
- AxShulkers 1.24.0: activo; apertura en mano/inventario, cooldown de 500 ms,
  base H2 y protecciones contra duplicacion conservadas. Sin comandos con caja
  abierta ni apertura en arena/mazmorras. Textos basicos en castellano, sin spam
  al abrir/cerrar. No se cambio UUID, tipo de base ni inventarios existentes.
- ExpendableBackpacks: JAR 1.2.0; se identifica internamente como 1.0.0. Activo;
  recetas del plugin, sin mochilas dentro de mochilas y sin regalo automatico al
  entrar. No se regalaron ni editaron objetos de jugadores.
- Sleep-most 5.7.0: activo al 50% solo en `world`, excluyendo creativos,
  espectadores y AFK (Essentials). Requiere cama; no cura ni alimenta. Mensajes
  basicos propios. `disable-daylight-cycle-gamerule: false`; consultado
  `minecraft:advance_time` en overworld: `true`.
- DamageIndicator 2.1.0 (StealingDaPenta): activo. Se preservaron integramente
  los colores de Claude (normal blanco, rayo cian, explosion naranja, sismo
  amarillo). Barras de vida y sustitucion de nombres desactivadas. La variante
  MagicCheese 2.2.4 fallo en 26.1.2 y fue retirada durante la instalacion inicial.
- Duels Optimised 8.3: se restauro su JAR faltante y arranco correctamente. Se
  preservo config-version 18: sin apuestas ni perdida de inventario, partidas de
  hasta 10 minutos, sin intercambios/almacenamiento externo durante el duelo.
  `arenas.json` estaba vacio: se registro `Astral`, en el mundo `arena`, usando
  dos puntos del conjunto de llegadas ya definido en `mobs/mazmorras_data.py`:
  (-216.5,73,-2381.5) y (-196.5,73,-2361.5), mirando al centro. `lobby.json`
  devuelve a (180.5,98,190.5) del lobby. No se alteraron NPCs ni mapas existentes.
  El Duels original 3.5.3 fallo por incompatibilidad y se sustituyo por esta edicion.
- Chessure: no disponible en el catalogo de Aternos. La busqueda no lo devuelve
  y `/addons/a/spigot/120649` muestra `File not found`. No se instalo ni se
  modificaron cofres. Aternos no permite subir JARs propios.

El aviso cada cinco minutos era `broadcast.example` de nonchat. Se cambio solo
su formato y su texto; se conservaron canales, titulos y filtros existentes:

> Tu proxima aventura empieza en el lobby: usa /menu para consultar misiones,
> mascotas y servicios. Mejora tu equipo en la Forja Astral y preparate para las mazmorras.

Formato: `&8[&dAstralRPG&8] &f{message}`. Intervalo conservado: 300 segundos.
Recarga de nonchat correcta y texto completo verificado en consola.

### Plugins existentes conservados

No se cambiaron AuthMe, AuraSkills, AxGraves, BetterModel, Bolt, ClearLag,
CrazyAuctions, CrazyCrates, DeluxeMenus, DonutOrders, EconomyShopGUI, Essentials,
EssentialsSpawn, ExcellentEnchants, LevelledMobs, LuckPerms, Multiverse-Core,
MythicMobs, nightcore, PacketEvents, PlaceholderAPI, RHLeafDecay, SkinsRestorer,
Skript, TAB, Vault, WorldEdit ni WorldGuard: ya tenian uso/configuracion documentados.
nonchat conserva su configuracion excepto el anuncio expresamente solicitado.
No se tocaron dependencias, cuentas, inventarios, saldos ni estadisticas.

### Verificacion y reproduccion

El arranque final confirma 35 plugins activos, `Duels 8.3`, `Loaded 1 arena(s)` y
habilitacion de DamageIndicator 2.1.0. `/duels list` enumera `Astral` disponible.
Registro privado: `.local/plugins-final-startup.log`. Falta probar un duelo completo
con dos jugadores, el intercambio real y la recuperacion de las mochilas/shulkers.
No se forzo una pelea ni se movio a jugadores para probar.

Los presets revisados estan en `datapack-src/plugin-presets/` y se exportan con
`node datapack-src/plugins_basicos.mjs` a `build/plugins-basicos/`. Son una base
de reinstalacion: antes de subirlos nuevamente hay que comparar los archivos
vivos para preservar cambios posteriores. No exportan configuraciones de otros
plugins ni bases de datos. Los JSON se validan al generar; el servidor cargo la arena.

Fuentes oficiales consultadas: fichas de los autores en Spigot/Modrinth,
https://docs.auroramc.gg/auroraquests/,
https://docs.nickuc.com/nantibot/about/,
https://docs.papermc.io/paper/profiling/,
https://github.com/pop4959/Chunky/wiki/Pregeneration y
https://hangar.papermc.io/Artillex-Studios/.
