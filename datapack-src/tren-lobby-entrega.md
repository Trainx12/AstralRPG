# Tren lobby → survival: entrega sin desplegar

Generador: `datapack-src/tren_lobby.py`. Posterior a esqueletos, Cosmeticos, tanda5a,
Alas/casco y Recetas de mesa. No reemplaza AstralDecor 1.5.0 ni el datapack actual.
Servidor vigente documentado: **Empower, Paper 26.1.2 build 74 / Java 25**.
Aternos es copia y no admite este JAR propio; no intentar subirlo por vias alternativas.

## Implementacion

TrainCarts **2.0.0 build 1720** y BKCommonLib **2.0.0 build 2018**, descargas oficiales
y SHA-512/SHA-256 en `build/tren/versions.json`. Compatibilidad declarada por el autor:
[TrainCarts 2.0.0](https://modrinth.com/plugin/traincarts/version/2.0.0).
Tres vagones, una plaza cada uno, mas locomotora sin asiento. Click normal para subir;
shift para bajar. El primer pasajero inicia 5 s de espera con avisos y sonido; si todos
bajan se cancela. Recorre 8 bloques a 0,16 bloques/tick, con silbato de salida.
Al llegar se transfieren exclusivamente los pasajeros actuales, a su punto de reaparicion
valido en `world` o al spawn de `world`. El tren se repone vacio en la estacion.
No admite subir durante el movimiento. Un viaje atascado se cancela a los 12 s,
devolviendo pasajeros al anden; desconexion y apagado tambien los devuelven.

AstralTrain 1.0.0 usa la API publica de TrainCarts para espera, llegada y recuperacion;
no requiere carteles de comandos ni dar permisos de teleport/TrainCarts a los jugadores.
Mantiene la espera nativa de TrainCarts hasta la salida, incluyendo la carga inicial
de mundos, para impedir desplazamientos antes de comenzar el viaje.
Guarda en su config los UUID de sus cuatro coches para retirar restos propios tras
un cierre abrupto, incluso si Paper carga alguna entidad tarde. Conservar esa config
en las actualizaciones; el archivo generado se usa solo en la primera instalacion.
El YAML propio final queda en el repo, sin arte. No se eligio la alternativa Skript:
TrainCarts tiene soporte oficial para 26.1.2 y gestiona asientos/trenes y movimiento.

**Diferencias verificadas respecto del plan:** el Viajero actual ejecuta
`mvtp <jugador> w:world` (`mobs/mythic.py`), no un regreso individual garantizado a la cama.
El tren implementa el destino individual solicitado. Los dos pastes originales
`donufamuju` y `ucupiwicob` devolvieron HTTP 403 en las rutas de datos; no se importaron.
Se preparo configuracion propia equivalente; faltan cotejo visual del asiento/modelo
con el cliente y, si el autor recupera esos pastes, comparacion con sus offsets originales.

## Lugar pendiente de confirmar

**No activar en el pasto ni usar 116.8 / 127.5 / 212.1 como centro de la estacion.**
Es la posicion de observacion mirando al norte, pitch 46, no la entrada.
Se inspecciono en solo lectura `.local/backups/lobby-antes-ambientacion.zip`:
hay terreno de la montaña frente a esa posicion, pero no se pudo identificar de forma
inequivoca el hueco elegido ni certificar espacio libre detras. La copia de pruebas
`.local/testsrv/.../lobby` no sirve para medir esa zona: contiene chunks vacios alli.
No se modifico ningun mapa ni se propone sustituirlo.

Paso para el dueno: pararse **en la entrada del hueco**, enviar XYZ con F3 y la direccion
hacia el interior. Luego revisar dentro, fijar la altura de las vias y medir una caja libre.
El anden debe quedar dentro/detras de la montaña. Conservar fachada, construcciones y
espacio vecino para futuras maquinas de minijuegos. Agrandar solo el tunel necesario,
con supervision en juego; estos archivos no excavan automaticamente.

Propuesta **relativa**, todavia sin rectangulo absoluto: estacion orientada norte,
centro de las vias `<x> <y> <z>`; caja X `[x-3,x+3]`, Y `[y-1,y+5]`,
Z `[z-16,z+16]` (7 × 7 × 33). Vias X=x, Y=y, Z `[z-14,z+14]`;
anden transitable a ambos lados. La salida de emergencia es `x+2.5,y+0.2,z+0.5`.
Mantener piso firme y aire sobre esa salida. El centro no es la locomotora: se
centran los cuatro coches y la locomotora mira al norte.

**Solo tras medir espacio completamente libre**, adaptar estos comandos de consola
(sustituir `<x> <y> <z>` por coordenadas enteras del centro; no ejecutar placeholders):

```text
execute in minecraft:lobby positioned <x> <y> <z> run fill ~-3 ~-1 ~-16 ~3 ~-1 ~16 minecraft:stone_bricks keep
execute in minecraft:lobby positioned <x> <y> <z> run fill ~ ~ ~-14 ~ ~ ~14 minecraft:rail[shape=north_south] keep
astraltren fijar <x> <y> <z> NORTH
```

`keep` solo agrega en aire; no limpia una sala ocupada ni garantiza que sea segura.
Revisar toda la caja, apoyos de vias, luces, techo y anden en juego antes de habilitarlo.
Para otra orientacion hay que rotar el rectangulo y cambiar shape a `east_west` si corresponde.
El complemento no toca bloques. No usar comandos fill con `replace` para abrir la montaña.

## Archivos exactos y destinos

| Local | Destino |
|---|---|
| `.local/tren-deps/traincarts.jar` | `plugins/TrainCarts.jar` (2.0.0-1720) |
| `.local/tren-deps/bkcommonlib.jar` | `plugins/BKCommonLib.jar` (2.0.0-2018) |
| `build/tren/AstralTrain.jar` | `plugins/AstralTrain.jar` (1.0.0) |
| `build/tren/AstralTrain/train.yml` | `plugins/AstralTrain/train.yml` |
| `build/tren/AstralTrain/config.yml` | `plugins/AstralTrain/config.yml`, **solo primera instalacion** |
| `build/tren/Train_Carts/savedTrainModules/astral_lobby.yml` | `plugins/Train_Carts/savedTrainModules/astral_lobby.yml` |
| `.local/terceros/AstralRPG-privado/build/entregas/tren-lobby/AstralRPG-Textures.zip` | R2, objeto `AstralRPG-Textures.zip` |

Con `ASTRAL_PRIVADO` personalizado, reemplazar el prefijo del ultimo archivo.
No subir `TrainProbe.jar`, mundos de prueba, logs, originales del pack ni el ZIP publico.
El modulo savedTrain permite inspeccionar `AstralLobby`; **no spawnearlo a mano**:
el complemento mantiene una unica instancia con nombre `astral_lobby_survival`.
Los JAR de terceros quedan locales; si faltan, descargarlos de las URL fijadas en versions.json
y verificar hashes antes de compilar/instalar. Nunca reemplazar configs completas de otros plugins.

AstralTrain.jar SHA-256: `{{JAR_SHA256}}`.
Pack FINAL SHA-1: `{{PACK_SHA1}}`.
Base Alas/casco SHA-1: `{{BASE_SHA1}}`; {{PRESERVED}} entradas anteriores conservadas
byte por byte; sin eliminaciones. El arte y procedencia detallada estan solo en privado.
Se convierten overrides de paper/CMD a `assets/astral/items/tren_head.json` y
`tren_cart.json`, componente `minecraft:item_model`, texturas en atlas item y
contexto FIXED de display. No cambia `minecraft:paper` ni se copia pack_format 9.

## Instalacion y WorldGuard (pendientes)

1. Respaldar destinos, config de WorldGuard y server.properties. Verificar cadena previa
   instalada; medir `spark health --memory` antes de agregar plugins y guardar el resultado privado.
2. **Apagar**, instalar los tres JAR y archivos propios de la tabla. No instalar duplicados
   de TrainCarts/BKCommonLib bajo otros nombres. Conservar SavedTrainProperties.yml y datos ajenos.
3. Publicar el FINAL privado solo durante el despliegue:

   ```text
   python tools/subir_pack_r2.py .local/terceros/AstralRPG-privado/build/entregas/tren-lobby/AstralRPG-Textures.zip
   ```

   Verificar descarga publica y poner `resource-pack-sha1={{PACK_SHA1}}` en
   server.properties. No cambiar URL/credenciales ni publicar el pack desde GitHub.
4. Iniciar y revisar consola: BKCommonLib, Train_Carts y AstralTrain deben habilitarse.
   La primera instalacion queda `enabled: false`; el tren no aparece hasta fijar estacion.
   **No usar `/reload`, PlugMan ni recarga general para los JAR.**
5. Tras definir XYZ, seleccionar con WorldEdit SOLO la caja medida, crear
   `rg define -w lobby astral_estacion` y poner prioridad superior a las regiones
   existentes que se superpongan (consultar `rg info -w lobby` antes).
   En esa region, y solo si estan bloqueados, aplicar:

   ```text
   rg flag -w lobby astral_estacion vehicle-place allow
   rg flag -w lobby astral_estacion vehicle-destroy deny
   rg flag -w lobby astral_estacion ride allow
   ```

   No abrir `build`/`use` globalmente. Si la seleccion incluye futuras maquinas,
   reducirla. Mantener `block-plugin-spawning: false` ya documentado; no permitir mobs
   naturales en el lobby. Probar entrada normal con jugador sin OP/bypass. El plugin
   no modifica WorldGuard; si otra proteccion cancela el viaje, conservarla y diagnosticar.
6. Construir solo en espacio libre, revisar salida de emergencia y ejecutar `astraltren fijar ...`.
   Ese comando guarda la estacion para reinicios. `/astraltren` informa estado;
   `/astraltren apagar` retira el tren y devuelve ocupantes, sin borrar la estacion guardada.
7. **Viajero conservado de respaldo por ahora.** Decision para el dueno al validar el tren:
   retirarlo o mantenerlo. No se eliminan todos los NPC ni se regenera lobby para esta tarea.
   Si decide retirarlo, identificar exclusivamente `astral_npc_viajero` con MythicMobs
   y retirarlo en juego; actualizar despues el generador para que no se recree.
8. Medir nuevamente `spark health --memory` con 0 y 3 pasajeros; comparar heap,
   Non-heap/Metaspace, TPS y MSPT con la misma carga y calentamiento. Anotar resultados
   privados; no extrapolar cifras de la PC local al hosting. Revisar consola tras viajar
   y tras reiniciar, y verificar un unico tren en el anden.

## Reproduccion y verificacion

```text
python datapack-src/tren_lobby.py --java <java25.exe> --server <Paper-local>
python tools/probar_tren_paper.py --java <java25.exe> --base <Paper-local>
python -m unittest discover -s datapack-src -p test_tren_lobby.py
python tools/verificar_terceros.py
```

En una PC nueva agregar `--download-deps` a la primera linea; usa las URL y hashes
fijados. `--source <ZIP-original>` permite preparar el circuito privado sin Downloads.

El ensayo usa un Paper aislado y jugadores NMS simulados; no equivale a tres clientes
reales ni a una captura del juego. Logs privados: `.local/tren-probe/`.
Estado de pruebas y limites se registran en `build/tren/verificacion.md`.
Pendientes obligatorios de aceptacion visual: click/asientos, espacio del tunel,
orientacion y escala del modelo, 1 y 3 clientes, bajarse antes, cama y sin cama,
reinicio con tren afuera, protecciones y consola del servidor real.
No hay captura en `build/previews/` porque no se dispuso de cliente Minecraft;
las futuras capturas que muestren este arte licenciado deben permanecer privadas.

**Despliegue remoto y subida a R2: no realizados.** No sustituir mundos ni usar
Worlds → Upload en la fila world. Esta entrega no incluye archivos de mapa.
