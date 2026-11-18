# Party y bordes alineados con los cercos — 18/11/2026

AstralParty **1.2.0**, Paper 26.1.2 build 74 / Java 25, Skript 2.17.1 y PlaceholderAPI.
Sustituye la propuesta de cuadrados de 05173b7 (1.1.0, no desplegada).
**Instalacion remota pendiente de Claude.** Esta tarea no entro al panel ni modifico mundos.
Empower figura como principal; Aternos como copia. Usar el destino vigente autorizado.

## Resultado

El controlador conserva centro XYZ y radio de entrada. Un rectangulo independiente
define la recuperacion por movimiento, empuje, perla y lag. El CSV del JAR contiene
99 salas de todas las copias. Sin dependencia de los mapas privados durante el build.
`zonas_pelea.json` contiene solo limites numericos, indicador de cerco y radio 3D.

Si los lados difieren <=4, borde fijo de lado menor centrado en el rectangulo.
Si difieren mas, lado menor y centro que sigue al jugador en el eje largo,
acotado para no salir del rectangulo. Usa la misma instancia, `setCenter` sin lerp,
solo con desplazamiento >=0,5 bloques. Advertencia 3, dano/buffer 0.
La recuperacion siempre usa el rectangulo completo, aunque el cuadrado visual se desplace.

Se conservan las invitaciones con token, los menus de miembros, el liderazgo,
las caidas/camara y la sincronizacion de 1.1.0. Controladores `.on` sin `.fin`
mantienen el borde entre oleadas. Infinita/Fosa usan enemigos etiquetados vivos;
sin enemigos el borde se oculta. Morir/salir/cambiar mundo/apagar lo limpia.

## Zonas de todas las mazmorras

Coordenadas de caras de bloque, limites abiertos para el centro del jugador.
La primera copia es el nombre base; las restantes agregan `_2`..`_6` (Fosa hasta `_3`).
Santuario es dimension: Bukkit `world_minecraft_santuario_azeroth` y sus sufijos.

| Mundo base (copias) | Sala | X | Z | Medicion |
|---|---|---|---|---|
| bosque (1..6) | Claro de las raices | 1411..1495 | 1512..1603 | cerco +4 |
| bosque (1..6) | Altar del Chaman | 1543..1649 | 1356..1425 | cerco +4 |
| mina (1..6) | Campamento Minero | -5.5..26.5 | -140.5..-108.5 | sin barreras claras; radio anterior |
| mina (1..6) | Lago Subterraneo | -2.5..41.5 | -180.5..-136.5 | sin barreras claras; radio anterior |
| mina (1..6) | Tuneles de Soporte | 27.5..59.5 | -217.5..-185.5 | sin barreras claras; radio anterior |
| mina (1..6) | Salon del Guardian | 1.5..71.5 | -283.5..-213.5 | sin barreras claras; radio anterior |
| tumba (1..6) | Patio de los olvidados | -176.5..-120.5 | -126.5..-70.5 | sin barreras claras; radio anterior |
| tumba (1..6) | Pasaje de los sellos | -211.5..-139.5 | 167.5..239.5 | sin barreras claras; radio anterior |
| tumba (1..6) | Trono del Rey de Arena | -55.432..56.568 | -55.488..56.512 | sin barreras claras; radio anterior |
| cumbre_hielo (1..6) | Plaza de la fuente | -59.6..8.4 | -57.4..10.6 | sin barreras claras; radio anterior |
| cumbre_hielo (1..6) | Trono del Yeti | -229.8..26.2 | -71.1..184.9 | sin barreras claras; radio anterior |
| forja_volcano (1..6) | Forja - sala 1 | -40.8..87.2 | -223.4..-95.4 | sin barreras claras; radio anterior |
| forja_volcano (1..6) | Forja - sala 2 | -173.5..-77.5 | -173.7..-77.7 | sin barreras claras; radio anterior |
| forja_volcano (1..6) | Nucleo de la Forja | -63.9..48.1 | -77.1..34.9 | sin barreras claras; radio anterior |
| santuario_azeroth (1..6) | Prueba de los cinco ecos | 106.5..406.5 | 106.5..406.5 | sin barreras claras; radio anterior |
| infinita (1..6) | Infinita | -31.5..32.5 | -31.5..32.5 | sin barreras claras; radio anterior |
| fosa (1..3) | Fosa | -57..61 | 35..153 | sin barreras claras; radio anterior |

