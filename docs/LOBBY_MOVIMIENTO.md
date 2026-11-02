# Velocidad del lobby

Instalado en Aternos el 01/11/2026. El usuario confirmo que funciona en supervivencia.

- Velocidad I, sin particulas, renovada cada segundo para jugadores del mundo del
  controlador (`lobby`). El efecto dura 60 ticks y se agota hasta tres segundos
  despues de abandonar ese mundo.
- Generador: `datapack-src/lobby.py`, funciones `movement_mob` y `movement_commands`.
- Archivo: `build/mythicmobs/mobs/lobby.yml` -> `plugins/MythicMobs/mobs/lobby.yml`.
- Controlador unico: `astral_lobby_movimiento`, en `lobby,180.5,98,190.5`.
  El chunk ya estaba cargado permanentemente; no se agregaron cargas nuevas.
- MythicMobs recargo sin errores nuevos (116 mobs y 384 skills). Permanecen los
  avisos conocidos de los dialogos de ejemplo.
- Se explicitan filtros para creativo e invulnerabilidad, excluyendo espectadores.
  La comprobacion del administrador en creativo no mostro efecto; el funcionamiento
  en supervivencia fue confirmado por el usuario. No se altero su modo de juego.

Para reinstalar: reemplazar el YAML, ejecutar `mm reload` y usar las lineas finales
de `build/lobby/comandos.txt` solo si falta el controlador. No crear duplicados.
Los cambios fuente y generados estan guardados localmente, pendientes de commit/push.

Referencia de sintaxis: [Potion](https://wiki.mythiccraft.io/mythicmobs/skills/mechanics/potion)
y [Targeters](https://wiki.mythiccraft.io/mythicmobs/Skills/Targeters).
