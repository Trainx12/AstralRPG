# Verificacion de la entrega unica

- Suite completa: 204 pruebas aprobadas.
- verify.py: JSON, funciones, loot, sprites, IDs y secuencia de mazmorras validos.
- Paper 26.1.2 / MythicMobs 5.13.0 / BetterModel 3.6.0: 158 comprobaciones aprobadas, cero fallos.
- 23 mascotas: invocacion con UUID de dueno, seguimiento (<25 bloques), cambio de mundo y guardado.
- 12 criaturas: tracker animado a ticks 1/8/15 y retirado al tick 24; transformaciones cambian al morir.
- Progreso real: vivos + cola pendiente, barra 3/4 -> 2/4, aislamiento entre dos salas y ocultacion al cambiar de mundo.
- Pack FINAL: SHA-1 `9c181ed2a097ea27021f761346714ca04416e24f`; 5193 referencias verificadas. Cero texturas obsoletas de Carnivora/Asura/peluches.
- Causa reproducida: <global.pet_owner> queda literal; <global.var.pet_owner> devuelve el nombre. La invocacion anterior quedaba sin UUID de dueno.
- Prueba con jugador NMS simulado: no es cliente grafico. Piso de prueba ampliado para evitar caidas al vacio.
- Sin WorldGuard/ClearLag en este Paper. Falta confirmar sus ajustes y la apariencia con cliente real en produccion.
- Sin despliegue remoto ni subida a R2. Logs solo en .local.

Reproduccion local: `python tools/probar_urgente_paper.py --java <java25> --server .local/tanda4a-paper --all-pets --install`.
