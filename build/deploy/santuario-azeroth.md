# Santuario Azeroth: entrega sin desplegar

Posterior a Recetas de mesa y Tren lobby. Generado por `datapack-src/deploy_santuario.py`.
Servidor vigente: Empower, Paper 26.1.2 build 74 / Java 25. Aternos es copia.
No se modifico ningun servidor remoto ni R2. **Falta prueba con cliente real antes de habilitar el cambio a jugadores.**

## Resultado

`Spires of Azeroth.zip` reemplaza al escenario del Santuario. Dimension `santuario_azeroth`,
clave `minecraft:santuario_azeroth` y nombre Bukkit **`world_minecraft_santuario_azeroth`**, con `level-name=world`.
La diferencia de nombres fue comprobada en Paper: los comandos vanilla usan la clave;
WorldGuard, MythicMobs, mascotas, Skript y TAB contemplan el nombre Bukkit.
No crear ni importar la dimension con Multiverse; Paper la carga desde el datapack.
Si el mundo principal remoto tiene otro `level-name`, ajustar `BUKKIT_WORLD` y sus
referencias antes de instalar. No copiar configuraciones completas del servidor de prueba.

El cielo usa `skybox: end`, `has_ender_dragon_fight: false`, luz ambiente 0,35 y
generador plano de aire. En 26.1 `effects` ya no es el formato vigente. El JAR local
confirmo el formato y el ensayo real confirmo End, ausencia de dragon y vacio fuera del mapa.
Referencia: [cambios oficiales de Minecraft 26.1](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-1).

Se conserva una sala con los cinco Ancestrales en orden, modelos, fases, afijos,
vida original del Santuario, barra roja, recompensas, espera de 30 minutos, historia,
descubrimiento, NPC y `SANTUARIO_ENTRAR`. Tier fijo 5 y factor x1,5 en la configuracion
del mundo, sin volver a escalar los atributos propios de los Ancestrales.
`astral:in_sanctuary` incluye el destino nuevo y las copias antiguas.
Las rutas activas dejan Interstellar; sus excepciones de proteccion y tier se conservan
para que siga siendo una copia segura. No borrar ni reemplazar ese mundo.

## Recorrido propuesto y puntos comprobados

| Punto | X Y Z |
|---|---|
| Entrada (mirar al sur, yaw 0) | 247.5 57 14.5 |
| 1. Cangrejo: sector norte | 233.5 57 1.5 |
| 2. Chaman: sector este | 299.5 57 37.5 |
| 3. Momia: sector sur | 267.5 57 106.5 |
| 4. Yeti: sector oeste | 197.5 57 36.5 |
| 5. Golem de Forja: regreso al norte interior | 247.5 57 19.5 |
| Cofre final | 247.5 57 23.5 |
| Guia de Expediciones | 249.5 57 23.5 |

Todos estan a Y=57 sobre el nivel de vidrio existente. La propuesta recorre el anillo:
norte -> este -> sur -> oeste -> regreso al norte interior. No obliga a escalar los
spires superiores. Desde el cofre se sale con su menu o con el guia; `/spawn` sigue
disponible. Cofre y guia distan exactamente dos bloques. No se agregaron plataformas.
Controlador unico: `247.5 57 19.5`, radio 104; limpieza/premios 112.
Se comprobo piso de 5x5 y nueve bloques de aire en cada jefe, piso y tres bloques de
aire en entrada/cofre/guia y conexion a pie entre todos: 2615 celdas transitables.
Esto no certifica como pelea o camina la IA en las pasarelas.

Caida por debajo de Y=0: vuelve a la **entrada del Santuario**, con velocidad y caida
acumulada en cero. No guarda un ultimo punto. Conservar inventario y experiencia al
morir y exclusion de AxGraves incluidas. El datapack aplica las gamerules del destino
al cargar y mantiene los **169 chunks** del recorte cargados para que los sectores
lejanos no desaparezcan del contador de la sala. No retirar esas cargas durante el uso.
Se limita a este mundo nuevo; revisar el costo real con spark en el servidor compartido.

