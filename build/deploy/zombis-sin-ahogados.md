# Zombis sin conversion a ahogado (27/11/2026)

Pedido: impedir que un zombi se convierta en ahogado y pierda su vida escalada conservando el tier.

Fuente: `datapack-src/zombis_sin_ahogados.py`.
Generar: `python datapack-src/zombis_sin_ahogados.py`.
Subir `build/gameplay/astral_zombis_sin_ahogados.sk` a
`plugins/Skript/scripts/astral_zombis_sin_ahogados.sk`.
Activar: `skript reload astral_zombis_sin_ahogados` y comprobar la respuesta sin errores.
No necesita reinicio ni otros archivos. No cambia mundos, plugins ni datos de jugadores.

Solo cancela EntityTransformEvent con causa DROWNED y entidad original de tipo ZOMBIE.
Conserva ahogados naturales, husk -> zombi, curacion de aldeanos y congelacion de esqueletos.
No modifica los ahogados que ya existan ni repara retroactivamente su vida.

Ensayo: `python tools/probar_zombis_paper.py --java <java25>`.
Paper 26.1.2 + Skript 2.17.1: 16 comprobaciones, 0 fallos; tres conversiones reales
(zombi normal, T3 y T10 elite), vida maxima/tier conservados y controles de otras transformaciones.
El plugin ZombieConversionProbe se usa exclusivamente en el ensayo local.

Estado: probado localmente; instalacion y comprobacion remota pendientes.
Anuncio para Discord cuando quede activo:
"Corregimos un fallo que permitia convertir zombis en ahogados con muy poca vida.
Los zombis ya no se transforman al permanecer bajo el agua. Gracias a PepeMega por avisar."
