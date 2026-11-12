# Verificacion local del tren

Generado por `tren_lobby.py`; no es evidencia de despliegue remoto.
Paper 26.1.2 build 74, Java 25; jugadores NMS simulados, sin clientes reales.

AstralTrain.jar SHA-256: `c401a19e6b6875d68a0bac0aa354304f47b68ddf43a221e34b7fac2a65542428`.
Los resultados solo se dan por correctos si el JAR del ensayo coincide byte por byte con la entrega.

| Ensayo | Resultado | Comprobaciones correctas |
|---|---|---|
| paper.log | Correcto | 24 |
| restart.log | Correcto | 5 |
| crash-restart.log | Correcto | 3 |

Memoria medida con `spark health --memory`, con TrainCarts/BKCommonLib cargados.
Estas son muestras del ensayo local, no un diferencial contra Paper sin plugins.
La primera es anterior a los viajes; la segunda posterior a los viajes.

| Muestra en paper.log | Heap | Non-heap |
|---|---|---|
| 1 | 689.1 MB | 217.7 MB |
| 2 | 911.7 MB | 259.9 MB |

Pruebas Python: `python -m unittest discover -s datapack-src -p test_tren_lobby.py` (4 casos).
Cubren plazas, reproducibilidad, preservacion de todas las entradas previas y rechazo de colisiones/falta de base.
Auditoria de arte publico: ejecutar `tools/verificar_terceros.py` con rutas agregadas al indice.

Pendiente: XYZ exactos y construccion del anden, protecciones WorldGuard con jugador sin OP,
click real, render de asientos/modelo con 1 y 3 clientes, reconexion real y memoria antes/despues en el hosting.
No hay captura de Minecraft. Logs y arte permanecen privados.