## Conversion privada e integridad

Original intacto: `C:/Users/Trainx/Downloads/Spires of Azeroth.zip`.
SHA-256 `680f67a1c49da6c9173db03992d8061c5debd360155355f5b47f982c649c275d`.
Etapa oficial 1.6.4: seis McRegion convertidas a Anvil; despues DataFixer oficial
incluido en Paper 26.1.2, desde version -1 hasta DataVersion 4790.
No se finge DataVersion 1.12 para omitir migraciones antiguas.
La [nota oficial de 1.18](https://feedback.minecraft.net/hc/en-us/articles/4415128577293-Minecraft-Java-Edition-1-18)
recomienda 1.6.4 para convertir mapas anteriores a Anvil.

Recorte X/Z `144 -48 .. 351 159`, 169 chunks, escenario mas margen; excluye el
terreno natural alejado. Conserva **97696 bloques**, 128 jukebox y ocho
carteles; no hay cofres en el recorte. Se excluyen `__MACOSX`, jugadores, entidades,
datapacks originales, comandos e inventarios originales. No se importa `level.dat`.
El mapa, originales, derivados y vistas quedan **solo en `.local/`**, nunca en GitHub.
No se publican capturas del mapa ni arte ajeno.

Regiones instalables (solo estas dos):
- `r.0.-1.mca`: SHA-256 `65b7679904345dd8f7b096e04feb6a86ebe96cb5cd8fa2f5d9ac9fc8aa83c33b`.
- `r.0.0.mca`: SHA-256 `0c192b378d156788d917e2ec5823a42c2138580c206e4baa15beef2117bdde95`.

## Archivos exactos y destinos

Con servidor APAGADO, despues de comprobar un respaldo valido:

| Local | Destino remoto |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `.local/santuario-azeroth/entrega/santuario_azeroth/region/r.0.-1.mca` | `world/dimensions/minecraft/santuario_azeroth/region/r.0.-1.mca` |
| `.local/santuario-azeroth/entrega/santuario_azeroth/region/r.0.0.mca` | `world/dimensions/minecraft/santuario_azeroth/region/r.0.0.mca` |
| `build/mythicmobs/mobs/santuario.yml` | `plugins/MythicMobs/mobs/santuario.yml` |
| `build/mythicmobs/skills/santuario.yml` | `plugins/MythicMobs/skills/santuario.yml` |
| `build/mythicmobs/skills/mascotas.yml` | `plugins/MythicMobs/skills/mascotas.yml` |
| `build/gameplay/astral_gameplay.sk` | `plugins/Skript/scripts/astral_gameplay.sk` |
| `build/mapas_exploracion/astral_viajes.sk` | `plugins/Skript/scripts/astral_viajes.sk` |
| `build/gameplay/AxGraves/config.yml`: agregar solo los dos nombres nuevos en `disabled-worlds` | `plugins/AxGraves/config.yml`, conservar el resto |
| `build/lobby/TAB/secciones-config.yml`: integrar `conditions.mundo`, `conditions.mundo_*`, `conditions.sidebar_world` y `conditions.sidebar_world_*` | `plugins/TAB/config.yml`, conservar las demas secciones |

SHA-256 del datapack: `69d5070625f48f021f761b9a81675dad55ff4b0fd18bd018337f0a4962d0b62f`.
Usar Files del panel de Empower o SFTP autorizado del panel. Crear **solo la carpeta
del destino nuevo** si falta. Si ya tiene archivos, respaldarlos y verificar por que
existe antes de sobrescribir. Nunca Worlds > Upload en `world`; nunca reemplazar
mundos completos, lobby, mina, ni regiones de Interstellar.
No hay resource pack, JAR de produccion ni subida R2 en esta tarea.

**Reinicio completo obligatorio** para registrar la dimension nueva y cargar regiones.
Tras iniciar: comprobar `datapack list enabled`, consola sin errores de registro y
`execute in minecraft:santuario_azeroth run forceload query` (169 chunks).
Aplicar `build/mazmorras/santuario/comandos.txt` con la mazmorra vacia: protecciones,
reglas y sustitucion del controlador viejo por uno nuevo. La eliminacion por tipo de
MythicMobs afecta todas sus instancias: verificar que no haya otra prueba en uso.
Los mundos viejos quedan como copia; se retira su controlador para no duplicar partidas.
No crear otro NPC de entrada: el existente ya llama a `SANTUARIO_ENTRAR`.

El arranque carga las configs. Si se ajustan despues: `mm reload`,
`skript:skript reload astral_gameplay`, `skript:skript reload astral_viajes`,
`tab reload` y `wg reload`. AxGraves se carga en el reinicio. No usar `/reload`
global para sustituir este reinicio. Si una recarga da errores, no abrir el acceso.

## Reproduccion y pruebas

Desde la raiz, con Python + Pillow/NumPy/PyYAML y JDK 25 disponibles:

```text
python tools/preparar_santuario_azeroth.py --source "C:/Users/Trainx/Downloads/Spires of Azeroth.zip" --vanilla164 <server-1.6.4.jar-oficial> --java <java25> --paper <Paper-local> --out .local/santuario-azeroth/nueva-conversion
python tools/inspeccionar_santuario_azeroth.py .local/santuario-azeroth/nueva-conversion
python datapack-src/build.py
python datapack-src/mobs/mazmorra.py
python datapack-src/mobs/mascotas.py
python datapack-src/gameplay.py
python datapack-src/viajes_mazmorras.py
python datapack-src/lobby.py
python tools/probar_santuario_paper.py --java <java25> --base <Paper-local> --regions .local/santuario-azeroth/entrega/santuario_azeroth/region --work .local/santuario-azeroth/nueva-prueba
python datapack-src/deploy_santuario.py
```

Vanilla 1.6.4 se descarga del manifiesto oficial de Mojang; SHA-1 admitido:
`050f93c1f3fe9e2052398f7bd6aca10c63d64a87`. Las salidas deben ser carpetas nuevas,
el preparador no borra ni reemplaza conversiones anteriores. `--anvil` permite
reutilizar una etapa oficial ya convertida, conservando el filtro de chunks originales.
Los tests Python se ejecutan desde `datapack-src`: `python -m unittest test_santuario_mapa test_mazmorras`.

Verificado: 19 tests Python (Santuario, mazmorras y regresiones de menu/TAB); 33 comprobaciones en Paper 26.1.2, MythicMobs 5.13,
BetterModel 3.6 y Skript 2.17.1. Carga de dimension, cielo End, sin dragon, generador
vacio, pisos/altura, ruta `/mazmorras santuario`, cinco oleadas en orden y posiciones,
cofre/guia, rescate y reset al salir. Skript cargo sin errores. Log privado:
`.local/santuario-azeroth/probe5/paper.log`. El ensayo congela IA y usa muertes
programadas y jugador NMS simulado; no demuestra balance ni combate real.
Los avisos de los tres dialogos de ejemplo de MythicMobs son previos.

Vistas **CPU**, inspeccionadas localmente, no capturas en juego:
`.local/santuario-azeroth/entrega/build/previews/santuario-azeroth-planta.png` y
`santuario-azeroth-oblicua.png`. Informes: `conversion.json`, `inspection.json`.

Pendientes: entrar con cliente real desde el menu, ver cielo/iluminacion con el pack
instalado, recorrer las pasarelas, combatir los cinco jefes con IA y afijos, comprobar
cobro/cooldown del cofre, historia, muerte/inventario/AxGraves, guia y salida `/spawn`.
No hubo cliente real en esta ejecucion: no hay capturas de juego ni verificacion remota.
El despliegue queda para Claude con acceso al panel. **No se afirma instalado.**
