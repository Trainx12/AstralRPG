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
Solo Sleep-most fue autorizado para instalar; el resto queda a decision del dueno.

Fuentes oficiales consultadas: fichas de los autores en Spigot/Modrinth,
https://docs.auroramc.gg/auroraquests/,
https://docs.nickuc.com/nantibot/about/,
https://docs.papermc.io/paper/profiling/,
https://github.com/pop4959/Chunky/wiki/Pregeneration y
https://hangar.papermc.io/Artillex-Studios/.
