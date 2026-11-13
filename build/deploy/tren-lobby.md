# Tren lobby -> survival: AstralTrain 1.2.0, despliegue pendiente

Generador: `datapack-src/tren_lobby.py`. Servidor vigente documentado: Empower,
Paper 26.1.2 build 74 / Java 25. Aternos es copia y no admite este JAR propio.
Esta actualizacion no cambia bloques, mapas, NPC, datapack ni resource pack.

## Comportamiento y geometria

Via norte-sur en x=120, y=99; centro del anden `home`: z=193.5.
Muros negros: cara norte z=176.0 y cara sur z=211.0; rieles z=178..208.
Locomotora de 4.89375 bloques y dos vagones de 3.6275125, dos plazas por vagon.
El tren aparece quieto con la cola junto al muro norte, admite pasajeros enseguida
y espera 3 s desde el primer pasajero (avisos 3, 2, 1). Si todos bajan se cancela
la cuenta. Sale hacia SOUTH a 0.16 bloques/tick (3.2 bloques/s a 20 TPS).
Teletransporta cuando el frente llega al muro sur; transfiere solo los ocupantes
actuales a su cama valida en `world` o al spawn de `world`.
Destruye el tren y lo repone quieto en la misma posicion inicial, sin regreso vacio.
El arranque y `astraltren recrear` usan esa posicion. El anden de emergencia
permanece junto a `home`: x=118.5, y=99.2, z=193.5.
Un viaje incompleto/atascado se cancela a los 600 ticks; devuelve pasajeros al anden.
Desconexion y apagado tambien los devuelven; conserva recuperacion de coches propios.

Valores embebidos `viaje`: `salida: -8.925612`, `teleport: 15.053125`,
`espera: 3`, `velocidad: 0.16`. `salida` mide el centro del tren desde `home`;
`teleport` mide el centro de la locomotora desde `home`.
El objetivo cola z=176.25 fue rechazado por `findSpawnLocations`. La busqueda
cada 0.001 bloques encontro el primer CENTER valido en salida=-8.925613;
se genera -8.925612 para quedar del lado aceptado del limite numerico.
El acople de TrainCarts agrega separacion entre coches: la cola real queda en
z=178.0000005, a **2.0000005 bloques del muro norte**; centro del ultimo vagon
z=179.81375675 y centro inicial de locomotora z=188.7019005.
Es la posicion mas cercana aceptada sin modificar rieles ni bloques.
La medicion efectiva esta en `build/tren/verificacion.md`. La locomotora debe llegar a z=208.553125;
se acorta el ultimo tick para que el frente quede en z=211.0.

El plugin lee `viaje.*` del config embebido en el JAR. El config del servidor
solo los reemplaza con `viaje.manual: true`; por defecto false, incluso si la
config antigua tiene otros valores. Para ajuste manual agregar esa clave y los
valores deseados, y reiniciar. Se elimina la clave obsoleta `viaje.parada` al guardar.
**Conservar el config del servidor**, con `enabled`, `station` y `cart-ids`.
No subir el config generado sobre una instalacion existente.

## Actualizacion exacta de una instalacion existente

| Archivo local | Destino remoto |
|---|---|
| `build/tren/AstralTrain.jar` | `plugins/AstralTrain.jar` (1.2.0) |
| `build/tren/AstralTrain/train.yml` | `plugins/AstralTrain/train.yml` |

Solo esos dos archivos son necesarios. El modulo opcional de inspeccion actualizado:
`build/tren/Train_Carts/savedTrainModules/astral_lobby.yml` ->
`plugins/Train_Carts/savedTrainModules/astral_lobby.yml`. No spawnearlo a mano:
el complemento mantiene una unica instancia `astral_lobby_survival`.

1. Respaldar los destinos y `plugins/AstralTrain/config.yml`. Confirmar estacion
   guardada `120 99 193 SOUTH` y que `viaje.manual` no este true salvo ajuste intencional.
2. Apagar completamente el servidor, reemplazar JAR y train.yml y volver a iniciar.
   No usar `/reload`, PlugMan ni recarga general de JAR.
3. Revisar consola: AstralTrain 1.2.0, Train_Carts y BKCommonLib habilitados sin errores.
   Dependencias fijadas: TrainCarts 2.0.0-1720 y BKCommonLib 2.0.0-2018,
   hashes en `build/tren/versions.json`; no reinstalarlas si ya coinciden.
4. Verificar un unico tren completo, quieto junto al muro norte. Si hace falta
   recrearlo: `astraltren recrear` (consola, sin `/`). No es una recarga del JAR.
5. Probar con cliente y jugador sin OP: entrada, avisos 3/2/1, bajarse antes,
   1 y 3 pasajeros, cama/sin cama, frente en muro sur, reaparicion inmediata,
   desconexion y reinicio. Mantener protecciones; no abrir permisos globalmente.
   Revisar consola y medir `spark health --memory` antes/despues en el hosting.

No hace falta subir packs a R2, cambiar server.properties ni recargar otros plugins.
No subir TrainProbe.jar, logs, arte privado ni mundos de ensayo.
Nunca sustituir mundos ni usar Worlds -> Upload en la fila world.

AstralTrain.jar SHA-256: `06794ff5a952f7ec47b6f4255be2fc0c0c37f06addd843439bf43d584c31e6b9`.
Pack privado conservado sin cambios: SHA-1 `0aa45479c57f98d1f555ff11fb559dc7504204df`.
Base Alas/casco SHA-1 `54ace74b9f9b6a962ca3bd92bc60ff6e74a3e838`; 12640 entradas previas conservadas.
El codigo/configuracion propia se publica; arte y procedencia permanecen privados.

## Reproduccion y verificaciones

```text
python datapack-src/tren_lobby.py --java <java25.exe> --server <Paper-local>
python tools/probar_tren_paper.py --java <java25.exe> --base <Paper-local>
python -m unittest discover -s datapack-src -p test_tren_lobby.py
python tools/verificar_terceros.py
```

En PC nueva usar `--download-deps` y preparar la base privada Alas/casco;
`--source <ZIP-original>` permite conservar el original fuera de Downloads.
Ensayo aislado con jugadores NMS simulados, geometria real reproducida en un lobby
sintetico; no sustituye render, click real, WorldGuard ni revision del hosting.
Resultados en `build/tren/verificacion.md`; logs solo en `.local/tren-probe/`.
**Despliegue remoto: no realizado.** Claude continuara con navegador si tiene acceso.
