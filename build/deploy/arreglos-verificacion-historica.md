# Verificacion local del 11/11/2026

- Suite completa: 193 pruebas aprobadas (incluye 9 regresiones nuevas).
- verify.py: JSON, funciones, loot, sprites, IDs y secuencia de mazmorras validos.
- Paper 26.1.2 / BetterModel 3.6.0 / MythicMobs 5.13.0: 10 casos aprobados. Todos los displays de los 7 modelos de sala tienen glow y RGB FFFFFF. Los 3 controles de mundo normal no reciben el glow del modelo.
- Texturas de las 5 variantes de esqueleto identicas a c3d4af8; arco unido a la mano durante 25 muestras por animacion.
- Alturas y piso/aire de todos los puntos generados validados con la propuesta de apoyos aplicada virtualmente. No certifica que esos apoyos esten instalados: requieren aprobacion y ejecucion explicita.
- Sin cliente Minecraft: captura del contorno, recorrido de salas y aprobacion visual pendientes. Sin despliegue remoto, sin subida a R2. Logs conservados solo en .local.
