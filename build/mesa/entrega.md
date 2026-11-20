# Mesa de encantamientos: AstralMesa (reemplaza a LynExp)

Problema: LynExp arma un libro por nivel y la ventana tiene 48 lugares. Con ExcellentEnchants
los libros pasan de 48 y los vanilla quedaban afuera.

AstralMesa muestra todo (vanilla primero, despues ExcellentEnchants, maldiciones al final) con paginas,
sin las mejoras del Herrero (`astral:`). Saca los niveles que el objeto ya tiene y los que chocan con
lo que ya tiene. El objeto queda en la mesa para encantar varias veces; al cerrar vuelve al inventario.

## Subir
1. Files: `plugins/` -> borrar (o renombrar a `.jar.off`) `LynExp-1.0.0-mc26.1-26.1.2.jar`.
2. Subir `build/mesa/AstralMesa.jar` a `plugins/`.
3. Reiniciar el server (crea `plugins/AstralMesa/config.yml`).
4. Probar: clic derecho en una mesa de encantamientos con una espada en el inventario.

Config: `plugins/AstralMesa/config.yml`, recargar con `astralmesa reload`.
