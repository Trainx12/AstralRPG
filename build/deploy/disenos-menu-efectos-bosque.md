# Disenos de menu: Efectos y Bosque Astral

Pedido: conservar ambos disenos e integrar visualmente los botones existentes.

- Menu principal: Efectos, casilla 31, entre Fragmentos y Duelos. Icono propio de engranaje dorado y destello violeta; abre Configuraciones, con Bajo/Medio/Alto. Conserva las otras posiciones.
- Minas Astrales: Bosque Astral, casilla 47, con su ilustracion existente y marco alineado con la grilla. Conserva las 20 minas, desbloqueos, saldo y acciones. El viaje `/bosque` ya estaba implementado.
- Vistas generadas: `build/Servicios-preview/menu-astral.png` y `build/Interfaces-preview/minas.png`. Son composiciones del generador, no capturas dentro del juego.

Regenerar solo esta entrega: `python datapack-src/disenos_menu.py` (Pillow y PyYAML).
La compilacion completa habitual `build_pack.py` tambien incorpora los cambios.
El generador actualiza el ZIP publico superponiendo solo los recursos de esta entrega; conserva todas las otras entradas y la fuente. No reconstruye equipo ni incorpora cambios locales de otras tareas.

## Recursos preparados

- `build/menus/DeluxeMenus/gui_menus/principal.yml`: destino `plugins/DeluxeMenus/gui_menus/principal.yml`.
- `build/disenos-menu/recursos-menu.zip`: superposicion con los paneles afectados y el modelo/textura nuevo. **No es un resource pack instalable**. Lista exacta: `build/disenos-menu/archivos.json`.
- No cambian glifos, dimensiones ni avances de las fuentes. No requiere modificar Minas Skript: la accion y modelo de Bosque ya existen.

## Estado del despliegue

Esta entrega corresponde al pedido de diseno. No se conecto al panel, no se publico en R2 ni se cambio el servidor.
Antes de instalar, comprobar el FINAL efectivamente instalado en Empower y superponer unicamente estos recursos, conservando el resto y el arte privado. No instalar el ZIP publico ni este ZIP de recursos como FINAL.
Despues: subir el FINAL a R2, verificar su descarga, actualizar SHA-1 en server.properties, instalar principal.yml y recargar DeluxeMenus. Reiniciar cuando corresponda para aplicar el resource pack y validar con un cliente.
No reemplazar mundos. Aternos figura como copia antigua en la documentacion actual.

## Validacion

Revision visual de ambas vistas y pruebas `test_menu_principal` y `test_travel_ui`; resultado final informado en el chat. Pendiente validacion con un cliente real y despliegue.