Solo el Bosque tiene cercos cerrados claros en la ventana inspeccionada. Los demas
conservan exactamente sus cuadrados anteriores: el informe "sin barreras" significa
sin cerco cerrado identificable, aunque haya techos o barreras parciales. No se quitan.
Deteccion por aire interior cerrado, columnas de al menos cuatro barreras, ventana
±100 XZ / -15..+70 Y, centro y llegada dentro del mismo componente. Nunca usar
`spawn_bounds` como limite. Informe: [medicion](zonas-pelea-medicion-18-11.md).
Vistas esquematicas, sin terreno ni texturas: `build/previews/zonas_*.png` (ocho mundos).

Bosque sala 1: interior original X1415..1491 / Z1516..1599; nuevo 84x91.
Jefe: X1547..1645 / Z1360..1421; nuevo 106x69. Las paredes tienen espesor y escalones;
son envolventes del interior medido. Los radios de conteo son **108 / 103**:
cubren cualquier esquina y hasta +70 Y. Entrada/arranque siguen en **44**.
Los selectores de enemigos por tag ya abarcan el mundo propio (`distance=0..`).
Las apariciones, terreno y controladores conservan sus ubicaciones.

## Instalacion: archivos exactos

Sin peleas en curso, apagar, respaldar estos cuatro destinos, subirlos y reiniciar.
No usar PlugMan ni reload general de Bukkit. No cambiar R2, pack, TAB, BetterModel
ni scripts de Skript. Conservar los Mythic privados `mobs/astral.yml` y `skills/astral.yml`.

| Archivo local desde raiz del repo | Destino desde raiz del servidor | SHA-256 |
|---|---|---|
| `build/runtime/AstralParty.jar` | `plugins/AstralParty.jar` | `b391808dbf7139787ca8a8ae429922ae7224e6539f169f332ddb079b6a057f2b` |
| `build/mythicmobs/mobs/bosque.yml` | `plugins/MythicMobs/mobs/bosque.yml` | `0be2cb9c5894b13664cd31962f2dfd53f62a52759b69b69d12752930b59c6a41` |
| `build/mythicmobs/skills/bosque.yml` | `plugins/MythicMobs/skills/bosque.yml` | `f3602310685a2f38412eb12f2108c4c333df7d0a5beeffd4409cd52dab317d95` |
| `build/AstralRPG-Bosque-Bordes.zip` | `world/datapacks/AstralRPG-Bosque-Bordes.zip` | `8852b4208dfe855e9cc95748344676c5f6feb4707feed2d907ef104798703242` |

El complemento contiene solo `pack.mcmeta` y las tres funciones
`astral:tanda2/bosque/sala1/wave1..3`; el ZIP principal queda intacto.
La unica diferencia funcional respecto al principal previo es `distance=..40` → `..108`.
Debe tener prioridad sobre el principal:

```text
minecraft:datapack list enabled
minecraft:datapack disable "file/AstralRPG-Bosque-Bordes.zip"
minecraft:datapack enable "file/AstralRPG-Bosque-Bordes.zip" last
minecraft:datapack list enabled
```

Omitir disable si no esta habilitado; si ya esta ultimo, no cambiar el orden.
El reinicio carga JAR y YAML. Solo si el JAR 1.2.0 ya esta instalado y se cambian
unicamente los YAML: `mm reload`. El futuro `build.py` integra el conteo nuevo;
al consolidarlo, retirar este complemento para no tapar oleadas futuras.
No reemplazar el datapack principal pendiente por una version anterior.

