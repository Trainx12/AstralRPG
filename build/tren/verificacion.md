# Verificacion local del tren

Generado por `tren_lobby.py`; no es evidencia de despliegue remoto.
Paper 26.1.2 build 74, Java 25; jugadores NMS simulados, sin clientes reales.

AstralTrain.jar SHA-256: `eb5b8efba24117ea24e8680b3fa331e8003f2ca949a5418d7c648c9c9c9a41ed`.
Los resultados solo se dan por correctos si el JAR del ensayo coincide byte por byte con la entrega.

| Ensayo | Resultado | Comprobaciones correctas |
|---|---|---|
| paper.log | Pendiente o fallido | 35 |
| restart.log | Pendiente o fallido | 5 |
| crash-restart.log | Pendiente o fallido | 3 |

Memoria medida con `spark health --memory`, con TrainCarts/BKCommonLib cargados.
Estas son muestras del ensayo local, no un diferencial contra Paper sin plugins.
La primera es anterior a los viajes; la segunda posterior a los viajes.

| Muestra en paper.log | Heap | Non-heap |
|---|---|---|
| 1 | 639.0 MB | 217.1 MB |
| 2 | 699.0 MB | 257.5 MB |

## Geometria y configuracion

Via sintetica identica: x=120, y=99, rieles z=178..208; muros z=175 y z=211.
Objetivo inicial cola z=176.25 rechazado: findSpawnLocations devuelve null.
Se busco el primer spawn aceptado en incrementos de 0.001 bloques, sin cambiar vias.
Valores embebidos: `{'velocidad': 0.38, 'espera': 3, 'teleport': 15.053125, 'salida': -10.825613}`; manual false por defecto.


Se acorta el ultimo tick: el ensayo exige frente en z=211.0 con tolerancia 0.001.
El ensayo comprueba tren completo quieto, JAR sobre config vieja, override manual,
pasajeros actuales, cama/spawn y recuperacion tras reinicio y corte abrupto.

Pruebas Python: `python -m unittest discover -s datapack-src -p test_tren_lobby.py` (6 casos).
Cubren plazas, posicion junto al muro, llegada, espera/velocidad, reproducibilidad y preservacion del pack privado.
Auditoria de arte publico: ejecutar `tools/verificar_terceros.py` con rutas agregadas al indice.

Pendiente: revision del anden en servidor remoto, protecciones WorldGuard con jugador sin OP,
click real, render de asientos/modelo con 1 y 3 clientes, reconexion real y memoria antes/despues en el hosting.
No hay captura de Minecraft. Logs y arte permanecen privados.
