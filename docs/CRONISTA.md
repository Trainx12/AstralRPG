# Cronista: aceptar y seguir misiones

La tarjeta muestra el objetivo y el premio base. Un clic en cualquier parte de
la tarjeta o en **ACEPTAR MISION** activa la misma mision. Cambiar de pestana no
acepta nada. Una confirmacion con sonido y el estado **ACTIVA** distinguen una
mision aceptada; el boton pasa a **COMPROBAR**. El progreso y los premios extra
aparecen al pasar el cursor sobre la tarjeta.

**COMPROBAR** valida los requisitos existentes antes de entregar premios.
**YA COBRADA** desactiva los clics de la diaria completada. Pausar una mision
activa requiere **Shift + clic**, conserva el progreso y permite retomarla.
Las diarias siguen cambiando a medianoche de Argentina. Una tarjeta anterior
al cambio de dia nunca acepta silenciosamente otra diaria.

El panel azul con relojes usa glifos privados y modelos `astral:cronista/*`.
Solo los cinco menus `misiones*.yml` usan estos assets. Las tarjetas y los
botones se dividen en fragmentos de 18 px para conservar el tamano nativo y
todos los puntos de clic. Las ventanas del fondo son transparentes para que
los titulos no tapen los objetos ni sus cantidades. El HUD, el menu de pausa,
los inventarios de ladrillos y las armaduras vanilla se conservan.

Generadores: `misiones.py`, `menus.py`, `cronista_ui.py`, `build_pack.py`.
Verificacion: `python -m unittest test_misiones` desde `datapack-src` y
`verify.py --client-jar ...`. La vista previa `build/Cronista-preview.png`
representa el diseno; la comprobacion final se realiza con DeluxeMenus.