## Barreras del Bosque: pendiente de revision del terreno

**No ejecutar todavia sin la decision de Claude/dueno sobre el terreno.** La copia
local tiene columnas transitables fuera del +4 en todos los lados de sala 1;
el jefe presenta vacio en todo el norte y sectores oeste/este, y piso abierto
en oeste/este/sur. No se certifica un cierre natural. Detalle y ejemplos en la
[medicion](zonas-pelea-medicion-18-11.md). El plugin protege XZ durante la pelea,
pero no impide caer dentro del rectangulo ni protege entre combates.

Comandos locales, no archivos para subir al servidor:

- `build/deploy/bosque-barreras-18-11.txt`: regiones finas de las dos paredes,
  `barrier -> air`, para bosque..bosque_6. No contiene un cubo grande de la sala.
- `build/deploy/bosque-barreras-18-11-deshacer.txt`: cuboides disjuntos de bloques
  originales, `set barrier`. No usa `replace air barrier`; restaura solo barreras
  originales. No construir ni modificar esos lugares entre retiro y restauracion.

Los TXT usan nombres de comando de consola Bukkit con una barra: `/world`,
`/pos1`, `/pos2`, `/replace`, `/set`. En chat se agrega una barra: `//world`,
`//pos1`, `//pos2`, `//replace`, `//set`. [Referencia WorldEdit](https://worldedit.enginehub.org/en/latest/commands/).
Omitir comentarios y ejecutar en orden desde la MISMA sesion de consola;
comprobar la seleccion y el primer reemplazo antes de continuar. Guardar respaldo
del proveedor antes de intervenir. No ejecutar inverso sobre un mundo diferente.
Las copias identicas fueron informadas por el arquitecto; verificar que sigan
iguales antes de aplicar la lista. Las regiones locales se abrieron solo en lectura.

No sustituir mundos ni subir regiones; nunca usar Worlds > Upload en la fila world.
Si Aternos no admite el JAR propio, el despliegue queda bloqueado por el proveedor;
no usar APIs privadas ni eludir restricciones.

## Verificacion y reproduccion

49 pruebas Python y 95 comprobaciones Paper con jugadores NMS, cero fallas.
Incluyen deteccion real de Bosque (cuando las copias privadas estan disponibles),
cercos separados/caminos/techos, fallback, conteo de esquinas en 3D y restauracion
sin aire agregado; en Paper clamp X/Z, casi cuadrado, umbral 0,5, misma instancia,
recuperacion rectangular, caidos, dos salas, Infinita y Fosa por enemigos vivos.
Skript carga sin errores. Ensayo en `.local/zonas-pelea-probe/paper.log` (privado).
No sustituye cliente real, MythicMobs completo ni consola remota.

Desde `datapack-src`:

```text
python zonas_pelea.py --maps ../.local/mapas/server-18-11
python mobs/mazmorra.py
python bosque_bordes.py
python party.py --java <java25> --server <Paper-local> --papi <PlaceholderAPI.jar>
python -m unittest test_zonas_pelea test_party test_duelos test_mazmorras test_mazmorras_copias test_oleadas_tanda2 test_tanda2c test_viajes_mazmorras
python deploy_party_bordes.py
```

El primer comando requiere mapas privados SOLO para volver a medir; se omite en
builds normales, que usan el JSON versionado. Ensayo desde raiz, solo 127.0.0.1:

```text
python tools/probar_party_paper.py --java <java25> --base <Paper-local> --papi <PlaceholderAPI.jar> --work .local/zonas-pelea-probe
```

Claude debe revisar consola tras reiniciar y probar con clientes en ambas salas del
Bosque: borde en los limites, recorrido de extremos largos, perla, empuje, caida,
avance/victoria y ausencia de barreras invisibles residuales. No subir PartyProbe,
mapas, regiones, `.local`, logs ni archivos ajenos a esta tarea.
